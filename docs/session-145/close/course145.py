#!/usr/bin/env python3
# s145 close (HPP-354): course row 145 by script (ROADMAP s122 p.309(zh)). Port of C:/kyty/s144/step4/course144.py:
# the s144 count reproduced first (asserted), then the decisions after p.273 in order: p.277(v) F11, p.280(zh) F12, p.281(a) B35 FIXED,
# p.282(a) B1b and F9 FIXED, p.287(b) B9b (born TUPIK - not open) and F13, p.294(d) F14, p.298(a) B37 FIXED, p.309(e) B39 and B40.
# Rule of the count (p.309(zh)): open = not FIXED, not TUPIK, not NE DEFEKT (as row 144: B26 dropped at B26a TUPIK + B26b FIXED).
# The second line prints the open rows that still act on the installed 9235a7ac (FIXED awaiting the shipment install). LOCAL ONLY.
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


# the s144 count (course144.py, p.273(d)) reproduced
course["Б1б"][0] = "K3"
del course["Б3б"]
course["Б35"] = ["K4", "дефект"]
course["Б36"] = ["K2", "дефект"]
course["Б5а"][0] = "K2"
del course["Б26"]
course["Б26в"] = ["K4", "наблюдение"]
course["Б26г"] = ["K4", "наблюдение"]
course["Ф9"] = ["K4", "дефект"]
course["Ф10"] = ["K4", "наблюдение"]
course["Б37"] = ["K4", "дефект"]
course["Б38"] = ["K5", "вне"]
k, n, d = count(course)
print("course 144 (reproduced):", k, n, "defects", d)
assert k == [2, 3, 7, 19, 8] and n == 39 and d == 15
# after p.273
course["Ф11"] = ["K4", "наблюдение"]          # p.277(v), register s13
course["Ф12"] = ["K5", "дефект"]              # p.280(zh), register s14
fixed = {}
for x in ("Б35", "Б1б", "Ф9", "Б37"):          # p.281(a), p.282(a), p.298(a): FIXED by track F (register s15, s16, s19)
    fixed[x] = course.pop(x)
# B9b: born TUPIK (p.287(b), register s17) - not open by the rule; register delta "K4 +1" corrected by p.309(zh)
course["Ф13"] = ["K5", "дефект"]              # p.287(b), register s17
course["Ф14"] = ["K5", "дефект"]              # p.294(d), register s18
course["Б39"] = ["K4", "наблюдение"]          # p.309(e)(1), register s21
course["Б40"] = ["K2", "дефект"]              # p.309(e)(2), register s21
k, n, d = count(course)
print("course 145:", k, n, "defects", d)
print("defects:", ", ".join(sorted(x for x, v in course.items() if v[1] == "дефект")))
inst = dict(course)
inst.update(fixed)
ki, ni, di = count(inst)
print("on the installed 9235a7ac (FIXED awaiting install: %s):" % ", ".join(sorted(fixed)), ki, ni, "defects", di)
assert k == [2, 4, 6, 18, 11] and n == 41 and d == 15
assert ki == [2, 4, 7, 21, 11] and ni == 45 and di == 19
print("ALL OK")
