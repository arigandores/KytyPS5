# F16a (HPP-518, ROADMAP s122 item 412(zh)): block sweep of the game logs of sessions 142-146 and of the tracks for
# F7 (ENOENT paths of KernelStat / KernelOpen) and for the log lines of F7 / F5 (alignment warning, 'cannot be used as
# texture', the six ignored GPU states).  Form of docs/track-f/f15a/sweep2_f15a.py: files are read in 64 MiB blocks,
# only whole lines are processed, a 4 KiB tail is carried to the next block; '.xz' goes through 'xz -dc'.
# Per log one JSON line in <out.jsonl>:
#   stat_total / nf_total      'KernelStat: <path>' lines / 'file not found' lines (fileSystem.cpp:1099)
#   stat{path:[n_stat,n_nf,first_line,n_adj]}  only ENOENT paths.  ENOENT of a path on /app0 or /hostapp = the path is
#                              absent from the package index (file or directory, case-insensitive; fileSystem.cpp:
#                              1093-1100); of another mount = 'file not found' on the NEXT line.  first_line - the line
#                              of the first such 'KernelStat:'; n_adj - events with 'file not found' on the next line
#                              (lines of other threads may come between the two LOGF calls)
#   app_stat / app_miss        KernelStat events on app mounts / of them absent from the package; identity of a log:
#                              app_miss + (ENOENT of other mounts) == nf_total; miss_noadj - absent, the next line is
#                              not 'file not found'; adj_inpkg - present in the package, yet 'file not found' follows
#   nf_unattr, nf_unattr_s     'file not found' lines whose previous line is not a KernelStat line (+ samples)
#   next{family:{kind:n}}      the next guest FS call in the log (KernelStat or KernelOpen request) after an ENOENT
#                              stat; family = path with digit runs replaced by '#'; next_s - one sample per kind
#   open_total, open_un{path|flags:[n_req,n_ok,first_line]}   KernelOpen requests ('path = ' + 'flags = ') without a
#                              matching 'Open: <real>' line of the same relative path (KernelOpen prints nothing on
#                              ENOENT, fileSystem.cpp:474-478); open_fail - '[fail]' lines
#   msg{name:count}, txt{name:[distinct line texts, cap 64]}   the F7 / F5 messages
#   hdr_stat                   '::KernelStat()' header lines (thread ids exist only under KYTY_PRINT_NAMES)
# Fixture directories are excluded ('/fx/', '/fx_', '/work_', '/mut', '/test_', '/fixt').
# Resumable: paths already in <out.jsonl> are skipped; stops between files after <budget_s> seconds of wall time and
# when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.  Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep_f16a.py <out.jsonl> <budget_s>
import hashlib, json, os, re, subprocess, sys, time

out = sys.argv[1]
budget = float(sys.argv[2])
roots = ['C:/kyty/s142', 'C:/kyty/s143', 'C:/kyty/s144', 'C:/kyty/s145', 'C:/kyty/s146', 'C:/kyty/f287', 'C:/kyty/p283',
         'C:/kyty/s288']
fx = re.compile(r'/(fx/|fx_|work_|mut|test_|fixt)')
files = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        dn[:] = [x for x in dn if x not in ('.git', 'build', 'wt', '_ShaderCache', '_Shaders', 'node_modules', '__pycache__')]
        d = dp.replace(os.sep, '/')
        for f in fn:
            ok = (f.startswith('log_') and (f.endswith('.txt') or f.endswith('.txt.xz'))) or (f.startswith('_kyty') and f.endswith('.txt'))
            if not ok:
                continue
            p = d + '/' + f
            if fx.search(p):
                continue
            files.append((p, os.path.getsize(p)))
files.sort()

done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{'):
            done.add(json.loads(l)['path'])
left = [(p, s) for p, s in files if p not in done]
print('files', len(files), 'done before', len(done), 'left', len(left), 'left GiB %.1f' % (sum(s for _, s in left) / 2.0 ** 30))

PKG = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app'
pkg = set()
for dp, dn, fn in os.walk(PKG):
    d = dp.replace(os.sep, '/')[len(PKG):].strip('/').lower()
    for x in list(dn) + list(fn):
        pkg.add((d + '/' + x.lower()).strip('/'))
pkg.add('')
print('package entries', len(pkg))


def app_rel(p):
    # the package-relative lower-case path of an /app0 or /hostapp guest path, None for other mounts
    q = p.replace(chr(92), '/')
    for m in ('/app0', '/hostapp'):
        if q == m or q.startswith(m + '/'):
            parts = [x for x in q[len(m):].split('/') if x not in ('', '.')]
            return '/'.join(parts).lower()
    return None


def fam_of(p):
    q = p.split('/', 2)
    if len(q) == 3 and q[0] == '':
        return '/' + q[1] + '/' + DIG.sub('#', q[2])
    return DIG.sub('#', p)


NL = b'\n'
A = b'\t KernelStat: '
B = b'\t path = '
FL = b'\t flags = '
C = b'\tOpen'
D = b'\t file not found'
VER = re.compile(rb'(?m)^\s*version:\s*([^\r\n]+)')
DIG = re.compile(r'\d+')
BLOCK = 64 << 20
OVER = 4096
COUNT_MSGS = {
    'align_size': b'size_bytes is not 256-byte aligned',
    'align_base': b'base is not 256-byte aligned',
    'round_mode': b'ignoring PS5 color round mode',
    'ds_unbound': b'without a bound attachment',
    'hdr_stat': b'::KernelStat()',
    'open_fail': b', [fail]',
}
TEXT_MSGS = {
    'no_texture': b'cannot be used as texture',
    'color_meta': b'ignoring PS5 color metadata',
    'meta_addr': b'ignoring PS5 metadata addresses',
    'stereo': b'GE_STEREO_CNTL',
    'zero_disp': b'skipping zero-sized dispatch',
}
TXT_CAP = 64


def positions(buf, pat, limit):
    res = []
    i = buf.find(pat)
    while i != -1 and i < limit:
        res.append(i)
        i = buf.find(pat, i + 1)
    return res


def line_at(buf, i):
    a = buf.rfind(NL, 0, i) + 1
    b = buf.find(NL, i)
    if b == -1:
        b = len(buf)
    return buf[a:b].rstrip(b'\r')


def dec(b):
    return b.decode('utf-8', 'replace')


def stem(p):
    b = p.rsplit('/', 1)[-1]
    return b.rsplit('.', 1)[0] if '.' in b else b


def rel_of(p):
    # the path below the mount point: '/app0/a/b' -> 'a/b'
    q = p.strip('/').split('/', 1)
    return q[1].lower() if len(q) == 2 else ''


def scan(p):
    if p.endswith('.xz'):
        proc = subprocess.Popen(['xz', '-dc', p], stdout=subprocess.PIPE)
        src = proc.stdout
    else:
        proc = None
        src = open(p, 'rb')
    sha = hashlib.sha256()
    build = ''
    first = True
    nbytes = 0
    base_line = 0
    buf = b''
    stat_total = nf_total = open_total = 0
    stat = {}            # path -> [n_stat, n_nf, first_nf_line]
    all_stat = {}        # path -> n (to fill n_stat of ENOENT paths)
    nf_unattr = 0
    nf_unattr_s = []
    nxt = {}             # family -> {kind: n}
    nxt_s = {}           # 'family|kind' -> sample
    pending = None       # the last ENOENT stat path waiting for the next guest FS call
    app_stat = app_miss = miss_noadj = adj_inpkg = 0
    adj_inpkg_s = []
    req = {}             # (path, flags) -> [n, first_line]
    oks = {}             # lower real name -> n
    msg = dict((k, 0) for k in COUNT_MSGS)
    txt = dict((k, {}) for k in TEXT_MSGS)
    while True:
        data = src.read(BLOCK)
        eof = not data
        if data:
            sha.update(data)
            nbytes += len(data)
        buf += data
        if first:
            m = VER.search(buf[:65536])
            if m:
                build = dec(m.group(1)).strip()
            first = False
        if eof:
            limit = len(buf)
        else:
            limit = buf.rfind(NL, 0, max(0, len(buf) - OVER)) + 1
        ev = []
        for i in positions(buf, A, limit):
            if i == 0 or buf[i - 1:i] == NL:
                ev.append((i, 0))
        for i in positions(buf, B, limit):
            if i == 0 or buf[i - 1:i] == NL:
                ev.append((i, 1))
        for i in positions(buf, C, limit):
            if i == 0 or buf[i - 1:i] == NL:
                ev.append((i, 2))
        dpos = [i for i in positions(buf, D, limit) if i == 0 or buf[i - 1:i] == NL]
        nf_total += len(dpos)
        attributed = set()
        ev.sort()
        last_pos = 0
        line = base_line + 1
        for i, kind in ev:
            line += buf.count(NL, last_pos, i)
            last_pos = i
            eol = buf.find(NL, i)
            if eol == -1:
                eol = len(buf)
            if kind == 0:
                path = dec(buf[i + len(A):eol].rstrip(b'\r'))
                stat_total += 1
                all_stat[path] = all_stat.get(path, 0) + 1
                if pending is not None:
                    pp = pending
                    if path == pp:
                        k = 'stat_same'
                    elif fam_of(path) == fam_of(pp):
                        k = 'stat_family'
                    elif stem(path) == stem(pp):
                        k = 'stat_samestem'
                    else:
                        k = 'stat_other'
                    fam = fam_of(pp)
                    d = nxt.setdefault(fam, {})
                    d[k] = d.get(k, 0) + 1
                    nxt_s.setdefault(fam + '|' + k, '%s -> KernelStat %s (line %d)' % (pp, path, line))
                    pending = None
                adj = buf.startswith(D, eol + 1)
                if adj:
                    attributed.add(eol + 1)
                ar = app_rel(path)
                miss = (ar not in pkg) if ar is not None else adj
                if ar is not None:
                    app_stat += 1
                    if miss:
                        app_miss += 1
                        if not adj:
                            miss_noadj += 1
                    elif adj:
                        adj_inpkg += 1
                        if len(adj_inpkg_s) < 8:
                            adj_inpkg_s.append('line %d %s' % (line, path))
                if miss:
                    e = stat.get(path)
                    if e is None:
                        stat[path] = [0, 1, line, 1 if adj else 0]
                    else:
                        e[1] += 1
                        e[3] += 1 if adj else 0
                    pending = path
            elif kind == 1:
                if not buf.startswith(FL, eol + 1):
                    continue
                path = dec(buf[i + len(B):eol].rstrip(b'\r'))
                flags = dec(buf[eol + 1 + len(FL):eol + 1 + len(FL) + 8])
                open_total += 1
                e = req.get((path, flags))
                if e is None:
                    req[(path, flags)] = [1, line]
                else:
                    e[0] += 1
                if pending is not None:
                    pp = pending
                    if path == pp:
                        k = 'open_same'
                    elif stem(path) == stem(pp):
                        k = 'open_samestem'
                    else:
                        k = 'open_other'
                    fam = fam_of(pp)
                    d = nxt.setdefault(fam, {})
                    d[k] = d.get(k, 0) + 1
                    nxt_s.setdefault(fam + '|' + k, '%s -> KernelOpen %s flags %s (line %d)' % (pp, path, flags, line))
                    pending = None
            else:
                t = buf[i + len(C):eol].rstrip(b'\r')
                if t.startswith(b': '):
                    t = t[2:]
                elif t.startswith(b' dir: '):
                    t = t[6:]
                elif t.startswith(b' device: '):
                    t = t[9:]
                else:
                    continue
                j = t.find(b', entries = ')
                if j == -1:
                    j = t.rfind(b', [')
                if j == -1:
                    continue
                if t.endswith(b'[fail]'):
                    continue
                r = dec(t[:j]).replace(chr(92), '/').lower()
                oks[r] = oks.get(r, 0) + 1
        for i in dpos:
            if i not in attributed:
                nf_unattr += 1
                if len(nf_unattr_s) < 8:
                    a = buf.rfind(NL, 0, max(0, i - 1)) + 1
                    nf_unattr_s.append('line %d prev: %s' % (base_line + buf.count(NL, 0, i) + 1, dec(buf[a:i].rstrip(b'\r\n'))[:160]))
        for k, pat in COUNT_MSGS.items():
            msg[k] += buf.count(pat, 0, limit)
        for k, pat in TEXT_MSGS.items():
            d = txt[k]
            for i in positions(buf, pat, limit):
                t = dec(line_at(buf, i)).strip()[:300]
                e = d.get(t)
                if e is not None:
                    e[0] += 1
                elif len(d) < TXT_CAP:
                    d[t] = [1, base_line + buf.count(NL, 0, i) + 1]
                else:
                    d['<over cap>'] = [d.get('<over cap>', [0, 0])[0] + 1, 0]
        if eof:
            base_line += buf.count(NL)
            break
        base_line += buf.count(NL, 0, limit)
        buf = buf[limit:]
    src.close()
    if proc:
        proc.wait()
    if pending is not None:
        fam = fam_of(pending)
        d = nxt.setdefault(fam, {})
        d['none'] = d.get('none', 0) + 1
    for path, e in stat.items():
        e[0] = all_stat.get(path, 0)
    # KernelOpen requests without a matching 'Open' line: by the relative path below the mount point
    by_base = {}
    for r, n in oks.items():
        by_base.setdefault(r.rsplit('/', 1)[-1], []).append((r, n))
    by_rel = {}
    for (path, flags), (n, ln) in req.items():
        by_rel.setdefault(rel_of(path) or path.lower(), []).append((path, flags, n, ln))
    open_un = {}
    for rel, lst in by_rel.items():
        n_req = sum(x[2] for x in lst)
        base = rel.rsplit('/', 1)[-1]
        n_ok = 0
        for r, n in by_base.get(base, ()):
            if r == rel or r.endswith('/' + rel) or any(r == x[0].lower() for x in lst):
                n_ok += n
        if n_ok < n_req:
            for path, flags, n, ln in lst:
                open_un[path + '|' + flags] = [n, n_ok, ln]
    return {
        'path': p, 'bytes': nbytes, 'sha256': sha.hexdigest(), 'build': build, 'lines': base_line,
        'stat_total': stat_total, 'nf_total': nf_total, 'stat': stat, 'app_stat': app_stat, 'app_miss': app_miss,
        'miss_noadj': miss_noadj, 'adj_inpkg': adj_inpkg, 'adj_inpkg_s': adj_inpkg_s, 'nf_unattr': nf_unattr, 'nf_unattr_s': nf_unattr_s,
        'next': nxt, 'next_s': nxt_s, 'open_total': open_total, 'open_un': open_un,
        'msg': msg, 'txt': txt,
    }


t0 = time.time()
n_done = 0
with open(out, 'a', encoding='utf-8', newline='\n') as o:
    for p, s in left:
        if time.time() - t0 > budget:
            print('BUDGET stop, left', len(left) - n_done)
            break
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            print('HALT before', p)
            break
        o.write(json.dumps(scan(p), ensure_ascii=True, sort_keys=True) + '\n')
        o.flush()
        n_done += 1
    else:
        print('SWEEP COMPLETE')
print('this call files', n_done, 'wall %.1f s' % (time.time() - t0))
