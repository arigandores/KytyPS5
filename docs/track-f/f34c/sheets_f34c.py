"""Track F link F34c (HPP-740; F34a section 5.3 (V4), ROADMAP s122 item 676 (v)): the sheets of a V tag of the B6 series for the lead.
Port of the F34a scripts docs/track-f/f34a/sheet.py and pair.py (frames chosen by the present of the .idx of KYTY_REC).

    python sheets_f34c.py <rec.mp4> <timeline.json> <out dir> <tag>

  room_<tag>.png     the room window: present in timeline sheet_p (vn: [P_intro + 2880; P_intro + 3330], vl: [n_intro + 2880;
                     n_intro + 3355]) step 10, tiles 384x216, 8 columns
  big_<tag>.png      four frames 960x540 at timeline big_p (+2950, +3050, +3150, +3250), 2x2
  cut_<tag>.png      the whole cutscene (timeline cut_p) step 100, tiles 256x144, 8 columns (reference)
  pair_<tag>.png     reference rows at the same offsets +2950 .. +3250: the tag, u_02 (FS8, -lvl intro_next, entry present 235), rec_e
                     (session 30, natural start, entry present 2620) - as F34a pair.py
A wanted present without an .idx record within +-3 is printed 'missing' and skipped.  Prints ASCII only; the last line 'sheets done' or
'sheets FAILED <why>'.
"""
import json
import os
import subprocess
import sys

REFS = (('u_02', 'C:/kyty/s288/s15/rec_u_02.mp4', 235), ('rec_e', 'C:/kyty/s30/rec_e.mp4', 2620))
BIG = (2950, 3050, 3150, 3250)
NEAR = 3


def idx_map(mp4):
    out = {}
    for l in open(mp4 + '.idx', 'rb'):
        p = l.split()
        if len(p) >= 2:
            out.setdefault(int(p[1]), int(p[0]))
    return out


def pick(p2f, wanted):
    pres = sorted(p2f)
    got, miss = [], []
    import bisect
    for w in wanted:
        i = bisect.bisect_left(pres, w)
        best = None
        for j in (i - 1, i):
            if 0 <= j < len(pres) and (best is None or abs(pres[j] - w) < abs(best - w)):
                best = pres[j]
        if best is not None and abs(best - w) <= NEAR:
            got.append((w, best, p2f[best]))
        else:
            miss.append(w)
    return got, miss


def tile(mp4, frames, out, w, h, cols):
    if not frames:
        return 'no frames'
    rows = (len(frames) + cols - 1) // cols
    sel = '+'.join('eq(n' + chr(92) + ',%d)' % f for f in frames)
    vf = "select='%s',scale=%d:%d,tile=%dx%d" % (sel, w, h, cols, rows)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vf', vf, '-vsync', '0', '-frames:v', '1', out],
                       capture_output=True, text=True)
    return 'rc %d %s' % (r.returncode, r.stderr.strip()[-160:].encode('ascii', 'replace').decode())


def main(argv):
    if len(argv) < 5:
        print('usage: sheets_f34c.py <rec.mp4> <timeline.json> <out dir> <tag>')
        return 2
    mp4, tl, od, tag = argv[1], json.load(open(argv[2], encoding='ascii')), argv[3], argv[4]
    if not tl or not tl.get('sheet_p'):
        print('sheets FAILED no sheet window in the timeline (%s)' % (None if not tl else tl.get('n_intro')))
        return 1
    p2f = idx_map(mp4)
    lo, hi = int(round(tl['sheet_p'][0])), int(round(tl['sheet_p'][1]))
    got, miss = pick(p2f, list(range(lo, hi + 1, 10)))
    print('room window present [%d; %d] step 10: %d tiles, missing %s' % (lo, hi, len(got), miss))
    print('room tiles (present wanted, present, video frame): %s' % got)
    print('room: %s' % tile(mp4, [f for _, _, f in got], os.path.join(od, 'room_%s.png' % tag), 384, 216, 8))
    big, bmiss = pick(p2f, [int(round(v)) for v in tl['big_p']])
    print('big frames %s missing %s: %s' % (big, bmiss, tile(mp4, [f for _, _, f in big], os.path.join(od, 'big_%s.png' % tag), 960, 540, 2)))
    if tl.get('cut_p'):
        c0, c1 = int(round(tl['cut_p'][0])), int(round(tl['cut_p'][1]))
        cut, cmiss = pick(p2f, list(range(c0, c1 + 1, 100)))
        print('cutscene [%d; %d] step 100: %d tiles, missing %d: %s' % (c0, c1, len(cut), len(cmiss),
                                                                    tile(mp4, [f for _, _, f in cut], os.path.join(od, 'cut_%s.png' % tag), 256, 144, 8)))
    p0 = int(round(tl['big_p'][0])) - BIG[0]
    rows = []
    for name, src, e in (('tag', mp4, p0),) + REFS:
        if not os.path.exists(src + '.idx'):
            print('pair row %s: no %s' % (name, src))
            continue
        g, ms = pick(idx_map(src), [e + b for b in BIG])
        o = os.path.join(od, 'pair_row_%s_%s.png' % (tag, name))
        print('pair row %s entry present %d frames %s missing %s: %s' % (name, e, g, ms, tile(src, [f for _, _, f in g], o, 384, 216, 4)))
        if os.path.exists(o):
            rows.append(o)
    if len(rows) >= 2:
        args = ['ffmpeg', '-v', 'error', '-y']
        for o in rows:
            args += ['-i', o]
        args += ['-filter_complex', 'vstack=inputs=%d' % len(rows), os.path.join(od, 'pair_%s.png' % tag)]
        r = subprocess.run(args, capture_output=True, text=True)
        print('pair: %s rows %d rc %d' % (os.path.join(od, 'pair_%s.png' % tag), len(rows), r.returncode))
    ok = os.path.exists(os.path.join(od, 'room_%s.png' % tag)) and os.path.exists(os.path.join(od, 'big_%s.png' % tag))
    print('sheets done' if ok else 'sheets FAILED room or big image missing')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
