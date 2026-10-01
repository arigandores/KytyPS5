"""rt144.py - Red Team, step 1 of s144 (HPP-331): own recount of the sealed tools of step 0 and checks on real logs.
Read only on the logs, the caches and the sealed files; writes only into C:/kyty/s144/step1 and the run scratch dir.
One long-lived process on purpose: procload.py of a track harness sees it (a child shorter than its 10 s span is not seen).
Parts: D1 the four suites (subprocess, first); D2 check-seal, regress143, regress142, calib, check1b, summary (in process);
A precache members on real logs; B profile 144 on real W logs (w143 -> w144_0N, w142 -> w144_00) by hard links;
C cache state now against the end of s143; E diffs of the ported files."""
import contextlib
import datetime
import difflib
import hashlib
import io
import json
import os
import re
import subprocess
import sys

NL = chr(10)
CR = chr(13)
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOPF = 'C:/kyty/s144/STOP'
S144 = 'C:/kyty/s144'
OUT = S144 + '/step1'
TIMES = OUT + '/times.txt'
SCR = (os.environ.get('PAPERCLIP_RUN_SCRATCH_DIR') or (OUT + '/scratch')).replace(chr(92), '/') + '/rt144'
CHUNK = 1 << 26


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def tline(s):
    with open(TIMES, 'a', encoding='utf-8') as f:
        f.write(utc() + ' ' + s + NL)


def guard(where):
    if os.path.exists(LOCK):
        tline('rt144 ABORT: the lock appeared before %s (%s)' % (where, open(LOCK, encoding='utf-8', errors='replace').read().strip()))
        sys.exit(3)
    if os.path.exists(STOPF):
        tline('rt144 ABORT: C:/kyty/s144/STOP before %s' % where)
        sys.exit(4)


def chain_shells():
    cmd = ['powershell', '-NoProfile', '-Command',
           r"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'bash.exe' -and $_.CommandLine -match 'go_s\.sh|go_f[0-9a-z]*\.sh|go_p[0-9a-z]*\.sh|go14[0-9]a\.sh' }).Count"]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip()


def put(name, text):
    p = OUT + '/' + name
    data = text.replace(NL, CR + NL).encode('ascii', 'replace')
    with open(p, 'wb') as f:
        f.write(data)
    return p, hashlib.sha256(data).hexdigest()


def main_out(S, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = S.main(argv)
    return rc, buf.getvalue()


RX_PRE = re.compile(rb'PipelinePrecache: \d+ recipes ->')
MEMBERS = (('pre_any', b'PipelinePrecache:'), ('seed', b'ShaderSeed:'), ('seed_compat', b'ShaderSeed: compatibility='),
           ('no_yet', b'PipelinePrecache: no '), ('stale', b'stale recipes'), ('saved', b'PipelinePrecache: saved'),
           ('allcreated', b'PipelinePrecache: all pipelines created'))


def members(path):
    r = dict(size=0, sha=None, pre_recipes=0, guest=None, err=None)
    for k, _ in MEMBERS:
        r[k] = 0
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    off = 0
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            h.update(b)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf
                    continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if whole:
                r['pre_recipes'] += len(RX_PRE.findall(whole))
                for k, m in MEMBERS:
                    r[k] += whole.count(m)
                if r['guest'] is None:
                    i = whole.find(b'GuestOut')
                    if i >= 0:
                        r['guest'] = off + i
                if r['err'] is None:
                    i = whole.find(b'--- Error ---')
                    if i >= 0:
                        r['err'] = off + i
                off += len(whole)
            if not b:
                break
    r['size'] = off
    r['sha'] = h.hexdigest()
    return r


def jinfo(jp):
    if not os.path.isfile(jp):
        return None, None
    js = json.load(open(jp, encoding='utf-8'))
    env = js.get('env') or {}
    cl = js.get('cmdline') or []
    val = None
    for i, a in enumerate(cl):
        if a == '--vulkan-validation' and i + 1 < len(cl):
            val = cl[i + 1]
    return env.get('KYTY_PIPELINE_PRECACHE', '<unset>'), val


def part_a():
    rows = ['PART A - precache members on real logs (counts of lines; json env KYTY_PIPELINE_PRECACHE; last --vulkan-validation)',
            'cols: tag | env | validation | log: recipes-> any PipelinePrecache: ShaderSeed: compat no-yet stale saved all-created | '
            'first GuestOut / first --- Error --- byte | stdout: recipes-> any ShaderSeed: | log sha256 size']
    shas = {}
    sets = [('C:/kyty/s143', ['v143_%02d' % i for i in range(1, 11)] + ['w143_%02d' % i for i in range(1, 11)]),
            ('C:/kyty/s142', ['v142', 'w142'] + ['c142_%02d' % i for i in range(1, 11)]),
            ('C:/kyty/f287/f2c', ['f2c_a', 'f2c_b', 'f2c_c']),
            ('C:/kyty/s288/s4', ['sw_m1', 'sw_m2'])]
    for root, tags in sets:
        for t in tags:
            guard('part A %s' % t)
            lg = members('%s/log_%s.txt' % (root, t))
            sd = members('%s/stdout_%s.txt' % (root, t))
            env, val = jinfo('%s/%s.json' % (root, t))
            if lg is None:
                rows.append('%s/%s | env %s | val %s | log MISSING' % (root, t, env, val))
                continue
            shas[t] = (lg['sha'], root)
            rows.append('%s/%s | env %s | val %s | log: %d %d %d %d %d %d %d %d | GuestOut %s Error %s | stdout: %s | %s %d' % (
                root, t, env, val, lg['pre_recipes'], lg['pre_any'], lg['seed'], lg['seed_compat'], lg['no_yet'], lg['stale'],
                lg['saved'], lg['allcreated'], lg['guest'], lg['err'],
                'MISSING' if sd is None else '%d %d %d' % (sd['pre_recipes'], sd['pre_any'], sd['seed']), lg['sha'], lg['size']))
    return rows, shas


def link(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    try:
        os.link(src, dst)
    except OSError:
        import shutil
        shutil.copyfile(src, dst)


def part_b(S, shas, seal_sha):
    rows = ['PART B - profile 144 on real W logs: w143_NN (precache by default, stopped at the start, s143) as w144_0N of the same '
            'level; w142 (Sky Garden, precache by default, held 310 s, s142) as the control w144_00. Root b1: the jsons as run; root '
            'b2: the same jsons with KYTY_PIPELINE_PRECACHE=0 added to env (what the W form member reads).']
    mp = [('w142', 'C:/kyty/s142', 'w144_00')] + [('w143_%02d' % n, 'C:/kyty/s143', 'w144_%02d' % k) for n, k in
                                                   ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (9, 7), (10, 8))]
    for rootname, add_env in (('b1', False), ('b2', True)):
        R = SCR + '/' + rootname
        os.makedirs(R + '/step2', exist_ok=True)
        tl = []
        for src, sroot, dst in mp:
            guard('part B %s %s' % (rootname, dst))
            js = json.load(open('%s/%s.json' % (sroot, src), encoding='utf-8'))
            if add_env:
                js['env'] = dict(js.get('env') or {}, KYTY_PIPELINE_PRECACHE='0')
            js['tag'] = dst
            json.dump(js, open('%s/%s.json' % (R, dst), 'w', encoding='utf-8'))
            for a, b in (('log_%s.txt', 'log_%s.txt'), ('stdout_%s.txt', 'stdout_%s.txt'), ('%s.stdout.txt', '%s.stdout.txt')):
                if os.path.isfile(sroot + '/' + a % src):
                    link(sroot + '/' + a % src, R + '/' + b % dst)
            tl.append('2026-10-01T00:00:00Z go144a %s enter_scene end rc 0 log_%s.txt sha256 %s' % (dst, dst, shas[src][0]))
        open(R + '/step2/times.txt', 'w', encoding='utf-8').write(NL.join(tl) + NL)
        for src, sroot, dst in mp:
            e = S.entry_of(dst, R, seal_sha)
            form = ['%s=%s(%s)' % (a[0].split('(')[0].strip(), 'ok' if a[1] else 'FAIL', a[2]) for a in e['admit']
                    if a[0].startswith('W form')]
            rows.append('%s %s <- %s: outcome %s; wkey %s; guestout %s; precache %s; form rows: %s' % (
                rootname, dst, src, e['outcome'], e['wkey'], e['guestout'], e['precache'], '; '.join(form)))
        for t in ('w144_01', 'w144_02', 'w144_03', 'w144_04'):
            stop, lines = S.stop_check144(t, R, seal_sha)
            rows.append('%s stop_check144(%s) -> %s' % (rootname, t, 'STOP rc 5' if stop else 'rc 0'))
            rows.extend('%s   %s' % (rootname, x) for x in lines)
    return rows


def load_mf(p):
    js = json.load(open(p, encoding='utf-8'))
    return dict(((x[0], x[1]), (x[2], x[3], x[4])) for x in js['files']), dict((x[0], bool(x[2])) for x in js['roots'])


def part_c():
    guard('part C')
    sys.path.insert(0, S144)
    import cachemf144 as CM
    rr, fr = CM.manifest(CM.default_roots())
    live = OUT + '/rt144_cache_now.json'
    json.dump(dict(taken_utc=utc(), roots=rr, files=fr), open(live, 'w', encoding='ascii'))
    rows = ['PART C - cache state now (cachemf144.manifest, %s, sha256 %s) against the end of s143 and the first s143 tag' % (
        live, sha(live))]
    a_files, a_roots = load_mf(live)
    for ref in ('C:/kyty/s143/runs143/cache_w143_10.after.json', 'C:/kyty/s143/runs143/cache_v143_01.before.json'):
        b_files, b_roots = load_mf(ref)
        rows.append('ref %s sha256 %s' % (ref, sha(ref)))
        for root in ('shader', 'pipeline', 'glcache'):
            fa = dict((k[1], v) for k, v in a_files.items() if k[0] == root)
            fb = dict((k[1], v) for k, v in b_files.items() if k[0] == root)
            add = sorted(set(fa) - set(fb))
            rem = sorted(set(fb) - set(fa))
            chg = sorted(k for k in set(fa) & set(fb) if fa[k][2] != fb[k][2])
            mt = sorted(k for k in set(fa) & set(fb) if fa[k][2] == fb[k][2] and fa[k][:2] != fb[k][:2])
            rows.append('  %s: now %d files, ref %d; added %d removed %d content-changed %d same-content-other-size/mtime %d; '
                        'present now %s ref %s' % (root, len(fa), len(fb), len(add), len(rem), len(chg), len(mt),
                                                   a_roots.get(root), b_roots.get(root)))
            if root != 'glcache':
                for k in (add[:15] + rem[:15] + chg[:15]):
                    rows.append('    %s %s now %s ref %s' % (root, k, fa.get(k), fb.get(k)))
        pb = [k for k in a_files if k[0] == 'shader' and k[1] == 'pipelines.bin']
        if pb:
            rows.append('  pipelines.bin now %s; ref %s' % (a_files[pb[0]], b_files.get(pb[0])))
    p = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/pipelines.bin'
    if os.path.isfile(p):
        head = open(p, 'rb').read(200)
        rows.append('pipelines.bin head (200 bytes, printable): %s' % ''.join(chr(c) if 32 <= c < 127 else '.' for c in head))
    return rows


def part_e():
    pairs = [('enter_scene.py', 'enter_scene.py'), ('fgcpu144.py', 'fgcpu143.py'), ('cachemf144.py', 'cachemf143.py'),
             ('lockcheck144.py', 'lockcheck143.py'), ('test_fgcpu144.py', 'test_fgcpu143.py'),
             ('test_tools144.py', 'test_tools143.py'), ('step2/next_one.sh', 'step2/next_one.sh'),
             ('step2/call_one.sh', 'step2/call_one.sh'), ('step2/wait_one.sh', 'step2/wait_one.sh'),
             ('procload.py', 'procload.py'), ('idle142.py', 'idle142.py'), ('sheet142.py', 'sheet142.py'),
             ('launch_run.py', 'launch_run.py'), ('run_safety99.py', 'run_safety99.py')]
    rows = ['PART E - diffs of the ported files s144 against s143 (changed lines only)']
    for a, b in pairs:
        pa, pb = S144 + '/' + a, 'C:/kyty/s143/' + b
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            rows.append('%s vs s143/%s: missing %s' % (a, b, pa if not os.path.isfile(pa) else pb))
            continue
        la = open(pa, encoding='utf-8', errors='replace').read().split(NL)
        lb = open(pb, encoding='utf-8', errors='replace').read().split(NL)
        d = [x for x in difflib.unified_diff(lb, la, lineterm='', n=0) if x[:1] in '+-' and x[:3] not in ('+++', '---')]
        rows.append('%s (%s) vs s143/%s (%s): %d changed lines' % (a, sha(pa)[:16], b, sha(pb)[:16], len(d)))
        rows.extend('    ' + x[:220] for x in d[:24])
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    guard('start')
    n = chain_shells()
    if n != '0':
        tline('rt144 ABORT before any work: a chain shell lives (%s) - wait for the next gap' % n)
        return 6
    tline('rt144 start pid %d: lock absent, STOP absent, chain shells 0' % os.getpid())
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    step0 = S144 + '/step0/'
    res = []
    for suite, ref in (('test_sc144.py', 'test_sc144.out.txt'), ('test_go144a.py', 'test_go144a.out.txt'),
                       ('test_fgcpu144.py', 'test_fgcpu144.out.txt'), ('test_tools144.py', 'test_tools144.out.txt')):
        guard(suite)
        p = subprocess.run([sys.executable, suite], cwd=S144, capture_output=True, env=env, timeout=600)
        data = p.stdout + p.stderr
        outp = OUT + '/' + ref
        open(outp, 'wb').write(data)
        s = hashlib.sha256(data).hexdigest()
        last = [x for x in data.decode('ascii', 'replace').replace(CR, '').split(NL) if x.strip()][-2:]
        res.append('%s rc %d -> %s sha256 %s; step0 %s; byte-equal %s; tail %s' % (
            suite, p.returncode, outp, s, sha(step0 + ref), s == sha(step0 + ref), ' | '.join(last)))
        tline('rt144 %s rc %d -> step1/%s sha256 %s (step0 equal %s)' % (suite, p.returncode, ref, s, s == sha(step0 + ref)))
    sys.path.insert(0, S144)
    os.chdir(S144)
    import sc144 as S
    seal_sha = sha(S.PRED_PATH)
    for argv, ref in ((['--check-seal'], 'checkseal144.out.txt'), (['--regress143'], 'regress143.out.txt'),
                      (['--regress142'], 'regress142.out.txt'), (['--calib'], 'calib144.out.txt'),
                      (['--check1b'], 'check1b144.out.txt'), (['--summary'], 'summary144_empty.txt')):
        guard(argv[0])
        rc, text = main_out(S, argv)
        outp, s = put(ref, text)
        res.append('sc144.py %s rc %d -> %s sha256 %s; step0 %s; byte-equal %s; last %s' % (
            argv[0], rc, outp, s, sha(step0 + ref), s == sha(step0 + ref), text.strip().split(NL)[-1][:160]))
        tline('rt144 sc144.py %s rc %d -> step1/%s sha256 %s (step0 equal %s)' % (argv[0], rc, ref, s, s == sha(step0 + ref)))
    p, s = put('rt144_recount.txt', NL.join(res) + NL)
    tline('rt144 recount -> step1/rt144_recount.txt sha256 %s' % s)
    ra, shas = part_a()
    p, s = put('rt144_members.txt', NL.join(ra) + NL)
    tline('rt144 part A precache members -> step1/rt144_members.txt sha256 %s' % s)
    rb = part_b(S, shas, seal_sha)
    p, s = put('rt144_wreal.txt', NL.join(rb) + NL)
    tline('rt144 part B profile 144 on real W logs -> step1/rt144_wreal.txt sha256 %s' % s)
    rc_ = part_c()
    p, s = put('rt144_cache.txt', NL.join(rc_) + NL)
    tline('rt144 part C cache state -> step1/rt144_cache.txt sha256 %s' % s)
    re_ = part_e()
    p, s = put('rt144_ported.txt', NL.join(re_) + NL)
    tline('rt144 part E ported diffs -> step1/rt144_ported.txt sha256 %s' % s)
    tline('rt144 end pid %d' % os.getpid())
    print(NL.join(res))
    return 0


if __name__ == '__main__':
    sys.exit(main())
