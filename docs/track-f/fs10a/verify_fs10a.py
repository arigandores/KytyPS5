# FS10a (HPP-684, ROADMAP s122 item 624(e)(1)): source members of the shipping binary FS10 (worktree C:/kyty/f287/fs10a/wt);
# port of fs9a/verify_fs9a.py (FS9a, HPP-671, item 604(d)(1)) with the base FS9 11164d72 and five source commits.
#   V1 "contains" (rule of item 615(b)(5)): every source commit has a worktree commit whose changed lines (+/- lines, file by
#      file, as multisets) equal the source's; git cherry printed as reference ('-' = same patch id). Negative controls: the
#      lines of 5064c5bb against the worktree commit of a8ee1b05 must differ; against its own worktree commit with one line
#      spoiled must differ.
#   V2 the diff of FS10 against the base 11164d72 - only the files of the five source commits, and its signed multiset of
#      changed lines = the sum of the five commits'. Negative control: the sum without the FS10a commit must differ.
#   V3 default table (own scanner, the form of knobs_fs8a.py / verify_fs9a.py V3): the knobs whose reading takes unset as ON
#      at FS10 = the base's plus KYTY_FIX_B36 and only it. Negative control: at the worktree commit before FS10a (5064c5bb
#      carried) the difference is empty (the member would fail there).
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS10 = base (blob), ParseMode returns 3 for unset or "".
#   V5 translation signature set: no path of the diff under src/graphics/shader/ (the signature lines of the builds - fs10a.md).
#   V6 KYTY_DIAG_B32 not carried: no line added by the diff base..FS10 names DiagB32 / diagB32.h / KYTY_DIAG_B32 except
#      comments; the base has no src/common/diagB32.h and FS10 neither.
# Usage: python verify_fs10a.py <FS10 HEAD> <wt a8ee1b05> <wt b4ee756a> <wt 0e4b2f5a> <wt 5064c5bb> <main FS10a> <wt FS10a>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "11164d72"
HEAD, W1, W2, W3, W4, M5, W5 = sys.argv[1:8]
SRC = [("a8ee1b05", W1), ("b4ee756a", W2), ("0e4b2f5a", W3), ("5064c5bb", W4), (M5, W5)]


def git(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")


def git_rc(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True).returncode


def changed(diff):
    """{file: Counter(signed line)} from a unified diff: '+text' and '-text' lines."""
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


ok = True
print("FS10 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip())

# V1
for src, wt in SRC:
    a, b = commit_lines(src), commit_lines(wt)
    eq = a == b
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d / %d, equal %s; git cherry %s" % (
        src, wt, sum(sum(c.values()) for c in a.values()), sum(sum(c.values()) for c in b.values()), eq, ch))
    ok &= eq
neg1 = commit_lines("5064c5bb") == commit_lines(W1)
spoiled = commit_lines(W4)
f0 = sorted(spoiled)[0]
k0 = sorted(spoiled[f0])[0]
spoiled = {f: collections.Counter(c) for f, c in spoiled.items()}
spoiled[f0][k0] -= 1
spoiled[f0][k0 + " x"] += 1
spoiled = {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in spoiled.items()}
neg2 = commit_lines("5064c5bb") == spoiled
print("V1 negative controls: 5064c5bb vs %s equal %s (want False); vs its own worktree commit with one line spoiled equal %s (want False)" % (
    W1, neg1, neg2))
ok &= (not neg1) and (not neg2)

# V2
names = set(git("diff", "--name-only", BASE, HEAD).split())
src_names = set()
for src, _ in SRC:
    src_names |= set(git("show", "--format=", "--name-only", src).split())
print("V2 files of diff %s..FS10: %s" % (BASE, " ".join(sorted(names))))
print("V2 files of the five source commits: %s" % " ".join(sorted(src_names)))
m = names == src_names
total = {}
for src, _ in SRC:
    total = add(total, signed(commit_lines(src)))
d = nonempty(signed(changed(git("diff", "-U0", BASE, HEAD))))
total = nonempty(total)
m2 = d == total
part = {}
for src, _ in SRC[:4]:
    part = add(part, signed(commit_lines(src)))
neg3 = nonempty(part) == d
print("V2 file sets equal %s; signed changed lines of the diff = sum of the five commits %s (lines %d); negative control without FS10a equal %s (want False)" % (
    m, m2, sum(sum(abs(v) for v in c.values()) for c in d.values()), neg3))
ok &= m and m2 and not neg3


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


b_on, h_on, w4_on = default_on(BASE), default_on(HEAD), default_on(W4)
print("V3 DEFAULT-ON base (%d): %s" % (len(b_on), " ".join(sorted(b_on))))
print("V3 DEFAULT-ON FS10 (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == {"KYTY_FIX_B36"} and b_on - h_on == set()
neg4 = w4_on - b_on == {"KYTY_FIX_B36"}
print("V3 FS10 = base + KYTY_FIX_B36 only: %s; negative control at %s (before FS10a): difference %s, member there %s (want False)" % (
    m, W4, sorted(w4_on - b_on) or "empty", neg4))
ok &= m and not neg4

# V4
p = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
bb, hb = git("rev-parse", "%s:%s" % (BASE, p)).strip(), git("rev-parse", "%s:%s" % (HEAD, p)).strip()
txt = git("show", "%s:%s" % (HEAD, p))
m4 = re.search(r"int ParseMode\(const char\* value\) \{.*?if \(value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", txt, re.S) is not None
print("V4 %s blob base %s FS10 %s equal %s; ParseMode unset/\"\" -> 3: %s" % (p, bb[:12], hb[:12], bb == hb, m4))
ok &= bb == hb and m4

# V5
sh = [n for n in names if n.startswith("src/graphics/shader/")]
print("V5 paths of the diff under src/graphics/shader/: %s" % (sh or "none"))
ok &= not sh

# V6
added = [l[1:] for l in git("diff", "-U0", BASE, HEAD).split("\n") if l.startswith("+") and not l.startswith("+++ ")]
code = [l for l in added if re.search(r"DiagB32|diagB32\.h|KYTY_DIAG_B32", l) and not l.lstrip().startswith("//")]
hb_h = git_rc("cat-file", "-e", "%s:src/common/diagB32.h" % HEAD)
bb_h = git_rc("cat-file", "-e", "%s:src/common/diagB32.h" % BASE)
cm = [l for l in added if re.search(r"DiagB32|diagB32\.h|KYTY_DIAG_B32", l)]
print("V6 added lines naming KYTY_DIAG_B32 code: %d (comments %d); src/common/diagB32.h in base %s, in FS10 %s" % (
    len(code), len(cm) - len(code), bb_h == 0, hb_h == 0))
for l in cm:
    print("   ", l.strip()[:150])
ok &= not code and hb_h != 0 and bb_h != 0

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
