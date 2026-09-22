# Sealed addendum 05 to pred/03 — session 102, knob `dabatch`: three defects of the text, fixed BEFORE any run

**Immutable once written.** `pred/03_dabatch.md` (6 909 B, `f828e257…`) is NOT edited. Found while
writing and testing its scorer on the session-101 logs, before the binary `346ba4f6…` was installed
or run. No limit is widened beyond what session 101 itself applied; one definition is replaced by
session 101's own, one tolerance is replaced by a bound that follows from how the walk flushes.

## 1. The work-split control is replaced by session 101's own definition

pred/03 §4: *"work split |median `draws` 8/1024 arm ÷ 64 arm − 1| ≤ 0.5 %"*. On the three
session-101 runs, whose arms do not change the work at all, the block-median reading fails `cm101a`
(+0.509 %) and the row-median reading fails `cm101c` (−0.640 %) and `cm101d` (−0.594 %): the rule as
written would declare an honest pilot INVALID by chance. Session 101 used a different definition and
the same limit (`cen100.py` `population`, carried by `cm101.py:296`): **work = mean of `draws` over
all retained rows of the non-default arm ÷ the same mean of the 64 arm − 1, strict |work| < 0.5 %.**
That definition replaces pred/03's; the limit is unchanged.

## 2. The arming tolerance at B = 1024 had no margin

pred/03 §4 compared the observed call ratio with `(W + R/B)/Q64` within ±25 %. A walk flushes
`ceil(r/B)` times plus the final flush, not `r/B`; with ≈ 5 walks of ≈ 1 690 requests each, B = 1024
gives ≈ 10 calls against a "prediction" of ≈ 13.2, −24.5 % — a coin toss for a knob that works.
**Replaced by bounds that hold for any split of R into W walks:** each arm's median `da_qcall` must lie
in `[0.75 · R/B, 1.25 · (W + R/B)]`, with `W` and `R` the 64 arm's medians and B the arm's batch
(64, 8 or 1024). The session-101 values give [99, 172] at 64, [795, 1 331] at 8 and [6.2, 16.5] at
1 024.

## 3. `da_qcall` lives on `FrameTrace-x`

pred/03 §1 says FrameTrace-draw; the build prints it on `FrameTrace-x` (`videoOut.cpp:2426`). The
scorer reads it there and fails the run if it appears on any other line. No number changes.

## 4. Unchanged

Everything else in pred/03: the arms, the population, `b̂`, `Ŝ`, the 60 µs decision, the ship rule,
the bands, the protocol, the predictions and what must not be claimed.
