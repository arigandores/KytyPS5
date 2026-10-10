"""F37a (HPP-761): summary of the F25 stand rows (f25_read_fail_stand TSV) by arm and entry, liveness of K and Z
(ROADMAP s122 item 688(zh)(3)) and the candidate outcome of item 688(zh) - not a verdict.

    python sum_f37a.py <rows.tsv> [--json out.json]
    python sum_f37a.py --fixture          # synthetic rows, prints ALL OK / FAIL

Classes per trial: zero (ret == 0), error (ret < 0; POSIX entries: ret == -1 and errno != sentry), full (ret == expected
and the bytes equal the file), other. Position: read entries - pos_after == pos_before + max(ret, 0); pread entries
(sceKernelPread, pread, AIO) - pos_after == pos_before (the file position q set before the call).
K alive on an entry: every K trial full, calls == 2, injected == 1, c2_host == 1, canary_ok, position ok.
Z alive on an entry: every Z trial full, calls == 1, injected == 0, canary_ok, position ok.
A reached: calls == 2 and injected == 2 in every A trial (the retry was taken and failed).
Candidate (item 688(zh)): K and Z alive and A reached on all entries - (1) if any A trial gives zero, (2) if every A
trial gives an error; else (3) (stand dead - one repair inside F37a)."""
import json
import sys

SENTRY = 12345
POSIX_ENTRIES = {1, 2, 4}
PREAD_ENTRIES = {3, 4, 5}
NAMES = ['sceKernelRead', 'read', '_read', 'sceKernelPread', 'pread', 'sceKernelAioSubmitReadCommands']


def classify(r):
    ret = r['ret']
    if ret == 0:
        cls = 'zero'
    elif ret < 0 and (r['entry'] not in POSIX_ENTRIES or (ret == -1 and r['err'] != SENTRY)):
        cls = 'error'
    elif ret == r['expected'] and r['data_ok'] == 1:
        cls = 'full'
    else:
        cls = 'other'
    if r['entry'] in PREAD_ENTRIES:
        pos_ok = r['pos_after'] == r['pos_before']
    else:
        pos_ok = r['pos_after'] == r['pos_before'] + max(ret, 0)
    return cls, pos_ok


def load(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        for line in f:
            v = dict(zip(head, line.rstrip('\n').split('\t')))
            r = {k: (v[k] if k in ('entry_name', 'arm') else int(v[k])) for k in head}
            rows.append(r)
    return rows


def summarize(rows):
    cells = {}
    for r in rows:
        cls, pos_ok = classify(r)
        key = (r['entry'], r['arm'])
        c = cells.setdefault(key, {'n': 0, 'zero': 0, 'error': 0, 'full': 0, 'other': 0, 'pos_ok': 0, 'live': 0,
                                   'reached': 0, 'untouched': 0, 'canary_ok': 0, 'errno_set': 0, 'aio_completed': 0,
                                   'aio_aborted': 0, 'ret_values': {}})
        c['n'] += 1
        c[cls] += 1
        c['pos_ok'] += 1 if pos_ok else 0
        c['canary_ok'] += r['canary_ok']
        c['untouched'] += r['untouched']
        c['errno_set'] += 1 if r['err'] != SENTRY else 0
        if r['entry'] == 5:
            c['aio_completed'] += 1 if r['aio_state'] == 3 else 0
            c['aio_aborted'] += 1 if r['aio_state'] == 4 else 0
        if cls in ('zero', 'error', 'other'):
            c['ret_values'][str(r['ret'])] = c['ret_values'].get(str(r['ret']), 0) + 1
        ok_common = r['canary_ok'] == 1 and pos_ok
        if r['arm'] == 'K':
            c['live'] += 1 if (cls == 'full' and r['calls'] == 2 and r['injected'] == 1 and r['c2_host'] == 1 and ok_common) else 0
        elif r['arm'] == 'Z':
            c['live'] += 1 if (cls == 'full' and r['calls'] == 1 and r['injected'] == 0 and ok_common) else 0
        else:
            c['reached'] += 1 if (r['calls'] == 2 and r['injected'] == 2 and r['c1_guest'] == 1 and r['c2_host'] == 1) else 0
    entries = sorted({k[0] for k in cells})
    k_alive = all(cells.get((e, 'K'), {'n': 0, 'live': -1})['live'] == cells.get((e, 'K'), {'n': 0})['n'] and cells.get((e, 'K'), {'n': 0})['n'] > 0 for e in entries)
    z_alive = all(cells.get((e, 'Z'), {'n': 0, 'live': -1})['live'] == cells.get((e, 'Z'), {'n': 0})['n'] and cells.get((e, 'Z'), {'n': 0})['n'] > 0 for e in entries)
    a_cells = [cells.get((e, 'A'), {'n': 0, 'reached': -1, 'zero': 0, 'error': 0}) for e in entries]
    a_reached = all(c['n'] > 0 and c['reached'] == c['n'] for c in a_cells)
    a_zero = sum(c['zero'] for c in a_cells)
    a_error = sum(c['error'] for c in a_cells)
    a_n = sum(c['n'] for c in a_cells)
    if not (k_alive and z_alive and a_reached):
        cand = '(3)'
    elif a_zero > 0:
        cand = '(1)'
    elif a_error == a_n:
        cand = '(2)'
    else:
        cand = 'none'
    return cells, {'entries': entries, 'k_alive': k_alive, 'z_alive': z_alive, 'a_reached': a_reached,
                   'a_n': a_n, 'a_zero': a_zero, 'a_error': a_error, 'candidate': cand}


def table(cells, s):
    out = ['| Вход | Плечо | Испытаний | Отдано 0 | Отдан код ошибки | Полное чтение | Прочее | Позиция верна | errno записан | Буфер не тронут | Живость / обход взят | Значения ret (не full) |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for e in s['entries']:
        for arm in ('A', 'K', 'Z'):
            c = cells.get((e, arm))
            if c is None:
                continue
            live = ('обход взят и отказал %d' % c['reached']) if arm == 'A' else ('жив %d' % c['live'])
            if e == 5:
                live += '; COMPLETED %d, ABORTED %d' % (c['aio_completed'], c['aio_aborted'])
            rv = ', '.join('%s×%d' % (k, v) for k, v in sorted(c['ret_values'].items())) or '—'
            out.append('| `%s` | %s | %d | %d | %d | %d | %d | %d | %d | %d | %s | %s |' % (
                NAMES[e], arm, c['n'], c['zero'], c['error'], c['full'], c['other'], c['pos_ok'], c['errno_set'],
                c['untouched'], live, rv))
    out.append('')
    out.append('K жив на всех входах: %s; Z жив: %s; A — обход взят и отказал во всех испытаниях: %s; A: испытаний %d, отдано 0 — %d, код ошибки — %d; кандидат п. 688(ж): %s' % (
        s['k_alive'], s['z_alive'], s['a_reached'], s['a_n'], s['a_zero'], s['a_error'], s['candidate']))
    return '\n'.join(out)


def fixture():
    def row(entry, arm, ret, expected, calls, injected, pos_before, pos_after, err=SENTRY, data_ok=1, c2=1, c1=1, aio_state=0):
        return {'entry': entry, 'arm': arm, 'ret': ret, 'expected': expected, 'calls': calls, 'injected': injected,
                'pos_before': pos_before, 'pos_after': pos_after, 'err': err, 'data_ok': data_ok, 'c2_host': c2,
                'c1_guest': c1, 'canary_ok': 1, 'untouched': 1 if ret <= 0 else 0, 'aio_state': aio_state}
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print('%s %s' % ('OK  ' if cond else 'FAIL', name))

    live = []
    for e in range(6):
        pb = 100
        for arm, calls, inj in (('K', 2, 1), ('Z', 1, 0)):
            pa = pb if e in PREAD_ENTRIES else pb + 10
            live.append(row(e, arm, 10, 10, calls, inj, pb, pa, c2=1 if arm == 'K' else 0, aio_state=3))
    a_zero = [row(e, 'A', 0, 10, 2, 2, 100, 100, aio_state=3) for e in range(6)]
    _, s = summarize(live + a_zero)
    check('A zero on all entries, K/Z alive -> (1)', s['candidate'] == '(1)')
    a_err = [row(e, 'A', -1 if e in POSIX_ENTRIES else -2147352571, 10, 2, 2, 100, 100, err=5 if e in POSIX_ENTRIES else SENTRY, aio_state=4) for e in range(6)]
    _, s = summarize(live + a_err)
    check('A error on all entries -> (2)', s['candidate'] == '(2)')
    mixed = a_err[:5] + [a_zero[5]]
    _, s = summarize(live + mixed)
    check('one entry zero -> (1)', s['candidate'] == '(1)')
    posix_no_errno = [row(1, 'A', -1, 10, 2, 2, 100, 100, err=SENTRY)]
    c, _ = summarize(live + posix_no_errno)
    check('POSIX -1 without errno is other, not error', c[(1, 'A')]['other'] == 1 and c[(1, 'A')]['error'] == 0)
    dead_k = [dict(r) for r in live]
    dead_k[0]['calls'] = 1
    _, s = summarize(dead_k + a_zero)
    check('K with one ReadFile call is dead -> (3)', s['candidate'] == '(3)' and not s['k_alive'])
    short_k = [dict(r) for r in live]
    short_k[0]['ret'] = 5
    _, s = summarize(short_k + a_zero)
    check('K short read is dead -> (3)', s['candidate'] == '(3)')
    a_not_reached = [dict(r) for r in a_zero]
    a_not_reached[2]['injected'] = 1
    _, s = summarize(live + a_not_reached)
    check('A without the second injected failure -> (3)', s['candidate'] == '(3)' and not s['a_reached'])
    bad_pos = [dict(r) for r in live]
    for r in bad_pos:
        if r['entry'] == 0 and r['arm'] == 'Z':
            r['pos_after'] = r['pos_before']
    _, s = summarize(bad_pos + a_zero)
    check('Z with a wrong read position is dead', not s['z_alive'])
    pread_pos = [row(3, 'A', 0, 10, 2, 2, 100, 77)]
    c, _ = summarize(live + pread_pos)
    check('pread entry position compares with pos_before', c[(3, 'A')]['pos_ok'] == 0)
    data_bad = [dict(r) for r in live]
    data_bad[1]['data_ok'] = 0
    _, s = summarize(data_bad + a_zero)
    check('Z with wrong bytes is dead', not s['z_alive'])
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    if sys.argv[1:] == ['--fixture']:
        sys.exit(fixture())
    rows = load(sys.argv[1])
    cells, s = summarize(rows)
    print(table(cells, s))
    if '--json' in sys.argv:
        out = sys.argv[sys.argv.index('--json') + 1]
        json.dump({'summary': s, 'cells': {'%s|%s' % k: v for k, v in cells.items()}, 'rows': len(rows)},
                  open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
