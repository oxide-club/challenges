"""SPDX-License-Identifier: MIT. Controles da política de cobertura."""
import importlib.util
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('policy', Path(__file__).parents[1] / 'verification_policy.py')
policy = importlib.util.module_from_spec(spec)
if spec.loader and spec.origin and Path(spec.origin).exists():
    spec.loader.exec_module(policy)

class Policy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        d = self.root / '001-example'; d.mkdir()
        (d / 'index.md').write_text('---\ndraft: true\n---\n')
        (d / 'README.md').write_text('Preparação em andamento')
        self.entries = {'001-example': {'mode': 'preparing', 'guide': 'README.md', 'reason': 'Ambiente ainda não validado'}}
    def check(self):
        return policy.validate(self.root, self.entries, [])
    def test_explicit_draft_pending_is_visible(self):
        self.assertEqual(self.check(), ['001-example'])
    def test_missing_registration_is_rejected_even_for_draft(self):
        self.entries.clear()
        with self.assertRaisesRegex(ValueError, 'cobertura'): self.check()
    def test_published_pending_is_rejected(self):
        (self.root/'001-example/index.md').write_text('---\ndraft: false\n---\n')
        with self.assertRaisesRegex(ValueError, 'rascunho'): self.check()
    def test_missing_draft_does_not_allow_pending(self):
        (self.root/'001-example/index.md').write_text('---\ntitle: Example\n---\n')
        with self.assertRaisesRegex(ValueError, 'rascunho'): self.check()
    def test_unknown_mode_is_rejected(self):
        self.entries['001-example']['mode']='ignored'
        with self.assertRaisesRegex(ValueError, 'modo'): self.check()
    def test_empty_reason_is_rejected(self):
        self.entries['001-example']['reason']=''
        with self.assertRaisesRegex(ValueError, 'motivo'): self.check()
    def test_missing_package_check_is_rejected(self):
        self.entries['001-example']={'mode':'package','guide':'README.md','check':'tests/check.py'}
        with self.assertRaisesRegex(ValueError, 'verificador'): self.check()
    def test_embedded_without_real_catalog_is_rejected(self):
        self.entries['001-example']={'mode':'embedded'}
        with self.assertRaisesRegex(ValueError, 'embutido'): self.check()
    def test_empty_checker_rejected_even_with_published_metadata(self):
        d=self.root/'001-example'
        (d/'index.md').write_text('---\ndraft: false\n---\n')
        (d/'check.py').write_text('')
        self.entries['001-example']={'mode':'package','guide':'README.md','check':'check.py'}
        with self.assertRaisesRegex(ValueError, 'vazio'): self.check()
    def test_published_package_requires_validation_receipt(self):
        d=self.root/'001-example'
        (d/'index.md').write_text('---\ndraft: false\n---\n')
        (d/'check.py').write_text('print("sem testes")')
        self.entries['001-example']={'mode':'package','guide':'README.md','check':'check.py'}
        with self.assertRaisesRegex(ValueError, 'evidência'): self.check()

    def publish(self, names=None):
        d=self.root/'001-example'
        (d/'index.md').write_text('---\ndraft: false\n---\n')
        (d/'check.py').write_text('print("verificação")')
        files=names if names is not None else policy.public_inventory(d)
        record={'package':'001-example','status':'validated','reference':'passed',
                'mutants':'rejected','pilot':'approved','editorial':'approved',
                'public_sha256':{name:hashlib.sha256((d/name).read_bytes()).hexdigest() for name in files}}
        evidence=self.root/'receipt.json';evidence.write_text(json.dumps(record))
        self.entries['001-example']={'mode':'package','guide':'README.md','check':'check.py',
            'validation':{'path':'receipt.json','sha256':hashlib.sha256(evidence.read_bytes()).hexdigest()}}
    def set_pilot(self, status, waiver=None):
        evidence = self.root/'receipt.json'
        record = json.loads(evidence.read_text())
        record['pilot'] = status
        if waiver is not None:
            record['pilot_waiver'] = waiver
        evidence.write_text(json.dumps(record))
        self.entries['001-example']['validation']['sha256'] = hashlib.sha256(evidence.read_bytes()).hexdigest()

    def test_owner_can_explicitly_waive_pilot(self):
        self.publish()
        self.set_pilot('waived_by_owner', {'approved_by':'responsavel', 'date':'2026-10-25',
            'reason':'Dispensa explícita do piloto para esta publicação', 'request':'resposta do responsável'})
        self.assertEqual(self.check(), [])

    def test_waiver_without_decision_is_rejected(self):
        self.publish()
        self.set_pilot('waived_by_owner')
        with self.assertRaisesRegex(ValueError, 'piloto'):
            self.check()

    def test_unexecuted_pilot_without_waiver_is_rejected(self):
        self.publish()
        self.set_pilot('not_run')
        with self.assertRaisesRegex(ValueError, 'piloto'):
            self.check()

    def test_empty_waiver_reason_is_rejected(self):
        self.publish()
        self.set_pilot('waived_by_owner', {'approved_by':'responsavel','date':'2026-10-25',
            'reason':'', 'request':'resposta do responsável'})
        with self.assertRaisesRegex(ValueError, 'piloto'):
            self.check()

    def test_complete_current_manifest_accepted(self):
        self.publish()
        self.assertEqual(self.check(),[])
    def test_incomplete_manifest_rejected(self):
        self.publish(['README.md'])
        with self.assertRaisesRegex(ValueError,'exatamente todos'):self.check()
    def test_new_unvalidated_public_file_rejected(self):
        self.publish()
        (self.root/'001-example/new-test.py').write_text('print("novo")')
        with self.assertRaisesRegex(ValueError,'exatamente todos'):self.check()
    def test_changed_checker_invalidates_receipt(self):
        self.publish()
        (self.root/'001-example/check.py').write_text('print("sem testes")')
        with self.assertRaisesRegex(ValueError,'diverge'):self.check()
    def test_build_artifacts_not_part_of_public_inventory(self):
        self.publish()
        d=self.root/'001-example/target';d.mkdir();(d/'binary').write_bytes(b'build')
        self.assertEqual(self.check(),[])

if __name__ == '__main__': unittest.main()
