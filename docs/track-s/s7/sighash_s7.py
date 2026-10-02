"""S7: recompute KYTY_SHADER_SOURCE_HASH (src/generate_version.cmake) from disk and from git HEAD.
ASCII output only."""
import hashlib
import os
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
ROOT = REPO + '/src'


def file_list():
    files = []
    for dp, _dn, fn in os.walk(ROOT + '/graphics/shader'):
        for f in fn:
            if f.endswith(('.cpp', '.h', '.inc')):
                files.append(os.path.join(dp, f).replace(os.sep, '/'))
    files += [ROOT + '/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
              ROOT + '/graphics/guest_gpu/gpu_format.h', ROOT + '/graphics/guest_gpu/gpu_defs.h']
    return sorted(files)


def digest(blobs):
    s = ''.join(hashlib.sha1(b).hexdigest() + '\n' for b in blobs)
    return hashlib.sha1(s.encode()).hexdigest()


def main():
    rev = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
    files = file_list()
    disk = [open(f, 'rb').read() for f in files]
    print('files', len(files))
    print('disk_hash', digest(disk))
    crlf = [f for f, b in zip(files, disk) if b'\r\n' in b]
    print('crlf_files', len(crlf))
    for f in crlf[:20]:
        print('  crlf', f)
    blobs = []
    for f in files:
        rel = os.path.relpath(f, REPO).replace(os.sep, '/')
        r = subprocess.run(['git', '-C', REPO, 'show', rev + ':' + rel], capture_output=True)
        if r.returncode != 0:
            print('  not_in_git', rel)
            blobs.append(open(f, 'rb').read())
        else:
            blobs.append(r.stdout)
    print('git_hash', rev, digest(blobs))
    diff = [f for f, a, b in zip(files, disk, blobs) if a != b]
    print('disk_ne_git', len(diff))
    for f in diff[:20]:
        print('  diff', f)


if __name__ == '__main__':
    main()
