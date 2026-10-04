"""S14j (HPP-533): real-data check of the dump text against the AvTrace: shader-spec lines of the session 142 logs, the
runs that wrote the translation cache before the snap0 snapshot (2026-09-30 23:41:52Z). For every log line
'AvTrace: shader-spec ShaderRecompiler <ST> hash=0x<h> perm=<n><spec>' the dump (KYTY_TEST_SPECDUMP_SIG=699c1e4b) is asked
whether some file of the same stage and hash has permutation n with the byte-equal spec tail. Logs are streamed in
binary mode; sha256 of every input is printed. One parser for both texts: the spec tail is everything after
'perm=<n>' in the log and after 'spec=' in the dump.

    python xcheck_s14j.py <specdump.txt> <log> [<log> ...]
"""
import collections
import hashlib
import re
import sys

LOG_RE = re.compile(rb'AvTrace: shader-spec ShaderRecompiler (\w+) hash=0x([0-9a-f]{16}) perm=(\d+)(.*)$')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


dump_path = sys.argv[1]
dump = collections.defaultdict(dict)  # (stage, hash) -> {(file, perm): spec}
with open(dump_path, 'rb') as f:
    for raw in f:
        line = raw.decode('utf-8').rstrip('\n')
        if line.startswith('SpecDump: file='):
            head, spec = line.split(' spec=', 1)
            fields = dict(kv.split('=', 1) for kv in head[len('SpecDump: '):].split(' '))
            dump[(fields['stage'], fields['hash'][2:])][(fields['file'], int(fields['perm']))] = spec
print('dump %s sha256 %s, (stage, hash) %d' % (dump_path, sha(dump_path), len(dump)))
total = collections.Counter()
for log in sys.argv[2:]:
    c = collections.Counter()
    with open(log, 'rb') as f:
        for raw in f:
            if b'AvTrace: shader-spec' not in raw:
                continue
            m = LOG_RE.search(raw.rstrip(b'\r\n'))
            if not m:
                c['unparsed'] += 1
                continue
            stage, h, n, spec = m.group(1).decode(), m.group(2).decode(), int(m.group(3)), m.group(4).decode()
            c['lines'] += 1
            entry = dump.get((stage, h))
            if entry is None:
                c['hash not in dump'] += 1
                continue
            same_perm = [s for (fn, p), s in entry.items() if p == n]
            if not same_perm:
                c['perm not in dump'] += 1
            elif spec in same_perm:
                c['EQUAL'] += 1
            else:
                c['DIFFERENT'] += 1
    print('%s sha256 %s: %s' % (log, sha(log), ', '.join('%s %d' % kv for kv in sorted(c.items()))))
    total.update(c)
print('TOTAL: %s' % ', '.join('%s %d' % kv for kv in sorted(total.items())))
