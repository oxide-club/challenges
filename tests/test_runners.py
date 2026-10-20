"""Exercise the public CLIs; fixture players here are not challenge solutions."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicRunners(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="candidate with spaces ")
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)

    def candidate(self, body):
        path = self.work / "participant program"
        path.write_text(f"#!{sys.executable}\n" + body)
        path.chmod(0o755)
        return path

    def run_suite(self, challenge, program, timeout="2"):
        return subprocess.run(
            [sys.executable, str(ROOT / challenge / "tests/test.py"),
             str(program), "--timeout", timeout],
            cwd=self.work, capture_output=True, text=True, timeout=30,
        )

    def assert_rejected(self, result, diagnostic):
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(diagnostic, result.stdout + result.stderr)

    def wc_fixture_player(self, transform="output"):
        # Literal examples and the explicitly specified generated stress fixture.
        pairs = [
            (b"", b"0 0 0\n"), (b"hello", b"0 1 5\n"),
            (b"hello\n", b"1 1 6\n"), (b"a b\n", b"1 2 4\n"),
            (b"a\nb", b"1 2 3\n"), (b"one   two\n", b"1 2 10\n"),
            (b" \t\n\r\v\f", b"1 0 6\n"), (b"\r\n", b"1 0 2\n"),
            (b"Hello world\nC is fun\n", b"2 5 21\n"),
            (b"\talpha\vbeta\fgamma\rdelta epsilon\n", b"1 5 32\n"),
            (b"   a  b   ", b"0 2 10\n"),
            (b"x" * 131072, b"0 1 131072\n"),
            (b"a b\n" * 32768, b"32768 65536 131072\n"),
        ]
        mapping = {data.hex(): output.decode() for data, output in pairs}
        data_file = self.work / "responses.json"
        data_file.write_text(json.dumps(mapping))
        return self.candidate(
            "import json, sys\n"
            f"responses = json.load(open({str(data_file)!r}))\n"
            "output = responses[sys.stdin.buffer.read().hex()].encode()\n"
            f"sys.stdout.buffer.write({transform})\n"
        )

    def ppm_fixture_player(self, mutation=None, ignore_errors=False, silent=False):
        # Materialize fixed test output; candidate only copies it.
        pixels = bytearray(196608)
        for row in range(256):
            start = row * 768
            pixels[start:start + 768:3] = bytes(range(256))
            pixels[start + 1:start + 768:3] = bytes([row]) * 256
        output = b"P6\n256 256\n255\n" + pixels
        if mutation:
            output = mutation(output)
        data_file = self.work / "image fixture"
        data_file.write_bytes(output)
        return self.candidate(
            "import sys\n"
            "try:\n"
            f"    sys.stdout.buffer.write(open({str(data_file)!r}, 'rb').read())\n"
            "    sys.stdout.buffer.flush()\n"
            "except OSError:\n"
            "    import os\n"
            + ("" if silent else "    os.write(2, b'write failed\\n')\n")
            + f"    os._exit({0 if ignore_errors else 1})\n"
        )

    def test_wc_accepts_exact_output_and_relative_path_with_spaces(self):
        candidate = self.wc_fixture_player()
        result = self.run_suite("001-wc", candidate.name)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wc_fixtures_match_unix_oracle(self):
        import os
        for path in sorted((ROOT / "001-wc/fixtures").glob("*.in")):
            with self.subTest(fixture=path.name):
                result = subprocess.run(
                    ["wc", "-l", "-w", "-c"], input=path.read_bytes(),
                    capture_output=True, timeout=5,
                    env={**os.environ, "LC_ALL": "C"},
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    list(map(int, result.stdout.split())),
                    list(map(int, path.with_suffix(".out").read_bytes().split())),
                )

    def test_wc_rejects_wrong_counts(self):
        self.assert_rejected(
            self.run_suite("001-wc", self.candidate("print('0 0 0')\n")),
            "FAIL",
        )

    def test_wc_rejects_missing_newline(self):
        self.assert_rejected(
            self.run_suite("001-wc", self.wc_fixture_player("output.rstrip(b'\\n')")),
            "FAIL",
        )

    def test_wc_rejects_alignment_spaces(self):
        self.assert_rejected(
            self.run_suite("001-wc", self.wc_fixture_player("b' ' + output")),
            "FAIL",
        )

    def test_nonzero_exit_is_not_success(self):
        candidate = self.wc_fixture_player()
        with candidate.open("a") as stream:
            stream.write("sys.exit(1)\n")
        self.assert_rejected(self.run_suite("001-wc", candidate), "FAIL")

    def test_ppm_accepts_fixed_image(self):
        result = self.run_suite("002-ppm", self.ppm_fixture_player())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ppm_rejects_header(self):
        candidate = self.ppm_fixture_player(lambda data: b"P3" + data[2:])
        self.assert_rejected(self.run_suite("002-ppm", candidate), "FAIL")

    def test_ppm_rejects_interior_pixel(self):
        candidate = self.ppm_fixture_player(
            lambda data: data[:90000] + bytes([data[90000] ^ 1]) + data[90001:]
        )
        self.assert_rejected(self.run_suite("002-ppm", candidate), "FAIL")

    def test_ppm_rejects_extra_bytes(self):
        candidate = self.ppm_fixture_player(lambda data: data + b"\n")
        self.assert_rejected(self.run_suite("002-ppm", candidate), "FAIL")

    def test_ppm_rejects_truncated_output(self):
        candidate = self.ppm_fixture_player(lambda data: data[:-1])
        self.assert_rejected(self.run_suite("002-ppm", candidate), "FAIL")

    @unittest.skipUnless(Path("/dev/full").exists(), "Linux /dev/full unavailable")
    def test_ppm_rejects_success_after_write_error(self):
        self.assert_rejected(
            self.run_suite("002-ppm", self.ppm_fixture_player(ignore_errors=True)),
            "FAIL",
        )

    @unittest.skipUnless(Path("/dev/full").exists(), "Linux /dev/full unavailable")
    def test_ppm_requires_write_error_diagnostic(self):
        self.assert_rejected(
            self.run_suite("002-ppm", self.ppm_fixture_player(silent=True)), "FAIL",
        )

    def test_timeout_fails_instead_of_hanging(self):
        candidate = self.candidate("import time\ntime.sleep(60)\n")
        self.assert_rejected(self.run_suite("002-ppm", candidate, "0.1"), "tempo")

    def test_missing_executable_is_reported(self):
        self.assert_rejected(
            self.run_suite("001-wc", self.work / "absent"), "executável",
        )

    def test_nonexecutable_file_is_reported(self):
        candidate = self.candidate("pass\n")
        candidate.chmod(0o644)
        self.assert_rejected(self.run_suite("001-wc", candidate), "executável")

    def test_invalid_timeout_is_rejected(self):
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(value=value):
                self.assert_rejected(
                    self.run_suite("002-ppm", self.ppm_fixture_player(), value),
                    "timeout",
                )


if __name__ == "__main__":
    unittest.main()
