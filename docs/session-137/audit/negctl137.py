# negctl137.py - negative control of test_recount137.py: each mutant of recount137.py must make the suite fail.
import subprocess, sys, os, tempfile
src = open('C:/kyty/s137/audit137/recount137.py', encoding='utf-8').read()
tst = open('C:/kyty/s137/audit137/test_recount137.py', encoding='utf-8').read()
MUT = [('W_LO, W_HI = 10, 88', 'W_LO, W_HI = 9, 88'), ('W_LO, W_HI = 10, 88', 'W_LO, W_HI = 10, 89'), ('K_RUN = 32', 'K_RUN = 31'),
       ('len(tn) > 3', 'len(tn) > 4'), ("abs(ss[-1]) > K_RUN))", "abs(ss[-1]) > K_RUN + 1))"),
       ("'(0,1)' if byb[k]['arm'] == 0 else '(1,0)'", "'(0,1)'"), ('for i in range(L - 1) if ov[i] and ov[i + 1]', 'for i in range(L - 1) if ov[i] and ov[i + 1] and False')]
tmp = tempfile.mkdtemp(dir=os.environ.get('PAPERCLIP_RUN_SCRATCH_DIR') or None).replace(chr(92), '/')
bad = 0
for a, b in MUT:
    assert src.count(a) >= 1, a
    open(tmp + '/recount137.py', 'w', encoding='utf-8').write(src.replace(a, b, 1))
    open(tmp + '/t.py', 'w', encoding='utf-8').write(tst.replace("C:/kyty/s137/audit137')", tmp + "')", 1).replace(
        "tgt = 'C:/kyty/s137/audit137/recount137.py'", "tgt = '" + tmp + "/recount137.py'"))
    r = subprocess.run([sys.executable, tmp + '/t.py'], capture_output=True, text=True)
    killed = r.returncode != 0
    bad += 0 if killed else 1
    print('%s  %s -> %s' % ('KILLED ' if killed else 'SURVIVED', a, b))
print('mutants %d killed %d survived %d' % (len(MUT), len(MUT) - bad, bad))
