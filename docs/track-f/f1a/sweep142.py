import glob, re, collections, hashlib
rx = re.compile(rb'hash=([0-9a-f]{16}) reason=.*?at pc (0x[0-9a-f]+).*?family=(\w+) opcode=(0x[0-9a-f]+)')
res = {}
for f in sorted(glob.glob('C:/kyty/s142/log_*.txt')):
    hs = set()
    pre = collections.Counter()
    fatal_other = 0
    first_ln = last_ln = None
    level_ln = None
    with open(f, 'rb') as fh:
        for ln, line in enumerate(fh, 1):
            if level_ln is None and b'Level has started' in line:
                level_ln = ln
            if b'shader CFG build failed' in line:
                if not line.startswith(b'CsPretranslate: skipped'):
                    fatal_other += 1
                m = rx.search(line)
                if m and b'unsupported decoded instruction' in line:
                    hs.add(m.groups())
                    first_ln = first_ln or ln
                    last_ln = ln
                pre[line[:24]] += 1
    key = hashlib.sha256(b''.join(sorted(b' '.join(x) for x in hs))).hexdigest()[:16]
    res[f] = key
    print(f.split('\\')[-1], 'lines', sum(pre.values()), 'distinct(hash,pc,op)', len(hs), 'set_sha', key,
          'non-pretranslate CFG fails', fatal_other, 'first/last line', first_ln, last_ln, 'level line', level_ln)
print('identical sets:', len(set(res.values())) == 1)
