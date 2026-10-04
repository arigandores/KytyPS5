"""Sensitivity of test_f16m_read.py (track F link F16m, HPP-585): each mutant is one textual change of f16m_read.py or f16m_pair.py in a
temporary copy; the suite must print NOT OK (caught).  ASCII only.   usage: python sens_f16m.py"""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
R, P = 'f16m_read.py', 'f16m_pair.py'
MUT = [
    (R, 'F5 line without f5cmu_exact_cpu', "'dcc_stale_bucket_only', 'dcc_stale_fallback', 'cmask_rt_bucket_only', 'f5cmu_exact_cpu']",
     "'dcc_stale_bucket_only', 'dcc_stale_fallback', 'cmask_rt_bucket_only']"),
    (R, 'Id names without stamp_late', "'next_overflow', 'keys_fce', 'keys_cs', 'overflow_fce', 'overflow_cs', 'stamp_late']",
     "'next_overflow', 'keys_fce', 'keys_cs', 'overflow_fce', 'overflow_cs']"),
    (R, 'kept_applied <= kept dropped', "('f5cmu_kept_applied', 'f5cmu_kept'), ", ""),
    (R, 'exact_cpu <= exact_stale dropped', ", ('f5cmu_exact_cpu', 'f5cmu_exact_stale')]", "]"),
    (R, 'identity kept counts kept only', "c['kept'] + c['kept_applied'], last['f5cmu_kept']", "c['kept'], last['f5cmu_kept']"),
    (R, 'identity fallback dropped', "            ('fallback = f5cmu_fallback', c['fallback'], last['f5cmu_fallback']),\n", ""),
    (R, 'identity reads only 3 equalities', "all(x[3] for x in letter[:4])", "all(x[3] for x in letter[:3])"),
    (R, 'letter = variant', "            letter = identity496(evs, L5)", "            letter = identity496([e for e in evs if e['line'] < s5.last_lineno], L5)"),
    (R, 'limit at 65', "EV_LIMIT = 64", "EV_LIMIT = 65"),
    (R, 'FixF5Cmu mode after GuestOut accepted', "    return len(lines) >= 1 and (guest_first is None or lines[0] < guest_first)",
     "    return len(lines) >= 1"),
    (R, 'pair1 DiagF5Id member dropped', "        ctl.append(('0 lines DiagF5Id: (KYTY_DIAG_F5ID not set)', r['id_any'] == 0))\n", ""),
    (R, 'pair0 nohit allowed', "all(e['fix'] == 'off' for e in evs) and res['limits']['nohit_lines'] == 0", "all(e['fix'] == 'off' for e in evs)"),
    (R, 'pair0 cmu nonzero allowed', "('f5cmu_* = 0 on every frame line (item 492 (v)(5))', L5 is not None and s5.cmu_nonzero == 0)",
     "('f5cmu_* = 0 on every frame line (item 492 (v)(5))', L5 is not None)"),
    (R, 'id printed only, no recount', "if s['id_fce'] != 'ok' or s['id_cs'] != 'ok' or id_recount(s) != ('ok', 'ok')]",
     "if s['id_fce'] != 'ok' or s['id_cs'] != 'ok']"),
    (R, 'recount without meta_clear', "s['img_clear'] + s['meta_clear'] + s['tracked_other']", "s['img_clear'] + s['tracked_other']"),
    (R, 'recount without r0', "s['fce'] == reasons and s['r0'] == 0", "s['fce'] == reasons"),
    (R, 'fce positive on all four', "        if tag in FCE_POS:\n", "        if True:\n"),
    (R, 'cs positive dropped', "        ctl.append(('positive: ClearMeta site events (cs) >= 1 on the last sum line', last is not None and last['cs'] >= 1))\n", ""),
    (R, 'meta_clear member dropped', "last is not None and last['meta_clear'] == 0))", "last is not None))"),
    (R, 'b42=drawn not interference', " or r['gamepatch'] or res['drawn'])", " or r['gamepatch'])"),
    (R, 'video minimum 2999', "VIDEO_MIN = 3000", "VIDEO_MIN = 2999"),
    (R, 'hold minimum 200 s', "HOLD_MIN_US = 300000000", "HOLD_MIN_US = 200000000"),
    (R, 'env f5cmu value not checked', "        return ok and env.get('KYTY_FIX_F5CMU') == '1' and 'KYTY_DIAG_F5ID' not in env",
     "        return ok and 'KYTY_DIAG_F5ID' not in env"),
    (R, 'env other fix allowed', "    ok = (other_fix == [] and", "    ok = (True and"),
    (R, 'scene flag ignored', "                    e['scene'] = scene\n", "                    e['scene'] = True\n"),
    (R, 'n_at_entry from key lines only', "max([int(d.get('key_n', '0')) for d in ls if not d['scene']] + [r['kf_before'].get(k, 0)])",
     "max([r['kf_before'].get(k, 0)])"),
    (P, 'window p..p+2', "    lo = min(p0, p1) - 1", "    lo = min(p0, p1)"),
    (P, 'window p-1..p+1', "    hi = max(p0, p1) + 2", "    hi = max(p0, p1) + 1"),
    (P, 'match by image only', "    return (e['kind'], e['image'], e['cmask'], e['extent'])", "    return (e['kind'], e['cmask'], e['extent'])"),
    (P, 'order never checked', "    order = all(pairs[i][1] < pairs[i + 1][1] for i in range(len(pairs) - 1))", "    order = True"),
    (P, 'glitch only 1 includes both', "gl_only1=sorted((g1 - g0) & set(W))", "gl_only1=sorted(g1 & set(W))"),
    (P, 'missing presents ignored', "        miss1 = [q for q in W if idx1 is None or q not in idx1]", "        miss1 = []"),
]


def main():
    srcs = dict((n, open(os.path.join(HERE, n), encoding='utf-8').read()) for n in (R, P))
    suite = open(os.path.join(HERE, 'test_f16m_read.py'), encoding='utf-8').read()
    print('sens sens_f16m.py sha256 %s target f16m_read.py sha256 %s target f16m_pair.py sha256 %s suite sha256 %s' % (
        hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
        hashlib.sha256(srcs[R].encode('utf-8')).hexdigest(), hashlib.sha256(srcs[P].encode('utf-8')).hexdigest(),
        hashlib.sha256(suite.encode('utf-8')).hexdigest()))
    caught = 0
    bad = []
    for target, name, a, b in MUT:
        src = srcs[target]
        if src.count(a) != 1:
            print('MUTANT %s: anchor count %d - BROKEN' % (name, src.count(a)))
            bad.append(name)
            continue
        d = tempfile.mkdtemp(prefix='f16m_sens_')
        for n in (R, P):
            open(os.path.join(d, n), 'w', encoding='utf-8', newline='\n').write(srcs[n].replace(a, b) if n == target else srcs[n])
        open(os.path.join(d, 'test_f16m_read.py'), 'w', encoding='utf-8', newline='\n').write(suite)
        pr = subprocess.run([sys.executable, os.path.join(d, 'test_f16m_read.py')], capture_output=True, cwd=d)
        out = pr.stdout.decode('ascii', 'replace')
        ok = 'NOT OK' in out and pr.returncode != 0
        print('MUTANT %s: %s' % (name, 'caught (%s)' % [x for x in out.split('\n') if x.startswith('checks ')][:1] if ok else 'SURVIVED'))
        caught += ok
        if not ok:
            bad.append(name)
        shutil.rmtree(d, ignore_errors=True)
    print('sensitivity %d/%d' % (caught, len(MUT)))
    print('ALL OK' if not bad else 'NOT OK')
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
