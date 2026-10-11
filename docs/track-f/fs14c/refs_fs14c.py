"""FS14c (HPP-814): check of the references <commit>:<path>:<line> of the seal docs/track-f/fs14c.md section 0 (general rule 24(1)): the
line contains the anchor, the next line contains the +1 control ('<EOF>' - the line is the last of the file; '<BLANK>' - the next line is
empty); negative control - every reference shifted by one line must FAIL.  Reads git objects only (git show).  Last line ALL OK.  ASCII
output.  Port of C:/kyty/f287/fs13c/refs_fs13c.py.
usage: python refs_fs14c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
GIT = 'C:/Program Files/Git/cmd/git.exe'
RM = '45dd78a2'
C = 'eb7e8b91'
JP = 'src/graphics/presentation/window/joyPump.cpp'
FM = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
REFS = [
    (RM, 'docs/ROADMAP.md', 24708, '710. **\u0417\u0432\u0435\u043d\u043e F40d \u0442\u0440\u0435\u043a\u0430 F (`HPP-773`, \u043b\u0438\u0434)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 F40c \u0441\u0442\u0440\u043e\u043a\u043e\u0439.**'),
    (RM, 'docs/ROADMAP.md', 24712, '(\u0433) **\u041e\u0442\u0433\u0440\u0443\u0437\u043a\u0430 FS14 \u2014 \u043a\u043e\u043d\u0441\u0442\u0430\u043d\u0442\u044b \u043b\u0438\u0434\u0430.**',
     '(\u0434) **\u0420\u0435\u0435\u0441\u0442\u0440 \u00a7121**'),
    (RM, 'docs/ROADMAP.md', 24716, '(\u0437) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u043f. 692(\u043b)',
     '711. **\u0417\u0432\u0435\u043d\u043e F46b'),
    (RM, 'docs/ROADMAP.md', 24724, '712. **\u0417\u0432\u0435\u043d\u043e F44d \u0442\u0440\u0435\u043a\u0430 F (`HPP-794`, \u043b\u0438\u0434)',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439.**'),
    (RM, 'docs/ROADMAP.md', 24728, '(\u0433) **\u041e\u0442\u0433\u0440\u0443\u0437\u043a\u0430 \u2014 \u0432 FS14, \u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0438 \u043a \u043f. 710(\u0433)',
     '(\u0434) **\u0420\u0435\u0435\u0441\u0442\u0440 \u00a7122**'),
    (RM, 'docs/ROADMAP.md', 24742, '(\u0431) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e.** (1) \u0421\u0435\u0440\u0438\u044f F46c',
     '(\u0432) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-800`'),
    (RM, 'docs/ROADMAP.md', 24781, '720. **\u0417\u0432\u0435\u043d\u043e FS14b \u0442\u0440\u0435\u043a\u0430 F (`HPP-813`, Red Team',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. FS14b'),
    (RM, 'docs/ROADMAP.md', 24786, '(\u0434) **\u0417\u0432\u0435\u043d\u044c\u044f.** FS14b `HPP-813`',
     '(\u0435) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u043f. 710(\u0437) \u0438 712(\u0437)'),
    (C, JP, 455, 'const char* value = std::getenv("KYTY_FIX_F24");', "g_enabled.store(value == nullptr || value[0] == '\\0'"),
    (C, JP, 457, 'LOGF("FixF24: mode=%d b24=%d\\n", Enabled() ? 1 : 0, Controller::FixB24On() ? 1 : 0);', '}'),
    (C, JP, 203, 'LOGF("FixF24: init tid=%"', 'pump_tid, main_tid);'),
    (C, JP, 97, 'LOGF("FixF24: init_owner hid=%"', 'helper, msg, pump, main_os_tid);'),
    (C, JP, 440, 'LOGF("FixF24: pump_stop_expired t_jp_ms=%u\\n", T_JP_MS);', 'thread.detach();'),
    (C, JP, 247, 'LOGF("FixF24: pump_update_long us=%"', '}'),
    (C, JP, 351, 'LOGF("FixF24: open failed instance=%d', '}'),
    (C, JP, 376, 'LOGF("Controller %d: \\"%s\\" type=%d', 'static_cast<int>(SDL_GameControllerGetType(pad)),'),
    (C, 'src/graphics/presentation/window/window.cpp', 404, 'LOGF("Controller %d: \\"%s\\" type=%d', 'SDL_GameControllerName(pad)'),
    (C, 'src/graphics/presentation/window/window.cpp', 376, 'LOGF("Controller %s: %d, time = %.04f\\n"', 'f.timestamp_seconds);'),
    (C, FM, 46, 'const char* value = std::getenv("KYTY_FIX_F29");', "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);"),
    (C, FM, 84, 'LOGF("FixF29: mode=%d\\n", FixF29Enabled() ? 1 : 0);', '<BLANK>'),
    (C, FM, 62, 'LOGF("FixF29: overflow pass=%"', 'pass.area, parse.raw, parse.count, total);'),
    (C, FM, 255, 'LOGF("Accessed non-GPU cached memory at 0x%016"', '},'),
    (C, 'src/kernel/fileSystem.cpp', 431, 'LOGF("FixF25: mode=%d\\n", FixF25Enabled() ? 1 : 0);', '}'),
]
CACHE = {}


def lines(c, p):
    k = (c, p)
    if k not in CACHE:
        out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8')
        CACHE[k] = out.split('\n')
        if CACHE[k] and CACHE[k][-1] == '':
            CACHE[k].pop()
    return CACHE[k]


def ok_ref(c, p, n, a, b):
    L = lines(c, p)
    if n < 1 or n > len(L) or a not in L[n - 1]:
        return False
    if b == '<EOF>':
        return n == len(L)
    if b == '<BLANK>':
        return n < len(L) and L[n].strip() == ''
    return n < len(L) and b in L[n]


good = True
for c, p, n, a, b in REFS:
    r = ok_ref(c, p, n, a, b)
    print('%s %s:%s:%d' % ('OK' if r else 'NOT OK', c, p, n))
    good &= r
neg = True
for c, p, n, a, b in REFS:
    r = ok_ref(c, p, n + 1, a, b)
    print('shift %s %s:%s:%d' % ('OK (BAD)' if r else 'NOT OK', c, p, n + 1))
    neg &= not r
print('refs %d, ok %s, every shift fails %s' % (len(REFS), good, neg))
print('ALL OK' if good and neg else 'FAILED')
sys.exit(0 if good and neg else 1)
