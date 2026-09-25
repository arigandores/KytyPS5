"""Session 119: mutants of g2_119.py - each must be killed by test_g2_119.py.  At the seal they are run through the
frozen mutlib v4.1 (--control --no-memo, work dir C:/kyty/s119/work*) on the sealed copy; this loop is the draft check
(one fresh `python test_g2_119.py <mutant>` per mutant, mutant files in C:/kyty/s119/work_mut119).  The mutants cover
every line the derivation changed (make_g2_119.py) and the G2 arithmetic and rule carried from a104.py."""
import subprocess
import sys
from pathlib import Path

STAGE = Path('C:/kyty/s119/work_mut119')
SRC = Path('C:/kyty/s119/g2_119.py').read_text(encoding='utf-8')
MUTANTS = [
    # the constants of ROADMAP 118 item 6 / 119 item 1
    ('f_050', 'F_SERIAL = 0.555', 'F_SERIAL = 0.5'),
    ('f_030', 'F_SERIAL = 0.555', 'F_SERIAL = 0.30'),
    ('f_sens', 'F_SENS = 0.564', 'F_SENS = 0.39'),
    ('spine_direct', 'SPINE_DIRECT_US = 959.0', 'SPINE_DIRECT_US = 900.0'),
    ('bar', 'BAR_US = 3000.0', 'BAR_US = 3001.0'),
    ('c_ts', 'C_TS_NS = 3.96', 'C_TS_NS = 3.5'),
    ('w_e', 'W_E_S101_US = 675.455 + 440.120', 'W_E_S101_US = 675.455'),
    ('area_xrun_hi', 'AREA_XRUN_PCT = 3.0', 'AREA_XRUN_PCT = 3.2'),
    ('area_xrun_lo', 'AREA_XRUN_PCT = 3.0', 'AREA_XRUN_PCT = 2.8'),
    ('min_pairs', 'MIN_PAIRS = 30', 'MIN_PAIRS = 31'),
    ('binary', "BINARY_SHA = 'd3a981a2", "BINARY_SHA = 'd3a981a3"),
    ('gates_sha', "GATES_SHA = '303a7849", "GATES_SHA = '303a7848"),
    ('sh_arm1', "SH_ARMS = ('shadowresolve=0 shadowmask=3', 'shadowresolve=1 shadowmask=3')",
     "SH_ARMS = ('shadowresolve=0 shadowmask=3', 'shadowresolve=4 shadowmask=3')"),
    ('tag_mut', "                tag_re=r'mut119b?(?:_entry1)?'),", "                tag_re=r'mut1\\d\\db?(?:_entry1)?'),"),
    # the spine: max(mut arm-0 proxy, 959)
    ('spine_min', "                  else max(lvl(mut, 0, 'spine_us'), SPINE_DIRECT_US))",
     "                  else min(lvl(mut, 0, 'spine_us'), SPINE_DIRECT_US))"),
    ('spine_sh', "                  else max(lvl(mut, 0, 'spine_us'), SPINE_DIRECT_US))",
     "                  else max(lvl(sh, 0, 'spine_us'), SPINE_DIRECT_US))"),
    ('spine_proxy_only', "                  else max(lvl(mut, 0, 'spine_us'), SPINE_DIRECT_US))",
     "                  else lvl(mut, 0, 'spine_us'))"),
    # the arming changes
    ('one_worker_len', "    checks['SH_ONE_WORKER'] = sorted(counts['shadow_workers']) == [0]",
     "    checks['SH_ONE_WORKER'] = len(counts['shadow_workers']) == 1"),
    ('one_worker_any', "    checks['SH_ONE_WORKER'] = sorted(counts['shadow_workers']) == [0]",
     "    checks['SH_ONE_WORKER'] = 0 in counts['shadow_workers']"),
    ('mut_dark_wjobs', "        for k in ('sh_jobs',):                 # da_wjobs: the dawalk=1 walker is the production path",
     "        for k in ('sh_jobs', 'da_wjobs'):"),
    ('mut_dark_none', "        for k in ('sh_jobs',):                 # da_wjobs: the dawalk=1 walker is the production path",
     "        for k in ():"),
    ('sh_dark_wjobs', "        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):",
     "        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n', 'da_wjobs'):"),
    ('sh_dark_hold', "        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):",
     "        for k in ('a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):"),
    # the G2 arithmetic and the rule
    ('g_tax_sign', '    return cpu_net - (s_ctx + f * (cpu_net - s_ctx)) - spine - t4',
     '    return cpu_net - (s_ctx + f * (cpu_net - s_ctx)) - spine + t4'),
    ('g_spine_drop', '    return cpu_net - (s_ctx + f * (cpu_net - s_ctx)) - spine - t4',
     '    return cpu_net - (s_ctx + f * (cpu_net - s_ctx)) - t4'),
    ('cpu_net_mut', "    t['cpu_net'] = lvl(sh, 0, 'cpu_net_us')", "    t['cpu_net'] = lvl(mut, 0, 'cpu_net_us')"),
    ('tax_on_dt', "    ps = pstat(sh, 'cpu_net_us')", "    ps = pstat(sh, 'dt_us')"),
    ('s_now_no_di', "        c['S_now'] = t['S_raw'] - max(t['P_mw'], 0.0) - t['dI']",
     "        c['S_now'] = t['S_raw'] - max(t['P_mw'], 0.0)"),
    ('e_move_no_we', "    c['E_move'] = None if t['E_rec'] is None else t['E_rec'] + W_E_S101_US",
     "    c['E_move'] = None if t['E_rec'] is None else t['E_rec']"),
    ('kill_f', "        kill_t4 = (1.0 - F_SERIAL) * (t['cpu_net'] - c['S_ctx']) - t['spine'] - BAR_US",
     "        kill_t4 = (1.0 - 0.30) * (t['cpu_net'] - c['S_ctx']) - t['spine'] - BAR_US"),
    ('rule_le', "        if_admitted = ('A_CLOSED_FOR_MAX_FPS' if central < BAR_US else 'A_PROCEEDS_BY_STAGES')",
     "        if_admitted = ('A_CLOSED_FOR_MAX_FPS' if central <= BAR_US else 'A_PROCEEDS_BY_STAGES')"),
    ('rule_ceiling', "    central = g['central']['G']", "    central = g['ceiling']['G']"),
    ('area_gate', "    if x is None or abs(x) * 100.0 > AREA_XRUN_PCT:", "    if x is None:"),
    ('verdict_admit', "        'verdict': if_admitted if not reasons else 'NOT_EVALUABLE',",
     "        'verdict': if_admitted,"),
    # item 3 probes of the pre-seal check
    ('sh_dark_mw', "        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):",
     "        for k in ('a_hold_us', 'a_mut_us', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):"),
    ('sh_dark_amut', "        for k in ('a_hold_us', 'a_mut_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):",
     "        for k in ('a_hold_us', 'mw_n', 'pl_em_n', 'pl_proc_n', 'pl_prog_n'):"),
    ('worker_set', "    checks['SH_ONE_WORKER'] = sorted(counts['shadow_workers']) == [0]",
     "    checks['SH_ONE_WORKER'] = set(counts['shadow_workers']) == {0}"),
    ('area_abs', "    if x is None or abs(x) * 100.0 > AREA_XRUN_PCT:", "    if x is None or x * 100.0 > AREA_XRUN_PCT:"),
    ('a11b_ge', "        g['central']['G'], None, BAR_US - 1e-9)", "        g['central']['G'], BAR_US, None)"),
    ('tag_sh', "               tag_re=r'sh119b?(?:_entry1)?'),", "               tag_re=r'sh1\\d\\db?(?:_entry1)?'),"),
]
if __name__ == '__main__':
    STAGE.mkdir(parents=True, exist_ok=True)
    killed = 0
    for name, old, new in MUTANTS:
        if SRC.count(old) != 1:
            print('%-18s ANCHOR x%d' % (name, SRC.count(old)))
            continue
        path = STAGE / ('mut_g2_119_%s.py' % name)
        path.write_bytes(SRC.replace(old, new).encode('utf-8'))
        r = subprocess.run([sys.executable, 'C:/kyty/s119/test_g2_119.py', str(path)], capture_output=True, text=True)
        killed += r.returncode != 0
        print('%-18s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
        path.unlink()
    print('killed %d of %d' % (killed, len(MUTANTS)))
