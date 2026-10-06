"""F20l3 (HPP-655): port of the F20l2 harness files into C:/kyty/f287/f20l3 - generic renames (f20l2 -> f20l3, F20l2 -> F20l3,
F20L2_ -> F20L3_, HPP-648 -> HPP-655); the tags, the installed binary (S18 b3cee576 instead of FS8), the cold form of b32_pa and the
series are edited after this step (edit_f20l3.py).  Refuses if the target exists.  LF, ASCII.  usage: python port_f20l3.py"""
import os
import re
import shutil
import sys

SRC = 'C:/kyty/f287/f20l2'
DST = 'C:/kyty/f287/f20l3'
# (source name, target name, renames applied)
FILES = [
    ('b32_read.py', 'b32_read.py', True), ('f20e_read.py', 'f20e_read.py', False), ('test_b32_read.py', 'test_b32_read.py', True),
    ('sens_b32.py', 'sens_b32.py', True), ('m6_f20l2.py', 'm6_f20l3.py', True),
    ('go_f20l2.sh', 'go_f20l3.sh', True), ('launch_f20l2.sh', 'launch_f20l3.sh', True), ('wait_f20l2.sh', 'wait_f20l3.sh', True),
    ('post_f20l2.sh', 'post_f20l3.sh', True), ('guard_f20l2.py', 'guard_f20l3.py', True), ('queue_f20l2.py', 'queue_f20l3.py', True),
    ('runchk_f20l2.py', 'runchk_f20l3.py', True),
    ('enter_scene.py', 'enter_scene.py', True), ('procload.py', 'procload.py', False), ('manifest_fs4c.py', 'manifest_fs4c.py', False),
    ('sheet142.py', 'sheet142.py', False), ('gates_default.txt', 'gates_default.txt', False), ('watch_f20l2.py', 'watch_f20l3.py', True),
    ('idle142.py', 'idle142.py', False), ('run_safety99.py', 'run_safety99.py', False), ('launch_run.py', 'launch_run.py', False),
    ('test_guard_f20l2.py', 'test_guard_f20l3.py', True), ('test_tools_f20l2.py', 'test_tools_f20l3.py', True),
    ('regress/regress_b32.py', 'regress/regress_b32.py', True), ('mk_seal_f20l2.py', 'mk_seal_f20l3.py', True),
]


def ren(s):
    s = re.sub(r'f20l2(?![0-9a-z])', 'f20l3', s)
    s = re.sub(r'F20l2(?![0-9a-z])', 'F20l3', s)
    s = s.replace('F20L2_', 'F20L3_')
    s = s.replace('HPP-648', 'HPP-655')
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
