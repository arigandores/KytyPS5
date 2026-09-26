# Session 121 — the R1 prototype: knob `texmemo8` (8-way texture memo with verify and positive-control modes)

Lead's synthesis of `texmemo8.md` (design) and `texmemo8_review.md` (adversarial review, SOUND_WITH_CHANGES), written
before any code. Both in `C:/kyty/s121/design/` (git `docs/session-121/design/`). **The instrument = the design with
every REQUIRED change RC1–RC8 of the review and the recommendations adopted below; where this file differs, it wins.**

## 1. Decisions

1. **Knob, not gate:** `texmemo8` (`KYTY_TEX_MEMO8`, 0..3, default 0; `Knob::TexMemo8` LAST, after `R2Census`; row after
   `r2cen`; `check_gate_order.py` before the build). 0 = today's direct memo; 1 = 512 sets × 8 ways of the same 4 096
   `Texture` entries (`memo_index = set·8 + way`, set = `memo_hash & 511`), compact 32-bit tags + LRU stamps in one
   64-B line per set, the full hit proof unchanged; 2 = 1 + VERIFY; 3 = 2 + a POSITIVE CONTROL (value 3 is the
   designer's addition, **accepted here**: it proves in the running game that the verify counter can fire; nothing in
   the memo is corrupted).
2. **Layout switch** by the stored `texture_mode`: a change between 0 and non-zero invalidates every entry (`valid =
   false`, `version++`, `fast_view = nullptr`, ways empty) — both ABBA arms pay the same cold start at block positions
   0–2, outside the window. `texmemo2` takes precedence (counted); `r1cen`/`r2cen` forced off under `texmemo8 ≠ 0`.
3. **Verify (2, 3):** the miss path `descriptors.cpp:2094-2252` moves verbatim into a local lambda `resolve_full`
   (**force-inlined**, RC7); every GAINED hit (decided by a direct-table shadow, exact or towards more checking; RC5: a
   key the direct shadow holds under a different image id is DROPPED, counted `tm8_directdiff`) runs the fresh full
   resolution and compares store / image id / `R1DescDigest`; a 1/64 xorshift sample (RC3) covers other hits; on any
   disagreement the fresh answer is stored and returned; after the fresh resolution the cached image is re-looked-up
   and re-checked (`registered`, `!needs_rebind`: `tm8_relive`, RC6 — the reason: `FindImage` can free an image).
   RC2: the real verdict is decided first; an injected lookup never refills; `tm8_inject_miss` counts injections that
   failed to fire. RC4: the `RebindImages` check is a PLACEMENT check (recompute the slot's hash; the index must belong
   to its set under the current layout, tag matching), with a wrong-set injection at 3.
4. **Counters** (`tm8_*`, raw, `micros = false`, adjacent in the enum, plus `Tm8Stale`): at 1 (the timed arm) only rare
   paths count (fills, evictions, evicted views, invalidations); per-lookup counters and the sampled probe timer only at
   2/3 (never timed). Arming in the timed run from counters both arms pay: `tex_hits` ≈ +1 190 a frame, key misses
   ≈ −1 190, `texfast_rec` down.
5. **Identities (RC1, RC8):** close-in-enum pairs ±8 per block window; far-apart pairs relative, ≤ max(64, 1 ‰ of the
   window sum); ratio bands for identities 17/23; identity 1's bound `+ tm8_vctl_bad`; S4's upper edge = the M arm's own
   key misses.
6. **Adopted recommendations:** skip the LRU write when the way is already the most recent; the 512 set lines inline in
   the memo struct (no vector); a counter that the verify's extra DCC adoption changes nothing where the hit path would
   have skipped it; risk 1 widened (the probe's dependent load may cost 2–4 ns a lookup, ≤ ≈ 185 µs a frame — the
   ABBA prices it).

## 2. Runs and rules

- **Unsealed smoke `smk121`** (disclosed): Sky Garden, 4 arms `texmemo8=2|1|0|3` with `texfastcheck=1`, `KYTY_REC`
  video; PASS = 0 `tm8_bad`/`tm8_*_bad` (value 2), the positive control fires at 3, arming counters as predicted, the
  video without one-frame glitches (`s51_vidglitch.py`).
- **Sealed run `shp121`**: Sky Garden, 300 s, pinned, `KYTY_GATE_SCHEDULE=90+1800:texmemo8=1|texmemo8=0`, ABBA, all
  censuses 0, window 10–88; scorer `shp121.py` (+ `vfy121.py` for the smoke), fixtures S1–S15 + the review's, mutants,
  `mutlib` v4.1 FULL, pre-seal check agent.
- **Rule (ROADMAP s121 item 1):** SHIP (`texmemo8` default → 1) only if Δ`dt_us` (P − M) + 2SE < 0, the smoke's verify
  PASS and a clean video; else the track closes with its measured number. Prediction [I] −350 µs (−250…−500) against
  `texmemo8=0` of the SAME build; power 79–95 % at 0.25 ms.
