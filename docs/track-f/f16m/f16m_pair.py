"""Track F link F16m (HPP-585; ROADMAP s122 item 492 (e)(2)-(6), item 495 (g), item 496 (b)(5)): the pair of witness f5cmu_0 / f5cmu_1 - the
matching of the events of both arms and the lead's sheet list by present number.  Rows only, no verdict (the reading is F16n's).
usage: python f16m_pair.py [--sheets <out dir>]          (reads runs/f5cmu_0/read.json, runs/f5cmu_1/read.json, rec_<tag>.mp4.idx)
       python f16m_pair.py --json0 <a> --json1 <b> --idx0 <a> --idx1 <b> [--sheets <dir> --rec0 <mp4> --rec1 <mp4>]   (fixtures)
Definitions (the seal docs/track-f/f16m.md section 5):
  events          the DiagF5Ev lines of both kinds (cmask_fce, cmask_fce_nohit; item 496 (b)(5): nohit enters the pair as cmask_fce does).
  matching        item 492 (e)(2): by order and (image, cmask, extent) - the k-th event of a key in arm 0 pairs with the k-th event of the same
                  key and kind in arm 1; 'order kept' = the arm 1 positions of the pairs grow with the arm 0 positions.  An event without a
                  partner is printed UNPAIRED.  A cmask_fce_nohit line exists only at KYTY_FIX_F5CMU=1 (fix not in {off, fresh}); at =0 the
                  code prints no such line (fix=off): a nohit event of arm 1 has no line partner in arm 0 by code - VARIANT OF THE EXECUTOR
                  (question to the lead in the seal): its arm 0 frames are taken at the same present numbers as in arm 1.
  window          item 495 (g): the presents p - 1, p, p + 1, p + 2 of each event in each arm; the sheet of a pair shows both arms aligned by
                  present number over W = [min(p0, p1) - 1, max(p0, p1) + 2] (both arms' windows; arms aligned by present, not by time).
  in idx          item 492 (e)(2): an event whose present number p is absent from the .idx of either arm - 'p not in idx' row (the reading
                  'not determined' is F16n's); each window present absent from an arm's idx is listed.
  glitches        the one-frame glitches of both arms (s51_vidglitch.py lines 'present N'); a glitch only in arm 1 inside W of an event is
                  printed GLITCH_ONLY_1 (item 492 (e)(6): a difference of (4)).
  aligned sheet   the whole-video sheets of both arms sampled at the same present numbers (48 presents evenly over the common present
                  range), arm 0 left, arm 1 right - for the lead's look at differences outside the windows (item 492 (e)(6)).
ASCII output only; sheets by ffmpeg (one pass per arm) and PIL."""
import json, os, subprocess, sys

G = 'C:/kyty/f287/f16m'


def load_idx(path):
    m = {}
    if not path or not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        for raw in f:
            parts = raw.split()
            if len(parts) >= 2:
                pr = int(parts[1])
                if pr not in m:
                    m[pr] = int(parts[0])
    return m


def key(e):
    return (e['kind'], e['image'], e['cmask'], e['extent'])


def match(ev0, ev1):
    """Pairs by (kind, image, cmask, extent) occurrence; returns pairs [(i0, i1)], unpaired lists and order flag."""
    occ0, occ1 = {}, {}
    for i, e in enumerate(ev0):
        occ0.setdefault(key(e), []).append(i)
    for i, e in enumerate(ev1):
        occ1.setdefault(key(e), []).append(i)
    pairs = []
    for k, l0 in occ0.items():
        l1 = occ1.get(k, [])
        for a, b in zip(l0, l1):
            pairs.append((a, b))
    pairs.sort()
    p1 = set(b for _, b in pairs)
    p0 = set(a for a, _ in pairs)
    un0 = [i for i in range(len(ev0)) if i not in p0]
    un1 = [i for i in range(len(ev1)) if i not in p1]
    order = all(pairs[i][1] < pairs[i + 1][1] for i in range(len(pairs) - 1))
    return pairs, un0, un1, order


def window(p0, p1):
    lo = min(p0, p1) - 1
    hi = max(p0, p1) + 2
    return list(range(lo, hi + 1))


def build(r0, r1, idx0, idx1):
    ev0 = [e for e in r0['events']]
    ev1 = [e for e in r1['events']]
    pairs, un0, un1, order = match(ev0, ev1)
    g0 = set(r0.get('glitch_presents') or [])
    g1 = set(r1.get('glitch_presents') or [])
    items = []
    for a, b in pairs:
        items.append(('PAIR', ev0[a], ev1[b]))
    nohit_un1 = [i for i in un1 if ev1[i]['kind'] == 'nohit']
    for i in nohit_un1:
        items.append(('NOHIT_ARM1', None, ev1[i]))
    for i in un0:
        items.append(('UNPAIRED_0', ev0[i], None))
    for i in un1:
        if i not in nohit_un1:
            items.append(('UNPAIRED_1', None, ev1[i]))
    out = []
    for kind, e0, e1 in items:
        p0 = e0['present'] if e0 else None
        p1 = e1['present'] if e1 else None
        if p0 is None:
            p0 = p1
        if p1 is None:
            p1 = p0
        W = window(p0, p1)
        miss0 = [q for q in W if idx0 is None or q not in idx0]
        miss1 = [q for q in W if idx1 is None or q not in idx1]
        out.append(dict(kind=kind, e0=e0, e1=e1, p0=p0, p1=p1, W=W,
                        p_in0=idx0 is not None and (e0 is None or e0['present'] in idx0),
                        p_in1=idx1 is not None and (e1 is None or e1['present'] in idx1),
                        p0_in_idx1=idx1 is not None and p0 in idx1, p1_in_idx0=idx0 is not None and p1 in idx0,
                        miss0=miss0, miss1=miss1, gl0=sorted(g0 & set(W)), gl1=sorted(g1 & set(W)),
                        gl_only1=sorted((g1 - g0) & set(W)),
                        fix1=e1['fix'] if e1 else None, why1=e1['why'] if e1 else None, fix0=e0['fix'] if e0 else None))
    return dict(pairs=len(pairs), unpaired0=len(un0), unpaired1=len(un1), nohit_arm1=len(nohit_un1), order=order, items=out,
                n0=len(ev0), n1=len(ev1))


def frames(rec, indices, outdir, label):
    """One ffmpeg pass: the frames of the given video indices as PNG (sorted order); returns {index: path}."""
    idx = sorted(set(indices))
    if not idx or not rec or not os.path.exists(rec):
        return {}
    os.makedirs(outdir, exist_ok=True)
    expr = '+'.join('eq(n\\,%d)' % i for i in idx)
    pat = os.path.join(outdir, '%s_%%05d.png' % label)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', rec, '-vf', "select='%s',scale=320:-1" % expr,
                    '-fps_mode', 'passthrough', pat], capture_output=True)
    res = {}
    for k, i in enumerate(idx, 1):
        p = pat % k
        if os.path.exists(p):
            res[i] = p
    return res


def compose(rowsets, path, label_rows):
    from PIL import Image, ImageDraw
    w, h = 320, 180
    cols = max(len(r) for r in rowsets)
    img = Image.new('RGB', (cols * w, len(rowsets) * (h + 14)), (40, 40, 40))
    dr = ImageDraw.Draw(img)
    for r, row in enumerate(rowsets):
        for c, (lab, p) in enumerate(row):
            y = r * (h + 14)
            if p and os.path.exists(p):
                t = Image.open(p).convert('RGB').resize((w, h))
                img.paste(t, (c * w, y + 14))
            dr.text((c * w + 2, y), '%s %s' % (label_rows[r], lab), fill=(255, 255, 0))
    img.save(path)


def sheets(res, idx0, idx1, rec0, rec1, outdir):
    os.makedirs(outdir, exist_ok=True)
    need0, need1 = [], []
    for it in res['items']:
        need0 += [idx0[q] for q in it['W'] if q in idx0]
        need1 += [idx1[q] for q in it['W'] if q in idx1]
    common = min(max(idx0), max(idx1)) if idx0 and idx1 else 0
    grid = [max(1, common * k // 48) for k in range(1, 49)]
    need0 += [idx0[q] for q in grid if q in idx0]
    need1 += [idx1[q] for q in grid if q in idx1]
    f0 = frames(rec0, need0, os.path.join(outdir, 'fr0'), 'a0')
    f1 = frames(rec1, need1, os.path.join(outdir, 'fr1'), 'a1')
    made = []
    for n, it in enumerate(res['items'], 1):
        r0 = [('p%d' % q, f0.get(idx0.get(q, -1))) for q in it['W']]
        r1 = [('p%d' % q, f1.get(idx1.get(q, -1))) for q in it['W']]
        p = os.path.join(outdir, 'event_%02d_%s.png' % (n, it['kind'].lower()))
        compose([r0, r1], p, ['f5cmu_0', 'f5cmu_1'])
        made.append(p)
    rows0 = [[('p%d' % q, f0.get(idx0.get(q, -1))) for q in grid[i:i + 8]] for i in range(0, 48, 8)]
    rows1 = [[('p%d' % q, f1.get(idx1.get(q, -1))) for q in grid[i:i + 8]] for i in range(0, 48, 8)]
    p = os.path.join(outdir, 'aligned_f5cmu_0.png')
    compose(rows0, p, ['f5cmu_0'] * 6)
    q = os.path.join(outdir, 'aligned_f5cmu_1.png')
    compose(rows1, q, ['f5cmu_1'] * 6)
    made += [p, q]
    return made, len(f0), len(f1), len(set(need0)), len(set(need1))


def fmt(e):
    if e is None:
        return '-'
    return '%s n=%d present=%d gpu=%d image=0x%s cmask=0x%s extent=%s fix=%s%s %s' % (
        e['kind'], e['n'], e['present'], e['gpu'], e['image'], e['cmask'], e['extent'], e['fix'],
        ' why=%s' % e['why'] if e['why'] else '', 'scene' if e['scene'] else 'before')


def rows(res):
    out = ['F16M PAIR events arm0 %d arm1 %d; pairs %d; unpaired arm0 %d arm1 %d (of them nohit of arm 1 %d); order kept %s' % (
        res['n0'], res['n1'], res['pairs'], res['unpaired0'], res['unpaired1'], res['nohit_arm1'], 'YES' if res['order'] else 'NO')]
    for n, it in enumerate(res['items'], 1):
        out.append('  ITEM %02d %s fix_arm1=%s why_arm1=%s fix_arm0=%s window presents %d..%d' % (
            n, it['kind'], it['fix1'], it['why1'] or '-', it['fix0'], it['W'][0], it['W'][-1]))
        out.append('    arm0: %s' % fmt(it['e0']))
        out.append('    arm1: %s' % fmt(it['e1']))
        out.append('    p in idx: arm0 %s arm1 %s; window presents absent from idx: arm0 %s arm1 %s' % (
            'YES' if it['p_in0'] else 'NO', 'YES' if it['p_in1'] else 'NO', it['miss0'], it['miss1']))
        out.append('    glitches in the window: arm0 %s arm1 %s; GLITCH_ONLY_1 %s' % (it['gl0'], it['gl1'], it['gl_only1'] or 'none'))
    return out


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv):
    j0 = arg(argv, '--json0', os.path.join(G, 'runs', 'f5cmu_0', 'read.json'))
    j1 = arg(argv, '--json1', os.path.join(G, 'runs', 'f5cmu_1', 'read.json'))
    i0 = arg(argv, '--idx0', os.path.join(G, 'rec_f5cmu_0.mp4.idx'))
    i1 = arg(argv, '--idx1', os.path.join(G, 'rec_f5cmu_1.mp4.idx'))
    r0, r1 = json.load(open(j0)), json.load(open(j1))
    idx0, idx1 = load_idx(i0), load_idx(i1)
    res = build(r0, r1, idx0, idx1)
    for x in rows(res):
        print(x.encode('ascii', 'replace').decode('ascii'))
    out = arg(argv, '--sheets')
    if out:
        rec0 = arg(argv, '--rec0', os.path.join(G, 'rec_f5cmu_0.mp4'))
        rec1 = arg(argv, '--rec1', os.path.join(G, 'rec_f5cmu_1.mp4'))
        made, n0, n1, w0, w1 = sheets(res, idx0 or {}, idx1 or {}, rec0, rec1, out)
        print('SHEETS frames extracted arm0 %d of %d arm1 %d of %d; files %d' % (n0, w0, n1, w1, len(made)))
        for p in made:
            print('  SHEET %s' % p)
    if '--json' in argv:
        json.dump(res, open(arg(argv, '--json'), 'w'), indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
