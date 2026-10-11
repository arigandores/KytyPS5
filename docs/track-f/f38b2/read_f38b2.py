"""F38b2 (HPP-778, Red Team): own reader of the F25 stand edition 3 rows by the letter of ROADMAP s122 items 691(d)(1)
and 693(b)(1)-(2); independent of sum_f38a.py / sum_f38a2.py. usage: read_f38b2.py <fix 0|1> <rows.tsv> [<rows.tsv> ...]

Letter members per trial (entry e; POSIX = read, _read, pread; PREAD = sceKernelPread, pread, AIO; AIO = 5):
  quiet(r)   : POSIX errno not written (12345); AIO call code 0 and state COMPLETED (3); sceKernel* - nothing to check;
  form(r)    : 691(v)(1) - sceKernelRead/sceKernelPread ret 0x80020005; POSIX ret -1 and errno 5; AIO call code 0,
               return_value 0x80020005, state ABORTED (4);
  pos(r)     : 691(v)(3) - read entries: position after = before (ret <= 0) or before + ret; PREAD entries: after = q;
  A =1 : form, untouched, pos              A =0 : ret 0, quiet, untouched, pos
  K    : full (ret = expected, data_ok), quiet, calls 2 with 1 injected (F37a), pos
  Z    : full, quiet, calls 1 with 0 injected (F37a), pos
  E    : ret 0, quiet, calls 1 with 0 injected, untouched, pos (693(b)(2) - the F38a variant is now the letter)
  T    : ret 0, quiet, trunc_done and size_at_c2 = offset, restore_ok
  G    : ret 0, quiet, calls 1 with 0 injected, untouched, pos, grown (trunc_done 1, size_at_c2 = offset + 8192),
         restore_ok, guard intact (693(b)(1))
Row members: N per (entry, arm) = A 200 / K 50 / Z 50 / E 50 / T 20 / G 50 (or the N given by --need), in E and G
offset = file size exactly in ceil(n/2) trials, remaining = 0 in all E and G trials. Guard bytes - a member of G, a
reference column elsewhere. Log: FixF25: mode=<fix> once per file, the other mode 0 times; read failed twice =
min(32, A rows) at =1, 0 at =0. Process: stdout_<seed>_f<fix>.txt beside the rows - FINAL file sha256 equal 1,
DONE trials = rows. Last line: MEMBERS LETTER YES/NO."""
import os
import re
import sys

EIO = -2147352571
SENTRY = 12345
POSIX = {1, 2, 4}
PREAD = {3, 4, 5}
AIO = 5
FILE_SIZE = 3 * 1024 * 1024 + 4321
NAMES = ['sceKernelRead', 'read', '_read', 'sceKernelPread', 'pread', 'AIO']
NEED = {'A': 200, 'K': 50, 'Z': 50, 'E': 50, 'T': 20, 'G': 50}
ARMS = 'AKZETG'


def rows_of(path):
    with open(path, encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        for line in f:
            v = dict(zip(head, line.rstrip('\n').split('\t')))
            yield {k: (v[k] if k in ('entry_name', 'arm') else int(v[k])) for k in head}


def quiet(r):
    e = r['entry']
    if e in POSIX:
        return r['err'] == SENTRY
    if e == AIO:
        return r['aio_rc'] == 0 and r['aio_state'] == 3
    return True


def form(r):
    e = r['entry']
    if e in (0, 3):
        return r['ret'] == EIO
    if e in POSIX:
        return r['ret'] == -1 and r['err'] == 5
    return r['aio_rc'] == 0 and r['ret'] == EIO and r['aio_state'] == 4


def pos(r):
    if r['entry'] in PREAD:
        return r['pos_after'] == r['pos_before']
    return r['pos_after'] == r['pos_before'] + (r['ret'] if r['ret'] > 0 else 0)


def full(r):
    return r['ret'] == r['expected'] and r['data_ok'] == 1


def calls(r, n, inj):
    return r['calls'] == n and r['injected'] == inj


def letter(r, fix):
    a = r['arm']
    if a == 'A':
        if fix == 1:
            return {'form': form(r), 'untouched': r['untouched'] == 1, 'pos': pos(r)}
        return {'zero': r['ret'] == 0, 'quiet': quiet(r), 'untouched': r['untouched'] == 1, 'pos': pos(r)}
    if a == 'K':
        return {'full': full(r), 'quiet': quiet(r), 'calls': calls(r, 2, 1), 'pos': pos(r)}
    if a == 'Z':
        return {'full': full(r), 'quiet': quiet(r), 'calls': calls(r, 1, 0), 'pos': pos(r)}
    if a == 'E':
        return {'zero': r['ret'] == 0, 'quiet': quiet(r), 'calls1': calls(r, 1, 0), 'untouched': r['untouched'] == 1,
                'pos': pos(r), 'rem0': r['remaining'] == 0}
    if a == 'T':
        return {'zero': r['ret'] == 0, 'quiet': quiet(r),
                'trunc': r['trunc_done'] == 1 and r['size_at_c2'] == r['offset'], 'restored': r['restore_ok'] == 1}
    return {'zero': r['ret'] == 0, 'quiet': quiet(r), 'calls1': calls(r, 1, 0), 'untouched': r['untouched'] == 1,
            'pos': pos(r), 'rem0': r['remaining'] == 0,
            'grown': r['trunc_done'] == 1 and r['size_at_c2'] == r['offset'] + 8192,
            'restored': r['restore_ok'] == 1, 'guard': r['canary_ok'] == 1}


def proc_of(path, n_rows):
    m = re.match(r'rows_(\d+)_f(\d)\.tsv$', os.path.basename(path))
    if not m:
        return False, 'no stdout name'
    p = os.path.join(os.path.dirname(path), 'stdout_%s_f%s.txt' % m.groups())
    try:
        txt = open(p, 'rb').read().decode('utf-8', 'replace')
    except OSError:
        return False, 'no stdout file'
    fin = 'FINAL file sha256 equal 1' in txt
    d = re.findall(r'DONE trials=(\d+)', txt)
    ok = fin and d == [str(n_rows)]
    return ok, 'FINAL 1 %s, DONE %s (rows %d)' % (fin, d, n_rows)


def main():
    args = sys.argv[1:]
    need = dict(NEED)
    if args and args[0] == '--need':
        need = dict(zip(ARMS, map(int, args[1].split(','))))
        args = args[2:]
    fix = int(args[0])
    files = args[1:]
    allrows = []
    ok_log = True
    ok_proc = True
    logline = []
    procline = []
    for p in files:
        rs = list(rows_of(p))
        allrows += rs
        try:
            txt = open(p + '.log', 'rb').read().decode('utf-8', 'replace')
        except OSError:
            txt = ''
        m1, m0 = txt.count('FixF25: mode=1'), txt.count('FixF25: mode=0')
        ft = txt.count('FixF25: read failed twice')
        n_a = sum(1 for r in rs if r['arm'] == 'A')
        if fix == 1:
            good = m1 == 1 and m0 == 0 and ft == min(32, n_a)
        else:
            good = m0 == 1 and m1 == 0 and ft == 0
        ok_log &= good
        logline.append('mode=1 %d mode=0 %d read_failed_twice %d (A rows %d) %s' % (m1, m0, ft, n_a, good))
        pg, pl = proc_of(p, len(rs))
        ok_proc &= pg
        procline.append(pl)
    stat = {}
    fails = {}
    canary_bad = 0
    for r in allrows:
        k = (r['entry'], r['arm'])
        s = stat.setdefault(k, [0, 0, 0])
        s[0] += 1
        m = letter(r, fix)
        if all(m.values()):
            s[1] += 1
        if r['arm'] in 'EG' and r['offset'] == FILE_SIZE:
            s[2] += 1
        for n, v in m.items():
            if not v:
                key = (NAMES[r['entry']], r['arm'], n)
                fails[key] = fails.get(key, 0) + 1
        canary_bad += r['canary_ok'] != 1
    print('fix=%d rows %d fix column values %s' % (fix, len(allrows), sorted(set(r['fix'] for r in allrows))))
    print('entry\tarm\tn\tletter_ok\toffset=size')
    ok_rows = True
    for e in range(6):
        for a in ARMS:
            n, l, x = stat.get((e, a), [0, 0, 0])
            print('%s\t%s\t%d\t%d\t%s' % (NAMES[e], a, n, l, x if a in 'EG' else '-'))
            ok_rows &= n == need[a] and l == n
            if a in 'EG':
                ok_rows &= x == (n + 1) // 2
    ok_fix = sorted(set(r['fix'] for r in allrows)) == [fix]
    print('letter failures:', ', '.join('%s/%s/%s %d' % (k + (v,)) for k, v in sorted(fails.items())) or 'none')
    by_arm = {}
    for (en, a, n), v in fails.items():
        by_arm.setdefault(a, set()).add(n)
    print('failing members by arm:', '; '.join('%s: %s' % (a, ','.join(sorted(s))) for a, s in sorted(by_arm.items()))
          or 'none')
    print('guard bad (all arms, reference outside G)', canary_bad)
    print('log:', '; '.join(logline))
    print('process:', '; '.join(procline))
    print('MEMBERS LETTER %s' % ('YES' if ok_rows and ok_log and ok_fix and ok_proc else 'NO'))


main()
