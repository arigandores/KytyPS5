import subprocess, sys
# p433 refs (F17b, HPP-526): anchor and +1 of every <commit>:<path>:<line> of ROADMAP item 433
G = 'C:/Program Files/Git/cmd/git.exe'
REFS = [('74a87005', 'docs/ROADMAP.md', 22160, '(е) **Следующая итерация очереди F — F17 = Ф6, офлайн, без игры и без замка**', '(`ShaderInfoCollection.cpp:379`), для которого нет привязанной цели)', False), ('2cadc203', 'docs/track-f/f17a.md', 7, '**Кандидат исхода для F17b (не вердикт; правило — п. 421(е)).**', '', False), ('2cadc203', 'docs/track-f/f17a.md', 51, '| П1 | **база 0** |', '| П2 | **повтор `rtskip`**', False), ('2cadc203', 'docs/track-f/f17a.md', 164, '## 4. Проект диагностики `KYTY_DIAG_F6` (умолчание 0; только измерение)', '', False), ('2cadc203', 'src/graphics/host_gpu/renderer/renderDraw.cpp', 2885, 'if (slot == 0 || (render_target_mask_slot(ctx.GetRenderTargetMask(), slot) != 0 &&', 'ctx.GetRenderTarget(slot).base.addr != 0)) {', False), ('2cadc203', 'src/graphics/host_gpu/renderer/colorRenderTarget.cpp', 184, 'if (rt.base.addr == 0 || mask == 0) {', 'if (graphics_debug_dump_enabled()) {', True), ('2cadc203', 'src/libs/audio.cpp', 640, 'if (SDL_QueueAudio(port->audio_device, queue_data, queue_size) < 0) {', 'LOGF("AudioOut: SDL_QueueAudio failed: %s\\n", SDL_GetError());', False), ('2cadc203', 'src/libs/audio.cpp', 854, 'SDL_CloseAudioDevice(port->audio_device);', 'SDL_QuitSubSystem(SDL_INIT_AUDIO);', True), ('2cadc203', 'docs/track-f/register.md', 781, '| Ф6 (поправка к §4) | K4 | наблюдение |', '', False), ('2cadc203', 'docs/track-f/register.md', 175, '| Ф8 | K4 | наблюдение (последняя с. 105) |', '| Б22 | K5 |', False)]
ok = 0
for c, p, ln, a, p1, ex in REFS:
    L = subprocess.run([G, '-C', 'C:/kyty/KytyPS5', 'show', c + ':' + p], capture_output=True, check=True).stdout.decode('utf-8').split(chr(10))
    s = L[ln - 1].strip(); n = L[ln].strip()
    good = (s == a if ex else s.startswith(a)) and (n == '' if p1 == '' else n.startswith(p1))
    print(('OK  ' if good else 'BAD ') + c + ':' + p + ':' + str(ln))
    ok += good
print(ok, 'of', len(REFS), 'ALL OK' if ok == len(REFS) else 'FAIL')
sys.exit(0 if ok == len(REFS) else 1)
