# proto143.py - Session Auditor, s143 step 3 (HPP-300): protocol checks of steps 0-2 of s143 against the lock windows.
#  1. general rule 27: mtime (and creation time) of the files of the track roots against the windows of runs143/lock.log
#  2. step2/times.txt: one attempt per tag, order of the rows against the lock, sha256 of the logs
#  3. the seal pred/02_sc143.md: its sha256, its mtime before the first lock, every "seal:" line against the file now
#  4. sha256 of the s142 and s143 video outputs against the rows of times.txt (item 239 (b)(7))
# READ ONLY (writes nothing but stdout). Usage: python proto143.py
import os, re, json, hashlib, datetime, sys

UTC = datetime.timezone.utc
S143 = 'C:/kyty/s143'
S142 = 'C:/kyty/s142'


def ts(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC).timestamp()


def iso(t):
    return datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


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


W = windows(S143 + '/runs143/lock.log')
print('LOCK WINDOWS %d: first taken %s, last released %s; sum held %.0f s; gaps between tags min %.0f s max %.0f s' % (
    len(W), iso(W[0][1]), iso(W[-1][2]), sum(b - a for _, a, b in W),
    min(W[i + 1][1] - W[i][2] for i in range(len(W) - 1)), max(W[i + 1][1] - W[i][2] for i in range(len(W) - 1))))


def inwin(t):
    for tag, a, b in W:
        if a <= t <= b:
            return tag
    return None


# 1. rule 27
PRE0, PRE1 = ts('2026-10-01T02:04:28Z'), W[0][1]
ROOTS = [('p283', 'C:/kyty/p283'), ('f287', 'C:/kyty/f287'), ('s288', 'C:/kyty/s288'),
         ('KytyPS5/docs', 'C:/kyty/KytyPS5/docs'), ('KytyPS5/src', 'C:/kyty/KytyPS5/src'),
         ('ps5 em/docs', 'C:/kyty/KytyPS5/ps5 em/docs'), ('s143/lead', S143 + '/lead'), ('s143/step4', S143 + '/step4'),
         ('s142', S142), ('build', 'C:/kyty/build'), ('kyty root files', 'C:/kyty')]
for name, root in ROOTS:
    n = 0
    hits = []
    chits = []
    pre = []
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
                hits.append((st.st_mtime, t, p.replace('\\', '/')))
            c = inwin(st.st_ctime)
            if c and not t:
                chits.append((st.st_ctime, c, p.replace('\\', '/')))
            if PRE0 <= st.st_mtime < PRE1:
                pre.append((st.st_mtime, p.replace('\\', '/')))
    print('RULE27 %s: files %d; mtime inside a lock window %d; created inside a window (mtime outside) %d; mtime in %s..%s (after the API start row, before the first lock) %d' % (
        name, n, len(hits), len(chits), iso(PRE0), iso(PRE1), len(pre)))
    for m, t, p in sorted(hits)[:40]:
        print('   IN-LOCK %s %s %s' % (iso(m), t, p))
    for m, t, p in sorted(chits)[:15]:
        print('   CREATED-IN-LOCK %s %s %s' % (iso(m), t, p))
    for m, p in sorted(pre)[:25]:
        print('   PRE-LOCK %s %s' % (iso(m), p))

# 2. times.txt of step 2
rows = open(S143 + '/step2/times.txt', encoding='utf-8', errors='replace').read().splitlines()
bad = [r[:80] for r in rows if not re.match(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ ', r)]
print('TIMES step2: rows %d; rows without a leading UTC stamp %d %s' % (len(rows), len(bad), bad[:5]))
A = {r['tag']: r for r in json.load(open(S143 + '/step3/aud143.json'))}
tags = []
for i in range(1, 11):
    tags += ['v143_%02d' % i, 'w143_%02d' % i]
win = {t: (a, b) for t, a, b in W}
ok = True
prev_rel = None
for t in tags:
    r = [x for x in rows if (' go143a %s ' % t) in x or ('go143a.sh %s' % t) in x]
    calls = [x for x in rows if 'next_one' in x and x.rstrip().endswith('go143a.sh %s' % t)]
    st = [x for x in r if 'enter_scene start' in x]
    en = [x for x in r if 'enter_scene end' in x]
    busy = [x for x in r if ' BUSY ' in x]
    a, b = win.get(t, (None, None))
    msg = []
    if len(st) != 1 or len(en) != 1:
        msg.append('enter_scene start %d end %d' % (len(st), len(en)))
    else:
        t0, t1 = ts(st[0][:20]), ts(en[0][:20])
        if not (a <= t0 <= t1 <= b):
            msg.append('enter_scene %s..%s not inside the lock %s..%s' % (iso(t0), iso(t1), iso(a), iso(b)))
        m = re.search(r'sha256 ([0-9a-f]{64})', en[0])
        if not m or m.group(1) != A[t]['log']['sha256']:
            msg.append('log sha of the times row != the log now')
    if not calls:
        msg.append('no next_one call row')
    else:
        c0 = ts(calls[-1][:20])
        if prev_rel is not None and c0 < prev_rel:
            msg.append('the call row %s is before the previous release %s' % (iso(c0), iso(prev_rel)))
        if a is not None and c0 > a:
            msg.append('the call row is after the lock')
    lm = os.stat('%s/log_%s.txt' % (S143, t)).st_mtime
    if a is None or not (a <= lm <= b):
        msg.append('log mtime %s outside its lock' % iso(lm))
    att = os.path.isfile('%s/attempt_%s.txt' % (S143, t))
    js = A[t]['json']
    na = len(js.get('attempts', [])) if isinstance(js, dict) else None
    ok &= not msg
    print('TAG %s lock %s..%s (%.0f s) calls %d busy %d starts %d attempt file %s json attempts %s rc %s %s' % (
        t, iso(a) if a else None, iso(b) if b else None, (b - a) if a else 0, len(calls), len(busy), len(st), att, na,
        (re.search(r'end rc (\d+)', en[0]).group(1) if en else None), ('PROBLEM: ' + '; '.join(msg)) if msg else 'ok'))
    prev_rel = b
print('OLD DIR (stale moves of a second attempt): %s' % os.path.isdir(S143 + '/old'))
print('STOP FILE now: %s' % os.path.exists(S143 + '/STOP'))
print('TIMES/LOCK CHECK: %s' % ('ALL OK' if ok else 'PROBLEMS'))

# 3. the seal
seal = S143 + '/pred/02_sc143.md'
sm = os.stat(seal).st_mtime
print('SEAL 02 sha256 %s mtime %s (first lock %s) before the first lock: %s' % (sha(seal), iso(sm), iso(W[0][1]), sm < W[0][1]))
sok = True
nseal = 0
for ln in open(seal, encoding='utf-8').read().splitlines():
    m = re.match(r'seal: ([0-9a-f]{64}) (\S+)$', ln)
    if not m:
        continue
    nseal += 1
    p = m.group(2) if m.group(2).startswith('C:/') else S143 + '/' + m.group(2)
    h = sha(p)
    fm = os.stat(p).st_mtime if os.path.isfile(p) else 0
    good = (h == m.group(1)) and fm <= sm
    sok &= good
    if not good:
        print('   SEAL LINE %s: sha now %s (seal %s) mtime %s' % (m.group(2), h[:16], m.group(1)[:16], iso(fm)))
print('SEAL LINES %d: every file = its seal line and not modified after the seal: %s' % (nseal, 'ALL OK' if sok else 'PROBLEMS'))

# 4. video outputs against the rows of times.txt
for root, trow in ((S142, S142 + '/step2/times.txt'), (S143, S143 + '/step2/times.txt')):
    vok = True
    nfile = 0
    for ln in open(trow, encoding='utf-8', errors='replace').read().splitlines():
        for fn, h in re.findall(r'((?:glitch|rec|sheet|score)_\w+\.(?:txt|mp4|png)) sha256 ([0-9a-f]{64})', ln):
            nfile += 1
            now = sha(root + '/' + fn)
            if now != h:
                vok = False
                print('   OUTPUT %s/%s: sha now %s != times row %s' % (root, fn, now[:16], h[:16]))
    print('OUTPUT SHA %s: %d file rows (glitch, rec, sheet, score) against the files now: %s' % (root, nfile, 'ALL OK' if vok else 'DIFFERENCES'))
    for f in sorted(os.listdir(root)):
        if re.match(r'glitch_\w+\.txt$', f):
            tail = [x for x in open(root + '/' + f, encoding='utf-8', errors='replace').read().splitlines() if x.strip()][-1:]
            print('   %s last line: %s' % (f, tail[0][:140] if tail else None))
print('ALL DONE')
