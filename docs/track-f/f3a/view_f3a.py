# F3a (HPP-308): compact view of scan_f3a.out.txt + lines naming the traversal shader / BVH.
import sys, os, re

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


FIELDS = ["n", "dt_us", "lat_us", "submits", "semwaits", "semwait_us", "draws", "dispatches", "faults",
          "gpu_busy_us", "gpu_n", "cpu_gpu_us", "faults_gpu", "semwait_gpu_us", "prios"]
src = open("C:/kyty/f287/f3a/scan_f3a.out.txt", encoding="utf-8").read().split("\n")
for l in src:
    if "FrameTrace: n=" in l and not l.lstrip().startswith("-- first"):
        d = dict(re.findall(r"(\w+)=(-?\d+)", l))
        p("   F", l.split()[0], " ".join("%s=%s" % (k, d.get(k, "?")) for k in FIELDS))
    elif l.lstrip().startswith("-- first FrameTrace"):
        p(l[:200])
    else:
        p(l[:400])

LOGS = [("c142_02", "C:/kyty/s142/log_c142_02.txt"), ("c142_09", "C:/kyty/s142/log_c142_09.txt")]
for tag, path in LOGS:
    p("===== lines naming the shader or BVH:", tag)
    n = 0
    with open(path, "rb") as f:
        for raw in f:
            n += 1
            if b"380bb9d636390bae" in raw or b"BVH" in raw or (b"Bvh" in raw and b"BvhLoopCap" not in raw):
                p("   ", n, raw.rstrip().decode("utf-8", "replace")[:500])
open("C:/kyty/f287/f3a/view_f3a.out.txt", "wb").write(("\n".join(out) + "\n").encode("utf-8"))
print(len(out))
