"""Track F link F46c (HPP-800; ROADMAP s122 item 702 (d)(1)-(4), (g)(3); item 711 (b)): the video measures of the pair series F26 -
the detector M(f), the brightness of a frame, the windows W(e), the control on the key, the visibility V(e), the difference measure d
and the lead's sheets.  Rows and numbers only, NO VERDICT and no event class (the class needs the lead's sheet, item 702 (d)(4)-(5);
the reading is F46d).  ASCII only.

    python f46c_vid.py --frames <tag> [--runs D] [--rec R --idx I]   per video frame: present, M, mean -> runs/<tag>/frames.json
    python f46c_vid.py --series [--runs D] [--no-sheets]              the event table -> runs/series/series.json, series.txt, sheets

DEFINITIONS (seal docs/track-f/f46c.md section 5; constants of item 702 (d) before the data):
  frame           a video frame decoded by ffmpeg to rgb24 at its own size; the size must be 960x540 (else a row SIZE and the frame
                  is scaled to 960x540 by ffmpeg); its present - the second column of its .idx record; a present with several video
                  frames - the first one.
  M(f)            the number of pixels with R >= 200, G <= 40, B >= 200.               theta = 500.
  mean(f)         the mean of all R, G, B bytes of the frame; an ENTRY SCREEN frame - mean <= 5.  A present is EXCLUDED from a comparison
                  when any frame of that comparison at that present is an entry screen frame.  Both readings are printed (with and
                  without the exclusion); the one WITH the exclusion counts (item 702 (d)).
  arms            per base tag the SETTLED attempt of next_f46c.py (admitted base or admitted _r1); an arm without an admitted attempt
                  - its event rows 'undetermined (arm not admitted)'.
  p(e)            the present of the dcc_stale line of S<k> in f26s_1.  p_end_x(e): the present of the f26_first_exec line of S<k> (n and
                  dcc of the event in arm x) in f26s_0 (x = 0) and f26s_1 (x = 1); no line - the end of the hold = the last present
                  of the .idx of that arm.
  W(e)            item 702 (g)(3): [p(e) - 1; min(max(p_end_0, p_end_1) + 3; p(e) + 600)] presents.
  control (1)     on f26s_c<k>: f26_tint_applied >= 1 (last DiagF5 line) and at least one present of the hold - every present common
                  to the .idx of f26s_c<k> and f26s_1 - with M_c - M_1 >= theta.  No -> event 'undetermined' (item 702 (d)(1)).
  V(e)            item 702 (d)(3): yes when a present f in W(e), common to f26s_t<k> and f26s_1 and not excluded, has M_t - M_1 >=
                  theta; W(e) without a comparable present after the exclusion - 'undetermined'.
  D(e) numbers    item 702 (d)(4), only when V = yes: mask(f) - the pixels of the f26s_t<k> frame at f passing the M test; for f in W(e)
                  with |mask| >= theta (and no excluded frame among t, 0, 1, 1b): d_x(f) = the mean over the mask of max over R, G, B
                  of |frame_x - frame_1| (0..255) for x = 0 and 1b; a CANDIDATE when d_0 - d_1b >= 16.  The member D = yes needs the
                  lead's sheet of that frame (f26s_0 / f26s_1 / f26s_1b, mask outlined) - printed, not decided here.
  exec            the execution present of S<k> in f26s_1 (kept_applied - the event present; a mark class - the present of its
                  cleared line); the row 'exec <= p(e) + 1' of item 702 (d)(5).
  sheets          runs/series/sheets/: ev<k>_cand_<present>.png - t | 0 | 1 | 1b with the mask outlined in yellow, for up to 6
                  presents of W(e) with |mask| >= theta and the largest d_0 - d_1b (the candidates first by construction);
                  ctl<k>_<present>.png - c | 1 at the present with the largest M_c - M_1.
"""
import json
import os
import subprocess
import sys

import numpy as np

G = 'C:/kyty/f287/f46c'
W0, H0 = 960, 540
THETA = 500
D_MIN = 16
DARK = 5.0
CAP = 600


def m_mask(fr):
    """item 702 (d): R >= 200, G <= 40, B >= 200 (fr - HxWx3 uint8)."""
    return (fr[:, :, 0] >= 200) & (fr[:, :, 1] <= 40) & (fr[:, :, 2] >= 200)


def m_count(fr):
    return int(m_mask(fr).sum())


def mean_of(fr):
    return float(fr.mean())


def d_measure(fr_x, fr_1, mask):
    """mean over the mask of max over channels |x - 1| (0..255); None for an empty mask."""
    n = int(mask.sum())
    if n == 0:
        return None
    diff = np.abs(fr_x.astype(np.int16) - fr_1.astype(np.int16)).max(axis=2)
    return float(diff[mask].mean())


def window(p, p_end_0, p_end_1):
    """item 702 (g)(3)."""
    return p - 1, min(max(p_end_0, p_end_1) + 3, p + CAP)


def load_idx(path):
    """present -> first video frame index; last present."""
    m = {}
    last = None
    if not path or not os.path.exists(path):
        return None, None
    with open(path, 'rb') as f:
        for raw in f:
            parts = raw.split()
            if len(parts) >= 2:
                pr = int(parts[1])
                last = pr
                if pr not in m:
                    m[pr] = int(parts[0])
    return m, last


def probe_size(rec):
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', rec],
                        capture_output=True)
    try:
        w, h = pr.stdout.decode().strip().split(',')[:2]
        return int(w), int(h)
    except ValueError:
        return None


class Reader(object):
    """Sequential rgb24 frames of one video (scaled to 960x540 only when the size differs)."""

    def __init__(self, rec):
        self.size = probe_size(rec)
        vf = [] if self.size == (W0, H0) else ['-vf', 'scale=%d:%d' % (W0, H0)]
        self.p = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', rec] + vf + ['-pix_fmt', 'rgb24', '-f', 'rawvideo',
                                                                                                     '-'], stdout=subprocess.PIPE)
        self.n = -1
        self.cur = None

    def next(self):
        b = self.p.stdout.read(W0 * H0 * 3)
        if len(b) < W0 * H0 * 3:
            self.cur = None
            return None
        self.n += 1
        self.cur = np.frombuffer(b, dtype=np.uint8).reshape(H0, W0, 3)
        return self.cur

    def at(self, vi):
        while self.n < vi:
            if self.next() is None:
                return None
        return self.cur if self.n == vi else None

    def close(self):
        try:
            self.p.stdout.close()
            self.p.kill()
        except OSError:
            pass


def frames_table(rec, idx):
    imap, last = load_idx(idx)
    inv = {}
    for pr, vi in (imap or {}).items():
        inv[vi] = pr
    r = Reader(rec)
    rows = []
    while True:
        fr = r.next()
        if fr is None:
            break
        if r.n in inv:
            rows.append([inv[r.n], m_count(fr), round(mean_of(fr), 3)])
    r.close()
    return dict(size=r.size, video_frames=r.n + 1, idx_records=len(imap or {}), last_present=last, rows=rows)


def load_json(p):
    return json.load(open(p, encoding='ascii')) if os.path.exists(p) else None


def settled(rd, base):
    r = load_json(os.path.join(rd, base, 'read.json'))
    if r is not None and r.get('status') == 'ADMITTED':
        return base, r
    r1 = load_json(os.path.join(rd, base + '_r1', 'read.json'))
    if r1 is not None and r1.get('status') == 'ADMITTED':
        return base + '_r1', r1
    return None, None


def mtab(rd, att):
    f = load_json(os.path.join(rd, att, 'frames.json'))
    if f is None:
        return None
    return dict((p, (m, mn)) for p, m, mn in f['rows'])


def compare(ma, mb, presents, excl):
    """presents with M_a - M_b >= THETA among presents common to both tables; excl - skip entry screen frames of either."""
    hits, comparable, best = [], 0, None
    for p in presents:
        if p not in ma or p not in mb:
            continue
        if excl and (ma[p][1] <= DARK or mb[p][1] <= DARK):
            continue
        comparable += 1
        dlt = ma[p][0] - mb[p][0]
        if best is None or dlt > best[1]:
            best = (p, dlt)
        if dlt >= THETA:
            hits.append(p)
    return dict(hits=len(hits), first=hits[0] if hits else None, comparable=comparable, best=best)


def ev_of(r, k):
    for e in (r or {}).get('events') or []:
        if e.get('k') == k:
            return e
    return None


def outline(fr, mask):
    o = fr.copy()
    edge = mask & ~(np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1))
    o[edge] = (255, 255, 0)
    return o


def save_sheet(path, panels, labels):
    from PIL import Image, ImageDraw
    w, h = W0 // 2, H0 // 2
    im = Image.new('RGB', (w * len(panels), h + 16))
    dr = ImageDraw.Draw(im)
    for i, (fr, lab) in enumerate(zip(panels, labels)):
        if fr is not None:
            im.paste(Image.fromarray(fr).resize((w, h)), (w * i, 16))
        dr.text((w * i + 4, 2), lab, fill=(255, 255, 255))
    im.save(path)


def d_scan(rd, atts, wins, sheets_dir, k):
    """Lockstep over t, 0, 1, 1b in W(e): candidates and sheets.  atts - dict arm -> attempt tag."""
    base = os.path.dirname(rd)
    idx = dict((a, load_idx(os.path.join(base, 'rec_%s.mp4.idx' % t))[0]) for a, t in atts.items())
    recs = dict((a, os.path.join(base, 'rec_%s.mp4' % t)) for a, t in atts.items())
    rdr = dict((a, Reader(recs[a])) for a in atts)
    lo, hi = wins
    rows, missing = [], []
    keep = []
    for p in range(lo, hi + 1):
        if any(p not in (idx[a] or {}) for a in atts):
            missing.append(p)
            continue
        fr = dict((a, rdr[a].at(idx[a][p])) for a in atts)
        if any(v is None for v in fr.values()):
            missing.append(p)
            continue
        mask = m_mask(fr['t'])
        n = int(mask.sum())
        dark = any(mean_of(v) <= DARK for v in fr.values())
        if n < THETA:
            continue
        d0 = d_measure(fr['0'], fr['1'], mask)
        d1b = d_measure(fr['1b'], fr['1'], mask)
        cand = d0 - d1b >= D_MIN
        rows.append(dict(present=p, mask=n, d0=round(d0, 3), d1b=round(d1b, 3), diff=round(d0 - d1b, 3), cand=cand, excluded=dark))
        if sheets_dir is not None:
            keep.append((p, d0 - d1b, dict((a, outline(v, mask)) for a, v in fr.items())))
            keep.sort(key=lambda z: -z[1])
            keep = keep[:6]
    for a in rdr.values():
        a.close()
    if sheets_dir is not None:
        for p, dd, fr in keep:
            save_sheet(os.path.join(sheets_dir, 'ev%d_cand_%d.png' % (k, p)), [fr['t'], fr['0'], fr['1'], fr['1b']],
                       ['t%d p%d' % (k, p), 'f26s_0', 'f26s_1', 'f26s_1b d0-d1b %.1f' % dd])
    return rows, missing


def series(rd, sheets):
    out = dict(theta=THETA, d_min=D_MIN, dark=DARK, events=[])
    att1, r1 = settled(rd, 'f26s_1')
    att0, r0 = settled(rd, 'f26s_0')
    att1b, r1b = settled(rd, 'f26s_1b')
    out['arms'] = dict(f26s_0=att0, f26s_1=att1, f26s_1b=att1b)
    sd = os.path.join(rd, 'series', 'sheets')
    if sheets:
        os.makedirs(sd, exist_ok=True)
    for k in (1, 2, 3, 4):
        row = dict(k=k)
        out['events'].append(row)
        e1, e0 = ev_of(r1, k), ev_of(r0, k)
        if r1 is None or e1 is None or not e1.get('found'):
            row['state'] = 'undetermined: f26s_1 not admitted or S%d not found' % k
            continue
        row.update(cls=e1['cls'], no_apply=e1['no_apply'], p=e1['present'], exec_present=e1.get('exec_present'),
                   exec_le_p1=(e1.get('exec_present') is not None and e1['exec_present'] <= e1['present'] + 1))
        if e1['cls'] not in ('kept_applied', 'kept why=decode', 'kept why=deferred'):
            row['state'] = 'undetermined, no mark by construction (item 711 (b)(1))'
            continue
        if e1['no_apply']:
            row['state'] = 'undetermined, not distinguishable by construction: NO_APPLY (item 702 (d)(2))'
            continue
        last1 = r1['idx']['last_present']
        last0 = (r0 or {}).get('idx', {}).get('last_present')
        pe1 = e1['first_exec'][0]['present'] if e1.get('first_exec') else last1
        pe0 = None
        if e0 is not None and e0.get('found'):
            pe0 = e0['first_exec'][0]['present'] if e0.get('first_exec') else last0
        row.update(p_end_1=pe1, p_end_0=pe0, p_end_1_source='first_exec' if e1.get('first_exec') else 'end of hold',
                   p_end_0_source=None if pe0 is None else ('first_exec' if e0.get('first_exec') else 'end of hold'))
        if pe0 is None:
            row['state'] = 'undetermined: f26s_0 not admitted or S%d not found there' % k
            continue
        lo, hi = window(e1['present'], pe0, pe1)
        row['window'] = [lo, hi]
        attc, rc = settled(rd, 'f26s_c%d' % k)
        attt, rt = settled(rd, 'f26s_t%d' % k)
        row['arms'] = dict(t=attt, c=attc)
        m1 = mtab(rd, att1)
        if rc is None:
            row['control'] = 'undetermined: f26s_c%d not admitted' % k
        else:
            mc = mtab(rd, attc)
            ta = ((rc.get('rows') or {}).get('last_f5') or {}).get('f26_tint_applied')
            pres = sorted(set(mc or {}) & set(m1 or {}))
            cx, cn = compare(mc or {}, m1 or {}, pres, True), compare(mc or {}, m1 or {}, pres, False)
            row['control'] = dict(tint_applied=ta, with_exclusion=cx, without_exclusion=cn,
                                  alive=bool(ta and ta >= 1 and cx['hits'] >= 1), alive_without_exclusion=bool(ta and ta >= 1 and cn['hits'] >= 1))
            if sheets and cx['best'] is not None:
                p = cx['best'][0]
                ic, _ = load_idx(os.path.join(os.path.dirname(rd), 'rec_%s.mp4.idx' % attc))
                i1, _ = load_idx(os.path.join(os.path.dirname(rd), 'rec_%s.mp4.idx' % att1))
                a, b = Reader(os.path.join(os.path.dirname(rd), 'rec_%s.mp4' % attc)), Reader(os.path.join(os.path.dirname(rd), 'rec_%s.mp4' % att1))
                fa, fb = a.at(ic[p]), b.at(i1[p])
                if fa is not None and fb is not None:
                    save_sheet(os.path.join(sd, 'ctl%d_%d.png' % (k, p)), [fa.copy(), fb.copy()],
                               ['c%d p%d M %d' % (k, p, m_count(fa)), 'f26s_1 M %d' % m_count(fb)])
                a.close()
                b.close()
        if rt is None:
            row['V'] = 'undetermined: f26s_t%d not admitted' % k
            continue
        mt = mtab(rd, attt)
        pres = list(range(lo, hi + 1))
        vx, vn = compare(mt or {}, m1 or {}, pres, True), compare(mt or {}, m1 or {}, pres, False)
        row['V_with_exclusion'] = vx
        row['V_without_exclusion'] = vn
        row['V'] = 'undetermined: no comparable present in W(e)' if vx['comparable'] == 0 else ('yes' if vx['hits'] >= 1 else 'no')
        if row['V'] == 'yes' and r1b is not None:
            dr, miss = d_scan(rd, dict(t=attt, **{'0': att0, '1': att1, '1b': att1b}), (lo, hi), sd if sheets else None, k)
            row['D_rows'] = dr[:40]
            row['D_candidates'] = [x['present'] for x in dr if x['cand'] and not x['excluded']]
            row['D_candidates_without_exclusion'] = [x['present'] for x in dr if x['cand']]
            row['D_missing_presents'] = miss[:20]
            row['D'] = 'number part yes at %s - the member needs the lead sheet' % row['D_candidates'][:6] if row['D_candidates'] else 'no'
        elif row['V'] == 'yes':
            row['D'] = 'undetermined: f26s_1b not admitted'
    return out


def series_text(out):
    t = ['F46c series (theta %d, d_min %d, entry screen mean <= %.0f); arms %s' % (out['theta'], out['d_min'], out['dark'], out['arms'])]
    for r in out['events']:
        t.append('S%d %s' % (r['k'], json.dumps(dict((k, v) for k, v in r.items() if k not in ('D_rows',)), sort_keys=True)))
    return t


def main(argv):
    rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
    if '--frames' in argv:
        tag = argv[argv.index('--frames') + 1]
        base = os.path.dirname(rd)
        rec = argv[argv.index('--rec') + 1] if '--rec' in argv else os.path.join(base, 'rec_%s.mp4' % tag)
        idx = argv[argv.index('--idx') + 1] if '--idx' in argv else rec + '.idx'
        t = frames_table(rec, idx)
        os.makedirs(os.path.join(rd, tag), exist_ok=True)
        with open(os.path.join(rd, tag, 'frames.json'), 'w', encoding='ascii', newline='\n') as f:
            json.dump(t, f)
        ms = [r[1] for r in t['rows']]
        print('frames %s: size %s video frames %d idx records %d rows %d last present %s; M max %s, frames with M >= %d: %d; entry screen '
              'frames %d' % (tag, t['size'], t['video_frames'], t['idx_records'], len(t['rows']), t['last_present'], max(ms) if ms else None,
                             THETA, sum(1 for m in ms if m >= THETA), sum(1 for r in t['rows'] if r[2] <= DARK)))
        print('SIZE %s' % ('960x540' if t['size'] == (W0, H0) else 'NOT 960x540 - scaled'))
        return 0
    if '--series' in argv:
        out = series(rd, '--no-sheets' not in argv)
        os.makedirs(os.path.join(rd, 'series'), exist_ok=True)
        with open(os.path.join(rd, 'series', 'series.json'), 'w', encoding='ascii', newline='\n') as f:
            json.dump(out, f, sort_keys=True, indent=1)
        txt = series_text(out)
        open(os.path.join(rd, 'series', 'series.txt'), 'w', encoding='ascii', newline='\n').write('\n'.join(txt) + '\n')
        print('\n'.join(txt))
        return 0
    print('usage: f46c_vid.py --frames <tag> | --series')
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
