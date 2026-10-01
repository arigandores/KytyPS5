#!/usr/bin/env python3
# s144 close (HPP-334): course row 144 by script (ROADMAP p.259(v) "the course row is counted by the s144 close with a script").
# Base: course 142 rows reproduced from docs/track-f/register.md section 4 (33 = register 41 minus 7 new F0 rows minus B34);
# then the decisions in order: p.237(b) V3, p.254(g), p.259(v), p.273(g). Defect column per p.228(b). LOCAL ONLY.
from collections import Counter
from pathlib import Path

REG = Path("C:/kyty/KytyPS5/docs/track-f/register.md")
L = REG.read_text(encoding="utf-8").split("\n")
i0 = L.index("## 4. Реестр")
rows = {}
for l in L[i0:]:
    if l.startswith("## 5."):
        break
    if l.startswith("| Б") or l.startswith("| Ф"):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 5:
            k = c[1].split()[0]
            rows[c[0]] = [k, c[2].split()[0].rstrip(";,")]
assert len(rows) == 41, len(rows)
F0NEW = {"Ф5", "Ф3", "Ф7", "Б9а", "Ф4", "Ф6", "Ф8"}
course = {n: v for n, v in rows.items() if n not in F0NEW and n != "Б34"}
assert len(course) == 33


def count(c):
    k = Counter(v[0] for v in c.values())
    d = sum(1 for v in c.values() if v[1] == "дефект")
    return [k["K1"], k["K2"], k["K3"], k["K4"], k["K5"]], len(c), d


k, n, d = count(course)
print("course 142 (register s4):", k, n, "defects", d)
assert k == [2, 1, 6, 17, 7] and n == 33
# p.237(b) V3: B1b K4 -> K3; B3b -> NE DEFEKT (closed)
course["Б1б"][0] = "K3"
del course["Б3б"]
# p.254(g): B35 new K4 defect, B36 new K2 defect, B5a K4 -> K2
course["Б35"] = ["K4", "дефект"]
course["Б36"] = ["K2", "дефект"]
course["Б5а"][0] = "K2"
k, n, d = count(course)
print("course 143 recount:", k, n, "defects", d, "(p.254(z) printed 35: 2/3/6/17/7)")
# p.259(v): B26 closed (B26a TUPIK, B26b FIXED); new K4: B26v, B26g (observations), F9 (defect), F10 (observation)
del course["Б26"]
course["Б26в"] = ["K4", "наблюдение"]
course["Б26г"] = ["K4", "наблюдение"]
course["Ф9"] = ["K4", "дефект"]
course["Ф10"] = ["K4", "наблюдение"]
# p.273(g): B37 new K4 defect; B38 new K5 (out of track)
course["Б37"] = ["K4", "дефект"]
course["Б38"] = ["K5", "вне"]
k, n, d = count(course)
print("course 144:", k, n, "defects", d)
print("defects:", ", ".join(sorted(x for x, v in course.items() if v[1] == "дефект")))
assert k == [2, 3, 7, 19, 8] and n == 39 and d == 15
print("ALL OK")
