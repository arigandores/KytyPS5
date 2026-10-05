"""F20l (HPP-631): manual sensitivity of test_b32_read.py - each edit of b32_read.py below must make the suite fail (exit != 0).
Form of F20e sens_f20e.py; the edits run 8 at a time.  usage: python sens_b32.py   (ASCII only; ends with ALL OK when every edit is
caught)"""
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'b32_read.py'), 'rb').read().decode('utf-8')
print('suite sens_b32.py sha256 %s target b32_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
EDITS = [
    ('slow threshold 100 001', 'SLOW_US = 100000', 'SLOW_US = 100001'),
    ('short threshold 70 001', 'SHORT_US = 70000', 'SHORT_US = 70001'),
    ('10 s + 1 us', 'WIN_US = 10000000', 'WIN_US = 10000001'),
    ('neighbours 9', 'NEIGH = 10', 'NEIGH = 9'),
    ('B2 window low 724', 'B2_LO, B2_HI = 723, 828', 'B2_LO, B2_HI = 724, 828'),
    ('B2 window high 827', 'B2_LO, B2_HI = 723, 828', 'B2_LO, B2_HI = 723, 827'),
    ('neighbours keep slow frames', "        if frames[j][2] < SLOW_US:\n            out.append(frames[j][1])\n        j -= 1",
     "        out.append(frames[j][1])\n        j -= 1"),
    ('freeze strict', "(num(h.get('sgap_max_us'), 0) or 0) >= 0.5 * e_us", "(num(h.get('sgap_max_us'), 0) or 0) > 0.5 * e_us"),
    ('freeze off', "    if h is not None and e_us is not None and (num", "    if False and h is not None and e_us is not None and (num"),
    ('i2 not checked', "        if h.get('i2') != 1:", "        if False:"),
    ('samples 0 not checked', "        if not h.get('samples'):", "        if False:"),
    ('no -x line accepted', "        return ['no -x line']", "        return []"),
    ('req_miss_w not an invariant', "'lines_cut_w', 'req_miss_w', 'sub_miss_w')", "'lines_cut_w', 'sub_miss_w')"),
    ('sub_miss_w not an invariant', "'lines_cut_w', 'req_miss_w', 'sub_miss_w')", "'lines_cut_w', 'req_miss_w')"),
    ('cumulative instead of _w', "return [k for k in ZERO_W if num(x.get(k), 0) != 0]", "return [k for k in ZERO_W if num(x.get(k[:-2]), 0) != 0]"),
    ('load strict', "other >= theta * ncpu * win:", "other > theta * ncpu * win:"),
    ('load without theta at 0.75', "    if theta is not None and ncpu and win", "    theta = 0.75 if theta is None else theta\n    if theta is not None and ncpu and win"),
    ('holder strict', "holder = vo if fr['lat'] - b['lat'] >= 0.5 * e_us else fl", "holder = vo if fr['lat'] - b['lat'] > 0.5 * e_us else fl"),
    ('holder always flip', "holder = vo if fr['lat'] - b['lat'] >= 0.5 * e_us else fl", "holder = fl"),
    ('half strict', '    half = 0.5 * samples\n', '    half = 0.5 * samples + 0.5\n'),
    ('W before H', "    hs = [(row['H'].get(c, 0), -i, c) for i, c in enumerate(CALLS) if row['H'].get(c, 0) >= half]\n    if hs:",
     "    hs = [(row['H'].get(c, 0), -i, c) for i, c in enumerate(CALLS) if row['H'].get(c, 0) >= half]\n    if hs and not any(v >= half for v in row['W'].values()):"),
    ('r counts as R', "        if (num(row.get(st), 0) or 0) >= half:",
     "        if (num(row.get(st), 0) or 0) + ((num(row.get('r'), 0) or 0) if st == 'R' else 0) >= half:"),
    ('present not a driver call', "DRIVER = ('present', 'acquire', 'qsubmit', 'semwait')", "DRIVER = ('acquire', 'qsubmit', 'semwait')"),
    ('protect a driver call', "DRIVER = ('present', 'acquire', 'qsubmit', 'semwait')", "DRIVER = ('present', 'acquire', 'qsubmit', 'semwait', 'protect')"),
    ('lock includes the holder', "others = [t for t in d['t'] if t['slot'] != cur and t['H'].get('qlock', 0) >= 0.5 * samples]",
     "others = [t for t in d['t'] if t['H'].get('qlock', 0) >= 0.5 * samples]"),
    ('lock strict', "t['H'].get('qlock', 0) >= 0.5 * samples]", "t['H'].get('qlock', 0) > 0.5 * samples]"),
    ('DRV_GPU strict', "fr['gbusy'] >= b['gbusy'] + 0.5 * e_us:", "fr['gbusy'] > b['gbusy'] + 0.5 * e_us:"),
    ('DRV_GPU before EMU_LOCK', "                if others:\n                    sp = 'EMU_LOCK'\n                elif",
     "                if False:\n                    sp = 'EMU_LOCK'\n                elif"),
    ('sleep steps to a waker', "            if x == 'sleep':", "            if x == 'sleepX':"),
    ('timeout record steps', "            if best is not None and best.get('to') == 1:", "            if False:"),
    ('record of any kind', "recs = [w for w in d['w'] if w.get('slot') == cur and w.get('kind') == x]", "recs = [w for w in d['w'] if w.get('slot') == cur]"),
    ('first record not the largest overlap', "best = max(recs, key=lambda w: (num(w.get('overlap_us'), 0) or 0)) if recs else None",
     "best = recs[0] if recs else None"),
    ('mutex peer not used', "            elif x == 'mutex' and pr is not None and pr >= 0:", "            elif False:"),
    ('chain 2 steps', "            if step == 3:\n                return 'UNDETERMINED'", "            if step == 2:\n                return 'UNDETERMINED'"),
    ('cycle allowed', "            if target in visited:", "            if False:"),
    ('guest R is EMU_RUN', "            if role != 'guest':\n                return 'EMU_RUN:%s' % role",
     "            if True:\n                return 'EMU_RUN:%s' % role"),
    ('Sr is UNMARKED', "        if st == 'Sr':\n            return 'HOST_PREEMPT'", "        if st == 'SrX':\n            return 'HOST_PREEMPT'"),
    ('RC6 off', "        if busy < 0.5 * samples and reg < 0.5 * samples:", "        if True:"),
    ('RC6 regmem off', "        if busy < 0.5 * samples and reg < 0.5 * samples:", "        if busy < 0.5 * samples:"),
    ('RC6 R only', "        busy = (num(gpu.get('R'), 0) or 0) + sum(gpu['H'].values())", "        busy = (num(gpu.get('R'), 0) or 0)"),
    ('RC6 missing GuestGpu passes', "        if gpu is None:\n            return 'UNDETERMINED', 'UNDETERMINED', 'no GuestGpu -t row for RC6'",
     "        if gpu is None:\n            return cls, cls.split(':')[0], ''"),
    ('INSTR_MADE strict', "x[2] - (row['instr_us'] or 0) < SLOW_US)", "x[2] - (row['instr_us'] or 0) <= SLOW_US)"),
    ('INSTR_MADE on DiagB32 dt', "row['instr_made'] = bool(row['p_i'] and h is not None and x[2] - (row['instr_us'] or 0) < SLOW_US)",
     "row['instr_made'] = bool(row['p_i'] and h is not None and (row['diag_dt_us'] or 0) - (row['instr_us'] or 0) < SLOW_US - 1)"),
    ('B5 in P_I', "row['p_i'] = att not in ('B5', 'B33', 'B1b')", "row['p_i'] = att not in ('B33', 'B1b')"),
    ('K_I without hold', "res['K_I'] = 1 if hold and pi else 0", "res['K_I'] = 1 if pi else 0"),
    ('K counts INSTR_MADE', "res['K'] = 1 if hold and cnt else 0", "res['K'] = 1 if hold and pi else 0"),
    ('kq0 over count, not P_I', "res['kq0'] = sum(1 for x in pi if x['diag'] and x['kq_n'] == 0)",
     "res['kq0'] = sum(1 for x in cnt if x['diag'] and x['kq_n'] == 0)"),
    ('kq0 share over in count', "res['kq0_share'] = round(res['kq0'] / len(pi), 4) if pi", "res['kq0_share'] = round(res['kq0'] / max(1, len(cnt)), 4) if pi"),
    ('m5r >= 0', "res['m5r'] = sum(1 for x in pi if (x['m5r_us'] or 0) > 0)", "res['m5r'] = sum(1 for x in pi if (x['m5r_us'] or 0) >= 0)"),
    ('prev frame strict', "prev_slow=(pos[n] > 0 and frames[pos[n] - 1][2] >= SLOW_US))", "prev_slow=(pos[n] > 0 and frames[pos[n] - 1][2] > SLOW_US))"),
    ('prev over P_I', "res['prev_slow_in_count'] = sum(1 for x in cnt if x['prev_slow'])", "res['prev_slow_in_count'] = sum(1 for x in pi if x['prev_slow'])"),
    ('hold class shortest', "res['hold_class'] = max(cnt, key=lambda x: x['dt_us'])['cls']", "res['hold_class'] = min(cnt, key=lambda x: x['dt_us'])['cls']"),
    ('PK-A EMU_CALL anywhere', "    return x['cls'].startswith('EMU_CALL:') and x.get('term_role') == 'Gpu'", "    return x['cls'].startswith('EMU_CALL:')"),
    ('PK-A EMU_RUN any role', "    if x['cls'] == 'EMU_RUN:Gpu':", "    if x['cls'].startswith('EMU_RUN'):"),
    ('RC13 keeps the lines', "            if line.startswith(b'DiagB32'):\n                n_out += 1\n                continue",
     "            if line.startswith(b'DiagB32X'):\n                n_out += 1\n                continue"),
    ('RC13 compares hold frames only', "same = a['frames'] == s['frames'] and ea['hold_frames'] == es['hold_frames']",
     "same = ea['hold_frames'] == es['hold_frames']"),
    ('bad prefix not counted', "            r['diag_bad_prefix'] += 1      # RC13", "            pass      # RC13"),
    ('recovering not counted', "            r['recovering'] += 1", "            pass"),
    ('stand 2 frames', "nxt = order[k + 1:k + 4] if k is not None else []", "nxt = order[k + 1:k + 3] if k is not None else []"),
    ('load window +2', "for n in range(ns, ne + 4):", "for n in range(ns, ne + 3):"),
    ('load window from n_start+1', "for n in range(ns, ne + 4):", "for n in range(ns + 1, ne + 4):"),
    ('U5(2) keeps B5', "F.attr(x, BIN_TEST, 'letter') != 'B5' and\n", "True and\n"),
    ('U5(2) keeps INSTR_MADE', "not (x[2] >= SLOW_US and n_instr(x[1], ft, diag)))", "True)"),
    ('U5(4) cumulative', "res['zero_w_sum'] = dict((k, sum(num((d['x'] or {}).get(k), 0) or 0 for d in diag.values())) for k in ZERO_W)",
     "res['zero_w_sum'] = dict((k, sum(num((d['x'] or {}).get(k[:-2]), 0) or 0 for d in diag.values())) for k in ZERO_W)"),
    ('admission binary not checked', "jbin == BIN_TEST),", "True),"),
    ('admission installed after not checked', "inst_b == BIN_FS8 and inst_a == BIN_FS8),", "inst_b == BIN_FS8),"),
    ('admission env not checked', "run is not None and extra == form),", "run is not None),"),
    ('admission env subset', "run is not None and extra == form),", "run is not None and all(extra.get(k) == v for k, v in form.items())),"),
    ('admission z0 mode line not checked', "(len(r['mode']) == 0 and r['diag_lines'] == 0))", "True)"),
    ('admission stand not checked', "(stand_ok(tests, want_test) if want_test else not tests)", "True"),
    ('stand mode not checked', "    mode = want.split(':')[1]", "    mode = ''"),
    ('admission rep_drop not checked', "r is not None and r['rep_drop'] == 0)", "r is not None)"),
    ('admission loader mode not checked', "load.get('status') == 'done' and load.get('mode') == LOADER[base_tag])", "load.get('status') == 'done')"),
    ('admission recovering not checked', "r is not None and r['minimized'] == 0 and r['recovering'] == 0)", "r is not None)"),
    ('admission manifest not checked', "bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')", "True"),
    ('admission hold not checked', "(run or {}).get('hold_s') == HOLD_S)", "True)"),
    ('signature not checked', "r is not None and r['sig'] == [SIG_FS8] and r['variant_dir'] == [VARIANT_DIR]),",
     "r is not None and r['variant_dir'] == [VARIANT_DIR]),"),
    ('cache dir not checked', "r is not None and r['sig'] == [SIG_FS8] and r['variant_dir'] == [VARIANT_DIR]),", "r is not None and r['sig'] == [SIG_FS8]),"),
    ('Sw + S variant off', "if sws >= 0.5 * samples else ''", "if False else ''"),
    ('repeat r7 allowed', "(_r[1-6])?$')", "(_r[1-7])?$')"),
    ('non-ASCII output', "    out.append('  ADMISSION %s' % ('PASS' if res['admitted'] else 'FAIL'))",
     "    out.append('  ADMISSION %s' % ('PASS \\u2014' if res['admitted'] else 'FAIL'))"),
]
T = tempfile.mkdtemp(prefix='f20l_sens_')


def one(k):
    name, old, new = EDITS[k]
    if SRC.count(old) != 1:
        return name, None, 'ANCHOR count %d' % SRC.count(old)
    d = os.path.join(T, 'e%02d' % k)
    os.makedirs(d)
    shutil.copy2(os.path.join(HERE, 'test_b32_read.py'), os.path.join(d, 'test_b32_read.py'))
    shutil.copy2(os.path.join(HERE, 'f20e_read.py'), os.path.join(d, 'f20e_read.py'))
    open(os.path.join(d, 'b32_read.py'), 'wb').write(SRC.replace(old, new).encode('utf-8'))
    p = subprocess.run([sys.executable, os.path.join(d, 'test_b32_read.py')], capture_output=True, cwd=d)
    nf = [x for x in p.stdout.decode('ascii', 'replace').split('\n') if x.startswith('checks ') or x.startswith('FAIL ')]
    return name, p.returncode != 0, (nf[0].strip()[:90] if nf else 'no count (rc %d)' % p.returncode)


bad = []
try:
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        for name, caught, note in ex.map(one, range(len(EDITS))):
            print('%s %s (%s)' % ('CAUGHT' if caught else 'MISSED' if caught is not None else 'ANCHOR', name, note))
            if not caught:
                bad.append(name)
finally:
    shutil.rmtree(T, ignore_errors=True)
print('edits %d missed %d' % (len(EDITS), len(bad)))
if bad:
    print('MISSED:', bad)
    sys.exit(1)
print('ALL OK')
