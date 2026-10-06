"""F20l2 (HPP-648): port of the F20l harness files into C:/kyty/f287/f20l2 - generic renames (f20l -> f20l2, F20l -> F20l2,
F20L_ -> F20L2_, HPP-631 -> HPP-648, tags b32_z0/pp/pc -> b32_z0b/ppb/pcb, the F20j2 test binary b9e0ee00 -> the F20j4 test binary
2d0c8815); the reader and suites are edited after this step.  Refuses if the target exists.  LF, ASCII.  usage: python port_f20l2.py"""
import os
import re
import shutil
import sys

SRC = 'C:/kyty/f287/f20l'
DST = 'C:/kyty/f287/f20l2'
# (source name, target name, renames applied)
FILES = [
    ('b32_read.py', 'b32_read.py', True), ('f20e_read.py', 'f20e_read.py', False), ('test_b32_read.py', 'test_b32_read.py', True),
    ('sens_b32.py', 'sens_b32.py', True), ('b32_load.py', 'b32_load.py', False), ('m6_f20l.py', 'm6_f20l2.py', True),
    ('go_f20l.sh', 'go_f20l2.sh', True), ('launch_f20l.sh', 'launch_f20l2.sh', True), ('wait_f20l.sh', 'wait_f20l2.sh', True),
    ('post_f20l.sh', 'post_f20l2.sh', True), ('guard_f20l.py', 'guard_f20l2.py', True), ('queue_f20l.py', 'queue_f20l2.py', True),
    ('enter_scene.py', 'enter_scene.py', True), ('procload.py', 'procload.py', False), ('manifest_fs4c.py', 'manifest_fs4c.py', False),
    ('sheet142.py', 'sheet142.py', False), ('gates_default.txt', 'gates_default.txt', False), ('watch_f20l.py', 'watch_f20l2.py', True),
    ('idle142.py', 'idle142.py', False), ('run_safety99.py', 'run_safety99.py', False), ('launch_run.py', 'launch_run.py', False),
    ('test_guard_f20l.py', 'test_guard_f20l2.py', True), ('test_tools_f20l.py', 'test_tools_f20l2.py', True),
    ('regress/regress_b32.py', 'regress/regress_b32.py', True), ('mk_seal_f20l.py', 'mk_seal_f20l2.py', True),
]
OLD_SHA = 'b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91'
NEW_SHA = '2d0c8815389bdc42a2371ba813dc9460fc5565f21f89e32fad4d9e5bd2394dc7'


def ren(s):
    s = s.replace(OLD_SHA, NEW_SHA).replace('b9e0ee00', '2d0c8815')
    s = s.replace('F20j2 test', 'F20j4 test').replace('F20j2 TEST', 'F20j4 TEST')
    s = re.sub(r'f20l(?![0-9a-z])', 'f20l2', s)
    s = re.sub(r'F20l(?![0-9a-z])', 'F20l2', s)
    s = s.replace('F20L_', 'F20L2_')
    s = s.replace('HPP-631', 'HPP-648')
    s = re.sub(r'(?<![a-z0-9])b32_(z0|pp|pc)(?![a-z0-9])', r'b32_\1b', s)
    return s


def main():
    if os.path.exists(DST):
        print('target exists - refused')
        return 1
    os.makedirs(DST + '/regress')
    os.makedirs(DST + '/pred')
    os.makedirs(DST + '/runs')
    for a, b, r in FILES:
        src = os.path.join(SRC, a)
        dst = os.path.join(DST, b)
        if not r:
            shutil.copy2(src, dst)
            print('copy %s' % b)
            continue
        raw = open(src, 'rb').read()
        crlf = b'\r\n' in raw
        s = raw.decode('utf-8').replace('\r\n', '\n')
        t = ren(s)
        open(dst, 'wb').write(t.encode('utf-8'))
        print('port %s (crlf in source %s, changed lines %d)' % (b, crlf, sum(1 for x, y in zip(s.split('\n'), t.split('\n')) if x != y)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
