"""Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(3); design edition 2 section 6, 7 (2)-(3), 9): the detector N_mag of one T188 tag
and the sheets for the lead.  Rows only, no verdict (the reading is M9g).  ASCII only.

  N_mag(record) = pixels with R >= 200, G <= 60, B >= 200 after the decode to rgb24 960x540 (the form of mb_kd_m9a2.py, M9a2).
  window        = the video records whose present number (2nd column of the .idx) >= first_scene_n of the reader (read.json of the tag);
                  w0 = the first window record; the offset of a record = record - w0 ("the same video frame numbers from the first scene
                  frame", item 785 (v)(3)).
  threshold     = max(2*M_b, 200) of the scene: Sky Garden 338, hoover_beach 648, mini_giants_garden 246 (section 6.1, item 785 (v)(3));
                  a record is marked when N_mag > threshold; the detector row is 'marked >= 3' (rows, M9g reads it with the sheet).
  top12         = up to 12 window records with the largest N_mag (ties - the earlier record); sheet_top.png - those frames of the tag.
  pairs         = for each top12 offset: the tag frame and the M6c frame (same scene, tag m6_<s>) at w0_m6c + offset; pairs_top_<k>.png
                  (6 pairs per sheet, tag left, M6c right).  Executor variant (printed as such): pairs_even_<k>.png - 12 offsets at even
                  steps over the window (the top12 of a tag without marked records are arbitrary frames of N_mag ~ 0).
  An offset beyond the M6c window - the pair is 'none' (row).

usage: python nmag_m9f.py <tag> <out dir>     (reads C:/kyty/m657/m9f/{rec_<tag>.mp4,.idx}, runs/<tag>/read.json and the M6c tag of the
       scene; ffmpeg at IDLE priority; exits 3 if the lock exists, also mid-run)
       python nmag_m9f.py --dir <fixture dir> <tag> <out dir>   (fixture form: rec.mp4, rec.idx, read.json, m6c.mp4, m6c.idx, m6c.json)
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

LOCK = 'C:/kyty/SEALED_RUN.lock'
G = 'C:/kyty/m657/m9f'
M6C = 'C:/kyty/m657/m6c'
W, H = 960, 540
FB = W * H * 3
IDLE = 0x00000040
THR = {'sg': 338, 'hb': 648, 'mg': 246}
M_B = {'sg': 169, 'hb': 324, 'mg': 123}
TOPN = 12
MARK_MIN = 3
TAG_RX = re.compile(r'^t188_(sg|hb|mg)2(_r[1-3])?$')


def sha(p):
    if not p or not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def lock():
    if os.path.exists(LOCK) and not os.environ.get('M9F_NMAG_NOLOCK'):
        sys.exit(3)


def nmag(a):
    return int(((a[:, :, 0] >= 200) & (a[:, :, 1] <= 60) & (a[:, :, 2] >= 200)).sum())


def frames(path):
    d = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE,
                         creationflags=IDLE if os.name == 'nt' else 0)
    i = 0
    try:
        while True:
            buf = d.stdout.read(FB)
            if len(buf) < FB:
                break
            yield i, np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3)
            i += 1
            if i % 500 == 0:
                lock()
    finally:
        d.kill()
        d.wait()


def read_idx(p):
    recs = []
    for ln in open(p, 'rb').read().decode('ascii', 'replace').split('\n'):
        q = ln.split()
        if len(q) == 3:
            recs.append((int(q[0]), int(q[1]), float(q[2])))
    return recs


def window(recs, fsn):
    return [r for r, pr, _ in recs if pr >= fsn]


def select(n, win):
    """top12 of the window: largest N_mag, ties - the earlier record."""
    cand = sorted((r for r in win if r < len(n)), key=lambda r: (-n[r], r))
    return sorted(cand[:TOPN])


def even(win, k=TOPN):
    if not win:
        return []
    if len(win) <= k:
        return list(win)
    return sorted(set(win[round(j * (len(win) - 1) / (k - 1))] for j in range(k)))


def tile(img, label):
    im = Image.fromarray(img).resize((480, 270))
    ImageDraw.Draw(im).rectangle([0, 0, 479, 14], fill=(0, 0, 0))
    ImageDraw.Draw(im).text((3, 2), label, fill=(255, 255, 255))
    return im


def blank(label):
    im = Image.new('RGB', (480, 270), (40, 40, 40))
    ImageDraw.Draw(im).text((3, 2), label, fill=(255, 255, 255))
    return im


def main(argv):
    lock()
    fx = None
    if argv and argv[0] == '--dir':
        fx, argv = argv[1], argv[2:]
    tag, od = argv[0], argv[1]
    m = TAG_RX.match(tag)
    if not m:
        print('usage: nmag_m9f.py [--dir D] <t188_sg2|t188_hb2|t188_mg2>[_rN] <out dir>')
        return 9
    s = m.group(1)
    thr = THR[s]
    os.makedirs(od, exist_ok=True)
    if fx:
        vid, idx, rj = (os.path.join(fx, x) for x in ('rec.mp4', 'rec.idx', 'read.json'))
        mvid, midx, mrj = (os.path.join(fx, x) for x in ('m6c.mp4', 'm6c.idx', 'm6c.json'))
    else:
        vid, idx, rj = '%s/rec_%s.mp4' % (G, tag), '%s/rec_%s.mp4.idx' % (G, tag), '%s/runs/%s/read.json' % (G, tag)
        mt = 'm6_' + s
        mvid, midx, mrj = '%s/rec_%s.mp4' % (M6C, mt), '%s/rec_%s.mp4.idx' % (M6C, mt), '%s/runs/%s/read.json' % (M6C, mt)
    fsn = ((json.load(open(rj, encoding='utf-8')).get('info') or {}).get('first_scene_n'))
    mfsn = ((json.load(open(mrj, encoding='utf-8')).get('info') or {}).get('first_scene_n'))
    if fsn is None or mfsn is None:
        print('NMAG UNDETERMINED: first_scene_n of the tag %s / of M6c %s' % (fsn, mfsn))
        return 2
    recs, mrecs = read_idx(idx), read_idx(midx)
    win, mwin = window(recs, fsn), window(mrecs, mfsn)
    if not win or not mwin:
        print('NMAG UNDETERMINED: empty window (tag %d, M6c %d)' % (len(win), len(mwin)))
        return 2
    n = [nmag(a) for _, a in frames(vid)]
    nw = [n[r] for r in win if r < len(n)]
    marked = [r for r in win if r < len(n) and n[r] > thr]
    top = select(n, win)
    evn = even([r for r in win if r < len(n)])
    w0, mw0 = win[0], mwin[0]
    need = sorted(set(top) | set(evn))
    pair = dict((r, (mw0 + (r - w0)) if (mw0 + (r - w0)) <= mwin[-1] else None) for r in need)
    mneed = set(v for v in pair.values() if v is not None)
    got, mgot = {}, {}
    for i, a in frames(vid):
        if i in need:
            got[i] = a.copy()
    for i, a in frames(mvid):
        if i in mneed:
            mgot[i] = a.copy()
    lock()
    with open(os.path.join(od, 'nmag.tsv'), 'wb') as f:
        f.write(('\n'.join('%d\t%d\t%d' % (r, recs[r][1], n[r]) for r in range(min(len(n), len(recs)))) + '\n').encode())
    sheet = Image.new('RGB', (480 * 4, 270 * 3), (0, 0, 0))
    for k, r in enumerate(top):
        im = tile(got[r], '%s rec %d off %d N_mag %d' % (tag, r, r - w0, n[r])) if r in got else blank('missing %d' % r)
        sheet.paste(im, ((k % 4) * 480, (k // 4) * 270))
    sheet.save(os.path.join(od, 'sheet_top.png'))
    outs = []
    for name, lst in (('top', top), ('even', evn)):
        for part in range(0, len(lst), 6):
            pg = Image.new('RGB', (960, 270 * 6), (0, 0, 0))
            for k, r in enumerate(lst[part:part + 6]):
                a = tile(got[r], '%s off %d N_mag %d' % (tag, r - w0, n[r])) if r in got else blank('missing %d' % r)
                mr = pair[r]
                b = tile(mgot[mr], 'm6_%s off %d rec %d' % (s, r - w0, mr)) if mr is not None and mr in mgot else blank('M6c none off %d' % (r - w0))
                pg.paste(a, (0, k * 270))
                pg.paste(b, (480, k * 270))
            pn = 'pairs_%s_%d.png' % (name, part // 6 + 1)
            pg.save(os.path.join(od, pn))
            outs.append(pn)
    res = dict(tag=tag, scene=s, threshold=thr, m_b=M_B[s], first_scene_n=fsn, w0=w0, window_records=len(nw), decoded=len(n),
               idx_records=len(recs), max_nmag_window=max(nw) if nw else None, marked=len(marked), marked_ge3=len(marked) >= MARK_MIN,
               marked_first=marked[:20], top=[dict(record=r, present=recs[r][1], offset=r - w0, nmag=n[r], m6c_record=pair[r]) for r in top],
               even=[dict(record=r, offset=r - w0, nmag=n[r], m6c_record=pair[r]) for r in evn],
               m6c=dict(first_scene_n=mfsn, w0=mw0, window_records=len(mwin), video_sha256=sha(mvid)),
               video_sha256=sha(vid), idx_sha256=sha(idx), read_json_sha256=sha(rj), sheets=['sheet_top.png'] + outs,
               variant='pairs_even_* - executor variant (12 offsets at even steps over the window)',
               script_sha256=sha(os.path.abspath(__file__)))
    with open(os.path.join(od, 'nmag.json'), 'w', encoding='ascii', newline='\n') as f:
        json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1)
    print('NMAG %s: threshold %d (M_b %d); window %d records from present %d (w0 %d); max N_mag %s; marked > threshold %d (>= %d: %s)' % (
        tag, thr, M_B[s], len(nw), fsn, w0, res['max_nmag_window'], len(marked), MARK_MIN, 'YES' if res['marked_ge3'] else 'NO'))
    print('  top12 (record off N_mag M6c record): ' + ' '.join('%d/%d/%d/%s' % (t['record'], t['offset'], t['nmag'], t['m6c_record'])
                                                              for t in res['top']))
    print('  sheets: %s; script sha256 %s' % (' '.join(res['sheets']), res['script_sha256']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
