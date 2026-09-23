# Session 108 — WIP, paused by the user before the port, the seal and the run: knob `cspfam` built (compiles, gate order clean), the scorer checked offline on 24 fixtures; the knob itself has never run; nothing measured in the game

**Status: PAUSED (user: «давай пока заканчивать и документировать», 2026-09-23).** This file replaces the usual
`C:/kyty/s108/FACTS.md` until the session resumes: the harness `C:/kyty/s108` does NOT exist (the port agent was
stopped before it wrote `C:/kyty/s107/s108_port.py`; nothing was created). No game run, no seal, no audit in this
session. The session loop and the heartbeat cron are stopped. **No speedup in session 108 (nothing measured). 60 FPS
not promised.** The documentation was checked by a three-lens verification workflow plus a critic; its 15
findings are applied here.

## 1. What is done

1. **Decisions recorded before action:** the executor's decision after session 107, item 1 (commit `87f1c2b`), and
   "СЕССИЯ 108 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–2 (commit `3cc53a2`), both in `ROADMAP.md` §0.1.
2. **Code** (commit `f9e19f7`; patch `docs/session-108/tools/patch_s108.py`):
   * knob **`cspfam`** (`KYTY_CS_PREFETCH_FAMILY`, new LAST knob row, default **0** = off, range 0..1024, the value
     is K = the streak): in `PipelineCache::PrefetchComputePipeline` a per-thread table keyed on the shader FAMILY
     (code hash and base + the stage static key from `BuildStageStaticKey`, no user SGPRs) counts consecutive
     locked prefetches that found a built pipeline; at a streak ≥ K the call returns before `PipelineCache::m_mutex`;
     "new pipeline" resets the streak; capacity 4 096. **The table is updated and re-stamped only while
     `cspfam` ≠ 0:** while `cspfam` = 0 (e.g. the ABBA's arm-0 blocks) it is frozen and is cleared only when the
     programs-epoch mirror (`g_programs_epoch_mirror`, session 107) or `ShaderRegistrations()` moved by the next
     armed call — and the epoch moves only on a new `programs` ENTRY, not on a new permutation. So the streak means
     "the last K locked prefetches observed while the knob was non-zero". Counters `cspfam_look`, `cspfam_skip`.
   * **guard counters in every run (no gate):** `cs_sync_new` (`GetComputePipeline` found no pipeline — compiled
     synchronously on the dispatch) and `cs_sync_wait` (found a pending entry still compiling — queued by the
     lookahead prefetch OR by the startup pipeline precache — and waited).
   * `check_gate_order.py` clean; nothing under `src/graphics/shader/**`; `gates.cpp` now yields **138 entries (111
     gates + 27 knobs)**, `ABSENT` **39** for the next port.
3. **Build `fd1d0bd7f68280e97680bc68dfe56fdf57a134429a49bc9223ece6254b7b1e72`** in `C:/kyty/build/install`, **NOT
   installed** into the game folder. **Not reproducible:** it was built from the working tree 7 s before commit
   `f9e19f7` and embeds the version label `KytyPS5-2026-09-15-6a2987a-1036-g3cc53a2-dirty`; any rebuild now bakes a
   different label and gets a different hash. The code is identical to `f9e19f7`.
4. **Scorer** `fam108.py` (derived from `C:/kyty/s107/dab107.py` by `make_fam108.py`; regenerating it reproduces the
   file byte for byte; `PRED_SHA`/`PRED_BYTES` still `None`; `GATES_FILE = C:/kyty/s108/gates_base.txt`,
   `BINARY_SHA = fd1d0bd7…`): the `dab107` controls with the batch arming replaced by `FAMILY_DARK_ARM0` /
   `FAMILY_ARMED_ARM1`, plus **`SYNC_COMPILE`** (over ALL rows from frame 2100, by row arm: Σ`cs_sync_new` arm 1 ≤ arm
   0 + 2); ship rule S1 Δ mean `dt` ≤ −100 µs, S2 2·SE excludes 0, pinned video (the scorer's nine video checks).
5. **Fixtures** `test_fam108.py` — **24 cases, ALL OK** (`test_fam108.out.txt`), NON-draft mode with full protocol
   metadata. Covered: every verdict branch (SHIP, SHIP_PENDING_VIDEO, KEEP by the bar, KEEP by a failed video, KEEP
   not admitted) and, alone, the terms the candidate adds or changes plus a set of inherited ones — S1, S2, five
   video checks (frames, no_glitch, gate text, pinned, binary), `FAMILY_DARK_ARM0` / `FAMILY_ARMED_ARM1` (asserted
   only as the combined `control:ARMING`), `SYNC_COMPILE`, `PIN_ONCE`, `RECORD_THREAD_TWO`, `NO_FATAL_MARKER`,
   `BANDS`, `GATEARM`, `PREREG_PINNED`, `BINARY_SEALED`, the protocol env check; coupled by construction and asserted
   as exact sets: work split + area verdict, area split + both area controls, pairs + duration, checkpoint env +
   protocol. **NOT covered alone (a pre-seal debt, §2 item 2):** integrity `SCHEMA`, `FIELD_ORIGIN`,
   `RAW_CONTIGUITY`, `NO_FLOOR`, `MARKERS_OFF`, `NO_RECORDING`, `STREAMS_COMPLETE`, `ROW_ARMS`, `AB_BA_BALANCED`,
   `INPUTS`, `DURATION` (only with `PAIRS`), `IDENTITY` (computed only in `main()`); controls `NO_CHECKPOINT_LINE`,
   `NO_GPUHANGABORT`; arming sub-checks `WALK_ARMED_ARM0/1`, `WALK_IDENTITY_ARM0/1`, `WALK_DROPS_ARM0/1`,
   `WALKS_SAME`, `INSTRUMENTS_DARK`, and the FAM sub-checks by name; video checks `recorded`, `no_schedule`,
   `no_checkpoints`, `one_ok_attempt`; protocol errors other than the extra env var (schedule text, gates sha,
   attempts, hold_s). The first fixture draft had two defects of its own (video variants overwrote one file; a
   random S2 case), both fixed; the scorer needed no change.
6. **Seal text drafted, NOT sealed:** `docs/session-108/01_cspfam.DRAFT-not-sealed.md` (ABBA `cspfam=0|4`, 600 s,
   pinned, predictions F1–F6). It is editable until sealed; its sha256 is recorded nowhere.

## 2. What is NOT done (resume here, in this order)

1. **Protect the build.** Check `sha256(C:/kyty/build/install/kyty_emulator.exe) = fd1d0bd7f682…`. Build NOTHING into
   `C:/kyty/build/install` until `fam108` (and `vfm108`) are scored — M3.2 code stays unbuilt or goes to a separate
   build dir. If the file was lost: rebuild at a clean `f9e19f7`, record the new hash, update `fam108.py`
   `BINARY_SHA` and the draft seal §1 before sealing.
2. **Fixture debt, before the seal:** either (a) add single-failure fixtures for every term listed as "NOT covered
   alone" in §1 item 5 and assert the FAM arming sub-checks by name (update the case count in the draft §3), or
   (b) record in ROADMAP §0.1 first that the rule is narrowed to "every verdict branch + the terms the candidate adds
   or changes" and say so in the draft. Option (a) is the rule as written (decision after 107, item 2).
3. **Port:** write `s108_port.py` fresh in `C:/kyty/s107/` (per `docs/next-session-108.md` §1; sealed texts 47 → 50,
   `gates.cpp` 138 entries, `ABSENT` 39; the session-107 files the global rewrite breaks and the new session-108
   names are listed there).
4. **Place and seal:** copy `fam108.py`, `make_fam108.py`, `test_fam108.py` into `C:/kyty/s108`; write
   `gates_fam4.txt` as ONE line — `gates_base.txt` with ` cspfam=4` inserted before its single trailing CRLF (1 101 B;
   record its sha256), like `gates_dab2.txt`; finalise the draft (fixes of §1 items 2 and 5 are already in it), save
   it as `C:/kyty/s108/pred/01_cspfam.md`, write `SEALS108.txt`, pin `PRED_SHA`/`PRED_BYTES` in `fam108.py`, re-run
   the fixtures on the sealed copy, copy the seal and `SEALS108.txt` into `docs/session-108/pred/`, remove the DRAFT
   file, commit — all before the run.
5. **Run** with a `go108.sh` modelled on `C:/kyty/s107/go107b.sh` (the main run WITHOUT `--no-install`, so it installs
   `fd1d0bd7`; `--attempts 1 --pred`; the video `vfm108` only on `SHIP_PENDING_VIDEO`, with `--attempts 1 --pred`, and
   the `s51_vidglitch.py` line that writes `vfm108_glitch.txt`). On SHIP: ROADMAP first, the `gates.cpp` default, a
   new build and its pinned video checked by a script pinned to that build's sha (as `check105.py` was).
6. Adversarial audit, FACTS (`C:/kyty/s108/FACTS.md` must carry over §1 and §3 of this file before the git mirror
   replaces it), ROADMAP end edit, `next-session-109.md`, contexts, commit without push.

## 3. State of the machine and the tree

Installed game binary: **`dd567a0f…`** (session 107; default behaviour = HEAD's defaults, but it lacks the `cspfam`
knob and the `cs_sync_*` counters). HEAD = `f9e19f7` + the documentation commit; build `fd1d0bd7` sits in
`C:/kyty/build/install`. Staging `C:/kyty/s106_stage/`: `fam108.py`, `make_fam108.py`, `test_fam108.py`,
`01_cspfam.md`, `patch_s108.py`, `test_fam108.out.txt`, `fx_fam108/` — copies of all but `fx_fam108/` (the draft
renamed `01_cspfam.DRAFT-not-sealed.md`) are in `docs/session-108/`. No push.
