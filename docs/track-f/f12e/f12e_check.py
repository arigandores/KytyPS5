# F12e (HPP-478, Red Team): own checks of the F12d code (KYTY_FIX_F10) without the GPU and without the game.
# Every step checks the lock and STOP. Output: C:/kyty/f287/f12e/f12e_check.out.txt, last line ALL OK or FAIL.
import hashlib, os, subprocess, sys, glob, csv, re, struct, itertools
import numpy as np

NL = chr(10)
OUT = 'C:/kyty/f287/f12e'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
D = 'C:/kyty/f287/f12d'
FIX = '1833ee280ec177b65feb6c4a97f626b0d4ce1b9f'
PARENT = '01c8981b'
log = []
bad = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    log.append(s)


def CHECK(name, ok, info=''):
    P(('OK   ' if ok else 'FAIL ') + name + (' | ' + str(info) if info != '' else ''))
    if not ok:
        bad.append(name)


def save():
    open(OUT + '/f12e_check.out.txt', 'w', encoding='utf-8', newline='').write(NL.join(log) + NL)


def lock():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        P('ABORT: lock or STOP appeared')
        save()
        sys.exit(3)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def git(*a, cwd=REPO, raw=False):
    r = subprocess.run([GIT, '-C', cwd] + list(a), capture_output=True, timeout=60)
    if raw:
        return r.returncode, r.stdout
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()


# ---------------------------------------------------------------- 1. provenance of the binary (reading (1), p.384(b))
lock()
P('== 1. binary provenance')
COPY = 'C:/kyty/f287/bin/kyty_emulator_b714f5c4.exe'
s_copy = sha(COPY)
s_build = sha(D + '/build/kyty_emulator.exe')
s_inst = sha(D + '/build/install/kyty_emulator.exe')
s_final = sha(D + '/final/kyty_emulator_b714f5c4.exe')
s_installed = sha('C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe')
P('sha256 copy', s_copy)
P('sha256 build', s_build)
P('sha256 install', s_inst)
P('sha256 final copy', s_final)
P('sha256 installed', s_installed)
CHECK('copy = build = install = final copy', s_copy == s_build == s_inst == s_final)
CHECK('copy sha starts b714f5c4', s_copy.startswith('b714f5c4'))
CHECK('installed is 540c035a', s_installed.startswith('540c035a'))
WT = D + '/wt'
rc, head = git('rev-parse', 'HEAD', cwd=WT)
CHECK('worktree HEAD = F12d code commit', head == FIX, head)
rc, st = git('status', '--porcelain', cwd=WT)
CHECK('worktree status --porcelain empty', rc == 0 and st == '', repr(st[:200]))
cache = open(D + '/build/CMakeCache.txt', encoding='utf-8', errors='replace').read()
m = re.search(r'^CMAKE_HOME_DIRECTORY:INTERNAL=(.*)$', cache, re.M)
home = m.group(1).strip() if m else ''
CHECK('CMakeCache home = worktree', home.replace(chr(92), '/').lower().rstrip('/') == WT.lower(), home)
m = re.search(r'^CMAKE_BUILD_TYPE:STRING=(.*)$', cache, re.M)
P('CMAKE_BUILD_TYPE', m.group(1) if m else '?')
ver = open(D + '/build/kytyGitVersion.h', encoding='utf-8').read()
CHECK('kytyGitVersion revision', 'KYTY_GIT_REVISION "' + FIX + '"' in ver)
CHECK('kytyGitVersion no -dirty', '-dirty' not in ver)
m = re.search(r'KYTY_SHADER_SOURCE_HASH "([0-9a-f]+)"', ver)
built_hash = m.group(1) if m else ''
P('KYTY_SHADER_SOURCE_HASH of the build', built_hash)
data = open(COPY, 'rb').read()
for s, want in [(built_hash.encode(), 1), (b'KYTY_FIX_F10', 1), (b':fixf10', 1), (b'g1833ee28', 1),
                (b'56189185f9e9', 0), (b'g1833ee28-dirty', 0), (b'1833ee2-dirty', 0)]:
    n = data.count(s)
    CHECK('copy contains ' + s.decode() + ' x' + str(want), n == want, n)

# ---------------------------------------------------------------- 2. git: parent, ancestors, files
lock()
P('== 2. git')
rc, par = git('rev-parse', FIX + '^')
CHECK('parent of 1833ee28 = 01c8981b', par.startswith(PARENT), par)
for anc in ['4e72289e', '68602c4f']:
    r = subprocess.run([GIT, '-C', REPO, 'merge-base', '--is-ancestor', anc, FIX], capture_output=True).returncode
    CHECK('ancestor ' + anc + ' of 1833ee28', r == 0)
rc, names = git('diff', '--name-only', PARENT, FIX)
P('files of 1833ee28:', names.replace(NL, ' '))
CHECK('6 files', len(names.split(NL)) == 6)
r = subprocess.run([GIT, '-C', REPO, 'diff', '--quiet', FIX, 'HEAD', '--', 'src', 'tests', 'CMakeLists.txt'],
                   capture_output=True).returncode
CHECK('HEAD src/tests/CMakeLists = 1833ee28', r == 0)
rc, grep = git('grep', '-n', 'KYTY_FIX_F10', FIX, '--', 'src')
reads = [l for l in grep.split(NL) if 'getenv' in l]
CHECK('one getenv("KYTY_FIX_F10") in src', len(reads) == 1, reads)
rc, grep = git('grep', '-n', 'FixF10Enabled()', FIX, '--', 'src')
P('FixF10Enabled() sites:')
for l in grep.split(NL):
    P('   ', l[len(FIX) + 1:][:150])

# ---------------------------------------------------------------- 3. translator signature recomputed (generate_version.cmake)
lock()
P('== 3. translator signature')


def src_hash(rev):
    rc, ls = git('ls-tree', '-r', '--name-only', rev, '--', 'src/graphics/shader')
    files = [f for f in ls.split(NL) if re.search(r'[.](cpp|h|inc)$', f)]
    files += ['src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
              'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h']
    files = sorted(set(files))
    dig = ''
    for f in files:
        rc, blob = git('show', rev + ':' + f, raw=True)
        if rc != 0:
            continue
        dig += hashlib.sha1(blob).hexdigest() + NL
    return hashlib.sha1(dig.encode()).hexdigest(), len(files)


h_fix, n_fix = src_hash(FIX)
h_par, n_par = src_hash(PARENT)
P('own hash 1833ee28', h_fix, 'files', n_fix)
P('own hash 01c8981b', h_par, 'files', n_par)
CHECK('own hash 1833ee28 = build e248e4a8', h_fix == built_hash and h_fix.startswith('e248e4a8'))
CHECK('own hash 01c8981b = 56189185', h_par.startswith('56189185'))

# ---------------------------------------------------------------- 4. =0 lines of the diff kept verbatim in the else branch
lock()
P('== 4. =0 path by text')
rc, diff = git('show', FIX, '--', 'src/graphics/shader', raw=True)
diff = diff.decode('utf-8').replace(chr(13), '')


def norm(l):
    l = l.strip()
    l = re.sub(r'^const (auto|IR::U1|Vec3)\s+', '', l)
    return re.sub(r'\s+', ' ', l)


for fname in ['spirvEmitterMemory.cpp', 'Memory.cpp']:
    part = diff.split('diff --git')
    part = [p for p in part if p.split(NL)[0].endswith(fname)][0]
    rem = [norm(l[1:]) for l in part.split(NL) if l.startswith('-') and not l.startswith('---')]
    add = [norm(l[1:]) for l in part.split(NL) if l.startswith('+') and not l.startswith('+++')]
    rem = [r for r in rem if r and not r.startswith('//')]
    missing = [r for r in rem if r not in add]
    CHECK(fname + ': every removed code line is an added line (else branch)', not missing, missing)

# ---------------------------------------------------------------- 5. vertex formulas of the code against GPURT CalcTriangleVertexOffsets
lock()
P('== 5. vertex selection formulas (code as written) vs GPURT b89f22aa')
gpurt = {0: (0, 1, 2), 1: (1, 3, 2), 2: (2, 3, 4), 3: (2, 4, 0)}
src = open('C:/kyty/f287/f12a/src_ext/Common_b89f22a.hlsl', encoding='utf-8').read()
m = re.search(r'static uint3 CalcTriangleVertexOffsets.*?return offsets;', src, re.S)
body = m.group(0)
parsed = {}
for t in range(4):
    mm = re.search(r'case NODE_TYPE_TRIANGLE_' + str(t) + r':.*?offsets.x = TRIANGLE_NODE_V(\d)_OFFSET;\s*'
                   r'offsets.y = TRIANGLE_NODE_V(\d)_OFFSET;\s*offsets.z = TRIANGLE_NODE_V(\d)_OFFSET;', body, re.S)
    parsed[t] = tuple(int(x) for x in mm.groups())
CHECK('GPURT source table = F12a 1.2 table', parsed == gpurt, parsed)


def sel(c, a, b):
    return a if c else b


def code_fix(t):
    i1, i2, i3 = t == 1, t == 2, t == 3
    a = sel(i2 or i3, 2, sel(i1, 1, 0))
    b = sel(i3, 4, sel(i1 or i2, 3, 1))
    c = sel(i2, 4, sel(i3, 0, 2))
    return (a, b, c)


def code_old(t):
    i1 = t == 1
    return (sel(i1, 1, 0), sel(i1, 3, 1), 2)


for t in range(4):
    CHECK('=1 type %d -> %s' % (t, code_fix(t)), code_fix(t) == gpurt[t])
for t in range(2):
    CHECK('=0 type %d -> %s (unchanged)' % (t, code_old(t)), code_old(t) == gpurt[t])
CHECK('is_tri =1 is t<4 = GPURT <= TRIANGLE_3', all((t < 4) == (t <= 3) for t in range(8)))

# ---------------------------------------------------------------- 6. own reference of the expected words (float32), against the test table
lock()
P('== 6. own reference (float32, GPURT fast_intersect_triangle + SwizzleBarycentrics)')
V = [(0, -8, 1), (8, 0, 2), (0, 0, 0), (0, 8, 3), (-8, 0, 4)]
TID = 0x09040209
f = np.float32


def u(x):
    return struct.unpack('<I', struct.pack('<f', float(x)))[0]


def isect(tri, ox, oy, tid_shift_type):
    o = np.array([ox, oy, -4], dtype=f)
    d = np.array([0, 0, 1], dtype=f)
    v1, v2, v3 = (np.array(V[i], dtype=f) for i in tri)
    e1, e2, e3 = v2 - v1, v3 - v1, o - v1
    s1 = np.cross(d, e2).astype(f)
    s2 = np.cross(e3, e1).astype(f)
    x, y, z, w = f(np.dot(e2, s2)), f(np.dot(s1, e1)), f(np.dot(e3, s1)), f(np.dot(d, s2))
    t, uu, vv = x / y, z / y, w / y
    miss = (uu < 0) or (uu > 1) or (vv < 0) or (uu + vv > 1) or (t < 0)
    if miss:
        x, y = f(np.inf), f(1.0)
    bary = [f(y - z - w), z, w, f(0.0)]
    sh = 8 * tid_shift_type
    return [u(x), u(y), u(bary[(TID >> sh) & 3]), u(bary[(TID >> (sh + 2)) & 3])]


tests = open(OUT + '/tests_1833.cpp', encoding='utf-8').read()
blk = re.search(r'const std::array<F10Ray, 10> &F10Rays\(\) \{(.*?)\}\};', tests, re.S).group(1)
ent = re.findall(r'\{"(F10\w+)", (\d)u, (F10\w+), (F10\w+),\s*\{([^}]*)\},\s*\{([^}]*)\}\}', blk)
CHECK('10 rays parsed from the test', len(ent) == 10, len(ent))
cst = {'F10PlusTwo': 2.0, 'F10MinusTwo': -2.0}


def words(s):
    return [0xffffffff if w.strip() == 'F10Ffff' else int(w.strip().rstrip('u'), 16) for w in s.split(',')]


FF = [0xffffffff] * 4
for name, t, ox, oy, fixed, cur in ent:
    t = int(t)
    if t < 4:
        ref1 = isect(gpurt[t], cst[ox], cst[oy], t)
        ref0 = ref1 if t < 2 else FF
    else:
        ref1 = ref0 = FF
    CHECK('%-14s =1 own ref' % name, words(fixed) == ref1, ' '.join('%08x' % x for x in ref1))
    CHECK('%-14s =0 own ref' % name, words(cur) == ref0)
    if t in (2, 3) and 'Hit' in name:
        alts = 0
        for perm in itertools.permutations(range(5), 3):
            if perm == gpurt[t]:
                continue
            if isect(perm, cst[ox], cst[oy], t) == ref1:
                alts += 1
        CHECK('%-14s no other vertex triple gives the same words' % name, alts == 0, alts)
        for bt in range(4):
            if bt != t:
                same = isect(gpurt[t], cst[ox], cst[oy], bt) == ref1
                P('   %s: ID byte of type %d instead of %d gives the same words: %s' % (name, bt, t, same))
# mix case composition
mix = re.search(r'F10MixWave64', tests) is not None
act = [((L >> 1) & 3) for L in range(64) if L % 2 == 0]
CHECK('mix: active lanes 8 of each type 0..3', all(act.count(k) == 8 for k in range(4)))
CHECK('mix: in each host subgroup of 32 all four types', all(len(set((L >> 1) & 3 for L in range(b, b + 32, 2))) == 4 for b in (0, 32)))
CHECK('mix: exec 0x55555555 lo and hi in the case', '0x55555555u' in tests and 'exec_hi' in tests and mix)

# ---------------------------------------------------------------- 7. SPIR-V of the test cases: =0 / unset byte for byte = base, =1 differs
lock()
P('== 7. SPIR-V of the 15 test cases')
for nat in ('0', '1'):
    base = {os.path.basename(p): sha(p) for p in glob.glob(D + '/final/spv_base_nat' + nat + '/*.spv')}
    CHECK('base nat' + nat + ' has 15 files', len(base) == 15, len(base))
    for var, want_eq in (('f100', True), ('f10unset', True), ('f101', False)):
        cur = {os.path.basename(p): sha(p) for p in glob.glob(D + '/final/spv_' + var + '_nat' + nat + '/*.spv')}
        eq = sum(1 for k in base if cur.get(k) == base[k])
        if want_eq:
            CHECK('%s nat%s: %d of 15 equal base' % (var, nat, eq), eq == 15 and len(cur) == 15)
        else:
            CHECK('%s nat%s: %d of 15 equal base (want 0)' % (var, nat, eq), eq == 0 and len(cur) == 15)

# ---------------------------------------------------------------- 8. corpus T1 recomputed from the out.spv files
lock()
P('== 8. corpus T1 from the files')
bvh = set()
for r in csv.DictReader(open('C:/kyty/f287/f11a/t1scan_f11a.tsv', encoding='utf-8'), delimiter='\t'):
    if r['bvh'] not in ('', '0'):
        bvh.add(r['hash16'])
P('BVH programs in t1scan', len(bvh))
C = D + '/final/corpus'
stats = {'rows': 0, 'eq0': 0, 'equ': 0, 'bvh_rows': 0, 'bvh_ne1': 0, 'non_ne1': 0, 'missing': 0}
ne_progs = set()
for suf in ('', '_ir'):
    for row in sorted(os.listdir(C + '/base' + suf)):
        lock()
        fs = {}
        for v in ('base', 'f0', 'fu', 'f1'):
            p = C + '/' + v + suf + '/' + row + '/out.spv'
            fs[v] = open(p, 'rb').read() if os.path.exists(p) else None
        if any(x is None or len(x) == 0 for x in fs.values()):
            stats['missing'] += 1
            continue
        stats['rows'] += 1
        h16 = row.split('_')[1]
        stats['eq0'] += fs['f0'] == fs['base']
        stats['equ'] += fs['fu'] == fs['base']
        if h16 in bvh:
            stats['bvh_rows'] += 1
            stats['bvh_ne1'] += fs['f1'] != fs['base']
        else:
            stats['non_ne1'] += fs['f1'] != fs['base']
        if fs['f1'] != fs['base']:
            ne_progs.add(h16)
P('corpus', stats)
CHECK('corpus rows 280, none missing', stats['rows'] == 280 and stats['missing'] == 0)
CHECK('=0 = base on all rows', stats['eq0'] == stats['rows'])
CHECK('unset = base on all rows', stats['equ'] == stats['rows'])
CHECK('=1 differs on every BVH row (22)', stats['bvh_rows'] == 22 and stats['bvh_ne1'] == 22)
CHECK('=1 = base on every non-BVH row', stats['non_ne1'] == 0)
CHECK('programs with a =1 difference = 9, all BVH', len(ne_progs) == 9 and ne_progs <= bvh, sorted(ne_progs))
t1 = list(csv.DictReader(open('C:/kyty/s288/s7/t1_base.tsv', encoding='utf-8'), delimiter='\t'))
nobvh_rows = sorted(set((r['row'], r['stage'], r['outcome']) for r in t1 if r['hash16'] in bvh - ne_progs))
P('BVH programs without a translated row:', sorted(bvh - ne_progs), nobvh_rows)
vsms = sum(1 for r in t1 if r['row'] == 'A' and r['outcome'] == 'HARNESS_UNSUPPORTED')
P('A rows HARNESS_UNSUPPORTED (vs/ms, not translated by either build):', vsms)
CHECK('no BVH program among HARNESS_UNSUPPORTED A rows',
      not any(r['hash16'] in bvh for r in t1 if r['row'] == 'A' and r['outcome'] == 'HARNESS_UNSUPPORTED'))
s380 = {os.path.basename(p): sha(p) for p in glob.glob(C + '/spv380/*')}
P('spv380 files', len(s380))
for k in sorted(s380):
    if k.endswith('.spv') and '_0_' in k:
        P('   ', s380[k], k)

# ---------------------------------------------------------------- 9. gate logs and cfg tests
lock()
P('== 9. gate logs')
for var, eff in (('f100', 0), ('f101', 1), ('f10unset', 0)):
    for nat in ('0', '1'):
        t = open(D + '/final/gate_' + var + '_nat' + nat + '.txt', encoding='utf-8', errors='replace').read()
        oks = re.findall(r'^\[compute\] (\S+)\s+ok\s*$', t, re.M)
        effm = re.search(r'KYTY_FIX_F10=\S+ effective=(\d)', t)
        natm = re.search(r'KYTY_BVH_NATIVE=(\S+)', t)
        tok = re.search(r'fixf10_in_signature=(\d) fixf10_in_dir=(\d) last_sig=(\d) last_dir=(\d)', t)
        good = (len(oks) == 15 and t.rstrip().endswith('ALL OK') and effm and int(effm.group(1)) == eff
                and natm and natm.group(1) == nat and tok and all(int(x) == eff for x in tok.groups())
                and 'F10MixWave64' in oks)
        CHECK('gate %s nat%s: 15 ok, ALL OK, effective %d, token %s' % (var, nat, eff, tok.groups() if tok else None), good)
P('== cfg tests')
logs = {}
for var in ('f100', 'f101', 'f10unset'):
    t = open(D + '/final/cfgtests_' + var + '.log', encoding='utf-8', errors='replace').read()
    t = NL.join(l for l in t.replace(chr(13), '').split(NL) if 'elapsed' not in l)
    logs[var] = t
    P(var, 'tests', len(re.findall(r'^\[test\]', t, re.M)), 'ShaderCfgTests: failed lines',
      len(re.findall(r'^ShaderCfgTests: failed', t, re.M)))
CHECK('cfg logs equal across unset/0/1', logs['f100'] == logs['f101'] == logs['f10unset'])

P('== verdict')
P('FAILED:', bad)
P('ALL OK' if not bad else 'FAIL')
save()
