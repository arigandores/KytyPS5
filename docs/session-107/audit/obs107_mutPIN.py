"""Session 107, pred/01_obs107.md scorer: one pinned run `obs107` (plkstat=1 cspmemo=3, defaults otherwise).
Reads the raw log only.  Window: FrameTrace rows with n >= 1800 (the ABBA convention's start), all of them.

    python C:/kyty/s107/obs107.py obs107 [--root <dir>] [--draft] [--out <json>]

Readouts (per flip means over the window; ratios are ratios of sums):
  spin share          = sum pl_cont_cpu_ns / sum pl_cont_wall_ns
  holder shares       = sum pl_cont_hK_ns / sum pl_cont_wall_ns, K = 0..3
  tag2_us             = mean pl_cont_h2_ns / 1000        (contended GuestGpu wall behind the walker's prefetch)
  would_rate          = sum cspm_would / sum cspm_look
Rules (pred/01 s4):
  VERIFY  PASS iff sum cspm_bad == 0, no "CspMemoVerify:" line, sum cspm_would > 0.
  GO      (run the ABBA cspmemo=0|2) iff VERIFY PASS and would_rate >= 0.5 and tag2_us >= 100.
  Admission: pin once, no fatal marker (incl. AsyncPipelines: skipped draw), two record threads, pl_prog_n > 0,
  cspm_look > 0, >= 3000 window rows, one ok attempt, gate text carries plkstat=1 and cspmemo=3.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

PRED = 'C:/kyty/s107/pred/01_obs107.md'
PRED_SHA = '85a65121dce86e65c442becf2f5859ef4c215f1848ad4439902e616872ac1db6'   # pred/01 sealed
PRED_BYTES = 3138
START = 1800
MIN_ROWS = 3000
LINE = re.compile(rb'^(FrameTrace(?:-draw|-x)?): n=(\d+)')
FIELD = re.compile(rb'(\w+)=(-?\d+)')
FATAL = (b'--- Error ---', b'--- Fatal Error ---', b'--- std::terminate ---', b'--- abort() ---',
         b'ErrorDeviceLost', b'Unhandled exception:', b'GpuWaitSlow:', b'AsyncPipelines: skipped draw',
         b'GpuHangAbort')
X_KEYS = ('pl_cont_n', 'pl_cont_wall_ns', 'pl_cont_cpu_ns', 'pl_cont_h0_ns', 'pl_cont_h1_ns', 'pl_cont_h2_ns',
          'pl_cont_h3_ns', 'pl_cont_h0_n', 'pl_cont_h1_n', 'pl_cont_h2_n', 'pl_cont_h3_n', 'pl_wq_hold_ns',
          'pl_wq_hold_n', 'pl_wp_hold_ns', 'pl_wp_hold_n', 'cspm_look', 'cspm_would', 'cspm_skip', 'cspm_bad',
          'cspm_store', 'cspm_clear', 'cspf_have', 'cspf_new', 'pl_prog_n', 'pl_prog_wait_us', 'pl_pipe_wait_us',
          'pl_cs_wait_us')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(root, tag):
    rows, fatal, pins, rec, verify_lines = {}, {}, 0, 0, 0
    with open(Path(root) / ('log_%s.txt' % tag), 'rb') as f:
        for line in f:
            m = LINE.match(line)
            if m:
                n = int(m.group(2))
                d = rows.setdefault(n, {})
                for k, v in FIELD.findall(line[m.end():]):
                    d[k.decode()] = int(v)
                continue
            for mk in FATAL:
                if mk in line:
                    fatal[mk.decode()] = fatal.get(mk.decode(), 0) + 1
            if b'GpuClockPin: mode 1' in line:
                pins += 1
            if b'RecordThread: started' in line:
                rec += 1
            if line.startswith(b'CspMemoVerify:'):
                verify_lines += 1
    return rows, fatal, pins, rec, verify_lines


def evaluate(root, tag, draft):
    out = {'scorer': 'obs107.py', 'scorer_sha256': sha(__file__), 'tag': tag, 'draft': draft}
    if not draft:
        if PRED_SHA is None or sha(PRED) != PRED_SHA or Path(PRED).stat().st_size != PRED_BYTES:
            raise SystemExit('seal mismatch: refusing to score')
    meta = json.loads((Path(root) / ('%s.json' % tag)).read_text(encoding='utf-8'))
    rows, fatal, pins, rec, verify_lines = read(root, tag)
    win = [d for n, d in sorted(rows.items()) if n >= START and all(k in d for k in X_KEYS) and 'dt_us' in d]
    tot = {k: sum(d[k] for d in win) for k in X_KEYS + ('dt_us', 'cpu_gpu_us')}
    nwin = len(win)
    mean = {k: (tot[k] / nwin if nwin else None) for k in tot}
    wall = tot['pl_cont_wall_ns']
    r = {
        'rows': nwin,
        'spin_share': tot['pl_cont_cpu_ns'] / wall if wall else None,
        'holder_share': {str(k): (tot['pl_cont_h%d_ns' % k] / wall if wall else None) for k in range(4)},
        'tag2_us': mean['pl_cont_h2_ns'] / 1000.0 if nwin else None,
        'cont_wall_us': mean['pl_cont_wall_ns'] / 1000.0 if nwin else None,
        'would_rate': tot['cspm_would'] / tot['cspm_look'] if tot['cspm_look'] else None,
        'means': mean,
    }
    gates = ' ' + (meta.get('gates') or '') + ' '
    attempts = meta.get('attempts') or []
    admission = {
        'PIN_ONCE': True,
        'NO_FATAL': not fatal,
        'RECORD_THREAD_TWO': True,
        'PLKSTAT_ARMED': tot['pl_prog_n'] > 0,
        'MEMO_ARMED': tot['cspm_look'] > 0,
        'ROWS': nwin >= MIN_ROWS,
        'ONE_OK_ATTEMPT': [a.get('outcome') for a in attempts] == ['ok'] and all(
            a.get('hold_exit') is None for a in attempts),
        'GATE_TEXT': ' plkstat=1 ' in gates and ' cspmemo=3 ' in gates,
    }
    verify = tot['cspm_bad'] == 0 and verify_lines == 0 and tot['cspm_would'] > 0
    go = bool(verify and r['would_rate'] is not None and r['would_rate'] >= 0.5
              and r['tag2_us'] is not None and r['tag2_us'] >= 100.0)
    admitted = all(admission.values())
    out.update(readouts=r, admission=admission, fatal=fatal, verify_lines=verify_lines,
               verify='PASS' if verify else 'FAIL', go=go, admitted=admitted,
               binary_sha256=meta.get('binary_sha256'), prereg=meta.get('prereg'))
    if draft:
        out['verdict'] = 'DRAFT (no verdict) verify=%s go=%s' % (out['verify'], go)
    elif not admitted:
        out['verdict'] = 'INVALID (run not admitted)'
    elif not verify:
        out['verdict'] = 'VERIFY FAIL - cspmemo closed (memo disagrees or never hits)'
    elif go:
        out['verdict'] = 'GO - run the ABBA cspmemo=0|2'
    else:
        out['verdict'] = 'NO-GO - cspmemo closed by the numbers (would_rate < 0.5 or tag2_us < 100)'
    p = {}

    def add(key, text, value, lo, hi):
        p[key] = {'text': text, 'value': value, 'band': [lo, hi],
                  'hit': value is not None and (lo is None or value >= lo) and (hi is None or value <= hi)}

    add('O1', 'spin share >= 0.6', r['spin_share'], 0.6, None)
    add('O2', 'holder tag 2 (walker prefetch) share of contended wall >= 0.4', r['holder_share']['2'], 0.4, None)
    add('O3', 'would_rate >= 0.8', r['would_rate'], 0.8, None)
    add('O4', 'pl_cont_n per flip in [50, 1000]', mean['pl_cont_n'], 50, 1000)
    add('O5', 'cspm_bad sum == 0', tot['cspm_bad'], 0, 0)
    add('O6', 'GO', 1.0 if go else 0.0, 1.0, 1.0)
    out['predictions'] = p
    return out


def main():
    tag = sys.argv[1]
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else 'C:/kyty/s107'
    draft = '--draft' in sys.argv
    out = evaluate(root, tag, draft)
    r = out['readouts']
    print('obs107.py %s rows=%s admitted=%s verify=%s' % (tag, r['rows'], out['admitted'], out['verify']))
    for k, v in out['admission'].items():
        print('  [%s] admission %s' % ('PASS' if v else 'FAIL', k))
    print('  spin share %s  holder shares %s' % (r['spin_share'], r['holder_share']))
    print('  contended wall %s us/flip  tag2 %s us/flip  would_rate %s' % (r['cont_wall_us'], r['tag2_us'],
                                                                         r['would_rate']))
    for k in ('pl_cont_n', 'pl_wq_hold_ns', 'pl_wq_hold_n', 'pl_wp_hold_ns', 'pl_wp_hold_n', 'cspm_look',
              'cspm_would', 'cspm_bad', 'cspm_clear', 'cspf_have', 'cspf_new', 'pl_prog_wait_us',
              'pl_pipe_wait_us', 'pl_cs_wait_us', 'dt_us', 'cpu_gpu_us'):
        print('  %-16s %s' % (k, r['means'].get(k)))
    for k, v in out['predictions'].items():
        print('  prediction %s %s value %s  %s' % (k, 'HIT ' if v['hit'] else 'MISS', v['value'], v['text']))
    print('  VERDICT: %s' % out['verdict'])
    if '--out' in sys.argv:
        path = Path(sys.argv[sys.argv.index('--out') + 1])
        if path.exists():
            raise SystemExit('output exists: never overwritten')
        path.write_text(json.dumps(out, indent=1, default=str), encoding='utf-8')


if __name__ == '__main__':
    main()
