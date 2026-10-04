# F20a RC1 (HPP-551, review of the lead): census of the emulator command-line flags of the tag json.
# Scope - the same 123 logs as the env census of ana_f20a.py, section (1): unique logs (sha256, the order of
# ana_f20a.py) of the course binaries, '--vulkan-validation false' (last occurrence), no '--rd', no fixture directory.
# For every flag: the value of its LAST occurrence (the harness appends '--emu-arg' pairs after the base line, the
# emulator takes the last one) and the number of logs; the modal value of a flag is the form of the harness V; every
# log with a value that differs from the modal one is printed, and every flag given more than once.
# The value of '--game' is cut to its last two path components.
# Usage: python flags_f20a.py [dir]
import collections, json, lzma, re, sys

D = (sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f20a').rstrip('/') + '/'
TAB = chr(9)
BS = chr(92)
COURSE = ('9235a7ac', 'dac02fb9', 'bbad499c', '4aa62e95', '540c035a', '31cbfee8', '631ff987', 'adb0c82f')
FXDIR = re.compile(r'/[^/]*fx[^/]*/')
ATT = re.compile(r'_a[0-9]+[.]txt')
rows = [l.rstrip(chr(10)).split(TAB) for l in open(D + 'list_f20a.tsv', encoding='utf-8') if l.strip()]
meta = {}
for l in open(D + 'meta_f20a.jsonl', encoding='utf-8'):
    r = json.loads(l)
    meta[r['path']] = r
sha = {}
for l in open(D + 'sweep_all.jsonl', encoding='utf-8'):
    if l.startswith('{'):
        r = json.loads(l)
        sha[r['path']] = r['sha256']
paths = [r[0] for r in rows]
by_sha = collections.OrderedDict()
for p in sorted(paths, key=lambda p: ('/lead/' in p or FXDIR.search(p) is not None or '/old/' in p, ATT.search(p) is not None, len(p), p)):
    by_sha.setdefault(sha[p], []).append(p)
uniq = [v[0] for v in by_sha.values()]


def load(p):
    if p.endswith('.xz'):
        return json.loads(lzma.open(p, 'rt', encoding='utf-8').read())
    return json.load(open(p, encoding='utf-8'))


def flags(cl):
    # [(flag, value)] in the order of the line; a flag followed by another flag (or the end) has the value ''
    out = []
    i = 1
    while i < len(cl):
        if cl[i].startswith('--'):
            if i + 1 < len(cl) and not cl[i + 1].startswith('--'):
                out.append((cl[i], cl[i + 1]))
                i += 2
            else:
                out.append((cl[i], ''))
                i += 1
        else:
            out.append(('<bare>', cl[i]))
            i += 1
    return out


def show(k, v):
    if k == '--game':
        return '<...>/' + '/'.join(v.replace(BS, '/').split('/')[-2:])
    return v


logs = []
for p in uniq:
    m = meta[p]
    b = (m['binary_sha256'] or '')[:8]
    if b in COURSE and m['validation'] == 'false' and not m['rd'] and not FXDIR.search(p):
        fl = flags([str(x) for x in load(m['json'])['cmdline']])
        last = collections.OrderedDict()
        cnt = collections.Counter()
        for k, v in fl:
            last[k] = show(k, v)
            cnt[k] += 1
        logs.append((p, b, last, cnt, fl))
print('logs', len(logs), '(course binaries, no validation, no RenderDoc, no fixture directory; unique by sha256)')
c = collections.Counter()
for p, b, last, cnt, fl in logs:
    for k, v in last.items():
        c[(k, v)] += 1
mode = {}
for (k, v), n in c.items():
    if k not in mode or n > c[(k, mode[k])]:
        mode[k] = v
print('flag | value of the last occurrence | logs | form')
for (k, v), n in sorted(c.items()):
    print('%s | %s | %d | %s' % (k, v, n, 'harness V (modal)' if mode[k] == v else 'DIFFERS'))
print('flags absent in some log:', sorted(k for k in mode if sum(n for (kk, v), n in c.items() if kk == k) != len(logs)) or 'none')
print('logs with a value that differs from the modal one:')
nd = 0
for p, b, last, cnt, fl in sorted(logs):
    d = [(k, v) for k, v in last.items() if mode[k] != v]
    if d:
        nd += 1
        print('  %s %s %s' % (p.replace('C:/kyty/', ''), b, ' '.join('%s %s' % kv for kv in d)))
print('  logs', nd)
print('flags given more than once (all values in the order of the line):')
nm = 0
for p, b, last, cnt, fl in sorted(logs):
    for k in cnt:
        if cnt[k] > 1:
            nm += 1
            print('  %s %s %s: %s' % (p.replace('C:/kyty/', ''), b, k, ' -> '.join(show(kk, v) for kk, v in fl if kk == k)))
print('  rows', nm)
sv = [p for p, b, last, cnt, fl in logs if last.get('--shader-validation') == 'true']
ok = all(meta[p]['shader_validation'] == 'true' for p in sv) and sum(1 for p, b, last, cnt, fl in logs if meta[p]['shader_validation'] == 'true') == len(sv)
print('--shader-validation true: %d logs; equal to the field shader_validation of meta_f20a.jsonl: %s' % (len(sv), 'yes' if ok else 'NO'))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
