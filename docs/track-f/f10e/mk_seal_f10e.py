"""F10e (HPP-453): fills the sha table and the reference time of the seal, checks the anchors (+1 lines) of the references with git show,
writes C:/kyty/f287/f10e/pred/f10e_seal.md and C:/kyty/KytyPS5/docs/track-f/f10e.md (identical), copies the harness text files to
docs/track-f/f10e/ (LF).  Port of FS3c mk_seal_fs3c.py.  ASCII output only."""
import datetime, hashlib, os, shutil, subprocess, sys

G = 'C:/kyty/f287/f10e'
REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
BODY = sys.argv[1]
FILES = ['go_f10e.sh', 'launch_f10e.sh', 'wait_f10e.sh', 'post_f10e.sh', 'run_f10e.py', 'manifest_f10e.py', 'f10e_read.py', 'test_f10e_read.py',
         'test_f10e_read.out.txt', 'enter_scene.py', 'idle142.py', 'procload.py', 'gates_default.txt', 'sheet142.py', 'run_safety99.py',
         'launch_run.py', 'mk_seal_f10e.py']
EXT = ['C:/kyty/f287/bin/kyty_emulator_36e2b042.exe', 'C:/kyty/f287/f10c/kyty_emulator_36e2b042.exe', 'C:/kyty/f287/bin/kyty_emulator_540c035a.exe',
       'C:/kyty/scripts/s51_vidglitch.py']
REFS = [('18d9c792', 'docs/ROADMAP.md', 20029, '369. **Звено F10b трека F (`HPP-446`, лид): F10a (`HPP-445`) принят',
         '`KYTY_FIX_SVAL` (умолчание 0) с критерием «ИСПРАВЛЕНО Ф16» ниже; звенья F10c'),
        ('18d9c792', 'docs/ROADMAP.md', 20068, 'под замком** (F10e, Harness Engineer; копия бинаря F10c с sha256',
         '`_ShaderCache/PPSA21564/` или иной способ, названный печатью'),
        ('571bb3a7', 'docs/track-f/f10d-review.md', 68, '**RC2 (печать F10e; исполнитель — Harness Engineer).**', None),
        ('571bb3a7', 'docs/track-f/f10d-review.md', 72, '**RC3 (чтение гейта R1 `validated ≥ 151`;', None),
        ('68602c4f', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 570,
         'm_directory = std::filesystem::path("_ShaderCache") / title_id;', None),
        ('68602c4f', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 6498, 'LOGF("PipelinePrecache: no %s yet', None),
        ('eb15b682', 'docs/ROADMAP.md', 20419, '375. **Звено FS3d трека F (`HPP-450`, лид): факт установки п. 374(д) — FS3 `540c035a` УСТАНОВЛЕН',
         None),
        ('eb15b682', 'docs/ROADMAP.md', 20405, 'который содержит коммиты Б42, если FS3 к тому времени отгружен») с этой установкой действует. **F10e**',
         None),
        ('68602c4f', 'src/main.cpp', 273, '} else if (arg == "--shader-validation") {',
         'if (!ParseBool(value, options.config.shader_validation_enabled)) {')]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


ok = True
for c, path, ln, anchor, nxt in REFS:
    txt = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    a = anchor in txt[ln - 1]
    b = True if nxt is None else (nxt in txt[ln])
    print('ref %s:%s:%d anchor %s +1 %s' % (c, path, ln, a, b))
    ok &= a and b
if not ok:
    print('REF CHECK FAILED')
    sys.exit(1)
now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
rows = ['| файл | sha256 |', '|---|---|']
for f in FILES:
    rows.append('| `%s` | `%s` |' % (f, sha(os.path.join(G, f))))
for p in EXT:
    rows.append('| `%s` | `%s` |' % (p, sha(p)))
body = open(BODY, 'rb').read().decode('utf-8').replace('\r\n', '\n')
assert body.count('@@REFTIME@@') == 1 and body.count('@@SHATABLE@@') == 1
body = body.replace('@@REFTIME@@', now).replace('@@SHATABLE@@', '\n'.join(rows))
data = body.encode('utf-8')
os.makedirs(os.path.join(G, 'pred'), exist_ok=True)
for out in (os.path.join(G, 'pred', 'f10e_seal.md'), os.path.join(REPO, 'docs', 'track-f', 'f10e.md')):
    with open(out, 'wb') as f:
        f.write(data)
dst = os.path.join(REPO, 'docs', 'track-f', 'f10e')
os.makedirs(dst, exist_ok=True)
LOCAL_ONLY = ['launch_run.py']   # its text names an outside application (general rule 28): local only, sha in the table
for f in [x for x in FILES if x not in LOCAL_ONLY]:
    b = open(os.path.join(G, f), 'rb').read().replace(b'\r\n', b'\n')
    with open(os.path.join(dst, f), 'wb') as o:
        o.write(b)
print('seal %s sha256 %s (time %s), %d files copied to docs/track-f/f10e/' % ('pred/f10e_seal.md', hashlib.sha256(data).hexdigest(), now, len(FILES) - len(LOCAL_ONLY)))
