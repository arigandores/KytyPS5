"""F20e (HPP-624): the report table of the series in the form of F20c section 4 (from runs/<tag>/read.json, the tag json, lock.log,
procload.txt), the list of unattributed hold frames, the summary lines of series.txt.  Reads only; ASCII only.
usage: python table_f20e.py [--out <md>]"""
import json
import os
import re
import sys

G = 'C:/kyty/f287/f20e'


def main(argv):
    lock = {}
    for l in open(G + '/runs/lock.log', encoding='ascii'):
        m = re.match(r'lock (taken|released) (\S+) \S+T(\d\d:\d\d:\d\d)Z', l.strip())
        if m:
            lock.setdefault(m.group(2), {})[m.group(1)] = m.group(3)
    rows = ['| tag | binary | lock (UTC) | admission | 1st scene frame | entry | dump in window | max `dt_us` window | B2 frames | '
            'hold, s | unattr. (F20a) | deaths | frames >= 1 s | glitches | video frames | skipped draw | CPU line before the tag (procload) |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    un = ['| tag | idx | n | `dt_us` | t from the first scene frame, s | class (letter / F20a) | `PriorityStall:` lines / us |',
          '|---|---|---|---|---|---|---|']
    att = ['| tag | idx | n | `dt_us` | t, s | class | ir / gcn / pcs / trip / prio |', '|---|---|---|---|---|---|---|']
    for t in sorted(os.listdir(G + '/runs')):
        j = G + '/runs/%s/read.json' % t
        if not re.match(r'^f20_v\d\d$', t) or not os.path.exists(j):
            continue
        r = json.load(open(j, encoding='ascii'))
        e = r['eval'] or {}
        rf = r['ref']
        pl = ''
        pp = G + '/runs/%s/procload.txt' % t
        if os.path.exists(pp):
            ls = [x.strip() for x in open(pp, encoding='ascii', errors='replace') if x.strip()]
            pl = ls[-1][:80] if ls else ''
        lk = lock.get(t, {})
        entry = 'warm' if e.get('warm') else ('cold' if e.get('window_read') else 'window not read')
        nd = len(rf['death_log'] or []) + len(rf['death_stdout'] or [])
        rows.append('| `%s` | %s | %s-%s | %s | %s | %s | %s | %s | %d | %.1f | %d (%d) | %d | %s | %s | %s | %s | %s |' % (
            t, (r['binary_sha256'] or '-')[:8], lk.get('taken', '?'), lk.get('released', '?'), 'YES' if r['admitted'] else 'NO',
            e.get('first_n'), entry, e.get('window_dump'), e.get('window_max_us'), len(e.get('b2_frames') or []), e.get('scene_s', 0),
            e.get('unattr', 0), e.get('unattr_f20a', 0), nd, rf['k1s_after'], rf['glitches'], rf['video_index'], rf['skipped_draw'], pl))
        for x in e.get('hold_frames') or []:
            if x['letter'] in ('nothing', 'prio only', 'pcs after S12') or x['f20a'] in ('nothing', 'prio only', 'pcs after S12'):
                un.append('| `%s` | %d | %d | %d | %.1f | %s / %s | %d / %d |' % (t, x['idx'], x['n'], x['dt_us'], x['t_before_s'], x['letter'],
                                                                             x['f20a'], x['prio'], x['prio_us']))
            else:
                att.append('| `%s` | %d | %d | %d | %.1f | %s | %d / %d / %d / %d / %d |' % (t, x['idx'], x['n'], x['dt_us'], x['t_before_s'],
                                                                                    x['letter'], x['ir'], x['gcn'], x['pcs'], x['trip'], x['prio']))
    ser = [l.rstrip() for l in open(G + '/series.txt', encoding='ascii') if l.startswith(('BASE', 'SUM', 'TAGS', 'READING', 'STOP', 'NEXT'))]
    out = ['## Table of tags'] + rows + ['', '## Unattributed hold frames'] + (un if len(un) > 2 else ['none']) + \
          ['', '## Attributed hold frames (reference)'] + (att if len(att) > 2 else ['none']) + ['', '## Summary (series.txt)', '```'] + ser + ['```']
    txt = '\n'.join(out) + '\n'
    if '--out' in argv:
        with open(argv[argv.index('--out') + 1], 'w', encoding='ascii', newline='\n') as f:
            f.write(txt)
    sys.stdout.write(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
