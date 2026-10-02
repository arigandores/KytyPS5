"""rdsum_f7a.py - F7a (HPP-397; ROADMAP p.327(e)): the summary of the rd_list.py listing of one capture (C:/kyty/scripts/rd_list.py
writes C:/kyty/rd_list.txt): number of DRAW / DISPATCH / CLEAR / COPY / PRESENT actions, the passes (maximal runs of consecutive
DRAW actions with the same render-target set and depth target) and the targets (each RT/DS set with its draw count).
ASCII only (p.175(v)).
  python rdsum_f7a.py <rd_list.txt> [--out <summary.txt>]
The last line starts with 'RDSUM' (draws, passes, targets, the 'done' marker of rd_list.py present or not).
"""
import re
import sys

RX_ACT = re.compile(r'^\s*EID=(\d+) (DRAW|DISPATCH|CLEAR|COPY|PRESENT) (.*)$')


def summarize(lines):
    kinds = dict(DRAW=0, DISPATCH=0, CLEAR=0, COPY=0, PRESENT=0)
    passes = []  # [first eid, last eid, count, target]
    targets = {}
    done = False
    capture = None
    for line in lines:
        line = line.rstrip('\r\n')
        if line.startswith('capture:'):
            capture = line[len('capture:'):].strip()
        if line.strip() == 'done':
            done = True
        m = RX_ACT.match(line)
        if not m:
            continue
        eid, kind, rest = int(m.group(1)), m.group(2), m.group(3)
        kinds[kind] += 1
        if kind != 'DRAW':
            passes.append(None)
            continue
        tgt = rest.split(' | ', 1)[1] if ' | ' in rest else '(no target)'
        targets[tgt] = targets.get(tgt, 0) + 1
        if passes and passes[-1] is not None and passes[-1][3] == tgt:
            passes[-1][1] = eid
            passes[-1][2] += 1
        else:
            passes.append([eid, eid, 1, tgt])
    passes = [p for p in passes if p is not None]
    return dict(kinds=kinds, passes=passes, targets=targets, done=done, capture=capture)


def render(s):
    out = []
    out.append('capture: %s' % s['capture'])
    out.append('actions: ' + ', '.join('%s %d' % (k, v) for k, v in s['kinds'].items()))
    out.append('passes (runs of consecutive DRAW with one RT/DS set): %d' % len(s['passes']))
    for i, p in enumerate(s['passes']):
        out.append('  pass %d: EID %d..%d draws %d | %s' % (i, p[0], p[1], p[2], p[3][:400]))
    out.append('targets (distinct RT/DS sets): %d' % len(s['targets']))
    for t, c in sorted(s['targets'].items(), key=lambda x: -x[1]):
        out.append('  draws %d | %s' % (c, t[:400]))
    out.append('RDSUM: draws %d, dispatches %d, clears %d, copies %d, presents %d, passes %d, targets %d, done marker %s' % (
        s['kinds']['DRAW'], s['kinds']['DISPATCH'], s['kinds']['CLEAR'], s['kinds']['COPY'], s['kinds']['PRESENT'],
        len(s['passes']), len(s['targets']), 'yes' if s['done'] else 'NO'))
    return '\n'.join(x.encode('ascii', 'replace').decode('ascii') for x in out)


def main(argv):
    if not argv:
        print('usage: rdsum_f7a.py <rd_list.txt> [--out <summary.txt>]')
        return 2
    try:
        with open(argv[0], encoding='utf-8', errors='replace') as f:
            s = summarize(f)
    except OSError as e:
        print('RDSUM: no listing (%s)' % type(e).__name__)
        return 2
    text = render(s)
    if '--out' in argv:
        with open(argv[argv.index('--out') + 1], 'w', encoding='ascii') as f:
            f.write(text + '\n')
    print(text.splitlines()[-1])
    return 0 if s['done'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
