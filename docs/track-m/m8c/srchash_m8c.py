"""Track M, M8c (HPP-860): the translator source hash KYTY_SHADER_SOURCE_HASH of a tree, computed as
src/generate_version.cmake does (GLOB_RECURSE *.cpp *.h *.inc under src/graphics/shader + the 4 extra files of
CMakeLists.txt SHADER_CACHE_EXTRA_FILES, list(SORT), SHA1 of each file + newline, SHA1 of the concatenation).
Usage: python srchash_m8c.py <tree root> [<tree root> ...]   Prints: <root> <files> <hash>."""
import hashlib
import os
import sys

EXTRA = ['graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 'graphics/guest_gpu/gpu_format.h',
         'graphics/guest_gpu/gpu_defs.h', 'graphics/host_gpu/renderer/image/imageInfo.h']

for root in sys.argv[1:]:
    src = root.replace(os.sep, '/') + '/src'
    files = []
    for d, _, fs in os.walk(src + '/graphics/shader'):
        for f in fs:
            if f.endswith(('.cpp', '.h', '.inc')):
                files.append((d.replace(os.sep, '/') + '/' + f))
    files += [src + '/' + e for e in EXTRA]
    files.sort()
    dig = ''
    for f in files:
        if os.path.exists(f):
            dig += hashlib.sha1(open(f, 'rb').read()).hexdigest() + chr(10)
    print(root, len(files), hashlib.sha1(dig.encode('ascii')).hexdigest())
