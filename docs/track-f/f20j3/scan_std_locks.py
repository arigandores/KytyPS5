#!/usr/bin/env python3
# F20j3 (HPP-646): draft scanner - std:: lock sites, the mutex expression, the lock scope and heavy tokens inside it.
import os, re, sys

ROOT = sys.argv[1]
LOCK = re.compile(r"std::(lock_guard|unique_lock|scoped_lock|shared_lock)(?:\s*<[^>]*>)?\s+\w+\s*[({]\s*([^,;)}]+)")
HEAVY = re.compile(r"\bvk[A-Z]\w*\(|device\.\w+\(|\.(create|Create)\w*\(|Wait\w*\(|\.wait\w*\(|Sleep\w*\(|sleep_for|LOGF\(|Log::|"
                   r"printf\(|fopen|fwrite|fread|WriteFile|ReadFile|VirtualProtect|Translate\w*\(|Compile\w*\(|SDL_\w+\(|"
                   r"submit\(|presentKHR|\.join\(|EXIT\(|Present\(")

def files():
    for d, _, fs in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT).replace("\\", "/")
        if rel.startswith("graphics/shader") or rel.startswith("launcher"):
            continue
        for f in fs:
            if f.endswith((".cpp", ".h", ".inc")):
                yield os.path.join(d, f)

def scope_end(lines, i):
    # the lock lives until the closing brace of the block that contains line i, or an explicit unlock() of its name
    depth = 0
    for j in range(i, len(lines)):
        t = re.sub(r"//.*", "", lines[j])
        t = re.sub(r'"([^"\\]|\\.)*"', '""', t)
        if j == i:
            k = t.find(";")
            t = t[k + 1:] if k >= 0 else ""
        for c in t:
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth < 0:
                    return j
    return len(lines) - 1

rows = []
for p in sorted(files()):
    lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
    rel = os.path.relpath(p, ROOT).replace("\\", "/")
    for i, l in enumerate(lines):
        if l.strip().startswith("//"):
            continue
        m = LOCK.search(l)
        if not m:
            continue
        mx = m.group(2).strip()
        end = scope_end(lines, i)
        name = re.sub(r"\s+", "", mx)
        unl = None
        var = re.search(r"std::\w+(?:\s*<[^>]*>)?\s+(\w+)", l).group(1)
        for j in range(i + 1, end + 1):
            if re.search(r"\b" + var + r"\.unlock\(\)", lines[j]):
                unl = j
                break
        stop = unl if unl is not None else end
        heavy = []
        for j in range(i + 1, stop):
            h = HEAVY.search(re.sub(r"//.*", "", lines[j]))
            if h:
                heavy.append(f"{j+1}:{h.group(0)}")
        rows.append((rel, i + 1, m.group(1), name, stop - i, heavy))

by = {}
for r in rows:
    key = (r[0], r[3])
    by.setdefault(key, []).append(r)
for (f, name), rs in sorted(by.items()):
    hv = [h for r in rs for h in r[5]]
    print(f"{f}\t{name}\tsites={len(rs)}\tmaxspan={max(r[4] for r in rs)}\theavy={len(hv)}\t{' '.join(hv[:6])}")
print("TOTAL sites", len(rows), "mutex keys", len(by))
