"""Links of the seal docs/track-f/f16q.md (track F link F16q, HPP-597; general rule 24(1)): each <commit>:<path>:<line> must carry its anchor
on that line (git show), the next line (+1) is printed and must carry its +1 text.  ASCII only (non-ASCII printed as ?).
usage: python refs_f16q.py   (run in C:/kyty/KytyPS5)"""
import subprocess, sys

D = 'src/graphics/host_gpu/renderer/diagF5.cpp'
REFS = [
    ('f5991e4e', 'docs/ROADMAP.md', 22835, '502. **', '(\u0430) **\u0412-F16m-1'),
    ('c6dd8b0f', 'docs/ROADMAP.md', 22853, '504. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F16m'),
    ('c6dd8b0f', 'docs/ROADMAP.md', 22860, '(\u0436) **\u0422\u0435\u0433\u0438 F16q', '(\u0437) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0447\u0442\u0435\u043d\u0438\u044f F16r'),
    ('c6dd8b0f', 'docs/ROADMAP.md', 22861, '(\u0437) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u0447\u0442\u0435\u043d\u0438\u044f F16r', '(\u0438) **\u0417\u0432\u0435\u043d\u044c\u044f**'),
    ('7d3c44c8', 'docs/ROADMAP.md', 22869, '507. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F16p'),
    ('7d3c44c8', 'docs/ROADMAP.md', 22871, '(\u0431) **RC1', '(\u0432) **\u041f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043f\u0440\u0430\u0432\u0438\u043b\u0430 \u0447\u0442\u0435\u043d\u0438\u044f F16r'),
    ('7d3c44c8', 'docs/ROADMAP.md', 22873, '(\u0433) **RC2', '(\u0434) **\u0417\u0432\u0435\u043d\u044c\u044f**'),
    ('edb9eb5f', 'docs/ROADMAP.md', 22906, '513. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439: F16o2'),
    ('44518629', 'docs/ROADMAP.md', 22918, '515. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439: F16p2'),
    ('44518629', 'docs/ROADMAP.md', 22921, '(\u0432) **\u0420\u0435\u0448\u0435\u043d\u0438\u0435 \u043f\u043e RC1', '(\u0433) **\u041d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u044f F16p2'),
    ('44518629', 'docs/ROADMAP.md', 22922, '(\u0433) **\u041d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u044f F16p2', '(\u0434) **\u0417\u0432\u0435\u043d\u044c\u044f:**'),
    ('365cc3c2', D, 159, 'constexpr const char* F5Names[] = {', '"rt_resolves",'),
    ('365cc3c2', D, 223, '"f26_deferred_declined",', '};'),
    ('365cc3c2', D, 606, 'EmitLine("FixF26: mode=1");', 'return true;'),
    ('365cc3c2', D, 667, 'auto text = fmt::format("DiagF5Ev: cmask_fce n={} present={} gpu={}', '"applied={} fix={}",'),
    ('365cc3c2', D, 679, 'if (n > 1024) {', 'return false;'),
    ('365cc3c2', D, 699, 'if (n > 64) {', 'return false;'),
    ('365cc3c2', D, 722, 'auto text = fmt::format("DiagF5Ev: dcc_stale site={} n={} present={} gpu={}', '"extent={}x{} exact={} fix={}",'),
    ('365cc3c2', D, 737, 'if (n > 256) {', 'return false;'),
    ('365cc3c2', D, 746, 'return fmt::format("DiagF5Ev: dcc_stale_apply n={} present={} gpu={}', '"layers=0x{:08x}",'),
    ('365cc3c2', D, 753, 'if (line.n == 0 || line.n > 256) {', 'return false;'),
    ('365cc3c2', D, 790, 'EmitLine(On() ? "DiagF5Id: mode=1" : "DiagF5Id: mode=0 needs=KYTY_DIAG_F5");', 'return true;'),
    ('365cc3c2', 'src/common/gates.cpp', 430, '{"KYTY_SKIP_CEILING", "skipceil", 0, 3},', '// Session 126, MEASUREMENT ONLY'),
    ('365cc3c2', 'src/graphics/presentation/window/screenshot.cpp', 243, 'DiagF5::NotePresent(m_presents);', '}'),
]


def main():
    ok = 0
    for c, p, n, a, b in REFS:
        t = subprocess.run(['git', 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
        line, nxt = (t[n - 1] if len(t) >= n else ''), (t[n] if len(t) > n else '')
        good = a in line and b in nxt
        ok += good
        print('%s %s:%s:%d anchor %s +1 %s | +1: %s' % ('OK ' if good else 'BAD', c, p, n, 'yes' if a in line else 'NO',
                                                       'yes' if b in nxt else 'NO',
                                                       nxt.strip()[:100].encode('ascii', 'replace').decode('ascii')))
    print('refs %d of %d' % (ok, len(REFS)))
    print('ALL OK' if ok == len(REFS) else 'NOT OK')
    return 0 if ok == len(REFS) else 1


if __name__ == '__main__':
    sys.exit(main())
