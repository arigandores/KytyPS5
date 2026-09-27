# -*- coding: utf-8 -*-
"""Session 122 audit: header note + audit section appended to C:/kyty/s122/FACTS.md (LF, idempotent guard)."""
from pathlib import Path

P = Path('C:/kyty/s122/FACTS.md')
s = P.read_bytes().decode('utf-8')
assert '## Audit (step 5, HPP-8' not in s, 'already patched'

OLD_HEAD = ('# Session 122 — PAUSED by the user: the bottleneck-map instrument (knob `burn`) is designed, implemented and '
            'code-reviewed but not yet smoke-tested; no sealed run; the vblank staircase found; the frame-skip plan recorded\n')
assert s.startswith(OLD_HEAD)
NEW_HEAD = ('# Session 122 — the bottleneck map through the knob `burn`: sealed burn ABBAs on five scenes (map complete by scene, '
            'partial by thread — code 1 and the placebo); reference scene NOT_RESOLVED; audited (recount CONFIRMED, 3 MAJOR / 5 MINOR)\n'
            '\n'
            '> **Header updated by the Session Auditor (HPP-8, 2026-09-27).** The previous title — "PAUSED by the user: … not yet '
            'smoke-tested; no sealed run; the vblank staircase found; the frame-skip plan recorded" — and the paragraph '
            '"Numbers" below describe the pause of 2026-09-26 and are kept as history; the session resumed (sections 4–8, '
            'Step 4, Audit). **The "vblank staircase" inference of §1.3 is refuted by `sky122` (Audit, MAJOR-2).**\n')
s = s.replace(OLD_HEAD, NEW_HEAD, 1)

s = s.rstrip('\n') + '\n' + '''
## Audit (step 5, HPP-8, Session Auditor, 2026-09-27)

Document `C:/kyty/s122/audit122/AUDIT122.md` (git `docs/session-122/audit/`), own parsers `recount122.py`, `obs122.py`,
`guards122.py` (no code shared with `map122.py`), checksums `SHA256SUMS.txt`.

* **Recount: CONFIRMED.** All six admitted runs equal the scorer to the last printed digit (Δ, 2SE, slope, interval,
  zone, draw-adjusted row, reading and its share, BDA regime, dose, game speed); a pair bootstrap (20 000) gives the same
  intervals. The block offset (row n of block k at position n − F_k − 1) was derived from the data: the first burnt row
  after an A→B switch is F + 1, and the main line's `arm=` agrees with the `GateArm:` arm on every row of all seven logs.
  A first pass shifted by one row moved Δ by ≤ 42 µs with the same zones — the verdicts are robust to the window edge.
* **Protocol: holds for the verdicts; 3 MAJOR, 5 MINOR, none changes a sealed verdict.**
  * MAJOR-1: agent work inside the sealed windows of `skyp122` and `skyp122r` (lead heartbeats on `HPP-3` committing
    ROADMAP items 22/23 and docs at 00:59, 01:09, 01:10; First agent on `HPP-19` 01:00–01:08), against item 6. The
    placebo verdict stands (unsynchronised load cannot bias an ABBA; top of the interval 0.083 ≪ 0.3), but its 2SE is not
    a clean-run noise figure.
  * MAJOR-2: "a saving below the distance to the next vblank step does not change `dt`" (item 2, `design122.md` §4, §1.3
    above, the scorer's PINCHED text) is refuted by `sky122`: on a scene with 91.2 % of frames at two vblanks a 2-ms dose
    moved MEAN `dt` by 1.80 ms (s 0.90; one-vblank share 11.15 → 2.47 %, three-vblank 0.93 → 3.07 %, which reproduces
    Δ). The design (`burn.md` §2.4) and the review (RC5) said so before the runs. Verdicts unchanged; the invisibility of
    past small wins is a noise limit (2SE ≈ 130–190 µs at ~42 pairs), and the session-123 frame-skip rationale cannot
    cite the staircase. The correction is a new ROADMAP item (HPP-9).
  * MAJOR-3: the seal loosened or dropped guards of the accepted design without a ROADMAP line — dose [0.97N; 1.03N+20]
    → ±5 %, `burn_late` ≤ 1 % → printed, coverage ≥ 0.95 in both arms → B > 0, the DRS guard (`rt_kpx/rt_att` within
    2 %) and `KYTY_GPU_WALL=1` dropped. On the runs the strict dose/late/GuestGpu-coverage guards pass; placebo coverage
    0.899/0.916; `dnn122` pooled DRS +2.33 % but paired +54 ± 57.5 (n.s.). Without `KYTY_GPU_WALL` the sealed runs
    cannot answer why s < 1.
  * MINOR-1 watchdog heartbeats `HPP-18`/`HPP-21` inside sealed windows; MINOR-2 chain and scorer measure idle
    differently (cost `skyp122`, repeat landed in BDA OLD); MINOR-3 this file's stale header and unmarked sections §5,
    §6, Step 4 (header fixed above); MINOR-4 item 21 mixes UTC with local time; MINOR-5 item 2 (N = 2 000 everywhere)
    vs RC5 (dose above the slack on locked scenes) unresolved — HEADROOM verdicts say only "≥ 2 ms of slack at 60 Hz".
* **Not proven:** GuestGpu critical on the reference (item 2's frame-skip condition is literally NOT met); record thread,
  M1 workers, main guest thread; any saving (the map is a derivative in added work at one dose; RC6); why s < 1 — an
  auditor's report-only observation: per pair Δ(`dt` − `cpu_gpu`) −22 ± 55 (`sky122`), −41 ± 31 (`ght122`), while
  `cpu_gpu` grew by only 0.91 / 0.96 of the dose (≈ 165 / 75 µs of GuestGpu's own work vanished under the dose,
  consistent with absorbed spin-waits; whose — [U]); a NEW-regime placebo; the picture of the sealed runs. 60 FPS is not
  promised; the three HEADROOM scenes ran at 0.9994–0.9998 game speed in their windows (pinned) — a measurement of those
  windows, not a claim about the game.
* **Debts** (to be parked at the close): code 4; code 7 off the main thread; codes 2/3/5/6 unsealed; NEW placebo;
  saving-side linearity; GuestGpu idle/spin under `KYTY_GPU_WALL=1`; the staircase correction; one idle criterion and the
  watchdog vs item 6; the missing `csky122` video; double/zero dose per flip on HEADROOM scenes.
'''
P.write_bytes(s.encode('utf-8'))
print('ok', len(s))
