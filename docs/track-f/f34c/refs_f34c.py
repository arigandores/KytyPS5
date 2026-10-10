"""F34c (HPP-740): check <commit>:<path>:<line> references of the seal docs/track-f/f34c.md (general rule 24(1)).
Each ref: the anchor must be in the line, the +1 control in the next line; negative control: the anchor shifted by +1 line must NOT match.
Last line ALL OK only if every real ref matches and every shifted copy fails.  ASCII only (Cyrillic anchors as escapes)."""
import subprocess
import sys

K = 'C:/kyty/KytyPS5'
REFS = [
    ('c5c18e55', 'docs/ROADMAP.md', 24283, '(2) **F34 = \u04116 (K3).**', '(3) **\u0414\u043e\u0432\u043e\u0434 \u0441\u0432\u0438\u043f\u0430'),
    ('c5c18e55', 'docs/ROADMAP.md', 24290, '674. **\u0417\u0432\u0435\u043d\u043e F34a', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430.**'),
    ('c5c18e55', 'docs/ROADMAP.md', 24293, '(\u0432) **\u04121 \u2014', '(\u0433) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0438\u0441\u0445\u043e\u0434\u0430 F34d'),
    ('c5c18e55', 'docs/ROADMAP.md', 24294, '(\u0433) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0438\u0441\u0445\u043e\u0434\u0430 F34d', '(\u0434) **\u04123:**'),
    ('c5c18e55', 'docs/ROADMAP.md', 24315, '676. **\u0417\u0432\u0435\u043d\u043e F34b', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439.'),
    ('c5c18e55', 'docs/ROADMAP.md', 24326, '(\u043b) **\u0411\u044e\u0434\u0436\u0435\u0442 \u0438 \u043f\u043e\u0432\u0442\u043e\u0440\u044b.**', '(\u043c) **\u0417\u0432\u0435\u043d\u044c\u044f:**'),
    ('72317680', 'docs/track-f/f34a.md', 103, '**\u041e\u043a\u043d\u043e \u043b\u0438\u0441\u0442\u0430 \u043a\u043e\u043c\u043d\u0430\u0442\u044b', '`Level has started: intro_next`'),
    ('72317680', 'docs/track-f/f34a.md', 117, '## 5. \u0424\u043e\u0440\u043c\u0430 \u0441\u0435\u0440\u0438\u0438 `b6`', ''),
    ('eef76f8c', 'docs/track-f/f34b-review.md', 34, '**RC1 \u2014', '\u0427\u0442\u043e \u043d\u0435 \u0442\u0430\u043a'),
    ('ee9632be', 'src/loader/runtimeLinker.cpp', 134, '*source = "none";', 'std::getenv("KYTY_GUEST_ARGS")'),
    ('ee9632be', 'src/graphics/presentation/window/inputScript.cpp', 151, 'LOGF("InputScript: scheduled %s at present %u (hold %.0f ms)', ''),
    ('ee9632be', 'src/graphics/presentation/window/screenshot.cpp', 513, 'std::fprintf(m_rec_index, "%u %u %.3f', ''),
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
