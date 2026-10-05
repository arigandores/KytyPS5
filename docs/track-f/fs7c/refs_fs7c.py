"""FS7c (HPP-567): the map of references of the seal docs/track-f/fs7c.md (general rule 24(1)): every <commit>:<path>:<line> - the anchor
is in the line, the control (+1) is in the next line.  usage: python refs_fs7c.py   (run in C:/kyty/KytyPS5; ASCII output; ALL OK)"""
import hashlib, os, subprocess, sys

print('suite refs_fs7c.py sha256 %s' % hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest())
RM = 'docs/ROADMAP.md'
A = 'src/libs/audio.cpp'
C = 'src/libs/controller.cpp'
W = 'src/graphics/presentation/window/window.cpp'
FS = 'src/kernel/fileSystem.cpp'
REFS = [
    ('62c57c57', RM, 22584, '467. **\u0417\u0432\u0435\u043d\u043e F18f', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439 \u043f\u043e \u0447\u043b\u0435\u043d\u0430\u043c \u043f. 441(\u0434).**'),
    ('62c57c57', RM, 22591, '(3) **FS7c (Harness Engineer, \u043f\u043e\u0434 \u0437\u0430\u043c\u043a\u043e\u043c', '- `fs7_n` \u2014 \u0444\u043e\u0440\u043c\u0430 `f8_n1`'),
    ('62c57c57', RM, 22592, '- `fs7_n` \u2014 \u0444\u043e\u0440\u043c\u0430 `f8_n1`', '\u041f\u0440\u043e\u0433\u043e\u043d\u0430 \u0441 \u0432\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u0435\u0439 \u043d\u0435\u0442'),
    ('62c57c57', RM, 22593, '\u041f\u0440\u043e\u0433\u043e\u043d\u0430 \u0441 \u0432\u0430\u043b\u0438\u0434\u0430\u0446\u0438\u0435\u0439 \u043d\u0435\u0442', '(4) **FS7d (\u043b\u0438\u0434):**'),
    ('62c57c57', RM, 22713, '487. **\u0417\u0432\u0435\u043d\u043e F19f', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439 \u043f\u043e \u0447\u043b\u0435\u043d\u0430\u043c \u043f. 451(\u0434).**'),
    ('62c57c57', RM, 22721, '(3) **FS7c:** \u0441\u0432\u0435\u0440\u0445 \u043f. 467(\u0433)(3)', '(4) **FS7d:** \u0441\u0432\u0435\u0440\u0445 \u043f. 467(\u0433)(4)'),
    ('62c57c57', RM, 22948, '518. **\u0417\u0432\u0435\u043d\u043e FS7b', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439: FS7b \u2713**'),
    ('62c57c57', RM, 22952, '(1) **\u041d1**', '(2) **\u041d2**'),
    ('62c57c57', RM, 22954, '(3) **\u041d3**', '(4) **\u041d4 \u2014 \u0447\u043b\u0435\u043d \u043f\u0435\u0447\u0430\u0442\u0438 FS7c'),
    ('62c57c57', RM, 22955, '(4) **\u041d4 \u2014 \u0447\u043b\u0435\u043d \u043f\u0435\u0447\u0430\u0442\u0438 FS7c', '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f:** FS7b `HPP-566`'),
    ('62c57c57', RM, 22489, '453. **\u0417\u0432\u0435\u043d\u043e F18d', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439: F18d \u2713**'),
    ('62c57c57', RM, 22539, '460. **\u0417\u0432\u0435\u043d\u043e F19d', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F19d \u2713.**'),
    ('d6ee2dc8', A, 298, 'LOGF("FixF8: mode=1', '}'),
    ('d6ee2dc8', A, 376, 'LOGF("AudioStat: t_us=%', '" init_calls=%" PRIu64 " acq=%" PRIu64'),
    ('d6ee2dc8', A, 536, 'LOGF("AudioOut: SDL audio init failed', 'return false;'),
    ('d6ee2dc8', A, 561, 'LOGF("AudioOut: opened SDL device', 'device != nullptr ? device : "(system default)"'),
    ('d6ee2dc8', A, 742, 'LOGF("AudioOut: SDL_QueueAudio failed: %s', 'if (audio_stat) {'),
    ('d6ee2dc8', A, 808, 'LOGF("AudioOut: vibration port %d', 'freq, port.channels_num, samples_num'),
    ('d6ee2dc8', A, 941, 'LOGF("AudioIn: SDL init failed', 'return;'),
    ('d6ee2dc8', C, 470, 'LOGF("Haptics: disabled by KYTY_HAPTICS=0', 'return;'),
    ('d6ee2dc8', C, 506, 'LOGF("Haptics: pad audio device \\"%s\\" opened', 'have.channels);'),
    ('d6ee2dc8', C, 843, 'LOGF("FixB24: mode=1', 'g_pad_output = new PadOutput;'),
    ('d6ee2dc8', FS, 406, 'LOGF("FixB4: mode=%d', '}'),
    ('d6ee2dc8', W, 394, 'LOGF("Controller %d: \\"%s\\" type=%d', 'SDL_GameControllerName(pad)'),
    ('d6ee2dc8', W, 1129, 'LOGF("TestHidLoss: config on delay_s=%g mode=%s hold_ms=%u', 'TEST_HIDLOSS_HOLD_MS);'),
    ('d6ee2dc8', W, 1180, 'LOGF("TestHidLoss: fire mode=%s t_us=', 'switch (mode) {'),
    ('d6ee2dc8', W, 1216, 'LOGF("TestHidLoss: stat mode=%s main_late_max_us=', '"pad_led=%llu pad_trig=%llu pad_wait_max_us=%llu'),
]
bad = 0
for c, p, n, anchor, nxt in REFS:
    t = subprocess.run(['git', 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    ok = len(t) > n and anchor in t[n - 1] and nxt != '' and nxt in t[n]
    print('%s %s:%s:%d' % ('OK' if ok else 'BAD', c, p, n))
    if not ok and len(t) > n:
        print('   line: %s' % t[n - 1].strip()[:150].encode('ascii', 'replace').decode('ascii'))
        print('   next: %s' % t[n].strip()[:150].encode('ascii', 'replace').decode('ascii'))
    bad += 0 if ok else 1
print('refs %d of %d' % (len(REFS) - bad, len(REFS)))
if bad:
    sys.exit(1)
print('ALL OK')
