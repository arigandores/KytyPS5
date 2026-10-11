"""F40c (HPP-772): check of the references <commit>:<path>:<line> of the seal pred/f40c_seal.md section 0 (general rule 24(1)): the line
contains the anchor, the next line contains the +1 control; negative control - every reference shifted by one line must FAIL.  Reads git
objects only (git show).  Last line ALL OK.  ASCII output.
usage: python refs_f40c.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
R = 'docs/ROADMAP.md'
W = 'src/graphics/presentation/window/window.cpp'
J = 'src/graphics/presentation/window/joyPump.cpp'
REFS = [
    ('d2e316ee', R, 24483, '692. **\u0417\u0432\u0435\u043d\u043e F39c \u0442\u0440\u0435\u043a\u0430 F (`HPP-769`',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F39a \u2713**'),
    ('d2e316ee', R, 24497, '(\u0433) **\u041a\u0440\u0438\u0442\u0435\u0440\u0438\u0439 \xab\u0418\u0421\u041f\u0420\u0410\u0412\u041b\u0415\u041d\u041e \u042424\xbb',
     '(0) **\u0414\u043e \u043a\u043e\u0434\u0430** (F40a'),
    ('d2e316ee', R, 24499, '(1) **\u0421\u0442\u0435\u043d\u0434 \u0438\u0437\u0434\u0430\u043d\u0438\u044f 2** (F40a;',
     '- `f24_u0` (`=0`, `upd`)'),
    ('d2e316ee', R, 24507, '\u041a\u0430\u0436\u0434\u044b\u0439 \u0442\u0435\u0433 \u2014 \u043e\u0434\u043d\u0430 \u043f\u043e\u043f\u044b\u0442\u043a\u0430;',
     '(2) **`=0` \u2014 \u043f\u0440\u0435\u0436\u043d\u0438\u0439 \u043f\u0443\u0442\u044c**'),
    ('d2e316ee', R, 24509, '(3) **\u0420\u0435\u0432\u044c\u044e \u043a\u043e\u0434\u0430** (F40b, Red Team)',
     '(4) **\u0422\u0435\u0433 \xab\u043d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\xbb** (F40c)'),
    ('d2e316ee', R, 24510, '(4) **\u0422\u0435\u0433 \xab\u043d\u0435\u0442 \u0432\u0440\u0435\u0434\u0430\xbb** (F40c)',
     '**\u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 F40c**'),
    ('d2e316ee', R, 24519, '(\u043b) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u042424',
     '693. **\u0417\u0432\u0435\u043d\u043e F38b'),
    ('d2e316ee', R, 24581, '696. **\u0417\u0432\u0435\u043d\u043e F40b \u0442\u0440\u0435\u043a\u0430 F (`HPP-771`',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F40b \u2713**'),
    ('d2e316ee', R, 24584, '(1) **RC1 \u043f\u0440\u0438\u043d\u044f\u0442 \u0432 \u0444\u043e\u0440\u043c\u0435 \u043e\u0442\u0437\u044b\u0432\u0430.**',
     '(2) **RC2 \u043f\u0440\u0438\u043d\u044f\u0442 \u0432 \u0444\u043e\u0440\u043c\u0435 \u043e\u0442\u0437\u044b\u0432\u0430.**'),
    ('d2e316ee', R, 24586, '(3) **RC3 \u043f\u0440\u0438\u043d\u044f\u0442.**',
     '(4) **\u041a\u043e\u0434 \u043f\u0440\u0430\u0432\u043a\u0438 \u043f\u043e \u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443 \u043d\u0435 \u043c\u0435\u043d\u044f\u0435\u0442\u0441\u044f:**'),
    ('d2e316ee', R, 24631, '700. **\u0417\u0432\u0435\u043d\u043e F40b2 \u0442\u0440\u0435\u043a\u0430 F (`HPP-786`',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F40b2 \u2713**'),
    ('d2e316ee', R, 24633, '(\u0431) **\u041a\u0440\u0430\u044f \u043e\u0442\u0437\u044b\u0432\u0430',
     '(\u0432) **\u0417\u0432\u0435\u043d\u044c\u044f.** `HPP-786`'),
    ('c6ceeecd', R, 24654, '703. **\u0417\u0432\u0435\u043d\u043e FS13d \u0442\u0440\u0435\u043a\u0430 F (`HPP-790`',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 FS13c \u0441\u0442\u0440\u043e\u043a\u043e\u0439.**'),
    ('c6ceeecd', R, 24659, '(\u0434) **F40c `HPP-772` \u043f\u043e\u0441\u043b\u0435 \u0444\u0430\u043a\u0442\u0430 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438:**',
     '(\u0435) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u043f. 697(\u0437)'),
    ('7c38e497', W, 1147, 'constexpr uint32_t TEST_HIDLOSS_HOLD_UPD_MS        = 8000;', 'TEST_HIDLOSS_IN_MS'),
    ('7c38e497', W, 1155, 'constexpr uint32_t TEST_HIDLOSS_FLAP_TASK_DELAY_MS = 50;', 'TEST_HIDLOSS_RING'),
    ('7c38e497', W, 1459, 'LOGF("TestHidLoss: f24 mode=%s fix=%d', 'in_seen=%llu in_post_fail=%llu'),
    ('7c38e497', W, 1695, 'JoyPump::Post([] { LOGF("TestHidLoss: jp_task ran', '}'),
    ('7c38e497', W, 1699, 'LOGF("TestHidLoss: quit posted', 'SDL_Event quit {};'),
    ('7c38e497', J, 97, 'LOGF("FixF24: init_owner hid=', 'helper, msg, pump, main_os_tid);'),
    ('7c38e497', J, 440, 'LOGF("FixF24: pump_stop_expired', 'thread.detach();'),
    ('7c38e497', J, 454, 'LOGF("FixF24: mode=%d b24=%d', '}'),
]
CACHE = {}


def lines(c, p):
    k = (c, p)
    if k not in CACHE:
        out = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8')
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
