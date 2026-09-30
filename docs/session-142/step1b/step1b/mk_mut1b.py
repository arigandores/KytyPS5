"""Link 1b (HPP-282): writes C:/kyty/s142/mut_sc142.py = the step-0 list (anchors the fixes moved replaced, two dropped)
+ the new mutants of step1b/mut_new.py; checks every anchor occurs exactly once in sc142.py and old != new.  LF, ASCII."""
import importlib.util
from pathlib import Path


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


old = load('C:/kyty/s142/step1b/v0/mut_sc142.py', 'mut_old')
new = load('C:/kyty/s142/step1b/mut_new.py', 'mut_new')
src = Path('C:/kyty/s142/sc142.py').read_bytes().decode('utf-8')
out = []
for name, a, b in old.MUTANTS:
    if name in new.DROPPED:
        continue
    if name in new.REPLACED:
        a, b = new.REPLACED[name]
    out.append((name, a, b))
out += new.NEW
names = [n for n, _, _ in out]
assert len(names) == len(set(names)), 'duplicate names'
bad = [(n, src.count(a)) for n, a, b in out if src.count(a) != 1 or a == b]
assert not bad, bad
HEAD = '''"""Session 142 step 0 (HPP-277), link 1b (HPP-282; ROADMAP s122 item 224 (a), (b)(3)): mutants of sc142.py (the scorer of
the scene census sc142 and of SCENE_OK on Sky Garden) - each must be killed by test_sc142.py.  Run through the frozen mutlib
v4.1 FULL (never --changed-from), ONE counted run on the final text of link 1b (items 84, 85, 87 (b)(3), 165 (v), 224 (b)(3)):
    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s142/sc142.py
        --test C:/kyty/s142/test_sc142.py --mutants C:/kyty/s142/mut_sc142.py --control --no-memo --workers 8
        --work-dir C:/kyty/s142/mutwork1b --cache-dir C:/kyty/s142/mutcache1b --out C:/kyty/s142/mut_sc142_1b.txt
One mutant per constant a fixture pins, per edge of the reading of item 221 (v), (g)(2)-(3) and of item 224 (a)(1)-(10) (the
first scene frame, the window of 599, K2 >= 1 s, K3 >= 100 ms and < 1 s, 120 s, hold_s 120, 300 s, V hold_s 330, 3 000
frames, the video >= 3 000 frames and >= FrameTrace rows - 100, 0 glitches, 0 [Vulkan][E], hold 300 s, W ft_tail > 0), per
death marker, its class and its ORDER (the first by position decides; stdout after the log; attempt markers last), per
scene-change term, per term of the W validation-active row, per term of the sheet sha row, per admission check, per SCENE_OK
condition and word, per term of the stop rule (an attempt without json breaks a run), per term of the seal check, per
calibration expectation and check line, per per-entry row a fixture reads, and the variant vx.  Every anchor occurs exactly
once in sc142.py (LF).  The cheap failures (constants) stand before the full paths (item 112 (a)).
Not mutated, EQUIVALENT (proofs): (1) scene_ok "w['hold_exit'] is None" and "v['hold_exit'] is None" - ended is already true
when hold_exit is set (build), so the term never decides alone; (2) stop_check "run[-STOP_RUN:]" -> "run" - the function
returns as soon as the run reaches STOP_RUN, so the run is never longer.  Not mutated: report texts no fixture reads; the
CHUNK size (the fixtures set it themselves); the path constants of the calibration logs (the fixtures set CALIB themselves;
the real logs are read by --calib).  Dropped at link 1b: oc_k1_marks, oc_k2_marks (the K1-before-K2 order of step 0 they
mutated is gone - oc_marks_first, oc_marks_any, mk_sort, mk_order mutate the order of item 224 (a)(1)).
"""
'''
body = 'MUTANTS = [\n' + ''.join('    (%r, %r, %r),\n' % t for t in out) + ']\n'
text = HEAD + body
assert all(ord(c) < 128 for c in text)
Path('C:/kyty/s142/mut_sc142.py').write_bytes(text.encode('ascii'))
print('mutants %d (old kept %d, new %d)' % (len(out), len(out) - len(new.NEW), len(new.NEW)))
