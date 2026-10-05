"""Track F link F16q (HPP-597; ROADMAP s122 items 504 (zh)-(z), 507 (v)-(g), 515 (v)): the two pairs of witness - pair A f5cmu_0b /
f5cmu_1b (branch 1 repeat, limit 1024) and pair B f26_0 / f26_1 (F26) - the matching of the events of both arms and the lead's sheets by
present number.  Rows only, no verdict (the reading is F16r's, HPP-598).
usage: python f16q_pair.py <cmu|f26> [--sheets <out dir>] [--json <out>]   (reads runs/<tag>/read.json and rec_<tag>.mp4(.idx) of both arms)
       python f16q_pair.py <cmu|f26> --json0 <a> --json1 <b> --idx0 <a> --idx1 <b> [--sheets <dir> --rec0 <mp4> --rec1 <mp4>]  (fixtures)
Definitions (the seal docs/track-f/f16q.md section 5):
  cmask items     pair A: the DiagF5Ev cmask_fce / cmask_fce_nohit lines matched by order and (kind, image, cmask, extent) as in F16m
                  (item 492 (e)(2)); a nohit event of arm 1 has no line partner at =0 by code (item 502 (a)): NOHIT_ARM1, arm 0 frames at the
                  same present numbers.
  dcc items       pair B (item 504 (zh)): the dcc_stale lines matched by order and (site, image, dcc) - the k-th event of a key in arm 0 with
                  the k-th event of the same key in arm 1; pair A (item 507 (g), RC2): by order, (site, image, dcc) and fix (both off); the
                  field exact is not compared between the arms (f5cmu_1b reads the ring on the DCC sites - read only, the decision is the
                  old one; f5cmu_0b does not).
  reading class   pair B, the arm 1 event (item 504 (z) with 507 (v) and 515 (v)): site=adopt fix=kept why=deferred with the dcc_stale_apply
                  line of the same n result=cleared and present and gpu equal to the event - kept_applied, window by the present of the
                  apply line; result=cleared with present or gpu different - kept (apply_late); result=declined - kept (declined); no apply
                  line of the n to the end of the log - kept (no apply line); any other event - its fix.
  window          item 495 (g): presents p - 1 .. p + 2 of each event in each arm; the sheet shows both arms aligned by present number over
                  W = [min(p0, p1) - 1, max(p0, p1) + 2]; a present of W absent from an arm's .idx is listed; 'p in idx' per arm.
  skips near      item 502 (v), 504 (z): the lines 'AsyncPipelines|BindFloor: skipped draw ... frame=<f>' of each arm log with f in
                  [gpu - 1, gpu + 3] of that arm's event (arm 1 adopt with an apply line: also of the apply line's gpu); printed per item.
  glitches        the one-frame glitches of both arms (s51_vidglitch.py 'present N'); a glitch only in arm 1 inside W - GLITCH_ONLY_1.
  sheets          runs/pair_<cmu|f26>/sheets/: pair B - event_NNN_<class>.png for EVERY dcc item; pair A - event_NNN_<kind>.png for every
                  cmask item whose arm 1 fix is not fresh, every NOHIT_ARM1 and every UNPAIRED item (VARIANT OF THE EXECUTOR: a fresh
                  event of arm 1 carries no reading of item 504 (z); all items are printed as rows); aligned_<tag>.png of each arm - 48
                  presents evenly over the common present range.  Frames are taken by the video frame number of the .idx, ffmpeg in
                  chunks of 300 frames per pass.
ASCII output only; sheets by ffmpeg and PIL."""
import json, os, subprocess, sys

G = 'C:/kyty/f287/f16q'
ARMS = {'cmu': ('f5cmu_0b', 'f5cmu_1b'), 'f26': ('f26_0', 'f26_1')}
CHUNK = 300


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


def key_cmask(e):
    return (e['kind'], e['image'], e['cmask'], e['extent'])


def key_dcc_b(e):
    return (e['site'], e['image'], e['dcc'])


def key_dcc_a(e):
    return (e['site'], e['image'], e['dcc'], e['fix'])


def match(ev0, ev1, key):
    """Pairs by key occurrence (the k-th of a key with the k-th); returns pairs [(i0, i1)], unpaired lists and order flag."""
    occ0, occ1 = {}, {}
    for i, e in enumerate(ev0):
        occ0.setdefault(key(e), []).append(i)
    for i, e in enumerate(ev1):
        occ1.setdefault(key(e), []).append(i)
    pairs = []
    for k, l0 in occ0.items():
        for a, b in zip(l0, occ1.get(k, [])):
            pairs.append((a, b))
    pairs.sort()
    p0 = set(a for a, _ in pairs)
    p1 = set(b for _, b in pairs)
    un0 = [i for i in range(len(ev0)) if i not in p0]
    un1 = [i for i in range(len(ev1)) if i not in p1]
    order = all(pairs[i][1] < pairs[i + 1][1] for i in range(len(pairs) - 1))
    return pairs, un0, un1, order


def window(p0, p1):
    return list(range(min(p0, p1) - 1, max(p0, p1) + 2 + 1))


def near(skips, gpus):
    return sorted(set(s[2] for s in skips for g in gpus if g is not None and g - 1 <= s[2] <= g + 3))


def apply_of(r1):
    m = {}
    for a in r1.get('apply') or []:
        m.setdefault(a['n'], a)
    return m


def reading_class(e1, applies):
    """item 504 (z), 507 (v), 515 (v): the reading class of an arm 1 dcc event and its apply line (or None)."""
    if e1 is None:
        return None, None
    if e1['site'] == 'adopt' and e1['fix'] == 'kept' and e1.get('why') == 'deferred':
        a = applies.get(e1['n'])
        if a is None:
            return 'kept_no_apply', None
        if a['result'] == 'declined':
            return 'kept_declined', a
        if a['present'] != e1['present'] or a['gpu'] != e1['gpu']:
            return 'kept_apply_late', a
        return 'kept_applied', a
    return e1['fix'], None


def items_of(ev0, ev1, key, mode, r0, r1, idx0, idx1):
    pairs, un0, un1, order = match(ev0, ev1, key)
    g0 = set(r0.get('glitch_presents') or [])
    g1 = set(r1.get('glitch_presents') or [])
    sk0, sk1 = r0.get('skips') or [], r1.get('skips') or []
    applies = apply_of(r1) if mode == 'dcc_b' else {}
    raw = [('PAIR', ev0[a], ev1[b]) for a, b in pairs]
    nohit_un1 = [i for i in un1 if ev1[i]['kind'] == 'nohit'] if mode == 'cmask' else []
    raw += [('NOHIT_ARM1', None, ev1[i]) for i in nohit_un1]
    raw += [('UNPAIRED_0', ev0[i], None) for i in un0]
    raw += [('UNPAIRED_1', None, ev1[i]) for i in un1 if i not in nohit_un1]
    out = []
    for kind, e0, e1 in raw:
        cls, ap = reading_class(e1, applies) if mode == 'dcc_b' else ((e1['fix'] if e1 else None), None)
        p0 = e0['present'] if e0 else None
        p1 = e1['present'] if e1 else None
        if ap is not None and cls == 'kept_applied':
            p1 = ap['present']
        if p0 is None:
            p0 = p1
        if p1 is None:
            p1 = p0
        W = window(p0, p1)
        gpu0 = e0['gpu'] if e0 else (e1['gpu'] if e1 else None)
        gpu1 = [e1['gpu'] if e1 else gpu0] + ([ap['gpu']] if ap else [])
        out.append(dict(kind=kind, e0=e0, e1=e1, p0=p0, p1=p1, W=W, cls=cls, apply=ap,
                        p_in0=idx0 is not None and (e0 is None or e0['present'] in idx0),
                        p_in1=idx1 is not None and (e1 is None or e1['present'] in idx1),
                        miss0=[q for q in W if idx0 is None or q not in idx0], miss1=[q for q in W if idx1 is None or q not in idx1],
                        gl0=sorted(g0 & set(W)), gl1=sorted(g1 & set(W)), gl_only1=sorted((g1 - g0) & set(W)),
                        skip0=near(sk0, [gpu0]), skip1=near(sk1, gpu1),
                        fix1=e1['fix'] if e1 else None, why1=e1.get('why') if e1 else None, fix0=e0['fix'] if e0 else None,
                        exact0=e0.get('exact') if e0 else None, exact1=e1.get('exact') if e1 else None))
    return dict(pairs=len(pairs), unpaired0=len(un0), unpaired1=len(un1), nohit_arm1=len(nohit_un1), order=order, items=out,
                n0=len(ev0), n1=len(ev1))


def build(which, r0, r1, idx0, idx1):
    res = dict(which=which, tags=ARMS[which])
    if which == 'cmu':
        res['cmask'] = items_of(r0['events'], r1['events'], key_cmask, 'cmask', r0, r1, idx0, idx1)
        res['dcc'] = items_of(r0['dcc'], r1['dcc'], key_dcc_a, 'dcc_a', r0, r1, idx0, idx1)
    else:
        res['dcc'] = items_of(r0['dcc'], r1['dcc'], key_dcc_b, 'dcc_b', r0, r1, idx0, idx1)
        res['cmask_counts'] = (len(r0.get('events') or []), len(r1.get('events') or []))
        cls = {}
        for it in res['dcc']['items']:
            if it['cls'] is not None:
                cls[it['cls']] = cls.get(it['cls'], 0) + 1
        res['classes'] = cls
    return res


def sheet_items(res):
    if res['which'] == 'f26':
        return [('dcc', n, it) for n, it in enumerate(res['dcc']['items'], 1)]
    return [('cmask', n, it) for n, it in enumerate(res['cmask']['items'], 1) if it['kind'] != 'PAIR' or it['fix1'] != 'fresh']


def frames(rec, indices, outdir, label):
    """ffmpeg passes of CHUNK frames: the frames of the given video indices as PNG; returns {index: path}."""
    idx = sorted(set(indices))
    if not idx or not rec or not os.path.exists(rec):
        return {}
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for c in range(0, len(idx), CHUNK):
        part = idx[c:c + CHUNK]
        expr = '+'.join('eq(n\\,%d)' % i for i in part)
        pat = os.path.join(outdir, '%s_c%03d_%%05d.png' % (label, c // CHUNK))
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', rec, '-vf', "select='%s',scale=320:-1" % expr,
                        '-fps_mode', 'passthrough', pat], capture_output=True)
        for k, i in enumerate(part, 1):
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
    t0, t1 = res['tags']
    its = sheet_items(res)
    need0, need1 = [], []
    for _, _, it in its:
        need0 += [idx0[q] for q in it['W'] if q in idx0]
        need1 += [idx1[q] for q in it['W'] if q in idx1]
    common = min(max(idx0), max(idx1)) if idx0 and idx1 else 0
    grid = [max(1, common * k // 48) for k in range(1, 49)]
    need0 += [idx0[q] for q in grid if q in idx0]
    need1 += [idx1[q] for q in grid if q in idx1]
    f0 = frames(rec0, need0, os.path.join(outdir, 'fr0'), 'a0')
    f1 = frames(rec1, need1, os.path.join(outdir, 'fr1'), 'a1')
    made = []
    for view, n, it in its:
        r0 = [('p%d' % q, f0.get(idx0.get(q, -1))) for q in it['W']]
        r1 = [('p%d' % q, f1.get(idx1.get(q, -1))) for q in it['W']]
        lab = (it['cls'] or it['kind']).lower() if view == 'dcc' else it['kind'].lower()
        p = os.path.join(outdir, 'event_%03d_%s.png' % (n, lab))
        compose([r0, r1], p, [t0, t1])
        made.append(p)
    for t, ff, ix in ((t0, f0, idx0), (t1, f1, idx1)):
        rows_ = [[('p%d' % q, ff.get(ix.get(q, -1))) for q in grid[i:i + 8]] for i in range(0, 48, 8)]
        p = os.path.join(outdir, 'aligned_%s.png' % t)
        compose(rows_, p, [t] * 6)
        made.append(p)
    return made, len(f0), len(f1), len(set(need0)), len(set(need1)), len(its)


def fmt(e):
    if e is None:
        return '-'
    if e['kind'] == 'dcc':
        return 'dcc_stale site=%s n=%d present=%d gpu=%d image=0x%s dcc=0x%s extent=%s exact=%s fix=%s%s %s' % (
            e['site'], e['n'], e['present'], e['gpu'], e['image'], e['dcc'], e['extent'], e['exact'], e['fix'],
            ' why=%s' % e['why'] if e.get('why') else '', 'scene' if e['scene'] else 'before')
    return '%s n=%d present=%d gpu=%d image=0x%s cmask=0x%s extent=%s fix=%s%s %s' % (
        e['kind'], e['n'], e['present'], e['gpu'], e['image'], e['cmask'], e['extent'], e['fix'],
        ' why=%s' % e['why'] if e.get('why') else '', 'scene' if e['scene'] else 'before')


def item_rows(view, part):
    out = []
    for n, it in enumerate(part['items'], 1):
        out.append('  %s ITEM %03d %s class_arm1=%s fix_arm1=%s why_arm1=%s fix_arm0=%s window presents %d..%d' % (
            view, n, it['kind'], it['cls'], it['fix1'], it['why1'] or '-', it['fix0'], it['W'][0], it['W'][-1]))
        out.append('    arm0: %s' % fmt(it['e0']))
        out.append('    arm1: %s' % fmt(it['e1']))
        if it['apply'] is not None:
            a = it['apply']
            out.append('    arm1 apply: n=%d present=%d gpu=%d result=%s layers=0x%s (event present=%d gpu=%d)%s' % (
                a['n'], a['present'], a['gpu'], a['result'], a['layers'], it['e1']['present'], it['e1']['gpu'],
                ' APPLY_LATE' if it['cls'] == 'kept_apply_late' else ''))
        out.append('    p in idx: arm0 %s arm1 %s; window presents absent from idx: arm0 %s arm1 %s' % (
            'YES' if it['p_in0'] else 'NO', 'YES' if it['p_in1'] else 'NO', it['miss0'], it['miss1']))
        out.append('    skipped draw frames in [gpu-1, gpu+3]: arm0 %s arm1 %s' % (it['skip0'] or 'none', it['skip1'] or 'none'))
        out.append('    glitches in the window: arm0 %s arm1 %s; GLITCH_ONLY_1 %s' % (it['gl0'], it['gl1'], it['gl_only1'] or 'none'))
    return out


def head(view, part):
    return '%s events arm0 %d arm1 %d; pairs %d; unpaired arm0 %d arm1 %d (of them nohit of arm 1 %d); order kept %s' % (
        view, part['n0'], part['n1'], part['pairs'], part['unpaired0'], part['unpaired1'], part['nohit_arm1'],
        'YES' if part['order'] else 'NO')


def rows(res):
    t0, t1 = res['tags']
    out = ['F16Q PAIR %s arms %s / %s' % (res['which'], t0, t1)]
    if res['which'] == 'cmu':
        out.append('  NOTE: %s reads the ring on the DCC sites (read only, the decision is the old one), %s does not (item 507 (g)); '
                   'the field exact is not compared' % (t1, t0))
        out.append('  ' + head('CMASK', res['cmask']))
        out += item_rows('CMASK', res['cmask'])
        out.append('  ' + head('DCC (key site, image, dcc, fix)', res['dcc']))
        out += item_rows('DCC', res['dcc'])
    else:
        out.append('  ' + head('DCC (key site, image, dcc)', res['dcc']))
        out.append('  reading classes of arm 1: %s; cmask event lines arm0 %d arm1 %d (reference)' % (
            ' '.join('%s=%d' % kv for kv in sorted(res['classes'].items())) or 'none', res['cmask_counts'][0], res['cmask_counts'][1]))
        out += item_rows('DCC', res['dcc'])
    return out


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv):
    which = argv[0] if argv else ''
    if which not in ARMS:
        raise SystemExit('usage: f16q_pair.py <cmu|f26> ...')
    t0, t1 = ARMS[which]
    j0 = arg(argv, '--json0', os.path.join(G, 'runs', t0, 'read.json'))
    j1 = arg(argv, '--json1', os.path.join(G, 'runs', t1, 'read.json'))
    i0 = arg(argv, '--idx0', os.path.join(G, 'rec_%s.mp4.idx' % t0))
    i1 = arg(argv, '--idx1', os.path.join(G, 'rec_%s.mp4.idx' % t1))
    r0, r1 = json.load(open(j0)), json.load(open(j1))
    idx0, idx1 = load_idx(i0), load_idx(i1)
    res = build(which, r0, r1, idx0, idx1)
    for x in rows(res):
        print(x.encode('ascii', 'replace').decode('ascii'))
    out = arg(argv, '--sheets')
    if out:
        rec0 = arg(argv, '--rec0', os.path.join(G, 'rec_%s.mp4' % t0))
        rec1 = arg(argv, '--rec1', os.path.join(G, 'rec_%s.mp4' % t1))
        made, n0, n1, w0, w1, ni = sheets(res, idx0 or {}, idx1 or {}, rec0, rec1, out)
        print('SHEETS items with an event sheet %d; frames extracted arm0 %d of %d arm1 %d of %d; files %d' % (ni, n0, w0, n1, w1,
                                                                                                         len(made)))
        for p in made:
            print('  SHEET %s' % p)
    if '--json' in argv:
        json.dump(res, open(arg(argv, '--json'), 'w'), indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
