# Session 107 — the walker holds `PipelineCache::m_mutex` behind 98.6 % of GuestGpu's contended wall; `cspmemo` closed (VERIFY FAIL); `dabatch=2` worse (+281 µs) — no speedup

**Single source of truth for session 107.** Mirrored into git as `docs/local-session-107.md`.
Harness root `C:/kyty/s107`. Everything below is measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned, with `dabatch=8` (session 106): median of block means `dt_us` ≈ 31.0–31.6
ms in this session's runs (`obs107` window mean 31 620 µs), game speed ≈ 0.53×. **No speedup this session.**

---

## 1. Result

1. **Instrument (source `a25c453`, build `dd567a0f…`, decision recorded before code `a74ef62`):** under gate
   `plkstat` GuestGpu's three `m_mutex` sites try the lock first and, on failure, record the wall and the thread
   CPU around the blocking `Lock` and the holder tag the tagged holders publish (1 walker `QueueDrawAhead`, 2 walker
   `PrefetchComputePipeline`, 3 compute compile completion); the walker's own holds are timed after its
   `LockGuard`. Knob **`cspmemo`** (default 0; 1 shadow, 2 skip, 3 skip + verify): a per-thread memo that would skip
   the walker's compute prefetch.
2. **`obs107`** (sealed `pred/01_obs107.md` `85a65121…`, 300 s, pinned, `plkstat=1 cspmemo=3`, 7 842 rows,
   ADMITTED): **VERIFY FAIL ⇒ `cspmemo` closed by the seal** — `cspm_bad` = 2 (shader `632642f4…` alternates
   permutations 79/82 under the same key; both already had pipelines, so the miss is harmless, but the rule does
   not forgive it); `would_rate` 0.438 < 0.5 (NO-GO in any case). **Measured for the first time:** the holder
   behind GuestGpu's contended wall is the walker thread in **98.6 %** (tag 1 `QueueDrawAhead` 57.7 %, tag 2
   `PrefetchComputePipeline` 40.9 %, untagged 1.4 %; scoped to the three instrumented sites, holder named at the first
   failed try; the tag split is not robust — removing the instrument's per-acquisition cost moves it to ~51/48 or
   45/55, the walker share up to ~99.7 %); contended wall 422 µs a flip over 321 contended acquisitions;
   walker holds `QueueDrawAhead` 1 021 µs a flip (1 080 × 0.95 µs), prefetch 342 µs (266 × 1.29 µs); **`cspf_have`
   266/266, `cspf_new` 0 — in the steady scene every compute prefetch finds its pipeline already built.**
   **Spin share ≥ 0.75, likely ≈ 1 (corrected by the audit, §7 item 1):** the two `QueryThreadCycleTime` calls on
   each contended acquisition add two costs to the wall but about one to the CPU numerator, pulling the share
   toward 0.5, so 0.75 is a LOWER bound (per-call cost ≤ 0.33 µs; for 0.2–0.33 µs the true share is 0.86–1.0). The
   session's first text ("biased upward, not a measurement") was wrong. This run's `pl_*_wait` are inflated by the
   instrument and not comparable with `gw106`. Memo: 2 disagreements in ~0.91 M hits (2.09 M lookups).
   Predictions O1 O2 O4 HIT; O3 O5 O6 MISS.
3. **`dab107`** (sealed `pred/02_dabatch2.md` `3a0d4043…`, ABBA `dabatch=8|2`, 600 s, pinned, 92 pairs, ADMITTED):
   **KEEP 8 — `dabatch=2` is worse: Δ mean `dt` +281.0 µs (2·SE 176.3, t +3.19), Δ`cpu_net` +280.4 (t +3.42)**;
   paired Δ walker `da_walk_us` +712.4, `da_queue_us` +630.3; `da_miss` +16.8 (t 3.1). B1–B5 MISS, B6 HIT. Of three
   tested values (64, 8, 2) 8 is best; smaller batches do not help in this direction. GuestGpu's on-CPU time rises
   (off-CPU part unchanged, Δ(dt − cpu_net) +0.6 ± 44; CPU per draw +0.9 %, t 3.95) — which includes the
   critical-section spin and self-materialisation on the extra M1 misses [I]; the effect is 0.5 fewer 1-vblank
   frames per block.

## 2. Harness

`C:/kyty/s107`, ported by a fresh `C:/kyty/s106/s107_port.py` (sha256 `03a05591…`): `PRECONDITIONS PASS: 5 root
constructs; 47 sealed texts (45 land in prev106/pred, 2 stay in carried prev103/pred and prev100/pred); 33 live
paths (22 files) + 10 expression paths (8 files); gates 1092 B / 99 names (sha 303a7849..., dawalk=1, no dabatch,
no ctxtick, no cspmemo); gates.cpp 137 entries (111 gates + 26 knobs; dabatch default 8; cspmemo last knob row,
default 0); ABSENT 38` → `PORT DIAGNOSTIC: clean; carried=6488 ledger=64 skipped=15` (the porter adapted the counts
to the `cspmemo` knob committed while it worked). New: `obs107.py` + `test_obs107.py` (nine fixtures, every
verdict branch in NON-draft mode, re-run on the sealed copy; the audit's mutants show not every TERM had its own
failing fixture), `dab107.py` + `make_dab107.py` + `test_dab107.py` (five
fixtures in NON-draft mode with full protocol metadata: SHIP, SHIP_PENDING_VIDEO, KEEP by the bar, KEEP by a failed
video, KEEP by the arming; re-run on the sealed copy), `gates_obs.txt`, `gates_dab2.txt`, `go107.sh`, `go107b.sh`.

## 3. Source, builds, provenance

Commits: `d7bd482` (session 106 close), `a74ef62` (records before action), `a25c453` (instrument + knob),
`e64fb42` (record: one merged observation run), `eedff9d` (seal 01 + scorer + port), `ba0d59c` (obs107 result +
candidate record), `1e1e4ac` (seal 02 + scorer), `083a73d` (dab107 result), the session commit. Build `dd567a0f…`
(installed): default behaviour = `2b30f836…` plus dark counters (`plkstat` off ⇒ plain `Lock`; `cspmemo=0` ⇒ no
memo; the prefetch adds two `Add`s, `QueueDrawAhead` one gate read). Nothing under `src/graphics/shader/**`;
`check_gate_order.py` clean (Knob 26/26). No push. No video pass owed: no change reaches the renderer.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `obs107` | observation `plkstat=1 cspmemo=3`, 300 s | ADMITTED; VERIFY FAIL (`cspm_bad` 2) ⇒ `cspmemo` closed; holder = walker 98.6 % |
| `dab107` | ABBA `dabatch=8|2`, 600 s | ADMITTED; KEEP 8 (Δ`dt` +281.0) |

## 5. Next

The contention is not tuned away by the batch knob. Since the spin share is ≥ 0.75 (likely ≈ 1), GuestGpu's
~420 µs a flip of contended wall is mostly its own CPU — a real lever. The steady-state compute prefetch is pure
lock holding (`cspf_new` 0): a code candidate skips the walker's prefetch per shader FAMILY (code hash + stage static
key, no user SGPRs) once the family has only ever found built pipelines and the programs epoch has not moved,
with a counter of dispatch-time synchronous compute compiles as the safety readout. (The session's first draft of
this section proposed `dapin=3` as "never shipped"; it is the default since session 82 — audit §7 item 2.) Then
M3.2. Plan: `docs/next-session-108.md`.

## 6. Proved, and not proved

**Measured.** At the three instrumented sites the walker is the holder behind 98.6 % of GuestGpu's contended wall
at `m_mutex`; the spin share of those waits is ≥ 0.75 (a lower bound); the steady-state compute prefetch always finds
its pipeline; the memo keyed on user SGPRs disagrees twice in ~0.91 M hits and hits 44 %; `dabatch=2` lengthens the
mean frame by 281 µs. **Not measured.** The exact spin share; the tag-1/tag-2 split net of the instrument; why more
walker acquisitions raise GuestGpu's CPU. **Not proved.** Any speedup this session; 60 FPS.

## 7. Adversarial audit

One agent, three lenses, sealed as `pred/03_audit107.md` (4 542 B, `7b6a6531…`). **Recount CONFIRMED** (every
number reproduced by own code; `dab107` paired median +534, 65/92 pairs positive). **Protocol HOLDS** (records before
actions, seals before runs, hashes match, the heartbeat only rescheduled during sealed runs, fixtures pass). **Code
NOT REFUTED** (defaults unchanged; recursive lock + `TryLock` handled; no crash/deadlock path). Findings:

1. **MAJOR:** the spin-share bias runs downward (0.75 is a lower bound, likely ≈ 1) — §1 item 2 and §6 corrected.
2. **MAJOR:** `dapin=3` is the default since session 82 — §5 and `next-session-108.md` rewritten.
3. "98.6 %" scoped (three sites, first failed try; ~99.7 % net of the instrument); `GetComputePipeline` locks the
   mutex un-instrumented. 4. The 57.7/40.9 split is not robust (~51/48 or 45/55 net). 5. `dabatch=2` "own CPU"
   qualified (spin, extra M1 misses; not independent of Δ`dt`); "knob exhausted" softened to three values.
6. ~0.91 M hits, not ~2 M comparisons. 7. Paired Δ +712.4 / +630.3. 8. Fixtures walk every branch but not every term
   (mutants with S2 or the pin/record-thread checks disabled survive) → rule: each decision and admission term gets
   a fixture where only it fails. 9. `tag2_us` carries ~40–52 µs of instrument cost; no decision affected.
