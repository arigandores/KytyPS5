# F3a (HPP-308): tables over sky_f3a.json - trip vs the first BVH address (X1) and its X>>8 page.
import sys, os, json, collections

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
D = "C:/kyty/f287/f3a/"
rows = json.load(open(D + "sky_f3a.json", encoding="utf-8"))
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


def x1(r):
    # first fault at an address above 4 GiB that has its X>>8 page faulted too
    for fr, a in r["fault_seq"]:
        ai = int(a, 16)
        if ai > 0x100000000 and any(int(b, 16) == ((ai >> 8) & ~0x3fff) for _, b in r["fault_seq"]):
            return a
    return None


def band(s):
    if s <= 112:
        return "103-112"
    if s <= 126:
        return "113-126"
    if s <= 141:
        return "127-141"
    return "142"


p("logs", len(rows))
with_low = [r for r in rows if r["lows"]]
p("logs with a fault page below 4 GiB:", len(with_low), "of", len(rows))
with_pair = [r for r in rows if r["pairs"]]
p("logs with a pair (X and X>>8 page both faulted):", len(with_pair))
# by band: logs, logs with trips, logs with pair
tab = collections.OrderedDict()
for r in rows:
    b = band(r["ses"])
    t = tab.setdefault(b, collections.Counter())
    t["logs"] += 1
    t["trip"] += 1 if r["trips"] else 0
    t["pair"] += 1 if r["pairs"] else 0
    t["low"] += 1 if r["lows"] else 0
p("band | logs | with trips | with X>>8 page fault | with pair")
for b, t in tab.items():
    p(" ", b, "|", t["logs"], "|", t["trip"], "|", t["low"], "|", t["pair"])
assert sum(t["logs"] for t in tab.values()) == len(rows)
assert sum(t["trip"] for t in tab.values()) == sum(1 for r in rows if r["trips"])
# per session
ps = collections.OrderedDict()
for r in sorted(rows, key=lambda r: r["ses"]):
    t = ps.setdefault(r["ses"], collections.Counter())
    t["logs"] += 1
    t["trip"] += 1 if r["trips"] else 0
p("per session logs/trip:", " ".join("%d:%d/%d" % (s, t["logs"], t["trip"]) for s, t in ps.items()))
# X1 vs trip
byx = collections.OrderedDict()
for r in rows:
    k = (band(r["ses"]), x1(r), tuple(r["lows"]))
    t = byx.setdefault(k, collections.Counter())
    t["logs"] += 1
    t["trip"] += 1 if r["trips"] else 0
p("band | X1 (first BVH address with its X>>8 page) | low pages | logs | with trips")
for k in sorted(byx, key=lambda k: (k[0], str(k[1]), k[2])):
    p(" ", k[0], "|", k[1], "|", ",".join(k[2]), "|", byx[k]["logs"], "|", byx[k]["trip"])
assert sum(t["logs"] for t in byx.values()) == len(rows)
# the trip logs in detail
p("trip logs:")
for r in rows:
    if r["trips"]:
        lowf = [fr for fr, a in r["fault_seq"] if int(a, 16) < 0x100000000]
        p(" ", r["ses"], r["path"].replace("C:/kyty/", ""), "trips", r["trips"], "sum", r["trip_sum"], "frames", r["trip_frames"],
          "X1", x1(r), "low", r["lows"], "seq", r["fault_seq"][:6], "cap", r["cap"])
# does every trip episode sit between the first and the second low-page fault?
ok = n = 0
for r in rows:
    if not r["trips"]:
        continue
    lowf = [fr for fr, a in r["fault_seq"] if int(a, 16) < 0x100000000 and fr is not None]
    tf = r["trip_frames"]
    n += 1
    if len(lowf) >= 2 and tf and lowf[0] < tf[0] and tf[-1] <= lowf[1] + 1:
        ok += 1
    else:
        p("  NOT between:", r["path"], lowf, tf)
p("trip episodes lying between the 1st and the 2nd X>>8 page fault (frame of 2nd + 1 allowed):", ok, "of", n)
p("sums checked: 3 asserts")
open(D + "skytab_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print("\n".join(out))
