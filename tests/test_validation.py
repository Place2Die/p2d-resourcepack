import unittest

from p2dpack.report import Report
from p2dpack.validation import PackValidator
from tests.testing.packs import PackFixture, png


class ValidationTest(unittest.TestCase):
    def setUp(self):
        self.pack = PackFixture.temporary(self).mcmeta().item("p2d_survival", "canteen")

    def validate(self) -> Report:
        return PackValidator.default().validate(self.pack.root)

    def assertError(self, report: Report, path: str, fragment: str):
        matching = [issue for issue in report.errors if issue.path == path and fragment in issue.message]
        self.assertTrue(matching, f"no error on {path} containing {fragment!r} in {report.messages()}")

    def test_a_complete_item_is_valid(self):
        report = self.validate()
        self.assertTrue(report.ok, report.messages())
        self.assertEqual([], report.warnings)

    def test_missing_directory(self):
        report = PackValidator.default().validate(self.pack.root / "nope")
        self.assertFalse(report.ok)

    # pack.mcmeta

    def test_missing_mcmeta(self):
        (self.pack.root / "pack.mcmeta").unlink()
        self.assertError(self.validate(), "pack.mcmeta", "missing")

    def test_format_range_must_include_26_2(self):
        self.pack.mcmeta(min_format=75, max_format=84)
        self.assertError(self.validate(), "pack.mcmeta", "does not include 88")

    def test_format_accepts_major_minor_lists(self):
        self.pack.mcmeta(min_format=[88, 0], max_format=[88, 0])
        self.assertTrue(self.validate().ok)

    def test_legacy_pack_format_alone_is_rejected(self):
        self.pack.json("pack.mcmeta", {"pack": {"description": "old", "pack_format": 46}})
        self.assertError(self.validate(), "pack.mcmeta", "min_format")

    def test_min_above_max(self):
        self.pack.mcmeta(min_format=90, max_format=88)
        self.assertError(self.validate(), "pack.mcmeta", "above max_format")

    # JSON

    def test_invalid_json(self):
        self.pack.raw("assets/p2d_survival/models/item/canteen.json", '{"parent": "item/generated",}')
        self.assertError(self.validate(), "assets/p2d_survival/models/item/canteen.json", "invalid JSON")

    def test_duplicate_keys(self):
        self.pack.raw("assets/p2d_survival/items/canteen.json",
                      '{"model": {"type": "model", "model": "p2d_survival:item/canteen"}, "model": {}}')
        self.assertError(self.validate(), "assets/p2d_survival/items/canteen.json", "duplicate key")

    def test_invalid_texture_mcmeta(self):
        self.pack.raw("assets/p2d_survival/textures/item/canteen.png.mcmeta", "{animation: {}}")
        self.assertError(self.validate(), "assets/p2d_survival/textures/item/canteen.png.mcmeta", "invalid JSON")

    # Naming

    def test_uppercase_namespace(self):
        self.pack.item("P2D_Loot", "crate")
        self.assertError(self.validate(), "assets/P2D_Loot/items/crate.json", "invalid namespace")

    def test_uppercase_path(self):
        self.pack.raw("assets/p2d_survival/textures/item/Bandage.png", png())
        self.assertError(self.validate(), "assets/p2d_survival/textures/item/Bandage.png", "invalid asset path")

    def test_file_outside_assets(self):
        self.pack.raw("notes.txt", "hello")
        self.assertError(self.validate(), "notes.txt", "outside assets/")

    def test_os_clutter_is_ignored(self):
        self.pack.raw("assets/p2d_survival/.DS_Store", b"\x00")
        self.assertTrue(self.validate().ok)

    # Item definitions

    def test_item_pointing_to_a_missing_model(self):
        self.pack.json("assets/p2d_survival/items/bandage.json",
                       {"model": {"type": "minecraft:model", "model": "p2d_survival:item/bandage"}})
        self.assertError(self.validate(), "assets/p2d_survival/items/bandage.json",
                         "assets/p2d_survival/models/item/bandage.json")

    def test_item_without_model(self):
        self.pack.json("assets/p2d_survival/items/bandage.json", {"hand_animation_on_swap": False})
        self.assertError(self.validate(), "assets/p2d_survival/items/bandage.json", "needs a \"model\"")

    def test_nested_select_cases_are_checked(self):
        self.pack.json("assets/p2d_survival/items/canteen.json", {"model": {
            "type": "minecraft:select", "property": "minecraft:custom_model_data",
            "cases": [{"when": "full", "model": {"type": "model", "model": "p2d_survival:item/canteen_full"}}],
            "fallback": {"type": "minecraft:model", "model": "p2d_survival:item/canteen"}}})
        report = self.validate()
        self.assertError(report, "assets/p2d_survival/items/canteen.json", "p2d_survival:item/canteen_full")
        self.assertEqual(1, len(report.errors), report.messages())

    def test_special_model_base_is_checked(self):
        self.pack.json("assets/p2d_survival/items/canteen.json", {"model": {
            "type": "minecraft:special", "base": "p2d_survival:item/missing",
            "model": {"type": "minecraft:head", "kind": "zombie"}}})
        self.assertError(self.validate(), "assets/p2d_survival/items/canteen.json", "p2d_survival:item/missing")

    def test_vanilla_models_are_trusted(self):
        self.pack.json("assets/p2d_survival/items/canteen.json",
                       {"model": {"type": "minecraft:model", "model": "item/potion"}})
        self.assertTrue(self.validate().ok)

    def test_model_reference_must_be_a_string(self):
        self.pack.json("assets/p2d_survival/items/canteen.json", {"model": {"type": "model", "model": 3}})
        self.assertError(self.validate(), "assets/p2d_survival/items/canteen.json", "must be a string")

    # Models

    def test_model_with_a_missing_texture(self):
        (self.pack.root / "assets/p2d_survival/textures/item/canteen.png").unlink()
        self.assertError(self.validate(), "assets/p2d_survival/models/item/canteen.json",
                         "assets/p2d_survival/textures/item/canteen.png")

    def test_model_with_a_missing_parent(self):
        self.pack.json("assets/p2d_survival/models/item/canteen.json",
                       {"parent": "p2d_survival:item/base_flask", "textures": {"layer0": "p2d_survival:item/canteen"}})
        self.assertError(self.validate(), "assets/p2d_survival/models/item/canteen.json", "parent model")

    def test_sprite_objects_and_variable_references(self):
        self.pack.json("assets/p2d_survival/models/item/canteen.json", {
            "parent": "item/generated",
            "textures": {"layer0": {"sprite": "p2d_survival:item/canteen"}, "particle": "#layer0"}})
        self.assertTrue(self.validate().ok, self.validate().messages())

    def test_texture_outside_the_atlas_folders_warns(self):
        self.pack.json("assets/p2d_survival/models/item/canteen.json",
                       {"parent": "item/generated", "textures": {"layer0": "p2d_survival:misc/canteen"}})
        self.pack.raw("assets/p2d_survival/textures/misc/canteen.png", png())
        report = self.validate()
        self.assertTrue(report.ok)
        self.assertEqual(1, len(report.warnings), report.messages())

    # Textures

    def test_a_png_that_is_not_a_png(self):
        self.pack.raw("assets/p2d_survival/textures/item/canteen.png", b"GIF89a....")
        self.assertError(self.validate(), "assets/p2d_survival/textures/item/canteen.png", "not a PNG")


if __name__ == "__main__":
    unittest.main()
