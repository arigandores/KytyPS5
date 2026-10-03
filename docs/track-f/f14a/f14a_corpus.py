"""F14a (HPP-487, ROADMAP s122 item 395(g)(1)): compare-sample opcodes in the T1 corpus (offline, no game, no device).

Part 1 (GCN): every distinct GCN file of C:/kyty/s288/s4/gcn/{g_1,g_2,g_3_0} (S7 corpus; names equal => bytes equal, the empty
  g_2/cs_900aba8df9448d3d.bin is skipped as in S7) is decoded by the pinned test binary of this link
  (KYTY_CFG_BENCH=<file> KYTY_CFG_BENCH_DECODE=1, one process per file) and its decoded instructions with the compare flag
  (mnemonic image_sample_c* / image_gather4_c*, 'sample_flags=' containing 'compare') are counted per mnemonic.
Part 2 (SPIR-V): every A row of t1_base.tsv with an out.spv of S7 pass A (sha256 checked against spv_sha256_a) is parsed:
  native compare sites = OpImageSampleDref{Implicit,Explicit}Lod (89, 90) and OpImageDrefGather (97);
  manual compare sites = the emitter pattern of ManualDepthCompare/CompareDepth (spirvEmitterImage.cpp): a non-Dref
  OpImageSample{Implicit,Explicit}Lod (87, 88) or OpImageGather (96) result R, OpCompositeExtract X = R[k],
  an ordered/unordered float compare C(ref, X) with X as the SECOND operand, OpSelect float C 1.0 0.0.
Scenes: the GCN directory (g_1 underwater_aerial_garden, g_2 big_hand_pirate_island, g_3_0 shuriken_ninja_castle; S7 s7-corpus.md 2).
Writes f14a_gcn.tsv, f14a_spv.tsv, f14a_corpus_summary.txt; ASCII output only. Halts on the lock or STOP before each process.
"""
import csv
import hashlib
import os
import re
import struct
import subprocess
import sys

GCN = 'C:/kyty/s288/s4/gcn'
DIRS = [('g_1', 'underwater_aerial_garden'), ('g_2', 'big_hand_pirate_island'), ('g_3_0', 'shuriken_ninja_castle')]
S7 = 'C:/kyty/s288/s7'
OUT = 'C:/kyty/f287/f14a'
EXE = OUT + '/bin/shader_cfg_tests_d3697275.exe'
EXE_SHA = 'd3697275c3a4ca03ce96c933bddc13a82d532594500d8942a3dbeaf1e1b7a256'
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


ok = True
exe_sha = sha256_file(EXE)
ok &= exe_sha == EXE_SHA
# ---------------- part 1: GCN decode ----------------
files = {}
scenes = {}
for d, scene in DIRS:
    for name in sorted(os.listdir(GCN + '/' + d)):
        if not name.endswith('.bin'):
            continue
        p = GCN + '/' + d + '/' + name
        if os.path.getsize(p) == 0:
            continue
        files.setdefault(name, p)
        scenes.setdefault(name, []).append(scene)
CMP = re.compile(r'^\s*0x[0-9a-f]+:\s+(image_\w+)\s.*sample_flags=([a-z0-9_|]+)')
gcn_rows = []
env0 = dict(os.environ)
for name in sorted(files):
    halt_check()
    env = dict(env0)
    env['KYTY_CFG_BENCH'] = files[name]
    env['KYTY_CFG_BENCH_DECODE'] = '1'
    r = subprocess.run([EXE], capture_output=True, env=env, cwd=OUT + '/build')
    text = r.stdout.decode('latin1').replace('\r', '')
    counts = {}
    total = 0
    for line in text.split('\n'):
        m = CMP.match(line)
        if m and 'compare' in m.group(2).split('|'):
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
            total += 1
    decoded = sum(1 for line in text.split('\n') if re.match(r'^\s*0x[0-9a-f]+:\s', line))
    stage, h = name[:-4].split('_', 1)
    gcn_rows.append({'name': name, 'stage': stage, 'hash16': h, 'rc': r.returncode, 'decoded': decoded,
                     'compare_total': total,
                     'compare_ops': ','.join('%s:%d' % kv for kv in sorted(counts.items())),
                     'scenes': ','.join(scenes[name])})
with open(OUT + '/f14a_gcn.tsv', 'wb') as f:
    cols = ['name', 'stage', 'hash16', 'rc', 'decoded', 'compare_total', 'compare_ops', 'scenes']
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for g in gcn_rows:
        f.write(('\t'.join(str(g[c]) for c in cols) + '\n').encode('ascii'))

# ---------------- part 2: SPIR-V of the A rows ----------------
OP_SAMPLE = {87, 88, 96}
OP_DREF = {89: 'DrefImplicitLod', 90: 'DrefExplicitLod', 97: 'DrefGather'}
OP_FCMP = {180, 183, 184, 186, 188, 190, 181, 182, 185, 187, 189, 191}
FCMP_NAME = {180: 'FOrdEqual', 181: 'FUnordEqual', 182: 'FOrdNotEqual', 183: 'FUnordNotEqual', 184: 'FOrdLessThan',
             185: 'FUnordLessThan', 186: 'FOrdGreaterThan', 187: 'FUnordGreaterThan', 188: 'FOrdLessThanEqual',
             189: 'FUnordLessThanEqual', 190: 'FOrdGreaterThanEqual', 191: 'FUnordGreaterThanEqual'}


def parse(path):
    data = open(path, 'rb').read()
    words = struct.unpack('<%dI' % (len(data) // 4), data)
    assert words[0] == 0x07230203
    insts = []
    i = 5
    while i < len(words):
        wc, op = words[i] >> 16, words[i] & 0xffff
        insts.append((op, words[i + 1:i + wc]))
        i += wc
    return insts


def analyse(path):
    insts = parse(path)
    float_types = set()
    const = {}
    for op, w in insts:
        if op == 22 and len(w) >= 2 and w[1] == 32:  # OpTypeFloat 32
            float_types.add(w[0])
    for op, w in insts:
        if op == 43 and w[0] in float_types:  # OpConstant
            const[w[1]] = w[2]
    native = {}
    sample_res = set()
    extract = {}
    fcmp = {}
    manual = 0
    kinds = {}
    sel = []
    for op, w in insts:
        if op in OP_DREF:
            native[OP_DREF[op]] = native.get(OP_DREF[op], 0) + 1
        elif op in OP_SAMPLE:
            sample_res.add(w[1])
        elif op == 81 and len(w) >= 3:  # OpCompositeExtract type res composite idx
            extract[w[1]] = w[2]
        elif op in OP_FCMP and len(w) >= 4:  # type res a b
            fcmp[w[1]] = (w[2], w[3], op)
        elif op == 169 and len(w) >= 5:  # OpSelect type res cond a b
            sel.append(w)
    for w in sel:
        if w[0] not in float_types or w[2] not in fcmp:
            continue
        if const.get(w[3]) != 0x3f800000 or const.get(w[4]) != 0:
            continue
        x = fcmp[w[2]][1]
        if x in extract and extract[x] in sample_res:
            manual += 1
            k = FCMP_NAME[fcmp[w[2]][2]]
            kinds[k] = kinds.get(k, 0) + 1
    return native, manual, kinds


rows = list(csv.DictReader(open(S7 + '/t1_base.tsv', encoding='ascii'), delimiter='\t'))
spv_rows = []
bad_sha = 0
for r in rows:
    if r['row'] != 'A' or r['outcome'] != 'OK':
        continue
    rid = '%s_%s_%s' % (r['hash16'], r['key16'], r['perm'])
    p = '%s/work/A/A_%s/out.spv' % (S7, rid)
    if not os.path.exists(p) or sha256_file(p) != r['spv_sha256_a']:
        bad_sha += 1
        continue
    native, manual, kinds = analyse(p)
    spv_rows.append({'stage': r['stage'], 'id': rid, 'hash16': r['hash16'],
                     'native': sum(native.values()), 'native_ops': ','.join('%s:%d' % kv for kv in sorted(native.items())),
                     'manual': manual, 'kinds': ','.join('%s:%d' % kv for kv in sorted(kinds.items()))})
with open(OUT + '/f14a_spv.tsv', 'wb') as f:
    cols = ['stage', 'id', 'hash16', 'native', 'native_ops', 'manual', 'kinds']
    f.write(('\t'.join(cols) + '\n').encode('ascii'))
    for s in spv_rows:
        f.write(('\t'.join(str(s[c]) for c in cols) + '\n').encode('ascii'))

# ---------------- summary ----------------
gcn_by_hash = {(g['stage'], g['hash16']): g for g in gcn_rows}
out = []
out.append('F14a corpus summary (HPP-487); test binary %s (sha256 ok: %s)' % (exe_sha[:8], exe_sha == EXE_SHA))
out.append('GCN files decoded: %d (rc != 0: %d)' % (len(gcn_rows), sum(1 for g in gcn_rows if g['rc'] != 0)))
for st in ('cs', 'ps', 'vs', 'ms'):
    sub = [g for g in gcn_rows if g['stage'] == st]
    cmpg = [g for g in sub if g['compare_total'] > 0]
    ops = {}
    for g in cmpg:
        for kv in g['compare_ops'].split(','):
            k, v = kv.split(':')
            ops[k] = ops.get(k, 0) + int(v)
    out.append('  %s: programs %d, with compare ops %d; ops %s' % (st, len(sub), len(cmpg),
               ', '.join('%s %d' % kv for kv in sorted(ops.items()))))
cmp_all = [g for g in gcn_rows if g['compare_total'] > 0]
for sc in [s for _, s in DIRS]:
    out.append('  scene %s: programs with compare ops %d' % (sc, sum(1 for g in cmp_all if sc in g['scenes'].split(','))))
out.append('SPIR-V A rows (OK) analysed: %d (sha mismatch/missing %d)' % (len(spv_rows), bad_sha))
nat_rows = [s for s in spv_rows if s['native'] > 0]
man_rows = [s for s in spv_rows if s['manual'] > 0]
out.append('  rows with native Dref sites: %d (sites %d); rows with manual compare sites: %d (sites %d); both: %d'
           % (len(nat_rows), sum(s['native'] for s in nat_rows), len(man_rows), sum(s['manual'] for s in man_rows),
              sum(1 for s in spv_rows if s['native'] > 0 and s['manual'] > 0)))
# cross-check: every A row whose GCN has compare ops shows native or manual sites
cross_cmp = [s for s in spv_rows if gcn_by_hash.get((s['stage'], s['hash16']), {}).get('compare_total', 0) > 0]
cross_none = [s for s in cross_cmp if s['native'] == 0 and s['manual'] == 0]
cross_extra = [s for s in spv_rows if (s['native'] > 0 or s['manual'] > 0)
               and gcn_by_hash.get((s['stage'], s['hash16']), {}).get('compare_total', 0) == 0]
out.append('  A rows whose GCN has compare ops: %d; of them with neither native nor manual sites: %d; '
           'rows with sites but no compare op in GCN: %d' % (len(cross_cmp), len(cross_none), len(cross_extra)))
for s in cross_none:
    out.append('    no-site row: %s %s' % (s['stage'], s['id']))
nat_keys = {(s['stage'], s['hash16']) for s in nat_rows}
man_keys = {(s['stage'], s['hash16']) for s in man_rows}
allk = {}
for s in man_rows:
    for kv in s['kinds'].split(','):
        if kv:
            k, v = kv.split(':')
            allk[k] = allk.get(k, 0) + int(v)
out.append('  manual programs (stage, hash): %d (CS %d, PS %d); of them with a native permutation too: %d; native programs: %d; '
           'compare ops of manual sites: %s' % (len(man_keys), sum(1 for k in man_keys if k[0] == 'cs'),
           sum(1 for k in man_keys if k[0] == 'ps'), len(man_keys & nat_keys), len(nat_keys),
           ', '.join('%s %d' % kv for kv in sorted(allk.items()))))
for s in man_rows:
    g = gcn_by_hash.get((s['stage'], s['hash16']), {})
    out.append('    manual row: %s %s manual %d (%s) native-sibling %s gcn %s scenes %s' % (s['stage'], s['id'], s['manual'],
               s['kinds'], 'yes' if (s['stage'], s['hash16']) in nat_keys else 'no',
               g.get('compare_ops', '?'), g.get('scenes', '?')))
# the 4 MS that end the linear decoder with 'unsupported scalar source operand 0x00000073' (S7 s7-corpus.md 5) are the
# only allowed rc != 0
KNOWN_MS = {'ms_3f716cc2835a4c3f.bin', 'ms_4e555b0ebf3b53f8.bin', 'ms_b6dbdd5904905160.bin', 'ms_c739f9614016bed4.bin'}
bad_rc = sorted(g['name'] for g in gcn_rows if g['rc'] != 0)
out.append('GCN rc != 0: %s (allowed: the 4 MS of S7 5)' % ','.join(bad_rc))
ok &= bad_sha == 0 and set(bad_rc) == KNOWN_MS
out.append('ALL OK' if ok else 'FAIL')
text = '\n'.join(out) + '\n'
open(OUT + '/f14a_corpus_summary.txt', 'wb').write(text.encode('ascii', 'replace'))
sys.stdout.write(text)
sys.exit(0 if ok else 1)
