import sys, re, collections
path = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s142/log_v142.txt'
rx = re.compile(rb'at pc (0x[0-9a-fA-F]+).*?family=(\w+) opcode=(0x[0-9a-fA-F]+) raw=\[([^\]]*)\]')
rxh = re.compile(rb'hash=(?:0x)?([0-9a-fA-F]+)')
by = collections.Counter()
shaders = collections.defaultdict(set)
prefixes = collections.Counter()
examples = {}
other = collections.Counter()
last_stage = {}
stage_rx = re.compile(rb'stage=(\w+) hash=0x([0-9a-fA-F]+) code_words=(\d+)')
words = {}
with open(path, 'rb') as f:
    for ln, line in enumerate(f, 1):
        m = stage_rx.search(line)
        if m:
            words[m.group(2).lower()] = (m.group(1), int(m.group(3)))
        if b'implemented' not in line and b'unsupported' not in line:
            continue
        m = rx.search(line)
        if not m:
            other[re.sub(rb'0x[0-9a-fA-F]+|\b[0-9a-fA-F]{6,}\b|\d+', b'X', line.strip())[:300]] += 1
            continue
        pc, fam, op, raw = m.groups()
        h = rxh.search(line)
        hh = h.group(1).lower() if h else b'?'
        pre = line.split(b':')[0][:60]
        prefixes[pre] += 1
        key = (fam, op, raw)
        by[key] += 1
        shaders[key].add((hh, pc))
        examples.setdefault(key, (ln, line.strip()[:700]))
for k, v in by.most_common():
    print(k[0].decode(), k[1].decode(), k[2].decode(), 'lines', v, 'shaders', len({s for s, _ in shaders[k]}))
    print('  example', examples[k][0], examples[k][1].decode('latin1'))
    for s, pc in sorted(shaders[k])[:200]:
        print('   ', s.decode(), pc.decode(), words.get(s, ('?', '?')))
print('prefixes', prefixes)
print('=== other implemented/unsupported')
for k, v in other.most_common(40):
    print(v, k.decode('latin1'))
