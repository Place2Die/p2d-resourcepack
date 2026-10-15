#!/usr/bin/env python3
"""Generates the PLACEHOLDER 16x16 item textures until the real art exists.

Every texture listed here is a placeholder: replace the PNG with real art and remove its
entry. Standard library only (zlib + struct), so it runs without Pillow:

    python3 scripts/placeholders.py
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "pack" / "assets"

PALETTE = {
    ".": (0, 0, 0, 0),
    "k": (40, 36, 32, 255),      # outline
    "g": (92, 104, 72, 255),     # olive canvas
    "G": (120, 134, 94, 255),    # olive highlight
    "m": (150, 150, 156, 255),   # metal
    "M": (196, 196, 204, 255),   # metal highlight
    "w": (226, 220, 204, 255),   # cloth
    "W": (246, 242, 230, 255),   # cloth highlight
    "r": (170, 36, 36, 255),     # red
    "o": (200, 120, 40, 255),    # amber bottle
    "O": (232, 164, 80, 255),    # amber highlight
}

# namespace -> texture path -> 16 rows of 16 palette keys
TEXTURES: dict[str, dict[str, list[str]]] = {
    "p2d_survival": {
        "item/canteen": [
            "................",
            "......kkkk......",
            "......kMmk......",
            "......kkkk......",
            ".......km.......",
            "....kkkkkkkk....",
            "...kGGGGGggggk..",
            "..kGGggggggggk..",
            "..kGgggggggggk..",
            "..kGgggkkggggk..",
            "..kGgggkkggggk..",
            "..kGgggggggggk..",
            "..kGgggggggggk..",
            "...kggggggggk...",
            "....kkkkkkkk....",
            "................",
        ],
        "item/bandage": [
            "................",
            "................",
            "................",
            ".....kkkkkk.....",
            "....kWWWWWWk....",
            "...kWwwwwwwwk...",
            "...kWwwrrwwwk...",
            "...kWwrrrrwwk...",
            "...kWwwrrwwwk...",
            "...kWwwwwwwwk...",
            "...kwwwwkkwwk...",
            "....kwwkmmkkk...",
            ".....kkkwwwwwk..",
            "........kkkkk...",
            "................",
            "................",
        ],
        "item/medicine": [
            "................",
            ".....kkkkkk.....",
            ".....kWWWWk.....",
            ".....kwwwwk.....",
            ".....kkkkkk.....",
            "....kOOooook....",
            "....kOWWWWok....",
            "....kOWrrWok....",
            "....kOrrrrok....",
            "....kOWrrWok....",
            "....kOWWWWok....",
            "....kOooooook...",
            "....kOooooook...",
            "....kOooooook...",
            ".....kkkkkkk....",
            "................",
        ],
    },
}


def png(rows: list[str]) -> bytes:
    if len(rows) != 16 or any(len(row) != 16 for row in rows):
        raise ValueError("placeholder textures are 16x16")

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    raw = b"".join(b"\x00" + b"".join(bytes(PALETTE[key]) for key in row) for row in rows)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 16, 16, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main() -> None:
    for namespace, textures in TEXTURES.items():
        for path, rows in textures.items():
            target = ROOT / namespace / "textures" / f"{path}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(png(rows))
            print(f"wrote {target.relative_to(ROOT.parent.parent)} (PLACEHOLDER)")


if __name__ == "__main__":
    main()
