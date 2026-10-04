# F22a (HPP-576, ROADMAP s122 item 474(e)(3)): sweep of the game logs for the markers of the paths that write file or
# device data into guest memory.  Form of f21a/sweep_f21a.py: 64 MiB blocks (F22A_BLOCK), only whole lines, the
# unfinished tail is carried; '.xz' goes through 'xz -dc'.  One JSON line per log in <out.jsonl>.  Measurement only:
# reads logs and the stdout files of the same tag, writes <out.jsonl>.
# Print sites (KytyPS5 f70a2232 = 58b6c5ad for these files):
#   src/kernel/fileSystem.cpp:770 LOGF 'KernelRead: direct read failed, dst=0x<16 hex> size=0x<hex>: reading through a
#     host buffer' - the fallback of ReadGuestWithRetry, both KernelRead and KernelPread; at most 32 lines per process
#     (:768-:769, 'static int logged', process-wide)
#   :857 '<TAB>Read <n> bytes from: <path>' (KernelRead, file), :1007 '<TAB>Read <n> bytes (pos = <off>) from: <path>'
#     (KernelPread; AIO reads and Posix::pread go through it), :812 '<TAB>Read <n> directory bytes from:', :820 / :971
#     '<TAB>Read <n> random bytes'
#   src/common/platform/sysWindowsFileIO.cpp:71 printf 'SysFileRead: ReadFile failed, error=<e> size=<n> data=<p>' -
#     to the process stdout (stdout_<tag>.txt), at most 32 lines per process; any host ReadFile through Common::File
#   src/libs/network.cpp:2004 LOGF block of Recvfrom ('<TAB> s     = ', ..., '<TAB> addr  = 0x<16 hex>',
#     '<TAB> addrlen = 0x<16 hex>') - Recv, recv, recvfrom and KernelRead/read of a socket; Sendto :1955 has the same
#     block with a decimal addrlen
#   src/libs/libAmpr.cpp:1362/:1373/:1466 '<TAB>APR submit failed for unknown file id' / 'APR submit read failed' /
#     'APR read missing host file' (APR reads go through a host buffer and memcpy, :1485-:1496)
#   src/libs/libs.h:58 PRINT_NAME '[<tid>][HH:MM:SS.FFF] <lib>::<module>::<func>()' - only with KYTY_PRINT_NAMES (or
#     PRINT_NAME_ENABLED / a forced thread)
# Fields (counts are lines; 'line' is 1-based):
#   size_now, lines; levels[] (name, line) at most 64 (levels_over)
#   drf_n; drf[] (line, dst, size, level, next_read: [form, n] of the first '<TAB>Read ' line after it in the same block
#     or null); drf_bad (lines with the text but not the form; invariant 0)
#   rd_file / rd_file0 (KernelRead lines / with n == 0), rd_pos / rd_pos0 (KernelPread), rd_dir, rd_rand, rd_other
#   recv_n, recv_first, recv_levels {level: n}; send_n; addrlen_other (an addrlen line after another block)
#   apr {text before ':' : n}
#   pn_n (PRINT_NAME lines), pn_read {func: n} for names with read|recv|aio|apr|mmap|getdent|getdirent|submit (any
#     case; 'read' not after 'th' - Pthread*), pn_funcs (distinct functions)
#   stream_n ('StreamRead:' lines), torn_n ('TORN:' in them), sfr_log (stdout form inside the log), fatal
#   stdout[] per stdout file: path, size, lines, sfr_n, sfr_err {error: n}, sfr_size {size: n} (at most 50 keys)
# Identities (ana_f22a.py): drf_n == len(drf) + drf_bad; drf_n <= 32 per process (one process per log: invariant
#   drf_n <= 32); for each drf with next_read, the form is 'file' or 'pos'.
# Resumable: paths already in <out.jsonl> are skipped; stops between files after <budget_s> seconds and when
# C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.  Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep_f22a.py <list.tsv> <out.jsonl> <budget_s>   (list: path TAB size TAB class TAB bin TAB sha TAB stdouts)
import json, os, re, subprocess, sys, time

lst, out, budget = sys.argv[1], sys.argv[2], float(sys.argv[3])
LOCK = os.environ.get('F22A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F22A_STOP', 'C:/kyty/f287/STOP')
BLOCK = int(os.environ.get('F22A_BLOCK', str(64 << 20)))
t0 = time.time()
TAB = chr(9)
NL = bytes([10])
CR = bytes([13])
T = bytes([9])
files = []
for l in open(lst, encoding='utf-8'):
    l = l.rstrip(chr(10))
    if l:
        f = l.split(TAB)
        files.append(f)
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{') and l.rstrip().endswith('}'):
            done.add(json.loads(l)['path'])
left = [x for x in files if x[0] not in done]
print('files', len(files), 'done before', len(done), 'left', len(left))

DRF = re.compile(rb'KernelRead: direct read failed, dst=0x([0-9a-fA-F]+) size=0x([0-9a-fA-F]+): reading through a host buffer')
RD = re.compile(rb'Read (\d+) (bytes from: |bytes \(pos = |directory bytes|random bytes)')
LITS = ((1, b'KernelRead: direct read failed'), (2, b'Level has started:'), (3, T + b'Read '),
        (4, T + b' addrlen = '), (5, T + b'APR '), (6, T + b'AMPR '), (7, T + b'AMM '), (8, b'StreamRead:'),
        (9, b'SysFileRead: ReadFile failed'), (10, b'--- Fatal Error ---'), (11, b'()' + NL), (12, b'()' + CR + NL))
PN = re.compile(rb'\[\d+\]\[\d\d:\d\d:\d\d\.\d+\] ([^\s:]+)::([^\s:]+)::(\w+)\(\)')
READISH = re.compile(r'(?i)(?<!th)read|recv|aio|apr|mmap|getdent|getdirent|submit')  # not 'thread'
SFR = re.compile(rb'SysFileRead: ReadFile failed, error=(\d+) size=(\d+)')
USER = re.compile(rb'([Uu]sers.)[^/ ' + bytes([92, 92, 9]) + rb']+')


def dec(b):
    return USER.sub(rb'\1<user>', b).decode('utf-8', 'replace')


def blocks(path):
    proc = None
    if path.endswith('.xz'):
        proc = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE)
        f = proc.stdout
    else:
        f = open(path, 'rb')
    carry = b''
    while True:
        b = f.read(BLOCK)
        buf = carry + b
        if b:
            cut = buf.rfind(NL)
            if cut == -1:
                carry = buf
                continue
            carry = buf[cut + 1:]
            buf = buf[:cut + 1]
        else:
            carry = b''
            if buf and not buf.endswith(NL):
                buf += NL
        yield buf
        if not b:
            break
    if proc is None:
        f.close()
    else:
        proc.wait()
        yield proc.returncode


def sweep_stdout(path):
    rec = {'path': path, 'size': os.path.getsize(path), 'lines': 0, 'sfr_n': 0, 'sfr_err': {}, 'sfr_size': {}}
    for buf in blocks(path):
        if isinstance(buf, int):
            rec['xz_rc'] = buf
            continue
        rec['lines'] += buf.count(NL)
        for m in SFR.finditer(buf):
            rec['sfr_n'] += 1
            e = m.group(1).decode()
            rec['sfr_err'][e] = rec['sfr_err'].get(e, 0) + 1
            s = m.group(2).decode()
            if s in rec['sfr_size'] or len(rec['sfr_size']) < 50:
                rec['sfr_size'][s] = rec['sfr_size'].get(s, 0) + 1
    return rec


def sweep(row):
    path = row[0]
    rec = {'path': path, 'size_list': int(row[1]), 'cls': row[2], 'bin': row[3], 'sha256_f21a': row[4],
           'size_now': os.path.getsize(path), 'lines': 0, 'levels': [], 'levels_over': 0,
           'drf_n': 0, 'drf': [], 'drf_bad': 0, 'rd_file': 0, 'rd_file0': 0, 'rd_pos': 0, 'rd_pos0': 0, 'rd_dir': 0,
           'rd_rand': 0, 'rd_other': 0, 'recv_n': 0, 'recv_first': None, 'recv_levels': {}, 'send_n': 0,
           'addrlen_other': 0, 'apr': {}, 'pn_n': 0, 'pn_read': {}, 'pn_funcs': 0, 'stream_n': 0, 'torn_n': 0,
           'sfr_log': 0, 'fatal': 0, 'stdout': []}
    funcs = set()
    curname = ''
    for buf in blocks(path):
        if isinstance(buf, int):
            rec['xz_rc'] = buf
            continue
        base_line = rec['lines']
        ev = []
        for kind, lit in LITS:
            i = buf.find(lit)
            while i != -1:
                ls = buf.rfind(NL, 0, i) + 1
                le = buf.find(NL, i)
                ev.append((ls, kind, le))
                i = buf.find(lit, le)
        ev.sort()
        lc_pos, lc_n = 0, 0
        last_ls = -1
        for pos, kind, le in ev:
            if kind in (11, 12) and pos == last_ls:
                continue
            last_ls = pos
            lc_n += buf.count(NL, lc_pos, pos)
            lc_pos = pos
            line = base_line + lc_n + 1
            t = buf[pos:le].rstrip(CR)
            if kind == 1:
                rec['drf_n'] += 1
                m = DRF.search(t)
                if not m:
                    rec['drf_bad'] += 1
                    continue
                nxt = None
                j = buf.find(T + b'Read ', le)
                if j != -1:
                    mr = RD.match(buf, j + 1)
                    if mr:
                        form = {b'bytes from: ': 'file', b'bytes (pos = ': 'pos'}.get(mr.group(2), 'other')
                        nxt = [form, int(mr.group(1)), base_line + lc_n + 1 + buf.count(NL, pos, j)]
                rec['drf'].append({'line': line, 'dst': m.group(1).decode(), 'size': int(m.group(2), 16),
                                   'level': curname, 'next_read': nxt})
            elif kind == 2:
                name = dec(t.split(b'Level has started:', 1)[1].strip())[:80]
                if name:
                    curname = name
                    if len(rec['levels']) < 64:
                        rec['levels'].append({'level': name, 'line': line})
                    else:
                        rec['levels_over'] += 1
            elif kind == 3:
                mr = RD.search(t)
                if not mr or not t.startswith(T + b'Read '):
                    continue
                n = int(mr.group(1))
                g = mr.group(2)
                if g == b'bytes from: ':
                    rec['rd_file'] += 1
                    rec['rd_file0'] += n == 0
                elif g == b'bytes (pos = ':
                    rec['rd_pos'] += 1
                    rec['rd_pos0'] += n == 0
                elif g == b'directory bytes':
                    rec['rd_dir'] += 1
                elif g == b'random bytes':
                    rec['rd_rand'] += 1
                else:
                    rec['rd_other'] += 1
            elif kind == 4:
                prev_s = buf.rfind(NL, 0, max(pos - 1, 0)) + 1
                prev = buf[prev_s:pos].rstrip(CR + NL)
                is_hex = t[len(T + b' addrlen = '):].startswith(b'0x')
                if prev.startswith(T + b' addr  = 0x') and is_hex:
                    rec['recv_n'] += 1
                    rec['recv_levels'][curname] = rec['recv_levels'].get(curname, 0) + 1
                    if rec['recv_first'] is None:
                        rec['recv_first'] = line
                elif prev.startswith(T + b' addr  = 0x'):
                    rec['send_n'] += 1
                else:
                    rec['addrlen_other'] += 1
            elif kind in (5, 6, 7):
                k = dec(t.strip().split(b':', 1)[0])[:60]
                rec['apr'][k] = rec['apr'].get(k, 0) + 1
            elif kind == 8:
                rec['stream_n'] += 1
                rec['torn_n'] += b'TORN:' in t
            elif kind == 9:
                rec['sfr_log'] += 1
            elif kind == 10:
                rec['fatal'] += 1
            elif kind in (11, 12):
                m = PN.search(t)
                if not m:
                    continue
                rec['pn_n'] += 1
                fn = m.group(3).decode()
                funcs.add(fn)
                if READISH.search(fn):
                    rec['pn_read'][fn] = rec['pn_read'].get(fn, 0) + 1
        rec['lines'] += buf.count(NL)
    rec['pn_funcs'] = len(funcs)
    if row[5] != '-':
        for sp in row[5].split(';'):
            rec['stdout'].append(sweep_stdout(sp))
    return rec


n = 0
for row in left:
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('STOPPED: lock or STOP present')
        sys.exit(3)
    if time.time() - t0 > budget:
        break
    if not os.path.exists(row[0]):
        rec = {'path': row[0], 'missing': True}
    else:
        rec = sweep(row)
    with open(out, 'ab') as fo:
        fo.write((json.dumps(rec, ensure_ascii=True, sort_keys=True) + chr(10)).encode('ascii'))
    n += 1
print('swept now', n, 'wall %.1f s' % (time.time() - t0))
if n == len(left):
    print('SWEEP COMPLETE')
