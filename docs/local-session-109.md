# Session 109 — the family skip closed for good; knob `cspfree` (the walker's compute prefetch without the lock on a (source, specialization) hit) verifies clean and shortens the mean frame by 154 µs, but its count guard fails (dispatch waits 12 vs 3) — not shipped

**Single source of truth for session 109.** Mirrored into git as `docs/local-session-109.md`. Harness root
`C:/kyty/s109`. Everything below is measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=0`: median
of block means `dt_us` ≈ 31.0 ms (≈ 0.54× game speed). **No speedup shipped this session.** 60 FPS is not promised.

---

## 1. Result

1. **Port** `C:/kyty/s108/s109_port.py` (`14be3f9c…`, 1 674 lines, modelled on `s108_port.py`): `PORT DIAGNOSTIC:
   clean; carried=8832 ledger=69 skipped=1726`; 52 sealed texts (50 in `prev108/pred`), all hashes checked;
   `gates_base.txt` `303a7849…`; `gates.cpp` 138 entries, ABSENT 39 at port time.
2. **`cspfam` v2** (record `bd52f86`, code `bc7d66f`, build `e90f5543…`): a process-wide count of compute-pipeline
   creations (`g_compute_creations`, bumped at the three `m_compute_pipelines` insertions) joins the family table's
   stamps; counter `cspfam_clr`. **`ent109`** (sealed `pred/01_ent109.md` `e2627de0…`, 8 entries A B B A A B B A into
   Sky Garden, compute precache off, 150 s each, pinned, ADMITTED): **FAIL — S_A 12, S_B 34** (A 2/2/4/4, B 9/7/9/9;
   B mostly `cs_sync_new`), ~150 table clears per B entry. **The prefetch skip per shader FAMILY is closed (v1 and
   v2):** the family does not determine the permutation, and a K = 4 streak builds inside one walk before a new
   permutation arrives. Record `600ca26`.
3. **Design** (Plan agent, `design109.md`): tag 2 first via a (source, specialization) memo — the exact permutation
   predicate — then tag 1 via per-slot synchronisation of the M1 table (`daslot`; a coarse `ahead_table_mutex` rejected
   by estimate). Record `20e7b31`.
4. **`cspfree`** (code `5770106`, build **`2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77`**,
   installed, default 0): per-thread memo `ProgramKey` → source entry (recorded under `m_mutex` only with a published
   compiled SRT) → "specialization → id with a pipeline"; `MaterializeResources` runs unlocked; hit (1) returns
   before the lock; (2) verifies (`cspfree_bad` at equal specializations, `cspfree_moved` otherwise). Nine counters
   `cspfree_*`. Nothing under `src/graphics/shader/**`; gate order clean.
5. **`vfy109`** (sealed `pred/01b_vfy109.md` `f626da41…`, 300 s, `cspfree=2`, precache off, pinned, ADMITTED): **GO** —
   `cspfree_bad` 0, `cspfree_moved` 0, `mat_fail` 0, hit rate 1.0000 over 2.06 M steady lookups; `cspf_new` 76, `cs_sync`
   1 + 2.
6. **`ent109b`** (sealed `pred/02_ent109b.md` `bf8adcd1…`, 8 entries A B B A A B B A, `cspfree=0|1`, precache off,
   pinned, ADMITTED): **FAIL — S_A 7, S_B 17** (A 3/2/1/1, B 3/5/3/6): synchronous compiles A 4 / B 5, waits for a
   still-compiling pipeline A 3 / B 12; `cspf_new` 74–77 in both arms (`cspfree` skips no new permutation, as designed);
   events at load and after it, in both arms (the excess splits evenly: B 6 at load / 6 after, A 2 / 1 — audit).
   **Not shipped by the seal; `frf109` (`pred/03`) not run.** Weakly significant (one-sided p 0.032 binomial, 0.043 by
   permutation over entries). Hypothesis [I], supported by the audit: without the contention GuestGpu reaches
   dispatches whose async compiles are still running sooner — after load, a flip where the walker queued a new
   pipeline has a wait in 6/14 cases in B against 1/17 in A (p 0.021); new-pipeline flips cost about the same in both
   arms (13.2 vs 15.3 ms extra), so the count does not show a duration penalty. Predictions: pred/01 E1 HIT, **E2
   MISS**, E3 E4 HIT; pred/01b V1–V5 HIT; pred/02 E1 HIT, **E2 MISS**, E3 E4 HIT.
7. **`frm109`** (sealed `pred/04_frm109.md` `50fbc61b…` — a MEASUREMENT recorded in ROADMAP item 7 after `ent109b`'s
   FAIL, nothing ships under any outcome; 600 s, pinned, 96 pairs, ADMITTED): **Δ mean `dt` −154.1 µs (2·SE 121.2,
   t −2.54)** — the bar would be met; Δ`cpu_net` −54.8 (t −0.98); `cspfree_hit` 266/266 a flip, `cspf_have` 0 (the
   prefetch never takes the lock); `da_walk_us` −36.1; **`gpu_busy_us` +70.6 µs (t 4.63), reproducing `fam108`'s +87.5
   — identified by the audit [I]: ~2 more buffer uploads a flip land inside render passes and split them (the only
   moving close reason; `sync_up_kb` +252 KiB; `nvidia-smi` +0.5 pp utilisation, +0.2 W)**. Robustness: sign-flip p
   0.012, bootstrap 95 % [−270, −36], paired median −16, dropping the 5 most negative pairs −94; the gain is
   one-vblank flips 13.11 → 14.26 %. Predictions of pred/04 (scored by the audit — `frm109.py` printed pred/03's
   G1–G6): M1 M2 M3 HIT, **M4 MISS** (Δ`da_walk_us` −36.1 against ≤ −100). Removing tag 2's hold is worth ≈ −150 µs by
   two different mechanisms.

## 2. Harness

`C:/kyty/s109`: `ent109.py`/`test_ent109.py` (37 fixtures, 23 mutants killed), `vfy109.py`/`test_vfy109.py` (33 / 22),
`ent109b.py` (`make_ent109b.py` from `ent109.py`; 38 / 24), `frf109.py` (`make_frf109.py` from `fam108.py`; 131 fixtures
incl. the two session-108 audit survivors, 110 mutants killed), `frm109.py` (`make_frm109.py`: `frf109.py` + seal 04
+ tag pattern), `go109.sh`, `go109b.sh`, `go109c.sh` (each holds `C:/kyty/SEALED_RUN.lock`), `gates_free{0,1,2}.txt`,
`design109.md`, scored-build copies `kyty_emulator_e90f5543.exe`, `kyty_emulator_2f593229.exe`, `kyty_emulator_379777bb.exe`
(in s108).

## 3. Source, builds, provenance

Commits: `60bf3d9` (session 108 close), `bd52f86` (records), `bc7d66f` (v2), `06ce534` (seal 01), `600ca26` (ent109
FAIL), `20e7b31` (cspfree record + design), `5770106` (cspfree), `1c6eb38` (seals 01b/02/03), `ee686cc` (results +
seal 04), the session commit. Builds: `e90f5543…` (v2; `ent109`), `2f593229…` (cspfree, default 0; installed; `vfy109`,
`ent109b`, `frm109`). Labels end `-dirty` (the `nlohmann_json` submodule's deleted PNGs only); not bit-reproducible.
No push. No video owed: no default changed.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `ent109_1..8` | cspfam=0/4 (v2), entries ABBA, precache off | FAIL S_A 12 / S_B 34 ⇒ family skip closed |
| `vfy109` | cspfree=2 verify, 300 s, precache off | GO: bad 0, hit rate 1.0000 |
| `ent109b_1..8` | cspfree=0/1, entries ABBA, precache off | FAIL S_A 7 / S_B 17 (waits 3 / 12) ⇒ not shipped |
| `frm109` | cspfree=0/1 frame-time ABBA, measurement | Δ`dt` −154.1 (2·SE 121.2); `gpu_busy` +70.6 |

## 5. Next

`cspfree` is correct (verify GO) and worth ≈ −150 µs, but its guard counts stall EVENTS and fails on waits. Session
110: counters of stall DURATION on the dispatch (`cs_sync_new_us`, `cs_sync_wait_us`), a powered guard by duration
(entries ABBA, rule recorded before), then a ship ABBA with video if it passes. In parallel: `daslot` (tag 1) code.
Plan: `docs/next-session-110.md`.

## 6. Proved, and not proved

**Measured.** The family skip lets through 34 vs 12 dispatch-time stalls with the compute precache off (v2) — closed.
`cspfree` agrees with the locked path on 2.06 M lookups (0 bad) and removes every prefetch acquisition of `m_mutex`;
with the precache off it shows 17 vs 7 stall events (mostly waits); at the pin it shortens the mean frame by 154 µs.
`gpu_busy_us` rises ~70–90 µs whenever the prefetch lock hold disappears. **Not measured.** Stall durations; the gain
without the pin; the size of the mid-pass upload effect in CPU time. **Not proved.** Any shipped speedup (none); 60 FPS.

## 7. Adversarial audit

One agent, three lenses, sealed as `pred/05_audit109.md` (`fd27a2f8…`). **Recount CONFIRMED** (every number of
`ent109`, `vfy109`, `ent109b`, `frm109` reproduced by own parsers). **Protocol HOLDS, with defects** (records before
actions, seals before runs, hashes, pin in all 18 runs, no writes inside sealed windows). **Code NOT REFUTED** (no
first-contact hole, no wrong id; unlocked materialization touches only immutable-after-publish plan data and
thread-local state). Findings: (1) **MAJOR** — pred/04's M1–M4 were never scored (the scorer printed pred/03's G1–G6);
M4 MISS; pred/01 and pred/02 E2 MISS — corrected above and in ROADMAP; (2) **MAJOR** — `ent109b` FAIL weakly
significant, harm not shown, hypothesis supported (6/14 vs 1/17) — corrected above; (3) **MAJOR** — the `gpu_busy`
rise is ~2 extra mid-pass buffer uploads a flip (render-pass splits) — recorded; (4) MINOR — pred/04 and its ROADMAP
record share a commit; shipping `cspfree` needs a fresh sealed ABBA; 10 of 30 new mutants survive (no verdict
changes); code debts (skip after retirement, "moved" on null source, raw pointers in a thread-local memo). Report:
`C:/kyty/s109/audit109/AUDIT109.md`.
