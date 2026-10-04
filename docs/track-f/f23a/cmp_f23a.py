"""F23a (HPP-578): compares the real decoder pass (dec_<set>.txt, KYTY_F23A_DECODE) with the own parser
(scan_<set>.jsonl, gcn_f23a.py): per program the VALU histogram (family:opcode_id -> count) must be equal; lists every
'U' (UNSUPPORTED) line of the real decoder by family and reason; prints ALL OK when every program matches.
Usage: python cmp_f23a.py t1|eboot"""
import collections
import json
import os
import re
import sys

D = 'C:/kyty/f287/f23a/'


def main(setname):
    own = {}
    for line in open(D + 'scan_%s.jsonl' % setname, encoding='utf-8'):
        r = json.loads(line)
        own[r['hash']] = r
    real = {}
    cur = None
    unsup = []
    crashes = []
    for line in open(D + 'dec_%s.txt' % setname, encoding='utf-8', errors='replace'):
        line = line.rstrip(chr(10))
        if line.startswith('P '):
            path = line.split()[2]
            h = re.search(r'([0-9a-f]{16})\.bin$', path).group(1)
            cur = h
            real[h] = {'hist': {}, 'inst': None, 'front': 'front=1' in line}
        elif line.startswith('U '):
            unsup.append((cur, line[2:]))
        elif line.startswith('H'):
            for tok in line[1:].split():
                fam, op, c = tok.split(':')
                real[cur]['hist']['%s:%x' % (fam, int(op, 16))] = int(c)
        elif line.startswith('E '):
            real[cur]['inst'] = int(line.split('inst=')[1])
        elif line.startswith('C '):
            crashes.append(line)
    match = diff = 0
    inst_eq = 0
    examples = []
    for h, r in real.items():
        o = own.get(h)
        if o is None:
            diff += 1
            examples.append((h, 'not in own scan'))
            continue
        if o['hist'] == r['hist']:
            match += 1
        else:
            diff += 1
            if len(examples) < 5:
                ks = set(o['hist']) | set(r['hist'])
                examples.append((h, [(k, o['hist'].get(k), r['hist'].get(k)) for k in sorted(ks)
                                     if o['hist'].get(k) != r['hist'].get(k)][:6]))
        if r['inst'] == o['n_inst']:
            inst_eq += 1
    print('set', setname, 'real decoder programs', len(real), 'own', len(own), 'crashes', len(crashes))
    print('VALU histogram equal', match, 'different', diff, '; instruction count equal', inst_eq)
    for e in examples:
        print('  DIFF', e)
    fam = collections.Counter()
    for h, u in unsup:
        m = re.search(r'family=(\w+) opcode=(0x[0-9a-f]+) .*reason=(.*)$', u)
        fam[(m.group(1), m.group(2), m.group(3)) if m else ('?', '?', u[:80])] += 1
    print('real decoder UNSUPPORTED instructions', len(unsup), 'in programs', len(set(h for h, _ in unsup)))
    for k, v in fam.most_common():
        print('  U', k, v)
    for c in crashes[:5]:
        print('  ', c[:300])
    tot_real = collections.Counter()
    for r in real.values():
        for k, v in r['hist'].items():
            tot_real[k] += v
    print('real decoder VALU instructions', sum(tot_real.values()), 'distinct family:op', len(tot_real))
    ok = diff == 0 and not crashes
    print('ALL OK' if ok else 'MISMATCH')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
