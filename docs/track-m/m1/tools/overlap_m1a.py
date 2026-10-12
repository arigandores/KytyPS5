"""M1a (HPP-835), member (3) of ROADMAP p.752(g): mechanical place-overlap of every upstream commit with OUR changes in the
files that carry our knobs (KYTY_FIX_*, KYTY_S_*, KYTY_PVAR*, KYTY_GAME_PATCH) at b3dc9c67.

Coordinates: base 6a2987a7 lines. Our hunks: git diff -U0 6a2987a7 b3dc9c67 -- F; a hunk is a KNOB hunk if its added text
matches KNOB_RE. Upstream commit C hunks: git diff -U0 C^ C -- F (C^ coordinates), mapped to base through git diff -U0
6a2987a7 C^ -- F (lines outside its hunks shift by offset; lines inside an upstream-changed region map onto that base
region). Overlap: base ranges intersect with margin M = 3 lines. Output overlap.tsv: sha, file, n_hunks, knob_overlap
(our knob hunks hit, with knob names), other_overlap (our non-knob hunks hit), knobs_in_file.
Read-only; refuses to run under C:/kyty/SEALED_RUN.lock."""
import json, os, re, subprocess, sys, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
BASE, OURS = '6a2987a7', 'b3dc9c67'
D = 'C:/kyty/m657/m1a/'
M = 3
KNOB_RE = re.compile(r'KYTY_(?:FIX_\w+|S_\w+|PVAR\w*|GAME_PATCH)|\bFix(?:B|F)\d+\w*|\bFixB\w+|\bFixF\w+|DualSrc\w*|'
                     r'\bMinimize\w*|JoyPump|LogAsync|PadOutput|ShaderReplay|\bPvar\w*|GamePatch\w*|\bPcw\w*|S_PCW')
NAME_RE = re.compile(r'KYTY_(?:FIX_[A-Z0-9]+|S_[A-Z0-9_]+|PVAR[A-Z0-9_]*|GAME_PATCH)')
HUNK = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')

def git(*a):
    return subprocess.run([GIT, '-C', REPO] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')

def hunks(diff):
    out = []
    cur = None
    for l in diff.split('\n'):
        m = HUNK.match(l)
        if m:
            bs, bl, ns, nl = int(m.group(1)), int(m.group(2) or 1), int(m.group(3)), int(m.group(4) or 1)
            cur = [bs, bl, ns, nl, []]
            out.append(cur)
        elif cur is not None and l.startswith('+') and not l.startswith('+++'):
            cur[4].append(l[1:])
    return out

def mapper(cum):
    """cum: hunks of base->X. returns f(x_line) -> (base_lo, base_hi)."""
    def f(x):
        off = 0
        for bs, bl, ns, nl, _ in cum:
            nlo, nhi = ns, ns + nl  # X lines [ns, ns+nl) changed (nl may be 0: insertion point after ns... deletion)
            blo, bhi = bs, bs + bl
            if nl == 0:
                nlo, nhi = ns + 1, ns + 1
            if bl == 0:
                blo, bhi = bs + 1, bs + 1
            if x < nlo:
                return (x - off, x - off)
            if x < nhi:
                return (blo, max(blo, bhi - 1))
            off = (nhi - nlo) - (bhi - blo) + off
        return (x - off, x - off)
    return f

C = json.load(open(D + 'commits.json', encoding='utf-8'))
knobfiles = [x.strip() for x in open(D + 'knobfiles.txt', encoding='utf-8') if x.strip()]
basefiles = set(x.strip() for x in open(D + 'basetree.txt', encoding='utf-8'))
ours = {}
knobs_in_file = {}
for F in knobfiles:
    txt = git('show', OURS + ':' + F)
    knobs_in_file[F] = sorted(set(NAME_RE.findall(txt)))
    if F not in basefiles:
        continue
    hs = hunks(git('diff', '-U0', BASE, OURS, '--', F))
    ours[F] = [(bs, bl, bool(KNOB_RE.search('\n'.join(add))), sorted(set(NAME_RE.findall('\n'.join(add))))) for bs, bl, ns, nl, add in hs]
rows = []
order = list(C.keys())
for h in order:
    for F in C[h]['knob']:
        if F not in ours:
            rows.append((h, F, 0, 'file_not_in_base', '', ' '.join(knobs_in_file.get(F, []))))
            continue
        cum = hunks(git('diff', '-U0', BASE, h + '^', '--', F))
        f = mapper(cum)
        up = hunks(git('diff', '-U0', h + '^', h, '--', F))
        kh, oh = set(), set()
        for ps, pl, ns, nl, _ in up:
            lo = f(ps if pl > 0 else ps)[0]
            hi = f(ps + max(pl, 1) - 1)[1]
            for i, (bs, bl, isk, names) in enumerate(ours[F]):
                b_lo, b_hi = (bs, bs + bl - 1) if bl > 0 else (bs, bs + 1)
                if lo <= b_hi + M and hi >= b_lo - M:
                    (kh if isk else oh).add(i)
        kn = sorted(set(n for i in kh for n in ours[F][i][3]))
        knob_txt = ('%d [%s]' % (len(kh), ' '.join(kn) if kn else 'call-site')) if kh else '0'
        rows.append((h, F, len(up), knob_txt, str(len(oh)), ' '.join(knobs_in_file.get(F, []))))
with open(D + 'overlap.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    fo.write('sha\tfile\tup_hunks\tour_knob_hunks_hit\tour_other_hunks_hit\tknobs_in_file\n')
    for r in rows:
        fo.write('\t'.join(str(x) for x in r) + '\n')
hit = collections.Counter(r[0] for r in rows if r[3] not in ('0', 'file_not_in_base'))
print('rows', len(rows), 'commits with knob-hunk overlap', len(hit))
