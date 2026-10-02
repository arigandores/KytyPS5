"""Track S, link S7 (HPP-319): corpus T1 - offline translation of the GCN collected by the G arms of S4.

ROADMAP p.241(i) (20b39318), S0 section 5, RC14 of S1. No game. ASCII output only.

Rows of the outcome table (one outcome per row; the denominator is the number of rows):
  A  GCN dump + translation cache file of the CURRENT signature (= signature of the tests binary):
     one row per (file, permutation); KYTY_RECOMPILE twice in two separate processes (pass A, then
     pass B), spirv-val --target-env vulkan1.3 on pass A, identity against the stored SPIR-V.
     Outcomes by precedence: HARNESS_UNSUPPORTED > EXIT > UNIMPL > VAL_FAIL > NONDET > STORED_DIFF > OK.
  B  GCN dump without a current-signature file: KYTY_CFG_BENCH (parse + CFG only) -> NO_CACHE_FILE.
  C  current-signature file whose shader hash has no GCN dump: one row per permutation -> NO_GCN.
  D  translation files of other signatures in snap0 (read only) -> OLD_SIGNATURE (counted, not run).
Executor variant (separate table t1_alt.tsv, not in the base): rows B recompiled with the 699c1e4b
file(s) (signature of 9235a7ac, the binary of the G arms) - identity there is not meaningful.

Rule 27: before every process the lock C:/kyty/SEALED_RUN.lock and C:/kyty/s288/STOP are checked;
found -> stop launching, keep finished rows (results.jsonl), exit 5 / 4. Re-run resumes.
"""
import argparse
import collections
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
ARMS = ['g_1', 'g_2', 'g_3_0']
CACHE_CUR = S7 + '/cache_cur'
CACHE_ROOT = S7 + '/cache_root'
SNAP0 = 'C:/kyty/s288/snap0/ShaderCache_PPSA21564'
BIN = S7 + '/bin/shader_cfg_tests_949f8e51.exe'
SPIRV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
CUR_SIG = 'KytySC3:56189185f9e9f9a0ea5174f3f85206e6d099db3d:robust:ftz:cbank:fixb26:fixb1b'
G_SIG = 'KytySC3:699c1e4b7db359067b461e029b913c4b6e78dc90:robust:ftz:cbank'
UNIMPL_RE = re.compile(rb'opcode is not implemented|unsupported decoded instruction', re.I)
UNSUP_RE = re.compile(rb'unsupported stage/static state|vertex fetch/clip/mesh state is not supported|'
                      rb'pixel static state too short')
FNAME_RE = re.compile(r'^(vs|ps|cs|ms|ls|hs|ds|xx)_([0-9a-f]{16})(?:_([0-9a-f]{16}))?\.bin$')
TIMEOUT = 180
# spirv-val forms: 'val' - the letter of S0 section 5 (no flags); 'valvk' - the in-game validator target
# (SPV_ENV_VULKAN_1_3, pipelineCache.cpp ValidateShaderSpirv); 'valdev' - executor variant: the device
# features the emulator enables (uniformBufferStandardLayout, vulkanWindow.cpp:705; log line 74 of log_g_1).
VAL_FORMS = [('val', []), ('valvk', ['--target-env', 'vulkan1.3']),
             ('valdev', ['--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout'])]


EMPTY = []


class Halt(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def signature_of(path):
    with open(path, 'rb') as f:
        head = f.read(512)
    return head.split(b'\n', 1)[0].decode('latin1')


def check_halt():
    if os.path.exists(STOP):
        raise Halt('STOP')
    if os.path.exists(LOCK):
        raise Halt('LOCK')


def gcn_inventory():
    """Union of the G-arm dumps; same name must carry the same bytes."""
    shaders = {}
    conflicts = []
    for arm in ARMS:
        d = os.path.join(GCN_ROOT, arm)
        for name in sorted(os.listdir(d)):
            m = FNAME_RE.match(name)
            if not m or m.group(3):
                continue
            path = d + '/' + name
            sha = sha256_file(path)
            words = os.path.getsize(path) // 4
            if words == 0:
                # an empty dump (file created, code not written) is not a corpus member
                EMPTY.append(arm + '/' + name)
                continue
            if name in shaders:
                if shaders[name]['sha'] != sha:
                    conflicts.append(name)
                shaders[name]['arms'].append(arm)
            else:
                shaders[name] = {'stage': m.group(1), 'hash': m.group(2), 'path': path, 'sha': sha,
                                 'words': words, 'arms': [arm]}
    return shaders, conflicts


def cache_index(d):
    out = []
    for name in sorted(os.listdir(d)):
        m = FNAME_RE.match(name)
        if not m or not m.group(3):
            continue
        path = d + '/' + name
        out.append({'name': name, 'stage': m.group(1), 'hash': m.group(2), 'key': m.group(3),
                    'path': path, 'sig': signature_of(path), 'sha': sha256_file(path)})
    return out


def run_proc(env_extra, cwd, timeout=TIMEOUT):
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('KYTY_'):
            del env[k]
    env.update(env_extra)
    t0 = time.time()
    try:
        p = subprocess.run([BIN], cwd=cwd, env=env, capture_output=True, timeout=timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = 'timeout', e.stdout or b'', e.stderr or b''
    return rc, out, err, time.time() - t0


def perm_count(gcn_path, cache_path, work):
    rc, out, err, _ = run_proc({'KYTY_RECOMPILE': '%s;%s;%s;999' % (gcn_path, cache_path, work + '/probe.spv')}, work)
    m = re.search(rb'permutation 999 of (\d+)', err)
    if m:
        return int(m.group(1)), None
    first = (err.strip().split(b'\n') or [b''])[0][:200].decode('latin1')
    return None, 'rc=%s %s' % (rc, first)


def first_line(b):
    for line in b.replace(b'\r', b'').split(b'\n'):
        line = line.strip()
        if line:
            return line[:200].decode('latin1').replace('\t', ' ')
    return ''


class Store:
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.rows = {}
        if os.path.exists(path):
            with open(path, encoding='ascii') as f:
                for line in f:
                    r = json.loads(line)
                    self.rows[r['id']] = r

    def put(self, r):
        with self.lock:
            self.rows[r['id']] = r
            with open(self.path, 'a', encoding='ascii') as f:
                f.write(json.dumps(r, sort_keys=True) + '\n')


def do_recompile(job, passname, store, workroot):
    rid = job['id'] + '|' + passname
    if rid in store.rows:
        return
    check_halt()
    work = '%s/%s/%s' % (workroot, passname, job['id'].replace('|', '_'))
    os.makedirs(work, exist_ok=True)
    spv = work + '/out.spv'
    if os.path.exists(spv):
        os.remove(spv)
    rc, out, err, wall = run_proc({'KYTY_RECOMPILE': '%s;%s;%s;%d' % (job['gcn'], job['cache'], spv, job['perm'])}, work)
    both = out + b'\n' + err
    r = {'id': rid, 'rc': rc, 'wall': round(wall, 3), 'unimpl': len(UNIMPL_RE.findall(both)),
         'unsup': 1 if UNSUP_RE.search(err) else 0, 'err1': first_line(err), 'out1': first_line(out)}
    m = re.search(rb'identical=(\d)', out)
    r['identical'] = int(m.group(1)) if m else None
    if os.path.exists(spv) and rc == 0:
        data = open(spv, 'rb').read()
        r['spv_sha'] = sha256_bytes(data)
        r['spv_words'] = len(data) // 4
        if passname == 'A':
            for tag, flags in VAL_FORMS:
                v = subprocess.run([SPIRV_VAL] + flags + [spv], capture_output=True)
                r[tag + '_rc'] = v.returncode
                r[tag + '1'] = first_line(v.stderr + v.stdout)
    else:
        r['spv_sha'] = None
    with open(work + '/stdout.txt', 'wb') as f:
        f.write(out)
    with open(work + '/stderr.txt', 'wb') as f:
        f.write(err)
    store.put(r)


def do_bench(job, store, workroot):
    rid = job['id'] + '|BENCH'
    if rid in store.rows:
        return
    check_halt()
    work = '%s/bench/%s' % (workroot, job['id'].replace('|', '_'))
    os.makedirs(work, exist_ok=True)
    rc, out, err, wall = run_proc({'KYTY_CFG_BENCH': job['gcn']}, work)
    m = re.search(rb' ok=(\d) failure=([^\r\n]*)', out)
    r = {'id': rid, 'rc': rc, 'wall': round(wall, 3), 'bench_ok': int(m.group(1)) if m else None,
         'bench_failure': m.group(2)[:200].decode('latin1').strip() if m else first_line(err),
         'unimpl': len(UNIMPL_RE.findall(out + err))}
    store.put(r)


def classify(a, b, current, val='val'):
    """Outcome of one recompile row from pass A and pass B."""
    if a['unsup']:
        return 'HARNESS_UNSUPPORTED'
    if a['rc'] != 0 or b['rc'] != 0:
        return 'EXIT'
    if a['unimpl'] or b['unimpl']:
        return 'UNIMPL'
    if a.get(val + '_rc') != 0:
        return 'VAL_FAIL'
    if a['spv_sha'] != b['spv_sha']:
        return 'NONDET'
    if current and a.get('identical') != 1:
        return 'STORED_DIFF'
    return 'OK'


def run_pool(fn, jobs, workers):
    halted = None
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(fn, j) for j in jobs]
        for f in cf.as_completed(futs):
            try:
                f.result()
            except Halt as h:
                halted = str(h)
                for g in futs:
                    g.cancel()
    return halted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--plan-only', action='store_true')
    args = ap.parse_args()
    t_start = time.time()

    shaders, conflicts = gcn_inventory()
    cur = cache_index(CACHE_CUR)
    snap = cache_index(SNAP0)
    root = cache_index(CACHE_ROOT)
    bad_cur = [c['name'] for c in cur if c['sig'] != CUR_SIG]
    print('gcn empty dumps (not members)', len(EMPTY), EMPTY)
    print('gcn files unique', len(shaders), 'conflicts', len(conflicts),
          'by stage', dict(collections.Counter(s['stage'] for s in shaders.values())))
    print('cache_cur files', len(cur), 'not current signature', len(bad_cur))
    print('snap0 files', len(snap), 'signatures', dict(collections.Counter(c['sig'][:16] for c in snap)))
    print('cache_root files', len(root), 'signatures', dict(collections.Counter(c['sig'][:16] for c in root)))
    if conflicts or bad_cur:
        print('ABORT: conflicts or wrong signature in cache_cur')
        sys.exit(2)

    cur_by_hash = collections.defaultdict(list)
    for c in cur:
        cur_by_hash[c['hash']].append(c)
    g_by_hash = collections.defaultdict(dict)
    for c in snap + root:
        if c['sig'] == G_SIG:
            g_by_hash[c['hash']].setdefault(c['name'], c)
    gcn_by_hash = collections.defaultdict(list)
    for s in shaders.values():
        gcn_by_hash[s['hash']].append(s)

    store = Store(S7 + '/results.jsonl')
    workroot = S7 + '/work'
    os.makedirs(workroot, exist_ok=True)

    # permutation counts (cheap probe, one process per file)
    probe_dir = workroot + '/probe'
    os.makedirs(probe_dir, exist_ok=True)
    perms = {}
    perm_path = S7 + '/perms.json'
    if os.path.exists(perm_path):
        perms = json.load(open(perm_path))
    probe_items = []
    for h, files in cur_by_hash.items():
        any_gcn = gcn_by_hash[h][0]['path'] if gcn_by_hash.get(h) else None
        for c in files:
            probe_items.append((c, any_gcn))
    for h, files in g_by_hash.items():
        if h in cur_by_hash or not gcn_by_hash.get(h):
            continue
        for c in files.values():
            probe_items.append((c, gcn_by_hash[h][0]['path']))
    dummy = probe_dir + '/empty.bin'
    open(dummy, 'wb').write(b'\0\0\0\0')
    lock = threading.Lock()

    def probe(item):
        c, g = item
        if c['path'] in perms:
            return
        check_halt()
        n, err = perm_count(g or dummy, c['path'], probe_dir + '/' + c['name'][:-4])
        with lock:
            perms[c['path']] = n if n is not None else ('ERR ' + err)

    for c, _ in probe_items:
        os.makedirs(probe_dir + '/' + c['name'][:-4], exist_ok=True)
    halted = run_pool(probe, probe_items, args.workers)
    json.dump(perms, open(perm_path, 'w'), indent=0, sort_keys=True)
    if halted:
        print('HALT', halted, 'during probe')
        sys.exit(5 if halted == 'LOCK' else 4)

    jobs_a, jobs_alt, bench_jobs, rows_c = [], [], [], []
    for name, s in sorted(shaders.items()):
        files = cur_by_hash.get(s['hash'], [])
        if files:
            for c in files:
                n = perms[c['path']]
                if not isinstance(n, int):
                    jobs_a.append({'id': 'A|%s|%s|probe' % (s['hash'], c['key']), 'gcn': s['path'], 'cache': c['path'],
                                   'perm': 0, 's': s, 'c': c, 'probe_err': n})
                    continue
                for p in range(n):
                    jobs_a.append({'id': 'A|%s|%s|%d' % (s['hash'], c['key'], p), 'gcn': s['path'], 'cache': c['path'],
                                   'perm': p, 's': s, 'c': c})
        else:
            bench_jobs.append({'id': 'B|%s|%s' % (s['stage'], s['hash']), 'gcn': s['path'], 's': s})
            for c in g_by_hash.get(s['hash'], {}).values():
                n = perms.get(c['path'])
                if not isinstance(n, int):
                    continue
                for p in range(n):
                    jobs_alt.append({'id': 'X|%s|%s|%d' % (s['hash'], c['key'], p), 'gcn': s['path'], 'cache': c['path'],
                                     'perm': p, 's': s, 'c': c})
    for h, files in sorted(cur_by_hash.items()):
        if h in gcn_by_hash:
            continue
        for c in files:
            n = perms.get(c['path'])
            rows_c.append((c, n))
    print('jobs: A rows', len(jobs_a), 'bench', len(bench_jobs), 'alt rows', len(jobs_alt), 'C files', len(rows_c))
    if args.plan_only:
        return

    for passname in ('A', 'B'):
        halted = run_pool(lambda j: do_recompile(j, passname, store, workroot), jobs_a + jobs_alt, args.workers)
        if halted:
            print('HALT', halted, 'during pass', passname)
            sys.exit(5 if halted == 'LOCK' else 4)
    halted = run_pool(lambda j: do_bench(j, store, workroot), bench_jobs, args.workers)
    if halted:
        print('HALT', halted, 'during bench')
        sys.exit(5 if halted == 'LOCK' else 4)

    # ---- table
    hdr = ['row', 'stage', 'hash16', 'key16', 'perm', 'gcn_words', 'gcn_sha256', 'gcn_arms', 'cache_sig', 'cache_sha256',
           'rc_a', 'rc_b', 'err_first_line', 'unimpl_lines', 'rc_spirv_val', 'rc_spirv_val_vk13', 'rc_spirv_val_dev',
           'spv_sha256_a', 'spv_sha256_b', 'det_equal', 'identical_stored', 'outcome', 'outcome_dev']
    lines = ['\t'.join(hdr)]
    alt_lines = ['\t'.join(hdr)]
    counts = collections.Counter()
    counts_dev = collections.Counter()
    alt_counts = collections.Counter()
    alt_counts_dev = collections.Counter()
    key_outcomes = collections.defaultdict(set)

    def add(table, cnt, cnt_dev, vals):
        assert len(vals) == len(hdr), (len(vals), vals)
        table.append('\t'.join(vals))
        cnt[vals[-2]] += 1
        cnt_dev[vals[-1]] += 1

    def rec_row(j, table, cnt, cnt_dev, current):
        s, c = j['s'], j['c']
        if 'probe_err' in j:
            outcome = 'HARNESS_UNSUPPORTED' if 'unsupported' in j['probe_err'] else 'EXIT'
            vals = ['A', s['stage'], s['hash'], c['key'], '-', str(s['words']), s['sha'], ','.join(s['arms']),
                    c['sig'].split(':')[1][:8], c['sha'], '-', '-', j['probe_err']] + ['-'] * 8 + [outcome, outcome]
        else:
            a = store.rows[j['id'] + '|A']
            b = store.rows[j['id'] + '|B']
            outcome = classify(a, b, current)
            outcome_dev = classify(a, b, current, 'valdev')
            vals = [j['id'][0], s['stage'], s['hash'], c['key'], str(j['perm']), str(s['words']), s['sha'],
                    ','.join(s['arms']), c['sig'].split(':')[1][:8], c['sha'], str(a['rc']), str(b['rc']),
                    a['err1'] or a.get('val1', '') or '', str(a['unimpl'] + b['unimpl']), str(a.get('val_rc', '-')),
                    str(a.get('valvk_rc', '-')), str(a.get('valdev_rc', '-')),
                    str(a['spv_sha']), str(b['spv_sha']), str(int(a['spv_sha'] == b['spv_sha'])),
                    str(a['identical']), outcome, outcome_dev]
        add(table, cnt, cnt_dev, vals)
        return outcome

    for j in jobs_a:
        o = rec_row(j, lines, counts, counts_dev, True)
        key_outcomes[(j['s']['stage'], j['s']['hash'], j['perm'])].add(o)
    for j in bench_jobs:
        s = j['s']
        r = store.rows[j['id'] + '|BENCH']
        vals = ['B', s['stage'], s['hash'], '-', '-', str(s['words']), s['sha'], ','.join(s['arms']), '-', '-',
                str(r['rc']), '-', 'bench ok=%s failure=%s' % (r['bench_ok'], r['bench_failure']), str(r['unimpl'])]
        add(lines, counts, counts_dev, vals + ['-'] * 7 + ['NO_CACHE_FILE', 'NO_CACHE_FILE'])
    for c, n in rows_c:
        nn = n if isinstance(n, int) else 1
        for p in range(nn):
            vals = ['C', c['stage'], c['hash'], c['key'], str(p) if isinstance(n, int) else '-', '-', '-', '-',
                    c['sig'].split(':')[1][:8], c['sha'], '-', '-', '' if isinstance(n, int) else str(n)]
            add(lines, counts, counts_dev, vals + ['-'] * 8 + ['NO_GCN', 'NO_GCN'])
    old = collections.Counter()
    for c in snap:
        if c['sig'] == CUR_SIG:
            continue
        sig8 = c['sig'].split(':')[1][:8]
        old[sig8] += 1
        vals = ['D', c['stage'], c['hash'], c['key'], '-', '-', '-', '-', sig8, c['sha'], '-', '-', '']
        add(lines, counts, counts_dev, vals + ['-'] * 8 + ['OLD_SIGNATURE', 'OLD_SIGNATURE'])
    for j in jobs_alt:
        rec_row(j, alt_lines, alt_counts, alt_counts_dev, False)

    with open(S7 + '/t1_base.tsv', 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    with open(S7 + '/t1_alt.tsv', 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(alt_lines) + '\n')
    total = sum(counts.values())
    print('tests binary', BIN, sha256_file(BIN))
    print('current signature', CUR_SIG)
    print('t1_base.tsv rows', total, 'sha256', sha256_file(S7 + '/t1_base.tsv'))
    for k in ['OK', 'EXIT', 'UNIMPL', 'VAL_FAIL', 'NONDET', 'STORED_DIFF', 'HARNESS_UNSUPPORTED', 'NO_GCN',
              'NO_CACHE_FILE', 'OLD_SIGNATURE']:
        print('  %-20s %5d   dev %5d' % (k, counts.get(k, 0), counts_dev.get(k, 0)))
    print('  old signatures in snap0', dict(old))
    multi = sum(1 for v in key_outcomes.values() if len(v) > 1)
    print('keys (stage,hash,perm) of rows A', len(key_outcomes), 'with >1 outcome over key16', multi)
    print('t1_alt.tsv rows', sum(alt_counts.values()), 'sha256', sha256_file(S7 + '/t1_alt.tsv'), dict(alt_counts),
          'dev', dict(alt_counts_dev))
    print('corpus does not contain registered but unused shaders (dump at first use, KYTY_DUMP_GCN=1 on 9235a7ac)')
    print('T1 does not catch a wrong picture: spirv-val without errors and identity are not correctness of the image')
    print('wall %.1f s' % (time.time() - t_start))


if __name__ == '__main__':
    main()
