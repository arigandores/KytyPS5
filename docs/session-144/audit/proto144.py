# proto144.py - Session Auditor, s144 step 3 (HPP-333): protocol checks of the s143 close and of steps 0-2 of s144.
#  1. lock windows of runs144/lock.log
#  2. general rule 27: mtime / creation time of the files of the track roots against the windows; commits of both repositories
#     against the windows
#  3. step2/times.txt: per tag - stop-check, gate, API row, call, enter_scene inside the lock, one attempt, sha256 of the log
#  4. the seal pred/01_sc144.md: sha256, mtime before the first lock, every "seal:" line against the file now
#  5. sha256 of the outputs (glitch, rec, sheet, score) against the rows of times.txt
#  6. the s143 close: commit times, instruction files (sha256, mtime), CLAUDE.md = AGENTS.md
# READ ONLY (writes nothing but stdout). Process names of BUSY / CPU rows are not printed. Usage: python proto144.py
import os, re, json, hashlib, datetime, subprocess

UTC = datetime.timezone.utc
S144 = 'C:/kyty/s144'
S143 = 'C:/kyty/s143'
GIT = 'C:/Program Files/Git/cmd/git.exe'
KY = 'C:/kyty/KytyPS5'
EM = 'C:/kyty/KytyPS5/ps5 em'


def ts(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC).timestamp()


def iso(t):
    return datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%dT%H:%M:%SZ') if t is not None else None


def sha(p):
    h = hashlib.sha256()
    try:
        with open(p, 'rb') as f:
            for c in iter(lambda: f.read(1 << 22), b''):
                h.update(c)
    except OSError:
        return 'unreadable'
    return h.hexdigest()


def windows(path):
    w = []
    cur = {}
    for ln in open(path, encoding='utf-8', errors='replace').read().splitlines():
        m = re.match(r'lock (taken|released) (\S+) (\S+Z)', ln)
        if not m:
            if ln.strip():
                print('LOCKLOG odd line: %r' % ln[:120])
            continue
        if m.group(1) == 'taken':
            cur[m.group(2)] = ts(m.group(3))
        else:
            w.append((m.group(2), cur.pop(m.group(2), None), ts(m.group(3))))
    for k in cur:
        print('LOCKLOG taken without release: %s' % k)
    return w


W = windows(S144 + '/runs144/lock.log')
gaps = [W[i + 1][1] - W[i][2] for i in range(len(W) - 1)]
print('LOCK WINDOWS %d: first taken %s, last released %s; sum held %.0f s; gaps between tags min %.0f s max %.0f s median %.0f s' % (
    len(W), iso(W[0][1]), iso(W[-1][2]), sum(b - a for _, a, b in W), min(gaps), max(gaps), sorted(gaps)[len(gaps) // 2]))
print('LOCK ORDER: %s' % ' '.join(t for t, a, b in W))


def inwin(t):
    for tag, a, b in W:
        if a <= t <= b:
            return tag
    return None


# 2. rule 27 - files
ROOTS = [('p283', 'C:/kyty/p283'), ('f287', 'C:/kyty/f287'), ('s288', 'C:/kyty/s288'), ('KytyPS5/docs', KY + '/docs'),
         ('KytyPS5/src', KY + '/src'), ('ps5 em/docs', EM + '/docs'), ('s144/lead', S144 + '/lead'), ('s144/step1', S144 + '/step1'),
         ('s143', S143), ('s142', 'C:/kyty/s142'), ('build', 'C:/kyty/build'), ('kyty root files', 'C:/kyty')]
for name, root in ROOTS:
    n = 0
    hits = []
    chits = []
    if not os.path.isdir(root):
        print('RULE27 %s: no such directory' % name)
        continue
    if name == 'kyty root files':
        it = [(root, [], [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))])]
    else:
        it = os.walk(root)
    for dp, dn, fn in it:
        for f in fn:
            p = os.path.join(dp, f)
            try:
                st = os.stat(p)
            except OSError:
                continue
            n += 1
            t = inwin(st.st_mtime)
            if t:
                hits.append((st.st_mtime, t, p.replace(chr(92), '/')))
            c = inwin(st.st_ctime)
            if c and not t:
                chits.append((st.st_ctime, c, p.replace(chr(92), '/')))
    print('RULE27 %s: files %d; mtime inside a lock window %d; created inside a window (mtime outside) %d' % (name, n, len(hits), len(chits)))
    bydir = {}
    for m, t, p in hits:
        d = os.path.dirname(p)
        bydir.setdefault(d, []).append((m, t, p))
    for d in sorted(bydir, key=lambda d: min(x[0] for x in bydir[d]))[:30]:
        xs = sorted(bydir[d])
        print('   IN-LOCK dir %s: %d files, %s (%s) .. %s (%s); e.g. %s' % (d, len(xs), iso(xs[0][0]), xs[0][1], iso(xs[-1][0]), xs[-1][1], os.path.basename(xs[0][2])))
    for m, t, p in sorted(chits)[:12]:
        print('   CREATED-IN-LOCK %s %s %s' % (iso(m), t, p))

# top-level directories of C:/kyty touched during the series (worktrees, build folders of the tracks)
for d in sorted(os.listdir('C:/kyty')):
    p = 'C:/kyty/' + d
    if os.path.isdir(p):
        m = os.stat(p).st_mtime
        if W[0][1] <= m <= W[-1][2]:
            print('TOPDIR C:/kyty/%s mtime %s in window %s' % (d, iso(m), inwin(m)))

# 2b. rule 27 - commits
for name, root in (('KytyPS5', KY), ('ps5-em', EM)):
    r = subprocess.run([GIT, '-C', root, 'log', '--since=2026-10-01T04:40:00Z', '--format=%H %ct %s'], capture_output=True)
    lines = r.stdout.decode('utf-8', 'replace').splitlines()
    n_in = 0
    for ln in reversed(lines):
        h, ct, subj = ln.split(' ', 2)
        ct = int(ct)
        t = inwin(ct)
        n_in += 1 if t else 0
        print('COMMIT %s %s %s %s %s' % (name, h[:8], iso(ct), ('IN-LOCK ' + t) if t else '-', subj[:110].encode('ascii', 'replace').decode()))
    print('COMMITS %s since 04:40Z: %d; committed inside a lock window: %d' % (name, len(lines), n_in))

# 3. times.txt of step 2
rows = open(S144 + '/step2/times.txt', encoding='utf-8', errors='replace').read().splitlines()
bad = [r[:80] for r in rows if not re.match(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ ', r)]
print('TIMES step2: rows %d; rows without a leading UTC stamp %d %s' % (len(rows), len(bad), bad[:5]))
A = {(r['root'][-4:], r['tag']): r for r in json.load(open(S144 + '/step3/aud144.json'))}
tags = ['w144_%02d' % i for i in range(0, 9)]
for i in range(9, 21):
    tags += ['v144_%02d' % i, 'w144_%02d' % i]
print('ORDER lock.log = the seal order (33 tags): %s' % ([t for t, a, b in W] == tags))
win = {t: (a, b) for t, a, b in W}
seal_sha = sha(S144 + '/pred/01_sc144.md')
ok = True
prev_rel = None
nrefused = 0
for t in tags:
    st = [x for x in rows if (' go144a %s enter_scene start' % t) in x]
    en = [x for x in rows if (' go144a %s enter_scene end' % t) in x]
    calls = [x for x in rows if ' next_one ' in x and x.rstrip().endswith('go144a.sh %s' % t)]
    rets = [x for x in rows if (' call_one go144a %s call returned rc=' % t) in x]
    # a refused call = a return with rc != 0 BEFORE the lock of the tag was taken (the made attempt of w144_20 returned rc=1 after it)
    refused = [x for x in rets if not x.rstrip().endswith('rc=0') and (win.get(t, (None,))[0] is None or ts(x[:20]) < win[t][0])]
    gate = [x for x in rows if (' GATE %s ' % t) in x]
    gate_pass = [x for x in gate if (' GATE %s PASS' % t) in x]
    api = [x for x in rows if (' apichk144 %s ' % t) in x]
    api_go = [x for x in api if x.rstrip().endswith('-> GO')]
    stopc = [x for x in rows if ('--stop-check %s rc 0' % t) in x]
    a, b = win.get(t, (None, None))
    msg = []
    if len(st) != 1 or len(en) != 1:
        msg.append('enter_scene start %d end %d' % (len(st), len(en)))
    else:
        t0, t1 = ts(st[0][:20]), ts(en[0][:20])
        if not (a <= t0 <= t1 <= b):
            msg.append('enter_scene %s..%s not inside the lock %s..%s' % (iso(t0), iso(t1), iso(a), iso(b)))
        m = re.search(r'sha256 ([0-9a-f]{64})', en[0])
        if not m or m.group(1) != A[('s144', t)]['log']['sha256']:
            msg.append('log sha of the times row != the log now')
    if len(calls) != len(rets):
        msg.append('calls %d != returns %d' % (len(calls), len(rets)))
    if len(calls) - len(refused) != 1:
        msg.append('accepted calls %d' % (len(calls) - len(refused)))
    if len(gate_pass) != len(calls) or len(gate) != len(gate_pass):
        msg.append('GATE rows %d pass %d for %d calls' % (len(gate), len(gate_pass), len(calls)))
    if len(api_go) != len(calls) or len(api) != len(api_go):
        msg.append('API rows %d GO %d for %d calls' % (len(api), len(api_go), len(calls)))
    if len(stopc) != len(calls):
        msg.append('stop-check rc 0 rows %d for %d calls' % (len(stopc), len(calls)))
    if calls:
        # the last sequence: stop-check <= gate <= api <= call <= lock
        seq = [ts(x[-1][:20]) for x in (stopc, gate_pass, api_go, calls) if x]
        if seq != sorted(seq):
            msg.append('order stop-check/gate/api/call broken')
        c0 = ts(calls[-1][:20])
        if prev_rel is not None and ts(stopc[0][:20]) < prev_rel:
            msg.append('the first stop-check row %s is before the previous release %s' % (stopc[0][:20], iso(prev_rel)))
        if a is not None and c0 > a:
            msg.append('the call row is after the lock')
    lm = os.stat('%s/log_%s.txt' % (S144, t)).st_mtime
    if a is None or not (a <= lm <= b):
        msg.append('log mtime %s outside its lock' % iso(lm))
    att = os.path.isfile('%s/attempt_%s.txt' % (S144, t))
    js = A[('s144', t)]['json']
    na = len(js.get('attempts', [])) if isinstance(js, dict) else None
    if na != 1 or not att:
        msg.append('attempts in json %s, attempt file %s' % (na, att))
    if (js.get('prereg') or {}).get('sha256') != seal_sha:
        msg.append('prereg sha of the json != the seal now')
    if js.get('binary_sha256', '')[:8] != '9235a7ac':
        msg.append('binary %s' % js.get('binary_sha256', '')[:8])
    nrefused += len(refused)
    ok &= not msg
    print('TAG %s lock %s..%s (%.0f s) calls %d refused before the lock %d (%s) gate PASS %d api GO %d stop-check %d starts %d json attempts %s rc %s %s' % (
        t, iso(a), iso(b), (b - a) if a else 0, len(calls), len(refused), ','.join(x[:20] for x in refused), len(gate_pass), len(api_go), len(stopc), len(st), na,
        (re.search(r'end rc (\d+)', en[0]).group(1) if en else None), ('PROBLEM: ' + '; '.join(msg)) if msg else 'ok'))
    prev_rel = b
# the eight V of the cross-session pairs: sha256 of the log now = the last "go143a v143_NN enter_scene end" row of s143 step2/times.txt
r143 = open(S143 + '/step2/times.txt', encoding='utf-8', errors='replace').read().splitlines()
p8 = True
for i in (1, 2, 3, 4, 5, 6, 9, 10):
    t = 'v143_%02d' % i
    en = [x for x in r143 if (' go143a %s enter_scene end' % t) in x]
    m = re.search(r'sha256 ([0-9a-f]{64})', en[-1]) if en else None
    good = bool(m) and m.group(1) == A[('s143', t)]['log']['sha256']
    p8 &= good
    js = A[('s143', t)]['json']
    print('PAIR-V %s: rows %d, sha of the last row = the log now %s; json prereg %s (seal 02 of s143 now %s); binary %s; attempts %s' % (
        t, len(en), good, str((js.get('prereg') or {}).get('sha256'))[:8], sha(S143 + '/pred/02_sc143.md')[:8], str(js.get('binary_sha256'))[:8], len(js.get('attempts', []))))
print('PAIR-V CHECK (8 logs of s143 against their own times.txt): %s; s143 step2/times.txt sha256 %s' % ('ALL OK' if p8 else 'PROBLEMS', sha(S143 + '/step2/times.txt')))
busy = [x for x in rows if ' BUSY ' in x]
first_calls = {}
for t in tags:
    cs = [ts(x[:20]) for x in rows if ' next_one ' in x and x.rstrip().endswith('go144a.sh %s' % t)]
    if len(cs) > 1:
        first_calls[t] = (len(cs) - 1, cs[-1] - cs[0])
print('REFUSALS by tag (refused calls, seconds from the first call row to the accepted call row): %s; total %.0f s' % (
    {k: (v[0], round(v[1])) for k, v in first_calls.items()}, sum(v[1] for v in first_calls.values())))
print('REFUSED CALLS (rc != 0, no attempt made): %d; BUSY rows %d at %s' % (nrefused, len(busy), [x[:20] + ' ' + x.split(' go144a ')[1].split(' ')[0] for x in busy if ' go144a ' in x]))
print('OLD DIR (stale moves of a second attempt): %s' % os.path.isdir(S144 + '/old'))
print('STOP FILE now: %s' % os.path.exists(S144 + '/STOP'))
extra = sorted(f for f in os.listdir(S144) if re.match(r'(log|stdout)_.*_a\d+\.txt$', f))
print('PER-ATTEMPT COPIES (_aN): %s' % extra)
for f in extra:
    base = re.sub(r'_a\d+\.txt$', '.txt', f)
    print('   %s sha %s = %s sha %s: %s' % (f, sha(S144 + '/' + f)[:12], base, sha(S144 + '/' + base)[:12], sha(S144 + '/' + f) == sha(S144 + '/' + base)))
print('TIMES/LOCK CHECK: %s' % ('ALL OK' if ok else 'PROBLEMS'))
# member (2) of the CPU row: processes born inside the lock window (names not printed)
n2 = []
for x in rows:
    m = re.search(r' go144a (\S+) foreign cpu at the end inside the lock: .*?\(2\) new at the end: foreign ([0-9.]+) CPU s/s = ([0-9.]+) % over (\d+) processes', x)
    if m:
        n2.append((m.group(1), float(m.group(2)), int(m.group(4))))
    m1 = re.search(r' go144a (\S+) foreign cpu at the end inside the lock: fgcpu144: run ([0-9.]+) s: \(1\) alive at both ends: foreign ([0-9.]+) CPU s/s', x)
    if m1 and m:
        n2[-1] = n2[-1] + (float(m1.group(3)),)
if n2:
    print('CPU ROW: tags %d; member (1) foreign CPU s/s min %.3f max %.3f (%s); member (2) processes born inside the window: min %d max %d, CPU s/s max %.3f (%s)' % (
        len(n2), min(x[3] for x in n2), max(x[3] for x in n2), max(n2, key=lambda x: x[3])[0], min(x[2] for x in n2), max(x[2] for x in n2),
        max(x[1] for x in n2), max(n2, key=lambda x: x[1])[0]))
    for x in n2:
        print('   CPU %s member1 %.3f CPU s/s member2 %d processes %.3f CPU s/s' % (x[0], x[3], x[2], x[1]))

# 4. the seal
seal = S144 + '/pred/01_sc144.md'
sm = os.stat(seal).st_mtime
print('SEAL 01 sha256 %s mtime %s (first lock %s) before the first lock: %s' % (seal_sha, iso(sm), iso(W[0][1]), sm < W[0][1]))
sok = True
nseal = 0
for ln in open(seal, encoding='utf-8').read().splitlines():
    m = re.match(r'seal: ([0-9a-f]{64}) (\S+)$', ln)
    if not m:
        continue
    nseal += 1
    p = m.group(2) if m.group(2).startswith('C:/') else S144 + '/' + m.group(2)
    h = sha(p)
    fm = os.stat(p).st_mtime if os.path.isfile(p) else 0
    good = (h == m.group(1)) and fm <= sm
    sok &= good
    if not good:
        print('   SEAL LINE %s: sha now %s (seal %s) mtime %s' % (m.group(2), h[:16], m.group(1)[:16], iso(fm)))
print('SEAL LINES %d: every file = its seal line and not modified after the seal: %s' % (nseal, 'ALL OK' if sok else 'PROBLEMS'))
for f in ('step2/gate144.py', 'step2/test_gate144.py', 'step2/pre_one.sh', 'step2/table144.py', 'step2/test_gate144.out.txt'):
    p = S144 + '/' + f
    if os.path.isfile(p):
        fm = os.stat(p).st_mtime
        print('STEP2 FILE %s sha256 %s mtime %s before the first lock %s in a lock window %s' % (f, sha(p), iso(fm), fm < W[0][1], inwin(fm)))

# 5. outputs against the rows of times.txt
vok = True
nfile = 0
for ln in rows:
    for fn, h in re.findall(r'((?:glitch|rec|sheet|score|log)_\w+\.(?:txt|mp4|png)) sha256 ([0-9a-f]{64})', ln):
        if fn.startswith('log_'):
            continue
        nfile += 1
        now = sha(S144 + '/' + fn)
        if now != h:
            vok = False
            print('   OUTPUT %s: sha now %s != times row %s (%s)' % (fn, now[:16], h[:16], ln[:20]))
print('OUTPUT SHA s144: %d file rows (glitch, rec, sheet, score) against the files now: %s' % (nfile, 'ALL OK' if vok else 'DIFFERENCES'))
for f in ('step2/summary144.txt', 'step2/table144.txt', 'step2/checkseal_final.txt', 'step2/sheets144.txt', 'FACTS.md', 'runs144/lock.log', 'step2/times.txt',
          'step0/times.txt', 'step1/times.txt'):
    print('FILE %s sha256 %s mtime %s' % (f, sha(S144 + '/' + f), iso(os.stat(S144 + '/' + f).st_mtime)))

# 6. the s143 close
for name, root, revs in (('KytyPS5', KY, ['d31de12b', 'd3a8d951', '522d2ec7', 'e83afd8e', '5558b64c', '919f43e0', 'de2c87af', '206ffda0', '43fc0b63', '075fe845', 'bacd57cc']),
                         ('ps5-em', EM, ['a41019e'])):
    for rv in revs:
        r = subprocess.run([GIT, '-C', root, 'show', '-s', '--format=%H %ct %s', rv], capture_output=True)
        o = r.stdout.decode('utf-8', 'replace').strip()
        if not o:
            print('CLOSE %s %s: not found' % (name, rv))
            continue
        h, ct, subj = o.split(' ', 2)
        print('CLOSE %s %s %s %s' % (name, h[:8], iso(int(ct)), subj[:120].encode('ascii', 'replace').decode()))
base = os.path.expanduser('~').replace(chr(92), '/') + '/.paperclip/instances/default/companies/' + os.environ.get('PAPERCLIP_COMPANY_ID', '') + '/agents'
ins = []
for d in sorted(os.listdir(base)):
    p = '%s/%s/instructions/AGENTS.md' % (base, d)
    if os.path.isfile(p):
        st = os.stat(p)
        first = open(p, encoding='utf-8', errors='replace').readline().strip()[:40]
        ins.append((d, sha(p), st.st_mtime, st.st_size, first))
for d, h, m, sz, first in ins:
    print('INSTR agent %s.. sha256 %s mtime %s size %d in a lock window %s; %s' % (d[:8], h[:8], iso(m), sz, inwin(m), first.encode('ascii', 'replace').decode()))
print('INSTR files %d' % len(ins))
for f in (EM + '/docs/agent-team.md', EM + '/docs/platform-traps.md', EM + '/CLAUDE.md', EM + '/AGENTS.md'):
    print('DOC %s sha256 %s size %d mtime %s' % (os.path.basename(f), sha(f), os.path.getsize(f), iso(os.stat(f).st_mtime)))
for rv in ('a41019e', 'HEAD'):
    o = {}
    for f in ('CLAUDE.md', 'AGENTS.md', 'docs/agent-team.md', 'docs/platform-traps.md'):
        r = subprocess.run([GIT, '-C', EM, 'show', '%s:%s' % (rv, f)], capture_output=True)
        o[f] = (hashlib.sha256(r.stdout).hexdigest(), len(r.stdout))
    print('PS5EM %s: CLAUDE.md %s (%d B) AGENTS.md %s (%d B) equal %s; agent-team.md %s; platform-traps.md %s' % (
        rv, o['CLAUDE.md'][0][:8], o['CLAUDE.md'][1], o['AGENTS.md'][0][:8], o['AGENTS.md'][1], o['CLAUDE.md'][0] == o['AGENTS.md'][0],
        o['docs/agent-team.md'][0][:8], o['docs/platform-traps.md'][0][:8]))
print('ALL DONE')
