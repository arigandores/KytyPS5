"""F19e (HPP-549): the map of references of the seal docs/track-f/f19e.md (general rule 24(1)): every <commit>:<path>:<line> - the anchor
is in the line, the control (+1) is in the next line.  usage: python refs_f19e.py   (run in C:/kyty/KytyPS5; ASCII output; ALL OK)"""
import hashlib, os, subprocess, sys

print('suite refs_f19e.py sha256 %s' % hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest())
W = 'src/graphics/presentation/window/window.cpp'
C = 'src/libs/controller.cpp'
REFS = [
    ('db8dacef', 'docs/ROADMAP.md', 22463, '451. **\u0417\u0432\u0435\u043d\u043e F19b', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F19a'),
    ('db8dacef', 'docs/ROADMAP.md', 22468, '(\u0434) **\u041a\u0440\u0438\u0442\u0435\u0440\u0438\u0439 \u00ab\u0418\u0421\u041f\u0420\u0410\u0412\u041b\u0415\u041d\u041e \u041124\u00bb', '- `b24_h0` (`KYTY_FIX_B24=0`'),
    ('db8dacef', 'docs/ROADMAP.md', 22469, '- `b24_h0` (`KYTY_FIX_B24=0`', '- `b24_s0` (`=0`'),
    ('db8dacef', 'docs/ROADMAP.md', 22470, '- `b24_s0` (`=0`', '- `b24_h1` (`=1`'),
    ('db8dacef', 'docs/ROADMAP.md', 22471, '- `b24_h1` (`=1`', '- `b24_d0`, `b24_d1`'),
    ('db8dacef', 'docs/ROADMAP.md', 22472, '- `b24_d0`, `b24_d1`', '- `b24_n1` (`=1`'),
    ('db8dacef', 'docs/ROADMAP.md', 22473, '- `b24_n1` (`=1`', '\u00ab\u041d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\u00bb \u0443 `b24_h1`'),
    ('db8dacef', 'docs/ROADMAP.md', 22474, '\u00ab\u041d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\u00bb \u0443 `b24_h1`', '**(5) \u041b\u0438\u0441\u0442 \u043b\u0438\u0434\u0430**'),
    ('db8dacef', 'docs/ROADMAP.md', 22539, '460. **\u0417\u0432\u0435\u043d\u043e F19d', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F19d'),
    ('db8dacef', 'docs/ROADMAP.md', 22544, '(\u0434) **\u0414\u043e\u043b\u0433\u0438 F19d', '(\u0435) **\u0417\u0432\u0435\u043d\u044c\u044f:**'),
    ('0b065a70', 'docs/track-f/f19a.md', 181, '### 6.1 \u0421\u0442\u0440\u043e\u043a\u0430 `TestHidLoss: stat`', ''),
    ('0b065a70', 'docs/track-f/f19a.md', 199, '**\u041e\u0431\u044f\u0437\u0430\u043d\u044b \u0431\u044b\u0442\u044c 0 (\u0438\u043d\u0432\u0430\u0440\u0438\u0430\u043d\u0442\u044b):**', '**\u0422\u043e\u0436\u0434\u0435\u0441\u0442\u0432\u0430 \u0434\u043b\u044f \u0440\u0438\u0434\u0435\u0440\u0430:**'),
    ('9c726d74', W, 394, 'LOGF("Controller %d: \\"%s\\" type=%d', 'SDL_GameControllerName(pad)'),
    ('9c726d74', W, 405, 'LOGF("Controller %d: removed', 'TestHidLossCount(g_test_hidloss.removed);'),
    ('9c726d74', W, 1123, 'LOGF("TestHidLoss: config invalid', 'return c;'),
    ('9c726d74', W, 1129, 'LOGF("TestHidLoss: config on delay_s=%g mode=%s hold_ms=%u', 'TEST_HIDLOSS_HOLD_MS);'),
    ('9c726d74', W, 1175, 'LOGF("TestHidLoss: attach index=%d t_us=', '}'),
    ('9c726d74', W, 1180, 'LOGF("TestHidLoss: fire mode=%s t_us=', 'switch (mode) {'),
    ('9c726d74', W, 1203, 'LOGF("TestHidLoss: done t_us=', 'g_test_hidloss_done_us.store'),
    ('9c726d74', W, 1216, 'LOGF("TestHidLoss: stat mode=%s main_late_max_us=', '"pad_led=%llu pad_trig=%llu pad_wait_max_us=%llu'),
    ('9c726d74', W, 1292, 'LOGF("TestHidLoss: armed t_us=', 'std::thread([armed_us]'),
    ('9c726d74', C, 831, 'LOGF("FixB24: mode=1', 'g_pad_output = new PadOutput;'),
    ('9c726d74', C, 1604, 'LOGF("PadTriggerEffect: #%u', 'sent=%d'),
]
bad = 0
for c, p, n, anchor, nxt in REFS:
    t = subprocess.run(['git', 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    ok = len(t) > n and anchor in t[n - 1] and (t[n].strip() == '' if nxt == '' else nxt in t[n])
    print('%s %s:%s:%d' % ('OK' if ok else 'BAD', c, p, n))
    if not ok and len(t) > n:
        print('   line: %s' % t[n - 1].strip()[:150].encode('ascii', 'replace').decode('ascii'))
        print('   next: %s' % t[n].strip()[:150].encode('ascii', 'replace').decode('ascii'))
    bad += 0 if ok else 1
print('refs %d of %d' % (len(REFS) - bad, len(REFS)))
if bad:
    sys.exit(1)
print('ALL OK')
