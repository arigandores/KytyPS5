# F32a (HPP-733): map of the references of docs/track-f/f32a.md (general rule 24(1)): every <commit>:<path>:<line> is read with
# 'git show', the anchor must be a substring of the target line (OK) and must NOT be in line + 1 (positive control NOT OK).
# Usage: python refs_f32a.py > refs_f32a.txt   (last line ALL OK)
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
R = 'docs/track-f/register.md'
RM = 'docs/ROADMAP.md'
C = 'bf783055'
B, F = '\u0411', '\u0424'
REFS = [
    # (id, commit, path, line, anchor)
    ('P672', '5d6bc10b', RM, 24239, '672. **\u0422\u0440\u0435\u043a F, \u043a\u043e\u0440\u0435\u043d\u044c `HPP-287`'),
    ('R103', C, R, 1471, '## 103. \u041e\u0447\u0435\u0440\u0435\u0434\u044c \u00a748.2 \u0438\u0441\u0447\u0435\u0440\u043f\u0430\u043d\u0430'),
    ('R4', C, R, 134, '## 4. \u0420\u0435\u0435\u0441\u0442\u0440'),
    ('B5', C, R, 1182, '| ' + B + '5 (\u0447\u0430\u0441\u0442\u044c'),
    ('B5a', C, R, 306, '| ' + B + '5\u0430 (\u0441\u043c\u0435\u043d\u0430 \u043a\u043b\u0430\u0441\u0441\u0430)'),
    ('B6', C, R, 153, '| ' + B + '6 | K3 |'),
    ('B34', C, R, 152, '| ' + B + '34 |'),
    ('B32', C, R, 1203, '| ' + B + '32 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a775)'),
    ('B32o', C, R, 1344, '| ' + B + '32 (\u043d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u0435'),
    ('B36', C, R, 1292, '| ' + B + '36, ' + B + '40 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a782)'),
    ('F3', C, R, 691, '| ' + F + '3 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a74, \u00a737)'),
    ('F3n', C, R, 950, '| ' + F + '3, ' + B + '26\u0432, ' + B + '26\u0433'),
    ('B26v', C, R, 322, '| ' + B + '26\u0432 (\u043d\u043e\u0432\u0430\u044f)'),
    ('B26g', C, R, 323, '| ' + B + '26\u0433 (\u043d\u043e\u0432\u0430\u044f)'),
    ('F4a', C, R, 965, '| ' + F + '4\u0430 (\u043d\u043e\u0432\u0430\u044f)'),
    ('F11', C, R, 354, '| ' + F + '11 (\u043d\u043e\u0432\u0430\u044f)'),
    ('F18', C, R, 647, '| ' + F + '18 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a735)'),
    ('F20', C, R, 738, '| ' + F + '20 (\u043d\u043e\u0432\u0430\u044f)'),
    ('F21', C, R, 752, '| ' + F + '21 (\u043d\u043e\u0432\u0430\u044f)'),
    ('F22', C, R, 1134, '| ' + F + '22 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a755)'),
    ('F24', C, R, 881, '| ' + F + '24 (\u043d\u043e\u0432\u0430\u044f)'),
    ('F25', C, R, 966, '| ' + F + '25 (\u043d\u043e\u0432\u0430\u044f)'),
    ('F26', C, R, 1094, '| ' + F + '26 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a764)'),
    ('F5', C, R, 1093, '| ' + F + '5 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a764)'),
    ('B8', C, R, 1045, '| ' + B + '8 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a74, \u00a757, \u00a761, \u00a762)'),
    ('B14', C, R, 1458, '| ' + B + '14, ' + B + '28 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a795'),
    ('B29', C, R, 1459, '| ' + B + '29 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a795'),
    ('B33', C, R, 1352, '| ' + B + '33 (\u043f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043a \u00a787'),
    ('B39', C, R, 598, '| ' + B + '39'),
    ('Q48', C, R, 814, '### 48.2 \u0421\u0442\u0440\u043e\u043a\u0438 K1\u2013K4 \u0431\u0435\u0437 \u0438\u0441\u0445\u043e\u0434\u0430'),
    ('BVHN', C, 'src/graphics/shader/recompiler/frontend/translate/Memory.cpp', 852, 'std::getenv("KYTY_BVH_NATIVE")'),
    ('BVHN2', C, 'src/graphics/shader/recompiler/frontend/translate/Memory.cpp', 853, "return value == nullptr || value[0] != '0';"),
    ('PNAME', C, 'src/libs/libs.h', 23, 'static thread_local bool PRINT_NAME_ENABLED = false;'),
    ('SOCK', C, 'src/libs/network.cpp', 1666, 'LOGF("\\t family   = %d\\n"'),
    ('RECV', C, 'src/libs/network.cpp', 2016, '"\\t len   = %" PRIu64 "\\n"'),
    ('SEND', C, 'src/libs/network.cpp', 1967, '"\\t len   = %" PRIu64 "\\n"'),
    ('ESA', C, 'src/common/assert.cpp', 25, 'Subsystems::EmergencyShutdownActive();'),
    ('CTLR', C, 'src/graphics/presentation/window/window.cpp', 406, 'LOGF("Controller %d: removed\\n", f.id);'),
    ('F19T', C, 'tests/shaderCfgTests.cpp', 5709, 'void TestF19IndirectComparisonTable() {'),
]


def lines_of(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
        cache[k] = out.stdout.decode('utf-8').replace(chr(13), '').split(chr(10))
    return cache[k]


def main():
    ok = True
    for rid, c, p, n, a in REFS:
        L = lines_of(c, p)
        hit = n <= len(L) and a in L[n - 1]
        ctl = n < len(L) and a in L[n]
        print('%-6s %s %s:%s:%d  anchor %s  +1 %s' % (rid, 'OK  ' if hit else 'FAIL', c, p, n, 'ok' if hit else 'MISSING',
                                                     'NOT OK' if not ctl else 'ALSO PRESENT'))
        ok &= hit and not ctl
    print('refs', len(REFS))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
