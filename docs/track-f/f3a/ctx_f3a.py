# F3a (HPP-308): extract the translation dump of 380bb9d6 and the context of trip / fault lines.
import sys, os, collections

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
D = "C:/kyty/f287/f3a/"
RANGES = {
    "c142_02": ("C:/kyty/s142/log_c142_02.txt", [(257240, 266215, "dump_380b_c142_02.txt"),
                                                 (267060, 267100, None), (267940, 267960, None),
                                                 (269080, 269185, None), (273860, 273915, None)]),
    "c142_09": ("C:/kyty/s142/log_c142_09.txt", [(206290, 206310, None), (206410, 206422, None),
                                                 (206620, 206650, None), (207260, 207300, None),
                                                 (207360, 207395, None)]),
}
out = []
for tag, (path, rs) in RANGES.items():
    hi = max(r[1] for r in rs)
    bufs = {r: [] for r in rs}
    prefix = collections.Counter()
    n = 0
    with open(path, "rb") as f:
        for raw in f:
            n += 1
            if n > hi:
                break
            for r in rs:
                if r[0] <= n <= r[1]:
                    bufs[r].append((n, raw.rstrip(b"\r\n")))
    for r in rs:
        if r[2]:
            with open(D + r[2], "wb") as g:
                for n_, raw in bufs[r]:
                    g.write(b"%d\t" % n_ + raw + b"\n")
            out.append("== %s lines %d-%d -> %s (%d lines)" % (tag, r[0], r[1], r[2], len(bufs[r])))
        else:
            out.append("== %s lines %d-%d" % (tag, r[0], r[1]))
            for n_, raw in bufs[r]:
                out.append("  %d %s" % (n_, raw.decode("utf-8", "replace")[:230]))
open(D + "ctx_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print(len(out))
