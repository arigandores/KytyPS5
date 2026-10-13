"""M6a (HPP-848): the stand of KYTY_DIAG_M5W2 - tests/MWave2DiagStand.cpp (from draft/) and its CMake target
m_wave2_diag_stand (EXCLUDE_FROM_ALL, no add_test) after m_wave1_hle_stand. Usage: python patch_m6a_stand.py <repo root>.
Whole-line anchor once; LF; lock and STOP checked first. Prints ALL OK / FAIL."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)

ROOT = sys.argv[1]
NL = chr(10)
ok = True

dst = os.path.join(ROOT, 'tests', 'MWave2DiagStand.cpp')
if os.path.exists(dst):
    print('FAIL tests/MWave2DiagStand.cpp exists')
    ok = False
else:
    data = open('C:/kyty/m657/m6a/draft/MWave2DiagStand.cpp', 'rb').read().replace(b'\r\n', b'\n')
    open(dst, 'wb').write(data)
    print('OK   new tests/MWave2DiagStand.cpp (%d bytes)' % len(data))

path = os.path.join(ROOT, 'CMakeLists.txt')
text = open(path, 'rb').read().decode('utf-8').replace('\r\n', NL)
anchor = 'add_kyty_full_emulator_test(m_wave1_hle_stand "${KYTY_TESTS_DIR}/MWave1HleStand.cpp")'
n = text.count(NL + anchor + NL)
if n != 1:
    print('FAIL CMakeLists.txt anchor x%d' % n)
    ok = False
else:
    add = [anchor, '',
           '# Track M, M6a (HPP-848, ROADMAP s122 item 767(i)): stand of the measurement-only knob KYTY_DIAG_M5W2 and of the',
           '# signature lines of T031, T309, T023; run by C:/kyty/m657/m6a/run_stand_m6a.py, not by ctest.',
           'add_kyty_full_emulator_test(m_wave2_diag_stand "${KYTY_TESTS_DIR}/MWave2DiagStand.cpp")']
    text = text.replace(NL + anchor + NL, NL + NL.join(add) + NL, 1)
    open(path, 'wb').write(text.encode('utf-8'))
    print('OK   CMakeLists.txt: m_wave2_diag_stand')

print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
