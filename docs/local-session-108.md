# Session 108 — `cspfam=4` shortened the mean frame by 141.8 µs at the pin and shipped, then the powered safety guard failed its rule (6 vs 3 + 2 dispatch-time compiles) and the default was rolled back to 0 — no speedup kept

**Single source of truth for session 108.** Mirrored into git as `docs/local-session-108.md` (it replaces the WIP
file of the pause; that file's §1 and §3 are carried over below). Harness root `C:/kyty/s108`. Everything below is
measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3` (`cspfam=0` again):
median of block means `dt_us` ≈ 31.0 ms (`fam108` arm 0 31 038.6, arm 1 31 031.4), game speed ≈ 0.54×. GuestGpu's
contended wall at `PipelineCache::m_mutex` was ≈ 420 µs a flip (`obs107`), holder the walker (~99 %); its compute
prefetch held the lock 342 µs a flip for nothing (`cspf_have` 266/266). 60 FPS is not promised.

---

## 1. Result

1. **Pause and resumption.** Session 108 was paused by the user on 2026-09-23 after the code (`f9e19f7`) and before
   the port, the seal and the run (WIP documentation `72d5fa2`); resumed the same day under the user's standing
   loop instruction (sessions in a row until "stop", no questions, continue after usage limits reset). Record:
   ROADMAP §0.1 "СЕССИЯ 108" item 4.
2. **Code** (`f9e19f7`, patch `docs/session-108/tools/patch_s108.py`; record before code `3cc53a2`): knob **`cspfam`**
   (`KYTY_CS_PREFETCH_FAMILY`, LAST knob row, range 0..1024, the value is K = the streak): in
   `PipelineCache::PrefetchComputePipeline` a per-thread table keyed on the shader FAMILY (code hash and base + the
   stage static key from `BuildStageStaticKey`, no user SGPRs) counts consecutive locked prefetches that found a
   built pipeline; at a streak ≥ K the call returns before `PipelineCache::m_mutex`; "new pipeline" resets the
   streak; capacity 4 096. The table is updated and re-stamped only while `cspfam` ≠ 0 (frozen in the ABBA's arm-0
   blocks) and cleared when the programs-epoch mirror or `ShaderRegistrations()` moved (the epoch moves on a new
   `programs` ENTRY, not on a new permutation). Counters `cspfam_look`, `cspfam_skip`. **Guard counters in every run
   (no gate):** `cs_sync_new` (`GetComputePipeline` found no pipeline — compiled synchronously on the dispatch) and
   `cs_sync_wait` (a pending entry — from the lookahead prefetch or the startup precache — still compiling, waited
   for). Nothing under `src/graphics/shader/**`; `check_gate_order.py` clean.
3. **`fam108`** (sealed `pred/01_cspfam.md` `a40cf056…`, ABBA `cspfam=0|4`, 600 s, pinned, 96 pairs, build
   `fd1d0bd7…`, ADMITTED — all 14 integrity terms, 13 controls and 10 arming sub-checks pass): **SHIP — Δ mean `dt`
   −141.8 µs (2·SE 107.0, t −2.65)**; Δ`cpu_net` +72.7 (t 1.50; not deciding; F3 MISS — the frame got shorter while
   GuestGpu's CPU did not: Δ(dt − cpu_net) ≈ −214 µs); walker `da_walk_us` −212.6 (t −28.7); arm-1 `cspfam_skip` 266
   a flip (F1), `cspf_have` 0 (F2); **guard `cs_sync_new` 0 / 0, `cs_sync_wait` 0 / 0**; `da_miss` +2.0 (F6). The
   medians of block means differ by 7 µs only: the gain sits in the frame-time tail (vblank quantisation, as
   `dab106`) — **corrected by the audit (§7 item 2): the gain is more 1-vblank frames (13.25 → 13.97 %), fewer
   2-vblank frames; the block-mean medians coincide because block means move in 575 µs steps.** Size marginal:
   sign-flip p 0.009, bootstrap 95 % CI [−246, −38] µs ⇒ +0.46 % (CI ≈ +0.12 … +0.79 %). Unreported side effect:
   `gpu_busy_us` +87.5 µs a frame in arm 1 (t 4.5), cause unknown. F3 was mis-specified (`cpu_net` tracks `dt`,
   per-pair correlation 0.93). Predictions F1 F2 F4 F5 F6 HIT, F3 MISS. Video `vfm108` (`cspfam=4` in the gate text, pinned,
   recorded): 3 630 frames, 0 one-frame glitches ⇒ **SHIP** (score `runs108/fam108_score_video.stdout.txt`).
4. **Default `cspfam` = 4** (ROADMAP item 5 recorded first; `eed387b`; source-traceable to that commit, not
   bit-reproducible — PE link time and `__DATE__`). **Build `fc78c56417815a0ebdea1c5a5aa94306720c3307d07a6feadf3c8e37f43aae43`**, label
   `KytyPS5-2026-09-15-6a2987a-1040-geed387b-dirty` (the "dirty" is the long-standing `3rdparty/nlohmann_json`
   submodule edit), installed until the rollback (§1 item 6). Video `vid108` (gate text without `cspfam`, pinned): 3 980 frames, 0 glitches,
   `cspfam_skip` 265.8 a flip, `cs_sync_new` 0 — `check108.py` (`77d87515…`, pinned to the build's sha) PASS.
5. **Desert smoke** (ROADMAP item 6, rule recorded in `3c988bb` before the runs): `sf108a` (`cspfam=0`) and `sf108b`
   (default 4), `--level intro_next --hold 300`, pinned: Σ`cs_sync_new` 0 and 0 over the whole logs, no failure
   marker; `sf108b` 2.07 M prefetch skips. **Without power (audit §7 item 1):** the startup precache builds all 121
   compute pipelines from `pipelines.bin`, so no new permutation was met — in this run or in `fam108`.
6. **Powered guard** (ROADMAP item 7, rule before the runs): Sky Garden 300 s, pinned, `KYTY_PIPELINE_PRECACHE=gfx`
   (compute precache off = first visit): `sf108c` (`cspfam=0`) `cspf_new` 74, **`cs_sync_new` 3** (the counter's first
   positive control), `cs_sync_wait` 0; `sf108d` (default 4) `cspf_new` 71, **`cs_sync_new` 6**, `cs_sync_wait` 0,
   2.53 M skips; no failure marker. Rule Σ(new + wait) ≤ 3 + 2 **not met** ⇒ **default rolled back to 0** (ROADMAP item
   8, `01f0c79`). The difference may be noise (separate runs), but the rule was recorded first. **Build
   `379777bba4271847b1b805c403944e4a6552acd0aac0b5cd3af12be36c489107`** (label `…-g01f0c79-dirty`), installed; its
   pinned video `vid108r`: 3 933 frames, 0 glitches, `cspfam_skip` 0, `cs_sync_new` 0 — `check108r.py` (`76543aa4…`,
   audit gaps closed) PASS. The knob stays in the tree (default 0).

## 2. Harness

`C:/kyty/s108`, ported by a fresh `C:/kyty/s107/s108_port.py` (sha256 `cb104f40…`, modelled on
`C:/kyty/s106/s107_port.py` `03a05591…`): `PORT DIAGNOSTIC: clean; carried=6574 ledger=67 skipped=6`; 50 sealed
texts (48 in `prev107/pred`, 2 in carried `prev103/pred` and `prev100/pred`), all hashes checked; `gates_base.txt`
1 092 B / 99 names / `303a7849…`; `gates.cpp` 138 entries (111 + 27), ABSENT 39. New: `fam108.py` (derived from
`dab107.py` by `make_fam108.py`, byte-reproducible; `PRED_SHA` pinned after the seal), `test_fam108.py` (**103
fixtures**, NON-draft: every verdict branch, every decision term, every admission term alone incl. arming sub-checks
by name and `IDENTITY` through `main()`, coupled terms as exact sets with the reason cited; ALL OK, also on the
sealed copy; the fixture agent's 10 mutants each killed by its own fixture), `gates_fam4.txt`, `gates_fam0.txt`,
`go108.sh` / `go108v.sh` / `go108s.sh` / `go108p.sh` / `go108r.sh` (each holds `C:/kyty/SEALED_RUN.lock`),
`check108.py`, `check108r.py`, `seal108.py` (the one-shot that placed and sealed), `kyty_emulator_fd1d0bd7.exe` and
`kyty_emulator_fc78c564.exe` (scored builds, kept for re-scoring), `audit108/` (the auditor's parsers and mutants).

## 3. Source, builds, provenance

Commits: `87f1c2b` (session 107 close), `3cc53a2` (records before action), `f9e19f7` (knob + guard), `72d5fa2`
(pause documentation), `e687a78` (resumption record + seal + fixtures + run chain), `eed387b` (fam108 SHIP record +
default 4), `3c988bb` (build video PASS + desert rule), `22d5ad4` (audit + powered-guard rule), `01f0c79` (rollback
record + default 0), the session commit. Build `fd1d0bd7…` (scored `fam108`; built from the working tree 7 s before
`f9e19f7`, label `…-g3cc53a2-dirty`, same code; copy kept). Build `fc78c564…` (`eed387b`, default 4; `vid108`,
`sf108a/b`, `sf108c/d`; copy kept). Build `379777bb…` (`01f0c79`, default 0; installed). The "-dirty" of every label
is 5 deleted PNGs in the `3rdparty/nlohmann_json` submodule, nothing else. No push.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `fam108` | ABBA `cspfam=0|4`, 600 s, pinned | ADMITTED; SHIP (Δ`dt` −141.8, 2·SE 107.0) |
| `vfm108` | video, `cspfam=4` gate text, pinned | 3 630 frames, 0 glitches |
| `vid108` | video of build `fc78c564`, default | 3 980 frames, 0 glitches; `check108` PASS |
| `sf108a`/`sf108b` | desert 300 s, `cspfam=0` / default 4 | `cs_sync_new` 0 / 0, no marker — no exposure |
| `sf108c`/`sf108d` | Sky Garden 300 s, compute precache off, `cspfam=0` / 4 | `cs_sync_new` 3 / 6 ⇒ rule failed, rollback |
| `vid108r` | video of build `379777bb`, default 0 | 3 933 frames, 0 glitches; `check108r` PASS |

## 5. Next

**First, `cspfam` v2:** the skip without the first-contact window — a global atomic count of compute-pipeline
creations (by the prefetch or synchronously on the dispatch) joins the table's stamps, so any creation clears every
streak and the walker prefetches everything again for K rounds; then a sealed ABBA in the shipping configuration
AND a powered-guard ABBA (compute precache off, ABBA rather than separate runs). Then the walker's second hold — `QueueDrawAhead` (tag 1, ~58 % of the contended wall in `obs107`, 1 021 µs a flip of
holding) — remains. It mutates the ahead table (`ahead_slots`, `ahead_hints`, lazily built `plan_class`) that
GuestGpu's `AheadTake` reads under the same `m_mutex`, so moving it off the lock is a design task (own lock for the
ahead table vs lock-free slots). Session 109 first re-observes the contention under `cspfam=4`, then designs and
codes the candidate behind a knob; M3.2 code may proceed without run time. Plan: `docs/next-session-109.md`.

## 6. Proved, and not proved

**Measured.** At the pin in Sky Garden, skipping the steady-state compute prefetch shortens the mean frame by
141.8 µs (t −2.65, 95 % CI [−246, −38]) when every permutation is precached; with the compute precache off it lets
through 6 dispatch-time compiles in 300 s against 3 without it (separate runs). `cs_sync_new` counts (positive
control). **Not measured.** The contention left after the skip; the gain without the pin; the cost of one
dispatch-time compile. **Not proved.** Any kept speedup this session (none); safety of a skip in scenes with new
content; additivity; 60 FPS.

## 7. Adversarial audit

One agent, three lenses, sealed as `pred/02_audit108.md` (`401a76cc…`). **Recount CONFIRMED**, **Protocol HOLDS**
(MINOR deviations), **Code NOT REFUTED**. Findings: (1) **MAJOR** — the guard and the desert smoke had no power →
powered test, rule failed, rollback (§1 items 5–6); (2) the gain is more 1-vblank frames, not "the tail"; (3) size
marginal (CI [−246, −38]); (4) `gpu_busy_us` +87.5 µs in arm 1, cause unknown; (5) F3 mis-specified; (6) the
heartbeat ran `ls` + `tasklist` during `vfm108` (not `fam108`) because its prompt told it to — prompt replaced; (7)
stray `grep` + orphaned `tail -F` watchers alive in every sealed run — killed; (8) provenance wording (not
bit-reproducible); (9) `cs_sync_*` exist only in traced runs; `check108.py` gaps closed in `check108r.py`; (10) two
fixture mutants survive (GATEARM order clause, `spin_gpu_us` in `cpu_net`) → fixtures for the next derived scorer.
Full report `C:/kyty/s108/audit108/AUDIT108.md`.
