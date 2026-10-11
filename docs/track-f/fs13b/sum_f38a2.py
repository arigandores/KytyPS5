"""F38a2 (HPP-777): members of ROADMAP s122 item 691(d)(1) with item 693(b)(1)-(2) on the rows of the F25 stand edition 3
- per arm and entry, for one process (=1 or =0). Not a verdict of the row (that is F38d). Own summator of the link,
written from the letter of the items (the arms A/K/Z/T members are the F38a sum_f38a.py members; E and G are new).

    python sum_f38a2.py <rows_<seed>_f<fix>.tsv> [--n A,K,Z,E,T,G] [--json out.json]
        # the log <rows>.log is read for the FixF25 lines, stdout_<seed>_f<fix>.txt next to the rows for FINAL / DONE
    python sum_f38a2.py --fixture        # synthetic rows and mutant forms, prints ALL OK / FAIL

Per trial members (entry e; POSIX entries read, _read, pread; pread entries sceKernelPread, pread, AIO):
  pos    - read entries: pos_after == pos_before + max(ret, 0); pread entries: pos_after == pos_before (q);
  canary - guard bytes intact;
  quiet  - no error: POSIX errno not written (== 12345), AIO aio_rc 0 and state COMPLETED (3);
  A at =1  : form (sceKernelRead/sceKernelPread ret 0x80020005; read/_read/pread ret -1 and errno 5; AIO aio_rc 0,
             return_value 0x80020005, state ABORTED (4)), untouched, pos, canary, reached (calls 2, injected 2,
             c1_guest 1, c2_host 1);
  A at =0  : ret 0 and quiet, untouched, pos, canary, reached;
  K        : full (ret == expected, data_ok), quiet, calls 2, injected 1, c2_host 1, pos, canary;
  Z        : full, quiet, calls 1, injected 0, pos, canary;
  E (693(b)(2)): remaining 0, ret 0, quiet, calls 1, injected 0, untouched, pos (read entries: pos_after == offset),
             canary;
  T        : ret 0, quiet, calls 2, injected 2, trunc_done 1, size_at_c2 == offset, restore_ok 1, untouched, pos, canary;
  G (693(b)(1)): remaining 0, ret 0, quiet, calls 1, injected 0, untouched, pos (read entries: pos_after == offset),
             grown (trunc_done 1, size_at_c2 == offset + 8192), restore_ok 1, canary.
Row members: the trials of every (entry, arm) = the N of the arm (--n, default 200,50,50,50,20,50); E and G: the
trials with offset == FILE_SIZE exactly = ceil(n / 2) (half, Н4). A trial passes when every member of its arm holds; an
arm row passes when all its trials pass and the row members hold. Log members: =1 - one line 'FixF25: mode=1', lines
'FixF25: read failed twice' = min(32, trials of A); =0 - one line 'FixF25: mode=0', 0 lines 'FixF25: read failed twice'.
Process members: stdout 'FINAL file sha256 equal 1' and 'DONE trials=<sum of rows>'; fix column = the fix of the process.
MEMBERS PASS - all of them. Stand defect lines (stop and a lead item, 693(b)(3)): a K, Z or E row not full, a T trial
without the shortening or a G trial without the growth."""
import json
import math
import os
import re
import sys

SENTRY = 12345
EIO = -2147352571
FILE_SIZE = 3 * 1024 * 1024 + 4321
GROW = 8192
POSIX_ENTRIES = {1, 2, 4}
PREAD_ENTRIES = {3, 4, 5}
AIO = 5
NAMES = ['sceKernelRead', 'read', '_read', 'sceKernelPread', 'pread', 'sceKernelAioSubmitReadCommands']
ARMS = ['A', 'K', 'Z', 'E', 'T', 'G']
N_DEFAULT = {'A': 200, 'K': 50, 'Z': 50, 'E': 50, 'T': 20, 'G': 50}


def pos_ok(r):
    if r['entry'] in PREAD_ENTRIES:
        return r['pos_after'] == r['pos_before']
    return r['pos_after'] == r['pos_before'] + max(r['ret'], 0)


def pos_at_offset(r):
    # E, G: read entries stay at the read position (offset); pread entries keep q
    if r['entry'] in PREAD_ENTRIES:
        return r['pos_after'] == r['pos_before']
    return r['pos_after'] == r['offset'] and r['pos_before'] == r['offset']


def quiet(r):
    if r['entry'] in POSIX_ENTRIES:
        return r['err'] == SENTRY
    if r['entry'] == AIO:
        return r['aio_rc'] == 0 and r['aio_state'] == 3
    return True


def eio_form(r):
    e = r['entry']
    if e in (0, 3):
        return r['ret'] == EIO
    if e in POSIX_ENTRIES:
        return r['ret'] == -1 and r['err'] == 5
    return r['aio_rc'] == 0 and r['ret'] == EIO and r['aio_state'] == 4


def members(r, fix):
    a = r['arm']
    m = {'pos': pos_ok(r), 'canary': r['canary_ok'] == 1}
    full = r['ret'] == r['expected'] and r['data_ok'] == 1
    if a == 'A':
        m['reached'] = r['calls'] == 2 and r['injected'] == 2 and r['c1_guest'] == 1 and r['c2_host'] == 1
        m['untouched'] = r['untouched'] == 1
        if fix == 1:
            m['eio_form'] = eio_form(r)
        else:
            m['zero'] = r['ret'] == 0
            m['quiet'] = quiet(r)
    elif a == 'K':
        m.update(full=full, quiet=quiet(r), calls=r['calls'] == 2 and r['injected'] == 1 and r['c2_host'] == 1)
    elif a == 'Z':
        m.update(full=full, quiet=quiet(r), calls=r['calls'] == 1 and r['injected'] == 0)
    elif a == 'E':
        m.update(remaining0=r['remaining'] == 0, zero=r['ret'] == 0, quiet=quiet(r),
                 calls=r['calls'] == 1 and r['injected'] == 0, untouched=r['untouched'] == 1,
                 pos_offset=pos_at_offset(r))
    elif a == 'T':
        m.update(zero=r['ret'] == 0, quiet=quiet(r), calls=r['calls'] == 2 and r['injected'] == 2,
                 trunc=r['trunc_done'] == 1 and r['size_at_c2'] == r['offset'], restored=r['restore_ok'] == 1,
                 untouched=r['untouched'] == 1)
    elif a == 'G':
        m.update(remaining0=r['remaining'] == 0, zero=r['ret'] == 0, quiet=quiet(r),
                 calls=r['calls'] == 1 and r['injected'] == 0, untouched=r['untouched'] == 1,
                 pos_offset=pos_at_offset(r), grown=r['trunc_done'] == 1 and r['size_at_c2'] == r['offset'] + GROW,
                 restored=r['restore_ok'] == 1)
    return m


def load(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        for line in f:
            v = dict(zip(head, line.rstrip('\n').split('\t')))
            rows.append({k: (v[k] if k in ('entry_name', 'arm') else int(v[k])) for k in head})
    return rows


def log_counts(path):
    try:
        data = open(path, 'rb').read().decode('utf-8', 'replace')
    except OSError:
        return None
    return {'mode1': data.count('FixF25: mode=1'), 'mode0': data.count('FixF25: mode=0'),
            'failed_twice': data.count('FixF25: read failed twice')}


def stdout_info(path):
    try:
        data = open(path, 'rb').read().decode('utf-8', 'replace')
    except OSError:
        return None
    m = re.search(r'^DONE trials=(\d+)', data, re.M)
    return {'final': 'FINAL file sha256 equal 1' in data, 'done': int(m.group(1)) if m else -1}


def summarize(rows, fix, logc, sout, n_want):
    table = {}
    fails = {}
    for r in rows:
        key = (r['entry'], r['arm'])
        t = table.setdefault(key, [0, 0])
        t[1] += 1
        m = members(r, fix)
        if all(m.values()):
            t[0] += 1
        for k, v in m.items():
            if not v:
                fails[(r['entry'], r['arm'], k)] = fails.get((r['entry'], r['arm'], k), 0) + 1
    row_members = {}
    for e in range(6):
        for a in ARMS:
            rs = [r for r in rows if r['entry'] == e and r['arm'] == a]
            rm = {'n': len(rs) == n_want[a]}
            if a in ('E', 'G'):
                rm['half_at_size'] = sum(1 for r in rs if r['offset'] == FILE_SIZE) == math.ceil(len(rs) / 2)
            row_members[(e, a)] = rm
            for k, v in rm.items():
                if not v:
                    fails[(e, a, 'row:' + k)] = 1
    ok_rows = all(table.get(k, [0, 0])[0] == table.get(k, [0, -1])[1] and all(v.values())
                  for k, v in row_members.items())
    n_a = sum(n for (e, a), (p, n) in table.items() if a == 'A')
    if logc is None:
        ok_log = False
    elif fix == 1:
        ok_log = logc['mode1'] == 1 and logc['mode0'] == 0 and logc['failed_twice'] == min(32, n_a)
    else:
        ok_log = logc['mode0'] == 1 and logc['mode1'] == 0 and logc['failed_twice'] == 0
    ok_proc = sout is not None and sout['final'] and sout['done'] == len(rows)
    fixes = sorted(set(r['fix'] for r in rows))
    ok_fix = fixes == [fix]
    defects = []
    for e in range(6):
        for a in ('K', 'Z', 'E'):
            p, n = table.get((e, a), [0, 0])
            if p != n or n == 0:
                defects.append('dead control %s/%s %d/%d' % (NAMES[e], a, p, n))
    for r in rows:
        if r['arm'] == 'T' and r['trunc_done'] != 1:
            defects.append('T without shortening %s/%d' % (NAMES[r['entry']], r['index']))
        if r['arm'] == 'G' and r['trunc_done'] != 1:
            defects.append('G without growth %s/%d' % (NAMES[r['entry']], r['index']))
    return table, fails, ok_rows, ok_log, ok_proc, ok_fix, defects


def report(rows, fix, logc, sout, n_want):
    table, fails, ok_rows, ok_log, ok_proc, ok_fix, defects = summarize(rows, fix, logc, sout, n_want)
    out = []
    out.append('| Вход | Плечо | Испытаний | Все члены | Ret: 0 / код ошибки / полное / прочее | Позиция верна | Охрана цела '
               '| `offset` = размер | Удлинение / укорочение | Восстановлен |')
    out.append('|---|---|---|---|---|---|---|---|---|---|')
    for e in range(6):
        for a in ARMS:
            rs = [r for r in rows if r['entry'] == e and r['arm'] == a]
            if not rs:
                continue
            z = sum(1 for r in rs if r['ret'] == 0)
            er = sum(1 for r in rs if r['ret'] < 0)
            fu = sum(1 for r in rs if r['ret'] > 0 and r['ret'] == r['expected'] and r['data_ok'] == 1)
            ot = len(rs) - z - er - fu
            at_size = str(sum(1 for r in rs if r['offset'] == FILE_SIZE)) if a in ('E', 'G') else '—'
            moved = str(sum(1 for r in rs if r['trunc_done'] == 1)) if a in ('T', 'G') else '—'
            rest = str(sum(1 for r in rs if r['restore_ok'] == 1)) if a in ('T', 'G') else '—'
            out.append('| `%s` | %s | %d | **%d** | %d / %d / %d / %d | %d | %d | %s | %s | %s |' % (
                NAMES[e], a, len(rs), table[(e, a)][0], z, er, fu, ot, sum(1 for r in rs if pos_ok(r)),
                sum(1 for r in rs if r['canary_ok'] == 1), at_size, moved, rest))
    out.append('')
    out.append('member failures: %s' % (', '.join('%s/%s/%s %d' % (NAMES[k[0]], k[1], k[2], v)
                                                   for k, v in sorted(fails.items())) or 'none'))
    out.append('log: %s' % logc)
    out.append('stdout: %s' % sout)
    out.append('fix column = %d in all rows: %s' % (fix, ok_fix))
    out.append('stand defect lines: %s' % ('; '.join(defects[:20]) or 'none'))
    out.append('arm rows full (with N and half members): %s; log members: %s; process members: %s' % (
        ok_rows, ok_log, ok_proc))
    ok = ok_rows and ok_log and ok_proc and ok_fix and not defects
    out.append('MEMBERS %s (fix=%d)' % ('PASS' if ok else 'FAIL', fix))
    return out, ok, table


# ---- fixture ----

def synth(fix, n=4):
    rows = []
    for e in range(6):
        for a in ARMS:
            for i in range(n):
                pread = e in PREAD_ENTRIES
                end_arm = a in ('E', 'G')
                off = (FILE_SIZE if i % 2 == 0 else FILE_SIZE + 1 + i) if end_arm else 1000 + i
                rem = 0 if end_arm else 4000 - i
                nb = 16
                exp = min(nb, rem)
                q = 77 + i
                r = {'seed': 1, 'fix': fix, 'entry': e, 'entry_name': NAMES[e], 'arm': a, 'index': i,
                     'pos_before': q if pread else off, 'offset': off, 'nbytes': nb, 'remaining': rem, 'expected': exp,
                     'ret': 0, 'err': SENTRY, 'aio_rc': 0, 'aio_state': 3 if e == AIO else 0, 'pos_after': 0, 'calls': 1,
                     'injected': 0, 'c1_guest': 1, 'c2_host': 0, 'data_ok': 1, 'canary_ok': 1, 'untouched': 1,
                     'trunc_done': 0, 'size_at_c2': -1, 'restore_ok': 1}
                if a in ('K', 'Z'):
                    r['ret'] = exp
                    r['untouched'] = 0
                    if a == 'K':
                        r.update(calls=2, injected=1, c2_host=1)
                if a == 'A':
                    r.update(calls=2, injected=2, c2_host=1)
                    if fix == 1:
                        if e in POSIX_ENTRIES:
                            r.update(ret=-1, err=5)
                        else:
                            r['ret'] = EIO
                        if e == AIO:
                            r['aio_state'] = 4
                if a == 'T':
                    r.update(calls=2, injected=2, c2_host=1, trunc_done=1, size_at_c2=off)
                if a == 'G':
                    r.update(trunc_done=1, size_at_c2=off + GROW)
                r['pos_after'] = r['pos_before'] if pread else r['pos_before'] + max(r['ret'], 0)
                rows.append(r)
    return rows


def fixture():
    ok = True
    n4 = {a: 4 for a in ARMS}
    good_log = {1: {'mode1': 1, 'mode0': 0, 'failed_twice': 24}, 0: {'mode1': 0, 'mode0': 1, 'failed_twice': 0}}
    good_out = {'final': True, 'done': 6 * 6 * 4}

    def check(name, rows, fix, logc, want, sout=good_out, n_want=n4):
        nonlocal ok
        got = report(rows, fix, logc, sout, n_want)[1]
        good = got == want
        ok &= good
        print('%s %s: want %s got %s' % ('OK  ' if good else 'FAIL', name, want, got))

    def mut(fix, pred, change):
        rows = synth(fix)
        for r in rows:
            if pred(r):
                change(r)
                break
        return rows

    def mut_all(fix, pred, change):
        rows = synth(fix)
        for r in rows:
            if pred(r):
                change(r)
        return rows

    check('good =1', synth(1), 1, good_log[1], True)
    check('good =0', synth(0), 0, good_log[0], True)
    # m1: the flag is not set - A gives 0 at =1
    check('m1 A zero at =1', mut(1, lambda r: r['arm'] == 'A' and r['entry'] == 0,
                                 lambda r: r.update(ret=0)), 1, good_log[1], False)
    # m2b form: the flag at remaining = 0 without the retry - EIO in G (the grown size hides nothing)
    check('m2b G EIO sceKernelRead', mut(1, lambda r: r['arm'] == 'G' and r['entry'] == 0,
                                         lambda r: r.update(ret=EIO)), 1, good_log[1], False)
    check('m2b G read -1 errno 5', mut(1, lambda r: r['arm'] == 'G' and r['entry'] == 1,
                                       lambda r: r.update(ret=-1, err=5)), 1, good_log[1], False)
    check('m2b G AIO aborted', mut(1, lambda r: r['arm'] == 'G' and r['entry'] == AIO,
                                   lambda r: r.update(ret=EIO, aio_state=4)), 1, good_log[1], False)
    # m2a form: the early return at remaining = 0 removed - a second (retry) read gives the appended data
    check('m2a G retry data', mut(1, lambda r: r['arm'] == 'G' and r['entry'] == 3,
                                  lambda r: r.update(ret=16, calls=2, c2_host=1, untouched=0)), 1, good_log[1], False)
    check('m2a G second call only', mut(1, lambda r: r['arm'] == 'G' and r['entry'] == 4,
                                        lambda r: r.update(calls=2)), 1, good_log[1], False)
    check('m2a E second call', mut(1, lambda r: r['arm'] == 'E' and r['entry'] == 2,
                                   lambda r: r.update(calls=2)), 1, good_log[1], False)
    # the same at =0 (G members are the same for both values)
    check('G EIO at =0', mut(0, lambda r: r['arm'] == 'G' and r['entry'] == 3,
                             lambda r: r.update(ret=EIO)), 0, good_log[0], False)
    # m2 old form: an error in E
    check('m2 E error at =1', mut(1, lambda r: r['arm'] == 'E' and r['entry'] == 1,
                                  lambda r: r.update(ret=-1, err=5)), 1, good_log[1], False)
    # m3: no size re-read - an error in T
    check('m3 T error at =1', mut(1, lambda r: r['arm'] == 'T' and r['entry'] == 3,
                                  lambda r: r.update(ret=EIO)), 1, good_log[1], False)
    # m4: EIO with a moved position
    check('m4 A position', mut(1, lambda r: r['arm'] == 'A' and r['entry'] == 0,
                               lambda r: r.update(pos_after=r['pos_after'] + 7)), 1, good_log[1], False)
    check('m4 A pread position', mut(1, lambda r: r['arm'] == 'A' and r['entry'] == 4,
                                     lambda r: r.update(pos_after=r['offset'])), 1, good_log[1], False)
    # m5: wrong form
    check('m5 sceKernelRead -1', mut(1, lambda r: r['arm'] == 'A' and r['entry'] == 0,
                                     lambda r: r.update(ret=-1)), 1, good_log[1], False)
    check('m5 AIO completed', mut(1, lambda r: r['arm'] == 'A' and r['entry'] == AIO,
                                  lambda r: r.update(aio_state=3)), 1, good_log[1], False)
    check('m5 POSIX errno 9', mut(1, lambda r: r['arm'] == 'A' and r['entry'] == 2,
                                  lambda r: r.update(err=9)), 1, good_log[1], False)
    check('=0 A error', mut(0, lambda r: r['arm'] == 'A' and r['entry'] == 3,
                            lambda r: r.update(ret=EIO)), 0, good_log[0], False)
    # E and G members
    check('E buffer written', mut(1, lambda r: r['arm'] == 'E', lambda r: r.update(untouched=0)), 1, good_log[1], False)
    check('E read pos moved', mut(1, lambda r: r['arm'] == 'E' and r['entry'] == 0,
                                  lambda r: r.update(pos_after=r['offset'] + 1, pos_before=r['offset'] + 1)),
          1, good_log[1], False)
    check('E injected', mut(1, lambda r: r['arm'] == 'E', lambda r: r.update(injected=1)), 1, good_log[1], False)
    check('E not half at size', mut_all(1, lambda r: r['arm'] == 'E' and r['entry'] == 1,
                                        lambda r: r.update(offset=FILE_SIZE + 5, pos_before=FILE_SIZE + 5,
                                                           pos_after=FILE_SIZE + 5)), 1, good_log[1], False)
    check('G not half at size', mut_all(1, lambda r: r['arm'] == 'G' and r['entry'] == 3,
                                        lambda r: r.update(offset=FILE_SIZE, size_at_c2=FILE_SIZE + GROW)),
          1, good_log[1], False)
    check('G no growth', mut(1, lambda r: r['arm'] == 'G', lambda r: r.update(trunc_done=0)), 1, good_log[1], False)
    check('G grown wrong size', mut(1, lambda r: r['arm'] == 'G', lambda r: r.update(size_at_c2=r['offset'])),
          1, good_log[1], False)
    check('G not restored', mut(1, lambda r: r['arm'] == 'G', lambda r: r.update(restore_ok=0)), 1, good_log[1], False)
    check('G remaining > 0', mut(1, lambda r: r['arm'] == 'G', lambda r: r.update(remaining=5)), 1, good_log[1], False)
    check('G buffer written', mut(1, lambda r: r['arm'] == 'G', lambda r: r.update(untouched=0)), 1, good_log[1], False)
    check('G read pos moved', mut(1, lambda r: r['arm'] == 'G' and r['entry'] == 2,
                                  lambda r: r.update(pos_after=r['offset'] + 3)), 1, good_log[1], False)
    # dead controls and T
    check('K dead', mut(1, lambda r: r['arm'] == 'K', lambda r: r.update(calls=1)), 1, good_log[1], False)
    check('Z partial', mut(1, lambda r: r['arm'] == 'Z', lambda r: r.update(ret=r['expected'] - 1)), 1, good_log[1],
          False)
    check('T no shortening', mut(1, lambda r: r['arm'] == 'T', lambda r: r.update(trunc_done=0)), 1, good_log[1],
          False)
    check('T not restored', mut(1, lambda r: r['arm'] == 'T', lambda r: r.update(restore_ok=0)), 1, good_log[1],
          False)
    check('A buffer written', mut(1, lambda r: r['arm'] == 'A', lambda r: r.update(untouched=0)), 1, good_log[1],
          False)
    # N, log, process members
    check('N wrong', synth(1), 1, good_log[1], False, n_want=dict(n4, G=5))
    check('arm G missing', [r for r in synth(1) if r['arm'] != 'G'], 1, good_log[1], False,
          sout={'final': True, 'done': 6 * 5 * 4})
    check('log =1 no mode line', synth(1), 1, {'mode1': 0, 'mode0': 0, 'failed_twice': 24}, False)
    check('log =1 lines 0', synth(1), 1, {'mode1': 1, 'mode0': 0, 'failed_twice': 0}, False)
    check('log =0 failed lines', synth(0), 0, {'mode1': 0, 'mode0': 1, 'failed_twice': 3}, False)
    check('log missing', synth(1), 1, None, False)
    check('stdout FINAL 0', synth(1), 1, good_log[1], False, sout={'final': False, 'done': 144})
    check('stdout DONE short', synth(1), 1, good_log[1], False, sout={'final': True, 'done': 143})
    check('stdout missing', synth(1), 1, good_log[1], False, sout=None)
    check('fix column wrong', synth(0), 1, good_log[1], False)
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    if sys.argv[1] == '--fixture':
        return fixture()
    path = sys.argv[1]
    rows = load(path)
    fix = rows[0]['fix']
    n_want = dict(N_DEFAULT)
    if '--n' in sys.argv:
        n_want = dict(zip(ARMS, (int(x) for x in sys.argv[sys.argv.index('--n') + 1].split(','))))
    logc = log_counts(path + '.log')
    tag = os.path.basename(path)[len('rows_'):-len('.tsv')]
    sout = stdout_info(os.path.join(os.path.dirname(path), 'stdout_%s.txt' % tag))
    out, ok, table = report(rows, fix, logc, sout, n_want)
    print('\n'.join(out))
    if '--json' in sys.argv:
        json.dump({'fix': fix, 'ok': ok, 'log': logc, 'stdout': sout, 'n': n_want,
                   'table': {'%s/%s' % (NAMES[e], a): v for (e, a), v in table.items()}},
                  open(sys.argv[sys.argv.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
