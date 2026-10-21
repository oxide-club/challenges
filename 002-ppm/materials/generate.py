"""Build the specified P6 image and both public runner vectors."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    image = b"P6\n256 256\n255\n" + bytes(channel for y in range(256) for x in range(256) for channel in (x, y, 0))
    (HERE / "gradient.ppm").write_bytes(image)
    cases = [
        dict(id="image", name="Header, length and all 65536 pixels", argv=[], stdin_hex="", stdout_hex=image.hex()),
        dict(id="write-error", name="Write error on /dev/full", argv=[], stdin_hex="", reject=True, io="full"),
    ]
    (HERE.parent / "tests/cases.json").write_text(json.dumps(dict(schema_version=1, cases=cases), indent=2) + "\n")


if __name__ == "__main__":
    import argparse
    import tempfile

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare regenerated artifacts without changing files")
    args = parser.parse_args()
    if args.check:
        original = HERE
        with tempfile.TemporaryDirectory(prefix="oxide-vectors-") as temporary:
            HERE = Path(temporary) / "materials"
            HERE.mkdir()
            (HERE.parent / "tests").mkdir()
            main()
            for generated in HERE.parent.rglob("*"):
                if generated.is_file():
                    committed = original.parent / generated.relative_to(HERE.parent)
                    if not committed.is_file() or committed.read_bytes() != generated.read_bytes():
                        parser.exit(1, f"Outdated artifact: {committed}\n")
        print("Generated artifacts are current")
    else:
        main()
