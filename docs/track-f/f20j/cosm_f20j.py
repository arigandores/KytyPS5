# F20j: two blank lines the line-based patch could not add (CMakeLists.txt before the new target, frameStats.cpp after
# CpuCyclesPerNs). Usage: python cosm_f20j.py <root>
import os
import sys

root = sys.argv[1]
fixes = [
    ('CMakeLists.txt', '\t"${KYTY_TESTS_DIR}/F8AudioStand.cpp")\n# Track F, F20j', '\t"${KYTY_TESTS_DIR}/F8AudioStand.cpp")\n\n# Track F, F20j'),
    ('src/common/frameStats.cpp', '#endif\n}\nuint64_t ProcessCpuNs() {', '#endif\n}\n\nuint64_t ProcessCpuNs() {'),
    ('src/kernel/pthread.cpp', '\t                      : 0;\n}\nstatic bool NativeCondDeadlineFromAbs(', '\t                      : 0;\n}\n\nstatic bool NativeCondDeadlineFromAbs('),
]
ok = True
for rel, old, new in fixes:
    p = os.path.join(root, rel)
    b = open(p, 'rb').read().decode('utf-8')
    crlf = '\r\n' in b
    t = b.replace('\r\n', '\n')
    if t.count(old) != 1:
        print('FAIL', rel, t.count(old))
        ok = False
        continue
    t = t.replace(old, new)
    if crlf:
        t = t.replace('\n', '\r\n')
    open(p, 'wb').write(t.encode('utf-8'))
    print('OK', rel)
print('ALL OK' if ok else 'FAILED')
