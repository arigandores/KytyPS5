# F32a (HPP-733): two targeted reads over the unique delta logs.
# (a) socket creation blocks (network.cpp Socket(): '<TAB> protocol = <n>') per build class - is the socket API used at all;
# (b) every 'KernelRead: direct read failed, dst=.. size=S' line and the next '<TAB>Read N bytes' line of the same log:
#     full read or not (row F25 witness form 1): a bypass of size S is FULL when a later '<TAB>Read S bytes' line exists in the
#     same log (threads interleave, the next Read line is often another file's read - pairing by size, as in F22a).
# Usage: python extra_f32a.py <binmap.tsv>
import os, re, sys, json, collections, multiprocessing

OUT = os.environ.get('F32A_OUT', 'C:/kyty/f287/f32a')
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
RX = re.compile(rb'^\t protocol = |KernelRead: direct read failed|^\tRead \d+ bytes', re.M)
RE_SZ = re.compile(rb'size=(0x[0-9a-fA-F]+|\d+)')
RE_RD = re.compile(rb'Read (\d+) bytes')


def gate():
    if os.path.exists(STOP):
        os._exit(4)
    if os.path.exists(LOCK):
        os._exit(3)


def scan(path):
    gate()
    sock = 0
    byp = []
    reads = []
    ln = 0
    with open(path, 'rb') as fh:
        carry = b''
        while True:
            gate()
            b = fh.read(8 << 20)
            buf = carry + b
            if not b:
                if not buf:
                    break
                carry = b''
            else:
                k = buf.rfind(b'\n')
                if k < 0:
                    carry = buf
                    continue
                carry = buf[k + 1:]
                buf = buf[:k + 1]
            prev = 0
            for m in RX.finditer(buf):
                le = buf.find(b'\n', m.start())
                line = buf[m.start():le if le >= 0 else len(buf)]
                ln += buf.count(b'\n', prev, m.start())
                prev = m.start()
                if line.startswith(b'\t protocol = '):
                    sock += 1
                elif b'KernelRead: direct read failed' in line:
                    s = RE_SZ.search(line)
                    byp.append((ln + 1, int(s.group(1), 0) if s else -1))
                else:
                    r = RE_RD.search(line)
                    if r:
                        reads.append((ln + 1, int(r.group(1))))
            ln += buf.count(b'\n', prev, len(buf))
            if not b:
                break
    pairs = []
    for l0, sz in byp:
        later = [l for l, n in reads if n == sz and l > l0]
        pairs.append((l0, sz, later[0] if later else None))
    return path, sock, pairs


def main():
    gate()
    course = {}
    for l in open(sys.argv[1], encoding='utf-8'):
        x = l.rstrip('\n').split('\t')
        if x[0] not in ('9235a7ac', 'dac02fb9'):
            course[x[3]] = x[0]
    recs = [r for r in json.load(open(OUT + '/agg_f32a.json', encoding='utf-8')) if not r['dup_of'] and not r['in_f0']]
    wit = {}
    import hashlib
    for r in recs:
        wit[r['path']] = json.load(open('%s/wit/%s.json' % (OUT, hashlib.md5(r['path'].encode('utf-8')).hexdigest()), encoding='utf-8'))
    todo = [r['path'] for r in recs if not r['path'].endswith('.xz')]
    pool = multiprocessing.Pool(24)
    res = {p: (s, pr) for p, s, pr in pool.imap_unordered(scan, todo, chunksize=1)}
    pool.close()
    pool.join()
    bc = collections.Counter()
    for r in recs:
        if r['path'] in res:
            c = 'COURSE_FS2' if r['build'] in course else 'OTHER_OR_PRE'
            bc[(c, 'logs')] += 1
            bc[(c, 'sock_lines')] += res[r['path']][0]
            bc[(c, 'logs_with_sock')] += 1 if res[r['path']][0] else 0
    print('(a) socket creation blocks', dict(bc))
    print('(b) KernelRead direct-read failures and the next Read line')
    n = full = 0
    for r in recs:
        if r['path'] in res and res[r['path']][1]:
            for l0, sz, lr in res[r['path']][1]:
                n += 1
                full += 1 if lr else 0
                print('   %s:%d build=%s size=%s full_read_line=%s %s' % (r['path'], l0, course.get(r['build'], r['build']), sz, lr, 'FULL' if lr else 'NOT_FULL'))
    print('   pairs', n, 'full', full)


if __name__ == '__main__':
    main()
