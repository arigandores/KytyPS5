"""S16e (HPP-609, Red Team): own recount of probe P-S16 from results_s16d.txt.xz (git) + jobs files (work, outside git).

Independent of s16d_score.py: own pipelines.bin reader, own job index, own cursor chain, own reason order (ROADMAP s122
p.516(v)(10)), own stand / b_diff / f19_both. Reused from s16d_lib: the cache-file walker (to read the stored manual flag
and the plan flag) and the eboot.bin AMDGPU ELF scan (method F11a / F23a). Usage: python s16e_recount.py
"""
import collections
import hashlib
import json
import lzma
import os
import struct
import sys

import xxhash

GIT = 'C:/kyty/KytyPS5/docs/track-s/s16d'
WORK = 'C:/kyty/s288/s16d/work'
CAT = 'C:/kyty/s288/s13/seeds/PPSA21564'
sys.path.insert(0, GIT)
import s16d_lib as L  # noqa: E402

NO = 0xFFFFFFFF
DEN = 1852


def sf(c, n):
    return c if (n != 0 and c <= 32 and n <= 32 - c) else NO


def adv(c, s, n):
    return s + n if s != NO else c


# ---------------------------------------------------------------- results (git artifact)
res = collections.defaultdict(dict)
heads = collections.defaultdict(list)
raw = lzma.open(GIT + '/results_s16d.txt.xz', 'rt', encoding='utf-8').read().split('\n')
for line in raw:
    if not line:
        continue
    arm, fname, rest = line.split(' ', 2)
    if rest.startswith(('R ', 'X ')):
        p = rest.split()
        d = {'id': p[1], 'tag': p[0]}
        for x in p[2:]:
            if '=' in x:
                k, v = x.split('=', 1)
                d[k] = v
        if p[1] in res[arm]:
            d['dup'] = True
        res[arm][p[1]] = d
    else:
        heads[arm].append(rest)
print('results lines %d; per arm %s' % (len(raw), {a: len(v) for a, v in res.items()}))
xlines = sum(1 for a in res for d in res[a].values() if d['tag'] == 'X')
print('X (crash/hang) lines %d' % xlines)

# ---------------------------------------------------------------- jobs (work)
jobs = {}
for name in ('jobs_A.txt', 'jobs_B1.txt', 'jobs_B2.txt', 'jobs_B3.txt'):
    for line in open(os.path.join(WORK, name), encoding='ascii'):
        p = line.split()
        if not p or p[0] != 'J':
            continue
        jid, arm, form, cache, perm, gcn, inp, start, f19, cor = p[1:11]
        jobs[jid] = dict(name=name, arm=arm, form=form, file=os.path.basename(cache), perm=int(perm), gcn=gcn,
                         inp=os.path.basename(inp) if inp != '-' else '-', start=start, f19=f19, cor=cor)
A_ix = {}
B_ix = collections.defaultdict(dict)
for jid, j in jobs.items():
    if j['arm'] == 'A':
        A_ix[(j['form'], j['file'], j['perm'], j['inp'], j['cor'])] = jid
    else:
        B_ix[(j['form'], j['file'], j['perm'], j['inp'], j['start'])][j['f19']] = jid
print('jobs A %d B %d (B3 %d)' % (sum(1 for j in jobs.values() if j['arm'] == 'A'),
                                  sum(1 for j in jobs.values() if j['arm'] == 'B'),
                                  sum(1 for j in jobs.values() if j['name'] == 'jobs_B3.txt')))
A1, A2 = res['A1'], res['A2']
B = {}
for arm in ('B1', 'B2', 'B3'):
    B.update(res[arm])
B_nob3 = {}
for arm in ('B1', 'B2'):
    B_nob3.update(res[arm])
missing = [j for j in jobs if (jobs[j]['arm'] == 'A' and (j not in A1 or j not in A2)) or (jobs[j]['arm'] == 'B' and j not in B)]
print('jobs without a result line: %d' % len(missing))

# ---------------------------------------------------------------- own recipe reader
d = open(CAT + '/pipelines.bin', 'rb').read()
assert d[:8] == b'KytyPR1\n'
n = struct.unpack_from('<I', d, 8)[0]
sig = d[12:12 + n].decode()
p = 12 + n
lay = [int(x) for x in sig.split('\n')[1].split(':')]
VS, PS, CS, RS, VI, ST = lay
cnt = struct.unpack_from('<I', d, p)[0]
p += 4


def rkey(p):
    st, h, udc, cs, k = struct.unpack_from('<IQIII', d, p)
    ss = struct.unpack_from('<%dI' % k, d, p + 24)
    data = struct.pack('<II', udc, cs) + struct.pack('<%dI' % k, *ss)
    pre = {1: 'vs', 2: 'ps'}.get(st, 'cs')  # ShaderTranslationCache::PathOf: Mesh files are named cs_
    name = '%s_%016x_%016x.bin' % (pre, h, xxhash.xxh3_64_intdigest(data))
    perm = struct.unpack_from('<I', d, p + 24 + 4 * k)[0]
    return dict(stage=st, hash=h, cs=cs, file=name, perm=perm, state=ss), p + 28 + 4 * k


recs = []
for i in range(cnt):
    kind = d[p]
    p += 1
    if kind == 1:
        a, p = rkey(p)
        has_ps = d[p]
        p += 1
        b = None
        if has_ps:
            b, p = rkey(p)
        p += RS + VI + ST
        a['inp'] = hashlib.sha256(d[p:p + VS]).hexdigest()[:24] + '.bin'
        p += VS
        stages = [a]
        if has_ps:
            b['inp'] = hashlib.sha256(d[p:p + PS]).hexdigest()[:24] + '.bin'
            p += PS
            stages.append(b)
    elif kind == 2:
        a, p = rkey(p)
        a['inp'] = hashlib.sha256(d[p:p + CS]).hexdigest()[:24] + '.bin'
        p += CS
        stages = [a]
    else:
        raise SystemExit('kind')
    recs.append(dict(kind=kind, stages=stages))
print('recipes %d end %s kinds %s' % (len(recs), p == len(d), dict(collections.Counter(r['kind'] for r in recs))))

# ---------------------------------------------------------------- catalogue: manual flags (two predicates)
cat_files = set(os.listdir(CAT))
manual_exec = {}   # executor predicate: spec flag and (beyond plan or plan flag)
manual_spec = {}   # spec flag alone (what the C++ stand counts)


def walk(path):
    dd = open(path, 'rb').read()
    nl = dd.index(b'\n') + 1
    r = L.R(dd, nl + 8)
    r.u32(); r.u64(); r.u32(); r.u32()
    k = r.u32()
    r.p += 4 * k
    base_dc = L._plan(r)
    out = []
    for _ in range(r.u32()):
        r.podvec(12)
        ni, ib = r.podvec(44)
        e = sum(1 for i in range(ni) if ib[44 * i + 33] and (i >= len(base_dc) or base_dc[i]))
        s = sum(1 for i in range(ni) if ib[44 * i + 33])
        L._compiled(r)
        r.podvec(4)
        out.append((e, s))
    assert r.p == len(dd)
    return out


for rec in recs:
    for s in rec['stages']:
        if s['file'] in cat_files and (s['file'], s['perm']) not in manual_exec:
            w = walk(os.path.join(CAT, s['file']))
            for k, (e, sp) in enumerate(w):
                manual_exec[(s['file'], k)] = e
                manual_spec[(s['file'], k)] = sp
ref = {(s['file'], s['perm']) for r in recs for s in r['stages']}
print('perms referenced %d; manual (executor predicate) %d; spec-flag-only %d; differ %d' % (
    len(ref), sum(1 for k in ref if manual_exec.get(k)), sum(1 for k in ref if manual_spec.get(k)),
    sum(1 for k in ref if bool(manual_exec.get(k)) != bool(manual_spec.get(k)))))
MAN = {k for k in ref if manual_exec.get(k)}

# ---------------------------------------------------------------- eboot programs
progs, n_elf = L.eboot_programs()
hashes = {h: len(c) for h, c in progs.items()}
absent = {(s['stage'], s['hash']) for r in recs for s in r['stages'] if hashes.get(s['hash'], -1) < s['cs'] * 4}
print('programs referenced %d; absent from eboot (or short) %d: by stage %s' % (
    len({(s['stage'], s['hash']) for r in recs for s in r['stages']}), len(absent),
    dict(collections.Counter(a[0] for a in absent))))


def okeq(r):
    return r is not None and r.get('st') == 'OK' and r.get('eq') == '1'


def bstat(r):
    if r is None:
        return 'translate'
    if r.get('st') == 'OK':
        return None if r.get('val') == '1' else 'val'
    if r.get('st') == 'SHAPE':
        return 'shape'
    if r.get('st') in ('CRASH', 'HANG'):
        return {'T': 'translate', 'E': 'emit', 'V': 'val'}.get(r.get('phase'), 'translate')
    return 'translate'


ORDER = ['src', 'fused', 'key', 'push', 'shape', 'ident', 'translate', 'emit', 'val']


def reason(rec, form, Bres):
    st = rec['stages']
    if any(s['file'] not in cat_files for s in st):
        return 'src', [], []
    if any((s['stage'], s['hash']) in absent and s['stage'] != 5 for s in st):
        return 'src', [], []
    if any((s['stage'], s['hash']) in absent for s in st):
        return 'fused', [], []
    a0 = [A1.get(A_ix.get(('A0', s['file'], s['perm'], s['inp'], '0'))) for s in st]
    if any(not okeq(r) for r in a0):
        return 'harness', [], []
    fa = [A1.get(A_ix.get((form, s['file'], s['perm'], s['inp'] if form == 'C' else '-', '0'))) for s in st]
    if any(not okeq(r) for r in fa):
        return 'key', [], []
    # push: cursor PS -> VS (arm A dd) against the stored start
    c = 6 if st[0]['stage'] == 5 else 0
    if rec['kind'] == 2:
        chain = {0: sf(0, int(fa[0]['dd']))}
    else:
        chain = {}
        if len(st) == 2:
            s1 = sf(c, int(fa[1]['dd']))
            chain[1] = s1
            c = adv(c, s1, int(fa[1]['dd']))
        chain[0] = sf(c, int(fa[0]['dd']))
    if any(chain[i] != int(fa[i]['stored_start']) for i in chain):
        return 'push', [], []
    # arm B: first stage at c0, VS after each PS outcome at the new-translator cursor
    c0 = 6 if st[0]['stage'] == 5 else 0
    used = []
    reasons = []
    inp = lambda s: s['inp'] if form == 'C' else '-'
    first = st[1] if (rec['kind'] == 1 and len(st) == 2) else st[0]
    want = ['k16UNorm', 'k8UNorm'] if (first['file'], first['perm']) in MAN else ['-']
    got = B_ix.get((form, first['file'], first['perm'], inp(first), str(c0)), {})
    for v in want:
        jid = got.get(v)
        r = Bres.get(jid) if jid else None
        used.append((first, v, jid, r))
        reasons.append(bstat(r))
        if len(st) == 2 and first is st[1] and r is not None and r.get('st') == 'OK':
            s_ps = sf(c0, int(r['dd']))
            cur = adv(c0, s_ps, int(r['dd']))
            vs = st[0]
            want_vs = ['k16UNorm', 'k8UNorm'] if (vs['file'], vs['perm']) in MAN else ['-']
            got_vs = B_ix.get((form, vs['file'], vs['perm'], inp(vs), str(cur)), {})
            for vv in want_vs:
                j2 = got_vs.get(vv)
                r2 = Bres.get(j2) if j2 else None
                used.append((vs, vv, j2, r2))
                reasons.append(bstat(r2))
    if 'shape' in reasons:
        return 'shape', used, reasons
    if any(r.get('plan') != 'same' for r in fa):
        return 'ident', used, reasons
    for x in ('translate', 'emit', 'val'):
        if x in reasons:
            return x, used, reasons
    return None, used, reasons


out = {}
for form in ('K', 'C'):
    cnt_r = collections.Counter()
    prep = 0
    harness = 0
    bdiff = []
    for rec in recs:
        why, used, _ = reason(rec, form, B)
        if why == 'harness':
            harness += 1
            continue
        if why is None:
            prep += 1
        else:
            cnt_r[why] += 1
        for s, v, jid, r in used:
            if r is None or r.get('st') != 'OK':
                continue
            exp = ((s['file'], s['perm']) not in MAN) or (v == 'k8UNorm' and r.get('ind', '0') == '0')
            if exp and r.get('eq') != '1':
                bdiff.append(jid)
    tot = prep + sum(cnt_r.values())
    rb = prep / (DEN - harness)
    out[form] = rb
    print('form %s: prepared %d %s harness %d | identity %d = %d - %d %s | R_B %.4f = %d/%d | b_diff jobs %d' % (
        form, prep, ' '.join('%s=%d' % (k, cnt_r[k]) for k in ORDER), harness, tot, DEN, harness,
        'OK' if tot == DEN - harness else 'FAIL', rb, prep, DEN - harness, len(set(bdiff))))

# ---------------------------------------------------------------- determinism, comparator, knobs
ids = set(A1) | set(A2)
nd = [j for j in ids if (A1.get(j) or {}).get('st') != (A2.get(j) or {}).get('st') or
      (A1.get(j) or {}).get('spv') != (A2.get(j) or {}).get('spv')]
print('determinism: A ids %d A1 %d A2 %d nondet %d' % (len(ids), len(A1), len(A2), len(nd)))
comp = collections.Counter()
comp_base = 0
cj = [j for j in jobs.values() if j['arm'] == 'A' and j['cor'] != '0']
for j in cj:
    jid = A_ix[(j['form'], j['file'], j['perm'], j['inp'], j['cor'])]
    r = A1.get(jid)
    comp[(j['cor'], 'ne' if (r and r.get('st') == 'OK' and r.get('eq') == '0') else 'eq' if okeq(r) else (r or {}).get('st'))] += 1
for j in {(j['file'], j['perm']) for j in cj}:
    comp_base += okeq(A1.get(A_ix[('K', j[0], j[1], '-', '0')]))
print('comparator perms %d base eq %d; outcomes %s' % (len({(j['file'], j['perm']) for j in cj}), comp_base, dict(comp)))
for arm in ('A1', 'A2', 'B1', 'B2', 'B3'):
    ks = [h[2:] for h in heads[arm] if h.startswith('K ')]
    bad = sorted({k for k in ks if not k.endswith('=<unset>')})
    sigs = sorted({h for h in heads[arm] if h.startswith('S signature=')})
    print('knobs %s: lines %d set %s; signature %s' % (arm, len(ks), bad, [s[12:60] for s in sigs]))

# ---------------------------------------------------------------- F19 stand and f19_both, with and without B3
for label, Bres, use_b3 in (('with B3', B, True), ('without B3', B_nob3, False)):
    for form in ('K', 'C'):
        seen = collections.defaultdict(lambda: collections.defaultdict(list))
        for rec in recs:
            _, used, _ = reason(rec, form, Bres)
            for s, v, jid, r in used:
                if (s['file'], s['perm']) in MAN:
                    seen[(s['file'], s['perm'])][v].append(r)
        if use_b3:
            for jid, j in jobs.items():
                if j['name'] == 'jobs_B3.txt' and j['form'] == form:
                    seen[(j['file'], j['perm'])][j['f19']].append(B.get(jid))
        good = both = 0
        for k in MAN:
            s = seen.get(k, {})
            ok16 = bool(s.get('k16UNorm')) and all(r and r.get('f19', '').endswith('manual_to_native=1_kept_manual=0') for r in s['k16UNorm'])
            ok8 = bool(s.get('k8UNorm')) and all(r and r.get('f19', '').endswith('manual_to_native=0_kept_manual=1') for r in s['k8UNorm'])
            good += ok16 and ok8
            both += bool(s.get('k16UNorm')) and bool(s.get('k8UNorm')) and all(bstat(r) is None for r in s['k16UNorm'] + s['k8UNorm'])
        print('stand %s form %s: manual perms %d, stand ok %d, f19_both %d' % (label, form, len(MAN), good, both))
k16 = collections.Counter((jobs[j]['form'], jobs[j]['name'], r.get('eq')) for j, r in B.items() if jobs[j]['f19'] == 'k16UNorm')
print('k16UNorm outcomes (form, jobs file, eq): %s' % dict(sorted(k16.items())))
pm = sum(1 for j, r in B.items() if r.get('st') == 'OK' and r.get('start') != r.get('stored_start'))
print('arm B jobs with start != stored_start: %d of %d' % (pm, len(B)))
st_vals = collections.Counter(r.get('stored_start') for r in A1.values())
print('stored_start values over A1: %s' % dict(st_vals.most_common(12)))
print('R_B K %.4f C %.4f' % (out['K'], out['C']))
