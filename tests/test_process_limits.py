from pathlib import Path
import sys
import tempfile
import unittest

from tools.runner import execute


class ProcessLimits(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def program(self, body):
        program = self.root / "candidate"
        program.write_text(f"#!{sys.executable}\n" + body)
        program.chmod(0o755)
        return program

    def test_excessive_stdout_is_stopped_before_completion(self):
        self.check_excessive_stream(1)

    def test_excessive_stderr_is_stopped_before_completion(self):
        self.check_excessive_stream(2)

    def check_excessive_stream(self, descriptor):
        marker = self.root / "completed"
        candidate = self.program(
            "import os\n"
            f"os.write({descriptor}, b'x' * (1024 * 1024))\n"
            f"open({str(marker)!r}, 'w').close()\n"
        )
        with self.assertRaisesRegex(AssertionError, "Limite de saída"):
            execute(candidate, timeout=2, limit=1024)
        self.assertFalse(marker.exists(), "Candidate completed its excessive write")

    def test_large_bidirectional_stream_does_not_deadlock(self):
        candidate = self.program(
            "import os\n"
            "while True:\n"
            "    data = os.read(0, 4096)\n"
            "    if not data: break\n"
            "    os.write(1, data)\n"
        )
        data = b"round trip\n" * 65536
        result = execute(candidate, data, timeout=2, limit=len(data))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, data)

    def test_closed_streams_do_not_disable_timeout(self):
        candidate = self.program(
            "import os, time\nos.close(1)\nos.close(2)\ntime.sleep(60)\n"
        )
        with self.assertRaisesRegex(AssertionError, "tempo"):
            execute(candidate, timeout=0.1)

    def test_arguments_preserve_spaces_and_empty_values(self):
        candidate = self.program("import sys\nprint(repr(sys.argv[1:]))\n")
        result = execute(candidate, argv=("encode", "a b", ""))
        self.assertEqual(result.stdout, b"['encode', 'a b', '']\n")

    def test_redirected_input_is_read_and_remains_open(self):
        candidate = self.program(
            "import sys\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n"
        )
        with tempfile.TemporaryFile() as source:
            source.write(b"\x00\xff")
            source.seek(0)
            result = execute(candidate, input_stream=source)
            self.assertFalse(source.closed)
        self.assertEqual(result.stdout, b"\x00\xff")


if __name__ == "__main__":
    unittest.main()
