"""F20l3 (HPP-655; ROADMAP s122 item 591 (v)(1)): the cold-translation form of the PK-A tags b32_pa / b32_pa2.  Inside the lock, after the
pre-tag copy of the caches, the translation and recipe files the F20j4 test binary could read and the known-scenes seed catalogue are MOVED
out of the live emulator folder into the reserve of the tag:
  _ShaderSeeds/PPSA21564                                    the whole directory (else InstallShaderSeed installs it into the empty variant dir)
  _ShaderCache/PPSA21564/<cs|ps|vs>_*.bin                   the program files of the root
  _ShaderCache/PPSA21564/pipelines.bin                      the recipes of the root
  _ShaderCache/PPSA21564/variant_fixb26_fixb1b_fixf10_fixf19 the whole directory (translations and pipelines.bin of the test binary's variant)
Not moved: _ShaderCache/PPSA21564/replay (S-replay of S18; the F20j4 binary has no S-replay code), the other variant directories (not the
variant of the test binary), _PipelineCache, _SaveData, the driver GLCache.
The return after the tag is the return of the whole _ShaderCache and _ShaderSeeds from the pre-tag copy (go_f20l3.sh, as every cache); the
reserve is then checked line by line against manifest_after (every reserve file with the same size and sha256 is back) and removed.
usage:
  python reserve_f20l3.py move <emu dir> <reserve dir>          rc 0 'RESERVE MOVED files <n> ...' + reserve.tsv; rc 1 on any failure
                                                               (what was moved stays in the reserve; the caller's return restores the live
                                                               folder from the pre-tag copy)
  python reserve_f20l3.py cold <emu dir>                        rc 0 'COLD OK' when none of the set is in the live folder, else rc 1
  python reserve_f20l3.py check <reserve.tsv> <manifest.tsv>    rc 0 'RESERVE IN AFTER <n> of <n>', else rc 1 with the first missing lines
reserve.tsv lines have the form of manifest_fs4c.py ('<label>\\t<path relative to the label dir>\\t<size>\\t<sha256>', labels _ShaderSeeds and
_ShaderCache), so they are compared with manifest_before / manifest_after directly.  ASCII only.
"""
import hashlib
import os
import re
import shutil
import sys

TITLE = 'PPSA21564'
VARIANT = 'variant_fixb26_fixb1b_fixf10_fixf19'
PROG = re.compile(r'^(cs|ps|vs)_[0-9a-f]{16}_[0-9a-f]{16}\.bin$')


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def the_set(emu):
    """[(label, rel path under the label dir, absolute path, is_dir)] of the live set (only what exists)."""
    out = []
    seeds = os.path.join(emu, '_ShaderSeeds', TITLE)
    if os.path.isdir(seeds):
        out.append(('_ShaderSeeds', TITLE, seeds, True))
    root = os.path.join(emu, '_ShaderCache', TITLE)
    if os.path.isdir(root):
        for fn in sorted(os.listdir(root)):
            p = os.path.join(root, fn)
            if os.path.isfile(p) and (PROG.match(fn) or fn == 'pipelines.bin'):
                out.append(('_ShaderCache', TITLE + '/' + fn, p, False))
        v = os.path.join(root, VARIANT)
        if os.path.isdir(v):
            out.append(('_ShaderCache', TITLE + '/' + VARIANT, v, True))
    return out


def lines_of(label, rel, path, is_dir):
    if not is_dir:
        return ['%s\t%s\t%d\t%s' % (label, rel, os.path.getsize(path), sha_file(path))]
    out = []
    for r, dirs, files in os.walk(path):
        dirs.sort()
        for fn in sorted(files):
            p = os.path.join(r, fn)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            sub = os.path.relpath(p, path).replace(os.sep, '/')
            out.append('%s\t%s/%s\t%d\t%s' % (label, rel, sub, os.path.getsize(p), sha_file(p)))
    return out


def move(emu, res):
    if os.path.exists(res):
        print('RESERVE FAILED reserve dir exists')
        return 1
    items = the_set(emu)
    if not any(x[0] == '_ShaderSeeds' for x in items) or not any(x[1].endswith(VARIANT) for x in items):
        print('RESERVE FAILED the live set is incomplete (seeds %s, variant dir %s) - not cold-able by this form' % (
            any(x[0] == '_ShaderSeeds' for x in items), any(x[1].endswith(VARIANT) for x in items)))
        return 1
    lines = []
    for label, rel, path, is_dir in items:
        lines += lines_of(label, rel, path, is_dir)
    lines.sort()
    os.makedirs(res)
    with open(os.path.join(res, 'reserve.tsv'), 'wb') as f:
        f.write(('\n'.join(lines) + '\n').encode('utf-8'))
    n_dirs = n_files = 0
    for label, rel, path, is_dir in items:
        dst = os.path.join(res, label, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            shutil.move(path, dst)
        except OSError as e:
            print('RESERVE FAILED move of %s/%s: %s' % (label, rel, type(e).__name__))
            return 1
        n_dirs += 1 if is_dir else 0
        n_files += 0 if is_dir else 1
    left = the_set(emu)
    if left:
        print('RESERVE FAILED %d items left in the live folder' % len(left))
        return 1
    nbytes = sum(int(x.split('\t')[2]) for x in lines)
    print('RESERVE MOVED files %d bytes %d (dirs %d, root files %d) listsha %s' % (
        len(lines), nbytes, n_dirs, n_files, hashlib.sha256(('\n'.join(lines) + '\n').encode('utf-8')).hexdigest()))
    return 0


def cold(emu):
    left = the_set(emu)
    if left:
        print('COLD NOT %d items: %s' % (len(left), ', '.join('%s/%s' % (a, b) for a, b, _, _ in left[:5])))
        return 1
    print('COLD OK')
    return 0


def check(res_tsv, man_tsv):
    a = [x for x in open(res_tsv, 'rb').read().decode('utf-8').split('\n') if x]
    b = set(x for x in open(man_tsv, 'rb').read().decode('utf-8').split('\n') if x)
    miss = [x for x in a if x not in b]
    if a and not miss:
        print('RESERVE IN AFTER %d of %d' % (len(a), len(a)))
        return 0
    print('RESERVE NOT IN AFTER missing %d of %d' % (len(miss), len(a)))
    for x in miss[:5]:
        print('  missing %s' % x.encode('ascii', 'backslashreplace').decode('ascii'))
    return 1


def main(argv):
    if len(argv) == 3 and argv[0] == 'move':
        return move(argv[1], argv[2])
    if len(argv) == 2 and argv[0] == 'cold':
        return cold(argv[1])
    if len(argv) == 3 and argv[0] == 'check':
        return check(argv[1], argv[2])
    print('usage: reserve_f20l3.py move <emu> <reserve> | cold <emu> | check <reserve.tsv> <manifest.tsv>')
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
