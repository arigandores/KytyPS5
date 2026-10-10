# F32a (HPP-733): report over the delta sweep (agg_f32a.json + segments) and the witness pass (wit/*.json).
# (1) witnesses of parked rows: regular-path Take (miss/hit) of hashes that the speculative thread skipped, by reason class;
# (2) socket headers, 'Read 0 bytes', 'Controller removed', VUID-06479, MainTaskLate >= 1 s, quits, fatal markers;
# (3) frames by the F0 rule (docs/track-f/f0/agg_f0.py frames(): first scene frame = first FrameTrace with draws >= 100 after
#     a level start, window 599 frames, then hold; validation logs excluded) for the course-line builds.
# Every number is split by build class: COURSE_FS2 (installed binaries from FS2 on), PRE_FS2 (9235a7ac, dac02fb9), OTHER.
# Usage: python rep_f32a.py <binmap.tsv> > rep_f32a.out.txt
import os, re, sys, json, pickle, hashlib, collections

OUT = os.environ.get('F32A_OUT', 'C:/kyty/f287/f32a')
SEG = OUT + '/seg'
WD = OUT + '/wit'
SEG_BYTES = int(os.environ.get('F32A_SEG_BYTES', 256 << 20))
AGG_F0 = os.environ.get('F32A_AGG_F0_PY', 'C:/kyty/KytyPS5/docs/track-f/f0/agg_f0.py')
B26G = '57c4d5848e02ecdc'
SG = 'underwater_aerial_garden'


def load_frames():
    # agg_f0.py calls main() at module level (it rewrites C:/kyty/f287/f0/agg_f0.json and sig_f0.tsv when imported):
    # only the text before 'def main' is executed here
    src = open(AGG_F0, encoding='utf-8').read().split(chr(10) + 'def main')[0]
    ns = {}
    exec(compile(src, AGG_F0, 'exec'), ns)
    return ns['frames']


def build_classes(binmap):
    course, pre = {}, {}
    for l in open(binmap, encoding='utf-8'):
        x = l.rstrip(chr(10)).split(chr(9))
        name, h = x[0], x[3]
        if name in ('9235a7ac', 'dac02fb9'):
            pre[h if h != '?' else '4fc501f'] = name
        else:
            course[h] = name
    return course, pre


def cls_of(b, course, pre):
    return 'COURSE_FS2' if b in course else ('PRE_FS2' if b in pre else 'OTHER')


def events_of(r):
    md = hashlib.md5(r['path'].encode('utf-8')).hexdigest()
    whole = r['kind'] == 'xz' or r['size'] <= SEG_BYTES
    nseg = 1 if whole else (r['size'] + SEG_BYTES - 1) // SEG_BYTES
    ev, off, vkw = [], 0, 0
    for i in range(nseg):
        s = pickle.load(open('%s/%s_%d.pkl' % (SEG, md, i), 'rb'))
        for x in s['events']:
            ev.append((x[0], x[1] + off) + tuple(x[2:]))
        vkw += sum(v[0] for k, v in s['sigs'].items() if k.startswith(b'[Vulkan][W]'))
        off += s['lines']
    return ev, vkw >= 100


def main():
    course, pre = build_classes(sys.argv[1])
    frames = load_frames()
    recs = [r for r in json.load(open(OUT + '/agg_f32a.json', encoding='utf-8')) if not r['dup_of'] and not r['in_f0']]
    print('unique delta logs', len(recs))
    byc = collections.Counter(cls_of(r['build'], course, pre) for r in recs)
    print('logs by build class', dict(byc))
    print('course builds present', dict(collections.Counter(course[r['build']] for r in recs if r['build'] in course)))
    W = {}
    for r in recs:
        W[r['path']] = json.load(open('%s/%s.json' % (WD, hashlib.md5(r['path'].encode('utf-8')).hexdigest()), encoding='utf-8'))
    # (1) witnesses
    print()
    print('(1) regular-path Take of speculatively skipped hashes')
    for c in ('COURSE_FS2', 'PRE_FS2', 'OTHER', 'ALL'):
        sel = [r for r in recs if c == 'ALL' or cls_of(r['build'], course, pre) == c]
        armed = [r for r in sel if W[r['path']]['take_lines'] > 0]
        lv = set()
        for r in armed:
            lv.update(r['levels'])
        wit = collections.Counter()
        wit_ex = {}
        skipped_cls = collections.Counter()
        for r in sel:
            w = W[r['path']]
            for h, k in w['skipped'].items():
                skipped_cls[k] += 1
                if h in w['take']:
                    wit[k] += 1
                    wit_ex.setdefault(k, '%s hash=%s' % (r['path'], h))
        b26g = sum(1 for r in sel if B26G in W[r['path']]['skipped'])
        b26g_w = sum(1 for r in sel if B26G in W[r['path']]['take'])
        print('  %-10s logs %4d | with Take lines (path armed) %4d, levels %3d, Take lines %6d | skipped hash-in-log by class %s | witnesses %s %s | B26g skipped in %d logs, taken %d'
              % (c, len(sel), len(armed), len(lv), sum(W[r['path']]['take_lines'] for r in sel), dict(skipped_cls), dict(wit) or 0,
                 wit_ex or '', b26g, b26g_w))
    # (2) other witnesses
    print()
    print('(2) other witness lines')
    keys = ['cfg_out', 'sock', 'read0', 'ctl_removed', 'vuid06479', 'late_ge1s', 'quit', 'fatal']
    for c in ('COURSE_FS2', 'PRE_FS2', 'OTHER'):
        sel = [r for r in recs if cls_of(r['build'], course, pre) == c]
        row = []
        for k in keys:
            n = sum((len(W[r['path']][k]) if k == 'cfg_out' else W[r['path']][k]) for r in sel)
            nl = sum(1 for r in sel if (W[r['path']][k] if k != 'cfg_out' else W[r['path']][k]))
            row.append('%s %d/%d logs' % (k, n, nl))
        print('  %-10s %s' % (c, '; '.join(row)))
    for k, e in (('cfg_out', None), ('sock', 'sock_ex'), ('read0', 'read0_ex'), ('ctl_removed', 'ctl_ex'), ('vuid06479', 'v_ex'),
                 ('late_ge1s', 'late_ex'), ('fatal', 'fatal_ex')):
        ex = [(r['path'], r['build'], (W[r['path']][e] if e else W[r['path']]['cfg_out'][:1])) for r in recs
              if (W[r['path']][k] if k != 'cfg_out' else W[r['path']]['cfg_out'])]
        for p, b, x in ex[:12]:
            print('    %s %s %s %s' % (k, p, b, x))
        if len(ex) > 12:
            print('    %s ... %d more' % (k, len(ex) - 12))
    # (3) frames on course-line logs
    print()
    print('(3) frames by the F0 rule on COURSE_FS2 logs without validation')
    allk2 = []
    per_level = collections.defaultdict(lambda: {'entries': 0, 'k2w': 0, 'k2h': 0, 'k3h': 0, 'hold_frames': 0, 'ex': []})
    for r in recs:
        if cls_of(r['build'], course, pre) != 'COURSE_FS2':
            continue
        ev, val = events_of(r)
        if val:
            continue
        for x in frames(ev, False):
            if x['first_n'] is None:
                continue
            d = per_level[x['level']]
            d['entries'] += 1
            d['hold_frames'] += max(0, x['frames'] - 599)
            for k in x['k2']:
                allk2.append('%s:%d %s n=%d dt_us=%d %s build=%s' % (r['path'], k[3], x['level'], k[0], k[1], 'window' if k[2] == 'w' else 'hold', course[r['build']]))
                d['k2w' if k[2] == 'w' else 'k2h'] += 1
                if len(d['ex']) < 4:
                    d['ex'].append('%s:%d n=%d dt=%d %s' % (r['path'], k[3], k[0], k[1], k[2]))
            d['k3h'] += x['k3h']
            if x['k3h'] and len(d['ex']) < 4:
                d['ex'].append('%s:%d k3h=%d first=%s' % (r['path'], x['k3h_ex'][0][2], x['k3h'], x['k3h_ex'][0][:2]))
    tot = collections.Counter()
    for lv in sorted(per_level, key=lambda k: -per_level[k]['entries']):
        d = per_level[lv]
        for k in ('entries', 'k2w', 'k2h', 'k3h', 'hold_frames'):
            tot[k] += d[k]
        print('  %-36s entries %3d  K2 window %2d  K2 hold %2d  K3 hold %3d  hold frames %7d  %s' % (lv, d['entries'], d['k2w'], d['k2h'], d['k3h'], d['hold_frames'], ' | '.join(d['ex'])))
    print('  TOTAL', dict(tot), 'levels', len(per_level))
    print('  all K2 frames (>= 1 s) after the first scene frame on COURSE_FS2 logs without validation:', len(allk2))
    for x in allk2:
        print('    ' + x)


if __name__ == '__main__':
    main()
