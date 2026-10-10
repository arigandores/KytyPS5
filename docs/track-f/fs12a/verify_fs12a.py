# FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): source members of the shipping binary FS12 (worktree C:/kyty/f287/fs12a/wt);
# port of fs11a/verify_fs11a.py (FS11a, HPP-714, item 647(d)(1)) with the base FS11 ee9632be and four source commits.
#   V1 every source commit has a worktree commit whose changed lines (+/- lines, file by file, as multisets) equal the
#      source's; git cherry printed. Negative controls: the lines of e5979953 against the worktree commit of 227e1b36 must
#      differ; against its own worktree commit with one line spoiled must differ.
#   V1b member "contains" of item 683(g)(1) (rule of item 656(g)): 227e1b36, c94c49e0, 726e751e, cb022252 - each an
#      ancestor of FS12 or 'git cherry FS12 <c> <c>^' gives '-'. Negative controls (the same rule must say NO): the stand
#      edition 1 5f48cc3e (not carried, item 683(g)(1)); 227e1b36 against the base ee9632be; c94c49e0 against FS10 dc5d4712.
#   V2 the diff of FS12 against the base ee9632be - only the files of the four source commits, and its signed multiset of
#      changed lines = the sum of the four commits'. Negative control: the sum without the FS12a commit must differ.
#   V2b member of item 683(g)(1): the paths of the diff outside tests/ = only files of 227e1b36, e5979953, 5237fdff, FS12a.
#   V3 default table (own scanner, the form of verify_fs11a.py V3): the knobs whose reading takes unset as ON at FS12 = the
#      base FS11's plus KYTY_FIX_F21 and only it. Negative control: at the worktree commit before FS12a (5237fdff carried)
#      the difference is empty (the member would fail there).
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS12 = base (blob), ParseMode returns 3 for unset or "".
#   V5 translation signature set: no path of the diff under src/graphics/shader/ (the signature lines of the builds - fs12a.md).
#   V6 code outside the base not carried: 5f48cc3e (stand edition 1) and 585d997d (F30d) are not ancestors of FS12; no line
#      added by the diff base..FS12 names KYTY_DIAG_B32 / DiagB32 / rts_bad_b / rts_bad_rx (except comments).
# Usage: python verify_fs12a.py <FS12 HEAD> <wt 227e1b36> <wt e5979953> <wt 5237fdff> <main FS12a> <wt FS12a>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "ee9632be"
HEAD, W1, W2, W3, M4, W4 = sys.argv[1:7]
SRC = [("227e1b36", W1), ("e5979953", W2), ("5237fdff", W3), (M4, W4)]
CONTAINS = ("227e1b36", "c94c49e0", "726e751e", "cb022252")


def git(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")


def git_rc(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True).returncode


def changed(diff):
    out = collections.defaultdict(collections.Counter)
    cur = None
    for line in diff.split("\n"):
        if line.startswith("diff --git "):
            cur = line.split(" b/", 1)[1]
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+") or line.startswith("-"):
            out[cur][line] += 1
    return {f: c for f, c in out.items()}


def commit_lines(c):
    return changed(git("show", "--format=", "-U0", c))


def signed(d):
    s = collections.defaultdict(collections.Counter)
    for f, c in d.items():
        for line, n in c.items():
            s[f][line[1:]] += n if line[0] == "+" else -n
    return {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in s.items()}


def add(a, b):
    out = collections.defaultdict(collections.Counter)
    for d in (a, b):
        for f, c in d.items():
            for k, v in c.items():
                out[f][k] += v
    return {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in out.items()}


def nonempty(d):
    return {f: c for f, c in d.items() if c}


def contains(tip, c):
    anc = git_rc("merge-base", "--is-ancestor", c, tip) == 0
    ch = git("cherry", tip, c, c + "^").strip()
    return anc or ch.startswith("-"), anc, ch


ok = True
print("FS12 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip())

# V1
for src, wt in SRC:
    a, b = commit_lines(src), commit_lines(wt)
    eq = a == b
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d / %d, equal %s; git cherry %s" % (
        src, wt, sum(sum(c.values()) for c in a.values()), sum(sum(c.values()) for c in b.values()), eq, ch))
    ok &= eq
neg1 = commit_lines("e5979953") == commit_lines(W1)
spoiled = commit_lines(W2)
f0 = sorted(spoiled)[0]
k0 = sorted(spoiled[f0])[0]
spoiled = {f: collections.Counter(c) for f, c in spoiled.items()}
spoiled[f0][k0] -= 1
spoiled[f0][k0 + " x"] += 1
spoiled = {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in spoiled.items()}
neg2 = commit_lines("e5979953") == spoiled
print("V1 negative controls: e5979953 vs %s equal %s (want False); vs its own worktree commit with one line spoiled equal %s (want False)" % (
    W1, neg1, neg2))
ok &= (not neg1) and (not neg2)

# V1b
for c in CONTAINS:
    yes, anc, ch = contains(HEAD, c)
    print("V1b contains %s: %s (ancestor %s, git cherry %s)" % (c, yes, anc, ch))
    ok &= yes
for tip, c, why in (("HEAD", "5f48cc3e", "stand edition 1, not carried"), (BASE, "227e1b36", "code F33c against the base FS11"),
                    ("dc5d4712", "c94c49e0", "code F29c against FS10")):
    t = HEAD if tip == "HEAD" else tip
    yes, anc, ch = contains(t, c)
    print("V1b negative control %s in %s (%s): %s (ancestor %s, git cherry %s) (want False)" % (c, tip, why, yes, anc, ch))
    ok &= not yes

# V2
names = set(git("diff", "--name-only", BASE, HEAD).split())
src_names = set()
by_commit = {}
for src, _ in SRC:
    fs = set(git("show", "--format=", "--name-only", src).split())
    by_commit[src] = fs
    src_names |= fs
print("V2 files of diff %s..FS12: %s" % (BASE, " ".join(sorted(names))))
print("V2 files of the four source commits: %s" % " ".join(sorted(src_names)))
m = names == src_names
total = {}
for src, _ in SRC:
    total = add(total, signed(commit_lines(src)))
d = nonempty(signed(changed(git("diff", "-U0", BASE, HEAD))))
total = nonempty(total)
m2 = d == total
part = {}
for src, _ in SRC[:3]:
    part = add(part, signed(commit_lines(src)))
neg3 = nonempty(part) == d
print("V2 file sets equal %s; signed changed lines of the diff = sum of the four commits %s (lines %d); negative control without FS12a equal %s (want False)" % (
    m, m2, sum(sum(abs(v) for v in c.values()) for c in d.values()), neg3))
ok &= m and m2 and not neg3

# V2b
outside = sorted(n for n in names if not n.startswith("tests/"))
allowed = set()
for src, _ in SRC:
    allowed |= by_commit[src]
extra = [n for n in outside if n not in allowed]
print("V2b paths of the diff outside tests/: %s" % " ".join(outside))
print("V2b paths outside tests/ not of 227e1b36 / e5979953 / 5237fdff / FS12a: %s" % (extra or "none"))
ok &= not extra


# V3
def default_on(tip):
    on = set()
    g = git("grep", "-n", "-E", "\"KYTY_[A-Z0-9_]+\"", tip, "--", "src/")
    cache = {}
    for l in g.strip().split("\n"):
        if not l:
            continue
        _, path, lineno, text = l.split(":", 3)
        if "getenv" not in text:
            continue
        if path not in cache:
            cache[path] = git("show", "%s:%s" % (tip, path)).split("\n")
        window = " ".join(cache[path][int(lineno) - 1:int(lineno) + 2])
        if re.search(r"== nullptr \|\|.*EnvValueOn", window):
            for k in re.findall(r'"(KYTY_[A-Z0-9_]+)"', text):
                on.add(k)
    return on


b_on, h_on, w3_on = default_on(BASE), default_on(HEAD), default_on(W3)
print("V3 DEFAULT-ON base (%d): %s" % (len(b_on), " ".join(sorted(b_on))))
print("V3 DEFAULT-ON FS12 (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == {"KYTY_FIX_F21"} and b_on - h_on == set()
neg4 = w3_on - b_on == {"KYTY_FIX_F21"}
print("V3 FS12 = base + KYTY_FIX_F21 only: %s; negative control at %s (before FS12a): difference %s, member there %s (want False)" % (
    m, W3, sorted(w3_on - b_on) or "empty", neg4))
ok &= m and not neg4

# V4
p = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
bb, hb = git("rev-parse", "%s:%s" % (BASE, p)).strip(), git("rev-parse", "%s:%s" % (HEAD, p)).strip()
txt = git("show", "%s:%s" % (HEAD, p))
m4 = re.search(r"int ParseMode\(const char\* value\) \{.*?if \(value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", txt, re.S) is not None
print("V4 %s blob base %s FS12 %s equal %s; ParseMode unset/\"\" -> 3: %s" % (p, bb[:12], hb[:12], bb == hb, m4))
ok &= bb == hb and m4

# V5
sh = [n for n in names if n.startswith("src/graphics/shader/")]
print("V5 paths of the diff under src/graphics/shader/: %s" % (sh or "none"))
ok &= not sh

# V6
added = [l[1:] for l in git("diff", "-U0", BASE, HEAD).split("\n") if l.startswith("+") and not l.startswith("+++ ")]
pat = r"DiagB32|diagB32\.h|KYTY_DIAG_B32|rts_bad_b|rts_bad_rx"
code = [l for l in added if re.search(pat, l) and not l.lstrip().startswith("//")]
a1 = git_rc("merge-base", "--is-ancestor", "5f48cc3e", HEAD) == 0
a2 = git_rc("merge-base", "--is-ancestor", "585d997d", HEAD) == 0
print("V6 added lines naming KYTY_DIAG_B32 / F30d counters (code): %d; 5f48cc3e ancestor of FS12 %s; 585d997d ancestor of FS12 %s" % (
    len(code), a1, a2))
ok &= not code and not a1 and not a2

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
