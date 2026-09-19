# Session 99 addendum04 — direct GC preservation audit for the settled experiment

SEALED on 2026-09-19 after tests and before new game data on this binary. The user requires completion
in this session and authorises necessary launches. Pred01/02/03 and their old results remain
immutable. eng99a3 stays NOT_MEASUREMENT because its required R6' was52>50, despite matched
dt0.2093% and work0.2422%. It is never re-admitted or used as a frozen source by this addendum.

## 1. Cause investigated before this change

The fixed ImageLife diagnostic life99a survived300.1s and captured all64121 events from startup:
32652 creates/31469 frees; the59-create difference from summed img_new is exactly55 before
the first reported row plus4 after the last. No free of ANY reason occurred in armed interiors.
One GC free at an ambiguous rising boundary was not a predecessor of a recovery candidate.

Recovery insertions are mainly newly observed BC5/BC4 texture signatures and signatures whose
prior GC retirement happened in the base arm BEFORE the current floor. In one explicitly
reported snapshot alignment,311 new signatures and181 prior-GC candidates occurred, versus
24/30 in the fixed controls; the nominal alignment gives the same qualitative finding. All
three alignments and identity ambiguities are retained in r6_raw/life_analysis. No claim of
universal content/identity correctness follows from printed signatures.

Source correction: GC's printed reason is operator():3402 (a lambda's __func__), not literal
RunGarbageCollector. img_new counts InsertImage, including non-GC insertions and reused
backing. Recycle backing may expire after2 seconds but that changes allocation price, not
the number of insertions. Neither keeping the pool nor deleting legitimate alias handling
is a justified fix for the number52.

Thus R6/R6' total-insertion caps are overbroad PROXIES for the old bug (live cache eviction
or aging while the binding floor suppresses touches). Replace those image-only proxies
for FUTURE data with a direct audit of that mechanism. This is an explicit change of control,
not raising50 to52, claiming the old rule passed, or proving every cache mechanism correct.

## 2. New additive observer; GC policy unchanged

New binary SHA25634206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f,
23743488 bytes. Required environment KYTY_BIND_FLOOR_GC_AUDIT=1,
plus all pred02 settings including CPUobserver1. New fields print including zero:

* bf_igc_checks: every observed TextureCache GC invocation, including early returns.
* bf_igc_hold: observed expected noncritical clock pauses, including below-trigger calls.
* bf_igc_bad: wrong/backward age-clock delta or a counted-armed CURRENT submission while
  the main hold helper reports false.
* bf_igc_critical: a critical override while expected held, after the original memory refresh
  and original usage>=trigger/usage>=critical checks. This is not a claim about all memory pressure.
* bf_igc_evict: root GC victims while expected held, including critical overrides. Any recursive
  stencil deletion has a counted root; children need not be double-counted.

The clock advances per GC CALL, not per presentation or guest frame. The oracle's expected
delta is0 iff expected_hold && !critical, otherwise1; it covers each early-return and normal
path exactly once and catches release catch-up. It does not change the actual update.
Expected hold is the existing helper OR the independently stored current submission's
sticky_armed_counted bit. The new getter only reads an active slice; it does not adopt a latch
or read stale CurrentOp TLS. This independently checks a SUBSET of hold states, not the full
base/pending implementation; that limitation is explicit. The source implementation of those
other states and the existing full-log latch controls remain reviewed, not re-proved by this bit.

Default0 leaves observation off. GC collections, critical overrides, aliases and recycle policy
are unmodified. The five counter updates are observable overhead, not secretly subtracted.

## 3. Deciding and reported controls on new data

All pred02 selection, CPU-burn endpoint, strict work<0.5%, C5<=2%, area<1%/matching>=90%,
C9<=3%, full-log completeness/provenance/failure markers, frame integrity, and buffer R7/R7'
stay unchanged. The numeric limits of these checks are not widened.

Image R6 and R6' keep their original calculations and original PASS/FAIL in a separate
reported_image_birth_proxies section with full text. They no longer decide FUTURE admission.
The new deciding image-cache audit requires:
  all five fields present on every report row, all nonnegative;
  bf_igc_checks>0 over the log;
  each retained armed block has bf_igc_hold>0;
  bf_igc_bad=bf_igc_critical=bf_igc_evict=0 over the ENTIRE raw log.
The runtime log must contain BindFloorGcAudit: mode1. Unsupported critical-floor pressure
invalidates the instrument; the observer must never disable its safety override.

The audit detects the previously diagnosed mechanisms even if insertion count is small.
Tests must show a broken frozen clock or held eviction fails with births<50, and show a
high birth count can pass only when direct invariants and every other control pass, while
its old R6/R6' FAIL remains visible. This is targeted mechanism coverage, not an identity-
complete proof of all resource correctness. Video and recovery observations remain mandatory.

## 4. Fresh campaign on the new observer

Same directory/session99. Fresh reset pilots eng99a4 and eng99c1 use17800us as an OPEN
engineering prior from the already observed dt tuning, not a carried accepted freeze.
They have no source JSON. Allowed follow-ups a5/a6 and c2/c3 use the same pred02 TUNE/source
chain; at most three settings in each new branch before causal reassessment. Old a1/a2/a3
are rejected as identities by the new scorer and cannot be replayed into acceptance.

Pilots are one300s process, no warmup/video, requiring the same minimum8 falls/10 pairs.
The freeze target remains1% with settled work/area passing. New clock audit and all other
technical controls must pass. Do not tune burn for a work-only failure. No B for pilots.

Fresh bf99e(a) and bf99f(c) each run900s with fixed LOCK provenance from a NEW pilot on this
binary/rule, requiring>=30 falls and>=30 paired blocks. Record>=3000 video frames on bf99e.
All p90/start1800/idx60..88/complete balanced quartets and no-repair-of-confirmation rules
from pred02 remain. Source tag/hash env, raw replay, exclusive artifacts and entry-only
retry suffix rules remain unchanged. Only the new scorer settled99_gc.py is used here.

Both CPU B values and their wall readouts complete the requested bindings-only experiment.
No global G/R1 licence,60 FPS promise or universal architecture impossibility follows.
Failure still triggers causal work under the user's authorisation, not an automatic end of
the task. No unseen safety/control failure is waived by the desire to finish.

## 5. Predictions and validation before new data

P1: direct held-age/eviction checks pass, based on source and zero armed-interior frees in
the separate diagnostic. P2: old birth proxy may exceed50 again; its outcome is not selected.
P3:17800 is close enough to begin a new independent engineering calibration, not guaranteed
to LOCK. P4: the confirmed settled work remains comparable; this is tested, not assumed.

Before sealing: build_local.cmd PASS; source audit passed independently
(verify_gc99_cpp/VERIFY.md,38 model cases including10 detected mutants; no gameplay).
The new scorer's initial21 tests passed, including old image-proxy FAIL retained with direct
audit pass, and direct-clock/eviction failure with low birth counts. Final pin/VERIFY follow
before gameplay. This file must not be edited after sealing; a correction needs a new addendum.
