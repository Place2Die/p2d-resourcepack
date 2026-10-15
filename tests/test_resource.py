import unittest
from pathlib import Path

from p2dpack.resource import ResourceLocation


class ResourceLocationTest(unittest.TestCase):
    def test_a_bare_path_is_vanilla(self):
        location = ResourceLocation.parse("item/generated")
        self.assertEqual(ResourceLocation("minecraft", "item/generated"), location)
        self.assertTrue(location.is_vanilla)

    def test_a_namespaced_id_keeps_its_namespace(self):
        location = ResourceLocation.parse("p2d_survival:item/canteen")
        self.assertEqual("p2d_survival", location.namespace)
        self.assertFalse(location.is_vanilla)

    def test_uppercase_is_invalid(self):
        self.assertFalse(ResourceLocation.parse("P2D:item/canteen").is_valid)
        self.assertFalse(ResourceLocation.parse("p2d:item/Canteen").is_valid)
        self.assertTrue(ResourceLocation.parse("p2d_survival:item/canteen-2.v1").is_valid)

    def test_file_resolves_under_assets(self):
        location = ResourceLocation.parse("p2d_survival:item/canteen")
        self.assertEqual(Path("root/assets/p2d_survival/textures/item/canteen.png"),
                         location.file(Path("root"), "textures", ".png"))


if __name__ == "__main__":
    unittest.main()
