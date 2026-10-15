"""Builds throwaway packs on disk for the tests."""

from __future__ import annotations

import json
import struct
import tempfile
import zlib
from pathlib import Path
from typing import Any


def png(width: int = 16, height: int = 16, rgba: tuple[int, int, int, int] = (255, 0, 255, 255)) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    row = b"\x00" + bytes(rgba) * width
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * height))
            + chunk(b"IEND", b""))


class PackFixture:
    """A pack under a temporary directory; every helper returns ``self`` for chaining."""

    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    @classmethod
    def temporary(cls, test_case, name: str = "pack") -> PackFixture:
        directory = tempfile.TemporaryDirectory()
        test_case.addCleanup(directory.cleanup)
        return cls(Path(directory.name) / name)

    def raw(self, path: str, content: bytes | str) -> PackFixture:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            target.write_text(content, encoding="utf-8")
        else:
            target.write_bytes(content)
        return self

    def json(self, path: str, document: Any) -> PackFixture:
        return self.raw(path, json.dumps(document, indent=2))

    def mcmeta(self, min_format: Any = 88, max_format: Any = 88) -> PackFixture:
        return self.json("pack.mcmeta", {"pack": {"description": "test",
                                                  "min_format": min_format, "max_format": max_format}})

    def item(self, namespace: str, item_id: str, model: str | None = None) -> PackFixture:
        """A complete item: definition, model and texture, the way the real pack lays them out."""
        model = model or f"{namespace}:item/{item_id}"
        return (self.json(f"assets/{namespace}/items/{item_id}.json",
                          {"model": {"type": "minecraft:model", "model": model}})
                .json(f"assets/{namespace}/models/item/{item_id}.json",
                      {"parent": "minecraft:item/generated", "textures": {"layer0": f"{namespace}:item/{item_id}"}})
                .raw(f"assets/{namespace}/textures/item/{item_id}.png", png()))
