# F48a (HPP-830): map of the references of docs/track-f/f48a.md (general rule 24(1)) - form of refs_f32a.py: every
# <commit>:<path>:<line> is read with 'git show', the anchor must be a substring of the target line (OK) and must NOT be in
# line + 1 (positive control NOT OK).  Usage: python refs_f48a.py > refs_f48a.txt   (last line ALL OK)
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
R = 'docs/track-f/register.md'
RM = 'docs/ROADMAP.md'
C = 'd336bb44'
REFS = [
    # (id, commit, path, line, anchor)
    ('P748', C, RM, 24995, '748. **Звено F47j трека F (`HPP-827`, лид'),
    ('P672', C, RM, 24239, '672. **Трек F, корень `HPP-287`'),
    ('P673', C, RM, 24254, '673. **Звено F32c трека F (`HPP-735`'),
    ('P237B3b', C, RM, 12571, 'Б3б → **`НЕ ДЕФЕКТ`**'),
    ('P593g', C, RM, 23561, '(г) **Строка Б32 Sky Garden'),
    ('R128', C, R, 1762, '## 128. Строка Б34 — чтение F47j'),
    ('R104', C, R, 1484, '## 104. Итерация F32'),
    ('R104rem', C, R, 1495, '| остатки Ф5, Б14/Б28, Б29, Б33, Б39, Б41 |'),
    ('B3b', C, R, 146, '| Б3б | K4 (п. 231(г)(4))'),
    ('B3b345', C, R, 345, 'Б3б → `НЕ ДЕФЕКТ`'),
    ('F28', C, R, 1521, '| Ф28 (новая) | K3 |'),
    ('K5harness', C, R, 1522, '| форма харнесса: чтение файла шлюза'),
    ('B32', C, R, 1523, '| Б32 (поправка к §88) | K3 |'),
    ('B36', C, R, 1493, '| Б36, Б40 (поправка к §83) | K2 |'),
    ('B5', C, R, 1494, '| Б5, Б5а (поправка к §4, §10, §74) |'),
    ('F5rem', C, R, 1093, '| Ф5 (поправка к §64) | K4 |'),
    ('B14rem', C, R, 1458, '| Б14, Б28 (поправка к §95, §96, §99) |'),
    ('B29rem', C, R, 1459, '| Б29 (поправка к §95, §96, §99) |'),
    ('B33rem', C, R, 1352, '| Б33 (поправка к §87'),
    ('B39rem', C, R, 598, '| Б39 (поправка к §21, §29) |'),
    ('B41rem', C, R, 677, '| Б41 (поправка к §22, §36, §37) |'),
    ('F21', C, R, 1542, '| Ф21 (поправка к §44, §104, §105) |'),
    ('F21n4', C, R, 1544, 'строки `nested_fatal`'),
    ('F24n2', C, R, 1691, 'Н2 — паркуется до строки `FixF24: mode=1`'),
    ('B8H', C, R, 1573, '| Б8-H (поправка к §63, §104, §110) |'),
    ('B8', C, R, 1574, '| Б8 (поправка к §63) | K4 |'),
    ('F26', C, R, 1711, '| Ф26 (поправка к §118) | K4 |'),
    ('B34', C, R, 1768, '| Б34 (поправка к §127) |'),
    ('F20', C, R, 1746, '| Ф20 (поправка к §125) | K4 |'),
    ('F29', C, R, 1723, '| Ф29 (поправка к §122) | K4 |'),
    ('srcStream', C, 'src/kernel/fileSystem.cpp', 664, 'const bool g_stream_trace = Common::EnvFlagOn("KYTY_STREAM_TRACE");'),
    ('srcStreamLog', C, 'src/kernel/fileSystem.cpp', 767, 'LOGF("StreamRead: #%"'),
    ('srcInject', C, 'src/emulator.cpp', 308, 'EXIT_IF(g_inject.load());'),
]


def show(commit, path):
    return subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True).stdout.decode('utf-8').split('\n')


def main():
    cache = {}
    ok = True
    for rid, c, p, ln, a in REFS:
        if (c, p) not in cache:
            cache[(c, p)] = show(c, p)
        lines = cache[(c, p)]
        hit = ln <= len(lines) and a in lines[ln - 1]
        ctl = ln < len(lines) and a in lines[ln]
        print('%-10s %s:%s:%d %s | +1 %s' % (rid, c, p, ln, 'OK' if hit else 'MISS', 'NOT OK' if not ctl else 'ANCHOR ALSO IN +1'))
        ok &= hit and not ctl
    print('refs', len(REFS))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
