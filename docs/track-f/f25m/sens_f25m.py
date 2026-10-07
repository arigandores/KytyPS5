"""F25m (HPP-680): the sensitivity of test_f25m_read.py (the form of F25f sens_f25.py - hand edits, not mutlib): every edit below is applied
alone to a copy of f25m_read.py in its own folder; the suite must FAIL on each (a kept edit = a hole of the fixtures).  Each old text must
occur exactly once.  Runs the edits on 8 workers.  ASCII only; ends with ALL OK when every edit is caught.
usage: python sens_f25m.py"""
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'sens_tmp')
FILES = ('f25_read.py', 'f20e_read.py', 'test_f25m_read.py')
EDITS = [
    ('POLL_US +1', 'POLL_US = 100000', 'POLL_US = 100001'),
    ('K2_US +1', 'K2_US = 1000000', 'K2_US = 1000001'),
    ('LF_S0_US +1', 'LF_S0_US = 2500000', 'LF_S0_US = 2500001'),
    ('STALL_S1_US +1', 'STALL_S1_US = 2900000', 'STALL_S1_US = 2900001'),
    ('STALL_S_US +1', 'STALL_S_US = 1000000', 'STALL_S_US = 1000001'),
    ('WIN_MS 1999', 'WIN_MS = 2000', 'WIN_MS = 1999'),
    ('WIN_MS 2001', 'WIN_MS = 2000', 'WIN_MS = 2001'),
    ('EXIT_MS 251', 'EXIT_MS = 250', 'EXIT_MS = 251'),
    ('EXIT_MS 249', 'EXIT_MS = 250', 'EXIT_MS = 249'),
    ('FH_CAP 33', 'FH_CAP = 32', 'FH_CAP = 33'),
    ('HOLD_STAND_S 121', 'HOLD_STAND_S = 120', 'HOLD_STAND_S = 121'),
    ('HOLD_V_US 299 997 000', 'HOLD_V_US = 300000000', 'HOLD_V_US = 299997000'),
    ('HOLD_W_S 311', 'HOLD_W_S = 310', 'HOLD_W_S = 311'),
    ('VIDEO_MIN 3001', 'VIDEO_MIN = 3000', 'VIDEO_MIN = 3001'),
    ('poll strict', "if (row['poll_us'] or 0) >= POLL_US:", "if (row['poll_us'] or 0) > POLL_US:"),
    ('poll unknown at cap + 1', 'elif cap_flip is not None and n > cap_flip + 1:', 'elif cap_flip is not None and n > cap_flip:'),
    ('INSTR_MADE_K2 not first', "if row['k2'] and row['p_i'] and not row['instr_made_k2']:", "if row['k2'] and row['p_i']:"),
    ('poll last not max', "pend_poll = max(pend_poll or 0, rec['poll'])", "pend_poll = rec['poll']"),
    ('poll kept across frames', "                    r['poll_ivl'][n] = pend_poll\n                pend_poll = None",
     "                    r['poll_ivl'][n] = pend_poll"),
    ('poll to the frame of the line', "                rec = dict(us=int(m.group(1)), present=int(m.group(2)), poll=int(m.group(3)), other=int(m.group(4)), flip=int(m.group(5)))\n",
     "                rec = dict(us=int(m.group(1)), present=int(m.group(2)), poll=int(m.group(3)), other=int(m.group(4)), flip=int(m.group(5)))\n"
     "                r['poll_ivl'][rec['flip']] = rec['poll']\n                r['fh'].append(rec)\n                continue\n"),
    ('mode=1 once -> any', "m1 = len([l for l in x['mode'] if l.startswith('LogAsync: mode=1 ')]) == 1 and len(x['mode']) == 1",
     "m1 = len([l for l in x['mode'] if l.startswith('LogAsync: mode=1 ')]) >= 1"),
    ('no summary not an interference', "        if why is None and not m2:\n", "        if False:\n"),
    ('RC3 at 2', "if summ is not None and (summ['drain_timeouts'] or 0) >= 1:", "if summ is not None and (summ['drain_timeouts'] or 0) >= 2:"),
    ('=0 stall lines allowed', "none = not x['mode'] and not x['summary'] and not x['stall'] and", "none = not x['mode'] and not x['summary'] and"),
    ('slept strict', "s['slept_us'] >= 2900000 for s in sl)", "s['slept_us'] > 2900000 for s in sl)"),
    ('config sleep_ms not checked', "c_ok = len(cfg) == 1 and cfg[0]['sleep_ms'] == 3000 and", "c_ok = len(cfg) == 1 and"),
    ('config on not checked', "and cfg[0]['k'] == 3 and cfg[0]['on'] == on", "and cfg[0]['k'] == 3"),
    ('three sleeps -> two', "s_ok = [s['i'] for s in sl] == [1, 2, 3] and", "s_ok = len(sl) >= 2 and"),
    ('exit strict', 'gap >= EXIT_MS, gap)', 'gap > EXIT_MS, gap)'),
    ('exit not a stand member', '    mem = [(em[0], em[1])]\n', '    mem = []\n'),
    ('window left open', 'return w[0] <= t <= w[1]', 'return w[0] < t <= w[1]'),
    ('window right open', 'return w[0] <= t <= w[1]', 'return w[0] <= t < w[1]'),
    ('s0 any sleep', "len(per) == 3 and all(p['hits'] for p in per)))", "len(per) == 3 and any(p['hits'] for p in per)))"),
    ('s1 LongFrame after the level line', "len(lf1), len(lf1_after)), not lf1),", "len(lf1), len(lf1_after)), not lf1_after),"),
    ('s1 two stalls', "('>= 3 LogAsync: stall lines us >= 2 900 000 (%d)' % len(st29), len(st29) >= 3),",
     "('>= 3 LogAsync: stall lines us >= 2 900 000 (%d)' % len(st29), len(st29) >= 2),"),
    ('s1 full_waits without a summary', "summ is not None and summ['full_waits'] == 0)]", "(summ or {}).get('full_waits', 0) == 0)]"),
    ('f0 every sleep', "len(per) == 3), any(p['hits'] for p in per)))", "len(per) == 3), all(p['hits'] for p in per)))"),
    ('f1 only frames after 10 s', "ge1 = [(n, dt) for (n, dt, t_before) in frames if dt >= K2_US]",
     "ge1 = [(n, dt) for (n, dt, t_before) in frames if dt >= K2_US and t_before >= 10000000]"),
    ('frame end prefers flip_ns', "    if n in lf_by_n:\n        return lf_by_n[n]['t_ms'], 'LongFrame'\n    d = diag.get(n) if diag else None\n"
     "    if d and d.get('hdr') and R.num(d['hdr'].get('flip_ns')) is not None:\n        return R.num(d['hdr']['flip_ns']) // 1000000, 'flip_ns'\n",
     "    d = diag.get(n) if diag else None\n    if d and d.get('hdr') and R.num(d['hdr'].get('flip_ns')) is not None:\n"
     "        return R.num(d['hdr']['flip_ns']) // 1000000, 'flip_ns'\n    if n in lf_by_n:\n        return lf_by_n[n]['t_ms'], 'LongFrame'\n"),
    ('frame end without flip_ns', "    if d and d.get('hdr') and R.num(d['hdr'].get('flip_ns')) is not None:\n        return R.num(d['hdr']['flip_ns']) // 1000000, 'flip_ns'\n",
     ''),
    ('S_flush counts all', "res['S_flush'] = sum(1 for s in stalls if s['us'] >= STALL_S_US and s['flush'])",
     "res['S_flush'] = sum(1 for s in stalls if s['us'] >= STALL_S_US)"),
    ('overlap end strict', "return [(s['us'], s['t_ms']) for s in x['stall'] if s['t_ms'] - s['us'] // 1000 <= end and s['t_ms'] >= a]",
     "return [(s['us'], s['t_ms']) for s in x['stall'] if s['t_ms'] - s['us'] // 1000 < end and s['t_ms'] >= a]"),
    ('overlap start strict', "return [(s['us'], s['t_ms']) for s in x['stall'] if s['t_ms'] - s['us'] // 1000 <= end and s['t_ms'] >= a]",
     "return [(s['us'], s['t_ms']) for s in x['stall'] if s['t_ms'] - s['us'] // 1000 <= end and s['t_ms'] > a]"),
    ('user env without LONGFRAME', "        e.update(KYTY_LONGFRAME='1', KYTY_TEST_LOGSTALL=STAND)\n        return e",
     "        e.update(KYTY_TEST_LOGSTALL=STAND)\n        return e"),
    ('env path keys compared', "        elif want[key] is not None and env[key] != want[key]:", "        elif env[key] != want[key]:"),
    ('cold HANG_ABORT 8', "e.update(KYTY_GPU_WALL='1', KYTY_GPU_HANG_ABORT_S='22', KYTY_DIAG_B32='1', KYTY_REC=None)",
     "e.update(KYTY_GPU_WALL='1', KYTY_GPU_HANG_ABORT_S='8', KYTY_DIAG_B32='1', KYTY_REC=None)"),
    ('w validation false', "vv = 'true' if base == 'b36_w' else 'false'", "vv = 'false'"),
    ('cold hold option 331', "'cold': 330, 'v': 330, 'w': 310}[kind]", "'cold': 331, 'v': 330, 'w': 310}[kind]"),
    ('user form FrameTrace allowed', "x is not None and not x['ft']),", "x is not None),"),
    ('stdout death ignored', "x is not None and not x['death'] and not sd)]\n    elif kind == 'stand_harness':",
     "x is not None and not x['death'])]\n    elif kind == 'stand_harness':"),
    ('recovering not checked', "x is not None and x['minimized'] == 0 and x['recovering'] == 0),", "x is not None and x['minimized'] == 0),"),
    ('GamePatch not checked', "x is not None and x['gamepatch'] == 0),", "x is not None),"),
    ('signature not checked', "x is not None and x['sig'] == [SIG] and x['variant_dir'] == [VARIANT_DIR]),", "x is not None and x['variant_dir'] == [VARIANT_DIR]),"),
    ('installed_sha not checked', "(F.text(p['installed_sha']) or '').strip() == BIN_T2),", "True),"),
    ('installed before not checked', 'inst_b == BIN_FS9 and inst_a == BIN_FS9),', 'inst_a == BIN_FS9),'),
    ('json binary T accepted', "('json binary_sha256 = T2 9745eb78 (%s)' % (jbin or '-')[:16], jbin == BIN_T2),",
     "('json binary_sha256 = T2 9745eb78 (%s)' % (jbin or '-')[:16], jbin is not None),"),
    ('cold other death allowed', "                ('no death marker other than GpuHangAbort (%s)' % other[:3], r is not None and not other),",
     "                ('no death marker other than GpuHangAbort (%s)' % other[:3], r is not None),"),
    ('TestLogStall outside the stands allowed', "not x['cfg'] and not x['sleep']))", "True))"),
    ('k12 bonus', "COLD_POT = ('b36_k01', 'b36_k03', 'b36_k05', 'b36_k07', 'b36_k09', 'b36_k11', 'b36_k12', 'b36_k13')",
     "COLD_POT = ('b36_k01', 'b36_k03', 'b36_k05', 'b36_k07', 'b36_k09', 'b36_k11', 'b36_k13')"),
    ('tag k14 accepted', "b36_k(?:0[1-9]|1[0-3])", "b36_k(?:0[1-9]|1[0-4])"),
    ('first scene frame draws > 100', 'if draws is not None and draws >= 100:', 'if draws is not None and draws > 100:'),
    ('w DualSrcBlend after GuestOut accepted', "dual = [d for d in x['dual'] if d[0] and d[1]]", "dual = [d for d in x['dual'] if d[0]]"),
    ('w no [Vulkan][W] needed', "x['vkw'], len(dual)), x['vkw'] > 0 and bool(dual)),", "x['vkw'], len(dual)), bool(dual)),"),
    ('FixB13 after GuestOut accepted', "bool(x['b13']) and all(v == 1 for v in x['b13']) and x['b13_before_guest'])]",
     "bool(x['b13']) and all(v == 1 for v in x['b13']))]"),
    ('w hold_s not checked', "att.get('hold_exit') is None and (att.get('hold_s') or 0) >= HOLD_W_S", "att.get('hold_exit') is None"),
    ('v glitch not checked', "('0 one-frame glitches (%s)' % gl, gl == 0),", "('0 one-frame glitches (%s)' % gl, True),"),
    ('v sheet not checked', "('sheet for the lead made (%s)' % sheet, bool(sheet))]", "('sheet for the lead made (%s)' % sheet, True)]"),
    ('w limit lines not checked', "('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),",
     "('0 limit lines of the layer (%d)' % x['vk_limit'], True),"),
    ('w [Vulkan][E] not checked', "('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),", "('0 [Vulkan][E] (%d)' % x['vke'], True),"),
    ('stand_harness scene length not checked', "r is not None and r['first_n'] is not None and (r['scene_s'] or 0) >= HOLD_STAND_S),",
     "r is not None and r['first_n'] is not None),"),
    ('stand_harness DiagB32 mode not checked', "r is not None and len(r['mode']) == 1 and not r['invalid'])]\n    elif kind == 'cold':",
     "r is not None)]\n    elif kind == 'cold':"),
    ('user hold not checked', "(att.get('hold_s') or 0) >= HOLD_STAND_S and att.get('hold_exit') is None),", "att.get('hold_exit') is None),"),
    ('snap_cmp not checked', "bool(scmp) and scmp[0].startswith('manifest cmp EQUAL')),", "True),"),
    ('manifest return not checked', "bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),", "True),"),
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
    open(os.path.join(d, 'f25m_read.py'), 'w', encoding='ascii', newline='\n').write(src.replace(a, b))
    p = subprocess.run([sys.executable, os.path.join(d, 'test_f25m_read.py')], capture_output=True, cwd=d, timeout=600)
    out = p.stdout.decode('ascii', 'replace')
    caught = p.returncode != 0
    crashed = 'FAILED' not in out
    fails = [l for l in out.splitlines() if l.startswith('FAIL ')]
    return i, name, ('caught%s (%d FAIL lines; first: %s)' % (' by a crash' if crashed else '', len(fails), fails[0][:90] if fails else p.stderr.decode('ascii', 'replace')[-90:].strip())
                     if caught else 'KEPT')


def main():
    src = open(os.path.join(HERE, 'f25m_read.py'), encoding='ascii').read()
    print('suite sens_f25m.py sha256 %s target f25m_read.py sha256 %s test_f25m_read.py sha256 %s' % (
        sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'f25m_read.py')), sha(os.path.join(HERE, 'test_f25m_read.py'))))
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    p = subprocess.run([sys.executable, os.path.join(HERE, 'test_f25m_read.py')], capture_output=True, cwd=HERE, timeout=600)
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
