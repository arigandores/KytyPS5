#!/usr/bin/env python3
# Session 127, step 2a (HPP-114), Probe Designer: rows design127.md rev 2 cites for RC3 (counter Adds a skip removes) and
# RC10 / Q3 (rt_kpx / rt_att by arm).  Read only; no run.  Rows, not a verdict and not a forecast.
#   k3c126 arm C rows = FrameTrace-x lines with rk3_n > 0 (every C row, window NOT applied); arm B rows = the other
#   FrameTrace-x lines after the first GateArm: line.  rt_hits lives on FrameTrace-draw, joined by n=.
import hashlib
import re
import sys

LOG = "C:/kyty/s126/log_k3c126.txt"
NUM = re.compile(rb"\bn=(\d+)")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def val(line, key):
    m = re.search(rb"\b" + key + rb"=(\d+)", line)
    return int(m.group(1)) if m else None


def main():
    print(f"k3c126: {LOG} sha256 {sha(LOG)[:8]}")
    hits = {}
    xrows = []
    armed = False
    with open(LOG, "rb") as f:
        for line in f:
            if line.startswith(b"GateArm:") or b" GateArm: " in line:
                armed = True
                continue
            if not armed:
                continue
            if b"FrameTrace-draw:" in line:
                m = NUM.search(line)
                h = val(line, b"rt_hits")
                if m and h is not None:
                    hits[int(m.group(1))] = h
            elif b"FrameTrace-x:" in line:
                m = NUM.search(line)
                if not m:
                    continue
                xrows.append((int(m.group(1)), val(line, b"rk3_n") or 0, val(line, b"rt_fast_ok") or 0,
                              val(line, b"rt_att") or 0, val(line, b"rt_kpx") or 0))
    for name, pick in (("C (rk3_n>0)", lambda r: r[1] > 0), ("B (rk3_n=0)", lambda r: r[1] == 0)):
        rs = [r for r in xrows if pick(r)]
        draws = sum(r[1] for r in rs)
        att = sum(r[3] for r in rs)
        fok = sum(r[2] for r in rs)
        rh = sum(hits.get(r[0], 0) for r in rs)
        ratios = [r[4] / r[3] for r in rs if r[3] > 0]
        zero = sum(1 for r in rs if r[3] == 0)
        mean = sum(ratios) / len(ratios) if ratios else 0.0
        print(f"arm {name}: rows {len(rs)}  rt_att=0 rows {zero}")
        print(f"  rt_kpx/rt_att mean of rows {mean:.2f}  min {min(ratios):.2f}  max {max(ratios):.2f}")
        print(f"  per row: rt_att {att / len(rs):.1f}  rt_hits {rh / len(rs):.1f}  rt_fast_ok {fok / len(rs):.1f}")
        if draws:
            print(f"  per draw (rk3_n {draws / len(rs):.1f}/row): rt_att {att / draws:.3f}  rt_hits {rh / draws:.3f}"
                  f"  rt_fast_ok {fok / draws:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
