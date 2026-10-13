import os, sys, re, subprocess, collections, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
# Value distribution of BufferFillTrace lines (KYTY_CLEAR_TRACE) kept in the KytyPS5 docs tree at HEAD,
# and of ClearDecodeFail lines there. Only reads git objects of HEAD.
REPO = 'C:/kyty/KytyPS5'
head = subprocess.run(['git', '-C', REPO, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
print('HEAD', head)
out = subprocess.run(['git', '-C', REPO, 'grep', '-I', '-a', 'BufferFillTrace: frame=', 'HEAD', '--', 'docs'],
                     capture_output=True).stdout
rx = re.compile(rb'BufferFillTrace: frame=(\d+) shader=0x([0-9a-f]+) addr=0x([0-9a-f]+) size=0x([0-9a-f]+) value=0x([0-9a-f]+) outcome=(\w+)')
per_file = collections.Counter()
vals = collections.Counter()
seen = set()
for line in out.splitlines():
    m = rx.search(line)
    if not m:
        continue
    fn = line.split(b':', 2)[1]
    key = (fn, m.group(0))
    if key in seen:
        continue
    seen.add(key)
    per_file[fn.decode()] += 1
    v = int(m.group(5), 16)
    vals[(m.group(6).decode(), v)] += 1
print('files with BufferFillTrace lines:')
for f, n in per_file.most_common():
    print('  ', n, f)
print('value x outcome (unique lines per file):')
for (o, v), n in sorted(vals.items(), key=lambda x: -x[1]):
    lo, hi = v & 0xffff, v >> 16
    rep8 = v == (v & 0xff) * 0x01010101
    print('   outcome=%-6s value=0x%08x n=%d halves_equal=%d byte_replicated=%d' % (o, v, n, int(lo == hi), int(rep8)))
nz_ok = sum(n for (o, v), n in vals.items() if o == 'ok' and v != 0)
uneq_ok = sum(n for (o, v), n in vals.items() if o == 'ok' and (v & 0xffff) != (v >> 16))
print('ok_nonzero', nz_ok, 'ok_unequal_halves', uneq_ok)
print('DONE')
