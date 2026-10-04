# F19a (HPP-543): for the logs with 'MainTaskLate: us=' >= 1 s printed before the first frame - the startup-wait lines
# that stand before it ('PrepareHold: ms=', 'ShaderPreparation: startup wait finished in N ms').  Reads the first
# 12 000 lines of each log ('.xz' through 'xz -dc').  Usage: python startup_f19a.py <out.txt> <log> ...
import re, subprocess, sys
o = open(sys.argv[1], 'w', encoding='utf-8', newline=chr(10))
for path in sys.argv[2:]:
    pr = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE) if path.endswith('.xz') else None
    f = pr.stdout if pr else open(path, 'rb')
    hold = wait = late = None
    for i, l in enumerate(f, 1):
        if i > 12000:
            break
        if l.startswith(b'PrepareHold: ms='):
            hold = (i, int(l.split(b'=')[1]))
        m = re.match(rb'ShaderPreparation: startup wait finished in (\d+) ms', l)
        if m:
            wait = (i, int(m.group(1)))
        m = re.match(rb'MainTaskLate: us=(\d+)', l)
        if m and int(m.group(1)) >= 1000000 and late is None:
            late = (i, int(m.group(1)))
    if pr:
        pr.kill()
    o.write('%-40s PrepareHold %s startup_wait_ms %s MainTaskLate %s late_minus_wait_ms %s\n' % (
        path.replace('C:/kyty/', ''), hold, wait, late, (late[1] // 1000 - wait[1]) if late and wait else None))
o.close()
print(open(sys.argv[1], encoding='utf-8').read())
