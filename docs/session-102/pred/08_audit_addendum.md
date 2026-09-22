# Sealed addendum 08 — session 102: the adversarial audit of M5. The measurement stands; "G is closed" is WITHDRAWN

**Immutable once written.** Seals 01–07 are NOT edited. Five auditors, each on one lens (independent
recount, instrument, variant fidelity, protocol, claims), each told to refute and to default to
refuted. **Recount: NOT REFUTED. Instrument: NOT REFUTED. Claims: NOT REFUTED for the numbers, with
wording defects. Protocol: REFUTED. Fidelity: REFUTED.** Every decisive point below was checked
against the sources or the raw bench data before being written here.

---

## 0. What stands and what is withdrawn

**Stands (reproduced exactly by two independent recounts from `bench_m5cap102.json`):** on the ten
top shaders of Sky Garden, in a capture of the session-102 binary, today's emitter's BDA path (arm V2)
costs **X − 1 = +0.4201** (90 % CI [0.4121, 0.4242]) against the recompiled base, **Y − 1 = +0.3324**
([0.3247, 0.3356]) against the same granularity through descriptors (V2s), and the const-bank → global
load alone (V1) **L − 1 = +0.0208** ([0.0183, 0.0256]); V2s/A − 1 = +0.0608; A/B − 1 = −0.0026; every
control V-a…V-g PASS; 10/10 items present; V2 excludes S1 and S8 by V-e (21.87 % of A time). The result
survives dropping any single item (worst: without S3, X 1.309, Y 1.245) and holds on the compute items
alone, which carry no STRONG loads (X 1.554, Y 1.480).

**Withdrawn: that M5 closes G, in either tier.** The scorer's label `CLOSE-machinery` is the arithmetic
of `pred/02` §3; it is **not** a licensed decision, for the three reasons below. G is **alive and
unlicensed**, exactly as before the session; whether it stays alive is put to the user.

## 1. Defect A (FATAL to the licence) — pred/02 changed the verdict and was not recorded in ROADMAP first

`pred/02` replaced the decision composition (arm V2s; X, Y, L; two CLOSE tiers; the "strict lower bound"
path; R = 20) and **withdrew the premise ROADMAP records** for trusting a CLOSE (`ROADMAP.md` §2 E, M5,
clause (в): "V2 is a LOWER bound, so a CLOSE on it is robust"). ROADMAP was last changed in `0d35faa`,
before `pred/02` (`1fc0e15`). This is the defect that withdrew sessions 100 and 101's numbers
(«спроси, ЗАПИШИ, потом мерь»), committed a third time. **Under the premise ROADMAP does record, the
only lower-bound arm is V1, and L − 1 = +2.08 % ≤ 6 %: M5 does not close G.** Under the unrecorded
tier, CLOSE-machinery — which `pred/02` §3 itself makes reopenable by the user.

## 2. Defect B (FATAL to "the price of BDA") — V2 does more than the seals disclose

1. **Every V2 pixel-shader module gains a store** (1–2 `STG` to the fault buffer, `EmitBdaFaultFlush`
   → `RecordBdaFault`, `spirvEmitterMemory.cpp` ~1784-1791); A, V1 and V2s have none. Six of the seven
   PS items contain `OpKill` and do not declare `EarlyFragmentTests` (`spirvEmitterModule.cpp`
   ~814-818). A fragment shader with side effects must behave as if depth tests run after shading, so
   V2 PS pipelines plausibly lose early depth rejection — **a fixed-function cost, not a load cost,
   and invisible to V2s** (which has no store). Upper bound of its effect: 1 789 of the 2 503 µs by which
   V2 exceeds V2s (71 %); attributing all PS excess to it gives X′ ≈ 1.16–1.20, Y′ ≈ 1.09–1.15.
2. **Each page lookup reads two table entries** (the page entry and entry 0, the null base), keeps a
   private fault-page load/select/store, and checks the index twice; with no `NonWritable`/`Restrict`
   decoration the CS variants reload entry 0 after every store (SASS `LDG.E.64 [RZ.U32+URx]`: S7 26,
   S6 38, S1 123). `pred/02` named "a page-table `LDG.E.64` per group" only.
3. The `LDG.E.STRONG.SM` cause stated in `pred/02` (a memory-model property of the pointer loads) is
   not established; the fault store of item 1 is the only store in those modules and is a candidate.
With the PS confounds and S7 set aside, Y″ ≈ 1.03. **So the machinery was not fully named, and the true
shader-side price of G is shown neither above nor below 6 %.**

## 3. Further defects, none moving a number

* **V2 reads different bytes than A on two items** — S8 by 746 B on a repeatable item, S1 by 4.15 MB
  with a fault bit set (null-page reads); V-e compares only each item's LAST event. Cause undiagnosed.
* **S1's V2 still runs inside the all-at-once V2 arm** although excluded from the sums; S4 renders into
  a texture S1 writes. Events before S1's first dispatch alone give X 1.54.
* **Per-event GPU durations are not additive** (30–54 % of PS event readings are exactly 0; non-item
  time falls when items are replaced); whole-frame X ≈ 1.387, L ≈ 1.010, V2s/A ≈ 1.028.
* **Carry-over is not balanced** by the five-arm design (measured order effects ≤ ~1 %); GPU clocks were
  not locked (SM 1 537–2 640 MHz; round 2 an outlier absorbed by the median).
* **pred/07 misdescribes the retry:** `KYTY_RECORD_THREAD=0` was overridden at frame 1 by
  `recordthread=1` in `gates_base.txt`; the retry ran with the record thread ON (off only for the
  captured flips, as `RecordThreadWanted` does). It succeeded because the start-up race did not recur;
  the crash at `commandRecorder.cpp:326` is undiagnosed. The capture content is unaffected.
* **The retry of an entry and of the capture:** the brief says "no warmup, no retry"; both retries
  were technical (an entry hang, a start-up crash) under clauses sealed before them, but addendum 06
  was written after the hang was seen and is disclosed as such.
* **Order:** the code change was built and the two candidate runs taken BEFORE the M5 capture, against
  the brief's "measure first and patch after"; the GPU replay ratios do not depend on it.
* **P2 MISSED** (X − 1 = 0.420 outside [0.02, 0.20]); P1, P3, P4 HIT.

## 4. What may be published

"M5 was measured. Today's emitter's BDA path costs +42 % (X) and +33 % at equal granularity (Y) on the
ten top shaders; the unavoidable const-bank → global-load component alone costs +2.1 % (L). Because the
variant carries unpriced machinery — a PS fault-buffer store that likely disables early depth testing,
doubled page-table reads — and because the tiered rule was not recorded in ROADMAP first, **M5 does not
close G**. A G prototype would first have to rebuild the BDA path; whether G's intrinsic GPU price
exceeds 6 % is not shown. G stays alive and unlicensed; the decision is the user's."
