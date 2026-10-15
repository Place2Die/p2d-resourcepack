"""Writes the pack as a reproducible zip: same files in, same bytes and SHA-1 out."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from p2dpack.files import pack_files

# Earliest date a zip can store: no build time leaks into the archive.
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644
UNIX = 3


class DeterministicZip:
    """Sorted entries, fixed timestamps and permissions, no directory entries, deflate level 9."""

    def write(self, root: Path, output: Path) -> str:
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w") as archive:
            for path in pack_files(root):
                info = zipfile.ZipInfo(path, FIXED_DATE_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = UNIX
                info.external_attr = FILE_MODE << 16
                archive.writestr(info, (root / path).read_bytes(), compresslevel=9)
        return sha1_of(output)


def sha1_of(file: Path) -> str:
    digest = hashlib.sha1()
    with file.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()
