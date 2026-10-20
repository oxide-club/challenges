#!/usr/bin/env python3
"""Check only identity conventions; the website owns the full Astro schema."""

from pathlib import Path
import re
import sys

IDENTIFIER = re.compile(r"(?!000-)[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*")
SLUG = re.compile(r"""^slug:\s*(?:'([^']+)'|"([^"]+)"|([a-z0-9-]+))[ \t]*$""", re.M)


def check(root):
    definitions = sorted(root.glob("*/index.md"))
    if not definitions:
        raise ValueError("Nenhum desafio encontrado")
    numbers = set()
    for path in definitions:
        identifier = path.parent.name
        if not IDENTIFIER.fullmatch(identifier):
            raise ValueError(f"identificador inválido: {identifier}")
        number = identifier.split("-", 1)[0]
        if number in numbers:
            raise ValueError(f"Número duplicado: {number}")
        numbers.add(number)
        text = path.read_text()
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            raise ValueError(f"Frontmatter ausente: {path}")
        slugs = SLUG.findall(parts[1])
        if len(slugs) != 1 or next(filter(None, slugs[0]), "") != identifier:
            raise ValueError(f"slug deve corresponder a {identifier}")
    return len(definitions)


if __name__ == "__main__":
    try:
        root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
        print(f"{check(root)} desafios: identificadores válidos")
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
