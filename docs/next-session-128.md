# Session 128 — ship `rtskip=1`, then the clean ceiling of K14 (GuestGpu page re-arming) with a sealed ABBA

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 87 (the close of 127: verdict and shipping (а), audit
decisions (б) — the UTC rule, the correction of item 86 (в), **the mutant budget counting rule (б)(3)**, **the FACTS-per-step
rule (б)(4)**; the course (в); the re-assessment K14 vs K5 (г); **the constants of this session (е)(1)–(8)**; the chain (ж));
items 84, 85, 86 (mutant rules: chain mutants once per session, scorer suites in the `mutlib` early-exit form, add-only top-up
with the closing-block rule); item 76 (ж) (the lever inventory, amended by 87 (г)); item 83 (г) (BDA regime per pair); item 77
(б) (the draws-adjusted estimator); item 78 (е) (the DRS rule); item 66 (а) (one attempt). `docs/session-127/audit/AUDIT127.md`
(§4 what is not proven, §5 debts); `docs/local-session-127.md`. `ps5 em/CLAUDE.md` environment entries of 127 (`rtskip`), 58
(`protbatch2`), 60 (`armdefer`), 27 (async protection, `prot_*` counters), 69 (`imgskip` — the "picture may break" ceiling
precedent), 113 (`bdanarrow`, BDA regime); `ps5 em/docs/levers/anyps5.md` (write-watch); `ps5 em/docs/agent-team.md`.
Code: `src/graphics/host_gpu/pageManager.cpp` (`Protect`, `ApplyGuard`, the protection worker), `memoryTracker.h`,
`cache/bufferCache.cpp` (arming after upload, `SynchronizeBuffersOfDirtyRanges`), `cache/textureCache.cpp` (`TrackImage`),
`src/common/gates.{h,cpp}`, `src/common/frameStats.h`.

**Open the report with these numbers:** session 127 verdict **`RTSKIP_GAIN`** — `k3p127` (build `98d98eee`, Sky Garden, BDA
NEW, pin, 42 ABBA pairs): Δ `dt_us` **−386.4 ± 118.9 µs**, draws-adjusted **−403.0 ± 134.0**, arm `rtskip=1` against arm
`rtskip=0` of the SAME build; every correctness condition of item 76 (з)(3) met (`k3k127` `rts_bad` 0 on 39.8 M checks,
control counted, validation classes ⊆ control, 0 video glitches); audit 0 MAJOR. Course base **50.36 %** (33 095.6 µs, arm 0
of `k3p127`, measuring build `98d98eee`, NEW) — NOT comparable with 52.0 % of session 126 (another build and run); remainder
16 428.6 µs; **16 sessions without shipped speed (112–127) — the count closes with step 0 of this session**. Installed build
at the start: `d3a981a2…`. The census R_K3⁺ 2 096.9 overstated the measured gain 5.4×. K14 lever: level of `prot_gpu_us` +
`pb_wait_gpu_us` ≤ 1 876 µs [I; level 1 666–1 744 M] — a LEVEL, not removable time; earlier prototypes moving the arming off
the thread (`armdefer`, `protbatch2`) did not pay. Honest estimate before measuring: the clean ceiling may well be below
500 µs; `K14_CLOSED` is a useful outcome. 60 FPS is not promised.

## Rule of the session

As since session 102 with the additions of 121–127: every decision in `ROADMAP.md` before the first action — also a rule
constant that differs from an accepted decision, BEFORE the agent brief, the lead as author; agent paragraphs tagged and
accepted explicitly; amendments as new items; a sealed consequence is not revoked. **Every specialist step writes its own
section `## Step N — …` in `C:/kyty/s128/FACTS.md` BEFORE `done` (item 87 (б)(4)); every table names its time scale (UTC).**
Mutants: the chain once, at step 1 (item 84 (в)(1)); constants and same-form tags — fixtures and `ALL OK` only; scorer suites
in the `mutlib` early-exit form (`ok = True`, `ok &= …`, last statement `sys.exit(0 if ok else 1)`) — `fast OFF` or
`workers: FORCED TO 1` in a header is a defect to fix before the run (item 85 (в)); ONE full scorer `mutlib` v4.1 on the final
text, cap 15 min at 28 workers; add-only top-up by items 74 / 86 (в) (closing block = 8 lines in the 127 suite form); the
session mutant budget is 30 min counted by item 87 (б)(3) (everything except the one full scorer run); each step reports the
wall sum of all its mutant runs. Suites end with `ALL OK`; edit scripts write LF; backslashes only through files written by
Write. **Blocks by `GateArm:` lines, never by `blk`.** Window 10–88 of item 55 (б) named with its item number, edge fixtures.
The harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call (item 76 (б)). **The knob `protceil` is
latched once per operation; default 0 is the old path byte for byte; it is MEASUREMENT ONLY and never ships.** One attempt
per registered tag (item 66 (а)); no restart to obtain a BDA regime. **After step 0 the installed build is the shipped
build (not `d3a981a2`); every chain with the game restores it.** While `C:/kyty/SEALED_RUN.lock` exists no run — lead
included — edits, commits or starts processes (item 25 (ж)). Long runs in the foreground (timeout 600 000 ms), start
verified; `procload` wait ≤ 540 s per call; a long run leaves its start time and expected end in the step comment (item 84
(д)). No agent creates user interactions (item 16). Privacy grep before commits (item 76 (и)). **The Δ of `pc128` is never a
gain.**

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

The specialist sets `done` with a report and its `FACTS.md` section; the platform moves the step to `in_review` and wakes
the lead; the lead checks the artifacts, writes the decisions the next step needs into `ROADMAP.md`, and sets `done` with
"Принято: …" — only then the next step unblocks. A return is "Доработать: …" in the same task, at most twice. Root `HPP-3`
is `blocked` on the terminal step.

## Steps

0. **Emu Engineer — ship `rtskip=1`** (item 87 (е)(1)): default of `{"KYTY_RT_SKIP", "rtskip", 0, 3}` in `gates.cpp` → 1, the
   `gates.h` comment, remove the dead `t_rts_a` (item 81 (г)); `check_gate_order.py`; commit to `main` (no push); `git status
   --short -- src` empty; build; `shader_cfg_tests` delta 0 against `C:/kyty/s126/tests_rk3.log`; install into
   `ps5 em/kyty_emulator.exe`; pinned copy `C:/kyty/s128/kyty_emulator_<sha8>.exe`; `d3a981a2` stays pinned in `C:/kyty/s119`
   (rollback). No game run. Parallel with step 2.
1. **Harness Engineer — port `C:/kyty/s128`** from `s127` (`procload.py`, name guard, `idle128.py`, `envchk128.py`,
   `hostdev128.py`, `enter_scene.py`, `gates_base.txt` = 127 + `rtskip=1`, the chain `go128a.sh`: smoke tags, the sealed tag
   `pc128` (ABBA `protceil=0|protceil=1`), the shipping video tag `shp128`; lock check before `procload`; install of a pinned
   measuring copy and restore of the INSTALLED shipped build; one attempt per registered tag; ONE full chain mutant run; scorer
   suites in the early-exit form). Then **the shipping video `shp128`** on the installed build, reference, `KYTY_REC`, 120 s,
   pin, gate file WITHOUT an `rtskip` line: `RtSkip: mode 1` in the log and Σ`rts_skip` > 0, `s51_vidglitch.py` 0 one-frame
   glitches, a frame sheet beside `k3w127` for the lead. Any failure ⇒ restore `d3a981a2`, report to the lead. After step 0.
2. **Probe Designer — design** `docs/session-128/design128.md` of the knob `protceil` under item 87 (е)(3)–(7): which
   GuestGpu protection calls are "arming to read-only" (sites, call graph, which caches: buffers, images), what the knob
   skips and what stays; the tracker state after a skipped call and its consistency argument (later unprotect, CPU write
   into an unarmed page, GC, the protection worker); what else the skip removes besides the syscall (re-uploads, guest
   faults, `pb_wait_gpu`) and the counters that show it; the latch and the operation; refusals; proof that 0 is the old path
   byte for byte; population, window, estimators, the BDA and DRS rules and the reading exactly as item 87 (е)(5)–(6);
   guards for the seal. Questions to the lead in the report. No game run, no emulator code. Parallel with step 0.
3. **Red Team — adversarial review** (ACCEPT / ACCEPT WITH REQUIRED CHANGES / REJECT, numbered RCs): can the skip crash,
   hang or silently corrupt the guest beyond the allowed broken picture; can it desynchronise the page tracker; is the ABBA
   biased (re-uploads, faults, BDA regime, the arm switch mid-operation); is 0 really the old path; is the ceiling really an
   upper bound of every mechanism that removes GuestGpu arming (write-watch, `armdefer`, `protbatch2`). Against code and logs.
   The lead accepts by a ROADMAP line BEFORE step 4.
4. **Emu Engineer — the knob `protceil`** (0..1, default 0, last knob row; `check_gate_order.py` before build) on top of the
   shipped tree; commit → `git status --short -- src` empty → build → pinned copy `C:/kyty/s128/kyty_emulator_<sha8>.exe`;
   the installed build unchanged (the shipped one). No game run. After steps 0 and 3.
5. **Red Team — code review** (PASS / PASS_WITH_FIXES / FAIL; BLOCKING items) against the accepted design and item 87 (е)(3),
   including "0 is the old path byte for byte", the latch and the per-mode split counters.
6. **Harness Engineer — smoke** on the pinned build: `protceil=1` survives 150 s on the reference; split of `prot_gpu` by mode
   at 0 and 1; re-upload and fault rows; BDA regime; rows only, questions to the lead (including the share of read-only
   arming — item 87 (е)(3) last sentence). After steps 1 and 5.
7. **Harness Engineer — scorer, fixtures (every estimator, every window edge, every outcome of item 87 (е)(6), every regime
   case of item 83 (г), DRS), the seal** `pred/01_pc128.md`; ONE full `mutlib` (early-exit form); `SEALS128.txt`.
8. **Harness Engineer — the sealed `pc128`** (lock, `procload --wait-s 540`, idle, one attempt, pin, ABBA
   `protceil=0|protceil=1`, `rtskip=1` in both arms) and its scoring; restore the installed build.
9. **Session Auditor — audit** (independent recount of Δ, both estimators, and of the base from the logs with an own parser,
   blocks by `GateArm:`; the shipping step 0 and the video `shp128`; protocol incl. the mutant budget of item 87 (б)(3) and
   FACTS per step; MAJOR/MINOR; debts), `audit128/`, git `docs/session-128/audit/`.
10. **Roadmap Lead — close:** verdict by item 87 (е)(6) (`K14_OPEN` / `K14_CLOSED` / `NOT_RESOLVED`), the course row (base —
    arm 0 of `pc128`), the re-assessment (K5 + K16 against the K14 outcome), documents, commit of both repositories, the chain
    of session 129 created before closing.

**Outside the chain:** nothing (item 87 (ж)); any off-chain task gets a formal consumer (item 73 (в)).

## Must not be claimed

60 FPS; the gain of `rtskip=1` against `d3a981a2`, in OLD, in another scene, or as a forecast (it is arm 1 against arm 0 of
`98d98eee`, NEW, Sky Garden, pin); the correctness of `rtskip=1` beyond the conditions of item 76 (з)(3) on the scenes run;
50.36 % as a drop against 52.0 %; the K14 level (`prot_gpu_us` + `pb_wait_gpu_us`) or any census number as a gain; the Δ of
`pc128` as a gain or as the value of any mechanism (it is an upper bound that includes skipped re-uploads and guest faults);
a broken picture of `protceil=1` as a defect; rows built by `blk`; a timing number beside another heavy job.
