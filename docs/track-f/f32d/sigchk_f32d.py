# F32d (HPP-742): signatures of the 36 out-of-mask logs (sweep_f32a.py agg, OUT=<f32d sweep>) that are new against F0 AND
# against the F32a delta (sig_f32a.tsv of F32a), plus the record list of the sweep: build, lines, dup / in_f0 / equal to an F32a log.
# Usage: python sigchk_f32d.py <f32a_out> <f32d_sweep_out>     (last line ALL OK when every record is read and the check ran)
import sys, json
TAB = chr(9)


def sigs(p):
    s = {}
    with open(p, encoding='utf-8') as f:
        f.readline()
        for l in f:
            x = l.rstrip(chr(10)).split(TAB)
            s[x[8]] = x
    return s


A, D = sys.argv[1:3]
a = sigs(A + '/sig_f32a.tsv')
d = sigs(D + '/sig_f32a.tsv')
nn = [k for k in d if d[k][2] == 'NEW' and k not in a]
print('signatures F32a', len(a), 'out-of-mask', len(d), 'new vs F0', sum(1 for k in d if d[k][2] == 'NEW'),
      'new vs F0 and F32a', len(nn))
for k in nn:
    print('  NEW', d[k][0], d[k][1], d[k][6], k[:160])
ra = json.load(open(A + '/agg_f32a.json', encoding='utf-8'))
rd = json.load(open(D + '/agg_f32a.json', encoding='utf-8'))
sa = {r['sha256']: r['path'] for r in ra if not r['dup_of'] and not r['in_f0']}
for r in rd:
    st = 'in_F0' if r['in_f0'] else ('dup ' + r['dup_of'] if r['dup_of'] else ('= F32a ' + sa[r['sha256']] if r['sha256'] in sa else 'unique new'))
    print('  %s %s lines %d %s' % (r['path'], r['build'], r['lines'], st))
print('records', len(rd), 'unique new', sum(1 for r in rd if not r['dup_of'] and not r['in_f0'] and r['sha256'] not in sa))
print('ALL OK' if len(rd) == 36 else 'FAILED')
