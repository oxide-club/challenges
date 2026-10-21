"""Consulta: python3 oracle.py W H RGB_HEX > exemplo.px. Não leia antes de investigar."""
import sys,struct
w,h=map(int,sys.argv[1:3]);p=bytes.fromhex(sys.argv[3])
if not (0<w<=64 and 0<h<=64 and len(p)==3*w*h): raise SystemExit("dimensões/pixels inválidos")
sys.stdout.buffer.write(b'PX'+bytes([1,0])+struct.pack('>HH',w,h)+b''.join(p[3*(y*w+x):3*(y*w+x)+3][::-1] for x in range(w) for y in range(h)))
