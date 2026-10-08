# F29d (HPP-703, Red Team): my stand matrix (runs/clean.txt) against F29c edition 2 (e2/runs/summary.txt) on the fields
# named by ROADMAP s122 item 642(b): B12-10n / B12-9n at 1 and the =0 controls of B12-10n and B12-1.
import re

KV = re.compile(r"(\w+)=([^ |" + chr(10) + r"]+)")
theirs = {}
for line in open("C:/kyty/KytyPS5/docs/track-f/f29c/e2/runs/summary.txt", encoding="utf-8"):
    m = re.match(r"(x[01]_\S+): (.*)", line)
    if m:
        theirs[m.group(1)] = dict(KV.findall(m.group(2)))
mine = {}
for line in open("C:/kyty/f287/f29d/runs/clean.txt", "rb").read().decode("utf-8").replace(chr(13), "").split(chr(10)):
    m = re.match(r"(\S+) rc=0 (.*)", line)
    if m:
        mine[m.group(1)] = dict(KV.findall(m.group(2)))
pairs = {}
for fix in "10":
    for hook, tag in (("lower", "10n"), ("upper", "9n")):
        for b in "01":
            pairs["x%s_B12-%s_b%s" % (fix, tag, b)] = "x%s_hole_none_hook%s_b%s_cache0" % (fix, hook, b)
    for bits in "01":
        for n in "012":
            for f in "01":
                pairs["x%s_B12-1_b%s_n%s_f%s" % (fix, bits, n, f)] = "x%s_hole_upper_b%s_n%s_f%s" % (fix, bits, n, f)
keys = ["hook_fired", "hlost", "hdirty", "lskip", "hlost1", "rewalk", "lost", "dirty"]
bad = 0
for a, b in pairs.items():
    if a not in mine or b not in theirs:
        print("MISSING", a, b)
        bad += 1
        continue
    d = [(k, mine[a].get(k), theirs[b].get(k)) for k in keys if mine[a].get(k) != theirs[b].get(k)]
    bad += len(d)
    if d:
        print(a, b, d)
print("pairs", len(pairs), "fields", len(keys), "DIFF", bad)
