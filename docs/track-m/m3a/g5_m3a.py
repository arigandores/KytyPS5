"""Track M link M3a (HPP-842; ROADMAP s122 item 756 (g)(5)): the G5 rows of the ABBA m3_g5_a1, m3_g5_b1, m3_g5_b2, m3_g5_a2 (A = FS15
bfac84be on K0, B = MS1 ea35b679 on K1, Sky Garden, V form 330 s) from their read.json (m3a_read.py).  NO VERDICT on a theme; the word of
the letter of item 756 (g)(5) is printed for M3b:
  delta = (sum mean B - sum mean A) / sum mean A over the measure 'end A' (mean dt_us from the first scene frame + 30 s to the last
  FrameTrace row before 'Event: quit'); the measure 'end B' (all rows after + 30 s) is printed beside it (the variant of the end).
  NOT_WORSE  delta <= +1.0 % (BETTER beside it when delta <= -1.0 %, a reference, not a goal)
  FAIL       delta > +1.0 %  (the culprit theme - the arm without T233 first: m3_g5_t2330p then m3_g5_t2330, seal section 3)
  NOT_EVALUABLE  any of the four not ADMITTED or without the measure.
Rows: each arm mean / n / sd / SE, FPS = 1e6 / mean and 'game speed' 16 667 / mean (60 FPS not promised); 2SE of the delta from the arm
SE (frames are autocorrelated - a row, not a test); the spread inside the arms |A1 - A2| / mean A and |B1 - B2| / mean B (the honest
noise of a 330 s run); the vblank step: the arms' share of frames is not read here.  Optional --culprit: delta of m3_g5_t2330 against
the A arms.  ASCII only.  usage: python g5_m3a.py [--runs <dir>] [--culprit]"""
import json
import math
import os
import sys

G = 'C:/kyty/m657/m3a'
ARMS = (('A', 'm3_g5_a1'), ('B', 'm3_g5_b1'), ('B', 'm3_g5_b2'), ('A', 'm3_g5_a2'))
LIMIT = 0.010


def arm(rd, tag, end):
    js = os.path.join(rd, tag, 'read.json')
    if not os.path.exists(js):
        return None, 'no read.json'
    r = json.load(open(js, encoding='utf-8'))
    if not r.get('admitted'):
        return None, 'not admitted: %s' % r.get('interference')
    m = ((r.get('g5') or {}).get(end) or {})
    if not m.get('n'):
        return None, 'no measure'
    return m, 'ok bin %s members %s' % (r.get('bin'), 'ALL YES' if r.get('ok') else 'NOT ALL YES')


def word(delta):
    if delta is None:
        return 'NOT_EVALUABLE'
    if delta > LIMIT:
        return 'FAIL'
    return 'NOT_WORSE' + (' (BETTER, a reference)' if delta <= -LIMIT else '')


def block(rd, end, out):
    vals = []
    for side, tag in ARMS:
        m, why = arm(rd, tag, end)
        vals.append((side, tag, m))
        if m:
            out('  %s %s: mean %.2f us, n %d, sd %.1f, SE %.3f, FPS %.3f, speed %.4f; %s' % (
                side, tag, m['mean'], m['n'], m['sd'], m['se'], 1e6 / m['mean'], 16667.0 / m['mean'], why))
        else:
            out('  %s %s: %s' % (side, tag, why))
    if any(m is None for _, _, m in vals):
        out('  delta: NOT_EVALUABLE')
        return None
    sa = sum(m['mean'] for s, _, m in vals if s == 'A')
    sb = sum(m['mean'] for s, _, m in vals if s == 'B')
    se = math.sqrt(sum(m['se'] ** 2 for _, _, m in vals))
    delta = (sb - sa) / sa
    a = [m['mean'] for s, _, m in vals if s == 'A']
    b = [m['mean'] for s, _, m in vals if s == 'B']
    out('  sum A %.2f, sum B %.2f; delta %+.4f %% (2SE from the arm SE %.4f %%); spread A |A1-A2|/mean %.4f %%, B |B1-B2|/mean %.4f %%' % (
        sa, sb, 100 * delta, 200 * se / sa, 100 * abs(a[0] - a[1]) / (sa / 2), 100 * abs(b[0] - b[1]) / (sb / 2)))
    return delta


def main(argv):
    rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
    out = print
    out('G5 (item 756 (g)(5)): ABBA %s; limit +1.0 %%' % ' '.join(t for _, t in ARMS))
    out('MEASURE end A (the letter: to the end of the hold - rows before Event: quit):')
    da = block(rd, 'end_a', out)
    out('MEASURE end B (variant: every row after + 30 s, the exit frames included):')
    db = block(rd, 'end_b', out)
    out('G5 WORD end A %s (delta %s); end B %s (delta %s)' % (word(da), 'n/a' if da is None else '%+.4f %%' % (100 * da), word(db),
                                                            'n/a' if db is None else '%+.4f %%' % (100 * db)))
    if '--culprit' in argv:
        m, why = arm(rd, 'm3_g5_t2330', 'end_a')
        a = [arm(rd, t, 'end_a')[0] for s, t in ARMS if s == 'A']
        if m and all(a):
            ma = sum(x['mean'] for x in a) / 2
            out('CULPRIT ARM m3_g5_t2330 (T233=0) delta against the A arms %+.4f %% (%s)' % (100 * (m['mean'] - ma) / ma, why))
        else:
            out('CULPRIT ARM m3_g5_t2330: NOT_EVALUABLE (%s)' % why)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
