# FS12b (HPP-751, Red Team, general rule 24(1)): the <commit>:<path>:<line> references of docs/track-f/fs12b-review.md - each
# by its anchor (whole line, stripped) and the +1 control line; the anchor must be unique in the file. Negative control: the
# same check at line+1 must fail for every reference. Port of my refs_fs11b.py with a commit per reference.
# Prints the references and REFS <n> ALL OK / FAILED.
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
BS = chr(92)
REFS = [
    ('730ed40a', 'src/common/subsystems.cpp', 'const char* value = std::getenv("KYTY_FIX_F21");',
     "g_fix_f21  = value == nullptr || value[0] == '" + BS + "0' || EnvValueOn(value);"),
    ('730ed40a', 'src/common/subsystems.cpp', 'if (g_f21_path) [[unlikely]] { // F33c: KYTY_FIX_F21=1 or the stand KYTY_TEST_EXITFATAL armed',
     'EmergencyShutdownActiveF21();'),
    ('730ed40a', 'src/common/subsystems.cpp', 'if (!g_fix_f21) {',
     '// KYTY_FIX_F21=0 with the stand armed: the FS11 sequence - every entry walks - observed.'),
    ('730ed40a', 'src/emulator.cpp', 'const char* value = std::getenv("KYTY_TEST_EXITFATAL");', "if (value == nullptr || value[0] == '" + BS + "0') {"),
    ('730ed40a', 'src/emulator.cpp',
     'ExitFatalStand::Parse(); // F33c stand KYTY_TEST_EXITFATAL (off when unset): the observer is set before the knob',
     'Common::Subsystems::InitFixF21();'),
    ('730ed40a', 'src/emulator.cpp', 'if (!ExitFatalStand::Armed()) {', 'subsystems.Initialize<Libs::Graphics::Lifecycle>();'),
    ('ee9632be', 'src/common/subsystems.cpp', 'void Subsystems::EmergencyShutdownActive() {', 'if (g_active_subsystems != nullptr) {'),
]
ok = True
neg_ok = True
for c, path, anchor, nxt in REFS:
    lines = subprocess.run([G, '-C', REPO, 'show', c + ':' + path], capture_output=True).stdout.decode('utf-8').split('\n')
    hits = [i for i, l in enumerate(lines) if l.strip() == anchor]
    if len(hits) != 1:
        print('FAIL anchor not unique/absent', c, path, anchor, hits)
        ok = False
        continue
    i = hits[0]
    nxt_line = lines[i + 1].strip() if i + 1 < len(lines) else None
    good = nxt is None or nxt_line == nxt
    print(('OK   ' if good else 'FAIL ') + '%s:%s:%d  anchor <<%s>>  +1 <<%s>>' % (c, path, i + 1, anchor, nxt if nxt is not None else nxt_line))
    ok &= good
    if lines[i + 1].strip() == anchor:
        neg_ok = False
print('negative control (shift +1 never matches):', 'FAILED as expected' if neg_ok else 'DID NOT FAIL')
print('REFS %d %s' % (len(REFS), 'ALL OK' if ok and neg_ok else 'FAILED'))
sys.exit(0 if ok and neg_ok else 1)
