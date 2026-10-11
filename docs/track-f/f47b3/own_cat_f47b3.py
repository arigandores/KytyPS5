# F47b3 (HPP-817, Red Team): own positive control of the F47a3 catalog matcher (find) on modules written to .spv files,
# and the T1 count of SCC readers the F47a3 classifier does not model (SOP2 s_cselect_b32/b64 0x0a/0x0b, s_addc_u32 0x04,
# s_subb_u32 0x05). Read only; ASCII only; exits 3 when the lock exists.
import importlib.util
import os
import struct
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3')
    sys.exit(3)

D = 'C:/kyty/KytyPS5/docs/track-f/f47a3/'
OUTD = sys.argv[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, D + name + '.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


K = load('cat_f47a3')
C = load('cls_f47a3')
CAT = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19'
files = [f for f in K.catalog(CAT) if f['ok']]
ps = [(f, k, w) for f in files if os.path.basename(f['path']).startswith('ps_') for k, (o, w) in enumerate(f['modules'])]


def write_spv(name, words):
    p = os.path.join(OUTD, name).replace(os.sep, '/')
    open(p, 'wb').write(struct.pack('<%dI' % len(words), *words))
    return p


def run_find(p, dual):
    args = [sys.executable, D + 'cat_f47a3.py', 'find', CAT, p] + (['--dual'] if dual else [])
    out = subprocess.run(args, capture_output=True, text=True).stdout.strip().splitlines()
    return out[-1], out


# (1) plain PS, unique place: the first unique non-dual module by sha order of the file names
picked = None
for f, k, w in ps:
    oc, nw = K.rewrite_loc1(w)
    if oc != 'patched':
        picked = (f, k, w)
        break
f, k, w = picked
p = write_spv('pc_plain.spv', w)
last, out = run_find(p, dual=True)
print('plain %s#%d -> %s' % (os.path.basename(f['path']), k, last))
# (2) dual-source: the emulator rewrite contract applied by the own copy of RewriteLocation1ToIndex1 below
def emu_rewrite(inp):
    # line-by-line transcription of ea6c6e9e dualSrcBlend.h RewriteLocation1ToIndex1 (patched path and every reject)
    if len(inp) < 5 or inp[0] != 0x07230203:
        return 'malformed', None
    bound = inp[3]
    if bound == 0 or bound > (1 << 22):
        return 'malformed', None
    is_out = [0] * bound
    locs = []
    i = 5
    while i < len(inp):
        cnt, op = inp[i] >> 16, inp[i] & 0xffff
        if cnt == 0 or cnt > len(inp) - i:
            return 'malformed', None
        if op == 59 and cnt >= 4:
            if inp[i + 2] >= bound:
                return 'malformed', None
            if inp[i + 3] == 3:
                is_out[inp[i + 2]] = 1
        elif op == 71 and cnt >= 3:
            if inp[i + 2] == 32:
                return 'has_index', None
            if inp[i + 2] == 30:
                if cnt != 4:
                    return 'malformed', None
                locs.append((i, inp[i + 1], inp[i + 3]))
        elif op == 72 and cnt >= 4:
            if inp[i + 3] in (30, 32):
                return 'member_decoration', None
        i += cnt
    l1, l0 = None, False
    for wd, t, loc in locs:
        if t >= bound or not is_out[t]:
            continue
        if loc >= 2:
            return 'location_above1', None
        if loc == 0:
            l0 = True
        elif l1 is not None:
            return 'multiple_location1', None
        else:
            l1 = wd
    if l1 is None:
        return 'no_location1', None
    if not l0:
        return 'no_location0', None
    t = inp[l1 + 1]
    out = list(inp[:l1 + 4])
    out[l1 + 3] = 0
    out += [(4 << 16) | 71, t, 32, 1]
    out += list(inp[l1 + 4:])
    return 'patched', tuple(out)


same = diff = 0
oc_diff = 0
first_dual = None
for f, k, w in ps:
    a, x = K.rewrite_loc1(w)
    b, y = emu_rewrite(w)
    oc_diff += a != b
    if a == 'patched':
        same += x == y
        diff += x != y
        if first_dual is None:
            first_dual = (f, k, y)
print('rewrite own(F47a3) vs emulator transcription: outcome differs %d of %d; patched equal %d differ %d' % (oc_diff, len(ps), same, diff))
f, k, y = first_dual
p = write_spv('pc_dual.spv', y)
last, out = run_find(p, dual=True)
print('dual %s#%d (emulator rewrite) -> %s' % (os.path.basename(f['path']), k, last))
for line in out[1:]:
    print('   ' + line)
# (3) the across-H module: must be MATCH_MANY
for f, k, w in ps:
    if K.sha(w).startswith('0073ca629876a570'):
        p = write_spv('pc_acrossH.spv', w)
        last, out = run_find(p, dual=True)
        print('acrossH %s#%d -> %s' % (os.path.basename(f['path']), k, last))
        break
# (4) T1 PS: SCC readers not modelled
cnt = {}
progs = 0
for arm in sorted(os.listdir(C.GCN_ROOT)):
    d = os.path.join(C.GCN_ROOT, arm)
    for fn in sorted(os.listdir(d)):
        if not (fn.startswith('ps_') and fn.endswith('.bin')):
            continue
        b = open(os.path.join(d, fn), 'rb').read()
        words = list(struct.unpack('<%dI' % (len(b) // 4), b))
        progs += 1
        ins, st = C.decode(words)
        for I in ins:
            if I.fam == 'SOP2' and I.op in (0x04, 0x05, 0x0a, 0x0b):
                cnt.setdefault(I.op, set()).add(fn)
print('T1 PS files %d; programs with SOP2 op: %s' % (progs, {('0x%02x' % k): len(v) for k, v in sorted(cnt.items())}))
print('done')
