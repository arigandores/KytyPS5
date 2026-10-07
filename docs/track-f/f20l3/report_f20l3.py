"""F20l3 (HPP-655): the link table (item 591 (zh)) - one row per tag of runs/: admission, sha256 of the log and of read.txt (both, item 591
(zh)), binary and translation signature, hold / K, frames in count with classes, PK-A cold domain, U5(1) median, glitches, video frames,
M6 foreign max, lock times (lock.log).  Not a seal member (reads the sealed reader's json).  usage: python report_f20l3.py > table_f20l3.md
ASCII only."""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f20l3'
RX = re.compile(r'^(b32_pa2?|b32_s(?:0[1-9]|[1-5][0-9]|60)|b32_z0c[1-5])(_r[1-6])?$')


def sha(p):
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def order(t):
    b = RX.match(t).group(1)
    k = 0 if b.startswith('b32_pa') else (2 if b.startswith('b32_z0c') else 1)
    return (k, t)


def main():
    lock = {}
    for l in open(os.path.join(G, 'runs', 'lock.log'), encoding='ascii'):
        p = l.split()
        if len(p) == 4:
            lock.setdefault(p[2], {})[p[1]] = p[3]
    tags = sorted((t for t in os.listdir(os.path.join(G, 'runs')) if RX.match(t)), key=order)
    print('| tag | adm | log sha256 | read.txt sha256 | bin / sig | hold / K | in count (n dt class) | PK-A cold (frames / armed / member) '
          '| U5(1) med | glitches / video | M6 foreign max | lock taken - released |')
    print('|' + '---|' * 12)
    for t in tags:
        d = os.path.join(G, 'runs', t)
        res = json.load(open(os.path.join(d, 'read.json'), encoding='utf-8'))
        r = res['log'] or {}
        cnt = ['%d %d %s' % (x['n'], x['dt_us'], x['cls']) for x in r.get('frames', []) if x['in_count']]
        m6 = open(os.path.join(d, 'm6.txt'), encoding='ascii').read().strip().splitlines()[-1] if os.path.exists(os.path.join(d, 'm6.txt')) else ''
        fm = re.search(r'foreign_max=([0-9.]+)', m6)
        print('| `%s` | %s | `%s` | `%s` | %s / %s | %s / %s | %s | %d / %d / %s | %s | %s / %s | %s | %s - %s |' % (
            t, 'PASS' if res['admitted'] else 'FAIL', sha(os.path.join(G, 'log_%s.txt' % t)), sha(os.path.join(d, 'read.txt')),
            (res['binary_sha256'] or '-')[:8], (res['ref'].get('signature') or '-')[:8], r.get('hold'), r.get('K'),
            '; '.join(cnt) or '-', len(r.get('pk_a3') or []), r.get('pk_a3_armed') or 0, r.get('pk_a3_member'), r.get('u5_med_dt'),
            res['ref'].get('glitches'), res['ref'].get('video_index'), fm.group(1) if fm else '-',
            (lock.get(t) or {}).get('taken', '-'), (lock.get(t) or {}).get('released', '-')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
