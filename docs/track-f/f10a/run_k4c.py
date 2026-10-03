"""F10a (HPP-445): control k4 extended within the T1 base - stored SPIR-V of the base rows C (stage ps,
outcome NO_GCN: translation cache files of the current signature 56189185 whose GCN was not dumped).

The stored SPIR-V is taken from the translation cache file C:/kyty/s288/s7/cache_cur/<stage>_<hash16>_<key16>.bin:
each module is '<u32 word count N><N words starting with the magic 0x07230203>'; modules are taken in file
order (permutation index = order), the scan continues after the end of each module. Calibration [c]:
on every base row A (stages ps and cs) the module of index perm must have the sha256 spv_sha256_a of the
row (pass-A output = stored, identical_stored=1); any mismatch stops the script.
Then for the rows C ps: SDK spirv-val '--target-env vulkan1.3' and '+ --uniform-buffer-standard-layout',
and sval_f10a.exe (built-in ValidateShaderSpirv, control k3). Writes k4c/*.spv, f10a_k4c.tsv,
f10a_k4c_summary.txt. ASCII output only.
"""
import csv
import hashlib
import os
import struct
import subprocess
import sys

S7 = 'C:/kyty/s288/s7'
BASE = S7 + '/t1_base.tsv'
CACHE = S7 + '/cache_cur'
OUT = 'C:/kyty/f287/f10a'
TOOL = OUT + '/sval_f10a.exe'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
MAGIC = struct.pack('<I', 0x07230203)


def modules(path):
    d = open(path, 'rb').read()
    out = []
    pos = 0
    while True:
        i = d.find(MAGIC, pos)
        if i < 4:
            if i < 0:
                break
            pos = i + 4
            continue
        n = struct.unpack_from('<I', d, i - 4)[0]
        if n >= 5 and i + 4 * n <= len(d):
            out.append(d[i:i + 4 * n])
            pos = i + 4 * n
        else:
            pos = i + 4
    return out


def one_line(b):
    t = b.decode('latin1').replace('\r', '')
    return ' | '.join(x.strip() for x in t.split('\n') if x.strip()).replace('\t', ' ')


for p in ('C:/kyty/SEALED_RUN.lock', 'C:/kyty/f287/STOP'):
    if os.path.exists(p):
        print('HALT', p)
        sys.exit(3)

rows = list(csv.DictReader(open(BASE, encoding='ascii'), delimiter='\t'))
cal_ok = cal_bad = 0
for r in rows:
    if r['row'] != 'A' or r['stage'] not in ('ps', 'cs'):
        continue
    m = modules('%s/%s_%s_%s.bin' % (CACHE, r['stage'], r['hash16'], r['key16']))
    perm = int(r['perm'])
    if perm < len(m) and hashlib.sha256(m[perm]).hexdigest() == r['spv_sha256_a']:
        cal_ok += 1
    else:
        cal_bad += 1
print('calibration rows A (ps, cs): module[perm] sha256 == spv_sha256_a: %d, mismatch %d' % (cal_ok, cal_bad))
if cal_bad:
    print('FAIL calibration')
    sys.exit(1)

os.makedirs(OUT + '/k4c', exist_ok=True)
items = []
for r in rows:
    if r['row'] != 'C' or r['stage'] != 'ps':
        continue
    path = '%s/%s_%s_%s.bin' % (CACHE, r['stage'], r['hash16'], r['key16'])
    m = modules(path)
    perm = int(r['perm'])
    rid = '%s_%s_%s' % (r['hash16'], r['key16'], r['perm'])
    if perm >= len(m):
        items.append({'id': rid, 'path': None, 'sha': 'NO_MODULE', 'nmod': len(m)})
        continue
    spv = '%s/k4c/C_%s.spv' % (OUT, rid)
    open(spv, 'wb').write(m[perm])
    items.append({'id': rid, 'path': spv, 'sha': hashlib.sha256(m[perm]).hexdigest(), 'nmod': len(m),
                  'cache_sha_ok': hashlib.sha256(open(path, 'rb').read()).hexdigest() == r['cache_sha256']})

for it in items:
    if not it['path']:
        continue
    v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', it['path']], capture_output=True)
    it['k1_rc'], it['k1_msg'] = v.returncode, one_line(v.stderr + v.stdout)
    v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', it['path']],
                       capture_output=True)
    it['k2_rc'], it['k2_msg'] = v.returncode, one_line(v.stderr + v.stdout)

listing = OUT + '/f10a_k4c_list.tsv'
with open(listing, 'wb') as f:
    for it in items:
        if it['path']:
            f.write(('%s\t%s\n' % (it['id'], it['path'])).encode('ascii'))
t = subprocess.run([TOOL, listing], capture_output=True)
open(OUT + '/sval_f10a_k4c.stdout.txt', 'wb').write(t.stdout)
by_id = {}
for line in t.stdout.decode('latin1').replace('\r', '').split('\n'):
    f = line.split('\t')
    if line and not f[0].startswith('#'):
        by_id[f[0]] = f

cols = ['set', 'stage', 'hash16_key16_perm', 'spv_sha256', 'words', 'cache_file_sha256_eq_base', 'sdk_vk13_rc',
        'sdk_vk13_msg', 'sdk_vk13_ubsl_rc', 'sdk_vk13_ubsl_msg', 'builtin', 'builtin_msg', 'builtin_ubsl',
        'builtin_ubsl_msg']
n_acc_sdk = n_acc_both = n_rej_sdk = n_rej_both = 0
with open(OUT + '/f10a_k4c.tsv', 'wb') as f:
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for it in items:
        if not it['path']:
            f.write(('K4C\tps\t%s\tNO_MODULE\t-\t-\t-\t-\t-\t-\t-\t-\t-\t-\n' % it['id']).encode('ascii'))
            continue
        g = by_id[it['id']]
        vals = ['K4C', 'ps', it['id'], it['sha'], g[1], str(int(it['cache_sha_ok'])), str(it['k1_rc']), it['k1_msg'],
                str(it['k2_rc']), it['k2_msg'], g[2], g[3], g[4], g[5]]
        f.write(('\t'.join(vals) + '\n').encode('ascii', 'replace'))
        if it['k1_rc'] == 0:
            n_acc_sdk += 1
            n_acc_both += g[2] == 'ACCEPT'
        else:
            n_rej_sdk += 1
            n_rej_both += g[2] == 'REJECT'
lines = ['F10a k4 within the base: rows C ps (stored SPIR-V, signature 56189185)',
         'calibration on rows A: %d of %d' % (cal_ok, cal_ok + cal_bad),
         'rows C ps: %d; module extracted: %d; cache file sha256 == base: %d'
         % (len(items), sum(1 for it in items if it['path']), sum(1 for it in items if it.get('cache_sha_ok'))),
         'SDK vulkan1.3 accepts %d; built-in ValidateShaderSpirv accepts %d of them' % (n_acc_sdk, n_acc_both),
         'SDK vulkan1.3 rejects %d; built-in rejects %d of them' % (n_rej_sdk, n_rej_both),
         'SDK vulkan1.3 + ubsl accepts %d; built-in + layout option accepts %d'
         % (sum(1 for it in items if it['path'] and it['k2_rc'] == 0),
            sum(1 for it in items if it['path'] and by_id[it['id']][4] == 'ACCEPT')),
         'tool rc %d' % t.returncode]
text = '\n'.join(lines) + '\n'
open(OUT + '/f10a_k4c_summary.txt', 'wb').write(text.encode('ascii'))
sys.stdout.write(text)
