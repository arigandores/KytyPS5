"""F38b (HPP-764, Red Team): own reader of the F25 stand edition 2 rows by the letter of ROADMAP s122 item 691(d)(1),
independent of sum_f38a.py. usage: read_f38b.py <fix 0|1> <rows.tsv> [<rows.tsv> ...]

Letter members per trial (entry e; POSIX = read, _read, pread; PREAD = sceKernelPread, pread, AIO; AIO = 5):
  quiet(r)   : POSIX errno not written (12345); AIO call code 0 and state COMPLETED (3); sceKernel* - nothing to check;
  form(r)    : (v)(1) - sceKernelRead/sceKernelPread ret 0x80020005; POSIX ret -1 and errno 5; AIO call code 0,
               return_value 0x80020005, state ABORTED (4);
  pos(r)     : (v)(3) - read entries: position after = position before (ret <= 0) or before + ret (full read);
               PREAD entries: position after = q (pos_before);
  A =1 : form, untouched, pos              A =0 : ret 0, quiet, untouched, pos
  K    : full (ret = expected, data_ok), quiet, calls 2 with 1 injected (as F37a), pos
  Z    : full, quiet, calls 1 with 0 injected (as F37a), pos
  E    : ret 0, quiet (letter: ret 0 without an error code)
  T    : ret 0, quiet, trunc_done and size_at_c2 = offset (T reached the shortening), restore_ok
Variant of the executor (not the letter, printed beside): E also calls 1 with 0 injected, untouched, pos.
Guard bytes (canary) - reference column. Log: FixF25: mode=<fix> once per file, the other mode 0 times; read failed
twice = min(32, A rows) per file at =1, 0 at =0 (691(v)(4), (d)(2)). Last line MEMBERS LETTER YES/NO."""
import sys

EIO = -2147352571
SENTRY = 12345
POSIX = {1, 2, 4}
PREAD = {3, 4, 5}
AIO = 5
NAMES = ['sceKernelRead', 'read', '_read', 'sceKernelPread', 'pread', 'AIO']


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


def letter(r, fix):
    a = r['arm']
    if a == 'A':
        if fix == 1:
            return {'form': form(r), 'untouched': r['untouched'] == 1, 'pos': pos(r)}
        return {'zero': r['ret'] == 0, 'quiet': quiet(r), 'untouched': r['untouched'] == 1, 'pos': pos(r)}
    if a == 'K':
        return {'full': full(r), 'quiet': quiet(r), 'calls': r['calls'] == 2 and r['injected'] == 1, 'pos': pos(r)}
    if a == 'Z':
        return {'full': full(r), 'quiet': quiet(r), 'calls': r['calls'] == 1 and r['injected'] == 0, 'pos': pos(r)}
    if a == 'E':
        return {'zero': r['ret'] == 0, 'quiet': quiet(r)}
    return {'zero': r['ret'] == 0, 'quiet': quiet(r), 'trunc': r['trunc_done'] == 1 and r['size_at_c2'] == r['offset'],
            'restored': r['restore_ok'] == 1}


def variant(r):
    if r['arm'] != 'E':
        return {}
    return {'calls1': r['calls'] == 1 and r['injected'] == 0, 'untouched': r['untouched'] == 1, 'pos': pos(r)}


def main():
    fix = int(sys.argv[1])
    files = sys.argv[2:]
    allrows = []
    ok_log = True
    logline = []
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
    stat = {}
    fails = {}
    vfails = {}
    canary_bad = 0
    for r in allrows:
        k = (r['entry'], r['arm'])
        s = stat.setdefault(k, [0, 0, 0])
        s[0] += 1
        m = letter(r, fix)
        if all(m.values()):
            s[1] += 1
        for n, v in m.items():
            if not v:
                key = (NAMES[r['entry']], r['arm'], n)
                fails[key] = fails.get(key, 0) + 1
        vm = variant(r)
        if all(vm.values()):
            s[2] += 1
        for n, v in vm.items():
            if not v:
                key = (NAMES[r['entry']], r['arm'], n)
                vfails[key] = vfails.get(key, 0) + 1
        canary_bad += r['canary_ok'] != 1
    need = {'A': 200, 'K': 50, 'Z': 50, 'E': 50, 'T': 20}
    print('fix=%d rows %d fix column values %s' % (fix, len(allrows), sorted(set(r['fix'] for r in allrows))))
    print('entry\tarm\tn\tletter_ok\tvariant_ok')
    ok_rows = True
    for e in range(6):
        for a in 'AKZET':
            n, l, v = stat.get((e, a), [0, 0, 0])
            print('%s\t%s\t%d\t%d\t%d' % (NAMES[e], a, n, l, v))
            ok_rows &= n >= need[a] and l == n
    ok_fix = sorted(set(r['fix'] for r in allrows)) == [fix]
    print('letter failures:', ', '.join('%s/%s/%s %d' % (k + (v,)) for k, v in sorted(fails.items())) or 'none')
    print('variant (E calls 1, untouched, pos) failures:',
          ', '.join('%s/%s/%s %d' % (k + (v,)) for k, v in sorted(vfails.items())) or 'none')
    print('canary bad (reference)', canary_bad)
    print('log:', '; '.join(logline))
    print('MEMBERS LETTER %s; VARIANT E %s' % ('YES' if ok_rows and ok_log and ok_fix else 'NO',
                                             'YES' if not vfails else 'NO'))


main()
