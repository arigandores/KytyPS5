"""FS13a (HPP-787, ROADMAP s122 item 697(g)(1)): members of item 691(d)(1) with item 693(b)(1)-(2) on the rows of the F25
stand edition 3 built from the FS13 worktree. The per trial, row, log and process members are those of the F38a2
summator sum_f38a2.py (copied verbatim next to this file, sha256 printed); this file adds the form 'd' of item 697(g)(1):
the stand process runs WITHOUT KYTY_FIX_F25 (the default of FS13).

Form 'd': the stand's own reading of the variable (Common::EnvValueOn, unset -> 0) fills the 'fix' column of the rows and
the stdout line 'FIXF25 env=(unset) on=0' - they say "the variable is not set", not the emulator path. The effective
emulator value is the log line 'FixF25: mode=<v>' printed by FileSystem::Initialize. Members of the form 'd':
  env    - stdout has 'FIXF25 env=(unset) on=0' and the fix column is 0 in every row;
  mode   - the log has exactly one 'FixF25: mode=1' and no 'FixF25: mode=0';
  =1     - every member of sum_f38a2 at fix=1 (rows taken with fix := 1).
MEMBERS LETTER YES - all of them (the letter of item 697(g)(1)).
Form '0' (control KYTY_FIX_F25=0): the sum_f38a2 members at fix=0; the member of item 697(g)(1) is A "0 returned" 200 of
200 on every entry (A row of each entry: all its trials pass the =0 members - ret 0, no error, buffer untouched,
position, canary, reached). CONTROL A ZERO YES / NO, plus the sum_f38a2 verdict line (reference).

    python sum_fs13a.py <rows tsv> --form d|0 [--n A,K,Z,E,T,G] [--json out.json]
    python sum_fs13a.py --fixture
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sum_f38a2 as S  # noqa: E402


def stdout_env(path):
    try:
        data = open(path, 'rb').read().decode('utf-8', 'replace')
    except OSError:
        return None
    return 'FIXF25 env=(unset) on=0' in data


def read_d(rows, logc, sout, env_unset, n_want):
    col0 = all(r['fix'] == 0 for r in rows) and len(rows) > 0
    mode = logc is not None and logc['mode1'] == 1 and logc['mode0'] == 0
    eff = [dict(r, fix=1) for r in rows]
    out, ok, table = S.report(eff, 1, logc, sout, n_want)
    out.append('form d: stdout FIXF25 env=(unset) on=0: %s; fix column 0 in all rows: %s; log FixF25: mode=1 once and '
               'no mode=0: %s' % (env_unset, col0, mode))
    yes = ok and bool(env_unset) and col0 and mode
    out.append('MEMBERS LETTER %s (form d - KYTY_FIX_F25 not set)' % ('YES' if yes else 'NO'))
    return out, yes, table


def read_0(rows, logc, sout, n_want):
    out, ok, table = S.report(rows, 0, logc, sout, n_want)
    per = []
    good = True
    for e in range(6):
        p, n = table.get((e, 'A'), [0, 0])
        per.append('%s %d/%d' % (S.NAMES[e], p, n))
        good &= n == n_want['A'] and p == n
    out.append('control =0: A "0 returned" per entry: %s' % ', '.join(per))
    out.append('CONTROL A ZERO %s' % ('YES' if good else 'NO'))
    return out, good, table


def fixture():
    ok = True
    n4 = {a: 4 for a in S.ARMS}
    sout = {'final': True, 'done': 6 * 6 * 4}
    log1 = {'mode1': 1, 'mode0': 0, 'failed_twice': 24}
    log0 = {'mode1': 0, 'mode0': 1, 'failed_twice': 0}

    def d_rows(fix_col=0, eio=True):
        rows = S.synth(1 if eio else 0)
        return [dict(r, fix=fix_col) for r in rows]

    def check(name, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print('%s %s: want %s got %s' % ('OK  ' if good else 'FAIL', name, want, got))

    check('d good', read_d(d_rows(), log1, sout, True, n4)[1], True)
    check('d old default (mode=0, A gives 0)', read_d(d_rows(eio=False), log0, sout, True, n4)[1], False)
    check('d log mode=1 but A gives 0', read_d(d_rows(eio=False), log1, sout, True, n4)[1], False)
    check('d variable set (column 1)', read_d(d_rows(fix_col=1), log1, sout, True, n4)[1], False)
    check('d stdout env not unset', read_d(d_rows(), log1, sout, False, n4)[1], False)
    check('d log mode line twice', read_d(d_rows(), dict(log1, mode1=2), sout, True, n4)[1], False)
    check('d log missing', read_d(d_rows(), None, sout, True, n4)[1], False)
    check('d one A trial 0', read_d([dict(r, ret=0, err=S.SENTRY, aio_state=3 if r['entry'] == S.AIO else 0,
                                          pos_after=r['pos_before']) if (r['arm'] == 'A' and r['entry'] == 2 and
                                                                           r['index'] == 0) else r
                                     for r in d_rows()], log1, sout, True, n4)[1], False)
    check('0 good', read_0(S.synth(0), log0, sout, n4)[1], True)
    check('0 one A trial EIO', read_0([dict(r, ret=S.EIO) if (r['arm'] == 'A' and r['entry'] == 3 and r['index'] == 1)
                                       else r for r in S.synth(0)], log0, sout, n4)[1], False)
    check('0 A short', read_0([r for r in S.synth(0) if not (r['arm'] == 'A' and r['entry'] == 5 and r['index'] == 3)],
                              log0, sout, n4)[1], False)
    check('0 rows of =1', read_0(S.synth(1), log0, sout, n4)[1], False)
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    if sys.argv[1] == '--fixture':
        return fixture()
    path = sys.argv[1]
    form = sys.argv[sys.argv.index('--form') + 1]
    rows = S.load(path)
    n_want = dict(S.N_DEFAULT)
    if '--n' in sys.argv:
        n_want = dict(zip(S.ARMS, (int(x) for x in sys.argv[sys.argv.index('--n') + 1].split(','))))
    logc = S.log_counts(path + '.log')
    tag = os.path.basename(path)[len('rows_'):-len('.tsv')]
    so = os.path.join(os.path.dirname(path), 'stdout_%s.txt' % tag)
    sout = S.stdout_info(so)
    if form == 'd':
        out, ok, table = read_d(rows, logc, sout, stdout_env(so), n_want)
    else:
        out, ok, table = read_0(rows, logc, sout, n_want)
    print('\n'.join(out))
    if '--json' in sys.argv:
        json.dump({'form': form, 'ok': ok, 'log': logc, 'stdout': sout, 'n': n_want,
                   'table': {'%s/%s' % (S.NAMES[e], a): v for (e, a), v in table.items()}},
                  open(sys.argv[sys.argv.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
