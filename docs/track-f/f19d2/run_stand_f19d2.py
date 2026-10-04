# F19d2 (HPP-559, ROADMAP s122 item 460(v)(2), (4)): driver of the new cases of the B24 stand tests/B24PadStand.cpp
# (target b24_pad_stand). Child environment as the F19c driver: every KYTY_* and SDL_* variable removed, then
# KYTY_FIX_B24=<fix>. The error mode of this process (inherited by the children) has no fault dialogs; a stand crash
# is a marker line (terminate=1 / abort=1, exit 3) or an exit code of the process.
# Halts before a process when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists (rules 27, 26): exit 3.
#
#   python run_stand_f19d2.py dd <exe> <out dir> <label> <first> <last>
#       cycles first..last (one process per cycle, KYTY_FIX_B24=1); appends one line per cycle to
#       <out dir>/dd_<label>_cycles.txt and every output to <out dir>/dd_<label>_all.txt; a cycle that is not clean
#       also gets <out dir>/dd_<label>_fail_<k>.txt. Resumes are by first/last (the summary rejects gaps and repeats).
#   python run_stand_f19d2.py ddsum <out dir> <label> <n> <member|reference>
#       -> <out dir>/dd_<label>_summary.txt. member (item 460(v)(2)): cycles 0..n-1 each exactly once, every cycle
#       clean (rc 0, END, both_returned=1, shutdown_ok=1, no marker, fix_b24=1, FixB24 line, connected=1,
#       num_joysticks_at_init=0) and the scenario happened (calls_started_before_unlock=1: both calls began while X
#       held the lock; po_wait_max_us >= 200 000: the PadOutput application waited for the lock) -> ALL OK.
#       reference: only the counts (crashes of n; UB - zero does not disprove RC1).
#   python run_stand_f19d2.py trig <exe> <out dir>
#       item 460(v)(4) -> <out dir>/trig_f19d2.txt: pad type; if PS5 - at =1 wall of each PadSetTriggerEffect < 50 ms
#       with the lock taken, SendEffect count >= 1 after the unlock (0 before), the last applied payload = the payload of
#       the last written effect (B), A and B differ, sent=1 in the PadTriggerEffect: lines of both calls; at =0 the first
#       wall >= 2 700 ms. Not PS5 - the line with the type, the member is parked (PARKED, not a failure).
import ctypes
import hashlib
import os
import re
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
HOLD_US = 2700000
FAST_US = 50000
PO_WAIT_US = 200000
SDL_CONTROLLER_TYPE_PS5 = 7

ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x0002 | 0x8000)


def halt_check():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('HALT lock or STOP', flush=True)
        sys.exit(3)


def run(exe, case, fix, cwd, timeout=60):
    os.makedirs(cwd, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_') and not k.upper().startswith('SDL_')}
    env['KYTY_FIX_B24'] = fix
    t0 = time.time()
    try:
        p = subprocess.run([exe, case], cwd=cwd, env=env, capture_output=True, timeout=timeout)
        rc, raw = p.returncode, p.stdout
    except subprocess.TimeoutExpired as e:
        rc, raw = 'timeout', e.stdout or b''
    out = raw.decode('utf-8', 'replace').replace('\r\n', '\n')
    kv = {}
    for line in out.split('\n'):
        m = re.match(r'^([a-z_0-9]+)=(.*)$', line)
        if m and m.group(1) not in kv:
            kv[m.group(1)] = m.group(2).strip('"')
    kv['_rc'] = rc
    kv['_end'] = out.rstrip('\n').endswith('END')
    kv['_fixb24_lines'] = sum(1 for line in out.split('\n') if line == 'FixB24: mode=1')
    kv['_wall'] = time.time() - t0
    kv['_sent'] = re.findall(r'^PadTriggerEffect: #(\d+) .* ok=(\d) sent=(\d)$', out, re.M)
    return kv, out


def num(kv, k):
    try:
        return int(kv.get(k, '-1'), 0)
    except ValueError:
        return -1


def dd_clean(kv):
    return [
        ('rc 0', kv['_rc'] == 0),
        ('END', kv['_end']),
        ('both_returned 1', num(kv, 'both_returned') == 1),
        ('shutdown_ok 1', num(kv, 'shutdown_ok') == 1),
        ('no terminate/abort marker', 'terminate' not in kv and 'abort' not in kv),
        ('fix_b24 1 and FixB24 line', num(kv, 'fix_b24') == 1 and kv['_fixb24_lines'] == 1),
        ('connected 1', num(kv, 'connected') == 1),
        ('num_joysticks_at_init 0', num(kv, 'num_joysticks_at_init') == 0),
    ]


def dd_scenario(kv):
    return [
        ('calls_started_before_unlock 1', num(kv, 'calls_started_before_unlock') == 1),
        ('po_wait_max_us >= %d' % PO_WAIT_US, num(kv, 'po_wait_max_us') >= PO_WAIT_US),
    ]


DD_KEYS = ['both_returned', 'call_a_wall_us', 'call_b_wall_us', 'start_skew_us', 'calls_started_before_unlock',
           'po_applied', 'po_wait_max_us', 'rumble_calls', 'terminate', 'abort']


def cmd_dd(exe, outdir, label, first, last):
    exe = os.path.abspath(exe)
    os.makedirs(outdir, exist_ok=True)
    cyc = open(os.path.join(outdir, 'dd_%s_cycles.txt' % label), 'a', encoding='utf-8', newline='\n')
    allf = open(os.path.join(outdir, 'dd_%s_all.txt' % label), 'a', encoding='utf-8', newline='\n')
    cwd = os.path.join(outdir, 'cwd_dd_%s' % label)
    nbad = 0
    for k in range(first, last + 1):
        halt_check()
        kv, out = run(exe, 'dd', '1', cwd)
        bad = [c for c, ok in dd_clean(kv) if not ok]
        vals = ' '.join('%s=%s' % (key, kv[key]) for key in DD_KEYS if key in kv)
        cyc.write('cycle=%d rc=%s end=%d clean=%d %s wall=%.2fs\n' % (k, kv['_rc'], 1 if kv['_end'] else 0,
                                                                     0 if bad else 1, vals, kv['_wall']))
        cyc.flush()
        allf.write('### cycle=%d rc=%s\n%s' % (k, kv['_rc'], out if out.endswith('\n') else out + '\n'))
        allf.flush()
        if bad:
            nbad += 1
            open(os.path.join(outdir, 'dd_%s_fail_%d.txt' % (label, k)), 'w', encoding='utf-8', newline='\n').write(out)
    print('dd %s cycles %d..%d not clean %d' % (label, first, last, nbad), flush=True)
    return 0


def cmd_ddsum(outdir, label, n, kind):
    lines = open(os.path.join(outdir, 'dd_%s_cycles.txt' % label), encoding='utf-8').read().split('\n')
    per = {}
    dup = 0
    for line in lines:
        m = re.match(r'^cycle=(\d+) (.*)$', line)
        if not m:
            continue
        k = int(m.group(1))
        if k in per:
            dup += 1
        kv = dict(re.findall(r'(\w+)=(\S+)', m.group(2)))
        per[k] = kv
    missing = [k for k in range(n) if k not in per]
    extra = [k for k in per if k >= n]

    def ival(kv, key):
        try:
            return int(kv.get(key, '-1'))
        except ValueError:
            return -1

    crashed = [k for k in sorted(per) if per[k].get('rc') != '0' or per[k].get('end') != '1' or
               'terminate' in per[k] or 'abort' in per[k] or per[k].get('both_returned') != '1']
    unclean = [k for k in sorted(per) if per[k].get('clean') != '1']
    no_scen = [k for k in sorted(per) if ival(per[k], 'calls_started_before_unlock') != 1 or
               ival(per[k], 'po_wait_max_us') < PO_WAIT_US]
    rcs = {}
    for k in crashed:
        key = 'rc=%s%s%s' % (per[k].get('rc'), ' terminate' if 'terminate' in per[k] else '',
                             ' abort' if 'abort' in per[k] else '')
        rcs[key] = rcs.get(key, 0) + 1

    def stat(key):
        v = sorted(ival(per[k], key) for k in per if ival(per[k], key) >= 0)
        return 'n=%d min=%s median=%s max=%s' % (len(v), v[0], v[len(v) // 2], v[-1]) if v else 'n=0'

    with open(os.path.join(outdir, 'dd_%s_summary.txt' % label), 'w', encoding='utf-8', newline='\n') as f:
        def w(s):
            print(s)
            f.write(s + '\n')
        w('# dd %s (%s): cycles expected %d, present %d, missing %d, repeated %d, beyond n %d' %
          (label, kind, n, len(per), len(missing), dup, len(extra)))
        w('crashed %d of %d (rc != 0, no END, marker or no both_returned): %s' % (len(crashed), len(per), rcs))
        w('not clean %d; scenario not met (calls before unlock and po_wait_max_us >= %d) %d' %
          (len(unclean), PO_WAIT_US, len(no_scen)))
        for key in ['call_a_wall_us', 'call_b_wall_us', 'start_skew_us', 'po_wait_max_us', 'po_applied', 'rumble_calls']:
            w('%s %s' % (key, stat(key)))
        if kind == 'member':
            ok = not missing and dup == 0 and not extra and not crashed and not unclean and not no_scen
            if not ok:
                w('first failing cycles: crashed %s unclean %s no_scenario %s missing %s' %
                  (crashed[:10], unclean[:10], no_scen[:10], missing[:10]))
            w('ALL OK' if ok else 'FAILED')
            return 0 if ok else 1
        w('REFERENCE (not a member): crashes %d of %d' % (len(crashed), len(per)))
        return 0


def cmd_trig(exe, outdir):
    exe = os.path.abspath(exe)
    sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
    os.makedirs(outdir, exist_ok=True)
    res = []
    for fix in ['1', '0']:
        halt_check()
        kv, out = run(exe, 'trig', fix, os.path.join(outdir, 'cwd_trig_fix%s' % fix))
        open(os.path.join(outdir, 'out_trig_fix%s.txt' % fix), 'w', encoding='utf-8', newline='\n').write(out)
        res.append((fix, kv))
    with open(os.path.join(outdir, 'trig_f19d2.txt'), 'w', encoding='utf-8', newline='\n') as f:
        def w(s):
            print(s)
            f.write(s + '\n')
        w('# exe %s sha256 %s' % (exe, sha))
        nbad = 0
        parked = False
        keys = ['pad_vendor', 'pad_product', 'pad_type', 'pad_type_ps5', 'wall_trig_a_us', 'wall_trig_b_us', 'trig_ok',
                'y_done_before_unlock', 'effect_calls_before_unlock', 'effect_calls_after_unlock', 'effect_latency_us',
                'ref_seen', 'payload_size', 'last_eq_b', 'a_ne_b', 'pad_trig', 'guest_sdl', 'po_applied', 'po_wait_max_us',
                'effect_calls']
        for fix, kv in res:
            fix1 = fix == '1'
            ps5 = num(kv, 'pad_type_ps5') == 1
            sent = kv['_sent']
            conds = [
                ('rc 0 and END', kv['_rc'] == 0 and kv['_end']),
                ('connected 1', num(kv, 'connected') == 1),
                ('num_joysticks_at_init 0', num(kv, 'num_joysticks_at_init') == 0),
                ('fix_b24 %s' % fix, num(kv, 'fix_b24') == int(fix)),
                ('pad_vendor 0x054c, pad_product 0x0ce6', num(kv, 'pad_vendor') == 0x054C and num(kv, 'pad_product') == 0x0CE6),
                ('trig_ok 1', num(kv, 'trig_ok') == 1),
            ]
            if not ps5:
                parked = True
                w('PARKED trig_fix%s: pad_type=%s (SDL_CONTROLLER_TYPE_PS5 = %d) - member item 460(v)(4) parked until a PS5 pad'
                  % (fix, kv.get('pad_type'), SDL_CONTROLLER_TYPE_PS5))
            elif fix1:
                conds += [
                    ('wall_trig_a_us < %d' % FAST_US, 0 <= num(kv, 'wall_trig_a_us') < FAST_US),
                    ('wall_trig_b_us < %d' % FAST_US, 0 <= num(kv, 'wall_trig_b_us') < FAST_US),
                    ('y_done_before_unlock 1', num(kv, 'y_done_before_unlock') == 1),
                    ('effect_calls_before_unlock 0', num(kv, 'effect_calls_before_unlock') == 0),
                    ('effect_calls_after_unlock >= 1', num(kv, 'effect_calls_after_unlock') >= 1),
                    ('ref_seen 1', num(kv, 'ref_seen') == 1),
                    ('last applied = last written (last_eq_b 1)', num(kv, 'last_eq_b') == 1),
                    ('payloads of A and B differ (a_ne_b 1)', num(kv, 'a_ne_b') == 1),
                    ('sent=1 in PadTriggerEffect #1 and #2', [s[2] for s in sent[:2]] == ['1', '1']),
                    ('guest_sdl 0', num(kv, 'guest_sdl') == 0),
                ]
            else:
                conds += [
                    ('wall_trig_a_us >= %d' % HOLD_US, num(kv, 'wall_trig_a_us') >= HOLD_US),
                    ('effect_calls_after_unlock >= 1', num(kv, 'effect_calls_after_unlock') >= 1),
                    ('last applied = last written (last_eq_b 1)', num(kv, 'last_eq_b') == 1),
                ]
            bad = [c for c, ok in conds if not ok]
            vals = ' '.join('%s=%s' % (k, kv[k]) for k in keys if k in kv)
            w('%s trig_fix%s rc=%s wall=%.1fs %s sent=%s' % ('PASS' if not bad else 'FAIL', fix, kv['_rc'], kv['_wall'],
                                                            vals, ','.join('#%s:%s' % (s[0], s[2]) for s in sent)))
            for c in bad:
                w('    failed: ' + c)
            nbad += 1 if bad else 0
        w(('ALL OK' if nbad == 0 else 'FAILED %d' % nbad) + (' (member PARKED: pad type not PS5)' if parked else ''))
    return 0 if nbad == 0 else 1


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'dd' and len(a) == 6:
        sys.exit(cmd_dd(a[1], a[2], a[3], int(a[4]), int(a[5])))
    if a and a[0] == 'ddsum' and len(a) == 5:
        sys.exit(cmd_ddsum(a[1], a[2], int(a[3]), a[4]))
    if a and a[0] == 'trig' and len(a) == 3:
        sys.exit(cmd_trig(a[1], a[2]))
    print(__doc__ or 'usage: see the header')
    sys.exit(2)
