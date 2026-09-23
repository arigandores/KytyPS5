# Adversarial audit — session 108 (`cspfam`, `fam108`, build `fc78c564`, desert smoke)

Auditor scripts and outputs: `C:/kyty/s108/audit108/` (`parse108.py`, `recount108.py`, `profile108.py`, `guards108.py`,
`mutants108.py`/`mutants108p.py`, `*.out`). Own parser; no session scorer imported. Nothing built or run in the game.

## Verdicts

| lens | verdict |
|---|---|
| Recount | **CONFIRMED** — every claimed number reproduced; SHIP robust in sign, marginal in size |
| Protocol | **HOLDS** — the seal came before the run, the pin was on in every run, fixtures 103/103 and 20 of 22 mutants killed; MINOR deviations only |
| Code | **NOT REFUTED** — a skip can cost only a dispatch-time compile, never a different result; one MAJOR finding: the guard had no power (F1) |

## Recount (`log_fam108.txt` sha `626b535d…`, unchanged since scoring)

| quantity | session | audit |
|---|---|---|
| pairs / orientations / excluded blocks | 96 / [48, 48] / [3, 196] | same; 0 rows with arm/blk ≠ frame-range block |
| Δ mean `dt_us` | −141.8 (2·SE 107.0, t −2.65) | −141.8 (2·SE 107.0, t −2.65) |
| sign-flip p / Wilcoxon p | — | 0.009 (200 k) / 0.008 |
| bootstrap 95 % CI; P(Δ ≤ −100) | — | [−246, −38]; 0.78 |
| paired median; share of pairs < 0 | — | −14.9 µs; 0.58 |
| leave-one-quartet-out range | — | [−163, −127] |
| Δ`cpu_net` (= `cpu_gpu_us − spin_gpu_us`) | +72.7 (t 1.50) | +72.7 (2·SE 96.7; p 0.14) |
| Δ(`dt − cpu_net`) | ≈ −214 | −214.5 (2·SE 40.2, t −10.7) |
| Δ`da_walk_us` / Δ`da_miss` | −212.6 / +2.0 | −212.6 (t −28.7) / +2.0 (2·SE 9.9) |
| Δ`gpu_busy_us` | not reported | **+87.5 (2·SE 38.6, t 4.54)**; area 2007.80 vs 2007.78 |
| arm-1 `cspfam_skip`, `cspf_have` | 266, 0 | 266.0, 0.0 (arm 0: 0, 266.0) |
| `cs_sync_new` / `cs_sync_wait` (rows ≥ 2100, by row arm) | 0/0, 0/0 | 0/0, 0/0 |
| frames by vblank count, kept rows (arm 0 → arm 1) | — | 1 vb 13.25 → 13.97 %; 2 vb 86.17 → 85.56 %; 3 vb 0.57 → 0.47 % |
| pairs by Δ(total vblanks in 29 frames) | — | −2: 7, −1: 31, 0: 38, +1: 18, +2: 2 (sign test p ≈ 0.026) |
| other keep windows ([0:90], [0:89], [30:89], [45:90], [60:90], [0:60]) | — | −168, −182, −140, −90, −103, −201 (all t ≤ −1.99) |
| videos `vfm108` / `vid108` | 3 630 / 3 980 frames, 0 glitches | same (ffprobe packets; `s51_vidglitch.py` re-run: 0, 0) |

Predictions: F1 HIT, F2 HIT, F3 MISS, F4 HIT, F5 HIT, F6 HIT, the same as the scorer. In the kept window the
orientation split is AB +12 ± 137 against BA −296 ± 153. It swaps sign across in-block segments ([30:60]: AB −295, BA
+19), and over whole blocks both orientations are negative (−159, −204), so it is noise, not carryover.

## Findings

1. **MAJOR — the safety guard and the desert check could not fail.** `cspf_new` = 0, `cs_sync_new` = 0 and
   `cs_sync_wait` = 0 on every row of all five logs, loading included (`fam108` 19 572 rows, `sf108a` 19 854, `sf108b`
   19 827, `vid108`, `vfm108`). At startup `PipelinePrecache` builds 121 compute pipelines from `pipelines.bin`
   (log line 573), before the first FrameTrace row. That file already holds every permutation of both scenes, so the
   prefetch never met a new permutation in either arm. `SYNC_COMPILE` and the ROADMAP item-6 rollback rule therefore
   had nothing they could trigger on, and `cs_sync_new` has never been seen non-zero (no positive control). What
   `sf108` does show: the skip engages in the desert (2.07 M skips, 99.8 % of lookups) with no failure marker over
   about 5.5 min, load included. **Correction:** report "0/0 with zero exposure (every compute permutation was
   precached)", not a safety pass. In FACTS §6, "the desert entry shows none either" becomes "the desert entry had no
   new permutation to miss". To give the guard power, run both arms with the compute precache off
   (`KYTY_PIPELINE_PRECACHE=gfx` or `0`). That run is also `cs_sync_new`'s first positive control. The hazard is
   bounded (a hitch with the guest clock frozen, never a wrong image), but it is untested exactly where it lives: new
   content, or any translator change, which invalidates `pipelines.bin`.
2. **MINOR — the effect's shape is misdescribed.** ROADMAP item 5 and FACTS §1.3 say "the gain sits in the frame-time
   tail". It does not. The gain is more 1-vblank frames (+0.21 per 29-frame block, t 2.17) and fewer 2-vblank frames
   (−0.18). 3-vblank frames do not move significantly (−0.03). The medians of the block means coincide because block
   means are quantised in 575 µs steps (one vblank per 29 frames) and the median block holds 54 vblanks in both arms.
3. **MINOR — the size is marginal.** The CI is [−246, −38], P(true Δ ≤ −100) ≈ 0.78, and dropping the 5 most negative
   pairs gives −86. The SHIP rule was met as sealed. Quote the gain as "+0.46 % (95 % CI ≈ +0.12 … +0.79 %)".
4. **MINOR — a side effect nobody reported.** `gpu_busy_us` rises +87.5 µs a frame in arm 1 (t 4.5; +150 µs within
   2-vblank frames) at equal area and draws. It is not predicted, and it is absent from ROADMAP and FACTS. It is
   harmless while the GPU runs at 12.7 of 31 ms. Record it; cause [U].
5. **MINOR — F3 was mis-specified.** `cpu_net` tracks `dt` (per-pair correlation 0.93), and within 2-vblank frames it
   is +209 µs higher in arm 1: GuestGpu fills the freed time with other CPU work. So Δ`cpu_net` cannot show lock spin,
   and fam108 neither supports nor refutes the session-107 "spin share ≥ 0.75" claim. Say so in ROADMAP rather than
   reading F3's MISS as a mechanism.
6. **MINOR (protocol) — the heartbeat ran commands during a sealed run, as its own prompt told it to.** At 19:24:18 it
   ran `ls SEALED_RUN.lock; tasklist`. That was during **`vfm108`** (emulator pid 50260 = `vfm108.json`), not during
   `fam108`, whose measurement ended at 19:23:38. No timing statistic depends on `vfm108`, so severity is negligible.
   But the heartbeat prompt and `C:/kyty/LOOP_STATE.md` ("only make sure `kyty_emulator.exe` … is alive") contradict
   ROADMAP (decision after 106, item 2; s108 item 4) and seal §2 ("a heartbeat only reschedules"), for the second
   time after `dab106`. Correct the self-report ("during vfm108") and align the rule with the prompt.
7. **MINOR (protocol) — the machine was not idle.** A stray `grep` (pid 50484, alive since ≤ 04:36; 95.4 → 97.3 s of
   CPU across the s108 runs, ≈ 0.1 % of a core) and three `claude` CLI processes were live during every sealed run.
   The load was symmetric across arms and negligible, but seal §2's "nothing else on the machine" was not literally
   true. Kill strays when `pre_run` lists them.
8. **MINOR (protocol) — build provenance.** Commit `eed387b`'s only `src/` change against `f9e19f7` is the `cspfam`
   default 0 → 4 (`gates.cpp:381`, plus a comment); `3c988bb` adds only ROADMAP. "-dirty" comes from 5 deleted PNGs
   in `3rdparty/nlohmann_json/tests/reports`, and nothing else is dirty (verified). But item 5's "clean label,
   reproducibility" is not met. The label is dirty, and no build here is bit-reproducible: the PE header carries the
   link time (0x6ab40c12 = 17:27:46 UTC) and `main.cpp:20` embeds `__DATE__`. **Correction:** "source-traceable to
   `eed387b`; not bit-reproducible; scored binary kept as `kyty_emulator_fd1d0bd7.exe` (sha verified)".
9. **MINOR — gaps in the guard and in `check108`.** The `cs_sync_*` counters are FrameStats counters, so they exist
   only under `KYTY_FRAME_TRACE`; untraced play has no guard, and the text's "every run" should read "every traced
   run". Within traced runs coverage is complete: the only dispatch-path compute pipeline creation is
   `GetComputePipeline` (`renderCompute.cpp:815`), and a new permutation always gets a new id. `check108.py`'s checks
   each test what they claim, but `guard` uses `d.get('cs_sync_new', 0)` (a missing field would pass; the field is
   present on all rows), its marker set lacks `--- Error ---` and `AsyncPipelines: skipped draw` (neither is in
   `vid108`), and it has no no-checkpoints check.
10. **MINOR — fixtures.** 103/103 OK on a re-run. 20 of 22 mutants killed (S1, S2 ×2, SYNC ×4 including kept-rows-only
    and arm-swap, FAMILY_ARMED ×2, FAMILY_DARK, PIN_ONCE ×2, IDENTITY ×2, MIN_PAIRS, video pin and frames, KEEP
    window, ROW_ARMS, the skipped-draw marker). Two survived:
    * Deleting GATEARM's ABBA-order clause survives, because the only pattern fixture (`AB_BA`) also sets `abba=0`.
    * Dropping `spin_gpu_us` from `cpu_net` survives. It is not a deciding term; in the run Δ`spin_gpu_us` = +1.3 µs.

**Code notes (no defect).**
- **A skip cannot change what is rendered.** It returns before the lock and before `ProgramCache::Get`, and the
  dispatch always resolves its own program and pipeline, so the worst case is a synchronous compile.
- **No data race.** The table is `thread_local` (`pipelineCache.cpp:206`). Its callers are the walker
  (`graphicsRun.cpp:1551`), GuestGpu for unwalked submissions (`:1834`) and the enqueue walk (`:1803`, mode 1 only),
  each with its own table. The shared inputs are atomics, and all four `programs_epoch++` sites bump the mirror.
- **No wrap or capacity hazard.** The counters are 64-bit. At capacity 4 096 the table is cleared (the scene
  needed ≈ 77 families; 308 locked lookups before skipping).
- **"New pipeline resets the streak" never runs once a family reaches K.** From then on the family is skipped until
  a stamp moves; this is the limitation already recorded in item 1.
- **Freezing the table at 0 does not bias the ABBA.** Arm-1 blocks skip from their first frame.
- **`eed387b` is exactly the default change.**
