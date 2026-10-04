# F15c (HPP-514, ROADMAP s122 item 412(v)): the B4 stand target b4_race_stand in main - one CMake line after the
# kernel_file_system_tests target (form of docs/track-f/f15a/patch_wt_f15a.py). add_kyty_full_emulator_test makes an
# EXCLUDE_FROM_ALL executable; no add_test and no kyty_tests dependency - the stand is outside the default ctest set.
# Anchor - whole lines; CR kept as found; fails when the anchor is not found once. Usage: python patch_f15c_cmake.py <repo root>
import sys

path = sys.argv[1] + '/CMakeLists.txt'
data = open(path, 'rb').read()
crlf = b'\r\n' in data
text = data.replace(b'\r\n', b'\n').decode('utf-8')
lines = text.split('\n')
anchor = ['add_kyty_full_emulator_test(kernel_file_system_tests', '\t"${KYTY_TESTS_DIR}/KernelFileSystemTests.cpp")']
hits = [i for i in range(len(lines) - 1) if lines[i] == anchor[0] and lines[i + 1] == anchor[1]]
if len(hits) != 1:
    print('ANCHOR hits', len(hits))
    sys.exit(1)
i = hits[0] + 2
add = ['',
       '# Track F, B4 exit race stand (F15a, F15c; ROADMAP s122 item 412(v)): run by docs/track-f/f15c/run_stand_f15c.py,',
       '# not by ctest.',
       'add_kyty_full_emulator_test(b4_race_stand',
       '\t"${KYTY_TESTS_DIR}/B4RaceStand.cpp")']
lines[i:i] = add
out = '\n'.join(lines).encode('utf-8')
if crlf:
    out = out.replace(b'\n', b'\r\n')
open(path, 'wb').write(out)
print('PATCH OK line', i + 1, 'crlf', crlf)
