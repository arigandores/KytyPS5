# FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): source members of the shipping binary FS11 (worktree C:/kyty/f287/fs11a/wt);
# port of fs10a/verify_fs10a.py (FS10a, HPP-684, item 624(e)(1)) with the base FS10 dc5d4712 and five source commits.
#   V1 "contains" (rule of item 615(b)(5)): every source commit has a worktree commit whose changed lines (+/- lines, file by
#      file, as multisets) equal the source's; git cherry printed as reference ('-' = same patch id). Negative controls: the
#      lines of 726e751e against the worktree commit of c94c49e0 must differ; against its own worktree commit with one line
#      spoiled must differ. Member of item 647(d)(1): c94c49e0 and 726e751e; the other three - the same rule, reported.
#   V2 the diff of FS11 against the base dc5d4712 - only the files of the five source commits, and its signed multiset of
#      changed lines = the sum of the five commits'. Negative control: the sum without the FS11a commit must differ.
#   V2b member of item 647(d)(1): the paths of the diff outside tests/ = the files of c94c49e0, 726e751e and FS11a; any other
#      path is printed with the commit that brings it and its added lines (an exception named, not hidden). For
#      CMakeLists.txt: every changed line lies inside the block of the target b12_bdastamp_stand (EXCLUDE_FROM_ALL) - no
#      line of another target changes.
#   V3 default table (own scanner, the form of verify_fs10a.py V3): the knobs whose reading takes unset as ON at FS11 = the
#      base's plus KYTY_FIX_B12 and only it. Negative control: at the worktree commit before FS11a (0db3b3eb carried) the
#      difference is empty (the member would fail there).
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS11 = base (blob), ParseMode returns 3 for unset or "".
#   V5 translation signature set: no path of the diff under src/graphics/shader/ (the signature lines of the builds - fs11a.md).
#   V6 diagnostics outside the base not carried: no line added by the diff base..FS11 names DiagB32 / diagB32.h /
#      KYTY_DIAG_B32 (except comments) or the F30d counters rts_bad_b / rts_bad_rx; 585d997d (F30d) is not an ancestor of FS11;
#      src/common/diagB32.h in neither base nor FS11.
# Usage: python verify_fs11a.py <FS11 HEAD> <wt 73a6e411> <wt c94c49e0> <wt 726e751e> <wt 0db3b3eb> <main FS11a> <wt FS11a>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "dc5d4712"
HEAD, W1, W2, W3, W4, M5, W5 = sys.argv[1:8]
SRC = [("73a6e411", W1), ("c94c49e0", W2), ("726e751e", W3), ("0db3b3eb", W4), (M5, W5)]
MEMBER_CONTAINS = ("c94c49e0", "726e751e")


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
print("FS11 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip())

# V1
for src, wt in SRC:
    a, b = commit_lines(src), commit_lines(wt)
    eq = a == b
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d / %d, equal %s; git cherry %s%s" % (
        src, wt, sum(sum(c.values()) for c in a.values()), sum(sum(c.values()) for c in b.values()), eq, ch,
        " (member 647(d)(1))" if src in MEMBER_CONTAINS else ""))
    ok &= eq
neg1 = commit_lines("726e751e") == commit_lines(W2)
spoiled = commit_lines(W3)
f0 = sorted(spoiled)[0]
k0 = sorted(spoiled[f0])[0]
spoiled = {f: collections.Counter(c) for f, c in spoiled.items()}
spoiled[f0][k0] -= 1
spoiled[f0][k0 + " x"] += 1
spoiled = {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in spoiled.items()}
neg2 = commit_lines("726e751e") == spoiled
print("V1 negative controls: 726e751e vs %s equal %s (want False); vs its own worktree commit with one line spoiled equal %s (want False)" % (
    W2, neg1, neg2))
ok &= (not neg1) and (not neg2)

# V2
names = set(git("diff", "--name-only", BASE, HEAD).split())
src_names = set()
by_commit = {}
for src, _ in SRC:
    fs = set(git("show", "--format=", "--name-only", src).split())
    by_commit[src] = fs
    src_names |= fs
print("V2 files of diff %s..FS11: %s" % (BASE, " ".join(sorted(names))))
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
print("V2 file sets equal %s; signed changed lines of the diff = sum of the five commits %s (lines %d); negative control without FS11a equal %s (want False)" % (
    m, m2, sum(sum(abs(v) for v in c.values()) for c in d.values()), neg3))
ok &= m and m2 and not neg3

# V2b
outside = sorted(n for n in names if not n.startswith("tests/"))
allowed = by_commit["c94c49e0"] | by_commit["726e751e"] | by_commit[M5]
extra = [n for n in outside if n not in allowed]
print("V2b paths of the diff outside tests/: %s" % " ".join(outside))
print("V2b files of c94c49e0, 726e751e, FS11a: %s" % " ".join(sorted(allowed)))
print("V2b paths outside tests/ not of c94c49e0 / 726e751e / FS11a: %s" % (extra or "none"))
cm_ok = True
for n in extra:
    who = [s for s, _ in SRC if n in by_commit[s]]
    print("   %s brought by %s" % (n, " ".join(who)))
    if n != "CMakeLists.txt":
        cm_ok = False
        continue
    new = git("show", "%s:%s" % (HEAD, n)).split("\n")
    hunk = git("diff", "-U0", BASE, HEAD, "--", n)
    starts = [(int(x), int(y or 1)) for x, y in re.findall(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", hunk, re.M)]
    blk = [i for i, l in enumerate(new) if l.startswith("add_executable(b12_bdastamp_stand EXCLUDE_FROM_ALL")]
    removed = [l for l in hunk.split("\n") if l.startswith("-") and not l.startswith("--- ")]
    if len(blk) != 1 or removed:
        cm_ok = False
        print("   CMakeLists: block found %d, removed lines %d" % (len(blk), len(removed)))
        continue
    b0 = blk[0]
    b1 = b0
    while b1 < len(new) and not new[b1].startswith("target_include_directories(b12_bdastamp_stand"):
        b1 += 1
    lo, hi = b0 - 3, b1  # three comment lines above add_executable, through target_include_directories (0-based)
    for s, c in starts:
        for ln in range(s - 1, s - 1 + c):
            inside = lo <= ln <= hi + 1  # +1: the blank line after the block
            print("   CMakeLists +%d %s %s" % (ln + 1, "inside" if inside else "OUTSIDE", new[ln][:110]))
            cm_ok &= inside
    print("   CMakeLists: every changed line inside the b12_bdastamp_stand block (EXCLUDE_FROM_ALL), none removed: %s" % cm_ok)
print("V2b member by the letter (no path outside tests/ beyond c94c49e0 / 726e751e / FS11a): %s; with the named exception "
      "CMakeLists.txt of 73a6e411 confined to the stand target: %s" % (not extra, cm_ok))
ok &= cm_ok


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
print("V3 DEFAULT-ON FS11 (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == {"KYTY_FIX_B12"} and b_on - h_on == set()
neg4 = w4_on - b_on == {"KYTY_FIX_B12"}
print("V3 FS11 = base + KYTY_FIX_B12 only: %s; negative control at %s (before FS11a): difference %s, member there %s (want False)" % (
    m, W4, sorted(w4_on - b_on) or "empty", neg4))
ok &= m and not neg4

# V4
p = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
bb, hb = git("rev-parse", "%s:%s" % (BASE, p)).strip(), git("rev-parse", "%s:%s" % (HEAD, p)).strip()
txt = git("show", "%s:%s" % (HEAD, p))
m4 = re.search(r"int ParseMode\(const char\* value\) \{.*?if \(value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", txt, re.S) is not None
print("V4 %s blob base %s FS11 %s equal %s; ParseMode unset/\"\" -> 3: %s" % (p, bb[:12], hb[:12], bb == hb, m4))
ok &= bb == hb and m4

# V5
sh = [n for n in names if n.startswith("src/graphics/shader/")]
print("V5 paths of the diff under src/graphics/shader/: %s" % (sh or "none"))
ok &= not sh

# V6
added = [l[1:] for l in git("diff", "-U0", BASE, HEAD).split("\n") if l.startswith("+") and not l.startswith("+++ ")]
pat = r"DiagB32|diagB32\.h|KYTY_DIAG_B32|rts_bad_b|rts_bad_rx"
code = [l for l in added if re.search(pat, l) and not l.lstrip().startswith("//")]
cm = [l for l in added if re.search(pat, l)]
hb_h = git_rc("cat-file", "-e", "%s:src/common/diagB32.h" % HEAD)
bb_h = git_rc("cat-file", "-e", "%s:src/common/diagB32.h" % BASE)
f30d_anc = git_rc("merge-base", "--is-ancestor", "585d997d", HEAD) == 0
print("V6 added lines naming KYTY_DIAG_B32 / F30d counters: %d (comments %d); src/common/diagB32.h in base %s, in FS11 %s; 585d997d ancestor of FS11 %s" % (
    len(code), len(cm) - len(code), bb_h == 0, hb_h == 0, f30d_anc))
for l in cm:
    print("   ", l.strip()[:150])
ok &= not code and hb_h != 0 and bb_h != 0 and not f30d_anc

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
