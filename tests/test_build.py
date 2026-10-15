import tempfile
import unittest
import zipfile
from pathlib import Path

from p2dpack.build import ARCHIVE_NAME, BuildError, PackBuilder
from p2dpack.merge import MergeError
from tests.testing.packs import PackFixture

REPOSITORY_PACK = Path(__file__).resolve().parent.parent / "pack"


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.ours = PackFixture.temporary(self, "ours").mcmeta().item("p2d_survival", "canteen")
        self.bettermodel = PackFixture.temporary(self, "bettermodel").item("bettermodel", "walker")
        output = tempfile.TemporaryDirectory()
        self.addCleanup(output.cleanup)
        self.output = Path(output.name)

    def test_build_writes_the_zip_and_its_sha1(self):
        result = PackBuilder.default().build(self.ours.root, self.output)
        self.assertEqual(self.output / ARCHIVE_NAME, result.archive)
        self.assertEqual(f"{result.sha1}  {ARCHIVE_NAME}\n",
                         (self.output / (ARCHIVE_NAME + ".sha1")).read_text())
        self.assertIsNone(result.merge)

    def test_build_merges_bettermodel(self):
        result = PackBuilder.default().build(self.ours.root, self.output, self.bettermodel.root)
        with zipfile.ZipFile(result.archive) as archive:
            names = archive.namelist()
        self.assertIn("assets/bettermodel/items/walker.json", names)
        self.assertIn("assets/p2d_survival/items/canteen.json", names)

    def test_an_invalid_source_stops_the_build(self):
        self.ours.raw("assets/p2d_survival/items/broken.json", "{")
        with self.assertRaises(BuildError) as raised:
            PackBuilder.default().build(self.ours.root, self.output)
        self.assertEqual("source pack", raised.exception.stage)
        self.assertFalse((self.output / ARCHIVE_NAME).exists())

    def test_an_invalid_bettermodel_part_stops_the_build(self):
        (self.bettermodel.root / "assets/bettermodel/textures/item/walker.png").unlink()
        with self.assertRaises(BuildError) as raised:
            PackBuilder.default().build(self.ours.root, self.output, self.bettermodel.root)
        self.assertEqual("merged pack", raised.exception.stage)

    def test_a_conflict_stops_the_build(self):
        self.bettermodel.json("assets/p2d_survival/items/canteen.json", {"model": {}})
        with self.assertRaises(MergeError):
            PackBuilder.default().build(self.ours.root, self.output, self.bettermodel.root)

    def test_the_repository_pack_builds_reproducibly(self):
        first = PackBuilder.default().build(REPOSITORY_PACK, self.output / "first")
        second = PackBuilder.default().build(REPOSITORY_PACK, self.output / "second")
        self.assertEqual([], first.source_report.issues)
        self.assertEqual(first.sha1, second.sha1)


if __name__ == "__main__":
    unittest.main()
