"""F42b (HPP-780, Red Team; ROADMAP s122 item 694(g)(4), (g)(5)): own recount of a T1 corpus run (rows/<rid>/out.spv,
f20.spv, stdout.txt, rc.txt) with the independent twin twin_f42b.py:
  per row: rc 0 and the 'recompile-f20:' line; f20.spv == twin(out.spv) byte for byte (out.spv itself when the twin
  rewrites nothing); C++ named/bound/sites/rewritten/unmatched against the scan; triples after = 0; OpAtomicOr scope
  value 1 (Device) and semantics 0.
  Sums: modules_bound, modules(named), sites, rewritten, unmatched, triples before/after, loads outside a triple.
Optional second dir (reference run): out.spv sha equal row by row (translation determinism) and f20.spv sha equal.
Mutant mode (--mutant): prints CAUGHT <members> / NOT CAUGHT instead of ALL OK / FAIL.
Usage: python rc_corpus_f42b.py <corpus dir> [<reference corpus dir>] [--mutant]"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twin_f42b as t  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
D = args[0]
REF = args[1] if len(args) > 1 else None
MUT = '--mutant' in sys.argv
LINE = re.compile(rb'recompile-f20: bound=(\d) named=(\d+) sites=(\d+) rewritten=(\d+) unmatched=(\d+) malformed=(\d)')
fails = {}


def bad(name, rid):
    fails.setdefault(name, []).append(rid)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


s = dict(rows=0, bound=0, named=0, sites=0, rewritten=0, unmatched=0, tri_before=0, tri_after=0, loads_out=0,
         rows_rw=0, ps_bound=0, sha_base_eq=0, sha_f20_eq=0)
for rid in sorted(os.listdir(D + '/rows')):
    w = '%s/rows/%s' % (D, rid)
    s['rows'] += 1
    rc = open(w + '/rc.txt').read().strip() if os.path.exists(w + '/rc.txt') else '?'
    m = LINE.search(open(w + '/stdout.txt', 'rb').read()) if os.path.exists(w + '/stdout.txt') else None
    if rc != '0' or m is None:
        bad('rc or line', rid)
        continue
    bound, named, sites, rewritten, unmatched, malformed = (int(x) for x in m.groups())
    base, new = t.read_spv(w + '/out.spv'), t.read_spv(w + '/f20.spv')
    sb, sn = t.scan(base), t.scan(new)
    tw, ts, tr = t.twin(base, bound=True)
    expect = tw if tw is not None else base
    if expect != new:
        bad('f20 != twin(out)', rid)
    if sb['named'] != named:
        bad('scan named != C++ named', rid)
    if bound != (1 if sb['named'] > 0 else 0):
        bad('bound != named', rid)
    if sb['triples'] != rewritten or sites != sb['triples']:
        bad('rewritten/sites != triples', rid)
    if sn['triples'] != 0:
        bad('triples after', rid)
    if unmatched != 0:
        bad('unmatched', rid)
    if sn['atomics_or'] and (sn['atomic_scopes'] != {1} or sn['atomic_sems'] != {0}):
        bad('scope/semantics', rid)
    if sn['atomics_xor']:
        bad('OpAtomicXor on fault_buffer', rid)
    s['bound'] += bound
    s['named'] += 1 if named > 0 else 0
    s['sites'] += sites
    s['rewritten'] += rewritten
    s['unmatched'] += unmatched
    s['tri_before'] += sb['triples']
    s['tri_after'] += sn['triples']
    s['loads_out'] += sb['loads_fb'] - sb['triples']
    s['rows_rw'] += 1 if rewritten else 0
    s['ps_bound'] += 1 if (bound and rid.startswith('ps_')) else 0
    if REF:
        r = '%s/rows/%s' % (REF, rid)
        s['sha_base_eq'] += sha(r + '/out.spv') == sha(w + '/out.spv')
        s['sha_f20_eq'] += sha(r + '/f20.spv') == sha(w + '/f20.spv')
print(' '.join('%s=%d' % kv for kv in s.items()))
for k, v in fails.items():
    print('FAIL %s %d %s' % (k, len(v), v[:5]))
if MUT:
    print('CAUGHT ' + ' | '.join(fails) if fails else 'NOT CAUGHT')
else:
    if REF and (s['sha_base_eq'] != s['rows'] or s['sha_f20_eq'] != s['rows']):
        print('FAIL reference sha')
        fails['ref'] = 1
    print('ALL OK' if not fails else 'FAIL')
