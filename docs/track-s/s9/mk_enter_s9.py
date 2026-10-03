"""mk_enter_s9.py - S9 (HPP-431): enter_scene_s9.py = C:/kyty/s288/enter_scene.py (sha pinned) + item 355 (e): the time from the
process start to the first "PipelinePrecache: all pipelines created" and to the first "ShaderPreparation: ready" line (seen by the
0.5 s poll of the log; json keys prep_created_s / prep_ready_s of the attempt) + the import path of the s288 root (the copy lives
in s9/).  Writes LF.  ASCII only."""
import hashlib
import sys

SRC = 'C:/kyty/s288/enter_scene.py'
DST = 'C:/kyty/s288/s9/enter_scene_s9.py'
WANT = '3eddc767b69844a2f35eaf69a4cea9ca0e7de0937bc1402546f34848a19df877'
NL = chr(10)

raw = open(SRC, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != WANT:
    sys.exit('source sha %s != %s' % (got, WANT))
t = raw.decode('utf-8').replace(chr(13) + NL, NL)
edits = [
    ('from run_safety99 import failure_marker' + NL + 'import idle142' + NL,
     "sys.path.insert(0, 'C:/kyty/s288')   # S9 (HPP-431): the copy lives in s9/, its helpers in the s288 root" + NL +
     'from run_safety99 import failure_marker' + NL + 'import idle142' + NL),
    ("                  stable_s=None, stable_frame=None, outcome='running', detail=None)" + NL +
     "    document = start_marker = stable = None" + NL,
     "                  stable_s=None, stable_frame=None, outcome='running', detail=None," + NL +
     "                  prep_created_s=None, prep_ready_s=None)" + NL +
     "    document = start_marker = stable = None" + NL +
     "    prep_created = prep_ready = None   # S9, item 355 (e): the preparation screen from the process start" + NL),
    ("        nonlocal document, start_marker, stable, run, frame" + NL,
     "        nonlocal document, start_marker, stable, run, frame, prep_created, prep_ready" + NL),
    ("            if b'GpuWaitSlow:' in line:  # session 58: read acopy= here before anything else" + NL,
     "            if prep_created is None and line.startswith(b'PipelinePrecache: all pipelines created'):" + NL +
     "                prep_created = time.monotonic() - started" + NL +
     "                result['prep_created_s'] = round(prep_created, 1)" + NL +
     "                print('%.1f s  PipelinePrecache: all pipelines created' % prep_created, flush=True)" + NL +
     "            if prep_ready is None and line.startswith(b'ShaderPreparation: ready'):" + NL +
     "                prep_ready = time.monotonic() - started" + NL +
     "                result['prep_ready_s'] = round(prep_ready, 1)" + NL +
     "                print('%.1f s  ShaderPreparation: ready' % prep_ready, flush=True)" + NL +
     "            if b'GpuWaitSlow:' in line:  # session 58: read acopy= here before anything else" + NL),
]
for a, b in edits:
    n = t.count(a)
    if n != 1:
        sys.exit('anchor found %d times: %r' % (n, a[:80]))
    t = t.replace(a, b)
head = ('"""enter_scene_s9.py - track S, link S9 (HPP-431; ROADMAP "SESSION 122" item 355 (e)): C:/kyty/s288/enter_scene.py (sha256 ' +
        WANT + ') with the preparation-screen times of the attempt (prep_created_s, prep_ready_s: seconds from the Popen of the' +
        ' emulator to the first line seen by the 0.5 s poll - an upper bound by at most one poll) and the s288 import path.' +
        ' Made by s9/mk_enter_s9.py; nothing else differs."""' + NL)
open(DST, 'wb').write((head + t).encode('ascii'))
print('enter_scene_s9.py written, sha256 %s' % hashlib.sha256(open(DST, 'rb').read()).hexdigest())
