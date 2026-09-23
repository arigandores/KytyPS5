# Session 103 — the BVH loop cap: 0 entry hangs in 67 but its series is NOT ACCEPTED (A3); M5′ CLOSES G on an upper bound; the presence class is fixed in the translator

**Single source of truth for session 103.** Mirrored into git as `docs/local-session-103.md`.
Harness root `C:/kyty/s103`. Everything below is measured unless marked otherwise.

> **This report was written after a four-lens adversarial audit** (§8; sealed `pred/04_audit_addendum.md`,
> 4 345 B, `cdc9bab4…`). Recount NOT REFUTED; code REFUTED narrowly on one descriptive claim (withdrawn:
> "trips always cover whole dispatches"); fidelity NOT REFUTED on the CLOSE but REFUTED on its size
> (**X′ is an upper bound**); protocol NOT REFUTED with one MAJOR disclosure (**the M5′ offline builds ran
> during the sealed series**). A fifth lens on the texts (claims, sealed `pred/05`) REFUTED the stated basis
> of the next route (vblank numbers and a causal claim); corrected before publication (§8).

**The three numbers route E opens with (`ROADMAP.md` §5 item 5):** the 60 FPS budget is ≤ ~3.0 µs a
draw on the median frame and ≤ ~2.3 µs on a p99 frame; the carried reference CPU path is 6.4 µs a
draw, 31.6 ms a frame, GPU busy 12.8 ms (this session's series, new binary, scene window of all 67
entries, 37 119 frames: `dt_us` median 33.5 ms, `cpu_gpu_us` 32.9 ms, `gpu_busy_us` 12.6 ms; frames on
2 / 3 / 1 vblanks = 79.3 / 20.1 / 0.5 %); **M1, M2, M3 (GAP), M5, M5′ done, M4 withdrawn.**
**No frame-rate gain, no speedup. 60 FPS is not promised.**

---

## 1. Result

1. **`KYTY_BVH_LOOP_CAP` (default ON: 65 536 loop-header steps per invocation, one budget, set
   `{380bb9d636390bae}`)** — the uncapped BVH traversal that the GPU named in entry hangs. **Series
   of 67 counted entries (sealed `pred/01`): 0 hangs, 67/67 reached the scene and survived the hold;
   trips in 7 entries** (05, 22, 30, 32, 36, 42, 49; 2 875 168 invocations over a few consecutive
   readbacks, all in frames 188–197 — the level-entry transition; readback sizes vary (uniform only in
   entries 05 and 42), so no whole-dispatch statement is made), worst frame 0.347 s. **Verdict NOT ACCEPTED on A3 alone**: in
   `ent103_42`, right after three readbacks of 129 024 trips each, three more readbacks of 129 024
   invocations each counted normal returns that had spent more than 1/16 of the budget.
   Outside trip episodes `bl_near` = 0 in all 67 entries (a post-hoc slicing, not a sealed item).
   Historical entry-hang rate 6.67 % ⇒ ≈ 4.5 hangs expected; P(0 | 6.67 %) = 0.0098 — but `pred/01` §4
   licenses a rate statement only for an ACCEPTED series, so none is claimed. **Disclosed (audit, MAJOR):
   the M5′ offline builds (tests exe, spirv-val, pipestat driver compiles, nvdisasm) ran during up to 53
   of the 67 counted entries — six of the seven trip entries (05 in the S4 probe; 30, 32, 36, 42, 49 in
   `m5p_recompile`) — and the video pass, against the seal's "GPU otherwise idle".**
2. **Decision (recorded in ROADMAP before the next action): the cap stays ON by default as a
   correctness fix that its seal did NOT accept** — without it ~1 in 15 entries loses the device;
   with it 0 of 67, and its failure mode (a traversal that writes no result for a few frames inside
   an episode) is far milder. Not claimed: that the 16× margin holds, or what the hang mechanism is.
3. **M5′ (sealed `pred/02` + `pred/03`): G CLOSED by the recorded rule — on an UPPER bound.** X′ =
   S[V2′]/S[A] = **1.2934** (90 % CI of X′ − 1: [0.2910, 0.2946], bench noise only) over eight items
   (S1, S8 fail V-e for V2′), every control V-a…V-g PASS; L = V1/A = 1.0201 ([0.0182, 0.0230], all ten);
   A/B = 1.0027. The rule (ROADMAP §0.1, recorded before any work): CI_lo(X′ − 1) > 0.06 ⇒ G CLOSED.
   The audit showed V2′ still carries removable machinery (the page-crossing slow path, the per-group
   dword fallback, the run-time alignment test on PER-LANE addresses, repeated page lookups); its
   estimate for G without them is **1.09–1.17 [I]**, still above 1.06 — the CLOSE rests on that
   inference, and it covers G with a page-table BDA path only.
4. **The presence class is closed in the translator:** the 15 deferred sites (12 variables) under
   `src/graphics/shader/**` now read the value (`Common::EnvFlagOn`); `=0` turns them off.
5. **Video pass (ROADMAP §6 debt) PASS**: 3 842 frames, 0 one-frame glitches, decodes cleanly —
   in a run with no trip (steady state only).

## 2. The loop cap

### 2.1 Code (commit `14db6c7`)

* Emitter (`spirvEmitterProgram.cpp`): `LoopGuards` — for a program in the cap set, every loop header
  spends from ONE Function u32 per invocation (`bvh_loop_budget`); the guard's abort block counts a
  trip (`EmitLoopCapTrip`: atomic add to the fault-buffer tail word 2^21, atomic max of the spent
  budget, a per-slot count) and leaves through `EmitReturnTail` (pixel kill + BDA fault flush +
  return). A normal return of a capped program counts `bl_near` when it spent more than cap/16
  (`EmitLoopCapNear`). `KYTY_LOOP_LIMIT` keeps its old per-loop bare-return behaviour.
* Config: `KYTY_BVH_LOOP_CAP` (default 65 536, `0` off), `KYTY_BVH_LOOP_CAP_SET` (hex list, ≤ 8);
  any override adds `:bvhcap<N>-<hashes>` to the translation-cache signature and its own cache
  directory (`variant_bvhcap…`).
* Host: the fault buffer grows by 16 words; the tail is zeroed at the first buffer registration
  (with the null page), copied next to the fault list in `ProcessFaultBuffer` and diffed as
  monotonic counters in the deferred operation; `FrameTrace-x` counters `bl_trip`, `bl_near`; log
  lines `BvhLoopCap: cap=… token='…'` (always, at start) and `BvhLoopCapTrip:` (≤ 64 lines).

### 2.2 Offline evidence before any run

* Default-off identity: the new `shader_cfg_tests.exe` recompiled every recompilable cached module of
  the session-102 signature (553 files; 12 had no GCN dump) (snapshot `C:/kyty/cache_snap/PPSA21564_2db9065a`, taken before any run):
  **106 CS and 173 PS byte-identical**, the only difference the three permutations of `380bb9d6`
  (VS are not recompilable offline — 260 modules not covered; 1 CS `900aba8d` has an empty GCN dump).
  A first sweep found all 13 BVH programs different: a changed id-allocation order in the null-page
  lookup, fixed before the build that ran (`identity_sweep.py`; `idsweep_default.json` holds the
  corrected sweep — the first sweep's output was overwritten, so that statement has no artefact).
* `380bb9d6` capped: spirv-val passes on all three permutations; registers 128 → 128, local memory
  80 → 64 B, binary +4 %; with `KYTY_BVH_LOOP_CAP=0` byte-identical to the stored modules.

### 2.3 The series

`ent103_warm` (cold: 53 s, armed, 0 trips, max frame 5.0 s — shader compilation), then
`ent103_01…67`, each `enter_scene.py --attempts 1 --hold 20`, binary
`16ef56b69c4a99fa6ad613d0dbf57d7f59e0d5443bd6509c55442d83c4780352`, ≈ 45 s an entry, 0 technical
failures, no replacement. Per trip entry (trips / near / worst frame):

| entry | trips | near | worst dt |
|---|---:|---:|---:|
| 05 | 786 432 (6 readbacks × 131 072) | 0 | 0.347 s |
| 22 | 746 112 | 0 | 0.299 s |
| 30 | 149 536 | 0 | 0.167 s |
| 32 | 292 864 (5 readbacks, 58 368…59 392) | 0 | 0.267 s |
| 36 | 128 320 | 0 | 0.184 s |
| 42 | 387 072 (3 readbacks × 129 024) | **387 072 (3 readbacks × 129 024)** | 0.333 s |
| 49 | 384 832 | 0 | 0.332 s |

A1 armed PASS, A2 no hang PASS, **A3 margin FAIL**, A4 7 ≤ 15 PASS, A5 0.347 s < 30 s PASS.
Predictions: Q1 (ACCEPTED) MISS, Q2 (0…10 trip entries) HIT, Q3 (no `bl_near`) MISS.

**Withdrawn by the audit:** "every trip episode spends whole dispatches" — entries 22, 30, 32, 36 and 49
have readbacks of unequal size or not multiples of a dispatch (dispatch size is not logged) (`ent103_30`: 149 536 = 2 336.5 groups of 64, so in
some groups one wave tripped and the other finished), and with it the inference "invalid
acceleration-structure data during level load". What stands: all trips fall in frames 188–197 (the
level-entry transition, before the scene is stable at 285–333) and the episodes end within a few
readbacks. Whether the abort's BDA fault flush (which the uncapped shader never reached) is what ends
them is **not shown**; the fault-bit store it goes through is non-atomic (pre-existing).

## 3. M5′

### 3.1 The switch `KYTY_BDA_LEAN` (measurement only, default off, `:bdalean` token + directory)

No fault-buffer store in pixel shaders; the null-page base read once per invocation; the page
index checked against the constant `CACHING_NUMPAGES`; PSB data through read-only views
(`NonWritable`, `Restrict` when the program writes no memory) and the page table `NonWritable` +
`Restrict`; in a scalar load group a run-time `(origin mod 16) == 0` branch picks `uvec4` loads for
16-byte windows with ≥ 2 members. The run-time branch is the session-103 amendment recorded in
ROADMAP (item 3) before the code: a copied V#'s alignment class describes the host copy, not the
guest base, so the literal rule would have priced G without vector loads.

### 3.2 Modules (`m5p/recompile.json`, `regs.json`)

48 modules, all built; A reproduces the capture's modules on all 16 permutations; V-f 0 of 36
fail. V2′ loads are `LDG.E.CONSTANT` / `.64.CONSTANT` / `.128.CONSTANT` (V2 had `LDG.E.STRONG.SM`).
Registers A/V1/V2′: S1 255/255/255, S2 72(70)/72/86, S3 64/78/102, S4 96/96/128 (local 80/112/144 B),
S5 80/86/128, S6 70/70/85, S7 41/41/62, S8 96–107/96–121/128 (V2′ 144 B local), S9/S10 16/16/20.
`pred/02` §1's "STL 30 → 0" on S4 was a misread truncated listing; corrected in `pred/03`
(30 → 9 in the window, 98 → 48 full code).

### 3.3 The bench (`m5p/real/`)

`find` 156 s, `sd_verify` 0 mismatches, all 10 items present and included, 0 excluded modules;
`equal` 109 s: V2′ fails S1 (4 153 398 B > 2E = 31 026) and S8 (729 B on a repeatable item) — the
same two items V2 failed in session 102 — 22.1 % of A time; `bench` 681 s, 20 rounds of the
Williams design, no extension needed.

| item | A µs | B/A | V1/A | V2′/A | (s102 V2/A) |
|---|---:|---:|---:|---:|---:|
| S1 CS | 1 264.9 | 1.000 | 1.001 | 1.499 (V-e FAIL) | 1.497 |
| S2 PS | 898.1 | 0.988 | 0.991 | 1.003 | 1.020 |
| S3 PS | 853.0 | 1.000 | 1.094 | 1.245 | 2.207 |
| S4 PS | 795.5 | 1.001 | 1.056 | 1.347 | 1.349 |
| S5 PS | 880.2 | 1.004 | 1.092 | 1.596 | 1.702 |
| S6 CS | 700.7 | 0.998 | 0.999 | 1.305 | 1.313 |
| S7 CS | 724.5 | 0.996 | 0.997 | **2.081** | 1.790 |
| S8 PS | 751.0 | 1.009 | 0.996 | 1.094 (V-e FAIL) | 1.113 |
| S9 PS | 1 649.4 | 1.000 | 1.000 | 1.026 | 1.087 |
| S10 PS | 604.0 | 1.001 | 1.005 | 1.047 | 1.146 |

Predictions: P1′ (X′ − 1 in [0, 0.12]) **MISS** (0.293), P2′ HIT (8 pass), P3′ HIT (L − 1 = 0.020),
P4′ HIT (1.293 < 1.420 on the same eight).

## 4. Env-flag sites (the rest of the session-102 class)

15 sites / 12 variables converted: `KYTY_VTX_TRACE` ×2, `KYTY_AV_TRACE` ×2 (recompiler),
`KYTY_KNOWN_VALUES_TRACE`, `KYTY_SRT_PLAN_STATS`, `KYTY_SRT_VERIFY`, `KYTY_SRT_NATIVE_STATS` ×2,
`KYTY_SRT_NATIVE_AUDIT`, `KYTY_BVH_STUB`, `KYTY_CFG_TRACE`, `KYTY_SAMPLE_LOD0`,
`KYTY_VEC_CONST_TRACE`, `KYTY_SCALAR_GROUP_TRACE`. Not converted (not presence tests): numeric,
path and first-character (`value[0] != '0'`) readers — a separate class where `false`/`off` read ON.
Test-only presence checks in `tests/shaderCfgTests.cpp` are unchanged.

## 5. Source, builds, provenance

* Commits: `27b492d` (ROADMAP pre-record), `9a49f88` (series seal + scorer), `14db6c7` (source),
  `4ed2219` (M5′ seal), `a3ff539` (series verdict + the keep-ON decision), `9b8212f` (addendum 03),
  and the session commit **`4a87d30`** (report, ROADMAP, plan, audit addenda 04–05). **No push.**
* Emulator `16ef56b6…` (the build that ran the warm-up, all 67 entries and the video pass); an
  earlier build `6b680ba2…` (before the id-order fix) was never run. Tests exe `e7a15418…` (arms of
  M5′). Translator hash `699c1e4b7db359067b461e029b913c4b6e78dc90` (was `2db9065a`): the translation
  cache went cold once (warm-up), and the startup seed `_ShaderSeeds/PPSA21564` is now incompatible
  and ignored (logged `ShaderSeed: incompatible … ignored`) — a debt.
* `check_gate_order.py` clean (no gate or knob added).

## 6. Harness

`C:/kyty/s103`, ported by a fresh `C:/kyty/s102/s103_port.py`: `PRECONDITIONS PASS: 5 root
constructs; 30 sealed texts (29 land in prev102/pred, 1 stays in carried prev100/pred); 27 live
paths (16 files) + 5 expression paths; gates 1092 B / 99 names; gates.cpp 135 entries (111 gates +
24 knobs); ABSENT 36` → `PORT DIAGNOSTIC: clean; carried=3369 ledger=51 skipped=19`. New:
`identity_sweep.py`, `bvh103.py`, `series103.py`, the M5′ harness (`m5p_103.py` + `test_m5p_103.py`
167 checks, `m5p_recompile.py`, `m5p_plan.py`, `rd_m5p_equal.py`, `rd_m5p_bench.py`, `m5p_run.py`,
`M5P_RUNBOOK.md`, `m5p_go.sh`), patch scripts `patch_s103_*.py`, the cache snapshot
`C:/kyty/cache_snap/PPSA21564_2db9065a` (+ manifest).

## 7. Runs

| tag | what | outcome |
|---|---|---|
| `ent103_warm` | cold warm-up | ok, not counted |
| `ent103_01…67` | sealed series | 67 ok, 0 hangs, trips in 7 — NOT ACCEPTED (A3) |
| `vid103` | video pass, 120 s hold | PASS, 3 842 frames, 0 glitches, no trip |
| M5′ stand | find/plan/equal/bench on the s102 capture | VALID, G CLOSED on an upper bound |

## 8. Adversarial audit (sealed `pred/04_audit_addendum.md`)

Four lenses, each told to refute, reports in `C:/kyty/s103/audit103/`:
* **Recount — NOT REFUTED.** Own code reproduced every number of §2–§3 to 4 decimals (a numpy
  bootstrap moves the CI by ≤ 0.001), the item↔event
  map (3 355 events), the Williams order of all 20 rounds, and found no FrameTrace-x line lost around
  the trips. Observed: V2′ has more zero-duration events than A (the excess is not shifted between
  events: +2 784 µs on item events vs +2 822 µs whole capture); round 0's ratio 1.2165 is an outlier
  (the median is unaffected); on S1 V2′ flips one byte of an 8 MiB buffer bound in both arms (probably
  the fault buffer — a real read fault, inferred).
* **Code — REFUTED narrowly** on "trips always whole dispatches" (withdrawn above); no code defect
  invalidates a verdict. Minor: the tail copy is not ordered against later atomics (per-readback
  attribution can split, totals exact); `bl_*` read 0 without FrameTrace or with `fslean=1`; 32-bit
  wrap stops the counters; a set entry without a fault binding would trip uncounted; `strtoul`
  parsing (`=true` turns the cap off, `=1` aborts at the first header); `KYTY_LOOP_LIMIT` is replaced
  by the cap for capped programs.
* **Fidelity — NOT REFUTED on the CLOSE, REFUTED on its size** (§1 item 3). Removing the slow path and
  the dword fallback in the SPIR-V: S4/S5/S8 128 → 96 registers, PS binaries −29…−36 %. Per-lane
  alignment branch confirmed in S7's SASS (`@P0 LDG.E.128` / `@!P0` three `LDG.E` for a 12-byte
  stride). Lookups repeated per block (S4 63 lookups for 16 V#s). The rule's explicit items are met
  (null base read once, no `STRONG`, no PS `STG`, `.CONSTANT` loads).
* **Protocol — NOT REFUTED**, one MAJOR (the builds during the series, §1 item 1) and minors: the
  cap/env code was written (not only drafted) before the ROADMAP record but first built after it; the
  M5′ amendment changed "constant null base" to "once per invocation" and silently dropped "no reloads
  after stores" (both bias toward CLOSE); the keep-ON decision is not a breach but its rate sentence
  over-reached (withdrawn); the M5′ scorer checks `pred/02` and its parents, not `pred/03`; the pre-fix
  identity sweep's output was overwritten (the "13 programs differed" statement has no artefact).
* **Claims (fifth lens, on the texts) — REFUTED on the basis of the next route, corrected before
  publication:** the vblank distribution first written (86/13/1 %, from the last 300 frames of five
  logs) does not reproduce over the scene window of all 67 entries (79.3/20.1/0.5 %); and "the vblank
  grid quantises the CPU frame" is NOT shown by the data — `cpu_gpu_us/dt_us` is 0.981 on two-vblank and
  0.980 on three-vblank frames (48.7 ms of GuestGpu CPU on 50 ms frames), so no idle GuestGpu time waits
  on the grid in this counter; route V is a hypothesis for session 104's steps (a)/(b), not a finding.
  Also corrected: "G CLOSED" is qualified everywhere; the goal is not changed (the executor may not
  change it) — 60 FPS has no route with a live estimate, and the work continues on the "maximum FPS"
  half of the goal; the whole-dispatch wording is removed everywhere; §9 counts the seed regression.

## 9. Proved, and not proved

**Observed/measured.** 0 entry hangs in 67 counted entries with the cap (no rate is licensed: the
series is NOT ACCEPTED, and the M5′ builds ran during it); the cap tripped in 7 entries during the
level-entry transition and every entry survived. V2′ — the BDA path with the recorded G properties
plus removable machinery — costs +29.3 % on eight top Sky Garden shaders: an upper bound; G CLOSED by
the recorded rule, resting on the inference (1.09–1.17 [I]) that G without the artefacts still exceeds
+6 %. **ROADMAP §6:** the session's real-path changes — the loop cap (its sealed series NOT ACCEPTED)
and the 15-site env conversion (identical for unset and truthy values by construction, no A/B) — include
no accepted change. **Regression booked:** the translator change made the startup shader seed
incompatible for every user (`ShaderSeed: incompatible … ignored`) until it is rebuilt.
**Not proved.** That the cap is accepted (A3 failed); what the hang mechanism is;
anything about the other 12 BVH programs (uncapped); that a G with a different address translation
(not the 16 KiB page table) would cost the same; VS behaviour of the translator change (not covered
offline, only by the runs). **No frame-rate gain, no speedup, no 60 FPS.**
