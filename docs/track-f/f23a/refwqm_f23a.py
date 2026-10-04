"""F23a (HPP-578): does the S_WQM fold of Control.cpp fire? Reference PS 0xe197e307a5f2cb39 (S_WQM_B64 exec, exec at pc 17
words) translated by the worktree binary with and without KYTY_F23A_NOWQMFOLD (which skips the fold); KYTY_PRED_DUMP
writes the IR right before and right after PredicationElimination. Equal IR and equal SPIR-V => the fold did not fire
(had it fired, EXEC after the S_WQM would be the constant true and the top-level selects would be folded before the
'before' dump). Also: the census status files of all 269 rows - SPIR-V equal with / without the knob."""
import hashlib
import json
import os
import subprocess

D = 'C:/kyty/f287/f23a/'
G = 'C:/kyty/s288/s4/gcn/g_1/ps_e197e307a5f2cb39.bin'
C = 'C:/kyty/s288/s7/cache_cur/ps_e197e307a5f2cb39_438e8f1d57f3b08b.bin'
W = D + 'work/ref/'
os.makedirs(W, exist_ok=True)
base = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
res = {}
for tag, extra in (('normal', {}), ('nowqm', {'KYTY_F23A_NOWQMFOLD': '1'})):
    e = dict(base)
    e.update(extra)
    e['KYTY_RECOMPILE'] = '%s;%s;%s;0' % (G, C, W + tag + '.spv')
    e['KYTY_PRED_DUMP'] = W + tag
    r = subprocess.run([D + 'build/shader_cfg_tests.exe'], env=e, capture_output=True, timeout=120, cwd=W)
    b = open(W + tag + '_before.txt', 'rb').read()
    a = open(W + tag + '_after.txt', 'rb').read()
    s = open(W + tag + '.spv', 'rb').read()
    res[tag] = (hashlib.sha256(b).hexdigest(), hashlib.sha256(a).hexdigest(), hashlib.sha256(s).hexdigest())
    t = b.decode('latin1')
    print('%-6s rc %d IR-before %s (%d B, SelectU32/F32 %d, WqmU64 %d, Ballot %d) IR-after %s SPIR-V %s' % (
        tag, r.returncode, res[tag][0][:16], len(b), t.count('SelectU32') + t.count('SelectF32'), t.count('WqmU64'),
        t.count('Ballot'), res[tag][1][:16], res[tag][2][:16]))
print('reference PS: IR before %s, IR after %s, SPIR-V %s' % tuple(
    'EQUAL' if res['normal'][i] == res['nowqm'][i] else 'DIFF' for i in range(3)))
sha = {}
for v in ('normal', 'nowqm'):
    for line in open(D + 'sel_%s.status.jsonl' % v, encoding='utf-8'):
        r = json.loads(line)
        if r['spv_sha']:
            sha.setdefault(r['id'], {})[v] = r['spv_sha']
both = [k for k, d in sha.items() if 'normal' in d and 'nowqm' in d]
print('census rows with SPIR-V in both variants %d, different %d' % (len(both), sum(1 for k in both if sha[k]['normal'] != sha[k]['nowqm'])))
