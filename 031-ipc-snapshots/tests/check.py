#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import argparse, os, pathlib, subprocess, tempfile, json, secrets, re, hashlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CASES = [
    "bad-token",
    "normal",
    "worker",
    "repeat",
    "long",
    "boundary",
    "extra",
    "max-generation",
    "owner-death",
    "disconnect",
    "timeout",
    "lock-timeout",
]


def check(candidate, hooks=False):
    candidate = str(pathlib.Path(candidate).resolve())
    with tempfile.TemporaryDirectory(prefix="ox-ipc-") as d:
        session_dir = pathlib.Path(d) / "sessions"
        session_dir.mkdir()
        witness = pathlib.Path(d) / "witness.json"
        for case in (
            CASES
            + (["seq-max-stop", "seq-max-state"] if hooks else [])
            + ["normal"] * 10
        ):
            env = os.environ.copy()
            env["OX_CASE"] = case
            env["TMPDIR"] = str(session_dir)
            nonce = secrets.token_hex(32)
            env["OX_WITNESS"] = str(witness)
            env["OX_WITNESS_NONCE"] = nonce
            witness.unlink(missing_ok=True)
            command = [candidate, "--observer", str(ROOT / "tests/peer.py")]
            if case == "worker":
                command += ["--test-worker"]
            if case.startswith("seq-max"):
                command += ["--test-sequence-max"]
            p = subprocess.run(
                command, env=env, capture_output=True, text=True, timeout=9
            )
            assert p.returncode == 0, (
                case,
                p.returncode,
                re.sub(r"[0-9a-fA-F]{64}", "[REDACTED]", p.stdout),
                re.sub(r"[0-9a-fA-F]{64}", "[REDACTED]", p.stderr),
            )
            assert witness.is_file(), ("observador de teste não concluiu", case)
            record = json.loads(witness.read_text())
            digest = record.pop("token_digest")
            assert record == {"case": case, "nonce": nonce}, (
                "testemunho inválido",
                case,
            )
            for word in re.findall(r"[0-9a-fA-F]{64}", p.stdout + p.stderr):
                assert hashlib.sha256(bytes.fromhex(word)).hexdigest() != digest, (
                    "token exposto em stdout/stderr",
                    case,
                )
            assert not list(session_dir.iterdir()), ("cleanup", case)
            print("PASS", case)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("candidate", nargs="?")
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--test-hooks", action="store_true")
    a = p.parse_args()
    try:
        if a.prepare:
            subprocess.run(["make", "-C", str(ROOT), "all"], check=True)
            p1 = subprocess.run([str(ROOT / "build/target")], capture_output=True)
            assert p1.returncode == 1
            subprocess.run([str(ROOT / "build/region-probe")], check=True)
            print("PASS suporte e starter incompleto; não aprova solução")
        elif a.candidate:
            check(a.candidate, a.test_hooks)
        else:
            p.error("informe target ou --prepare")
    except (
        AssertionError,
        ValueError,
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        OSError,
    ) as e:
        p.exit(1, "FAIL " + str(e) + "\n")
