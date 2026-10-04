# F16a (HPP-518): second block sweep - what the guest does after ENOENT (terminal outcome of the directory search).
# Only the logs kept by agg_f16a.py (one path per sha256 of sweep_f16a.jsonl).  Per log one JSON line:
#   odx_enoent_inpkg   resource stems (file name without '.odx'/'.odxb') with >= 1 ENOENT KernelStat in the log whose
#                      '.odx'/'.odxb' file exists somewhere in the package
#   odx_reached        of them: the log also has a KernelStat of an existing '.odx'/'.odxb' path of the stem, or a
#                      KernelOpen request of such a path (the search came to the file)
#   odx_unreached_s    the stems that were not reached (cap 40) - a search that ended before the existing file
#   odx_enoent_nopkg   stems with ENOENT and no '.odx'/'.odxb' file anywhere in the package
#   open_enoent{path:[n, {kind:n}]}  KernelOpen requests of an app-mount path absent from the package, flags without
#                      O_CREAT (fileSystem.cpp:474-478), and the next guest FS call in the log (open_same / stat_same =
#                      a retry of the same path; *_samestem; *_other; none)
#   empty{path:[n, [samples 'line N prev: <previous guest FS call> next: <next guest FS call>']]}  the two paths with
#                      an empty resource name ('/app0/.anim', '/app0/data/prein/save_data/.xml')
# Resumable, budget and halt as sweep_f16a.py.  Usage: python sweep2_f16a.py <out.jsonl> <budget_s>
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
out = sys.argv[1]
budget = float(sys.argv[2])
PKG = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app'
pkg = set([''])
odx_stems = set()
for dp, dn, fn in os.walk(PKG):
    d = dp.replace(os.sep, '/')[len(PKG):].strip('/').lower()
    for x in list(dn) + list(fn):
        xl = x.lower()
        pkg.add((d + '/' + xl).strip('/'))
        if xl.endswith('.odx') or xl.endswith('.odxb'):
            odx_stems.add(xl.rsplit('.', 1)[0])
seen = {}
for l in open(HERE + '/sweep_f16a.jsonl', encoding='utf-8'):
    if l.startswith('{'):
        d = json.loads(l)
        if d['sha256'] not in seen or d['path'] < seen[d['sha256']]:
            seen[d['sha256']] = d['path']
files = sorted(seen.values())
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{'):
            done.add(json.loads(l)['path'])
left = [p for p in files if p not in done]
print('files', len(files), 'done before', len(done), 'left', len(left))

NL = b'\n'
A = b'\t KernelStat: '
B = b'\t path = '
FL = b'\t flags = '
BLOCK = 64 << 20
OVER = 4096
EMPTY = ('/app0/.anim', '/app0/data/prein/save_data/.xml')


def positions(buf, pat, limit):
    res = []
    i = buf.find(pat)
    while i != -1 and i < limit:
        res.append(i)
        i = buf.find(pat, i + 1)
    return res


def app_rel(p):
    for m in ('/app0', '/hostapp'):
        if p == m or p.startswith(m + '/'):
            return '/'.join(x for x in p[len(m):].split('/') if x not in ('', '.')).lower()
    return None


def stem(p):
    b = p.rsplit('/', 1)[-1]
    return b.rsplit('.', 1)[0] if '.' in b else b


def odx_stem(p):
    b = p.rsplit('/', 1)[-1].lower()
    if b.endswith('.odx') or b.endswith('.odxb'):
        return b.rsplit('.', 1)[0]
    return None


def scan(p):
    if p.endswith('.xz'):
        proc = subprocess.Popen(['xz', '-dc', p], stdout=subprocess.PIPE)
        src = proc.stdout
    else:
        proc = None
        src = open(p, 'rb')
    base_line = 0
    buf = b''
    en_in, en_no, reached = set(), set(), set()
    open_en = {}
    empty = {}
    pend_open = None     # the last ENOENT open path waiting for the next guest FS call
    pend_empty = None    # (path, line, prev) waiting for the next guest FS call
    prev_call = ''
    while True:
        data = src.read(BLOCK)
        eof = not data
        buf += data
        limit = len(buf) if eof else buf.rfind(NL, 0, max(0, len(buf) - OVER)) + 1
        ev = [(i, 0) for i in positions(buf, A, limit) if i == 0 or buf[i - 1:i] == NL]
        ev += [(i, 1) for i in positions(buf, B, limit) if i == 0 or buf[i - 1:i] == NL]
        ev.sort()
        last_pos = 0
        line = base_line + 1
        for i, kind in ev:
            eol = buf.find(NL, i)
            if eol == -1:
                eol = len(buf)
            if kind == 1 and not buf.startswith(FL, eol + 1):
                continue
            line += buf.count(NL, last_pos, i)
            last_pos = i
            path = buf[i + (len(A) if kind == 0 else len(B)):eol].rstrip(b'\r').decode('utf-8', 'replace')
            what = ('KernelStat ' if kind == 0 else 'KernelOpen ') + path
            if pend_open is not None:
                pp = pend_open
                pre = 'stat_' if kind == 0 else 'open_'
                k = pre + ('same' if path == pp else ('samestem' if stem(path) == stem(pp) else 'other'))
                open_en[pp][1][k] = open_en[pp][1].get(k, 0) + 1
                pend_open = None
            if pend_empty is not None:
                e = empty[pend_empty[0]]
                if len(e[1]) < 6:
                    e[1].append('line %d prev: %s next: %s' % (pend_empty[1], pend_empty[2], what))
                pend_empty = None
            ar = app_rel(path)
            miss = ar is not None and ar not in pkg
            s = odx_stem(path)
            if s is not None:
                if miss:
                    if kind == 0:
                        (en_in if s in odx_stems else en_no).add(s)
                else:
                    reached.add(s)
            if kind == 1 and miss:
                flags = buf[eol + 1 + len(FL):eol + 1 + len(FL) + 8]
                try:
                    creat = (int(flags, 16) & 0x200) != 0
                except ValueError:
                    creat = False
                if not creat:
                    open_en.setdefault(path, [0, {}])[0] += 1
                    pend_open = path
            if path in EMPTY and miss:
                empty.setdefault(path, [0, []])[0] += 1
                pend_empty = (path, line, prev_call)
            prev_call = what
        if eof:
            break
        base_line += buf.count(NL, 0, limit)
        buf = buf[limit:]
    src.close()
    if proc:
        proc.wait()
    if pend_open is not None:
        open_en[pend_open][1]['none'] = open_en[pend_open][1].get('none', 0) + 1
    unreached = sorted(en_in - reached)
    return {'path': p, 'odx_enoent_inpkg': len(en_in), 'odx_reached': len(en_in & reached), 'odx_unreached': len(unreached),
            'odx_unreached_s': unreached[:40], 'odx_enoent_nopkg': len(en_no), 'open_enoent': open_en, 'empty': empty}


t0 = time.time()
n_done = 0
with open(out, 'a', encoding='utf-8', newline='\n') as o:
    for p in left:
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
