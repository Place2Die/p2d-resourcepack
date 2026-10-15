"""Read-only view of a pack directory with a cache of parsed JSON documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from p2dpack.files import pack_files

JSON_SUFFIXES = (".json", ".mcmeta")


class DuplicateKeyError(ValueError):
    pass


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


class PackTree:
    """The files of one pack root (the directory holding ``pack.mcmeta`` and ``assets/``)."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.files = pack_files(root) if root.is_dir() else []
        self._json: dict[str, Any] = {}
        self._json_errors: dict[str, str] = {}

    def json_files(self) -> list[str]:
        return [path for path in self.files if path.endswith(JSON_SUFFIXES)]

    def asset_files(self, kind: str, suffix: str) -> list[str]:
        """Files of ``assets/<namespace>/<kind>/**`` ending with ``suffix``."""
        result = []
        for path in self.files:
            parts = path.split("/")
            if len(parts) >= 4 and parts[0] == "assets" and parts[2] == kind and path.endswith(suffix):
                result.append(path)
        return result

    def load_json(self, path: str) -> Any:
        """The parsed document, or ``None`` when it does not parse (see :meth:`json_error`)."""
        if path not in self._json and path not in self._json_errors:
            try:
                text = (self.root / path).read_text(encoding="utf-8")
                self._json[path] = json.loads(text, object_pairs_hook=_reject_duplicates)
            except (OSError, UnicodeDecodeError, ValueError) as error:
                self._json_errors[path] = str(error)
        return self._json.get(path)

    def json_error(self, path: str) -> str | None:
        self.load_json(path)
        return self._json_errors.get(path)

    def exists(self, file: Path) -> bool:
        return file.is_file()
