import tempfile
import unittest
import zipfile
from pathlib import Path

from p2dpack.merge import MergeError, PackMerger
from tests.testing.packs import PackFixture, png


class MergeTest(unittest.TestCase):
    def setUp(self):
        self.ours = PackFixture.temporary(self, "ours").mcmeta().item("p2d_survival", "canteen")
        self.bettermodel = PackFixture.temporary(self, "bettermodel")
        self.bettermodel.json("pack.mcmeta", {"pack": {"description": "BetterModel", "pack_format": 46}})
        self.bettermodel.raw("pack.png", png())
        self.bettermodel.json("assets/bettermodel/models/item/walker_head.json", {"parent": "item/generated"})
        self.bettermodel.raw("assets/bettermodel/textures/item/walker.png", png(32, 32))
        output = tempfile.TemporaryDirectory()
        self.addCleanup(output.cleanup)
        self.output = Path(output.name) / "merged"

    def merge(self, extra: Path | None = None):
        return PackMerger().merge(self.ours.root, extra or self.bettermodel.root, self.output)

    def test_assets_are_added_next_to_ours(self):
        result = self.merge()
        self.assertEqual(["assets/bettermodel/models/item/walker_head.json",
                          "assets/bettermodel/textures/item/walker.png"], result.added)
        self.assertTrue((self.output / "assets/p2d_survival/items/canteen.json").is_file())
        self.assertTrue((self.output / "assets/bettermodel/textures/item/walker.png").is_file())

    def test_our_pack_mcmeta_wins(self):
        result = self.merge()
        self.assertEqual(["pack.mcmeta", "pack.png"], result.replaced_root_files)
        self.assertEqual((self.ours.root / "pack.mcmeta").read_bytes(), (self.output / "pack.mcmeta").read_bytes())
        self.assertFalse((self.output / "pack.png").exists())

    def test_a_conflicting_file_fails_the_merge(self):
        self.bettermodel.json("assets/p2d_survival/items/canteen.json", {"model": {"type": "model", "model": "x:y"}})
        with self.assertRaises(MergeError) as raised:
            self.merge()
        self.assertEqual(["assets/p2d_survival/items/canteen.json: conflict, both packs ship this file "
                          "with different content"], raised.exception.problems)

    def test_every_conflict_is_reported(self):
        self.bettermodel.raw("assets/p2d_survival/textures/item/canteen.png", png(rgba=(0, 0, 0, 255)))
        self.bettermodel.raw("assets/p2d_survival/models/item/canteen.json", "{}")
        with self.assertRaises(MergeError) as raised:
            self.merge()
        self.assertEqual(2, len(raised.exception.problems))

    def test_an_identical_file_is_not_a_conflict(self):
        self.bettermodel.raw("assets/p2d_survival/textures/item/canteen.png",
                             (self.ours.root / "assets/p2d_survival/textures/item/canteen.png").read_bytes())
        result = self.merge()
        self.assertEqual(["assets/p2d_survival/textures/item/canteen.png"], result.identical)

    def test_overlay_folders_fail_the_merge(self):
        self.bettermodel.raw("bettermodel_legacy/assets/minecraft/models/item/leather_horse_armor.json", "{}")
        with self.assertRaises(MergeError) as raised:
            self.merge()
        self.assertIn("generate-legacy-model", raised.exception.problems[0])

    def test_a_zip_is_merged_like_a_folder(self):
        archive = self.output.parent / "bettermodel.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("pack.mcmeta", "{}")
            zip_file.writestr("assets/", "")
            zip_file.writestr("assets/bettermodel/textures/item/walker.png", png())
            zip_file.writestr("assets/bettermodel/.DS_Store", b"\x00")
        result = self.merge(archive)
        self.assertEqual(["assets/bettermodel/textures/item/walker.png"], result.added)

    def test_a_zip_cannot_escape_the_output(self):
        archive = self.output.parent / "evil.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("assets/../../escaped.txt", "x")
        with self.assertRaises(MergeError) as raised:
            self.merge(archive)
        self.assertIn("unsafe path", raised.exception.problems[0])
        self.assertFalse((self.output.parent / "escaped.txt").exists())

    def test_a_missing_input_fails(self):
        with self.assertRaises(MergeError):
            self.merge(self.output.parent / "nope")

    def test_merging_twice_starts_from_a_clean_output(self):
        self.merge()
        (self.bettermodel.root / "assets/bettermodel/textures/item/walker.png").unlink()
        self.merge()
        self.assertFalse((self.output / "assets/bettermodel/textures/item/walker.png").exists())


if __name__ == "__main__":
    unittest.main()
