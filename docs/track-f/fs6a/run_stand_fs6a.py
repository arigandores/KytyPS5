# FS6a (HPP-555, ROADMAP s122 item 454(g)(1)): copy of docs/track-f/f15c/run_stand_f15c.py of main (H4 text of item 454(v));
# the only change - plane L expects the FS6 default: fix 'none' (KYTY_FIX_B4 unset) -> 'FixB4: mode=1', '0' -> 0, '1' -> 1.
# Was:
# F15c (HPP-514, ROADMAP s122 item 412(g)(1)-(3)): driver of the B4 stand tests/B4RaceStand.cpp (target b4_race_stand) -
# one process per trial; copy of docs/track-f/f15a/run_stand_f15a.py with the knob, plane D and the log check added.
# Usage: python run_stand_f15c.py <exe> <mode A|B|C|D|L> <N> <out.tsv> <fix none|0|1> [first_seed]
# The child environment: every KYTY_* variable removed, then KYTY_FIX_B4=<fix> unless fix is 'none'.
# Halts before a trial when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists (rule 27, rule 26).
# Classes A/B/C: FATAL207 (DeleteDescriptor EXIT_IF m_files[index] == nullptr), FATAL446 (KernelOpen EXIT_IF after
# GetFile), FATAL_OTHER, CLEAN, CRASH (exit code not 0/77), TIMEOUT (60 s per trial, the stand itself ends in < 3 s).
# F15a matched the fatal by the line numbers :207 / :446 of fileSystem.cpp; the fix moves them (+15 and +40 lines: :207 -> :222, :446 -> :486),
# so the class is decided by the line text of the source file the stand was built from (argument-free: the path in the
# FATAL line is the compile-time __FILE__, read here).
# Class D: DATA_OK (exit 0, last line 'DATA 65536 fstat=65536', file on disk = pattern byte for byte), DATA_BAD (file
# differs or missing - first differing offset in the line), CRASH, TIMEOUT. Pattern byte i: (i*131 + seed*17 + (i>>8)) & 0xFF.
# Class L: LOG_OK (exit 0, 'LOGCHECK' and exactly one 'FixB4: mode=<expected>' line, expected 0 for fix=0 else 1 - FS6), LOG_BAD.
import collections, hashlib, os, re, subprocess, sys, time

exe, mode, n, out, fix = os.path.abspath(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
first = int(sys.argv[6]) if len(sys.argv) > 6 else 1
assert mode in ('A', 'B', 'C', 'D', 'L') and fix in ('none', '0', '1')
cwd = os.path.join(os.path.dirname(os.path.abspath(out)), 'cwd_' + mode)
os.makedirs(cwd, exist_ok=True)
sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
if fix != 'none':
    env['KYTY_FIX_B4'] = fix
expected_mode = '0' if fix == '0' else '1'
fatal_line_text = {}


def fatal_class(loc):
    # loc = '<path>:<line>' as printed by the stand from __FILE__/__LINE__ of the fatal site.
    path, _, line = loc.rpartition(':')
    if not path.replace('\\', '/').endswith('kernel/fileSystem.cpp'):
        return 'FATAL_OTHER'
    key = (path, line)
    if key not in fatal_line_text:
        try:
            src = open(path, 'rb').read().decode('utf-8', 'replace').split('\n')
            fatal_line_text[key] = src[int(line) - 1].strip()
        except (OSError, ValueError, IndexError):
            fatal_line_text[key] = ''
    t = fatal_line_text[key]
    if t == 'EXIT_IF(m_files[index] == nullptr);':
        return 'FATAL207'
    if t.startswith('EXIT_IF(file == nullptr || file->opened'):
        return 'FATAL446'
    return 'FATAL_OTHER'


def pattern(seed):
    return bytes(((i * 131 + seed * 17 + (i >> 8)) & 0xFF) for i in range(65536))


counts = collections.Counter()
t_start = time.time()
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('# exe %s sha256 %s mode %s N %d first_seed %d fix %s\n' % (exe, sha, mode, n, first, fix))
    f.write('seed\trc\tclass\tline\n')
    done = 0
    for seed in range(first, first + n):
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            f.write('# HALT before seed %d (lock or STOP)\n' % seed)
            print('HALT before seed', seed)
            break
        dfile = os.path.join(cwd, 'stand_data', 'd_%d.bin' % seed)
        if mode == 'D' and os.path.exists(dfile):
            os.remove(dfile)
        try:
            p = subprocess.run([exe, mode, str(seed)], cwd=cwd, env=env, capture_output=True, timeout=60)
            rc = p.returncode
            stdout = p.stdout.decode('utf-8', 'replace')
            text = stdout.strip().splitlines()
            line = text[-1] if text else ''
        except subprocess.TimeoutExpired:
            rc, line, stdout = None, '', ''
        if rc is None:
            cls = 'TIMEOUT'
        elif mode == 'L':
            plain = re.sub(r'\x1b\[[0-9;]*m', '', stdout)
            modes = re.findall(r'FixB4: mode=(\d+)', plain)
            ok = rc == 0 and line == 'LOGCHECK' and modes == [expected_mode]
            cls = 'LOG_OK' if ok else 'LOG_BAD'
            line = '%s modes=%s' % (line, ','.join(modes))
        elif mode == 'D':
            if rc == 0 and line == 'DATA 65536 fstat=65536':
                try:
                    got = open(dfile, 'rb').read()
                except OSError:
                    got = None
                want = pattern(seed)
                if got == want:
                    cls = 'DATA_OK'
                else:
                    cls = 'DATA_BAD'
                    if got is None:
                        line += ' file missing'
                    else:
                        diff = next((i for i in range(min(len(got), len(want))) if got[i] != want[i]), min(len(got), len(want)))
                        line += ' size %d first diff %d' % (len(got), diff)
            else:
                cls = 'CRASH' if not line.startswith('FATAL') else fatal_class(line.split()[1])
        elif line.startswith('FATAL'):
            # The interceptor printed: the fatal was reached. rc may be an access violation instead of 77 when
            # another thread faults on a freed File between the print and _Exit (F15a smoke B seed 1002) - kept in rc.
            cls = fatal_class(line.split()[1])
        elif rc == 0 and line.startswith('CLEAN'):
            cls = 'CLEAN'
        else:
            cls = 'CRASH'
        counts[cls] += 1
        done += 1
        f.write('%d\t%s\t%s\t%s\n' % (seed, rc, cls, line))
        f.flush()
    f.write('# done %d wall %.1f s counts %s\n' % (done, time.time() - t_start, dict(sorted(counts.items()))))
print('exe sha256', sha)
print('mode', mode, 'fix', fix, 'done', done, 'of', n, 'wall %.1f s' % (time.time() - t_start))
print('counts', dict(sorted(counts.items())))
fat = sum(v for k, v in counts.items() if k.startswith('FATAL'))
print('fatal %d of %d -> p_s = %.4f' % (fat, done, fat / done if done else float('nan')))
