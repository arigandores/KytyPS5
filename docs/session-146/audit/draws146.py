# draws146.py - Session Auditor s146 step 3 (HPP-389): data beyond the letter, own reading of the logs (mmap, binary).
#  (1) the tags NOT_EVALUABLE "no stable (timeout)": draws per FrameTrace row after the entry line against the sealed
#      "stable" rule of enter_scene.py (STABLE_FRAMES 90 consecutive rows with draws >= 300, --stable-draws 300);
#  (2) K2 frames: presented time after the first scene frame; skipped-draw lines;
#  (3) w146_08 / w146_10 / v146_08 / v146_10: draws before and after the last validation-layer line.
import re, mmap, json, statistics
A = {r['tag']: r for r in json.load(open('C:/kyty/s146/step3/aud146.json'))}
RN = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
RD = re.compile(rb' draws=(\d+)')
def rows(tag):
    out = []
    with open('C:/kyty/s146/log_%s.txt' % tag, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        p = mm.find(b'FrameTrace: n=')
        while p != -1:
            e = mm.find(b'\n', p)
            ln = mm[p:e if e != -1 else p + 400]
            m = RN.match(ln)
            d = RD.search(ln)
            if m:
                out.append((p, int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else -1))
            p = mm.find(b'FrameTrace: n=', p + 1)
        mm.close()
    return out
def runs(v, thr):
    best = cur = 0
    for x in v:
        cur = cur + 1 if x >= thr else 0
        best = max(best, cur)
    return best
for t in ('v146_09', 'w146_09', 'v146_11', 'w146_11', 'v146_12', 'w146_12', 'v146_13', 'w146_13', 'v146_08', 'w146_08', 'v146_10', 'w146_10', 'v146_07', 'v146_05'):
    L = A[t]['log']
    R = [r for r in rows(t) if r[0] > L['entry_pos']]
    dr = [r[3] for r in R]
    dts = [r[2] for r in R]
    q = sorted(dr)
    print('DRAWS %s %s: rows after the entry line %d; draws min %d, p10 %d, median %d, p90 %d, max %d; rows with draws >= 300: %d (%.1f %%), >= 100: %d; longest run of rows with draws >= 300: %d '
          '(the sealed rule needs 90); dt after entry: sum %.1f s, max %d us, rows >= 100 ms %d, >= 1 s %d' % (
              t, A[t]['level'], len(R), q[0], q[len(q) // 10], q[len(q) // 2], q[len(q) * 9 // 10], q[-1], sum(1 for x in dr if x >= 300), 100.0 * sum(1 for x in dr if x >= 300) / len(dr),
              sum(1 for x in dr if x >= 100), runs(dr, 300), sum(dts) / 1e6, max(dts), sum(1 for x in dts if x >= 100000), sum(1 for x in dts if x >= 1000000)))
    lp = L.get('layer_last_pos')
    if lp:
        b = [r[3] for r in R if r[0] <= lp]
        a = [r[3] for r in R if r[0] > lp]
        if a and b:
            print('   LAYER %s: rows up to the last validation-layer line %d (draws median %d, max %d); rows after it %d (draws median %d, min %d, max %d)' % (
                t, len(b), statistics.median_high(b), max(b), len(a), statistics.median_high(a), min(a), max(a)))
    if t in ('v146_08', 'w146_08'):
        # draws by 30 s bins of presented time after the entry line
        c = 0
        bins = {}
        for r in R:
            c += r[2]
            bins.setdefault(int(c // 30e6), []).append(r[3])
        print('   BINS %s (30 s of presented time after the entry line: median draws): %s' % (t, [statistics.median_high(v) for k, v in sorted(bins.items())]))
for t in ('r146_02', 'r146_03', 'v146_10', 'r146_01', 'r146_04', 'i146_v'):
    L = A[t]['log']
    R = [r for r in rows(t) if r[0] > L['entry_pos']]
    fi = next(k for k, r in enumerate(R) if r[3] >= 100)
    post = R[fi + 1:]
    c = 0
    ev = []
    for k, r in enumerate(post):
        c += r[2]
        if r[2] >= 100000:
            ev.append((r[1], r[2], round(c / 1e6, 2), 'entry' if k < 599 else 'hold'))
    print('SLOW %s %s: first scene frame n %d; frames >= 100 ms after it %d: %s; skipped-draw lines %s / frames %s; PriorityStall over 50 ms %s' % (
        t, A[t]['level'], R[fi][1], len(ev), ev[:12], L['skip']['lines'], L['skip']['frames_by_id'], L['prio']['over']))
print('ALL DONE')
