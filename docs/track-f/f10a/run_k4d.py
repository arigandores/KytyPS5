"""F10a (HPP-445): control k4 within the T1 base - stored SPIR-V of the base rows D (stage ps, outcome
OLD_SIGNATURE: translation cache files of other signatures in snap0, read only).

Every module of every row-D ps file is taken (the extractor of run_k4c.py, calibrated 269 of 269 on rows A;
for old file versions an extracted module is used only if the SDK parses it - a module SDK accepts is a
well-formed module by construction). k4 asks: on PS of the base that the SDK accepts in form vulkan1.3,
does the built-in ValidateShaderSpirv accept too (no false rejection by the older SPIRV-Tools 7f2d9ee)?
Writes k4d/*.spv, f10a_k4d.tsv, f10a_k4d_summary.txt. ASCII output only.
"""
import csv
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/f287/f10a')
S7 = 'C:/kyty/s288/s7'
BASE = S7 + '/t1_base.tsv'
SNAP = 'C:/kyty/s288/snap0/ShaderCache_PPSA21564'
OUT = 'C:/kyty/f287/f10a'
TOOL = OUT + '/sval_f10a.exe'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'

for p in ('C:/kyty/SEALED_RUN.lock', 'C:/kyty/f287/STOP'):
    if os.path.exists(p):
        print('HALT', p)
        sys.exit(3)

import struct
MAGIC = struct.pack('<I', 0x07230203)


def modules(path):
    d = open(path, 'rb').read()
    out = []
    pos = 0
    while True:
        i = d.find(MAGIC, pos)
        if i < 0:
            break
        if i < 4:
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


rows = list(csv.DictReader(open(BASE, encoding='ascii'), delimiter='\t'))
os.makedirs(OUT + '/k4d', exist_ok=True)
items = []
files = 0
sha_ok = 0
for r in rows:
    if r['row'] != 'D' or r['stage'] != 'ps':
        continue
    path = '%s/ps_%s_%s.bin' % (SNAP, r['hash16'], r['key16'])
    data = open(path, 'rb').read()
    files += 1
    sha_ok += hashlib.sha256(data).hexdigest() == r['cache_sha256']
    for k, m in enumerate(modules(path)):
        rid = '%s_%s_m%d' % (r['hash16'], r['key16'], k)
        spv = '%s/k4d/D_%s.spv' % (OUT, rid)
        open(spv, 'wb').write(m)
        items.append({'id': rid, 'sig': r['cache_sig'], 'path': spv, 'sha': hashlib.sha256(m).hexdigest()})

for it in items:
    v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', it['path']], capture_output=True)
    it['k1_rc'], it['k1_msg'] = v.returncode, one_line(v.stderr + v.stdout)

listing = OUT + '/f10a_k4d_list.tsv'
with open(listing, 'wb') as f:
    for it in items:
        f.write(('%s\t%s\n' % (it['id'], it['path'])).encode('ascii'))
t = subprocess.run([TOOL, listing], capture_output=True)
open(OUT + '/sval_f10a_k4d.stdout.txt', 'wb').write(t.stdout)
by_id = {}
for line in t.stdout.decode('latin1').replace('\r', '').split('\n'):
    f = line.split('\t')
    if line and not f[0].startswith('#'):
        by_id[f[0]] = f

cols = ['set', 'stage', 'hash16_key16_module', 'cache_sig', 'spv_sha256', 'words', 'sdk_vk13_rc', 'sdk_vk13_msg',
        'builtin', 'builtin_msg', 'builtin_ubsl', 'builtin_ubsl_msg']
acc_sdk = acc_both = rej_sdk = rej_both = 0
by_sig = {}
with open(OUT + '/f10a_k4d.tsv', 'wb') as f:
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for it in items:
        g = by_id[it['id']]
        f.write(('\t'.join(['K4D', 'ps', it['id'], it['sig'], it['sha'], g[1], str(it['k1_rc']), it['k1_msg'],
                            g[2], g[3], g[4], g[5]]) + '\n').encode('ascii', 'replace'))
        s = by_sig.setdefault(it['sig'], [0, 0, 0, 0])
        if it['k1_rc'] == 0:
            acc_sdk += 1
            acc_both += g[2] == 'ACCEPT'
            s[0] += 1
            s[1] += g[2] == 'ACCEPT'
        else:
            rej_sdk += 1
            rej_both += g[2] == 'REJECT'
            s[2] += 1
            s[3] += g[2] == 'REJECT'
lines = ['F10a k4 within the base: rows D ps (stored SPIR-V of old signatures, snap0)',
         'files %d (sha256 == base cache_sha256: %d); modules %d' % (files, sha_ok, len(items)),
         'SDK vulkan1.3 accepts %d modules; built-in ValidateShaderSpirv accepts %d of them' % (acc_sdk, acc_both),
         'SDK vulkan1.3 rejects %d modules; built-in rejects %d of them' % (rej_sdk, rej_both)]
for sig, s in sorted(by_sig.items()):
    lines.append('  sig %s: SDK accepts %d (built-in accepts %d), SDK rejects %d (built-in rejects %d)'
                 % (sig, s[0], s[1], s[2], s[3]))
lines.append('tool rc %d' % t.returncode)
text = '\n'.join(lines) + '\n'
open(OUT + '/f10a_k4d_summary.txt', 'wb').write(text.encode('ascii'))
sys.stdout.write(text)
