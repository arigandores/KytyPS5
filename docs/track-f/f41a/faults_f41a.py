# F41a (HPP-774): census of the fault path in FS12 tag logs (FS12c, installed binary 46892c20, Sky Garden).
# Every line 'Accessed non-GPU cached memory at 0x<addr>' is one page of one ProcessFaultBuffer readback
# (faultManager.cpp, deferred operation). Lines of one readback are printed together; a gap of > 20 log lines
# starts a new readback ('pass'). Prints per log: sha256, line of 'Level has started', number of fault lines,
# distinct pages, repeats, passes with their pages as <bitmap word>:<bit> (word = addr >> 19, bit = (addr >> 14) & 31).
# Last line ALL OK when every log was read. Usage: python faults_f41a.py <log> [<log> ...]
import collections, hashlib, os, sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
ok = True
for fn in sys.argv[1:]:
    h = hashlib.sha256()
    ev, lvl, tot = [], None, 0
    with open(fn, 'rb') as f:
        for i, l in enumerate(f):
            h.update(l)
            if b'Accessed non-GPU cached memory at 0x' in l:
                ev.append((i + 1, int(l.split(b'0x')[1][:16], 16)))
            if lvl is None and b'Level has started' in l:
                lvl = i + 1
            tot = i + 1
    pages = collections.Counter(a for _, a in ev)
    print('log', os.path.basename(fn), 'sha256', h.hexdigest(), 'lines', tot, 'level_started_line', lvl)
    print('  fault_lines', len(ev), 'distinct_pages', len(pages), 'max_repeat', max(pages.values()) if pages else 0,
          'first_line', ev[0][0] if ev else None, 'last_line', ev[-1][0] if ev else None)
    groups, last = [], -10 ** 9
    for i, a in ev:
        if i - last > 20:
            groups.append([])
        groups[-1].append(a)
        last = i
    print('  passes', len(groups))
    for k, g in enumerate(groups):
        print('   pass', k + 1, 'n', len(g), ' '.join('%d:%d' % (a >> 19, (a >> 14) & 31) for a in g))
    words = collections.defaultdict(set)
    for a in pages:
        words[a >> 19].add((a >> 14) & 31)
    for w in sorted(words):
        print('  word', w, 'bits', len(words[w]), sorted(words[w]))
    ok &= len(ev) > 0
print('ALL OK' if ok else 'FAIL')
