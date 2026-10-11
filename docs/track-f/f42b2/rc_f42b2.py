"""F42b2 (HPP-806, Red Team; ROADMAP s122 item 705(b)(1), (3), (6)): own recount of a stand run of edition 2 (arms W, X, S,
N, E-W, E-X) from the TSV rows and the 'F20Stand:' lines - written for this link, independent of sum_stand_f42a2.py.

Per row: lost = expected_bits - seen_bits; mode column = the file's mode; seed column = the given seed; each arm has
exactly R rows and every round has the six arms once (positions 0..5). Per (mode, arm) sums; the 'F20Stand: sum' lines
must equal the recount. Lines 'F20Stand: emu' (E-W, E-X) and 'F20Stand: emu_stat' are read as numbers.

Members of item 705(b)(1) + edition 1 members kept (694(g)(1)):
  =0: W lost > 0 (positive control of the edition 1 arms), S lost = 0; E-W lost > 0 summed over R (positive control of
      the arm E); calls = 0 (both emu lines and emu_stat), emu_mode = 0;
  =1: W, X, S, E-W, E-X lost = 0 in every round; calls >= 1, rewritten >= 1 (each emu line and emu_stat), emu_mode = 1;
      N: form line unmatched >= 1;
  everywhere: extra = 0, out_nonzero = 0, form line wave 32 subgroup 32 lane_count 1 local 64x1x1 returns_main 1 valid 1.
Catch rules (named before the mutant data, ROADMAP 705(b)(1), (6)):
  m1b - at =1 E-W or E-X lost > 0;      m6 - at =0 calls > 0 or E-W lost = 0;
  m1a - at =1 W lost > 0;               m4 - at =1 X lost > 0;         m5 - at =1 N form unmatched = 0.
Usage:
  python rc_f42b2.py <dir> <seed> <R> [m0,m1]                 -> per-member lines, ALL OK / NOT OK
  python rc_f42b2.py <dir> <seed> <R> <m0,m1|m1> --mutant <m> -> member lines, then CAUGHT <rule> / NOT CAUGHT
"""
import re
import sys
from collections import defaultdict

D, SEED, R = sys.argv[1], sys.argv[2], int(sys.argv[3])
MODES = sys.argv[4].split(',') if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else ['m0', 'm1']
MUT = sys.argv[sys.argv.index('--mutant') + 1] if '--mutant' in sys.argv else None
ARMS = ['W', 'X', 'S', 'N', 'E-W', 'E-X']
res = {}      # (mode, member) -> bool
fails = []
data = {}


def member(mode, name, cond):
    res[(mode, name)] = bool(cond)
    print('%s %-48s %s' % (mode, name, 'yes' if cond else 'NO'))
    if not cond:
        fails.append('%s:%s' % (mode, name))


def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))


for m in MODES:
    mode = m[1:]
    rows = open('%s/%s.tsv' % (D, m), encoding='utf-8').read().splitlines()
    col = {k: i for i, k in enumerate(rows[0].split('\t'))}
    acc = defaultdict(lambda: defaultdict(int))
    per_round = defaultdict(list)
    bad = 0
    for ln in rows[1:]:
        r = ln.split('\t')
        g = lambda k: r[col[k]]
        arm = g('arm')
        e, s, lost = int(g('expected_bits')), int(g('seen_bits')), int(g('lost'))
        bad += (lost != e - s) + (g('mode') != mode) + (g('seed') != SEED) + (arm not in ARMS)
        per_round[int(g('round'))].append((int(g('position')), arm))
        a = acc[arm]
        a['rounds'] += 1
        a['expected'] += e
        a['seen'] += s
        a['lost'] += lost
        a['extra'] += int(g('extra'))
        a['words_lost'] += int(g('words_lost'))
        a['out_nonzero'] += int(g('out_nonzero'))
        a['rounds_with_loss'] += lost > 0
    out = open('%s/%s.out.txt' % (D, m), encoding='utf-8', errors='replace').read().splitlines()
    sums = {kv(x)['arm']: kv(x) for x in out if x.startswith('F20Stand: sum ')}
    forms = {kv(x)['arm']: kv(x) for x in out if x.startswith('F20Stand: form ')}
    emus = {kv(x)['arm']: kv(x) for x in out if x.startswith('F20Stand: emu ')}
    stat = [kv(x) for x in out if x.startswith('F20Stand: emu_stat ')]
    data[mode] = (acc, forms, emus, stat)
    member(mode, 'rows identity/mode/seed/arm name (bad=%d)' % bad, bad == 0)
    member(mode, 'R rows per arm, six arms per round', all(acc[x]['rounds'] == R for x in ARMS) and len(per_round) == R and
           all(sorted(p for p, _ in v) == list(range(6)) and sorted(a for _, a in v) == sorted(ARMS)
               for v in per_round.values()))
    member(mode, 'sum lines = recount', all(
        x in sums and int(sums[x]['lost']) == acc[x]['lost'] and int(sums[x]['expected_bits']) == acc[x]['expected'] and
        int(sums[x]['rounds_with_loss']) == acc[x]['rounds_with_loss'] and int(sums[x]['extra']) == acc[x]['extra'] and
        int(sums[x]['words_lost']) == acc[x]['words_lost'] and int(sums[x]['rounds']) == acc[x]['rounds'] for x in ARMS))
    member(mode, 'extra 0, out_nonzero 0 everywhere', all(acc[x]['extra'] == 0 and acc[x]['out_nonzero'] == 0 for x in ARMS))
    member(mode, 'form lines (wave/subgroup/lanes/local/return/valid)', all(
        x in forms and forms[x]['wave'] == '32' and forms[x]['subgroup'] == '32' and forms[x]['lane_count'] == '1' and
        forms[x]['local'] == '64x1x1' and forms[x]['returns_main'] == '1' and forms[x]['valid'] == '1' for x in ARMS))
    member(mode, 'emu lines E-W, E-X present, module=1, bound_flag=1', all(
        x in emus and emus[x]['module'] == '1' and emus[x]['bound_flag'] == '1' for x in ('E-W', 'E-X')) and len(stat) == 1)
    for x in ARMS:
        print('%s   %-4s rounds %d expected %d seen %d lost %d rounds_with_loss %d words_lost %d' % (
            mode, x, acc[x]['rounds'], acc[x]['expected'], acc[x]['seen'], acc[x]['lost'], acc[x]['rounds_with_loss'],
            acc[x]['words_lost']))
    for x in ('E-W', 'E-X'):
        if x in emus:
            print('%s   emu %s emu_mode %s calls %s rewritten %s' % (mode, x, emus[x]['emu_mode'], emus[x]['calls'],
                                                                  emus[x]['rewritten']))
    if stat:
        print('%s   emu_stat emu_mode %s calls %s rewritten %s' % (mode, stat[0]['emu_mode'], stat[0]['calls'],
                                                                  stat[0]['rewritten']))
    calls = [int(emus[x]['calls']) for x in ('E-W', 'E-X') if x in emus] + [int(s['calls']) for s in stat]
    rew = [int(emus[x]['rewritten']) for x in ('E-W', 'E-X') if x in emus] + [int(s['rewritten']) for s in stat]
    emode = {emus[x]['emu_mode'] for x in emus} | {s['emu_mode'] for s in stat}
    if mode == '0':
        member(mode, 'W lost > 0 (positive control, edition 1 arms)', acc['W']['lost'] > 0)
        member(mode, 'S lost = 0 (zero control)', acc['S']['lost'] == 0)
        member(mode, 'E-W lost > 0 summed over R (positive control arm E)', acc['E-W']['lost'] > 0)
        member(mode, 'calls = 0 (emu lines and emu_stat)', calls and all(c == 0 for c in calls))
        member(mode, 'emu_mode = 0', emode == {'0'})
    else:
        for x in ('W', 'X', 'S', 'E-W', 'E-X'):
            member(mode, '%s lost = 0 in every round' % x, acc[x]['rounds_with_loss'] == 0 and acc[x]['lost'] == 0)
        member(mode, 'calls >= 1 and rewritten >= 1 (each emu line, emu_stat)', calls and all(c >= 1 for c in calls) and
               all(c >= 1 for c in rew))
        member(mode, 'emu_mode = 1', emode == {'1'})
        member(mode, 'N form unmatched >= 1', int(forms.get('N', {}).get('unmatched', '0')) >= 1)

if MUT:
    rule = {
        'm1b': ('=1 E-W or E-X lost > 0', '1' in data and (data['1'][0]['E-W']['lost'] > 0 or data['1'][0]['E-X']['lost'] > 0)),
        'm6': ('=0 calls > 0 or E-W lost = 0', '0' in data and (
            any(int(e['calls']) > 0 for e in data['0'][1 + 1].values()) or any(int(s['calls']) > 0 for s in data['0'][3]) or
            data['0'][0]['E-W']['lost'] == 0)),
        'm1a': ('=1 W lost > 0', '1' in data and data['1'][0]['W']['lost'] > 0),
        'm4': ('=1 X lost > 0', '1' in data and data['1'][0]['X']['lost'] > 0),
        'm5': ('=1 N form unmatched = 0', '1' in data and data['1'][1].get('N', {}).get('unmatched') == '0'),
    }[MUT]
    print('mutant %s rule [%s]: %s; failing members: %s' % (MUT, rule[0], 'CAUGHT' if rule[1] else 'NOT CAUGHT',
                                                           ', '.join(fails) or '-'))
else:
    print('ALL OK' if not fails else 'NOT OK ' + ', '.join(fails))
