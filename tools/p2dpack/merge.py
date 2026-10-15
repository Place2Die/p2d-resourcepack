"""Merges the pack BetterModel generates for 3D mobs into ours, so players get one pack."""

from __future__ import annotations

import shutil
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from p2dpack.files import IGNORED_FILE_NAMES, pack_files

# Root files of the extra pack that ours replaces: one pack, one description and icon.
REPLACED_ROOT_FILES = frozenset({"pack.mcmeta", "pack.png"})


class MergeError(Exception):
    """The extra pack cannot be merged. Lists every problem found, not just the first."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


@dataclass
class MergeResult:
    added: list[str] = field(default_factory=list)
    identical: list[str] = field(default_factory=list)
    replaced_root_files: list[str] = field(default_factory=list)


class PackSource(ABC):
    """Where the extra pack comes from: BetterModel writes a folder or a zip (``pack-type``)."""

    @abstractmethod
    def files(self) -> list[str]: ...

    @abstractmethod
    def read(self, path: str) -> bytes: ...

    @staticmethod
    def open(path: Path) -> PackSource:
        if path.is_dir():
            return DirectorySource(path)
        if path.is_file() and zipfile.is_zipfile(path):
            return ZipSource(path)
        raise MergeError([f"{path}: neither a pack directory nor a zip file"])


class DirectorySource(PackSource):
    def __init__(self, root: Path) -> None:
        self.root = root

    def files(self) -> list[str]:
        return pack_files(self.root)

    def read(self, path: str) -> bytes:
        return (self.root / path).read_bytes()


class ZipSource(PackSource):
    def __init__(self, archive: Path) -> None:
        self.archive = archive
        with zipfile.ZipFile(archive) as zip_file:
            self._entries = {
                info.filename: zip_file.read(info)
                for info in zip_file.infolist()
                if not info.is_dir() and PurePosixPath(info.filename).name not in IGNORED_FILE_NAMES
            }

    def files(self) -> list[str]:
        return sorted(self._entries)

    def read(self, path: str) -> bytes:
        return self._entries[path]


class PackMerger:
    """Copies ``base`` into ``output``, then adds the extra pack's ``assets/``.

    A file present in both packs with different bytes is a conflict and fails the merge; a
    byte-identical file is harmless and kept once. The extra pack's ``pack.mcmeta`` and
    ``pack.png`` are replaced by ours. Anything else outside ``assets/`` (overlay folders,
    e.g. BetterModel's legacy models) fails the merge: overlays would need our
    ``pack.mcmeta`` to declare them.
    """

    def merge(self, base: Path, extra: Path, output: Path) -> MergeResult:
        source = PackSource.open(extra)
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(base, output, ignore=shutil.ignore_patterns(*IGNORED_FILE_NAMES))

        result = MergeResult()
        problems: list[str] = []
        for path in source.files():
            if not self._is_safe(path):
                problems.append(f"{path}: unsafe path in the extra pack")
                continue
            if path in REPLACED_ROOT_FILES:
                result.replaced_root_files.append(path)
                continue
            if not path.startswith("assets/"):
                problems.append(f"{path}: outside assets/ (overlay folder?); set BetterModel's "
                                f"pack.generate-legacy-model to false")
                continue
            data = source.read(path)
            target = output / path
            if target.exists():
                if target.read_bytes() == data:
                    result.identical.append(path)
                else:
                    problems.append(f"{path}: conflict, both packs ship this file with different content")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            result.added.append(path)
        if problems:
            raise MergeError(problems)
        return result

    @staticmethod
    def _is_safe(path: str) -> bool:
        posix = PurePosixPath(path)
        return not posix.is_absolute() and ".." not in posix.parts and "\\" not in path
