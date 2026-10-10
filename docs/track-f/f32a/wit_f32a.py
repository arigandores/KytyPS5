# F32a (HPP-733): witness pass over the unique delta logs (agg_f32a.json, dup_of == None) for the parked rows whose witness
# line is not caught by the F0 key list. Per log: CsPretranslate skipped hashes with reason class, regular-path miss/hit hashes
# (Take), 'shader CFG build failed' outside 'CsPretranslate:', socket blocks (network.cpp LOGF lines '<TAB> addrlen = ' and
# '<TAB> len   = <decimal>' - printed on every socket data/address call; PRINT_NAME headers are off by default), 'Read 0 bytes',
# 'Controller <id>: removed', VUID-...-06479, MainTaskLate >= 1 s, 'Event: quit', guest fatal markers.
# Usage: python wit_f32a.py run [workers] | python wit_f32a.py agg
# Exit 3 on C:/kyty/SEALED_RUN.lock, 4 on C:/kyty/f287/STOP (checked before every 8 MiB block); resumable (one json per log).
import os, re, sys, json, lzma, hashlib, collections, multiprocessing

OUT = os.environ.get('F32A_OUT', 'C:/kyty/f287/f32a')
WD = OUT + '/wit'
LOCK = os.environ.get('F32A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F32A_STOP', 'C:/kyty/f287/STOP')
BLOCK = 8 << 20
NL = bytes([10])
KEY = re.compile(rb'CsPretranslate: (?:skipped|miss|hit) hash=|shader CFG build failed|Recvfrom|Sendto|Read 0 bytes|'
                 rb'Controller -?\d+: removed|VUID-[^ ]*06479|MainTaskLate: us=|^	 addrlen = |^	 len   = \d|^Event: quit|--- Fatal Error ---|Unhandled exception|'
                 rb'Unhandled host exception', re.M)
RE_HASH = re.compile(rb'hash=([0-9a-fA-Fx]+)')
RE_OP = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
RE_US = re.compile(rb'MainTaskLate: us=(\d+)')


def gate():
    if os.path.exists(STOP):
        os._exit(4)
    if os.path.exists(LOCK):
        os._exit(3)


def reason_class(line):
    m = RE_OP.search(line)
    if m:
        return 'op:' + m.group(1).decode() + ':' + m.group(2).decode()
    if b'resource tracking' in line:
        return 'resource_tracking'
    if b'budget exceeded' in line:
        return 'budget'
    return 'other'


def scan(path):
    gate()
    out = '%s/%s.json' % (WD, hashlib.md5(path.encode('utf-8')).hexdigest())
    r = {'path': path, 'skipped': {}, 'take': collections.Counter(), 'take_lines': 0, 'cfg_out': [], 'sock': 0, 'sock_ex': None,
         'read0': 0, 'read0_ex': None, 'ctl_removed': 0, 'ctl_ex': None, 'vuid06479': 0, 'v_ex': None, 'late_ge1s': 0,
         'late_ex': None, 'quit': 0, 'fatal': 0, 'fatal_ex': None, 'lines': 0}
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    carry = b''
    lineno = 0
    try:
        while True:
            gate()
            blk = fh.read(BLOCK)
            if not blk:
                buf = carry
                if buf and not buf.endswith(NL):
                    buf += NL
                carry = b''
                if not buf:
                    break
                last_block = True
            else:
                buf = carry + blk
                k = buf.rfind(NL)
                if k < 0:
                    carry = buf
                    continue
                carry = buf[k + 1:]
                buf = buf[:k + 1]
                last_block = False
            p = 0
            prev = 0
            for m in KEY.finditer(buf):
                if m.start() < p:
                    continue
                ls = buf.rfind(NL, 0, m.start()) + 1
                le = buf.find(NL, m.start())
                lineno += buf.count(NL, prev, ls)
                prev = ls
                p = le + 1
                ln = lineno + 1
                line = buf[ls:le].rstrip(bytes([13]))
                t = line.lstrip()
                ex = '%d:%s' % (ln, t[:200].decode('utf-8', 'replace'))
                if b'CsPretranslate: skipped hash=' in t:
                    h = RE_HASH.search(t)
                    if h:
                        r['skipped'].setdefault(h.group(1).decode().lower(), reason_class(t))
                    continue
                if b'CsPretranslate: miss hash=' in t or b'CsPretranslate: hit hash=' in t:
                    h = RE_HASH.search(t)
                    r['take_lines'] += 1
                    if h:
                        r['take'][h.group(1).decode().lower()] += 1
                    continue
                if b'shader CFG build failed' in t and b'CsPretranslate' not in t:
                    if len(r['cfg_out']) < 5:
                        r['cfg_out'].append(ex)
                    continue
                if t.startswith(b'addrlen = ') or (t.startswith(b'len   = ') and t[8:9].isdigit() and t[8:10] != b'0x') or (b'::Recvfrom()' in t or b'::Sendto()' in t):
                    r['sock'] += 1
                    r['sock_ex'] = r['sock_ex'] or ex
                    continue
                if b'Read 0 bytes' in t:
                    r['read0'] += 1
                    r['read0_ex'] = r['read0_ex'] or ex
                    continue
                if b'removed' in t and t.startswith(b'Controller'):
                    r['ctl_removed'] += 1
                    r['ctl_ex'] = r['ctl_ex'] or ex
                    continue
                if b'VUID-' in t and b'06479' in t:
                    r['vuid06479'] += 1
                    r['v_ex'] = r['v_ex'] or ex
                    continue
                mu = RE_US.search(t)
                if mu:
                    if int(mu.group(1)) >= 1000000:
                        r['late_ge1s'] += 1
                        r['late_ex'] = r['late_ex'] or ex
                    continue
                if t.startswith(b'Event: quit'):
                    r['quit'] += 1
                    continue
                if b'--- Fatal Error ---' in t or b'Unhandled exception' in t or b'Unhandled host exception' in t:
                    r['fatal'] += 1
                    r['fatal_ex'] = r['fatal_ex'] or ex
            lineno += buf.count(NL, prev, len(buf))
            if last_block:
                break
    finally:
        fh.close()
    r['lines'] = lineno
    r['take'] = dict(r['take'])
    tmp = out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as o:
        json.dump(r, o)
    os.replace(tmp, out)
    return path


def logs():
    recs = json.load(open(OUT + '/agg_f32a.json', encoding='utf-8'))
    return [(r['path'], r['size']) for r in recs if not r['dup_of'] and not r['in_f0']]


def cmd_run(workers):
    gate()
    os.makedirs(WD, exist_ok=True)
    todo = [p for p, s in sorted(logs(), key=lambda x: -x[1])
            if not os.path.exists('%s/%s.json' % (WD, hashlib.md5(p.encode('utf-8')).hexdigest()))]
    print('todo', len(todo))
    pool = multiprocessing.Pool(workers)
    n = 0
    for _ in pool.imap_unordered(scan, todo, chunksize=1):
        n += 1
    pool.close()
    pool.join()
    print('done', n, 'of', len(todo))
    if n == len(todo):
        print('WITNESS PASS COMPLETE')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        cmd_run(int(sys.argv[2]) if len(sys.argv) > 2 else 24)
    elif len(sys.argv) > 1 and sys.argv[1] == 'one':
        os.makedirs(WD, exist_ok=True)
        scan(sys.argv[2])
        print(open('%s/%s.json' % (WD, hashlib.md5(sys.argv[2].encode('utf-8')).hexdigest()), encoding='utf-8').read())
    else:
        print('usage: run [workers] | one <path>')
        sys.exit(2)
