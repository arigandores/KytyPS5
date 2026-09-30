import json, struct, collections, sys, re
sys.path.insert(0, 'C:/kyty/f287/f1a')
from rdis import dis
idx = json.load(open('C:/kyty/f287/f1a/code/index.json'))
W = {'s_load_dword': 1, 's_load_dwordx2': 2, 's_load_dwordx4': 4, 's_load_dwordx8': 8, 's_load_dwordx16': 16,
     's_buffer_load_dword': 1, 's_buffer_load_dwordx2': 2, 's_buffer_load_dwordx4': 4, 's_buffer_load_dwordx8': 8, 's_buffer_load_dwordx16': 16}
def writes(text):
    m = re.match(r'(s_\w+) s(\d+)', text)
    if not m:
        return set()
    name, r = m.group(1), int(m.group(2))
    if name in W:
        return set(range(r, r + W[name]))
    if name.startswith(('s_cmp', 's_bitcmp', 's_cbranch', 's_branch', 's_waitcnt', 's_setpc', 's_nop')):
        return set()
    n = 2 if name.endswith(('_b64', '_u64', '_i64')) and not name.startswith('s_bfe') else 1
    if name == 's_swappc_b64' or name == 's_getpc_b64':
        n = 2
    return set(range(r, r + n))
origin = collections.Counter()
ex = {}
for it in idx:
    if it['op'] != '0x21':
        continue
    words = list(struct.unpack('<%dI' % it['words'], open('C:/kyty/f287/f1a/code/%s.bin' % it['hash'], 'rb').read()))
    ins = dis(words)
    for k, (pc, ws, text) in enumerate(ins):
        if not text.startswith('s_swappc_b64'):
            continue
        src = None
        for j in range(k - 1, -1, -1):
            if ins[j][2].startswith('s_mov_b32 s14, s'):
                src = int(ins[j][2].split(', s')[1]); start = j
                break
        if src is None:
            origin['s14 not from s_mov_b32'] += 1
            continue
        w = None
        for j in range(start - 1, -1, -1):
            if src in writes(ins[j][2]):
                w = ins[j][2]
                break
        key = 'user/initial SGPR (never written before)' if w is None else ('written by ' + w.split(' ')[0])
        origin[key] += 1
        ex.setdefault(key, (it['hash'], hex(pc), src, w))
print(origin)
for k, v in ex.items():
    print(k, v)
