# M9a2 (HPP-866, track M): the code-check lists of edition 2 by `git grep` of the whole tree at 1ffda330
# (ROADMAP item 780(a), (b)(3), (b)(5), (c)(3)). Read-only; exits 3 if the lock exists.
# Usage: python grep_m9a2.py <repo> <out file>
import os, sys, subprocess, hashlib

LOCK = "C:/kyty/SEALED_RUN.lock"
if os.path.exists(LOCK):
    sys.exit(3)
REPO, OUT = sys.argv[1], sys.argv[2]
REV = "1ffda330"
PATTERNS = [
    ("MarkGpuModified call sites (src + tests)", r".MarkGpuModified()", ["src", "tests"]),
    ("ClearGpuModified call sites", r".ClearGpuModified()", ["src"]),
    ("IsBufferModified() readers", r"IsBufferModified()", ["src"]),
    ("MarkBufferModified call sites", r".MarkBufferModified()", ["src"]),
    ("ClearBufferModified call sites", r".ClearBufferModified()", ["src"]),
    ("InvalidateMemoryFromGPU callers", r"InvalidateMemoryFromGPU(", ["src"]),
    ("CommitGpuWrite callers", r"CommitGpuWrite(", ["src"]),
    ("CompletePendingUpload callers", r"CompletePendingUpload(", ["src"]),
    ("FreeImage callers", r"FreeImage(", ["src"]),
    ("SynchronizeBufferFromImage callers", r"SynchronizeBufferFromImage(", ["src"]),
    ("DownloadImageMemory callers", r"DownloadImageMemory(", ["src"]),
    ("DB_RENDER_OVERRIDE handlers", r"Pm4::DB_RENDER_OVERRIDE]", ["src"]),
    ("SetGraphicsDynamicParams callers", r"SetGraphicsDynamicParams(", ["src"]),
]
full = subprocess.run(["git", "-C", REPO, "rev-parse", REV], capture_output=True, text=True).stdout.strip()
out = ["rev %s (%s)" % (REV, full)]
for title, pat, paths in PATTERNS:
    r = subprocess.run(["git", "-C", REPO, "grep", "-n", "-F", pat, REV, "--"] + paths, capture_output=True, text=True)
    lines = [ln.split(":", 1)[1] for ln in r.stdout.splitlines() if ln]
    code = [ln for ln in lines if not ln.split(":", 2)[2].lstrip().startswith("//")]
    out.append("== %s: %d lines (%d not comments)" % (title, len(lines), len(code)))
    for ln in code:
        p = ln.split(":", 2)
        out.append("  %s:%s  %s" % (p[0], p[1], p[2].strip()[:140]))
out.append("script sha256 %s" % hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest())
out.append("ALL OK")
open(OUT, "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("\n".join(out))
