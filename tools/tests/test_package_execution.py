"""SPDX-License-Identifier: MIT. Controles de execução dos pacotes."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).parents[1]
sys.path.insert(0,str(TOOLS))
import check_packages as packages

class Execution(unittest.TestCase):
    def test_library_preparation_requires_compilation_pairs_and_support(self):
        base=[['cargo','check','--offline'],['cargo','test','--offline','--no-run']]
        pairs=['python3','tests/compile.py']
        support=['cargo','test','--offline','--test','support_contract']
        for processes in (base, base+[pairs], base+[support]):
            with self.assertRaisesRegex(ValueError,'não executou'):
                packages.require_execution('022',{'processes':processes,'calls':[]})
        packages.require_execution('022',{'processes':base+[pairs,support],'calls':[]})
    def test_ipc_preparation_requires_both_support_programs(self):
        base=[['make','all']]
        target=['/copy/build/target']
        probe=['/copy/build/region-probe']
        for processes in (base+[['true'],['true']], base+[target], base+[probe]):
            with self.assertRaisesRegex(ValueError,'não executou'):
                packages.require_execution('031',{'processes':processes,'calls':[]})
        packages.require_execution('031',{'processes':base+[target,probe],'calls':[]})
    def test_arbitrary_failure_is_not_expected_incomplete(self):
        result=subprocess.CompletedProcess([],1,'','SyntaxError: código inválido')
        with self.assertRaisesRegex(ValueError,'diagnóstico'):
            packages.require_result(result,1,['participant:','test result: FAILED'])
    def test_wrong_status_is_not_accepted_by_matching_text(self):
        result=subprocess.CompletedProcess([],0,'participant: test result: FAILED','')
        with self.assertRaises(ValueError): packages.require_result(result,1,['participant:'])
    def test_noop_checker_is_actually_executed_and_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'022-typestate';(source/'tests').mkdir(parents=True)
            (source/'tests/check.py').write_text('print("sem testes")\n')
            logs=root/'logs';logs.mkdir()
            with self.assertRaisesRegex(ValueError,'diagnóstico'):
                packages.run_package(source,{'check':'tests/check.py'},logs)
            self.assertIn('sem testes',(logs/'022-typestate-prepare.log').read_text())
    def test_noop_cannot_fake_preparation_by_printing_success(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'022-typestate';(source/'tests').mkdir(parents=True)
            (source/'tests/check.py').write_text('print("APROVADO: preparação; cargo test --offline --no-run")\n')
            logs=root/'logs';logs.mkdir()
            with self.assertRaisesRegex(ValueError,'não executou'):
                packages.run_package(source,{'check':'tests/check.py'},logs)
    def test_unavailable_is_not_passed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'030-windows-inspector';(source/'tests').mkdir(parents=True)
            (source/'tests/check.py').write_text('print("NOT_RUN: Windows x64 ausente")\nraise SystemExit(77)\n')
            logs=root/'logs';logs.mkdir()
            result=packages.run_package(source,{'check':'tests/check.py'},logs)
            self.assertEqual(result['preparation'],'not_verified')
            self.assertEqual(result['starter'],'not_verified')
    def test_bare_77_has_no_environment_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'030-windows-inspector';(source/'tests').mkdir(parents=True)
            (source/'tests/check.py').write_text('raise SystemExit(77)\n')
            logs=root/'logs';logs.mkdir()
            with self.assertRaises(ValueError):packages.run_package(source,{'check':'tests/check.py'},logs)

    def test_false_77_rejected_when_dependencies_present(self):
        with patch.object(packages.shutil, 'which', return_value='/tool'):
            with self.assertRaisesRegex(ValueError,'sem dependência ausente'):
                packages.unavailable_evidence('022')
    def test_missing_dependency_independently_recorded(self):
        with patch.object(packages.shutil, 'which', side_effect=lambda tool: None if tool=='rustc' else '/tool'):
            self.assertEqual(packages.unavailable_evidence('022'),['executável ausente no PATH: rustc'])
    def test_windows_77_rejected_on_windows_host(self):
        with patch.object(packages.os, 'name', 'nt'):
            with self.assertRaisesRegex(ValueError,'sem ausência comprovada'):
                packages.unavailable_evidence('030')
    def test_fake_77_checker_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'022-typestate';(source/'tests').mkdir(parents=True)
            (source/'tests/check.py').write_text('print("INDISPONÍVEL")\nraise SystemExit(77)\n')
            logs=root/'logs';logs.mkdir()
            with patch.object(packages.shutil,'which',return_value='/tool'):
                with self.assertRaisesRegex(ValueError,'sem dependência ausente'):
                    packages.run_package(source,{'check':'tests/check.py'},logs)

if __name__=='__main__':unittest.main()
