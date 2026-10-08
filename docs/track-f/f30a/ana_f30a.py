# F30a (HPP-706, ROADMAP s122 item 640(d)(1)(ii)-(iii)): reading of sweep_f30a.jsonl.
#   (ii)  every log with a line 'RtSkip: mode 2|3', 'RtSkip: refused' or 'RtSkipVerify:' - binary, scene, lines, rts_* sums;
#         the knob value of every log ('RtSkip: mode <v>' lines) - count by binary;
#   (iii) BDA mode of every scene entry by the bands of item 40(e)(1) over 90-frame blocks (mean <= 300 NEW, >= 600 OLD,
#         between - mixed), the first BLK_SKIP blocks of an entry (loading) excluded; by level on FS10 and on the course line; an entry
#         is OLD / NEW when >= 90 % of its read blocks are in the band, else MIXED.
# Duplicates (same size and the same first entry line set in another directory) are reported, not removed: the counts are
# of logs as listed.  usage: python ana_f30a.py <sweep.jsonl> <out.txt> <entries.tsv>
import json, re, sys
from collections import defaultdict

COURSE = {  # binary sha256 prefix -> name (the installed line, CLAUDE.md "Установлена сборка" chain)
    'abfded5e': 'FS10', '3861eeea': 'FS9', 'b3cee576': 'S18', '2c9b69b9': 'FS8', '8df61c00': 'FS7', '9325446c': 'FS6',
    'adb0c82f': 'S12', '631ff987': 'FS5', '31cbfee8': 'FS4', '540c035a': 'FS3', '4aa62e95': 'P23', 'bbad499c': 'FS2',
    'dac02fb9': 'dac02fb9', '9235a7ac': '9235a7ac', '98d98eee': 's127-98d98eee', 'd3a981a2': 'd3a981a2'}
BLK_SKIP = 2      # blocks (2 x 90 frames) after the entry line not read (entry transition)
MIN_BLOCKS = 3    # an entry is classified with at least 3 read blocks
SHARE = 0.9       # entry mode: >= 90 % of its read blocks in the band (a lone spike block does not make an entry mixed)
sweep, out, ent_out = sys.argv[1], sys.argv[2], sys.argv[3]
rows = [json.loads(l) for l in open(sweep, encoding='utf-8')]
o = open(out, 'w', encoding='utf-8', newline='\n')
P = lambda *a: print(*a, file=o)


def binname(r):
    sha = (r.get('binary_sha256') or '')
    sha = sha if isinstance(sha, str) else ''
    if sha[:8] in COURSE:
        return COURSE[sha[:8]], True
    if sha:
        return 'test:' + sha[:8], False
    v = [l for _, l in r.get('lines', {}).get('VER', [])]
    return 'nojson:' + (re.search(r'KytyPS5-[\w.-]+', v[0]).group(0) if v and re.search(r'KytyPS5-[\w.-]+', v[0]) else '?'), False


def level(e):
    m = re.search(r'Level has started: (\S*)', e['line'])
    return (m.group(1) if m else '?') or '(empty)'


def mode_of(blocks):
    rb = blocks[BLK_SKIP:]
    if len(rb) < MIN_BLOCKS:
        return 'SHORT', rb
    n_old = sum(b >= 600 for b in rb)
    n_new = sum(b <= 300 for b in rb)
    if n_old >= SHARE * len(rb):
        return 'OLD', rb
    if n_new >= SHARE * len(rb):
        return 'NEW', rb
    return 'MIXED', rb


P('logs', len(rows), 'empty', sum(1 for r in rows if r.get('empty')), 'xz', sum(1 for r in rows if r.get('xz')))
# ---- (ii) knob values seen
P('\n== (ii) RtSkip mode lines by binary (value -> logs)')
bym = defaultdict(lambda: defaultdict(int))
for r in rows:
    b, _ = binname(r)
    vals = sorted(set(re.search(r'mode (\d)', l).group(1) for _, l in r.get('lines', {}).get('RTS', []) if 'mode ' in l))
    bym[b][','.join(vals) or 'none'] += 1
for b in sorted(bym):
    P('  %-32s %s' % (b, dict(bym[b])))
P('\n== (ii) logs with RtSkip: mode 2|3, refused or RtSkipVerify:')
hits = []
for r in rows:
    L = r.get('lines', {})
    rts = [l for _, l in L.get('RTS', [])]
    rtv = L.get('RTV', [])
    m23 = [l for l in rts if re.search(r'mode [23]', l)]
    ref = [l for l in rts if 'refused' in l]
    gate = [l for _, l in L.get('GATE', [])]
    if m23 or ref or rtv:
        hits.append(r)
        b, _ = binname(r)
        P('-', r['path'], '|', b, '| xz' if r.get('xz') else '')
        P('    RTS:', rts[:6], ' GATE:', gate[:6], '(total %d)' % r.get('totals', {}).get('GATE', 0),
          ' GARM total', r.get('totals', {}).get('GARM', 0))
        P('    RTV lines total', r.get('totals', {}).get('RTV', 0))
        bits = defaultdict(int)
        for _, l in rtv:
            mm = re.search(r'bits=(0x[0-9a-f]+).*reg=(\d).*mode=(\d)', l)
            if mm:
                bits[(mm.group(3), mm.group(1), mm.group(2))] += 1
        P('    RTV (mode, bits, reg) -> lines:', dict(bits))
        for i, e in enumerate(r['entries']):
            rs = e['rts']
            if not rs and i == 0:
                continue
            P('    entry %d %-34s frames %5d bda_mean %s hold %s | rts_n %s skip %s chk %s chk_b %s bad %s noreg %s race %s refuse %s xthr %s acqw %s bad_lines %d'
              % (i - 1, level(e) if i else '(pre)', e['frames'], e['bda_mean'], None if e['hold_s'] is None else round(e['hold_s'], 1),
                 rs.get('rts_n'), rs.get('rts_skip'), rs.get('rts_chk'), rs.get('rts_chk_b'), rs.get('rts_bad'),
                 rs.get('rts_bad_noreg'), rs.get('rts_race'), rs.get('rts_refuse'), rs.get('rts_xthr'), rs.get('rts_acqw'),
                 e['rts_bad_lines']))
P('logs with mode 2|3 / refused / RTV:', len(hits))
# guards over every log: rts_xthr, rts_acqw, rts_refuse, rts_bad at value 1
P('\n== guards over all logs (sum over entries): rts_refuse, rts_xthr, rts_acqw; rts_bad in logs without mode 2|3')
g = defaultdict(int)
for r in rows:
    rts = [l for _, l in r.get('lines', {}).get('RTS', [])]
    m23 = any(re.search(r'mode [23]', l) for l in rts)
    for e in r.get('entries', []):
        for k in ('rts_refuse', 'rts_xthr', 'rts_acqw'):
            g[k] += e['rts'].get(k, 0)
        if not m23:
            g['rts_bad(no mode 2|3)'] += e['rts'].get('rts_bad', 0)
            g['rts_chk(no mode 2|3)'] += e['rts'].get('rts_chk', 0)
        g['rtsx_lines'] += e['rtsx_lines']
P(' ', dict(g))
# ---- (iii) BDA mode
P('\n== (iii) BDA mode by entry (blocks of 90 frames, first %d skipped, >= %d read blocks)' % (BLK_SKIP, MIN_BLOCKS))
lev = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
tsv = open(ent_out, 'w', encoding='utf-8', newline='\n')
tsv.write('path\tbinary\tcourse\tentry\tlevel\tframes\tblocks_read\tmode\tmean_read\tmin_blk\tmax_blk\tn_old_blk\tn_new_blk\thold_s\trtskip_values\n')
for r in rows:
    b, course = binname(r)
    rts = [l for _, l in r.get('lines', {}).get('RTS', [])]
    vals = ','.join(sorted(set(re.search(r'mode (\d)', l).group(1) for l in rts if 'mode ' in l))) or '-'
    for i, e in enumerate(r.get('entries', [])):
        if i == 0:
            continue
        md, rb = mode_of(e['bda_blocks'])
        lv = level(e)
        lev[b][lv][md] += 1
        tsv.write('%s\t%s\t%d\t%d\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s\n' % (
            r['path'], b, course, i - 1, lv, e['frames'], len(rb), md,
            round(sum(rb) / len(rb), 1) if rb else '', min(rb) if rb else '', max(rb) if rb else '',
            sum(x >= 600 for x in rb), sum(x <= 300 for x in rb),
            '' if e['hold_s'] is None else round(e['hold_s'], 1), vals))
tsv.close()
for b in ['FS10'] + sorted(x for x in lev if x != 'FS10'):
    if b not in lev:
        continue
    tot = defaultdict(int)
    for lv in lev[b]:
        for md, n in lev[b][lv].items():
            tot[md] += n
    P('  %s: %s' % (b, dict(tot)))
    if b in ('FS10',) or COURSE.get(b[:8]) or b in COURSE.values():
        for lv in sorted(lev[b]):
            d = lev[b][lv]
            if d.get('OLD') or d.get('MIXED') or b == 'FS10':
                P('     %-36s %s' % (lv, dict(d)))
o.close()
print(open(out, encoding='utf-8').read()[:200])
