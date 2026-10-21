"""The data-driven runner must test candidates, not merely load fixtures."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.vector_runner import load_cases, check_case


class Vectors(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.document = {"schema_version": 1, "cases": [{
            "id": "binary", "name": "Bytes including NUL", "argv": [],
            "stdin_hex": "00ff0a", "stdout_hex": "00ff0a",
        }]}

    def load(self, document=None):
        path = self.root / "cases.json"
        path.write_text(json.dumps(document or self.document))
        return load_cases(path)

    def candidate(self, body):
        path = self.root / "candidate with spaces"
        path.write_text("#!/usr/bin/env python3\n" + body + "\n")
        path.chmod(0o755)
        return path

    def test_binary_exact_output_and_wrong_output(self):
        case = self.load()[0]
        check_case(case, self.candidate("import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"), 2)
        with self.assertRaises(AssertionError):
            check_case(case, self.candidate("print('wrong')"), 2)

    def test_input_file_is_temporary_and_not_also_stdin(self):
        self.document["cases"][0].update(input_file=True, argv=["{input}"])
        program = self.candidate("import sys; from pathlib import Path\n"
                                 "assert sys.stdin.buffer.read() == b''\n"
                                 "sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())")
        check_case(self.load()[0], program, 2)

    def test_rejection_requires_failure_and_diagnostic(self):
        case = self.document["cases"][0]
        del case["stdout_hex"]
        case["reject"] = True
        loaded = self.load()[0]
        check_case(loaded, self.candidate("import sys; print('bad input', file=sys.stderr); sys.exit(1)"), 2)
        for body in ("pass", "raise SystemExit(1)", "import sys; sys.stderr.write(' \\v\\n'); sys.exit(1)"):
            with self.subTest(body=body), self.assertRaises(AssertionError):
                check_case(loaded, self.candidate(body), 2)

    def test_trace_is_compared_when_requested(self):
        self.document["cases"][0]["stderr_hex"] = b"trace\n".hex()
        program = self.candidate("import sys; sys.stdout.buffer.write(sys.stdin.buffer.read()); print('trace', file=sys.stderr)")
        check_case(self.load()[0], program, 2)
        with self.assertRaises(AssertionError):
            check_case(self.load()[0], self.candidate("import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"), 2)

    def test_roundtrip_checks_encoding_then_actual_decoded_output(self):
        self.document["cases"][0].update(
            argv=["encode"], stdout_hex="01fe0b", roundtrip_argv=["decode"])
        transform = "import sys\ndata=sys.stdin.buffer.read()\n"
        correct = self.candidate(transform + "sys.stdout.buffer.write(bytes(b ^ 1 for b in data))")
        check_case(self.load()[0], correct, 2)
        # Paired but wrong transformations must fail the independent encoding.
        identity = self.candidate(transform + "sys.stdout.buffer.write(data)")
        with self.assertRaises(AssertionError):
            check_case(self.load()[0], identity, 2)
        broken_decode = self.candidate(transform +
            "sys.stdout.buffer.write(bytes(b ^ 1 for b in data) if sys.argv[1]=='encode' else data)")
        with self.assertRaises(AssertionError):
            check_case(self.load()[0], broken_decode, 2)

    def test_roundtrip_limits_apply_to_second_invocation(self):
        self.document["cases"][0].update(
            argv=["encode"], roundtrip_argv=["decode"])
        for action, diagnostic in [("import time; time.sleep(5)", "tempo"),
                                   ("sys.stdout.buffer.write(b'x' * 10000)", "Limite de saída"),
                                   ("sys.exit(1)", "Status")]:
            with self.subTest(action=action):
                program = self.candidate("import sys\ndata=sys.stdin.buffer.read()\n"
                    "if sys.argv[1]=='encode': sys.stdout.buffer.write(data)\n"
                    f"else: {action}")
                with self.assertRaisesRegex(AssertionError, diagnostic):
                    check_case(self.load()[0], program, 0.2)

    def test_ppm_mismatch_names_pixel_and_channel(self):
        expected = b"P6\n2 1\n255\n" + b"\x00" * 6
        self.document["cases"][0].update(stdin_hex="", stdout_hex=expected.hex())
        changed = expected[:-1] + bytes([1])
        program = self.candidate(f"import sys; sys.stdout.buffer.write({changed!r})")
        with self.assertRaisesRegex(AssertionError, r"Pixel \(1, 0\), channel B"):
            check_case(self.load()[0], program, 2)

    def test_invalid_schema_is_rejected_before_execution(self):
        mutations = [
            lambda d: d.update(schema_version=2),
            lambda d: d.update(schema_version=True),
            lambda d: d.update(cases=[]),
            lambda d: d["cases"].append(copy.deepcopy(d["cases"][0])),
            lambda d: d["cases"][0].update(stdin_hex="0"),
            lambda d: d["cases"][0].update(stdin_hex="zz"),
            lambda d: d["cases"][0].update(stdin_hex="00 ff"),
            lambda d: d["cases"][0].update(reject=True),
            lambda d: d["cases"][0].update(stdout_hex=None, reject=True),
            lambda d: d["cases"][0].update(stderr_hex=None),
            lambda d: d["cases"][0].pop("stdout_hex"),
            lambda d: d["cases"][0].update(argv=["a\0b"]),
            lambda d: d["cases"][0].update(input_file=True),
            lambda d: d["cases"][0].update(argv=["{input}"]),
            lambda d: d["cases"][0].update(io="missing"),
            lambda d: d["cases"][0].update(unrecognized=True),
            lambda d: d["cases"][0].update(roundtrip_argv=None),
            lambda d: d["cases"][0].update(roundtrip_argv=[]),
            lambda d: d["cases"][0].update(roundtrip_argv="decode"),
            lambda d: d["cases"][0].update(roundtrip_argv=["de\0code"]),
            lambda d: d["cases"][0].update(roundtrip_argv=["{input}"]),
            lambda d: d["cases"][0].update(roundtrip_argv=["decode"], io="full"),
            lambda d: d["cases"][0].update(roundtrip_argv=["decode"], input_file=True, argv=["{input}"]),
            lambda d: (d["cases"][0].pop("stdout_hex"),
                       d["cases"][0].update(roundtrip_argv=["decode"], reject=True)),
        ]
        for mutate in mutations:
            document = copy.deepcopy(self.document)
            mutate(document)
            with self.subTest(document=document), self.assertRaises(ValueError):
                self.load(document)


if __name__ == "__main__":
    unittest.main()
