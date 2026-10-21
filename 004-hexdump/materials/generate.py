"""Gera dados binários determinísticos em fluxo (biblioteca padrão)."""
import sys
if len(sys.argv) != 2 or not sys.argv[1].isascii() or not sys.argv[1].isdigit():
    raise SystemExit("uso: generate.py TAMANHO (0..16777216)")
n = int(sys.argv[1])
if not 0 <= n <= 16777216:
    raise SystemExit("tamanho fora do limite")
block = bytes(range(256)) * 16
while n:
    part = block[:min(n, len(block))]
    sys.stdout.buffer.write(part)
    n -= len(part)
