# F25k2 (HPP-682): the positive control of the RC4 test - the RC4 guard of Drain / ExitDrain removed (the F25k form of
# the two lines restored) in a worktree copy of log.cpp; built as log_async_tests_rc4off.exe, then the file is restored
# (git checkout + patch_f25k2.py). Usage: python rc4_off.py <repo root>
import sys

p = sys.argv[1].rstrip('/') + '/src/common/logging/log.cpp'
t = open(p, 'rb').read().decode('utf-8')
old = '\tif (t_writer || t_in_queue || t_sink_owner) {\n'
new = '\tif (t_writer || t_in_queue) {\n'
n = t.count(old)
if n != 2:
    raise SystemExit('anchor: %d occurrences (expected 2: Drain, ExitDrain)' % n)
open(p, 'wb').write(t.replace(old, new).encode('utf-8'))
print('RC4 guard removed in Drain and ExitDrain')
