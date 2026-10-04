# F15a (HPP-491, ROADMAP s122 item 400(d)(2)): driver of the B4 stand - one process per trial.
# Usage: python run_stand_f15a.py <exe> <mode> <N> <out.tsv> [first_seed]
# Halts before a trial when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists (rule 27, rule 26).
# Classes: FATAL207 (DeleteDescriptor :207), FATAL446 (KernelOpen :446), FATAL_OTHER, CLEAN, CRASH (exit code not 0/77),
# TIMEOUT (60 s per trial, the stand itself ends in < 3 s).
import collections, hashlib, os, subprocess, sys, time

exe, mode, n, out = os.path.abspath(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4]
first = int(sys.argv[5]) if len(sys.argv) > 5 else 1
cwd = os.path.join(os.path.dirname(os.path.abspath(out)), 'cwd_' + mode)
os.makedirs(cwd, exist_ok=True)
sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
counts = collections.Counter()
t_start = time.time()
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('# exe %s sha256 %s mode %s N %d first_seed %d\n' % (exe, sha, mode, n, first))
    f.write('seed\trc\tclass\tline\n')
    done = 0
    for seed in range(first, first + n):
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            f.write('# HALT before seed %d (lock or STOP)\n' % seed)
            print('HALT before seed', seed)
            break
        try:
            p = subprocess.run([exe, mode, str(seed)], cwd=cwd, capture_output=True, timeout=60)
            rc = p.returncode
            text = p.stdout.decode('utf-8', 'replace').strip().splitlines()
            line = text[-1] if text else ''
        except subprocess.TimeoutExpired:
            rc, line = None, ''
        if rc is None:
            cls = 'TIMEOUT'
        elif line.startswith('FATAL'):
            # The interceptor printed: the fatal was reached. rc may be an access violation instead of 77 when
            # another thread faults on a freed File between the print and _Exit (smoke B seed 1002) - kept in rc.
            loc = line.split()[1]
            cls = 'FATAL207' if loc.endswith('fileSystem.cpp:207') else ('FATAL446' if loc.endswith('fileSystem.cpp:446') else 'FATAL_OTHER')
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
print('mode', mode, 'done', done, 'of', n, 'wall %.1f s' % (time.time() - t_start))
print('counts', dict(sorted(counts.items())))
fat = sum(v for k, v in counts.items() if k.startswith('FATAL'))
print('fatal %d of %d -> p_s = %.4f' % (fat, done, fat / done if done else float('nan')))
