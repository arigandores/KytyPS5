# F4b2 (HPP-347, Red Team): own recount of KYTY_SHADER_SOURCE_HASH of the F4c build tree by the model of
# src/generate_version.cmake (GLOB_RECURSE *.cpp *.h *.inc under src/graphics/shader + the three
# SHADER_CACHE_EXTRA_FILES of CMakeLists.txt:156, list(SORT), "<sha1 of file>\n" per file, sha1 of the
# concatenation). Forms: the bytes on disk of the work tree; the git blobs of a commit.
# Usage: python sig_f4b2.py <tree> <commit> [<commit> ...]
import glob
import hashlib
import os
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
tree = sys.argv[1].rstrip('/')
src = tree + '/src'
files = []
for ext in ('cpp', 'h', 'inc'):
    files += glob.glob(src + '/graphics/shader/**/*.' + ext, recursive=True)
files = [f.replace('\\', '/') for f in files]
files += [src + '/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
          src + '/graphics/guest_gpu/gpu_format.h', src + '/graphics/guest_gpu/gpu_defs.h']
files = sorted(set(files))
print('set files', len(files))


def sig(blobs):
    return hashlib.sha1(''.join(hashlib.sha1(b).hexdigest() + '\n' for b in blobs).encode()).hexdigest()


disk = [open(f, 'rb').read() for f in files]
crlf = sum(1 for b in disk if b'\r\n' in b)
print('work tree bytes: signature', sig(disk), 'files with CRLF', crlf)
rel = [f[len(tree) + 1:] for f in files]
for c in sys.argv[2:]:
    blobs = [subprocess.run([GIT, '-C', tree, 'show', f'{c}:{r}'], capture_output=True, check=True).stdout for r in rel]
    print('blobs of', c, 'signature', sig(blobs))
    eq = [r for r, a, b in zip(rel, disk, blobs) if a != b]
    eol = [r for r, a, b in zip(rel, disk, blobs) if a != b and a.replace(b'\r\n', b'\n') == b.replace(b'\r\n', b'\n')]
    print('  files differing from the blob', len(eq), 'of which only by CRLF', len(eol))
# files of the set changed by the F4 commits (must be none)
out = subprocess.run([GIT, '-C', tree, 'diff', '--name-only', '4fc501f4', 'HEAD', '--'] + rel, capture_output=True, check=True).stdout.decode()
print('set files changed 4fc501f4..HEAD:', out.split() or 'none')
