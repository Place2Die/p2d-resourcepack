"""The validation rules. Each :class:`Check` is one strategy run over the whole pack."""

from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from p2dpack.report import Report
from p2dpack.resource import NAMESPACE_PATTERN, PATH_PATTERN, ResourceLocation
from p2dpack.validation.tree import PackTree

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ROOT_FILES = frozenset({"pack.mcmeta", "pack.png"})
# Texture folders stitched into the vanilla atlases for every namespace. A model texture
# elsewhere renders as the missing texture unless the pack adds an atlas source for it.
ATLAS_FOLDERS = ("item/", "block/")


def _type_of(node: dict[str, Any]) -> str | None:
    value = node.get("type")
    if not isinstance(value, str):
        return None
    return value.removeprefix("minecraft:")


class Check(ABC):
    """One validation rule."""

    @abstractmethod
    def run(self, tree: PackTree, report: Report) -> None: ...


class PackMetaCheck(Check):
    """``pack.mcmeta`` exists and its supported format range covers the server's version."""

    def __init__(self, target_format: int) -> None:
        self.target_format = target_format

    def run(self, tree: PackTree, report: Report) -> None:
        if "pack.mcmeta" not in tree.files:
            report.error("pack.mcmeta", "missing")
            return
        meta = tree.load_json("pack.mcmeta")
        if meta is None:
            return  # JsonSyntaxCheck reports it
        pack = meta.get("pack") if isinstance(meta, dict) else None
        if not isinstance(pack, dict):
            report.error("pack.mcmeta", "missing the \"pack\" object")
            return
        if "description" not in pack:
            report.error("pack.mcmeta", "missing pack.description")
        low = self._format(pack.get("min_format"))
        high = self._format(pack.get("max_format"))
        if low is None or high is None:
            report.error("pack.mcmeta", "pack.min_format and pack.max_format must be a number or [major, minor]")
            return
        if low > high:
            report.error("pack.mcmeta", f"min_format {low} is above max_format {high}")
        if not low[0] <= self.target_format <= high[0]:
            report.error("pack.mcmeta", f"format range {low[0]}..{high[0]} does not include {self.target_format}")

    @staticmethod
    def _format(value: Any) -> tuple[int, int] | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value, 0
        if isinstance(value, list) and 1 <= len(value) <= 2 and all(
                isinstance(part, int) and not isinstance(part, bool) for part in value):
            return value[0], value[1] if len(value) == 2 else 0
        return None


class JsonSyntaxCheck(Check):
    """Every ``.json`` and ``.mcmeta`` file parses, without duplicate keys."""

    def run(self, tree: PackTree, report: Report) -> None:
        for path in tree.json_files():
            error = tree.json_error(path)
            if error is not None:
                report.error(path, f"invalid JSON: {error}")


class NamingCheck(Check):
    """Namespaces and asset paths use only the characters Minecraft accepts (lowercase)."""

    def run(self, tree: PackTree, report: Report) -> None:
        for path in tree.files:
            parts = path.split("/")
            if parts[0] != "assets":
                if path not in ROOT_FILES:
                    report.error(path, "unexpected file outside assets/ (only pack.mcmeta and pack.png)")
                continue
            if len(parts) < 3:
                report.error(path, "file directly under assets/ or a namespace, outside any asset folder")
                continue
            namespace = parts[1]
            if not NAMESPACE_PATTERN.fullmatch(namespace):
                report.error(path, f"invalid namespace {namespace!r}: use [a-z0-9_.-] only")
            relative = "/".join(parts[2:])
            if not PATH_PATTERN.fullmatch(relative):
                report.error(path, f"invalid asset path {relative!r}: use [a-z0-9_./-] only")


class TextureCheck(Check):
    """Every ``.png`` really is a PNG with a sane size."""

    def run(self, tree: PackTree, report: Report) -> None:
        for path in tree.files:
            if not path.endswith(".png"):
                continue
            header = (tree.root / path).read_bytes()[:24]
            if not header.startswith(PNG_SIGNATURE) or header[12:16] != b"IHDR":
                report.error(path, "not a PNG file")
                continue
            width, height = struct.unpack(">II", header[16:24])
            if width == 0 or height == 0:
                report.error(path, f"empty image {width}x{height}")


class ItemDefinitionCheck(Check):
    """Every item definition (``assets/<ns>/items/*.json``, read for the ``item_model``
    component) points to models that exist."""

    def run(self, tree: PackTree, report: Report) -> None:
        for path in tree.asset_files("items", ".json"):
            document = tree.load_json(path)
            if document is None:
                continue
            model = document.get("model") if isinstance(document, dict) else None
            if not isinstance(model, dict):
                report.error(path, "item definition needs a \"model\" object")
                continue
            for reference in self._model_references(model):
                self._check_reference(tree, report, path, reference)

    def _model_references(self, node: Any) -> Iterator[Any]:
        """Model ids of every ``model`` node and every ``special`` base, at any depth
        (select cases, conditions, range dispatch, composites)."""
        if isinstance(node, dict):
            kind = _type_of(node)
            if kind == "model":
                yield node.get("model")
            elif kind == "special":
                yield node.get("base")
            for key, value in node.items():
                if not (kind == "model" and key == "model"):
                    yield from self._model_references(value)
        elif isinstance(node, list):
            for value in node:
                yield from self._model_references(value)

    @staticmethod
    def _check_reference(tree: PackTree, report: Report, path: str, reference: Any) -> None:
        if not isinstance(reference, str):
            report.error(path, f"model reference must be a string, got {reference!r}")
            return
        location = ResourceLocation.parse(reference)
        if not location.is_valid:
            report.error(path, f"invalid model id {reference!r}")
        elif not location.is_vanilla and not tree.exists(location.file(tree.root, "models", ".json")):
            report.error(path, f"model {location} not found (expected "
                               f"assets/{location.namespace}/models/{location.path}.json)")


class ModelCheck(Check):
    """Every model's parent and textures exist."""

    def run(self, tree: PackTree, report: Report) -> None:
        for path in tree.asset_files("models", ".json"):
            document = tree.load_json(path)
            if document is None:
                continue
            if not isinstance(document, dict):
                report.error(path, "a model must be a JSON object")
                continue
            self._check_parent(tree, report, path, document.get("parent"))
            textures = document.get("textures", {})
            if not isinstance(textures, dict):
                report.error(path, "\"textures\" must be an object")
                continue
            for name, value in sorted(textures.items()):
                self._check_texture(tree, report, path, name, value)

    @staticmethod
    def _check_parent(tree: PackTree, report: Report, path: str, parent: Any) -> None:
        if parent is None:
            return
        if not isinstance(parent, str):
            report.error(path, f"parent must be a string, got {parent!r}")
            return
        location = ResourceLocation.parse(parent)
        if not location.is_valid:
            report.error(path, f"invalid parent {parent!r}")
        elif not location.is_vanilla and not tree.exists(location.file(tree.root, "models", ".json")):
            report.error(path, f"parent model {location} not found")

    @staticmethod
    def _check_texture(tree: PackTree, report: Report, path: str, name: str, value: Any) -> None:
        sprite = value.get("sprite") if isinstance(value, dict) else value
        if not isinstance(sprite, str):
            report.error(path, f"texture {name!r} must be a string or {{\"sprite\": ...}}")
            return
        if sprite.startswith("#"):
            return  # a reference to another texture variable of the model
        location = ResourceLocation.parse(sprite)
        if not location.is_valid:
            report.error(path, f"invalid texture id {sprite!r} for {name!r}")
            return
        if location.is_vanilla:
            return
        if not tree.exists(location.file(tree.root, "textures", ".png")):
            report.error(path, f"texture {location} ({name!r}) not found (expected "
                               f"assets/{location.namespace}/textures/{location.path}.png)")
        elif not location.path.startswith(ATLAS_FOLDERS):
            report.warning(path, f"texture {location} is outside item/ and block/: it is only "
                                 f"stitched if the pack adds an atlas source for it")
