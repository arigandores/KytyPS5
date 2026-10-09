# F30i (HPP-719, Red Team): checks of the review of F30h. Offline, read only: git show / git grep in C:/kyty/KytyPS5,
# the lead recount C:/kyty/f287/lead/p653/lead_f30f.out.txt and docs/track-f/f30h/gamma.out.txt. Prints ALL OK.
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = "C:/kyty/KytyPS5"
GIT = "C:/Program Files/Git/cmd/git.exe"
T = "a1d1d863"
RM = "8518d69b"
ok = True


def show(rev, path):
    return subprocess.run([GIT, "-C", REPO, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout.decode(
        "utf-8").replace("\r", "").split("\n")


def anchor(lines, n, text):
    # whole-line anchor (stripped), 1-based line number
    return 1 <= n <= len(lines) and lines[n - 1].strip() == text


def check(name, cond, detail=""):
    global ok
    print(("OK   " if cond else "FAIL ") + name + (" | " + detail if detail else ""))
    ok &= bool(cond)


rd = show(T, "src/graphics/host_gpu/renderer/renderDraw.cpp")
refs = [
    ("X1 depth load-clear sets X without the record", 3772, "if (hd && state.depth_info.depth_load_clear_enable) {"),
    ("X1+1", 3773, "bits |= 0x020u;"),
    ("R compare", 3761, "if (!(rendering == rec->state)) {"),
    ("load-clear source: register OR HTile meta", 2203, "depth.depth_load_clear_enable = depth.depth_clear_enable || meta_clear;"),
    ("RenderState carries the clear flag", 2312, "attachment.depth_clear    = depth.depth_load_clear_enable;"),
    ("attachment is RenderState's", 2306, "auto&      attachment     = state.depth_stencil_attachment;"),
    ("capture state is RenderState", 2066, "RenderState state {};"),
    ("extents reset per capture", 2070, "g_pass_extents              = {}; // session 72: rpa_tkpx / rpa_mix, see renderTarget.h"),
    ("rx counter merges R and X", 1576, "if ((bits & 0x030u) != 0) {"),
    ("rx counter +1", 1577, "FS::Add(FS::Counter::RtsBadRx, 1);"),
    ("A-diff depth compares clear enable", 1521,
     "if (!RtsSameDesc(a.desc, b.desc) || a.depth_clear_enable != b.depth_clear_enable ||"),
    ("PA item 3 off at =3", 3470, "} else if (t_rts != 3 && t_rts_reg) {"),
    ("PA and PB: record not refreshed", 3801, "if (t_rts_pb) {"),
    ("PA and PB: re-pin only", 3803, "rec->age++;"),
    ("skip path forces layout without transition", 3704, "image.binding.attachment_layout = t.att_layout;"),
    ("S bit", 3781, "bits |= 0x040u; // S"),
]
for name, n, text in refs:
    check(f"{T}:renderDraw.cpp:{n} {name}", anchor(rd, n, text))
# negative controls: the same anchors shifted by one line must be rejected
neg = sum(1 for _, n, text in refs[:4] if anchor(rd, n + 1, text))
check("negative controls (+1 shift) rejected", neg == 0, f"accepted {neg} of 4")

# scope of F30h (i): files under src/ that read t_rts or the knob RtSkip
g = subprocess.run([GIT, "-C", REPO, "grep", "-l", "-E", r"\bt_rts\b|Knob::RtSkip|RtsReport\(", T, "--", "src"],
                   capture_output=True).stdout.decode("utf-8").split("\n")
files = sorted({x.split(":", 1)[1] for x in g if x})
print("files reading t_rts / Knob::RtSkip / RtsReport(:", files)
check("t_rts / RtsReport only in renderDraw.cpp (+ knob table)",
      all(f.endswith("renderDraw.cpp") or "/common/" in f or f.endswith("gates.cpp") or f.endswith("gates.h")
          for f in files), str(files))
knob_users = subprocess.run([GIT, "-C", REPO, "grep", "-n", "Knob::RtSkip", T, "--", "src"],
                            capture_output=True).stdout.decode("utf-8").strip().split("\n")
print("Knob::RtSkip readers:")
for x in knob_users:
    print("  ", x[:200])

# ROADMAP 643(v): the lead separated control A (=3) and control B (=4) before data
rm = "\n".join(show(RM, "docs/ROADMAP.md"))
q643 = "Отдельно от `=3` — чтобы контроль A (регистры) и контроль B (не-регистровые предикаты захвата) читались каждый своим тегом."
check("643(v) separation quote present at " + RM, q643 in rm)
q643d5 = "(5) **Контроль B жив (К_B):** у `c4` Σ `rts_bad_rx` процесса ≥ 1"
check("643(d)(5) quote present", q643d5 in rm)
q654v = "**Это чтение основанием К_B не служит**"
check("654(v) quote present", q654v in rm)
reg = "\n".join(show(RM, "docs/track-f/register.md"))
row28 = [l for l in reg.split("\n") if l.startswith("| Б28 |")]
check("register row B28 criterion names the =3 control", len(row28) == 1 and "контроль `rtskip=3` падает" in row28[0])

# lead recount: c3 rx = b, c3 bad >> b; xb_pass ranges cited by F30h 3.2; c4/v xb_ser = xb_meta = 0 (s8_v meta 1)
L = open("C:/kyty/f287/lead/p653/lead_f30f.out.txt", encoding="utf-8").read().split("\n")
rows = {}
for l in L:
    m = re.match(r"(f30_s\d_(c3|c4|v)) ", l)
    if m:
        rows[m.group(1)] = {k: int(v) for k, v in re.findall(r"\b([a-z_]+)=(\d+)\b", l.split("|")[1])}
check("27 rows", len(rows) == 27)
c3 = [rows[f"f30_s{k}_c3"] for k in range(1, 10)]
check("c3: bad_rx == bad_b on 9 of 9", all(r["bad_rx"] == r["bad_b"] for r in c3))
frac = [r["bad_b"] / r["bad"] for r in c3]
print("c3 share of B reports in all reports:", ", ".join(f"{x:.4f}" for x in frac))
check("c3: B reports are a minority of reports (A-only reports dominate)", max(frac) < 0.15)
c4p = [rows[f"f30_s{k}_c4"]["xb_pass"] for k in range(1, 10)]
vp = [rows[f"f30_s{k}_v"]["xb_pass"] for k in range(1, 10)]
check("xb_pass c4 17367..2064300", min(c4p) == 17367 and max(c4p) == 2064300)
check("xb_pass v 34581..4813357", min(vp) == 34581 and max(vp) == 4813357)
check("c4, v: xb_ser = 0, xb_ids = 0", all(rows[t]["xb_ser"] == 0 and rows[t]["xb_ids"] == 0
                                           for t in rows if not t.endswith("c3")))
check("c4, v: bad = 0", all(rows[t]["bad"] == 0 for t in rows if not t.endswith("c3")))

# gamma: the only natural PB-4 bursts under PA are two cymbal_party_land entries of session 145 (binary 9235a7ac)
G = open(REPO + "/docs/track-f/f30h/gamma.out.txt", encoding="utf-8").read().split("\n")
hits = [l for l in G if l.startswith("HIT ")]
cym = [l for l in hits if "cymbal_party_land" in l]
check("gamma: 2 cymbal hits, both s145", len(cym) == 2 and all("/s145/" in l for l in cym))
lv = [l for l in G if l.startswith("LVL cymbal_party_land ")]
check("gamma: cymbal entries total 2 in the whole sweep", len(lv) == 1 and lv[0].split()[2] == "2")

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
