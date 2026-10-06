#!/usr/bin/env python3
"""F20j4 (HPP-652; ROADMAP s122 item 581(v)(2), (4)): the negative control of the new runtime tests - the two cases
TestPeerSelfRuntime (RC2) and TestLockUnderHRuntime (RC4), taken from the F20j4 test file, are put into the tests of the
F20j3 worktree (9db7938b code, uncommitted, restored by git checkout after the control run). Expected on 9db7938b: both
cases FAIL (the owner field keeps the waiter itself; W:emu_mutex displaces H:qlock / H:present).

    python ctl_f20j4.py <F20j4 tests/DiagB32Tests.cpp> <F20j3 tests/DiagB32Tests.cpp>
"""
import sys

new = open(sys.argv[1], encoding='utf-8').read().replace('\r\n', '\n')
dst = sys.argv[2]
old = open(dst, encoding='utf-8').read().replace('\r\n', '\n')

a = new.index('static void TestPeerSelfRuntime() {')
b = new.index('int main() {')
block = new[a:b]
assert 'static void TestLockUnderHRuntime() {' in block
assert old.count('#include <string>\n') == 1 and old.count('int main() {') == 1 and old.count('\tTestEmuMutexRuntime();\n') == 1
old = old.replace('#include <string>\n', '#include <shared_mutex>\n#include <string>\n')
old = old.replace('int main() {', block + 'int main() {')
old = old.replace('\tTestEmuMutexRuntime();\n', '\tTestEmuMutexRuntime();\n\tTestPeerSelfRuntime();\n\tTestLockUnderHRuntime();\n')
open(dst, 'wb').write(old.encode('utf-8'))
print('control cases inserted into', dst)
