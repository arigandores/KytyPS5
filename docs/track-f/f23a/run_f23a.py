"""F23a (HPP-578, ROADMAP s122 item 483(e)): driver of the worktree diagnostic binary (patch_f23a_wt.py on main
dd7c6b33) - resumable; meant to run under watch_f23a.py (the tree dies on the lock / a gate process / STOP).

  python run_f23a.py decode --set t1|eboot     real Decoder::DecodeProgram (KYTY_F23A_DECODE) over raw code files
  python run_f23a.py seldiag --variant normal|nowqm|predoff [--only HASH16]
                                               KYTY_RECOMPILE of the T1 A rows (t1_base.tsv) with KYTY_F23A_SELDIAG
  python run_f23a.py spvcheck --n N            same rows with and without KYTY_F23A_SELDIAG: out.spv identical?

Variants: normal = defaults; nowqm = KYTY_F23A_NOWQMFOLD=1 (positive control only); predoff = KYTY_PRED_ELIM=0
(upper bound: selects before PredicationElimination). Every KYTY_* of the parent environment is dropped first (form of
t1_s7.py run_proc).
"""
import argparse
import concurrent.futures as cf
import csv
import hashlib
import json
import os
import struct
import subprocess
import sys
import threading

sys.path.insert(0, 'C:/kyty/f287/f23a')
import gcn_f23a as G  # noqa: E402

D = 'C:/kyty/f287/f23a/'
BIN = D + 'build/shader_cfg_tests.exe'
CACHE_CUR = 'C:/kyty/s288/s7/cache_cur'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
NL = chr(10)
TAB = chr(9)


def halt():
    if os.path.exists(LOCK):
        print('LOCK - exit 3', flush=True)
        os._exit(3)
    if os.path.exists(STOP):
        print('STOP - exit 4', flush=True)
        os._exit(4)


def env_with(extra):
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('KYTY_'):
            del env[k]
    env.update(extra)
    return env


def decode(setname):
    tabs = G.load_tables('dd7c6b33')
    if setname == 't1':
        progs, _ = G.t1_programs()
        paths = [('F|' if G.walk(p['words'])[1] == 'FRONT_OK' else '') + p['path'] for p in progs.values()]
    else:
        progs, _ = G.eboot_programs()
        os.makedirs(D + 'eboot_text', exist_ok=True)
        paths = []
        for h, p in progs.items():
            fp = D + 'eboot_text/%s.bin' % h
            if not os.path.exists(fp):
                open(fp, 'wb').write(p['code'])
            paths.append(('F|' if G.walk(G.words_of(p['code']))[1] == 'FRONT_OK' else '') + fp)
    lst = D + 'dec_%s.list' % setname
    out = D + 'dec_%s.txt' % setname
    open(lst, 'w', encoding='utf-8', newline=NL).write(NL.join(paths) + NL)
    done = set()
    started = set()
    if os.path.exists(out):
        for line in open(out, encoding='utf-8', errors='replace'):
            if line.startswith('E '):
                done.add(int(line.split()[1]))
            elif line.startswith('P '):
                started.add(int(line.split()[1]))
    crashed = sorted(started - done)
    i = 0
    while i < len(paths):
        halt()
        if i in done or i in crashed:
            i += 1
            continue
        r = subprocess.run([BIN], env=env_with({'KYTY_F23A_DECODE': '%s;%s;%d' % (lst, out, i)}), capture_output=True,
                           timeout=1200)
        # re-read progress
        done = set()
        started = set()
        for line in open(out, encoding='utf-8', errors='replace'):
            if line.startswith('E '):
                done.add(int(line.split()[1]))
            elif line.startswith('P '):
                started.add(int(line.split()[1]))
        newcrash = sorted(started - done - set(crashed))
        if newcrash:
            k = newcrash[0]
            err = (r.stderr + r.stdout).decode('latin1', 'replace').strip().replace(NL, ' | ')[:600]
            with open(out, 'a', encoding='utf-8', newline=NL) as f:
                f.write('C %d rc=%s %s%s' % (k, r.returncode, err, NL))
            crashed.append(k)
            i = k + 1
        elif r.returncode != 0:
            print('decoder process rc', r.returncode, r.stderr[-400:], flush=True)
            return 2
        else:
            i = len(paths)
    print('decode', setname, 'programs', len(paths), 'done', len(done), 'crashed', len(crashed), flush=True)
    return 0


SNAP0 = 'C:/kyty/s288/snap0/ShaderCache_PPSA21564'


def cd_jobs():
    # Extension of the census (not the S7 A rows): T1 base rows C (current-signature file, no GCN dump) and D (snap0
    # files of other signatures) whose hash16 has no A row; code = the eboot .shader_text with that XXH3 (eboot_text/,
    # calibrated 331/331 on the dumps); one job per (hash, key, perm) row of the base.
    rows = list(csv.DictReader(open(G.T1_BASE, encoding='utf-8'), delimiter=TAB))
    a = set(r['hash16'] for r in rows if r['row'] == 'A')
    jobs = []
    seen = set()
    for r in rows:
        if r['row'] not in ('C', 'D') or r['hash16'] in a:
            continue
        h = r['hash16']
        gcn = D + 'eboot_text/%s.bin' % h
        cache = '%s/%s_%s_%s.bin' % (CACHE_CUR if r['row'] == 'C' else SNAP0, r['stage'], h, r['key16'])
        if not os.path.exists(gcn) or not os.path.exists(cache):
            continue
        perms = [int(r['perm'])] if r['perm'] not in ('-', '') else [0]
        for pm in perms:
            jid = '%s|%s|%s|%d' % (r['row'], h, r['key16'], pm)
            if jid in seen:
                continue
            seen.add(jid)
            jobs.append(dict(id=jid, hash=h, stage=r['stage'], key=r['key16'], perm=pm, gcn=gcn, cache=cache,
                             s7=r['outcome']))
    return jobs


def a_jobs(rowset='A'):
    if rowset == 'CD':
        return cd_jobs()
    progs, _ = G.t1_programs()
    rows = list(csv.DictReader(open(G.T1_BASE, encoding='utf-8'), delimiter=TAB))
    jobs = []
    for r in rows:
        if r['row'] != 'A':
            continue
        h = r['hash16']
        if h not in progs:
            continue
        cache = '%s/%s_%s_%s.bin' % (CACHE_CUR, r['stage'], h, r['key16'])
        jobs.append(dict(id='%s|%s|%s' % (h, r['key16'], r['perm']), hash=h, stage=r['stage'], key=r['key16'],
                         perm=int(r['perm']), gcn=progs[h]['path'], cache=cache, s7=r['outcome']))
    return jobs


def run_one(job, extra, workdir, spv_name='out.spv'):
    os.makedirs(workdir, exist_ok=True)
    spv = workdir + '/' + spv_name
    if os.path.exists(spv):
        os.remove(spv)
    e = {'KYTY_RECOMPILE': '%s;%s;%s;%d' % (job['gcn'], job['cache'], spv, job['perm'])}
    e.update(extra)
    try:
        r = subprocess.run([BIN], cwd=workdir, env=env_with(e), capture_output=True, timeout=300)
        rc, err = r.returncode, r.stderr
    except subprocess.TimeoutExpired:
        rc, err = 'timeout', b''
    sha = hashlib.sha256(open(spv, 'rb').read()).hexdigest() if os.path.exists(spv) else None
    first = ''
    for line in err.replace(b'\r', b'').split(b'\n'):
        if line.strip():
            first = line.strip()[:200].decode('latin1')
            break
    return rc, sha, first


def seldiag(variant, only, rowset='A'):
    extra = {'normal': {}, 'nowqm': {'KYTY_F23A_NOWQMFOLD': '1'}, 'predoff': {'KYTY_PRED_ELIM': '0'}}[variant]
    suffix = variant if rowset == 'A' else variant + '_cd'
    out = D + 'sel_%s.jsonl' % suffix
    status = D + 'sel_%s.status.jsonl' % suffix
    done = set()
    if os.path.exists(status):
        for line in open(status, encoding='utf-8'):
            done.add(json.loads(line)['id'])
    jobs = [j for j in a_jobs(rowset) if j['id'] not in done and (only is None or j['hash'] == only)]
    lock = threading.Lock()
    print('seldiag', variant, 'jobs', len(jobs), 'already', len(done), flush=True)

    def work(job):
        halt()
        e = dict(extra)
        wd = D + 'work/%s/%s' % (suffix, job['id'].replace('|', '_'))
        os.makedirs(wd, exist_ok=True)
        own = wd + '/sel.json'
        if os.path.exists(own):
            os.remove(own)
        # one diag file per process (parallel appends to one file interleaved - first run 19:32Z, discarded)
        e['KYTY_F23A_SELDIAG'] = own
        rc, sha, first = run_one(job, e, wd)
        rec = dict(id=job['id'], hash=job['hash'], stage=job['stage'], perm=job['perm'], rc=rc, spv_sha=sha,
                   err1=first, s7=job['s7'])
        line = open(own, encoding='utf-8').read() if os.path.exists(own) else ''
        with lock:
            if line:
                with open(out, 'a', encoding='utf-8', newline=NL) as f:
                    f.write(line if line.endswith(NL) else line + NL)
            with open(status, 'a', encoding='utf-8', newline=NL) as f:
                f.write(json.dumps(rec, sort_keys=True) + NL)
        return rec

    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(work, jobs))
    print('seldiag', variant, 'ran', len(res), 'rc0', sum(1 for r in res if r['rc'] == 0), flush=True)
    return 0


def spvcheck(n):
    jobs = [j for j in a_jobs() if j['s7'] == 'OK']
    step = max(1, len(jobs) // n)
    pick = jobs[::step][:n]
    ok = True
    for j in pick:
        halt()
        w = D + 'work/spvcheck/' + j['id'].replace('|', '_')
        rc0, s0, _ = run_one(j, {}, w, 'plain.spv')
        rc1, s1, _ = run_one(j, {'KYTY_F23A_SELDIAG': D + 'work/spvcheck/sel.jsonl'}, w, 'diag.spv')
        same = rc0 == 0 and rc1 == 0 and s0 == s1
        ok &= same
        print('%s %s rc %s/%s spv %s %s' % (j['stage'], j['id'], rc0, rc1, (s0 or '-')[:16], 'EQUAL' if same else 'DIFF'),
              flush=True)
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode')
    ap.add_argument('--set')
    ap.add_argument('--variant')
    ap.add_argument('--only')
    ap.add_argument('--n', type=int, default=12)
    ap.add_argument('--rows', default='A')
    a = ap.parse_args()
    halt()
    if a.mode == 'decode':
        return decode(a.set)
    if a.mode == 'seldiag':
        return seldiag(a.variant, a.only, a.rows)
    if a.mode == 'spvcheck':
        return spvcheck(a.n)
    return 2


if __name__ == '__main__':
    sys.exit(main())
