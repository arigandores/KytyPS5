"""Audit 108: mutants of fam108.py, each disabling or weakening one admission/decision term; run test_fam108.py on each."""
import subprocess
import sys
from pathlib import Path

SRC = Path('C:/kyty/s108/fam108.py').read_text(encoding='utf-8')
OUT = Path('C:/kyty/s108/audit108/mutants')
OUT.mkdir(exist_ok=True)

MUTANTS = {
    'S2_off': ("'S2_dt_2se_excludes_0': (dt['mean'] is not None and dt['se'] is not None\n"
               "                                 and dt['mean'] + 2 * dt['se'] < 0),",
               "'S2_dt_2se_excludes_0': True,"),
    'S2_1se': ("and dt['mean'] + 2 * dt['se'] < 0)", "and dt['mean'] + 1 * dt['se'] < 0)"),
    'S1_bar_-50': ("dt['mean'] <= SHIP_US,", "dt['mean'] <= SHIP_US + 50,"),
    'SYNC_off': ("controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK",
                 "controls['SYNC_COMPILE'] = True"),
    'SYNC_slack3': ("controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK",
                    "controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK + 1"),
    'SYNC_kept_rows_only': ("sync = {a: sum(r.get('cs_sync_new', 0) for n, r in rows.items() if n >= geo['first'] and r.get('arm') == a)",
                            "sync = {a: sum(rows[n].get('cs_sync_new', 0) for n in sel['rows'] if rows[n].get('arm') == a)"),
    'SYNC_arm_swapped': ("controls['SYNC_COMPILE'] = sync[1] <= sync[0] + SYNC_SLACK",
                         "controls['SYNC_COMPILE'] = sync[0] <= sync[1] + SYNC_SLACK"),
    'FAM_ARMED_off': ("checks['FAMILY_ARMED_ARM1'] = bool((lev[1].get('cspfam_skip') or 0) >= 1)",
                      "checks['FAMILY_ARMED_ARM1'] = True"),
    'FAM_ARMED_look': ("checks['FAMILY_ARMED_ARM1'] = bool((lev[1].get('cspfam_skip') or 0) >= 1)",
                       "checks['FAMILY_ARMED_ARM1'] = bool((lev[1].get('cspfam_look') or 0) >= 1)"),
    'FAM_DARK_off': ("checks['FAMILY_DARK_ARM0'] = look0 == 0", "checks['FAMILY_DARK_ARM0'] = True"),
    'PIN_ONCE_off': ("controls['PIN_ONCE'] = pins.get('1', 0) == 1 and sum(pins.values()) == 1",
                     "controls['PIN_ONCE'] = True"),
    'PIN_ONCE_any': ("controls['PIN_ONCE'] = pins.get('1', 0) == 1 and sum(pins.values()) == 1",
                     "controls['PIN_ONCE'] = pins.get('1', 0) >= 1"),
    'IDENTITY_off': ("result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)",
                     "result['integrity']['IDENTITY'] = True"),
    'IDENTITY_meta_only': ("result['integrity']['IDENTITY'] = (exe_sha == result.get('binary_sha256') == BINARY_SHA)",
                           "result['integrity']['IDENTITY'] = (result.get('binary_sha256') == BINARY_SHA)"),
    'MIN_PAIRS_1': ('MIN_PAIRS = 60', 'MIN_PAIRS = 1'),
    'VIDEO_pin_off': ("'pinned': env.get('KYTY_GPU_CLOCK_PIN') == '1',", "'pinned': True,"),
    'VIDEO_frames_1000': ('VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 1000'),
    'KEEP_all': ('KEEP_LO, KEEP_HI = 60, 89', 'KEEP_LO, KEEP_HI = 0, 90'),
    'ROW_ARMS_off': ("integrity['ROW_ARMS'] = all(", "integrity['ROW_ARMS'] = True or all("),
    'FATAL_no_skipped_draw': ("b'AsyncPipelines: skipped draw')", "b'AsyncPipelines: skipped draw XX')"),
    'CPU_NET_no_spin': ("out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']",
                        "out['cpu_net_us'] = row['cpu_gpu_us']"),
    'ABBA_pattern_unchecked': ("or g['arm'] != (0, 1, 1, 0)[i % 4] ", ""),
}

res = {}
for name, (old, new) in MUTANTS.items():
    if SRC.count(old) != 1:
        res[name] = 'ANCHOR x%d' % SRC.count(old)
        continue
    p = OUT / ('fam108_%s.py' % name)
    p.write_text(SRC.replace(old, new), encoding='utf-8')
    r = subprocess.run([sys.executable, 'C:/kyty/s108/test_fam108.py', str(p)], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    txt = r.stdout + r.stderr
    (OUT / ('%s.out' % name)).write_text(txt, encoding='utf-8')
    failed = [ln.split()[0] for ln in txt.splitlines() if (' FAIL ' in ln or ln.rstrip().endswith('FAIL')
                                                           or ' MISMATCH' in ln or ' BAD' in ln)]
    allok = 'ALL OK' in txt
    res[name] = 'SURVIVED' if allok else 'KILLED (%s)' % (', '.join(failed[:4]) or txt.strip().splitlines()[-1][:80])
    print('%-24s %s' % (name, res[name]), flush=True)
