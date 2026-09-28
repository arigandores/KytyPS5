# -*- coding: utf-8 -*-
"""s128 audit (HPP-125): append the Step 9 section to C:/kyty/s128/FACTS.md. LF; write_bytes; refuses a second append."""
from pathlib import Path

P = Path('C:/kyty/s128/FACTS.md')
SEC = '''
## Step 9 — audit (Session Auditor, HPP-125; ROADMAP s122 p. 87(ж), 93(д))

Time scale of this section: **UTC** (platform API, `TZ=UTC git log`, file `mtime`). Document —
`C:/kyty/s128/audit128/AUDIT128.md` (git `docs/session-128/audit/`). No lock at any moment; no game, no build, no emulator
code, no `mutlib` (**mutant wall of this step: 0 s**). Installed build `9235a7ac…` (sha256 checked, = pinned copy).

| event (time scale: UTC) | time |
|---|---|
| step started (blocker `HPP-124` resolved, lock absent) | 2026-09-28 15:26 |
| `recount128.py` on `log_pd128.txt` (7 s), window rows, smoke `s4s128`, `shp128` sums | ≈ 15:40–15:55 |
| audit document written | ≈ 16:05 |

- **Recount — CONFIRMED to the digit** (`recount128.py`, no code shared with `pd128.py`, `step8/recount8.py`,
  `lead/recount6c_lead.py`; blocks by `GateArm:`, `n = frame + 1 + p`, window 10..88 inclusive p. 55(б), mean of window
  rows, SE over ABBA pairs, BDA from `FrameTrace-draw`). `pd128`, NEW, 42 pairs: **Δ `dt_us` +1 016,84 ± 140,76; Δ_adj
  +1 023,81 ± 118,23 (β 6,656541)** ⇒ lower +876,08 ≥ +500 ⇒ **`K14_OPEN`**; OLD 0 pairs. Base p. 87(е)(7)/93(г)(4)
  **31 700,65 µs** (arm 0, 3 397 rows, 43 blocks, NEW, `45d36512`; 52,58 %; not comparable with 50,36 %). Dose guards:
  delivery 1,00755 (complete blocks) / **1,00753** with the window of incomplete block 85 (= scorer), per block
  1,0032…1,0185, 0 arm-2 blocks without dose, arm-0 window dose 0, whole-log `pc_u_set`/`pc_skip_n`/`pc_refuse` 0; one
  `ProtCeil: mode 2`, one `RtSkip: mode 1`, 0 refused, 0 death markers; DRS 2 007,626 / 2 007,590. Windows 10..87 / 60..88 /
  0..89 — `K14_OPEN` in all (rows).
- Smoke `s4s128` by the same parser: 16 pairs OLD, +995,02 ± 269,37, delivery 1,00935 — equal to §Step 6c. Shipping video
  `shp128`: Σ`rts_skip` 16 989 163 / Σ`rts_n` 19 210 396, one `RtSkip: mode 1`, 0 refused; `ffprobe` 4 026 frames = index;
  0 one-frame glitches; the sheet `sheet_a_o5.png` viewed — same scene, animation phase differs.
- **Protocol: 0 MAJOR, 3 MINOR** (verdict unchanged): (1) the lead recount named in p. 95(а) (`lead/recount6c_lead.py`)
  does not produce the cited numbers — run by the auditor it gives +975,15 ± 247,64, delivery 1,00950, `bda_scan` 0/0
  (slices `main[10:89]`, reads `bda_scan` from `-x`); the numbers of p. 95(а) are right (scorer, `step6c/recount6c.py`,
  audit), the provenance is not; (2) the value-1 refusal added to `go128a.sh` in step 6c is new stage logic (rc 1 before DRY)
  — no `--only` (p. 84(в)(3)) and no stop-and-ask with ≈ 2,4 min of budget left (p. 91(г), 93(д)); covered by fixtures v1–v6
  and a negative control only; (3) OLD (0 pairs) is not in the scorer's debt list while p. 93(г)(4) / seal §5 say "< 10
  pairs — debt". Row: the header of p. 93 says "12:50 UTC", the commit `1369d6ac` is 12:44:45 — before step 6a (12:47:30).
- Load during `pd128` (15:16:25–15:21:59): the only agent run was step 8 itself (`46a54e9b`); no commits; procload clean.
  Video `shp128` overlapped the step-4 Emu Engineer run and a lead acceptance run — not a timed run (row).
- **Not proven:** that Δ `pd128` equals the gain of any mechanism (calibration; linearity [I]; lock-hold wait of other
  threads [U]; kernel side effects [U]); that a mechanism moving the arming off GuestGpu pays (value 1 hung the GPU; `armdefer`,
  `protbatch2` did not pay); OLD; other scenes; the time of the installed `9235a7ac` (base is on `45d36512`); tests of
  `protceil` at 1/2. 60 FPS not promised.
- Debts for the close (`HPP-126`): K14 in OLD; linearity checked by the first prototype ABBA; time of `9235a7ac` / cost of the
  measurement code at 0; `protceil=1` hangs the GPU — into the env record of `CLAUDE.md`; tests at 1/2; MINOR-1…3.
'''

t = P.read_bytes().decode('utf-8')
assert chr(13) not in t
assert '## Step 9' not in t, 'already appended'
if not t.endswith(chr(10)):
    t += chr(10)
P.write_bytes((t + SEC).encode('utf-8'))
print('appended', len(SEC), 'chars')
