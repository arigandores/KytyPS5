"""Session 103: the 15 presence-only env switches under src/graphics/shader/** (deferred by
session 102 to keep the translation cache warm) read their VALUE through Common::EnvFlagOn."""
import sys

DRY = len(sys.argv) > 1 and sys.argv[1] == '--dry'
ROOT = 'C:/kyty/KytyPS5/src/graphics/shader/'
# file -> (variables, expected replacements, file that gets the include)
SITES = {
    'shader.cpp': (['KYTY_VTX_TRACE'], 2),
    'recompiler/ShaderRecompiler.cpp': (['KYTY_AV_TRACE'], 2),
    'recompiler/ir/passes/ConstantPropagation.cpp': (['KYTY_KNOWN_VALUES_TRACE'], 1),
    'recompiler/ir/passes/SrtWalker.cpp': (['KYTY_SRT_PLAN_STATS', 'KYTY_SRT_VERIFY'], 2),
    'recompiler/ir/passes/SrtNative.inc': (['KYTY_SRT_NATIVE_STATS', 'KYTY_SRT_NATIVE_AUDIT'], 3),
    'recompiler/frontend/translate/Memory.cpp': (['KYTY_BVH_STUB'], 1),
    'recompiler/frontend/cfg/ShaderCFG.cpp': (['KYTY_CFG_TRACE'], 1),
    'recompiler/backend/spirv/spirvEmitterImage.cpp': (['KYTY_SAMPLE_LOD0'], 1),
    'recompiler/backend/spirv/spirvEmitterMemory.cpp': (['KYTY_VEC_CONST_TRACE',
                                                          'KYTY_SCALAR_GROUP_TRACE'], 2),
}
INCLUDE = '#include "common/envFlag.h"\n'
total = 0
out = {}
for rel, (names, expected) in SITES.items():
    b = open(ROOT + rel, 'rb').read().decode('utf-8')
    assert '\r\n' not in b, rel
    n = 0
    for name in names:
        old = 'std::getenv("%s") != nullptr' % name
        n += b.count(old)
        b = b.replace(old, 'Common::EnvFlagOn("%s")' % name)
    assert n == expected, (rel, n, expected)
    total += n
    if not rel.endswith('.inc'):
        lines = b.split('\n')
        # after the first block of #include lines (the file's own header first)
        idx = next(i for i, l in enumerate(lines) if l.startswith('#include'))
        while idx < len(lines) and lines[idx].startswith('#include'):
            idx += 1
        # put it in the next include group if there is a blank line then more includes
        j = idx
        while j < len(lines) and lines[j] == '':
            j += 1
        if j < len(lines) and lines[j].startswith('#include'):
            lines.insert(j, INCLUDE.rstrip('\n'))
        else:
            lines.insert(idx, INCLUDE.rstrip('\n'))
        b = '\n'.join(lines)
    out[rel] = b
assert total == 15, total
# SrtNative.inc is included only from SrtWalker.cpp, which now includes envFlag.h.
assert 'common/envFlag.h' in out['recompiler/ir/passes/SrtWalker.cpp']
if DRY:
    print('DRY ok: 15 sites in', len(out), 'files')
else:
    for rel, b in out.items():
        open(ROOT + rel, 'wb').write(b.encode('utf-8'))
    print('written: 15 sites in', len(out), 'files')
