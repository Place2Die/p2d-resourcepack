import os
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

from p2dpack.archive import FIXED_DATE_TIME, DeterministicZip
from tests.testing.packs import PackFixture, png


class DeterministicZipTest(unittest.TestCase):
    def setUp(self):
        output = tempfile.TemporaryDirectory()
        self.addCleanup(output.cleanup)
        self.output = Path(output.name)

    def pack(self, name: str, reverse: bool) -> Path:
        files = [("pack.mcmeta", '{"pack": {}}'), ("assets/a/items/x.json", "{}"),
                 ("assets/b/textures/item/y.png", png()), ("assets/a/models/item/x.json", "{}")]
        fixture = PackFixture.temporary(self, name)
        for path, content in reversed(files) if reverse else files:
            fixture.raw(path, content)
            time.sleep(0.01)
        return fixture.root

    def test_same_files_give_the_same_sha1(self):
        first = self.pack("first", reverse=False)
        second = self.pack("second", reverse=True)
        os.utime(second / "pack.mcmeta", (1_000_000, 1_000_000))
        sha_first = DeterministicZip().write(first, self.output / "first.zip")
        sha_second = DeterministicZip().write(second, self.output / "second.zip")
        self.assertEqual(sha_first, sha_second)
        self.assertEqual((self.output / "first.zip").read_bytes(), (self.output / "second.zip").read_bytes())

    def test_a_content_change_changes_the_sha1(self):
        root = self.pack("pack", reverse=False)
        before = DeterministicZip().write(root, self.output / "before.zip")
        (root / "assets/a/items/x.json").write_text('{"model": {}}')
        self.assertNotEqual(before, DeterministicZip().write(root, self.output / "after.zip"))

    def test_entries_are_sorted_files_with_fixed_metadata(self):
        root = self.pack("pack", reverse=True)
        DeterministicZip().write(root, self.output / "pack.zip")
        with zipfile.ZipFile(self.output / "pack.zip") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            self.assertEqual(sorted(names), names)
            self.assertEqual(4, len(names))
            for info in infos:
                self.assertEqual(FIXED_DATE_TIME, info.date_time)
                self.assertEqual(0o100644, info.external_attr >> 16)
                self.assertEqual(zipfile.ZIP_DEFLATED, info.compress_type)
            self.assertEqual(png(), archive.read("assets/b/textures/item/y.png"))

    def test_the_sha1_is_the_file_sha1(self):
        import hashlib
        root = self.pack("pack", reverse=False)
        sha1 = DeterministicZip().write(root, self.output / "pack.zip")
        self.assertEqual(hashlib.sha1((self.output / "pack.zip").read_bytes()).hexdigest(), sha1)


if __name__ == "__main__":
    unittest.main()
