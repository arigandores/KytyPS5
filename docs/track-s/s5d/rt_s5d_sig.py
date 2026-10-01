# S5d: own KYTY_SHADER_SOURCE_HASH of a tree by src/generate_version.cmake:43-56 (GLOB_RECURSE *.cpp *.h *.inc under
# src/graphics/shader + 3 extra files, SORT of absolute paths, sha1 of "<sha1 file>\n" per existing file); as is and with CR removed.
import hashlib, os, sys
BS = chr(92)
root = sys.argv[1].replace(BS, '/')
sd = root + '/src/graphics/shader'
names = [os.path.join(d, f).replace(BS, '/') for d, ds, fs in os.walk(sd) for f in fs
         if os.path.splitext(f)[1] in ('.cpp', '.h', '.inc')]
names += [root + '/' + x for x in ('src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
                                   'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h')]
names.sort()
NL = chr(10)
for mode in ('as_is', 'cr_removed'):
    acc = ''
    for n in names:
        if os.path.exists(n):
            data = open(n, 'rb').read()
            if mode == 'cr_removed':
                data = data.replace(bytes([13, 10]), bytes([10]))
            acc += hashlib.sha1(data).hexdigest() + NL
    print(mode, hashlib.sha1(acc.encode()).hexdigest(), len(names), root)
