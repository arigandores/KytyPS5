"""F24e (HPP-664): the reference map of the seal docs/track-f/f24e.md (rule 24(1)): every <commit>:<path>:<line> is checked by git show -
the line starts with its anchor and the next line starts with its +1 anchor.  A negative control (the line moved by one) must fail.
Prints one line per reference and ALL OK.  ASCII only (the anchors are compared as UTF-8 bytes, printed escaped).
usage: python refs_f24e.py"""
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
C = '47d618fe'
R = 'docs/ROADMAP.md'
REFS = [
    (C, R, 23569, '595. **\u0417\u0432\u0435\u043d\u043e F24b', '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F24a'),
    (C, R, 23580, '   (4) **\u0422\u0435\u0433\u0438 \u043f\u043e\u0434 \u0437\u0430\u043c\u043a\u043e\u043c', '   **\u0427\u0442\u0435\u043d\u0438\u0435:** (1)'),
    (C, R, 23582, '   (\u0436) **\u0417\u0432\u0435\u043d\u044c\u044f F24**', '   (\u0437) **\u0420\u0435\u0435\u0441\u0442\u0440 \u00a777:**'),
    (C, R, 23585, '   (\u043a) **\u041d\u0435 \u0437\u0430\u044f\u0432\u043b\u044f\u0435\u0442\u0441\u044f:** \u0447\u0442\u043e \u041113', '596. **\u0417\u0432\u0435\u043d\u043e F25b'),
    (C, R, 23644, '603. **\u0417\u0432\u0435\u043d\u043e F24d', '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F24d'),
    (C, R, 23649, '   (3) **\u041d3** (\u0446\u0435\u043d\u0430 `FixB13Enabled()`', '   (4) **\u041d4**'),
    (C, R, 23651, '   (5) **\u041d5**', '   (\u0432) **\u0417\u0432\u0435\u043d\u044c\u044f:** `HPP-663`'),
    (C, R, 23506, '587. **\u0417\u0432\u0435\u043d\u043e S18c2', '   (\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439 (\u043f\u0440\u0430\u0432\u0438\u043b\u043e 24):**'),
    (C, R, 23538, '590. **\u0417\u0432\u0435\u043d\u043e S18d', '   (\u0430) **\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u043f\u043e \u0448\u0430\u0433\u0430\u043c'),
    (C, R, 23096, '   (\u0433) **\u041e\u0431\u0449\u0435\u0435 \u043f\u0440\u0430\u0432\u0438\u043b\u043e 33', '   (\u0434) **\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044e**'),
]


def lines(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True).stdout.split(b'\n')
    return cache[k]


def ok_ref(commit, path, n, a, b):
    L = lines(commit, path)
    return n >= 1 and n < len(L) and L[n - 1].startswith(a.encode('utf-8')) and L[n].startswith(b.encode('utf-8'))


def main():
    bad = 0
    for commit, path, n, a, b in REFS:
        good = ok_ref(commit, path, n, a, b)
        bad += not good
        print('%s %s:%s:%d anchor %s' % ('OK  ' if good else 'BAD ', commit, path, n, a.encode('ascii', 'backslashreplace').decode()[:60]))
    neg = ok_ref(REFS[0][0], REFS[0][1], REFS[0][2] + 1, REFS[0][3], REFS[0][4])
    print('negative control (line + 1): %s' % ('FAILED as expected' if not neg else 'PASSED - BAD'))
    bad += neg
    print('REFS %d, mismatches %d' % (len(REFS), bad))
    print('ALL OK' if bad == 0 else 'FAILED')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
