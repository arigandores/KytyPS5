# F32d (HPP-742): map of the references of docs/track-f/f32d.md (general rule 24(1)): every <commit>:<path>:<line> is read with
# 'git show', the anchor must be a substring of the target line (OK) and must NOT be in line + 1 (positive control NOT OK).
# Usage: python refs_f32d.py > refs_f32d.txt   (last line ALL OK)
import subprocess

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RM = 'docs/ROADMAP.md'
W = 'src/graphics/presentation/window/window.cpp'
V = 'src/graphics/presentation/videoOut.cpp'
REFS = [
    ('P673', '91cbf7ea', RM, 24254, '673. **\u0417\u0432\u0435\u043d\u043e F32c \u0442\u0440\u0435\u043a\u0430 F (`HPP-735`'),
    ('P673z3', '91cbf7ea', RM, 24284, '(3) **\u0414\u043e\u0432\u043e\u0434 \u0441\u0432\u0438\u043f\u0430 (RC1, RC8)'),
    ('F32a35', 'eb61b8d7', 'docs/track-f/f32a.md', 151, '281 \u0432\u0445\u043e\u0434, 25 \u0443\u0440\u043e\u0432\u043d\u0435\u0439'),
    ('F32bRC1', 'f793bf5d', 'docs/track-f/f32b-review.md', 27, '**RC1 ('),
    ('F32bRC8', 'f793bf5d', 'docs/track-f/f32b-review.md', 79, '**RC8 ('),
    ('R88B32', '595b38dd', 'docs/track-f/register.md', 1344, '| \u042132 (\u043d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u0435'.replace('\u0421', '\u0411')),
    ('R89B33', '595b38dd', 'docs/track-f/register.md', 1352, '| \u041133 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a787'),
    ('R104', '595b38dd', 'docs/track-f/register.md', 1484, '## 104. \u0418\u0442\u0435\u0440\u0430\u0446\u0438\u044f F32'),
    ('PAUSELOG', 'ee9632be', W, 211, 'LOGF("Pause: %s\\n"'),
    ('SPACE', 'ee9632be', W, 256, 'case SDLK_SPACE: SetPause(game'),
    ('BG', 'ee9632be', W, 434, 'SetPause(game, true);'),
    ('HELD', 'ee9632be', V, 1210, '" held (incomplete frame)\\n"'),
    ('FLIPHOLD', 'ee9632be', V, 3561, 'LOGF("FlipHold: us=%llu'),
]


def line_of(c, p, n):
    t = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
    return (t[n - 1] if n - 1 < len(t) else ''), (t[n] if n < len(t) else '')


ok = True
for rid, c, p, n, anc in REFS:
    a, b = line_of(c, p, n)
    good = anc in a
    ctrl = anc in b
    ok = ok and good and not ctrl
    print('%-9s %s   %s:%s:%d  anchor %s  +1 %s' % (rid, 'OK' if good and not ctrl else 'BAD', c, p, n, 'ok' if good else 'MISSING',
                                                   'OK (anchor repeats)' if ctrl else 'NOT OK'))
print('ALL OK' if ok else 'FAILED')
