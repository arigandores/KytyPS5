# seed_s0.py - S0 (HPP-294): starter seed against the log line and recipe counts of pipelines.bin (seed, snap0). Counts only.
import struct, os, re, hashlib
def recipes(path):
    d = open(path, 'rb').read()
    # layout (pipelineCache.cpp WriteRecipes): magic bytes, u32 signature size, signature, u32 count, records
    for mlen in range(4, 17):
        if mlen + 4 > len(d):
            break
        size, = struct.unpack_from('<I', d, mlen)
        if 16 <= size <= 512 and mlen + 4 + size + 4 <= len(d):
            sig = d[mlen + 4:mlen + 4 + size]
            if sig.startswith(b'KytySC'):
                cnt, = struct.unpack_from('<I', d, mlen + 4 + size)
                return d[:mlen], sig.decode('latin1').replace(chr(10), ':'), cnt, len(d)
    return None
seed = 'C:/kyty/KytyPS5/ps5 em/_ShaderSeeds/PPSA21564'
stored = open(seed + '/compatibility.txt', 'rb').read().split(b'\n')[0].rstrip(b'\r').decode()
log = None
with open('C:/kyty/s142/log_c142_01.txt', 'rb') as f:
    for i, line in enumerate(f, 1):
        if line.startswith(b'ShaderSeed: compatibility='):
            log = line[len(b'ShaderSeed: compatibility='):].rstrip().decode(); ln = i; break
print('seed compatibility.txt == log line %d of log_c142_01.txt: %s' % (ln, stored == log))
print('seed shaders', sum(1 for f in os.listdir(seed) if f.endswith('.bin') and f != 'pipelines.bin'))
for name, p in (('seed', seed + '/pipelines.bin'), ('snap0', 'C:/kyty/s288/snap0/ShaderCache_PPSA21564/pipelines.bin')):
    r = recipes(p)
    print(name, 'pipelines.bin magic', r[0], 'signature+layout', r[1], 'recipes', r[2], 'bytes', r[3], 'sha256', hashlib.sha256(open(p, 'rb').read()).hexdigest())
