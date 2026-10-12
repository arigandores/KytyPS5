"""M2c (HPP-840, task member (4)): KYTY_SHADER_SOURCE_HASH of a tree by the algorithm of src/generate_version.cmake
(GLOB_RECURSE *.cpp *.h *.inc under src/graphics/shader + the four SHADER_CACHE_EXTRA_FILES of CMakeLists.txt, sorted
by full path, SHA1 of each file's bytes as 40 hex + newline, SHA1 of the concatenation). Self-check: the FS15 tree must
give 9177b4267de1fb8bac7d1113afd8733210addfac (the FS8..FS15 signature).
Usage: python srchash_m2c.py <tree> [<tree> ...]"""
import glob
import hashlib
import sys

EXTRA = ['graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 'graphics/guest_gpu/gpu_format.h',
         'graphics/guest_gpu/gpu_defs.h', 'graphics/host_gpu/renderer/image/imageInfo.h']
for tree in sys.argv[1:]:
    src = tree.rstrip('/') + '/src'
    files = []
    for ext in ('cpp', 'h', 'inc'):
        files += glob.glob(src + '/graphics/shader/**/*.' + ext, recursive=True)
    files = [f.replace('\\', '/') for f in files] + [src + '/' + e for e in EXTRA]
    files.sort()
    digests = ''.join(hashlib.sha1(open(f, 'rb').read()).hexdigest() + '\n' for f in files)
    print(tree, len(files), hashlib.sha1(digests.encode()).hexdigest())
