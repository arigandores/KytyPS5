"""M1a2 (HPP-837, ROADMAP p.756(b)(4), RC4 of M1b): witnesses of log lines.
For every upstream commit of 6a2987a7..dad900c6 (no merges; plus the merge 8cecaf4e by its combined diff) take the string
literals of removed ('-') source lines under src/ that belong to a print/log call (a line with a print token -
LOGF/printf/EXIT*/PRINT*/fmt::print/...Log...(/Fail(/...Trace...( - and its continuation lines up to ';'; #include lines
are skipped); the keys of a literal = its pieces between format directives ('%...'
including a lone '%' before a PRI macro, '{...}') and backslash escapes, stripped, >= 10 characters with >= 3 letters.
A key of the form '<identifier> =' / '<identifier>:' is searched by its identifier when the identifier has >= 10
characters (our readers match 'flipPendingNum' with their own spacing). A key is a WITNESS if it occurs in one of our scripts tracked under docs/ at our tree (default b3dc9c67; *.py, *.sh,
*.ps1, *.cmd). For every witnessed key: does the same key still occur in upstream src/ at dad900c6 (kept as text - the
print condition or place may have changed) or not (removed upstream). Output: TSV (theme, sha, key, fate, n_scripts,
scripts) to argv[1]; summary to stdout; ALL OK when the four themes named by RC4 (T124, T116, T151, T017) each have >= 1
witness row. Read-only; exit 3 under C:/kyty/SEALED_RUN.lock, exit 4 under C:/kyty/m657/STOP.
Usage: python wit_m1a2.py <out.tsv> [ours=b3dc9c67]   (cwd = KytyPS5 repo root)"""
import collections, csv, os, re, subprocess, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP present - exit 4'); sys.exit(4)
GIT = 'C:/Program Files/Git/cmd/git.exe' if os.path.exists('C:/Program Files/Git/cmd/git.exe') else 'git'
BASE, UP = '6a2987a7', 'dad900c6'
MERGE = '8cecaf4e'
OUT = sys.argv[1]
OURS = sys.argv[2] if len(sys.argv) > 2 else 'b3dc9c67'
HERE = os.path.dirname(os.path.abspath(__file__))


def git(*a):
    return subprocess.run([GIT] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')


def blobs(rev, paths):
    """Contents of rev:path for many paths via one git cat-file --batch."""
    req = ''.join('%s:%s\n' % (rev, p) for p in paths).encode('utf-8')
    data = subprocess.run([GIT, 'cat-file', '--batch'], input=req, capture_output=True).stdout
    out, pos = {}, 0
    for p in paths:
        eol = data.index(b'\n', pos)
        head = data[pos:eol].split()
        if len(head) < 3 or head[1] == b'missing':
            pos = eol + 1
            continue
        size = int(head[2])
        out[p] = data[eol + 1:eol + 1 + size].decode('utf-8', 'replace')
        pos = eol + 1 + size + 1
    return out


LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
SPLIT = re.compile(r'%[-+ #0]*\d*(?:\.\d+)?(?:hh|h|ll|l|z|j|t|L|I64|I32)?[a-zA-Z%]|\{[^{}]*\}|\\.|%')


PRINT = re.compile(r'(?<![A-Za-z_])(LOGF?|LOG_[A-Z_]+|printf|fprintf|snprintf|EXIT\w*|PRINT\w*|fmt::print|std::print\w*|puts|'
                   r'std::cout|std::cerr|Fail|\w*Log\w*|Warn\w*|\w*Trace\w*|DbgReport)\s*\(|<<\s*"')
prev_end = True


def keys_of(line):
    out = []
    for m in LIT.finditer(line):
        for piece in SPLIT.split(m.group(1)):
            piece = piece.strip()
            if len(piece) >= 10 and re.search(r'[A-Za-z]{3}', piece):
                out.append(piece)
    return out


names = [n for n in git('ls-tree', '-r', '--name-only', OURS, 'docs').split('\n')
         if n.endswith(('.py', '.sh', '.ps1', '.cmd'))]
scripts = blobs(OURS, names)
print('our scripts under docs/ at', OURS, len(scripts), 'of', len(names))
up_names = [n for n in git('ls-tree', '-r', '--name-only', UP, 'src').split('\n') if n]
up_src = '\n'.join(blobs(UP, up_names).values())
theme_of = {}
for r in csv.DictReader(open(os.path.join(HERE, '..', 'upstream.tsv'), encoding='utf-8'), delimiter='\t',
                        quoting=csv.QUOTE_NONE):
    theme_of[r['sha'][:9]] = r['тема']
shas = git('rev-list', '--no-merges', '--reverse', BASE + '..' + UP).split()
rows = []
for sha in shas + [MERGE]:
    if sha == MERGE:
        diff = git('diff-tree', '--cc', '-U0', MERGE, '--', 'src')
        removed = [l[2:] for l in diff.split('\n') if l[:2] in ('--', '- ', ' -') and not l.startswith('---')]
        theme = 'T053'
    else:
        diff = git('show', '--format=', '-U0', sha, '--', 'src')
        removed = [l[1:] for l in diff.split('\n') if l.startswith('-') and not l.startswith('---')]
        theme = theme_of.get(sha[:9], '?')
    ks = []
    in_print = False
    for l in removed:
        t = l.strip()
        in_print = bool(PRINT.search(t)) or (in_print and not prev_end)
        prev_end = t.endswith(';') or t.endswith('{') or t.endswith('}') or t == ''
        if in_print and not t.startswith('#'):
            ks.extend(keys_of(l))
    for k in dict.fromkeys(ks):
        stem = k.rstrip(' =:').strip()
        needle = stem if len(stem) >= 10 and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', stem) else k
        hit = sorted(n for n, t in scripts.items() if needle in t)
        if not hit:
            continue
        fate = 'kept_text_upstream' if k in up_src else 'removed_upstream'
        rows.append((theme, sha[:9], k, fate, len(hit), ';'.join(hit)))
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write('тема\tsha\tключ\tсудьба_в_upstream\tскриптов\tскрипты\n')
    for r in rows:
        f.write('%s\t%s\t%s\t%s\t%d\t%s\n' % r)
by_theme = collections.Counter(r[0] for r in rows)
fate = collections.Counter(r[3] for r in rows)
print('witness rows', len(rows), 'themes', len(by_theme), dict(fate))
print('themes:', ' '.join('%s:%d' % kv for kv in sorted(by_theme.items())))
need = ['T124', 'T116', 'T151', 'T017']
miss = [t for t in need if by_theme[t] == 0]
print('RC4 named themes without witness:', miss)
print('ALL OK' if not miss else 'NOT OK')
sys.exit(0 if not miss else 1)
