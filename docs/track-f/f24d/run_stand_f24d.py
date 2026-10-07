# F24d (HPP-663, Red Team, ROADMAP s122 item 595(zh)): own run of the B13 stand on own build (worktree fbae3a68 =
# 0005e11f + ebf5484f + fbae3a68, build C:/kyty/f287/f24d/buildB) or on a mutant build. Written from scratch (not a copy
# of run_stand_f24c.py); the member of item 595(e)(1) is evaluated with the review sizes of 595(zh):
#   M1-a KYTY_FIX_B13=1 forced, points 11/12/13 x bdabits 0/1: lost 0
#   M1-b KYTY_FIX_B13=1 free, points 11/12 x bdabits 0/1: lost 0       (free point 13 is run too - report only, 601(v)(3))
#   M1-c KYTY_FIX_B13=1 controls before/after x bdabits 0/1: lost 0
#   M1-d KYTY_FIX_B13=0 same build, forced point 1 bdabits 0: lost >= 1
#   M1-e every =1 arm rc 0 with its result line, fix_b13=1 and "FixB13: mode=1"; every =0 arm fix_b13=0, "mode=0"
# Every arm >= 1e5 iterations (forced and controls --iters, free --free-iters).
# --mutant: the =0 arm is skipped (a mutant changes only the =1 branch) and the expected verdict is MEMBER FAIL.
# Usage: python run_stand_f24d.py --build <dir> --tag <t> [--iters N] [--free-iters N] [--mutant]
import argparse, hashlib, os, re, subprocess, sys, time

ap = argparse.ArgumentParser()
ap.add_argument('--build', required=True)
ap.add_argument('--tag', required=True)
ap.add_argument('--iters', type=int, default=100000)
ap.add_argument('--free-iters', type=int, default=1000000)
ap.add_argument('--mutant', action='store_true')
a = ap.parse_args()
RUNS = 'C:/kyty/f287/f24d/runs'
os.makedirs(RUNS, exist_ok=True)
exe = a.build + '/b13_epoch_stand.exe'
out = []
out.append('exe %s sha256 %s' % (exe, hashlib.sha256(open(exe, 'rb').read()).hexdigest()))


def run(name, knob, mode, point, bits, iters):
    env = dict(os.environ)
    env.pop('KYTY_FIX_B13', None)
    if knob is not None:
        env['KYTY_FIX_B13'] = knob
    args = [exe, mode, str(point), str(bits), str(iters)]
    t0 = time.time()
    try:
        r = subprocess.run(args, capture_output=True, timeout=400, env=env)
        rc, so = r.returncode, r.stdout.decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        rc, so = -999, 'TIMEOUT'
    open('%s/%s_%s.txt' % (RUNS, a.tag, name), 'w', encoding='utf-8').write(
        'args: %s\nKYTY_FIX_B13: %s\nrc: %d\nseconds: %.1f\n%s\n' % (' '.join(args), knob, rc, time.time() - t0, so))
    res = [l for l in so.splitlines() if l.startswith('B13 ')]
    modeline = [l for l in so.splitlines() if l.startswith('FixB13: mode=')]
    f = dict(re.findall(r'(\w+)=([^ ]+)', res[0])) if len(res) == 1 else {}
    out.append('%s_%s | rc=%d | %s | %s' % (a.tag, name, rc, modeline[0] if modeline else 'NO_MODE_LINE', res[0] if res else 'NO_RESULT'))
    return rc, f, modeline


ok = {'a': True, 'b': True, 'c': True, 'd': True, 'e': True}
lost = {}
for p in (11, 12, 13):
    for b in (0, 1):
        n = 'k1_forced_p%d_b%d' % (p, b)
        rc, f, ml = run(n, '1', 'forced', p, b, a.iters)
        lost[n] = int(f.get('lost', -1))
        ok['a'] &= lost[n] == 0
        ok['e'] &= rc == 0 and f.get('fix_b13') == '1' and ml == ['FixB13: mode=1'] and f.get('iters') == str(a.iters)
for p in (11, 12, 13):
    for b in (0, 1):
        n = 'k1_free_p%d_b%d' % (p, b)
        rc, f, ml = run(n, '1', 'free', p, b, a.free_iters)
        lost[n] = int(f.get('lost', -1))
        if p != 13:
            ok['b'] &= lost[n] == 0
        ok['e'] &= rc == 0 and f.get('fix_b13') == '1' and ml == ['FixB13: mode=1'] and f.get('iters') == str(a.free_iters)
for m in ('before', 'after'):
    for b in (0, 1):
        n = 'k1_%s_p11_b%d' % (m, b)
        rc, f, ml = run(n, '1', m, 11, b, a.iters)
        lost[n] = int(f.get('lost', -1))
        ok['c'] &= lost[n] == 0
        ok['e'] &= rc == 0 and f.get('fix_b13') == '1' and ml == ['FixB13: mode=1']
if not a.mutant:
    for knob, tag in (('0', 'k0'), (None, 'ku')):
        n = '%s_forced_p1_b0' % tag
        rc, f, ml = run(n, knob, 'forced', 1, 0, a.iters)
        lost[n] = int(f.get('lost', -1))
        if knob == '0':
            ok['d'] &= lost[n] >= 1
        ok['e'] &= rc == 0 and f.get('fix_b13') == '0' and ml == ['FixB13: mode=0']
    for n, p, b, md in (('k0_forced_p2_b1', 2, 1, 'forced'), ('k0_free_p1_b0', 1, 0, 'free'), ('k0_free_p1_b1', 1, 1, 'free')):
        rc, f, ml = run(n, '0', md, p, b, a.free_iters if md == 'free' else a.iters)
        lost[n] = int(f.get('lost', -1))
        out.append('REPORT %s lost %d' % (n, lost[n]))
for k, txt in (('a', '=1 forced 11/12/13 x b0/b1 lost 0'), ('b', '=1 free 11/12 x b0/b1 lost 0'),
               ('c', '=1 controls before/after x b0/b1 lost 0'), ('d', '=0 forced p1 b0 lost >= 1'),
               ('e', 'rc 0, result line, fix_b13 and FixB13 mode by knob')):
    if a.mutant and k == 'd':
        continue
    out.append('MEMBER M1-%s %s: %s' % (k, txt, 'PASS' if ok[k] else 'FAIL'))
out.append('REPORT =1 free p13 b0/b1 lost %d,%d' % (lost['k1_free_p13_b0'], lost['k1_free_p13_b1']))
member = all(v for k, v in ok.items() if not (a.mutant and k == 'd'))
out.append('LOST ' + ' '.join('%s=%d' % kv for kv in lost.items()))
if a.mutant:
    out.append('MUTANT %s: member 595(e)(1) %s -> %s' % (a.tag, 'PASS' if member else 'FAIL',
                                                       'CAUGHT' if not member else 'NOT CAUGHT'))
else:
    out.append('ALL OK' if member else 'MEMBER FAILED')
open('%s/summary_%s.txt' % (RUNS, a.tag), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
