"""F33d (HPP-745): mutants of KYTY_FIX_F21 (ROADMAP s122 item 675(d)(3)) on the F33d worktree file
src/common/subsystems.cpp (tree of 0c57cfed). usage: mut_f33d.py <wt> <m1|m2|m3|m4a|m4b>
Each mutant replaces exactly one anchor (whole lines, asserted count 1); the file is LF (CR stripped and restored).
  m1  - a non-owner also walks (after the re-entry branch: walk and return)
  m2  - a non-owner returns without waiting (after the re-entry branch: return)
  m3  - the wait has no limit (the expiry test never fires)
  m4a - re-entry of the owner thread is not recognised (the branch with its event is disabled; the entry falls to
        the done / wait path)
  m4b - re-entry of the owner thread reports the event but does not return (falls to the done / wait path)
"""
import sys

wt, m = sys.argv[1], sys.argv[2]
path = wt + '/src/common/subsystems.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')

REENTER = ('\tif (owner == self) {\n'
           '\t\t// Re-entry of the owner thread (DbgExit after DbgReport, a fatal inside an emergency callback): no nested walk.\n'
           '\t\tif (hook != nullptr) {\n'
           '\t\t\thook(kEmergencyReenter, 0, 0);\n'
           '\t\t}\n'
           '\t\treturn;\n'
           '\t}\n')
EXPIRE = '\t\tif (now >= limit) {\n'

if m == 'm1':
    old, new = REENTER, REENTER + '\tactive->EmergencyWalkF21(hook); // MUTANT m1\n\treturn;\n'
elif m == 'm2':
    old, new = REENTER, REENTER + '\treturn; // MUTANT m2\n'
elif m == 'm3':
    old, new = EXPIRE, '\t\tif (false && now >= limit) { // MUTANT m3\n'
elif m == 'm4a':
    old, new = REENTER, REENTER.replace('\tif (owner == self) {\n', '\tif (false && owner == self) { // MUTANT m4a\n')
elif m == 'm4b':
    old, new = REENTER, REENTER.replace('\t\treturn;\n\t}\n', '\t\t// MUTANT m4b: no return\n\t}\n')
else:
    sys.exit('bad mutant ' + m)
assert t.count(old) == 1, ('anchor count', t.count(old))
t = t.replace(old, new)
assert 'MUTANT ' + m in t
if crlf:
    t = t.replace('\n', '\r\n')
open(path, 'wb').write(t.encode('utf-8'))
print('applied', m, 'crlf', crlf)
