# F32a (HPP-733, ROADMAP p.672(b)(2)): delta sweep of logs modified after 2026-10-01 00:00Z by the F0 method.
# The F0 scanner (docs/track-f/f0/sweep_f0.py: KEY, SKIP_PREFIX, norm(), scan_segment()) is imported unchanged; only its
# output folder, the lock gate (exit instead of sleep, general rule 27) and the opener for .xz are replaced.
# Usage:
#   python sweep_f32a.py list                 -> OUT/loglist_f32a.tsv
#   python sweep_f32a.py run <budget_s> [workers]   (resumable; prints SWEEP COMPLETE)
#   python sweep_f32a.py agg                  -> OUT/agg_f32a.json, OUT/sig_f32a.tsv, OUT/new_f32a.tsv
# Read-only on logs, binary mode, chunked. Exit 3 on C:/kyty/SEALED_RUN.lock, exit 4 on C:/kyty/f287/STOP.
import os, re, sys, time, json, pickle, hashlib, calendar, collections, multiprocessing, importlib.util, lzma, builtins

HERE = os.path.dirname(os.path.abspath(__file__))
F0_PATH = os.environ.get('F32A_F0', 'C:/kyty/KytyPS5/docs/track-f/f0/sweep_f0.py')
OUT = os.environ.get('F32A_OUT', 'C:/kyty/f287/f32a')
ROOT = os.environ.get('F32A_ROOT', 'C:/kyty')
F0_SIGS = os.environ.get('F32A_F0_SIGS', 'C:/kyty/f287/f0/logsigs_f0.pkl')
F0_AGG = os.environ.get('F32A_F0_AGG', 'C:/kyty/f287/f0/agg_f0.json')
MANIFEST = os.environ.get('F32A_MANIFEST', 'C:/kyty/_cleanup401/manifest.tsv')
LOCK = os.environ.get('F32A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F32A_STOP', 'C:/kyty/f287/STOP')
T0 = calendar.timegm((2026, 10, 1, 0, 0, 0))
SEG = OUT + '/seg'
TAB = chr(9)
NLc = chr(10)
BS = chr(92)
NAME = re.compile(r'^(log_.*\.txt|_kyty.*\.txt)(\.xz)?$')
RE_BUILD = re.compile(rb'Fork build \S+ ([0-9a-f]{7,40})')
RE_GITREV = re.compile(rb'KytyPS5-\d{4}-\d\d-\d\d-[0-9a-f]+-\d+-g([0-9a-f]{7,40})')


def load_f0():
    spec = importlib.util.spec_from_file_location('sweep_f0', F0_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


F0 = load_f0()
FIX = F0.FIX
SEG_BYTES = int(os.environ.get('F32A_SEG_BYTES', F0.SEG_BYTES))


def gate():
    if os.path.exists(STOP):
        os._exit(4)
    if os.path.exists(LOCK):
        os._exit(3)


def xopen(path, mode='r', *a, **k):
    if path.endswith('.xz') and 'r' in mode and 'b' in mode:
        return lzma.open(path, 'rb')
    return builtins.open(path, mode, *a, **k)


F0.SEG = SEG
F0.wait_gate = gate
F0.open = xopen


def walk_logs(root):
    rows = []
    for d, dirs, files in os.walk(root):
        r = d.replace(BS, '/')
        if '/.git' in r or r.startswith(root + '/build'):
            dirs[:] = []
            continue
        for f in files:
            if NAME.match(f):
                p = r + '/' + f
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                rows.append((p, st.st_size, int(st.st_mtime)))
    return rows


def manifest():
    m = {}
    if os.path.exists(MANIFEST):
        for l in open(MANIFEST, encoding='utf-8'):
            x = l.rstrip(NLc).split(TAB)
            if len(x) >= 3:
                m[x[0]] = (int(x[1]), x[2])
    return m


def f0_shas():
    s = {}
    if os.path.exists(F0_AGG):
        for r in json.load(open(F0_AGG, encoding='utf-8')):
            if r.get('sha256'):
                s[r['sha256']] = r['path']
    return s


def classify(rows, man, f0sha):
    # -> (path, size, mtime, kind, orig_size, status, note); status SWEEP | F0_SAME | FIXTURE | EMPTY
    out = []
    for p, s, mt in rows:
        if mt <= T0:
            continue
        kind = 'xz' if p.endswith('.xz') else 'txt'
        if FIX.search(p):
            out.append((p, s, mt, kind, s, 'FIXTURE', 'F0 rule FIX'))
            continue
        if s == 0:
            out.append((p, s, mt, kind, 0, 'EMPTY', ''))
            continue
        if kind == 'xz':
            orig = p[:-3]
            mm = man.get(orig)
            if mm is None:
                out.append((p, s, mt, kind, 0, 'SWEEP', 'xz not in manifest'))
            elif mm[1] in f0sha:
                out.append((p, s, mt, kind, mm[0], 'F0_SAME', 'manifest sha256 ' + mm[1][:16] + ' = F0 ' + f0sha[mm[1]]))
            else:
                out.append((p, s, mt, kind, mm[0], 'SWEEP', 'manifest sha256 ' + mm[1][:16] + ' not in F0'))
        else:
            out.append((p, s, mt, kind, s, 'SWEEP', ''))
    out.sort()
    return out


def cmd_list():
    gate()
    os.makedirs(OUT, exist_ok=True)
    rows = classify(walk_logs(ROOT), manifest(), f0_shas())
    with open(OUT + '/loglist_f32a.tsv', 'w', encoding='utf-8', newline=NLc) as o:
        for r in rows:
            o.write(TAB.join(str(x) for x in r) + NLc)
    c = collections.Counter((r[3], r[5]) for r in rows)
    for k in sorted(c):
        print('list', k[0], k[1], c[k])
    print('list total', len(rows))


def read_list():
    rows = []
    for l in open(OUT + '/loglist_f32a.tsv', encoding='utf-8'):
        x = l.rstrip(NLc).split(TAB)
        rows.append((x[0], int(x[1]), int(x[2]), x[3], int(x[4]), x[5], x[6] if len(x) > 6 else ''))
    return rows


def tasks():
    ts = []
    for p, s, mt, kind, osz, st, note in read_list():
        if st != 'SWEEP':
            continue
        md = hashlib.md5(p.encode('utf-8')).hexdigest()
        if kind == 'xz' or osz <= SEG_BYTES:
            end = osz if osz > 0 else (1 << 62)
            ts.append((p, 0, 0, end, osz, True, md))
        else:
            ts.append((p, -1, 0, 0, osz, False, md))
            n = (osz + SEG_BYTES - 1) // SEG_BYTES
            for i in range(n):
                ts.append((p, i, i * SEG_BYTES, min(osz, (i + 1) * SEG_BYTES), osz, False, md))
    return ts


def work(task):
    gate()
    return F0.work(task)


def cmd_run(budget, workers):
    gate()
    os.makedirs(SEG, exist_ok=True)
    ts = tasks()
    todo = []
    for t in ts:
        out = '%s/%s_%s.pkl' % (SEG, t[6], 'sha' if t[1] == -1 else str(t[1]))
        if not os.path.exists(out):
            todo.append(t[:6])
    # largest first: the long tail is one big file per worker
    todo.sort(key=lambda t: -(t[3] - t[2] if not t[5] else t[4]))
    print('tasks total', len(ts), 'todo', len(todo))
    if not todo:
        print('SWEEP COMPLETE')
        return
    t0 = time.time()
    done = 0
    pool = multiprocessing.Pool(workers)
    it = pool.imap_unordered(work, todo, chunksize=1)
    try:
        while True:
            left = budget - (time.time() - t0)
            if left <= 0:
                break
            try:
                it.next(timeout=left)
            except multiprocessing.TimeoutError:
                break
            except StopIteration:
                break
            done += 1
    finally:
        pool.terminate()
        pool.join()
    print('done this run', done, 'of', len(todo), 'wall %.0f s' % (time.time() - t0), 'lock_now', os.path.exists(LOCK))
    if done == len(todo):
        print('SWEEP COMPLETE')


def head_build(p, kind):
    # binary of the log: 'Fork build <owner>/<repo> <hash>' (only the hash is kept) or the KytyPS5 version string
    gate()
    fh = lzma.open(p, 'rb') if kind == 'xz' else builtins.open(p, 'rb')
    try:
        b = fh.read(8 << 20)
    finally:
        fh.close()
    m = RE_BUILD.search(b)
    if m:
        return m.group(1).decode()[:8]
    m = RE_GITREV.search(b)
    if m:
        return m.group(1).decode()[:8]
    return '?'


def group_of(p):
    q = p[len(ROOT) + 1:] if p.startswith(ROOT + '/') else p
    parts = q.split('/')
    return '/'.join(parts[:2]) if len(parts) > 2 else (parts[0] if len(parts) > 1 else '.')


def cmd_agg():
    gate()
    base = set()
    if os.path.exists(F0_SIGS):
        for p, sg in pickle.load(builtins.open(F0_SIGS, 'rb')).items():
            base.update(sg.keys())
    print('F0 baseline signatures', len(base))
    recs = []
    sigtab = {}
    seen = {}
    missing = 0
    f0sha = f0_shas()
    files = [r for r in read_list() if r[5] == 'SWEEP']
    files.sort(key=lambda x: (x[0].startswith(ROOT + '/KytyPS5/'), x[0]))
    for p, s, mt, kind, osz, st, note in files:
        md = hashlib.md5(p.encode('utf-8')).hexdigest()
        whole = kind == 'xz' or osz <= SEG_BYTES
        nseg = 1 if whole else (osz + SEG_BYTES - 1) // SEG_BYTES
        sigs = {}
        levels = []
        off = 0
        sha = None
        ok = True
        for i in range(nseg):
            fn = '%s/%s_%d.pkl' % (SEG, md, i)
            if not os.path.exists(fn):
                ok = False
                break
            r = pickle.load(builtins.open(fn, 'rb'))
            for k, v in r['sigs'].items():
                e = sigs.get(k)
                if e is None:
                    sigs[k] = [v[0], v[1] + off, v[2]]
                else:
                    e[0] += v[0]
            for x in r['events']:
                if x[0] == 'L' and x[2] not in levels:
                    levels.append(x[2])
            off += r['lines']
            if r['sha256']:
                sha = r['sha256']
        if ok and not whole:
            fn = '%s/%s_sha.pkl' % (SEG, md)
            if os.path.exists(fn):
                sha = pickle.load(builtins.open(fn, 'rb'))['sha256']
            else:
                ok = False
        if not ok:
            missing += 1
            continue
        dup = sha in seen
        if not dup:
            seen[sha] = p
        build = head_build(p, kind)
        rec = {'path': p, 'kind': kind, 'size': osz, 'mtime': mt, 'sha256': sha, 'dup_of': seen[sha] if dup else None,
               'in_f0': f0sha.get(sha), 'lines': off, 'build': build, 'levels': levels, 'group': group_of(p), 'nsig': len(sigs)}
        recs.append(rec)
        if dup or rec['in_f0']:
            continue
        for k, v in sigs.items():
            t = sigtab.get(k)
            if t is None:
                t = sigtab[k] = {'logs': 0, 'lines': 0, 'builds': collections.Counter(), 'levels': collections.Counter(),
                                 'groups': collections.Counter(), 'ex': None}
            t['logs'] += 1
            t['lines'] += v[0]
            t['builds'][build] += 1
            for lv in levels[:3]:
                t['levels'][lv] += 1
            t['groups'][rec['group']] += 1
            if t['ex'] is None:
                t['ex'] = (p, v[1], sha, v[2])
    uniq = [r for r in recs if not r['dup_of'] and not r['in_f0']]
    print('records', len(recs), 'unique new', len(uniq), 'dups', sum(1 for r in recs if r['dup_of']),
          'same as F0 log', sum(1 for r in recs if r['in_f0'] and not r['dup_of']), 'missing', missing)
    print('bytes', sum(r['size'] for r in uniq), 'lines', sum(r['lines'] for r in uniq))
    with builtins.open(OUT + '/agg_f32a.json', 'w', encoding='utf-8', newline=NLc) as o:
        json.dump(recs, o, ensure_ascii=False, indent=0)

    def row(k, t):
        ex = t['ex']
        b = ', '.join('%s %d' % x for x in t['builds'].most_common(6))
        lv = ', '.join('%s %d' % x for x in t['levels'].most_common(4))
        gr = ', '.join('%s %d' % x for x in t['groups'].most_common(4))
        return TAB.join([str(t['logs']), str(t['lines']), 'NEW' if k not in base else 'F0', b, lv, gr,
                         '%s:%d' % (ex[0], ex[1]), ex[2][:16],
                         k.decode('latin1').replace(TAB, ' '), ex[3].decode('utf-8', 'replace').replace(TAB, ' ')[:300]])
    hdr = TAB.join(['logs', 'lines', 'base', 'builds', 'levels', 'groups', 'example_path:line', 'sha256', 'signature', 'example_text'])
    items = sorted(sigtab.items(), key=lambda kv: (-kv[1]['logs'], kv[0]))
    with builtins.open(OUT + '/sig_f32a.tsv', 'w', encoding='utf-8', newline=NLc) as o:
        o.write(hdr + NLc)
        for k, t in items:
            o.write(row(k, t) + NLc)
    nnew = 0
    with builtins.open(OUT + '/new_f32a.tsv', 'w', encoding='utf-8', newline=NLc) as o:
        o.write(hdr + NLc)
        for k, t in items:
            if k not in base:
                o.write(row(k, t) + NLc)
                nnew += 1
    print('signatures', len(sigtab), 'new vs F0', nnew, 'missing logs', missing)


if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else ''
    if c == 'list':
        cmd_list()
    elif c == 'run':
        cmd_run(float(sys.argv[2]) if len(sys.argv) > 2 else 480, int(sys.argv[3]) if len(sys.argv) > 3 else 16)
    elif c == 'agg':
        cmd_agg()
    else:
        print(__doc__ or 'usage: list | run <budget> [workers] | agg')
        sys.exit(2)
