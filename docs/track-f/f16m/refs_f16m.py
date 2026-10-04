"""Links of the seal docs/track-f/f16m.md (track F link F16m, HPP-585; general rule 24(1)): each <commit>:<path>:<line> must carry its anchor
on that line (git show), the next line (+1) is printed and must carry its +1 text.  ASCII only (non-ASCII printed as ?).
usage: python refs_f16m.py   (run in C:/kyty/KytyPS5)"""
import subprocess, sys

REFS = [
    ('c0789a34', 'docs/ROADMAP.md', 22758, '492. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430.**'),
    ('b6858d6d', 'docs/ROADMAP.md', 22786, '495. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u043f\u043e \u043f. 492(\u0437)(1)'),
    ('b6858d6d', 'docs/ROADMAP.md', 22790, '(\u0433) **\u0412-F16k-1', '(\u0434) **\u0412-F16k-2'),
    ('781ec04f', 'docs/ROADMAP.md', 22795, '496. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F16l'),
    ('781ec04f', 'docs/ROADMAP.md', 22802, '(5) **RC5', '(6) **\u041e\u0431\u0449\u0438\u0435 \u0447\u043b\u0435\u043d\u044b F16k2'),
    ('b3ec1d4c', 'docs/ROADMAP.md', 22823, '500. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u043f\u043e \u043f. 496(\u0431)(1)'),
    ('25e0985f', 'docs/ROADMAP.md', 22829, '501. **', '(\u0430) **\u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0441\u0442\u0440\u043e\u043a\u043e\u0439. F16l2'),
    ('25e0985f', 'docs/ROADMAP.md', 22831, '(\u0431) **\u041f\u0440\u0430\u0432\u0438\u043b\u0430 \u0447\u0442\u0435\u043d\u0438\u044f', '(\u0432) **\u0417\u0432\u0435\u043d\u044c\u044f:**'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 159, 'constexpr const char* F5Names[] = {', '"rt_resolves",'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 218, '"f5cmu_exact_cpu",', '};'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 586, 'EmitLine("FixF5Cmu: mode=1");', 'return true;'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 644, 'auto text = fmt::format("DiagF5Ev: cmask_fce n={} present={} gpu={}',
     '"applied={} fix={}",'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 664, 'auto text = fmt::format("DiagF5Ev: cmask_fce_nohit n={} b42={}',
     '"extent={}x{} fix={}",'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 713, 'EmitLine(On() ? "DiagF5Id: mode=1" : "DiagF5Id: mode=0 needs=KYTY_DIAG_F5");',
     'return true;'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 1042, 'const bool id_fce = reasons == dcc_fce_no_image && cnt[kFce] == reasons',
     'const bool id_cs  = cnt[kImgClear] + cnt[kMetaClear]'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/diagF5.cpp', 1047, 'std::string line = fmt::format("DiagF5Id: sum frame={} exit={}"',
     'for (uint32_t i = 0; i < kIdCount; i++) {'),
    ('ed4f96d8', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 3995,
     'if (DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&', 'f5_cmu.fix != DiagF5::CmuFix::Fresh) [[unlikely]] {'),
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
