#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Observe a execução real do verificador sem modificar seus arquivos."""
import json
from pathlib import Path
import runpy
import sys

checker=Path(sys.argv[1]).resolve()
trace=Path(sys.argv[2]).resolve()
root=checker.parents[1]
processes=[]
calls=set()
def audit(event,args):
    if event=='subprocess.Popen':
        processes.append([str(x) for x in args[1]] if not isinstance(args[1],str) else [args[1]])
def profile(frame,event,arg):
    if event=='call':
        path=Path(frame.f_code.co_filename)
        if path.is_absolute() and path.is_relative_to(root):
            calls.add((str(path.relative_to(root)),frame.f_code.co_name))
sys.addaudithook(audit)
sys.setprofile(profile)
sys.argv=[str(checker),'--prepare']
try:
    runpy.run_path(str(checker),run_name='__main__')
finally:
    sys.setprofile(None)
    trace.write_text(json.dumps({'processes':processes,'calls':sorted(calls)},indent=2)+'\n')
