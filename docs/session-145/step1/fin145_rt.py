# Red Team s145 step 1: pending checks after the lock, fill the review, copies to git (third-party layer name -> <app>).
# Usage: python fin145_rt.py <scratch dir> <lock end text>
import os, re, sys, hashlib, subprocess, difflib, shutil, time
SCR = sys.argv[1]
LOCKEND = sys.argv[2]
S1 = 'C:/kyty/s145/step1'
DOC = 'C:/kyty/KytyPS5/docs/session-145'
GIT = 'C:/Program Files/Git/cmd/git.exe'
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - abort'); sys.exit(3)
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 24), b''):
            h.update(b)
    return h.hexdigest()
def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
out = []
# (1) ROADMAP items after 291
rm = open('C:/kyty/KytyPS5/docs/ROADMAP.md', encoding='utf-8').read().split('\n')
head = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()
after = [l[:140] for l in rm if re.match(r'^(29[2-9]|3\d\d)\. ', l)]
RM = ('пункты после 291 перечитаны перед сдачей (KytyPS5 `%s`): %s' % (head, '; '.join(a.split('**')[1][:110] if '**' in a else a[:110] for a in after))) if after else (
    'пунктов после 291 перед сдачей нет (KytyPS5 `%s`)' % head)
out.append('RM ' + RM)
# (2) scorer of the counted mutant run vs now
old = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', 'b25ef509:docs/session-145/step0/sc145.py'], capture_output=True).stdout
cur = open('C:/kyty/s145/sc145.py', 'rb').read()
if old:
    so = hashlib.sha256(old).hexdigest()
    d = [l for l in difflib.unified_diff(old.decode('utf-8', 'replace').split('\n'), cur.decode('utf-8', 'replace').split('\n'), lineterm='', n=0)
         if (l.startswith('+') or l.startswith('-')) and not l.startswith('+++') and not l.startswith('---')]
    SCDIFF = ('копия в git `b25ef509:docs/session-145/step0/sc145.py` — sha256 `%s…`%s; против нынешнего `dd93bb1e…` — %d строк разности: %s' % (
        so[:8], ' (= 001cb6af)' if so.startswith('001cb6af') else ' (≠ 001cb6af — копия, не оригинал)', len(d), ' / '.join(x.strip()[:90] for x in d)))
else:
    SCDIFF = 'копии зачётного скорера в `b25ef509` нет — разность против `001cb6af` не проверена'
out.append('SCDIFF ' + SCDIFF)
# (3) v144_09 against the s144 times
tp = 'C:/kyty/s144/step2/times.txt'
lines = open(tp, encoding='utf-8', errors='replace').read().split('\n')
last = None; rec = None; sht = None
for l in lines:
    m = re.search(r'go144a v144_09 enter_scene end rc \S+ log_v144_09\.txt sha256 ([0-9a-f]{64})', l)
    if m: last = m.group(1)
    m = re.search(r'go144a v144_09 s51_vidglitch rc \S+ glitch_v144_09\.txt sha256 \S* rec_v144_09\.mp4 sha256 ([0-9a-f]{64})', l)
    if m: rec = m.group(1)
    m = re.search(r'go144a v144_09 sheet rc \S+ sheet_v144_09\.png sha256 ([0-9a-f]{64})', l)
    if m: sht = m.group(1)
lv = sha('C:/kyty/s144/log_v144_09.txt'); rv = sha('C:/kyty/s144/rec_v144_09.mp4'); sv = sha('C:/kyty/s144/sheet_v144_09.png')
ts = sha(tp)
V14409 = ('sha256 `C:/kyty/s144/log_v144_09.txt` `%s…` %s последней строке `go144a v144_09 enter_scene end` (`%s…`); видео `%s…` %s строке `s51_vidglitch`; лист `%s…` %s строке `sheet`; `times.txt` с. 144 `%s…` %s строке печати `6867bf88…`' % (
    lv[:16], '=' if lv == last else '≠', (last or 'нет')[:16], rv[:16], '=' if rv == rec else '≠', sv[:16], '=' if sv == sht else '≠', ts[:16],
    '=' if ts.startswith('6867bf88') else '≠'))
out.append('V14409 ' + V14409)
# (4) fgcpu / cachemf ports
def port(a, b, x, y):
    A = open(a, encoding='utf-8').read().replace(x, 'NNN'); B = open(b, encoding='utf-8').read().replace(y, 'NNN')
    d = [l for l in difflib.unified_diff(A.split('\n'), B.split('\n'), lineterm='', n=0) if l[:1] in '+-' and not l.startswith(('+++', '---'))]
    return d
d1 = port('C:/kyty/s144/fgcpu144.py', 'C:/kyty/s145/fgcpu145.py', '144', '145')
d2 = port('C:/kyty/s144/cachemf144.py', 'C:/kyty/s145/cachemf145.py', '144', '145')
FGCPU = '`fgcpu145.py` против `C:/kyty/s144/fgcpu144.py` при замене 144 → 145: %d строк разности%s; `cachemf145.py` против `cachemf144.py`: %d%s' % (
    len(d1), (' (' + ' / '.join(x.strip()[:80] for x in d1[:4]) + ')') if d1 else '', len(d2), (' (' + ' / '.join(x.strip()[:80] for x in d2[:4]) + ')') if d2 else '')
out.append('FGCPU ' + FGCPU)
# (5) shas of own outputs
SH = dict((k, sha('%s/%s' % (S1, f))) for k, f in (('VKSCAN', 'vkscan145_rt.out.txt'), ('VUIDH', 'vuidhash145_rt.out.txt'),
                                                   ('VCONT', 'vcont145_rt.out.txt'), ('F6TIME', 'f6time145_rt.out.txt')))
for k, v in SH.items():
    out.append('%s %s' % (k, v))
print('\n'.join(out))
# times line for this script's findings (before the table is built)
with open(S1 + '/times.txt', 'a', encoding='utf-8') as f:
    f.write('%s fin145_rt.py checks: %s | %s | %s | %s\n' % (utc(), RM[:200], SCDIFF[:200], V14409[:300], FGCPU[:200]))
T = open(S1 + '/times.txt', encoding='utf-8').read().rstrip('\n').split('\n')
TIMES = '| UTC | событие |\n|---|---|\n' + '\n'.join('| %s | %s |' % (l[:20], l[21:].replace('|', '/')[:300]) for l in T if l.strip())
rv = open(SCR + '/review145.md', encoding='utf-8').read()
for k, v in dict(RM=RM, SCDIFF=SCDIFF, V14409=V14409, FGCPU=FGCPU, LOCKEND=LOCKEND, TIMES=TIMES, **SH).items():
    rv = rv.replace('{{%s}}' % k, v)
left = re.findall(r'\{\{[A-Z0-9]+\}\}', rv)
if left:
    print('PLACEHOLDERS LEFT', left); sys.exit(1)
if os.path.exists(LOCK):
    print('LOCK present - abort before writing'); sys.exit(3)
os.makedirs(DOC + '/step1', exist_ok=True)
open(DOC + '/review145.md', 'wb').write(rv.encode('utf-8'))
open(S1 + '/review145.md', 'wb').write(rv.encode('utf-8'))
# copies of the step-1 files; the loader line of the third-party implicit layer -> <app>
RX = re.compile(rb'Removing layer \S+ \([^)]*\)')
for f in sorted(os.listdir(S1)):
    p = S1 + '/' + f
    if not os.path.isfile(p) or f == 'review145.md':
        continue
    b = open(p, 'rb').read()
    nb, n = RX.subn(b'Removing layer <app> (<app>)', b)
    if n:
        nb += ('(copy for git: %d third-party layer names replaced by <app>; sha256 of the local original %s)\n' % (n, hashlib.sha256(b).hexdigest())).encode()
    open(DOC + '/step1/' + f, 'wb').write(nb)
RS = sha(DOC + '/review145.md')
print('review sha256', RS)
print('copies', len(os.listdir(DOC + '/step1')))
fx = open(SCR + '/facts1.md', encoding='utf-8').read().replace('{{REVSHA}}', RS).replace('{{LOCKEND}}', LOCKEND).replace('{{TIMES}}', TIMES)
if re.findall(r'\{\{[A-Z0-9]+\}\}', fx):
    print('FACTS PLACEHOLDERS LEFT'); sys.exit(1)
if os.path.exists(LOCK):
    print('LOCK present - abort before FACTS'); sys.exit(3)
with open('C:/kyty/s145/FACTS.md', 'ab') as f:
    f.write(fx.encode('utf-8'))
print('FACTS sha256', sha('C:/kyty/s145/FACTS.md'))
