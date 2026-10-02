# proto145.py - Session Auditor, s145 step 3 (HPP-353): protocol checks of the s144 close and of steps 0-2 of s145.
#  1. lock windows: runs145/lock.log (session) and every lock.log under the track roots (p283, f287, s288) since the s144 close
#  2. general rules 27-28: mtime of the files of the track roots and of the lead folders against the SESSION windows and the
#     series window; files of the session steps against the TRACK windows; commits of both repositories against all windows
#  3. step2/times.txt: per tag - gate row before the call, one lock per tag, one attempt, one-time rows of items 304 / 305
#  4. the seal pred/03_sc145.md: sha256, mtime before the first lock, every "seal:" line against the file now, prereg of every json
#  5. start rows of the steps against the commit times of the inputs they name
#  6. the s144 close: commit times, instruction files (sha256 prefixes against item 274 (b)), CLAUDE.md = AGENTS.md
# READ ONLY (writes nothing but stdout). Process names of BUSY rows are masked. Usage: python proto145.py
import os, re, json, hashlib, datetime, subprocess

UTC = datetime.timezone.utc
S145 = 'C:/kyty/s145'
GIT = 'C:/Program Files/Git/cmd/git.exe'
KY = 'C:/kyty/KytyPS5'
EM = 'C:/kyty/KytyPS5/ps5 em'
CLOSE144 = '2026-10-01T12:30:00Z'
SKIPD = ('mutwork', 'mutcache', '__pycache__', 'vidframes', 'fx_', 'wt', 'build', 'bin', '.git')


def ts(s):
    return datetime.datetime.strptime(s[:19].replace(' ', 'T'), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=UTC).timestamp()


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


def windows(path, since=None):
    w = []
    cur = {}
    odd = 0
    for ln in open(path, encoding='utf-8', errors='replace').read().splitlines():
        m = re.match(r'lock (taken|released) (\S+) (\S+Z)', ln)
        if not m:
            odd += 1 if ln.strip() else 0
            continue
        if m.group(1) == 'taken':
            cur.setdefault(m.group(2), []).append(ts(m.group(3)))
        elif cur.get(m.group(2)):
            a = cur[m.group(2)].pop(0)
            if since is None or a >= since:
                w.append((m.group(2), a, ts(m.group(3))))
    left = [k for k, v in cur.items() if v]
    return w, left, odd


def walk(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith(SKIPD)]
        for f in fn:
            p = os.path.join(dp, f).replace(chr(92), '/')
            try:
                yield p, os.stat(p)
            except OSError:
                pass


# 1. windows
W, left, odd = windows(S145 + '/runs145/lock.log')
gaps = [W[i + 1][1] - W[i][2] for i in range(len(W) - 1)]
tags = [w[0] for w in W]
print('SESSION LOCK WINDOWS %d (distinct tags %d; taken without release %s; odd lines %d): first taken %s, last released %s; sum held %.0f s; '
      'gaps between tags min %.0f s, median %.0f s, max %.0f s (%s -> %s)' % (
          len(W), len(set(tags)), left, odd, iso(W[0][1]), iso(W[-1][2]), sum(b - a for _, a, b in W), min(gaps), sorted(gaps)[len(gaps) // 2], max(gaps),
          tags[gaps.index(max(gaps))], tags[gaps.index(max(gaps)) + 1]))
SER = (W[0][1], W[-1][2])
big = sorted(((g, tags[i], tags[i + 1], W[i][2], W[i + 1][1]) for i, g in enumerate(gaps)), reverse=True)[:4]
for g, a, b, t0, t1 in big:
    print('   GAP %6.0f s between %s (released %s) and %s (taken %s)' % (g, a, iso(t0), b, iso(t1)))
TW = []
for root in ('C:/kyty/p283', 'C:/kyty/f287', 'C:/kyty/s288'):
    for p, st in walk(root):
        if os.path.basename(p) == 'lock.log':
            w, lf, od = windows(p, ts(CLOSE144))
            for t, a, b in w:
                TW.append((a, b, t, p.replace('C:/kyty/', '')))
            print('TRACK LOCKLOG %s: windows since %s: %d; taken without release %s' % (p.replace('C:/kyty/', ''), CLOSE144, len(w), lf))
TW.sort()
for a, b, t, p in TW:
    print('   TRACK WINDOW %s..%s %4.0f s %s (%s)%s' % (iso(a), iso(b), b - a, t, p, '  <== INSIDE THE SERIES WINDOW' if SER[0] <= a <= SER[1] else ''))
print('TRACK WINDOWS since the s144 close: %d; inside the series window %s..%s: %d' % (len(TW), iso(SER[0]), iso(SER[1]), sum(1 for a, b, t, p in TW if SER[0] <= a <= SER[1])))


def insess(t):
    for tag, a, b in W:
        if a <= t <= b:
            return tag
    return None


def intrack(t):
    for a, b, tag, p in TW:
        if a <= t <= b:
            return tag
    return None


# 2. files against the windows
for name, roots in (('track P', ['C:/kyty/p283']), ('track F', ['C:/kyty/f287']), ('track S', ['C:/kyty/s288']),
                    ('lead (s145/lead, s145/step4_lead, s144/step4)', [S145 + '/lead', S145 + '/step4_lead', 'C:/kyty/s144/step4']),
                    ('repository docs (KytyPS5/docs/track-p, track-f, track-s, session-145, agent)', [KY + '/docs/track-p', KY + '/docs/track-f', KY + '/docs/track-s', KY + '/docs/session-145', KY + '/docs/agent']),
                    ('emulator folder docs', [EM + '/docs'])):
    n = 0
    inl, inser = [], []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for p, st in walk(root):
            n += 1
            t = insess(st.st_mtime)
            if t:
                inl.append((st.st_mtime, t, p, st.st_size))
            elif SER[0] <= st.st_mtime <= SER[1]:
                inser.append((st.st_mtime, p, st.st_size))
    print('FILES %s: %d; mtime inside a SESSION lock window: %d; inside the series window but outside the locks: %d' % (name, n, len(inl), len(inser)))
    for m, t, p, sz in sorted(inl)[:30]:
        print('   IN-SESSION-LOCK %s under %s %s (%d bytes)' % (iso(m), t, p.replace('C:/kyty/', ''), sz))
    by = {}
    for m, p, sz in inser:
        d = '/'.join(p.replace('C:/kyty/', '').split('/')[:3])
        e = by.setdefault(d, [0, m, m, 0])
        e[0] += 1
        e[1] = min(e[1], m)
        e[2] = max(e[2], m)
        e[3] += sz
    for d, e in sorted(by.items(), key=lambda x: x[1][1]):
        print('   IN-SERIES-WINDOW %s: %d files, %s..%s, %d bytes' % (d, e[0], iso(e[1]), iso(e[2]), e[3]))
# session step files under the TRACK windows
hits = []
n = 0
for p, st in walk(S145):
    if '/runs145/' in p or re.search(r'/(log_|rec_|stdout_|sheet_|glitch_|gpuclk_|score_|attempt_|[vw]145_)', p):
        continue
    n += 1
    t = intrack(st.st_mtime)
    if t:
        hits.append((st.st_mtime, t, p))
print('S145 STEP FILES %d (without run outputs, mutant work folders, fixtures); mtime inside a TRACK lock window: %d' % (n, len(hits)))
for m, t, p in sorted(hits)[:40]:
    print('   IN-TRACK-LOCK %s under %s %s' % (iso(m), t, p.replace('C:/kyty/', '')))
# commits
for name, root in (('KytyPS5', KY), ('ps5-em', EM)):
    r = subprocess.run([GIT, '-C', root, 'log', '--since=' + CLOSE144, '--format=%h %ct %s'], capture_output=True)
    lines = r.stdout.decode('utf-8', 'replace').splitlines()
    ks = kt = kw = 0
    for ln in lines:
        h, ct, subj = ln.split(' ', 2)
        s, t = insess(int(ct)), intrack(int(ct))
        sub = subj[:100].encode('ascii', 'replace').decode()
        if s:
            ks += 1
            print('   COMMIT-IN-SESSION-LOCK %s %s %s under %s: %s' % (name, h, iso(int(ct)), s, sub))
        if t:
            kt += 1
            print('   COMMIT-IN-TRACK-LOCK %s %s %s under %s: %s' % (name, h, iso(int(ct)), t, sub))
        if SER[0] <= int(ct) <= SER[1]:
            kw += 1
    print('COMMITS %s since %s: %d; inside a session lock window %d; inside a track lock window %d; inside the series window %d' % (name, CLOSE144, len(lines), ks, kt, kw))

# 3. times.txt of step 2
T = open(S145 + '/step2/times.txt', encoding='utf-8', errors='replace').read().splitlines()
rows = []
for ln in T:
    m = re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) (.*)', ln)
    if m:
        rows.append((ts(m.group(1)), m.group(2)))
print('TIMES step2: lines %d, rows with a leading UTC time %d; non-monotonic rows %d' % (len(T), len(rows), sum(1 for a, b in zip(rows, rows[1:]) if b[0] < a[0])))
gate = [(t, x) for t, x in rows if x.startswith('GATE ')]
print('GATE rows %d: start %d, PASS %d (of them "by ROADMAP item" %d), STOP %d' % (
    len(gate), sum(1 for t, x in gate if x.startswith('GATE start')), sum(1 for t, x in gate if re.match(r'GATE \S+ PASS', x)),
    sum(1 for t, x in gate if 'PASS by ROADMAP item' in x), sum(1 for t, x in gate if re.match(r'GATE \S+ STOP', x))))
for t, x in gate:
    if 'PASS by ROADMAP item' in x or re.match(r'GATE \S+ STOP', x):
        print('   %s %s' % (iso(t), x[:150]))
order = ['w145_00', 'w145_01']
for i in range(2, 18):
    order += ['v145_%02d' % i, 'w145_%02d' % i]
okg = True
for tag, a, b in W:
    g = [(t, x) for t, x in gate if x.startswith('GATE %s ' % tag) and t <= a]
    last = g[-1] if g else None
    calls = [t for t, x in rows if ('call: PLWAIT=540 bash C:/kyty/s145/go145a.sh %s' % tag) in x]
    good = last is not None and ' PASS' in last[1][:30] and any(last[0] <= c <= a for c in calls)
    okg &= good
    if not good or 'by ROADMAP item' in (last[1] if last else '') or len(calls) != 1:
        print('   TAG %s: lock taken %s; last gate row before it %s "%s"; call rows %s -> %s' % (
            tag, iso(a), iso(last[0]) if last else None, last[1][:60] if last else None, [iso(c) for c in calls], 'ok' if good else 'VIOLATED'))
print('EVERY LOCK PRECEDED BY A GATE PASS ROW AND A CALL ROW OF ITS TAG: %s; order of the locks = the sealed order: %s' % (okg, tags == order))
att = {t: os.path.isfile('%s/attempt_%s.txt' % (S145, t)) for t in order}
js = {}
for t in order:
    try:
        js[t] = json.load(open('%s/%s.json' % (S145, t), encoding='utf-8'))
    except (OSError, ValueError):
        js[t] = None
print('ATTEMPT FILES %d of %d; json present %d (missing %s); attempts per json %s; locks per tag max %d' % (
    sum(att.values()), len(order), sum(1 for v in js.values() if v), [t for t, v in js.items() if not v],
    sorted(set(len(v.get('attempts') or []) for v in js.values() if v)), max(tags.count(t) for t in order)))
gl = open(S145 + '/go145a.log', encoding='utf-8', errors='replace').read()
gl = re.sub(r"busy \[\('[^']*'", "busy [('<app>'", gl)
es = re.findall(r'(\S+) enter_scene start', gl)
print('go145a.log: "enter_scene start" rows %d; "procload: busy" rows %d; refusal rows (rc 1 / order) %d' % (
    len(es), len(re.findall(r'procload: busy', gl)), len(re.findall(r'refus|not made|order', gl))))
old = S145 + '/runs145/old'
print('runs145/old: %s' % (sorted(os.listdir(old)) if os.path.isdir(old) else 'absent'))

# 4. the seal
seal = S145 + '/pred/03_sc145.md'
sh = sha(seal)
sm = os.stat(seal).st_mtime
print('SEAL 03 sha256 %s mtime %s; first lock %s; seal before the first lock: %s' % (sh, iso(sm), iso(W[0][1]), sm < W[0][1]))
bad = 0
late = 0
ns = 0
for ln in open(seal, encoding='utf-8').read().splitlines():
    m = re.match(r'seal: ([0-9a-f]{64}) (\S+)', ln)
    if not m:
        continue
    ns += 1
    p = m.group(2) if m.group(2).startswith('C:/') else S145 + '/' + m.group(2)
    now = sha(p)
    mt = os.stat(p).st_mtime if os.path.isfile(p) else None
    if now != m.group(1):
        bad += 1
        print('   SEAL LINE DIFFERS %s: seal %s now %s' % (m.group(2), m.group(1)[:16], now[:16]))
    if mt is not None and mt > sm:
        late += 1
        print('   SEALED FILE mtime after the seal: %s %s' % (m.group(2), iso(mt)))
print('SEAL LINES %d: files differing now %d; files with mtime after the seal %d' % (ns, bad, late))
pr = {t: ((v.get('prereg') or {}).get('sha256'), v.get('binary_sha256')) for t, v in js.items() if v}
print('JSON prereg = seal 03: %d of %d; binary 9235a7ac: %d of %d' % (
    sum(1 for a, b in pr.values() if a == sh), len(pr), sum(1 for a, b in pr.values() if str(b).startswith('9235a7ac')), len(pr)))

# 5. start rows of the steps against the commits they name
for step in ('step0', 'step0b', 'step1', 'step1b', 'step2'):
    L = open('%s/%s/times.txt' % (S145, step), encoding='utf-8', errors='replace').read().splitlines()
    first = L[0]
    t0 = ts(first[:20])
    hs = re.findall(r'\b([0-9a-f]{8})\b', first)
    out = []
    for h in hs:
        r = subprocess.run([GIT, '-C', KY, 'show', '-s', '--format=%ct', h], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip().isdigit():
            ct = int(r.stdout.strip())
            out.append('%s committed %s (%+d s before the start)' % (h, iso(ct), t0 - ct))
    print('STEP %s: first row %s; last row %s; commits named in the first row: %s' % (step, first[:20], L[-1][:20], '; '.join(out) or 'none resolved'))

# 6. the s144 close
for name, root, hs in (('KytyPS5', KY, ['717b12a7', 'e7d0e45f', '05da9fda']), ('ps5-em', EM, ['c15da20'])):
    for h in hs:
        r = subprocess.run([GIT, '-C', root, 'show', '-s', '--format=%ct %s', h], capture_output=True)
        o = r.stdout.decode('utf-8', 'replace').strip()
        if o:
            ct, subj = o.split(' ', 1)
            print('CLOSE144 COMMIT %s %s %s: %s' % (name, h, iso(int(ct)), subj[:110].encode('ascii', 'replace').decode()))
home = os.environ.get('USERPROFILE', '').replace(chr(92), '/')
co = home + '/.paperclip/instances/default/companies/f6a17988-768c-4cca-805c-868da6fede4f/agents'
ROLE = {'06386e1c': 'Session Auditor', '2f5a0935': 'Harness Engineer', '8e98843f': 'Probe Designer', 'aabc0a15': 'Lever Researcher',
        'dc34de0a': 'Red Team', 'eb15eb75': 'Emu Engineer', 'f1276629': 'Roadmap Lead', '641ba04e': 'First agent', '9cac1833': 'agent 9cac1833'}
AFTER = {'f1276629': 'b21f5b64', '2f5a0935': 'c6ab2111', '06386e1c': 'fd7e34ee'}
REST = ['ca226dd3', '9844cefa', '193b43fe', '92e128c1', 'b6b612b2', 'ee077e21', '96942b1c']
if os.path.isdir(co):
    for a in sorted(os.listdir(co)):
        p = '%s/%s/instructions/AGENTS.md' % (co, a)
        if os.path.isfile(p):
            h = sha(p)
            exp = AFTER.get(a[:8])
            st = ('= item 274 (b)' if h[:8] == exp else 'CHANGED since item 274 (b) (%s)' % exp) if exp else ('in the unchanged seven of item 274 (b)' if h[:8] in REST else 'NOT in the list of item 274 (b)')
            print('INSTR %s (%s): sha256 %s mtime %s size %d -> %s' % (a[:8], ROLE.get(a[:8], '?'), h[:8], iso(os.stat(p).st_mtime), os.path.getsize(p), st))
for nm, exp in (('docs/agent-team.md', '38c23579'), ('docs/platform-traps.md', '2a2c5a6b')):
    p = EM + '/' + nm
    print('DOC %s: sha256 %s mtime %s (item 274 (b): %s) -> %s' % (nm, sha(p)[:8], iso(os.stat(p).st_mtime), exp, 'same' if sha(p)[:8] == exp else 'changed'))
c, a = sha(EM + '/CLAUDE.md'), sha(EM + '/AGENTS.md')
print('CLAUDE.md sha256 %s size %d; AGENTS.md sha256 %s size %d; identical: %s' % (c, os.path.getsize(EM + '/CLAUDE.md'), a, os.path.getsize(EM + '/AGENTS.md'), c == a))
for name, root in (('KytyPS5', KY), ('ps5-em', EM)):
    r = subprocess.run([GIT, '-C', root, 'status', '--short'], capture_output=True)
    ls = [x for x in r.stdout.decode('utf-8', 'replace').splitlines() if x.strip()]
    print('STATUS %s: %d lines %s' % (name, len(ls), [x[:70] for x in ls[:12]]))
print('ALL DONE')
