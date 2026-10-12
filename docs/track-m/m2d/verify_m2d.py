"""M2d (HPP-841, ROADMAP s122 items 756(g), 761(z), 762(v)): source members of the MS1 candidate (worktree
C:/kyty/m657/m2d/wt, base FS15 6beb3b73). Helpers ported from f287/fs15a/verify_fs15a.py.
  V1  every worktree commit has a source commit whose changed lines (+/- lines, file by file, as multisets) are equal:
      M2a worktree 0361b202 and main 674f8c27; M2b worktree 8a717ac0 and main 274ee39a; M2a2 main adc3c33d; git cherry of
      the main commits against MS1 printed ('-' = contained). Negative control: 674f8c27 against the MS1 M2b commit -
      differ.
  V1b item 737(g): FS15 6beb3b73 is an ancestor of MS1; every commit of the FS15 "contains" list (old sha of the
      FS15a list and its new sha from docs/track-m/sha_map.tsv) - ancestor of MS1 or 'git cherry MS1 <c> <c>^' gives
      '-'. Negative control: the MS1 defaults commit against FS15 -> '+' (not contained).
  V2  the diff FS15..MS1 - only the files of the four commits; signed changed lines = the sum of the four. Negative
      control: the sum without the defaults commit differs.
  V2b the M2a2 commit touches only tests/ and docs/ (not src/, not CMakeLists): the kyty_emulator target sources are
      unchanged by it.
  V3  default table of every KYTY_M_*, KYTY_FIX_*, KYTY_S_* knob read in src/ at FS15, at MS1 before the defaults commit
      (10da0b8b) and at MS1: member - MS1 = FS15 for every KYTY_FIX_* / KYTY_S_* knob, MS1 ON adds exactly KYTY_M_T234,
      KYTY_M_T233, KYTY_M_T032, KYTY_M_T203, KYTY_M_T265, KYTY_M_T272, KYTY_M_T231, KYTY_M_T256 and KYTY_M_T306 are 0.
      Negative control: at 10da0b8b every KYTY_M_* is 0 (the member would fail there).
  V5  KYTY_SHADER_SOURCE_HASH and KYTY_GIT_VERSION of the MS1 build (kytyGitVersion.h) printed; FS15 9177b426 for
      reference (the signature changes - item 756(g)(3)).
Usage: python verify_m2d.py <MS1 HEAD> <MS1 kytyGitVersion.h>"""
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
FS15 = "6beb3b73"
HEAD, VH = sys.argv[1], sys.argv[2]


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


def add(*ds):
    out = collections.defaultdict(collections.Counter)
    for d in ds:
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
head = git("rev-parse", HEAD).strip()
print("MS1 HEAD", head, "base FS15", git("rev-parse", FS15).strip())
log = git("log", "--format=%H %P %s", FS15 + ".." + HEAD).rstrip().split("\n")
print("worktree log FS15..MS1 (%d):" % len(log))
for l in log:
    print("   " + l[:170])
wt = [l.split()[0] for l in reversed(log)]
ok &= len(wt) == 4
W_M2A, W_M2B, W_M2A2, W_DEF = wt

# V1
pairs = [("0361b202", W_M2A), ("674f8c27", W_M2A), ("8a717ac0", W_M2B), ("274ee39a", W_M2B), ("adc3c33d", W_M2A2)]
for src, w in pairs:
    a, b = commit_lines(src), commit_lines(w)
    eq = a == b
    n = sum(sum(c.values()) for c in a.values())
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d, equal %s; git cherry %s%s" % (
        src, w[:8], n, eq, ch[:3], "" if src in ("0361b202", "8a717ac0", "adc3c33d") else " (reference: main context)"))
    ok &= eq
neg = commit_lines("674f8c27") == commit_lines(W_M2B)
print("V1 negative control 674f8c27 vs the MS1 M2b commit %s equal %s (want False)" % (W_M2B[:8], neg))
ok &= not neg

# V1b
CONTAINS = ("a6342c98", "82570fd2", "38fc76c1", "5c21c387", "57f9e528", "c8836f14", "15c9d2f2", "78e45af3", "e9dd8604",
            "3630f116", "227e1b36", "cbfe8375", "c94c49e0", "726e751e", "cb022252", "a9d6fd1c")
smap = {}
for line in open(REPO + "/docs/track-m/sha_map.tsv", encoding="ascii"):
    p = line.rstrip("\n").split("\t")
    if len(p) == 2 and p[0] != "old":
        smap[p[0]] = p[1]
anc15 = git_rc("merge-base", "--is-ancestor", FS15, HEAD) == 0
print("V1b FS15 %s ancestor of MS1: %s" % (FS15, anc15))
ok &= anc15
for c in CONTAINS:
    full = git("rev-parse", c).strip()
    new = smap.get(full)
    yes, anc, ch = contains(HEAD, c)
    line = "V1b contains %s: %s (ancestor %s, git cherry %s)" % (c, yes, anc, ch[:3])
    ok &= yes
    if new:
        yes2, anc2, ch2 = contains(HEAD, new)
        line += "; new sha %s: %s (ancestor %s, git cherry %s)" % (new[:8], yes2, anc2, ch2[:3])
        ok &= yes2
    print(line)
yes, anc, ch = contains(FS15, W_DEF)
print("V1b negative control: MS1 defaults commit %s in FS15: %s (git cherry %s) (want False)" % (W_DEF[:8], yes, ch[:3]))
ok &= not yes

# V2
parts = [commit_lines(c) for c in (W_M2A, W_M2B, W_M2A2, W_DEF)]
total = changed(git("diff", "-U0", FS15, HEAD))
files = set(total)
want_files = set().union(*[set(p) for p in parts])
eqf = files == want_files
eql = nonempty(signed(total)) == nonempty(signed(add(*parts)))
negl = nonempty(signed(total)) == nonempty(signed(add(*parts[:3])))
print("V2 files of FS15..MS1 (%d) = files of the four commits (%d): %s; signed changed lines = sum of the four: %s; "
      "negative control without the defaults commit equal %s (want False)" % (len(files), len(want_files), eqf, eql, negl))
ok &= eqf and eql and not negl
src = sorted(f for f in files if f.startswith("src/"))
shader = [f for f in src if f.startswith("src/graphics/shader/")]
print("V2 src/ paths (%d): %s" % (len(src), " ".join(src)))
print("V2 src/graphics/shader/ paths (%d, the translator signature set changes): %s" % (len(shader), " ".join(shader)))
print("V2 paths outside src/: %s" % " ".join(sorted(f for f in files if not f.startswith("src/"))))
print("V2 git diff --stat FS15 MS1:")
for l in git("diff", "--stat=160", FS15, HEAD).rstrip().split("\n"):
    print("    " + l)

# V2b
m2a2_files = git("diff-tree", "--no-commit-id", "--name-only", "-r", "adc3c33d").split()
bad = [f for f in m2a2_files if not (f.startswith("tests/") or f.startswith("docs/"))]
print("V2b adc3c33d files (%d): tests/ %s; outside tests/ and docs/: %s (want none)" % (
    len(m2a2_files), [f for f in m2a2_files if f.startswith("tests/")], bad or "none"))
ok &= not bad
for l in git("show", "--stat=160", "--format=", "adc3c33d").rstrip().split("\n"):
    print("    " + l)


# V3
def knob_table(tip):
    g = git("grep", "-n", "-E", "\"KYTY_(M|FIX|S)_[A-Z0-9_]+\"", tip, "--", "src/")
    cache = {}
    table = {}
    for l in g.strip().split("\n"):
        if not l:
            continue
        _, path, lineno, text = l.split(":", 3)
        if path not in cache:
            cache[path] = git("show", "%s:%s" % (tip, path)).split("\n")
        for k in re.findall(r'"(KYTY_(?:M|FIX|S)_[A-Z0-9_]+)"', text):
            if "getenv" not in text:
                table.setdefault(k, ("0", "named %s:%s (not a getenv line)" % (path, lineno)))
                continue
            window = " ".join(cache[path][int(lineno) - 1:int(lineno) + 2])
            if re.search(r"== nullptr \|\|.*EnvValueOn", window):
                table[k] = ("1", "unset/\"\" = on, %s:%s" % (path, lineno))
            elif k == "KYTY_S_REPLAY":
                pm = " ".join(cache[path])
                three = re.search(r"value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", pm) is not None
                table[k] = ("3" if three else "?", "ParseMode unset/\"\" -> 3 %s, %s:%s" % (three, path, lineno))
            elif k not in table or table[k][0] == "0" and table[k][1].startswith("named"):
                table[k] = ("0", "unset = off, %s:%s" % (path, lineno))
    # translator themes: knobs[] and default_on[] of ShaderDecoder.cpp
    p = "src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp"
    try:
        sd = git("show", "%s:%s" % (tip, p))
    except subprocess.CalledProcessError:
        sd = ""
    km = re.search(r"knobs\[\] = \{([^}]*)\}", sd)
    if km:
        names = re.findall(r'"(KYTY_M_T\d+)"', km.group(1))
        dm = re.search(r"default_on\[\] = \{([^}]*)\}", sd)
        dflt = [v.strip() == "true" for v in dm.group(1).split(",")] if dm else [False] * len(names)
        assert len(dflt) == len(names), (names, dflt)
        for n, d in zip(names, dflt):
            table[n] = ("1" if d else "0", "MThemeMask %s (%s)" % ("default_on[] = true" if d else
                                                                   ("default_on[] = false" if dm else "no default_on[]"),
                                                                   p))
    return table


t15, tpre, tms1 = knob_table(FS15), knob_table(W_M2A2), knob_table(HEAD)
names = sorted(set(t15) | set(tms1))
print("V3 knob table (KYTY_M_*, KYTY_FIX_*, KYTY_S_* read in src/): name | FS15 | MS1 before defaults (%s) | MS1 | where (MS1)"
      % W_M2A2[:8])
for n in names:
    a = t15.get(n, ("absent", ""))[0]
    b = tpre.get(n, ("absent", ""))[0]
    c, w = tms1.get(n, ("absent", ""))
    print("V3 %-28s | %-6s | %-6s | %-6s | %s%s" % (n, a, b, c, w, "  <- changed" if a != c else ""))
WANT_ON = {"KYTY_M_T234", "KYTY_M_T233", "KYTY_M_T032", "KYTY_M_T203", "KYTY_M_T265", "KYTY_M_T272", "KYTY_M_T231"}
diff_names = {n for n in names if t15.get(n, ("absent",))[0] != tms1.get(n, ("absent",))[0]}
m_on = {n for n in names if n.startswith("KYTY_M_") and tms1.get(n, ("",))[0] == "1"}
m_off = {n for n in names if n.startswith("KYTY_M_") and tms1.get(n, ("",))[0] == "0"}
fix_s_same = all(t15.get(n) is not None and t15[n][0] == tms1[n][0]
                 for n in names if not n.startswith("KYTY_M_") and n in tms1)
fix_s_lost = [n for n in t15 if n not in tms1]
member = (m_on == WANT_ON and {"KYTY_M_T256", "KYTY_M_T306"} <= m_off and fix_s_same and not fix_s_lost
          and all(n.startswith("KYTY_M_") for n in diff_names))
print("V3 MS1 KYTY_M_* on: %s" % " ".join(sorted(m_on)))
print("V3 MS1 KYTY_M_* off: %s" % " ".join(sorted(m_off)))
print("V3 every KYTY_FIX_*/KYTY_S_* default of MS1 = FS15: %s (lost %s); changed names all KYTY_M_*: %s; member %s" % (
    fix_s_same, fix_s_lost or "none", all(n.startswith("KYTY_M_") for n in diff_names), member))
ok &= member
pre_on = {n for n in tpre if n.startswith("KYTY_M_") and tpre[n][0] == "1"}
print("V3 negative control: at %s KYTY_M_* on = %s (want empty - the member fails there)" % (W_M2A2[:8],
                                                                                            sorted(pre_on) or "empty"))
ok &= not pre_on
on15 = sorted(n for n in t15 if t15[n][0] == "1")
print("V3 FS15 default-ON (%d): %s" % (len(on15), " ".join(on15)))

# V5
vh = open(VH, encoding="utf-8").read()
for key in ("KYTY_GIT_VERSION", "KYTY_GIT_REVISION", "KYTY_SHADER_SOURCE_HASH"):
    m = re.search(r'#define %s "([^"]*)"' % key, vh)
    print("V5 %s %s" % (key, m.group(1) if m else "MISSING"))
    ok &= m is not None
rev = re.search(r'#define KYTY_GIT_REVISION "([^"]*)"', vh).group(1)
print("V5 KYTY_GIT_REVISION = MS1 HEAD: %s" % (rev == head))
ok &= rev == head
print("V5 (reference) FS15 KYTY_SHADER_SOURCE_HASH 9177b4267de1fb8bac7d1113afd8733210addfac, main after M2a aac6db69...")
print("ALL OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
