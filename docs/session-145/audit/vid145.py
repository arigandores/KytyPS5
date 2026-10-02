# vid145.py - Session Auditor, s145 step 3 (HPP-353): own count of the video frames, the coverage row and the continuity
# of the video against the presented frames (B38). No code of sc145.py / s51_vidglitch.py / sheet142.py (a port of the
# auditor's own vid144.py + vidcont144.py). Three independent frame counts per video:
#   (1) own parser of the fragmented MP4 container: sum of the sample_count fields of every moof/traf/trun box;
#   (2) frames actually decoded by ffprobe (-count_frames, nb_read_frames);
#   (3) records of the recorder index rec_<tag>.mp4.idx (lines "<index> <present> <seconds>").
# Continuity: the idx records carry the time of every recorded present, the FrameTrace rows carry dt_us; both are put on
# one clock by anchoring their ends; inside every idx gap > 60 ms the rows that END strictly inside the gap (margin 12 ms)
# are presented frames without a video record. READ ONLY. Usage: python vid145.py [--no-decode]
import os, sys, json, struct, hashlib, subprocess, re, mmap, bisect
from concurrent.futures import ThreadPoolExecutor

A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s145/step3/aud145.json'))}
VID = [('s145', 'C:/kyty/s145', 'runs145', 'v145_%02d' % i) for i in range(2, 18)] + [('s144', 'C:/kyty/s144', 'runs144', 'v144_09')]
DECODE = '--no-decode' not in sys.argv
RN = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
GAP = 0.060
MARG = 0.012


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


def boxes(f, start, end):
    off = start
    while off + 8 <= end:
        f.seek(off)
        h = f.read(16)
        n, t = struct.unpack('>I4s', h[:8])
        hd = 8
        if n == 1:
            n = struct.unpack('>Q', h[8:16])[0]
            hd = 16
        elif n == 0:
            n = end - off
        if n < hd:
            raise ValueError('bad box size at %d' % off)
        yield t, off, hd, n
        off += n


def mp4(p):
    size = os.path.getsize(p)
    out = {'size': size, 'moof': 0, 'trun': 0, 'samples': 0, 'mdat_bytes': 0, 'trun_bytes': 0, 'top': {}, 'tail_bytes': 0, 'last_box_overrun': 0}
    with open(p, 'rb') as f:
        end = 0
        try:
            for t, off, hd, n in boxes(f, 0, size):
                out['top'][t.decode('latin1')] = out['top'].get(t.decode('latin1'), 0) + 1
                if off + n > size:
                    out['last_box_overrun'] = off + n - size
                end = min(off + n, size)
                if t == b'mdat':
                    out['mdat_bytes'] += min(n, size - off) - hd
                elif t == b'moof':
                    out['moof'] += 1
                    for t2, o2, h2, n2 in boxes(f, off + hd, off + n):
                        if t2 != b'traf':
                            continue
                        dflt = None
                        for t3, o3, h3, n3 in boxes(f, o2 + h2, o2 + n2):
                            f.seek(o3 + h3)
                            body = f.read(n3 - h3)
                            if t3 == b'tfhd':
                                fl = struct.unpack('>I', body[:4])[0] & 0xffffff
                                q = 8
                                if fl & 0x1: q += 8
                                if fl & 0x2: q += 4
                                if fl & 0x8: q += 4
                                if fl & 0x10:
                                    dflt = struct.unpack('>I', body[q:q + 4])[0]
                            elif t3 == b'trun':
                                fl = struct.unpack('>I', body[:4])[0] & 0xffffff
                                cnt = struct.unpack('>I', body[4:8])[0]
                                out['trun'] += 1
                                out['samples'] += cnt
                                q = 8
                                if fl & 0x1: q += 4
                                if fl & 0x4: q += 4
                                per = (4 if fl & 0x100 else 0) + (4 if fl & 0x200 else 0) + (4 if fl & 0x400 else 0) + (4 if fl & 0x800 else 0)
                                if fl & 0x200:
                                    so = 4 if fl & 0x100 else 0
                                    for k in range(cnt):
                                        out['trun_bytes'] += struct.unpack('>I', body[q + k * per + so:q + k * per + so + 4])[0]
                                elif dflt is not None:
                                    out['trun_bytes'] += dflt * cnt
        except (ValueError, struct.error) as e:
            out['parse_error'] = repr(e)
        out['tail_bytes'] = size - end
    return out


def idx(p):
    if not os.path.isfile(p):
        return None, []
    ls = [x.split() for x in open(p, 'rb').read().decode('ascii', 'replace').splitlines() if x.strip()]
    a = [int(x[0]) for x in ls]
    b = [int(x[1]) for x in ls]
    t = [float(x[2]) for x in ls]
    gaps = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    gi = max(range(len(gaps)), key=lambda i: gaps[i]) if gaps else None
    return {'records': len(ls), 'index_consecutive': a == list(range(a[0], a[0] + len(a))) if a else None,
            'present_step_not_1': sum(1 for i in range(len(b) - 1) if b[i + 1] != b[i] + 1),
            'span_s': (t[-1] - t[0]) if t else None, 'max_gap_s': gaps[gi] if gaps else None, 'max_gap_at': a[gi] if gaps else None,
            'gaps_ge_1s': sum(1 for g in gaps if g >= 1.0)}, t


def decode(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_frames,width,height,codec_name', '-of', 'default=nw=1', p],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    d = dict(x.split('=', 1) for x in r.stdout.split() if '=' in x)
    return {'rc': r.returncode, 'frames': int(d['nb_read_frames']) if d.get('nb_read_frames', '').isdigit() else None,
            'w': d.get('width'), 'h': d.get('height'), 'codec': d.get('codec_name'), 'err': ' | '.join(r.stderr.strip().splitlines()[:3])[:300]}


def rows_of(log):
    rows = []
    with open(log, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        p = mm.find(b'FrameTrace: n=')
        while p != -1:
            m = RN.match(mm[p:p + 60])
            if m:
                rows.append((int(m.group(1)), int(m.group(2))))
            p = mm.find(b'FrameTrace: n=', p + 1)
        mm.close()
    return rows


def cont(rows, it, fn):
    ends = []
    c = 0.0
    for n, dt in reversed(rows):
        ends.append(it[-1] - c)
        c += dt / 1e6
    ends.reverse()
    miss = []
    for i in range(len(it) - 1):
        g = it[i + 1] - it[i]
        if g > GAP:
            lo = bisect.bisect_right(ends, it[i] + MARG)
            hi = bisect.bisect_left(ends, it[i + 1] - MARG)
            if hi > lo:
                miss.append((i, g, [rows[k][0] for k in range(lo, hi)], sum(rows[k][1] for k in range(lo, hi)) / 1e6))
    near = 0
    for e in ends:
        k = bisect.bisect_left(it, e)
        d = min(abs(it[k] - e) if k < len(it) else 9, abs(it[k - 1] - e) if k > 0 else 9)
        near += 1 if d <= 0.008 else 0
    after = [(i, g, [n for n in ns if n > fn], s) for i, g, ns, s in miss if fn is not None and ns[-1] > fn]
    tot_after = sum(len(x[2]) for x in after)
    tot_before = sum(len([n for n in ns if fn is None or n <= fn]) for i, g, ns, s in miss)
    worst = max(after, key=lambda x: len(x[2])) if after else None
    # presented time after the first scene frame at the end of the last missing row
    t_last = None
    if after and fn is not None:
        last_n = max(x[2][-1] for x in after)
        t_last = sum(dt for n, dt in rows if fn < n <= last_n) / 1e6
    return {'near': near, 'after': tot_after, 'gaps': len(after), 'before': tot_before,
            'longest': [len(worst[2]), worst[2][0], worst[2][-1], round(worst[3], 3), round(worst[1], 3)] if worst else None,
            'runs_ge2': sorted([len(x[2]) for x in after if len(x[2]) >= 2], reverse=True), 'last_missing_s_after_first': t_last}


def one(v):
    ses, root, runs, tag = v
    p = '%s/rec_%s.mp4' % (root, tag)
    R = {'ses': ses, 'tag': tag, 'path': p, 'present': os.path.isfile(p)}
    if not R['present']:
        return R
    R['sha256'] = sha(p)
    R['mp4'] = mp4(p)
    R['idx'], it = idx(p + '.idx')
    R['dec'] = decode(p) if DECODE else None
    L = A[(ses, tag)]['log']
    first = L.get('first')
    rows = rows_of('%s/log_%s.txt' % (root, tag))
    R['rows'] = len(rows)
    R['cont'] = cont(rows, it, first[0] if first else None) if it and rows else None
    try:
        S = json.load(open('%s/%s/%s.score.json' % (root, runs, tag), encoding='utf-8'))
        R['score'] = {'video_frames': (S.get('glitch') or {}).get('video_frames'), 'glitches': (S.get('glitch') or {}).get('glitches'),
                      'idx': S.get('idx'), 'cover': S.get('cover'), 'rows_total': S.get('rows_total'), 'vcont': S.get('vcont'), 'vq': S.get('vq'),
                      'rec_sha': (S.get('sheet') or {}).get('rec_sha'), 'times_rec_sha': (S.get('sheet') or {}).get('times_rec_sha'),
                      'sheet_sha': (S.get('sheet') or {}).get('sha'), 'sheet_times_sha': (S.get('sheet') or {}).get('times_sha')}
    except (OSError, ValueError) as e:
        R['score'] = {'error': repr(e)}
    sh = '%s/sheet_%s.png' % (root, tag)
    R['sheet_sha'] = sha(sh) if os.path.isfile(sh) else None
    gl = '%s/glitch_%s.txt' % (root, tag)
    if os.path.isfile(gl):
        b = open(gl, 'rb').read()
        t = [x for x in b.decode('utf-8', 'replace').splitlines() if x.strip()]
        R['glitch_sha'] = hashlib.sha256(b).hexdigest()
        R['glitch_last'] = t[-1][:120] if t else None
        R['glitch_err_lines'] = sum(1 for x in t if x.startswith('['))
        m = re.search(r'(\d+) frames (\d+)x(\d+), index entries (\d+)', '\n'.join(t))
        R['glitch_head'] = [int(x) for x in m.groups()] if m else None
    return R


def main():
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(one, VID))
    ok = True
    nd = 0
    nf = 0
    for R in res:
        if not R['present']:
            print('VIDEO %s %s: file absent' % (R['ses'], R['tag']))
            continue
        L = A[(R['ses'], R['tag'])]['log']
        rows = L.get('rows_total')
        m, ix, dc, sc, ct = R['mp4'], R['idx'], R['dec'], R['score'], R['cont']
        mine = m['samples']
        new = R['ses'] == 's145'
        checks = [('container samples = decoded frames', mine, dc['frames'] if dc else mine),
                  ('container samples = idx records', mine, ix['records'] if ix else None),
                  ('decoded frames = scorer video_frames', dc['frames'] if dc else sc.get('video_frames'), sc.get('video_frames')),
                  ('idx records = scorer idx', ix['records'] if ix else None, sc.get('idx')),
                  ('FrameTrace rows (own) = scorer rows_total', rows, sc.get('rows_total')),
                  ('FrameTrace rows (second own read) = rows of aud145', R['rows'], rows),
                  ('coverage (decoded frames >= rows - 100) = scorer cover', (dc['frames'] if dc else mine) >= rows - 100, sc.get('cover')),
                  ('sha256 of the video = scorer rec_sha', R['sha256'], sc.get('rec_sha')),
                  ('sha256 of the video = times.txt row (scorer field)', R['sha256'], sc.get('times_rec_sha')),
                  ('sha256 of the sheet = scorer sheet sha', R['sheet_sha'], sc.get('sheet_sha')),
                  ('sha256 of the sheet = times.txt row (scorer field)', R['sheet_sha'], sc.get('sheet_times_sha'))]
        if new and ct and sc.get('vcont'):
            vc = sc['vcont']
            checks += [('continuity: rows without a record after the first scene frame', ct['after'], vc.get('after')),
                       ('continuity: gaps after the first scene frame', ct['gaps'], vc.get('gaps')),
                       ('continuity: rows without a record before / at the first scene frame', ct['before'], vc.get('before')),
                       ('continuity: longest run (rows, n from, n to)', (ct['longest'] or [None] * 3)[:3], (vc.get('longest') or [None] * 3)[:3]),
                       ('alignment: rows with a record within 8 ms', ct['near'], (sc.get('vq') or {}).get('near'))]
        bad = [(n, a, b) for n, a, b in checks if a != b]
        nf += len(checks)
        nd += len(bad)
        ok &= not bad
        print('VIDEO %s %s sha %s size %d: container moof %d trun %d samples %d (sample bytes %d of mdat %d; bytes after the last whole box %d, last box overrun %d%s); '
              'decoded %s (%sx%s %s rc %s%s); idx records %s (index consecutive %s, present step != 1: %s, span %.1f s, max gap %.3f s at %s, gaps >= 1 s: %s); '
              'FrameTrace rows %s; decoded - rows = %+d; >= 3000: %s; coverage (>= rows - 100): %s; scorer frames %s idx %s cover %s; glitch file %s: %s | %s (decoder error lines %s); '
              'continuity own: within 8 ms %s, without a record before/at first %s, after %s in %s gaps, longest %s, runs >= 2 rows %s, last missing row at %.2f s after the first scene frame; scorer vcont %s -> %s' % (
                  R['ses'], R['tag'], R['sha256'][:16], m['size'], m['moof'], m['trun'], mine, m['trun_bytes'], m['mdat_bytes'], m['tail_bytes'], m['last_box_overrun'],
                  (' parse error %s' % m['parse_error']) if m.get('parse_error') else '',
                  dc['frames'] if dc else 'n/a', dc['w'] if dc else '', dc['h'] if dc else '', dc['codec'] if dc else '', dc['rc'] if dc else '',
                  (' stderr: ' + dc['err']) if dc and dc['err'] else '',
                  ix['records'] if ix else None, ix['index_consecutive'] if ix else None, ix['present_step_not_1'] if ix else None,
                  ix['span_s'] if ix else 0, ix['max_gap_s'] if ix else 0, ix['max_gap_at'] if ix else None, ix['gaps_ge_1s'] if ix else None,
                  rows, (dc['frames'] if dc else mine) - rows, (dc['frames'] if dc else mine) >= 3000, 'yes' if (dc['frames'] if dc else mine) >= rows - 100 else 'NO',
                  sc.get('video_frames'), sc.get('idx'), sc.get('cover'), str(R.get('glitch_sha'))[:16], R.get('glitch_head'), R.get('glitch_last'), R.get('glitch_err_lines'),
                  ct['near'] if ct else None, ct['before'] if ct else None, ct['after'] if ct else None, ct['gaps'] if ct else None, ct['longest'] if ct else None,
                  ct['runs_ge2'] if ct else None, (ct['last_missing_s_after_first'] or 0) if ct else 0, sc.get('vcont'), 'ok' if not bad else 'DIFF %r' % (bad,)))
    print('VIDEO CHECKS: %d videos, %d comparisons, %d differences: %s' % (sum(1 for r in res if r['present']), nf, nd, 'ALL OK' if ok else 'DIFFERENCES'))
    json.dump(res, open('C:/kyty/s145/step3/vid145.json', 'w', encoding='ascii'), ensure_ascii=True, indent=1, default=str)
    print('ALL DONE')


if __name__ == '__main__':
    main()
