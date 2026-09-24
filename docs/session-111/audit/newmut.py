# New mutants (audit 111) of the sealed shp111.py and vds111b.py, run against their fixture suites (copies in
# audit111/rerun).  A mutant is KILLED when the set of failing fixture cases differs from the unmutated baseline
# (shp111: {CONSTANTS} by design on the sealed copy; vds111b: none).  Everything is written under audit111/mut.
import re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
A = Path('C:/kyty/s111/audit111'); R = A / 'rerun'; M = A / 'mut'
M.mkdir(exist_ok=True)
SHP = (R / 'shp111.py').read_text(encoding='utf-8')
VDS = (R / 'vds111b.py').read_text(encoding='utf-8')
muts = []


def mut(target, name, old, new):
    src = SHP if target == 'shp' else VDS
    assert src.count(old) == 1, (name, old)
    muts.append((target, name, src.replace(old, new)))


mut('shp', 'S2_le0', "and dt['mean'] + 2 * dt['se'] < 0)", "and dt['mean'] + 2 * dt['se'] <= 0)")
mut('shp', 'FATAL_no_unhandled', "b'Unhandled exception:', ", "")
mut('shp', 'FATAL_no_devicelost', "b'ErrorDeviceLost', ", "")
mut('shp', 'FATAL_no_terminate', "b'--- std::terminate ---', ", "")
mut('shp', 'SLOT_DARK_tol5', "checks['SLOT_DARK_ARM0'] = free0 == 0", "checks['SLOT_DARK_ARM0'] = free0 is not None and free0 <= 5")
mut('shp', 'BANDS_gpu_wide', "'gpu_busy_us': (10000.0, 16000.0)}", "'gpu_busy_us': (1000.0, 160000.0)}")
mut('shp', 'HOLD_tol_50', "if (a.get('hold_s') or 0) < HOLD_S - 5:", "if (a.get('hold_s') or 0) < HOLD_S - 50:")
mut('shp', 'AREA_min_flips_0', "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 8",
    "AREA_TOL_PCT, AREA_WORK_PCT, AREA_MIN_FLIPS = 1.0, 90.0, 0.5, 0.5, 0")
mut('shp', 'ID_TOL_10x', "ID_TOL = 0.01", "ID_TOL = 0.1")
mut('shp', 'VIDEO_frames_strict', "'frames': frames is not None and frames >= VIDEO_MIN_FRAMES,",
    "'frames': frames is not None and frames > VIDEO_MIN_FRAMES,")
mut('shp', 'SCHEMA_no_q_taking', "'da_guard_busy': 'x', 'da_q_taking': 'x',", "'da_guard_busy': 'x',")
mut('shp', 'DROPS_loose', "checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= DROP_MAX",
    "checks['WALK_DROPS_ARM%d' % a] = bool(po) and dr is not None and dr / po <= 1.0")
mut('vds', 'V_ARMED_checks_1', "MIN_CHECKS = 10000", "MIN_CHECKS = 1")
mut('vds', 'V_BAD_no_lines', "bad = tot['da_slot_bad'] + tot['da_chk_bad'] + sum(mismatch.values())",
    "bad = tot['da_slot_bad'] + tot['da_chk_bad']")
mut('vds', 'V_PIN_ge1', "if pins != 1 or pin1 != 1:", "if pin1 < 1:")
mut('vds', 'V_ROWS_4000', "MIN_ROWS = 5000", "MIN_ROWS = 4000")
mut('vds', 'V_GATES_no_count', "gates.count(' smemocheck=') != 1\n            or ", "")
mut('vds', 'V_ATTEMPT_hold_half', "< 0.95 * HOLD_S):", "< 0.5 * HOLD_S):")
mut('vds', 'V_FORBID_no_precache', ", 'KYTY_PIPELINE_PRECACHE')", ")")
mut('vds', 'V_MARKERS_stdout_off', "markers += scan_markers(Path(root) / ('stdout_%s.txt' % TAG))", "markers += 0")


def fails(text, shp):
    out = set()
    for l in text.splitlines():
        if shp:
            m = re.match(r'(\S+)\s+want .* (OK|FAIL)\s', l)
            if m and m.group(2) == 'FAIL': out.add(m.group(1))
        else:
            m = re.match(r'(\S+)\s+.*\s(OK|FAIL)\s*$', l)
            if m and m.group(2) == 'FAIL': out.add(m.group(1))
    return out, ('ALL OK' in text)


def run(item):
    target, name, src = item
    d = M / name; shutil.rmtree(d, ignore_errors=True); d.mkdir()
    if target == 'shp':
        (d / 'shp111.py').write_text(src, encoding='utf-8')
        p = subprocess.run([sys.executable, str(R / 'test_shp111.py'), str(d / 'shp111.py'), str(d / 'fx')],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
    else:
        (d / 'vds111b.py').write_text(src, encoding='utf-8')
        t = (R / 'test_vds111b.py').read_text(encoding='utf-8').replace(
            "Path('C:/kyty/s111/audit111/rerun/fx_vds111b')", "Path('%s')" % (d / 'fx').as_posix())
        (d / 'test_vds111b.py').write_text(t, encoding='utf-8')
        p = subprocess.run([sys.executable, str(d / 'test_vds111b.py'), str(d / 'vds111b.py')],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
    text = p.stdout + p.stderr
    (d / 'out.txt').write_text(text, encoding='utf-8')
    shutil.rmtree(d / 'fx', ignore_errors=True)
    f, allok = fails(text, target == 'shp')
    if target == 'shp':
        killed = f != {'CONSTANTS'}
    else:
        killed = not allok
    return name, killed, sorted(f)[:8]


if __name__ == '__main__':
    only = sys.argv[1:]
    items = [m for m in muts if not only or m[1] in only]
    with ThreadPoolExecutor(3) as ex:
        for name, killed, f in ex.map(run, items):
            print('%-24s %s  failing=%s' % (name, 'KILLED' if killed else 'SURVIVED', f), flush=True)
