"""F23a (HPP-578): positive / zero control of the REAL decoder pass - synthetic programs (same words as gcn_f23a.py
--synthetic) written to C:/kyty/f287/f23a/synth/*.bin and decoded by the worktree binary (KYTY_F23A_DECODE); expected:
'U' lines exactly in the pos_* programs, none in zero_*; prints ALL OK."""
import os
import struct
import subprocess
import sys

D = 'C:/kyty/f287/f23a/'
BIN = D + 'build/shader_cfg_tests.exe'
endpgm = 0xBF810000
v_mul_f32 = (0x08 << 25) | (1 << 17) | (2 << 9) | 256 | 3
v_mul_legacy = (0x07 << 25) | (1 << 17) | (2 << 9) | 256 | 3
v_fmac_legacy = (0x06 << 25) | (1 << 17) | (2 << 9) | 256 | 3
vop3_mul_legacy = [(0x35 << 26) | ((0x100 + 0x07) << 16) | 1, (256 + 3) | ((256 + 2) << 9)]
cases = {
    'zero_clean': [v_mul_f32, v_mul_f32, endpgm],
    'pos_vop2_mul_legacy': [v_mul_f32, v_mul_legacy, endpgm],
    'pos_vop2_fmac_legacy': [v_fmac_legacy, endpgm],
    'pos_vop3_mul_legacy': vop3_mul_legacy + [endpgm],
    'pos_after_branch_dead': [0xBF820001, v_mul_legacy, endpgm],
    'zero_after_endpgm': [v_mul_f32, endpgm, v_mul_legacy],
    'pos_fwd_target_after_endpgm': [0xBF850001, endpgm, v_mul_legacy, endpgm],
}
os.makedirs(D + 'synth', exist_ok=True)
paths = []
for k, ws in cases.items():
    fp = D + 'synth/%s.bin' % k
    open(fp, 'wb').write(struct.pack('<%dI' % len(ws), *ws))
    paths.append(fp)
lst = D + 'synth/list.txt'
out = D + 'synth/dec_synth.txt'
open(lst, 'w', newline=chr(10)).write(chr(10).join(paths) + chr(10))
if os.path.exists(out):
    os.remove(out)
env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
env['KYTY_F23A_DECODE'] = '%s;%s;0' % (lst, out)
r = subprocess.run([BIN], env=env, capture_output=True, timeout=120)
print('rc', r.returncode)
cur = None
got = {}
for line in open(out, encoding='utf-8', errors='replace'):
    if line.startswith('P '):
        cur = os.path.basename(line.split()[2])[:-4]
        got[cur] = []
    elif line.startswith('U '):
        got[cur].append(line.strip()[2:])
ok = True
for k in cases:
    exp = k.startswith('pos_')
    good = k in got and (len(got[k]) > 0) == exp
    ok &= good
    print('%-28s U lines %d %s %s' % (k, len(got.get(k, [])), 'ok' if good else 'FAIL', (got.get(k) or [''])[0][:150]))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
