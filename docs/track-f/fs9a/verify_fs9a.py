# FS9a (HPP-671, ROADMAP s122 item 604(d)(1)): source members of the ship binary FS9 (worktree C:/kyty/f287/fs9a/wt).
#   V1 "contains": every source commit has a worktree commit whose changed lines (+/- lines, file by file, as multisets)
#      equal the source's: 1570d110, 21f8ca76 (its include conflict - the context line only), the FS9a main commit;
#      git cherry is printed as reference. Negative control: the same comparison of 21f8ca76 against the worktree commit
#      of 1570d110 must fail, and against its own worktree commit with one changed line spoiled must fail.
#   V2 the diff of FS9 against the base 0005e11f - only the files of the three source commits, and its signed multiset of
#      changed lines (per file: + counts +1, - counts -1) = the sum of the three source commits'. Negative control: the
#      sum without the FS9a commit must differ.
#   V3 default table (own scanner, the form of knobs_fs8a.py): the set of knobs whose reading takes unset as ON at the
#      FS9 HEAD = the set of the base plus KYTY_FIX_B13 and only it. Negative control: the same at the worktree commit
#      before FS9a (21f8ca76 carried) - the difference is empty (the member would fail there).
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS9 = base (blob), ParseMode returns 3 for unset or "".
#   V5 translation signature: no path of the diff under src/graphics/shader/ (the signature line of the builds - in fs9a.md).
# Usage: python verify_fs9a.py <FS9 HEAD> <wt 1570d110> <wt 21f8ca76> <main FS9a> <wt FS9a>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "0005e11f"
HEAD, W1, W2, M3, W3 = sys.argv[1:6]
SRC = [("1570d110", W1), ("21f8ca76", W2), (M3, W3)]


def git(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")


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
print("FS9 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip())

# V1
for src, wt in SRC:
    a, b = commit_lines(src), commit_lines(wt)
    eq = a == b
    n = sum(sum(c.values()) for c in a.values())
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d / %d, equal %s; git cherry %s" % (
        src, wt, n, sum(sum(c.values()) for c in b.values()), eq, ch))
    ok &= eq
neg1 = commit_lines("21f8ca76") == commit_lines(W1)
spoiled = commit_lines(W2)
f0 = sorted(spoiled)[0]
k0 = sorted(spoiled[f0])[0]
spoiled = {f: collections.Counter(c) for f, c in spoiled.items()}
spoiled[f0][k0] -= 1
spoiled[f0][k0[0] + k0[1:] + " x"] += 1
spoiled = {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in spoiled.items()}
neg2 = commit_lines("21f8ca76") == spoiled
print("V1 negative controls: 21f8ca76 vs %s equal %s (want False); vs its own worktree commit with one line spoiled equal %s (want False)" % (W1, neg1, neg2))
ok &= (not neg1) and (not neg2)

# V2
names = set(git("diff", "--name-only", BASE, HEAD).split())
src_names = set()
for src, _ in SRC:
    src_names |= set(git("show", "--format=", "--name-only", src).split())
print("V2 files of diff %s..FS9: %s" % (BASE, " ".join(sorted(names))))
print("V2 files of the three source commits: %s" % " ".join(sorted(src_names)))
m = names == src_names
total = {}
for src, _ in SRC:
    total = add(total, signed(commit_lines(src)))
d = nonempty(signed(changed(git("diff", "-U0", BASE, HEAD))))
total = nonempty(total)
m2 = d == total
part = {}
for src, _ in SRC[:2]:
    part = add(part, signed(commit_lines(src)))
neg3 = nonempty(part) == d
print("V2 file sets equal %s; signed changed lines of the diff = sum of the three commits %s (lines %d); negative control without FS9a equal %s (want False)" % (
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


b_on, h_on, w2_on = default_on(BASE), default_on(HEAD), default_on(W2)
print("V3 DEFAULT-ON base (%d): %s" % (len(b_on), " ".join(sorted(b_on))))
print("V3 DEFAULT-ON FS9  (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == {"KYTY_FIX_B13"} and b_on - h_on == set()
neg4 = w2_on - b_on == {"KYTY_FIX_B13"}
print("V3 FS9 = base + KYTY_FIX_B13 only: %s; negative control at %s (before FS9a): difference %s, member there %s (want False)" % (
    m, W2, sorted(w2_on - b_on) or "empty", neg4))
ok &= m and not neg4

# V4
p = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
bb, hb = git("rev-parse", "%s:%s" % (BASE, p)).strip(), git("rev-parse", "%s:%s" % (HEAD, p)).strip()
txt = git("show", "%s:%s" % (HEAD, p))
m4 = re.search(r"int ParseMode\(const char\* value\) \{.*?if \(value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", txt, re.S) is not None
print("V4 %s blob base %s FS9 %s equal %s; ParseMode unset/\"\" -> 3: %s" % (p, bb[:12], hb[:12], bb == hb, m4))
ok &= bb == hb and m4

# V5
sh = [n for n in names if n.startswith("src/graphics/shader/")]
print("V5 paths of the diff under src/graphics/shader/: %s" % (sh or "none"))
ok &= not sh

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
