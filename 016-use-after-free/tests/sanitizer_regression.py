"""Compila o starter e uma implementação candidata sob ASan/UBSan."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

challenge = Path(__file__).resolve().parents[1]
implementation = Path(sys.argv[1]).resolve()
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0')
with tempfile.TemporaryDirectory() as tmp:
    buggy = Path(tmp) / 'buggy'
    fixed = Path(tmp) / 'fixed'
    flags = ['cc', '-std=c11', '-g', '-O0', '-fsanitize=address,undefined',
             '-fno-omit-frame-pointer']
    subprocess.run(flags + [str(challenge / 'materials/buggy.c'), '-o', str(buggy)], check=True)
    result = subprocess.run([str(buggy)], capture_output=True, env=env)
    assert result.returncode != 0 and b'heap-use-after-free' in result.stderr, result.stderr
    subprocess.run(flags + ['-I', str(challenge / 'materials'), str(implementation),
                            str(challenge / 'materials/adapter.c'), '-o', str(fixed)], check=True)
    subprocess.run([sys.executable, str(challenge / 'tests/test.py'), str(fixed)], env=env, check=True)
print('starter rejeitado pelo ASan; correção passou nos vetores com ASan/UBSan')
