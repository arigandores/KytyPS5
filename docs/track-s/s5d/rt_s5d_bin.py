# S5d: binary provenance of the S6 binary: sha of the copy and of the build output, signature strings, strings of the
# S5c code, absent strings, own translator signature of the worktree, build dir source, mtimes (UTC).
import hashlib, os, re, subprocess, datetime
BIN = 'C:/kyty/s288/bin/kyty_emulator_f3b3aa3b.exe'; OUT = 'C:/kyty/s288/build_s5c/install/kyty_emulator.exe'
INST = 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'; PIN = 'C:/kyty/s128/kyty_emulator_9235a7ac.exe'
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def utc(p): return datetime.datetime.utcfromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%dT%H:%M:%SZ')
for p in (BIN, OUT, INST, PIN):
    print('sha256', sha(p), utc(p), p) if os.path.isfile(p) else print('ABSENT', p)
b = open(BIN, 'rb').read(); pin = open(PIN, 'rb').read()
def sig(x):
    return sorted(set(m.decode() for m in re.findall(rb'KytySC3:[0-9a-f]{8,40}', x))), sorted(set(m.decode() for m in re.findall(rb'[0-9a-f]{7,8}-dirty|4fc501f[0-9a-f]*', x)))[:5]
print('bin  sig/hash', sig(b)); print('9235 sig/hash', sig(pin))
src_hash = re.findall(rb'699c1e4b[0-9a-f]{32}', b); print('699c1e4b... in bin:', [s.decode() for s in set(src_hash)], ' in 9235:', len(re.findall(rb'699c1e4b[0-9a-f]{32}', pin)) > 0)
for s in [b'S-pcw: KYTY_S_PCW', b'KYTY_S_PCW_FORCE_MS', b'GcnDumpReg: skip type=', b'GcnDumpReg: type=', b'wait gfx', b'wait cs',
          b' lock_us=', b' hold_us=', b'AvTrace: pcw overlap %s', b'AvTrace: pcw recipes copied=%zu count=%u lock_us=',
          b'AvTrace: pcw recipes copied=%zu count=%u wait_us=', b'KYTY_FIX_B26', b'KYTY_FIX_']:
    print('%-55s bin %d  9235 %d' % (s.decode(), b.count(s), pin.count(s)))
cache = open('C:/kyty/s288/build_s5c/CMakeCache.txt', 'rb').read().decode('utf-8', 'replace')
for k in ('CMAKE_HOME_DIRECTORY', 'CMAKE_BUILD_TYPE', 'CMAKE_INTERPROCEDURAL_OPTIMIZATION', 'CMAKE_CXX_COMPILER:', 'KYTY_BUILD_LAUNCHER'):
    print([l for l in cache.splitlines() if l.startswith(k)][:1])
WT = 'C:/kyty/s288/wt_s5c'
for f in ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.h',
          'src/graphics/shader/shaderBindings.cpp', 'src/graphics/guest_gpu/gpu_defs.h'):
    print('mtime', utc(os.path.join(WT, f)), f)
newest = max((os.path.getmtime(os.path.join(d, f)), os.path.join(d, f)) for d, ds, fs in os.walk(WT + '/src') for f in fs)
print('newest src file', datetime.datetime.utcfromtimestamp(newest[0]).strftime('%Y-%m-%dT%H:%M:%SZ'), newest[1])
gv = [os.path.join(d, f) for d, ds, fs in os.walk('C:/kyty/s288/build_s5c') for f in fs if f == 'kytyGitVersion.h']
for g in gv: print('gen', g, [l for l in open(g, encoding='utf-8', errors='replace').read().splitlines() if 'HASH' in l])
