"""S16d (HPP-608, ROADMAP s122 item 516(v)(1)-(12)): scorer of probe P-S16 (pure function of the run results).

    python s16d_score.py <work folder> <out folder> <diffstat file>   # writes probe.out.txt, causes.tsv, b_diff.tsv

Rules (item 516(v), written before the data; executor variants marked as such and asked to the lead in HPP-608):
  unit and denominator - recipe of pipelines.bin S13b with all its stages, 1 852 (v)(1);
  harness - some stage of the recipe: arm A form A0 (raw recipe bytes) not byte-equal to the stored SPIR-V (or the job
            failed); out of the denominator, share > 2 % -> NO_POWER (v)(3);
  reasons - one per recipe and form, first in the order src, fused, key|canon, push, shape, ident, translate, emit, val (v)(10):
    src       a stage whose program hash is not in eboot.bin (not a Mesh stage) or whose cache file is absent;
    fused     a Mesh stage whose hash is not in eboot.bin (the fused hash; the back half's size is not in the key);
    key|canon arm A, the form's input not built, the job failed, or its SPIR-V not byte-equal to the stored one;
    push      [executor variant] arm A: the start of the cursor PS -> VS (graphics; start 6 when the vertex stage is Mesh,
              else 0; compute 0) computed from the form's shader data dwords differs from the stored start;
    shape     arm B: the stored specialization does not map onto the new plan by identity (kind, first_use_pc, ordinal) (v)(8);
    ident     [executor variant] arm A: the form's plan identities differ from the stored plan's (expected 0, (v)(11));
    translate arm B: the translator died / hung (phase T) or the job could not run;
    emit      arm B: died in emission (phase E);
    val       arm B: the SPIR-V failed the device-form check (or died in it).
  Every F19-ambiguous stage (a stored manual image) is run in arm B with both outcomes k16UNorm and k8UNorm; the recipe
  counts only if every outcome of every stage passes (v)(7).
  R_B = prepared / (1 852 - harness) per form; read by the better form (v)(11).
  NO_POWER - any of: manifest, signature of arm A (26ce5fc7...), layout, parse; harness share > 2 %; nondet > 0 (v)(5);
  comparator not 10 of 10 'not equal' (v)(6, letter: stride); a knob read once per process not at its default (v)(6);
  the F19 stand line wrong at any of the 81 permutations in either form (v)(7); jobs without result.
  Outcome word: NO_POWER, else KILL when R_B < 0.90 in both forms, else PASS_K0; R_B is not read before the lead reads b_diff
  (v)(9); the reading is the lead's (S16f).
"""
import collections
import json
import os
import sys

NO_START = 0xFFFFFFFF
DENOM = 1852
ORDER = ['src', 'fused', 'key', 'push', 'shape', 'ident', 'translate', 'emit', 'val']
SIG_A = 'KytySC3:26ce5fc78ea3b20be537c7696be041f5e97d9e58'


def start_for(cursor, size):
    return cursor if (size != 0 and cursor <= 32 and size <= 32 - cursor) else NO_START


def advance(cursor, start, dd):
    return start + dd if start != NO_START else cursor


def chain_starts(rec, res_of):
    """Starts of the cursor chain of a recipe from the shader data dwords of the given results (stage index -> start);
    None when a result is missing."""
    stages = rec['stages']
    if rec['kind'] == 2:
        r = res_of(0)
        if r is None:
            return None
        return {0: start_for(0, int(r['dd']))}
    c = 6 if stages[0]['stage'] == 5 else 0
    out = {}
    if len(stages) == 2:
        r = res_of(1)
        if r is None:
            return None
        s = start_for(c, int(r['dd']))
        out[1] = s
        c = advance(c, s, int(r['dd']))
    r = res_of(0)
    if r is None:
        return None
    out[0] = start_for(c, int(r['dd']))
    return out


def ok_eq(r):
    return r is not None and r.get('st') == 'OK' and r.get('eq') == '1'


def b_status(r):
    """None = pass; else the reason of one arm B job."""
    if r is None:
        return 'translate'
    st = r.get('st')
    if st == 'OK':
        return None if r.get('val') == '1' else 'val'
    if st == 'SHAPE':
        return 'shape'
    if st in ('CRASH', 'HANG'):
        return {'T': 'translate', 'E': 'emit', 'V': 'val'}.get(r.get('phase'), 'translate')
    return 'translate'


def b_jobs_of(rec, form):
    """Every arm B job id of a recipe for a form (phase 1 first stage, phase 2 VS after each PS outcome)."""
    ids = []
    for st in rec['stages']:
        for v, jid in st.get('jobsB1', {}).get(form, {}).items():
            ids.append(jid)
        for v_ps, d in st.get('jobsB2', {}).get(form, {}).items():
            ids.extend(d.values())
    return ids


def recipe_reason(rec, form, A1, B):
    """(reason or None, harness flag) of a recipe in one form."""
    stages = rec['stages']
    if any(not s.get('file_ok') for s in stages):
        return 'src', False
    if any((not s['in_eboot']) and not s.get('fused') for s in stages):
        return 'src', False
    if any(s.get('fused') for s in stages):
        return 'fused', False
    if any(not ok_eq(A1.get(s['jobsA']['A0'])) for s in stages):
        return None, True
    fa = [A1.get(s['jobsA'][form]) for s in stages]
    if any(not ok_eq(r) for r in fa):
        return 'key', False
    chain = chain_starts(rec, lambda i: fa[i])
    if chain is None or any(chain[i] != int(fa[i]['stored_start']) for i in chain):
        return 'push', False
    bids = b_jobs_of(rec, form)
    reasons = [b_status(B.get(j)) for j in bids]
    if not bids:
        reasons = ['translate']
    if 'shape' in reasons:
        return 'shape', False
    if any(r.get('plan') != 'same' for r in fa):
        return 'ident', False
    for reason in ('translate', 'emit', 'val'):
        if reason in reasons:
            return reason, False
    return None, False


def score(meta, A1, A2, B, headers, diffstat=''):
    recipes = meta['recipes']
    denom = meta.get('denominator', DENOM)
    f19_n = meta.get('f19_expected', 81)
    out = collections.OrderedDict()
    lines = []
    no_power = []
    # ---- controls before data
    man = meta['manifest']
    man_ok = man['sha'].startswith('65a95adf') and man['ok'] == man['listed'] and man['listed'] > 0
    if not man_ok:
        no_power.append('manifest')
    lines.append('control manifest sha256 %s listed %d ok %d -> %s' % (man['sha'], man['listed'], man['ok'],
                                                                     'ok' if man_ok else 'FAIL'))
    sigs = meta['cache_sigs']
    cat_sig_ok = list(sigs) == [SIG_A + ':robust:ftz:cbank:fixb26:fixb1b:fixf10']
    if not cat_sig_ok or meta['parse_fail']:
        no_power.append('catalogue')
    lines.append('control catalogue signatures %s parse_fail %d -> %s' % (sigs, len(meta['parse_fail']),
                                                                        'ok' if cat_sig_ok and not meta['parse_fail'] else 'FAIL'))
    if len(recipes) != denom:
        no_power.append('denominator')
    lines.append('control recipes %d (denominator %d)' % (len(recipes), denom))
    for arm in [a for a in ('A1', 'A2', 'B1', 'B2', 'B3') if a in headers or a != 'B3']:
        h = headers.get(arm, [])
        sig = sorted({x.split()[1] for x in h if x.startswith('S signature=')})
        lay = sorted({x.split()[1] for x in h if x.startswith('S layout=')})
        knobs = collections.Counter(x[2:] for x in h if x.startswith('K '))
        bad = sorted(k for k in knobs if not (k.endswith('=<unset>') or (arm.startswith('B') and k == 'KYTY_FIX_F19=1')))
        want_lay = 'layout=%d:%d:%d' % (meta['layout']['vs'], meta['layout']['ps'], meta['layout']['cs'])
        if arm.startswith('A'):
            sig_ok = sig == ['signature=' + SIG_A + ':robust:ftz:cbank:fixb26:fixb1b:fixf10']
            if not sig_ok:
                no_power.append('signature_' + arm)
        else:
            sig_ok = True
            if not any(k == 'KYTY_FIX_F19=1' for k in knobs):
                no_power.append('f19_env_' + arm)
        if lay != [want_lay]:
            no_power.append('layout_' + arm)
        if bad or not knobs:
            no_power.append('knobs_' + arm)
        eff = sorted({x for x in h if x.startswith('S effective')})
        lines.append('control %s signature %s (%s) layout %s knobs %d not-default %s' % (
            arm, sig, 'member' if arm.startswith('A') else 'reference', lay, len(knobs), bad or 'none'))
        for e in eff:
            lines.append('  %s %s' % (arm, e))
    if diffstat:
        lines.append('arm B tree: git diff --stat 4d9e8ab7 <commit> -- <signature set>:')
        for x in diffstat.strip().split(chr(10)):
            lines.append('  ' + x)
    # ---- determinism (v)(5)
    nondet = []
    for jid, r1 in A1.items():
        r2 = A2.get(jid)
        if r2 is None:
            nondet.append((jid, 'missing_second'))
            continue
        if r1.get('st') != r2.get('st') or (r1.get('st') == 'OK' and r1.get('spv') != r2.get('spv')):
            nondet.append((jid, '%s/%s %s/%s' % (r1.get('st'), r2.get('st'), r1.get('spv'), r2.get('spv'))))
    if nondet:
        no_power.append('nondet')
    lines.append('determinism: arm A jobs %d in run 1, %d in run 2 (reverse order, other processes); nondet %d' % (
        len(A1), len(A2), len(nondet)))
    for jid, why in nondet[:50]:
        lines.append('  nondet %s %s' % (jid, why))
    # ---- comparator (v)(6)
    comp = meta['comparator']
    n_ne = {'stride': 0, 'format': 0, 'spirv': 0}
    for c in comp:
        base = A1.get(c['base'])
        row = ['comparator %s#%d base %s' % (c['file'], c['perm'], 'eq' if ok_eq(base) else 'NOT_EQ')]
        for kind in ('stride', 'format', 'spirv'):
            r = A1.get(c[kind])
            ne = r is not None and r.get('st') == 'OK' and r.get('eq') == '0'
            n_ne[kind] += ne
            row.append('%s=%s' % (kind, 'not_equal' if ne else ('equal' if ok_eq(r) else (r or {}).get('st', 'none'))))
        lines.append('  ' + ' '.join(row))
    comp_ok = len(comp) == 10 and n_ne['stride'] == 10
    if not comp_ok:
        no_power.append('comparator')
    lines.append('comparator (letter: corrupt key word stride): not equal %d of %d -> %s; executor variant (reference): '
                 'format %d of %d, SPIR-V word %d of %d' % (n_ne['stride'], len(comp), 'ok' if comp_ok else 'FAIL',
                                                             n_ne['format'], len(comp), n_ne['spirv'], len(comp)))
    # ---- F19 stand control (v)(7) and f19_both
    manual = {k: v for k, v in meta['manual'].items() if v}
    lines.append('F19: permutations referenced %d, with a stored manual image %d' % (len(meta['manual']), len(manual)))
    stand_bad = {}
    f19_both = {}
    for form in ('K', 'C'):
        seen = collections.defaultdict(dict)
        for rec in recipes:
            for st in rec['stages']:
                key = '%s#%d' % (st['file'], st['perm'])
                if key not in manual:
                    continue
                jobs = []
                for v, jid in st.get('jobsB1', {}).get(form, {}).items():
                    jobs.append((v, jid))
                for v_ps, d in st.get('jobsB2', {}).get(form, {}).items():
                    jobs.extend(d.items())
                for v, jid in jobs:
                    r = B.get(jid)
                    seen[key].setdefault(v, []).append(r)
        for key, forms in meta.get('f19_control', {}).items():
            for v, jid in forms.get(form, {}).items():
                seen[key].setdefault(v, []).append(B.get(jid))
        bad = []
        both = 0
        for key in manual:
            d = seen.get(key, {})
            ok16 = bool(d.get('k16UNorm')) and all(r is not None and r.get('f19', '').endswith(
                '_manual_to_native=1_kept_manual=0') for r in d['k16UNorm'])
            ok8 = bool(d.get('k8UNorm')) and all(r is not None and r.get('f19', '').endswith(
                '_manual_to_native=0_kept_manual=1') for r in d['k8UNorm'])
            if not (ok16 and ok8):
                bad.append(key)
            if d.get('k16UNorm') and d.get('k8UNorm') and all(b_status(r) is None for r in d['k16UNorm'] + d['k8UNorm']):
                both += 1
        stand_bad[form] = bad
        f19_both[form] = both
        lines.append('F19 stand control form %s: permutations %d, line wrong or absent %d -> %s; f19_both %d (<= %d)' % (
            form, len(manual), len(bad), 'ok' if not bad and len(manual) == f19_n else 'FAIL', both, len(manual)))
        for key in bad[:20]:
            lines.append('  stand_bad %s %s' % (form, key))
        if bad or len(manual) != f19_n:
            no_power.append('f19_stand_' + form)
    # ---- reasons and R_B
    harness = []
    reasons = {'K': collections.Counter(), 'C': collections.Counter()}
    prepared = {'K': 0, 'C': 0}
    per_recipe = []
    for rec in recipes:
        row = {'index': rec['index']}
        h_any = False
        for form in ('K', 'C'):
            reason, h = recipe_reason(rec, form, A1, B)
            h_any = h_any or h
            row[form] = 'harness' if h else (reason or 'prepared')
            if h:
                continue
            if reason is None:
                prepared[form] += 1
            else:
                reasons[form][reason] += 1
        if h_any:
            harness.append(rec['index'])
        per_recipe.append(row)
    n_h = len(harness)
    share = n_h / denom
    if share > 0.02:
        no_power.append('harness_share')
    lines.append('harness (arm A0 not equal): %d of %d = %.4f (limit 0.02) -> %s' % (n_h, denom, share,
                                                                                 'ok' if share <= 0.02 else 'NO_POWER'))
    rb = {}
    for form in ('K', 'C'):
        total = prepared[form] + sum(reasons[form].values())
        ident_ok = total == denom - n_h
        if not ident_ok:
            no_power.append('identity_' + form)
        rb[form] = prepared[form] / (denom - n_h) if denom - n_h else 0.0
        name = 'key' if form == 'K' else 'canon'
        parts = ' '.join('%s=%d' % (name if r == 'key' else r, reasons[form][r]) for r in ORDER)
        lines.append('form %s: prepared %d %s | identity prepared + sum rejected = %d = %d - %d -> %s; R_B = %.4f' % (
            form, prepared[form], parts, total, denom, n_h, 'ok' if ident_ok else 'FAIL', rb[form]))
    # ---- b_diff (v)(9)
    bdiff = []
    pushmoved = collections.Counter()
    for rec in recipes:
        for st in rec['stages']:
            key = '%s#%d' % (st['file'], st['perm'])
            for form in ('K', 'C'):
                jobs = list(st.get('jobsB1', {}).get(form, {}).items())
                for v_ps, d in st.get('jobsB2', {}).get(form, {}).items():
                    jobs.extend(d.items())
                for v, jid in jobs:
                    r = B.get(jid)
                    if r is None or r.get('st') != 'OK':
                        continue
                    if r.get('start') != r.get('stored_start'):
                        pushmoved[form] += 1
                    expect = (key not in manual) or (v == 'k8UNorm' and r.get('ind', '0') == '0')
                    if expect and r.get('eq') != '1':
                        bdiff.append((form, jid, key, v, r.get('start'), r.get('stored_start'), r.get('words'),
                                      r.get('stored_words')))
    bd_unique = {f: len({b[2] + '|' + b[3] for b in bdiff if b[0] == f}) for f in ('K', 'C')}
    lines.append('b_diff (arm B SPIR-V != stored where (v)(9) expects equal): jobs %d; unique permutation outcomes K %d, '
                 'C %d; b_push_moved K %d C %d (reference)' % (len(bdiff), bd_unique['K'], bd_unique['C'],
                                                              pushmoved['K'], pushmoved['C']))
    # reference lines (item 516(v)(1): permutations and programs apart; no decision rests on them)
    perms_all = {'%s#%d' % (s['file'], s['perm']) for rec in recipes for s in rec['stages']}
    progs_all = {(s['stage'], s.get('hash', s['file'])) for rec in recipes for s in rec['stages']}
    for form in ('K', 'C'):
        ok_idx = {row['index'] for row in per_recipe if row[form] == 'prepared'}
        pp = {'%s#%d' % (s['file'], s['perm']) for rec in recipes if rec['index'] in ok_idx for s in rec['stages']}
        pg = {(s['stage'], s.get('hash', s['file'])) for rec in recipes if rec['index'] in ok_idx for s in rec['stages']}
        lines.append('reference form %s: permutations in prepared recipes %d of %d referenced; programs %d of %d' % (
            form, len(pp), len(perms_all), len(pg), len(progs_all)))
    k16 = collections.Counter()
    for key, forms in meta.get('f19_control', {}).items():
        for form, d in forms.items():
            r = B.get(d.get('k16UNorm'))
            k16[(form, 'control', (r or {}).get('eq'))] += 1
    for rec in recipes:
        for st in rec['stages']:
            for form in ('K', 'C'):
                jobs = list(st.get('jobsB1', {}).get(form, {}).items())
                for v_ps, d in st.get('jobsB2', {}).get(form, {}).items():
                    jobs.extend(d.items())
                for v, jid in jobs:
                    if v == 'k16UNorm':
                        k16[(form, 'recipe', (B.get(jid) or {}).get('eq'))] += 1
    lines.append('reference k16UNorm outcomes (native comparison; not expected equal to stored), (form, kind, eq): %s' % (
        dict(sorted(k16.items())),))
    missing = [j for j in set(meta.get('all_jobs', [])) if j not in A1 and j not in B]
    if missing:
        no_power.append('missing_results')
    lines.append('jobs without result: %d' % len(missing))
    # ---- outcome
    if no_power:
        word = 'NO_POWER'
    elif rb['K'] < 0.90 and rb['C'] < 0.90:
        word = 'KILL'
    else:
        word = 'PASS_K0'
    best = 'K' if rb['K'] >= rb['C'] else 'C'
    lines.append('R_B by form: K %.4f C %.4f; better form %s %.4f' % (rb['K'], rb['C'], best, rb[best]))
    lines.append('NO_POWER members: %s' % (', '.join(sorted(set(no_power))) or 'none'))
    lines.append('OUTCOME (word by item 516(v)(11)-(12); R_B not read before the lead reads b_diff; reading - S16f): %s' % word)
    out['word'] = word
    out['rb'] = rb
    out['prepared'] = prepared
    out['reasons'] = {f: dict(reasons[f]) for f in reasons}
    out['harness'] = n_h
    out['nondet'] = len(nondet)
    out['no_power'] = sorted(set(no_power))
    out['f19_both'] = f19_both
    out['bdiff'] = bdiff
    out['per_recipe'] = per_recipe
    out['comparator'] = n_ne
    return out, lines


def load_results(folder):
    res = {}
    heads = []
    if not os.path.isdir(folder):
        return res, heads
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.out'):
            continue
        for line in open(os.path.join(folder, name), 'r', encoding='utf-8', errors='replace'):
            line = line.rstrip(chr(10))
            if line.startswith(('R ', 'X ')):
                parts = line.split()
                d = {'id': parts[1]}
                for p in parts[2:]:
                    if '=' in p:
                        k, v = p.split('=', 1)
                        d[k] = v
                res[d['id']] = d
            elif line.startswith(('S ', 'K ')):
                heads.append(line)
    return res, heads


def main():
    work, outdir, diffstat_path = sys.argv[1], sys.argv[2], sys.argv[3]
    meta = json.load(open(os.path.join(work, 'meta.json')))
    A1, hA1 = load_results(os.path.join(work, 'res_A1'))
    A2, hA2 = load_results(os.path.join(work, 'res_A2'))
    B1, hB1 = load_results(os.path.join(work, 'res_B1'))
    B2, hB2 = load_results(os.path.join(work, 'res_B2'))
    B3, hB3 = load_results(os.path.join(work, 'res_B3'))
    B = dict(B1)
    B.update(B2)
    B.update(B3)
    jobs_all = []
    for name in ('jobs_A.txt', 'jobs_B1.txt', 'jobs_B2.txt', 'jobs_B3.txt'):
        p = os.path.join(work, name)
        if os.path.exists(p):
            jobs_all += [x.split()[1] for x in open(p) if x.startswith('J ')]
    meta['all_jobs'] = jobs_all
    diffstat = open(diffstat_path, encoding='utf-8').read() if os.path.exists(diffstat_path) else ''
    heads = {'A1': hA1, 'A2': hA2, 'B1': hB1, 'B2': hB2}
    if hB3:
        heads['B3'] = hB3
    out, lines = score(meta, A1, A2, B, heads, diffstat)
    head = ['S16d probe P-S16 (HPP-608, ROADMAP s122 item 516(v)); catalogue S13b; ' + ' / '.join(meta['report'])]
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'probe.out.txt'), 'w', encoding='utf-8', newline=chr(10)) as f:
        f.write(chr(10).join(head + lines) + chr(10))
    with open(os.path.join(outdir, 'causes.tsv'), 'w', encoding='utf-8', newline=chr(10)) as f:
        f.write('recipe' + chr(9) + 'form_K' + chr(9) + 'form_C' + chr(10))
        for row in out['per_recipe']:
            f.write('%d%s%s%s%s%s' % (row['index'], chr(9), row['K'], chr(9), row['C'], chr(10)))
    with open(os.path.join(outdir, 'b_diff.tsv'), 'w', encoding='utf-8', newline=chr(10)) as f:
        f.write(chr(9).join(['form', 'job', 'permutation', 'f19', 'start', 'stored_start', 'words', 'stored_words']) + chr(10))
        for b in out['bdiff']:
            f.write(chr(9).join(str(x) for x in b) + chr(10))
    for line in lines:
        print(line)


if __name__ == '__main__':
    main()
