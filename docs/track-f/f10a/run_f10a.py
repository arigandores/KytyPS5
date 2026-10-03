"""Track F, link F10a (HPP-445), ROADMAP s122 item 366(d): offline test of ValidateShaderSpirv.

Input: T1 base C:/kyty/s288/s7/t1_base.tsv and the pass-A SPIR-V that S7 left in
C:/kyty/s288/s7/work/A/A_<hash16>_<key16>_<perm>/out.spv (sha256 checked against spv_sha256_a).
Sets:
  S151 - rows A, stage ps, rc_spirv_val_vk13=1, rc_spirv_val_dev=0, identical_stored=1 (the Ф16 set);
  K4PS - rows A, stage ps, rc_spirv_val_vk13=0 (PS of the base that the SDK accepts in form vulkan1.3);
  K4CS - rows A, stage cs, rc_spirv_val_vk13=0 (supplement to k4, not in the letter of item 366(d)).
Per shader: SDK spirv-val 1.4.357 '--target-env vulkan1.3' (k1) and the same with
'--uniform-buffer-standard-layout' (k2); sval_f10a.exe: ValidateShaderSpirv compiled from the extracted
body (built-in) and control k3 (same env, ValidatorOptions::SetUniformBufferStandardLayout(true)).
Writes f10a_out.tsv (one line per shader), f10a_summary.txt; ASCII output only. No game, no device.
"""
import csv
import hashlib
import os
import subprocess
import sys

S7 = 'C:/kyty/s288/s7'
BASE = S7 + '/t1_base.tsv'
OUT = 'C:/kyty/f287/f10a'
TOOL = OUT + '/sval_f10a.exe'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def one_line(b):
    t = b.decode('latin1').replace('\r', '')
    parts = [x.strip() for x in t.split('\n') if x.strip()]
    return ' | '.join(parts).replace('\t', ' ')


def halt_check():
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(3)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)


rows = list(csv.DictReader(open(BASE, encoding='ascii'), delimiter='\t'))
sets = []
for r in rows:
    if r['row'] != 'A':
        continue
    if r['stage'] == 'ps' and r['rc_spirv_val_vk13'] == '1' and r['rc_spirv_val_dev'] == '0' and r['identical_stored'] == '1':
        sets.append(('S151', r))
    elif r['stage'] == 'ps' and r['rc_spirv_val_vk13'] == '0':
        sets.append(('K4PS', r))
    elif r['stage'] == 'cs' and r['rc_spirv_val_vk13'] == '0':
        sets.append(('K4CS', r))

items = []
bad_sha = 0
for s, r in sets:
    rid = '%s_%s_%s' % (r['hash16'], r['key16'], r['perm'])
    p = '%s/work/A/A_%s/out.spv' % (S7, rid)
    sha = sha256_file(p) if os.path.exists(p) else 'MISSING'
    if sha != r['spv_sha256_a']:
        bad_sha += 1
    items.append({'set': s, 'id': rid, 'stage': r['stage'], 'path': p, 'sha': sha, 'base_sha': r['spv_sha256_a'],
                  'base_vk13': r['rc_spirv_val_vk13'], 'base_dev': r['rc_spirv_val_dev']})

halt_check()
ver = subprocess.run([SPIRV_VAL, '--version'], capture_output=True)
sdk_version = one_line(ver.stdout + ver.stderr)
for it in items:
    halt_check()
    v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', it['path']], capture_output=True)
    it['k1_rc'], it['k1_msg'] = v.returncode, one_line(v.stderr + v.stdout)
    v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', it['path']],
                       capture_output=True)
    it['k2_rc'], it['k2_msg'] = v.returncode, one_line(v.stderr + v.stdout)

listing = OUT + '/f10a_list.tsv'
with open(listing, 'wb') as f:
    for it in items:
        f.write(('%s\t%s\n' % (it['id'], it['path'])).encode('ascii'))
halt_check()
t = subprocess.run([TOOL, listing], capture_output=True)
open(OUT + '/sval_f10a.stdout.txt', 'wb').write(t.stdout)
open(OUT + '/sval_f10a.stderr.txt', 'wb').write(t.stderr)
tool_version = ''
by_id = {}
count = None
for line in t.stdout.decode('latin1').replace('\r', '').split('\n'):
    if not line:
        continue
    f = line.split('\t')
    if f[0] == '#spirv-tools':
        tool_version = f[1]
    elif f[0] == '#count':
        count = int(f[1])
    else:
        by_id[f[0]] = f
for it in items:
    f = by_id[it['id']]
    it['words'], it['builtin'], it['builtin_msg'], it['k3'], it['k3_msg'] = f[1], f[2], f[3], f[4], f[5]

cols = ['set', 'stage', 'hash16_key16_perm', 'spv_sha256', 'words', 'sdk_vk13_rc', 'sdk_vk13_msg',
        'sdk_vk13_ubsl_rc', 'sdk_vk13_ubsl_msg', 'builtin', 'builtin_msg', 'builtin_ubsl', 'builtin_ubsl_msg']
with open(OUT + '/f10a_out.tsv', 'wb') as f:
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for it in items:
        vals = [it['set'], it['stage'], it['id'], it['sha'], it['words'], str(it['k1_rc']), it['k1_msg'],
                str(it['k2_rc']), it['k2_msg'], it['builtin'], it['builtin_msg'], it['k3'], it['k3_msg']]
        f.write(('\t'.join(vals) + '\n').encode('ascii', 'replace'))


def sel(s):
    return [it for it in items if it['set'] == s]


S = sel('S151')
K4PS = sel('K4PS')
K4CS = sel('K4CS')
out = []
out.append('F10a (HPP-445) summary; ROADMAP s122 item 366(d)')
out.append('tool SPIRV-Tools: %s' % tool_version)
out.append('SDK spirv-val: %s' % sdk_version)
out.append('sets: S151 %d, K4PS %d, K4CS %d; spv sha256 != base: %d; tool count %s, tool rc %d'
           % (len(S), len(K4PS), len(K4CS), bad_sha, count, t.returncode))
k1 = sum(it['k1_rc'] != 0 for it in S)
k2 = sum(it['k2_rc'] == 0 for it in S)
k3 = sum(it['k3'] == 'ACCEPT' for it in S)
k4ps_sdk = [it for it in K4PS if it['k1_rc'] == 0]
k4ps = sum(it['builtin'] == 'ACCEPT' for it in k4ps_sdk)
k4cs_sdk = [it for it in K4CS if it['k1_rc'] == 0]
k4cs = sum(it['builtin'] == 'ACCEPT' for it in k4cs_sdk)
rej = sum(it['builtin'] == 'REJECT' for it in S)
acc = sum(it['builtin'] == 'ACCEPT' for it in S)
out.append('k1 SDK vulkan1.3 rejects: %d of %d' % (k1, len(S)))
out.append('k2 SDK vulkan1.3 + ubsl accepts: %d of %d' % (k2, len(S)))
out.append('k3 built-in env + SetUniformBufferStandardLayout accepts: %d of %d' % (k3, len(S)))
out.append('k4 PS of the base accepted by SDK vulkan1.3: %d (letter: >= 10); built-in accepts %d of them'
           % (len(k4ps_sdk), k4ps))
out.append('k4 supplement CS accepted by SDK vulkan1.3: %d; built-in accepts %d of them' % (len(k4cs_sdk), k4cs))
out.append('built-in ValidateShaderSpirv on S151: REJECT %d, ACCEPT %d' % (rej, acc))
msgs = {}
for it in S:
    if it['builtin'] == 'REJECT':
        m = it['builtin_msg']
        # message text without the position prefix and the struct id, for grouping
        key = m.split(') ', 1)[1] if ') ' in m else m
        key = ' '.join(w if not w.isdigit() else '<n>' for w in key.split(' '))[:160]
        msgs[key] = msgs.get(key, 0) + 1
for k, v in sorted(msgs.items(), key=lambda kv: -kv[1]):
    out.append('  built-in reject message x%d: %s' % (v, k))
text = '\n'.join(out) + '\n'
open(OUT + '/f10a_summary.txt', 'wb').write(text.encode('ascii', 'replace'))
sys.stdout.write(text)
