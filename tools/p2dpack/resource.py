"""Resource locations (``namespace:path``) and the naming rules Minecraft applies to them."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

VANILLA_NAMESPACE = "minecraft"
NAMESPACE_PATTERN = re.compile(r"[a-z0-9_.-]+")
PATH_PATTERN = re.compile(r"[a-z0-9_./-]+")


@dataclass(frozen=True)
class ResourceLocation:
    """A ``namespace:path`` reference, resolved to files under ``assets/``."""

    namespace: str
    path: str

    @classmethod
    def parse(cls, text: str) -> ResourceLocation:
        namespace, separator, path = text.partition(":")
        if not separator:
            return cls(VANILLA_NAMESPACE, text)
        return cls(namespace, path)

    @property
    def is_valid(self) -> bool:
        return bool(NAMESPACE_PATTERN.fullmatch(self.namespace)) and bool(PATH_PATTERN.fullmatch(self.path))

    @property
    def is_vanilla(self) -> bool:
        """Vanilla assets are not in our pack, so references to them cannot be checked."""
        return self.namespace == VANILLA_NAMESPACE

    def file(self, root: Path, kind: str, extension: str) -> Path:
        """The file this location points to inside a pack, e.g. ``kind="models"``, ``extension=".json"``."""
        return root / "assets" / self.namespace / kind / (self.path + extension)

    def __str__(self) -> str:
        return f"{self.namespace}:{self.path}"
