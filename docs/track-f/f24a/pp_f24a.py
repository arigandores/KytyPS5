# F24a (HPP-658): the emulator's translation units that include regionManager.h, preprocessed exactly as the
# kyty_emulator target compiles them (ninja -t compdb -x of the worktree build), before and after patch_f24a.py; the
# token stream without line markers and blank lines must be the same - the test-build hooks compile to nothing there.
# Usage (inside the vcvars64 environment): python pp_f24a.py <base|after|compare>
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys

DIR = "C:/kyty/f287/f24a"
BUILD = DIR + "/build"
NINJA = os.path.expandvars("%LOCALAPPDATA%/Microsoft/WinGet/Packages/"
                           "Ninja-build.Ninja_Microsoft.Winget.Source_8wekyb3d8bbwe/ninja.exe")
UNITS = ("graphics/host_gpu/memoryTracker.cpp", "renderer/cache/bufferCache.cpp", "renderer/renderContext.cpp",
         "graphics/host_gpu/pageManager.cpp")


def units():
    # compdb.json: written by "ninja -C build -t compdb -x" from bash (Python cannot start the WinGet ninja link).
    out = open(DIR + "/compdb.json", "rb").read()
    sel = []
    for entry in json.loads(out.decode("utf-8")):
        if "kyty_emulator.dir" not in entry["command"]:
            continue
        name = entry["file"].replace(os.sep, "/").replace("\\", "/")
        for unit in UNITS:
            if name.endswith(unit):
                sel.append((unit, entry))
    if len(sel) != len(UNITS):
        sys.exit("units found %d of %d" % (len(sel), len(UNITS)))
    return sel


def preprocess(entry):
    args = shlex.split(entry["command"], posix=False)
    args = [a.strip('"') for a in args]
    keep = []
    skip_next = False
    for a in args:
        if skip_next:
            skip_next = False
            continue
        low = a.lower()
        if low in ("-c", "/c"):
            continue
        if low.startswith(("/fo", "-fo", "/fd", "-fd", "/fs", "-fs")):
            continue
        if low in ("-o",):
            skip_next = True
            continue
        if low.startswith("-clang:-m"):
            continue
        keep.append(a)
    keep.insert(1, "/E")  # before the "--" that ends the options
    res = subprocess.run(keep, capture_output=True, cwd=entry["directory"])
    if res.returncode != 0:
        sys.exit("preprocess failed: %s" % res.stderr.decode("utf-8", "replace")[:2000])
    lines = []
    for line in res.stdout.decode("utf-8", "replace").replace("\r\n", "\n").split("\n"):
        if line.startswith("#") or line.strip() == "":
            continue
        lines.append(line.strip())
    return "\n".join(lines).encode("utf-8")


def main():
    mode = sys.argv[1]
    if mode in ("base", "after"):
        for unit, entry in units():
            data = preprocess(entry)
            name = "%s/pp/%s.%s.i" % (DIR, unit.replace("/", "_"), mode)
            os.makedirs(os.path.dirname(name), exist_ok=True)
            open(name, "wb").write(data)
            print(mode, unit, len(data), hashlib.sha256(data).hexdigest()[:16])
        return
    # The only allowed difference: the __LINE__ argument of the EXIT messages of regionManager.h (the inserted lines move
    # them); everything else - every token of every other line - must be the same, line by line.
    line_arg = re.compile(rb'(regionManager\.h", )[0-9]+(,)')
    ok = True
    for unit in UNITS:
        a = open("%s/pp/%s.base.i" % (DIR, unit.replace("/", "_")), "rb").read().split(b"\n")
        b = open("%s/pp/%s.after.i" % (DIR, unit.replace("/", "_")), "rb").read().split(b"\n")
        moved = sum(1 for x, y in zip(a, b) if x != y)
        other = sum(1 for x, y in zip(a, b) if line_arg.sub(rb"\1N\2", x) != line_arg.sub(rb"\1N\2", y))
        same = len(a) == len(b) and other == 0
        ok &= same
        print(unit, "lines", len(a), len(b), "line-constant differences", moved, "other differences", other,
              "SAME_BUT_LINE_CONSTANTS" if same else "DIFFERENT")
    print("ALL OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


main()
