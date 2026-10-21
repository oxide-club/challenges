"""Validate the shared, ordered challenge area registry."""

import json
from pathlib import Path
import re

KEY = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def load_areas(path: Path) -> list[dict[str, str]]:
    areas = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(areas, list) or not areas:
        raise ValueError(f"{path}: areas.json deve conter uma lista não vazia")
    ids, slugs = set(), set()
    for area in areas:
        if not isinstance(area, dict) or any(
            not isinstance(area.get(field), str) or not area[field].strip()
            for field in ("id", "slug", "title", "description")
        ):
            raise ValueError(f"{path}: campos inválidos em areas.json")
        if any(not KEY.fullmatch(area[field]) for field in ("id", "slug")):
            raise ValueError(f"{path}: id ou slug inválido em areas.json")
        if area["id"] in ids or area["slug"] in slugs:
            raise ValueError(f"{path}: id ou slug duplicado em areas.json")
        ids.add(area["id"])
        slugs.add(area["slug"])
    return areas
