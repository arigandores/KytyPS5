"""S3b (HPP-325): mut_sc_s.py - the 11 anchors broken by the S3b edits re-anchored, new mutants for RC1-RC11 (item 250).
Writes LF; checks that every mutant anchor occurs exactly once in sc_s.py."""
import re
from pathlib import Path

MP = Path('C:/kyty/s288/mut_sc_s.py')
SP = Path('C:/kyty/s288/sc_s.py')
src = SP.read_text(encoding='ascii')
txt = MP.read_bytes().decode('ascii').replace('\r\n', '\n')

FIX = {
    'fam_s': ("'KYTY_S_', 'KYTY_DUMP_', 'KYTY_FIX_')", "'KYTY_DUMP_', 'KYTY_FIX_')"),
    'fam_dump': ("'KYTY_S_', 'KYTY_DUMP_', 'KYTY_FIX_')", "'KYTY_S_', 'KYTY_FIX_')"),
    'pipe1s': ("pipe1s=sum(1 for x in ss if x['gap_pipe_us'] >= K2_US),",
               "pipe1s=sum(1 for x in ss if x['gap_us'] >= K2_US),"),
    'att_held': ("r = sum(1 for x in fz['long'] if counted_row(x) and x['dt'] >= x_us and not x['held'])",
                 "r = sum(1 for x in fz['long'] if counted_row(x) and x['dt'] >= x_us)"),
    'g_perm': ("level_cold = perm_after >= 1 and rec_new_after >= 1 and skip_after >= 1",
               "level_cold = rec_new_after >= 1 and skip_after >= 1"),
    'g_rec': ("level_cold = perm_after >= 1 and rec_new_after >= 1 and skip_after >= 1",
              "level_cold = perm_after >= 1 and skip_after >= 1"),
    'g_skip': ("level_cold = perm_after >= 1 and rec_new_after >= 1 and skip_after >= 1",
               "level_cold = perm_after >= 1 and rec_new_after >= 1"),
    'g_attr': ("cold = attr_ok and level_cold\n", "cold = level_cold\n"),
    'cr_bin': ("ib is not None and len(ib) == 64 and ia == ib,", "ib is not None and len(ib) == 64,"),
    'rp_d': ("d = None if vstop else bool(v['val']['ok'] and v.get('vke') == 0 and v.get('entered'))",
             "d = None if vstop else bool(v['val']['ok'] and v.get('entered'))"),
    'rp_e_g': ("and (rs[t]['glitch'] or {}).get('glitches') == 0", ""),
}

NEW = [
    # RC7 (item 250 (zh), item 245 (a))
    ('fam_fix', "'KYTY_DUMP_', 'KYTY_FIX_')", "'KYTY_DUMP_')"),
    # RC1 / RC2 / RC10 admission rows (item 250 (b), (v), (zh))
    ('cr_bin_len', "ib is not None and len(ib) == 64 and ia == ib,", "ib is not None and ia == ib,"),
    ('cr_bin_none', "ib is not None and len(ib) == 64 and ia == ib,", "ia == ib,"),
    ('cr_prev', "jget(cj, 'return_prev', 'ok') == '1', jget", "True, jget"),
    ('cr_launch', "ml is not None and ml == rg.get('got'),", "True,"),
    ('cr_launch_eq', "ml is not None and ml == rg.get('got'),", "ml is not None,"),
    ('jget_dict', "return v.get(sub) if isinstance(v, dict) else None", "return v.get(sub) if isinstance(v, dict) else v"),
    # RC2 continuity (a data row, not FAIL)
    ('ct_diff', "if ((cj.get(m) or {}).get('sha') or 'x') != ((po.get(r) or {}).get('got') or 'y')]", "if False]"),
    ('ct_glc', "('glc', 'man_pre_glc', 'return_glc'))", "('glc', 'man_pre_glc', 'return_app'))"),
    # RC3 + answer 2 (item 250 (g))
    ('gp_prio', "sub = sum(rows[k][1] for k in idx if rows[k][1] >= K3_US and cl(k)[0] == 'PRIO')",
     "sub = sum(rows[k][1] for k in idx if rows[k][1] >= K3_US and cl(k)[0] in ('PCW', 'PRIO'))"),
    ('gp_old', "sub_old = sum(rows[k][1] for k in idx if rows[k][1] >= K3_US and cl(k)[0] in ('PCW', 'PRIO'))",
     "sub_old = sum(rows[k][1] for k in idx if rows[k][1] >= K3_US and cl(k)[0] == 'PRIO')"),
    ('cr_pcw', "return x['attr'].startswith('SHADER') or x['cls'] == 'PCW'", "return x['attr'].startswith('SHADER')"),
    ('ap_pcw', "return sum(1 for x in fz['long'] if x['cls'] == 'PCW' and x['dt'] >= x_us and not x['held'])",
     "return sum(1 for x in fz['long'] if x['cls'] == 'PRIO' and x['dt'] >= x_us and not x['held'])"),
    ('ao_old', "return r + sum(1 for x in fz['series'] if x['gap_pipe_old_us'] >= x_us)",
     "return r + sum(1 for x in fz['series'] if x['gap_pipe_us'] >= x_us)"),
    # RC8 not attributed
    ('ua_cls', "rows = [x for x in fz['long'] if x['dt'] >= x_us and not x['held'] and not counted_row(x)]",
     "rows = [x for x in fz['long'] if x['dt'] >= x_us and not x['held']]"),
    ('ua_ser', "ser = sum(1 for x in fz['series'] if x['gap_us'] >= x_us and x['gap_pipe_us'] < x_us)",
     "ser = sum(1 for x in fz['series'] if x['gap_us'] >= x_us)"),
    # RC4 cold gate (item 250 (d))
    ('cw_word', "word = 'cold' if cold else ('undetermined (T-3/T-4)' if not attr_ok else 'level not cold')",
     "word = 'cold' if cold else 'level not cold'"),
    ('l0_nc', "if cw == 'level not cold':\n                rows.append", "if False:\n                rows.append"),
    ('c_gate', "g = ok_arm(r) and cw == 'cold'", "g = ok_arm(r)"),
    # RC5 pcw_int class T and the AvTrace pcw lines
    ('int_t', "add('pcw_int', 's6', SKY, 'T',", "add('pcw_int', 's6', SKY, 'M',"),
    ('ov_parse', "elif line.startswith(b'AvTrace: pcw overlap '):", "elif line.startswith(b'AvTrace: pcw overlapX'):"),
    ('rec_parse', "elif line.startswith(b'AvTrace: pcw recipes'):", "elif line.startswith(b'AvTrace: pcw recipesX'):"),
    ('z1_none', "if not ov and not rc:\n        return None", "if not ov:\n        return None"),
    ('z1_wait', "wait_us_max=max(waits) if waits else None", "wait_us_max=sum(waits) if waits else None"),
    ('z1_lock', "lock_us_max=max(lk) if lk else None", "lock_us_max=sum(lk) if lk else None"),
    ('z1_hold', "hold_us_max=max(hd) if hd else None", "hold_us_max=sum(hd) if hd else None"),
    ('z1_word', "elif d is None or z1 is None:\n        word = 'MACHINE_UNDETERMINED'",
     "elif d is None:\n        word = 'MACHINE_UNDETERMINED'"),
    ('chk_int', "chk = zero + one + ('pcw_int',) + ", "chk = zero + one + "),
    # RC6 Incomplete -> ARM1_CODE_DEFECT (item 245 (v))
    ('inc_parse', "elif line.startswith(b'Vulkan pipeline cache: save failed (Incomplete'):",
     "elif line.startswith(b'Vulkan pipeline cache: save failed (IncompleteX'):"),
    ('inc_word', "elif any(inc.values()):\n        word = 'ARM1_CODE_DEFECT'", "elif False:\n        word = 'ARM1_CODE_DEFECT'"),
    ('inc_one', "inc = dict((t, rs[t]['saves']['incomplete']) for t in one)",
     "inc = dict((t, rs[t]['saves']['incomplete']) for t in zero + one)"),
    # RC11 VALIDATION_STOP_PRE_LEVEL (item 250 (z))
    ('vs_vke', "vstop = not v.get('entered') and (v.get('vke') or 0) >= 1", "vstop = not v.get('entered')"),
    ('vs_ent', "vstop = not v.get('entered') and (v.get('vke') or 0) >= 1", "vstop = (v.get('vke') or 0) >= 1"),
    ('d_false', "elif not (b and c and e) or d is False:", "elif not (b and c and e):"),
]

bad = []
for name, (a, b) in FIX.items():
    if src.count(a) != 1:
        bad.append(('fix', name, src.count(a)))
for name, a, b in NEW:
    if src.count(a) != 1:
        bad.append(('new', name, src.count(a)))
if bad:
    raise SystemExit('anchors not unique: %r' % bad)

lines = txt.split('\n')
out = []
seen = set()
for ln in lines:
    m = re.match(r"    \('([a-z0-9_]+)', ", ln)
    if m and m.group(1) in FIX:
        a, b = FIX[m.group(1)]
        out.append('    (%r, %r, %r),' % (m.group(1), a, b))
        seen.add(m.group(1))
        continue
    if ln == '    # seal and main':
        out.append('    # S3b (HPP-325, item 250): RC1-RC11')
        for name, a, b in NEW:
            out.append('    (%r, %r, %r),' % (name, a, b))
    out.append(ln)
assert seen == set(FIX), set(FIX) - seen
new = '\n'.join(out)
new = new.replace('test_sc_s.py.  Run through', 'test_sc_s.py (S3b, HPP-325: anchors moved by item 250, mutants of RC1-RC11 '
                  'added).  Run through', 1)
ns = {}
exec(compile(new, 'mut', 'exec'), ns)
names = [m[0] for m in ns['MUTANTS']]
assert len(names) == len(set(names)), 'duplicate names'
for m in ns['MUTANTS']:
    assert src.count(m[1]) == 1, m[0]
MP.write_bytes(new.encode('ascii'))
print('mutants %d (fixed %d, new %d); all anchors unique in sc_s.py' % (len(names), len(FIX), len(NEW)))
