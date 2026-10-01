#!/usr/bin/env python3
"""cachex_s.py - track S, link S3 (HPP-313; ROADMAP "SESSION 122" item 241 (g)(1)-(3), S1 RC1, RC12): the cache protocol of
one arm of track S under the lock, called only by go_s.sh.

Two cache sets:
  app  - the emulator's _ShaderCache/PPSA21564 and _PipelineCache; manifest lines "<path> <size> <sha256>", sorted, with
         the path map of RC12 (_PipelineCache/ <-> PipelineCache/, _ShaderCache/PPSA21564/ <-> ShaderCache_PPSA21564/); the
         manifest of C:/kyty/s288/snap0 is d8ca8c8e... (S0 3.1, S1 RC12).  A copy directory has the snapshot's layout
         (PipelineCache/, ShaderCache_PPSA21564/) and its MANIFEST.txt.
  glc  - <known folder FOLDERID_LocalAppData>/NVIDIA/GLCache (S3b RC9, item 250 (zh): the path comes from
         SHGetKnownFolderPath, the folder the driver writes to; every glc operation refuses rc 1 when %LOCALAPPDATA% of the
         environment is absent or is not that folder, and restore / copy refuse rc 1 when the live root does not exist -
         nothing is created); manifest lines "<rel>\\t<size>\\t<mtime UTC>\\t<sha256>", sorted (the format of
         C:/kyty/s288/lead/snap0_drv.py; C:/kyty/s288/snap0_drv is 1767ca0a...).  A copy directory holds the files and
         MANIFEST.txt.  DXCache is never touched (item 241 (g)(3)).
Operations (each prints one ASCII line "<op> ... sha <manifest sha256>" and ends rc 0, or rc 1 on any mismatch):
  man app | man glc [--save <file>]    the manifest of the live set (read only; --save writes its text, under the lock)
  where glc                            the GLCache path, the known folder and %LOCALAPPDATA% (rc 1 on a mismatch)
  copy app|glc <dst>                   copy the live set into <dst> (refuses an existing <dst> unless --replace)
  restore app|glc <src> <expected>     mirror the live set from the copy <src>: files not in <src> are removed, every file
                                       of <src> is copied (mtime kept); then the live manifest must equal <expected> and
                                       the MANIFEST.txt of <src>
  copy gcn <dst> | man gcn             the GCN dumps of KYTY_DUMP_GCN (<emulator>/_Shaders/gcn), app-style lines
  note <json> <key> <k>=<v> ...        set json[key] = {k: v, ...} in the arm's cache json (created when missing)
WRITES (copy, restore) refuse rc 3 unless C:/kyty/SEALED_RUN.lock exists and its first line starts with "go_s.sh <tag>"
for the --tag given (the arm that holds the lock).  Paths can be moved by the environment for fixtures only:
CACHEX_EMU, CACHEX_GLC, CACHEX_LOCK, CACHEX_KNOWN_LAD (stands for the known folder; the check against %LOCALAPPDATA%
runs the same way).
    python cachex_s.py --tag <tag> <op> ...
"""
import datetime
import hashlib
import os
import shutil
import sys

def known_lad(override=True):
    """FOLDERID_LocalAppData {F1B32785-6FBA-4FCF-9D55-7B8E7F157091} by SHGetKnownFolderPath (RC9); CACHEX_KNOWN_LAD stands
    for it in fixtures only; None when the call fails."""
    if override and os.environ.get('CACHEX_KNOWN_LAD'):
        return os.environ['CACHEX_KNOWN_LAD']
    try:
        import ctypes
        import uuid
        from ctypes import wintypes
        guid = (ctypes.c_ubyte * 16).from_buffer_copy(uuid.UUID('{F1B32785-6FBA-4FCF-9D55-7B8E7F157091}').bytes_le)
        p = ctypes.c_wchar_p()
        f = ctypes.windll.shell32.SHGetKnownFolderPath
        f.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)]
        if f(ctypes.byref(guid), 0, None, ctypes.byref(p)) != 0:
            return None
        v = p.value
        ctypes.windll.ole32.CoTaskMemFree(p)
        return v
    except Exception:
        return None


def same_path(a, b):
    return a is not None and b is not None and \
        os.path.normcase(os.path.normpath(a.replace('/', os.sep))) == os.path.normcase(os.path.normpath(b.replace('/', os.sep)))


def glc_check():
    """(ok, line): %LOCALAPPDATA% of the environment must be the known folder (RC9)."""
    k, e = known_lad(), os.environ.get('LOCALAPPDATA')
    ok = same_path(k, e)
    return ok, 'glc path %s known %s env LOCALAPPDATA %s %s' % (GLC, k, e, 'ok' if ok else 'MISMATCH')


EMU = os.environ.get('CACHEX_EMU') or 'C:/kyty/KytyPS5/ps5 em'
GLC = os.environ.get('CACHEX_GLC') or os.path.join(known_lad() or 'C:/NO_KNOWN_FOLDER', 'NVIDIA', 'GLCache')
LOCK = os.environ.get('CACHEX_LOCK') or 'C:/kyty/SEALED_RUN.lock'
APP_MAP = (('PipelineCache/', '_PipelineCache'), ('ShaderCache_PPSA21564/', '_ShaderCache/PPSA21564'))
GCN_SUB = '_Shaders/gcn'
MAN = 'MANIFEST.txt'


def sha_of(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def text_sha(lines):
    t = ''.join(x + '\n' for x in lines)
    return t, hashlib.sha256(t.encode('utf-8')).hexdigest()


def walk(root):
    """Relative file paths under root (sorted, '/' separators); [] when root does not exist."""
    out = []
    if os.path.isdir(root):
        for dp, _, fn in os.walk(root):
            for f in fn:
                out.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/'))
    return sorted(out)


def app_pairs(base):
    """(manifest name, absolute path) of the app set rooted at base: the live emulator folder or a copy directory."""
    live = base is None
    out = []
    for prefix, sub in APP_MAP:
        root = os.path.join(EMU, sub) if live else os.path.join(base, prefix.rstrip('/'))
        for rel in walk(root):
            out.append((prefix + rel, os.path.join(root, rel)))
    return out


def app_manifest(base=None):
    lines = sorted('%s %d %s' % (n, os.path.getsize(p), sha_of(p)) for n, p in app_pairs(base))
    return text_sha(lines)


def glc_manifest(root):
    lines = []
    for rel in walk(root):
        if root != GLC and rel == MAN:
            continue
        p = os.path.join(root, rel)
        st = os.stat(p)
        t = datetime.datetime.fromtimestamp(int(st.st_mtime), datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        lines.append('%s\t%d\t%s\t%s' % (rel, st.st_size, t, sha_of(p)))
    return text_sha(sorted(lines))


def gcn_manifest(root):
    lines = sorted('%s %d %s' % (rel, os.path.getsize(os.path.join(root, rel)), sha_of(os.path.join(root, rel)))
                   for rel in walk(root) if not (root != os.path.join(EMU, GCN_SUB) and rel == MAN))
    return text_sha(lines)


def note(path, key, pairs):
    import json
    d = json.load(open(path, encoding='utf-8')) if os.path.isfile(path) else {}
    v = {}
    for p in pairs:
        if '=' not in p:
            return 2, 'note: bad pair %s' % p
        k, x = p.split('=', 1)
        v[k] = x
    d[key] = v
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=1, sort_keys=True)
    return 0, 'note %s %s %s' % (path, key, ' '.join(sorted(pairs)))


def lock_ok(tag):
    if not tag or not os.path.isfile(LOCK):
        return False
    with open(LOCK, 'r', encoding='utf-8', errors='replace') as f:
        first = f.readline()
    return first.startswith('go_s.sh %s ' % tag)


def copy_set(kind, dst, replace=False):
    if os.path.exists(dst):
        if not replace:
            return 1, 'copy %s refused: %s exists' % (kind, dst)
        shutil.rmtree(dst)
    os.makedirs(dst)
    if kind == 'gcn':
        src = os.path.join(EMU, GCN_SUB)
        for rel in walk(src):
            q = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(os.path.join(src, rel), q)
        text, sha = gcn_manifest(src)
        t2, s2 = gcn_manifest(dst)
    elif kind == 'app':
        for name, p in app_pairs(None):
            q = os.path.join(dst, name)
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(p, q)
        text, sha = app_manifest(None)
        t2, s2 = app_manifest(dst)
    else:
        if not os.path.isdir(GLC):
            shutil.rmtree(dst)
            return 1, 'copy glc refused: the live root %s does not exist' % GLC
        for rel in walk(GLC):
            q = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(os.path.join(GLC, rel), q)
        text, sha = glc_manifest(GLC)
        t2, s2 = glc_manifest(dst)
    with open(os.path.join(dst, MAN), 'wb') as f:
        f.write(text.encode('utf-8'))
    if s2 != sha:
        return 1, 'copy %s %s: copy manifest %s != live %s' % (kind, dst, s2, sha)
    return 0, 'copy %s %s files %d sha %s' % (kind, dst, text.count('\n'), sha)


def restore_set(kind, src, expected):
    if not os.path.isfile(os.path.join(src, MAN)):
        return 1, 'restore %s refused: %s has no %s' % (kind, src, MAN)
    with open(os.path.join(src, MAN), 'rb') as f:
        src_sha = hashlib.sha256(f.read()).hexdigest()
    if src_sha != expected:
        return 1, 'restore %s refused: %s/%s sha %s != expected %s' % (kind, src, MAN, src_sha, expected)
    if kind == 'app':
        for prefix, sub in APP_MAP:
            live = os.path.join(EMU, sub)
            copy = os.path.join(src, prefix.rstrip('/'))
            want = set(walk(copy))
            for rel in walk(live):
                if rel not in want:
                    os.remove(os.path.join(live, rel))
            for rel in sorted(want):
                q = os.path.join(live, rel)
                os.makedirs(os.path.dirname(q), exist_ok=True)
                shutil.copy2(os.path.join(copy, rel), q)
        _, got = app_manifest(None)
    else:
        if not os.path.isdir(GLC):
            return 1, 'restore glc refused: the live root %s does not exist (nothing created)' % GLC
        want = set(r for r in walk(src) if r != MAN)
        for rel in walk(GLC):
            if rel not in want:
                os.remove(os.path.join(GLC, rel))
        for rel in sorted(want):
            q = os.path.join(GLC, rel)
            os.makedirs(os.path.dirname(q), exist_ok=True)
            shutil.copy2(os.path.join(src, rel), q)
        _, got = glc_manifest(GLC)
    if got != expected:
        return 1, 'restore %s from %s: live sha %s != expected %s' % (kind, src, got, expected)
    return 0, 'restore %s from %s sha %s' % (kind, src, got)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    tag = None
    replace = False
    if '--tag' in a:
        i = a.index('--tag')
        tag = a[i + 1] if i + 1 < len(a) else None
        del a[i:i + 2]
    if '--replace' in a:
        a.remove('--replace')
        replace = True
    save = None
    if '--save' in a:
        i = a.index('--save')
        save = a[i + 1] if i + 1 < len(a) else None
        del a[i:i + 2]
        if not save:
            print('usage: --save <file>')
            return 2
    if a[:2] == ['where', 'glc'] and len(a) == 2:
        ok, line = glc_check()
        print('where ' + line)
        return 0 if ok else 1
    if len(a) >= 2 and a[1] == 'glc' and a[0] in ('man', 'copy', 'restore'):
        ok, line = glc_check()
        if not ok:
            print('%s glc refused: %s' % (a[0], line))
            return 1
    if a and a[0] == 'note':
        if len(a) < 3:
            print('usage: note <json> <key> k=v ...')
            return 2
        if not lock_ok(tag):
            print('note refused: the lock is not held by go_s.sh %s' % tag)
            return 3
        rc, msg = note(a[1], a[2], a[3:])
        print(msg)
        return rc
    if len(a) < 2 or a[1] not in ('app', 'glc', 'gcn'):
        print('usage: cachex_s.py --tag <tag> man|copy|restore app|glc|gcn ...')
        return 2
    op, kind = a[0], a[1]
    if op == 'man' and len(a) == 2:
        text, sha = app_manifest(None) if kind == 'app' else (glc_manifest(GLC) if kind == 'glc' else
                                                              gcn_manifest(os.path.join(EMU, GCN_SUB)))
        if save:
            if not lock_ok(tag):
                print('man %s --save refused: the lock is not held by go_s.sh %s' % (kind, tag))
                return 3
            os.makedirs(os.path.dirname(save) or '.', exist_ok=True)
            with open(save, 'wb') as f:
                f.write(text.encode('utf-8'))
        print('man %s sha %s' % (kind, sha))
        return 0
    if op == 'restore' and kind == 'gcn':
        print('usage: gcn is never restored')
        return 2
    if op not in ('copy', 'restore'):
        print('usage: unknown op %s' % op)
        return 2
    if not lock_ok(tag):
        print('%s %s refused: the lock is not held by go_s.sh %s' % (op, kind, tag))
        return 3
    if op == 'copy' and len(a) == 3:
        rc, msg = copy_set(kind, a[2], replace)
    elif op == 'restore' and len(a) == 4:
        rc, msg = restore_set(kind, a[2], a[3])
    else:
        print('usage: bad arguments for %s' % op)
        return 2
    print(msg)
    return rc


if __name__ == '__main__':
    sys.exit(main())
