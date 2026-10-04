# F15d (HPP-515): mutants of the worktree src/kernel/fileSystem.cpp (5c2c5e52) for item 412(d) "own mutant (=1 with delete)".
#   M1 - the =1 branch of EmergencyShutdown calls CloseAll (Close + delete + nullptr) instead of FlushAll.
#   M2 - FlushAll (=1) deletes every File without Close and without writing nullptr (use-after-free, no EXIT_IF).
#   restore - git checkout of the file.
# Anchors are whole lines; the file is LF (the worktree has 0 CR in src/).
import sys, subprocess
P = 'C:/kyty/f287/f15d/wt/src/kernel/fileSystem.cpp'
G = 'C:/Program Files/Git/cmd/git.exe'
mode = sys.argv[1]
if mode == 'restore':
    subprocess.check_call([G, '-C', 'C:/kyty/f287/f15d/wt', 'checkout', '--', 'src/kernel/fileSystem.cpp'])
    print(subprocess.check_output([G, '-C', 'C:/kyty/f287/f15d/wt', 'status', '--short']).decode() or 'clean')
    sys.exit(0)
b = open(P, 'rb').read()
assert b'\r' not in b
lines = b.decode('utf-8').split(chr(10))
def one(text):
    idx = [i for i, l in enumerate(lines) if l == text]
    assert len(idx) == 1, (text, idx)
    return idx[0]
if mode == 'M1':
    i = one(chr(9) * 3 + 'g_files->FlushAll();')
    lines[i] = chr(9) * 3 + 'g_files->CloseAll(); // F15d mutant M1'
elif mode == 'M2':
    i = one('void FileDescriptors::FlushAll() {')
    T = chr(9)
    lines[i + 1:i + 1] = [T + 'for (auto* f: m_files) { // F15d mutant M2: delete without Close and without nullptr',
                          T + T + 'delete f;', T + '}']
else:
    sys.exit('mode?')
open(P, 'wb').write(chr(10).join(lines).encode('utf-8'))
print(subprocess.check_output([G, '-C', 'C:/kyty/f287/f15d/wt', 'diff']).decode())
