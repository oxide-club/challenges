import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from challenge_areas import load_areas
from check_catalog import check

AREA = {"id": "memory", "slug": "memoria-e-alocacao", "title": "Memória e alocação", "description": "Explore alocação."}


class ChallengeAreas(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.registry = self.root / "areas.json"
        self.write_areas([AREA])
        self.definition = self.root / "001-example" / "index.md"
        self.definition.parent.mkdir()
        self.write_definition("area: memory")

    def write_areas(self, values):
        self.registry.write_text(json.dumps(values), encoding="utf-8")

    def write_definition(self, area):
        self.definition.write_text(f"---\ntitle: Example\nslug: 001-example\ndraft: true\n{area}\n---\n", encoding="utf-8")

    def test_valid_registry_and_reference_including_quoted_area(self):
        self.assertEqual(load_areas(self.registry), [AREA])
        for area in ["memory", "'memory'", '"memory"']:
            with self.subTest(area=area):
                self.write_definition(f"area: {area}")
                self.assertEqual(check(self.root), 1)

    def test_missing_registry(self):
        self.registry.unlink()
        with self.assertRaisesRegex((ValueError, OSError), "areas.json"):
            check(self.root)

    def test_invalid_registry(self):
        for values in [[], {}, [None], [{**AREA, "title": " "}], [{**AREA, "id": "../memory"}], [{**AREA, "slug": "Bad"}], [AREA, AREA], [AREA, {**AREA, "id": "other"}], [AREA, {**AREA, "slug": "other"}]]:
            with self.subTest(values=values):
                self.write_areas(values)
                with self.assertRaisesRegex(ValueError, "areas.json"):
                    load_areas(self.registry)

    def test_missing_duplicate_unknown_or_nonscalar_area_even_for_drafts(self):
        for area in ["", "area: missing", "area: [memory]", "area: memory\narea: memory", "area: null", "area:\n  - memory"]:
            with self.subTest(area=area):
                self.write_definition(area)
                with self.assertRaisesRegex(ValueError, "001-example.*area"):
                    check(self.root)

    def test_order_is_editorial(self):
        other = {**AREA, "id": "algorithms", "slug": "algoritmos"}
        self.write_areas([other, AREA])
        self.assertEqual([a["id"] for a in load_areas(self.registry)], ["algorithms", "memory"])
