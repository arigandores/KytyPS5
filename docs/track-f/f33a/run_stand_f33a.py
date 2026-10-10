"""F33a (HPP-736; ROADMAP s122 item 673(z)(1)): driver of the stand KYTY_TEST_EXITFATAL.

    python run_stand_f33a.py <arm P|R|C|N> <seed_from> <seed_to> [--out runs] [--timeout 30]

One process = one trial: the test binary (copy kyty_emulator_<sha8>.exe in run/, cwd run/, an empty app0 dir - no game)
with KYTY_TEST_EXITFATAL=<arm>:<seed>. Between trials: stop at once (exit 3 / 4) if C:/kyty/SEALED_RUN.lock or
C:/kyty/f287/STOP exists. A trial longer than --timeout is killed with its tree (taskkill /T /F) and classed HANG; after
every trial the driver checks that no process of the copy is alive (and kills it if one is - counted in 'leftover').

Per trial (one TSV row, appended; resumable - seeds already in the TSV are skipped):
  rc            - exit code (None on timeout)
  control       - 1 if a walk of the injector thread began while the main thread's walk was active
                  (an 'ExitFatal: walk_begin ... role=guest ... in_window=1' line) - the positive control of injection
  inj_walk      - main_walk of the 'ExitFatal: inject' line (the fatal raised while the main walk was active)
  main_cbs / guest_cbs - emergency callbacks run by each role ('ExitFatal: cb' lines)
  second        - main_cbs >= 1 and guest_cbs >= 1: two emergency sequences ran callbacks in one process
  crash         - rc not in {0, 321} (not a timeout), or '--- abort() ---' / '--- std::terminate ---' in stdout/stderr
  hang          - the timeout
  k1            - crash or hang or second (the K1 outcomes of item 673(z)(1)(i))
"""
import csv
import os
import re
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
BASE = 'C:/kyty/f287/f33a'
RUN = BASE + '/run'
EXE_NAME = 'kyty_emulator_b42e1791.exe'
EXE = RUN + '/' + EXE_NAME

ARGS = ['--screen-width', '1280', '--screen-height', '720', '--user-name', '<user>', '--user-id', '1000',
        '--present-mode', 'Fifo', '--vblank-frequency', '60', '--console-language', '1',
        '--vulkan-validation', 'false', '--shader-validation', 'false', '--shader-optimization-type', 'Size',
        '--shader-log-direction', 'File', '--shader-log-folder', '_Shaders', '--command-buffer-dump', 'false',
        '--command-buffer-dump-folder', '_Buffers', '--printf-direction', 'File', '--printf-output-file', '_kyty.txt',
        '--spirv-debug-printf', 'false', '--game', RUN + '/app0']

FIELDS = ['arm', 'seed', 'pos', 'rc', 'rc_hex', 'dur_s', 'hang', 'control', 'inj_walk', 'inj_main_pos', 'walks',
          'main_cbs', 'guest_cbs', 'guest_walks', 'guest_size', 'waited_us', 'guest_walk_begun', 'fatal_text',
          'abort', 'second', 'crash', 'k1', 'leftover', 'utc']


def alive_copies():
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ' + EXE_NAME, '/FO', 'CSV', '/NH'],
                         capture_output=True, text=True).stdout
    return [int(r[1]) for r in csv.reader(out.splitlines()) if len(r) > 1 and r[0].lower() == EXE_NAME.lower()]


def kill_tree(pid):
    subprocess.run(['taskkill', '/T', '/F', '/PID', str(pid)], capture_output=True)


def parse(text):
    r = {'control': 0, 'inj_walk': '', 'inj_main_pos': '', 'walks': 0, 'main_cbs': 0, 'guest_cbs': 0,
         'guest_walks': 0, 'guest_size': '', 'waited_us': '', 'guest_walk_begun': '', 'pos': ''}
    for line in text.splitlines():
        if not line.startswith('ExitFatal: '):
            continue
        kv = dict(re.findall(r'(\w+)=(\S+)', line))
        kind = line.split()[1]
        if kind == 'config':
            r['pos'] = kv.get('pos', '')
        elif kind == 'walk_begin':
            r['walks'] += 1
            if kv.get('role') == 'guest':
                r['guest_walks'] += 1
                if r['guest_size'] == '':
                    r['guest_size'] = kv.get('size', '')
                if kv.get('in_window') == '1':
                    r['control'] = 1
        elif kind == 'cb':
            r['main_cbs' if kv.get('role') == 'main' else 'guest_cbs'] += 1
        elif kind == 'inject':
            r['inj_walk'] = kv.get('main_walk', '')
            r['inj_main_pos'] = kv.get('main_pos', '')
        elif kind == 'trigger':
            r['waited_us'] = kv.get('waited_us', '')
            r['guest_walk_begun'] = kv.get('guest_walk_begun', '')
    return r


def main():
    arm, s0, s1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    out_dir = BASE + '/runs'
    timeout = 30.0
    if '--out' in sys.argv:
        out_dir = sys.argv[sys.argv.index('--out') + 1]
    if '--timeout' in sys.argv:
        timeout = float(sys.argv[sys.argv.index('--timeout') + 1])
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
        p = subprocess.Popen([EXE] + ARGS, cwd=RUN, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hang = 0
        try:
            so, se = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            hang = 1
            kill_tree(p.pid)
            so, se = p.communicate()
        dur = time.time() - t0
        rc = None if hang else p.returncode
        leftover = 0
        for pid in alive_copies():
            leftover += 1
            kill_tree(pid)
        so_t = so.decode('utf-8', 'replace')
        se_t = se.decode('utf-8', 'replace')
        base = '%s/%s/%d' % (out_dir, arm, seed)
        open(base + '.out', 'w', encoding='utf-8').write(so_t)
        open(base + '.err', 'w', encoding='utf-8').write(se_t)
        if os.path.exists(log):
            open(base + '.log', 'wb').write(open(log, 'rb').read())
        r = parse(se_t)
        both = so_t + se_t
        abort = int('--- abort() ---' in both or '--- std::terminate ---' in both)
        fatal_text = int('--- Fatal Error ---' in both)
        rc_u = None if rc is None else (rc & 0xffffffff)
        crash = int(not hang and (rc_u not in (0, 321) or abort == 1))
        second = int(r['main_cbs'] >= 1 and r['guest_cbs'] >= 1)
        k1 = int(crash or hang or second)
        row = {'arm': arm, 'seed': seed, 'rc': '' if rc is None else rc,
               'rc_hex': '' if rc_u is None else '0x%08X' % rc_u, 'dur_s': '%.3f' % dur, 'hang': hang,
               'fatal_text': fatal_text, 'abort': abort, 'second': second, 'crash': crash, 'k1': k1,
               'leftover': leftover, 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        row.update(r)
        with open(tsv, 'a', encoding='utf-8', newline='') as f:
            f.write('\t'.join(str(row[k]) for k in FIELDS) + '\n')
        n += 1
    print('done', arm, s0, s1, 'new trials', n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
