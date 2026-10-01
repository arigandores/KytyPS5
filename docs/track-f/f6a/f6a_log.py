# F6a (HPP-372): AudioPropagation lines of a log - stream scan in binary mode.
# usage: f6a_log.py <log> ; prints counts per symbol/function, first/last line numbers, order of first occurrences, thread ids.
import sys, re, collections, hashlib
path = sys.argv[1]
h = hashlib.sha256()
cnt = collections.Counter(); first = {}; last = {}; samples = collections.defaultdict(list)
tids = collections.defaultdict(collections.Counter)
events = []           # (line, kind, text) for first occurrences and level markers
seq = []              # compact sequence of stub calls (symbol letters) in order
relo = []
rx_call = re.compile(rb'Unresolved import stub called \[(\d+)\]: patch_vaddr=0x([0-9a-f]+) jmprela_index=(\d+) symbol=(\S+)')
rx_tid = re.compile(rb'^\[(\d+)\]\[([0-9:.]+)\]')
n = 0; total_stub = 0; last_idx = -1
with open(path, 'rb') as f:
    for line in f:
        n += 1
        h.update(line)
        if b'AudioPropagation' not in line and b'Level has started' not in line and b'Unresolved import stub called' not in line:
            continue
        if b'Level has started' in line:
            events.append((n, 'level', line.strip()[:160].decode('latin1')))
            continue
        if b'unresolved PLT import patched' in line or b'unresolved non-PLT' in line:
            if b'AudioPropagation' in line:
                relo.append((n, line.strip()[:260].decode('latin1')))
            continue
        m = rx_call.search(line)
        if m:
            total_stub += 1
            last_idx = max(last_idx, int(m.group(1)))
            sym = m.group(4).decode('latin1')
            key = 'STUB ' + sym.split('[')[0] + (' AudioPropagation' if 'AudioPropagation' in sym else ' OTHER:' + sym)
            pv = m.group(2).decode(); key += ' patch=0x' + pv
            seq.append((n, sym.split('[')[0], int(m.group(1))))
        elif b'Unresolved import stub called' in line:
            key = 'STUBPRINTF ' + line.strip()[:120].decode('latin1')
        else:
            t = rx_tid.match(line)
            body = line.strip().decode('latin1')
            mm = re.search(r'(\w*AudioPropagation\w*)', body)
            key = 'LINE ' + (mm.group(1) if mm else body[:80])
            if t: tids[key][t.group(1).decode()] += 1
        cnt[key] += 1
        if key not in first:
            first[key] = n; events.append((n, 'first', key))
        last[key] = n
        if len(samples[key]) < 2: samples[key].append(line.strip()[:300].decode('latin1'))
print('log %s lines %d sha256 %s' % (path, n, h.hexdigest()))
print('stub LOGF lines total %d, max index %d' % (total_stub, last_idx))
for k in sorted(cnt, key=lambda k: first[k]):
    print('%7d  first %9d last %9d  %s  tids=%s' % (cnt[k], first[k], last[k], k, dict(tids.get(k, {}))))
    for s in samples[k]: print('          | ' + s)
print('--- relocation lines with AudioPropagation: %d' % len(relo))
for ln, s in relo: print('%9d %s' % (ln, s))
print('--- events in order')
for e in events: print('%9d %-6s %s' % e)
# order of stub calls: run-length encoding of the symbol sequence
print('--- stub call sequence (run-length), first 60 runs and last 10')
runs = []
for ln, s, idx in seq:
    if runs and runs[-1][0] == s: runs[-1][2] += 1; runs[-1][3] = ln
    else: runs.append([s, ln, 1, ln])
print('runs %d' % len(runs))
for r in runs[:60]: print('   %s x%d lines %d..%d' % (r[0], r[2], r[1], r[3]))
print('   ...')
for r in runs[-10:]: print('   %s x%d lines %d..%d' % (r[0], r[2], r[1], r[3]))
pat = collections.Counter()
for i in range(len(runs) - 2): pat[(runs[i][0], runs[i][2], runs[i+1][0], runs[i+1][2], runs[i+2][0], runs[i+2][2])] += 1
print('--- most common 3-run patterns')
for k, v in pat.most_common(8): print('   %d x %s' % (v, k))
