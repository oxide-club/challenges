import sys
from pathlib import Path
w,h=map(int,sys.argv[1:3]);rgb=bytes.fromhex(sys.argv[3])
if len(rgb)!=w*h*3 or w<1 or h<1: raise SystemExit("pixels inválidos")
Path(sys.argv[4]).write_bytes(f"P6\n{w} {h}\n255\n".encode()+rgb)
