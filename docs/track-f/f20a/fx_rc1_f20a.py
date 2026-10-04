# F20a RC1 (HPP-551, review of the lead): fixture of the sample rule 'a log whose LAST --shader-validation is true is
# out of the sample' - the whole chain meta_f20a.py -> sweep_f20a.py -> ana_f20a.py on six synthetic logs with tag json:
#   A  --shader-validation false                          strict in both variants
#   B  --shader-validation false ... true  (last true)    out in nosval, strict in asis; frame 150 ms at n 950
#   C  --shader-validation true ... false  (last false)   strict in both variants
#   D  --shader-validation true            (single)       out in nosval, strict in asis; frame 150 ms at n 950
#   E  no --shader-validation in the line                 strict in both variants
#   F  --vulkan-validation false ... true  (last true)    out by validation in both variants (control of 'last wins')
# Members: the fields of meta, the class and the reason of every log in both variants, N and the hits of the B2 section,
# the count line of section (1a).  With a second argument (the directory of the real records: list_f20a.tsv,
# meta_f20a.jsonl, sweep_all.jsonl, ana_f20a.txt as submitted) two more members: the variant 'asis' reproduces the
# submitted ana_f20a.txt line by line (variant marks and section (1a) removed), and the variant 'nosval' runs with its
# assertion 'no log of the sample has the flag true'.
# The work directory must not have 'fx' in a path component (such directories are fixtures for ana_f20a.py).
# Usage: python fx_rc1_f20a.py <work dir> [real dir]     prints 'ALL OK' and exits 0 when every member holds.
import json, os, re, subprocess, sys

wd = os.path.abspath(sys.argv[1]).replace(chr(92), '/')
real = sys.argv[2] if len(sys.argv) > 2 else None
here = os.path.dirname(os.path.abspath(__file__))
NL, TAB = chr(10), chr(9)
if re.search(r'/[^/]*fx[^/]*/', wd + '/'):
    print('FAIL work dir has fx in a path component:', wd)
    sys.exit(1)
os.makedirs(wd, exist_ok=True)
BASE = ['kyty_emulator.exe', '--screen-width', '1280', '--screen-height', '720', '--vulkan-validation', 'false']
SF, ST = ['--shader-validation', 'false'], ['--shader-validation', 'true']
GAME = ['--game', 'games/PPSA21564-app']
CASES = [('A', BASE + SF + GAME, False), ('B', BASE + SF + GAME + ST, True), ('C', BASE + ST + GAME + SF, False),
         ('D', BASE + ST + GAME, True), ('E', BASE + GAME, False), ('F', BASE + SF + GAME + ['--vulkan-validation', 'true'], False)]
ENV = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden'}
lst5, lst3 = [], []
for name, cl, slow in CASES:
    L = ['Fixture: ' + name]
    for n in range(1, 3):
        L.append('FrameTrace: n=%d dt_us=16000 cpu=1 draws=5 x=1' % n)
    L.append('GuestOut: Level has started: underwater_aerial_garden')
    for n in range(3, 1201):
        L.append('FrameTrace: n=%d dt_us=%d cpu=1 draws=200 x=1' % (n, 150000 if (slow and n == 950) else 16000))
    L.append('Event: quit')
    p = wd + '/log_%s.txt' % name
    with open(p, 'w', encoding='utf-8', newline=NL) as f:
        f.write(NL.join(L) + NL)
    j = wd + '/%s.json' % name
    with open(j, 'w', encoding='utf-8', newline=NL) as f:
        json.dump({'binary_sha256': '31cbfee8' + '0' * 56, 'cmdline': cl, 'env': ENV}, f)
    lst5.append(TAB.join([p, str(os.path.getsize(p)), '0', wd, j]))
    lst3.append(TAB.join([p, str(os.path.getsize(p)), 'sweep']))
with open(wd + '/list_f20a.tsv', 'w', encoding='utf-8', newline=NL) as f:
    f.write(NL.join(lst5) + NL)
with open(wd + '/plan.tsv', 'w', encoding='utf-8', newline=NL) as f:
    f.write(NL.join(lst3) + NL)
for fn in ('sweep_all.jsonl', 'meta_f20a.jsonl'):
    if os.path.exists(wd + '/' + fn):
        os.remove(wd + '/' + fn)
bad = []
members = 0


def chk(name, got, want):
    global members
    members += 1
    if got != want:
        bad.append('%s: got %r want %r' % (name, got, want))


def run(args, env=None):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, encoding='utf-8', env=env)
    return r.returncode, r.stdout, r.stderr


rc, o, e = run([here + '/meta_f20a.py', wd + '/list_f20a.tsv', wd + '/meta_f20a.jsonl'])
chk('meta rc', rc, 0)
env = dict(os.environ, F20A_LOCK=wd + '/no.lock', F20A_STOP=wd + '/no.stop')
rc, o, e = run([here + '/sweep_f20a.py', wd + '/plan.tsv', wd + '/sweep_all.jsonl', '60'], env)
chk('sweep complete', 'SWEEP COMPLETE' in o, True)
meta = {}
for l in open(wd + '/meta_f20a.jsonl', encoding='utf-8'):
    r = json.loads(l)
    meta[r['path'].rsplit('/', 1)[1][4]] = r
chk('meta shader_validation A..F', [meta[c]['shader_validation'] for c in 'ABCDEF'], ['false', 'true', 'false', 'true', None, 'false'])
chk('meta validation A..F', [meta[c]['validation'] for c in 'ABCDEF'], ['false'] * 5 + ['true'])


def ana(d, variant, extra=()):
    rc, o, e = run([here + '/ana_f20a.py', d, variant] + list(extra))
    return rc, o.split(NL), e


def classes(lines):
    out = {}
    for l in lines:
        if l.startswith('CLASS' + TAB):
            _, p, k, why = l.split(TAB)
            out[p.rsplit('/', 1)[1][4]] = (k, why)
    return out


def b2(lines, variant):
    i = [k for k, l in enumerate(lines) if l.startswith('[%s] (3) B2, sample strict' % variant)][0]
    m = re.match(r'  entries N = (\d+); entries with >= 1 frame: (\d+); frames: (\d+)', lines[i + 1])
    return tuple(int(x) for x in m.groups())


def count1a(lines):
    return [l for l in lines if l.startswith('  logs of the sample (strict or wide) with the flag true:')]


SV = 'flag --shader-validation true'
rc, o, e = ana(wd, 'nosval', ['--classes'])
chk('nosval rc', rc, 0)
c = classes(o)
chk('nosval classes', [c.get(x) for x in 'ABCDEF'],
    [('strict', '-'), ('out', SV), ('strict', '-'), ('out', SV), ('strict', '-'), ('out', 'validation')])
chk('nosval B2 (N, entries with a frame, frames)', b2(o, 'nosval'), (3, 0, 0))
chk('nosval (1a) count', count1a(o), ['  logs of the sample (strict or wide) with the flag true: 0'])
rc, o, e = ana(wd, 'asis', ['--classes'])
chk('asis rc', rc, 0)
c = classes(o)
chk('asis classes', [c.get(x) for x in 'ABCDEF'], [('strict', '-')] * 5 + [('out', 'validation')])
chk('asis B2 (N, entries with a frame, frames)', b2(o, 'asis'), (5, 2, 2))
chk('asis (1a) count', count1a(o), ['  logs of the sample (strict or wide) with the flag true: 2'])
rc, o, e = ana(wd, 'other')
chk('unknown variant refused', rc != 0, True)

if real:
    real = real.rstrip('/')
    rc, o, e = ana(real, 'asis')
    chk('real asis rc', rc, 0)
    body = []
    skip = False
    for l in o:
        if l.startswith('[asis] '):
            l = l[len('[asis] '):]
        if l.startswith('(1a) '):
            skip = True
            body.pop()                      # the blank line printed before the heading of (1a)
            continue
        if skip:
            if l == '':
                skip = False
            else:
                continue
        body.append(l)
    old = open(real + '/ana_f20a.txt', encoding='utf-8').read().split(NL)
    diff = [k for k in range(max(len(old), len(body))) if (old[k] if k < len(old) else None) != (body[k] if k < len(body) else None)]
    chk('real asis == submitted ana_f20a.txt (lines that differ)', (len(body), diff[:3]), (len(old), []))
    rc, o, e = ana(real, 'nosval')
    chk('real nosval rc (assertion: no log of the sample has the flag true)', rc, 0)
    chk('real nosval (1a) count', count1a(o), ['  logs of the sample (strict or wide) with the flag true: 0'])
for b in bad:
    print('FAIL', b)
print('members', members, 'failed', len(bad))
if not bad:
    print('ALL OK')
sys.exit(1 if bad else 0)
