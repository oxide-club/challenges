from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class Catalogue(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def definition(self, directory, slug):
        path = self.root / directory
        path.mkdir()
        (path / "index.md").write_text(f"---\ntitle: 'Example'\nslug: '{slug}'\n---\n")

    def check(self):
        return subprocess.run(
            [sys.executable, str(ROOT / "tools/check_catalog.py"), str(self.root)],
            capture_output=True, text=True,
        )

    def test_matching_ids_pass(self):
        self.definition("001-wc", "001-wc")
        self.definition("002-ppm", "002-ppm")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mismatched_slug_fails(self):
        self.definition("001-wc", "recriando-wc")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("slug", result.stderr)

    def test_duplicate_number_fails(self):
        self.definition("001-wc", "001-wc")
        self.definition("001-other", "001-other")
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicado", result.stderr)

    def test_invalid_identifiers_fail(self):
        for identifier in ("000-zero", "01-short", "003-UPPER", "003-two--words"):
            with self.subTest(identifier=identifier):
                self.definition(identifier, identifier)
                result = self.check()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("identificador", result.stderr)

    def test_empty_catalogue_fails(self):
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Nenhum", result.stderr)


if __name__ == "__main__":
    unittest.main()
