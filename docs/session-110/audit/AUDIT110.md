# AUDIT110 — adversarial audit of session 110 (RECOUNT · PROTOCOL · CODE)

Own parsers only (`audit110/parse_stall.py`, `parse_abba.py`, `abba_stats.py`, `windows.py`, `hetero.py`, `robust.py`,
`estimators.py`, `levels.py`, `hitches.py`, `clocks.py`, `protocol.py`, `mtime_scan.py`, `transcript_scan.py`,
`newmut.py`; outputs `*.txt`/`*.json` beside them). No session scorer imported. Nothing built, run or edited outside
`audit110/` (fixture re-runs wrote only under `C:/kyty/s106_stage/fx_*`).

## Verdicts
- **RECOUNT — CONFIRMED, with one MAJOR on the quoted size.** Every claimed number reproduces exactly. The ship
  decision is robust; **the −418.7 µs size is not** (MAJOR-1): the best estimate is ≈ −200 µs.
- **PROTOCOL — HOLDS.** Records precede actions (session transcript), seals precede runs, all 21 SEALS110 hashes and
  all 18 prereg hashes match, pin (env + exactly one `GpuClockPin: mode 1`) on all 19 runs, no foreign file write under `C:/kyty` (175 845 files scanned) and no tool call
  but `ScheduleWakeup` (session transcript) inside any sealed window. The
  stl110 → stl110b re-run is a legitimate correction, not rule-shopping. Defects: MAJOR-2 (the D/M rule mostly measures
  a startup lottery), MINOR-4…6.
- **CODE — NOT REFUTED.** The stall instrument is inert in the shipped configuration (0 stalls in 1 800 s of
  shp110/vsh110/vid110) and cannot explain shp110 vs frm109; the `cspfree` debts are perf-only (MINOR-7).

## Recount
| claim | recount (own parser) |
|---|---|
| stl110 NOT_ADMITTED: CsStall lines at startup before the first FT-x row | **Confirmed.** In all 8 entries: lines after the first row = Σ(`cs_sync_new`+`cs_sync_wait`) exactly, their Σ µs = Σ `cs_sync_*_us` exactly; the surplus (1–2 lines/entry) all precede row n=2. Would have PASSED: D_B 42 427 ≤ 75 501, M_B 12 334 ≤ 24 206; corrected STALL_SYNC holds 8/8 |
| stl110b PASS; D_A 19 569, D_B 10 878, M_A 12 293, M_B 1 619, S_A 15, S_B 16 | identical (bounds 44 461 / 22 293; N_A 20). After the first row only: D_A 4 796, D_B 6 315, M_A 667, M_B 1 619 — still PASS. stl110 after-row: D 4 063 / 5 175, M 1 236 / 1 036 |
| the ~12.3 ms "startup wait" | shader 497 (`0x5c118936…`) at guest frame 3: if the lookahead walk queues its prefetch before GuestGpu reaches the dispatch, the dispatch waits ≈ the walk's duration (waits 12 118–14 206 µs; that walk 12 476–15 092 µs, walk ≥ wait by 0.3–0.9 ms in 7/7); otherwise it compiles synchronously in 0.93–0.99 ms. Arm-independent (memo empty at start): drawn by A 4/8, B 3/8 entries (stl110 3/4 vs 3/4, stl110b 1/4 vs 0/4). **M_A, M_B and most of D are this one event** |
| shp110 Δdt −418.7 (2SE 135.3, t −6.19), Δcpu_net −302.1, da_walk −55.3, gpu_busy +32.2, 96 pairs | identical. Sign-flip p < 5·10⁻⁵, bootstrap95 [−557, −295], paired median −540 (block means of 29 flips are quantised in ≈575 µs steps, so medians of either run are artefacts). Vblank (kept rows): 1-vbl 12.90 → 14.87 %, 3-vbl 0.75 → 0.18 % (−328 and −95 µs) |
| vid110 PASS: 4 004 frames, 0 glitches, hit 265.8/row, bad 0, sync 0 | identical; also `cspf_have` 5 (mode 1, not 2), 0 CsStall lines, one `GpuClockPin: mode 1`, `cspfree` absent from gate text and env |

## Findings
**MAJOR-1 (recount) — the shipped size is an upper-tail draw of the sealed window; quote ≈ −200 µs, not −418.7.**
The sealed estimator (flips 60–88 of each 90-flip block, 32 % of the data) reproduces all six same-harness ABBA runs
(dwk104 −265.9, dab106 −169.3, dab107 +281.0, fam108 −141.8, frm109 −154.1, shp110 −418.7). Against the full block
(0–89) the gap is within ±1.6 SE in five runs and **−185.6 µs, z −3.09 in shp110 only** (`estimators.txt`). Full
block: **shp110 −233.1 (2SE 56.6), frm109 −171.3 (70.3), difference −62 ± 90 (z −1.37); pooled −202.2 ± 45.2**
(192 pairs). Within shp110 the tail window beats the rest of the same blocks by −245 µs (t −2.81; frm109 +26, t 0.38).
Cause: arm-independent ~48 ms (3-vblank) hitch bursts (pooled A 91, B 89) fell in arm-0 tails (tail hitches A 21 vs B 5;
frm109 A 10 vs B 16) and 29-flip sampling noise of the 1-vblank share (full-block gain +1.20 pp in
shp110 vs +1.03 pp in frm109 — the same). Capping 3-vblank flips shrinks the gap to −152 ± 172 between runs. The
builds differ only by `3d8af4c`, which never executed (0 stalls); mechanism counters match to within noise (da_walk
−41.5/−37.0, da_queue +13/+14, sync_up_kb +213/+212, prot_us −69/−71, fault_us +434/+456, gpu_busy +41/+68, draws
flat); GPU SM clock 2 415 vs 2 460 MHz median, same throttle mask 0x400, CPU clocks and background set identical.
**Ship decision is robust:** S1/S2 hold in both runs under every window tried ([0:90], [10:90], [30:90], [45:90],
thirds, capped). Corrections: FACTS title, ROADMAP item 6/7, `gates.cpp` comment and `0776f6a` message should read
"Δ mean dt ≈ −200 µs (pooled full-block frm109+shp110, 2SE 45; sealed window −418.7, an outlier of its estimator)",
≈ +0.65 % game speed at the pin; Δcpu_net ≈ −100 (full −130.5 / −65.0). Future seals: pre-register the full block
(or 10–89) as the primary estimator — 2SE falls ~2×.

**MAJOR-2 (protocol/design) — the D/M guard mostly scored the startup lottery.** Thresholds were fixed blind
(proposal 21:27Z, ROADMAP `9031f17` 00:09 local; first duration datum 00:30:54) and not loosened — fine. But post-load
stall time is ~1.0–1.6 ms per 150-s entry, so D_B ≤ 1.25·D_A + 20 ms lets B's post-load stall time grow ≈ 4–12×
before failing, while the arm-independent 12–14 ms startup event (p ≈ 0.44/entry) makes the rule FAIL **12 % of the
time under the null** (resampling the 16 real entries, 2·10⁵ draws: D 7.9 %, M 9.0 %). stl110b PASSED its M-term because B drew 0/4. The guard's substantive answer still stands on better grounds:
after the first row B adds +2.6 ms over 8 entries (+0.33 ms per 150 s; same sign in both runs: +27 %/+32 %), and in
the shipped configuration (compute precache on) there are **0 CsStall lines in 1 800 s** (shp110 both arms, vsh110,
vid110). Correction: record this in ROADMAP; future duration guards exclude pre-first-row stalls from D/M (they are
load-screen) and use a slack scaled to the post-load baseline.

**Legitimacy of the re-run (asked):** not rule-shopping. stl110 already passed D/M (D_B/D_A 0.96), so re-running could
only add FAIL risk (~12 %, above); the alternative (re-scoring seen data with a changed scorer) would have been the
violation. Rule identical word for word; the defect (counters cannot see pre-first-row stalls) is real and was
disclosed. Blemish (MINOR-4): pred/02 moved L5 from [0.8, 2.5] to [0.6, 2.0] after seeing 0.955 without saying so.

**MINOR-4 (reporting) — pred/02 predictions never scored.** By hand: L1 HIT, L2 HIT (16 > 15, marginal), L3 HIT, L4
HIT, **L5 MISS (0.556 ∉ [0.6, 2.0])**. `stl110b.py` prints no predictions (audit-109 MAJOR-1 repeated for this
lineage); ROADMAP item 5 omits them. shp110's H1–H6 are scored (H3 MISS reported).
**MINOR-5 (protocol) — same-commit records.** Record+code (`1d9dcf0`/`3d8af4c`, same second), record+seal (`016722c`),
record+default (`0776f6a`). The transcript proves order (ROADMAP edits 22:10:02Z < patch 22:10:16Z; 22:55:11Z <
seal 22:59:39Z; 00:25:23.9Z < gates.cpp 00:25:35Z); commits alone do not. `check110.py` (sha `2efd7414`) was written 7 s
before `go110v.sh` launched but its sha was published only after the run; docstring still describes check108
(`cspfam_skip`, `vid108.json`); it checks `pins ≥ 1` of `mode 1` (a stray `mode 2` passes), not `cspf_have ≈ 0`
(mode 2 would pass `default_armed`), not `KYTY_CS_PREFETCH_FREE` in env. None changes the verdict (verified directly).
FACTS.md with "−418.7" was written (00:30:11Z) after this audit was launched and before its result.
**MINOR-6 (fixtures).** `test_stl110b.py` ALL OK, byte-identical to the sealed output. `test_shp110.py` byte-identical
to the sealed output; 152 cases; the only failure is CONSTANTS, which differs exactly in `PRED_SHA`/`PRED_BYTES`
(checked against the source) — so the sealed suite is red by design and cannot flag real constant drift; pin the
sealed values at seal time. New mutants: stl110b 11/12 killed (survivor: `STALL.match`→`search`, harmless — every
CsStall is at line start); shp110 8/8 killed (keep window 0–90, first frame 1800, MIN_PAIRS 6, bar −99,
DROP_MAX 0.5, raw cpu_net, video 300 frames, WALKS_TOL 0.5).

**MINOR-7 (code).** `3d8af4c`: correct identities on real data; the stall wall starts after `m_mutex` is acquired (lock
waits of the dispatch are not a "stall"); the `new` path LOGFs while holding `m_mutex` (rare, ≤ 4 096/process);
pre-first-row stalls are invisible to counters by construction. `0776f6a`: default only, comment cites −418.7. The
session-109 `cspfree` debts after shipping: all perf-only — the dispatch never consumes the prefetch's result, so a
stale hit can only skip a warm-up (then a counted dispatch stall); memory-safe (sources are only `extract`ed into
`retired_sources`, never erased, pointers stay valid). TOCTOU (restamp before unlocked materialize): one-call window on
the rare "cached plan failed to materialize" drop → MINOR; "moved on null" is verify-mode only (mode 2 not shipped) →
cosmetic; raw `thread_local` pointers need one `PipelineCache` per process (true) → latent. Fix the TOCTOU (re-read
the mirror after `MaterializeUnlocked`) the next time the code is touched, with a vfy re-run.
