# Session 88 — FACTS

**The single source of truth for session 88.** Everything is marked **[M]** measured (a counter in
an ADMITTED run of this session, or a prior session's run named), **[I]** inferred (read from
source and reasoned), **[NM]** not measured, **[R]** retracted.

**REVISED AFTER AN INDEPENDENT AUDIT.** Four agents re-derived every headline number with their own
parsers and attacked the reasoning. **Every number reproduced to the digit** — `skip88` 15.0026,
`ceiling88` 514.10, `T_clean` 567.39, `T_live` 285.12, `W` 0.34662, the arming identities, the
pre-schedule zeros and the 0-of-7 190 part/whole checks. **Nine defects were found in the TEXT and
every one of them is repaired below rather than argued with**: a mislabelled population (§3.3), a
median quoted where the convention is sums (§2), a unit price divided by the wrong arm (§3.3), an
unstated precision on `skip88` (§3.3), an allocation the verdict is NOT robust to (§3.4), a
denominator the pre-registration asked for and did not get (§4), a share marked [M] whose
denominator comes from another binary (§4.1), and three scoreboard entries scored against text the
pre-registrations forbid or that had been re-worded (§8). **The two verdicts — MARGINAL at 514 µs
and MIXED at W = 0.347 — survive every repair; one of them survives it less comfortably than §3.4
originally said, and that is now stated.**

## 0. In one sentence

**Both of session 87's headline numbers shrank by a factor of about two when the missing term was
measured, and both shrank the same way — the proof is smaller than the thing it was quoted as
being.** Route C's image half: the part of a memo-hit `ResolveTextureWith` that runs **after** the
proof is **15.00 ns a slot**, so `ceiling88` = 14 831.7 × (19.66 + 15.00) = **514 µs a frame**
against session 87's 1 107 µs — **MARGINAL by the rule sealed before the run, and the re-opening
does not survive its own missing term.** D2: the M1 witness loops inside the pipeline-cache lock
cost **567.4 µs (clean) + 285.1 µs (live) = 852.5 µs a frame**, i.e. **34.7 % of `AheadTake`** and
**21 % of the 4 049 µs block** — against the ~82 % / ~48 % that `FACTS` s87 §4.4 quoted from
session 72's reading on a different binary. Beside them: **a null control I wrote before the run
caught a defect in my own instrument and cost a run** (§2), a slot whose resolve does **not** take
the memo-hit path is priced for the first time at **284 ns** — of which **48.1 % is the cheap
null-descriptor path**, so the memo **miss** alone is **284…548 ns** and its exact value is [NM]
(§3.3) — and the eighth-session `dapin` debt was **taken, run, and failed admission** for a reason
that is now measured (§6).

## 1. The runs

Deciding binary **`25fd4f2e0010f7998bdff01fa01d464a77743af42fc1af3e80eb1ffc6a6073f8`**,
23 612 416 bytes. Sky Garden (`-lvl underwater_aerial_garden`), settled window **n ≥ 2100**,
`KYTY_FRAME_TRACE=lite`, `KYTY_GATE_SCHEDULE_ABBA=1`, period `30+1800`.

| tag | what | pre-registration | verdict |
|---|---|---|---|
| `spv88a` | one arm, `bindwit=2 bindlap slotstat slotstatcheck`, 120 s | `pred/01` §6 | **SCOUTING — every identity held**, §3.1. On the FIRST binary (`a78b4e57…`) |
| `wit88a` | ABBA `bindwit=1\|2`, 300 s | `pred/01` | **VALID and ADMITTED, and its null control C8 FAILED ⇒ NO NUMBER OF §3.1 IS REPORTED FROM IT**, §2. On the SECOND binary (`32d00058…`) |
| `wit88b` | ABBA `bindwit=1\|2`, instrument **repaired**, 300 s | `pred/04` | **VALID, both null controls PASS — THE DECIDING RUN**, §3 |
| `dwl88a` | ABBA `dawitloop=0\|1`, 300 s | `pred/02` | **INVALID** — pair match 70.4 % against ≥ 90 %. **Replaced; its contrast is quoted nowhere** |
| `dwl88b` | ABBA `dawitloop=0\|2`, 300 s | `pred/02` | **VALID** — §4 |
| `dwl88c` | ABBA `dawitloop=0\|1`, 300 s | `pred/02` | **VALID** — §4 |
| `dap88a` | ABBA `dapin=0\|3`, `recordthread=0` in **both** arms | `pred/03` | **INVALID** — area split +12.93 %, pair match 33.0 %. **Its contrast is quoted nowhere**, §6 |

**Ten emulator entries.** Three hit the historical `GpuHangAbort role=4` on the first entry after a
fresh build (the rule of sessions 54/61/85) and were absorbed by `--warmup-first` or by a second
attempt; **every counted entry reached the scene in 14.8–26.3 s.** Three binaries were built: the
first two are superseded and only `spv88a` and `wit88a` ran on them, which is said rather than
smoothed.

## 2. THE NULL CONTROL I WROTE BEFORE THE RUN CAUGHT MY OWN INSTRUMENT [M]

`pred/01` §4 named two checks that **can** fail, after session 87's A8 was scored NOT EVALUABLE for
being an algebraic identity. Both were written by substituting the definitions and asking whether
the run could disagree. **One of them did.**

| | `bindwit=1` | `bindwit=2` | |
|---|---:|---:|---|
| **C8** `bl_res_us / bl_res_n` | 75.14 ns | 72.30 ns | **−3.78 %, band ±3 % ⇒ FAIL** |
| C7 `bl_wnh_us / bl_wnh_n` | 290.45 ns | 289.56 ns | −0.31 %, PASS |
| `cpu_net_us` (endpoint, 119 pairs) | — | — | −126.1 ± 74.6 µs, t = −3.38 |
| `cpu/draw` (`area_verdict`, 119 matched pairs) | — | — | −0.402 % ± 0.127 %, t = −6.34 |
| `mh_bind_us`, **means over the settled window** | 11 030.4 | 10 892.7 | **−137.7 µs** — the whole difference is in the bind phase |

*(The first edition of this table printed 11 063 / 10 972 = −91 µs. Those are **medians**, and this
document's own convention — and `dawit88.py`'s docstring — is ratios of sums. The audit caught it;
the means are above, they are larger, and they agree better with `cpu_net_us` = −126.1 µs than the
medians did. **Medians are still not additive, and I still reached for one.**)*

Both arms take **exactly one** `NowNs()` a slot, so it is not a mark count. The explanation,
**found after the fact and labelled as such**: `NowNs()` (`frameStats.cpp:197-210`) is `__rdtsc()`
divided by a calibrated `double`; at `bindwit=2` the mark sat **inside** `ResolveTextureWith` with
`ConfigureImageSource`, `TouchImage`, the DCC adoption and `emit` still ahead of it, so its latency
overlapped independent work, while at `bindwit=1` it sat in the caller and the very next
instructions **depended on it**. Per sampled hit slot the gap is 2.84 × 47 800 / 19 638 =
**6.9 ns** — one mark (session 87 measured `T` = 7.40 ns).

**It mattered beyond bookkeeping.** If a closing `rdtsc` can retire before the work it is timing,
that arm's interval is short and `skip88` = W1 − W2 is biased **up** — the anti-conservative
direction for a re-opening. `wit88a` returned `skip88` = 24.05 ns; the repaired instrument returns
**15.00 ns**. **The control was worth its run.**

`pred/04` repaired it before `wit88b` existed: **both** armed values now stamp inside
`ResolveTextureWith` on the memo-hit path — 2 at the decision, 1 at the **end of the memo-hit
tail**, immediately before `return emit(...)`. The loop then takes no timestamp at all on a sampled
hit slot, and `skip88` additionally **excludes `emit`** (the caller's `emplace_back`), which an
amortisation would still have to perform.

**A second defect of my own was caught earlier, by reading rather than by a run** [I]: as first
written, `PrepareBindings` armed the resolve for the **whole loop**, so at `bindwit=2` a stamp was
taken on memo-hit slots the alternating phase does not sample — a second timestamp on about half
the hits, ~165 µs a frame in one arm only. It was found and repaired **before any number**
(`patch_s88_fix.py`), and C8 would have caught it too.

## 3. §3.1 — THE WITNESS SHARE, MEASURED [M], `wit88b`

### 3.1 Admission

| criterion (session 81 §1, carried unchanged) | `wit88b` | |
|---|---|---|
| 1. `guards.py --first-frame 2100` check 2 | 0 MISMATCH lines; **3/16 counters REACHABLE and zero** (`sl_bad` among them, because `slotstatcheck=1` rides both arms) | PASS |
| 1. …check 10 | binary confirmed, 250 `GateArm` blocks, arm0 ×125 arm1 ×125 | PASS |
| 2. arming by a counter inside the run | §3.2 | PASS |
| 3. area split < 1.0 % | **−0.001 %** | PASS |
| 3. pair match ≥ 90 % | **100.0 % (120/120)** | PASS |
| 3. work within 0.5 % | **+0.001 %** | PASS |
| 4. `summary4` / `area_verdict` cpu/draw | −0.327 % ± 0.130 %, t = −5.02 | reported |
| 5. bracketing timer `da_take_us` | on `FrameTrace-draw`, unmoved within noise | reported |
| 6. everything on matched pairs | 120 of 120 | PASS |

`guards.py` returns **9 PASS, 0 FAIL, 1 WARN, 2 SKIP** and check 6 (cores) PASSED, which it usually
does not. `spv88a`, on the first binary, had already shown every identity of `pred/01` §6 holding.

### 3.2 Arming, proved inside the run [M]

**All six new counters read exactly 0 — median AND maximum — over the 1 200 settled frames before
the first `GateArm:` line**, in `wit88a` and in `wit88b`, because `gates_base.txt` does not name
`bindwit` and it keeps its compiled fallback of 0. **Both arms of this ABBA are armed, so the
pre-schedule window is the only zero test the run has** — `pred/01` §6 said so before the run
rather than quoting an arm-0 median as one.

### 3.3 THE SPLIT [M] — `wit88b`, sums over 3 600 + 3 590 settled frames

| | ns a sampled hit slot |
|---|---:|
| `W1` = `bl_wit_us/bl_wit_n`, arm `bindwit=1` — loop + the memo-hit resolve **up to the end of its tail**, i.e. **excluding `emit`**, + `T` | **37.49** |
| `W2` = the same, arm `bindwit=2` — loop + **the proof** + `T` | **22.48** |
| **`skip88` = W1 − W2 — the memo-hit tail, `T` CANCELS EXACTLY** | **15.00** |

Coverage `(bl_wit_n + bl_wnh_n + bl_wit0_n) / bl_res_n` = **0.5001 / 0.4998**, as the alternating
phase constructs it. **No frame of 7 190 has the sampled parts exceeding `bl_res_us`, and none has
the sampled count exceeding `bl_res_n`.** The memo-hit share of the loop's own population is
**93.62 % / 93.71 %**, against this run's `tex_hits / b_texn` = **93.85 %** — a 0.2 pp agreement
between a counter this instrument defines and one it does not touch. `bl_img_us / bl_img_n` reads
**22.75 / 22.74 ns** against session 86's 22.30 (+2.0 %).

**Both null controls PASS:** C7 **+1.58 %** (band ±10 %), C8 **−2.66 %** (band ±3 %). The residual
instrument asymmetry is `cpu_net_us` **−106.7 ± 77.7 µs**, down from −126.1 in `wit88a`.

**Priced for the first time: a slot whose resolve does NOT take the memo-hit path costs
`bl_wnh_us / bl_wnh_n` = 284.35 / 288.85 ns**, over 6.38 % of the slots, against **37.49 ns** for a
slot that does — **7.6× like for like**.

**And that population is not "a memo miss", which the first edition of this file called it.** It is
*"did not reach the stamp"*, and the stamp is on the memo-hit path only, so it also contains the
null-descriptor block (`descriptors.cpp:781-846`). Measured on `wit88b`: non-hit resolves =
`b_texn − tex_hits` = **2 941.90 a frame**, decomposing exactly into `tnull_hit` **1 414.65
(48.1 %)** + `texmemo_collide` **1 518.05** + `texmemo_stale` **9.20**. **So half the priced
population is the cheap null path, the memo miss alone is bounded by 284…548 ns, and its exact
value is [NM].** The first edition also divided 284.35 by `W2` = 22.48 — the *proof* half of a
hit, from the other arm — and published **12.6×**. **That was wrong twice over and it is
retracted [R]; the like-for-like figure is 7.6×.**

**Importing session 87's `T` = 7.40 ns** — a between-run constant, and labelled as one — the proof
is `(22.48 − 7.40) / (37.49 − 7.40)` = **50.1 %** of that interval, and the tail is the other half.

### 3.3a HOW PRECISE `skip88` IS, which the first edition did not say [I]

**C8 passing at ±3 % does not certify `skip88` to ±3 %.** At `P_res` = 73.73 ns, a 3 % band is
±2.21 ns a slot; the arms differ only on sampled memo-hit slots, of which there are
19 676.5 a frame against 47 848.9 slots, so ±2.21 ns a slot is **±5.4 ns a sampled hit slot =
±36 % of `skip88`**. The measured residual is −2.66 %, i.e. **≈ 4.8 ns a hit slot, about 32 % of
the 15.00 ns**, in the direction `pred/04` §1 identified as inflating `skip88`. So the honest
reading is **`skip88` = 15.0 ns known to about ±32 %, i.e. 10…20 ns**, and `ceiling88` is
**514 µs in a band of roughly 440…590 µs** — **MARGINAL throughout**, which is why the verdict is
unaffected and the precision is stated anyway.

**One arm asymmetry is unexplained and is named rather than smoothed** [M]: `bl_wit0_n` reads
2 912.5 against 2 874.5 (**−1.30 %**) and `bl_wnh_n` 1 340.3 against 1 323.5 (**−1.25 %**) between
arms whose underlying populations are identical to 0.06 % (`bl_res_n`) and 0.02 % (non-hit
resolves), and `bl_wit0_us / bl_wit0_n` differs by **−22.8 %** (78.72 against 60.76 ns). That parks
**55.6 µs a frame** of real arm difference in the slot-0 bucket, **which neither null control
inspects**.
It does not enter `skip88`, which is formed from `bl_wit_*` alone.

### 3.4 THE VERDICT, by the rule fixed in `pred/01` §7 before the run

    ceiling88 = sl_img_dupv x (19.66 ns + skip88) = 14 831.7 x (19.66 + 15.00) = 514.1 us a frame
    RE-OPEN at >= 1 000      MARGINAL at 300..1 000      CLOSED FOR GOOD below 300

→ **514.1 µs. MARGINAL. ROUTE C'S IMAGE HALF DOES NOT STAY RE-OPENED**, against session 87's
1 106.9 µs — **−53.6 %**. The margin to the nearest threshold is +71.4 % above 300 and −49 % below
1 000, i.e. **it is not near either edge**, unlike session 86's 2.5 % and session 87's 10.7 %.

**`sl_img_dupv` was measured in this session's own run** (`slotstat=1` in both arms), as
`FACTS` s87 §3.5 required: **14 831.7 a frame**, against `drm86a`'s borrowed 14 875.5 — **−0.3 %**.
The borrowed number was right; **the term that was missing was the one nobody had measured, and it
was the one that moved.**

**THE VERDICT IS NOT ROBUST TO THE RULE'S OWN ALLOCATION, AND THE AUDIT IS RIGHT THAT THE FIRST
EDITION DID NOT SAY SO** [I]. The rule treats the 19.66 ns of `RebindImages` as **wholly
removable** and the proof half of `PrepareBindings` as **wholly not**. Neither end of that is
argued anywhere:

| allocation | `ceiling88` | band |
|---|---:|---|
| **the sealed rule** — 19.66 removable, the proof not | **514 µs** | MARGINAL |
| `FACTS` s85 §12.6c read strictly — the 19.66 ns **is itself the proof** and is not removable | **222 µs** | **CLOSED FOR GOOD** |
| the whole memo-hit interval removable, as a per-stage witness amortisation would claim | **738 µs** | MARGINAL |

**The 300 µs threshold lies inside that span.** The sealed rule was fixed before the run and its
answer is the one this session routes on — but **the stricter reading, which is the one
`FACTS` s85 §12.6c actually supports, CLOSES the route rather than leaving it marginal.** Both
readings say the same thing about what to do next: **do not build it.**

### 3.5 AND WHAT IS STILL AN UPPER BOUND

`ceiling88` is an **UPPER** bound, and `pred/01` §5 listed why before the number existed:

* `ConfigureImageSource`'s own early-out (`textureCache.cpp:1244-1247`) is a liveness test in
  substance and is counted on the **skippable** side.
* `TouchImage`, `tick_accessed_last` and the DCC adoption are **side effects**; whether an
  amortisation may skip them is **[NM]** and is not argued here.
* the 19.66 ns of `RebindImages` is itself, per `FACTS` s85 §12.6c, the proof of correctness; its
  own witness share is **[NM]**, so the rule's first term is an upper bound too.
* `BindImage` (8.49 ns, session 87) is outside `skip88` and provably cannot be skipped.

**And the honest reading: 514 µs is 1.6 % of a 31.6 ms frame, it is an upper bound with four
unmeasured reductions inside it, and the mechanism that would collect it does not exist.**

## 4. §3.2 — THE WITNESS LOOPS PRICED INSIDE THE LOCK [M], `dwl88c` + `dwl88b`

`AheadTake` runs with `PipelineCache::m_mutex` held — the lock is taken at
`pipelineCache.cpp:4307` and every path to `AheadTake` (`:3070`) is below it in the same scope.

| | value |
|---|---:|
| `da_take_us`, arm `dawitloop=0` of `dwl88c` | 2 459.5 µs a frame (283.14 ns a call over 8 686.7 calls) |
| …arm `dawitloop=1` (the **clean** loop uncompared) | 1 892.2 µs (217.61 ns) |
| **`T_clean`** | **+567.4 µs a frame, 65.5 ns a call** |
| `da_take_us`, arm `dawitloop=0` of `dwl88b` | 2 381.2 µs (273.75 ns) |
| …arm `dawitloop=2` (the **live** loop uncompared) | 2 096.0 µs (240.87 ns) |
| **`T_live`** | **+285.1 µs a frame, 32.9 ns a call** |
| **`T_clean` + `T_live`** | **852.5 µs a frame** |
| **`W` = (T_clean + T_live) / `da_take_us`(unarmed)** | **0.3466** |
| residue — the singles loop, the two-probe lookup, the `dawitptr` prefetch pass, `CopyAheadResult` | **1 607.0 µs a frame, DERIVED** |

**By the routing rule of `pred/02` §3, applied mechanically: 0.25 ≤ W < 0.50 ⇒ MIXED.** The rule
was sealed before the run and it is reported as it reads.

**`pred/02` §3 also asked for the second denominator to be quoted beside the first, and the first
edition printed only one** — the audit caught it. `852.5 / 2 381.2` (`dwl88b`'s unarmed arm) =
**0.3580**; normalising each shift on its own run's baseline gives **0.3504**; on per-call ns,
**0.3476**. **The band across every defensible normalisation is 0.347…0.358, and MIXED holds in
all of them.** `T_clean` and `T_live` are summed across two runs whose identically-configured
unarmed arms differ by **3.3 %**, and the sum assumes the two loops are additive — **untestable
with a 0/1/2 knob, and said here rather than left to be noticed.**

### 4.1 THE CORRECTION THIS MAKES TO SESSION 87 [M]

`FACTS` s87 §4.4 attributed **~82 % of `AheadTake` and ~48 % of the whole 4 049 µs block** to the
M1 witness verification, **on the strength of session 72's 1.929 ms on a different binary, outside
the lock — and said so rather than pretending to have measured it.** Measured here, inside the
lock, on this binary:

| | session 72, quoted by s87 | **session 88** | factor |
|---|---:|---:|---:|
| the witness share of `AheadTake` | 82.5 % | **34.7 %** [M] | **2.4** |
| the witness share of the 4 049 µs block | 47.6 % | **21.1 %** [I] | **2.3** |

**The second row is [I], not [M], and the first edition marked it [M]** — the audit caught it. Its
denominator, 4 049.4 µs, is session 87's `pgl87a` **on a different binary**; this run's own
`pg_ahead_us` reads 2 678.1 against session 87's 2 557.3 (**+4.7 %**), so the block is not
identical and `pred/02` §5 forbids exactly that comparison. The share of `AheadTake` — the [M] row
— is entirely within-run.

**A factor of 2.4 on the measured row and 2.3 on the inferred one.** It is the sixth time in this
record that a figure carried from elsewhere was wrong by 2–20×, and the first time the quotation
was flagged as a quotation by the session that made it — which is exactly what made it cheap to
check.

### 4.2 The identities and cross-reads [M]

* **Arming:** `da_loop_skip` = **27 722.2** against `da_runs_clean` **27 723.6** (−0.00 %) in
  `dwl88c`'s armed arm, and **54 952.5** against `da_runs − da_runs_clean − da_singles` =
  **54 955.9** (−0.01 %) in `dwl88b`'s. Two different arithmetic identities, both to 0.01 %.
* **An independent, containing timer moves with it:** `pg_ahead_us` shifts **+566.9** against
  `da_take_us`'s **+567.4** in `dwl88c` (**−0.1 %**) and **+285.5** against **+285.1** in `dwl88b`
  (**+0.1 %**).
* **The lock hold moves with it:** `pl_prog_hold_us` **4 522.8 → 3 986.9** (−535.9 µs) and
  **4 508.0 → 4 228.0** (−280.0 µs). **816 µs of the 4.5 ms pipeline-cache-lock hold is the M1
  witness loops.**
* **The endpoint sees most of it:** `cpu_net_us` **−470.8 ± 75.7 µs, t = −12.44** (`dwl88c`) and
  **−270.4 ± 74.9 µs, t = −7.22** (`dwl88b`) — 83 % and 95 % of the `da_take_us` shift, on a
  counter the knob does not touch.
* **The knob removes comparisons, not failures:** `da_stale` = 0.0 and `da_late` ≤ 0.5 a frame in
  every arm, and `da_hit` moves +0.09 % / +0.04 %. Nothing was validated that would not have been.
* `da_singles` reads **0.000 a frame**, so the singles loop — which **neither** value of the knob
  skips — is empty in this scene and the residue is the lookup, the prefetch pass and the copy.

### 4.3 What the residue is, and what it is not [I]

**1 607 µs a frame — 65 % of `AheadTake` — is not the witness.** It is the two-probe
open-addressed slot lookup (`pipelineCache.cpp:2731-2905`), the `dawitptr` prefetch pass over
`witness.live_runs` (`:786-805`, which `dawitloop` does **not** skip at either value) and
`CopyAheadResult`. **That is D2's next number and it is a different lever from the proof.**

## 5. THE ODDS, restated after the measurements

| | before session 88 | after |
|---|---:|---:|
| route C's image half | 1 107 µs, RE-OPENED (margin 10.7 %) | **514 µs, MARGINAL** |
| D2's block attributed to the witness | ~1 930 µs (~48 %), quoted from s72 | **852 µs (21.1 %), measured** |

Both of session 87's headline figures were **upper bounds with one unmeasured term each**, both
terms were measured this session, and **both figures fell by a factor of about two.** The sum of
what the two now bound is **1.37 ms of a 31.6 ms frame** — and neither is a saving, because neither
mechanism exists.

## 6. §3.3 — THE `dapin` DEBT WAS TAKEN, RUN, AND FAILED ADMISSION

Eight sessions old; sessions 86 and 87 both declined it. It was taken.

**The run the brief prescribes is a two-variable contrast** [I], and that was read out of the
source before anything ran (`pred/03` §2): `PacketsWanted()` (`context.cpp:208-211`) requires
`m_recorder != nullptr` and `CommandScheduler::BeginCommand` (`commandScheduler.cpp:671`) nulls it
when the gate is off, so **`recordthread=0|1` turns off the record thread AND the whole
packet-recording path together**, and every draw takes the direct path. It also does not destroy
the thread — `Recorder()` (`commandScheduler.cpp:643-649`) creates it lazily and once — so in the
off arm it is idle, not absent, and its `dapin` affinity is sticky.

`dap88a` therefore ran the single-variable contrast instead: **`dapin=0 | dapin=3` with
`recordthread=0` pinned in both arms.**

**The configuration was proved** [M]: `rec_pack`, `rec_bind`, `rec_pub`, `rec_n` and `rec_direct`
all read **0.000 a frame in both arms**, and `cpu_record_us` reads ~16 µs a frame — the idle
thread, exactly as the source said. **Predictions E1, E2 and E7 HIT.**

**And the run is INVALID and its contrast is quoted nowhere**: area split **+12.93 %** against
< 1.0 %, pair match **33.0 %** against ≥ 90 %. The cause is structural and it is read off the
**admission diagnostics themselves** — the arms are ~9 % of CPU a frame apart, which moves the DRS
ladder, which makes them render different areas, which is what the matched estimator refuses.
**That ~9 % is an admission statistic of a rejected run, not a measurement of anything**, and it is
labelled so because the first edition quoted it two sentences after saying the contrast is quoted
nowhere.

**So the brief's claim that one run separates existence from affinity is false** [I], and it is
false for a reason nobody had measured: **the contrast is too large for this harness's
DRS-matched estimator once the record path is off.** The debt stays open with a sharper next step
than it had — an estimator that survives a DRS shift, or a contrast small enough not to cause one —
and **`pred/03` §5 forbids quoting anything else from this run, which is honoured.**

## 7. WHAT WAS NOT DONE

* **No video pass, and none is owed.** `bindwit` is compiled default 0, nothing shipped, and with
  it off `ResolveTextureWith` gains one never-taken branch and `PrepareBindings` two. Not a
  byte-identical binary, no pixel comparison made — the same argument and the same limitation as
  sessions 86 and 87.
* **No `acc88a`.** No default changed.
* **`pg_pm_us` = 462 µs a frame at 52 ns a call is still unattributed** — `PushData::StartFor`
  against the `specialization ==` compare.
* **D1 was not started**; its ~2.1 ms ceiling is known and it is a rewrite.
* **The witness share of the 19.66 ns of `RebindImages` is still [NM]**, and it is the last
  unmeasured term inside `ceiling88`.
* **Whether the memo-hit tail may be skipped at all is [NM].** `skip88` prices it; nothing here
  argues it is skippable.

## 8. THE SCOREBOARD — all forty-seven predictions, scored

`pred/01_bindwit.md` §8 — sixteen, on `wit88a` (**whose §3.1 quantities are NOT published**, §2):

| | prediction | result |
|---|---|---|
| C1 | every `bl_wit*` / `bl_wnh*` 0 median and 0 maximum pre-schedule | **HIT** (1 200 frames) |
| C2 | coverage in 0.40…0.60 | **HIT, and DISCOUNTED** (0.5000) — constructed |
| C3 | parts ≤ whole in every frame | **HIT** (0 of 7 160) |
| **C4** | **hit share 0.80…0.99 and within 5 pp of `tex_hits/b_texn`** | **HIT** (0.9351 against 0.9378, 0.27 pp) |
| **C5** | **`W1 > W2`** | **HIT** (47.14 > 23.09) — scored on a defective instrument, **not a published measurement** |
| **C6** | **`skip88` in 5…60 ns** | **HIT** (24.05) — **scored, NOT a published measurement.** The audit is right that printing the value is in tension with §1's "no number of §3.1 is reported from it"; it is printed because a scoreboard nobody can audit is worse, and it is marked here, at C5, at C9 and at C11 |
| **C7** | **null control 1 within 10 %** | **HIT** (−0.31 %) |
| **C8** | **null control 2 within 3 %** | **MISS (−3.78 %) — and it caught a real defect in my own instrument.** §2 |
| C9 | `W1` in 30…75 ns | **HIT** (47.14) — scored, **not a published measurement** |
| C10 | `bl_img_us/bl_img_n` within 15 % of 22.30 | **HIT** (21.75 / 21.78) |
| **C11** | **`ceiling88` < 1 107 µs** | **HIT** (647.9) — scored, **not a published measurement**; the published ceiling is `wit88b`'s 514.1 |
| **C12** | **`sl_img_dupv` within 25 % of 14 875.5** | **HIT** (14 823.8, −0.3 %) |
| C13 | `sl_over` = 0 and `sl_bad` = 0 | **HIT** |
| C14 | `gpu_busy_us` inside its own 2·SE | **HIT** (+0.062 % ± 0.188 %) |
| C15 | `draws` within 1.5 % on sums | **HIT** (+0.030 %) |
| **C16** | **`\|cpu_net_us\|` < 400 µs** | **HIT** (126.1) |

`pred/04_bindwit2.md` §4 — ten, on `wit88b`:

| | prediction | result |
|---|---|---|
| **F1** | **C8 repaired: within 3 %** | **HIT** (−2.66 %) — discriminating, and it is the point of the repair |
| **F2** | **C7 still holds** | **HIT** (+1.58 %) |
| **F3** | **`\|cpu_net_us\|` < 200 µs** | **HIT** (106.7) |
| F4 | every identity of `pred/01` §6 | **HIT** |
| **F5** | **`skip88` in 5…60 ns** | **HIT** (15.00) |
| **F6** | **`skip88` < `wit88a`'s 24.05 ns** | **HIT** (15.00, −38 %) |
| F7 | `sl_img_dupv` within 3 % of 14 823.8 | **HIT** (14 831.7, +0.05 %) |
| F8 | `bl_img_us/bl_img_n` within 15 % of 22.30 | **HIT** (22.75 / 22.74) |
| **F9** | **the routing rule returns the same band** | **HIT** (MARGINAL both ways) — the band did not rest on the defect |
| F10 | `draws` within 1.5 %, `gpu_busy_us` inside its own 2·SE | **HIT** (+0.001 %, +0.088 % ± 0.170 %) |

`pred/02_dawitloop.md` §4 — thirteen, on `dwl88c` and `dwl88b`:

| | prediction | result |
|---|---|---|
| **D1** | **`da_loop_skip` = 0 in the unarmed arm AND = `da_runs_clean` within 2 % in the armed one** | **MISS on the first clause** (1.7 a frame, **0.006 %** of the armed value — the schedule straddle), **HIT on the second** (−0.00 %). **The defect is mine**: session 86 recorded that "exactly 0" is unreachable on sums and `pred/01` §6 named the statistic — `pred/02` did not. **The second clause was sealed against `dwl88a`, which went INVALID; it is scored on its replacement `dwl88c`, and the substitution is flagged here rather than left silent** |
| **D2** | the same for `dawitloop=2` | **MISS on the first clause** (3.2 a frame), **HIT on the second** (−0.01 %) |
| **D3** | **`T_clean` positive, 100…2 000 µs** | **HIT** (567.4) |
| **D4** | **`T_live` positive, 50…2 000 µs** | **HIT** (285.1) |
| **D5** | **parts ≤ whole** | **HIT** (852.5 < 2 459.5) |
| **D6** | **`W` ≥ 0.50, i.e. session 72's reading transfers** | **MISS (0.3466) — and the miss is the finding.** §4.1 |
| D7 | `\|Δpg_ahead_us − Δda_take_us\|` < 30 % of `Δda_take_us` | **HIT** (+0.1 % in both) |
| **D8** | **`da_hit` within 1 % between arms** | **HIT** (+0.09 % / +0.04 %) |
| D9 | `cpu_net_us` negative, 100…2 500 µs | **HIT** (−470.8 / −270.4) |
| D10 | `gpu_busy_us` inside its own 2·SE in both runs | **MISS on `dwl88c`** (+0.204 % against ±0.174 %), HIT on `dwl88b` (+0.094 % ± 0.176 %) |
| D11 | `draws` within 1.5 % on sums | **HIT** (+0.082 % / +0.039 %) |
| **D12** | **neither run hits `GpuHangAbort:`, `ErrorDeviceLost` or `Unhandled exception:`** | **MISS.** An *entry* attempt of `dwl88c` hit the historical `role=4` hang. The first edition scored this HIT by restating the sealed band as "neither **counted** run", and **the word "counted" is not in the sealed text.** The audit caught the narrowing. The counted runs are clean and `guards.py` check 1 PASSes on both — **but a band is not re-worded at scoring time, and this is the sixth defect in a prediction I wrote myself** |
| D13 | `pg_ahead_n` within 1.5 % between arms | **HIT** (+0.10 % / +0.04 %) |

`pred/03_dapin.md` §4 — eight, on `dap88a`:

| | prediction | result |
|---|---|---|
| **E1** | **`rec_pack`, `rec_bind`, `rec_pub`, `cpu_record_us` show the record path off in both arms** | **HIT** (0.000 a frame; `cpu_record_us` ~16 µs = the idle thread) |
| E2 | `rec_ccd_x` = 0 in both arms | **HIT** |
| **E3** | **the `gpu_busy_us` effect reproduces at ≥ +1.0 %** | **NOT EVALUABLE — the run is INVALID** and `pred/03` §5 forbids quoting it |
| E4 | `da_take_us` per call moves < 5 % | **NOT EVALUABLE** |
| E5 | `draws` within 1.5 % on sums | **NOT EVALUABLE.** The first edition scored it HIT at +0.126 %; that is a between-arm contrast of a run `pred/03` §5 forbids quoting. **The audit caught it.** The figure survives only as an admission diagnostic of the rejected run |
| E6 | `cpu_net_us` negative, < 4 000 µs | **NOT EVALUABLE** |
| **E7** | **the run reaches the scene with `recordthread=0`, no hang** | **HIT** (14.9 s, first attempt) |
| E8 | both arms' `gpu_busy_us` above a record-path-live run | **NOT EVALUABLE** — and it is a between-run comparison, which this programme does not make |

**Across four pre-registrations: 47 predictions, 36 hits, 6 misses, 5 not evaluable** — after the
audit moved D12 from HIT to MISS and E5 from HIT to NOT EVALUABLE. One hit (C2) is discounted as
constructed. **Three of the six misses (D1, D2, D12) are defects in predictions I wrote myself** —
the fourth, fifth and sixth in three sessions, after session 86's H1 and I1 and session 87's A8 —
and **one miss (C8) is the control doing its job**, which is the first time in this record a
pre-registered check has caught the session's own instrument.

## 9. WHAT IS NOT CLOSED, with the next measurement named for each

| debt | next number | since |
|---|---|---|
| **the residue of `AheadTake`, 1 607 µs a frame (65 %)** — the two-probe lookup, the `dawitptr` prefetch pass and `CopyAheadResult` | a rolling-mark chain inside `AheadTake`, the `proglap` idiom one level down | **88** |
| **whether `AheadTake` can run outside `PipelineCache::m_mutex`** — §4.2 now says 816 µs of the 4.5 ms hold is the witness loops | read the source; the lock is taken at `pipelineCache.cpp:4307` | 83 |
| **`dapin`'s GPU cost** — the corrected contrast was run and FAILED admission at +12.93 % area split | an estimator that survives a DRS shift, or a contrast that does not cause one | 79 |
| **the witness share of the 19.66 ns of `RebindImages`** — the last unmeasured term inside `ceiling88` | a counter in the `texfast` fast path | 88 |
| **`pg_pm_us` = 462 µs a frame at 52 ns a call** | split `PushData::StartFor` from the `specialization ==` compare | 87 |
| **D1 — `BufferCache::UploadCopies`**, 22.8 MiB a frame at 11 GB/s | a rewrite, ceiling ~2.1 ms known | 85 |
| route B items 2, 8, 10, 12 and the corrected item 3 | read the source first; every line number in `PLAN_82_bind.md` is stale | 85 |
| the marginal price of a slot (`b_hit`) — OLS degenerate, VIF 60.9 | another source of variation | 85 |

## 10. THE ARITHMETIC

| | value |
|---|---:|
| shipped baseline (`acc82a`, not re-measured since session 82) | 31 642 µs = 31.60 FPS |
| 60 FPS | 16 667 µs |
| the measured sequential floor `S_hi` (session 83) | 20 838 µs |
| **§3.1: the memo-hit tail of `ResolveTextureWith`** | **15.00 ns a slot; the proof is the other 50 %** |
| **route C's image half, by the rule sealed before the run** | **514 µs ⇒ MARGINAL, against session 87's 1 107 ⇒ −53.6 %** |
| a slot that does NOT take the memo-hit path, priced for the first time | **284 ns, 7.6× a hit**, on 6.4 % of slots; **48.1 % of that population is the null path, so the memo miss alone is 284…548 ns [NM]** |
| **§3.2: the M1 witness loops inside the lock** | **567.4 + 285.1 = 852.5 µs a frame = 34.7 % of `AheadTake`, 21.1 % of the block** |
| …against what session 87 quoted from session 72 | ~82 % / ~48 % — **a factor of 2.4** |
| the residue of `AheadTake`, derived | **1 607 µs a frame** |
| of the 4.5 ms `PipelineCache::m_mutex` hold, the witness loops | **816 µs** |

**The honest statement of the task.** Session 87 said both of the largest unopened blocks were the
price of proving a cached answer is still good, and published two figures for it. **Session 88
measured the term each of those figures was missing, and both figures halved.** The proof is
**50 %** of a memo-hit resolve, not all of it; the witness loops are **21 %** of the block under
the pipeline-cache lock, not ~48 %. What is left in the two blocks is **work** — a two-probe
lookup, a prefetch pass and a copy on one side, a `ConfigureImageSource` / `TouchImage` /
DCC-adoption tail on the other — and **route C's image half no longer clears its own re-opening
floor.** The programme is not out of levers; it is out of the belief that these two were big.
