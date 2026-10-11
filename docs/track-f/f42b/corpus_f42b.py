# F42b (HPP-780, Red Team): copy of the F42a corpus_f42a.py with f42a->f42b in ALL lines (runner only; members are recounted by own rc_corpus_f42b.py with twin_f42b.py).
"""F42b (HPP-779, ROADMAP s122 item 694(g)(4)): the T1 corpus at KYTY_FIX_F20=1 - offline, no game.

Rows: the A rows of C:/kyty/s288/s7/t1_base.tsv whose S7 outcome is not HARNESS_UNSUPPORTED and perm != '-' (the row
set of corpus_f12d.py). Each row is translated by the FS12 translator of the F42b build (shader_cfg_tests of the worktree
26283087 = 730ed40a + the F42b commits; the translator files are those of FS12 - signature 9177b426...) in its own
process, every KYTY_* variable removed, with
  KYTY_RECOMPILE="<gcn>;<cache file>;<work>/out.spv;<perm>"   - the words the cache keeps (= the module at =0)
  KYTY_RECOMPILE_F20=<work>/f20.spv                            - the module of =1 (FixF20::RewriteFaultOr with the
                                                                  FaultBuffer binding of the compiled program)
and its line "recompile-f20: bound named sites rewritten unmatched malformed". The independent count (spvscan_f42b.scan,
own Python code) runs on out.spv and f20.spv; the instruction-stream diff (diff_ok) checks that f20.spv differs from
out.spv only by triples replaced with OpAtomicOr of the same type, result id, pointer and bit. spirv-val
(--target-env vulkan1.3 --uniform-buffer-standard-layout, the options of ValidateShaderSpirv at KYTY_FIX_SVAL=1) runs on
f20.spv of every row with rewritten > 0 and on its out.spv (control).
Members (item 694(g)(4)): rewritten (C++) = triples of out.spv (Python) on every row and in sum; triples of f20.spv = 0;
unmatched = 0; modules_bound (bound) = modules (named > 0) row by row; every rewritten module passes spirv-val; plus
rc 0 everywhere and diff_ok on every rewritten row. Writes corpus_f42b.tsv and corpus_f42b.txt (ALL OK / FAIL).
Rows already done (out.spv, f20.spv and stdout present) are not run again (a watchdog kill resumes).
Usage: python corpus_f42b.py <exe> <out dir> [--workers N]. Rule 27: lock and STOP before every process."""
import argparse
import collections
import concurrent.futures as cf
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spvscan_f42b as sv  # noqa: E402

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CACHE_CUR = S7 + '/cache_cur'
T1 = S7 + '/t1_base.tsv'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
LINE = re.compile(rb'recompile-f20: bound=(\d) named=(\d+) sites=(\d+) rewritten=(\d+) unmatched=(\d+) malformed=(\d)')


class Halt(Exception):
    pass


def check_halt():
    if os.path.exists(STOP):
        raise Halt('STOP')
    if os.path.exists(LOCK):
        raise Halt('LOCK')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def diff_ok(base, new):
    """new = base with triples OpLoad/OpBitwiseOr/OpStore replaced by OpAtomicOr(type, v, p, c1, c0, bit); returns
    (ok, replaced)."""
    a = list(sv.walk(base))
    b = list(sv.walk(new))
    if base[:5] != new[:5]:
        return False, 0
    i = j = 0
    replaced = 0
    while i < len(a) and j < len(b):
        ia, oa, ca = a[i]
        ib, ob, cb = b[j]
        if base[ia:ia + ca] == new[ib:ib + cb]:
            i += 1
            j += 1
            continue
        if (oa == sv.OP_LOAD and ob == sv.OP_ATOMIC_OR and cb == 7 and i + 2 < len(a) and ca == 4
                and a[i + 1][1] == sv.OP_BITWISE_OR and a[i + 2][1] == sv.OP_STORE):
            lt, lv, lp = base[ia + 1], base[ia + 2], base[ia + 3]
            o_at = a[i + 1][0]
            bit = base[o_at + 4] if base[o_at + 3] == lv else base[o_at + 3]
            s_at = a[i + 2][0]
            if (new[ib + 1] == lt and new[ib + 2] == lv and new[ib + 3] == lp and new[ib + 6] == bit
                    and base[s_at + 1] == lp and base[s_at + 2] == base[o_at + 2]):
                replaced += 1
                i += 3
                j += 1
                continue
        return False, replaced
    return i == len(a) and j == len(b), replaced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('exe')
    ap.add_argument('out')
    ap.add_argument('--workers', type=int, default=4)
    args = ap.parse_args()
    check_halt()
    with open(T1, encoding='ascii') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        rows_all = [dict(zip(hdr, line.rstrip('\n').split('\t'))) for line in f if line.strip()]
    rows = [r for r in rows_all if r['row'] == 'A' and r['outcome'] != 'HARNESS_UNSUPPORTED' and r['perm'] != '-']
    print('t1 rows', len(rows_all), 'A rows run', len(rows), 'stages', dict(collections.Counter(r['stage'] for r in rows)))

    def gcn_path(r):
        for arm in r['gcn_arms'].split(','):
            p = '%s/%s/%s_%s.bin' % (GCN_ROOT, arm, r['stage'], r['hash16'])
            if os.path.exists(p) and os.path.getsize(p) > 0:
                if sha256_file(p) != r['gcn_sha256']:
                    raise SystemExit('GCN sha mismatch ' + p)
                return p
        raise SystemExit('no GCN for ' + r['hash16'])

    def run(r):
        check_halt()
        rid = '%s_%s_%s_%s' % (r['stage'], r['hash16'], r['key16'], r['perm'])
        work = '%s/rows/%s' % (args.out, rid)
        os.makedirs(work, exist_ok=True)
        out_spv, f20_spv, so = work + '/out.spv', work + '/f20.spv', work + '/stdout.txt'
        if not (os.path.exists(out_spv) and os.path.exists(f20_spv) and os.path.exists(so)):
            cache = '%s/%s_%s_%s.bin' % (CACHE_CUR, r['stage'], r['hash16'], r['key16'])
            if sha256_file(cache) != r['cache_sha256']:
                raise SystemExit('cache sha mismatch ' + cache)
            env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
            env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (gcn_path(r), cache, out_spv, r['perm'])
            env['KYTY_RECOMPILE_F20'] = f20_spv
            p = subprocess.run([args.exe], cwd=work, env=env, capture_output=True, timeout=180)
            open(work + '/stderr.txt', 'wb').write(p.stderr)
            open(work + '/rc.txt', 'w').write('%d\n' % p.returncode)
            open(so, 'wb').write(p.stdout)
        rc = int(open(work + '/rc.txt').read().strip()) if os.path.exists(work + '/rc.txt') else -1
        m = LINE.search(open(so, 'rb').read())
        res = {'rid': rid, 'rc': rc, 'line': m is not None}
        if m:
            res.update(zip(('bound', 'named', 'sites', 'rewritten', 'unmatched', 'malformed'),
                           (int(x) for x in m.groups())))
        base = sv.read_spv(out_spv) if os.path.exists(out_spv) else None
        new = sv.read_spv(f20_spv) if os.path.exists(f20_spv) else None
        if base is not None and new is not None:
            sb, sn = sv.scan(base), sv.scan(new)
            res.update(py_named=sb['named'], py_bound_dec=sb['bound_dec'], py_triples=sb['triples'],
                       py_loads_out=sb['loads_fb'] - sb['triples'], py_triples_after=sn['triples'],
                       py_atomic_or_after=sn['atomics_or'], py_atomic_or_before=sb['atomics_or'])
            if res.get('rewritten', 0) > 0:
                res['diff_ok'], res['diff_replaced'] = diff_ok(base, new)
                for name, path in (('val_f20', f20_spv), ('val_base', out_spv)):
                    check_halt()
                    v = subprocess.run([SPIRV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout',
                                        path], capture_output=True)
                    res[name] = v.returncode
                    open(work + '/%s.txt' % name, 'wb').write(v.stdout + v.stderr)
            res['sha_base'] = sha256_file(out_spv)
            res['sha_f20'] = sha256_file(f20_spv)
        return res

    results = []
    halted = None
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run, r) for r in rows]
        for fu in cf.as_completed(futs):
            try:
                results.append(fu.result())
            except Halt as h:
                halted = str(h)
                for g in futs:
                    g.cancel()
    if halted:
        print('HALT', halted, 'rows done', len(results))
        sys.exit(5 if halted == 'LOCK' else 4)
    results.sort(key=lambda x: x['rid'])
    cols = ['rid', 'rc', 'bound', 'named', 'sites', 'rewritten', 'unmatched', 'malformed', 'py_named', 'py_bound_dec',
            'py_triples', 'py_loads_out', 'py_triples_after', 'py_atomic_or_before', 'py_atomic_or_after', 'diff_ok',
            'diff_replaced', 'val_f20', 'val_base', 'sha_base', 'sha_f20']
    with open(args.out + '/corpus_f42b.tsv', 'w', encoding='ascii', newline='\n') as f:
        f.write('\t'.join(cols) + '\n')
        for res in results:
            f.write('\t'.join(str(res.get(c, '')) for c in cols) + '\n')
    s = collections.Counter()
    bad = collections.defaultdict(list)
    for res in results:
        s['rows'] += 1
        if res['rc'] != 0 or not res['line']:
            bad['rc_or_line'].append(res['rid'])
            continue
        s['bound'] += res['bound']
        s['named'] += res['named'] > 0
        s['sites'] += res['sites']
        s['rewritten'] += res['rewritten']
        s['unmatched'] += res['unmatched']
        s['py_triples'] += res['py_triples']
        s['py_triples_after'] += res['py_triples_after']
        s['py_loads_out'] += res['py_loads_out']
        s['py_atomic_or_after'] += res['py_atomic_or_after'] - res['py_atomic_or_before']
        s['rows_rewritten'] += res['rewritten'] > 0
        if res['rewritten'] != res['py_triples']:
            bad['rewritten != python triples'].append(res['rid'])
        if res['py_triples_after'] != 0:
            bad['triples after rewrite'].append(res['rid'])
        if res['unmatched'] != 0:
            bad['unmatched'].append(res['rid'])
        if res['bound'] != (1 if res['named'] > 0 else 0):
            bad['bound != named'].append(res['rid'])
        if res['py_named'] != res['named']:
            bad['python named != C++ named'].append(res['rid'])
        if res['rewritten'] > 0:
            if not res.get('diff_ok'):
                bad['diff wider than triples'].append(res['rid'])
            if res.get('diff_replaced') != res['rewritten']:
                bad['diff replaced != rewritten'].append(res['rid'])
            if res.get('val_f20') != 0:
                bad['spirv-val f20'].append(res['rid'])
            s['val_base_fail'] += res.get('val_base') != 0
    lines = ['rows %d rc0+line %d' % (s['rows'], s['rows'] - len(bad.get('rc_or_line', []))),
             'modules_bound %d modules(named) %d sites %d rewritten %d unmatched %d' % (
                 s['bound'], s['named'], s['sites'], s['rewritten'], s['unmatched']),
             'independent count: triples before %d, after %d, loads outside a triple %d, OpAtomicOr added %d' % (
                 s['py_triples'], s['py_triples_after'], s['py_loads_out'], s['py_atomic_or_after']),
             'rows rewritten %d; spirv-val of their base (control) failing %d' % (s['rows_rewritten'],
                                                                                 s['val_base_fail'])]
    for k, v in sorted(bad.items()):
        lines.append('BAD %s: %d %s' % (k, len(v), ' '.join(v[:8])))
    ok = not bad and s['rewritten'] == s['py_triples'] and s['py_triples_after'] == 0 and s['unmatched'] == 0 \
        and s['bound'] == s['named']
    lines.append('ALL OK' if ok else 'FAIL')
    text = '\n'.join(lines) + '\n'
    open(args.out + '/corpus_f42b.txt', 'w', encoding='ascii', newline='\n').write(text)
    sys.stdout.write(text)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
