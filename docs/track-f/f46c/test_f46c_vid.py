"""Fixtures of f46c_vid.py (Track F link F46c, HPP-800; ROADMAP s122 item 702 (d)(1)-(4), (g)(3)): the detector M(f) on a tinted frame
(600 magenta pixels -> 600), an ordinary frame (0), the colour edges (R 200 / 199, G 40 / 41, B 200 / 199), the edge theta = 500 of a
difference (500 - hit, 499 - no); the brightness and the entry screen exclusion (mean 5.0 excluded, 5.01 not; both readings); the measure
d (mask mean of max |x - 1| over channels; d_0 - d_1b = 16 - candidate, 15.x - not; empty mask - None); the window W(e) (letter of item
702 (g)(3): p - 1 .. min(max(p_end_0, p_end_1) + 3, p + 600), cap edge); an end-to-end synthetic series on lossless videos (libx264rgb
crf 0, 960x540): control alive on c1, V yes on t1 inside W, D candidates at the presents with d_0 - d_1b >= 16, an excluded entry
screen present, S2 NO_APPLY, S3 class 'kept why=layers', S4 without tint tags; the sheets are written; strict cp1250 output; the last
line is ALL OK.  Early-exit form.  ASCII only.
usage: python test_f46c_vid.py [<f46c_vid.py under test>]"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f46c_vid.py')
BASE = os.path.join(HERE, 'fx_f46c_vid')
_spec = importlib.util.spec_from_file_location('f46c_vid_under_test', SRC)
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f46c_vid.py sha256 %s target f46c_vid.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
ok = True
H, W = 540, 960


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


def gray(v=100):
    return np.full((H, W, 3), v, dtype=np.uint8)


def box(fr, n, col=(255, 0, 255), x0=100, y0=100):
    fr = fr.copy()
    w = 30
    rows = n // w
    fr[y0:y0 + rows, x0:x0 + w] = col
    rest = n - rows * w
    if rest:
        fr[y0 + rows, x0:x0 + rest] = col
    return fr


# ---- detector
ok &= check('M tinted 600', V.m_count(box(gray(), 600)) == 600)
ok &= check('M ordinary 0', V.m_count(gray()) == 0 and V.m_count(gray(255)) == 0)
ok &= check('M colour edges', V.m_count(box(gray(), 10, (200, 40, 200))) == 10 and V.m_count(box(gray(), 10, (199, 40, 200))) == 0 and
            V.m_count(box(gray(), 10, (200, 41, 200))) == 0 and V.m_count(box(gray(), 10, (200, 40, 199))) == 0)
ok &= check('theta 500', V.THETA == 500 and V.D_MIN == 16 and V.DARK == 5.0 and V.CAP == 600)
ma = {10: (600, 50.0), 11: (599, 50.0), 12: (1000, 50.0), 13: (900, 3.0)}
mb = {10: (100, 50.0), 11: (100, 50.0), 12: (100, 50.0), 13: (0, 50.0)}
c1 = V.compare(ma, mb, [10, 11, 12, 13, 14], True)
c0 = V.compare(ma, mb, [10, 11, 12, 13, 14], False)
ok &= check('compare edge 500 hit / 499 no; 13 excluded by mean 3.0', c1['hits'] == 2 and c1['first'] == 10 and c1['comparable'] == 3 and
            c0['hits'] == 3 and c0['comparable'] == 4 and c0['best'] == (12, 900))
ok &= check('exclusion edge mean 5.0 excluded, 5.01 not', V.compare({1: (600, 5.0)}, {1: (0, 50)}, [1], True)['comparable'] == 0 and
            V.compare({1: (600, 5.01)}, {1: (0, 50)}, [1], True)['hits'] == 1)
ok &= check('mean black 0, gray 100', V.mean_of(gray(0)) == 0.0 and V.mean_of(gray()) == 100.0)
# ---- d
f1 = gray()
mask = V.m_mask(box(gray(), 600))
f0 = f1.copy()
f0[mask] = (120, 100, 90)
fb = f1.copy()
fb[mask] = (104, 100, 100)
ok &= check('d_0 = 20, d_1b = 4 (max over channels)', V.d_measure(f0, f1, mask) == 20.0 and V.d_measure(fb, f1, mask) == 4.0)
ok &= check('d empty mask None', V.d_measure(f0, f1, np.zeros((H, W), bool)) is None)
f0b = f1.copy()
f0b[mask] = (100, 100, 84)
ok &= check('d uses |x - 1| (negative difference 16)', V.d_measure(f0b, f1, mask) == 16.0)
# ---- window
ok &= check('window letter', V.window(238, 300, 240) == (237, 303) and V.window(238, 240, 300) == (237, 303))
ok &= check('window cap', V.window(238, 2000, 240) == (237, 838) and V.window(238, 835, 10) == (237, 838) and V.window(238, 834, 10) == (237, 837))

# ---- end to end
shutil.rmtree(BASE, ignore_errors=True)
RD = os.path.join(BASE, 'runs')
os.makedirs(RD)
NF = 40


def frame_of(arm, p):
    if p <= 3:
        return gray(0)
    fr = gray()
    if arm == 't1' and 11 <= p <= 13:
        fr = box(fr, 600)
    if arm == 't1' and p == 30:
        fr = box(fr, 600)
    if arm == 'c1' and 20 <= p <= 22:
        fr = box(fr, 600, x0=400)
    m = V.m_mask(box(gray(), 600))
    if arm == '0':
        fr[m] = {11: (110, 100, 100), 12: (140, 100, 100), 13: (119, 100, 100)}.get(p, (100, 100, 100))
    if arm == '1b':
        fr[m] = {11: (103, 100, 100), 12: (103, 100, 100), 13: (103, 100, 100)}.get(p, (100, 100, 100))
    return fr


def make_video(arm, tag):
    rec = os.path.join(BASE, 'rec_%s.mp4' % tag)
    p = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                          '-r', '60', '-i', '-', '-c:v', 'libx264rgb', '-crf', '0', '-preset', 'ultrafast', rec], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame_of(arm, i + 1).tobytes())
    p.stdin.close()
    p.wait()
    with open(rec + '.idx', 'w') as f:
        for i in range(NF):
            f.write('%d %d %.3f\n' % (i, i + 1, i / 60.0))
    return rec


def ev(k, cls, p, fx=None, no_apply=False, found=True):
    return dict(k=k, found=found, cls=cls, no_apply=no_apply, present=p, dcc='0', exec_present=p if cls == 'kept_applied' else None,
                first_exec=[dict(present=fx, image='x', site='prepare')] if fx else [])


def readjson(tag, events, tint=0):
    os.makedirs(os.path.join(RD, tag), exist_ok=True)
    json.dump(dict(status='ADMITTED', events=events, idx=dict(records=NF, last_present=NF), rows=dict(last_f5=dict(f26_tint_applied=tint))),
              open(os.path.join(RD, tag, 'read.json'), 'w'))


E1 = [ev(1, 'kept_applied', 10, fx=12), ev(2, 'kept why=decode', 10, no_apply=True), ev(3, 'kept why=layers', 10), ev(4, 'kept_applied', 10)]
E0 = [ev(1, 'off', 10, fx=15), ev(2, 'off', 10), ev(3, 'off', 10), ev(4, 'off', 10)]
for arm, tag, evs, tint in (('1', 'f26s_1', E1, 0), ('0', 'f26s_0', E0, 0), ('1b', 'f26s_1b', E1, 0), ('t1', 'f26s_t1', E1, 3),
                            ('c1', 'f26s_c1', E1, 2)):
    make_video(arm, tag)
    readjson(tag, evs, tint)
    t = V.frames_table(os.path.join(BASE, 'rec_%s.mp4' % tag), os.path.join(BASE, 'rec_%s.mp4.idx' % tag))
    json.dump(t, open(os.path.join(RD, tag, 'frames.json'), 'w'))
    if tag == 'f26s_t1':
        mt = dict((r[0], r[1]) for r in t['rows'])
        ok &= check('frames table lossless: t1 M at 12 = 600, at 5 = 0, size 960x540, rows 40', mt[12] == 600 and mt[5] == 0 and
                    tuple(t['size']) == (960, 540) and len(t['rows']) == 40)
out = V.series(RD, True)
e = dict((r['k'], r) for r in out['events'])
ok &= check('S1 window [9, 18] (p 10, p_end_0 15 first_exec, p_end_1 12)', e[1].get('window') == [9, 18] and e[1]['p_end_0'] == 15 and
            e[1]['p_end_1'] == 12)
ok &= check('S1 control alive (c1 M 600 at 20..22, tint_applied 2)', e[1]['control']['alive'] and e[1]['control']['with_exclusion']['hits'] == 3)
ok &= check('S1 V yes, hits 3 in W (present 30 outside W not counted)', e[1]['V'] == 'yes' and e[1]['V_with_exclusion']['hits'] == 3)
ok &= check('S1 D candidates [12, 13] (d0-d1b 37, 16), 11 not (7)', e[1]['D_candidates'] == [12, 13] and
            [r['diff'] for r in e[1]['D_rows']] == [7.0, 37.0, 16.0])
ok &= check('S1 exec <= p + 1 (kept_applied)', e[1]['exec_le_p1'] is True)
ok &= check('S2 NO_APPLY undetermined', 'NO_APPLY' in e[2]['state'])
ok &= check('S3 layers - no mark by construction', 'no mark by construction' in e[3]['state'])
ok &= check('S4 tint tags absent - control / V undetermined', 'not admitted' in str(e[4].get('control')) and 'not admitted' in e[4]['V'])
sh = sorted(os.listdir(os.path.join(RD, 'series', 'sheets')))
ok &= check('sheets written: ev1_cand_* and ctl1_* (%s)' % sh[:6], any(s.startswith('ev1_cand_12') for s in sh) and
            any(s.startswith('ctl1_') for s in sh))
# without the exclusion: an entry-screen present with magenta only in t
json.dump(dict(V.load_json(os.path.join(RD, 'f26s_t1', 'frames.json')), rows=[[p, (700 if p == 9 else m), (3.0 if p == 9 else mn)] for p, m, mn in
                                                                              V.load_json(os.path.join(RD, 'f26s_t1', 'frames.json'))['rows']]),
          open(os.path.join(RD, 'f26s_t1', 'frames.json'), 'w'))
out = V.series(RD, False)
e = dict((r['k'], r) for r in out['events'])
ok &= check('excluded present 9 counts only without the exclusion', e[1]['V_with_exclusion']['hits'] == 3 and e[1]['V_without_exclusion']['hits'] == 4)
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
p = subprocess.run([sys.executable, SRC, '--series', '--runs', RD, '--no-sheets'], capture_output=True, env=env)
ok &= check('CLI --series rc 0, ASCII (cp1250 strict)', p.returncode == 0 and all(c < 128 for c in p.stdout) and b'S1 ' in p.stdout)
shutil.rmtree(BASE, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok and N[1] == 0:
    print('ALL OK')
sys.exit(0 if ok and N[1] == 0 else 1)
