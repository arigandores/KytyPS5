# F0 (HPP-289): the 12 logs of s142 - are the shaders with unexecuted opcodes (B26) ever requested by the normal path?
# plus: unresolved import stubs called, KernelRead fallback, CsStall, budget / resource tracking / dispatcher fallback.
import re, glob, collections, hashlib, sys

RE_SK = re.compile(rb'CsPretranslate: skipped hash=([0-9a-f]{16}) reason=(.*)$')
RE_H16 = re.compile(rb'\b(?:0x)?([0-9a-f]{16})\b')
tot = collections.Counter()
for f in sorted(glob.glob('C:/kyty/s142/log_*.txt')):
    tag = f.replace(chr(92), '/').split('/')[-1]
    skipped = {}      # hash -> class
    other = collections.defaultdict(collections.Counter)   # hash -> kinds of other lines
    stub = collections.Counter()
    stub_first = {}
    kread = 0
    kread_first = None
    csstall = []
    cs_summary = None
    lvl = None
    lines = []
    with open(f, 'rb') as fh:
        for i, line in enumerate(fh, 1):
            if b'CsPretranslate' in line or b'hash' in line or b'cs=' in line or b'Unresolved import stub called' in line \
               or b'KernelRead: direct' in line or b'CsStall' in line or b'Level has started: ' in line:
                lines.append((i, line.rstrip()))
    for i, line in lines:
        m = RE_SK.search(line)
        if m:
            r = m.group(2)
            if b'opcode is not implemented' in r:
                k = re.search(rb'family=(\w+) opcode=(0x\w+)', r)
                c = 'OP ' + k.group(1).decode() + ' ' + k.group(2).decode()
            elif b'budget exceeded' in r:
                c = 'BUDGET'
            elif b'resource tracking' in r:
                c = 'RESTRACK ' + r.split(b'pc=', 1)[-1].split(b' ', 1)[-1][:60].decode('latin1')
            else:
                c = 'OTHER ' + r[:80].decode('latin1')
            skipped[m.group(1)] = (c, i)
    for i, line in lines:
        if b'Level has started: ' in line:
            n = line.split(b'Level has started: ', 1)[1].strip()
            if n:
                lvl = (n.decode(), i)
        if b'Unresolved import stub called' in line:
            s = re.search(rb'symbol=(\S+)', line)
            k = s.group(1).decode('latin1') if s else '?'
            stub[k] += 1
            stub_first.setdefault(k, i)
        if b'KernelRead: direct' in line:
            kread += 1
            kread_first = kread_first or i
        if line.startswith(b'CsStall'):
            csstall.append((i, line.decode('latin1')[:120]))
        if b'CsPretranslate: summary' in line:
            cs_summary = line.decode('latin1')
        if RE_SK.search(line):
            continue
        for h in set(RE_H16.findall(line)):
            if h in skipped:
                kind = line.split(b'hash=')[0].split(b'cs=')[0][:60].decode('latin1').strip()
                kind = re.sub(r'\d+', 'X', kind)
                other[h][kind] += 1
    cls = collections.Counter(v[0].split(' pc')[0] if v[0].startswith('OP') else v[0].split(' ')[0] for v in skipped.values())
    print('==', tag, 'level', lvl, 'skipped hashes', len(skipped), dict(cls))
    ref = collections.Counter()
    for h, kinds in other.items():
        for k, n in kinds.items():
            ref[(skipped[h][0].split(' ')[0] + (' ' + ' '.join(skipped[h][0].split(' ')[1:3]) if skipped[h][0].startswith('OP') else ''), k)] += 1
    nref = sum(1 for h in skipped if h in other)
    print('   skipped hashes seen on any other line:', nref, 'of', len(skipped))
    for (c, k), n in sorted(ref.items(), key=lambda x: -x[1])[:25]:
        print('     ', n, 'hashes |', c, '|', k)
        tot[(c, k)] += n
    if stub:
        print('   STUB CALLED:', {k: (v, stub_first[k]) for k, v in stub.items()})
    if kread:
        print('   KernelRead direct read failed:', kread, 'first line', kread_first)
    if csstall:
        print('   CsStall:', csstall[:6])
    print('  ', cs_summary)
print('TOTAL over 12 logs (class, kind of other line) -> hashes:')
for (c, k), n in sorted(tot.items(), key=lambda x: -x[1]):
    print('  ', n, '|', c, '|', k)
