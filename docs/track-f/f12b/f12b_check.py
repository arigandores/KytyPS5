# F12b (HPP-475, Red Team): own checks of the F12a project (docs/track-f/f12a.md, KytyPS5 08bd2a87).
# Offline only: reads the disassembly of 380bb9d636390bae (C:/kyty/f287/f3a/asm_380b.txt, F3a),
# the F12a CPU reference (docs/track-f/f12a/ref_f12a.py) and the emulator sources at 08bd2a87.
# Prints one line per check and ALL OK at the end.
import contextlib
import hashlib
import importlib.util
import io
import itertools
import re
import subprocess
import sys

ASM = 'C:/kyty/f287/f3a/asm_380b.txt'
REF = 'C:/kyty/KytyPS5/docs/track-f/f12a/ref_f12a.py'
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REV = '08bd2a87'

ok = True


def check(name, cond, extra=''):
    global ok
    ok &= bool(cond)
    print('%s  %s%s' % ('OK  ' if cond else 'FAIL', name, ('  ' + extra) if extra else ''))


raw = open(ASM, 'rb').read()
print('asm sha256', hashlib.sha256(raw).hexdigest())
L = raw.decode('utf-8', 'replace').splitlines()


def line(n):
    return L[n - 1]


def ops(n):
    m = re.match(r'0x[0-9a-f]+: (\S+)\s*(.*)', line(n))
    return (m.group(1), m.group(2).split(';')[0].strip()) if m else (None, '')


# (1) words 2-3 (z, w) of the leaf answer are not consumed by the leaf loop of 380bb9d6
check('leaf call at asm:241', 'IMAGE_BVH_INTERSECT_RAY v0, v0' in line(241) and '0x00000474' in line(241))
check('z (v2) overwritten first at asm:243', ops(243) == ('V_LSHRREV_B32', 'v2, 31, v0'))
reads_w = [n for n in range(242, 271) if re.search(r'\bv3\b', ops(n)[1])]
check('w (v3) not read in the leaf loop asm:242-270', reads_w == [], str(reads_w))
check('loop back edge asm:269 -> 0x45c, exit asm:270 -> 0x504',
      'S_BRANCH 0x0000045c' in line(269) and '0x00000504: S_MOV_B64 exec_lo, s24' in line(270))
check('box answer regs preset to -1 before the BLAS box call (asm:272-275)',
      all(ops(n)[0] == 'V_MOV_B32' and ops(n)[1].endswith('-1') for n in range(272, 276)))

# (2) vertex order of the hit triangle: the game normal is (C - A) x (B - A), i.e. e1 x e2 of (A, C, B)
# A = v9..v11 (asm:658), B = v12..v14 (asm:659), C = v15..v17 (asm:660)
seq = {
    662: ('V_SUB_F32', 'v14, v14, v11'),   # Bz - Az
    664: ('V_SUB_F32', 'v16, v16, v10'),   # Cy - Ay
    665: ('V_SUB_F32', 'v10, v13, v10'),   # By - Ay
    666: ('V_SUB_F32', 'v13, v17, v11'),   # Cz - Az
    667: ('V_SUB_F32', 'v11, v12, v9'),    # Bx - Ax
    668: ('V_SUB_F32', 'v12, v15, v9'),    # Cx - Ax
    669: ('V_MUL_F32', 'v17, v16, v14'),   # (Cy-Ay)(Bz-Az)
    672: ('V_MAC_F32', 'v17, v10, v13.neg'),  # - (By-Ay)(Cz-Az)
}
for n, want in seq.items():
    check('normal term asm:%d %s %s' % (n, want[0], want[1]), ops(n) == want, line(n)[:60])
# symbolic: n.x = (C-A).y*(B-A).z - (C-A).z*(B-A).y = ((C-A) x (B-A)).x  -> triangle (A, C, B), normal e1 x e2
check('loads A/B/C at asm:658-660', ops(658)[1].startswith('v9, v9') and ops(659)[1].startswith('v12, v12')
      and ops(660)[1].startswith('v15, v15'))

# (3) best t (v25) is the ray extent operand of all three calls; an accepted NaN poisons it
for n in (241, 280, 458):
    m = re.search(r'nsa_addr=(\d+),', line(n))
    check('extent operand v25 at asm:%d' % n, m is not None and m.group(1) == '25', m.group(0) if m else '')
check('accepted t written to v25 at asm:261 (0x4dc)', ops(261) == ('V_MOV_B32', 'v25, v0'))
check('accept test t > best uses v25 at asm:250', ops(250) == ('V_CMP_GT_F32', 's32, v0, v25'))


def git_show(path):
    return subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (REV, path)], capture_output=True).stdout.decode(
        'utf-8', 'replace').splitlines()


em = git_show('src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp')
ir = git_show('src/graphics/shader/recompiler/frontend/translate/Memory.cpp')
check('emitter: box max_t = nmin(max_of, extent) at :2277',
      'nmin(max_of, extent)' in em[2276] and 'const auto max_t' in em[2276])
check('emitter: nmin = NaN-suppressing fmin at :2168-2170',
      'NaN-suppressing' in em[2167] and em[2169].strip() == 'const auto nmin = fmin;')
check('IR: box max_t = nmin(max_of, extent) at Memory.cpp:930', 'nmin(max_of, extent)' in ir[929])
check('IR: nmin NaN-suppressing at Memory.cpp:759, :764',
      'NaN suppressing' in ir[758] and 'fsel(fnan(a), b, fsel(fnan(b), a, fmin(a, b)))' in ir[763])

# (4) type 6 at the TLAS and BLAS sites goes to the box call and its answer is parsed as box children
check('TLAS: (type-4) <= 2 -> 0x8d8 (asm:152-155)', 'S_CBRANCH_SCC1 0x000008d8' in line(155))
check('TLAS box call asm:458 then child checks v0..v3 != -1 (asm:460, 464, 467, 470)',
      all('V_CMP_NE_U32' in line(n) and ', -1, v' in line(n) for n in (460, 464, 467, 470)),
      ' | '.join(line(n)[12:40] for n in (460, 464, 467, 470)))
check('TLAS non-box: type 7 vs instance descriptor load (asm:163, 172)',
      'S_CMP_LG_U32 7, s54' in line(163) and 'S_LOAD_DWORDX16 s20, s50' in line(172))

# (5) mixed GPU-test case of F12a 7.2: type = lane & 3 with odd lanes inactive
active_types = sorted({lane & 3 for lane in range(64) if lane % 2 == 0})
check('finding: mixed case of F12a 7.2 as written has active lanes of types 0 and 2 only', active_types == [0, 2],
      'active types %s' % active_types)
fixed = sorted({(lane >> 1) & 3 for lane in range(64) if lane % 2 == 0})
print('      variant: type = (lane >> 1) & 3, odd lanes inactive -> active types %s' % fixed)

# (6) sensitivity of the exact 4-word test to the vertex ORDER of types 2-3 (not declared in F12a)
spec = importlib.util.spec_from_file_location('ref_f12a', REF)
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
F = m.F
undetected4 = []
only_zw = []
for k in (2, 3):
    good = m.MAPPING[k]
    for perm in itertools.permutations(good):
        if perm == good:
            continue
        for kind, xy in (('hit', m.HIT_XY[k]), ('miss', m.MISS_XY[k])):
            o = (xy[0], xy[1], -4)
            a, b, c = (m.V[i] for i in perm)
            res, _, _ = m.fast_intersect_triangle(o, m.DIR, a, b, c, F)
            bary = [res[1] - res[2] - res[3], res[2], res[3]]
            sh = 8 * k
            alt = [m.bits(F(x)) for x in (res[0], res[1], bary[(m.TRI_ID >> sh) % 4],
                                          bary[(m.TRI_ID >> (sh + 2)) % 4])]
            e = m.hw_answer(k, o)[0]
            if alt == e:
                undetected4.append((k, perm, kind))
            elif alt[:2] == e[:2] and kind == 'hit':
                only_zw.append((k, perm))
check('every wrong order of types 2-3 changes some of the 4 words (20 of 20)', undetected4 == [])
print('      hit cases where only z/w differ (cyclic rotations; words 0-1 equal): %d %s' % (len(only_zw), only_zw))

print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
