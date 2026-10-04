"""F18e (HPP-541): the map of references of the seal docs/track-f/f18e.md (general rule 24(1)): every <commit>:<path>:<line> - the anchor
is in the line, the control (+1) is in the next line.  usage: python refs_f18e.py   (run in C:/kyty/KytyPS5; ASCII output; ALL OK)"""
import hashlib, os, subprocess, sys

print('suite refs_f18e.py sha256 %s' % hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest())
REFS = [
    ('f55f7e03', 'docs/ROADMAP.md', 22379, '441. **\u0417\u0432\u0435\u043d\u043e F18b', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F18a'),
    ('f55f7e03', 'docs/ROADMAP.md', 22384, '(\u0434) **\u041a\u0440\u0438\u0442\u0435\u0440\u0438\u0439', '- `f8_s0` (`KYTY_FIX_F8=0`'),
    ('f55f7e03', 'docs/ROADMAP.md', 22385, '- `f8_s0` (`KYTY_FIX_F8=0`', '- `f8_s1` (`=1`'),
    ('f55f7e03', 'docs/ROADMAP.md', 22386, '- `f8_s1` (`=1`', '- `f8_n0` (`=0`'),
    ('f55f7e03', 'docs/ROADMAP.md', 22387, '- `f8_n0` (`=0`', '- `f8_n1` (`=1`'),
    ('f55f7e03', 'docs/ROADMAP.md', 22388, '- `f8_n1` (`=1`', '\u00ab\u041d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\u00bb'),
    ('f55f7e03', 'docs/ROADMAP.md', 22389, '\u00ab\u041d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\u00bb', '**(5) \u041b\u0438\u0441\u0442 \u043b\u0438\u0434\u0430**'),
    ('f55f7e03', 'docs/ROADMAP.md', 22449, '(\u0432) **\u0414\u043e \u0434\u0430\u043d\u043d\u044b\u0445 F18e', ''),
    ('f55f7e03', 'docs/ROADMAP.md', 22492, '**N5** \u2014 \u0434\u043e\u043f\u0443\u0441\u043a', '(\u0433) **\u0417\u0432\u0435\u043d\u044c\u044f:** F18d'),
    ('10a4800b', 'src/libs/audio.cpp', 373, 'LOGF("AudioStat: t_us=', '" init_calls=%"'),
    ('10a4800b', 'src/libs/audio.cpp', 533, 'LOGF("AudioOut: SDL audio init failed: %s', 'return false;'),
    ('10a4800b', 'src/libs/audio.cpp', 558, 'LOGF("AudioOut: opened SDL device', '"(system default)"'),
    ('10a4800b', 'src/libs/audio.cpp', 739, 'LOGF("AudioOut: SDL_QueueAudio failed: %s', 'if (audio_stat) {'),
    ('10a4800b', 'src/libs/audio.cpp', 805, 'LOGF("AudioOut: vibration port %d', 'freq, port.channels_num'),
    ('10a4800b', 'src/libs/audio.cpp', 938, 'LOGF("AudioIn: SDL init failed: %s', 'return;'),
    ('10a4800b', 'src/libs/controller.cpp', 158, 'LOGF("TestAudioLoss: config on delay_s=%g mode=retry', '}'),
    ('10a4800b', 'src/libs/controller.cpp', 175, 'LOGF("Haptics: disabled by KYTY_HAPTICS=0', 'return;'),
    ('10a4800b', 'src/libs/controller.cpp', 211, 'LOGF("Haptics: pad audio device \\"%s\\" opened', 'have.channels);'),
    ('10a4800b', 'src/libs/controller.cpp', 234, 'LOGF("TestAudioLoss: armed t_us=', 'return RETRY_US;'),
    ('10a4800b', 'src/libs/controller.cpp', 241, 'LOGF("TestAudioLoss: fire t_us=', 'AudioStatForce();'),
    ('10a4800b', 'src/libs/controller.cpp', 252, 'LOGF("TestAudioLoss: done attempts=%u t_us=', 'AudioStatForce();'),
    ('5b5ef739', 'docs/track-f/f18c.md', 93, '## 6. \u0427\u0442\u043e \u043f\u0440\u043e\u0432\u0435\u0440\u0438\u0442 F18e', ''),
]
bad = 0
for c, p, n, anchor, nxt in REFS:
    t = subprocess.run(['git', 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    ok = len(t) > n and anchor in t[n - 1] and (t[n].strip() == '' if nxt == '' else nxt in t[n])
    print('%s %s:%s:%d' % ('OK' if ok else 'BAD', c, p, n))
    bad += 0 if ok else 1
print('refs %d of %d' % (len(REFS) - bad, len(REFS)))
if bad:
    sys.exit(1)
print('ALL OK')
