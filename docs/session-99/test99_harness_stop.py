"""Execute only the actual launch-loop AST with attempt() mocked; never import/launch emulator."""
import ast
import contextlib
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from run_safety99 import FAILURE_TOKENS, failure_marker

source = Path('C:/kyty/s99/enter_scene.py').read_text(encoding='utf8')
tree = ast.parse(source)
loop = next(n for n in ast.walk(tree) if isinstance(n, ast.For)
            and isinstance(n.target, ast.Tuple)
            and ast.unparse(n.target) == '(label, index)')
code = compile(ast.fix_missing_locations(ast.Module(body=[loop], type_ignores=[])), '<launch-loop-only>', 'exec')

class Stop(unittest.TestCase):
    def run_case(self, outcome='ok', hold_s=300.0, hold_exit=None, log=b'normal\n', exists=True,
                 stdout=b'normal\n', stdout_exists=True):
        with tempfile.TemporaryDirectory(prefix='s99-no-game-') as tmp:
            root = Path(tmp)
            if exists:
                (root/'log_fixture_warmup.txt').write_bytes(log)
            if stdout_exists:
                (root/'stdout_fixture_warmup.txt').write_bytes(stdout)
            calls = []
            def attempt(label, *args):
                calls.append(label)
                return dict(outcome=outcome if label=='warmup' else 'ok', hold_s=hold_s,
                            hold_exit=hold_exit)
            ns = dict(plan=[('warmup',0),('attempt 1',1)], env={}, attempts=[], success=None,
                      attempt=attempt, copy_artifacts=lambda *a:None, ROOT=root, tag='fixture',
                      options=SimpleNamespace(hold=300), args=[])
            ns['failure_marker'] = failure_marker
            with contextlib.redirect_stdout(io.StringIO()):
                exec(code, ns)
            return calls, ns['success']

    def test_success_runs_exactly_two(self):
        self.assertEqual(self.run_case()[0], ['warmup','attempt 1'])
    def test_entry_failure_stops(self):
        for outcome in ['ErrorDeviceLost','GpuHangAbort','timeout','crash']:
            with self.subTest(outcome=outcome):
                self.assertEqual(self.run_case(outcome=outcome), (['warmup'],None))
    def test_hold_death_stops(self):
        self.assertEqual(self.run_case(hold_exit=321), (['warmup'],None))
    def test_short_hold_stops(self):
        self.assertEqual(self.run_case(hold_s=299.9), (['warmup'],None))
    def test_missing_log_stops(self):
        self.assertEqual(self.run_case(exists=False), (['warmup'],None))
    def test_missing_stdout_stops(self):
        self.assertEqual(self.run_case(stdout_exists=False), (['warmup'],None))
    def test_failure_markers_stop(self):
        for token in FAILURE_TOKENS:
            with self.subTest(token=token):
                self.assertEqual(self.run_case(log=token.upper()+b'\n'), (['warmup'],None))
    def test_stdout_only_failure_markers_stop(self):
        for token in FAILURE_TOKENS:
            with self.subTest(token=token):
                self.assertEqual(self.run_case(stdout=token.upper()+b'\n'), (['warmup'],None))

if __name__=='__main__':
    unittest.main(verbosity=2)
