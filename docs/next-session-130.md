# Session 130 — ship `armcopy=1` (step 0 with the debts of items 103 (б), 104 (б), 105 (б)), then the K14 remainder: the prototype `acinline` (the arming of inline copies moved into the copy pool), sealed ABBA

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 105 (the close of 129: verdict `ARMCOPY_GAIN` (а);
**the shipping conditions (б)(1)–(7)**; audit decisions (в) — the `PLWAIT` rule; the course (г); the re-assessment (д); debts
(е); **the constants of this session (ж)(1)–(7)**; the chain (з)); items 97 (е) (the pattern this session copies), 98–104 (the
accepted design of `armcopy`, RC1–RC11, the null value 4, the reading of `LEFT`, F1–F4, the content-check debt, the lesson
"kill conditions in critical-thread units"), 84–87, 83 (г), 77 (б), 78 (е), 66 (а), 55 (б). `docs/session-129/audit/AUDIT129.md`;
`docs/local-session-129.md`; `docs/session-129/design129.md` ред. 2 (§2–§9: the chunk path, `apply`, the detector, counters);
`docs/session-129/design/codereview129.md` (F1–F4); `ps5 em/CLAUDE.md` environment entries of 129 (`armcopy`), 128
(`protceil`), 25 (async copy pool), 91 (`stg_pool_*`, `ASYNC_COPY_MIN_BYTES`); `ps5 em/docs/agent-team.md`.
Code: `src/graphics/host_gpu/memoryTracker.h` (`ForEachUploadRange`), `pageManager.cpp` (`TakePendingRun`, `apply`,
`Protect`), `renderer/cache/bufferCache.cpp` (`CopyGuestToStaging`, inline copies < `ASYNC_COPY_MIN_BYTES`, `UploadCopies`),
`src/common/parallelCopy.{h,cpp}`, `src/common/gates.{h,cpp}`, `src/common/frameStats.h` (`ac_*`).

**Open the report with these numbers:** session 129 verdict **`ARMCOPY_GAIN`** (NEW) — `ac129` (measuring build `edd17418`,
Sky Garden, pin, 44 ABBA pairs, arms `armcopy=0|1`): Δ `dt_us` **−334.9 ± 144.4 µs**, draws-adjusted **−361.3 ± 105.1**; OLD
0 pairs (`DEBT`); all correctness conditions met (`ack129` `SELFCHECK_CLEAN`: 0 bad of 44.7 M + 3.9 M checks; videos 0 glitches;
validation; no death markers); audit 0 MAJOR / 2 MINOR. Rows (not a gain): Δ`prot_gpu_ro_ns` −374.1 µs, Δ`cpu_gpu_us` −1 002,
Δ `ac129` / Δ `pd128` = −0.329. **Shipping decided — this session's step 0.** Course base **53.36 %** (31 237.1 µs, arm 0 of
`ac129`, `edd17418` at `armcopy=0`, NEW) — not comparable with 52.58 % (other build); remainder 14 570.1 µs; sessions without
shipping: 1 (129). K14 remainder ≈ 682 µs [I: calibration minus gain]; on GuestGpu at `armcopy=1` ≈ 974 µs/frame of read-only
arming remains, 963.6 of it for inline copies (< 64 KiB). Honest estimate: the `acinline` gain is probably well below 682
(small pool jobs pay the enqueue, the GPU copy-semaphore wait, kernel contention [U]); `ACINLINE_NO_GAIN` is a useful outcome.
60 FPS is not promised.

## Rule of the session

As in session 129 (item 97 (в), 105 (в)): every decision in `ROADMAP.md` before the first action — also a rule constant that
differs from an accepted decision, BEFORE the agent brief; agent paragraphs tagged and accepted explicitly; amendments as new
items; a sealed consequence is not revoked. Every specialist step writes `## Step N — …` in `C:/kyty/s130/FACTS.md` BEFORE
`done`, time in UTC, the scale named in every table. A lead citing an own recount puts its output file and both sha beside the
acceptance item. Mutants: the chain once at step 1 (≤ 8 workers; shared-queue control rule of item 100 (д)); constants and
same-form tags — fixtures and `ALL OK` only; a stage-logic edit without budget left — stop and ask the lead; scorer suites in
the `mutlib` early-exit form; ONE full scorer `mutlib` v4.1, cap 15 min; session budget 30 min by item 87 (б)(3). A regime with
0 pairs prints `DEBT`. **Blocks by `GateArm:` lines, never by `blk`.** Window 10–88 of item 55 (б) named with its item number.
The harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call (item 76 (б)); **the chain call of a sealed
tag is verbatim from the seal and the chain logs its `PLWAIT`; a mismatch refuses before the lock (item 105 (в))**. One
attempt per registered tag. **The installed build is `9235a7ac…` until step 0г installs the shipping build; after that the
shipping build; every chain with the game restores the installed one.** While `C:/kyty/SEALED_RUN.lock` exists nobody edits,
commits or starts processes (item 25 (ж)). Long runs in the foreground (timeout 600 000 ms); start time and expected end in the
step comment. No agent creates user interactions (item 16). Privacy grep before commits. **Kill conditions of a "move off the
thread" mechanism are written in critical-thread units (item 104 (а), 105 (е)).**

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

0а, 1 and 2 start in parallel. The specialist sets `done` with a report and its `FACTS.md` section; the platform moves the step
to `in_review`; the lead writes the decisions the next step needs into `ROADMAP.md` and sets `done` with "Принято: …". Root
`HPP-3` is `blocked` on step 10.

## Steps

**0а. Emu Engineer — shipping code** on top of `main`: F1–F4 (item 103 (б)); the content check also at `armcopy=4` (item 105
(б)(2)); the stale-mark discriminator — `ac_jstale`, `LEFT` lines with `remark=` and `host=` (item 105 (б)(3); stamps written only
by operations latched at 2/3/4, paths 0/1 unchanged); the default of `armcopy` 0 → 1 (value 1 works without `KYTY_FRAME_TRACE`;
refusals turn it off with a log line). `check_gate_order.py`, commit → `git status --short -- src` empty → build → pinned copy
`C:/kyty/s130/kyty_emulator_<sha8>.exe`; `shader_cfg_tests` delta 0; NOT installed. No game run.
**0б. Red Team — diff review** of 0а (PASS / PASS_WITH_FIXES / FAIL; BLOCKING items) against items 103 (б), 104 (б), 105 (б):
F1–F4 by name, the content check at 4 is the same code as at 2, `ac_jstale` cannot be satisfied by a stale take, stamps do not
touch paths 0/1, the default and its refusals.
**0в. Harness Engineer — shipping evidence** on the pinned build (after 0б and 1): `s1s130` / `s2s130` (ABBA `armcopy=2|armcopy=4`,
reference / desert, 150 s: the content rule of item 105 (б)(2)); `s3s130` (`armcopy=2`, desert); the registered `ack130`
(`armcopy=2`, reference, 300 s: item 105 (б)(5)); the video `shp130` (gate file WITHOUT an `armcopy` line, 120 s: one `ArmCopy:
mode 1`, 0 one-frame glitches, frame sheet for the lead); death markers in every run. Does NOT install. Questions to the lead.
**0г. Harness Engineer — install** the shipping build after the lead accepted 0в (sha before/after, `ArmCopy: mode 1` on a short
launch is not required — the video proved it); rollback `KYTY_ARM_IN_COPY=0` or `9235a7ac`.
**1. Harness Engineer — port `C:/kyty/s130`** from `s129`: `gates_base.txt` with explicit `armcopy=1`, `protceil=0`, `rtskip=1`
(sha in FACTS); the chain `go130a.sh` with the shipping tags of 0в and the lever tags (smokes of `acinline`: ABBA `acinline=0|1`
at `armcopy=1`; `armcopy=2 acinline=1` reference and desert; `armcopy=3 acinline=1`; validation at `acinline=1`; the sealed
`ai130`; the registered `aik130`, `aiv130` / `aiw130`); the `PLWAIT` fixture of item 105 (в); lock before `procload`; one attempt;
install/restore of the INSTALLED build; ONE full chain mutant run. No game run.
**2. Probe Designer — design** `docs/session-130/design130.md` of `acinline` under item 105 (ж)(1)–(6): which inline copies carry
deferred read-only arming and how many (by the rows of `ac129`); the job form (per copy / per operation / threshold) with numbers;
why "a guest write is either in the copy or faults" holds unchanged (same chunk path, same `apply`); the detector and the control
on the inline class (why `ai_bad` > 0 at 3 is a host-state fact, not a counter path); no new waits under `m_mutex` / `apply` /
`RegionManager::lock`; the GPU copy-semaphore wait; counters; "0 is the shipping path byte for byte". Questions to the lead.
**3. Red Team — adversarial review** of the design (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT, numbered RCs): lost guest
write or stale GPU data for small copies; ordering of many small jobs against later syncs of the same pages; waits and lock
inversions; ABBA bias by the copy-semaphore wait or the arm switch mid-operation.
**4. Emu Engineer — the knob `acinline`** on top of the shipping commit (after 3 and 0в): default 0, last knob row, latched
with `armcopy`; commit → build → pinned copy; `shader_cfg_tests` delta 0; installed build unchanged.
**5. Red Team — code review** (PASS / PASS_WITH_FIXES / FAIL).
**6. Harness Engineer — smokes** of `acinline` (after 5 and 0г): the kill condition of item 105 (ж)(2) in critical-thread units;
correctness (ж)(3)(а), (б), (д), (е); cost rows; BDA regime. Rows and questions only.
**7. Harness Engineer — scorer, fixtures, the seal** `pred/01_ai130.md` (every estimator, every window edge, every outcome of
item 105 (ж)(5) including `DEBT` for 0 pairs, every regime case, DRS; rows Δ/682 and the second linearity point); ONE full
`mutlib`; `SEALS130.txt`.
**8. Harness Engineer — the sealed `ai130`** and its scoring; then `aik130`, `aiv130`, `aiw130`; frame sheet for the lead;
restore the installed build.
**9. Session Auditor — audit**: own recount of Δ (both estimators), the base, the moved inline share and the self-check sums;
the shipping evidence of step 0 (content ratio, `ac_jstale`, `ack130`, `shp130`); protocol; MAJOR/MINOR; debts; `audit130/`,
git `docs/session-130/audit/`.
**10. Roadmap Lead — close**: verdict by item 105 (ж)(5); shipping decision for `acinline` (the default change is step 0 of 131);
the course row (base — arm 0 of `ai130`); the second linearity point; the re-assessment (K16 dose calibration against K5);
documents; commit of both repositories; the chain of session 131 before closing.

**Outside the chain:** nothing; any off-chain task gets a formal consumer (item 73 (в)).

## Must not be claimed

60 FPS; the gain of `armcopy=1` in OLD, in other scenes, on the shipping build (another build — F1–F4) or against `9235a7ac` /
`d3a981a2`; that the move never loses a guest write (the self-check is evidence on two scenes); that the `LEFT perms=1` line of
`ack129` was a foreign mark; S, 682 or any census number as a gain; linearity of the dose; 53.36 % as a rise against 52.58 %;
the time of the installed build; rows built by `blk`; a timing number beside another heavy job.
