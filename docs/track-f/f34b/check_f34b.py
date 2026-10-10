# F34b (HPP-739, Red Team): checks behind the review docs/track-f/f34b-review.md.
# Offline; reads git objects, two FS11-era logs and the save file. Last line ALL OK.
import hashlib, lzma, re, subprocess, sys

REPO = 'C:/kyty/KytyPS5'
ok = True


def show(rev, path):
    return subprocess.run(['git', '-C', REPO, 'show', rev + ':' + path], capture_output=True,
                          check=True).stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')


def ref(rev, path, line, anchor, nxt):
    """anchor must be in line `line`, +1 control: anchor not in line+1, nxt in line+1."""
    global ok
    L = show(rev, path)
    a = anchor in L[line - 1]
    c = anchor not in L[line] and nxt in L[line]
    print('REF %s:%s:%d anchor=%s plus1=%s' % (rev, path, line, 'OK' if a else 'NOT OK', 'OK' if c else 'NOT OK'))
    ok &= a and c


# ROADMAP item 674 and the sub-items reviewed
ref('2829896b', 'docs/ROADMAP.md', 24290, '674. **Звено F34a трека F (`HPP-738`', '(а) **Приёмка.** F34a принят')
ref('2829896b', 'docs/ROADMAP.md', 24293, '(в) **В1 — решение лида: форма N остаётся основной', '(г) **Правило исхода F34d')
ref('2829896b', 'docs/ROADMAP.md', 24294, '(г) **Правило исхода F34d — дополнение', '(д) **В3:**')
ref('2829896b', 'docs/ROADMAP.md', 24283, '(2) **F34 = Б6 (K3).**', '(3) **Довод свипа')
# F34a form lines
F = 'docs/track-f/f34a.md'
ref('72317680', F, 140, '| `b6_w` | W катсцены |', '')  # +1 is the blank line after the table
ref('72317680', F, 162, '(П5) последняя `FrameTrace` удержания', 'у V `ROOM_NOT_COVERED`')
ref('72317680', F, 169, '(V2) кадры катсцены — записи `.idx`', '− `n` последней `FrameTrace` перед ней')
ref('72317680', F, 175, '(V5) строки `AsyncPipelines: skipped draw`', 'могут быть без части draw')
ref('72317680', F, 180, '**Члены W (`b6_w0`', '`[Vulkan][E]`; 0 строк предела слоя')
ref('72317680', F, 194, '- Помеха (событие окна, игра или сеанс пользователя', 'не идёт. Маркер смерти в катсцене')
# FS11 code (ee9632be = FS11a worktree HEAD)
E = 'ee9632be'
ref(E, 'src/graphics/presentation/window/swapchain.cpp', 947, 'm_impl->screenshot.Poll()', 'm_impl->input_script.Poll()')
ref(E, 'src/graphics/presentation/window/screenshot.cpp', 513, 'job.present, job.time_s', 'std::fflush(m_rec_index)')
ref(E, 'src/graphics/presentation/window/inputScript.cpp', 201, 'InputScript: press %s at %.2f s (present %u)', 'i++;')
ref(E, 'src/graphics/host_gpu/renderer/renderDraw.cpp', 4451, 'm_context.GetGpu().GetFrameNum()', 'ps.program->shader_hash')
ref(E, 'src/graphics/presentation/videoOut.cpp', 1209, 'held.fetch_add(1, std::memory_order_relaxed) < 64', 'held (incomplete frame)')
ref(E, 'src/graphics/presentation/window/vulkanWindow.cpp', 932, 'if (error) {', 'EXIT_COLOR(severity_style')
ref(E, 'src/common/assert.cpp', 46, 'BuildFatalReport("--- Error ---"', 'return 1;')
ref(E, 'src/loader/runtimeLinker.cpp', 1610, 'GuestArgs: source=%s argc=%d', 'for (size_t i = 0; i < count; i++)')
ref(E, 'src/common/frameStats.cpp', 85, 'std::strcmp(value, "lite") != 0', '}')

# (1) FS11 lite FrameTrace carries no skc_held_inc / skc_ap_skip
n = 0; fld = None
with open('C:/kyty/f287/fs11c/log_fs11_v.txt', 'rb') as f:
    for line in f:
        if b'FrameTrace: n=' in line[:40]:
            n += 1
            if fld is None:
                fld = (b'skc_held_inc=' in line) or (b'skc_ap_skip=' in line)
print('FS11 log_fs11_v FrameTrace lines', n, 'skc fields present', fld)
ok &= n > 0 and fld is False

# (2) no W (validation) log of intro_next among -lvl intro_next logs s122..s136 found by name scan
W = ['s122/log_des122.txt', 's122/log_edes122.txt', 's127/log_s2s127.txt.xz', 's129/log_s3s129.txt.xz',
     's130/log_s2s130.txt.xz', 's131/log_lw2s131.txt.xz', 's134/log_s3s134.txt.xz', 's136/log_s3s136.txt.xz']
for p in W:
    p = 'C:/kyty/' + p
    f = lzma.open(p, 'rb') if p.endswith('.xz') else open(p, 'rb')
    b = f.read(3000000); f.close()
    vw = b.count(b'[Vulkan][W]') + b.count(b'[Vulkan][E]')
    lv = b'intro_next' in b
    print('LOG', p, 'intro_next', lv, 'vulkan_layer_lines', vw)
    ok &= lv and vw == 0

# (3) save file
h = hashlib.sha256(open('C:/kyty/KytyPS5/ps5 em/_SaveData/PPSA21564/sce_sdmemory/memory.bin', 'rb').read()).hexdigest()
print('save memory.bin', h[:8])
ok &= h.startswith('705bebbb')

# (4) u_02 (FS8, -lvl intro_next) covers the whole cutscene with 0 detector glitches
g = open('C:/kyty/s288/s15/glitch_u_02.txt', encoding='utf-8').read()
print('u_02', ' '.join(g.split()))
ok &= '7471 frames' in g and 'one-frame glitches: 0' in g

print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
