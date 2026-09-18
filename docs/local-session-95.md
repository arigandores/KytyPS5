# Session 95 — route E, measurements M1 and M2. The single source of truth.

**Route E opens every session with three numbers:**

* **the budget:** ≤ ~3.0 µs a draw on a median frame, ≤ ~2.3 µs on a p99 frame (7 284 draws);
* **where the path stands:** 6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms (p50 12.83,
  p90 13.94, p99 15.77 with the clock pinned);
* **which of M1–M5 is undone: M3, M4, M5.** M1 and M2 are done, and each closed a route.

**Do not promise 60 FPS.** The estimate was ~15 % (8–25 %) before this session and it did not
rise: this session removed candidates, it did not find a way.

## 0. What this session decided

**M1 closed route P (parallel translation), and with it P+G.** Real, non-spin work outside the
translation thread is **181 278 µs a flip = 10.88 logical CPUs at twice today's frame rate**,
against the rule's ~8 (`ROADMAP.md:1011`, sealed before the numbers in `M1_RULE.md`). The
second branch did NOT fire: the most expensive guest thread costs 9 003 µs a game frame against
a threshold of ~12 000, so "60 FPS is out of reach for every route" is not supported.

**M2 closed route F (frame replay).** Coverage **C = 0.0035** against the sealed threshold 0.84
(`ROADMAP.md:1017`) — the share of GuestGpu draw time carried by draws whose resources repeat a
draw of the previous frame. `fr95a` was admitted in full and every control passed.

**What is left of route E: G (GPU-driven, 5–12 %) and R1 (≤ 3 %), both still needing M3 and
M5.** The two candidates this session removed carried the largest share of the estimate
(P 12–25 %, P+G 15–30 %, `judge.md` §3).

**Nothing was shipped. No default moved.** Two gates were added, both `MEASUREMENT ONLY`,
both default 0.

## 1. M1 — where the process's CPU goes

Full numbers and their sealed rule: **`M1_RULE.md`** (4 013 B, sha256 `929c5273e6d525da…`,
written before the emulator was opened) and **`M1_RESULT.md`**. In short:

* the record reproduces to the digit: `cpu_proc_us` 247 261.1 µs a flip on `log_mc94a.txt`,
  attributed 99 241.5, **unattributed 148 019.7 = 4.52 logical CPUs**;
* the unattributed CPU has a face: **12 threads, each 8 767–9 003 µs a flip, together 106 993
  µs a flip = 3.29 logical CPUs**, spread 2.7 %;
* ETW (`wpr` + `tracerpt`; xperf and wpa are NOT installed here) says those threads run the
  GAME's own x86-64 code — `guest/unmapped` **69–72 %** of their samples. Across the whole
  process: guest 40.58 %, `kyty_emulator.exe` 35.35 %, ntdll 9.56 %, kernel 9.06 %, and the
  **graphics driver only 1.83 %**;
* spin is separated from work by how the sampled instruction pointers concentrate: the record
  thread has **1 497 distinct addresses with two carrying 74 %** (spin, confirming
  `rec_spin_us`), the translation thread **8 080 addresses with top-10 at 12.8 %** (work), the
  12 guest threads **8 901 addresses over 870 pages, top-10 ≈ 28 %** (not a tight spin; two
  narrow places carry 16.8 % of it);
* **verdict: route P is CLOSED.** Robustness: writing off both narrow places as spin still
  gives 10.07 CPUs; subtracting the four M1 draw-ahead workers as well gives 9.16. For P to
  survive, another ~19 % of the whole process's CPU would have to be spin.

**The tension, recorded for the user's decision.** The rule fired on its letter, but its stated
reason — "there are no free cores to move the work onto" — does not follow on THIS machine
(16 cores / 32 logical): 10.88 CPUs of work would leave ~17 logical processors idle at 60 FPS.
The rule was applied as sealed, not reinterpreted after the fact.

## 2. M2 — frame-to-frame repetition of a draw's content

### 2.1 The instrument (gate `framerep`, `KYTY_FRAME_REP`, default 0)

Pre-registration **`pred/01_framerep.md`**, 12 348 B, sha256 `fafab3c4d85223e4…`, sealed before
the emulator was opened; the scorer `fr95.py` was written and **dry-run on the record (session
94's log with its arms relabelled) BEFORE the seal**, which caught two of its defects — a
control gated on the wrong instrument, and a band printing a vacuous HIT on an instrument that
never fired. Both were fixed before sealing. That order is the one session 94 got wrong.

The census reuses session 94's walk (`MergeCostCensus`) and hashes it three ways:

* **H_ident** — layout DEFINITION, image views + layouts + samplers, non-ring buffers
  {handle, offset, range}, BDA-convertible slots from `ok_raw` UNMASKED; stream-ring entries
  and flattened-SRT / shader-data descriptors collapse to fixed markers;
* **H_pay** = H_ident ⊕ the hash of the SRT / shader-data payload BYTES;
* **H_full** = H_pay ⊕ draw arguments ⊕ index buffer identity ⊕ topology ⊕ primitive restart ⊕
  every bound vertex buffer.

Three multisets per past frame (N−1, N−2, N−3), rotated by index when `GetFrameNum()` changes,
on the GuestGpu thread under the render mutex. A hit CONSUMES one occurrence. Frames are never
aligned by draw index (s66).

The instrument's own time is measured (`fr_sig_ns`, `fr_pre_ns`) and **subtracted from
`mc_pre_ns` / `mc_post_ns`** exactly as `mc_sig_ns` was in session 94, so both arms are
comparable and `mc_*` keeps its session-94 meaning.

### 2.2 The run `fr95a` — admitted in full

`30+1800:framerep=0 …|framerep=1 …` with `mergecost=1 bdacap=1 drawmerge=1` in BOTH arms,
ABBA, `KYTY_GPU_CLOCK_PIN=1`, binary `24debfc1dd7b820c…` (23 651 840 B), 8 556 flips,
window n ≥ 2100, arms 3 240 / 3 218 flips.

* `guards.py`: criteria 1, 2, 3, 3b, 4, 6, 7, 10 **PASS**. Check 0 WARN (two idle foreign
  windows, GPU at 1.0 %), check 5 WARN (draw distribution moved 8.52 pp — expected of anything
  that moves the GuestGpu thread's speed; the work itself is check 4, 0.126 % apart), checks 8
  and 9 SKIP (recorder off). **Check 6 is not a criterion; check 10 confirmed the binary and
  226 GateArm blocks, arm0 ×113 arm1 ×113.**
* `area_verdict.py`: **VALID** — area split −0.004 %, pair match 100.0 % (107/107), work within
  −0.126 %.
* `endpoint84.py`: the instrument's price **+1 467.8 ± 232.1 µs (2·SE), t = +12.65** on 108
  pairs. Per draw it is **0.627 µs** (`fr_sig_ns` 2 694.5 + `fr_pre_ns` 455.7 µs a flip).
* `check_s95_counters.py`: **10/10 identities PASS**, including `fr_n`/`mc_n` = 0.9999 and
  `fr_all_ns` / (`mc_pre_ns` + `mc_post_ns`) = 0.9999.

### 2.3 The numbers, armed arm, per flip

| | |
|---|---:|
| `fr_n` | 5 023.64 (`mc_n` 5 023.90) |
| `fr_id1` / `fr_id2` / `fr_id3` | **9.46** / 0.48 / 7.35 |
| `fr_pay1` / `fr_full1` | 8.18 / 8.18 |
| **C = `fr_id_ns` / `fr_all_ns`** | **0.0035** |
| C_pay / C_full | 0.0026 / 0.0026 |
| hits a draw | **0.0019** |
| `fr_ring` / `fr_id1` | 0.688 |
| payload hashed | 2 004 KiB a flip over 9 397 hashes (218 B each) |
| convertible slots a draw | 3.641, of which 10.12 % off-class |

**Controls: 7 HIT, 0 MISS.** Among them C6 `mc_has_ring`/`mc_n` = 0.8172 against session 94's
0.818 on another binary — the scene did not move; and the leak control read exactly 0.0000 with
every non-zero frame of the unarmed arm sitting at distance 29 of 30, i.e. a straddle.

**Predictions: 5 HIT, 7 MISS**, and all seven misses point the same way — I predicted 55 %
repetition and measured 0.19 %. The honest reading is that the prediction was wrong by two
orders of magnitude, not that the band was unlucky.

**Verdict by the sealed rule: C = 0.0035 < 0.84 ⇒ route F is CLOSED permanently.**

### 2.4 The defect I found in my own instrument, and what was done about it

`H_ident` takes the BDA-convertible slots from `ok_raw` unmasked, and such a slot can be served
by the stream ring, whose offset is fresh every draw by construction — session 94 wrote that
sentence itself. A Poisson reading of 3.641 convertible slots a draw with 10.12 % off-class puts
**~31 % of draws** carrying one. That cannot explain a 0.19 % hit rate, but it means **C as
measured is a LOWER bound**.

Rather than argue about it, a second pre-registration was sealed — **`pred/02_framerep_ring.md`**,
7 428 B, sha256 `f3962d75c9e4df36…` — and the instrument repaired to build THREE identities over
the same walk: the strict one, one with ring-served convertible slots collapsed (`H_identr`),
and one with EVERY convertible slot masked (`H_identm`), which is session 94's own signature and
therefore the CEILING of any canonicalisation. Its rule, sealed before the run:

> **`C_ceiling` < 0.84 ⇒ F is closed and the closing does not depend on how the convertible
> slots are canonicalised; `C_ceiling` ≥ 0.84 ⇒ `pred/01`'s verdict was carried by my hashing,
> not by the scene, and M2 is NOT settled.**

**Run `fr95b`, admitted in full** (guards criteria PASS; `area_verdict` VALID; counter
identities 10/10; controls **7 HIT, 0 MISS**; predictions **9 HIT, 0 MISS**; instrument
**+2 334.6 ± 108.1 µs, t = +43.19** on 114 pairs, 0.718 µs a draw). Binary ``b3161c1029c6930f…` (23655424 B)`.

| reading | hits a draw | coverage |
|---|---:|---:|
| strict `H_ident` | 0.0020 | **0.0033** |
| repaired `H_identr` | 0.0021 | **0.0038** |
| **ceiling `H_identm`** (session 94's own signature) | 0.0064 | **0.0072** |

**`C_ceiling` = 0.0072 < 0.84 ⇒ F is closed by the SCENE, not by my hashing.** Masking every
convertible slot — the most generous canonicalisation that exists — multiplies the hits by
3.23 and still lands 117× below the threshold.

What the repair also measured, and what it corrected in my own diagnosis:

* `fr_okring` / `fr_n` = **0.1406** — 14 % of draws carry a ring-served convertible slot, not
  the ~31 % my Poisson reading of `mc_mask_x` predicted. The band held (R4 ∈ [0.10, 0.60]),
  the point estimate did not;
* `fr_okslot` / `fr_n` = **3.64**, replicating session 94 and `fr95a` to three digits;
* the walk sees **28.41 image values and 15.32 non-ring buffer values a draw** — that is where
  the remaining distinctions live, and no session has ever split them;
* `mc_p` / `mc_n` = **0.1281**, against `fr95a`'s 0.1281 and session 94's 0.1278 — the scene
  did not move between the two runs (control C7);
* the asymmetry survives the repair: `fr_id2r` 0.8 against `fr_id3r` 7.8 a flip.

### 2.5 The asymmetry worth the next session's attention

`fr_id2` / `fr_id1` = **0.050** but `fr_id3` / `fr_id1` = **0.776**: matches against frame N−3
are fifteen times more common than against N−2, while all three are negligible in absolute
terms. If the repair keeps the asymmetry, the scene has a three-frame period (three frames in
flight is the obvious candidate) and every replay-shaped idea should be measured against N−3,
not N−1.

## 3. What is proven, what is not

**Proven.** Route P is closed by M1's sealed rule, on two independent instruments (per-thread
CPU accounting and ETW instruction-pointer concentration). Route F is closed by M2's sealed
rule on an admitted run whose every control passed. The unattributed CPU of the record belongs
to the game's own threads. The graphics driver costs 1.83 % of the process's CPU.

**Not proven.** That all of the guest threads' 69–72 % is work rather than waiting — two narrow
places (16.8 %) look like waiting and no guest symbols exist to split them. That the guest load
scales with the frame rate; it is assumed because the game steps its simulation at a fixed
1/60 s a frame, and that assumption is what turns 181 278 µs a flip into 10.88 CPUs.

**Traps this session walked into, recorded so the next one does not.** `StartAddress` is
useless for classifying threads on Windows — it is `RtlUserThreadStart` for all of them, and a
prediction written on it (M1's P2) is NOT EVALUABLE as phrased. A scorer's dry run on the
record is not a formality: it caught two defects in `fr95.py` minutes before the seal. And an
instrument that reuses another session's census inherits the reasons that census masked things
— session 94 masked the convertible slots for a different question, and taking them unmasked
put ring addresses back into an identity that was supposed to be canonical.

## 4. Not closed

* M3 (`bindfloor` ceiling stub), M4 (what must be sequential), M5 (the GPU price of BDA/LDG) —
  the three measurements route E still needs, and M3 is now the next one that can close
  anything (its rule closes G and R1 at ≥ 15.5 ms).
* The 4.05 ms outside the render mutex and the ~5 ms of `mh_emit` beyond `CommitBindings`, both
  never split — M3's preparation.
* The DRS clock floor: before any faster CPU path, the game must be kept off the 4K step
  (`ROADMAP.md:1032-1035`; the session-91 pin at pacer speed 1.0 does NOT do this).
* Carried from session 94: the BDA regime (OLD costs 2 242 µs a flip of `PrepareBda` alone, and
  OLD is the common launch state); the written `bc_ok` slots (490.5 µs a flip); `C_bda` in the
  NEW regime; the GPU side of the `bdaall` contrast; the single-chunk notify (99.9 µs); the
  `ObtainBuffer` ring timer; `pfhint`/`pfcap`/`dapin` with the pin; route B items 2, 8, 10, 12
  and the corrected 3.
* The video pass is a debt for both gates (neither can reach the renderer with its default 0,
  but neither was run with `--video`).
