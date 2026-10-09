"""Track F link F29e (HPP-704): the F25m file copied with ROOT moved; only merge-return and manifest are used by go_f29e.sh.
Track F link F25m (HPP-680; ROADMAP s122 item 596 (g), item 599 (b)(6), item 606 (v)(2)-(6)): the cache snapshots A / C1 / B of the
series and their user-file updates A' / B'.  The set is the five folders of the F20l3 harness manifest (C:/kyty/f287/f20l3/go_f20l3.sh,
array MF: _ShaderCache with replay/, _ShaderSeeds, _PipelineCache, _SaveData and the driver GLCache) - "cold" = A together with GLCache.
Runs ONLY under the lock taken by go_f25m.sh (writes the live caches on restore).  ASCII only.

  python snap_f25m.py take <name> [--replace]     copy the live set to snap/<name>/<label> and write snap/<name>.tsv (manifest of the live
                                                  set); then the manifest of the copy is compared with it - 'SNAP TAKEN <name> ...' rc 0
  python snap_f25m.py restore <name>              each live folder is removed and copied back from snap/<name>/<label> (an absent one stays
                                                  absent); then the live manifest is compared with snap/<name>.tsv - 'SNAP RESTORED <name>
                                                  manifest cmp EQUAL ...' rc 0, else 'SNAP RESTORE FAILED' rc 1.  The snapshots A / B carry
                                                  every user file D (item 606 (v)(2)), so a restore never removes a file of D (item 606 (v)(3)).
  python snap_f25m.py reconcile                   item 606 (v)(2)-(5): the live manifest L against the expected state S (snap/STATE: 'B' -
                                                  B', 'A' - A'; absent = 'B').  A file of S removed or changed that is not a user file D ->
                                                  'RECONCILE STOP' rc 4 (item 606 (v)(4)); a file of L outside S that is a series file
                                                  (A0 / B0 / A / B) and not in D -> STOP; L = S -> 'RECONCILE EQUAL' rc 0; else a user update:
                                                  new files outside the series files, changed or removed files of D - applied to BOTH snapshots
                                                  A and B (copies of the live user files, tsv lines, snap/D.tsv), one line in snap/updates.log -
                                                  'RECONCILE UPDATED ...' rc 0; the third update -> 'RECONCILE LIMIT' rc 5, nothing changed
                                                  (item 606 (v)(5)).  A0.tsv / B0.tsv keep the first A / B.
  python snap_f25m.py state <A|B>                 writes snap/STATE
  python snap_f25m.py promote <label/rel> ...     item 622 (v)(1)-(2): series files equal in A and B and changed outside the tags become
                                                  user files D.  Only at STATE B; each named file is in A.tsv and B.tsv with one sha, not in
                                                  D, present live and changed against B; the live manifest L differs from B ONLY in the named
                                                  files - else 'PROMOTE STOP' rc 4, nothing touched (item 606 (v)(4)); a bad name - 'PROMOTE
                                                  REFUSED' rc 2; the third update - 'PROMOTE LIMIT' rc 5.  Then the live files are copied into
                                                  both snapshots (A', B'), their tsv lines and snap/D.tsv are written, one line in
                                                  snap/updates.log (an update of item 606 (v)(5)) - 'PROMOTE DONE update n of 2 ...' - and
                                                  reconcile runs: rc 0 only with 'RECONCILE EQUAL' (item 622 (v)(2)).  Afterwards a change of
                                                  these files reads as a user update (item 622 (v)(3)).
  python snap_f25m.py merge-return <label> <before dir> <live dir>   item 606 (v)(3) for a tag that saw a user VM: every file of the
                                                  copy before is written back (same content), live files not in the copy are KEPT and
                                                  listed - 'MERGE RETURN kept n' rc 0
  python snap_f25m.py manifest <out.tsv>          the live manifest (the form of manifest_fs4c.py)
  --root <dir> (fixtures only): the snapshot folder instead of C:/kyty/f287/f29e/snap; --live <label>=<dir> ... replaces the live set.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifest_fs4c as M  # noqa: E402

EMU = 'C:/kyty/KytyPS5/ps5 em'
GL = os.path.join(os.environ.get('USERPROFILE', 'C:/Users/x'), 'AppData/Local/NVIDIA/GLCache').replace('\\', '/')
LIVE = ['_ShaderCache=%s/_ShaderCache' % EMU, '_ShaderSeeds=%s/_ShaderSeeds' % EMU, '_PipelineCache=%s/_PipelineCache' % EMU,
        '_SaveData=%s/_SaveData' % EMU, 'GLCache=%s' % GL]
ROOT = 'C:/kyty/f287/f29e/snap'
UPDATES_MAX = 2


def write_manifest(out, pairs):
    lines = M.manifest(pairs)
    data = ('\n'.join(lines) + '\n').encode('utf-8')
    with open(out, 'wb') as f:
        f.write(data)
    return len(lines), data


def read_tsv(path):
    out = {}
    if not os.path.exists(path):
        return out
    for l in open(path, 'rb').read().decode('utf-8').split('\n'):
        if not l:
            continue
        lab, rel, size, sha = l.split('\t')
        if rel == '<MISSING>':
            continue
        out[(lab, rel)] = (size, sha)
    return out


def write_tsv(path, d, missing_labels=()):
    lines = ['%s\t%s\t%s\t%s' % (k[0], k[1], v[0], v[1]) for k, v in d.items()]
    lines += ['%s\t<MISSING>\t0\t-' % lab for lab in missing_labels]
    lines.sort()
    with open(path, 'wb') as f:
        f.write(('\n'.join(lines) + '\n').encode('utf-8'))


def missing_of(path):
    out = []
    if os.path.exists(path):
        for l in open(path, 'rb').read().decode('utf-8').split('\n'):
            if l and l.split('\t')[1] == '<MISSING>':
                out.append(l.split('\t')[0])
    return out


def live_dir(live, label):
    for pair in live:
        lab, d = pair.split('=', 1)
        if lab == label:
            return d
    return None


def reconcile(root, live):
    st = open(os.path.join(root, 'STATE'), encoding='ascii').read().strip() if os.path.exists(os.path.join(root, 'STATE')) else 'B'
    stsv = os.path.join(root, st + '.tsv')
    S = read_tsv(stsv)
    try:
        L = dict(((x.split('\t')[0], x.split('\t')[1]), (x.split('\t')[2], x.split('\t')[3])) for x in M.manifest(live)
                 if x.split('\t')[1] != '<MISSING>')
    except OSError as e:
        print('RECONCILE ERROR live manifest %s' % type(e).__name__)
        return 6
    series = set(read_tsv(os.path.join(root, 'A0.tsv'))) | set(read_tsv(os.path.join(root, 'B0.tsv'))) | \
        set(read_tsv(os.path.join(root, 'A.tsv'))) | set(read_tsv(os.path.join(root, 'B.tsv')))
    D = read_tsv(os.path.join(root, 'D.tsv'))
    stop, new, changed, removed = [], [], [], []
    for k, v in S.items():
        if k not in L:
            (removed if k in D else stop).append(k)
        elif L[k] != v:
            (changed if k in D else stop).append(k)
    for k in L:
        if k not in S:
            if k in series and k not in D:
                stop.append(k)
            else:
                new.append(k)
    if stop:
        print('RECONCILE STOP state %s: %d series files changed, removed or unexpected (item 606 (v)(4)): %s' % (
            st, len(stop), ['%s/%s' % k for k in sorted(stop)[:5]]))
        return 4
    if not new and not changed and not removed:
        print('RECONCILE EQUAL state %s files %d' % (st, len(L)))
        return 0
    ulog = os.path.join(root, 'updates.log')
    nupd = len([l for l in open(ulog, encoding='ascii').read().splitlines() if l.strip()]) if os.path.exists(ulog) else 0
    if nupd >= UPDATES_MAX:
        print('RECONCILE LIMIT state %s: update %d > %d (item 606 (v)(5)) - new %d changed %d removed %d; nothing changed' % (
            st, nupd + 1, UPDATES_MAX, len(new), len(changed), len(removed)))
        return 5
    for snap in ('A', 'B'):
        if not os.path.exists(os.path.join(root, snap + '0.tsv')):
            shutil.copy2(os.path.join(root, snap + '.tsv'), os.path.join(root, snap + '0.tsv'))
    for snap in ('A', 'B'):
        tsv = os.path.join(root, snap + '.tsv')
        T = read_tsv(tsv)
        miss = missing_of(tsv)
        for k in new + changed:
            src = os.path.join(live_dir(live, k[0]), k[1])
            dst = os.path.join(root, snap, k[0], k[1])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            T[k] = L[k]
        for k in removed:
            p = os.path.join(root, snap, k[0], k[1])
            if os.path.exists(p):
                os.remove(p)
            T.pop(k, None)
        miss = [m for m in miss if not any(k[0] == m for k in new + changed)]
        write_tsv(tsv, T, miss)
    for k in new + changed:
        D[k] = L[k]
    for k in removed:
        D.pop(k, None)
    write_tsv(os.path.join(root, 'D.tsv'), D)
    with open(ulog, 'a', encoding='ascii') as f:
        f.write('%s update %d state %s new %d changed %d removed %d: %s\n' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), nupd + 1, st,
                                                                         len(new), len(changed), len(removed),
                                                                         ['%s/%s %s' % (k[0], k[1], L[k][1][:16]) for k in sorted(new + changed)][:20]))
    S2 = read_tsv(stsv)
    ok = S2 == L
    print('RECONCILE UPDATED %d of %d: state %s new %d changed %d removed %d; snapshot %s = live %s' % (
        nupd + 1, UPDATES_MAX, st, len(new), len(changed), len(removed), st, 'EQUAL' if ok else 'DIFFER'))
    return 0 if ok else 1


def promote(root, live, names):
    """Item 622 (v)(1)-(2): the named series files (equal in A and B) changed outside the tags -> user files D in both snapshots."""
    st = open(os.path.join(root, 'STATE'), encoding='ascii').read().strip() if os.path.exists(os.path.join(root, 'STATE')) else 'B'
    if st != 'B':
        print('PROMOTE REFUSED state %s - only at state B (item 622 (v)(2))' % st)
        return 2
    keys = []
    for n in names:
        if '/' not in n:
            print('PROMOTE REFUSED bad name %s (label/rel)' % n)
            return 2
        keys.append(tuple(n.split('/', 1)))
    if not keys or len(set(keys)) != len(keys):
        print('PROMOTE REFUSED no names or a name twice')
        return 2
    A = read_tsv(os.path.join(root, 'A.tsv'))
    B = read_tsv(os.path.join(root, 'B.tsv'))
    D = read_tsv(os.path.join(root, 'D.tsv'))
    try:
        L = dict(((x.split('\t')[0], x.split('\t')[1]), (x.split('\t')[2], x.split('\t')[3])) for x in M.manifest(live)
                 if x.split('\t')[1] != '<MISSING>')
    except OSError as e:
        print('PROMOTE ERROR live manifest %s' % type(e).__name__)
        return 6
    for k in keys:
        why = None
        if k not in A or k not in B:
            why = 'not in both A and B'
        elif A[k] != B[k]:
            why = 'differs between A and B'
        elif k in D:
            why = 'already a user file D'
        elif k not in L:
            why = 'not in the live set'
        elif L[k] == B[k]:
            why = 'not changed against B'
        if why:
            print('PROMOTE REFUSED %s/%s: %s; nothing touched' % (k[0], k[1], why))
            return 2
    others = sorted(k for k in set(B) | set(L) if B.get(k) != L.get(k) and k not in keys)
    if others:
        print('PROMOTE STOP state B: %d other files differ from B (item 606 (v)(4), item 622 (v)(2)): %s; nothing touched' % (
            len(others), ['%s/%s' % k for k in others[:5]]))
        return 4
    ulog = os.path.join(root, 'updates.log')
    nupd = len([l for l in open(ulog, encoding='ascii').read().splitlines() if l.strip()]) if os.path.exists(ulog) else 0
    if nupd >= UPDATES_MAX:
        print('PROMOTE LIMIT state B: update %d > %d (item 606 (v)(5)); nothing touched' % (nupd + 1, UPDATES_MAX))
        return 5
    for snap in ('A', 'B'):
        if not os.path.exists(os.path.join(root, snap + '0.tsv')):
            shutil.copy2(os.path.join(root, snap + '.tsv'), os.path.join(root, snap + '0.tsv'))
    for snap in ('A', 'B'):
        tsv = os.path.join(root, snap + '.tsv')
        T = read_tsv(tsv)
        miss = missing_of(tsv)
        for k in keys:
            dst = os.path.join(root, snap, k[0], k[1])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(live_dir(live, k[0]), k[1]), dst)
            T[k] = L[k]
        write_tsv(tsv, T, miss)
    for k in keys:
        D[k] = L[k]
    write_tsv(os.path.join(root, 'D.tsv'), D)
    with open(ulog, 'a', encoding='ascii') as f:
        f.write('%s update %d state B promote %d (item 622 (v)(1)): %s\n' % (
            time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), nupd + 1, len(keys),
            ['%s/%s %s -> %s %s' % (k[0], k[1], B[k][0], L[k][0], L[k][1]) for k in keys]))
    print('PROMOTE DONE update %d of %d: state B promote %d: %s' % (nupd + 1, UPDATES_MAX, len(keys),
                                                                  ['%s/%s %s %s' % (k[0], k[1], L[k][0], L[k][1][:16]) for k in keys]))
    rc = reconcile(root, live)
    return 0 if rc == 0 and read_tsv(os.path.join(root, 'B.tsv')) == L else 1


def merge_return(before, live):
    """Write every file of the copy before back into the live folder (same content), keep the live files not in it."""
    kept = []
    for dp, dn, fn in os.walk(live):
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, live)
            if not os.path.exists(os.path.join(before, rel)):
                kept.append(rel.replace(os.sep, '/'))
    for dp, dn, fn in os.walk(before):
        for f in fn:
            src = os.path.join(dp, f)
            dst = os.path.join(live, os.path.relpath(src, before))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    shutil.rmtree(before)
    print('MERGE RETURN kept %d: %s' % (len(kept), kept[:10]))
    return 0


def main(argv):
    root = argv[argv.index('--root') + 1] if '--root' in argv else ROOT
    live = LIVE
    if '--live' in argv:
        i = argv.index('--live') + 1
        live = []
        while i < len(argv) and '=' in argv[i]:
            live.append(argv[i])
            i += 1
    if not argv or argv[0] not in ('take', 'restore', 'manifest', 'reconcile', 'state', 'merge-return', 'promote'):
        print(__doc__.split('\n')[5].strip())
        return 2
    if argv[0] == 'manifest':
        n, data = write_manifest(argv[1], live)
        print('manifest %s files %d' % (argv[1], n))
        return 0
    if argv[0] == 'reconcile':
        return reconcile(root, live)
    if argv[0] == 'promote':
        names = []
        for a in argv[1:]:
            if a.startswith('--'):
                break
            names.append(a)
        return promote(root, live, names)
    if argv[0] == 'state':
        with open(os.path.join(root, 'STATE'), 'w', encoding='ascii') as f:
            f.write(argv[1] + '\n')
        print('STATE %s' % argv[1])
        return 0
    if argv[0] == 'merge-return':
        return merge_return(argv[2], argv[3])
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
