"""SPDX-License-Identifier: MIT. Cobertura explícita dos mecanismos de teste."""
import json
import ast
import hashlib
from datetime import date
from pathlib import Path
import re


def public_inventory(package):
    """Arquivos distribuídos; artefatos locais de build não validam a publicação."""
    generated = {'build', 'target', '.git'}
    return {str(path.relative_to(package)) for path in package.rglob('*')
            if path.is_file() and path.relative_to(package).parts[0] not in generated
            and '__pycache__' not in path.relative_to(package).parts}


def pilot_authorized(record):
    """Dispensa explícita não significa piloto executado ou aprovado."""
    if record.get('pilot') == 'approved':
        return True
    if record.get('pilot') != 'waived_by_owner':
        return False
    waiver = record.get('pilot_waiver')
    if not isinstance(waiver, dict) or waiver.get('approved_by') != 'responsavel':
        return False
    if any(not isinstance(waiver.get(key), str) or not waiver[key].strip()
           for key in ('date', 'reason', 'request')):
        return False
    try:
        date.fromisoformat(waiver['date'])
    except ValueError:
        return False
    return True


def validate(root, entries, embedded):
    definitions = {p.parent.name: p for p in root.glob('*/index.md')}
    if definitions.keys() != entries.keys():
        raise ValueError('cobertura: cada definição exige exatamente um registro')
    listed = set()
    pending = []
    for identifier, entry in entries.items():
        mode = entry.get('mode')
        if mode == 'embedded':
            listed.add(identifier)
            continue
        if mode not in ('package', 'preparing'):
            raise ValueError(f'{identifier}: modo desconhecido')
        guide = entry.get('guide', '')
        if not guide or not (root / identifier / guide).is_file() or Path(guide).is_absolute() or '..' in Path(guide).parts:
            raise ValueError(f'{identifier}: guia ausente ou inválido')
        if mode == 'package':
            check = entry.get('check', '')
            if not check or Path(check).is_absolute() or '..' in Path(check).parts or not (root/identifier/check).is_file():
                raise ValueError(f'{identifier}: verificador ausente ou inválido')
            source = (root/identifier/check).read_text()
            try:
                tree = ast.parse(source)
            except SyntaxError as error:
                raise ValueError(f'{identifier}: verificador Python inválido') from error
            if not any(isinstance(node, ast.Call) for node in ast.walk(tree)):
                raise ValueError(f'{identifier}: verificador vazio ou sem execução')
            front = definitions[identifier].read_text().split('---', 2)[1]
            if not re.search(r'^draft:\s*true\s*$', front, re.M):
                receipt = entry.get('validation', {})
                path = receipt.get('path', '')
                if not path or Path(path).is_absolute() or '..' in Path(path).parts:
                    raise ValueError(f'{identifier}: publicação exige evidência de validação')
                evidence = root / path
                if not evidence.is_file() or hashlib.sha256(evidence.read_bytes()).hexdigest() != receipt.get('sha256'):
                    raise ValueError(f'{identifier}: evidência de validação ausente ou divergente')
                record = json.loads(evidence.read_text())
                if (record.get('package') != identifier or record.get('status') != 'validated'
                        or record.get('reference') != 'passed' or record.get('mutants') != 'rejected'
                        or not pilot_authorized(record) or record.get('editorial') != 'approved'):
                    raise ValueError(f'{identifier}: evidência não aprova referência, controles, piloto e editorial')
                hashes = record.get('public_sha256', {})
                if not isinstance(hashes, dict) or set(hashes) != public_inventory(root/identifier):
                    raise ValueError(f'{identifier}: manifesto público deve cobrir exatamente todos os materiais')
                if not hashes or any(not (root/identifier/name).is_file()
                    or Path(name).is_absolute() or '..' in Path(name).parts
                    or hashlib.sha256((root/identifier/name).read_bytes()).hexdigest() != digest
                    for name, digest in hashes.items()):
                    raise ValueError(f'{identifier}: revisão validada diverge dos materiais')
        else:
            front = definitions[identifier].read_text().split('---', 2)[1]
            if not re.search(r'^draft:\s*true\s*$', front, re.M):
                raise ValueError(f'{identifier}: preparação pendente exige rascunho explícito')
            if not entry.get('reason', '').strip():
                raise ValueError(f'{identifier}: motivo pendente obrigatório')
            pending.append(identifier)
    if listed != set(embedded):
        raise ValueError('catálogo embutido diverge da política de cobertura')
    return sorted(pending)


def check_repository(root):
    entries = json.loads((root/'docs/verification-policy.json').read_text())
    source = (root/'tools/oxide-test/src/challenges/mod.rs').read_text()
    embedded = re.findall(r'^\s*"([0-9]{3}-[a-z0-9-]+)"\s*=>', source, re.M)
    return validate(root, entries, embedded)

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    pending = check_repository(root)
    print(f'Cobertura declarada: {len(list(root.glob("*/index.md")))} definições; {len(pending)} preparações pendentes')
    for identifier in pending: print('PENDENTE: ' + identifier)
