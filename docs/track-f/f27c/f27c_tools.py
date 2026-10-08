"""Track F link F27c (HPP-694; ROADMAP s122 item 631 (v)): small helpers of the series - ASCII only.
  python f27c_tools.py salt-name <salt>                    -> 'PPSA21564.<xxh3_64(salt) as 016x>.bin' (pipelineCache.cpp InitializeDriverCache)
  python f27c_tools.py blob <file>                         -> 'blob size <s> header <h> payload <p> sha256 <sha>' (header = the signature line
                                                              'KytyPC2:...\\n' + 8 bytes of the payload hash, DriverCacheSignature / WriteDriverCache)
  python f27c_tools.py cmp-labels <a.tsv> <b.tsv> <label> ...  -> the manifest lines of the named labels only: 'labels EQUAL ...' rc 0 /
                                                              'labels DIFFER ...' rc 1 (lines of manifest_fs4c.py: label, rel, size, sha)
"""
import hashlib
import sys

TITLE = 'PPSA21564'


def salt_name(salt):
    import xxhash
    return '%s.%016x.bin' % (TITLE, xxhash.xxh3_64_intdigest(salt.encode('utf-8')))


def blob(path):
    h = hashlib.sha256()
    size = 0
    head = b''
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            if len(head) < 4096:
                head += chunk[:4096]
            size += len(chunk)
            h.update(chunk)
    nl = head.find(b'\n')
    header = nl + 1 + 8 if nl >= 0 else -1
    return dict(size=size, header=header, payload=size - header if header >= 0 else -1, sha256=h.hexdigest())


def label_lines(path, labels):
    out = []
    for l in open(path, 'rb').read().decode('utf-8').split('\n'):
        if l and l.split('\t')[0] in labels:
            out.append(l)
    return sorted(out)


def cmp_labels(a, b, labels):
    la, lb = label_lines(a, labels), label_lines(b, labels)
    if la == lb:
        return 0, 'labels EQUAL %s lines %d sha %s' % (','.join(labels), len(la), hashlib.sha256('\n'.join(la).encode()).hexdigest()[:16])
    sa, sb = set(la), set(lb)
    oa = sorted(sa - sb)
    ob = sorted(sb - sa)
    msg = 'labels DIFFER %s only-a %d only-b %d' % (','.join(labels), len(oa), len(ob))
    for x in oa[:3]:
        msg += '\n  a-only %s' % x.encode('ascii', 'backslashreplace').decode('ascii')
    for x in ob[:3]:
        msg += '\n  b-only %s' % x.encode('ascii', 'backslashreplace').decode('ascii')
    return 1, msg


def main(argv):
    if len(argv) >= 2 and argv[0] == 'salt-name':
        print(salt_name(argv[1]))
        return 0
    if len(argv) == 2 and argv[0] == 'blob':
        b = blob(argv[1])
        print('blob size %d header %d payload %d sha256 %s' % (b['size'], b['header'], b['payload'], b['sha256']))
        return 0
    if len(argv) >= 4 and argv[0] == 'cmp-labels':
        rc, msg = cmp_labels(argv[1], argv[2], argv[3:])
        print(msg)
        return rc
    print(__doc__.split('\n')[1])
    return 9


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
