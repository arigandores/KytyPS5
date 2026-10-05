"""Sensitivity of test_f16q_read.py (track F link F16q, HPP-597): each mutant is one textual change of f16q_read.py, f16q_pair.py or
f16q_luma.py in a temporary copy; the suite must print NOT OK (caught).  The form of sens_f16m.py (F16m, accepted by the lead in item 504).
ASCII only.   usage: python sens_f16q.py"""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
R, P, L = 'f16q_read.py', 'f16q_pair.py', 'f16q_luma.py'
MUT = [
    (R, 'F5 line without f26_deferred_declined', "'f5cmu_exact_cpu',\n            'f26_kept', 'f26_kept_applied', 'f26_exact_stale', 'f26_fallback', 'f26_deferred_declined']",
     "'f5cmu_exact_cpu',\n            'f26_kept', 'f26_kept_applied', 'f26_exact_stale', 'f26_fallback']"),
    (R, 'limit cmask_fce 64', "LIM_FCE = 1024", "LIM_FCE = 64"),
    (R, 'limit dcc 257', "LIM_DCC = 256", "LIM_DCC = 257"),
    (R, 'limit cmask sum >=', "last['cmask_fce_b42'] + last['cmask_fce_unapplied'] > LIM_FCE)",
     "last['cmask_fce_b42'] + last['cmask_fce_unapplied'] >= LIM_FCE)"),
    (R, 'dcc counter limit dropped', "kind == 'f26_1' and last is not None and last['f26_kept'] + last['f26_exact_stale'] + last['f26_fallback'] > LIM_DCC)",
     "False)"),
    (R, 'identity 496 = letter', "all(x[3] for x in res['id496_variant'][:4])", "all(x[3] for x in res['id496_letter'][:4])"),
    (R, 'identity 496 3 equalities', "all(x[3] for x in res['id496_variant'][:4])", "all(x[3] for x in res['id496_variant'][:3])"),
    (R, 'identity 496 counts kept only', "c['kept'] + c['kept_applied'], last['f5cmu_kept']", "c['kept'], last['f5cmu_kept']"),
    (R, 'identity 507 = letter', "                    ctl.append(('identity of item 507 (b)(4) (VARIANT: dcc lines before the last DiagF5 line), 6 equalities',\n"
     "                                all(x[3] for x in res['id507_variant'])))",
     "                    ctl.append(('identity of item 507 (b)(4) (VARIANT: dcc lines before the last DiagF5 line), 6 equalities',\n"
     "                                all(x[3] for x in res['id507_letter'])))"),
    (R, 'identity 507 cleared not counted', "ka_prep + cleared, last['f26_kept_applied']", "ka_prep, last['f26_kept_applied']"),
    (R, 'identity 507 kept_applied of adopt counted', "if e['fix'] == 'kept_applied' and e['site'] == 'prepare'])",
     "if e['fix'] == 'kept_applied'])"),
    (R, 'identity 507 declined row dropped', "            ('declined = f26_deferred_declined', declined, last['f26_deferred_declined']),\n", ""),
    (R, 'identity 507 adopt kept_applied row dropped', "            ('site=adopt fix=kept_applied = 0', ka_adopt, 0)]", "]"),
    (R, 'identity 507 kept counts kept only', "c['kept'] + c['kept_applied'], last['f26_kept']", "c['kept'], last['f26_kept']"),
    (R, 'frame-line f26 LE without declined', "if d['f26_kept_applied'] + d['f26_deferred_declined'] > d['f26_kept']:",
     "if d['f26_kept_applied'] > d['f26_kept']:"),
    (R, 'frame-line kept = bucket_only dropped', "        if d['f26_kept'] != d['dcc_stale_bucket_only']:", "        if False:"),
    (R, 'frame-line f26 zero dropped on =0', "    elif any(d[n] for n in F26C):", "    elif False:"),
    (R, 'apply_late on present only', "(a['present'] != e['present'] or a['gpu'] != e['gpu'])", "(a['present'] != e['present'])"),
    (R, 'apply_late on gpu only', "(a['present'] != e['present'] or a['gpu'] != e['gpu'])", "(a['gpu'] != e['gpu'])"),
    (R, 'apply_late includes declined', "late = None if e is None else (a['result'] == 'cleared' and (", "late = None if e is None else (True and ("),
    (R, 'FixF26 mode after GuestOut accepted', "    return len(lines) >= 1 and (guest_first is None or lines[0] < guest_first)",
     "    return len(lines) >= 1"),
    (R, 'f26_0 FixF26 line allowed', "            ctl.append(('0 lines FixF26:', r['f26_any'] == 0))", "            ctl.append(('0 lines FixF26:', True))"),
    (R, 'pair FixF26 / f26 zero dropped', "r['f26_any'] == 0 and L5 is not None and s5.f26_nonzero == 0))", "L5 is not None))"),
    (R, 'pair dcc fix off dropped', "        ctl.append(('every dcc_stale line fix=off, 0 lines dcc_stale_apply', all(e['fix'] == 'off' for e in ds) and len(da) == 0))\n"
     "    elif kind in ('f26_0', 'f26_1'):", "    elif kind in ('f26_0', 'f26_1'):"),
    (R, 'dcc events counted as cmask', "                    if e['kind'] in ('fce', 'nohit'):", "                    if e['kind'] in ('fce', 'nohit', 'dcc'):"),
    (R, 'f26 DiagF5Id mode member dropped', "        ctl.append(('DiagF5Id: mode=1 before the first GuestOut (KYTY_DIAG_F5ID=1)', mode_ok(r['id_mode'], r['guest_first'])))\n", ""),
    (R, 'env skipceil allowed', " and 'skipceil' not in (gates or '')", ""),
    (R, 'env warm zeros not checked', "        return (ok and env.get('KYTY_FIX_F5CMU') == '0' and env.get('KYTY_FIX_F26') == '0' and 'KYTY_DIAG_F5ID' not in env)",
     "        return (ok and 'KYTY_DIAG_F5ID' not in env)"),
    (R, 'env f26 value not checked', "    return ok and env.get('KYTY_DIAG_F5ID') == '1' and env.get('KYTY_FIX_F26') == want and 'KYTY_FIX_F5CMU' not in env",
     "    return ok and env.get('KYTY_DIAG_F5ID') == '1' and 'KYTY_FIX_F5CMU' not in env"),
    (R, 'video minimum 2999', "VIDEO_MIN = 3000", "VIDEO_MIN = 2999"),
    (R, 'b42=drawn not interference', " or r['gamepatch'] or res['drawn'])", " or r['gamepatch'])"),
    (R, 'scene flag ignored', "                    e['scene'] = scene\n", "                    e['scene'] = True\n"),
    (P, 'window p..p+2', "    return list(range(min(p0, p1) - 1, max(p0, p1) + 2 + 1))", "    return list(range(min(p0, p1), max(p0, p1) + 2 + 1))"),
    (P, 'window p-1..p+1', "    return list(range(min(p0, p1) - 1, max(p0, p1) + 2 + 1))", "    return list(range(min(p0, p1) - 1, max(p0, p1) + 1 + 1))"),
    (P, 'pair A dcc key without fix', "    return (e['site'], e['image'], e['dcc'], e['fix'])", "    return (e['site'], e['image'], e['dcc'])"),
    (P, 'pair A dcc key with exact', "    return (e['site'], e['image'], e['dcc'], e['fix'])", "    return (e['site'], e['image'], e['dcc'], e['fix'], e['exact'])"),
    (P, 'pair B key without site', "    return (e['site'], e['image'], e['dcc'])\n\n\ndef key_dcc_a", "    return (e['image'], e['dcc'])\n\n\ndef key_dcc_a"),
    (P, 'apply late -> kept_applied', "        if a['present'] != e1['present'] or a['gpu'] != e1['gpu']:", "        if False:"),
    (P, 'declined -> kept_applied', "        if a['result'] == 'declined':", "        if False:"),
    (P, 'skips near gpu-2', "g - 1 <= s[2] <= g + 3", "g - 2 <= s[2] <= g + 3"),
    (P, 'skips near gpu+4', "g - 1 <= s[2] <= g + 3", "g - 1 <= s[2] <= g + 4"),
    (P, 'sheets of fresh too', "if it['kind'] != 'PAIR' or it['fix1'] != 'fresh']", "]"),
    (P, 'glitch only 1 includes both', "gl_only1=sorted((g1 - g0) & set(W))", "gl_only1=sorted(g1 & set(W))"),
    (P, 'order never checked', "    order = all(pairs[i][1] < pairs[i + 1][1] for i in range(len(pairs) - 1))", "    order = True"),
    (L, 'luma threshold >=', "        if all(x > THR for x in m[i:i + held]) and len(m[i:i + held]) == held:",
     "        if all(x >= THR for x in m[i:i + held]) and len(m[i:i + held]) == held:"),
    (L, 'luma held 30', "HELD = 60", "HELD = 30"),
]


def main():
    names = (R, P, L)
    srcs = dict((n, open(os.path.join(HERE, n), encoding='utf-8').read()) for n in names)
    suite = open(os.path.join(HERE, 'test_f16q_read.py'), encoding='utf-8').read()
    print('sens sens_f16q.py sha256 %s target f16q_read.py sha256 %s target f16q_pair.py sha256 %s target f16q_luma.py sha256 %s '
          'suite sha256 %s' % (hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
                               hashlib.sha256(srcs[R].encode('utf-8')).hexdigest(), hashlib.sha256(srcs[P].encode('utf-8')).hexdigest(),
                               hashlib.sha256(srcs[L].encode('utf-8')).hexdigest(), hashlib.sha256(suite.encode('utf-8')).hexdigest()))
    caught = 0
    bad = []
    for target, name, a, b in MUT:
        src = srcs[target]
        if src.count(a) != 1:
            print('MUTANT %s: anchor count %d - BROKEN' % (name, src.count(a)))
            bad.append(name)
            continue
        d = tempfile.mkdtemp(prefix='f16q_sens_')
        for n in names:
            open(os.path.join(d, n), 'w', encoding='utf-8', newline='\n').write(srcs[n].replace(a, b) if n == target else srcs[n])
        open(os.path.join(d, 'test_f16q_read.py'), 'w', encoding='utf-8', newline='\n').write(suite)
        pr = subprocess.run([sys.executable, os.path.join(d, 'test_f16q_read.py')], capture_output=True, cwd=d)
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
