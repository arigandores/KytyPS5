#!/usr/bin/env python3
# F25h (HPP-675): the table of the 22 frames of item 611(d)(2) - 18 with the reader chain
# "Gpu(Gpu)=W:emu_mutex->waker > Present(Present)=Sw" and the 4 frames in count of the cold layer - from the outputs of
# f25h_scan.py (scan_<tag>.txt). Checks the counts 10 / 5 / 3 and 1 + 3 and prints one row per frame.
# usage: f25h_table.py scan_f25_s15.txt scan_f25_k04.txt scan_f25_k05.txt
import re
import sys

want_chain = {'f25_s15': 10, 'f25_k04': 5, 'f25_k05': 3}
want_count = {'f25_k04': [8966], 'f25_k05': [17344, 17394, 17512]}
rows = []
for path in sys.argv[1:]:
    cur = None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'FRAME (\S+) n (\d+) dt_us (\d+) t ([\d.]+) \| (.*?) \|', line)
        if m:
            cur = {'tag': m.group(1), 'n': int(m.group(2)), 'dt': int(m.group(3)), 't': float(m.group(4)),
                   'chain': 'CHAIN' in m.group(5), 'count': 'IN_COUNT' in m.group(5), 'w': [], 't_': {}}
            rows.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r'  -t (\S+?)/(\S+) R .*? Sw (\d+) .*? H (\S+) SwR (\S+) cpu_us', line)
        if m:
            cur['t_'][m.group(1)] = (m.group(3), m.group(5), m.group(4))
        m = re.match(r'  -w emu_mutex waiter (\S+)\(slot \d+\) obj (\S+) off (\S+) (.*?) start_us \S+ wait_us (\d+) waker \S+\((\S+)\)', line)
        if m:
            cur['w'].append((m.group(1), m.group(4), int(m.group(5)), m.group(6)))
        m = re.match(r'  FrameTrace-draw n=\d+ logs (\S+) log_us (\S+) log_gpu_us (\S+)', line)
        if m:
            cur['log'] = (m.group(2), m.group(3))
        m = re.match(r'  FlipHold flip=\d+ us (\d+) present_us (\d+) poll_us (\d+) other_us (\d+)', line)
        if m:
            cur['fh'] = tuple(int(x) for x in m.groups())

sel = [r for r in rows if r['chain'] or r['count']]
ok = True
for tag, k in want_chain.items():
    got = sum(1 for r in sel if r['tag'] == tag and r['chain'])
    print('chain frames %s: %d (reader read.txt; item 611(g): %d)' % (tag, got, k))
    ok &= got == k
for tag, ns in want_count.items():
    got = sorted(r['n'] for r in sel if r['tag'] == tag and r['count'])
    print('in-count frames %s: %s (item 611(v): %s)' % (tag, got, ns))
    ok &= got == ns
print('frames of item 611(d)(2) (chain or cold in count): %d' % sum(1 for r in sel if r['tag'] != 'f25_s15' or r['chain']))
print('tag | n | dt_us | set | Gpu emu_mutex record (waiter obj wait_us waker) | Present Sw SwR H | Gpu Sw SwR | DrawThread Sw SwR | '
      'log_us log_gpu_us | FlipHold(n-1) us present poll other | other/dt')
for r in sel:
    if r['tag'] == 'f25_s15' and not r['chain']:
        continue  # f25_s15 in-count frames (HOST_LOAD) are not of item 611(d)(2); printed by scan_f25_s15.txt
    gw = [w for w in r['w'] if w[0] == 'Gpu/Gpu']
    gw = max(gw, key=lambda w: w[2]) if gw else None
    p = r['t_'].get('Present', ('-', '-', '-'))
    g = r['t_'].get('Gpu', ('-', '-', '-'))
    d = r['t_'].get('DrawThread', ('-', '-', '-'))
    fh = r.get('fh')
    ratio = '%.3f' % (fh[3] / r['dt']) if fh else '-'
    print('%s | %d | %d | %s | %s | %s %s %s | %s %s | %s %s | %s %s | %s | %s' % (
        r['tag'], r['n'], r['dt'], ('CHAIN' if r['chain'] else '') + ('+COUNT' if r['count'] else ''),
        ('Gpu %s %d waker %s' % (gw[1], gw[2], gw[3])) if gw else 'no Gpu emu_mutex record',
        p[0], p[1], p[2], g[0], g[1], d[0], d[1], r.get('log', ('-', '-'))[0], r.get('log', ('-', '-'))[1],
        ('%d %d %d %d' % fh) if fh else '-', ratio))
print('COUNTS OK' if ok else 'COUNTS MISMATCH')
