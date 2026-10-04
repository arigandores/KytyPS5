"""Sensitivity of test_f16f_read.py (track F link F16f, HPP-523): each mutant is one textual change of f16f_read.py in a temporary copy;
the suite must print NOT OK (caught).  ASCII only.   usage: python sens_f16f.py"""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MUT = [
    ('family dropped', "            ('dcc_fce', ['dcc_fce_image', 'dcc_fce_no_image']),\n", ''),
    ('child dropped from cmask_fce', "'cmask_fce_drawn', 'cmask_fce_b42', 'cmask_fce_unapplied'])]", "'cmask_fce_drawn', 'cmask_fce_b42'])]"),
    ('pair <= reversed', "        if d[a] > d[b]:", "        if d[a] > d[b] + 1:"),
    ('F6 slot identity off', "    if s != 8 * d['draws']:", "    if s > 8 * d['draws']:"),
    ('F6 h_bound sign', "    h = d['s_bound'] - d['bound_missing'] + d['bound_extra']", "    h = d['s_bound'] + d['bound_missing'] + d['bound_extra']"),
    ('F6 ps <= off', "    if d['ps_draws'] > d['draws']:", "    if d['ps_draws'] > d['draws'] + 1:"),
    ('identities only on the last line', "        bad = self.ident(d)\n", "        bad = []\n"),
    ('no monotonicity', "            if dec or d['frame'] < p['frame'] or", "            if False and"),
    ('malformed ignored', "('identities (7 families =, 3 pairs <=) hold on every line, 0 malformed lines', s5.malformed == 0 and not s5.ident_bad)",
     "('identities (7 families =, 3 pairs <=) hold on every line, 0 malformed lines', not s5.ident_bad)"),
    ('stereo limit 15', "min(L['stereo_writes'], 16)", "min(L['stereo_writes'], 15)"),
    ('zero limit 33', "min(L['zero_disp'], 32)", "min(L['zero_disp'], 33)"),
    ('letter = variant', "        mm = mismatch(L5, r['journal'], None)", "        mm = mismatch(L5, r['journal'], s5.last_lineno)"),
    ('mode after GuestOut accepted', "    return len(series.mode) >= 1 and (guest_first is None or series.mode[0] < guest_first)",
     "    return len(series.mode) >= 1"),
    ('noimage member dropped', "L5['cmask_fce_noimage'] == 0)]", "True)]"),
    ('sg dcc_rt_pending dropped', "(L5['dcc_rt'] >= 1 and L5['dcc_rt_pending'] >= 1)", "(L5['dcc_rt'] >= 1)"),
    ('sg draws_mesh dropped', "('f5_sg: draws_mesh > 0 (item 433 (v))', L6['draws_mesh'] > 0)", "('f5_sg: draws_mesh > 0 (item 433 (v))', True)"),
    ('cmask_fce_layout out of B', "'cmask_fce_unapplied', 'cmask_fce_layout']", "'cmask_fce_unapplied']"),
    ('null control ignores DiagF6', "res['null_ok'] = r['f5_any'] == 0 and r['f6_any'] == 0", "res['null_ok'] = r['f5_any'] == 0"),
    ('hold minimum 200 s', "HOLD_MIN_US = {'diag': 300000000,", "HOLD_MIN_US = {'diag': 200000000,"),
    ('env diag not required', "            env_ok = env_ok and env.get('KYTY_DIAG_F5') == '1' and env.get('KYTY_DIAG_F6') == '1'", "            pass"),
    ('journal counted once per line', "                c = raw.count(pat)", "                c = 1 if pat in raw else 0"),
    ('w sum member off', "L6['w_mask0'] + L6['w_addr0_fmt'] + L6['w_addr0_nofmt'] > 0", "L6['w_mask0'] + L6['w_addr0_fmt'] + L6['w_addr0_nofmt'] >= 0"),
]


def main():
    src = open(os.path.join(HERE, 'f16f_read.py'), encoding='utf-8').read()
    suite = open(os.path.join(HERE, 'test_f16f_read.py'), encoding='utf-8').read()
    print('sens sens_f16f.py sha256 %s target f16f_read.py sha256 %s suite sha256 %s' % (
        hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
        hashlib.sha256(src.encode('utf-8')).hexdigest(), hashlib.sha256(suite.encode('utf-8')).hexdigest()))
    caught = 0
    bad = []
    for name, a, b in MUT:
        if src.count(a) != 1:
            print('MUTANT %s: anchor count %d - BROKEN' % (name, src.count(a)))
            bad.append(name)
            continue
        d = tempfile.mkdtemp(prefix='f16f_sens_')
        open(os.path.join(d, 'f16f_read.py'), 'w', encoding='utf-8', newline='\n').write(src.replace(a, b))
        open(os.path.join(d, 'test_f16f_read.py'), 'w', encoding='utf-8', newline='\n').write(suite)
        pr = subprocess.run([sys.executable, os.path.join(d, 'test_f16f_read.py')], capture_output=True, cwd=d)
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
