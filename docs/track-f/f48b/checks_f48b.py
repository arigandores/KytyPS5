# F48b (HPP-831): the one-off checks of the review, saved as one script (read-only; exit 3 on lock/STOP).
#   outline  - is the 'outcome_line' of census_f48a.tsv a table row of that id (first cell)?          -> outline_f48b.out.txt
#   codecmp  - own last outcome row word (census_f48b.tsv) = F48a code?                                -> codecmp_f48b.out.txt
#   outmask  - signatures of the stand logs outside the F48a mask (sw_f32b.py output outmask.json) not in the F0/F32a/F32d/F48a
#              tables; logs with >= 2 '--- Fatal Error ---' and torn 'LogAsync' summary lines by arm  -> outmask_f48b.out.txt
#   f5pre    - form (A) keys of F5 branch 2 before the scene (forma_f48a.scan/form_a, its own boundary) on F46c logs -> f5pre_f48b.out.txt
# Usage: python checks_f48b.py outline|codecmp|outmask|f5pre
import os, re, sys, json, glob, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    sys.exit(3)
HERE = os.path.dirname(os.path.abspath(__file__))
REG = 'C:/kyty/f287/f48b/reg.md'   # git show d336bb44:docs/track-f/register.md
IDRE = re.compile(r'(?<![\w`])([БФ]\d+[абвгд]?(?:-H)?)(?![\w])')


def outline():
    L = open(REG, encoding='utf-8').read().split('\n')
    bad = []; n = 0
    for l in open(HERE + '/../f48a/census_f48a.tsv', encoding='utf-8').read().split('\n')[1:]:
        if not l.strip():
            continue
        c = l.split('\t'); k = c[0]
        m = re.match(r's[\d.]+:(\d+)', c[4])
        if not m:
            continue
        n += 1
        line = L[int(m.group(1)) - 1]
        if not (line.startswith('|') and k in IDRE.findall(re.sub(r'\(.*', '', line.strip().strip('|').split('|')[0]))):
            bad.append((k, c[1], c[4], line[:160]))
    print('outcome_line checked', n, 'not a row of this id', len(bad))
    for b in bad:
        print(b)


def codecmp():
    rows = [l.split('\t') for l in open(HERE + '/census_f48b.tsv', encoding='utf-8').read().split('\n')[1:] if l.strip()]
    mis = []; ok = 0
    M = {'FIXED': 'FIXED', 'FIXED+REM': 'FIXED', 'NE_DEFEKT': 'NE_DEFEKT', 'NE_DEFEKT+REM': 'NE_DEFEKT', 'TUPIK': 'TUPIK',
         'TRACK_S': 'TUPIK', 'DUBL': 'DUBL', 'SPLIT': 'SPLIT'}
    for r in rows:
        if r[6] == 'K5':
            continue
        words = r[4].split()[1].split(',') if r[4] != 'NONE' else []
        if M[r[6]] in words:
            ok += 1
        else:
            mis.append((r[0], r[6], r[4], r[1][:40]))
    print('K1-K4+dubl+split ids', ok + len(mis), 'own last outcome row word = F48a code', ok)
    for m in mis:
        print('MISMATCH', m)


def sigs(p):
    L = open(p, encoding='utf-8').read().split('\n'); i = L[0].split('\t').index('signature')
    return {l.split('\t')[i] for l in L[1:] if l.strip()}


def outmask():
    known = (sigs('C:/kyty/f287/f0/sig_f0.tsv') | sigs('C:/kyty/f287/f32a/sig_f32a.tsv') | sigs('C:/kyty/f287/f32d/sw/sig_f32a.tsv')
             | sigs(HERE + '/../f48a/sig_f48a.tsv'))
    print('known signatures', len(known))
    res = json.load(open('C:/kyty/f287/f48b/outmask.json', encoding='utf-8'))
    c = collections.Counter(); ex = {}; fork = collections.Counter(); fat = fat2 = 0
    dbl = collections.Counter(); torn = collections.Counter()
    for r in res:
        fork[r['fork']] += 1
        nf = sum(1 for n, l in r['fatal_lines'] if 'Fatal Error' in l)
        fat += nf > 0; fat2 += nf > 1
        d = re.sub(r'/[^/]*$', '', r['path'])
        if nf > 1:
            dbl[(d, r['fork'])] += 1
        for s in r['sigs']:
            if s not in known:
                c[s] += 1; ex.setdefault(s, r['path'] + ':' + str(r['ex'][s]))
            if 'ogAsync: full_waits' in s and not s.startswith('LogAsync'):
                torn[(d, r['fork'], s[:12])] += 1
    print('logs', len(res), 'by build', dict(fork), 'with fatal', fat, 'with >=2 fatal lines', fat2)
    print('signatures not in F0/F32a/F32d/F48a tables:', len(c))
    for s, v in c.most_common():
        print(v, '\t', s[:150], '\t', ex[s])
    print('logs with >=2 "--- Fatal Error ---" lines by arm directory:')
    for k, v in sorted(dbl.items()):
        print(v, k)
    print('torn LogAsync summary lines by arm:')
    for k, v in sorted(torn.items()):
        print(v, k)


def f5pre():
    sys.path.insert(0, HERE + '/../f48a')
    import forma_f48a as F
    tot = logs = 0
    for p in sorted(glob.glob('C:/kyty/f287/f46c/log_f26s_*.txt')):
        lvl, armed, ev, nxt, kp, kl = F.scan(p)
        if not armed:
            continue
        logs += 1
        pre = [e for e in ev if lvl is None or e[0] <= lvl]
        a = set()
        for e in pre:
            nx = next((x for x in nxt if x[0] > e[0] and x[1] == e[1]), None)
            if F.form_a(e[3], nx):
                a.add(e[2])
        tot += len(a)
        print(os.path.basename(p), 'pre-scene events', len(pre), 'form (A) keys before scene', len(a), sorted(k[0] for k in a))
    print('logs', logs, 'form (A) keys before scene total', tot)


{'outline': outline, 'codecmp': codecmp, 'outmask': outmask, 'f5pre': f5pre}[sys.argv[1]]()
