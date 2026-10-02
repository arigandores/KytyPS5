# proto146.py - Session Auditor, s146 step 3 (HPP-389): protocol checks of the s145 close and of steps 0-2 of s146.
#  1. lock windows: runs146/lock.log (warm-up i146_v + the series) and every lock.log under the track roots since the s145 close
#  2. general rules 27-28: mtime of the files of the track roots, of the lead folders and of the repository docs against the
#     SESSION windows and the series window; files of the session steps against the TRACK windows; commits against all windows
#  3. step2/times.txt: per tag - gate row before the call, one lock per tag, one attempt; LEAD-OVERRIDE rows; BUSY rows;
#     foreign process names (masked, count only)
#  4. the seals pred/00_i146.md, 01, 02: sha256, mtime before the first lock, every "seal:" line against the file now, prereg
#  5. start rows of the steps against the commit times of the inputs they name
#  6. the install (item 300 (b)): sha256 of the binary now, of the pinned copy and of the source; rows of step0/times.txt
#  7. the s145 close: commit times, instruction files (sha256 prefixes against item 310 (c)), CLAUDE.md = AGENTS.md
# READ ONLY (writes nothing but stdout). Process names of BUSY rows are masked. Usage: python proto146.py
import os, re, json, hashlib, datetime, subprocess

UTC = datetime.timezone.utc
S146 = 'C:/kyty/s146'
GIT = 'C:/Program Files/Git/cmd/git.exe'
KY = 'C:/kyty/KytyPS5'
EM = 'C:/kyty/KytyPS5/ps5 em'
CLOSE145 = '2026-10-02T05:40:00Z'
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
WA, left, odd = windows(S146 + '/runs146/lock.log')
W = [w for w in WA if w[0] != 'i146_v']
WI = [w for w in WA if w[0] == 'i146_v']
gaps = [W[i + 1][1] - W[i][2] for i in range(len(W) - 1)]
tags = [w[0] for w in W]
print('SESSION LOCK WINDOWS %d = warm-up %d %s + series %d (distinct tags %d; taken without release %s; odd lines %d): series first taken %s, last released %s; '
      'sum held (series) %.0f s; gaps between tags min %.0f s, median %.0f s, max %.0f s (%s -> %s)' % (
          len(WA), len(WI), [(iso(a), iso(b)) for _, a, b in WI], len(W), len(set(tags)), left, odd, iso(W[0][1]), iso(W[-1][2]), sum(b - a for _, a, b in W),
          min(gaps), sorted(gaps)[len(gaps) // 2], max(gaps), tags[gaps.index(max(gaps))], tags[gaps.index(max(gaps)) + 1]))
SER = (W[0][1], W[-1][2])
big = sorted(((g, tags[i], tags[i + 1], W[i][2], W[i + 1][1]) for i, g in enumerate(gaps)), reverse=True)[:5]
for g, a, b, t0, t1 in big:
    print('   GAP %6.0f s between %s (released %s) and %s (taken %s)' % (g, a, iso(t0), b, iso(t1)))
for t, a, b in W:
    print('   LOCK %s %s..%s %4.0f s' % (t, iso(a), iso(b), b - a))
TW = []
for root in ('C:/kyty/p283', 'C:/kyty/f287', 'C:/kyty/s288'):
    for p, st in walk(root):
        if os.path.basename(p) == 'lock.log':
            w, lf, od = windows(p, ts(CLOSE145))
            for t, a, b in w:
                TW.append((a, b, t, p.replace('C:/kyty/', '')))
            print('TRACK LOCKLOG %s: windows since %s: %d; taken without release %s' % (p.replace('C:/kyty/', ''), CLOSE145, len(w), lf))
TW.sort()
for a, b, t, p in TW:
    print('   TRACK WINDOW %s..%s %4.0f s %s (%s)%s' % (iso(a), iso(b), b - a, t, p, '  <== INSIDE THE SERIES WINDOW' if SER[0] <= a <= SER[1] else ''))
print('TRACK WINDOWS since %s: %d; inside the series window %s..%s: %d' % (CLOSE145, len(TW), iso(SER[0]), iso(SER[1]), sum(1 for a, b, t, p in TW if SER[0] <= a <= SER[1])))


def insess(t):
    for tag, a, b in WA:
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
                    ('lead (s146/lead, s146/step4, s145/step4)', [S146 + '/lead', S146 + '/step4', 'C:/kyty/s145/step4']),
                    ('red team and link 1b (s146/step1, s146/step1b)', [S146 + '/step1', S146 + '/step1b']),
                    ('repository docs (KytyPS5/docs/track-p, track-f, track-s, session-145, session-146, agent)',
                     [KY + '/docs/track-p', KY + '/docs/track-f', KY + '/docs/track-s', KY + '/docs/session-145', KY + '/docs/session-146', KY + '/docs/agent']),
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
    for m, t, p, sz in sorted(inl)[:40]:
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
    for m, p, sz in sorted(inser)[:25]:
        print('      file %s %s (%d bytes)' % (iso(m), p.replace('C:/kyty/', ''), sz))
# files of the session root itself (not the run outputs) written inside the series window by somebody else than the harness
other = []
for f in sorted(os.listdir(S146)):
    p = S146 + '/' + f
    if os.path.isfile(p) and not re.match(r'(log_|rec_|stdout_|sheet_|glitch_|gpuclk_|score_|attempt_|tiles_|skipped_|[rvw]146_|go146a[.]log|gates[.]req|FACTS[.]md)', f):
        m = os.stat(p).st_mtime
        if SER[0] <= m <= SER[1]:
            other.append((iso(m), f, insess(m)))
print('S146 ROOT files (not run outputs) with mtime inside the series window: %d %s' % (len(other), other))
# session step files under the TRACK windows
hits = []
n = 0
for p, st in walk(S146):
    if '/runs146/' in p or re.search(r'/(log_|rec_|stdout_|sheet_|glitch_|gpuclk_|score_|attempt_|tiles_|[rvw]146_)', p):
        continue
    n += 1
    t = intrack(st.st_mtime)
    if t:
        hits.append((st.st_mtime, t, p))
print('S146 STEP FILES %d (without run outputs, mutant work folders, fixtures); mtime inside a TRACK lock window: %d' % (n, len(hits)))
for m, t, p in sorted(hits)[:40]:
    print('   IN-TRACK-LOCK %s under %s %s' % (iso(m), t, p.replace('C:/kyty/', '')))
# commits
for name, root in (('KytyPS5', KY), ('ps5-em', EM)):
    r = subprocess.run([GIT, '-C', root, 'log', '--since=' + CLOSE145, '--format=%h %ct %s'], capture_output=True)
    lines = r.stdout.decode('utf-8', 'replace').splitlines()
    ks = kt = kw = 0
    for ln in lines:
        h, ct, subj = ln.split(' ', 2)
        s, t = insess(int(ct)), intrack(int(ct))
        sub = subj[:110].encode('ascii', 'replace').decode()
        if s:
            ks += 1
            print('   COMMIT-IN-SESSION-LOCK %s %s %s under %s: %s' % (name, h, iso(int(ct)), s, sub))
        if t:
            kt += 1
            print('   COMMIT-IN-TRACK-LOCK %s %s %s under %s: %s' % (name, h, iso(int(ct)), t, sub))
        if SER[0] <= int(ct) <= SER[1]:
            kw += 1
            if not s:
                print('   COMMIT-IN-SERIES-WINDOW %s %s %s: %s' % (name, h, iso(int(ct)), sub))
    print('COMMITS %s since %s: %d; inside a session lock window %d; inside a track lock window %d; inside the series window %d' % (name, CLOSE145, len(lines), ks, kt, kw))

# 3. times.txt of step 2
order = ['w146_00'] + ['r146_%02d' % i for i in range(1, 5)]
for i in range(5, 20):
    order += ['v146_%02d' % i, 'w146_%02d' % i]
T = open(S146 + '/step2/times.txt', encoding='utf-8', errors='replace').read().splitlines()
rows = []
for ln in T:
    m = re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) (.*)', ln)
    if m:
        rows.append((ts(m.group(1)), m.group(2)))
print('TIMES step2: lines %d, rows with a leading UTC time %d; non-monotonic rows %d; sha256 %s' % (
    len(T), len(rows), sum(1 for a, b in zip(rows, rows[1:]) if b[0] < a[0]), sha(S146 + '/step2/times.txt')))
for a, b in zip(rows, rows[1:]):
    if b[0] < a[0]:
        print('   NON-MONOTONIC %s after %s: %s' % (iso(b[0]), iso(a[0]), b[1][:110]))
gate = [(t, x) for t, x in rows if x.startswith('GATE ')]
print('GATE rows %d: start %d, PASS %d (of them LEAD-OVERRIDE %d), STOP %d' % (
    len(gate), sum(1 for t, x in gate if x.startswith('GATE start')), sum(1 for t, x in gate if re.match(r'GATE [rvw]\S+ PASS', x)),
    sum(1 for t, x in gate if 'LEAD-OVERRIDE' in x), sum(1 for t, x in gate if re.match(r'GATE \S+ STOP', x))))
for t, x in gate:
    if 'LEAD-OVERRIDE' in x or re.match(r'GATE \S+ STOP', x):
        print('   %s %s' % (iso(t), x[:330]))
okg = True
for tag, a, b in W:
    g = [(t, x) for t, x in gate if x.startswith('GATE %s ' % tag) and t <= a]
    last = g[-1] if g else None
    calls = [t for t, x in rows if ('call: PLWAIT=540 bash C:/kyty/s146/go146a.sh %s' % tag) in x]
    good = last is not None and ' PASS' in last[1][:30] and any(last[0] <= c <= a for c in calls)
    okg &= good
    if not good or 'LEAD-OVERRIDE' in (last[1] if last else '') or len(calls) != 1:
        print('   TAG %s: lock taken %s; last gate row before it %s "%s"; call rows %s -> %s' % (
            tag, iso(a), iso(last[0]) if last else None, last[1][:60] if last else None, [iso(c) for c in calls], 'ok' if good else 'VIOLATED'))
print('EVERY LOCK PRECEDED BY A GATE PASS ROW AND A CALL ROW OF ITS TAG: %s; order of the locks = the sealed order: %s' % (okg, tags == order))
busy = [(t, x) for t, x in rows if ' BUSY ' in x and x.startswith('go146a ')]
for t, x in busy:
    print('   BUSY %s %s' % (iso(t), re.sub(r"busy \[\('[^']*'", "busy [('<name>'", x)[:150]))
att = {t: os.path.isfile('%s/attempt_%s.txt' % (S146, t)) for t in order}
js = {}
for t in order:
    try:
        js[t] = json.load(open('%s/%s.json' % (S146, t), encoding='utf-8'))
    except (OSError, ValueError):
        js[t] = None
print('ATTEMPT FILES %d of %d; json present %d (missing %s); attempts per json %s; locks per tag max %d; enter_scene start rows per tag %s; skipped_*.txt files %s' % (
    sum(att.values()), len(order), sum(1 for v in js.values() if v), [t for t, v in js.items() if not v],
    sorted(set(len(v.get('attempts') or []) for v in js.values() if v)), max(tags.count(t) for t in order),
    sorted(set(sum(1 for _, x in rows if x.startswith('go146a %s enter_scene start' % t)) for t in order)),
    [f for f in os.listdir(S146) if f.startswith('skipped_')]))
# foreign process names in the step files: any name inside the TOP / busy lists that is not the mask
for step in ('step0', 'step1', 'step1b', 'step2'):
    p = '%s/%s/times.txt' % (S146, step)
    tx = open(p, encoding='utf-8', errors='replace').read()
    names = re.findall(r"\('([^'<][^']*)', \d+, [0-9.]+\)", tx) + re.findall(r'top ((?!<app>)[A-Za-z][\w .+-]*):\d+:[0-9.]+', tx) + re.findall(r', ((?!<app>)[A-Za-z][\w.+-]*):\d+:0[.]\d+', tx)
    masked = len(re.findall(r'<app>', tx))
    lines_with = sorted(set(ln[:20] for ln in tx.splitlines() if re.search(r"\('[^'<][^']*', \d+, [0-9.]+\)|(?:top |, )(?!<app>)[A-Za-z][\w.+-]*:\d+:0[.]\d+", ln)))
    print('NAMES %s/times.txt: unmasked process-name tokens %d in rows %s; <app> masks %d' % (step, len(names), lines_with[:6], masked))
gl = open(S146 + '/go146a.log', encoding='utf-8', errors='replace').read()
print('go146a.log: "enter_scene start" rows %d; "procload: busy" rows %d; unmasked names in busy rows %d; "files:" rows %d (distinct %d)' % (
    len(re.findall(r'enter_scene start', gl)), len(re.findall(r'procload: busy', gl)), len(re.findall(r"busy \[\('[^'<]", gl)),
    len(re.findall(r'(?m)^.*files:.*$', gl)), len(set(re.sub(r'^\S+ \S+ ', '', x) for x in re.findall(r'(?m)^.*files:.*$', gl)))))
old = S146 + '/step2/old'
print('step2/old: %s' % (sorted(os.listdir(old)) if os.path.isdir(old) else 'absent'))

# 4. the seals
for nm in ('pred/00_i146.md', 'pred/01_sc146.md', 'pred/02_sc146.md'):
    seal = S146 + '/' + nm
    sh = sha(seal)
    sm = os.stat(seal).st_mtime
    first = WI[0][1] if nm.startswith('pred/00') else W[0][1]
    print('SEAL %s sha256 %s mtime %s; first lock it governs %s; seal before the first lock: %s' % (nm, sh, iso(sm), iso(first), sm < first))
    if nm == 'pred/01_sc146.md':
        continue
    bad = late = ns = 0
    for ln in open(seal, encoding='utf-8').read().splitlines():
        m = re.match(r'seal: ([0-9a-f]{64}) (\S+)', ln)
        if not m:
            continue
        ns += 1
        p = m.group(2) if m.group(2).startswith('C:/') else S146 + '/' + m.group(2)
        now = sha(p)
        mt = os.stat(p).st_mtime if os.path.isfile(p) else None
        if now != m.group(1):
            bad += 1
            print('   SEAL LINE DIFFERS %s: seal %s now %s (mtime %s)' % (m.group(2), m.group(1)[:16], now[:16], iso(mt)))
        if mt is not None and mt > sm:
            late += 1
            print('   SEALED FILE mtime after the seal: %s %s' % (m.group(2), iso(mt)))
    print('   SEAL LINES %d: files differing now %d; files with mtime after the seal %d; call lines %d' % (
        ns, bad, late, len(re.findall(r'(?m)^go146[ai] call: ', open(seal, encoding='utf-8').read()))))
sh2 = sha(S146 + '/pred/02_sc146.md')
pr = {t: ((v.get('prereg') or {}).get('sha256'), v.get('binary_sha256')) for t, v in js.items() if v}
print('JSON prereg = seal 02: %d of %d %s; binary dac02fb9: %d of %d' % (
    sum(1 for a, b in pr.values() if a == sh2), len(pr), sorted(set(str(a)[:8] for a, b in pr.values())), sum(1 for a, b in pr.values() if str(b).startswith('dac02fb9')), len(pr)))

# 5. start rows of the steps against the commits they name
for step in ('step0', 'step1', 'step1b', 'step2'):
    L = open('%s/%s/times.txt' % (S146, step), encoding='utf-8', errors='replace').read().splitlines()
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

# 6. the install
exe = EM + '/kyty_emulator.exe'
print('INSTALL now: kyty_emulator.exe sha256 %s (mtime %s); pinned copy s146 %s; source f287/bin %s; rollback s128 %s' % (
    sha(exe), iso(os.stat(exe).st_mtime), sha(S146 + '/kyty_emulator_dac02fb9.exe')[:16], sha('C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe')[:16],
    sha('C:/kyty/s128/kyty_emulator_9235a7ac.exe')[:16]))
for ln in open(S146 + '/step0/times.txt', encoding='utf-8', errors='replace').read().splitlines():
    if re.search(r'sha256 before|sha256 after|pinned|lock taken|lock released|cache manifest|GLCache|WARMUP VERDICT|install', ln) and ts(ln[:20]) < ts('2026-10-02T07:01:00Z'):
        print('   STEP0 %s' % re.sub(r"\('[^'<][^']*'", "('<name>'", ln)[:260])

# 7. the s145 close
for name, root, hs in (('KytyPS5', KY, ['6aaff10f', '62bd7f2f', '5ef50069', '23d64824']), ('ps5-em', EM, ['57680b2', '09f4d00'])):
    for h in hs:
        r = subprocess.run([GIT, '-C', root, 'show', '-s', '--format=%ct %s', h], capture_output=True)
        o = r.stdout.decode('utf-8', 'replace').strip()
        if o:
            ct, subj = o.split(' ', 1)
            print('CLOSE145 COMMIT %s %s %s (session lock %s, track lock %s): %s' % (name, h, iso(int(ct)), insess(int(ct)), intrack(int(ct)), subj[:110].encode('ascii', 'replace').decode()))
home = os.environ.get('USERPROFILE', '').replace(chr(92), '/')
co = home + '/.paperclip/instances/default/companies/f6a17988-768c-4cca-805c-868da6fede4f/agents'
ROLE = {'06386e1c': 'Session Auditor', '2f5a0935': 'Harness Engineer', '8e98843f': 'Probe Designer', 'aabc0a15': 'Lever Researcher',
        'dc34de0a': 'Red Team', 'eb15eb75': 'Emu Engineer', 'f1276629': 'Roadmap Lead', '641ba04e': 'First agent', '9cac1833': 'agent 9cac1833'}
AFTER = {'f1276629': 'e7d85565', '2f5a0935': 'd148f802', '06386e1c': '054d84d3', 'eb15eb75': '87c251a1', 'dc34de0a': '6aebc723', '8e98843f': 'e43a22e0',
         'aabc0a15': '8133de87'}
BEFORE = {'f1276629': 'b21f5b64', '2f5a0935': 'c6ab2111', '06386e1c': 'fd7e34ee', 'eb15eb75': '96942b1c', 'dc34de0a': 'b6b612b2', '8e98843f': '9844cefa',
          'aabc0a15': '92e128c1'}
REST = ['ca226dd3', '193b43fe', 'ee077e21']
n_ok = n_all = 0
if os.path.isdir(co):
    for a in sorted(os.listdir(co)):
        p = '%s/%s/instructions/AGENTS.md' % (co, a)
        if os.path.isfile(p):
            h = sha(p)
            exp = AFTER.get(a[:8])
            good = (h[:8] == exp) if exp else (h[:8] in REST)
            n_all += 1
            n_ok += good
            st = ('= item 310 (c) after (before %s)' % BEFORE[a[:8]] if h[:8] == exp else 'CHANGED since item 310 (c) (%s)' % exp) if exp else (
                'in the unchanged three of item 310 (c)' if h[:8] in REST else 'NOT in the list of item 310 (c)')
            print('INSTR %s (%s): sha256 %s mtime %s size %d -> %s' % (a[:8], ROLE.get(a[:8], '?'), h[:8], iso(os.stat(p).st_mtime), os.path.getsize(p), st))
print('INSTR files %d; equal to the "after" row of item 310 (c): %d' % (n_all, n_ok))
isf = 'C:/kyty/s145/step4/instr_sha.txt'
if os.path.isfile(isf):
    tx = open(isf, encoding='utf-8', errors='replace').read()
    print('INSTR before-table %s sha256 %s mtime %s lines %d; "before" prefixes of item 310 (c) found in it: %d of %d; unchanged three found: %d of 3' % (
        isf, sha(isf)[:16], iso(os.stat(isf).st_mtime), len(tx.splitlines()), sum(1 for v in BEFORE.values() if v in tx), len(BEFORE), sum(1 for v in REST if v in tx)))
for nm, exp in (('docs/agent-team.md', '9e5063a5'), ('docs/platform-traps.md', '157c61c3')):
    p = EM + '/' + nm
    print('DOC %s: sha256 %s mtime %s (item 310 (c): %s) -> %s' % (nm, sha(p)[:8], iso(os.stat(p).st_mtime), exp, 'same' if sha(p)[:8] == exp else 'changed'))
c, a = sha(EM + '/CLAUDE.md'), sha(EM + '/AGENTS.md')
print('CLAUDE.md sha256 %s size %d; AGENTS.md sha256 %s size %d; identical: %s' % (c, os.path.getsize(EM + '/CLAUDE.md'), a, os.path.getsize(EM + '/AGENTS.md'), c == a))
for name, root in (('KytyPS5', KY), ('ps5-em', EM)):
    r = subprocess.run([GIT, '-C', root, 'status', '--short'], capture_output=True)
    ls = [x for x in r.stdout.decode('utf-8', 'replace').splitlines() if x.strip()]
    print('STATUS %s: %d lines %s' % (name, len(ls), [x[:70] for x in ls[:12]]))
print('ALL DONE')
