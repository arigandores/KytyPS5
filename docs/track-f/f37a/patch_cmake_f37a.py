"""F37a (HPP-761): add the CMake target f25_read_fail_stand after b4_race_stand. Usage: patch_cmake_f37a.py <repo root>"""
import sys

path = sys.argv[1].rstrip('/') + '/CMakeLists.txt'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
anchor = 'add_kyty_full_emulator_test(b4_race_stand\n\t"${KYTY_TESTS_DIR}/B4RaceStand.cpp")\n'
assert text.count(anchor) == 1, 'anchor count %d' % text.count(anchor)
add = ('\n# Track F, F25 double read failure stand (F37a HPP-761; ROADMAP s122 item 688(e)): ReadFile import hook of the test\n'
       '# executable, arms A/K/Z over six read entries; run by docs/track-f/f37a/run_stand_f37a.py, not by ctest.\n'
       'add_kyty_full_emulator_test(f25_read_fail_stand\n\t"${KYTY_TESTS_DIR}/F25ReadFailStand.cpp")\n')
assert 'f25_read_fail_stand' not in text
text = text.replace(anchor, anchor + add)
if crlf:
    text = text.replace('\n', '\r\n')
open(path, 'wb').write(text.encode('utf-8'))
print('patched', path, 'crlf' if crlf else 'lf')
