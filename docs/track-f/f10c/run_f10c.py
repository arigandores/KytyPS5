"""Track F, link F10c (HPP-451), ROADMAP s122 item 369(v)(1): offline check of KYTY_FIX_SVAL with the F10a inputs.

Tool: sval_f10c.exe (sval_f10c.cpp + sval_body_f10c.inc extracted from the F10c commit by extract_body_f10c.py).
Inputs (read only): the modules of F10a and its tables C:/kyty/f287/f10a/{f10a_out,f10a_k4c,f10a_k4d}.tsv and lists.
Sets (ids prefixed with the set name):
  S151 - the F16 set (151 PS, rows A);              C51  - rows C ps (51, stored SPIR-V, signature 56189185);
  K4   - PS of the base accepted by SDK vulkan1.3: rows A ps (7) + modules of rows D (16) = 23;
  CS   - rows A cs accepted by SDK vulkan1.3 (111);  D442 - modules of rows D rejected by SDK vulkan1.3 (442);
  NEG  - modules of D442 that SDK rejects also with --uniform-buffer-standard-layout (selected here); if none - a
         synthetic violation (first OpDecorate ArrayStride 4 of the first S151 module set to 3), checked the same way.
Runs of the tool over one list (S151, C51, K4, CS, D442, NEG):
  r_unset - KYTY_FIX_SVAL unset, device value 1;  r_0 - KYTY_FIX_SVAL=0, device 1;
  r_1     - KYTY_FIX_SVAL=1, device 1;            r_1u0 - KYTY_FIX_SVAL=1, device 0 (the "iff" half).
Gates (item 369(v)(1)): =0 - S151 REJECT 151; =1 - S151 ACCEPT 151, C51 51, K4 23, CS 111, NEG REJECT (>= 1); envFlag
fixture; plus: =0 and =1/device 0 verdicts and messages equal to the F10a built-in on every module (the old path), no
FixSvalStat line at =0, FixSvalStat lines at =1 on checks 256k with validated = 256k and rejected = REJECTs so far.
Count (not a gate): D442 at =1. Writes f10c_out.tsv, f10c_summary.txt. ASCII output, ends with ALL OK.
"""
import csv
import hashlib
import os
import struct
import subprocess
import sys

F10A = 'C:/kyty/f287/f10a'
OUT = 'C:/kyty/f287/f10c'
TOOL = OUT + '/sval_f10c.exe'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'


def halt_check():
    if os.path.exists(LOCK):
        print('HALT lock')
        sys.exit(3)
    if os.path.exists(STOP):
        print('HALT stop')
        sys.exit(4)


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def one_line(b):
    t = b.decode('latin1').replace('\r', '')
    return ' | '.join(x.strip() for x in t.split('\n') if x.strip()).replace('\t', ' ')


def table(p):
    return list(csv.DictReader(open(p, encoding='ascii', errors='replace'), delimiter='\t'))


def listing(p):
    d = {}
    for line in open(p, encoding='ascii'):
        line = line.rstrip('\r\n')
        if line:
            k, v = line.split('\t')
            d[k] = v
    return d


ok = True
out = []


def gate(name, cond, text):
    global ok
    ok &= bool(cond)
    out.append('%s %s: %s' % ('PASS' if cond else 'FAIL', name, text))


halt_check()
la = listing(F10A + '/f10a_list.tsv')
lc = listing(F10A + '/f10a_k4c_list.tsv')
ld = listing(F10A + '/f10a_k4d_list.tsv')
items = []  # dict: set, id, path, sha, sdk (rc vk13), f10a_builtin, f10a_msg
for r in table(F10A + '/f10a_out.tsv'):
    rid = r['hash16_key16_perm']
    base = {'id': rid, 'path': la[rid], 'sha': r['spv_sha256'], 'sdk': int(r['sdk_vk13_rc']), 'f10a': r['builtin'],
            'f10a_msg': r['builtin_msg']}
    if r['set'] == 'S151':
        items.append(dict(base, set='S151'))
    elif r['set'] == 'K4PS' and base['sdk'] == 0:
        items.append(dict(base, set='K4'))
    elif r['set'] == 'K4CS' and base['sdk'] == 0:
        items.append(dict(base, set='CS'))
for r in table(F10A + '/f10a_k4c.tsv'):
    rid = r['hash16_key16_perm']
    items.append({'set': 'C51', 'id': rid, 'path': lc[rid], 'sha': r['spv_sha256'], 'sdk': int(r['sdk_vk13_rc']),
                  'f10a': r['builtin'], 'f10a_msg': r['builtin_msg']})
for r in table(F10A + '/f10a_k4d.tsv'):
    rid = r['hash16_key16_module']
    it = {'id': rid, 'path': ld[rid], 'sha': r['spv_sha256'], 'sdk': int(r['sdk_vk13_rc']), 'f10a': r['builtin'],
          'f10a_msg': r['builtin_msg']}
    items.append(dict(it, set='K4' if it['sdk'] == 0 else 'D442'))
order = ['S151', 'C51', 'K4', 'CS', 'D442']
items.sort(key=lambda it: order.index(it['set']))
bad_sha = [it['id'] for it in items if sha256_file(it['path']) != it['sha']]
counts = {s: sum(it['set'] == s for it in items) for s in order}
out.append('F10c (HPP-451) offline check, ROADMAP s122 item 369(v)(1)')
out.append('sets: ' + ', '.join('%s %d' % (s, counts[s]) for s in order) + '; module sha256 != F10a table: %d' % len(bad_sha))
gate('inputs', not bad_sha and counts == {'S151': 151, 'C51': 51, 'K4': 23, 'CS': 111, 'D442': 442},
     'sets as F10a, every module sha256 = F10a table')

# SDK with the layout option on D442 -> negative control.
halt_check()
ver = subprocess.run([SPIRV_VAL, '--version'], capture_output=True)
out.append('SDK spirv-val: %s' % one_line(ver.stdout + ver.stderr))
for it in items:
    if it['set'] != 'D442':
        continue
    halt_check()
    v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', it['path']],
                       capture_output=True)
    it['sdk_ubsl'], it['sdk_ubsl_msg'] = v.returncode, one_line(v.stderr + v.stdout)
neg = [dict(it, set='NEG') for it in items if it['set'] == 'D442' and it['sdk_ubsl'] != 0]
out.append('D442: SDK vulkan1.3 + ubsl accepts %d, rejects %d'
           % (sum(it.get('sdk_ubsl') == 0 for it in items if it['set'] == 'D442'), len(neg)))
neg_kind = 'D442'
if not neg:
    neg_kind = 'synthetic'
    src = [it for it in items if it['set'] == 'S151'][0]
    words = list(struct.unpack('<%dI' % (os.path.getsize(src['path']) // 4), open(src['path'], 'rb').read()))
    i = 5
    hit = None
    while i < len(words):
        n, op = words[i] >> 16, words[i] & 0xffff
        if op == 71 and n == 4 and words[i + 2] == 6 and words[i + 3] == 4:  # OpDecorate <id> ArrayStride 4
            hit = i
            break
        i += max(n, 1)
    assert hit is not None
    # The second one in the Uniform block itself: the array type of member 0 of the structure the F10a message names
    # ("Structure id N decorated as Block for variable in Uniform storage class"); its ArrayStride 4 -> 3.
    sid = int(src['f10a_msg'].split('Structure id ', 1)[1].split(' ', 1)[0])
    arr = None
    i = 5
    while i < len(words):
        n, op = words[i] >> 16, words[i] & 0xffff
        if op == 30 and words[i + 1] == sid:  # OpTypeStruct <result id> <member 0 type> ...
            arr = words[i + 2]
        i += max(n, 1)
    ubo_hit = None
    i = 5
    while i < len(words):
        n, op = words[i] >> 16, words[i] & 0xffff
        if op == 71 and n == 4 and words[i + 1] == arr and words[i + 2] == 6 and words[i + 3] == 4:
            ubo_hit = i
        i += max(n, 1)
    assert arr is not None and ubo_hit is not None
    os.makedirs(OUT + '/neg', exist_ok=True)
    neg = []
    for name, at, target in (('synthetic_stride3_first', hit, words[hit + 1]), ('synthetic_stride3_ubo', ubo_hit, arr)):
        w = list(words)
        w[at + 3] = 3
        p = OUT + '/neg/NEG_' + name + '_' + src['id'] + '.spv'
        open(p, 'wb').write(struct.pack('<%dI' % len(w), *w))
        v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', p],
                           capture_output=True)
        neg.append({'set': 'NEG', 'id': name + '_' + src['id'], 'path': p, 'sha': sha256_file(p), 'sdk': -1,
                    'sdk_ubsl': v.returncode, 'sdk_ubsl_msg': one_line(v.stderr + v.stdout), 'f10a': '', 'f10a_msg': ''})
        out.append('synthetic NEG %s: word %d (ArrayStride of id %d) 4 -> 3; SDK + ubsl rc %d'
                   % (name, at + 3, target, v.returncode))
        gate('neg-%s' % name, v.returncode != 0, 'SDK with the option rejects the synthetic module')
    out.append('synthetic NEG source: S151 %s (structure id %d, member 0 array id %d)' % (src['id'], sid, arr))
gate('neg-exists', len(neg) >= 1, 'negative control modules (%s): %d' % (neg_kind, len(neg)))
items += neg

listpath = OUT + '/f10c_list.tsv'
with open(listpath, 'wb') as f:
    for it in items:
        f.write(('%s:%s\t%s\n' % (it['set'], it['id'], it['path'])).encode('ascii'))


def run(tag, env_value, ubo):
    halt_check()
    env = dict(os.environ)
    env.pop('KYTY_FIX_SVAL', None)
    if env_value is not None:
        env['KYTY_FIX_SVAL'] = env_value
    t = subprocess.run([TOOL, listpath, ubo], capture_output=True, env=env)
    open('%s/sval_f10c_%s.stdout.txt' % (OUT, tag), 'wb').write(t.stdout)
    res = {'rc': t.returncode, 'stat': [], 'v': {}, 'msg': {}, 'order': []}
    for line in t.stdout.decode('latin1').replace('\r', '').split('\n'):
        if not line:
            continue
        f = line.split('\t')
        if f[0] in ('#spirv-tools', '#mode', '#ubo', '#count'):
            res[f[0][1:]] = f[1]
        elif f[0] == '#stat':
            res['stat'].append((int(f[1]), f[2]))
        else:
            res['v'][f[0]] = f[2]
            res['msg'][f[0]] = f[3]
            res['order'].append(f[0])
    return res


R = {'r_unset': run('r_unset', None, '1'), 'r_0': run('r_0', '0', '1'), 'r_1': run('r_1', '1', '1'),
     'r_1u0': run('r_1u0', '1', '0')}
out.append('tool SPIRV-Tools: %s' % R['r_1'].get('spirv-tools'))
N = len(items)
for tag, r in R.items():
    gate('%s-run' % tag, r['rc'] == 0 and r.get('count') == str(N) and len(r['v']) == N,
         'rc %d, count %s of %d, mode %s, ubo %s' % (r['rc'], r.get('count'), N, r.get('mode'), r.get('ubo')))


def key(it):
    return '%s:%s' % (it['set'], it['id'])


def tally(tag, s):
    sel = [it for it in items if it['set'] == s]
    acc = sum(R[tag]['v'][key(it)] == 'ACCEPT' for it in sel)
    return acc, len(sel) - acc, len(sel)


for tag in ('r_unset', 'r_0', 'r_1', 'r_1u0'):
    out.append('%s: ' % tag + ', '.join('%s ACCEPT %d REJECT %d of %d' % ((s,) + tally(tag, s))
                                      for s in order + ['NEG']))

# =0: the old path.
for tag in ('r_unset', 'r_0'):
    a, rj, n = tally(tag, 'S151')
    gate('%s-S151' % tag, R[tag].get('mode') == '0' and rj == 151 and n == 151, 'mode %s, S151 REJECT %d of %d'
         % (R[tag].get('mode'), rj, n))
    gate('%s-nostat' % tag, not R[tag]['stat'], 'FixSvalStat lines: %d' % len(R[tag]['stat']))
for tag in ('r_unset', 'r_0', 'r_1u0'):
    same = diff_msg = 0
    for it in items:
        if it['set'] == 'NEG':
            continue
        if R[tag]['v'][key(it)] == it['f10a']:
            same += 1
        if R[tag]['msg'][key(it)].replace('f10c SPIR-V validation failed', 'f10a SPIR-V validation failed', 1) != it['f10a_msg']:
            diff_msg += 1
    n = N - len(neg)
    gate('%s-asF10a' % tag, same == n and diff_msg == 0,
         'verdict = F10a built-in on %d of %d modules; message differs (label aside) on %d' % (same, n, diff_msg))

# =1 with the device value 1.
r1 = R['r_1']
want = {'S151': 151, 'C51': 51, 'K4': 23, 'CS': 111}
for s, n in want.items():
    a, rj, m = tally('r_1', s)
    gate('r_1-%s' % s, r1.get('mode') == '1' and r1.get('ubo') == '1' and a == n and m == n, '%s ACCEPT %d of %d' % (s, a, m))
a, rj, m = tally('r_1', 'NEG')
gate('r_1-NEG', m >= 1 and rj == m, 'NEG REJECT %d of %d' % (rj, m))
for it in neg:
    out.append('  NEG %s: SDK+ubsl: %s' % (it['id'], it['sdk_ubsl_msg'][:200]))
    out.append('  NEG %s: built-in =1: %s' % (it['id'], r1['msg'][key(it)][:200]))
a, rj, m = tally('r_1', 'D442')
agree = sum((r1['v'][key(it)] == 'ACCEPT') == (it['sdk_ubsl'] == 0) for it in items if it['set'] == 'D442')
out.append('count (not a gate) D442 at =1: ACCEPT %d, REJECT %d of %d; agrees with SDK + ubsl on %d of %d' % (a, rj, m, agree, m))
# FixSvalStat lines at =1: one per 256 checks, validated = n, rejected = REJECTs among the first n checks.
def expected_stat(r):
    exp = []
    rej = 0
    for n, k in enumerate(r['order'], 1):
        rej += r['v'][k] == 'REJECT'
        if n % 256 == 0:
            exp.append((n, 'FixSvalStat: validated=%d rejected=%d' % (n, rej)))
    return exp


for tag in ('r_1', 'r_1u0'):
    exp = expected_stat(R[tag])
    gate('%s-stat' % tag, R[tag]['stat'] == exp and len(exp) == N // 256,
         'lines %d (expected %d): %s' % (len(R[tag]['stat']), len(exp), '; '.join('#%d %s' % x for x in R[tag]['stat'])))
a, rj, m = tally('r_1u0', 'S151')
gate('r_1u0-S151', R['r_1u0'].get('mode') == '1' and R['r_1u0'].get('ubo') == '0' and rj == 151,
     'device without uniformBufferStandardLayout: S151 REJECT %d of %d (no option)' % (rj, m))

# envFlag fixture: the extracted FixSvalEnabled through the real common/envFlag.h.
cases = [(None, 0), ('', 0), ('0', 0), ('false', 0), ('FALSE', 0), ('False', 0), ('off', 0), ('OFF', 0), ('no', 0),
         ('No', 0), ('1', 1), ('yes', 1), ('true', 1), ('on', 1), ('2', 1), ('nv', 1), ('00', 1), (' 0', 1), ('0 ', 1),
         ('offx', 1)]
bad = []
rows = []
for value, expect in cases:
    halt_check()
    env = dict(os.environ)
    env.pop('KYTY_FIX_SVAL', None)
    if value is not None:
        env['KYTY_FIX_SVAL'] = value
    t = subprocess.run([TOOL, '--mode'], capture_output=True, env=env)
    got = t.stdout.decode().strip()
    rows.append('%r->%s' % (value, got.split('\t')[-1]))
    if got != 'mode\t%d' % expect:
        bad.append((value, got))
gate('envflag', not bad, '%d cases, mismatches %s; %s' % (len(cases), bad, ' '.join(rows)))
once = []
for value in (None, '1'):
    env = dict(os.environ)
    env.pop('KYTY_FIX_SVAL', None)
    if value is not None:
        env['KYTY_FIX_SVAL'] = value
    once.append(subprocess.run([TOOL, '--mode-once'], capture_output=True, env=env).stdout.decode().strip())
gate('read-once', once == ['mode-once\t0\t0', 'mode-once\t1\t1'],
     'unset: %s; =1: %s (env flipped between the two calls)' % (once[0].replace('\t', ' '), once[1].replace('\t', ' ')))

cols = ['set', 'id', 'spv_sha256', 'sdk_vk13_rc', 'sdk_vk13_ubsl_rc', 'f10a_builtin', 'r_unset', 'r_0', 'r_1', 'r_1u0',
        'r_1_msg']
with open(OUT + '/f10c_out.tsv', 'wb') as f:
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for it in items:
        k = key(it)
        vals = [it['set'], it['id'], it['sha'], str(it['sdk']), str(it.get('sdk_ubsl', '')), it['f10a'],
                R['r_unset']['v'][k], R['r_0']['v'][k], R['r_1']['v'][k], R['r_1u0']['v'][k], R['r_1']['msg'][k][:300]]
        f.write(('\t'.join(vals) + '\n').encode('ascii', 'replace'))
out.append('ALL OK' if ok else 'FAIL')
text = '\n'.join(out) + '\n'
open(OUT + '/f10c_summary.txt', 'wb').write(text.encode('ascii', 'replace'))
sys.stdout.write(text)
sys.exit(0 if ok else 1)
