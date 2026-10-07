"""F25f (HPP-669): the sensitivity of test_f25_read.py (the form of F20l3 sens_b32.py - hand edits, not mutlib): every edit below is applied
alone to a copy of f25_read.py in its own folder; the suite must FAIL on each (a kept edit = a hole of the fixtures).  Each old text must
occur exactly once.  Runs the edits on 8 workers.  ASCII only; ends with ALL OK when every edit is caught.
usage: python sens_f25.py"""
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'sens_tmp')
FILES = ('f20e_read.py', 'test_f25_read.py', 'f25f_seal_body.md')
EDITS = [
    ('K2 threshold +1', 'K2_US = 1000000', 'K2_US = 1000001'),
    ('envelope +1', 'ENV_US = 20475000', 'ENV_US = 20475001'),
    ('precursor window -1', 'PRE_US = 5000000', 'PRE_US = 4999999'),
    ('M6 foreign threshold', 'M6_FOREIGN = 8.0', 'M6_FOREIGN = 8.01'),
    ('M6 pad -1 ns', 'M6_PAD_NS = 1500000000', 'M6_PAD_NS = 1499999999'),
    ('H2 records +1', 'H2_REC = 20000', 'H2_REC = 20001'),
    ('N_MID 13', 'N_MIN, N_MID, N_MAX, K_STOP = 5, 14, 20, 3', 'N_MIN, N_MID, N_MAX, K_STOP = 5, 13, 20, 3'),
    ('N_MAX 21', 'N_MIN, N_MID, N_MAX, K_STOP = 5, 14, 20, 3', 'N_MIN, N_MID, N_MAX, K_STOP = 5, 14, 21, 3'),
    ('N_MIN 4', 'N_MIN, N_MID, N_MAX, K_STOP = 5, 14, 20, 3', 'N_MIN, N_MID, N_MAX, K_STOP = 4, 14, 20, 3'),
    ('K_STOP 2', 'N_MIN, N_MID, N_MAX, K_STOP = 5, 14, 20, 3', 'N_MIN, N_MID, N_MAX, K_STOP = 5, 14, 20, 2'),
    ('key 0.5 edge strict', 'if w is not None and 2 * w >= dt:', 'if w is not None and 2 * w > dt:'),
    ('key without n + 1', 'for k in (n, n + 1):', 'for k in (n,):'),
    ('key tie to n + 1', 'cand.append((w, -k, k))', 'cand.append((w, k, k))'),
    ('trunc: header last field not checked', "if d['last']['hdr'] and d['last']['hdr'][0] != LAST_KEY['hdr']:", 'if False:'),
    ('trunc: -x fields of ZERO_W only', "        for k in ZERO_F25:\n            if k not in x:", "        for k in ZERO_W:\n            if k not in x:"),
    ('trunc: -t last key', "LAST_KEY = {'hdr': 'flip_ns', 't': 'peer',", "LAST_KEY = {'hdr': 'flip_ns', 't': 'since_us',"),
    ('trunc: -w last key', "'w': 'peer_tid', 'x': 'others_cut_w'}", "'w': 'peer', 'x': 'others_cut_w'}"),
    ('trunc: no -x not an item', "        out.append('no -x line')", '        pass'),
    ('trunc: header fields', "HDR_NEED = ('dt_us', 'cover_us', 'sgap_max_us', 'flip_ns')", "HDR_NEED = ('dt_us',)"),
    ('agreement +2', "> (num(h.get('sgap_max_us'), 0) or 0) + 1", "> (num(h.get('sgap_max_us'), 0) or 0) + 2"),
    ('envelope check in classify dropped', "    if win > ENV_US:\n        return done('NO_SAMPLES:cover'", "    if False:\n        return done('NO_SAMPLES:cover'"),
    ('hist_exh_w >= 2', "if num(x.get('hist_exh_w'), 0) >= 1:", "if num(x.get('hist_exh_w'), 0) >= 2:"),
    ('agreement not used in classify', '    if agreement_bad(h, x):\n        return done', '    if False:\n        return done'),
    ('HOST_FREEZE strict', "if e_us is not None and (num(h.get('sgap_max_us'), 0) or 0) >= 0.5 * e_us:",
     "if e_us is not None and (num(h.get('sgap_max_us'), 0) or 0) > 0.5 * e_us:"),
    ('zero_bad on ZERO_W', 'return [k for k in ZERO_F25 if', 'return [k for k in ZERO_W if'),
    ('others_cut_w not a zero invariant', "ZERO_F25 = ZERO_W + ('hist_exh_w', 'w_cut_w', 'others_cut_w')", "ZERO_F25 = ZERO_W + ('hist_exh_w', 'w_cut_w')"),
    ('INSTR_MADE_K2 <=', "dt - (row['instr_us'] or 0) < K2_US)", "dt - (row['instr_us'] or 0) <= K2_US)"),
    ('B33 not excluded', "row['p_i'] = att not in ('B5', 'B33', 'B1b')", "row['p_i'] = att not in ('B5', 'B1b')"),
    ('NO_SAMPLES:key as INSTR_MADE', "h is not None and dt - (row['instr_us'] or 0) < K2_US)", "(h is None or dt - (row['instr_us'] or 0) < K2_US))"),
    ('SHARED_WIN +2', "b['n'] == a['n'] + 1:", "b['n'] == a['n'] + 2:"),
    ('precursor strict', "0 <= c['t_us'] - x['t_us'] <= PRE_US", "0 <= c['t_us'] - x['t_us'] < PRE_US"),
    ('K_I from cnt', "res['K_I'] = 1 if res['hold_any'] and (k2 or abort_hold) else 0", "res['K_I'] = 1 if res['hold_any'] and (cnt or abort_hold) else 0"),
    ('K from k2', "res['K'] = 1 if res['hold_any'] and (cnt or abort_hold) else 0", "res['K'] = 1 if res['hold_any'] and (k2 or abort_hold) else 0"),
    ('abort strict 10 s', 'hold=ab is not None and ab >= WIN_US / 1e6)', 'hold=ab is not None and ab > WIN_US / 1e6)'),
    ('abort error line anywhere', "not (ia is not None and i > ia and x == '--- Error ---')", "not (ia is not None and x == '--- Error ---')"),
    ('abort not a hold', "res['hold_any'] = bool(e['hold'] or abort_hold)", "res['hold_any'] = bool(e['hold'])"),
    ('form SEM strict', 'if semwait is not None and 2 * semwait >= dt:', 'if semwait is not None and 2 * semwait > dt:'),
    ('form NOFLIP strict', 'if fh_other is not None and 2 * fh_other >= dt:', 'if fh_other is not None and 2 * fh_other > dt:'),
    ('M6 foreign strict', "s['foreign'] >= M6_FOREIGN", "s['foreign'] > M6_FOREIGN"),
    ('M6 start strict', "start - M6_PAD_NS <= s['qpc']", "start - M6_PAD_NS < s['qpc']"),
    ('M6 end strict', "s['qpc'] <= end + M6_PAD_NS", "s['qpc'] < end + M6_PAD_NS"),
    ('calibration max', '    pairs.sort()\n', '    pairs.sort(reverse=True)\n'),
    ('calibration sign', 'pairs.append((cal[n] - fn, n))', 'pairs.append((fn - cal[n], n))'),
    ('M6 window start /10', 'start = end - dt * 1000', 'start = end - dt * 100'),
    ('read_cal last sight', '            if n not in out:\n                out[n] = int(m.group(1))', '            if True:\n                out[n] = int(m.group(1))'),
    ('H2 strict', 'if prev >= H2_REC:', 'if prev > H2_REC:'),
    ('H2 window n - 2', 'p = diag.get(n - 1)', 'p = diag.get(n - 2)'),
    ('U5 envelope dropped', '        if win > ENV_US:\n            excl.append', '        if False:\n            excl.append'),
    ('warm member from 0 s', 'warm_dump = [(x[1], x[4] + x[5]) for x in frames if x[3] >= WIN_US and', 'warm_dump = [(x[1], x[4] + x[5]) for x in frames if x[3] >= 0 and'),
    ('warm need without series', "warm_need = kind in ('series', 'control0', 'stand')", "warm_need = kind in ('control0', 'stand')"),
    ('NOT_WARM as admitted', '    elif warm_need and not warm_ok:', '    elif False:'),
    ('admission abort 22', "env.get('KYTY_GPU_HANG_ABORT_S') == HANG_ABORT)", "env.get('KYTY_GPU_HANG_ABORT_S') != '0')"),
    ('admission harness level', 'and hlev == level),', '),'),
    ('admission fixed level', '(want_level is None or level == want_level)', 'True'),
    ('admission prewarm noreturn', "noret.startswith('NO RETURN')))", 'True))'),
    ('admission warm noreturn', "and not noret))", '))'),
    ('admission snap_cmp', "bool(scmp) and scmp[0].startswith('manifest cmp EQUAL')", 'True'),
    ('admission hold member', "r is not None and r['hold_any']),", 'r is not None),'),
    ('admission other death', "r is not None and not other_death),", 'r is not None),'),
    ('control stand min -1', "sf['dt_us'] >= STAND_MIN_US[base]),", "sf['dt_us'] >= STAND_MIN_US[base] - 1),"),
    ('control w_cut_w', "zw.get('lines_cut_w') == 0 and zw.get('w_cut_w') == 0 and", "zw.get('lines_cut_w') == 0 and True and"),
    ('control others_cut_w', "zw.get('others_cut_w') == 0),", 'True),'),
    ('control trunc windows', "             not any(any('without' in i", "             True or any(any('without' in i"),
    ('control key', "('key reduced (window %s, branch %s)' % (key, sf.get('key_branch')), key is not None),",
     "('key reduced (window %s, branch %s)' % (key, sf.get('key_branch')), True),"),
    ('control hist_exh_w', "zw.get('hist_exh_w') == 0),", 'True),'),
    ('control pb class', "str(sf['cls']).startswith('EMU_CALL:present')", 'True'),
    ('control pc class', "(sf['cls'] == 'UNMARKED:Gpu' or bool(sf.get('gpu_sw_or_s50')))", 'True'),
    ('control z lines', "r['diag_lines'] == 0 and not r['mode'])]", "not r['mode'])]"),
    ('stop K_I 0 or 1 as U2', '        if ki == 0:', '        if ki <= 1:'),
    ('stop N_MAX strict', '    if n >= N_MAX:', '    if n > N_MAX:'),
    ('same hash needs 3', 'if len(ts) >= 2)', 'if len(ts) >= 3)'),
    ('interference budget >=', "' - STOP_INTERFERENCE' if interf > BUDGET_INTERF else ''", "' - STOP_INTERFERENCE' if interf >= BUDGET_INTERF else ''"),
    ('U5(4) needs 3', 'u4 = len(u5_tags) >= 2', 'u4 = len(u5_tags) >= 3'),
    ('cold 5 strict', 'if len(tags) >= COLD_MAX else', 'if len(tags) > COLD_MAX else'),
    ('controls FAIL as PASS', "ctl = 'PENDING' if None in cres.values() else ('PASS' if all(cres.values()) else",
     "ctl = 'PENDING' if None in cres.values() else ('PASS' if True else"),
    ('hold class shortest', "        big = max(cnt, key=lambda x: x['dt_us'])", "        big = min(cnt, key=lambda x: x['dt_us'])"),
    ('FlipHold not kept', "cur['fh'] = max(cur['fh'], int(m.group(1)))", "cur['fh'] = 0"),
    ('hash not lowered', "cur['hashes'].append(m.group(1).decode('ascii').lower())", "cur['hashes'].append(m.group(1).decode('ascii'))"),
    ('NO_SAMPLES family', "out.update(cls=cls, family=cls.split(':')[0], note=note)", "out.update(cls=cls, family=cls, note=note)"),
    ('abort class', "res['hold_class'], res['hold_family'] = 'NO_SAMPLES:abort', 'NO_SAMPLES'",
     "res['hold_class'], res['hold_family'] = 'NO_SAMPLES', 'NO_SAMPLES'"),
    ('first_good any status', "def first_good(runs, base, want=('ADMITTED',)):", "def first_good(runs, base, want=('ADMITTED', 'INTERFERENCE', 'NOT_WARM')):"),
    ('level of the scene fixed', '    F.SG = level.encode()', '    F.SG = b\'pot_treasure_cave\''),
]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(i, name, a, b, src):
    d = os.path.join(WORK, 'e%02d' % i)
    os.makedirs(d)
    for f in FILES:
        shutil.copy2(os.path.join(HERE, f), d)
    if src.count(a) != 1:
        return i, name, 'BAD EDIT (old text occurs %d times)' % src.count(a)
    open(os.path.join(d, 'f25_read.py'), 'w', encoding='ascii', newline='\n').write(src.replace(a, b))
    p = subprocess.run([sys.executable, os.path.join(d, 'test_f25_read.py')], capture_output=True, cwd=d, timeout=300)
    out = p.stdout.decode('ascii', 'replace')
    caught = p.returncode != 0
    crashed = 'FAILED' not in out
    fails = [l for l in out.splitlines() if l.startswith('FAIL ')]
    return i, name, ('caught%s (%d FAIL lines; first: %s)' % (' by a crash' if crashed else '', len(fails), fails[0][:90] if fails else p.stderr.decode('ascii', 'replace')[-90:].strip())
                     if caught else 'KEPT')


def main():
    src = open(os.path.join(HERE, 'f25_read.py'), encoding='ascii').read()
    print('suite sens_f25.py sha256 %s target f25_read.py sha256 %s test_f25_read.py sha256 %s' % (
        sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'f25_read.py')), sha(os.path.join(HERE, 'test_f25_read.py'))))
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    p = subprocess.run([sys.executable, os.path.join(HERE, 'test_f25_read.py')], capture_output=True, cwd=HERE, timeout=300)
    base_ok = p.returncode == 0 and 'ALL OK' in p.stdout.decode('ascii', 'replace')
    print('control: the suite on the unedited reader %s' % ('ALL OK' if base_ok else 'FAILED'))
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda x: run(x[0], x[1][0], x[1][1], x[1][2], src), enumerate(EDITS)))
    kept = 0
    for i, name, r in sorted(res):
        print('edit %02d %-40s %s' % (i, name, r))
        kept += 0 if r.startswith('caught') else 1
    shutil.rmtree(WORK)
    print('edits %d caught %d kept %d' % (len(EDITS), len(EDITS) - kept, kept))
    print('ALL OK' if base_ok and kept == 0 else 'FAILED')
    return 0 if base_ok and kept == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
