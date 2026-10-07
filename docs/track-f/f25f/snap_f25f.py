"""Track F link F25f (HPP-669; ROADMAP s122 item 596 (g), item 599 (b)(6)): the cache snapshots A / C1 / B of the series.  The set is the
five folders of the F20l3 harness manifest (C:/kyty/f287/f20l3/go_f20l3.sh, array MF: _ShaderCache with replay/, _ShaderSeeds,
_PipelineCache, _SaveData and the driver GLCache) - "cold" = A together with GLCache.  Runs ONLY under the lock taken by go_f25f.sh
(writes the live caches on restore).  ASCII only.

  python snap_f25f.py take <name> [--replace]     copy the live set to snap/<name>/<label> and write snap/<name>.tsv (manifest of the live
                                                  set); then the manifest of the copy is compared with it - 'SNAP TAKEN <name> ...' rc 0
  python snap_f25f.py restore <name>              each live folder is removed and copied back from snap/<name>/<label> (an absent one stays
                                                  absent); then the live manifest is compared with snap/<name>.tsv - 'SNAP RESTORED <name>
                                                  manifest cmp EQUAL ...' rc 0, else 'SNAP RESTORE FAILED' rc 1
  python snap_f25f.py manifest <out.tsv>          the live manifest (the form of manifest_fs4c.py)
  --root <dir> (fixtures only): the snapshot folder instead of C:/kyty/f287/f25f/snap; --live <label>=<dir> ... replaces the live set.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifest_fs4c as M  # noqa: E402

EMU = 'C:/kyty/KytyPS5/ps5 em'
GL = os.path.join(os.environ.get('USERPROFILE', 'C:/Users/x'), 'AppData/Local/NVIDIA/GLCache').replace('\\', '/')
LIVE = ['_ShaderCache=%s/_ShaderCache' % EMU, '_ShaderSeeds=%s/_ShaderSeeds' % EMU, '_PipelineCache=%s/_PipelineCache' % EMU,
        '_SaveData=%s/_SaveData' % EMU, 'GLCache=%s' % GL]
ROOT = 'C:/kyty/f287/f25f/snap'


def write_manifest(out, pairs):
    lines = M.manifest(pairs)
    data = ('\n'.join(lines) + '\n').encode('utf-8')
    with open(out, 'wb') as f:
        f.write(data)
    return len(lines), data


def main(argv):
    root = argv[argv.index('--root') + 1] if '--root' in argv else ROOT
    live = LIVE
    if '--live' in argv:
        i = argv.index('--live') + 1
        live = []
        while i < len(argv) and '=' in argv[i]:
            live.append(argv[i])
            i += 1
    if not argv or argv[0] not in ('take', 'restore', 'manifest'):
        print(__doc__.split('\n')[5].strip())
        return 2
    if argv[0] == 'manifest':
        n, data = write_manifest(argv[1], live)
        print('manifest %s files %d' % (argv[1], n))
        return 0
    name = argv[1]
    sd = os.path.join(root, name)
    tsv = os.path.join(root, name + '.tsv')
    if argv[0] == 'take':
        if os.path.exists(sd) or os.path.exists(tsv):
            if '--replace' not in argv:
                print('SNAP EXISTS %s - refused (use --replace)' % name)
                return 1
            shutil.rmtree(sd, ignore_errors=True)
            if os.path.exists(tsv):
                os.remove(tsv)
        os.makedirs(sd)
        copy_pairs = []
        for pair in live:
            label, d = pair.split('=', 1)
            dst = os.path.join(sd, label)
            if os.path.isdir(d):
                shutil.copytree(d, dst, copy_function=shutil.copy2)
            copy_pairs.append('%s=%s' % (label, dst))
        n, data = write_manifest(tsv, live)
        n2, data2 = write_manifest(tsv + '.copy', copy_pairs)
        ok = data == data2
        os.remove(tsv + '.copy')
        print('SNAP TAKEN %s files %d copy %s' % (name, n, 'EQUAL' if ok else 'DIFFER'))
        return 0 if ok else 1
    # restore
    if not os.path.isdir(sd) or not os.path.exists(tsv):
        print('SNAP RESTORE FAILED no snapshot %s' % name)
        return 1
    for pair in live:
        label, d = pair.split('=', 1)
        src = os.path.join(sd, label)
        if os.path.isdir(d):
            shutil.rmtree(d)
        if os.path.isdir(src):
            shutil.copytree(src, d, copy_function=shutil.copy2)
    got = tsv + '.live'
    write_manifest(got, live)
    a = open(tsv, 'rb').read()
    b = open(got, 'rb').read()
    os.remove(got)
    if a == b:
        print('SNAP RESTORED %s manifest cmp EQUAL files %d' % (name, len([x for x in a.split(b'\n') if x])))
        return 0
    print('SNAP RESTORE FAILED %s manifest differs' % name)
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
