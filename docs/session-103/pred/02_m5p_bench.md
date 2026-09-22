# Session 103, sealed before any timing: M5′ — the GPU price of the BDA path as design G would build it

**Immutable once written.** A correction goes into a new sealed addendum, never into this file.
The rule is recorded in `docs/ROADMAP.md` §0.1 FIRST: the M5′ rule (commit `89c095e`, "РЕШЕНИЕ
ИСПОЛНИТЕЛЯ ПО G ПОСЛЕ С. 102") and its session-103 amendment (commit `27b492d`, item 3: the run-time
alignment test). This file fixes the protocol; it does not move the threshold or the branches.
Written after the V2′ modules of one item (S4 p0) were compiled and read (registers/SASS are
"reported, never deciding"), and before any EventGPUDuration of any V2′ module exists.

## 0. The rule (ROADMAP §0.1, verbatim in substance)

`X′ = median_r S[V2′,r] / S[A,r]` over the items that pass V-e for V2′.
**CI_lo(X′ − 1) > 0.06 ⇒ G CLOSED. CI_hi(X′ − 1) ≤ 0.06 ⇒ G's GPU side PASSES** (the next decision
becomes a slice prototype of G's CPU side). Overlap ⇒ one extension of 20 rounds, then the point
decides (X′ − 1 > 0.06 ⇒ CLOSED, else PASSES), published as *decided at the point after extension*.
If the items failing V-e for V2′ carry more than 40 % of the valid A-arm time ⇒ **M5′ NOT DECIDED**.

## 1. The arm V2′ (built by the test recompiler, `KYTY_RECOMPILE` path)

`KYTY_RECOMPILE_BDA=1 KYTY_BDA_LEAN=1`: the session-102 V2 rewrite (unchanged test code
`RewriteBuffersToBda`: every read-only non-formatted buffer and constant load through the BDA page
table at base(V#) + offset, V# at run time, run-time stride and `num_records` bounds) emitted by the
session-103 lean emitter (`KYTY_BDA_LEAN`, source commit `14db6c7`):
* no fault-buffer store in pixel shaders (the binding stays in the layout, unused);
* one page-table read per lookup; the null-page base read once per invocation at entry; the index
  check against the constant `CACHING_NUMPAGES` instead of `OpArrayLength`;
* PSB data read through read-only views (`NonWritable`; `Restrict` when the program writes no buffer
  or image memory); the page table decorated `NonWritable` + `Restrict`;
* in a scalar load group, a run-time test `(origin mod 16) == 0` selects `uvec4` loads for every
  16-byte window with two or more members, else the 32-bit loads.
Known before timing (S4 p0 only): V2′ compiles to `LDG.E.CONSTANT` / `LDG.E.64.CONSTANT` /
`LDG.E.128.CONSTANT`, V2 to `LDG.E.STRONG.SM` / `LDG.E.64`; STL 30 → 0 (S4 V2 → V2′). The fits-in-page
branch and its per-dword slow path remain (the M5′ rule does not remove them).

What V2′ still omits of G (each removes cost): SRT pointer chasing through BDA, run-time format
decode (formatted loads stay on descriptors), every VS/mesh stage, and all of G's CPU side.

## 2. Arms, set, capture — inherited

* Arms **B, A, V1, V2′** (`B` = the capture's modules; `A` = `KYTY_RECOMPILE`, no switch; `V1` =
  `KYTY_RECOMPILE_CBANK=0`). V2 and V2s are not benched.
* Shader set S1–S10 of session 102 `pred/01` §2, unchanged, no substitution.
* Capture `_RenderDoc/kyty_1790110985179586_capture.rdc`, sha256
  `92a10b3cad28064e8b16d08dad074758be0627b66ac081dc2fd42f036dcf416d` (accepted under V-a in session 102;
  no new game run). Cache inputs: the snapshot `C:/kyty/cache_snap/PPSA21564_2db9065a` taken before
  any session-103 game run (manifest `manifest_2db9065a.json`), signature prefix `KytySC3:2db9065a`.
* Test recompiler `C:/kyty/build/shader_cfg_tests.exe` sha256
  `e7a154187c09b74ed83c5276de80605eaade06845bcf2e9510bc5b3b605726c2`, built from `14db6c7`.
  Offline, with no switch it reproduced every recompilable cached module of the session-102 cache
  byte for byte (106 CS, 173 PS) except the capped `380bb9d6` (not in the set).

## 3. Validity — session 102 `pred/01` §6 as amended by `pred/02` §1, §2, §5, applied to V1 and V2′

V-a (capture above), V-b (≥ 7 of 10 items present carrying ≥ 60 % of the 4 508 µs weight), V-c
(a captured module belongs to an item when its md5 equals arm A's for one permutation; exclusion
> 40 % of the present items' A time ⇒ INVALID), V-d (`median_r S[A]/S[B]` in [0.97, 1.03]), V-e
(three A replays per item; bit-equal for repeatable items, ≤ 2·E otherwise; a failing item leaves
that variant's sums), V-f (`spirv-val --target-env vulkan1.3 --uniform-buffer-standard-layout` on
every module of every arm), V-g (every fetch returns a value for every event; a crashed bench may be
restarted from scratch once; a completed bench is never re-run). `find` and `equal` are run afresh
on this capture (arm-independent find; equality for V1 and V2′).

## 4. Design and estimator

* Two warm-up fetches with B, discarded. **R = 20** rounds; round r uses sequence `r mod 4` of the
  Williams design for four arms `[B A V1 V2′]`, `[A V2′ B V1]`, `[V1 B V2′ A]`, `[V2′ V1 A B]`
  (five full cycles); extension +20 rounds, same design. The 10-minute fetch rule of `pred/01` §5
  (never below 8 rounds) is unchanged.
* `T[X,i,r]` = Σ EventGPUDuration over item i's events; `S[X,r]` = Σ over valid items. X′ as in §0;
  90 % two-sided percentile bootstrap over rounds, 20 000 resamples, **seed 103**, the same resample
  indices for every statistic.
* Reported always, never deciding: `L = median_r S[V1]/S[A]`, `A/B`, every per-item ratio
  (B/A, V1/A, V2′/A), the V-e table, registers, local memory, SASS counts and LDG variants of every
  module of A, V1, V2′.

## 5. Predictions (published whether hit or miss, never repaired)

* P1′: X′ − 1 in [0.00, +0.12].
* P2′: at least 8 of the present items pass V-e for V2′.
* P3′: L − 1 in [0.00, +0.05] (session 102 measured +2.1 % on the same capture).
* P4′: X′ < X of session 102 (1.4201) on the common items.

## 6. Must not be claimed

That M5′ measured G's full price (SRT chasing, formats, VS/mesh, CPU side are not priced) · that a
PASS licenses G or says anything about 60 FPS · that a CLOSE is about CPU, P, F or R1 · that
`KYTY_BDA_LEAN` is a shippable path (no fault reporting in PS; measurement only) · that the run-time
alignment test is free (its branch is inside the price) · **any speedup or frame-rate gain.**
