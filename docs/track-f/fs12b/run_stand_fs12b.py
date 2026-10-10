# FS12b (HPP-751, Red Team, ROADMAP s122 item 683(g)(2)): copy of docs/track-f/fs12a/run_stand_fs12a.py (0b5f0a14) with one change - BASE -> C:/kyty/f287/fs12b.
# FS12a (HPP-750; ROADMAP s122 item 683(g)(1)): copy of docs/track-f/f33c2/run_stand_f33c2.py made by
# mk_driver_fs12a.py - BASE -> C:/kyty/f287/fs12a, --fix d = KYTY_FIX_F21 not set (the FS12 default); no other change.
# Was:
# F33c2 (HPP-748; ROADMAP s122 item 681(v)(1)-(3)): copy of docs/track-f/f33c/run_stand_f33c.py (a4212bed) made by
# mk_driver.py - BASE -> C:/kyty/f287/f33c2, arm CN (stand edition 3), field nested_fatal; no other change.
"""F33c (HPP-744; ROADMAP s122 item 675(d)(1)): driver of the stand KYTY_TEST_EXITFATAL edition 2.
Copy of F33a run_stand_f33a.py (one process per trial, lock/STOP between trials, timeout kill of the tree, leftover
check) with the arms, the fields and the classes of item 675(d)(1).

    python run_stand_f33c2.py <arm P2|R2|G|C|N|H|HG|CN> <seed_from> <seed_to> --fix <0|1> --exe <name in run/>
                             [--out runs] [--timeout 30]

One trial: the binary run/<exe> (cwd run/, an empty app0 dir - no game) with KYTY_TEST_EXITFATAL=<arm>:<seed> and
KYTY_FIX_F21=<fix>; every other KYTY_* variable of the environment is removed. The TSV is per (fix, arm):
<out>/fix<fix>/stand_<arm>.tsv, resumable (seeds already there are skipped); stdout, stderr and _kyty.txt of each
trial are kept in <out>/fix<fix>/<arm>/<seed>.{out,err,log}.

Fields / classes (stderr lines 'ExitFatal: ...' of the stand, 'FixF21: wait_expired' of the fix):
  control   - P2, R2, H: the first entry of the guest into EmergencyShutdownActive saw the main thread's walk in progress
              ('ExitFatal: enter role=guest ... main_walk=1'); G: the first entry of the main thread saw the guest's walk
              in progress ('enter role=main ... guest_walk=1'); HG (reference arm): as G; C, N: '' (no peer)
  second    - emergency callbacks run by both roles ('ExitFatal: cb' lines of role main and of role guest)
  crash     - rc not in {0, 321} (not a timeout), or '--- abort() ---' / '--- std::terminate ---' in stdout/stderr
  hang      - the timeout (default 30 s)
  cut       - a walk that began ('walk_begin seq=<n>') has no 'walk_end seq=<n>' at the end of the process
  expired   - number of 'FixF21: wait_expired' lines
  reenter   - number of 'ExitFatal: reenter' lines (a re-entry of the owner thread returned without a walk)
  walks     - number of walks ('walk_begin'), walks_cb - walks that ran >= 1 callback, nested - walks begun inside a walk
              of the same thread ('nested=1')
  h_dt_s    - seconds from the first entry of the waiting role (guest for P2, R2, H, C, N; main for G, HG; e_us of its
              'enter' line) to the end of the process (the driver's system clock right after the process ended); read
              for H and HG
  k1        - crash or hang or second or cut or expired>0
  nested_fatal - (edition 3, arm CN) number of 'ExitFatal: nested_fatal' lines (the second fatal of the injector
              inside its own walk); dur_s - wall seconds of the trial (the driver's clock)
"""
import csv
import os
import re
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
BASE = 'C:/kyty/f287/fs12b'
RUN = BASE + '/run'

ARGS = ['--screen-width', '1280', '--screen-height', '720', '--user-name', '<user>', '--user-id', '1000',
        '--present-mode', 'Fifo', '--vblank-frequency', '60', '--console-language', '1',
        '--vulkan-validation', 'false', '--shader-validation', 'false', '--shader-optimization-type', 'Size',
        '--shader-log-direction', 'File', '--shader-log-folder', '_Shaders', '--command-buffer-dump', 'false',
        '--command-buffer-dump-folder', '_Buffers', '--printf-direction', 'File', '--printf-output-file', '_kyty.txt',
        '--spirv-debug-printf', 'false', '--game', RUN + '/app0']

FIELDS = ['fix', 'arm', 'seed', 'pos', 'cfg_fix', 'rc', 'rc_hex', 'dur_s', 'hang', 'control', 'enters', 'walks',
          'walks_cb', 'nested', 'main_cbs', 'guest_cbs', 'second', 'cut', 'expired', 'reenter', 'done_seen',
          'wait_done', 'expired_seen', 'trig_waited_us', 'h_dt_s', 'fatal_text', 'abort', 'crash', 'k1', 'leftover',
          'nested_fatal', 'utc']


def alive_copies(exe_name):
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ' + exe_name, '/FO', 'CSV', '/NH'],
                         capture_output=True, text=True).stdout
    return [int(r[1]) for r in csv.reader(out.splitlines()) if len(r) > 1 and r[0].lower() == exe_name.lower()]


def kill_tree(pid):
    subprocess.run(['taskkill', '/T', '/F', '/PID', str(pid)], capture_output=True)


def parse(arm, text):
    r = {'pos': '', 'cfg_fix': '', 'control': '', 'enters': 0, 'walks': 0, 'walks_cb': 0, 'nested': 0, 'main_cbs': 0,
         'guest_cbs': 0, 'cut': 0, 'expired': 0, 'reenter': 0, 'done_seen': 0, 'wait_done': 0, 'expired_seen': 0,
         'trig_waited_us': '', 'guest_enter_e_us': None, 'nested_fatal': 0}
    begun = {}
    ended = set()
    first_guest_enter = None
    first_main_enter = None
    for line in text.splitlines():
        if line.startswith('FixF21: wait_expired'):
            r['expired'] += 1
            continue
        if not line.startswith('ExitFatal: '):
            continue
        kv = dict(re.findall(r'(\w+)=(\S+)', line))
        kind = line.split()[1]
        role = kv.get('role', '')
        if kind == 'config':
            r['pos'] = kv.get('pos', '')
            r['cfg_fix'] = kv.get('fix', '')
        elif kind == 'enter':
            r['enters'] += 1
            if role == 'guest' and first_guest_enter is None:
                first_guest_enter = kv
            if role == 'main' and first_main_enter is None:
                first_main_enter = kv
        elif kind == 'walk_begin':
            r['walks'] += 1
            begun[kv.get('seq')] = 0
            if kv.get('nested') == '1':
                r['nested'] += 1
        elif kind == 'cb':
            r['main_cbs' if role == 'main' else 'guest_cbs'] += 1
            if kv.get('seq') in begun:
                begun[kv.get('seq')] += 1
        elif kind == 'walk_end':
            ended.add(kv.get('seq'))
        elif kind == 'reenter':
            r['reenter'] += 1
        elif kind == 'done_seen':
            r['done_seen'] += 1
        elif kind == 'wait_done':
            r['wait_done'] += 1
        elif kind == 'expired_seen':
            r['expired_seen'] += 1
        elif kind == 'nested_fatal':
            r['nested_fatal'] += 1
        elif kind == 'trigger':
            r['trig_waited_us'] = kv.get('waited_us', '')
    r['walks_cb'] = sum(1 for v in begun.values() if v > 0)
    r['cut'] = int(any(seq not in ended for seq in begun))
    if arm in ('P2', 'R2', 'H'):
        r['control'] = int(first_guest_enter is not None and first_guest_enter.get('main_walk') == '1')
    elif arm in ('G', 'HG'):
        r['control'] = int(first_main_enter is not None and first_main_enter.get('guest_walk') == '1')
    waiter = first_main_enter if arm in ('G', 'HG') else first_guest_enter
    if waiter is not None and 'e_us' in waiter:
        r['guest_enter_e_us'] = int(waiter['e_us'])
    return r


def opt(name, default=None):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


def main():
    arm, s0, s1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    if arm not in ('P2', 'R2', 'G', 'C', 'N', 'H', 'HG', 'CN'):
        sys.exit('bad arm ' + arm)
    fix = opt('--fix')
    if fix not in ('0', '1', 'd'):
        sys.exit('--fix 0|1|d is required')
    exe_name = opt('--exe')
    if not exe_name or not os.path.exists(RUN + '/' + exe_name):
        sys.exit('--exe <name in run/> is required')
    exe = RUN + '/' + exe_name
    out_dir = opt('--out', BASE + '/runs') + '/fix' + fix
    timeout = float(opt('--timeout', '30'))
    os.makedirs(out_dir + '/' + arm, exist_ok=True)
    tsv = '%s/stand_%s.tsv' % (out_dir, arm)
    done = set()
    if os.path.exists(tsv):
        for row in csv.DictReader(open(tsv, encoding='utf-8'), delimiter='\t'):
            done.add(int(row['seed']))
    else:
        with open(tsv, 'w', encoding='utf-8', newline='') as f:
            f.write('\t'.join(FIELDS) + '\n')
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('KYTY_'):
            del env[k]
    if fix != 'd':  # FS12a: 'd' - the default, KYTY_FIX_F21 not set (removed above with every KYTY_*)
        env['KYTY_FIX_F21'] = fix
    args = list(ARGS)
    args[args.index('--user-name') + 1] = os.environ.get('F33C_USER_NAME', 'user')
    n = 0
    for seed in range(s0, s1 + 1):
        if seed in done:
            continue
        if os.path.exists(LOCK):
            print('LOCK - stop before seed', seed)
            return 3
        if os.path.exists(STOP):
            print('STOP - stop before seed', seed)
            return 4
        env['KYTY_TEST_EXITFATAL'] = '%s:%d' % (arm, seed)
        log = RUN + '/_kyty.txt'
        if os.path.exists(log):
            os.remove(log)
        t0 = time.time()
        p = subprocess.Popen([exe] + args, cwd=RUN, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hang = 0
        try:
            so, se = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            hang = 1
            kill_tree(p.pid)
            so, se = p.communicate()
        t_end = time.time()
        dur = t_end - t0
        rc = None if hang else p.returncode
        leftover = 0
        for pid in alive_copies(exe_name):
            leftover += 1
            kill_tree(pid)
        so_t = so.decode('utf-8', 'replace')
        se_t = se.decode('utf-8', 'replace')
        base = '%s/%s/%d' % (out_dir, arm, seed)
        open(base + '.out', 'w', encoding='utf-8').write(so_t)
        open(base + '.err', 'w', encoding='utf-8').write(se_t)
        if os.path.exists(log):
            open(base + '.log', 'wb').write(open(log, 'rb').read())
        r = parse(arm, se_t)
        both = so_t + se_t
        abort = int('--- abort() ---' in both or '--- std::terminate ---' in both)
        fatal_text = int('--- Fatal Error ---' in both)
        rc_u = None if rc is None else (rc & 0xffffffff)
        crash = int(not hang and (rc_u not in (0, 321) or abort == 1))
        second = int(r['main_cbs'] >= 1 and r['guest_cbs'] >= 1)
        k1 = int(crash or hang or second or r['cut'] or r['expired'] > 0)
        h_dt = '' if r['guest_enter_e_us'] is None else '%.3f' % (t_end - r['guest_enter_e_us'] / 1e6)
        row = {'fix': fix, 'arm': arm, 'seed': seed, 'rc': '' if rc is None else rc,
               'rc_hex': '' if rc_u is None else '0x%08X' % rc_u, 'dur_s': '%.3f' % dur, 'hang': hang,
               'second': second, 'h_dt_s': h_dt, 'fatal_text': fatal_text, 'abort': abort, 'crash': crash, 'k1': k1,
               'leftover': leftover, 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        for k in FIELDS:
            if k not in row:
                row[k] = r[k]
        with open(tsv, 'a', encoding='utf-8', newline='') as f:
            f.write('\t'.join(str(row[k]) for k in FIELDS) + '\n')
        n += 1
    print('done fix', fix, arm, s0, s1, 'new trials', n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
