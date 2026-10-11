"""F42b2 (HPP-780, Red Team; ROADMAP s122 item 694(g)(1), (g)(5)): own recount of an F20 stand run from the TSV rows -
written independently of sum_stand_f42a.py. Per row: identity lost = expected_bits - seen_bits, mode column = file mode.
Per (mode, arm): rounds, sum of expected/seen/lost/extra/words_lost/out_nonzero, rounds with loss. The 'F20Stand: sum'
lines of <dir>/m<k>.out.txt must equal the recount. Members of 694(g)(1) at R rounds:
  =0: W lost > 0 (positive control), S lost = 0 (zero control); X - reading line;
  =1: W, X, S lost = 0 in every round; N: form line unmatched >= 1;
  everywhere extra = 0, out_nonzero = 0; form line of every arm: wave 32 subgroup 32 lane_count 1 local 64x1x1
  returns_main 1 valid 1; at =1 arms W, X, S: sites = rewritten = 1, unmatched 0.
Mutant mode (--mutant <name> <expect>): reads only the files present (m0 / m1) and prints which members fail;
'caught' = at least one member fails. Usage:
  python rc_stand_f42b2.py <dir> [m0,m1]            -> ALL OK / FAIL
  python rc_stand_f42b2.py <dir> m1 --mutant         -> CAUGHT <members> / NOT CAUGHT
"""
import re
import sys
from collections import defaultdict

D = sys.argv[1]
MODES = sys.argv[2].split(',') if len(sys.argv) > 2 else ['m0', 'm1']
MUT = '--mutant' in sys.argv
fails = []


def check(cond, name):
    if not cond:
        fails.append(name)


for m in MODES:
    mode = m[1:]
    lines = open('%s/%s.tsv' % (D, m), encoding='utf-8').read().splitlines()
    head = lines[0].split('\t')
    col = {k: i for i, k in enumerate(head)}
    acc = defaultdict(lambda: defaultdict(int))
    bad_ident = 0
    for ln in lines[1:]:
        r = ln.split('\t')
        arm = r[col['arm']]
        e = int(r[col['expected_bits']])
        s = int(r[col['seen_bits']])
        lo = int(r[col['lost']])
        if lo != e - s or r[col['mode']] != mode:
            bad_ident += 1
        a = acc[arm]
        a['rounds'] += 1
        a['rounds_with_loss'] += 1 if lo > 0 else 0
        a['expected_bits'] += e
        a['seen_bits'] += s
        a['lost'] += lo
        for k in ('extra', 'words_lost', 'out_nonzero'):
            a[k] += int(r[col[k]])
    check(bad_ident == 0, '%s identity rows bad %d' % (m, bad_ident))
    out = open('%s/%s.out.txt' % (D, m), encoding='utf-8', errors='replace').read()
    forms = {}
    for f in re.finditer(r'F20Stand: form (.*)', out):
        kv = dict(x.split('=', 1) for x in f.group(1).split())
        forms[kv['arm']] = kv
    sums = {}
    for f in re.finditer(r'F20Stand: sum (.*)', out):
        kv = dict(x.split('=', 1) for x in f.group(1).split())
        sums[kv['arm']] = kv
    for arm in ('W', 'X', 'S', 'N'):
        a = acc[arm]
        print('%s arm=%s rounds=%d expected=%d seen=%d lost=%d rounds_with_loss=%d extra=%d words_lost=%d out_nonzero=%d' % (
            m, arm, a['rounds'], a['expected_bits'], a['seen_bits'], a['lost'], a['rounds_with_loss'], a['extra'],
            a['words_lost'], a['out_nonzero']))
        sm = sums.get(arm, {})
        check(sm.get('lost') == str(a['lost']) and sm.get('expected_bits') == str(a['expected_bits'])
              and sm.get('extra') == str(a['extra']) and sm.get('words_lost') == str(a['words_lost'])
              and sm.get('rounds_with_loss') == str(a['rounds_with_loss']), '%s %s sum line != recount' % (m, arm))
        check(a['extra'] == 0, '%s %s extra' % (m, arm))
        check(a['out_nonzero'] == 0, '%s %s out_nonzero' % (m, arm))
        fm = forms.get(arm, {})
        check(fm.get('wave') == '32' and fm.get('subgroup') == '32' and fm.get('lane_count') == '1'
              and fm.get('local') == '64x1x1' and fm.get('returns_main') == '1' and fm.get('valid') == '1',
              '%s %s form' % (m, arm))
    if mode == '0':
        check(acc['W']['lost'] > 0, 'm0 W lost > 0 (positive control)')
        check(acc['S']['lost'] == 0, 'm0 S lost = 0 (zero control)')
        print('reading m0 X lost=%d of %d, rounds_with_loss=%d' % (acc['X']['lost'], acc['X']['expected_bits'],
                                                                   acc['X']['rounds_with_loss']))
    else:
        for arm in ('W', 'X', 'S'):
            check(acc[arm]['rounds'] > 0 and acc[arm]['rounds_with_loss'] == 0, 'm1 %s lost = 0 in every round' % arm)
            fm = forms.get(arm, {})
            check(fm.get('sites') == '1' and fm.get('rewritten') == '1' and fm.get('unmatched') == '0',
                  'm1 %s sites=rewritten=1 unmatched=0' % arm)
        check(int(forms.get('N', {}).get('unmatched', '0')) >= 1, 'm1 N unmatched >= 1')

if MUT:
    print('CAUGHT ' + ' | '.join(fails) if fails else 'NOT CAUGHT')
else:
    for f in fails:
        print('FAIL', f)
    print('ALL OK' if not fails else 'FAIL')
