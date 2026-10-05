"""Track F link F20l (HPP-631; ROADMAP s122 item 550 (zh), (z)(2)): the U5 base before the seal - over the 41 holds of F20c + F20e
(F20a main variant 8 holds + F20c 22 holds without the interference tags f20_v08, f20_v10 (item 543 (v)) + F20e 11 holds; the same
41 as 'F20c 3 of 30, F20e 1 of 11 - 4 of 41' of F20g s4) and the 11 tags of F20e.  The F20c reader (f20e_read.py, unchanged) gives the
scene frames and the attribution.  ASCII only.

    python b32_base.py [--out <txt>] [--json <json>]

Members (item 550 (zh)):
  (2) slow70_per_hold = (number of frames with dt_us >= 70 000 that start at >= 10 s of the scene, not attributed B5) / 41 holds
      ('INSTR_MADE' does not exist at KYTY_DIAG_B32=0).  Beside: the same without B5, B33, B1b (executor variant, reference).
  (1) med_dt_b2win = the median over the 11 F20e tags of the per-tag median FrameTrace dt_us of the scene frames idx 723..828 ('F20e
      (medians over 11 tags)').  Beside: the mean of the 11 medians and the pooled median (reference).
  (3) mean_dt_b5 = the mean dt_us of the F20e hold frames attributed B5 (dt_us >= 100 000, start >= 10 s, letter).
"""
import json
import multiprocessing
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f20e_read as F  # noqa: E402

F20C = 'C:/kyty/f287/f20c'
F20E = 'C:/kyty/f287/f20e'
F20C_OUT = ('f20_v08', 'f20_v10')        # interference by item 543 (v)


def holds():
    out = []
    for path, b in F.REGRESS:
        out.append(('F20a', os.path.basename(path), path, b))
    for i in range(1, 25):
        t = 'f20_v%02d' % i
        if t in F20C_OUT:
            continue
        j = json.load(open('%s/%s.json' % (F20C, t), encoding='utf-8'))
        out.append(('F20c', t, '%s/log_%s.txt' % (F20C, t), j['binary_sha256']))
    for i in range(25, 36):
        t = 'f20_v%02d' % i
        j = json.load(open('%s/%s.json' % (F20E, t), encoding='utf-8'))
        out.append(('F20e', t, '%s/log_%s.txt' % (F20E, t), j['binary_sha256']))
    return out


def one(a):
    series, tag, path, b = a
    r = F.scan(path)
    e = F.evaluate(r, b)
    fr = r['frames']
    s70 = [x for x in fr if x[2] >= 70000 and x[3] >= F.WIN_US]
    slow70 = sum(1 for x in s70 if F.attr(x, b, 'letter') != 'B5')
    slow70v = sum(1 for x in s70 if F.attr(x, b, 'letter') not in ('B5', 'B33', 'B1b'))
    win = [x[2] for x in fr if F.B2_LO <= x[0] <= F.B2_HI]
    b5 = [x[2] for x in fr if x[2] >= F.SLOW_US and x[3] >= F.WIN_US and F.attr(x, b, 'letter') == 'B5']
    return dict(series=series, tag=tag, path=path, binary=b[:8], hold=e['hold'], scene_s=e['scene_s'], slow70=slow70, slow70_var=slow70v,
                win_n=len(win), win=win if len(fr) >= F.B2_HI else None, b5=b5, sha256=F.sha_file(path))


def main(argv):
    hs = holds()
    with multiprocessing.Pool(8) as pool:
        res = pool.map(one, hs)
    out = ['suite b32_base.py sha256 %s target f20e_read.py sha256 %s' % (F.sha_file(os.path.abspath(__file__)), F.sha_file(F.__file__))]
    for r in res:
        out.append('%s %s %s bin %s hold %s scene %.1f s slow70 %d (variant %d) window medians %s B5 %s sha256 %s' % (
            r['series'], r['tag'], r['path'].replace('C:/kyty/', ''), r['binary'], r['hold'], r['scene_s'], r['slow70'], r['slow70_var'],
            statistics.median(r['win']) if r['win'] else None, r['b5'], r['sha256'][:16]))
    hr = [r for r in res if r['hold']]
    by = dict((s, sum(1 for r in hr if r['series'] == s)) for s in ('F20a', 'F20c', 'F20e'))
    n = len(hr)
    s70 = sum(r['slow70'] for r in hr)
    s70v = sum(r['slow70_var'] for r in hr)
    e = [r for r in res if r['series'] == 'F20e']
    meds = [statistics.median(r['win']) for r in e if r['win']]
    pooled = [v for r in e if r['win'] for v in r['win']]
    b5 = [v for r in e if r['hold'] for v in r['b5']]
    base = dict(holds=n, holds_by=by, slow70_total=s70, slow70_per_hold=round(s70 / n, 4) if n else None,
                slow70_var_per_hold=round(s70v / n, 4) if n else None,
                med_dt_b2win=statistics.median(meds) if meds else None, med_dt_b2win_tags=len(meds), med_dt_b2win_list=meds,
                med_dt_b2win_mean=round(sum(meds) / len(meds), 1) if meds else None, med_dt_b2win_pooled=statistics.median(pooled) if pooled else None,
                mean_dt_b5=round(sum(b5) / len(b5), 1) if b5 else None, b5_frames=len(b5), b5_list=b5)
    out.append('HOLDS %d (F20a %d, F20c %d, F20e %d; want 41 = 8 + 22 + 11)' % (n, by['F20a'], by['F20c'], by['F20e']))
    out.append('U5(2) BASE slow70_per_hold %s (%d frames / %d holds); variant without B5, B33, B1b %s' % (
        base['slow70_per_hold'], s70, n, base['slow70_var_per_hold']))
    out.append('U5(1) BASE med_dt_b2win %s (median of %d F20e tag medians %s; mean %s; pooled %s)' % (
        base['med_dt_b2win'], len(meds), meds, base['med_dt_b2win_mean'], base['med_dt_b2win_pooled']))
    out.append('U5(3) BASE mean_dt_b5 %s (%d B5 frames of F20e holds)' % (base['mean_dt_b5'], len(b5)))
    ok = n == 41 and by == {'F20a': 8, 'F20c': 22, 'F20e': 11} and len(meds) == 11
    out.append('BASE %s' % ('OK' if ok else 'CHECK (hold count or tag count differs)'))
    if '--out' in argv:
        with open(argv[argv.index('--out') + 1], 'w', encoding='ascii', newline='\n') as f:
            f.write('\n'.join(out) + '\n')
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w', encoding='ascii', newline='\n') as f:
            json.dump(base, f, ensure_ascii=True, sort_keys=True, indent=1)
    for l in out:
        print(l)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
