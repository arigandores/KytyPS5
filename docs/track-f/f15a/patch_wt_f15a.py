# F15a (HPP-491, ROADMAP s122 item 400(d)(2)): adds the B4 stand to the F15a worktree only (not main):
# copies B4RaceStand.cpp to <wt>/tests/ and appends one CMake line after the kernel_file_system_tests target.
# Anchor - whole lines; LF kept (the worktree is LF, core.autocrlf=false); fails when the anchor is not found once.
import shutil, sys

wt = sys.argv[1]
src = sys.argv[2]
shutil.copyfile(src, wt + '/tests/B4RaceStand.cpp')
path = wt + '/CMakeLists.txt'
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
       '# Track F, F15a (ROADMAP s122 item 400(d)(2), B4): exit race stand, F15a worktree only.',
       'add_kyty_full_emulator_test(b4_race_stand',
       '\t"${KYTY_TESTS_DIR}/B4RaceStand.cpp")']
lines[i:i] = add
out = '\n'.join(lines).encode('utf-8')
if crlf:
    out = out.replace(b'\n', b'\r\n')
open(path, 'wb').write(out)
print('PATCH OK line', i + 1, 'crlf', crlf)
