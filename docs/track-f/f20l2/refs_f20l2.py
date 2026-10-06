"""F20l2 (HPP-648): check of the references <commit>:<path>:<line> of the seal 2 and the report - the anchor is in the line, the +1 text is
in the next line (general rule 24(1)).  usage: python refs_f20l2.py   (ASCII only output; ends with ALL OK)"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('e8511f53', 'docs/ROADMAP.md', 23423, '574. **\u0417\u0432\u0435\u043d\u043e F20m \u0442\u0440\u0435\u043a\u0430 F (`HPP-632`, \u043b\u0438\u0434): \u0447\u0442\u0435\u043d\u0438\u0435 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439 F20l', '(\u0430) **\u0414\u0430\u043d\u043d\u044b\u0435 \u043b\u0438\u0434\u0430 [c]**'),
    ('e8511f53', 'docs/ROADMAP.md', 23428, '(\u0434) **\u041f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043f\u0440\u0430\u0432\u0438\u043b\u0430 \u0447\u0442\u0435\u043d\u0438\u044f \u043f. 550(\u0433)(2)(iv)', '(\u0435) **\u041f\u043e\u0432\u0442\u043e\u0440 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439 \u2014 F20l2'),
    ('e8511f53', 'docs/ROADMAP.md', 23429, '(\u0435) **\u041f\u043e\u0432\u0442\u043e\u0440 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439 \u2014 F20l2', '(\u0436) **\u0417\u0432\u0435\u043d\u044c\u044f'),
    ('e8511f53', 'docs/ROADMAP.md', 23465, '581. **\u0417\u0432\u0435\u043d\u043e F20k3 \u0442\u0440\u0435\u043a\u0430 F', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439 (\u043f\u0440\u0430\u0432\u0438\u043b\u043e 24):**'),
    ('e8511f53', 'docs/ROADMAP.md', 23468, '(\u0432) **\u0420\u0435\u0448\u0435\u043d\u0438\u044f \u043f\u043e RC (\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430).**', '(\u0433) **\u0421\u0447\u0451\u0442 \u04231.**'),
    ('e8511f53', 'docs/ROADMAP.md', 23472, '(\u0436) **F20l2 `HPP-648` \u2014 \u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043f. 574(\u0435):**', '(\u0437) **\u0417\u0432\u0435\u043d\u044c\u044f'),
    ('e8511f53', 'docs/ROADMAP.md', 23483, '584. **\u0417\u0432\u0435\u043d\u043e F20k4 \u0442\u0440\u0435\u043a\u0430 F', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439'),
    ('e8511f53', 'docs/ROADMAP.md', 23486, '(\u0432) **\u0417\u0430\u043c\u0435\u0447\u0430\u043d\u0438\u044f \u043e\u0442\u0437\u044b\u0432\u0430 \u2014 \u043a\u0430\u0436\u0434\u043e\u043c\u0443 \u043e\u0434\u043d\u043e \u0438\u0437 \u0442\u0440\u0451\u0445', '(\u0433) **\u0414\u0430\u043b\u044c\u0448\u0435:**'),
    ('4371ff4b', 'src/common/diagB32.cpp', 58, 'const char* WaitName(uint8_t kind) {', 'static constexpr const char* names[] = {"-", "cond", "mutex"'),
    ('4371ff4b', 'src/common/diagB32.cpp', 659, '"DiagB32-w: n=%llu slot=%d tid=%d kind=%s obj=0x%llx', '" waker_tid=%d req_us=%llu to=%u open=%u peer=%d peer_tid=%d'),
    ('4371ff4b', 'src/common/diagB32.cpp', 677, '"DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu', '" sgap_bad=%llu sgap_bad_w=%llu'),
    ('4371ff4b', 'src/common/diagB32.h', 81, '[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {', 'return (kind >= kFirstEmuWait && kind < kFirstGuestHleWait) ||'),
]
ok = True
print('suite refs_f20l2.py refs %d' % len(REFS))
for c, p, ln, a, b in REFS:
    t = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    good = a in t[ln - 1] and b in t[ln]
    ok &= good
    print('%s %s:%s:%d' % ('ok' if good else 'BAD', c, p, ln))
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
