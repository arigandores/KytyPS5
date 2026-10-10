"""F33e (HPP-746): check <commit>:<path>:<line> references of the seal docs/track-f/f33e.md (general rule 24(1)).
Each ref: the anchor must be in the line, the +1 control in the next line; negative control: the anchor shifted by +1 line must NOT match.
Last line ALL OK only if every real ref matches and every shifted copy fails.  Port of C:/kyty/f287/f34c/refs_f34c.py.  ASCII only
(Cyrillic anchors as escapes)."""
import subprocess
import sys

K = 'C:/kyty/KytyPS5'
REFS = [
    ('eac45df9', 'docs/ROADMAP.md', 24299, '675. **\u0417\u0432\u0435\u043d\u043e F33b',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F33a'),
    ('eac45df9', 'docs/ROADMAP.md', 24309, '(4) **\u0422\u0435\u0433 \u043f\u043e\u0434 \u0437\u0430\u043c\u043a\u043e\u043c',
     '**\u0427\u0442\u0435\u043d\u0438\u0435:** (1)\u2013(4) \u0432\u0441\u0435 \u2713 \u2014 **\u042421'),
    ('eac45df9', 'docs/ROADMAP.md', 24366, '(\u0432) **RC1 \u2014 \u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430.**',
     '(\u0433) **F33d2 (Red Team)'),
    ('eac45df9', 'docs/ROADMAP.md', 24371, '682. **\u0417\u0432\u0435\u043d\u043e F33d2',
     '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F33d2'),
    ('eac45df9', 'docs/track-f/f33c.md', 64, '2b393af8e9c1a85ad6d24bc47a3bc08f5cad2dcdd59b8f6a1ed7293859d0c612',
     'KytyPS5-2026-09-15-6a2987a-1912-g0c57cfed'),
    ('227e1b36', 'src/common/subsystems.cpp', 77, 'LOGF("FixF21: mode=%d wait_ms=%u', '}'),
    ('227e1b36', 'src/common/subsystems.cpp', 175, 'std::fprintf(stderr, "FixF21: wait_expired tid=', 'waited_us / 1000u'),
    ('227e1b36', 'src/emulator.cpp', 233, 'Common::Subsystems::InitFixF21();', 'Common::Subsystems subsystems(true);'),
    ('227e1b36', 'src/emulator.cpp', 236, 'Common::Subsystems::LogFixF21();', ''),
]


def lines(rev, path):
    out = subprocess.run(['git', '-C', K, 'show', '%s:%s' % (rev, path)], capture_output=True).stdout
    return out.decode('utf-8').split('\n')


ok = True
cache = {}
for rev, path, n, anchor, plus1 in REFS:
    key = (rev, path)
    if key not in cache:
        cache[key] = lines(rev, path)
    L = cache[key]
    good = n - 1 < len(L) and anchor in L[n - 1] and (plus1 == '' or plus1 in L[n])
    shifted = n < len(L) and anchor in L[n]
    print('%s %s:%s:%d' % ('OK    ' if good else 'BAD   ', rev, path, n))
    print('%s %s:%s:%d (shift +1, negative control)' % ('NOT OK' if not shifted else 'MATCH!', rev, path, n + 1))
    ok &= good and not shifted
print('refs', len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
