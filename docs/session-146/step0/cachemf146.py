"""cachemf146.py - the cache manifest of one call of go146a.sh (session 143 (ported to s144 by HPP-330, to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146) link 1b, HPP-321; ROADMAP s122 item 242 (b)):
written before the lock and after the run, read by sc146.py --summary (one continuity line per adjacent pair of tags:
the manifest after N = the manifest before N+1).  READ ONLY on the caches: it lists and hashes, never writes there.

    python cachemf146.py <out.json> [--root <name>=<dir> ...]

Roots (defaults; --root replaces one, for fixtures):
  shader    C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564      (the translation cache of the emulator)
  pipeline  C:/kyty/KytyPS5/ps5 em/_PipelineCache              (the Vulkan pipeline cache of the emulator, if present)
  glcache   %LOCALAPPDATA%/NVIDIA/GLCache                       (the driver cache; LOCALAPPDATA, else USERPROFILE/AppData/Local)
Every file under a root (recursive): its path relative to the root ('/'), size, mtime (ns) and sha256 ("unreadable" when it
cannot be read).  The json: {taken_utc, roots: [[name, dir, present]], files: [[name, rel, size, mtime_ns, sha256]]}.  One
ASCII line: per root the number of files and bytes (a missing root: "absent"), and the sha256 of the json written; the
directories are not printed (the driver cache lies under the user profile).  rc 0 with the line written, rc 1 when the json
cannot be written.
"""
import datetime
import hashlib
import json
import os
import sys

EMU = 'C:/kyty/KytyPS5/ps5 em'
ORDER = ('shader', 'pipeline', 'glcache')
CHUNK = 1 << 22


def default_roots(env=None):
    env = os.environ if env is None else env
    lad = env.get('LOCALAPPDATA') or os.path.join(env.get('USERPROFILE') or os.path.expanduser('~'), 'AppData', 'Local')
    return dict(shader=EMU + '/_ShaderCache/PPSA21564', pipeline=EMU + '/_PipelineCache',
                glcache=os.path.join(lad, 'NVIDIA', 'GLCache').replace('\\', '/'))


def sha_of(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while True:
                b = f.read(CHUNK)
                if not b:
                    break
                h.update(b)
    except OSError:
        return 'unreadable'
    return h.hexdigest()


def manifest(roots):
    """(roots rows, file rows) of the roots dict {name: dir} in ORDER."""
    rrows, frows = [], []
    for name in ORDER:
        d = roots[name]
        present = os.path.isdir(d)
        rrows.append([name, d, present])
        if not present:
            continue
        for dp, dn, fn in os.walk(d):
            dn.sort()
            for f in sorted(fn):
                p = os.path.join(dp, f)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                rel = os.path.relpath(p, d).replace('\\', '/')
                frows.append([name, rel, st.st_size, st.st_mtime_ns, sha_of(p)])
    return rrows, frows


def main(argv=None, env=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0].startswith('--'):
        print('usage: cachemf146.py <out.json> [--root <name>=<dir> ...]')
        return 2
    roots = default_roots(env)
    i = 1
    while i < len(argv):
        if argv[i] == '--root' and i + 1 < len(argv) and '=' in argv[i + 1]:
            k, v = argv[i + 1].split('=', 1)
            if k not in roots:
                print('usage: unknown root %s' % k)
                return 2
            roots[k] = v
            i += 2
        else:
            print('usage: cachemf146.py <out.json> [--root <name>=<dir> ...]')
            return 2
    rrows, frows = manifest(roots)
    js = dict(taken_utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), roots=rrows,
              files=frows)
    try:
        with open(argv[0], 'w', encoding='ascii') as f:
            json.dump(js, f)
    except (OSError, UnicodeError) as e:
        print('cachemf146: manifest not written (%s)' % type(e).__name__)
        return 1
    parts = []
    for name, d, present in rrows:
        fs = [x for x in frows if x[0] == name]
        parts.append('%s %s' % (name, ('%d files %d bytes%s' % (len(fs), sum(x[2] for x in fs), (', unreadable %d' % sum(
            1 for x in fs if x[4] == 'unreadable')) if any(x[4] == 'unreadable' for x in fs) else '')) if present
            else 'absent'))
    print('cachemf146: %s; %s sha256 %s' % ('; '.join(parts), os.path.basename(argv[0]), sha_of(argv[0])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
