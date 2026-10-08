# F29d (HPP-703, Red Team): the path of KYTY_FIX_B12=0 is the old text. For the code (bufferCache.cpp
# SynchronizeBuffersByRegion, renderContext.cpp PrepareBda) and the stand model (ByRegion, Prepare): the body at 726e751e with
# every block "if (b12_pass ...) { ... }" / "if (fix_b12) { ... }" and the line "const bool b12_pass = ...;" /
# "const bool fix_b12 = ...;" removed, comments dropped, must equal the body at 73a6e411 (also comments dropped).
# Stand-only hook lines of Prepare are reported, not removed. Usage: python eq0_f29d.py
import re
import subprocess

GIT = "C:/Program Files/Git/cmd/git.exe"
NL = chr(10)


def show(c, p):
    return subprocess.run([GIT, "-C", "C:/kyty/KytyPS5", "show", "%s:%s" % (c, p)], capture_output=True,
                          check=True).stdout.decode("utf-8")


def body(text, header):
    i = text.index(header)
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j + 1:k]


def lines(src):
    out = []
    for ln in src.split(NL):
        ln = re.sub(r"//.*$", "", ln).strip()
        if ln:
            out.append(ln)
    return out


def strip_b12(ls):
    out = []
    i = 0
    while i < len(ls):
        ln = ls[i]
        if re.match(r"const bool (b12_pass|fix_b12) = ", ln):
            i += 1
            continue
        if re.match(r"if \((b12_pass|fix_b12)\b", ln):
            depth = ln.count("{") - ln.count("}")
            i += 1
            while depth > 0:
                depth += ls[i].count("{") - ls[i].count("}")
                i += 1
            continue
        out.append(ln)
        i += 1
    return out


CASES = [
    ("code ByRegion", "src/graphics/host_gpu/renderer/cache/bufferCache.cpp", "void BufferCache::SynchronizeBuffersByRegion("),
    ("code PrepareBda", "src/graphics/host_gpu/renderer/renderContext.cpp", "void RenderContext::PrepareBda()"),
    ("model ByRegion", "tests/B12BdaStampStand.cpp", "void ByRegion("),
    ("model Prepare", "tests/B12BdaStampStand.cpp", "void Prepare()"),
]
for name, path, header in CASES:
    new = strip_b12(lines(body(show("726e751e", path), header)))
    old = lines(body(show("73a6e411", path), header))
    import difflib
    d = [x for x in difflib.unified_diff(old, new, "73a6e411", "726e751e-minus-b12", lineterm="", n=0) if not x.startswith("@@")]
    print("== %s: old %d lines, new-minus-b12 %d lines, diff %d" % (name, len(old), len(new), max(0, len(d) - 2)))
    for x in d[2:]:
        print("   " + x)
