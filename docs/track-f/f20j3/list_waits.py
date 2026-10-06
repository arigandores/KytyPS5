#!/usr/bin/env python3
# F20j3 (HPP-646): draft lister - every blocking-wait line in src with its enclosing function (column-0 definition).
import os, re, sys

ROOT = sys.argv[1]
PAT = re.compile(r"\.(Wait|WaitFor)\(|\.(wait|wait_for|wait_until)\(|->(Wait|WaitFor|wait|wait_for)\(|WaitForSingleObject\(|"
                 r"WaitForMultipleObjects\(|SleepMicro\(|sleep_for\(|(?<![A-Za-z_])Sleep\(|\.acquire\(\)|WaitOnAddress\(|"
                 r"SleepConditionVariable|EnterCriticalSection\(")
FUNC = re.compile(r"^[A-Za-z_][^;]*?([A-Za-z_~][A-Za-z_0-9:<>~]*)\s*\(")

def files():
    for d, _, fs in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT).replace("\\", "/")
        if rel.startswith("graphics/shader") or rel.startswith("launcher"):
            continue
        for f in fs:
            if f.endswith((".cpp", ".h", ".inc")):
                yield os.path.join(d, f)

for p in sorted(files()):
    lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
    rel = os.path.relpath(p, ROOT).replace("\\", "/")
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("//") or not PAT.search(l):
            continue
        func = "-"
        for j in range(i, -1, -1):
            t = lines[j]
            if t[:1] in ("", " ", "\t", "}", "#", "/", "{"):
                continue
            if t.startswith(("namespace", "class ", "struct ", "using ", "template", "static_assert", "enum ", "KYTY_SUBSYSTEM", "LIB_")):
                if t.startswith("template"):
                    continue
                break
            m = FUNC.match(t)
            if m:
                func = m.group(1)
            break
        print(f"{rel}:{i+1}\t{func}\t{s[:110]}")
