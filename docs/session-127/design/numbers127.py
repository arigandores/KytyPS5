#!/usr/bin/env python3
# Session 127, step 1 (HPP-105), Probe Designer: the rows design127.md cites from EXISTING logs.  Read only; no run.
# Rows, not a verdict and not a forecast (ROADMAP s122 item 76(l)).
#   k3c126: census arm C (rk3cen=1), rows = FrameTrace-x lines with rk3_n > 0 (every C row, window not applied - the
#           recount of the audit, docs/session-126/audit/recount126.out.json, is the windowed number).
#   cen120: spcen arm P, the would-hit A counters of the same-pass render-target memo (sp_rt_*).
import hashlib
import re
import sys

LOGS = {
    "k3c126": "C:/kyty/s126/log_k3c126.txt",
    "cen120": "C:/kyty/s120/log_cen120.txt",
}
K3 = ["rk3_n", "rk3_rec0", "rk3_xw", "rk3_w", "rk3_wi", "rk3_xid", "rk3_xctx", "rk3_slow", "rk3_wr_set",
      "rk3_wr_obj", "rk3_dclr", "rk3_rt_ns", "rk3_res_ns", "rk3_rt_r_ns", "rk3_res_r_ns"]
SP = ["sp_rt_n", "sp_rt_would", "sp_rt_bad", "sp_rt_race", "sp_rt_rst"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(path, keys, arm_key):
    tot = {k: 0 for k in keys}
    n = 0
    pats = {k: re.compile(rb"\b" + k.encode() + rb"=(\d+)") for k in keys}
    arm = re.compile(rb"\b" + arm_key.encode() + rb"=(\d+)")
    with open(path, "rb") as f:
        for line in f:
            if b"FrameTrace-x:" not in line:
                continue
            m = arm.search(line)
            if not m or int(m.group(1)) == 0:
                continue
            n += 1
            for k, p in pats.items():
                mm = p.search(line)
                if mm:
                    tot[k] += int(mm.group(1))
    return n, tot


def main():
    for tag, path in LOGS.items():
        print(f"{tag}: {path} sha256 {sha(path)[:8]}")
    n, t = rows(LOGS["k3c126"], K3, "rk3_n")
    print(f"k3c126 armed rows {n}")
    for k in K3:
        print(f"  {k:14s} {t[k] / n:14.1f} /row")
    print(f"  rt ns/draw {t['rk3_rt_ns'] / t['rk3_n']:.1f}  res ns/draw {t['rk3_res_ns'] / t['rk3_n']:.1f}")
    print(f"  w/n {t['rk3_w'] / t['rk3_n']:.4f}  xw/n {t['rk3_xw'] / t['rk3_n']:.4f}  "
          f"wr_obj/row {t['rk3_wr_obj'] / n:.1f}")
    n, t = rows(LOGS["cen120"], SP, "sp_rt_n")
    print(f"cen120 armed rows {n}")
    for k in SP:
        print(f"  {k:14s} {t[k] / n:14.1f} /row  (sum {t[k]})")
    print(f"  would/draws {t['sp_rt_would'] / max(t['sp_rt_n'], 1):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
