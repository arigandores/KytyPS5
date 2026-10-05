"""F20l (HPP-631): check of the references <commit>:<path>:<line> of the seal and the report - the anchor is in the line, the +1 text is in
the next line (general rule 24(1)).  usage: python refs_f20l.py   (ASCII only output; ends with ALL OK)"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('fe0bf0a0', 'docs/ROADMAP.md', 23217, '550. **\u0417\u0432\u0435\u043d\u043e F20i', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F20g'),
    ('fe0bf0a0', 'docs/ROADMAP.md', 23221, '(\u0433) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0447\u0442\u0435\u043d\u0438\u044f', '(\u0434) **\u041a\u043e\u043d\u0442\u0440\u043e\u043b\u0438'),
    ('fe0bf0a0', 'docs/ROADMAP.md', 23222, '(\u0434) **\u041a\u043e\u043d\u0442\u0440\u043e\u043b\u0438', '(\u0435) **\u0421\u0435\u0440\u0438\u044f \u0438 \u0431\u044e\u0434\u0436\u0435\u0442'),
    ('fe0bf0a0', 'docs/ROADMAP.md', 23224, '(\u0436) **\u0423\u0431\u0438\u0439\u0441\u0442\u0432\u043e', '(\u0437) **\u0417\u0432\u0435\u043d\u044c\u044f'),
    ('fe0bf0a0', 'docs/ROADMAP.md', 23225, '(\u0437) **\u0417\u0432\u0435\u043d\u044c\u044f', '(\u0438) **\u0414\u043e\u043b\u0433\u0438 F20g'),
    ('aaf4504e', 'docs/ROADMAP.md', 23237, '552. **\u0417\u0432\u0435\u043d\u043e F20k', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F20k'),
    ('8f3ee6ad', 'docs/ROADMAP.md', 23246, '553. **\u0417\u0432\u0435\u043d\u043e F20j2', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F20j2'),
    ('3c2ece7b', 'docs/ROADMAP.md', 23254, '554. **\u0417\u0432\u0435\u043d\u043e F20k2', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F20k2'),
    ('3c2ece7b', 'docs/ROADMAP.md', 23258, '(\u0433) **\u0427\u043b\u0435\u043d \u043f\u0435\u0447\u0430\u0442\u0438 F20l', '(\u0434) **\u0417\u0432\u0435\u043d\u044c\u044f.**'),
    ('61b410bf', 'src/common/diagB32.cpp', 579, '"DiagB32: n=%llu dt_us=%llu instr_us=%llu', '" kq_n=%u kq_us=%llu m5r_us=%llu"'),
    ('61b410bf', 'src/common/diagB32.cpp', 653, '"DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu', '" sgap_bad=%llu sgap_bad_w=%llu'),
]
ok = True
print('suite refs_f20l.py refs %d' % len(REFS))
for c, p, ln, a, b in REFS:
    t = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    good = a in t[ln - 1] and b in t[ln]
    ok &= good
    print('%s %s:%s:%d' % ('ok' if good else 'BAD', c, p, ln))
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
