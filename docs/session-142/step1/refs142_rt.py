# Red Team s142 step 1: the reference map of review142.md (general rule 24(1)): every reference <where>:<line> with an
# anchor substring that must be IN that line and must NOT be in line+1 (the +1 control).  Git files are read at the
# pinned commit (git show), the sealed s142 files at their seal sha (checked first).  ASCII output; ALL OK at the end.
import hashlib
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = 'f8db4d5b'
SEALED = {'C:/kyty/s142/sc142.py': '66322f32cbb4a5d5e935bc44576bd933dbf885886bed7d5a001172b45b886c56',
          'C:/kyty/s142/test_sc142.py': '6620af0d6798f87c74006bbca0fe83df78a5a2a20e83afd6b586240b33592390',
          'C:/kyty/s142/enter_scene.py': 'ab2194bef5aaa9b294f01379b1153dea255d47482474cff010c8a573d4b15d63',
          'C:/kyty/s142/go142a.sh': '5bab53b49a266cab0edd742f9589ff7cc7668efba63cb00f038c84f2be855b5e',
          'C:/kyty/s142/sheet142.py': 'c1bf9e2903c7db7a30cde63b3fa346e6ea2064bbdf8ad6929e85030fa147471d',
          'C:/kyty/scripts/s51_vidglitch.py': '6afe4e3335da68f28792ada0c6c4f05f741f037f78a00bf83fb1de409ee46c1c'}
REFS = [
    # ROADMAP at the commit of item 223
    ('git', 'docs/ROADMAP.md', 11506, 'видео ≥ 3 000 кадров с 0 глитчей и'),
    ('git', 'docs/ROADMAP.md', 11632, 'Первый кадр сцены — первая строка `FrameTrace` после строки'),
    ('git', 'docs/ROADMAP.md', 11762, '`ErrorDeviceLost` при `protceil=1`'),
    ('git', 'docs/ROADMAP.md', 11769, 'окно входа — 599 показанных кадров после него'),
    ('git', 'docs/ROADMAP.md', 11790, '(`--attempts 1`: неудача — данные, повтора нет)'),
    ('git', 'docs/ROADMAP.md', 11802, 'в V ≥ 3 000 показанных кадров после первого кадра сцены'),
    ('git', 'docs/ROADMAP.md', 11803, 'в W 0 строк `[Vulkan][E]` и удержание дошло до конца'),
    ('git', 'docs/ROADMAP.md', 11872, '(1) Класс маркера смерти — **по букве скорера**'),
    ('git', 'docs/ROADMAP.md', 11873, '`GpuHangAbort:`, `ErrorDeviceLost` — K2'),
    ('git', 'docs/ROADMAP.md', 11875, '(2) `ft_tail` = 0'),
    ('git', 'docs/ROADMAP.md', 11877, '(3) Удержание W — стена `hold_s`'),
    ('git', 'docs/ROADMAP.md', 11879, '(4) Удержание переписи — сумма `dt_us`'),
    ('git', 'docs/ROADMAP.md', 11886, '(8) Исход `NOT_EVALUABLE`'),
    ('git', 'docs/ROADMAP.md', 11891, '(б) **Глитчи V**'),
    # emulator code at the same commit
    ('git', 'src/main.cpp', 263, '} else if (arg == "--vulkan-validation") {'),
    ('git', 'src/graphics/presentation/window/vulkanWindow.cpp', 810, 'r.enable_validation_layers = false;'),
    ('git', 'src/graphics/presentation/window/vulkanWindow.cpp', 837, 'LOGF("no validation layer: %s\\n", l);'),
    ('git', 'src/graphics/presentation/window/vulkanWindow.cpp', 853, 'LOGF("VK_LAYER_KHRONOS_validation available extension: %s, version = %u\\n",'),
    ('git', 'src/graphics/presentation/window/vulkanWindow.cpp', 860, 'r.enable_validation_layers = false;'),
    ('git', 'src/graphics/presentation/window/vulkanWindow.cpp', 912, 'EXIT_COLOR(severity_style, "[Vulkan][%s][%u]: %s\\n", severity_str,'),
    ('git', 'src/graphics/presentation/window/vulkanWindow.cpp', 1054, 'if (r.enable_validation_layers) {'),
    ('git', 'src/graphics/host_gpu/renderer/masterSemaphore.cpp', 109, 'LOGF("GpuHangAbort: role=%u'),
    ('git', 'src/graphics/host_gpu/renderer/masterSemaphore.cpp', 128, 'EXIT("GPU stopped completing submissions\\n");'),
    ('git', 'src/common/assert.cpp', 40, 'Log::WriteFatal(BuildFatalReport("--- Error ---", text, file, line));'),
    ('git', 'src/graphics/presentation/videoOut.cpp', 1382, 'static_cast<unsigned long long>((cur.host_ns - prev.host_ns) / 1000u),'),
    # the sealed files of s142
    ('file', 'C:/kyty/s142/sc142.py', 208, "out['other_starts'] = [name for name, p in sc['starts'] if p > epos and name != level]"),
    ('file', 'C:/kyty/s142/sc142.py', 380, "if any(m['cls'] == 'K1' for m in marks) or r['ended'] or r['exited']:"),
    ('file', 'C:/kyty/s142/sc142.py', 382, "if any(m['cls'] == 'K2' for m in marks) or k2 or r['tail_stall']:"),
    ('file', 'C:/kyty/s142/sc142.py', 386, "if d['dt_after_entry_us'] >= HOLD_CENSUS_US:"),
    ('file', 'C:/kyty/s142/sc142.py', 393, "key = ms[0]['kind'] if ms else ('attempt:%s' % r.get('attempt_outcome'))"),
    ('file', 'C:/kyty/s142/sc142.py', 419, "add('V 0 one-frame glitches (s51_vidglitch.py 4 6)', g is not None and g['glitches'] == 0,"),
    ('file', 'C:/kyty/s142/sc142.py', 427, "add('W 0 [Vulkan][E] lines', w.get('vke', 1) == 0 and w['log_present'], w.get('vke'))"),
    ('file', 'C:/kyty/s142/sc142.py', 433, "elif sheet == 'viewed':"),
    ('file', 'C:/kyty/s142/sc142.py', 530, "out.append('TAG %s: not made' % t)"),
    ('file', 'C:/kyty/s142/test_sc142.py', 287, "ok &= case('o7b ft_tail None -> no tail stall; timeout of enter_scene is not a marker', not e['tail_stall']"),
    ('file', 'C:/kyty/s142/enter_scene.py', 479, "result.update(outcome='timeout',"),
    ('file', 'C:/kyty/s142/enter_scene.py', 516, 'kill_game(game)'),
    ('file', 'C:/kyty/s142/enter_scene.py', 702, "(ROOT / ('%s.json' % tag)).write_text(json.dumps(dict("),
    ('file', 'C:/kyty/s142/go142a.sh', 241, 'echo "go142a.sh $T pid $$ attempt started'),
    ('file', 'C:/kyty/s142/sheet142.py', 31, 'step = max(1, total // (cols * rows))'),
    ('file', 'C:/kyty/scripts/s51_vidglitch.py', 48, 'if len(buf) < frame_bytes:'),
    ('file', 'C:/kyty/scripts/s51_vidglitch.py', 66, 'reader.wait()'),
]


def lines_of(kind, path):
    if kind == 'git':
        raw = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (C, path)], capture_output=True).stdout
    else:
        raw = open(path, 'rb').read()
        sh = hashlib.sha256(raw).hexdigest()
        if SEALED.get(path) != sh:
            print('BAD seal sha of %s: %s' % (path, sh[:16]))
            return None
    return raw.decode('utf-8').replace('\r\n', '\n').split('\n')


cache = {}
ok = True
n_ok = n_ctl = 0
for kind, path, ln, anchor in REFS:
    key = (kind, path)
    if key not in cache:
        cache[key] = lines_of(kind, path)
    L = cache[key]
    where = ('%s:%s:%d' % (C, path, ln)) if kind == 'git' else ('%s:%d' % (path, ln))
    good = L is not None and ln - 1 < len(L) and anchor in L[ln - 1]
    ctl = L is not None and ln < len(L) and anchor not in L[ln]
    n_ok += good
    n_ctl += ctl
    ok &= good and ctl
    print('%s %s | +1 control %s' % ('OK' if good else 'NOT OK', where.encode('ascii', 'replace').decode(),
                                     'NOT OK (as required)' if ctl else 'FOUND AT +1 (bad)'))
print('refs %d, OK %d, +1 control NOT OK %d' % (len(REFS), n_ok, n_ctl))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
