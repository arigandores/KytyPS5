# F11b (HPP-456, Red Team): evidence lines for the review, read at a fixed commit.
import hashlib, subprocess, sys
REPO = 'C:/kyty/KytyPS5'
COMMIT = sys.argv[1]
OUT = sys.argv[2]
SPANS = [
    ('src/graphics/host_gpu/renderer/cache/faultManager.cpp', 40, 44, 'fault buffer size = LoopTripOffset + LoopTripBytes'),
    ('src/graphics/host_gpu/renderer/cache/faultManager.cpp', 92, 94, 'ClearLoopTripTail fills only LoopTripBytes'),
    ('src/graphics/host_gpu/renderer/cache/faultManager.cpp', 150, 153, 'tail copy only when trips'),
    ('src/graphics/host_gpu/renderer/cache/faultManager.cpp', 189, 196, 'grown(): max logic'),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 152, 158, 'ClearLoopTripTail at first registration'),
    ('tests/ShaderRecompilerComputeTests.cpp', 15681, 15682, 'test fault buffer has no tail'),
    ('src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp', 568, 569, 'loop cap default on 380bb9d6'),
    ('src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp', 848, 852, 'cap slot / dispatcher fallback'),
    ('src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.h', 38, 40, 'LoopTrip words'),
    ('src/graphics/shader/recompiler/frontend/translate/Memory.cpp', 713, 721, 'KYTY_BVH_STUB returns before'),
    ('src/graphics/shader/recompiler/frontend/translate/Memory.cpp', 845, 857, 'native fork, exec passed'),
    ('src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp', 2141, 2144, 'desc0, desc1, active, node64'),
    ('src/generate_version.cmake', 44, 56, 'translator content hash'),
    ('src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 578, 587, 'variant directory'),
]
FILES = [
    ('C:/kyty/f287/f3a/asm_380b.txt', [(152, 155), (217, 225), (229, 241), (148, 151)], 'game traversal 380bb9d6'),
    ('C:/kyty/KytyPS5/docs/track-f/f11a/t1scan_f11a.tsv', [(1, 1), (2, 8)], 'NOT_FOUND rows (all CS)'),
    ('C:/kyty/f287/f3a/src_ext/gfx10_sq_ko_reg.h', [(99, 111)], 'sq_bvh_rsrc_t'),
]
out = []
out.append('commit ' + COMMIT)
for path, a, b, note in SPANS:
    text = subprocess.run(['git', '-C', REPO, 'show', COMMIT + ':' + path], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
    out.append('== ' + COMMIT + ':' + path + ':' + str(a) + '-' + str(b) + ' -- ' + note)
    for i in range(a, b + 1):
        out.append(str(i) + ': ' + text[i - 1].rstrip('\r'))
for path, spans, note in FILES:
    raw = open(path, 'rb').read()
    lines = raw.decode('utf-8', 'replace').split('\n')
    out.append('== ' + path + ' sha256 ' + hashlib.sha256(raw).hexdigest()[:16] + ' -- ' + note)
    for a, b in spans:
        for i in range(a, b + 1):
            out.append(str(i) + ': ' + lines[i - 1].rstrip('\r'))
data = ('\n'.join(out) + '\n').encode('utf-8')
open(OUT, 'wb').write(data)
print(OUT, hashlib.sha256(data).hexdigest()[:8], len(out))
