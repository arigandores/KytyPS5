"""M2a2 (HPP-843, ROADMAP s122 item 761(v)): members of the link from its own outputs in C:/kyty/m657/m2a2.
(1) source hash of the translator after the test = aac6db69... for main and the worktree (FS15 self-check 9177b426...);
(2) new test TestMWave1T306OffsetWriteMask: PASS on main (cfg_test.exe) at KYTY_M_T306=0 and =1; on the mutant build
    (cfg_mut.exe) FAIL at M2C_MUT=t306_mask KYTY_M_T306=1 with the 'other' check, control (M2C_MUT unset) PASS at 0 and 1.
PASS of a run = the test line printed, no 'ShaderCfgTests: failed', rc file content not needed (CONTINUE keeps rc 0).
Prints one line per member and the last line ALL OK or FAIL."""
import re

D = 'C:/kyty/m657/m2a2/'
ok = True


def member(name, cond, detail):
    global ok
    ok &= cond
    print('%s\t%s\t%s' % ('PASS' if cond else 'FAIL', name, detail))


hashes = {}
for line in open(D + 'srchash.out.txt', encoding='utf-8'):
    tree, n, h = line.split()
    hashes[tree] = h
member('(1) hash main', hashes.get('C:/kyty/KytyPS5', '').startswith('aac6db69'), hashes.get('C:/kyty/KytyPS5'))
member('(1) hash wt', hashes.get('C:/kyty/m657/m2a2/wt', '').startswith('aac6db69'), hashes.get('C:/kyty/m657/m2a2/wt'))
member('(1) self-check FS15', hashes.get('C:/kyty/m657/m2c/wt15', '').startswith('9177b426'),
       hashes.get('C:/kyty/m657/m2c/wt15'))


def run(name):
    t = open(D + name, 'rb').read().decode('utf-8', 'replace')
    ran = '[test] TestMWave1T306OffsetWriteMask' in t
    failed = [f.strip() for f in re.findall(r'ShaderCfgTests: failed: (.*)', t)]
    m = re.search(r'other: OpImageSample=(\d+) ConstOffset=(\d+)', t)
    return ran, failed, m.group(0) if m else '-'


for name, want_pass in [('run_main_t306_0.txt', True), ('run_main_t306_1.txt', True), ('run_mut_ctl_0.txt', True),
                        ('run_mut_ctl_1.txt', True), ('run_mut_t306_mask_1.txt', False)]:
    ran, failed, other = run(name)
    if want_pass:
        member('(2) PASS ' + name, ran and not failed, other)
    else:
        caught = ran and 'T306: offset written under another lane mask became a ConstOffset' in failed
        member('(2) CAUGHT ' + name, caught, other + ' ' + '; '.join(failed))
print('ALL OK' if ok else 'FAIL')
