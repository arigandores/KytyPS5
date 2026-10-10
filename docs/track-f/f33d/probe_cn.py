"""F33d (HPP-745): LOCAL PROBE ONLY (not for main) - adds to the stand KYTY_TEST_EXITFATAL of the F33d worktree an arm
CN: as C (the injector raises a fatal 50 ms after the start, the main thread never exits), and inside the injector's own
walk, before its first emergency callback, the injector raises a second fatal (EXIT_IF) - a fatal inside an emergency
callback of the owner, i.e. the nested re-entry of item 675(g) "a fatal inside an emergency callback".
usage: probe_cn.py <wt>"""
import sys

path = sys.argv[1] + '/src/emulator.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')
BS = chr(92)


def rep(old, new):
    global t
    assert t.count(old) == 1, ('anchor', old[:60], t.count(old))
    t = t.replace(old, new)


rep('enum class Arm { Off, P2, R2, G, C, N, H, HG };\n', 'enum class Arm { Off, P2, R2, G, C, N, H, HG, CN }; // PROBE CN\n')
rep('\t\tcase Arm::HG: return "HG";\n', '\t\tcase Arm::HG: return "HG";\n\t\tcase Arm::CN: return "CN";\n')
rep('\t\t         : name == "HG" ? Arm::HG\n', '\t\t         : name == "HG" ? Arm::HG\n\t\t         : name == "CN" ? Arm::CN\n')
rep('\tif (g_arm == Arm::C || g_arm == Arm::G || g_arm == Arm::HG) {\n',
    '\tif (g_arm == Arm::C || g_arm == Arm::G || g_arm == Arm::HG || g_arm == Arm::CN) {\n')
rep('\tif (g_arm == Arm::C) {\n\t\tfor (;;) {\n', '\tif (g_arm == Arm::C || g_arm == Arm::CN) {\n\t\tfor (;;) {\n')
cb = ('\t\t\tLine(fmt::format("ExitFatal: cb seq={} role={} pos={} t_us={}' + BS + 'n", t_seq, Role(), index, NowUs()));\n')
rep(cb, cb + '\t\t\tif (g_arm == Arm::CN && !main && g_triggered.exchange(1) == 0) {\n'
              '\t\t\t\tLine(fmt::format("ExitFatal: nested_fatal t_us={}' + BS + 'n", NowUs()));\n'
              '\t\t\t\tEXIT_IF(g_arm == Arm::CN);\n'
              '\t\t\t}\n')
if crlf:
    t = t.replace('\n', '\r\n')
open(path, 'wb').write(t.encode('utf-8'))
print('probe CN applied, crlf', crlf)
