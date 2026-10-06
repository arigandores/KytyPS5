"""F20l3 (HPP-655): edits of the ported sens_b32.py - the five F20l2 edits whose anchors left the reader (b32_pd reference reread, loader,
FS8 installed) are replaced, and the edits of item 591 are added (PK-A domain and member, cold / warm admission, S18, tag names, form,
the exact Mann-Whitney test, the U5 rule, the series stop rule, --pka).  LF.  usage: python edit_sens_f20l3.py <sens_b32.py>"""
import sys

OLD = [
    '''    ('pd ref with the new binary', "    want_bin = BIN_F20J2 if base_tag == 'b32_pd' else BIN_TEST", "    want_bin = BIN_TEST"),\n''',
    '''    ('pd ref paths in f20l3', "    gg, seal = (G_F20L, SEAL_F20L) if", "    gg, seal = (G, SEAL_PATH) if"),\n''',
    '''    ('pd2 allowed', "TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd)(_r[1-6])?$')", "TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd|b32_pd2)(_r[1-6])?$')"),\n''',
    '''    ('admission installed after not checked', "inst_b == BIN_FS8 and inst_a == BIN_FS8),", "inst_b == BIN_FS8),"),\n''',
    '''    ('admission loader mode not checked', "load.get('status') == 'done' and load.get('mode') == LOADER[base_tag])", "load.get('status') == 'done')"),\n''',
]
NEW = r'''    ('admission installed after not checked', "inst_b == BIN_INST and inst_a == BIN_INST),", "inst_b == BIN_INST),"),
    ('admission installed before not checked', "inst_b == BIN_INST and inst_a == BIN_INST),", "inst_a == BIN_INST),"),
    ('installed S18 short prefix', "BIN_INST = 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a'", "BIN_INST = 'b3cee576'"),
    ('admission loader not checked', "('no loader (%s)' % (None if load is None else load.get('status')), load is None),",
     "('no loader (%s)' % (None if load is None else load.get('status')), True),"),
    ('tag s61 allowed', "b32_s(?:0[1-9]|[1-5][0-9]|60)", "b32_s(?:0[1-9]|[1-5][0-9]|6[01])"),
    ('tag s00 allowed', "b32_s(?:0[1-9]|[1-5][0-9]|60)", "b32_s(?:0[0-9]|[1-5][0-9]|60)"),
    ('tag z0c6 allowed', "|b32_z0c[1-5])(_r[1-6])?$')", "|b32_z0c[1-6])(_r[1-6])?$')"),
    ('tag pa3 allowed', "TAG_RX = re.compile(r'^(b32_pa2?|", "TAG_RX = re.compile(r'^(b32_pa[23]?|"),
    ('form z0c at =1', "KYTY_DIAG_B32='0' if base.startswith('b32_z0c') else '1'", "KYTY_DIAG_B32='1'"),
    ('form without GPU_WALL', "else '1', KYTY_GPU_WALL='1')", "else '1')"),
    ('pa2 not cold', "COLD = ('b32_pa', 'b32_pa2')", "COLD = ('b32_pa',)"),
    ('cold move not checked', "('cold form: reserve moved (%s)' % rmv[:60], rmv.startswith('RESERVE MOVED')),",
     "('cold form: reserve moved (%s)' % rmv[:60], True),"),
    ('cold live folder not checked', "('cold form: live folder cold before the start (%s)' % rcl[:40], rcl.startswith('COLD OK')),",
     "('cold form: live folder cold before the start (%s)' % rcl[:40], True),"),
    ('cold reserve back not checked', "('cold form: reserve back in manifest after (%s)' % rck[:40], rck.startswith('RESERVE IN AFTER')),",
     "('cold form: reserve back in manifest after (%s)' % rck[:40], True),"),
    ('cold precache no line not needed', "r is not None and r['precache_no'] >= 1 and r['precache_recipes'] == 0 and not r['seed_other']),",
     "r is not None and r['precache_recipes'] == 0 and not r['seed_other']),"),
    ('cold recipes line allowed', "r is not None and r['precache_no'] >= 1 and r['precache_recipes'] == 0 and not r['seed_other']),",
     "r is not None and r['precache_no'] >= 1 and not r['seed_other']),"),
    ('cold seed install allowed', "r is not None and r['precache_no'] >= 1 and r['precache_recipes'] == 0 and not r['seed_other']),",
     "r is not None and r['precache_no'] >= 1 and r['precache_recipes'] == 0),"),
    ('warm reserve files allowed', "not rmv and not rcl and not rck)]", "True)]"),
    ('warm one reserve file allowed', "not rmv and not rcl and not rck)]", "not (rmv and rcl and rck))]"),
    ('recipes regex any PipelinePrecache', "PRECACHE_RECIPES = re.compile(rb'^PipelinePrecache: \\d+ recipes ')",
     "PRECACHE_RECIPES = re.compile(rb'^PipelinePrecache: ')"),
    ('seed other includes compatibility', "        if line.startswith(b'ShaderSeed: ') and not line.startswith(b'ShaderSeed: compatibility='):",
     "        if line.startswith(b'ShaderSeed: '):"),
    ('pk3 member strict 2/3', "    return 'ARMED' if 3 * armed >= 2 * n else 'FAIL'", "    return 'ARMED' if 3 * armed > 2 * n else 'FAIL'"),
    ('pk3 member at half', "    return 'ARMED' if 3 * armed >= 2 * n else 'FAIL'", "    return 'ARMED' if 2 * armed >= n else 'FAIL'"),
    ('pk3 not called at 3', "    if n < 3:\n        return 'NOT_CALLED'", "    if n <= 3:\n        return 'NOT_CALLED'"),
    ('pk3 not called at 2', "    if n < 3:\n        return 'NOT_CALLED'", "    if n < 2:\n        return 'NOT_CALLED'"),
    ('pk3 10 s threshold kept', "        if x[2] < SLOW_US or F.attr(x, BIN_TEST, 'letter') != 'B5':",
     "        if x[2] < SLOW_US or x[3] < WIN_US or F.attr(x, BIN_TEST, 'letter') != 'B5':"),
    ('pk3 not only B5', "        if x[2] < SLOW_US or F.attr(x, BIN_TEST, 'letter') != 'B5':",
     "        if x[2] < SLOW_US or F.attr(x, BIN_TEST, 'letter') not in ('B5', 'nothing'):"),
    ('pk3 slow strict', "        if x[2] < SLOW_US or F.attr(x, BIN_TEST, 'letter') != 'B5':",
     "        if x[2] <= SLOW_US or F.attr(x, BIN_TEST, 'letter') != 'B5':"),
    ('pk3 instr ignored', "        if x[2] - instr < SLOW_US:\n            pk3_instr.append", "        if False:\n            pk3_instr.append"),
    ('pk3 instr edge', "        if x[2] - instr < SLOW_US:\n            pk3_instr.append", "        if x[2] - instr <= SLOW_US:\n            pk3_instr.append"),
    ('pk3 armed by the old rule set off', "    for x in pk3:\n        x['armed'] = armed_b5(x)", "    for x in pk3:\n        x['armed'] = x['cls'] == 'EMU_RUN:Gpu'"),
    ('pk3 member from the old pk_a', "    res['pk_a3_member'] = pka_member(len(pk3), res['pk_a3_armed'])",
     "    res['pk_a3_member'] = pka_member(len(res['pk_a']), res['pk_a_armed'])"),
    ('pk3 theta off', "        c = classify(fr, d, b, theta) if b else dict(cls='UNDETERMINED', family='UNDETERMINED', note='no base')\n        pk3.append",
     "        c = classify(fr, d, b, None) if b else dict(cls='UNDETERMINED', family='UNDETERMINED', note='no base')\n        pk3.append"),
    ('pre-scene off by one', "        pre = [(n, ft[n][0]) for n in order[k0:k1 + 1] if ft[n][0] >= SLOW_US]",
     "        pre = [(n, ft[n][0]) for n in order[k0 + 1:k1 + 1] if ft[n][0] >= SLOW_US]"),
    ('pre-scene strict', "        pre = [(n, ft[n][0]) for n in order[k0:k1 + 1] if ft[n][0] >= SLOW_US]",
     "        pre = [(n, ft[n][0]) for n in order[k0:k1 + 1] if ft[n][0] > SLOW_US]"),
    ('mw ties not mid ranks', "            r2[k] = i + j + 2\n", "            r2[k] = 2 * (k + 1)\n"),
    ('mw one-sided', "    extreme = sum(c for s, c in dp[m].items() if abs(s - mean2) >= dev)",
     "    extreme = sum(c for s, c in dp[m].items() if s - mean2 >= s_obs - mean2)"),
    ('mw strict extreme', "    extreme = sum(c for s, c in dp[m].items() if abs(s - mean2) >= dev)",
     "    extreme = sum(c for s, c in dp[m].items() if abs(s - mean2) > dev)"),
    ('mw wrong mean', "    mean2 = m * (n + 1)            # E of the doubled rank sum", "    mean2 = m * n            # E of the doubled rank sum"),
    ('u5 2 % strict edge to 3 %', "                fires=bool(abs(dev) > 0.02 and p < 0.05),", "                fires=bool(abs(dev) > 0.03 and p < 0.05),"),
    ('u5 or instead of and', "                fires=bool(abs(dev) > 0.02 and p < 0.05),", "                fires=bool(abs(dev) > 0.02 or p < 0.05),"),
    ('u5 p 0.10', "                fires=bool(abs(dev) > 0.02 and p < 0.05),", "                fires=bool(abs(dev) > 0.02 and p < 0.10),"),
    ('u5 one-sided dev', "                fires=bool(abs(dev) > 0.02 and p < 0.05),", "                fires=bool(dev > 0.02 and p < 0.05),"),
    ('u5 base mean not median', "    bm = statistics.median(base_meds)", "    bm = statistics.mean(base_meds)"),
    ('u5 F20e base wrong value', "U5_F20E_MEDS = (36818.5, 46632.0,", "U5_F20E_MEDS = (36818.5, 46632.5,"),
    ('u5 z0b median wrong', "('b32_z0b', 41478.5)", "('b32_z0b', 41478.0)"),
    ('z0 base admitted not checked', "        got = [res for t, res in runs.items() if TAG_RX.match(t).group(1) == name and res.get('admitted')]",
     "        got = [res for t, res in runs.items() if TAG_RX.match(t).group(1) == name]"),
    ('z0 base used with 6', "    if len(zb) == 7:", "    if len(zb) >= 6:"),
    ('u5 z0 base ignored in any', "    u1f = u1z['fires'] if u1z is not None else u1['fires']", "    u1f = u1['fires']"),
    ('series not-admitted counted', "        if not base.startswith('b32_s') or not res.get('admitted'):", "        if not base.startswith('b32_s'):"),
    ('series pa counted', "        if not base.startswith('b32_s') or not res.get('admitted'):", "        if base.startswith('b32_z0c') or not res.get('admitted'):"),
    ('series holds include no-hold', "        holds += 1 if h else 0", "        holds += 1"),
    ('series K without hold', "        k += 1 if h and r.get('K') else 0", "        k += 1 if r.get('K') else 0"),
    ('series min holds 28', "HOLDS_MIN, HOLDS_MAX, K_STOP = 29, 60, 3", "HOLDS_MIN, HOLDS_MAX, K_STOP = 28, 60, 3"),
    ('series max holds 59', "HOLDS_MIN, HOLDS_MAX, K_STOP = 29, 60, 3", "HOLDS_MIN, HOLDS_MAX, K_STOP = 29, 59, 3"),
    ('series K stop 2', "HOLDS_MIN, HOLDS_MAX, K_STOP = 29, 60, 3", "HOLDS_MIN, HOLDS_MAX, K_STOP = 29, 60, 2"),
    ('series K 0 continues', "    elif k == 0:\n        stop = 'STOP_U2", "    elif k < 0:\n        stop = 'STOP_U2"),
    ('series upto ignored', "    if upto is not None:\n        st = st[:upto]", "    if False:\n        st = st[:upto]"),
    ('u5(2) factor 1.4', "    u2 = (per > 1.5 * U5_BASE['slow70_per_hold']) if per is not None else None",
     "    u2 = (per > 1.4 * U5_BASE['slow70_per_hold']) if per is not None else None"),
    ('u5(3) not computable counts', "        u3 = None\n        out.append('U5(3) not computable", "        u3 = True\n        out.append('U5(3) not computable"),
    ('u5(3) factor 1.3', "        u3 = b5m > 1.25 * U5_BASE['mean_dt_b5']", "        u3 = b5m > 1.3 * U5_BASE['mean_dt_b5']"),
    ('u5(3) unweighted mean', "            b5sum += r['u5_b5_mean'] * r['u5_b5_n']", "            b5sum += r['u5_b5_mean']"),
    ('u5(4) one tag', "    u4 = nz >= 2", "    u4 = nz >= 1"),
    ('pka pa2 decides first', "    elif a['pk_a3_member'] != 'NOT_CALLED':\n        res = '%s on b32_pa' % a['pk_a3_member']",
     "    elif b is not None and b['pk_a3_member'] != 'NOT_CALLED':\n        res = '%s on b32_pa2' % b['pk_a3_member']\n    elif a['pk_a3_member'] != 'NOT_CALLED':\n        res = '%s on b32_pa' % a['pk_a3_member']"),
    ('pka pooled decides', "    elif b['pk_a3_member'] != 'NOT_CALLED':\n        res = '%s on b32_pa2' % b['pk_a3_member']",
     "    elif pka_member(len(a['pk_a3']) + len(b['pk_a3']), a['pk_a3_armed'] + b['pk_a3_armed']) != 'NOT_CALLED':\n        res = 'ARMED on b32_pa2'"),
    ('pka not-admitted taken', "        tags = sorted(t for t in runs if TAG_RX.match(t).group(1) == name and runs[t].get('admitted'))",
     "        tags = sorted(t for t in runs if TAG_RX.match(t).group(1) == name)"),
'''


def main(argv):
    path = argv[0]
    s = open(path, 'rb').read().decode('utf-8')
    for a in OLD:
        if s.count(a) != 1:
            print('old edit line count %d - refused: %r' % (s.count(a), a[:70]))
            return 1
    s = s.replace(OLD[0], NEW)
    for a in OLD[1:]:
        s = s.replace(a, '')
    open(path, 'wb').write(s.encode('ascii'))
    print('sens edits: %d old removed, %d new lines added' % (len(OLD), NEW.count('\n')))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
