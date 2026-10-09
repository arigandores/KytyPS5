# Track F link F30f (HPP-711; ROADMAP s122 item 643 (g) RC6, item 643 (d)(6)): the support of kappa by level AND BDA mode.
# Input: docs/track-f/f30a/sweep_f30a.jsonl.xz (F30a, 1 078 logs).  The filter of rate_f30a.py unchanged (course binaries dac02fb9 .. FS10,
# knob value set {1}, entries >= 1000 frames, one copy of (binary, level, frames)); the mode of an entry - mode_of of ana_f30a.py unchanged
# (90-frame blocks of bda_scan, the first 2 skipped, >= 3 read blocks, OLD / NEW at >= 90 % of the read blocks in the band, else MIXED,
# SHORT below 3 blocks).  Output: one row per (level, mode) and per (level, ALL): entries, frames, rts_n, rts_skip, skip share.
# usage: python kref_f30f.py <sweep.jsonl.xz> <out.tsv>        ASCII only.
import json, lzma, re, sys
from collections import defaultdict

COURSE = {'abfded5e': 'FS10', '3861eeea': 'FS9', 'b3cee576': 'S18', '2c9b69b9': 'FS8', '8df61c00': 'FS7', '9325446c': 'FS6',
          'adb0c82f': 'S12', '631ff987': 'FS5', '31cbfee8': 'FS4', '540c035a': 'FS3', '4aa62e95': 'P23', 'bbad499c': 'FS2',
          'dac02fb9': 'dac02fb9'}
BLK_SKIP = 2
MIN_BLOCKS = 3
SHARE = 0.9


def mode_of(blocks):
    rb = blocks[BLK_SKIP:]
    if len(rb) < MIN_BLOCKS:
        return 'SHORT'
    if sum(b >= 600 for b in rb) >= SHARE * len(rb):
        return 'OLD'
    if sum(b <= 300 for b in rb) >= SHARE * len(rb):
        return 'NEW'
    return 'MIXED'


def main(src, out):
    agg = defaultdict(lambda: defaultdict(int))
    seen = set()
    with lzma.open(src, 'rt', encoding='utf-8') as fh:
        for line in fh:
            r = json.loads(line)
            sha = r.get('binary_sha256') or ''
            b = COURSE.get(sha[:8]) if isinstance(sha, str) else None
            if b is None:
                continue
            vals = set(re.search(r'mode (\d)', l).group(1) for _, l in r.get('lines', {}).get('RTS', []) if 'mode ' in l)
            if vals != {'1'}:
                continue
            for e in r['entries'][1:]:
                if e['frames'] < 1000:
                    continue
                lv = (re.search(r'Level has started: (\S*)', e['line']) or [None, '?'])[1] or '(empty)'
                key = (b, lv, e['frames'])
                if key in seen:
                    continue
                seen.add(key)
                md = mode_of(e.get('bda_blocks') or [])
                for k in (md, 'ALL'):
                    a = agg[(lv, k)]
                    a['entries'] += 1
                    a['frames'] += e['frames']
                    a['rts_n'] += e['rts'].get('rts_n', 0)
                    a['rts_skip'] += e['rts'].get('rts_skip', 0)
    with open(out, 'w', encoding='ascii', newline='\n') as o:
        o.write('level\tmode\tentries\tframes\trts_n\trts_skip\tskip_share\n')
        for (lv, md) in sorted(agg):
            a = agg[(lv, md)]
            sh = '%.4f' % (a['rts_skip'] / a['rts_n']) if a['rts_n'] else 'nan'
            o.write('%s\t%s\t%d\t%d\t%d\t%d\t%s\n' % (lv, md, a['entries'], a['frames'], a['rts_n'], a['rts_skip'], sh))
    print('rows', len(agg))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
