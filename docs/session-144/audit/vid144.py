# vid144.py - Session Auditor, s144 step 3 (HPP-333), debt D-4: own count of the video frames and the coverage row.
# No code of sc144.py / s51_vidglitch.py / sheet142.py. Three independent counts per video:
#   (1) own parser of the fragmented MP4 container: sum of the sample_count fields of every moof/traf/trun box;
#   (2) frames actually decoded by ffprobe (-count_frames, nb_read_frames);
#   (3) records of the recorder index rec_<tag>.mp4.idx (lines "<index> <present> <seconds>").
# Against: FrameTrace rows of the log (own aud144.json), the scorer json (glitch.video_frames, idx, cover) and the rows
# "V video >= 3000 frames", "V video frames >= FrameTrace rows in all - 100". READ ONLY.
# Usage: python vid144.py [--no-decode]
import os, sys, json, struct, hashlib, subprocess, re
from concurrent.futures import ThreadPoolExecutor

A = {(r['root'][-4:], r['tag']): r for r in json.load(open('C:/kyty/s144/step3/aud144.json'))}
VID = [('s144', 'C:/kyty/s144', 'runs144', 'v144_%02d' % i) for i in range(9, 21)] + \
      [('s143', 'C:/kyty/s143', 'runs143', 'v143_%02d' % i) for i in range(1, 11)] + [('s142', 'C:/kyty/s142', 'runs142', 'v142')]
PAIR_V143 = ['v143_%02d' % i for i in (1, 2, 3, 4, 5, 6, 9, 10)]
DECODE = '--no-decode' not in sys.argv


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
    out = {'size': size, 'moof': 0, 'trun': 0, 'samples': 0, 'mdat_bytes': 0, 'trun_bytes': 0, 'tracks': set(), 'stsz_samples': 0, 'top': {}}
    with open(p, 'rb') as f:
        for t, off, hd, n in boxes(f, 0, size):
            out['top'][t.decode('latin1')] = out['top'].get(t.decode('latin1'), 0) + 1
            if t == b'mdat':
                out['mdat_bytes'] += n - hd
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
                            out['tracks'].add(struct.unpack('>I', body[4:8])[0])
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
            elif t == b'moov':
                f.seek(off + hd)
                body = f.read(n - hd)
                k = body.find(b'stsz')
                if k != -1:
                    out['stsz_samples'] = struct.unpack('>I', body[k + 12:k + 16])[0]
    out['tracks'] = sorted(out['tracks'])
    return out


def idx(p):
    if not os.path.isfile(p):
        return None
    ls = [x.split() for x in open(p, 'rb').read().decode('ascii', 'replace').splitlines() if x.strip()]
    a = [int(x[0]) for x in ls]
    b = [int(x[1]) for x in ls]
    t = [float(x[2]) for x in ls]
    gaps = [t[i + 1] - t[i] for i in range(len(t) - 1)]
    gi = max(range(len(gaps)), key=lambda i: gaps[i]) if gaps else None
    return {'records': len(ls), 'first': ls[0] if ls else None, 'last': ls[-1] if ls else None,
            'index_consecutive': a == list(range(a[0], a[0] + len(a))) if a else None,
            'present_step_not_1': sum(1 for i in range(len(b) - 1) if b[i + 1] != b[i] + 1),
            'span_s': (t[-1] - t[0]) if t else None, 'max_gap_s': gaps[gi] if gaps else None, 'max_gap_at': a[gi] if gaps else None,
            'gaps_ge_1s': sum(1 for g in gaps if g >= 1.0)}


def decode(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_frames,width,height,codec_name', '-of', 'default=nw=1'], capture_output=True, text=True, stdin=subprocess.DEVNULL) \
        if False else subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                      'stream=nb_read_frames,width,height,codec_name', '-of', 'default=nw=1', p],
                                     capture_output=True, text=True, stdin=subprocess.DEVNULL)
    d = dict(x.split('=', 1) for x in r.stdout.split() if '=' in x)
    return {'rc': r.returncode, 'frames': int(d['nb_read_frames']) if d.get('nb_read_frames', '').isdigit() else None,
            'w': d.get('width'), 'h': d.get('height'), 'codec': d.get('codec_name'), 'err': r.stderr.strip()[:200]}


def one(v):
    ses, root, runs, tag = v
    p = '%s/rec_%s.mp4' % (root, tag)
    R = {'ses': ses, 'tag': tag, 'path': p, 'present': os.path.isfile(p)}
    if not R['present']:
        return R
    R['sha256'] = sha(p)
    R['mp4'] = mp4(p)
    R['idx'] = idx(p + '.idx')
    R['dec'] = decode(p) if DECODE else None
    try:
        S = json.load(open('%s/%s/%s.score.json' % (root, runs, tag), encoding='utf-8'))
        R['score'] = {'video_frames': (S.get('glitch') or {}).get('video_frames'), 'glitches': (S.get('glitch') or {}).get('glitches'),
                      'idx': S.get('idx'), 'cover': S.get('cover'), 'rows_total': S.get('rows_total'),
                      'rec_sha': (S.get('sheet') or {}).get('rec_sha'), 'times_rec_sha': (S.get('sheet') or {}).get('times_rec_sha')}
    except (OSError, ValueError) as e:
        R['score'] = {'error': repr(e)}
    gl = '%s/glitch_%s.txt' % (root, tag)
    if os.path.isfile(gl):
        t = [x for x in open(gl, encoding='utf-8', errors='replace').read().splitlines() if x.strip()]
        R['glitch_last'] = t[-1][:120] if t else None
        m = re.search(r'(\d+) frames (\d+)x(\d+), index entries (\d+)', '\n'.join(t))
        R['glitch_head'] = [int(x) for x in m.groups()] if m else None
    return R


def main():
    with ThreadPoolExecutor(4) as ex:
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
        m, ix, dc, sc = R['mp4'], R['idx'], R['dec'], R['score']
        mine = m['samples']
        checks = [('container samples = decoded frames', mine, dc['frames'] if dc else mine),
                  ('container samples = idx records', mine, ix['records'] if ix else None),
                  ('container samples = scorer video_frames', mine, sc.get('video_frames')),
                  ('idx records = scorer idx', ix['records'] if ix else None, sc.get('idx')),
                  ('FrameTrace rows (own) = scorer rows_total', rows, sc.get('rows_total')),
                  ('coverage (frames >= rows - 100) = scorer cover', mine >= rows - 100, sc.get('cover')),
                  ('sha256 of the video = scorer rec_sha', R['sha256'], sc.get('rec_sha')),
                  ('sha256 of the video = times.txt row (scorer field)', R['sha256'], sc.get('times_rec_sha'))]
        bad = [(n, a, b) for n, a, b in checks if a != b]
        nf += len(checks)
        nd += len(bad)
        ok &= not bad
        print('VIDEO %s %s sha %s size %d: container moof %d trun %d samples %d (track ids %s, sample bytes %d of mdat %d); decoded %s (%sx%s %s rc %s); '
              'idx records %s (index consecutive %s, present step != 1: %s, span %.1f s, max gap %.3f s at %s, gaps >= 1 s: %s); FrameTrace rows %s; '
              'frames - rows = %+d; >= 3000: %s; coverage (>= rows - 100): %s; scorer frames %s idx %s cover %s; glitch file: %s | %s -> %s' % (
                  R['ses'], R['tag'], R['sha256'][:16], m['size'], m['moof'], m['trun'], mine, m['tracks'], m['trun_bytes'], m['mdat_bytes'],
                  dc['frames'] if dc else 'n/a', dc['w'] if dc else '', dc['h'] if dc else '', dc['codec'] if dc else '', dc['rc'] if dc else '',
                  ix['records'] if ix else None, ix['index_consecutive'] if ix else None, ix['present_step_not_1'] if ix else None,
                  ix['span_s'] if ix else 0, ix['max_gap_s'] if ix else 0, ix['max_gap_at'] if ix else None, ix['gaps_ge_1s'] if ix else None,
                  rows, mine - rows, mine >= 3000, 'yes' if mine >= rows - 100 else 'NO', sc.get('video_frames'), sc.get('idx'), sc.get('cover'),
                  R.get('glitch_head'), R.get('glitch_last'), 'ok' if not bad else 'DIFF %r' % (bad,)))
    print('VIDEO CHECKS: %d videos, %d comparisons, %d differences: %s' % (sum(1 for r in res if r['present']), nf, nd, 'ALL OK' if ok else 'DIFFERENCES'))
    json.dump(res, open('C:/kyty/s144/step3/vid144.json', 'w', encoding='ascii'), ensure_ascii=True, indent=1, default=str)
    print('ALL DONE')


if __name__ == '__main__':
    main()
