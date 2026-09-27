# Session 126, step 1 (HPP-84), Probe Designer: the cheap path of ROADMAP s122 item 62(zh)(3).
# Read-only over two sealed scorer outputs; prints what they can say about R_K3+ (design126.md s.1).
# Usage: python cheap126.py [spc120_cen120.json] [obs116.score.json]
import hashlib
import json
import sys

SPC = sys.argv[1] if len(sys.argv) > 1 else "C:/kyty/s120/runs120/spc120_cen120.json"
OBS = sys.argv[2] if len(sys.argv) > 2 else "C:/kyty/s116/runs116/obs116.score.json"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r is not None:
                return r
    return None


spc = json.load(open(SPC, encoding="utf-8"))
p = spc["report"]["0"]  # arm 0 = P (spcen=1 pathlap=1 mutsite=1), per-frame means of the scorer's window
print("spc120/cen120 sha256", sha(SPC)[:16], "build", spc["build_sha256"][:8], "regime", p["bda_regime"],
      "frames", p["frames"])
n = p["sp_rt_n"]
rt = p["pl_em_rt_ns"] / 1000.0
hit = p["pl_em_rt_hit_ns"] / 1000.0
print("  sp_rt_n            %9.1f draws/frame" % n)
print("  sp_rt_would        %9.1f (%.1f %%)" % (p["sp_rt_would"], 100.0 * p["sp_rt_would"] / n))
for k in ("memo", "cfg", "dclr", "meta", "ids", "live", "ser", "bound", "dsmp", "pass"):
    print("  sp_rt_x_%-10s %9.1f" % (k, p["sp_rt_x_" + k]))
miss = n - p["sp_rt_would"]
print("  pl_em_rt   (all)   %9.1f us/frame  (%.0f ns/draw)" % (rt, 1000.0 * rt / n))
print("  pl_em_rt_hit (S_A) %9.1f us/frame  (%.0f ns/draw)" % (hit, 1000.0 * hit / p["sp_rt_would"]))
print("  miss remainder     %9.1f us/frame  (%.0f ns/draw)" % (rt - hit, 1000.0 * (rt - hit) / miss))
print("  rt_fast_ok / draw  %9.2f   rt_fast_no/frame %.1f" % (p["rt_fast_ok"] / n, p["rt_fast_no"]))
print("  G_A %.1f  N_A %.1f  N_A_up %.1f (sealed members)" % (spc["terms"]["G_A"], spc["terms"]["N_A"],
                                                             spc["terms"]["N_A_up"]))

obs = json.load(open(OBS, encoding="utf-8"))
print("obs116 score sha256", sha(OBS)[:16])
for key in ("pl_em_rt", "pl_em_n", "mh_rt_us", "draws"):
    v = find_key(obs, key)
    print("  %-10s %s" % (key, json.dumps(v)[:160]))
print("ALL OK")
