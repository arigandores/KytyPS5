"""S16d (HPP-608, ROADMAP s122 item 516(v)(1)-(12)): probe P-S16 - preparation and runs (no game, no lock).

    python s16d_run.py prep                      # manifest, catalogue, recipes, GCN from eboot.bin, inputs, jobs A and B1
    python s16d_run.py run A1 <shader_cfg_tests.exe> <tree>    # arm A, first process set (job order as written)
    python s16d_run.py run A2 <exe> <tree>       # arm A, second process set (reverse order) - determinism, item (v)(5)
    python s16d_run.py run B1 <exe> <tree>       # arm B, first stage of every recipe (PS / VS without PS / CS), KYTY_FIX_F19=1
    python s16d_run.py prepB2                    # arm B, VS after PS: start = cursor of the new translator (RC1)
    python s16d_run.py run B2 <exe> <tree>

Work folder (outside git): C:/kyty/s288/s16d/work - GCN of the game (gcn/), recipe input bytes (in/), jobs, results.
Every command first checks the lock C:/kyty/SEALED_RUN.lock and the STOP file C:/kyty/s288/STOP; a run is watched every
1.5 s: lock, STOP or a live procload.py process kill the child processes (exit 3 / 4 / 7, nothing written under a
foreign lock); a process silent for HANG_S seconds is killed and its current job is recorded as a hang.
"""
import collections
import hashlib
import json
import os
import struct
import subprocess
import sys
import time

import psutil

import s16d_lib as L

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
WORK = 'C:/kyty/s288/s16d/work'
TIMES = 'C:/kyty/s288/s16d/times.txt'
NPROC = 8
HANG_S = 180
COMPARATOR_N = 10


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def guard():
    if os.path.exists(LOCK):
        print('LOCKED - exit 3, nothing written')
        sys.exit(3)
    if os.path.exists(STOP):
        print('STOP - exit 4')
        sys.exit(4)


def times_line(text):
    with open(TIMES, 'a', encoding='utf-8', newline='\n') as f:
        f.write('%s %s\n' % (utc(), text))


def wpath(*parts):
    return os.path.join(WORK, *parts).replace(chr(92), '/')


# ------------------------------------------------------------------------------------------------ prep
def prep():
    guard()
    os.makedirs(wpath('gcn'), exist_ok=True)
    os.makedirs(wpath('in'), exist_ok=True)
    report = []
    msha, listed, ok, bad = L.verify_manifest()
    report.append('manifest sha256 %s listed %d ok %d bad %d' % (msha, listed, ok, len(bad)))
    files = sorted(x for x in os.listdir(L.CATALOG) if x.endswith('.bin') and x != 'pipelines.bin')
    cache = {}
    parse_fail = []
    sigs = collections.Counter()
    for name in files:
        try:
            c = L.parse_cache_file(os.path.join(L.CATALOG, name))
        except Exception as e:  # noqa: BLE001 - every failure is printed and voids the run
            parse_fail.append((name, str(e)))
            continue
        cache[name] = c
        sigs[c['sig']] += 1
    report.append('cache files %d parsed %d parse_fail %d permutations %d signatures %s' % (
        len(files), len(cache), len(parse_fail), sum(len(c['perms']) for c in cache.values()), dict(sigs)))
    sig, lay, recipes, end_ok = L.parse_recipes(os.path.join(L.CATALOG, 'pipelines.bin'))
    report.append('recipes %d end_ok %s signature %s layout %s' % (len(recipes), end_ok, sig.replace(chr(10), '|'), lay))
    progs, n_elf = L.eboot_programs()
    report.append('eboot sha256 %s elf_texts %d unique %d' % (L.sha256_file(L.EBOOT), n_elf, len(progs)))
    # stage descriptors
    missing_file = 0
    gcn_written = {}
    inputs = {}
    perm_manual = {}
    for rec in recipes:
        for st in rec['stages']:
            name = L.key_file_name(st['stage'], st['hash'], st['udc'], st['code_size'], st['state'])
            st['file'] = name
            c = cache.get(name)
            if c is None or (c['stage'], c['hash'], c['udc'], c['code_size'], c['state']) != (
                    st['stage'], st['hash'], st['udc'], st['code_size'], st['state']) or st['perm'] >= len(c['perms']):
                st['file_ok'] = False
                missing_file += 1
            else:
                st['file_ok'] = True
                st['manual'] = c['perms'][st['perm']]
                perm_manual[(name, st['perm'])] = st['manual']
            code = progs.get(st['hash'])
            st['in_eboot'] = code is not None
            st['fused'] = (not st['in_eboot']) and st['stage'] == 5
            if code is not None:
                if len(code) < st['code_size'] * 4:
                    st['in_eboot'] = False
                    st['short_text'] = True
                else:
                    gname = '%016x_%d.bin' % (st['hash'], st['code_size'])
                    if gname not in gcn_written:
                        with open(wpath('gcn', gname), 'wb') as f:
                            f.write(code[:st['code_size'] * 4])
                        gcn_written[gname] = hashlib.sha256(code[:st['code_size'] * 4]).hexdigest()
                    st['gcn'] = wpath('gcn', gname)
            sha = hashlib.sha256(st['info']).hexdigest()[:24]
            if sha not in inputs:
                with open(wpath('in', sha + '.bin'), 'wb') as f:
                    f.write(st['info'])
                inputs[sha] = len(st['info'])
            st['input'] = wpath('in', sha + '.bin')
            st['input_sha'] = sha
            del st['info']
    report.append('stage file missing %d gcn files %d input blobs %d' % (missing_file, len(gcn_written), len(inputs)))
    report.append('permutations referenced %d manual>0 %d manual counts %s' % (
        len(perm_manual), sum(1 for v in perm_manual.values() if v), dict(collections.Counter(perm_manual.values()))))
    # jobs of arm A: forms A0 and C per (file, perm, input), K per (file, perm)
    jobs = collections.OrderedDict()

    def job(arm, form, st, start='S', f19='-', corrupt='0'):
        inp = st['input'] if form in ('A0', 'C') else '-'
        k = (arm, form, st['file'], st['perm'], st['gcn'], inp, start, f19, corrupt)
        if k not in jobs:
            jobs[k] = '%s%d' % (arm.lower(), len(jobs))
        return jobs[k]

    for rec in recipes:
        for st in rec['stages']:
            st['jobsA'] = {}
            if not (st['file_ok'] and st['in_eboot']):
                continue
            for form in ('A0', 'K', 'C'):
                st['jobsA'][form] = job('A', form, st)
    # comparator control (item (v)(6)): the first COMPARATOR_N VS permutations with resources_num >= 1 by file name and
    # permutation index (chosen before data); stride (letter of the rule), format and one SPIR-V word (executor variant).
    vs_perms = sorted({(st['file'], st['perm']) for rec in recipes for st in rec['stages']
                       if st['stage'] == 1 and st['file_ok'] and st['in_eboot'] and cache[st['file']]['state'][3] >= 1})
    comp = vs_perms[:COMPARATOR_N]
    comparator = []
    for name, perm in comp:
        st = next(s for rec in recipes for s in rec['stages'] if s['file'] == name and s['perm'] == perm)
        comparator.append(dict(file=name, perm=perm, base=job('A', 'K', st),
                               stride=job('A', 'K', st, corrupt='stride'), format=job('A', 'K', st, corrupt='format'),
                               spirv=job('A', 'K', st, corrupt='spirv')))
    write_jobs('jobs_A.txt', jobs)
    # arm B phase 1: the first stage of the cursor chain of every recipe (PS of a graphics recipe with PS; VS of one
    # without; CS) for forms K and C, both F19 outcomes for a stage with a stored manual image.
    jobsB = collections.OrderedDict()

    def jobb(form, st, start, f19):
        inp = st['input'] if form == 'C' else '-'
        k = ('B', form, st['file'], st['perm'], st['gcn'], inp, str(start), f19, '0')
        if k not in jobsB:
            jobsB[k] = 'b%d' % len(jobsB)
        return jobsB[k]

    for rec in recipes:
        stages = rec['stages']
        rec['mesh'] = stages[0]['stage'] == 5 if rec['kind'] == 1 else False
        first = stages[1] if (rec['kind'] == 1 and len(stages) == 2) else stages[0]
        rec['first'] = 1 if first is not stages[0] else 0
        c0 = 6 if rec['mesh'] else 0
        for st in stages:
            st['jobsB1'] = {}
        if not all(s['file_ok'] and s['in_eboot'] for s in stages):
            continue
        for form in ('K', 'C'):
            variants = ['k16UNorm', 'k8UNorm'] if first.get('manual') else ['-']
            first['jobsB1'][form] = {v: jobb(form, first, c0, v) for v in variants}
    write_jobs('jobs_B1.txt', jobsB)
    meta = dict(report=report, sig=sig, layout=lay, recipes=recipes, comparator=comparator,
                manual={'%s#%d' % k: v for k, v in perm_manual.items()}, parse_fail=parse_fail,
                cache_sigs=dict(sigs), manifest=dict(sha=msha, listed=listed, ok=ok, bad=bad),
                gcn_sha=gcn_written, catalog_states={n: list(c['state']) for n, c in cache.items()},
                jobsB_index={'|'.join(map(str, k)): v for k, v in jobsB.items()})
    json.dump(meta, open(wpath('meta.json'), 'w'), indent=0)
    for line in report:
        print(line)
    print('jobs A %d (comparator %d perms) jobs B1 %d' % (len(jobs), len(comparator), len(jobsB)))


def write_jobs(name, jobs, only=None):
    lines = []
    for k, jid in jobs.items():
        if only is not None and jid not in only:
            continue
        arm, form, fname, perm, gcn, inp, start, f19, corrupt = k
        lines.append('J %s %s %s %s %d %s %s %s %s %s' % (jid, arm, form, L.CATALOG + '/' + fname, perm, gcn, inp, start,
                                                          f19, corrupt))
    with open(wpath(name), 'w', encoding='ascii', newline=chr(10)) as f:
        f.write(chr(10).join(lines) + chr(10))
    return len(lines)


def index_key(text):
    parts = text.split('|')
    return (parts[0], parts[1], parts[2], int(parts[3]), parts[4], parts[5], parts[6], parts[7], parts[8])


def prep_b2():
    guard()
    meta = json.load(open(wpath('meta.json')))
    res = parse_results(wpath('res_B1'))
    jobsB = collections.OrderedDict((index_key(k), v) for k, v in meta['jobsB_index'].items())
    n_new = 0

    def jobb(form, st, start, f19):
        nonlocal n_new
        inp = st['input'] if form == 'C' else '-'
        k = ('B', form, st['file'], st['perm'], st['gcn'], inp, str(start), f19, '0')
        if k not in jobsB:
            jobsB[k] = 'b%d' % len(jobsB)
            n_new += 1
        return jobsB[k]

    for rec in meta['recipes']:
        stages = rec['stages']
        for st in stages:
            st['jobsB2'] = {}
        if rec['kind'] != 1 or len(stages) != 2 or not all(s['file_ok'] and s['in_eboot'] for s in stages):
            continue
        vs, ps = stages[0], stages[1]
        c0 = 6 if rec['mesh'] else 0
        for form in ('K', 'C'):
            out = {}
            for v_ps, jid in ps['jobsB1'].get(form, {}).items():
                r = res.get(jid)
                if r is None or r.get('st') != 'OK':
                    continue
                s_ps = L.start_for(c0, int(r['dd']))
                cursor = L.advance(c0, s_ps, int(r['dd']))
                variants = ['k16UNorm', 'k8UNorm'] if vs.get('manual') else ['-']
                out[v_ps] = {v: jobb(form, vs, cursor, v) for v in variants}
            vs['jobsB2'][form] = out
    meta['jobsB_index'] = {'|'.join(map(str, k)): v for k, v in jobsB.items()}
    json.dump(meta, open(wpath('meta.json'), 'w'), indent=0)
    todo = {v for v in jobsB.values() if v not in res}
    n = write_jobs('jobs_B2.txt', jobsB, todo)
    print('jobs B2 new %d written %d' % (n_new, n))


# ------------------------------------------------------------------------------------------------ results
def parse_line(line):
    parts = line.split()
    d = {'_tag': parts[0], 'id': parts[1] if len(parts) > 1 else ''}
    for p in parts[2:]:
        if '=' in p:
            k, v = p.split('=', 1)
            d[k] = v
    return d


def parse_results(folder):
    """{job id: fields} over every out file of a run folder; a job begun without a result line gets st=CRASH with
    the last phase (T translate, E emit, V validate) or st=HANG."""
    res = {}
    if not os.path.isdir(folder):
        return res
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.out'):
            continue
        for line in open(os.path.join(folder, name), 'r', encoding='utf-8', errors='replace'):
            line = line.rstrip(chr(10))
            if line.startswith('R '):
                d = parse_line(line)
                res[d['id']] = d
            elif line.startswith('X '):
                d = parse_line(line)
                res[d['id']] = d
    return res


def header_lines(folder):
    out = []
    for name in sorted(os.listdir(folder)):
        if name.endswith('.out'):
            for line in open(os.path.join(folder, name), 'r', encoding='utf-8', errors='replace'):
                if line.startswith(('S ', 'K ')):
                    out.append(line.rstrip(chr(10)))
    return out


# ------------------------------------------------------------------------------------------------ run
def procload_alive(own):
    for p in psutil.process_iter(['pid', 'cmdline']):
        try:
            if p.info['pid'] in own:
                continue
            cmd = ' '.join(p.info['cmdline'] or [])
            if 'procload.py' in cmd:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def kill_tree(proc):
    try:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(proc.pid)], capture_output=True)
    except OSError:
        pass


def run(tag, exe, tree):
    guard()
    names = {'A1': 'jobs_A.txt', 'A2': 'jobs_A.txt', 'B1': 'jobs_B1.txt', 'B2': 'jobs_B2.txt', 'B3': 'jobs_B3.txt'}
    lines = [x for x in open(wpath(names[tag]), 'r', encoding='ascii').read().split(chr(10)) if x.startswith('J ')]
    if tag == 'A2':
        lines.reverse()
    folder = wpath('res_' + tag)
    os.makedirs(folder, exist_ok=True)
    # resume: jobs with a result line (R or X) from an earlier invocation are not run again
    have = parse_results(folder)
    n_all = len(lines)
    lines = [x for x in lines if x.split()[1] not in have]
    stamp = time.strftime('%H%M%S', time.gmtime())
    knobs = wpath('knobs_%s.txt' % tag)
    with open(knobs, 'w', encoding='ascii', newline='\n') as f:
        f.write(chr(10).join(L.knob_names(tree)) + chr(10))
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
    env['KYTY_S16D_KNOBS'] = knobs
    if tag.startswith('B'):
        env['KYTY_FIX_F19'] = '1'
    cwd = wpath('cwd_' + tag)
    os.makedirs(cwd, exist_ok=True)
    chunks = [lines[i::NPROC] for i in range(NPROC)]
    pending = {i: list(c) for i, c in enumerate(chunks) if c}
    procs = {}
    attempt = collections.Counter()
    t0 = time.time()
    own = {os.getpid()}

    def start(i):
        attempt[i] += 1
        jf = os.path.join(folder, 'c%s_%02d_%02d.jobs' % (stamp, i, attempt[i]))
        out = os.path.join(folder, 'c%s_%02d_%02d.out' % (stamp, i, attempt[i]))
        with open(jf, 'w', encoding='ascii', newline='\n') as f:
            f.write(chr(10).join(pending[i]) + chr(10))
        e = dict(env)
        e['KYTY_S16D_JOBS'] = jf
        e['KYTY_S16D_OUT'] = out
        p = subprocess.Popen([exe], cwd=cwd, env=e, stdout=subprocess.DEVNULL, stderr=open(out + '.err', 'wb'))
        own.add(p.pid)
        procs[i] = (p, out, time.time(), 0)

    for i in list(pending):
        start(i)
    while procs:
        time.sleep(1.5)
        trip = 'lock' if os.path.exists(LOCK) else 'STOP' if os.path.exists(STOP) else (
            'procload' if procload_alive(own) else None)
        if trip:
            for p, _, _, _ in procs.values():
                kill_tree(p)
            print('KILLED: %s %s' % (trip, utc()))
            if trip != 'lock':
                times_line('s16d run %s KILLED: %s' % (tag, trip))
            sys.exit({'lock': 3, 'STOP': 4, 'procload': 7}[trip])
        for i in list(procs):
            p, out, t_last, size = procs[i]
            cur = os.path.getsize(out) if os.path.exists(out) else 0
            if cur != size:
                procs[i] = (p, out, time.time(), cur)
                t_last = time.time()
            rc = p.poll()
            hung = rc is None and time.time() - t_last > HANG_S
            if rc is None and not hung:
                continue
            if hung:
                kill_tree(p)
                p.wait()
            del procs[i]
            # what finished in this attempt
            begun = None
            phase = None
            finished = set()
            for line in open(out, 'r', encoding='utf-8', errors='replace'):
                if line.startswith('B '):
                    begun = line.split()[1]
                    phase = None
                elif line.startswith('P '):
                    phase = line.split()[2]
                elif line.startswith('R '):
                    finished.add(line.split()[1])
            ids = [x.split()[1] for x in pending[i]]
            rest = [x for x in pending[i] if x.split()[1] not in finished]
            if begun is not None and begun not in finished:
                with open(out, 'a', encoding='ascii', newline='\n') as f:
                    f.write('X %s st=%s phase=%s rc=%s\n' % (begun, 'HANG' if hung else 'CRASH', phase or '-',
                                                              'hang' if hung else rc))
                rest = [x for x in rest if x.split()[1] != begun]
            done_all = len(rest) == 0
            pending[i] = rest
            if not done_all:
                if attempt[i] > 200:
                    print('chunk %d: too many restarts' % i)
                    continue
                start(i)
    wall = time.time() - t0
    res = parse_results(folder)
    n_total = n_all
    st = collections.Counter(r.get('st') for r in res.values())
    print('run %s: jobs %d results %d st %s wall %.1f s' % (tag, n_total, len(res), dict(st), wall))
    times_line('s16d run %s done: jobs %d results %d st %s wall %.1f s' % (tag, n_total, len(res), dict(st), wall))


def prep_b3():
    """Control-only jobs of the F19 stand (item 516(v)(7)): every permutation with a stored manual image whose recipes
    gave it no arm B job (all its recipes stopped earlier, e.g. a fused Mesh stage) gets both outcomes in both forms, the
    start of its recipe's first stage; the jobs count only for the stand control and f19_both, not for any recipe."""
    guard()
    meta = json.load(open(wpath('meta.json')))
    jobsB = collections.OrderedDict((index_key(k), v) for k, v in meta['jobsB_index'].items())
    covered = collections.defaultdict(set)
    for rec in meta['recipes']:
        for st in rec['stages']:
            key = '%s#%d' % (st['file'], st['perm'])
            for form in ('K', 'C'):
                if st.get('jobsB1', {}).get(form) or st.get('jobsB2', {}).get(form):
                    covered[key].add(form)
    control = {}
    for rec in meta['recipes']:
        for st in rec['stages']:
            key = '%s#%d' % (st['file'], st['perm'])
            if not st.get('manual') or key in control or covered[key] == {'K', 'C'} or not st.get('gcn'):
                continue
            c0 = 6 if rec.get('mesh') else 0
            control[key] = {}
            for form in ('K', 'C'):
                control[key][form] = {}
                for v in ('k16UNorm', 'k8UNorm'):
                    inp = st['input'] if form == 'C' else '-'
                    k = ('B', form, st['file'], st['perm'], st['gcn'], inp, str(c0), v, '0')
                    if k not in jobsB:
                        jobsB[k] = 'b%d' % len(jobsB)
                    control[key][form][v] = jobsB[k]
    meta['f19_control'] = control
    meta['jobsB_index'] = {'|'.join(map(str, k)): v for k, v in jobsB.items()}
    json.dump(meta, open(wpath('meta.json'), 'w'), indent=0)
    done = set(parse_results(wpath('res_B1'))) | set(parse_results(wpath('res_B2')))
    todo = {jid for d in control.values() for f in d.values() for jid in f.values() if jid not in done}
    n = write_jobs('jobs_B3.txt', jobsB, todo)
    print('F19 control permutations %d jobs B3 %d: %s' % (len(control), n, sorted(control)))


def main():
    cmd = sys.argv[1]
    if cmd == 'prep':
        prep()
    elif cmd == 'prepB2':
        prep_b2()
    elif cmd == 'prepB3':
        prep_b3()
    elif cmd == 'run':
        run(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        raise SystemExit('unknown command')


if __name__ == '__main__':
    main()
