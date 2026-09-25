# Audit 118: independent recount of the spk118 seal and the arithmetic in ROADMAP 118 item 5

Auditor: adversarial recount. I did not run the game or the emulator, did not build anything and did not edit any
existing file. I wrote my own parser, `C:/kyty/s118/audit118/recount118.py`, which does not import or copy `spk118.py`.
Its output is in `recount118.json` and `recount118.out.txt` next to it. I read `spk118.py` only for its docstring and
its constants (START 1800, PERIOD 90, KEEP 10..88, ABBA 0110, CMP_MIN 90 %, SAFE_MAX 10 %, K3 bar 250 ‰, K4 bar 300 ‰,
K4_MIN 50 %). The log was parsed in binary mode: 1 258 106 lines.

## 0. Seals: CONFIRMED

All 12 files listed in `SEALS118.txt` still hash to their sealed sha256, including `/c/kyty/KytyPS5/docs/session-116/
mutlib_v41/mutlib.py` (`db82ef4b…`). The post-seal tally `mut_spk118.out.txt` also matches (`6df4798e…`), and its text reads
"125 of 125 killed, controls 3 of 3 survived". The sealed pre-registration's mtime is 23:03:45, the seal is at 23:04 and
the launch at 23:05:52, and `spk118.json` records the pre-registration's sha256 as `fe65225a…`, the same as the seal.

## 1. Log integrity: CONFIRMED

| check | my count |
|---|---|
| `FrameTrace` / `-draw` / `-x` lines | 9 148 each, n = 2..9149, **0 duplicate n, 0 gaps** |
| `GateArm:` | 82 lines, blocks 0..81 consecutive, arms=2, period=90, abba=1, frame = 1800+90b, arm = ABBA[b%4], two texts exactly P/M |
| `Gate:` | 248 lines, all at a block start with the value of that block's arm (246 = 41 flips × 6 names, plus 2 at block 0) |
| arm/blk labels | 0 mismatches between the main line's `arm=`/`blk=` and the block of n, across all n > 1800 |
| complete blocks | **P 41, M 40**. Block 81 (M) is incomplete because the run ended at n=9149, so it is excluded. No other frame is excluded. |
| kept frames | P 3 239 = 41×79, M 3 160 = 40×79 |
| `Spine: mode=` | 1 line: `mode=2 snap=4096 ctx=2672 ucfg=148 sh=1208` |
| failure markers / diagnostics | 0 in the log and 0 in `stdout_spk118.txt` (GpuHangAbort, GpuWaitSlow, GpuMarkerHung, ErrorDeviceLost, Error/Fatal/terminate/abort, `AsyncPipelines: skipped draw`, `SpineMismatch`, `SpineMisalign`, `SpineCarry`, `SpineAbort`, `SpineUncertain`, all searched anywhere in a line) |
| arming | M arm: `spine_n` 0, `sc_frames` 0. P arm: `da_t_n` 0. `spine_el/(draws+dispatches)` = 1.00001 |
| BDA regime | means per kept block run from 46 to 143 in both arms, so there is no OLD block (≈1 066). M-arm mean 57.6 means NEW. |

## 2. Verdict numbers: all CONFIRMED

| claim (item 5 / scorer) | recount |
|---|---|
| K5: 0 `spine_bad`/`spine_misal`/`cram_write`, 0 lines | raw sums over all 7 349 x-lines with n > 1800 are 0 / 0 / 0; 0 lines |
| `spine_cmp` 5 308.8 of 5 308.9 per frame | 5 308.81 / 5 308.86 (P kept). Over all rows after 1800, `spine_cmp` = `spine_el` = 19 586 580 exactly. The 165 missing in the kept window is a row-latching skew, not missed compares. |
| C: `carry_cmp` 8 of 8, `carry_skip` 0 %, 0 `carry_bad` | 7.9975 / 7.9975 per frame; `carry_cmp` 25 904 = plans 25 904; `carry_skip` 0 in the kept frames. Over all rows it is 84, all at block positions 0 (71) and 1 (13), which is the first plan after each M block, outside the window. `carry_bad` 0. |
| safe plan 0/0 on 25 904 plans | `spine_unc` + `spine_abort` = 0 (also 0 over all 29 507 plans after 1800) |
| K3 median 0.162 ⇒ W up to 8 | 0.16215 over 3 239 frames (min 0.134, max 0.198) |
| K4 W=2 PASS, median 47, p90 48, 0.0 % above | median 47, p90 48 (nearest rank), max 102, above 300: 0.0 % of 3 229 qualifying frames (99.7 % of kept) |
| K4 W=4 FAIL, median 325, p90 325, 75.1 % above | 325 / 325; 2 259 of 3 008 = 75.10 % (92.9 % of kept qualify) |
| block medians W=4: 325 in 33, 90 in 8 (23–28, 59–64) | 325 in 33 P blocks. 90 in P blocks 23, 24, 27, 28, 59, 60, 63, 64. The ranges "23–28, 59–64" also cover M blocks 25, 26, 61, 62; read as a time span this is correct. |
| W=2 block medians 46–48 and 31–32 | 46–48 in 33 blocks and 31–32 in the same 8 blocks |
| `any` medians | W=2 259, W=4 742 |
| P `spine_ns` 959 µs | 958 833.7 ns = 958.8 µs |
| M: `da_t_ver` 1 211, `pfa` 653, `cpy` 462 | 1 211.2 / 653.4 / 462.0 |
| M: `bl_prep` 4 235, `bl_buf` 3 868, `bl_res` 3 213, `bl_img` 1 095 | 4 235.0 / 3 868.1 / 3 213.4 / 1 094.7 |
| M: `mh_bind` 10 969, `mh_prog` 6 662, `mh_emit` 7 426 | 10 968.5 / 6 661.8 / 7 425.9 |
| M: emit com/rt/vtx/rec/pipe 2 376/1 565/1 363/1 226/745 | 2 375.6 / 1 565.4 / 1 363.3 / 1 225.6 / 745.1 µs |
| M `bda_scan` 57.6 | 57.65 (P 69.58) |

The two-mode scene is real: the low-dep blocks carry about 5 210 draws a frame against about 5 000 in the other blocks,
and the neighbouring M blocks (25, 26, 61, 62) show the same draw level. It is a scene phase, not an instrument artefact.

## 3. `sc_frames` ≠ 1 (the "~4.5 %" of pre-registration m7): MINOR, the disclosure names the wrong counter and nothing changes

- After 1800, **every arm-P x-row has `sc_frames` = 1** (3 690 of 3 690). Every arm-M row has 0 because the gate is off
  (3 659). The `sc_frames == 1` filter drops **0** rows, not ~4.5 %.
- The row tear shows up in the **K4 counters** instead. With `sc_frames` = 1, `k4_w2_n` is 0 in 5 rows and 2 in 5 rows;
  `k4_w4_n` is 0 in 132 rows and 2 in 130 rows. The row with 2 immediately follows the row with 0 (5 of 5 at W=2, 127 of
  132 at W=4), and it carries additive sums (for example W=2 `dep` 94 = 47 + 47). One frame's K4 has spilled into the next
  flip row. `sc_ns` tears the same way. `k3_max`/`sc_el` do not tear.
- The scorer's `k4_wW_n == 1` filter removes both rows of each torn pair: 0.31 % of kept frames at W=2 and 7.13 % at W=4.
  The loss is equal across modes (7.0 % in high-dep blocks, 7.6 % in low-dep blocks), so m7's "equal in both modes" holds.
  Even if every dropped W=4 row had been 90 ‰, the share at 325 would be 2 259 / 3 239 = 69.7 % > 50 %, so the median
  stays 325 and the verdict cannot flip.

## 4. Arithmetic of item 5

The s104 source numbers are **CONFIRMED** against `C:/kyty/s104/runs104/a104_score_b.stdout.txt`/`.json`:
- `cpu_net` = 30 976.47
- `S_now` = 20 072.6
- `S_ctx` = 17 690.15
- T4 = 2 532.49 (t 32.53)
- spine = 1 084.83
- G = 5 683.10 and G^ = 7 629.0

ROADMAP lines 639–641 cite exactly these values.

The derivation is **CONFIRMED**. The s104 rule (ROADMAP:617–618) is G = `cpu_net` − [`S_ctx` + 0.30·(`cpu_net` − `S_ctx`)]
− spine − T4 = 0.7·X − spine − T4, where X = `cpu_net` − `S_ctx`.
- X = 30 976.47 − 17 690.15 = **13 286.3** (from G: (5 683.10 + 1 084.83 + 2 532.49) / 0.7 = 13 286.3).
- G₂ = 0.5·X − spine − T₂ = 6 643.16 − 1 084.83 − T₂ = **5 558.3 − T₂**.
- T₂ ∈ [0; 2 532.5] gives **G₂ ∈ [3 025.8; 5 558.3]**, which rounds to [3 026; 5 558].
- The margin over 3 000 is 25.8 µs ("26 µs"). The s119 rule as written is algebraically the same formula with 0.5.

On "f = max(f_max, 1/W) = 0.5 because the largest K3 run 0.16 < 0.5": this is **internally consistent with the
DESIGN_82 §1 model**. There f_max is the share of the largest indivisible unit; s104's 0.30 was the same formula at DCB
granularity, max(0.30, 0.25). K3's median here is 0.162 and its maximum over all 3 239 frames is 0.198, both < 0.5. It
also matches the sealed wording, "best case recomputed with f = 0.5". See finding M1 for what the same run says about that
best case.

## 5. Findings

**M1: MAJOR. The s119 kill rule hard-codes f = 0.5, while this run measures the actual W=2 cut at 0.555.**

The census's own `k4_w2_fmax` (the largest segment's share of elements at the best pass-start cut) has a median of
**555 ‰**. Its p10–p90 is 543–564 over 3 229 frames, and it is the same in both scene modes (553 / 563). For comparison,
`k4_w4_fmax` has a median of 300 ‰, which is s104's F = 0.30.

The model's max(f_max, 1/W) ignores that segments must be contiguous in command order, so 0.5 is an unreachable ideal in
this scene, not an estimate. With the measured f = 0.555:
- G₂ = 0.445·X − spine − T₂ = **4 827.6 − T₂**.
- G₂ ∈ **[2 295; 4 828]**, so the conservative end is **705 µs below** the 3 000 bar.
- The T₂ at which G₂ = 3 000 moves from **2 558 to 1 828 µs**.

That band is exactly where T₂ is expected to fall (T4 = 2 532; s64 says one reader taxes about as much as four). So the
constant flips the s119 outcome for any T₂ in [1 828; 2 558]. The difference is 0.055·X ≈ 731 µs, 28 times the margin
item 5 quotes.

Caveats:
- fmax is a share of elements, not of time, and the time-weighted share is unmeasured in either direction.
- Item 5 itself obeys the seal; the defect is in the rule written for s119.

Fix before s119: write the rule with f = the measured `k4_w2_fmax`, or a time-weighted equivalent, or require
G₂ ≥ 3 000 under both 0.5 and 0.555.

**m1: MINOR. "Conservatively T₂ = T4" is not a bound in this scene.**

HANDOFF (s64, `sky64a`, Sky Garden) records K=1 **+6.3 %** against K=4 +6.5 / +4.2 / +5.3 %. In Sky Garden one reader
taxes as much as or more than four (ratio ≈ 1.18); only the desert shows K=1 < K=4 (+4.1…4.6 against +7.5…8.2).

With T₂ = 1.18·T4 ≈ 2 992, G₂(f = 0.5) = 2 567 < 3 000. So [3 026; 5 558] is not an interval with a conservative lower
end; T₂ = T4 is a central guess.

Item 5 already calls the 26 µs margin "not a verdict" and orders the T₂ measurement for s119, so no decision flips now.

**m2: MINOR. Wrong build named for the s104 terms.**

Item 5 says "`mut104b`/`sh104`, build `61ae7347…`". Both run records and the a104 scorer show **`16ef56b6…`**, run with
**`dawalk=0`** pinned (`mut104b.json`/`sh104.json` gates). `61ae7347…` is the later s104 build with `dawalk=1` baked in.

The numbers are unaffected. However, the transfer-error argument understates the gap: the terms predate `dawalk=1`,
`dabatch=8`, `cspfree=1` and `daslot=1`, and the "spine" term (`da_walk_us − da_queue_us`) was measured with the walk in
the other configuration.

**m3: MINOR. The spine term in the s119 rule ignores this run's direct spine measurement.**

The s119 rule re-measures the spine as the s104 proxy (`da_walk_us − da_queue_us`), while spk118 measured the spine plan
directly at 959 µs on its own timer. Audit 117 treats that timer as a lower bound, undercounting by about 0.55 ms. If the
real spine is about 1.5 ms instead of 1 085, G₂ drops by about 0.42 ms, to 2 602 at T₂ = T4.

M1, m1 and m3 all push the conservative end of G₂ down. None of them pushes it up.

**m4: MINOR. Decision (2)'s candidate list omits `bl_img` (`RebindImages`, 1 094.7 µs ≥ 1 ms).**

`frameStats.h:1051` shows `bl_img` is a separate function from `bl_res` (the image loop inside `PrepareBindings`), so it
is not nested. It meets the item's own "≥ 1 ms" criterion. Separately, `mh_prog` 6 662 − `da_take` 3 039 ≈ 3.6 ms of
`RefreshShaders` stays un-itemised.

**m5: MINOR. The `sc_frames` disclosure (m7) does not describe this run.** See §3; there is no effect on any verdict.

**CONFIRMED**, no defect found:
- admission facts
- block counts and arm labels
- K5, C and safe plan
- K3
- K4 W=2 and W=4 medians, p90s, shares and block medians
- all arm-M levels, `spine_ns`, `bda_scan`/regime
- the `mutlib` tally
- X, G₂ = 5 558 − T₂, [3 026; 5 558], the 26 µs margin
- ADMITTED ⇒ W2_CEILING under the sealed table (K5 PASS, C PASS, K4 W=2 PASS, W=4 FAIL)

## Verdict

The recount confirms every number and the seal's W2_CEILING. The arithmetic in item 5 is right for the formula it uses.
One MAJOR finding: the s119 G₂ kill rule hard-codes f = 0.5, but this run measures the W=2 cut at 0.555. That moves the
T₂ kill threshold from 2 558 to 1 828 µs, inside the band where T₂ is expected. Four MINOR findings: "T₂ = T4" is not
conservative in Sky Garden, the s104 build is mislabelled (`16ef56b6` with `dawalk=0`, not `61ae7347`), the spine term
ignores the direct 959 µs measurement, and `bl_img` is missing from the candidate list.
