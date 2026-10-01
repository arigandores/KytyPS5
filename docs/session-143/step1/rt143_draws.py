"""rt143_draws.py - Red Team s143 step 1 (HPP-298): how close the s142 scenes come to the --stable-draws 300 threshold of
V/W (p.239(b)(1)).  Per log: first scene frame (draws >= 100 after the entry line), draws percentiles of the 600 rows after
it and of all rows after it, the share of rows with draws < 300, and the frame where 90 consecutive rows >= 300 / >= 100
first come after the entry line.  Binary streaming read via sc143.scan.  ASCII output."""
import sys

sys.path.insert(0, 'C:/kyty/s143')
import sc143 as S

LOGS = [('v142', 'underwater_aerial_garden')] + list(S.CENSUS142)


def first_run(rows, thr, n=90):
    run = 0
    for r in rows:
        run = run + 1 if r[2] >= thr else 0
        if run >= n:
            return r[0]
    return None


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


for tag, lv in LOGS:
    sc = S.scan('C:/kyty/s142/log_%s.txt' % tag)
    ent = [p for name, p in sc['starts'] if name == lv]
    if not ent:
        print('%s no entry' % tag)
        continue
    after = [r for r in sc['rows'] if r[3] > ent[0]]
    fi = next((i for i, r in enumerate(after) if r[2] >= 100), None)
    post = after[fi + 1:]
    d600 = [r[2] for r in post[:600]]
    dall = [r[2] for r in post]
    lo = sum(1 for x in dall if x < 300)
    print('%s %s sha %s first n %s; draws first600 p1 %s p10 %s p50 %s; all p1 %s p50 %s min %s; rows < 300: %d of %d; '
          '90-run >=300 at n %s, >=100 at n %s' % (
              tag, lv, sc['sha256'][:16], after[fi][0], pct(d600, 0.01), pct(d600, 0.1), pct(d600, 0.5), pct(dall, 0.01),
              pct(dall, 0.5), min(dall), lo, len(dall), first_run(after, 300), first_run(after, 100)))
