"""Track F link F27c (HPP-694; ROADMAP s122 item 631 (v)(6), the lead's decision: the NVIDIA driver disk shader cache - a snapshot before
the first tag f27_* and its return after the last).  Runs ONLY under the lock of go_f27c.sh (base / return modes).  ASCII only.

Folders (seal section 6): <NV>/GLCache (whole; FS10c / F25m practice) and <NV>/DXCache, NV = %USERPROFILE%/AppData/Local/NVIDIA.  The
DXCache group of the emulator is the file-name prefix EMU_GROUP (evidence in the seal: the files of this group are the ones changed inside
the lock windows of the F26c series on the same installed binary); only GLCache and the files of this group are copied (66 GB of DXCache
hold other applications' groups that a tag does not touch), every file of both folders is in the manifest (size, mtime_ns).

  python drvsnap_f27c.py take <root>               manifest <root>/drv_base.tsv (label, rel, size, mtime_ns), copy of GLCache and of the
                                                   DXCache group into <root>/drv_copy/<label>/ (copy2, mtime kept), sha256 of every copied
                                                   source and copy -> <root>/drv_copy.tsv; 'DRVSNAP TAKEN ...' rc 0, a mismatch rc 1
  python drvsnap_f27c.py return <root> <lock.log>  the live manifest against drv_base.tsv:
       a base file changed (size or mtime_ns) or removed, with a copy: restored from the copy when removed or when its live mtime lies
         inside a tag window [lock taken, lock released + SLACK_S] of lock.log - sha256 of the restored file = sha256 of the copy
         (RESTORED); changed outside every window - KEPT_USER (a user change, not touched);
       a base file changed or removed without a copy (other DXCache groups): NOT_COPIED (cannot be restored - question to the lead);
       a new file inside a window and (GLCache or the emulator group): moved to <root>/drv_moved/<label>/<rel> (MOVED); else KEPT_NEW.
     'DRVSNAP RETURNED restored a moved b kept_user c kept_new d not_copied e failed f' - rc 0 when not_copied + failed = 0, else 1.
  --nv <dir> (fixtures only): the NVIDIA folder.
"""
import datetime
import hashlib
import os
import shutil
import sys

NV = os.path.join(os.environ.get('USERPROFILE', 'C:/Users/x'), 'AppData/Local/NVIDIA').replace('\\', '/')
LABELS = ('GLCache', 'DXCache')
EMU_GROUP = '5d8aa91c'
SLACK_S = 5.0


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def asc(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')


def walk(nv):
    out = {}
    for lab in LABELS:
        d = os.path.join(nv, lab)
        if not os.path.isdir(d):
            continue
        for root, dirs, files in os.walk(d):
            dirs.sort()
            for fn in files:
                p = os.path.join(root, fn)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                out[(lab, os.path.relpath(p, d).replace(os.sep, '/'))] = (st.st_size, st.st_mtime_ns)
    return out


def copied(key):
    lab, rel = key
    return lab == 'GLCache' or (lab == 'DXCache' and '/' not in rel and rel.startswith(EMU_GROUP))


def write_tsv(path, d):
    with open(path, 'wb') as f:
        for k in sorted(d):
            f.write(('%s\t%s\t%s\n' % (k[0], k[1], '\t'.join(str(x) for x in d[k]))).encode('utf-8'))


def read_tsv(path):
    out = {}
    for l in open(path, 'rb').read().decode('utf-8').split('\n'):
        if l:
            p = l.split('\t')
            out[(p[0], p[1])] = tuple(p[2:])
    return out


def take(root, nv):
    base = walk(nv)
    write_tsv(os.path.join(root, 'drv_base.tsv'), base)
    cp = {}
    bad = 0
    nbytes = 0
    for k in sorted(base):
        if not copied(k):
            continue
        src = os.path.join(nv, k[0], k[1])
        dst = os.path.join(root, 'drv_copy', k[0], k[1])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        a, b = sha_file(src), sha_file(dst)
        st = os.stat(src)
        if a != b or (st.st_size, st.st_mtime_ns) != base[k]:
            bad += 1
        cp[k] = (st.st_size, a)
        nbytes += st.st_size
    write_tsv(os.path.join(root, 'drv_copy.tsv'), cp)
    print('DRVSNAP %s files %d (GLCache %d, DXCache %d) copied %d bytes %d mismatches %d' % (
        'TAKEN' if bad == 0 else 'TAKE FAILED', len(base), sum(1 for k in base if k[0] == 'GLCache'),
        sum(1 for k in base if k[0] == 'DXCache'), len(cp), nbytes, bad))
    return 0 if bad == 0 else 1


def windows(lock_log):
    taken = {}
    out = []
    for l in open(lock_log, encoding='ascii', errors='replace').read().splitlines():
        p = l.split()
        if len(p) == 4 and p[0] == 'lock' and p[1] in ('taken', 'released'):
            t = datetime.datetime.strptime(p[3], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()
            if p[1] == 'taken':
                taken[p[2]] = t
            elif p[2] in taken and p[2].startswith('f27_'):
                out.append((taken.pop(p[2]), t + SLACK_S))
    for tag, t in taken.items():   # a window without its release line: open to now
        if tag.startswith('f27_'):
            out.append((t, datetime.datetime.now(datetime.timezone.utc).timestamp()))
    return out


def inside(mtime_ns, wins):
    t = int(mtime_ns) / 1e9
    return any(a <= t <= b for a, b in wins)


def ret(root, lock_log, nv):
    base = dict((k, (int(v[0]), int(v[1]))) for k, v in read_tsv(os.path.join(root, 'drv_base.tsv')).items())
    cp = read_tsv(os.path.join(root, 'drv_copy.tsv'))
    wins = windows(lock_log)
    live = walk(nv)
    n = dict(restored=0, moved=0, kept_user=0, kept_new=0, not_copied=0, failed=0)
    rows = []
    for k, v in sorted(base.items()):
        lv = live.get(k)
        if lv == v:
            continue
        if k not in cp:
            n['not_copied'] += 1
            rows.append('NOT_COPIED %s/%s' % k)
            continue
        if lv is None or inside(lv[1], wins):
            src = os.path.join(root, 'drv_copy', k[0], k[1])
            dst = os.path.join(nv, k[0], k[1])
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                ok = sha_file(dst) == cp[k][1]
            except OSError:
                ok = False
            n['restored' if ok else 'failed'] += 1
            rows.append('%s %s/%s' % ('RESTORED' if ok else 'FAILED', k[0], k[1]))
        else:
            n['kept_user'] += 1
            rows.append('KEPT_USER %s/%s' % k)
    for k, v in sorted(live.items()):
        if k in base:
            continue
        ours = (k[0] == 'GLCache' or k[1].startswith(EMU_GROUP)) and inside(v[1], wins)
        if ours:
            dst = os.path.join(root, 'drv_moved', k[0], k[1])
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(os.path.join(nv, k[0], k[1]), dst)
                n['moved'] += 1
                rows.append('MOVED %s/%s' % k)
            except OSError:
                n['failed'] += 1
                rows.append('FAILED_MOVE %s/%s' % k)
        else:
            n['kept_new'] += 1
            rows.append('KEPT_NEW %s/%s' % k)
    with open(os.path.join(root, 'drv_return.txt'), 'w', encoding='ascii') as f:
        f.write('windows %d\n' % len(wins))
        for r in rows:
            f.write(asc(r) + '\n')
    print('DRVSNAP RETURNED restored %d moved %d kept_user %d kept_new %d not_copied %d failed %d windows %d' % (
        n['restored'], n['moved'], n['kept_user'], n['kept_new'], n['not_copied'], n['failed'], len(wins)))
    return 0 if n['not_copied'] + n['failed'] == 0 else 1


def main(argv):
    nv = NV
    if '--nv' in argv:
        i = argv.index('--nv')
        nv = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) == 2 and argv[0] == 'take':
        return take(argv[1], nv)
    if len(argv) == 3 and argv[0] == 'return':
        return ret(argv[1], argv[2], nv)
    print(__doc__.split('\n')[0])
    return 9


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
