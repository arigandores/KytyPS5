"""F36a (HPP-758): check of the references <commit>:<path>:<line> of docs/track-f/f36a.md - the line holds the anchor and the next
line holds the +1 text (git show of the commit, real git). Prints one line per reference and ALL OK / FAIL."""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('02531a91', 'docs/ROADMAP.md', 24411, '687. **Звено F35c трека F (`HPP-757`, лид;', '   (а) **Приёмка строкой. F35a ✓**'),
    ('02531a91', 'docs/ROADMAP.md', 24417, '   (е) **Задание F36a (Emu Engineer;', '      (0) **§0 до данных**'),
    ('02531a91', 'docs/ROADMAP.md', 24419, '      (1) **Член годности события (до данных):**', '      (2) **Прогон:**'),
    ('02531a91', 'docs/ROADMAP.md', 24422, '   (ж) **Правило исхода F36c (лид, до данных).**', '      (1) **Проверка опор (е)(0)(v) не прошла**'),
    ('f22eccf5', 'docs/track-f/f23g-review.md', 92, '**RC1. «Годные» события `be4c` не наблюдают своё исполнение;', 'Что не так: замена модуля действует на все исполнения'),
    ('f22eccf5', 'docs/track-f/f23g-review.md', 113, '**RC2. Счётчики `n_t`/`n_f`/`n_entry` события включают атомики', 'Что не так: `before` читается без замены'),
    ('f793bf5d', 'docs/track-f/f32b-review.md', 95, '**RC10 (строка 181, Б8-H).**', 'замена модуля действует на все исполнения программы в кадре'),
    ('11311fb1', 'docs/track-f/f23f/rd_f23f.py', 192, '        def run_state(nid):', '            if nid is not None:'),
    ('11311fb1', 'docs/track-f/f23f/rd_f23f.py', 291, '                    ctrl.SetFrameEvent(eid - 1, True)', '                    before = bytes(ctrl.GetBufferData('),
    ('ee9632be', 'tests/shaderCfgTests.cpp', 15832, '  if (const char *recompile = std::getenv("KYTY_RECOMPILE"); recompile != nullptr) {', '    // Offline recompilation:'),
]


def main():
    ok = True
    for c, p, n, a, b in REFS:
        t = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
        la, lb = t[n - 1] if n - 1 < len(t) else '', t[n] if n < len(t) else ''
        good = la.startswith(a) and lb.startswith(b)
        ok &= good
        print('%s:%s:%d anchor %s +1 %s' % (c, p, n, 'OK' if la.startswith(a) else 'FAIL', 'OK' if lb.startswith(b) else 'FAIL'))
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
