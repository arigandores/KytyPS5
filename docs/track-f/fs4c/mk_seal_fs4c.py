"""FS4c (HPP-472): fills the sha table, the binary strings and the reference time of the seal, checks the anchors (+1 lines) of the
references with git show, writes C:/kyty/f287/fs4c/pred/fs4c_seal.md and C:/kyty/KytyPS5/docs/track-f/fs4c.md (identical), copies the
harness text files to docs/track-f/fs4c/ (LF).  Port of F10e mk_seal_f10e.py.  ASCII output only."""
import datetime, hashlib, os, subprocess, sys

G = 'C:/kyty/f287/fs4c'
REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
BODY = sys.argv[1]
FILES = ['go_fs4c.sh', 'launch_fs4c.sh', 'wait_fs4c.sh', 'post_fs4c.sh', 'run_fs4c.py', 'manifest_fs4c.py', 'fs4c_read.py', 'test_fs4c_read.py',
         'test_fs4c_read.out.txt', 'enter_scene.py', 'idle142.py', 'procload.py', 'gates_default.txt', 'sheet142.py', 'run_safety99.py',
         'launch_run.py', 'mk_seal_fs4c.py']
BIN = 'C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe'
EXT = [BIN, 'C:/kyty/f287/bin/kyty_emulator_540c035a.exe', 'C:/kyty/scripts/s51_vidglitch.py']
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
REFS = [('8449030a', 'docs/ROADMAP.md', 20552, '378. **Звено F10f трека F (`HPP-454`, лид): Ф16 `FIXED` по п. 369(в)',
         'прошла; счёт трека F, не отгрузка; умолчание `KYTY_FIX_SVAL=1`'),
        ('8449030a', 'docs/ROADMAP.md', 20588, '(г) **Отгрузка — FS4, четвёртый бинарь отгрузки трека F (константы лида):**',
         '(1) **FS4a (Emu Engineer, без замка).**'),
        ('8449030a', 'docs/ROADMAP.md', 20601, '(3) **FS4c (Harness Engineer, под замком; очередь P > F > S, п. 322(г)).**',
         'удаление живого каталога варианта, манифест sha256 кэшей до/после, EQUAL'),
        ('8449030a', 'docs/ROADMAP.md', 20622, '(5) **Порядок установки с треком P.** Бинарь FS4 обязан содержать', None),
        ('a193028b', 'docs/ROADMAP.md', 20734, '383. **Звено FS4b трека F (`HPP-471`, Red Team, review лида): принят',
         'FS4c; FS4c (`HPP-472`) снимается с блока**'),
        ('a193028b', 'docs/ROADMAP.md', 20749, '(в) **З2 (откат возвращает отказ Ф16 только на новой трансляции)**',
         'холодном каталоге варианта; если `fs4_r0` идёт после'),
        ('17b51c7f', 'docs/track-f/fs4b-review.md', 108, '**З2 — откат `KYTY_FIX_SVAL=0`', None),
        ('3d0e46da', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 570,
         'm_directory = std::filesystem::path("_ShaderCache") / title_id;', None),
        ('3d0e46da', PC, 6503, 'LOGF("PipelinePrecache: no %s yet', None),
        ('3d0e46da', PC, 4670, 'LOGF("FixSval: mode=%d ubo_std_layout=%d', None),
        ('3d0e46da', PC, 1357, 'if (!Config::ShaderValidationEnabled()) {', 'return true;'),
        ('3d0e46da', 'src/main.cpp', 273, '} else if (arg == "--shader-validation") {',
         'if (!ParseBool(value, options.config.shader_validation_enabled)) {')]
BINSTR = [b'Fork build arigandores/KytyPS5 3d0e46d', b'KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da', b'-g92d11340']
SAME_AS_F10E = [('run_fs4c.py', 'C:/kyty/f287/f10e/run_f10e.py'), ('manifest_fs4c.py', 'C:/kyty/f287/f10e/manifest_f10e.py'),
                ('idle142.py', 'C:/kyty/f287/f10e/idle142.py'), ('procload.py', 'C:/kyty/f287/f10e/procload.py'),
                ('gates_default.txt', 'C:/kyty/f287/f10e/gates_default.txt'), ('sheet142.py', 'C:/kyty/f287/f10e/sheet142.py'),
                ('run_safety99.py', 'C:/kyty/f287/f10e/run_safety99.py'), ('launch_run.py', 'C:/kyty/f287/f10e/launch_run.py')]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


ok = True
for c, path, ln, anchor, nxt in REFS:
    txt = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    a = anchor in txt[ln - 1]
    b = True if nxt is None else (nxt in txt[ln])
    print('ref %s:%s:%d anchor %s +1 %s' % (c, path, ln, a, b))
    ok &= a and b
for f, ref in SAME_AS_F10E:
    e = sha(os.path.join(G, f)) == sha(ref)
    print('same as F10e %s: %s' % (f, e))
    ok &= e
binb = open(BIN, 'rb').read()
found = [(s.decode(), binb.count(s)) for s in BINSTR]
print('binary strings %s' % found)
ok &= all(n >= 1 for _, n in found)
if not ok:
    print('SEAL CHECK FAILED')
    sys.exit(1)
now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
rows = ['| файл | sha256 |', '|---|---|']
for f in FILES:
    rows.append('| `%s` | `%s` |' % (f, sha(os.path.join(G, f))))
for p in EXT:
    rows.append('| `%s` | `%s` |' % (p, sha(p)))
binstr = '; '.join('`%s` — %d' % (s, n) for s, n in found)
body = open(BODY, 'rb').read().decode('utf-8').replace('\r\n', '\n')
assert body.count('@@REFTIME@@') == 1 and body.count('@@SHATABLE@@') == 1 and body.count('@@BINSTR@@') == 1
body = body.replace('@@REFTIME@@', now).replace('@@SHATABLE@@', '\n'.join(rows)).replace('@@BINSTR@@', binstr)
data = body.encode('utf-8')
os.makedirs(os.path.join(G, 'pred'), exist_ok=True)
for out in (os.path.join(G, 'pred', 'fs4c_seal.md'), os.path.join(REPO, 'docs', 'track-f', 'fs4c.md')):
    with open(out, 'wb') as f:
        f.write(data)
dst = os.path.join(REPO, 'docs', 'track-f', 'fs4c')
os.makedirs(dst, exist_ok=True)
LOCAL_ONLY = ['launch_run.py']   # its text names an outside application (general rule 28): local only, sha in the table
for f in [x for x in FILES if x not in LOCAL_ONLY]:
    b = open(os.path.join(G, f), 'rb').read().replace(b'\r\n', b'\n')
    with open(os.path.join(dst, f), 'wb') as o:
        o.write(b)
print('seal %s sha256 %s (time %s), %d files copied to docs/track-f/fs4c/' % ('pred/fs4c_seal.md', hashlib.sha256(data).hexdigest(), now,
                                                                              len(FILES) - len(LOCAL_ONLY)))
