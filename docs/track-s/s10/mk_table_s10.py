# S10 (HPP-433): per-tag table from s10/times.txt, runs_s/lock.log and score_<tag>.txt.  ASCII only.  usage: python mk_table_s10.py
import re, hashlib
R = 'C:/kyty/s288/s10/'
TAGS = ['pi_w1', 'pi_r1', 'pi_w0', 'pi_r0', 'c5_0', 't2_1', 't2_cs0', 't2_2', 't2_3', 't2_4', 't2_5', 't2_6', 't2_7',
        'u_1', 'u_2', 'u_3', 'u_4', 'u_5']
times = open(R + 'times.txt', 'rb').read().decode('utf-8', 'replace').splitlines()
locks = open(R + 'runs_s/lock.log', 'rb').read().decode('utf-8', 'replace').splitlines()
def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()
out = ['| tag | level | lock taken - released (UTC) | outcome | sc142 | first scene frame | video frames / glitches | log sha256 | foreign CPU (whole run) |',
       '|---|---|---|---|---|---|---|---|---|']
for t in TAGS:
    tk = [l.split()[3] for l in locks if l.startswith('lock taken %s ' % t)]
    rl = [l.split()[3] for l in locks if l.startswith('lock released %s ' % t)]
    s = open(R + 'score_%s.txt' % t, 'rb').read().decode('utf-8', 'replace')
    m = re.match(r'ARM \S+ level (\S+) class \S+ form \S+: (\S+); sc142 outcome (\S+)', s)
    fi = re.search(r'first scene frame \(n, dt, draws\) \((\d+), (\d+), (\d+)\); attribution', s)
    v = re.search(r'video: (\d+) frames, (\d+) glitches', s)
    logl = [l for l in times if (' go_s9 %s enter_scene end' % t) in l]
    ls = re.search(r'sha256 ([0-9a-f]{64})', logl[-1]).group(1) if logl else '-'
    cpu = [l for l in times if (' go_s9 %s foreign cpu' % t) in l]
    c = re.search(r'= ([0-9.]+) % of', cpu[-1]).group(1) if cpu else '-'
    out.append('| `%s` | %s | %s - %s | %s | %s | %s | %s / %s | `%s` | %s %% |' % (
        t, m.group(1), tk[-1] if tk else '-', rl[-1] if rl else '-', m.group(2), m.group(3),
        '%s (dt %s us)' % (fi.group(1), fi.group(2)) if fi else '-', v.group(1) if v else '-', v.group(2) if v else '-',
        ls[:16], c))
open(R + 'table_s10.md', 'wb').write(('\n'.join(out) + '\n').encode('ascii'))
print('\n'.join(out))
print('table_s10.md sha256', sha(R + 'table_s10.md'))
