<!-- Mirror of C:/kyty/s128/FACTS.md (source of truth), personal identifiers and foreign application names removed by audit128/mirror_facts128.py. -->
# Session 128 - FACTS (source of truth; every table names its time scale)

## Step 0 — ship `rtskip=1` (Emu Engineer, HPP-116; ROADMAP s122 p. 87(е)(1))

Time scale of this section: **UTC** (git `%cI` printed +02:00 is converted).

| Event (UTC) | Time | Evidence |
|---|---|---|
| lock `C:/kyty/SEALED_RUN.lock` absent, start | 2026-09-28 10:39:17 | `date -u` |
| commit `4fc501f4f6c3c5638f472ee6d9c59523d67e472c` (`main`, no push) | 2026-09-28 10:40:38 | `git log -1 --format=%cI` = 12:40:38+02:00 |
| build start / end (`build_local.cmd`, rc 0) | 10:40:42 / 10:41:08 | `step0/build_step0.log` (51 CXX units incl. `gates.cpp`, `renderDraw.cpp`) |
| exe mtime `C:/kyty/build/install/kyty_emulator.exe` | 10:41:08.45 | later than the commit by 30 s |
| install + pinned copy | 10:41:54 | `sha256sum` below |

**Patch** (`C:/kyty/s128/step0/patch_ship.py`, whole-line anchors, LF, `ALL OK`), 3 files, +2 / −5:
- `src/common/gates.cpp`: `{"KYTY_RT_SKIP", "rtskip", 0, 3}` → `{"KYTY_RT_SKIP", "rtskip", 1, 3}` (one line).
- `src/common/gates.h`: `Knob::RtSkip` comment + `; default 1 since session 128`.
- `src/graphics/host_gpu/renderer/renderDraw.cpp`: dead `t_rts_a` removed (declaration, reset in the latch, the only write
  `t_rts_a = true;` at place A) — p. 81(г); no read of it existed.

**Checks**
- `check_gate_order.py` (s113) after the patch, before the build: **`GATE ORDER: clean`**, `Knob: 40 enum entries, 40 table
  rows`; output byte-identical to s127 `hpp107/check_gate_order_hpp107.txt` (the three `UNMATCHED … check by hand` lines are the
  same pre-existing ones). Log `C:/kyty/s128/step0/check_gate_order.txt`.
- `git status --short -- src` after the commit: **empty**.
- Privacy grep of the diff (user name, mail, launcher name): clean.
- `shader_cfg_tests` (`build_tests.cmd` rc 0; `KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`): **delta 0** against
  `C:/kyty/s126/tests_rk3.log` — the same 134 lines, the same `[test]` set and the same failure lines (two pixel dref tests,
  `pretranslation … failed=1`, two `ReadConstBuffer` lines); the only differing byte is a timing value
  `ASTRO BOT PS 5457 structurize: … elapsed_ms=18` → `19`. Byte-identical to s127 `hpp107/tests_hpp107.log`.
  Log `C:/kyty/s128/step0/tests_step0.log`.

**Builds (sha256)**
- shipped, installed: `C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe` =
  `9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7`; pinned copy `C:/kyty/s128/kyty_emulator_9235a7ac.exe`
  (same sha); built from commit `4fc501f4` with a clean `src`.
- rollback: `C:/kyty/s119/kyty_emulator_d3a981a2.exe` = `d3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64`
  (untouched; it was the installed build before this step); or `KYTY_RT_SKIP=0` on `9235a7ac`.

**Not done here / not proven:** no game run (the shipping video `shp128` — step 1 checks `RtSkip: mode 1` and Σ`rts_skip` > 0,
i.e. that the default is really live in the running binary); no gain against `d3a981a2`, in OLD or in another scene is
claimed (the gain is arm 1 against arm 0 of `98d98eee`, NEW, Sky Garden, pin). **Note for the harness:** with the new default
every run that turns on `rk3cen`, `spine`, `spcen`, `slicecen`, `skipceil`, `bindfloor`, `m4baton`, turns off `rtfast`, uses
the debug dump, `KYTY_RENDER_MEMO_FAST=0` or linear readback now prints one `RtSkip: refused reason=…` line and counts
`rts_refuse` (the knob falls back to the full path; not fatal) — such profiles should pin `rtskip=0` if a clean log is needed.
Mutant runs of this step: none (wall sum 0 s).

## Step 1 — harness C:/kyty/s128 and the shipping video shp128 (Harness Engineer, HPP-118; ROADMAP s122 p. 87(е)(1)–(2))

Time scale of this section: **UTC** (`go128a.log` prints local UTC+2; converted here).

| Event (UTC) | Time | Evidence |
|---|---|---|
| lock absent, start of the port | 10:43 | `date -u` |
| chain mutants part 1/4 (24 workers) | 11:01:26 – 11:13:26 | `mut_go128a.q1.txt` (wall 720.4 s) |
| part 2/4 (8 workers) | 11:13:30 – 11:19:25 | `mut_go128a.q2.txt` (354.3 s) |
| part 3/4 | 11:19:29 – 11:24:14 | `mut_go128a.q3.txt` (285.2 s) |
| part 4/4 | 11:24:19 – 11:28:39 | `mut_go128a.q4.txt` (259.6 s) |
| `procload --wait-s 540` clean | 11:28:50 – 11:29:04 | rc 0 |
| `shp128` call 1: BUSY rc 4 (a user process above 0.5 CPU s/s at `PLWAIT=0`; no lock, no install, no attempt) | 11:29:08 – 11:29:22 | `go128a.log` |
| `shp128` call 2 (`PLWAIT=240`): guards clean, lock, install, run | 11:29:28 – 11:32:52 | `go128a.log` |
| enter_scene launched / finished (hold 120 s) | 11:30:13 / 11:32:37 | `shp128.json` |
| shipped build restored, lock removed | 11:32:52 | `go128a.log` |

**Port** (`port128.py` `ee7bd5e8…`, LF, whole-token replacements 127→128, `ALL OK`): byte copies `procload.py` `d9e7a777…`,
`launch_run.py`, `run_safety99.py`; ported `idle128.py` `5a9b706b…`, `envchk128.py` `f040c73b…`, `hostdev128.py` `6c1ed8ee…`,
`enter_scene.py` `c7d33143…` with their suites/mutant lists. Suites: `test_idle128` 118 checks, `test_envchk128` 94 (g0 now:
100 names, `rtskip=1` last, no `protceil`), `test_hostdev128` 87 — all `ALL OK`. Negative controls on the files of 127 (p.
84(в)(4)): `test_idle128` vs `idle127.py` — FAIL (the one-line name), `test_envchk128` vs `envchk127.py` — FAIL (m1, f1);
`hostdev128.py` differs from 127 only in names inside comments/usage and its suite does not see the name — that negative
control is not discriminating (said, not hidden). No `mutlib` on the ported helpers (p. 84(в)(4)).

**Gate files (p. 87(е)(2)):** `gates_base.txt` = the session-127 file byte for byte + one line `rtskip=1` (CRLF, the file's own
line end) — sha256 **`ed54101da106914ca467018710d6fcebb583c0d806fa2079b0f90ece96ea8adb`**, 100 names; `gates_base127.txt` =
the session-127 file byte for byte, `303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf` (no `rtskip`; the gate
file of `shp128`). The emulator's `FindAssignment` accepts `\r`/`\n` before a name (checked in `gates.cpp`).

**Chain `go128a.sh` `5adc975a…`** (port of `go127a.sh`): tags `s1s128` (smoke, ABBA `90+1800` `protceil=0|protceil=1` on the
base, 150 s, ONE attempt inside the call — a retry would hide a death), `s2s128` (smoke, base + `protceil=1`, no schedule, 150
s, one attempt inside the call), `pc128` (registered + one attempt, ABBA `90+1800` `protceil=0|protceil=1`, `rtskip=1` in both
arms from the base, `PHOLD` 300, no video, `KYTY_GPU_MARKERS=0`; needs `PRED/SC/CHK` of step 7), `shp128` (one attempt, not
registered: installs the pinned copy of the SHIPPED build `C:/kyty/s128/kyty_emulator_9235a7ac.exe`, gate file
`gates_base127.txt`, `--rec`, `SHOLD` 120, then `s51_vidglitch.py` and `ship128.py`; a failed check ends rc 1). `KNOB/EXPECT/
PINNED` (step 6, the build of step 4) and `PRED/SC/CHK` (step 7) are EMPTY: the three protceil tags refuse rc 2; `shp128` needs
none of them. `KNOB` must be `protceil`. RESTORE = the shipped build `9235a7ac…` (not `d3a981a2`). Kept from 127: the lock is
checked before any process in every call (6 `lockheld`), `procload`/name guard (`mut_*128|test_*128|mutlib` + the emulator),
CPU < 15, `idle128`, second guard at 0 s, noclobber lock, EXIT trap restore with sha check, one-attempt marker (p. 66(а)) incl.
the rc 3 cases, pin + markers 0 on every run, no `KYTY_GPU_CHECKPOINTS`/`KYTY_GPU_WALL`.
Suite `test_go128a.py` `7516fe96…`: **199 checks, ALL OK** (63–70 s); negative control against `go127a.sh`: 177 of 199 FAIL
(`negctl_s128.txt`). The suite has `FAILFAST=1` (set by the runner only): first failing check → rc 1 — the kill decision is the
same, killed mutants stop early.

**The ONE full chain mutant run (p. 84(в)(1))** `mut_go128a.py` `3741712c…`, 158 mutants, 4 parts, every part names the same
`go128a.sh` `5adc975a…` and `test_go128a.py` `7516fe96…`: part 1 40/40 (controls 24/24), part 2 40/40 (8/8), part 3 39/39 (8/8),
part 4 38/39 (8/8) ⇒ **157/158 killed, controls 48/48**. Survivor **`files_no_gates`** (drop `$GATES` from the files line of a
registered tag) — **equivalent**: the only registered tag is `pc128`, whose `$GATES` = `gates_base.txt`, already on the same
line; no input can tell it apart (in 127 `k3k127` had its own gate file). Wall 720.4 + 354.3 + 285.2 + 259.6 = **1 619.5 s**.
Lesson: 24 workers were a loss (a full control took ~515 s vs ~63 s alone — bash spawn contention on Windows); 8 workers ≈ 210 s.

**`ship128.py`** (conditions of p. 87(е)(1): C1 `RtSkip: mode 1` line, C2 Σ`rts_skip` over `FrameTrace-x` > 0, C3 exactly one
line `one-frame glitches: 0`; admission A1 json, A2 `binary_sha256` = `9235a7ac…`, A3 gates = `gates_base127.txt` words and no
`rtskip=`, A4 pin / `KYTY_REC` / no schedule / no checkpoints; rows only: refusals, `rts_refuse`, share, frames, skipped draws,
`bda_scan`). Suite `test_ship128.py` in the `mutlib` early-exit form (`ok = True`, `ok &= …`, last `sys.exit(0 if ok else 1)`, no
subprocess). **Defect found by the real run and fixed:** the first version `4d8bf295…` crashed printing a Cyrillic `г` to the
cp1250 console AFTER all ten condition/admission rows printed `ok` (`ship_shp128.crash.txt`; the chain logged `shipcheck shp128
rc=1` with an empty verdict and ended rc 1). Fix: ASCII output (`10995013…`) + fixture p5 (output must encode in cp1250; the old
version fails it). Final suite `d4303f5c…`: 72 checks ALL OK. Full `mutlib` v4.1 on the final text (`--control --no-memo
--work-dir/--cache-dir C:/kyty/s128/...`): header `fast on (40 guarded updates)`, `workers 28` (not FORCED), **ALL KILLED 62/62,
controls 3/3, 18.4 s** (`mut_ship128.txt` `4c6f3d3b…`). Earlier runs of the step: refused (no `BASE = Path`) 0 s; run 1 61/62 (8.4
s, survivor `a3_rtskip_ok` → fixture a3_base_rtskip); run 2 62/62 (8.7 s, `mut_ship128.run2.txt`).

**Mutant wall sum of this step (p. 85(в)(4), counted by p. 87(б)(3) — all of it is budget):** chain 1 619.5 s + `ship128`
0 + 8.4 + 8.7 + 18.4 = **1 655.0 s ≈ 27.6 min of the 30-min session budget** — about 2.4 min remain for the other steps outside
the one full scorer run of step 7.

**The shipping video `shp128`** (one attempt, made; installed build before and after = `9235a7ac…`):
- Entry: `underwater_aerial_garden in 18.4 s - PASS`; hold 120 s; `hostdev` RUN_CLEAN; `envchk128` PASS (pin, no checkpoints,
  markers 0, `KYTY_REC` set, no schedule, gates = `gates_base127.txt`); `hold_gpu` median 46.0 % over 237 rows (a row).
- `ship128.py shp128` rescored offline on the same files with the fixed checker (`ship_shp128.txt` `cbaf48af…`):
  **VERDICT: SHIP_VIDEO_PASS** — A1–A4 ok; **C1** 1 line `RtSkip: mode 1` (0 `RtSkip: refused`, Σ`rts_refuse` 0); **C2**
  Σ`rts_skip` **16 989 163** of Σ`rts_n` 19 210 396 (share 0.8844) over 4 014 `FrameTrace-x` rows; **C3** `s51_vidglitch.py`
  `rec_shp128.mp4` (4 026 frames 960x540) — **one-frame glitches: 0**. `AsyncPipelines: skipped draw` 0; no `--- Error`,
  `std::terminate`, `GpuHangAbort` lines. BDA regime (row): `bda_scan` lives on `FrameTrace-draw`, mean over all 4 014 rows 188.5
  (whole run incl. loading; NEW band ≤ 300) — `ship128`'s own row reads only `FrameTrace-x` and prints `n/a` (a row, not a
  condition; noted for the scorer of step 7).
- Files: `rec_shp128.mp4` `d36b7380…`, `log_shp128.txt` `97c0bbdb…`, `shp128.json` `9467a158…`, `vid_shp128.txt` `e787ce28…`.
- **Frame sheet for the lead** (`mk_sheet128.py`; left `shp128`, right the `k3w127` frames of `sheet127`): `sheet128/sheet_a.png`
  `6877d659…`, `sheet_b.png` `1cdfacfa…` (same t as 127: the first rows are out of phase — `shp128` is 300 frames = 5 s longer at
  its start); **in phase: `sheet_a_o5.png` `528b45fe…`, `sheet_b_o5.png` `6d3d8fec…`** (left at t + 5 s). By eye: the same
  scene, objects, light, sky, grass, shadows; differences are the animation phase (Astro, flamingos, the ship). No pixel diff.
- Not claimed: a gain of `rtskip=1` against `d3a981a2`, in OLD or in another scene; correctness beyond p. 76(з)(3). **No failure
  ⇒ `d3a981a2` NOT reinstalled**; the installed build stays the shipped `9235a7ac…`.

**Questions to the lead:** (1) accept `files_no_gates` as equivalent (157/158), or should the chain drop `$GATES` from the
registered files line? (2) the mutant budget is ≈ 27.6/30 min spent by this step (the chain run is the bulk). (3) the smokes run
ONE attempt inside the call (my choice, to keep a death visible) — confirm for step 6. (4) step 6 fills `KNOB="protceil"`,
`EXPECT` = `b037d3dd…` (step 4), `PINNED=/c/kyty/s128/kyty_emulator_b037d3dd.exe` with one fixture each (c2 of the suite changes).

## Step 2 — design of the knob `protceil` (Probe Designer, HPP-117; ROADMAP s122 p. 87(е)(3)–(7), (ж))

Time scale of this section: **UTC**.

| Event (UTC) | Time | Evidence |
|---|---|---|
| lock `C:/kyty/SEALED_RUN.lock` absent, start of reading | 2026-09-28 ≈ 10:41 | checked before every write |
| rows [c] computed from the sealed `k3p127` log (read only) | ≈ 10:50 | `design/numbers128.py` → `design/numbers128.out.txt` |
| commit `46a68df4` (`main`, no push) | 2026-09-28 10:53:23 | `git log -1 --format=%cI` = 12:53:23+02:00 |

**Artifacts (git `46a68df4`, sha256):**
- `docs/session-128/design128.md` rev 1 — `d146b98165e1e555694069e68e85130be64ac26d05f091daf3f27a111e829bb3` (72 385 B, LF).
- `docs/session-128/design/numbers128.py` — `c1ac02b67bcb579966a377bb387b8155dbd5a232ac768f75c604fc244291d6e1`.
- `docs/session-128/design/numbers128.out.txt` — `188fe9d6bac8a3537438fee6a1843432b268c4f2d5735115a23bca0f3489cae8`
  (input `C:/kyty/s127/log_k3p127.txt`; blocks by `GateArm:`, window 10–88 of p. 55(б)).

**Design in one paragraph.** `protceil` (`KYTY_PROT_CEILING`, 0..1, default 0, last knob row, MEASUREMENT ONLY). Latch: RAII
`PageManager::CeilScope` around `ForEachUploadRange` in `BufferCache::SynchronizeBuffer` (`bufferCache.cpp:835`), GuestGpu
only, one knob read per operation, nested scopes inherit. At 1 the host call `Protect(Read)` is skipped in P1
(`ProtectRun` of `UpdateRegionWatchers<track, !is_read>`) and P2 (`FlushRegion` runs `Read`: the scope flush and the range
flush of that synchronization); `NoAccess`, `ReadWrite`, the NA → Read de-arm, the protection worker and everything off
GuestGpu stay as at 0. Tracker state is changed exactly as at 0; a new bit U per page (under the region `apply` lock) marks
pages whose host protection may be weaker; invariant P′: host never stricter than the tracker, difference only in the
write bit ⇒ no new fault, GPU → CPU reads untouched, only CPU writes into unarmed pages are lost (broken picture allowed).
Re-arm sweep on the latch edge 1 → 0 (positions 0–1 of an arm-0 block, outside the window). Refusals: `armdefer`,
`protbatch2`. 29 raw counters (`prot_gpu_{ro,na,rw}_*`, `pc_elig_*`, `pc_skip_*`, `pc_u_*`, `pc_rearm_*`, `pc_vfy_u*`,
`pc_op0/1`, `pc_refuse`, `pc_offthr`); zero invariants and identities Т1–Т7 — §7.

**Rows [c] (`k3p127` arm `rtskip=0`, window 10–88, means per row; build `98d98eee`, NEW):** `prot_gpu_us` 1 742,3 /
`prot_gpu` 209,9 / `prot_gpu_pages` 6 595,3; `prot_ro` 173,0 / 5 965,8 pages (all non-worker threads); `prot_na` 21,7;
`prot_rw_us` 1 724,7; `fw_n` 1 246,4; `faults` 1 250,7 / `fault_us` 15 139,9; `faults_main` 76,4 / `fault_main_us`
1 131,7; `pb_wait_gpu_us` 195,1; `pb_wait_us` 10 296,8; `sync_up_kb` 23 191,2; `sync_ups` 84,6; `bda_scan` 56,5. Read-only
share of GuestGpu protection ≈ 82 % of calls / ≈ 90 % of pages [I] — the "< 1/3" question of p. 87(е)(3) is not expected
to trigger; the smoke decides.

**Questions to the lead (design §12):** В1 re-arm on 1 → 0 and its seal guard; В2 foreign deferred arming in the range flush
(skipped); В3 written-upload arming (skipped); В4 threshold of the effect control К2 (`fw_n` arm 1 ≤ 0,25 · arm 0); В5 BDA
regime can depend on the arm (`bda_scan` moves with faults) — p. 83(г) unchanged, extra rows; В6 read-only share = `pc_elig_ns
/ prot_gpu_ns`; В7 smoke tag with `pbcheck=1` (К3); В8 (not s128) value 2 "skip + keep dirty" for a mechanism-realistic
bound; В9 `protceil=0` line in `gates_base.txt` (letter of p. 87(е)(5) "replace in place") vs schedule-owned name.

**Not done / not proven:** no game run, no emulator code; every number is [c]/[I], not a gain; the Δ of `pc128` will be an
upper bound inflated by removed re-uploads and guest faults (design §11). Adversarial review — step 3 (Red Team).
Mutant runs of this step: none (wall sum 0 s).

## Step 3 — adversarial review of the design `protceil` (Red Team, HPP-119; ROADMAP s122 p. 87(ж), 88(л))

Time scale: UTC. Review written 2026-09-28 11:06 UTC. No game run, no emulator code, no scorer; nothing started beside the
log reading below (no `SEALED_RUN.lock`, no emulator process at the time).

**Artifact:** `docs/session-128/design/review128.md` (git, sha256 `e2606783…` of the LF text), subject `design128.md` rev. 1
(`d146b981…`, `46a68df4`) with lead decisions p. 88 (`34f3c56e`). Verdict **ACCEPT WITH REQUIRED CHANGES**: 3 MAJOR, 6 MINOR.

| RC | class | one line |
|---|---|---|
| RC1 | MAJOR | upper bound not established for write-watch (image arming by the worker, NA → Read re-arming, GuestGpu faults stay in arm 1); `K14_CLOSED` closes `armdefer`/`protbatch2` by the letter, write-watch only with a residual correction — question to the lead |
| RC2 | MAJOR | ABBA carryover unmeasured (1 → 0 stale GPU data, 0 → 1 armed pages with write period > 10 frames), both push Δ toward 0; ABBA already contains after-own/after-other blocks — print them; base p. 87(е)(7) question |
| RC3 | MAJOR | "no new path to crash or hang" is wrong: torn CPU → GPU data can hang GPU loops; add device-lost text, `GpuWaitSlow:`, `bl_trip`/`BvhLoopCapTrip:` rows; cause line in the smoke report |
| RC4 | MINOR | U pages with host `Read` do fault (middle pages of a skipped run); name the `Verify` class |
| RC5 | MINOR | add `faults_gpu`/`fault_gpu_us` rows (the only fault time on the critical path) |
| RC6 | MINOR | Т1/Т2 as `NOT_ADMITTED` with an unmeasured tolerance; tolerance from the smoke; Т6 made exact (`pc_u_live` or full `pc_rearm_pages`) |
| RC7 | MINOR | `pc_elig` by the same predicate as the skip, passed as an argument; operation = whole `ForEachUploadRange` incl. `upload_func` |
| RC8 | MINOR | re-arm cost scales with the U set of a whole block, not one frame; rows by transition |
| RC9 | MINOR | new `Region` fields after `applying_run`; size before/after |

**Numbers read for the review [c]** (`C:/kyty/s127/log_k3p127.txt`, build `98d98eee`, Sky Garden, NEW, pin; blocks by `GateArm:`,
window 10–88 of p. 55(б), mean of window rows; a copy of `design/numbers128.py` with extra keys, run in the run scratch dir,
not committed): arm `rtskip=0` — `faults_gpu` 21,1, `fault_gpu_us` 104,6, `gpu_busy_us` 13 676,2, `fw_refault` 17,6,
`tex_inval` 1 246,4 (= `fw_n` 1 246,4); arm `rtskip=1` — 21,1 / 102,5 / 13 632,9 / 17,5 / 1 246,4. Not a gain; not `pc128`.

**Checked without findings (review §2):** single host exit of guest protection (`Protect` → `ProtectGuestHostMemory`); no
application without `apply`; P′ on `faultkb`, `InvalidateRegion` under `protbatch`, `KeepApplied`/`FlushBlocker` at
`applyskip=0`, `MarkStaleReadable`, `UntrackMemory`; U races (all under the region `apply`; role `Gpu` only on GuestGpu,
`graphicsRun.cpp:690`); `CheckNotInUploadCallback` keeps invalidations/downloads out of the latched operation; "0 is the old
path" as behaviour.

**Open (owner):** RC1(в), RC2(в) — decisions of the lead (ROADMAP line before step 4); RC1(а)–(б), RC2(а)–(б), RC3–RC9 —
Probe Designer (design rev. 2) or, for code items RC5/RC7/RC9, Emu Engineer under the accepted design. Mutant runs of this
step: none (wall sum 0 s).

## Step 4 — code of the knob `protceil` (Emu Engineer, HPP-120; ROADMAP s122 p. 87(е)(3), 88, 89)

**Commits in `main` (no push):** `558411009640fcb0ee7fd9bdb6c9743ba15ece66` (`55841100`, the knob) and
`252b0c76a6fd4d20ddb4c0c032f6de084010e160` (`252b0c76`, the `FrameTrace-x` rows of `videoOut.cpp`, left out of the first
`git add`). `git status --short -- src` empty after `252b0c76`; the build ran after that commit (label `252b0c76-dirty` — the
same `-dirty` as `4fc501f4`/`defd2c91`: the long-standing modified submodule `3rdparty/nlohmann_json`, not `src`).
**Measurement build:** sha256 `b037d3ddebca86413a7d37ec8302e8d2da6e9f761d007f7f2acba000a03915c1`, pinned copy
`C:/kyty/s128/kyty_emulator_b037d3dd.exe`. **Installed build unchanged:** `ps5 em/kyty_emulator.exe` = `9235a7ac…` (step 0).
`check_gate_order.py`: **`GATE ORDER: clean`** after the patch and before the build (one `UNMATCHED` line — `ProtCeiling` ↔
`protceil`, the design's enum name; not a swap, last row). Game not run in this step; **no smoke — WIP until step 6.**

| event (UTC) | time |
|---|---|
| patch applied (`step4/patch_protceil.py`, dry run first) | 11:25 |
| compile check build | 11:26:26 |
| commit `55841100` / `252b0c76` | 11:27:15 / 11:27:21 |
| build from the committed tree, copy pinned | 11:27:48 / 11:28:03 |
| `memory_tracker_tests` / `shader_cfg_tests` | 11:28:43 / 11:29:22 |

**Files (10):** `common/gates.h`, `common/gates.cpp` (knob — LAST row / last entry before `Count`, default 0, max 1),
`common/frameStats.h` (33 counters at the end of `Counter`), `graphics/presentation/videoOut.cpp` (32 rows after `rts_early`
+ `pc_u_live`), `graphics/host_gpu/pageManager.h`/`.cpp` (latch, U bit, skip, re-arm, `Verify` classes),
`host_gpu/renderer/cache/bufferCache.cpp` (latch in `SynchronizeBuffer`), `host_gpu/renderer/renderContext.h`/`.cpp`
(`ProtCeilRearm`), `guest_gpu/graphicsRun.cpp` (re-arm call site). `src/graphics/shader/**` untouched — translation cache
signature unchanged. `regionManager.h`, `memoryTracker.h`, `textureCache.cpp` untouched.

**Counters (`FrameTrace-x`, all raw, `micros=false`; 33 names):** `prot_gpu_ro_ns`, `prot_gpu_ro_n`, `prot_gpu_ro_pages`,
`prot_gpu_na_ns`, `prot_gpu_na_n`, `prot_gpu_rw_ns`, `prot_gpu_rw_n` (every value; split of `prot_gpu`/`prot_gpu_us`, the same
`if` as `ProtectGpuNs`), `pc_op0`, `pc_op1`, `pc_refuse`, `pc_offthr`, `pc_elig_ns`, `pc_elig_n`, `pc_elig_pages`,
`pc_elig_scope_n`, `pc_elig_rng_n`, `pc_skip_n`, `pc_skip_pages`, `pc_skip_scope_n`, `pc_skip_rng_n`, `pc_u_set`, `pc_u_clr`,
`pc_u_live` (**printed as the running total** at the end of the line, not per frame — p. 89(ж)), `pc_rearm_n`, `pc_rearm_runs`,
`pc_rearm_pages`, `pc_rearm_ns`, `pc_rearm_decl`, `pc_rearm_pend`, `pc_rearm_odd`, `pc_vfy_u`, `pc_vfy_u_na`, `pc_vfy_u_ro`.
T6 (p. 89(ж)): every U bit 1 → 0 increments exactly one of `pc_u_clr` (an application outside the pass, any thread) or
`pc_rearm_pages` (= `pc_rearm_decl` + `pc_rearm_pend` + `pc_rearm_odd`); `pc_u_live` = Σset − Σclr − Σrearm_pages in the same
places. Log lines: `ProtCeil: mode 1`, `ProtCeil: refused reason=armdefer|protbatch2` (once each per process);
`PbCheck: MISMATCH … unarmed=1` (stderr, ≤ 32) only for `pc_vfy_u_na`.

**Layout (p. 89(к)):** new `Region` fields `unarmed[16]`, `has_unarmed`, `unarmed_listed` after `applying_run`;
`sizeof(Region)` **1176 → 1312** bytes, pinned by `static_assert(sizeof(Region) == 1312)` (compiled); no field above moved.
`unarmed_regions` (vector of region + base) and the TLS `t_ceil_state`, `t_ceil_rearm` — in `Impl`, outside `Region`.

**Tests:** `memory_tracker_tests` — `all cases passed` (as `s96/test_memory_tracker_tests.txt`); `shader_cfg_tests`
(`KYTY_TESTS_CONTINUE=1`, 127 tests) — two failures `IMAGE_SAMPLE_C` / `IMAGE_SAMPLE_C_LZ`, the long-standing pair of HANDOFF
(delta 0). `page_manager_tests` does not link: `OverlapsGuestStack` has no stub in `tests/PageManagerTests.cpp` since
`c7516a8a` (2026-09-09) — pre-existing, not this change. No test exercises the knob at 1 (the latch is opened only by
`BufferCache`). Logs: `C:/kyty/s128/step4/`.

**Implementation decisions — questions to the lead (not decided by the engineer):**
1. **Re-arm call site (p. 89(в)(1)):** `RenderContext::ProtCeilRearm()` at the top of each GuestGpu submission in
   `GuestGpu::ThreadRun`, right before `Process` (next to the `burn` hook: outside `m_queue_mutex` and the render mutex, no
   region/cache lock, not in an upload callback). Condition: some page unarmed (GuestGpu-only list, one empty test at 0) and
   the knob reads 0. **Deviation from the letter "before the first operation at 0":** operations of a submission already
   running when `Gates::Poll` flips 1 → 0 run at 0 before the pass (the prior path; U pages stay unarmed until the next
   submission boundary, positions 89/0 of the block). The declaration is `RenderContext::InvalidateMemory` — the very function
   `Memory::InvalidateMemory` reaches (buffer + texture cache); a GuestGpu write fault already calls both caches'
   `InvalidateMemory` on this thread. Runs never cross a 4 MiB tracking region (bounds the `ReadMemoryOnGpu`/`FindBuffer`
   window of a GPU-dirty run). Legality and lock order — step 5 (Red Team).
2. **Order inside the pass (P′ kept throughout):** (1) under `apply`+`lock` per region: U ∧ pending → cleared
   (`pc_rearm_pend`), U ∧ ¬Read → cleared (`pc_rearm_odd`), U ∧ Read → a run to declare, **bit kept**; (2) declare with no lock
   held — applications it makes on this thread clear U as `pc_rearm_decl`; (3) fallback per region: whatever is still U ∧ Read
   ∧ ¬pending is protected read-only inside the same `apply` hold that read it (`pc_rearm_decl`), the region's marks reset.
3. **`pc_elig_*` at a refused latch:** not counted (state `CeilRefused` ≠ `CeilZero`) — a refused latch would not skip.
   Refused latches count in `pc_op0` (design §7.1).
4. **Latch inside the re-arm pass** reads 0 without reading the knob (a `SynchronizeBuffer` reached from the declaration
   cannot skip and cannot touch the list being swept); counted `pc_op0`.
5. **Latch scope** is the `else` block of `SynchronizeBuffer`: `ForEachUploadRange` plus the `pbcheck` `VerifyProtection`
   after it (no protection change there).
6. **Skipped П2 runs** are not counted as host calls of `FlushRegion` (return value) — the counters `BatchMerged`, `BatchRefault`,
   `BatchRuns`, `BatchKb` differ in arm 1 by construction (rows, not guards).

**Mutant runs of this step:** none (wall sum 0 s).

## Step 5 — code review of the knob `protceil` (Red Team, HPP-121; ROADMAP s122 p. 87(е)(3), 89(л), 90(б))

Time scale: UTC. Review 2026-09-28 11:30–11:47 UTC. No game run, no build, no scorer, no mutants (wall sum 0 s); the only
process started was `C:/kyty/s96/check_gate_order.py` on `HEAD` `8dc1302d` (`GATE ORDER: clean`); no `SEALED_RUN.lock`.

**Artifact:** `docs/session-128/design/codereview128.md` (git, sha256 `0b9503eb…` of the LF text); subject commits
`55841100` + `252b0c76`, build `b037d3dd…` (`C:/kyty/s128/kyty_emulator_b037d3dd.exe`). Verdict **PASS, not BLOCKING** — no code
change required.

| item | result |
|---|---|
| 0 = old path byte for byte | yes: skip needs `CeilSkip`; U never set at 0, so `ClearUnarmed`/`Verify` class/re-arm never write; added only counters, one knob read per `else`-sync, one empty-vector test per submission, `Region` 1176 → 1312 B |
| latch once per operation / nesting / refusals | yes (`CeilScope`, `pageManager.cpp:1481–1531`, `bufferCache.cpp:838`); refusals read only at 1, logged once per reason, `pc_refuse`, refused → `pc_op0` |
| one arming predicate (p. 89(з)) | yes (П1 `:510–512`, П2 `:1010–1018`, same `arm` to `Protect` for `pc_elig`) |
| U only under the region `apply`; P′; `pc_rearm_odd`, `pc_vfy_u_na` unreachable | yes (argument in the review §2.2) |
| re-arm place (p. 90(б)) | **accepted**: same loop point as `m_commands`; no lock held; `ReadMemory`/`WaitPendingHostReads` handle GuestGpu; lock order apply → lock; past position 9 only if one submission spans ≥ 9 flips (code argument; guard p. 88(б) checks) |
| T6 on code (p. 89(ж)) | yes; read caveat R1 |
| split by mode (T1/T2) | same `ns`, same `if` as `ProtectGpuNs` |
| knob order; shader tree | last row / last enum entry; `src/graphics/shader/**` untouched |

**Open (MINOR, owner step 7 Harness Engineer; rules — the lead):** R1 — T6 as an exact guard on the log's last line fails
spuriously by the non-atomic snapshot (arm-1 line, `SkipRun` between the reads of `pc_u_set` and `pc_u_live`); guard it on
window lines 10–88 (p. 55(б)) of arm-0 blocks after arm 1 (`pc_u_live` = 0, Σ identity = 0 exactly), elsewhere a row; parse
`pc_u_live` as signed 64-bit. R2 — carryover rows p. 89(и) also `img_up_kb`, `tex_inval`, `img_pend_kb` (the declaration
invalidates images too). R3 — refusal guard by arm text (`protbatch2=0`, `armdefer=0`), `pc_refuse` = 0 in addition (the
batched pass `CollectBufferUpload` opens no `CeilScope`). Known debt (p. 90(а)): no test at 1.

## Step 6 — smoke of the knob `protceil` (Harness Engineer, HPP-122; ROADMAP s122 p. 87(е)(3), 88, 91(е), 92)

Time scale of this section: **UTC** (the chain log `go128a.log` and the attempt json write local time = UTC + 2 h; converted
here). Build under test: pinned `C:/kyty/s128/kyty_emulator_b037d3dd.exe` (`b037d3dd…`, step 4). Chain `go128a.sh`
`b50af0f2…`, base `gates_base.txt` `606da34a…` (+ `protceil=0`, p. 88(к)), `gates_s2s128.txt` `190e0d8a…`,
`gates_s3s128.txt` `d61149d6…`. Sky Garden, `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, no `KYTY_GPU_CHECKPOINTS`, no video
(envchk128 PASS on both runs).

| event (UTC) | time | evidence |
|---|---|---|
| `s2s128` attempt 1: `procload` 540 s not clean (third-party app ≈ 3–4 cores) → BUSY rc 4, no run | 11:59:02–12:07:50 | `go128a.log` |
| `s2s128` attempt 2: same, BUSY rc 4, no run | 12:09:46–12:18:34 | `go128a.log` |
| `s2s128` requested / `procload` clean / idle128 IDLE (GPU 2 %) | 12:30:18 / 12:33:08 / 12:33:24 | `go128a.log` |
| `s2s128` start; `Level has started` at +14,8 s; `nvlddmkm/153` (TDR) | 12:33:24 / ≈ 12:33:47 / 12:33:48 | `s2s128.stdout.txt`, `hostdev_s2s128.txt` |
| `s2s128` `vkWaitSemaphores failed: ErrorDeviceLost (-4), tick=4561`; shipped build restored | 12:33:54 / 12:33:55 | log, `go128a.log` |
| `s1s128` requested / start; level stable at 15,9 s | 12:34:42 / 12:35:22 | `go128a.log` |
| `s1s128` `GateArm` block 0 `protceil=0` frame 1800; block 1 `protceil=1` frame 1890 | ≈ 12:36:3x | log lines 438219, 448656 |
| `s1s128` `nvlddmkm/153`; game ended in the hold at 65,3 s of 150 (`vkQueueSubmit failed: ErrorDeviceLost`, `--- Fatal Error ---` `commandScheduler.cpp:968`) | 12:36:43 / 12:36:49 | `hostdev_s1s128.txt`, `stdout_s1s128.txt` |
| shipped build restored, sha256 checked `9235a7ac…` | 12:36:51 | `go128a.log`, `sha256sum` |

**Survival (p. 87(е)(3)): `protceil=1` DOES NOT LIVE — 2 of 2 runs, both GPU hangs (TDR `nvlddmkm/153`, device lost).**
- `s2s128` (`protceil=1` from frame 1, `Gate: protceil=1 frame=1`, `ProtCeil: mode 1`): died ≈ 1 s after `Level has started`
  (last `FrameTrace` n = 317; `GpuWaitSlow:` ×2 on tick 4561, `acopy` 2406/2406/2406, `submit_backlog=0`).
- `s1s128` (ABBA `90+1800` `protceil=0|protceil=1`, entry at 0 from the base): 1 799 frames at `protceil=0` on the SAME build,
  level entry and the whole arm-0 block 0 included — no hang; after the latch 0 → 1 at frame 1890 the GPU hung within
  **4 frames** (last `FrameTrace` n = 1894 = position 3 of block 1, p = n − F − 1).
- Attribution row: death follows the arm, not the build and not the entry (same build lives 1 799 frames at 0). Cause lines
  (RC3): `GpuWaitSlow:` 1 / 2, `BvhLoopCapTrip:` 0 / 0, `bl_trip` 0 / 0, `PbCheck:` 0 / 0, `pc_vfy_u_na` 0, `pc_refuse` 0,
  `pc_offthr` 0, `pb_bad` 0, `pc_rearm_odd` 0 (s1 / s2). Unarmed pages at death `pc_u_live` **14 784** (s1, 4 frames of arm 1;
  Σ`pc_u_set` 14 873 − Σ`pc_u_clr` 89 − `pc_rearm_pages` 0 = 14 784, T6 exact) and **21 309** (s2; 40 809 − 19 500 − 0).
  Mechanism [U]: CPU writes into unarmed pages are not seen by the buffer cache → the GPU consumes stale guest data → a GPU
  loop hangs (predicted by RC3 of step 3). Which operation hung is not measured (`KYTY_GPU_MARKERS=0` in the chain).
- `hostdev128` prints RUN_INVALID for both (the TDR the run itself caused).

**Rows — arm `protceil=0`, block 0 (F = 1800) of `s1s128`, window 10–88 of p. 55(б), 79 rows, means per row, NEW
(`bda_scan` 66,8 ≤ 300, p. 40(е)(1)); a row, not an estimator:** `dt_us` 32 911,0; `draws` 5 092,0; `gpu_busy_us` 13 567,1;
`prot_gpu_us` **1 789,5** / `prot_gpu` 220,6 / `prot_gpu_pages` 6 958,3. **Split by mode (p. 87(е)(3), 88(ж)):**
`prot_gpu_ro` 1 488,9 µs (164,3 calls, 5 872,0 pages) / `prot_gpu_na` 167,8 µs (21,7) / `prot_gpu_rw` 133,3 µs (34,7);
**read-only share of the split sum 0,832**; **В6 share `pc_elig_ns / (ro+na+rw)` = 0,808** (`pc_elig` 1 446,9 µs, 149,8
calls, 5 522,8 pages) — above 1/3, so the "< 1/3" question of p. 87(е)(3) does not trigger. T1 (calls) +0 over 79 rows; T2
+38,3 µs over 79 rows (split 141 410,3 µs vs Σ`prot_gpu_us` 141 372). R_gpu 2 107,9 µs/row (`smk128`). Re-upload / fault rows:
`faults` 1 248,3, `faults_gpu` 25,5 / `fault_gpu_us` 125,1, `fw_n` 1 244,1, `fw_refault` 19,1, `tex_inval` 1 251,0,
`sync_ups` 90,0 / `sync_up_kb` 23 320,1, `img_up_kb` 101 258,5, `img_pend_kb` 466,6, `pb_wait_gpu_us` 192,8, `pc_op0`
1 128,3. Pre-schedule in-scene rows (1 618 rows with `draws` ≥ 300, mixed load/BDA — `bda_scan` 378,1, between the bands,
not cited as a level): ro share 0,816, В6 0,797.

**Rows — arm `protceil=1`:** window population **empty** (0 rows of 10–88 in `s1s128`; `s2s128` has no scene population:
16 settled rows, `draws` 71,4 — entry only). Positions 0–3 of block 1 (4–5 rows, not a window): `pc_op1` 911,8, `pc_skip_n`
72,0 / `pc_skip_pages` 2 974,6 per row, `prot_gpu_us` 463,0, ro share 0,596, `fw_n` 854,4, `sync_up_kb` 17 239,6, `bda_scan`
30,4. **Price rows (ABBA `protceil=0|1`, p. 82(в)): 0 pairs — NOT EVALUABLE.** K2 (p. 88(д)): arm-1 window 0 rows — **NOT
EVALUABLE**. Transitions 1 → 0: none (run died in arm 1); T6 guard rows 0. BDA regime per arm: arm 0 NEW; arm 1 not
evaluable.

**Not run:** `s3s128` (K3, `protceil=1 pbcheck=1`, 90 s) — after two deaths out of two on `protceil=1` I stopped the series
(CLAUDE.md "stop on the first reproduction"; each TDR freezes the desktop ≈ 60 s for the user); `pbcheck` does not change the
skip, so the run would die the same way [U]. Decision to the lead (question 2).

**Tools:** `smk128.py` fixed (my defect found on the real log: K2 printed `within` with an empty arm-1 window; now `NOT
EVALUABLE`, `evaluable` flag in the json) — `smk128.py` `12f6c37c…`, `test_smk128.py` `d559841f…` **20 checks `ALL OK`**, new
fixture a14 fails on the pre-fix text (negative control: 1 FAIL, a14). `step6/rows128s6.py` `93562289…` (rows by `GateArm:`,
p = n − F − 1, same as `k3p127.py`/`smk128.py`; agrees with `smk128` to the digit) → `step6/rows_s6.txt` `f88b4116…`;
readouts `step6/smk_s1s128.txt` `dbb18cb1…`, `step6/smk_s2s128.txt` `332d0b7f…`. Logs: `log_s1s128.txt` `c9427f94…`,
`log_s2s128_a1.txt` `b9988b60…`. **Mutant runs of this step: none (wall sum 0 s).** Installed build after the step:
**`9235a7ac…` (shipped, `rtskip=1`)**, sha256 checked.

**Questions to the lead (no decision taken):**
1. `protceil=1` as built (skip GuestGpu read-only arming, lose CPU writes to unarmed pages) hangs the GPU within 4 frames in the
   scene: the sealed `pc128` (ABBA `protceil=0|1`, hold 300 s) cannot live, so the K14 ceiling cannot be measured with this
   knob. Options I see (the choice is the lead's): (а) value 2 = В8 "skip + keep dirty" (skip the host `Protect(Read)` but keep
   the pages CPU-dirty so every sync re-uploads — data correct, cost of the host call removed; a mechanism-realistic bound);
   (б) one diagnostic smoke with `KYTY_GPU_MARKERS=2` to name the hung operation (one more TDR); (в) how K14 is decided when
   its ceiling is unmeasurable (the census row R_gpu 2 107,9 µs/row, ro part 1 488,9 µs, is a census, not a wall — s. 121 items 8–9).
2. `s3s128` (K3): run it anyway, or drop it with the knob value 1.
3. For step 7: `smk128` prints the LAST death marker (`--- Fatal Error ---`); the informative line is the device-lost text
   (`vkQueueSubmit failed: ErrorDeviceLost` / `vkWaitSemaphores failed`) — print both? (row, no rule change).

**Not proven:** which GPU operation hangs; that value 2 would live; any effect of `protceil` on time (0 pairs); OLD regime;
other scenes.

## Step 6a — code of the value `protceil=2`, the dose at the call site (Emu Engineer, HPP-127; ROADMAP s122 p. 93(г)(1), (д))

**Commit:** `04ae3390` on `main` (no push), one commit, 6 files, +55/−10; `git status --short -- src` empty after it.
**Measurement build:** sha256 `45d365126cca16fb54519aef8878040be37b4a243a577914124eb09cdac35c3a`, built from the committed
tree (embedded label `04ae339-dirty` — the dirty mark is the untouched `3rdparty/nlohmann_json` submodule and untracked
`.claude/`, as in `b037d3dd` = `252b0c7-dirty`), pinned copy `C:/kyty/s128/kyty_emulator_45d36512.exe`.
**Installed build unchanged:** `ps5 em/kyty_emulator.exe` = `9235a7ac…` (the shipped build of step 0; `build_local.cmd` only
writes `C:/kyty/build/install`). `check_gate_order.py` (`C:/kyty/s96`): **`GATE ORDER: clean`** after the patch and before the
build (no new name — only the knob maximum 1 → 2; the `UNMATCHED` lines are the name heuristic, as in step 4). Game not run in
this step; **no smoke — WIP until step 6в.** No sealed lock at any moment of the step.

| event (time scale: UTC) | time |
|---|---|
| patch script written, dry run, applied (`step6a/patch_s128_6a.py`, sha256 `3416d026…`) | 12:47:30–12:47:40 |
| compile-check build from the working tree (`0b9f0bfa…`, discarded) | 12:47:46–12:48:13 |
| commit `04ae3390` | 12:48:33 |
| build from the committed tree (6 objects: git version header), copy pinned | 12:48:34–12:49:01 |
| `shader_cfg_tests` build / `memory_tracker_tests` build and run / `shader_cfg_tests` run | 12:49:12–12:49:34 / 12:49:55 / 12:49:55–12:49:56 |

**What changed (files):**
- `common/gates.cpp`: row `{"KYTY_PROT_CEILING", "protceil", 0, 2}` (max 1 → 2; still the LAST row); `common/gates.h`: comment.
- `graphics/host_gpu/pageManager.cpp`:
  - new latch state `CeilDose = 4` (latched 2). `CeilScope` reads the knob once per synchronization exactly as before
    (nested scopes inherit; inside the re-arm pass the latch is 0 without reading). At 2: with the FrameStats clock
    (`FS::Enabled()`, i.e. `KYTY_FRAME_TRACE` or `KYTY_AV_TRACE` — the same condition under which `Protect` takes `t0` and
    computes `ns`) → `CeilDose`, one line `ProtCeil: mode 2`; without it → `CeilRefused` (the path of 0, nothing eligible),
    `pc_refuse` +1, one line `ProtCeil: refused reason=noclock`. Latches of 2 are counted in `pc_op0` (`pc_op1` stays "latched 1").
  - `Protect`: the `pc_elig_*` condition is `arm != No && (state == CeilZero || state == CeilDose)` — the same predicate
    `arm` (p. 89(з)) inside the same `t0 != 0`, not-worker, `ThreadRole::Gpu` block, so `pc_elig_*` at 2 = as at 0. Inside it,
    at `CeilDose` only: after all counters of the call, `d0 = FS::NowNs(); while (d1 − d0 < ns) { YieldProcessor(); d1 =
    FS::NowNs(); }`, then `pc_dose_n` +1, `pc_dose_ns` += `d1 − d0` (ns actually spun, ≥ `ns`; overshoot one pause + one
    `NowNs`). The call itself is made unchanged; `prot_gpu_*_ns`, `prot_gpu_us`, `ProtectNs`, `pc_elig_ns` hold `ns` of the
    call alone. `ProtectRun` / the flush path test `CeilSkip` only, so at 2 nothing is skipped and no U bit is set; the
    re-arm (`RenderContext::ProtCeilRearm`, unchanged, returns while the knob ≠ 0 and has an empty list anyway) never runs.
  - `pc_offthr` (synchronizations off the GuestGpu thread) now counts at knob ≠ 0 (was `== 1`); at 0 and 1 identical.
- `common/frameStats.h`: counters `PcDoseN`, `PcDoseNs` appended after `PcVfyURo` (end of `Counter`, before `Count`);
  comments of `pc_refuse`/`pc_offthr`. `graphics/presentation/videoOut.cpp`: rows `pc_dose_n`, `pc_dose_ns` after
  `pc_vfy_u_ro` (raw, `micros=false`; `pc_u_live` still the last field). `graphics/host_gpu/pageManager.h`: comment.
- `src/graphics/shader/**` untouched — translation cache signature unchanged. `bufferCache.cpp`, `renderContext.*`,
  `graphicsRun.cpp`, `Region` layout untouched (`sizeof(Region)` 1312, `static_assert` compiled).

**At 0 and 1 (p. 93(г)(1) "0 — прежний путь побайтно; 1 — без изменений"):** the only 0/1-visible edits are an `||` term that
is false unless the state is `CeilDose` (reachable only from a latch of 2), a `!= 0` in place of `== 1` in the off-thread row
(same truth value at 0 and 1), a new `else if (value == 2)` branch after the value-1 branch, two counters at the end of the
enum and two printed rows. Byte-equality of the 0/1 path against `b037d3dd` — step 6б (Red Team).

**Tests (logs `C:/kyty/s128/step6a/`):** `memory_tracker_tests` — `all cases passed`; `shader_cfg_tests`
(`KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1`, 127 tests — the same sorted list as step 4) — two failures `IMAGE_SAMPLE_C` /
`IMAGE_SAMPLE_C_LZ`, identical sorted `failed` lines to `step4/shader_cfg_tests.log`: **delta 0 against step 4.** No test
exercises the knob (the latch is opened only by `BufferCache` on GuestGpu).

**Notes for step 6б / the lead (not decided by the engineer):**
1. The dose spins **after** the `sync_waiters` bracket of the call (the bracket is inside the timed span of `ns`; moving it
   would change the path of 0): during the dose the protection worker is not paused, and the kernel-side effects of a call
   (TLB shootdown etc.) are not reproduced — both on the side p. 93(г)(2) already names ([U], Δ a lower estimate).
   The dose does run under the region `lock`/`apply` the call was made under (as the call itself).
2. Refusal reasons at 2 are only `noclock`; `armdefer` / `protbatch2`+`protbatch` are NOT refusals at 2 (no skip, so no
   missing data; with them fewer calls are eligible and the delivery guard Σ`pc_dose_ns`/Σ`pc_elig_ns` stays exact). Without
   the clock `FS::Add` is a no-op, so `pc_refuse` cannot be read in that case — the witness is the log line.
3. `ProtCeilRearm` still returns at knob ≠ 0: a U set by a latch of 1 would survive a 1 → 2 edge until a 0 (not in the
   `pd128` arms `0|2`; the guard Σ`pc_u_set` = 0 covers it).

**Mutants:** none in this step (0 min).

**Not proven:** that value 2 lives in the game; that the dose is delivered at the ratio [0,95; 1,10] (step 6в); byte-equality
of 0/1 by review (step 6б); any effect on time; OLD regime; other scenes.

## Step 6b — code review of the value `protceil=2` (Red Team, HPP-128; ROADMAP s122 p. 93(г)(1), (д))

**Verdict: PASS — NOT BLOCKING.** 0 MAJOR / 4 MINOR (all for step 6в / step 7 texts and harness; no code change required).
Reviewed: `git diff 252b0c76 04ae3390 -- src` (step 4 `55841100`+`252b0c76` = source of `b037d3dd` → step 6a `04ae3390`),
6 files, +55/−10; context read: `pageManager.cpp` `Protect` (:326–449), `ProtectRun` (:465–478), flush path (:1015–1035),
`CeilScope` (:1495–1564); `renderContext.cpp:222–229`; `graphicsRun.cpp:684–694`, `:805`; `bufferCache.cpp:838`;
`frameStats.cpp:161–165` (`Enabled`), `:199–211` (`NowNs`). `check_gate_order.py` (`C:/kyty/s96`) re-run by the reviewer on
the committed tree: **`GATE ORDER: clean`** (3 `UNMATCHED` lines — the name heuristic, as in steps 4–5). No lock at any moment
of the step; no build, no game, no mutants (0 min).

| event (time scale: UTC) | time |
|---|---|
| review started (lock absent) | 12:52:14 |
| `check_gate_order.py` | 12:54 |
| section written | 12:55:01 |

**Checklist of p. 93(д) — each item with the evidence:**
1. **0 and 1 — the executed path as in `b037d3dd`: YES.** The only edits reachable at 0/1: (а) `pageManager.cpp:415` the
   `pc_elig` condition gains `|| t_ceil_state == CeilDose` — `CeilDose` (=4) is assigned only at `:1543` inside `value == 2`,
   so at 0 (`CeilZero`) and 1 (`CeilSkip`/`CeilRefused`) the truth value is unchanged; the inner `if (CeilDose)` (`:424`) is
   false. (б) `:1499` `!= 0` in place of `== 1` — same truth value at 0 and 1. (в) the new `else if (value == 2)` (`:1536`)
   follows the value-1 branch and is not entered at 0/1. (г) `Counter::Count` +2 and two new `FrameTrace-x` fields (see
   MINOR 4) — the output text of 0/1 is not byte-identical (two zero fields), the executed path is. Skip sites still test
   `CeilSkip` only (`:467`, `:1027`); re-arm trigger unchanged (`renderContext.cpp:223`).
2. **Dose only on GuestGpu: YES.** `t_ceil_state` is `thread_local` (`:1244`, `:1268`); a non-outside state is set only by an
   engaged `CeilScope`, engaged only with `GuestGpu::IsGpuThread()` (`bufferCache.cpp:838`); the dose sits additionally inside
   `!worker` and `CurrentRole() == Gpu` (`:368`, `:394`); the role is registered on the same thread before `g_gpu_thread`
   (`graphicsRun.cpp:690–693`).
3. **Only inside `CeilScope`: YES.** `CeilDose` lives from `:1557` to the RAII restore `:1562`; nested scopes inherit the
   outer latch (`:1506–1507`); the re-arm pass latches 0 without reading the knob (`:1510`).
4. **Only by the `pc_elig` predicate: YES, and it is the skip predicate of 1.** The dose is nested in the same
   `if (arm != Arm::No && …)` that counts `pc_elig_*`; `Protect` receives `arm != No` at exactly two sites (`:470`, `:1032`),
   and they are exactly the two sites where a latch of 1 skips (`:467`, `:1027`) — dose ⇔ skip at 1 call for call.
5. **Clock of the dose = clock of `ns`: YES.** `ns = FS::NowNs() − t0` (`:348`, `:364`); the dose spins on `FS::NowNs()`
   (`:428–433`) until `d1 − d0 ≥ ns`; `pc_dose_ns` = `d1 − d0` actually spun (overshoot one `NowNs` + one pause; at ≈ 9,7 µs
   per eligible call — `pc_elig` 1 446,9 µs / 149,8 calls in `s1s128`, Step 6 — the overshoot is ≈ 0,3 %, inside the
   delivery guard [0,95; 1,10]). A descheduled spin is recorded honestly (ratio grows) and caught by the guard.
6. **`prot_gpu_*_ns` without the dose: YES.** `ProtectNs`, `ProtectRwNs`, `ProtectSpin*`, `ProtectGpuNs` (→ `prot_gpu_us`,
   `videoOut.cpp:1427`), `ProtGpuRo/Na/RwNs`, `PcEligNs` are all added with `ns` before the dose (`:366–423`); the dose adds
   only `PcDoseN`/`PcDoseNs`.
7. **At 2 no U and no re-arm: YES.** U is set only by `SkipRun`, reached only at `CeilSkip` (`:467–468`, `:1027–1028`); at 2
   `ClearUnarmed` runs as at 0; `ProtCeilRearm` returns at knob ≠ 0 (`renderContext.cpp:223`).
8. **Refusal without the clock: YES**, on the same condition as the clock of `Protect` (`FS::Enabled()`, `:1540` vs `:348`):
   state `CeilRefused` = the path of 0 without `pc_elig`, one line `ProtCeil: refused reason=noclock` (separate `logged` static,
   no bit collision with value 1). See MINOR 1.
9. **Knob order:** no new name; row `{"KYTY_PROT_CEILING", "protceil", 0, 2}` stays the LAST row of `KNOB_DEFINITIONS`,
   `ProtCeiling` the last `Knob` before `Count`; `GATE ORDER: clean`. `src/graphics/shader/**` untouched — translation cache
   signature unchanged. Stack: two `uint64_t` locals, no frame concern.

**Findings (MINOR, none blocking):**
- **MINOR 1 — `pc_refuse` for `noclock` is dead** (`pageManager.cpp:1546`): without `KYTY_FRAME_TRACE`/`KYTY_AV_TRACE`
  `FS::Add` is a no-op, so the counter can never read non-zero in the only case it is added. Failure scenario: a `pd128` arm
  that silently runs refused would pass a guard "Σ`pc_refuse` = 0". In practice no `FrameTrace-x` exists then either, so the
  scorer is NOT_EVALUABLE — but the refusal witness is the log line only, and `pc_op0` merges latches of 0 and 2 (no latch
  counter of 2). **Change (step 7 scorer / step 6в smoke):** positive witness of the arm-2 latch — exactly one line
  `ProtCeil: mode 2` in the log and Σ`pc_dose_n` > 0 in every arm-2 block of the window 10–88 p. 55(б); 0 lines
  `ProtCeil: refused` (already in p. 93(г)(3)). Owner: Harness Engineer.
- **MINOR 2 — the dose extends the hold of the locks the call was made under** (`:424–436` inside `ProtectRun` under the
  region lock / the flush path under `apply`), and runs after `sync_waiters` is released (`:359–361`), so the protection
  worker is not paused during it. Failure scenario of interpretation: a guest thread faulting on a page of that region during
  the dose waits up to 2·`ns` instead of `ns`; Δ `pd128` then contains that extra wait on other threads, not only GuestGpu
  time — the text "чувствительность `dt` к времени этих вызовов на GuestGpu" (p. 93(г)(2)) would understate what is dosed.
  The direction is consistent with a ceiling (removing the arming removes that wait too), so no code change. **Change:**
  `pred/01_pd128.md` names it next to the [U] of p. 93(г)(2) (lock hold dosed; worker pause and kernel-side effects not).
  Owner: Harness Engineer (step 7 text), lead to accept.
- **MINOR 3 — a 1 → 2 edge leaves U un-re-armed** (`renderContext.cpp:223` returns at knob ≠ 0): pages unarmed by a latch
  of 1 stay unwatched while at 2, guest writes to them lost. Not reachable in arms `0|2`; it stays a guard, not a row:
  Σ`pc_u_set` = 0 over the whole run and harness refusal of `protceil=1` in every gate file / arm of s128 (p. 93(б)).
  Owner: Harness Engineer (keep both).
- **MINOR 4 — `FrameTrace-x` gains two fields at every value** (`videoOut.cpp:3132–3134`, `pc_dose_n`, `pc_dose_ns` after
  `pc_vfy_u_ro`; `pc_u_live` still last). Failure scenario: a smoke/scorer fixture that pins the exact field list of step 6
  (`smk128`) rejects every line of the new build, or a parser by position shifts by two. **Change:** step 6в `EXPECT`/`PINNED`
  = `45d36512…` with the new field list, a fixture line carrying both new fields (trap of s. 105 in `ps5 em/CLAUDE.md`: a derived scorer is checked on a line
  with every new field). Owner: Harness Engineer.

**Not verified by this review:** that `C:/kyty/s128/kyty_emulator_45d36512.exe` is built from `04ae3390` (no rebuild by the
reviewer — the FACTS Step 6a claim stands as the engineer's); that value 2 lives in the game; the delivery ratio; linearity
of the dose; any effect on time; OLD regime.

## Step 6c — smoke of the dose value `protceil=0|2` (Harness Engineer, HPP-129; ROADMAP s122 p. 93(г)(3), (д), 94(в), (е))

Time scale of this section: **UTC** (`go128a.log` and the json write local time = UTC + 2 h; converted here). Build under
test: pinned `C:/kyty/s128/kyty_emulator_45d36512.exe` (`45d36512…`, step 6a). Chain `go128a.sh` `cbdfbe69…`, base
`gates_base.txt` `606da34a…` (unchanged; `rtskip=1` and `protceil=0` from the base, arms by the schedule). Sky Garden,
`KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, no `KYTY_GPU_CHECKPOINTS`, no video (envchk128 PASS). One attempt.

| event (time scale: UTC) | time | evidence |
|---|---|---|
| harness edits (`step6c/edit_go128a.py`, `step6c/edit_test_go128a.py`), fixtures run | 13:00–13:06 | below |
| `s4s128` requested / `procload` clean / idle128 IDLE (GPU 1 %) / installed `45d36512` | 13:06:53 / 13:07:17 / 13:07:17 / 13:07:34 | `go128a.log` |
| launched; level stable at 15,9 s; hold 150,2 s | 13:07:38; hold 13:07:54.0–13:10:24.2 | `s4s128.json`, `gpuclk_s4s128.csv` |
| run end rc 0; hostdev RUN_CLEAN; shipped build restored, sha `9235a7ac…` checked | 13:10:30 / 13:10:31 / 13:10:31 | `go128a.log`, `sha256sum` |

**Harness (constants and a tag of the same form, p. 91(г), 94(е); no stage logic besides the refusal of p. 93(б)):**
`go128a.sh` `cbdfbe69…`: `EXPECT`/`PINNED` = `45d36512…` / `C:/kyty/s128/kyty_emulator_45d36512.exe`; new smoke tag
**`s4s128`** (ABBA `90+1800` `protceil=0|protceil=2` on `gates_base.txt`, hold 150, one attempt inside the call, envchk
`--abba --no-rec`); **value 1 refused** (p. 93(б)): a schedule arm or the gate file of the tag carrying the word `protceil=1`
→ rc 1 `value 1 refused` after the lock and configuration checks, before DRY and any guard (so `s1s128`, `s2s128`, `s3s128`
and `pc128` now refuse). `test_go128a.py` `5323738f…`: **264 checks `ALL OK`** (older stage fixtures of pc128 0|1 /
s1–s3s128 run on variants with the refusal disabled; the refusal on variants keeping it: v1–v6, word boundaries
`protceil=10`/`xprotceil=1`/`protceil=21` not refused, `protceil=1` in any arm or in the gate file refused; full path g8 of
`s4s128`); negative control — the same suite on the pre-edit chain `step6c/go128a.pre6c.sh`: FAIL (c2a, v1–v6, g8, …).
Readout **`smk128d.py` `f7839d41…`** (new file; imports `smk128.py` parse/blocks, adds the two fields to its kept list) +
**`test_smk128d.py` `3ea10a78…` 36 checks `ALL OK`**: a row with both new fields; an arm-2 block without `pc_dose_n` (field
missing → S4 FAIL; zero → S4 FAIL); window edges 9/10/88/89; delivery edges 0,95 / 1,10; ProtCeil lines; arm by GateArm
TEXT. Negative controls (sabotaged copies): S4 → 6 FAIL, band → 2, fields not parsed → 11, S6 → 1, old hold rule → 1.
**Mutant runs of this step: none (wall sum 0 s).**

**My defect, disclosed:** the first readout (`step6c/smk_s4s128.prefix.txt` `fd2c05f2…`) printed `NOT PASSED` on S1 only
because survival required `hold_s == requested` (copied from `smk128.py`); `enter_scene.py` records the measured hold (150,2
of 150) and itself fails only `hold_s < hold` (`enter_scene.py:659`). Fixed to `>=`, fixture d2b (150,2 / 150,0 pass; 149,9 /
None fail; fails on the pre-fix text). `smk128.py` of step 6 carries the same `==` (both of its runs died, so it never
decided anything); not edited.

**Smoke conditions (p. 93(г)(3), 94(в)) — all PASS → SMOKE PASSED** (`step6c/smk_s4s128.txt` `6790b665…`, json
`b17a53c1…`; log `log_s4s128.txt` `9bda743e…`, `s4s128.json` `af874afa…`):
- S1 survival: outcome ok, hold 150,2 of 150, `hold_exit` None, ft_tail 152, **no death marker, no `ErrorDeviceLost` line**,
  hostdev RUN_CLEAN (no host event); `GpuWaitSlow:` 0, `BvhLoopCapTrip:` 0.
- S2 exactly one `ProtCeil: mode 2`, no `mode 1`; S3 0 `ProtCeil: refused`.
- S4 **positive witness of arm 2 (p. 94(в)): Σ`pc_dose_n` > 0 in every one of 16 arm-2 blocks** (window 10–88 of p. 55(б),
  10 633…11 304 per block); 0 window rows without the two fields.
- S5 **dose delivery Σ`pc_dose_ns` / Σ`pc_elig_ns` = 1,0094** over 1 264 arm-2 window rows (per block 1,0059…1,0142), in
  [0,95; 1,10].
- S6 Σ`pc_dose_n` arm-0 window rows (1 286) = 0 (row: 2 on arm-0 positions 0–9 — an operation latched in the previous arm-2
  block; outside the window).
- S7 whole log Σ`pc_u_set` 0, Σ`pc_skip_n` 0, Σ`pc_refuse` 0 (rows: `pc_op1` 0, `pc_offthr` 0).
- S8 GateArm texts only `protceil=0` / `protceil=2`; 33 blocks from frame 1800, 32 complete.

**Rows (not a verdict; Δ of the dose is a ceiling row, never a gain; p. 93(г)(2), (е)):** BDA regime **OLD in every block**
(`bda_scan` window 1 310…1 572; arm 0 1 499,4, arm 2 1 490,9) — this run is OLD, the step-6 run `s1s128` was NEW; levels
of different regimes are not compared. **Δ `dt_us` (arm 2 − arm 0) = +995,0 ± 269,4 (2SE) µs over 16 pairs, all OLD/OLD**
(pairs +210,9…+1 963,7); Δ draws −4,3. Levels (window rows of complete blocks, arm 0 / arm 2): `dt_us` 32 672,4 / 33 667,4;
`cpu_gpu_us` 31 681,9 / 32 711,4 (+1 029,5); `gpu_busy_us` 13 878,8 / 13 766,5; `pc_elig_ns` 1 422,3 / 1 330,3 µs
(`pc_elig_n` 139,3 / 138,2); `pc_dose_ns` 0 / 1 342,7 µs; `prot_gpu_us` 1 709,7 / 1 618,0; `pb_wait_gpu_us` 184,2 / 120,8;
`fw_n` 1 231,9 / 1 240,9; `rts_skip` 4 421,6 / 4 418,0; `bl_trip` 0. Independent recount `step6c/recount6c.py`
`6e2d9de7…` (no shared code): delivery 1,00935, arm-0 window dose 0, no zero arm-2 block, 16 pairs Δ +995,02 ± 269,37 —
to the digit.

**Questions to the lead (no decision taken):**
1. The smoke ran in the OLD regime (16/16 pairs); `pd128` needs ≥ 10 pairs per regime (p. 93(г)(4)); the regime is a
   state of the run — no action proposed by me, a row for step 7/8.
2. Arm-2 call time `pc_elig_ns` is 92 µs/row lower than arm 0 (1 330 vs 1 422): the dose is measured against the call time
   of its own arm (delivery 1,009); the dose-free call time of arm 2 is lower — a row for the text of `pred/01_pd128.md`
   (step 7)?
3. S1 survival rule in `pd128`: `hold_s >= requested` (as fixed here), not equality.

**Not proven:** that Δ `pd128` will be as here; linearity of the dose; that Δ equals the gain of any mechanism; NEW regime of
value 2; other scenes; 60 FPS not promised.

## Step 7 — scorer, fixtures, seal `pred/01_pd128.md`, one full `mutlib` (Harness Engineer, HPP-123; ROADMAP s122 p. 93(г)(3)–(4), 94(в)–(е), 95(в)–(г))

Time scale of this section: **UTC** (file times read with `date -u -r`; `go128a.log` writes local time = UTC + 2 h, one line
of this step there — the DRY refusal of `pc128` at local 16:53:56 = 14:53:56 UTC). No game, no build, no sealed lock at any
moment of the step. Installed build unchanged: `9235a7ac…` (shipped). `pc128` (0|1) is not scored: per p. 93 the seal and the
scorer are for **`pd128`** (arms `protceil=0|protceil=2`).

| event (time scale: UTC) | time |
|---|---|
| step started (blocker `HPP-129` resolved, lock absent), comment on `HPP-123` | 14:12:43 |
| scorer `pd128.py` dry run on the real smoke `log_s4s128.txt` (reproduces the lead's recount of p. 95(а)) | ≈ 14:20 |
| seal `pred/01_pd128.md` written, `PRED_SHA`/`PRED_BYTES` filled | 14:31:50 |
| chain edit; `test_go128a.py` run 1 (7 FAIL — my v5 anchor, see below) / run 2 `ALL OK` / negative control | 14:35:41–14:38:03 / 14:38:32–14:40:59 / ≈ 14:41–14:43 |
| **the one counted full `mutlib` v4.1** (parent No. 1) | 14:43:33–14:48:17 |
| top-up `--only` 5 (p. 74 (б)) | 14:50:11–14:51:20 |
| evidence `checks/pd128_checks.json`, pre-seal gate PASS, `SEALS128.txt` | 14:53:42 / 14:54 / 14:54:41 |

**Files (sha256, `C:/kyty/s128`):** scorer **`pd128.py` `60f128da…`** (carries `PRED_SHA` = `5342cddd…`, `PRED_BYTES` 28 405);
seal **`pred/01_pd128.md` `5342cddd0890ddbfef163f217961ac30c93d0a3ee440a04682f6de2203bfeb86`**; fixtures **`test_pd128.py`
`6f08d967…` — 274 checks `ALL OK`** (synthetic logs; mutlib early-exit form, no subprocess, 23 s); mutants **`mut_pd128.py`
`6afda00a…`** (196); pre-seal gate `chk_pd128.py` `a1aaeb29…`; evidence writer `mk_checks128.py` `2f0ffc1a…` → `checks/pd128_checks.json`
`a1191dfe…`; append check `addonly128.py` `7af831ed…` + `test_addonly128.py` `af49d446…` (26 checks `ALL OK`); `mk_seals128.py`
`7fc28fcd…` → **`SEALS128.txt` `8bc7d81d…`** (43 files by sha256 + the evidence lines); chain **`go128a.sh` `1177b3bc…`**, **`test_go128a.py`
`f9565765…` — 294 checks `ALL OK`**.

**What the scorer reads (p. 93(г)(3)–(4); all constants filled):** blocks by `GateArm:` lines only, the arm by the TEXT
(`protceil=0` / `protceil=2`, any other text — `arms` fails); window positions 10..88 inclusive (p. 55(б)); level = mean of
the window rows; pairs (2k, 2k+1) of complete blocks; BDA regime per block from `bda_scan` of `FrameTrace-draw` (≤ 300 NEW,
≥ 600 OLD), a pair enters a regime only with both blocks of it, the rest counted by direction; simple Δ and adjusted Δ (β by
p. 77(б)), SE by pairs; per regime with ≥ 10 pairs `K14_OPEN` at min(Δ − 2SE) ≥ +500 over both estimators, `K14_CLOSED` at
max(Δ + 2SE) < +500 over both, else `NOT_RESOLVED`; < 10 pairs — `DEBT` (not read); T = OPEN in any read regime, else CLOSED if
every read regime is CLOSED, else `NOT_RESOLVED`; `DRS_MIXED` (p. 78(е), exact rationals, 1 %) → `NOT_RESOLVED`; no pair —
`NOT_EVALUABLE`. **Guards `NOT_ADMITTED`** (p. 93(г)(3), 94(в)): exactly one `ProtCeil: mode …` line and it is `mode 2`; 0
`ProtCeil: refused`; both dose fields on every `-x` line of a window row; Σ`pc_dose_n` > 0 in the window of every arm-2 block
with window rows (at least one); delivery Σ`pc_dose_ns`/Σ`pc_elig_ns` of the arm-2 window rows in [0,95; 1,10] (integers);
Σ`pc_dose_n` = 0 on the arm-0 window rows; whole log Σ`pc_u_set` = Σ`pc_skip_n` = Σ`pc_refuse` = 0; base = the words of
`gates_base.txt` `606da34a…` with `rtfast=1`, `rtskip=1`, `protbatch2=0`, `armdefer=0` (p. 92(е)), exactly one `protceil=` word
= `protceil=0` (p. 88(к)), no arm text naming those names; markers of p. 89(г) (`ErrorDeviceLost`, `GpuHangAbort:` …) → `FAIL`;
**survival p. 95(г)**: measured `hold_s` of the attempt ≥ the requested `hold_s` of the json and `hold_exit` empty (fixtures
150,2/150 pass, 150,0/150 pass, 149,9/150, missing, `True`, `'150.2'` fail). **Rows only** (p. 93(г)(3)): levels by arm and
regime incl. `pc_elig_ns`, `pc_elig_n`, `pc_dose_ns`, `pc_dose_n` and Δ / `pc_dose_ns` of arm 2 (p. 95(в)); `R_gpu` (p. 89(б));
`CARRYOVER` (p. 89(в)(2), 92(д)); T1/T2 (p. 89(ж)); T6 with signed `pc_u_live` (p. 92(г)); Σ`pc_rearm_n` (p. 88(б)); K2 (p. 88(д));
inflation rows (p. 87(е)(3)); BDA rows; `GpuWaitSlow:` / `BvhLoopCapTrip:` by arm; base p. 87(е)(7). The caveats of p. 93(г)(2)
and the lock-hold text of p. 94(г) are in the seal (§10) and printed by the scorer beside Δ.

**Real-log check (pre-seal gate, `chk_pd128.py --tag pd128` PASS):** the scorer on `log_s4s128.txt` (plan `s4s128`, hold 150,
the pinned build as installed) → `NOT_ADMITTED` failing exactly `prereg`, `prereg_sha` (every dose guard, survival, base,
env, host, streams pass); 16 pairs, all OLD; rows **Δ `dt_us` +995,0 ± 269,4**, adjusted **+1 024,1 ± 240,5** (β 6,7634 µs/draw),
Δdraws −4,3 ± 26,9, Δ`cpu_gpu_us` +1 029,5 ± 236,2, Δ`gpu_busy_us` −112,3 ± 55,4; delivery **1,00935** (1 264 arm-2 window rows);
`pc_elig_ns` arm 0 / arm 2 1 422,3 / 1 330,3 µs, `pc_dose_ns` 1 342,7 µs, Δ / `pc_dose_ns` 0,741; DRS 2 007,45 / 2 007,42 — not
mixed. **Equal to the lead's recount of p. 95(а) to the digit** (+995,02 ± 269,37, 1,00935, 16 pairs). A row of the smoke,
not a verdict and not in `pd128` (p. 95(б)).

**Chain (p. 84(в)(2): constants and a tag of the same form — fixtures and `ALL OK`, no chain mutants):** `go128a.sh`
`cbdfbe69…` → `1177b3bc…` by `step7/edit_go128a.py` (whole-line anchors): `PRED="pred/01_pd128.md"`, `SC="pd128.py"`,
`CHK="chk_pd128.py"`; tag **`pd128`** = the branch of `pc128` with `$KNOB=0|$KNOB=2` (fixture c17b: the branch equals the
`pc128` branch with that one replacement); header and usage. `DRY=1 go128a.sh pd128` prints: lock?; procload 540; cpu; idle128;
procload 0; lock; install `45d36512`; `enter_scene.py pd128 … --attempts 1 … --gates-file gates_base.txt --hold 300
[KYTY_GATE_SCHEDULE=90+1800:protceil=0|protceil=2] KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0`;
hostdev; envchk `--sealed`; scorer `pd128.py --tag pd128 --out runs128/pd128.score.json`; restore `9235a7ac` (registered 1, one
attempt 1). `pc128` still refuses (`value 1 refused`). `test_go128a.py` `5323738f…` → `f9565765…` (section 13: p1–p10 on
variants keeping the value-1 refusal — seal empty/partial, bad hold, DRY, pred sha, pre-seal refusal, full run args/envchk
sealed/scorer/marker/restore, repeat, marker isolation; `pd128` added to TAGS/ONES/PINS so the lock, config, attempt, build,
base and after-install fixtures cover it): **294 checks `ALL OK`**; negative control — the new suite on the pre-edit chain
`step7/go128a.pre7.sh`: **29 FAIL**, all of `pd128`. **My defect, disclosed:** run 1 of the suite failed 7 checks (v5) because
their anchor — the `SCHED` line of `s4s128` — now occurs twice (`pd128` has the same line); fixed by anchoring the two lines of
the `s4s128` branch (`step7/edit_test_go128a_v5.py`), fixture text only.

**Mutants (p. 84(в)(5), 85(в), 74, 86(в)):** the **one counted full run** (parent No. 1) on the final scorer text with the seal
constants filled — `old/run1_pd/mut_pd128.run1.txt` `cb5b6944…`: header **`fast on` (161 guarded updates), `workers 28`**,
BASELINE / BASELINE#2 SURVIVED (34,6 / 34,4 s), fixture replay on, **wall 283,6 s (≤ 15 min)**; **191 of 197 killed** (7 by a
crash of the suite), controls 3/3, **6 survivors**: `num_bool`, `arms_dup`, `p_gatearm_strip`, `pred_bytes`, `v_admit` (holes of
the fixtures) and `p_gatearm_nocr` (equivalent). **Top-up by p. 74 (б)** (the rule of s. 127, p. 86(г)): five cases t1–t5
APPENDED after every earlier case right before the closing block (`step7/topup_pd128.py`; `addonly128.py` PASS: prefix 866
lines byte for byte, 17 lines added, closing block 3 lines the same; the appended text binds `ok` only as `ok &=`, no exit);
`p_gatearm_nocr` removed with an EQUIVALENT proof in the docstring of `mut_pd128.py` (`rstrip(b'\n')` leaves a CR that the
regex puts into the text group and `.strip()` removes); `--only` the 5 → `mut_pd128.add.txt` `ad25521c…`: **5 of 5 killed**,
controls 3/3, workers 8, wall 69,3 s. `mk_checks128.py` (parent + top-up mode, port of `mk_checks127.py`) certifies **196 of
196 killed, 0 survived, 0 unresolved**. **Mutant wall of the step: 283,6 + 69,3 = 352,9 s (5,9 min)**; session budget p. 87(б)(3)
(without the counted full run): 1 655 s (step 1, p. 91(г)) + 69,3 s = **1 724,3 s = 28,7 of 30 min**. `chk_pd128`, `mk_checks128`,
`addonly128` — no mutants (budget; `addonly128` has its fixture set).

**Questions to the lead (no decision taken):**
1. The seal §11 says "ОДИН полный прогон"; the certification is parent No. 1 + a top-up of 5 by p. 74 (б) with one EQUIVALENT
   removal (as in s. 127, p. 86(г)). The seal was not edited after the full run (its sha is in the scorer; an edit would void
   the full run). Accept the parent + top-up as the certification of p. 84(в)(5)?
2. Guards I put into the seal beyond the letter of p. 93(г)(3)/94(в), named there (§6, §7): `rtskip_live` (exactly one
   `RtSkip: mode 1`, 0 `RtSkip: refused` — the shipped state of both arms, p. 87(е)(5)/(7)), `rts_guards` (`rts_xthr` =
   `rts_acqw` = `rts_refuse` = 0 on window rows), `dose_fields` on arm-0 rows too, and `pbcheck`, `armcheck` in the absent-or-0
   list of the base. All pass on the real smoke log. Accept?
3. "Режим без ≥ 10 пар — долг" is printed as the per-regime label `DEBT` and a list; T with only debt regimes is
   `NOT_RESOLVED` (no read regime). Accept the reading?

**Not proven:** any number of `pd128` (not run); that `pd128` will reach ≥ 10 pairs in one regime; linearity of the dose; the
share of other threads' lock wait in Δ; that Δ equals the gain of any mechanism; 60 FPS not promised.

## Step 8 — the sealed `pd128` and its scoring (Harness Engineer, HPP-124; ROADMAP s122 p. 93(г)(3)–(4), 94(в)–(г), 95(в)–(г), 96(д))

Time scale of this section: **UTC** (`go128a.log`, `pd128.json`, `hostdev_pd128.txt` write local time = UTC + 2 h; converted
here). Per p. 93 the sealed run is **`pd128`** (arms `protceil=0|protceil=2`), not `pc128`; the chain still refuses `pc128`.
Seal `pred/01_pd128.md` `5342cddd…`, scorer `pd128.py` `60f128da…`, chain `go128a.sh` `1177b3bc…`, pre-seal check
`chk_pd128.py` `a1aaeb29…` — the files accepted in p. 96(а), checked by sha before the run (and by the chain inside the lock).
One attempt, no video, Sky Garden, `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, no `KYTY_GPU_CHECKPOINTS`.

| event (time scale: UTC) | time | evidence |
|---|---|---|
| step started; sha of the sealed files checked; lock absent; no `pd128.json`/marker; `DRY=1 go128a.sh pd128` rc 0 | 15:00:07 | this section, comment on `HPP-124` |
| `procload.py --wait-s 540` call 1 — **busy the whole 540 s** (a foreign user process ≈ 3,2–4,3 CPU s/s + browser), rc 1 | 15:00:16–15:09:05 | terminal output |
| `procload.py --wait-s 540` call 2 — clean after ≈ 380 s, rc 0 | 15:09:17–15:15:38 | terminal output |
| `PLWAIT=0 go128a.sh pd128` requested (foreground, right after call 2) | 15:15:42 | `go128a.log` |
| procload clean; `chk_pd128` PASS; CPU 3 %; idle128 IDLE (GPU median 0 %); procload clean | 15:15:42–15:16:25 | `go128a.log` |
| installed before `9235a7ac…`; installed `45d36512…`; attempt marker; `pd128 start` | 15:16:25 | `go128a.log`, `attempt_pd128.txt` |
| emulator launched; level stable at 16,4 s; hold 300,0 s | 15:16:29; hold 15:16:45.8–15:21:45.8 | `pd128.json`, `gpuclk_pd128.csv` |
| run end rc 0; hostdev RUN_CLEAN; envchk PASS; scorer rc 0 **`K14_OPEN`** inside the lock | 15:21:51 / 15:21:53 / 15:21:53 / 15:21:58 | `go128a.log` |
| shipped build restored `9235a7ac…` (checked by the chain and again by me), lock removed | 15:21:59 | `go128a.log`, `sha256sum` |

**Verdict of the seal (§2, §5; printed by the scorer verbatim):**
`ADMISSION: ADMITTED` · `READING (item 93 (г)(4)): T = K14_OPEN; debt regimes (< 10 pairs) -` · **`VERDICT: K14_OPEN`** ·
`CONSEQUENCE: K14_OPEN - the ceiling of the GuestGpu arming time measured by the dose is >= 0.5 ms in the regime named (item
93 (г)(4)): the K14 track is open; next - a prototype of a mechanism with its own ABBA, the choice is the close of session 128.
Not a gain.`

**Admission — all 35 checks ok** (G1 `binary`, `installed_now`, `installed_before`, `prereg`, `prereg_sha`; G2 `no_marker`,
`alive` (hold 300,0 of 300, `hold_exit` empty), `ft_tail` 160, `gap` (largest `dt_us` 50 726 at frame 7 295 < 5 000 000),
`no_skip_window` (skipped draws 0); G3 `arms`, `gate_lines`, `base`; G4 `dose_mode` (one line `ProtCeil: mode 2`),
`no_refused` 0, `dose_fields` (0 window rows without a field), `dose_blocks` (43 arm-2 blocks with rows, none with Σ`pc_dose_n`
= 0), **`dose_delivery` 4 393 062 927 / 4 360 242 414 ns = 1,00753** (3 344 arm-2 window rows; band [0,95; 1,10]), `dose_zero0`
(Σ`pc_dose_n` of 3 397 arm-0 window rows = 0), `ceil_zero` (whole log Σ`pc_u_set` = Σ`pc_skip_n` = Σ`pc_refuse` = 0),
`rtskip_live` (one `RtSkip: mode 1`, 0 refused), `rts_guards` (`rts_xthr` = `rts_acqw` = `rts_refuse` = 0); G5 `pinned` (one
`GpuClockPin: mode 1`), `gclk`, `env_exact`, `env_forbidden`, `env_vk`, `idle`, `host_clean` (RUN_CLEAN), `host_tool`,
`envchk` (PASS), `hold` 300, `one_attempt`, `stable`, `streams`). Markers of p. 89(г): none; `GpuWaitSlow:` 0 / 0 / 0 and
`BvhLoopCapTrip:` 0 / 0 / 0 (before the schedule / arm 0 / arm 2).

**Blocks and window (p. 55(б)):** 86 blocks by `GateArm:` lines (frames 1 800 + 90·b, texts only `protceil=0` / `protceil=2`),
85 complete (arm 0 — 43, arm 2 — 42), incomplete — block 85 (the end of the hold); window positions 10..88 inclusive, row of
position p = `FrameTrace n` = F + 1 + p (seal §5); level statistic = mean of the window rows of a block. **BDA regime: NEW in
every complete block** (block means of `bda_scan` 44,0…89,4 ≤ 300, p. 40(е)(1)); pairs outside a regime — none.

**Δ by regime (arm 2 − arm 0, ± 2SE over pairs):**

| regime | pairs | Δ `dt_us` simple | Δ `dt_us` adjusted (β 6,6565 µs/draw, p. 77(б)) | min(Δ − 2SE) / max(Δ + 2SE) | Δdraws | Δ`cpu_gpu_us` | Δ`gpu_busy_us` | reading |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| NEW | 42 | **+1 016,8 ± 140,8** | **+1 023,8 ± 118,2** | +876,1 / +1 157,6 | −1,0 ± 14,3 | +1 062,4 ± 134,5 | −118,4 ± 37,9 | **`K14_OPEN`** (+876,1 ≥ +500) |
| OLD | 0 | — | — | — | — | — | — | no pair (not a debt line: the scorer prints `no pair`; debt list empty) |

DRS guard (p. 78(е)): `rt_kpx/rt_att` arm 0 2 007,63 (3 397 rows), arm 2 2 007,59 (3 318 rows), 0 rows with `rt_att` = 0 —
not mixed. **Rows of p. 95(в):** arm 2 mean `pc_dose_ns` 1 314,1 µs/row, **Δ / `pc_dose_ns` = 0,774** (smoke 6c: 0,741, OLD);
`pc_elig_ns` arm 0 / arm 2 = 1 400,2 / 1 304,3 µs per row (`pc_elig_n` 144,8 / 142,5) — arm 2 again lower without the dose
(96 µs; cause [U], p. 95(в)).

**Base (p. 87(е)(7), 93(г)(4)):** mean `dt_us` of the arm-0 window rows **31 700,6 µs** over 43 blocks, all NEW, build
**`45d36512`** (the measuring build at `protceil=0`, `rtskip=1` — the shipped state); speed = 16 667 / 31 700,6 = **52,58 %**.
Not measured against `9235a7ac`/`4fc501f4`, not comparable with 50,36 % (`98d98eee`, `k3p127`, `rtskip=0`) — other build and
run (p. 87(в), 89(к)).

**Levels (window rows of complete blocks, NEW, arm 0 / arm 2):** `dt_us` 31 700,6 / 32 728,9; `draws` 5 037,3 / 5 038,4;
`cpu_gpu_us` 30 918,6 / 31 991,8; `gpu_busy_us` 13 164,8 / 13 043,5; `prot_gpu_us` 1 689,0 / 1 586,4 (ro 1 434,0 / 1 335,5, na
159,4 / 157,5, rw 96,1 / 93,9 µs); **`R_gpu` (p. 89(б)) 1 967,0 / 1 798,1 µs**.
**Inflation rows (p. 87(е)(3); arm 0 / arm 2):** `sync_up_kb` 23 140,0 / 22 650,9; `faults_main` 76,3 / 76,9; `fault_main_us`
1 067,0 / 1 283,1; `pb_wait_gpu_us` 176,6 / 113,4; `faults_gpu` 20,8 / 20,8; `fault_gpu_us` 100,9 / 97,7; `fw_n` 1 230,0 /
1 234,6; `img_up_kb` 100 635,8 / 100 662,8; `tex_inval` 1 233,5 / 1 238,0; `img_pend_kb` 387,5 / 378,5; BDA `bda_scan` 56,8 /
53,0, `bda_ginv_reg` 0,0068 / 0,0060, `bda_ginv_map` 0 / 0; `bl_trip` 0 / 0, `bl_near` 0 / 0.
**Other rows:** K2 Σ`fw_n` arm 2 / arm 0 = 0,9804 (p. 88(д)); Σ`pc_rearm_n` 0 (p. 88(б)); T6 0 − 0 − 0 = 0, last `pc_u_live` 0
(p. 92(г)); T1/T2 (p. 89(ж)) arm 0 −3 / 1 651,9 µs over 3 397 rows, arm 2 −3 / 1 643,6 µs over 3 318 rows (no tolerance written).
**CARRYOVER (p. 89(в)(2), rows; after other − after own, ± 2SE, 21/21 blocks):** arm 0 `dt_us` −10,5 ± 430,1, `fw_n` −3,4 ±
4,4, `tex_inval` −3,6 ± 4,5; arm 2 `dt_us` −122,1 ± 448,4, `fw_n` +4,8 ± 4,5, `tex_inval` +5,0 ± 4,4 (just beyond 2SE, rows;
the carry-over rule p. 89(в)(3) is not in force for `pd128`); all other fields within 2SE. Hold GPU busy median 41,0 % (592
rows, a row).

**Independent recount (no code shared with `pd128.py`):** `step8/recount8.py` `c5a02f4a…` → `step8/recount8.txt` `805f7c2b…`:
blocks by `GateArm:`, positions by `n` = F + 1 + p (asserted for every block), pairs (2k, 2k+1), regime from `bda_scan` of
`FrameTrace-draw`: **42 pairs NEW, simple +1 016,84 ± 140,76, adjusted +1 023,81 ± 118,23 (β 6,6565), Δdraws −1,05 ± 14,30,
delivery 1,00753, arm-0 window dose 0, no zero arm-2 block, base 31 700,6 — equal to the scorer to the digit.** Scorer re-run
after the restore with `--installed-sha 45d36512…` → `step8/pd128.score.txt` `24d207ab…` (ADMITTED, K14_OPEN), its json
`step8/pd128.rescore.json` byte-equal to the sealed `runs128/pd128.score.json` (`b34144ca…`).

**Files (sha256, `C:/kyty/s128`):** `log_pd128.txt` `02da2d235cb3c7e5b4ea0106a7b41c0df3990088576e9720dc5627a1afd45773`
(271 854 606 B); `pd128.json` `964fd604…`; `stdout_pd128.txt` `b4b957b8…`; `hostdev_pd128.txt` `70b2cb57…`; `envchk_pd128.txt`
`562ca8c2…`; `gpuclk_pd128.csv` `002d9060…`; `attempt_pd128.txt` `21052119…`; **`runs128/pd128.score.json` `b34144ca6dfbad8c19078a8a583c293670cd5e46f6f7fd1c66ba7cc223353c43`**;
seal `pred/01_pd128.md` `5342cddd0890ddbfef163f217961ac30c93d0a3ee440a04682f6de2203bfeb86`. Installed after the step:
`9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7` (shipped). **Mutant runs of this step: none (wall 0 s).**

**Disclosed:**
1. My first attempt of the recount sliced the window by the line index after `GateArm:` ([10:89]) and gave +1 020,2 / base
   31 684,4 — one row off: the first main line after `GateArm: frame=F` carries `n = F`, and the seal defines position p as
   `n = F + 1 + p`. Fixed to the seal (index [11:90] with an assert on `n`), equal to the scorer. Before the fix nothing was
   reported.
2. A call `python pd128.py --help` (the scorer has no help) ran a default rescore to stdout only (`installed_now` FAIL — the
   shipped build was already back); it wrote no file (`runs128/pd128.score.json` mtime 15:21:58 unchanged).
3. **Row for the lead, not about this run:** the file `lead/recount6c_lead.py` (`c25a7a46…`) as it is on disk slices
   `main[10:89]` and reads `bda_scan` from `-x` lines; run on `log_s4s128.txt` now it prints Δ **+975,15 ± 247,64** (16 pairs)
   and `bda_scan` 0/0 — not the +995,02 ± 269,37 cited in p. 95(а) (the text of p. 95(а) names n = F + 1 + p, which the file
   does not do). The accepted smoke numbers of step 6c (scorer and `step6c/recount6c.py`) are +995,0 ± 269,4; the sealed
   `pd128` numbers do not depend on it.

**Questions to the lead (no decision taken):** none needed for the reading — the verdict follows §1 of the seal. The choice
of the mechanism prototype (p. 93(г)(4) «выбор — на закрытии с. 128») is the lead's.

**Not proven:** that Δ equals the gain of any mechanism (Δ `pd128` is a ceiling, never a gain, never shipped); linearity of the
dose; the share of other threads' lock wait in Δ (p. 94(г), [U]); kernel-side effects of the call (TLB etc., [U] — Δ is a lower
estimate of the full effect); the OLD regime (0 pairs); other scenes; the base against `9235a7ac`; 60 FPS not promised.

## Step 9 — audit (Session Auditor, HPP-125; ROADMAP s122 p. 87(ж), 93(д))

Time scale of this section: **UTC** (platform API, `TZ=UTC git log`, file `mtime`). Document —
`C:/kyty/s128/audit128/AUDIT128.md` (git `docs/session-128/audit/`). No lock at any moment; no game, no build, no emulator
code, no `mutlib` (**mutant wall of this step: 0 s**). Installed build `9235a7ac…` (sha256 checked, = pinned copy).

| event (time scale: UTC) | time |
|---|---|
| step started (blocker `HPP-124` resolved, lock absent) | 2026-09-28 15:26 |
| `recount128.py` on `log_pd128.txt` (7 s), window rows, smoke `s4s128`, `shp128` sums | ≈ 15:40–15:55 |
| audit document written | ≈ 16:05 |

- **Recount — CONFIRMED to the digit** (`recount128.py`, no code shared with `pd128.py`, `step8/recount8.py`,
  `lead/recount6c_lead.py`; blocks by `GateArm:`, `n = frame + 1 + p`, window 10..88 inclusive p. 55(б), mean of window
  rows, SE over ABBA pairs, BDA from `FrameTrace-draw`). `pd128`, NEW, 42 pairs: **Δ `dt_us` +1 016,84 ± 140,76; Δ_adj
  +1 023,81 ± 118,23 (β 6,656541)** ⇒ lower +876,08 ≥ +500 ⇒ **`K14_OPEN`**; OLD 0 pairs. Base p. 87(е)(7)/93(г)(4)
  **31 700,65 µs** (arm 0, 3 397 rows, 43 blocks, NEW, `45d36512`; 52,58 %; not comparable with 50,36 %). Dose guards:
  delivery 1,00755 (complete blocks) / **1,00753** with the window of incomplete block 85 (= scorer), per block
  1,0032…1,0185, 0 arm-2 blocks without dose, arm-0 window dose 0, whole-log `pc_u_set`/`pc_skip_n`/`pc_refuse` 0; one
  `ProtCeil: mode 2`, one `RtSkip: mode 1`, 0 refused, 0 death markers; DRS 2 007,626 / 2 007,590. Windows 10..87 / 60..88 /
  0..89 — `K14_OPEN` in all (rows).
- Smoke `s4s128` by the same parser: 16 pairs OLD, +995,02 ± 269,37, delivery 1,00935 — equal to §Step 6c. Shipping video
  `shp128`: Σ`rts_skip` 16 989 163 / Σ`rts_n` 19 210 396, one `RtSkip: mode 1`, 0 refused; `ffprobe` 4 026 frames = index;
  0 one-frame glitches; the sheet `sheet_a_o5.png` viewed — same scene, animation phase differs.
- **Protocol: 0 MAJOR, 3 MINOR** (verdict unchanged): (1) the lead recount named in p. 95(а) (`lead/recount6c_lead.py`)
  does not produce the cited numbers — run by the auditor it gives +975,15 ± 247,64, delivery 1,00950, `bda_scan` 0/0
  (slices `main[10:89]`, reads `bda_scan` from `-x`); the numbers of p. 95(а) are right (scorer, `step6c/recount6c.py`,
  audit), the provenance is not; (2) the value-1 refusal added to `go128a.sh` in step 6c is new stage logic (rc 1 before DRY)
  — no `--only` (p. 84(в)(3)) and no stop-and-ask with ≈ 2,4 min of budget left (p. 91(г), 93(д)); covered by fixtures v1–v6
  and a negative control only; (3) OLD (0 pairs) is not in the scorer's debt list while p. 93(г)(4) / seal §5 say "< 10
  pairs — debt". Row: the header of p. 93 says "12:50 UTC", the commit `1369d6ac` is 12:44:45 — before step 6a (12:47:30).
- Load during `pd128` (15:16:25–15:21:59): the only agent run was step 8 itself (`46a54e9b`); no commits; procload clean.
  Video `shp128` overlapped the step-4 Emu Engineer run and a lead acceptance run — not a timed run (row).
- **Not proven:** that Δ `pd128` equals the gain of any mechanism (calibration; linearity [I]; lock-hold wait of other
  threads [U]; kernel side effects [U]); that a mechanism moving the arming off GuestGpu pays (value 1 hung the GPU; `armdefer`,
  `protbatch2` did not pay); OLD; other scenes; the time of the installed `9235a7ac` (base is on `45d36512`); tests of
  `protceil` at 1/2. 60 FPS not promised.
- Debts for the close (`HPP-126`): K14 in OLD; linearity checked by the first prototype ABBA; time of `9235a7ac` / cost of the
  measurement code at 0; `protceil=1` hangs the GPU — into the env record of `CLAUDE.md`; tests at 1/2; MINOR-1…3.
