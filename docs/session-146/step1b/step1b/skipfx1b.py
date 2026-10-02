"""s146 link 1b (HPP-395; ROADMAP s122 item 316 (d)): the experiment rt146_skipfx of the Red Team (step 1, docs/session-146/step1/
rt146_skipfx.out.txt bb003909) repeated on the edited sc146.py - a synthetic root step1b/skipfx_root with only v146_05.json (a
copy of the real C:/kyty/s145/v145_02.json): case A no log, case B a log of 0 bytes; then the cases of item 316 (b)-(c) that
the experiment did not have: C the log present with its enter_scene end line (no marker) -> SKIPPED with the key; D the same
with a "--- Error ---" line (K1 key) -> RUN.  ASCII output."""
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import sys

ROOT = 'C:/kyty/s146/step1b/skipfx_root'
spec = importlib.util.spec_from_file_location('sc146', 'C:/kyty/s146/sc146.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
PRED = 'C:/kyty/s146/pred/01_sc146.md'


def call():
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = S.main(['--skip-w', 'w146_05'], root=ROOT, pred=PRED)
    return 'rc %d | %s' % (rc, b.getvalue().strip())


if os.path.isdir(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
shutil.copyfile('C:/kyty/s145/v145_02.json', ROOT + '/v146_05.json')
print('sc146.py sha256 %s' % S.sha_file('C:/kyty/s146/sc146.py'))
print('case A: V json present, log_v146_05.txt ABSENT, no score.json, no step2/times.txt')
print(call())
open(ROOT + '/log_v146_05.txt', 'wb').close()
print('case B: log_v146_05.txt present, 0 bytes')
print(call())
body = b'PipelinePrecache: 1 recipes -> 1 graphics + 0 compute pipelines queued\nFrameTrace: n=1 dt_us=16667\n'
open(ROOT + '/log_v146_05.txt', 'wb').write(body)
os.makedirs(ROOT + '/step2')
with open(ROOT + '/step2/times.txt', 'a') as f:
    f.write('2026-10-02T00:00:00Z go146a v146_05 enter_scene end rc 0 log_v146_05.txt sha256 %s\n' % hashlib.sha256(body).hexdigest())
print('case C: the log present (%d bytes) = its enter_scene end line of step2/times.txt, no entry line, no marker' % len(body))
print(call())
body2 = body + b'--- Error ---\n'
open(ROOT + '/log_v146_05.txt', 'wb').write(body2)
with open(ROOT + '/step2/times.txt', 'a') as f:
    f.write('2026-10-02T00:00:01Z go146a v146_05 enter_scene end rc 0 log_v146_05.txt sha256 %s\n' % hashlib.sha256(body2).hexdigest())
print('case D: the same with a "--- Error ---" line before any entry line (its times.txt line renewed)')
print(call())
sys.exit(0)
