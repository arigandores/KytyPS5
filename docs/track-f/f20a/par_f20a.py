# F20a (HPP-551; form of f19a/par_f19a.py): runs N copies of sweep_f20a.py on N parts of a list (round-robin split, each
# part keeps the order) and waits for them; the parts and the outputs are <list>.p<i> and <out>.p<i>.  Meant to be started
# under watch_f20a.py - the copies are direct children of this process, so the watchdog's tree kill reaches them.
# The split is made once: existing parts are kept (a resumed run reads the same parts).
# Usage: python par_f20a.py <list.tsv> <out.jsonl> <budget_s> <N>
import os, subprocess, sys

lst, out, budget, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
here = os.path.dirname(os.path.abspath(__file__))
lines = [l for l in open(lst, encoding='utf-8') if l.strip()]
procs = []
for i in range(n):
    part = '%s.p%d' % (lst, i)
    if not os.path.exists(part):
        with open(part, 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(lines[i::n])
    procs.append(subprocess.Popen([sys.executable, os.path.join(here, 'sweep_f20a.py'), part, '%s.p%d' % (out, i), budget],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
rc = 0
complete = 0
for i, p in enumerate(procs):
    o = p.communicate()[0]
    rc |= p.returncode
    complete += 'SWEEP COMPLETE' in o
    print('p%d rc %d: %s' % (i, p.returncode, ' | '.join(o.strip().split('\n')[-3:])))
print('PAR COMPLETE' if complete == n else 'PAR NOT COMPLETE %d of %d' % (complete, n))
sys.exit(rc)
