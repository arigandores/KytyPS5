import re, struct, mmap, os, json, hashlib, collections, xxhash
EBOOT = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin'
scan = open('C:/kyty/f287/f1a/scanb_v142.out.txt', 'rb').read().decode('latin1')
cur = None
items = []
for line in scan.splitlines():
    m = re.match(r'^(SOP1|VOPC) (0x[0-9a-f]+) (0x[0-9a-f]+) lines', line)
    if m:
        cur = m.groups()
        continue
    m = re.match(r"^    ([0-9a-f]{16}) (0x[0-9a-f]+) \(b'CS', (\d+)\)", line)
    if m and cur:
        items.append(dict(fam=cur[0], op=cur[1], raw=int(cur[2], 16), hash=m.group(1), pc=int(m.group(2), 16), words=int(m.group(3))))
os.makedirs('C:/kyty/f287/f1a/code', exist_ok=True)
with open(EBOOT, 'rb') as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    occ = {}
    for raw in {it['raw'] for it in items}:
        rb = struct.pack('<I', raw)
        lst = []
        i = mm.find(rb)
        while i != -1:
            if i % 4 == 0:
                lst.append(i)
            i = mm.find(rb, i + 1)
        occ[raw] = lst
        print(hex(raw), 'aligned occurrences', len(lst))
    for it in items:
        for j in occ[it['raw']]:
            start = j - it['pc']
            if start < 0:
                continue
            code = mm[start:start + it['words'] * 4]
            if '%016x' % xxhash.xxh3_64_intdigest(code) == it['hash']:
                it['start'] = start
                open('C:/kyty/f287/f1a/code/%s.bin' % it['hash'], 'wb').write(code)
                it['sha256'] = hashlib.sha256(code).hexdigest()
                break
json.dump(items, open('C:/kyty/f287/f1a/code/index.json', 'w'), indent=1)
ok = [r for r in items if 'start' in r]
print('located', len(ok), 'of', len(items))
for r in items:
    if 'start' not in r:
        print('MISSING', r['hash'], r['op'], hex(r['pc']))
for r in items:
    if r['op'] != '0x21':
        print(r['fam'], r['op'], r['hash'], 'pc', hex(r['pc']), 'words', r['words'], 'eboot', hex(r.get('start', -1)))
