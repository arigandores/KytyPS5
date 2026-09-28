# Session 129 — the K14 prototype `armcopy`: arming of buffer syncs moved off GuestGpu into the copy-pool job, sealed ABBA

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 97 (the close of 128: verdict `K14_OPEN` (а), shipping
(б), audit decisions (в) — the correction of item 95 (а), the stop rule for stage-logic edits, the 0-pair regime = `DEBT`; the
course (г); the re-assessment and the choice of the mechanism (д); **the constants of this session (е)(1)–(7)**; the chain (ж));
items 93 (г) (the dose calibration and its reading), 94 (г) (lock-hold wait inside Δ), 89 (б)–(з) (tracker facts accepted
from the review of 128: `Perms() == Read` is not "GPU-clean", `ForEachUploadRange` is the operation), 84–87 (mutant rules, the
budget counting, FACTS per step), 83 (г) (BDA regime per pair), 77 (б) (draws-adjusted estimator), 78 (е) (DRS), 76 (з)
(the K3 prototype pattern this session copies), 66 (а) (one attempt). `docs/session-128/audit/AUDIT128.md`;
`docs/local-session-128.md`; `docs/session-128/design128.md` §2–3 (the arming sites and classes (а)–(в), the census of 128);
`ps5 em/CLAUDE.md` environment entries of 128 (`protceil`), 127 (`rtskip`), 60 (`armdefer`), 58 (`protbatch2`), 27 (async
protection), 25 (async copy pool), 91 (`stg_pool_*`, `ASYNC_COPY_MIN_BYTES`); `ps5 em/docs/agent-team.md`.
Code: `src/graphics/host_gpu/memoryTracker.h` (`ForEachUploadRange`: `batch.Flush()` and `FlushProtection` before
`upload_func`), `regionManager.h`, `pageManager.cpp` (`Protect`, `FlushRegion`, `ApplyPending`, `applying_run`, `Verify`),
`renderer/cache/bufferCache.cpp` (`SynchronizeBuffer`, `CopyGuestToStaging` `:224–264`, `UploadCopies`), the copy pool
(`CopyPool`), `src/common/gates.{h,cpp}`, `src/common/frameStats.h`.

**Open the report with these numbers:** session 128 verdict **`K14_OPEN`** — `pd128` (measuring build `45d36512`, Sky
Garden, BDA NEW, pin, 42 ABBA pairs, arms `protceil=0|2`): Δ `dt_us` **+1 016.8 ± 140.8 µs**, draws-adjusted **+1 023.8 ±
118.2**, lower bound +876.1 ≥ +500; dose delivery 1.00753; slope Δ / dose 0.774 — **a calibration of the time of the
read-only arming calls on GuestGpu, not a gain**. Shipped by 128: `rtskip=1` (step 0, installed `9235a7ac…`; gain −386.4 ±
118.9 µs against arm 0 of `98d98eee`, NEW); sessions without shipping: 0. Course base **52.58 %** (31 700.6 µs, arm 0 of
`pd128`, `45d36512` at `protceil=0` with `rtskip=1`, NEW) — not comparable with 50.36 % (another build and run); remainder
15 033.6 µs. `protceil=1` (skip the arming) hung the GPU in 2 of 2 smokes: the arming carries live CPU → GPU data within
4 frames — a mechanism must MOVE it, not drop it. Honest estimate before measuring: the prototype gain is probably well below
1 017 µs (slope 0.77, lock waits [U], inline copies and written uploads stay on GuestGpu, kernel contention of the pool
workers [U]); `ARMCOPY_NO_GAIN` is a useful outcome. 60 FPS is not promised.

## Rule of the session

As since session 102 with the additions of 121–128: every decision in `ROADMAP.md` before the first action — also a rule
constant that differs from an accepted decision, BEFORE the agent brief, the lead as author; agent paragraphs tagged and
accepted explicitly; amendments as new items; a sealed consequence is not revoked. **Every specialist step writes its own
section `## Step N — …` in `C:/kyty/s129/FACTS.md` BEFORE `done` (item 87 (б)(4)); every table names its time scale (UTC).**
A lead citing an own recount puts its output file and both sha beside the acceptance item (item 97 (в)(1)). Mutants: the chain
once, at step 0 (item 84 (в)(1)), ≤ 8 workers; constants and same-form tags — fixtures and `ALL OK` only; a stage-logic edit
without budget left — stop and ask the lead, no exceptions (item 97 (в)(2)); scorer suites in the `mutlib` early-exit form —
`fast OFF` or `workers: FORCED TO 1` in a header is a defect to fix before the run (item 85 (в)); ONE full scorer `mutlib`
v4.1 on the final text, cap 15 min; add-only top-up by items 74 / 86 (в) / 96 (б); the session mutant budget is 30 min
counted by item 87 (б)(3); each step reports the wall sum of all its mutant runs. A regime with 0 pairs prints `DEBT` like a
regime with < 10 pairs (item 97 (в)(3)). Suites end with `ALL OK`; edit scripts write LF; backslashes only through files
written by Write. **Blocks by `GateArm:` lines, never by `blk`.** Window 10–88 of item 55 (б) named with its item number, edge
fixtures. The harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call (item 76 (б)). **The knob `armcopy`
is latched once per operation (the whole `ForEachUploadRange` of one call); default 0 is the old path byte for byte.** One
attempt per registered tag (item 66 (а)); no restart to obtain a BDA regime. **The installed build is the shipped `9235a7ac…`;
every chain with the game restores it.** While `C:/kyty/SEALED_RUN.lock` exists no run — lead included — edits, commits or
starts processes (item 25 (ж)). Long runs in the foreground (timeout 600 000 ms), start verified; `procload` wait ≤ 540 s per
call; a long run leaves its start time and expected end in the step comment (item 84 (д)). No agent creates user interactions
(item 16). Privacy grep before commits (item 76 (и)). **The Δ of `pd128` is never a gain.**

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

The specialist sets `done` with a report and its `FACTS.md` section; the platform moves the step to `in_review` and wakes
the lead; the lead checks the artifacts, writes the decisions the next step needs into `ROADMAP.md`, and sets `done` with
"Принято: …" — only then the next step unblocks. A return is "Доработать: …" in the same task, at most twice. Root `HPP-3`
is `blocked` on the terminal step.

## Steps

0. **Harness Engineer — port `C:/kyty/s129`** from `s128` (`procload.py`, name guard, `idle129.py`, `envchk129.py`,
   `hostdev129.py`, `enter_scene.py`, `gates_base.txt` = the file of 128 with `protceil=0` and `rtskip=1` pinned, sha in FACTS;
   the chain `go129a.sh`: smoke tags of `armcopy` (values 1, 2, 3; reference and desert; validation at 1), the sealed tag
   `ac129` (ABBA `90+1800` `armcopy=0|armcopy=1`), the registered tags `ack129` (`armcopy=2`, 300 s), `acv129` / `acw129`
   (video at 1 / 0); lock check before `procload`; install of a pinned measuring copy and restore of the INSTALLED `9235a7ac`;
   one attempt per registered tag; the harness refuses `protceil` ≠ 0 in every arm; ONE full chain mutant run (≤ 8 workers);
   scorer suites in the early-exit form). No game run. Parallel with step 1.
1. **Probe Designer — design** `docs/session-129/design129.md` of the knob `armcopy` under item 97 (е)(1)–(6): what exactly
   moves into the pool job and what stays on GuestGpu (with its share by the rows of `pd128`/`design128` §3.3 — [c], not a
   gain); the lock order of the pool worker, GuestGpu, the guest fault handler and the protection worker (`apply`, region
   `lock`, `applying_run`, `Drain` on flip); what the job does if `Perms()` is no longer `Read` when it applies; the proof
   "a guest write is either in the copy or faults" for every interleaving; the self-check of value 2 and why the control of
   value 3 is not a tautology; refusals; counters; proof that 0 is the old path byte for byte; population, window,
   estimators, BDA/DRS and the reading exactly as item 97 (е)(4)–(5). Questions to the lead in the report. No game run, no
   emulator code. Parallel with step 0.
2. **Red Team — adversarial review** (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT, numbered RCs): can the move lose a guest
   write or feed the GPU stale data; can the worker apply a stale permission over a later unprotect or no-access; deadlock or
   lock inversion with guest faults and the protection worker; can the ABBA be biased by `apply`/copy waits, the arm switch
   mid-operation or the BDA regime; is 0 the old path; is the control of value 3 real. Against code and logs. The lead
   accepts by a ROADMAP line BEFORE step 3.
3. **Emu Engineer — the knob `armcopy`** (0..3, default 0, last knob row; `check_gate_order.py` before build) on top of
   `main`; commit → `git status --short -- src` empty → build → pinned copy `C:/kyty/s129/kyty_emulator_<sha8>.exe`;
   `shader_cfg_tests` delta 0; the installed build unchanged (`9235a7ac`). No game run. After step 2.
4. **Red Team — code review** (PASS / PASS_WITH_FIXES / FAIL; BLOCKING items) against the accepted design and item 97 (е)(1):
   "0 is the old path byte for byte", the latch, the arm-before-copy order in the job, the lock order, the check and the
   control, the counters.
5. **Harness Engineer — smokes** on the pinned build: the kill rule of item 97 (е)(2) (moved share ≥ 0.5 at value 1, window
   10–88 of item 55 (б)); correctness conditions (3)(а) (value 2 on the reference and in the desert), (б) (value 3), (д)
   (Vulkan validation at 1, duplicate limit lifted, rule of item 83 (б)), (е) (no death markers at 1/2); cost rows, BDA regime;
   rows only, questions to the lead. After steps 0 and 4.
6. **Harness Engineer — scorer, fixtures (every estimator, every window edge, every outcome of item 97 (е)(5) including
   `DEBT` for 0 pairs, every regime case of item 83 (г), DRS), the seal** `pred/01_ac129.md`; ONE full `mutlib` (early-exit
   form); `SEALS129.txt`.
7. **Harness Engineer — the sealed `ac129`** (lock, `procload --wait-s 540`, idle, one attempt, pin, ABBA
   `armcopy=0|armcopy=1`, `rtskip=1` and `protceil=0` in both arms) and its scoring; then the registered `ack129`, `acv129`,
   `acw129` (conditions (3)(в), (г)); a frame sheet of both videos for the lead; restore the installed build.
8. **Session Auditor — audit** (independent recount of Δ, both estimators, the base, the moved share and the self-check sums
   from the logs with an own parser, blocks by `GateArm:`; protocol incl. the mutant budget and FACTS per step;
   MAJOR/MINOR; debts), `audit129/`, git `docs/session-129/audit/`.
9. **Roadmap Lead — close:** verdict by item 97 (е)(5) (`ARMCOPY_GAIN` / `ARMCOPY_NO_GAIN` / `ARMCOPY_INCORRECT` /
   `NOT_RESOLVED`), shipping decision (the default change itself is step 0 of session 130), the course row (base — arm 0 of
   `ac129`), the row Δ `ac129` / Δ `pd128`, the re-assessment (K14 remainder, K5 + K16), documents, commit of both
   repositories, the chain of session 130 created before closing.

**Outside the chain:** nothing (item 97 (ж)); any off-chain task gets a formal consumer (item 73 (в)).

## Must not be claimed

60 FPS; the Δ of `pd128` as a gain or as the value of any mechanism; linearity of the dose; that the move pays, or that it
cannot hang the GPU, before the sealed run and the correctness conditions; K14 in OLD; 52.58 % as a rise against 50.36 %;
the time of the installed `9235a7ac` (never measured); the gain of `rtskip=1` against `d3a981a2`, in OLD or in another scene;
rows built by `blk`; a timing number beside another heavy job.
