"""Listing the files of a pack, shared by the validator, the merger and the zip writer."""

from __future__ import annotations

from pathlib import Path

# OS clutter that never belongs in a shipped pack.
IGNORED_FILE_NAMES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini"})


def pack_files(root: Path) -> list[str]:
    """Every file under ``root`` as a sorted list of POSIX relative paths, clutter excluded."""
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name not in IGNORED_FILE_NAMES
    )
