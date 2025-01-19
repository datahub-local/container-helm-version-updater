import json
import unittest

from update_versions.semantic_versioning import (
    SemanticVersion,
    is_newer,
    get_last_valid_version,
    parse,
)


class TestSemanticVersioning(unittest.TestCase):

    def test_error_class(self):
        with self.assertRaises(ValueError):
            SemanticVersion("latests")

    def test_error_parse(self):
        self.assertIsNone(parse("latests"))

    def test_major_comparison(self):
        self.assertTrue(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.2.0"), "major")
        )
        self.assertTrue(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.1.0"), "major")
        )
        self.assertTrue(
            is_newer(SemanticVersion("2.0.0"),
                    SemanticVersion("1.2.3"), "major")
        )
        self.assertFalse(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.3.0"), "major")
        )

    def test_major_comparison(self):
        self.assertTrue(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.2.0"), "major")
        )
        self.assertTrue(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.1.0"), "major")
        )
        self.assertTrue(
            is_newer(SemanticVersion("2.0.0"),
                    SemanticVersion("1.2.3"), "major")
        )
        self.assertFalse(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.3.0"), "major")
        )
        self.assertFalse(
            is_newer(SemanticVersion("2"), SemanticVersion("1.2.0"), "major")
        )
        self.assertFalse(
            is_newer(SemanticVersion("1.2.3-aaa"),
                    SemanticVersion("1.2.2"), "major")
        )

    def test_minor_comparison(self):
        self.assertTrue(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.2.2"), "minor")
        )
        self.assertTrue(
            is_newer(SemanticVersion("1.4.0"),
                    SemanticVersion("1.3.2"), "minor")
        )
        self.assertFalse(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.2.4"), "minor")
        )
        self.assertFalse(
            is_newer(SemanticVersion("2.1.3"),
                    SemanticVersion("1.2.3"), "minor")
        )

    def test_patch_comparison(self):
        self.assertTrue(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.2.2"), "patch")
        )
        self.assertFalse(
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("1.2.5"), "patch")
        )

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            is_newer(SemanticVersion("1.2.3"),
                    SemanticVersion("2.3.4"), "invalid")

    def test_get_last_valid_version(self):
        versions = [
            SemanticVersion("1.2.8beta"),
            SemanticVersion("1.2.7abc"),
            SemanticVersion("1.2.3"),
            SemanticVersion("0.2.3"),
            SemanticVersion("2.3.4"),
            SemanticVersion("1.3.4"),
        ]
        self.assertEqual(
            get_last_valid_version(
                versions,
                SemanticVersion("1.2.0"),
                "major",
            ),
            SemanticVersion("2.3.4"),
        )
        self.assertEqual(
            get_last_valid_version(
                versions,
                SemanticVersion("1.2.0"),
                "minor",
            ),
            SemanticVersion("1.3.4"),
        )
        self.assertEqual(
            get_last_valid_version(
                versions,
                SemanticVersion("1.2.0"),
                "patch",
            ),
            SemanticVersion("1.2.3"),
        )
        self.assertEqual(
            get_last_valid_version(
                versions,
                SemanticVersion("1.2.0a"),
                "patch",
            ),
            SemanticVersion("1.2.7abc"),
        )


if __name__ == "__main__":
    unittest.main()
