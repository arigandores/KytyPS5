"""S7 supplement (executor variant, not the base): KYTY_CFG_BENCH (decode + CFG build + structurize) on every
GCN dump of the corpus, twice in separate processes; graph_hash equality = determinism of the CFG stage.
Covers the VS/MS shaders the KYTY_RECOMPILE harness cannot take (HARNESS_UNSUPPORTED). ASCII output only.
Rule 27: lock/STOP checked before each process."""
import collections
import concurrent.futures as cf
import hashlib
import os
import re
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/s288/s7')
import t1_s7  # noqa: E402

S7 = t1_s7.S7


def bench(path, work):
    t1_s7.check_halt()
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_CFG_BENCH'] = path
    p = subprocess.run([t1_s7.BIN], cwd=work, env=env, capture_output=True, timeout=300)
    m = re.search(rb' ok=(\d) failure=([^\r\n]*)', p.stdout)
    g = re.search(rb'graph_hash=([0-9a-f]{16})', p.stdout)
    return (p.returncode, int(m.group(1)) if m else None, m.group(2).decode('latin1').strip() if m else '',
            g.group(1).decode() if g else None, len(t1_s7.UNIMPL_RE.findall(p.stdout + p.stderr)))


def main():
    shaders, conflicts = t1_s7.gcn_inventory()
    assert not conflicts
    work = S7 + '/work/bench_all'
    os.makedirs(work, exist_ok=True)
    items = sorted(shaders.items())
    res = {}
    try:
        for passname in ('A', 'B'):
            with cf.ThreadPoolExecutor(max_workers=6) as ex:
                futs = {ex.submit(bench, s['path'], work): name for name, s in items}
                for f in cf.as_completed(futs):
                    res[(futs[f], passname)] = f.result()
    except t1_s7.Halt as h:
        print('HALT', h)
        sys.exit(5 if str(h) == 'LOCK' else 4)
    lines = ['stage\thash16\tgcn_words\tgcn_sha256\trc_a\tok_a\tfailure_a\tgraph_hash_a\trc_b\tok_b\tgraph_hash_b\tunimpl\tdet_equal\tbench_outcome']
    cnt = collections.Counter()
    for name, s in items:
        a, b = res[(name, 'A')], res[(name, 'B')]
        if a[0] != 0 or b[0] != 0:
            o = 'BENCH_EXIT'
        elif a[1] != 1 or b[1] != 1:
            o = 'CFG_FAIL'
        elif a[4] or b[4]:
            o = 'UNIMPL'
        elif a[3] != b[3]:
            o = 'NONDET'
        else:
            o = 'CFG_OK'
        cnt[(s['stage'], o)] += 1
        lines.append('\t'.join([s['stage'], s['hash'], str(s['words']), s['sha'], str(a[0]), str(a[1]), a[2], str(a[3]),
                                str(b[0]), str(b[1]), str(b[3]), str(a[4] + b[4]), str(int(a[3] == b[3])), o]))
    out = S7 + '/t1_bench.tsv'
    with open(out, 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('t1_bench.tsv rows', len(lines) - 1, 'sha256', hashlib.sha256(open(out, 'rb').read()).hexdigest())
    for k, v in sorted(cnt.items()):
        print('  %s %-10s %d' % (k[0], k[1], v))


if __name__ == '__main__':
    main()
