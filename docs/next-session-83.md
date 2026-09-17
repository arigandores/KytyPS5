# Session 83 — prompt

Session 82's commits are on `merge-upstream`: **5f12c18** (WIP checkpoint) and **e092382** (the
session). **Source code DID change and the binary WAS rebuilt** — the first time since session 77.
The installed `kyty_emulator.exe` is `143dbc4313a9def2…`, 23 568 896 bytes. Harness —
**`C:/kyty/s82`**, port it to `C:/kyty/s83`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden**. The baseline of record
is no longer 28.61 FPS: **session 82 shipped a default and the confirmation run reads 31.60 FPS**
(`acc82a`, 5658 settled frames, mean `dt_us` 31 642.1).

## 0. Read first

1. `C:/kyty/s82/FACTS.md` — the single source of truth. **§2 (what shipped and on what evidence),
   §3.4 (three defects found by a self-check), §4 (four corrections to the record), §5 (the first
   full CPU frame decomposition), §7 (the vblank plateau — it governs your endpoint choice).**
2. `C:/kyty/s82/DESIGN_82_parallel.md` — the slice-parallel rewrite, its build order and its kill
   criteria K1–K8. **Read §0 and §1 before proposing any parallel work.**
3. `C:/kyty/s82/PLAN_82_bind.md` — the binding path, thirteen ranked items.
4. `C:/kyty/s82/README.md` — the standing traps.

**Check the byte count of anything large you read.** Reading through the rtk-rewritten shell
truncates silently.

**Harness:** port `C:/kyty/s82` → `C:/kyty/s83`, roots rewritten, `.txt`/`.json` byte-exact.
**`gates_base.txt` CHANGED in session 82** and is now **1092 bytes, 99 names, sha256
`00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8`** — it pins `dapin=3` to match
the shipped default. The old `4724bf81…f8c4f` pinned `dapin=1` and would silently override it.
**`area_series.py` still carries a stale `--root C:/kyty/s70` default** (session 82 had to pass
`--root C:/kyty/s82` by hand); fix it in the port or you will regenerate nothing.

## 1. What session 82 settled

* **`dapin` mode 3 is shipped and measured.** `dap82b`, VALID on all six pre-registered criteria:
  `cpu/draw` −2.185 % ± 0.140 %, t = −31.12 over 123 matched pairs; `dt_us` −820.7 µs; 30.791 →
  31.590 FPS. Arming is an **identity in the log**, not a statistic: `mode=3 mask=0x0000000000005555`,
  exactly the raw mask sessions 79 and 81 measured three times.
* **The first attempt at that contrast was VOID** (`dap82a`, area split +3.937 %, pair match 54.5 %)
  and was not quoted. The criterion was not substituted. The second run then read a *smaller*
  effect — the direction session 81's prospective bias predicts.
* **A write map for the BDA region walk buys nothing.** `bdb82a`, VALID, armed to 99.95 %, both arms
  doing identical work (`bda_scan` 1066 each): **−50.8 µs ± 87.5**, inside the ±75…92 µs A/A floor.
  The 17 518 skipped region visits a frame were never the cost.
* **22.421 ms is not the mutating floor** — that is `a_hold_us − mh_prog_us`. `a_mut_us` reads
  13 300 / 14 035.5. **The true floor is NOT MEASURED, bracketed [13.3, 29.0] ms.**
* **89 % of the CPU frame is spent holding one render mutex** (`a_hold_us` 29 004 of `cpu_gpu_us`
  32 501), and the GPU is at 12.5 ms — it could sustain ~80 FPS.

## 2. What is settled — do not reopen

* Micro-gates on the binding path. Thirteen were ranked and the honest total is 0.7–2.5 ms.
* A stage-level binding memo: the key carries per-object guest base addresses that change every
  draw by construction. A descriptor-level 4096-way memo already exists and hits 92.98 %.
* `srtmemo` (−11 % FPS), demand-driven SRT walk (100 % of read nodes needed), shadow/duplicate
  resolve on workers (+4–8 % pure tax), M4 at PM4-*range* granularity (93–94 % of hand-offs inside
  an open render pass).
* Inter-run `cpu/draw`, `cpu_gpu_us` and FPS comparisons. **They are not measurements.** `acc82a`'s
  31.60 FPS is a confirmation that a default is live, nothing more.

## 3. The work — THIS IS A CODING SESSION

**THE RULE, and it is not negotiable.** Sessions 75 to 81 changed no source at all and the FPS did
not move for eight sessions. Session 82 changed source and it moved. **This session ends with a
source change that was A/B'd on this machine, or it failed.** A session whose output is a document,
a pre-registration or a table of numbers has failed regardless of how good the numbers are.
Measurement is a step inside the work, never the purpose of the session.

Budget it as: **the first hour measures one number, the rest of the session builds.**

### 3.0 First hour, not first session: the true sequential floor

One instrumented build plus **one ABBA run**. This is the number that decides whether the parallel
rewrite is worth months (`DESIGN_82_parallel.md` §1: 60 FPS needs `S <= 14 ms`), and it has never
been measured — it is open item 10 of session 72. Today `MutScope` sits at six sites and brackets
13.3-14.0 ms; `a_hold_us` brackets 29.0 ms. The truth is between.

Method, from `DESIGN_82_parallel.md` §5: add `MutScope` **one per phase, not per site**, so the
40 480 and 43 480 inner calls nest and cost nothing, behind its own gate so the instrument itself
is A/B-able. **The instrument is not free** - `amut` already costs 0.949-0.979 ms a frame, of which
**+958.4 us lands inside `mh_bind_us`**, the very phase being measured. A/B the counter before
quoting any floor derived from it.

Then branch, and build either way:

* **S <= 14 ms** -> the rewrite is alive. Spend the rest of the session on step 1 of
  `DESIGN_82_parallel.md` §3 and land it.
* **S >= 16 ms** -> kill criterion K2. The parallel rewrite cannot reach 60 FPS at any granularity
  this architecture allows. Say so in FACTS, **restate the programme's goal**, and spend the rest of
  the session on `PLAN_82_bind.md`'s top items, which are worth 0.7-2.5 ms and are real.
* **in between** -> build the binding-path items this session and take the floor question to a
  finer instrument next time. Do not spend a second session deciding.

### 3.1 The two debts that cost one run each

Fold these into runs you are taking anyway; neither is worth a dedicated session.

* **`dapin`'s GPU cost.** +1.238 % (+147.1 us), replicated a FOURTH time and unexplained. One
  `KYTY_GPU_TIME` pair on a `dapin` ABBA shows which pass kind grows. It does not bind (12.56 ms of
  a 32.5 ms frame) - this is a debt on a shipped default, not a blocker.
* **The video pass session 82 owes.** `--video`, `s20_vidglitch.py`, >= 3000 frames. Nothing shipped
  in session 82 can reach the renderer, but the debt must not accumulate past one session.

### 3.2 Where `bda_us` 2181 us a frame goes - NOT MEASURED, and it is code, not a study

181 `PrepareBda` calls at 12.05 us each, and session 82 proved it is **not** the 18 582 region
visits. Next candidate: the `m_buffers` `std::map` lookups of `SynchronizeBuffersInRange`
(`bufferCache.cpp:2519`, `:2526`, `:2461`) - three `upper_bound`/`lower_bound` per call over a map
walked again per dirty range. **No timer exists on them.** `bda_us` is a `Scope` and reads 0 in
`KYTY_FRAME_TRACE=lite`, so add an `Add`-style counter rather than a non-lite run. If the map is the
cost, replacing it on this path is a bounded change with a measurable endpoint.

### 3.3 The parallel rewrite, if 3.0 licenses it

`DESIGN_82_parallel.md` has the nine-step build order; every step compiles, runs and is individually
A/B-able, which is exactly what the rule above demands. Honour the kill criteria: K1
(`spine_us` > 1200 us -> step A closed), K2 (see 3.0), K7 (after step 7,
`cpu_gpu_us - spin_gpu_us` must have fallen >= 4000 us or the rewrite is reverted).

Two facts the design corrects; do not re-derive them the old way. **All four substantial slices run
on ONE graphics `CommandProcessor`** - `slc_cp_same = 0.011` measures temporal adjacency under
round-robin over 57 queues, not separation - so a context fork is needed, 6803 bytes, cheap. And
**5 graphics DCBs a frame, none of which suspends**, while `slc_resume = 4.7955` belongs entirely to
the compute ACBs.

### 3.4 `bdabits` stays at 0

Correct, armed, and null. One gate flip away if anything ever makes the region walk hot. It must get
a video pass before it ships.

## 4. Do NOT

**New, from session 82:**

* **Do not quote any `bk_*` number.** Run `bk82a` is invalid in its entirety (last flip n = 669,
  18.3 FPS, a machine state in no run of the record), and its one-slot comparison answers the wrong
  question anyway.
* **Do not quote any counter printed after `bda_skip` in `log_bdv82a.txt`** — that printf had four
  specifiers against six arguments and everything after it is shifted by two.
* **Do not put a format string and its argument list in one patch call.** When the second anchor
  fails the file is never written, and applying the arguments separately produces exactly the bug
  above.
* **Do not estimate a saving from a population without a measured unit price.** 17 518 region visits
  a frame looked like ~1 ms and were worth −50.8 ± 87.5 µs, because the data was already hot.
* **Do not ship a memo whose skip condition is weaker than the condition it replaces.** A clear bit
  proved "no write since the clear"; the code it replaced also required "scanned under the current
  generation". Omitting the second half skipped regions that had never been scanned at all.
* **Every verify line needs a cap.** The tree's convention is 32–64; an uncapped one printed
  40 361 555 lines and would have distorted the run on its own.
* **Do not read `dt_us` as the endpoint inside the vblank plateau.** Between −1.6 ms and −15.8 ms of
  saving the scoreboard reads 30.0 FPS and does not move. Decide the endpoint before the run.

**Carried:** no optional stopping; pre-registrations are sealed in place and never edited; arming is
proved by a counter inside the run, never by the launcher; `guards.py` check 10 hashes the exe
installed *now*, so compare check **lines**, not verdicts; a gate enum entry goes immediately before
`Count` and nowhere else; `gen_gates.py --with` replaces the **first** occurrence of a name.

## 5. The arithmetic

| article | measured | state |
|---|---|---|
| `dapin` mode 3 | `cpu/draw` −2.185 % ± 0.140 %, t = −31.12, 123 pairs; `dt_us` −820.7 µs | **SHIPPED** |
| …its GPU cost | +1.238 % (+147.1 µs), fourth replication | **UNEXPLAINED** |
| `bdabits` | −50.8 µs ± 87.5, armed to 99.95 %, identical work both arms | **NULL, gate at 0** |
| the sequential floor | `a_mut_us` 13 300 / 14 035.5; `a_hold_us` 29 004 | **NOT MEASURED**, [13.3, 29.0] ms |
| the CPU frame | bind 12 027, emit 7403, prog 5831, disp 2419, of 29 004 held | **MEASURED** |
| the GPU | `gpu_busy_us` 12.5 ms — would sustain ~80 FPS | **MEASURED** |
| 60 FPS condition | `S ≤ 14 ms` **and** `f_eff ≤ 0.125` simultaneously | **derived, `DESIGN` §1** |

**The honest statement of the task.** Session 82 moved the number for the first time in eight
sessions, by shipping a placement contrast the record had already measured three times and could
not express portably. That was the last cheap win on the shelf: **31.60 FPS, and ≈ 15 ms still to
find.** Everything remaining is either worth ≤ 2.5 ms (the binding path) or is behind a rewrite
whose feasibility turns on one unmeasured number. **Measure that number first. If it comes back at
16 ms or more, the programme's goal should be restated rather than pursued.**
