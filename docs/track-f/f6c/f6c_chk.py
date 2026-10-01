# F6c (HPP-375, ROADMAP s122 item 287(c)(1)): "before code" table of the report, recounted on the commit of the change.
# Own code (imports nothing of F6a). (1) NID = hash of the name for the 22 AudioPropagation LIB_FUNC of
# src/libs/libAudio.cpp at the commit; 6 outside the KYTY_FIX_B9A block, 16 inside; the 16 = the "not resolved" rows of
# the F6a table 1; the 22 = all rows of that table.  (2) Files of the diff parent..commit.  (3) Translation signature
# KYTY_SHADER_SOURCE_HASH computed from the git blobs (generate_version.cmake rule) at the parent and at the commit,
# and the value in the build header.
import base64, hashlib, re, struct, subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
COMMIT = sys.argv[1] if len(sys.argv) > 1 else '5f67f829d714b9f75204c74e0cc3692a08256550'
HEADER = 'C:/kyty/f287/f6c/build/kytyGitVersion.h'
F6A = 'C:/kyty/f287/f6a/f6a-b9a.md'
SUFFIX = bytes.fromhex('518D64A635DED8C1E6B039B1C3E55230')

ok = True


def git(*args):
    return subprocess.run([GIT, '-C', REPO, *args], capture_output=True, check=True).stdout


def nid(name):
    d = hashlib.sha1(name.encode() + SUFFIX).digest()
    v = struct.unpack('<Q', d[:8])[0]
    return base64.b64encode(struct.pack('>Q', v)).decode().rstrip('=').replace('/', '-')


def check(cond, text):
    global ok
    print(('ok   ' if cond else 'FAIL ') + text)
    ok &= bool(cond)


check(nid('sceKernelGetProcessTimeCounter') == 'fgxnMeTNUtY', 'control: sceKernelGetProcessTimeCounter = fgxnMeTNUtY')

parent = git('rev-parse', COMMIT + '^').decode().strip()
print('commit', COMMIT, 'parent', parent)

# (1) LIB_FUNC of the AudioPropagation library at the commit
src = git('show', COMMIT + ':src/libs/libAudio.cpp').decode()
lib = src[src.index('namespace LibAudioPropagation {'):src.index('} // namespace LibAudioPropagation')]
define = lib[lib.index('LIB_DEFINE(InitAudio_1_AudioPropagation)'):]
gate = define.index('if (fix_b9a) {')
rx = re.compile(r'LIB_FUNC\("([^"]+)", LibAudioPropagation::(AudioPropagation\w+)\);')
rows = []
for m in rx.finditer(define):
    rows.append((m.group(1), 'sce' + m.group(2), m.start() > gate))
check(len(rows) == 22, 'LIB_FUNC in the library: %d (22)' % len(rows))
check(sum(1 for r in rows if not r[2]) == 6, 'outside the KYTY_FIX_B9A block: %d (6)' % sum(1 for r in rows if not r[2]))
check(sum(1 for r in rows if r[2]) == 16, 'inside the KYTY_FIX_B9A block: %d (16)' % sum(1 for r in rows if r[2]))
check(len(set(r[0] for r in rows)) == 22, 'distinct NIDs 22')

# F6a table 1
f6a = open(F6A, encoding='utf-8').read()
trx = re.compile(r'^\| (\d{4}) \| `0x[0-9a-f]+` \| `([^`]+)` \| `([^`]+)` \| [^|]+ \| ([^|]+) \|', re.M)
table = [(m.group(1), m.group(2), m.group(3), m.group(4).strip()) for m in trx.finditer(f6a)]
check(len(table) == 22, 'F6a table 1 rows: %d (22)' % len(table))
by_nid = {r[0]: r for r in rows}
print()
print('| GOT | NID | name | hash(name) | LIB_FUNC | F6a |')
print('|---|---|---|---|---|---|')
for got, n, name, status in table:
    r = by_nid.get(n)
    h = nid(name)
    where = 'none' if r is None else ('new (=1)' if r[2] else 'old')
    print('| %s | `%s` | `%s` | `%s` | %s | %s |' % (got, n, name, h, where, status))
    check(h == n, 'hash(%s) = %s' % (name, n))
    check(r is not None and r[1] == name, 'LIB_FUNC %s -> %s' % (n, r[1] if r else None))
    check(r is not None and r[2] == (status == 'не разрешён'), 'block of %s matches F6a "%s"' % (name, status))
print()
new = sorted(r[1] for r in rows if r[2])
print('16 new:', ', '.join(new))

# (2) files of the diff
files = git('diff', '--name-only', parent, COMMIT).decode().split()
print('diff files:', files)
check([f for f in files if f.startswith('src/')] == ['src/libs/libAudio.cpp'], 'src/ files of the diff: only src/libs/libAudio.cpp')


# (3) translation signature
def signature(commit):
    names = git('ls-tree', '-r', '--name-only', commit, 'src/graphics/shader').decode().split('\n')
    names = [n for n in names if n.endswith(('.cpp', '.h', '.inc'))]
    names += ['src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',
              'src/graphics/guest_gpu/gpu_format.h', 'src/graphics/guest_gpu/gpu_defs.h']
    names.sort()
    digests = ''.join(hashlib.sha1(git('show', commit + ':' + n)).hexdigest() + '\n' for n in names)
    return hashlib.sha1(digests.encode()).hexdigest(), len(names)


sp, np_ = signature(parent)
sc, nc = signature(COMMIT)
hdr = re.search(r'KYTY_SHADER_SOURCE_HASH "([0-9a-f]+)"', open(HEADER).read()).group(1)
print('signature parent %s (%d files), commit %s (%d files), build header %s' % (sp, np_, sc, nc, hdr))
check(sp == sc == hdr, 'signature parent = commit = build header')

print('F6C RECOUNT ALL OK' if ok else 'F6C RECOUNT FAILED')
sys.exit(0 if ok else 1)
