#!/usr/bin/env python3
"""Generates the PLACEHOLDER 16x16 item and block textures until the real art exists.

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
    "b": (110, 74, 40, 255),     # wood
    "B": (150, 108, 62, 255),    # wood highlight
    "s": (104, 104, 108, 255),   # stone
    "S": (140, 140, 146, 255),   # stone highlight
    "l": (64, 92, 48, 255),      # leaves
    "L": (96, 128, 64, 255),     # leaves highlight
    "u": (150, 84, 48, 255),     # rust
    "U": (190, 120, 70, 255),    # rust highlight
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
    "p2d_gathering": {
        "item/wood": [
            "................",
            "................",
            "..........kkkk..",
            ".........kBBBBk.",
            "........kbBbbBk.",
            ".......kbbBbbBk.",
            "......kbbbkBBk..",
            ".....kbbbbbkk...",
            "....kbbbbbbk....",
            "...kbbbbbbk.....",
            "..kBBbbbbk......",
            ".kBbbBbbk.......",
            ".kBbbBbk........",
            "..kBBkk.........",
            "...kk...........",
            "................",
        ],
        "item/stone": [
            "................",
            "................",
            "................",
            "......kkkk......",
            "....kkSSSSkk....",
            "...kSSSsSSSSk...",
            "..kSSsSSSSsSk...",
            "..kSSSSSsSSSSk..",
            "..ksSSSsSSSSsk..",
            "..kssSSSSSsssk..",
            "...kssssSsssk...",
            "....kksssskk....",
            "......kkkk......",
            "................",
            "................",
            "................",
        ],
        "item/raw_metal": [
            "................",
            "................",
            "................",
            ".....kkkkk......",
            "....kMMmmuk.....",
            "...kMmmuummkk...",
            "..kMmmmmuUmmmk..",
            "..kmmuummmmMmk..",
            "..kmUuummmMmmk..",
            "..kmmmmmmmmuuk..",
            "...kmmuummmuk...",
            "....kkmmmmkk....",
            "......kkkk......",
            "................",
            "................",
            "................",
        ],
        "item/hatchet": [
            "................",
            "................",
            "....kkkk........",
            "...kMMmmk.......",
            "..kMmmmmbk......",
            "..kMmmmbBk......",
            "...kkkbBk.......",
            ".....kbBk.......",
            "....kbBk........",
            "...kbBk.........",
            "..kbBk..........",
            ".kbBk...........",
            ".kBk............",
            "..k.............",
            "................",
            "................",
        ],
        "item/pickaxe": [
            "................",
            "....kkkkkk......",
            "...kMMmmmmkk....",
            "..kMk..kbBmmk...",
            "..kk...kbBk.kk..",
            "......kbBk..kMk.",
            ".....kbBk....kk.",
            "....kbBk........",
            "...kbBk.........",
            "..kbBk..........",
            ".kbBk...........",
            ".kBk............",
            "..k.............",
            "................",
            "................",
            "................",
        ],
        "block/tree": [
            "llLlLLllLLlLLlLl",
            "lLlLlLlLlLlLlLlL",
            "LLllLLLLllLLLlll",
            "lllllLLlLlllLlLl",
            "LLlLLLlLlLlLLLll",
            "LllllLLLlLLlLLLl",
            "BBkbBbbbBbbbBbbb",
            "BbbbBbbbBbbbBbbb",
            "BbbbBkbbBbbbBBbb",
            "BbbbBbbbBbbbBbbk",
            "BbbbBbbbBbbbBbbb",
            "BBkbBbbbBbbbBbbb",
            "BbbbBBbbBkbbBbbb",
            "BBbbBbbbBbbbBbbb",
            "BbbbBkkbBkbbBbbb",
            "BBbbBbbbBbbbBbbb",
        ],
        "block/tree_depleted": [
            "kkkkkkkkkkkkkkkk",
            "kBBBBBBBBBBBBBBk",
            "kBbbbbbbbbbbbbBk",
            "kBbbbbbbbbbbbbBk",
            "kBbbBBBBBBBBbbBk",
            "kBbbBbbbbbbBbbBk",
            "kBbbBbbbbbbBbbBk",
            "kBbbBbbBBbbBbbBk",
            "kBbbBbbBBbbBbbBk",
            "kBbbBbbbbbbBbbBk",
            "kBbbBbbbbbbBbbBk",
            "kBbbBBBBBBBBbbBk",
            "kBbbbbbbbbbbbbBk",
            "kBbbbbbbbbbbbbBk",
            "kBBBBBBBBBBBBBBk",
            "kkkkkkkkkkkkkkkk",
        ],
        "block/tree_small": [
            "LLlLLlLLlLLlLLlL",
            "lLLlLLlLLLlLLlLL",
            "LlLLLlLLlLLLlLLl",
            "LLlLLLLlLLlLLLlL",
            "lLLLlLLLLLLlLLLL",
            "LLlLLlLLlLLLlLLl",
            "LLLLlLLLLlLLLLlL",
            "lLLLLLlLLLLlLLLL",
            "BBBbBBBBbBBBBbBB",
            "BbBBBBbBBBBbBBBB",
            "BBBBbBBBBbBBBBbB",
            "BbBBBBBbBBBBbBBB",
            "BBBbBBBBBbBBBBBb",
            "BBbBBBbBBBBbBBBB",
            "BBBBBbBBBBBBbBBB",
            "BbBBBBBBbBBBBBbB",
        ],
        "block/tree_small_depleted": [
            "................",
            "................",
            "................",
            "................",
            "....kkkkkkkk....",
            "....kBBBBBBk....",
            "....kBbbbbBk....",
            "....kBbBBbBk....",
            "....kBbBBbBk....",
            "....kBbbbbBk....",
            "....kBBBBBBk....",
            "....kkkkkkkk....",
            "................",
            "................",
            "................",
            "................",
        ],
        "block/tree_large": [
            "lllkllllllkllllk",
            "lklllllkllllklll",
            "llllklllllllllkl",
            "lllllllklllkllll",
            "kbbbbbbbbbbbbbbk",
            "bbbkbbbbbbbkbbbb",
            "bbbbbbkbbbbbbbbb",
            "bkbbbbbbbbbbkbbb",
            "bbbbbkbbbbbbbbbb",
            "bbbbbbbbbkbbbbbk",
            "bbkbbbbbbbbbbbbb",
            "bbbbbbbbkbbbbkbb",
            "bbbbkbbbbbbbbbbb",
            "bkbbbbbbbbbkbbbb",
            "bbbbbbbkbbbbbbbb",
            "bbbbbbbbbbbbbbkb",
        ],
        "block/tree_large_depleted": [
            "kkkkkkkkkkkkkkkk",
            "kbbbbbbbbbbbbbbk",
            "kbBBBBBBBBBBBBbk",
            "kbBbbbbbbbbbbBbk",
            "kbBbBBBBBBBBbBbk",
            "kbBbBbbbbbbBbBbk",
            "kbBbBbBBBBbBbBbk",
            "kbBbBbBkkBbBbBbk",
            "kbBbBbBkkBbBbBbk",
            "kbBbBbBBBBbBbBbk",
            "kbBbBbbbbbbBbBbk",
            "kbBbBBBBBBBBbBbk",
            "kbBbbbbbbbbbbBbk",
            "kbBBBBBBBBBBBBbk",
            "kbbbbbbbbbbbbbbk",
            "kkkkkkkkkkkkkkkk",
        ],
        "block/rock": [
            "SSSSSsSSSsSSssSs",
            "SSsSSSsSSssssSSS",
            "SSSsSSsSSSSSsssS",
            "SsSSSSSSSssSSSSs",
            "ssSSSSSSSSSSSSSS",
            "SSSSssSSSSSsSSSs",
            "sSSsSssSSsSSSsSS",
            "ssSSSSSSsssSSsss",
            "sSsSsSSSSSsSSsSS",
            "SSSSsSSSSsSSSSSS",
            "sSSsSsSSSSSssSSS",
            "sssSsSSsSSSSsSSS",
            "SSSSsSSSSSssSsSs",
            "SSSssSSSSSSSSsSS",
            "sSsSSSSsSSSSSSSS",
            "SSSsSSSSSSssSSSs",
        ],
        "block/rock_depleted": [
            "sssskkskssksksss",
            "ssssssksskskssss",
            "skksssskssssskss",
            "ksskskkkksskskss",
            "ssssskksksssssks",
            "skskkssskkksssss",
            "sssssskssskkksss",
            "ssksksssssssssss",
            "kkkkskksssssssss",
            "ssssssksssskskss",
            "sssssssssssssssk",
            "ssssssssskskskks",
            "sssskkssksssssss",
            "ssskssskkksssssk",
            "sssskksssskksssk",
            "kkssskkskssssssk",
        ],
        "block/ore": [
            "MSsSSssMSSsSssMm",
            "SsSSssSSSSsMSsSS",
            "SMSSSsSSMSSssssM",
            "sSsSSMmSssSSMsSS",
            "sSMmSSSsSMmSSSSs",
            "mSsSsSMmSSsSSMmS",
            "sSSSmssSSSSsSsSS",
            "MmSSsssMmSSSsSMm",
            "SSSSMmSSSSSMmSsS",
            "sMmSSsSsMSSssssM",
            "SSSSSMmSSSsSMmSs",
            "sSMSSSSSsMSSsSSS",
            "mSSSSSSmSSSSSSmS",
            "ssSMmSsSSsMSSSSS",
            "MmSSSSSMsssSsSSS",
            "SSSSMmSsSSSSmSSS",
        ],
        "block/ore_depleted": [
            "usskskkussksssss",
            "ssskuskssskussss",
            "ssssskkssssskssu",
            "ssksssksssssusss",
            "sksssskksksssssk",
            "ssssksussskssssk",
            "ssssssksssukssss",
            "ussskssssssskkkk",
            "ssksssskksssssss",
            "sussssssusksssss",
            "sskssusssssssssk",
            "ssuskssssskkksss",
            "ssssssusksskksss",
            "kkssskssssssssks",
            "skssssssksskkkss",
            "sssksssssskkssks",
        ],
    },
    "p2d_loot": {
        "block/barrel": [
            "kkkkkkkkkkkkkkkk",
            "kuUUuuuuuuuuUUuk",
            "kkkkkkkkkkkkkkkk",
            "kuUUuuuuuuuuUUuk",
            "kuUUuuuuuuuuUUuk",
            "kuUUuuuuuuuuUUuk",
            "kuUUuuuuuuuuUUuk",
            "kkkkkkkkkkkkkkkk",
            "kuUUuuuuuuuuUUuk",
            "kuUUuuuuuuuuUUuk",
            "kuUUuuuuuuuuUUuk",
            "kuUUuuuuuuuuUUuk",
            "kuUUuuuuuuuuUUuk",
            "kkkkkkkkkkkkkkkk",
            "kuUUuuuuuuuuUUuk",
            "kkkkkkkkkkkkkkkk",
        ],
        "block/crate": [
            "kkkkkkkkkkkkkkkk",
            "kBBBBBBBBBBBBBBk",
            "kBbbbbbbbbbbbbBk",
            "kBBbbbbbbbbbbBBk",
            "kBbBbbbbbbbbBbBk",
            "kBbbBbbbbbbBbbBk",
            "kBbbbBgggbBbbbBk",
            "kBbbbbBggBbbbbBk",
            "kBbbbbBggBbbbbBk",
            "kBbbbBgggbBbbbBk",
            "kBbbBbbbbbbBbbBk",
            "kBbBbbbbbbbbBbBk",
            "kBBbbbbbbbbbbBBk",
            "kBbbbbbbbbbbbbBk",
            "kBBBBBBBBBBBBBBk",
            "kkkkkkkkkkkkkkkk",
        ],
    },
    "p2d_building": {
        "block/tool_cupboard": [
            "kkkkkkkkkkkkkkkk",
            "kBBBBBBBBBBBBBBk",
            "kBbbbbbkkbbbbbBk",
            "kBbmmbbkkbbmmbBk",
            "kBbmmbbkkbbmmbBk",
            "kBbbbbbkkbbbbbBk",
            "kBbbbbbkkbbbbbBk",
            "kBbbbbMkkMbbbbBk",
            "kBbbbbMkkMbbbbBk",
            "kBbbbbbkkbbbbbBk",
            "kBbbbbbkkbbbbbBk",
            "kBbmmbbkkbbmmbBk",
            "kBbmmbbkkbbmmbBk",
            "kBbbbbbkkbbbbbBk",
            "kBBBBBBBBBBBBBBk",
            "kkkkkkkkkkkkkkkk",
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
