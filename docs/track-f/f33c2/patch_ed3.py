"""F33c2 (HPP-748; ROADMAP s122 item 681(v)(1)-(2)): stand KYTY_TEST_EXITFATAL edition 3 - arm CN (as C, plus a second
fatal EXIT_IF of the injector inside its own walk, right before an emergency callback - the form of the F33d probe
probe_cn.py), event 'nested_fatal'. Only src/emulator.cpp (namespace ExitFatalStand) changes; src/common/subsystems.* untouched.
usage: patch_ed3.py <repo or worktree root>"""
import sys

path = sys.argv[1] + '/src/emulator.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')
BS = chr(92)
NL = BS + 'n'


def rep(old, new):
    global t
    assert t.count(old) == 1, ('anchor', old[:70], t.count(old))
    t = t.replace(old, new)


rep('// Track F, F33c (HPP-744; ROADMAP s122 item 675(d)(1), (v)(3)-(5)): stand KYTY_TEST_EXITFATAL=<arm>:<seed>, edition 2\n'
    '// (edition 1 - F33a 5f48cc3e, test binary only); off when unset or empty. The process runs the real Init (the Graphics\n',
    '// Track F, F33c (HPP-744; ROADMAP s122 item 675(d)(1), (v)(3)-(5)): stand KYTY_TEST_EXITFATAL=<arm>:<seed>, edition 3\n'
    '// (edition 1 - F33a 5f48cc3e, test binary only; edition 2 - F33c e5979953; edition 3 - F33c2 HPP-748, item 681(v)(1):\n'
    '// the arm CN and the event nested_fatal); off when unset or empty. The process runs the real Init (the Graphics\n')
rep('//        while it holds the CRT exit lock - the wait limit of the thread that ends the process.\n',
    '//        while it holds the CRT exit lock - the wait limit of the thread that ends the process;\n'
    '//   CN - edition 3 (F33c2, item 681(v)(1)): as C (the injector raises a fatal 50 ms after the start, the main thread\n'
    '//        never exits), and inside the injector\'s own walk, right before the first emergency callback it reaches, the\n'
    '//        injector raises a second fatal (EXIT_IF) - a fatal inside an emergency callback of the owner (the form of\n'
    '//        the F33d probe probe_cn.py; once per process; line "ExitFatal: nested_fatal"). pos is printed, not used.\n')
rep('enum class Arm { Off, P2, R2, G, C, N, H, HG };\n', 'enum class Arm { Off, P2, R2, G, C, N, H, HG, CN };\n')
rep('static std::atomic<int>  g_triggered {0};\n',
    'static std::atomic<int>  g_triggered {0};\n'
    'static std::atomic<int>  g_nested_fatal {0}; // CN: the second fatal was raised (once per process)\n')
rep('\t\tcase Arm::HG: return "HG";\n', '\t\tcase Arm::HG: return "HG";\n\t\tcase Arm::CN: return "CN";\n')
rep('\t\t         : name == "HG" ? Arm::HG\n', '\t\t         : name == "HG" ? Arm::HG\n\t\t         : name == "CN" ? Arm::CN\n')
rep('(<P2|R2|G|C|N|H|HG>:<seed>), stand off', '(<P2|R2|G|C|N|H|HG|CN>:<seed>), stand off')
cb = '\t\t\tLine(fmt::format("ExitFatal: cb seq={} role={} pos={} t_us={}' + NL + '", t_seq, Role(), index, NowUs()));\n'
rep(cb, cb +
    '\t\t\tif (g_arm == Arm::CN && !main && g_nested_fatal.exchange(1) == 0) {\n'
    '\t\t\t\t// CN: a fatal inside the owner\'s emergency callback (the callback of this entry is not reached).\n'
    '\t\t\t\tLine(fmt::format("ExitFatal: nested_fatal role={} seq={} pos={} t_us={}' + NL + '", Role(), t_seq, index,\n'
    '\t\t\t\t                 NowUs()));\n'
    '\t\t\t\tEXIT_IF(g_arm == Arm::CN);\n'
    '\t\t\t}\n')
rep('\tif (g_arm == Arm::C || g_arm == Arm::G || g_arm == Arm::HG) {\n\t\tCommon::Thread::Sleep(50);\n',
    '\tif (g_arm == Arm::C || g_arm == Arm::G || g_arm == Arm::HG || g_arm == Arm::CN) {\n\t\tCommon::Thread::Sleep(50);\n')
rep('\tif (g_arm == Arm::C) {\n\t\tfor (;;) {\n', '\tif (g_arm == Arm::C || g_arm == Arm::CN) {\n\t\tfor (;;) {\n')
if crlf:
    t = t.replace('\n', '\r\n')
open(path, 'wb').write(t.encode('utf-8'))
print('edition 3 applied, crlf', crlf)
