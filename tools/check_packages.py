#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute preparação e sentinelas de starters em cópias descartáveis."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from verification_policy import check_repository

ROOT = Path(__file__).resolve().parents[1]
PREPARE = {
    '022': ['APROVADO: preparação', 'cargo test --offline --no-run'],
    '023': ['APROVADO: preparação', 'cargo test --offline --no-run'],
    '024': ['APROVADO: preparação', 'cargo test --offline --no-run'],
    '025': ['Preparação válida', 'Layout Rust: 24/8/0/8/16'],
    '026': ['Preparação válida', 'Núcleo do participante não executado'],
    '027': ['OK preparação: fixtures, JSON e cinco controles negativos'],
    '028': ['PASS build e falha intencional API do starter'],
    '029': ['PASS alvos ET_EXEC/PIE sem INTERP e starter incompleto'],
    '031': ['PASS suporte e starter incompleto'],
}

DEPENDENCIES = {
    '022': ('cargo', 'rustc'), '023': ('cargo', 'rustc'),
    '024': ('cargo', 'rustc'),
    '025': ('cc', 'ar', 'rustc', 'nm'),
    '026': ('cc', 'rustc', 'readelf', 'nm'),
    '027': ('rustc',),
    '028': ('make', 'cc'), '029': ('make', 'cc', 'readelf'),
    '031': ('make', 'cc'),
}


def unavailable_evidence(number):
    """Confirme indisponibilidade fora do checker que declarou status 77."""
    if number == '030':
        if os.name != 'nt':
            return ['host não Windows: os.name=' + os.name]
        raise ValueError('030: status 77 sem ausência comprovada de Windows')
    missing = [tool for tool in DEPENDENCIES.get(number, ()) if shutil.which(tool) is None]
    if not missing:
        raise ValueError(f'{number}: status 77 sem dependência ausente comprovada')
    return ['executável ausente no PATH: ' + tool for tool in missing]

def require_execution(number, trace):
    processes=trace['processes']
    def invoked(program, *arguments):
        return any(Path(command[0]).name == program and all(arg in command for arg in arguments)
                   for command in processes if command)
    if number in {'022','023','024'}:
        meaningful=invoked('cargo','check','--offline') and invoked('cargo','test','--no-run')
        if number in {'022','023','024'}:
            meaningful = meaningful and any(
                Path(c[0]).name.startswith('python') and 'tests/compile.py' in c
                for c in processes if c)
        if number in {'022','023'}:
            meaningful = meaningful and invoked('cargo','test','--offline','--test','support_contract')
    elif number in {'025','026'}:
        meaningful=invoked('rustc') and any(Path(c[0]).name in {'cc','gcc','clang'} for c in processes if c)
    elif number=='027':
        meaningful=['materials/generate.py','generate'] in trace['calls'] and ['tests/check.py','validate'] in trace['calls']
    elif number=='028':
        meaningful=invoked('make','all') and any(any(arg.endswith('tests/test.py') for arg in c) for c in processes)
    elif number=='031':
        meaningful=invoked('make','all') and all(
            any(Path(c[0]).parts[-2:] == ('build', binary) for c in processes if c)
            for binary in ('target','region-probe'))
    elif number=='029':
        meaningful=invoked('make','all') and len(processes)>=3
    else:
        meaningful=False
    if not meaningful:
        raise ValueError('verificador não executou as etapas de preparação exigidas; texto de aprovação não basta')

def require_result(result, status, markers):
    output = result.stdout + result.stderr
    if result.returncode != status or not all(marker in output for marker in markers):
        raise ValueError(f'status/diagnóstico inesperado: {result.returncode}; esperado {status}, {markers}')
    return output


def run_package(source, entry, output_dir):
    identifier = source.name
    number = identifier[:3]
    records = []
    with tempfile.TemporaryDirectory(prefix='oxide-package-') as temp:
        package = Path(temp)/identifier
        shutil.copytree(source, package, ignore=shutil.ignore_patterns('build', 'target', '__pycache__', '.git'))
        def execute(label, command, expected=0, markers=()):
            result = subprocess.run(command, cwd=package, text=True, capture_output=True, timeout=240)
            output = result.stdout + result.stderr
            (output_dir/f'{identifier}-{label}.log').write_text(output)
            records.append({'stage': label, 'command': command, 'status': result.returncode})
            require_result(result, expected, markers)
            return result
        trace_path=Path(temp)/'execution.json'
        preparation = subprocess.run([sys.executable, str(ROOT/'tools/package_worker.py'),
                                      str(package/entry['check']), str(trace_path)], cwd=package,
                                     text=True, capture_output=True, timeout=240)
        (output_dir/f'{identifier}-prepare.log').write_text(preparation.stdout+preparation.stderr)
        records.append({'stage': 'prepare', 'command': [sys.executable,entry['check'],'--prepare'], 'status': preparation.returncode})
        if preparation.returncode == 77:
            require_result(preparation, 77, ['NOT_RUN' if number == '030' else 'INDISPONÍVEL'])
            evidence = unavailable_evidence(number)
            return {'package': identifier, 'preparation': 'not_verified', 'starter': 'not_verified', 'records': records,
                    'unavailable_evidence': evidence}
        require_result(preparation, 0, PREPARE.get(number, ['Preparação válida']))
        if not trace_path.is_file(): raise ValueError('verificador encerrou sem registro de execução')
        execution=json.loads(trace_path.read_text())
        (output_dir/f'{identifier}-execution.json').write_text(json.dumps(execution,indent=2)+'\n')
        require_execution(number,execution)
        if number in {'022','023','024'}:
            execute('starter', [sys.executable, entry['check']], 1, ['participant:', 'test result: FAILED'])
        elif number == '025':
            execute('starter', [sys.executable,entry['check']], 1, ['tests/helper.rs', 'left: 0', 'right: 2'])
        elif number == '026':
            execute('starter', [sys.executable,entry['check']], 1, ['Err(Syscall(38))','zero_e_erro','test result: FAILED'])
        elif number == '027':
            execute('build', ['rustc','--edition','2021','-D','warnings','materials/starter/main.rs','-o','peinspect'])
            execute('starter', [sys.executable,entry['check'],'./peinspect'],1,['not_implemented','casos aprovados'])
        elif number == '028':
            execute('starter',[sys.executable,entry['check'],'build'],1,
                    ["'API'", "'positive'", "'rc': -1", "'out': 123", "'after': 38"])
        elif number == '029':
            execute('starter',['./build/oxdbg','--','./build/arith-exec'],1,['não implementado'])
        elif number == '031':
            execute('starter',['./build/target'],1,['sessão ainda não implementada'])
        else:
            raise ValueError(f'{identifier}: sentinela do starter não configurada')
        return {'package': identifier, 'preparation': 'passed', 'starter': 'expected_incomplete', 'records': records}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/package-checks')
    args=parser.parse_args()
    check_repository(ROOT)
    args.output.mkdir(parents=True,exist_ok=True)
    entries=json.loads((ROOT/'docs/verification-policy.json').read_text())
    results=[]
    for identifier, entry in entries.items():
        if entry['mode']!='package': continue
        try:
            result=run_package(ROOT/identifier,entry,args.output)
        except (ValueError,OSError,subprocess.SubprocessError) as error:
            result={'package':identifier,'preparation':'failed','error':str(error)}
        results.append(result)
        print(identifier, result['preparation'], result.get('starter',''), flush=True)
        if 'error' in result: print(result['error'], file=sys.stderr)
    (args.output/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
    print('Esta execução verifica preparação e sentinelas dos starters; não aprova soluções nem publicação.')
    unavailable=[r['package'] for r in results if r['preparation']=='not_verified']
    if unavailable: print('NÃO VERIFICADOS: '+', '.join(unavailable))
    return int(any(r['preparation']=='failed' for r in results))

if __name__=='__main__': sys.exit(main())
