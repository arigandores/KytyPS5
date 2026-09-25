# Audit of session 117 — lenses PROTOCOL and CODE

Read-only audit (2026-09-25). The only files written are under `C:/kyty/s117/audit117/protocol/`:
`roadmap117.txt` (extract), `src117.diff`, `src117_nohw.diff`, `all117.diff`, `privacy_scan.py`, `recount_k5k1.py`, and this report.
The rule applied throughout is "refuted when in doubt".

**How the times were established**

- **Commit times:** `git log` from 509fff5 to 6f26e6c.
- **When each ROADMAP item was written:** the mtime of its original patch script in `C:/kyty/s106_stage/patch_roadmap117_N.py`. The copies in `docs/session-117/tools/` carry copy times.
- **Build times:** `C:/kyty/build/.ninja_log`. Its mtime field is in 100-ns units from 2000. I calibrated it against the disk mtime of `kyty_emulator.exe`.
- **Timing-run bounds:** `t0_start.txt` = 1790357920 (19:38:40) and `t0_end.txt` = 1790360444 (20:20:44).
- **Sealed chain:** `go117a.log`.
- **Probe compile:** `cp.cpp`, `cp.obj` and `cp.asm` in the session scratchpad.

## Verdicts per question

| # | question | verdict |
|---|---|---|
| 1 | Each ROADMAP item recorded before its action | items 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14 HOLD; **item 4 BROKEN** (code written before the item); **item 9 UNPROVEN** (treated as broken by default) |
| 2 | Smokes disclosed; were rules or bars changed after the smokes? | **HOLDS.** The smokes are disclosed and the K1 bar is unchanged. The item-11 changes were legitimate pre-seal fixes and could not have changed this outcome. Several MINOR notes follow. |
| 3 | Re-seals 01 → 01r → 01r2 | **HOLDS.** 01 → 01r changed only CR bytes; 01r → 01r2 changed only the final print. No run used an earlier seal. |
| 4 | Items 2 and 3 "by the record" | item 2 **PARTLY supported**; item 3 **OVER-CLAIMED (MAJOR)** |
| 5 | Item 7 timing: comparison with s114 and idle machine | comparison **HOLDS**; "machine idle" **BROKEN (MAJOR, protocol)** |
| 6 | Privacy | **HOLDS.** No email addresses, personal names, or other games or emulators. A Windows user path is noted as information. |
| 7 | Can the spine change what executes? | knob 0 **HOLDS**; knobs 1/2 **BROKEN in general (MAJOR)**, not triggered in the sealed run |
| 8 | `hardwareContext.h` `operator==` | **HOLDS** |
| 9 | Can K5 pass vacuously; is element indexing aligned? | **HOLDS for this run.** The compares are real and byte-equal. Two MINOR edge cases. |

## 1. Timeline: each item against its action

| item | recorded (script mtime / commit) | action it governs, and when | status |
|---|---|---|---|
| 1 | 19:37:54 / 19:37:58 `09b65e7` | timing run started 19:38:40 | HOLDS (but its own "only code reading while it runs" was broken — see M1) |
| 2 | 19:38:44 / 19:38:48 `e862f5b` | a rule; nothing acted on it before this time | HOLDS |
| 3 | 19:42:37 / 19:42:41 `a430787` | design `designA4_spine.md`, mtime 19:47:04 | HOLDS as ordering (it also said "after the mutlib measurement: design → code", which was broken — see M1) |
| 4 | 19:51:33.98 / 19:51:38 `ff672e6` | the complete spine code, `patch_spine117.py` v1 (595 lines, 26 KB), is in the **same commit** | **BROKEN** (m1) |
| 5 | 19:55:11 / 19:55:15 `beaef51` | compile probe 19:52:32–38 (information gathering, allowed); snapshot/`operator==` patch applied to src 19:57:21 (gates.h, gates.cpp, commandProcessor.h, hardwareContext.h) and 19:58:31 (frameStats.h, videoOut.cpp) | HOLDS |
| 6 | 20:00:59 / 20:01:02 `9807fe2` | rules for later actions | HOLDS |
| 7 | 20:21:03.9 / 20:21:07 `04a21f0` | timing ended 20:20:44; first emulator build started ≈20:21:12 (ninja log, 24 s) | HOLDS as ordering; content false (M1) |
| 8 | 20:23:59 / 20:24:06 `e8404d9` | smoke started (`gates_smoke117.txt` 20:24:23) | HOLDS |
| 9 | 20:28:37.8 / 20:29:06 `fbcfd49` | fix to `graphicsRun.cpp`: its time was overwritten by item 10's edit; it happened no later than the build117b start ≈20:28:43.97 | **UNPROVEN** (m2) |
| 10 | 20:32:37.1 / 20:33:02 `36c8350` | `graphicsRun.cpp` edited 20:32:45.26; build ≈20:32:46 | HOLDS |
| 11 | 20:56:15.6 / 20:56:19 `09da5de` | scorer/test/mutant/pred fixes 20:57:35 – 21:06:17 | HOLDS |
| 12 | 21:07:32.8 / 21:11:22 `482a824` | LF conversion 21:07:39.79; re-seal 21:11:22 | HOLDS |
| 13 | 21:11:51.0 / 21:12:08 `81c6a89` | `test_spn117.py` "ALL OK" edit 21:11:58.73; re-seal 21:12:08 | HOLDS |
| 14 | 21:20:23.1 / 21:20:27 `6f26e6c` | chain ended 21:20:03; audit agents started 21:20:55 or later; build d3a981a2 re-installed 21:20:40 | HOLDS |

**The sealed chain.**
- The chain was requested at 21:12:44, after the mutant tally was committed (`bd6c278`, 21:12:43; mutants ran 21:12:08–21:12:34).
- Its file hashes at 21:14:10 equal seal 01r2. The idle check read CPU 5 % and GPU 0 %.
- Between 21:14:33 and 21:20:03 the only files modified outside the build tree were the run's own (`find -newermt`).
- `_kyty.prev.txt` is smoke117c (91 257 811 B, 20:35:33), so no other game run happened between the smokes and the seal.

## 2. Smokes and post-smoke rule changes (Q2)

**Disclosure.** `pred/01_spn117.md` "Before the seal (disclosed)" names all three smokes. My recount of the smoke logs:

| smoke | `spine_bad` per frame | `spine_ns` (mode 2) | compares |
|---|---|---|---|
| smoke117 | 24.05 | 780 µs/frame | — |
| smoke117b | 20.32 | 789 µs/frame | — |
| smoke117c | 0 | 842 µs/frame | 19.66 M |

**K1 bar.** The 1 200 µs bar predates session 117: `DESIGN_82_parallel.md:332` and `designA_review.md:21,57`. It is unchanged.

**Item 11 changes** (all made after the smoke numbers, before the seal):
- **Walker fit.** The old predicate could never fail; the new one makes CLOSE_A reachable, so it is stricter. It matters only if K1 FAILs, and K1 was known to be about 0.6–0.84 ms against the 1.2 ms bar.
- **K5 scope.** Now every x line, plus any `SpineMismatch:`/`SpineMisalign:` line ⇒ FAIL, plus `cram_write`. Stricter.
- **`spine_lost` is no longer a failure.** This is looser than item 5's text. The code committed before any smoke (`e8404d9`) already had this meaning, and the smoke showed 0 lost, so the smokes gave no motive.
- **`el_ops` admission.** New, stricter.
- **`armed` ≤ 1 % instead of = 0.** Looser (see m4).

None of these could have been tuned toward a pass from the smoke data:
- the smokes had no schedule;
- `check_spn117/synth_real.py` zeroed the arm-0 `spine_cmp` values in the synthetic rewrite.

**Verdict: legitimate pre-seal check, not post-hoc tuning.**

## 3. Re-seals (Q3)

- **01 → 01r.** The blobs committed at `17baed5` and `482a824` hash identically with CR stripped (pred `ca866441…`, spn117 `ab5d5996…`, test `4bd8c0ec…`, mut `6b551bd1…`). CR counts went from 84/386/348/142 to 0.
- **01r → 01r2.** The only change is the last line of `test_spn117.py` (`'ok'` → `'ALL OK'`).
- **`go117a.sh`** hashes `61bd09b9…` in all three seals and now.
- **Seal 01 was never run.** mutlib refused it before starting (task output 21:06:43: "REFUSED: mutant arms_none: anchor found 0 times").
- **Current state.** Every current file hash equals 01r2. `old/` holds only the smokes.

## 4. Items 2 and 3 against the cited record (Q4)

**Item 2 — PARTLY supported.**
- Supported: `gw_idle` is 27.6 µs and render-mutex waiting is small (`a_wait_us` 170 µs/frame = 0.55 %, `runs116/obs116.score.txt:39`).
- Not measured: "the 92.3 % is work, not waiting" is inferred. `plkstat` was off in `obs116`, so spin inside the `PipelineCache::m_mutex` holds was not measured on `d3a981a2`. The last value was about 420 µs/frame, before `daslot`/`cspfree`.
- The closure is a legitimate program rule (reopen at ≥ 1 ms).

**Item 3 — OVER-CLAIMED.** See M2.
- The reorder (stage 4 before M3.2–M3.5) is not authorised by `designA_review.md`, which lists stage 4 after stage 3 without stating a dependency. It is consistent with the original `DESIGN_82_parallel.md:122-123,153-163`, where the spine comes before `RecordCtx`. Acceptable under the delegation.

## 5. Item 7 timing (Q5)

**The comparison with session 114 holds.**
- All 345 mutant verdicts and killers equal `C:/kyty/s114/mut_ttl114b.out.txt`; the only extra line is `BASELINE#2`.
- Controls 3/3, 28 workers on both sides.
- Wall 2 523.7 s against v2's 4 085.9 s; worker time 63 823 s.
- Early exit median 86 %; replay 216.5 calls per job.
- `procload` was clean at the start (task output 20:20:44).

**The "machine idle (except code reading)" claim is false.** See M1.

## 6. Privacy (Q6)

- **Scope:** every line added in 509fff5..HEAD (`privacy_scan.py`).
- **No hits for:** email addresses, personal names, other games, other emulators, URLs.
- **One informational item:** `docs/session-117/harness/go117a.sh` and `spn117.py` contain the Windows user path `C:/Users/<user>/OneDrive/Desktop/ps5 em/…`. The same path has been committed since `docs/session-102/*`, so this is existing practice. The username is derived from a personal name; stripping it is optional.

## 7–9. Code

### Knob 0 — HOLDS

- **Per-submission cost:** one relaxed atomic load (`Gates::Value`, `gates.h:631-636`) in `SpinePlan`. It then returns, having set `m_spine_mode = 0`.
- **Hooks:** the `ProcessPm4Range` hook checks `m_spine_mode == 2`; `SpineFinish` runs only if `m_spine_mode != 0`.
- **Layout:** new fields in `Pm4Execution` and `CommandProcessor`. `CommandProcessor` is `NO_COPY`; compute processors are held by `unique_ptr`.
- **Knob table:** `Spine` is appended after `TitleAsync` in both `enum Knob` and `KNOB_DEFINITIONS`.

### The shadow processor never reaches the renderer — HOLDS

- The constructor only stores the reference (`commandProcessor.h:73-74`).
- The register handlers use only `cp.GetCtx` ×182, `GetShCtx` ×38, `GetUcfg` ×16, `Get/SetUserDataMarker`, and `SetIndexType`. My scan covered `pm4Handlers.cpp` 1–1317 and 2698–end.
- `Reset` and `ApplyContextStateOperation` touch members only (`graphicsRun.cpp:365-402`).
- `SET_PREDICATION`, `COND_EXEC`, the 14-dword branch and `INDIRECT_BUFFER` are handled inline, not through their handlers. This avoids `BufferFlushAndWait` and `ProcessIndirectBuffer`/`g_current_execution`.
- `AgcIsInternalDataPacket` is pure (`agc.cpp:3997`).
- `WalkComputeDispatches` receives `&m_sh_ctx` as `const HW::Shader*` (`graphicsRun.cpp:1627`).

### Knobs 1/2 — BROKEN in general

See M3. Static state touched by the shadow: log budgets only (m10).

### `hardwareContext.h` — HOLDS

- **What changed:** 61 `[[nodiscard]] bool operator==(const T&) const = default;` preceded by `public:`. Each is the last member before `};` (verified for all 61). Nothing else in the file changed.
- **Type properties:** no data member follows a new access specifier, so standard-layout, aggregate and trivially-copyable status are unchanged, and layout and ABI are unchanged.
- **Overload risk:** `src/` has no generic `operator==` templates and no `requires`/`decltype` tests on `==` whose selection could change.
- **Shader-cache signature:** it hashes only `graphics/shader/**` plus `shaderTranslationCache.cpp`, `gpu_format.h` and `gpu_defs.h` (`CMakeLists.txt:155-156`, `src/generate_version.cmake:43-55`). None of these changed in 509fff5..HEAD, and nothing under `src/graphics/shader/**` changed.
- **Only caveat:** NaN floats compare unequal. This is disclosed.

### Counters and alignment — HOLDS for the sealed run

**My own recount** (`recount_k5k1.py`, separate parser) over all `FrameTrace-x` lines with n > 1800:
- `spine_bad`, `spine_misal`, `cram_write`, `spine_lost`, `spine_abort` and `spine_pad` are all 0.
- There are no `Spine*` diagnostic lines and no duplicate x lines.
- Arm-0 `spine_ns` over the kept frames is 608.6 µs; the scorer says 608.0.
- Arm-1 cmp/el is 1.0001.
- `spine_pad` = 0, so every compare was byte-identical: the compares are real, not vacuous.

**Alignment on each path:**
- **Predicated skips:** the same test runs before the hook (`graphicsRun.cpp:2402` vs the spine). The spine evaluates the predicate at plan time, and any divergence is visible through `regs[6]` or misal.
- **Nested IBs and branches:** same depth-first order.
- **Suspension:** `SuspendPm4` is reachable only from `WaitCe`, `WaitDeDiff`, `WaitForRewind` and `WaitRegMem` (`graphicsRun.cpp:460-551`), never from an element packet, so no element is checked twice. The cursor lives in `Pm4Execution`, and an interleaved plan ⇒ `spine_lost`.
- **m4baton relay:** the same execution, running while GuestGpu is parked.

## Findings

### FATAL

None. The sealed result (ADMITTED, K5 PASS, K1 PASS ⇒ PART2) stands on the evidence above.

### MAJOR

**M1 (protocol) — the timing measurement was not exclusive, and item 7 records it as idle.**

During the sealed `mutlib` timing (19:38:40–20:20:44) the executor:
- wrote the design (mtime 19:47:04);
- wrote the 595-line spine patch script (committed 19:51:38);
- compiled a clang probe (`scratchpad/cp.cpp` → `cp.obj`/`cp.asm`, 19:52:32–19:52:38);
- **applied the spine patch to seven source files** (19:57:21 and 19:58:31);
- committed ROADMAP items 2–6.

Two rules were broken:
- item 1: "пока он идёт — … только чтение кода исполнителем";
- item 3: "План с. 117 после замера `mutlib`: проект … код".

Item 7 then wrote "Машина во время замера простаивала (кроме чтения кода исполнителем)", which is false.

The number itself survives:
- no emulator build ran until about 20:21:12 (ninja log);
- no agents ran, per the task list;
- the side load was seconds of single-core CPU against 63 823 s of worker time.

**Fix:** correct the record. The 42.1 min figure may stay citable, with the caveat stated.

**M2 (decision basis) — item 3's "exhausted by the record" is over-claimed.**

1. **The witness figure is mis-cited.** Item 3 lists the six `AheadTake` phases with session-89 values but substitutes "петли свидетеля 852 (с. 88)" for the sixth. Session 89's sixth phase `da_t_ver_us` is **1 057.9 µs, or 1 027.9 µs instrument-corrected** (`local-session-89.md:213,232`), which is ≥ 1 ms. The 852.5 µs figure is only the loop bodies, measured on an older binary (`local-session-88.md:28`).
2. **`mh_emit` was never examined.** Its sub-parts ≥ 1 ms — com 2 275, rt 1 600, vtx 1 403, rec 1 280 µs — were only split (`local-session-96.md:64-76`), never analysed for removability. For com, only the descriptor writes are bounded (312 µs, s85); the transitions, about 1 ms, were not examined. The stop rule of item 2 itself names `mh_emit`.
3. **Resolution is only partly bounded.** 86.6 % of 76 % of `PrepareBindings` ≈ **2.6–2.7 ms/frame**. Only the repeat-skip mechanism is bounded (514 µs, or 222 µs strict, s88); a cheaper resolve was never measured.
4. **The drift is material.** `da_take_us` rose +390 µs since s89 (3 002 now); scaled, the witness phase is about 1.15–1.2 ms.

The stop rule therefore did not fire "by the record", and `fin117`, the measurement item 1 (2) planned, was cancelled on a wrong premise. Choosing route A is within the delegation; the stated ground is not.

**Fix:** record the correction. Keep "re-measure `takelap`/`bindlap`/`proglap` on the current build" as owed, not optional.

**M3 (code / measurement-only rule) — "Never changes what executes" (`gates.h` knob comment, design §2) is false at `spine` = 1/2 in general.**

(a) **Plan-time guest reads on the GuestGpu thread.**
- **What is read, and when:** at submission start, before earlier packets of the same submission have executed, the spine reads:
  - `IB` contents;
  - the `SET_PREDICATION` word (without the `BufferFlushAndWait` the real handler does, `graphicsRun.cpp:2506-2509`);
  - the `COND_EXEC` word;
  - the 14-dword-branch compare word;
  - the CX/SH/UC indirect register tables, through the real handlers `CpOpIndirect*Regs`.
- **Why it matters:** the codebase documents that a GuestGpu read of a GPU-dirty page faults and drains the whole GPU queue (`pm4Handlers.cpp:1357-1359`, `graphicsRun.cpp:2578-2582`, `2872-2874`). The spine can therefore add drains or downloads and move protection state.
- **Already present in default code:** the default walker `WalkComputeDispatches` already reads SH-indirect pairs and IB contents ahead of execution: at enqueue on the `DrawAheadWalk` thread under `dawalk=1`, otherwise at submission start on GuestGpu (`graphicsRun.cpp:1625` onward).
- **New with the spine:** CX/UC tables, and the predicate, `COND_EXEC` and branch words. These are typically GPU-written labels and predicates.

(b) **`EXIT` reachable only through the spine.**
- The real handlers `EXIT` on unknown or unsupported indirect register offsets (`pm4Handlers.cpp:2034,2072,2119,2135,2159,2177,2190`). A plan-time table that differs from the execution-time one (for example written earlier in the same submission by `WRITE_DATA`/`DMA_DATA`/`COPY_DATA` or by the GPU) can hit these.
- `ApplyContextStateOperation` does `EXIT_IF` on a push/pop imbalance (`graphicsRun.cpp:384,389,395`) when the spine's plan-time control flow diverges from the real one.
- In both cases the process terminates at a knob that should only measure.

**Not triggered in the sealed run:** `spine_ib` = `spine_cf_br` = `spine_cf_cond` = `spine_cf_pred` = 0, `spine_abort` 0, no failure markers. K5 and K1 stand.

**Inherited by PART2**, because the spine will run unseeded on the walker thread and must be tried in other scenes.

**Fix:** before part 2, record a design that:
- aborts the plan on these words rather than reading them;
- or reads the indirect tables without the `EXIT`ing handlers.

### MINOR

- **m1 — Item 4: the code preceded its record.**
  - `ff672e6` carries item 4, the design and the full spine code (`docs/session-117/tools/patch_spine117.py`, 595 lines: knob, counters, hook, digest).
  - The item-4 text was written at 19:51:33.98 and committed 4 s later. 26 KB of code cannot have been produced in those 4 s, so the code existed before item 4's "записано до кода".
  - Mitigations: item 3 (19:42) had already decided on gated, measurement-only code after a design; the design mtime (19:47:04) precedes the commit; nothing reached `src/` before 19:57:21, after item 5.
- **m2 — Item 9: order unprovable.**
  - The `graphicsRun.cpp` fix time was overwritten by item 10's edit.
  - The pattern of items 10, 12 and 13 (record script, then the change within about 8 s, then copy, then build) suggests compliance; default-refuted.
- **m3 — The pred's disclosure sentence is false.**
  - "The verdict rules and consequences above were recorded in ROADMAP items 4–5 before any smoke run" does not hold for the item-11 parts: K5 scope, `cram_write`, lost vs misal, walker fit, `armed`, `el_ops`.
  - Item 8 also said "нельзя: … менять следствия" after the smoke, and item 11 changed the walker-fit predicate that selects PART2_WALKER vs CLOSE_A. It was a stricter bug fix that could not affect this outcome, but it is in tension with item 8.
- **m4 — Admission hinged on the item-11 `armed` relaxation, and its stated reason is not what happened.**
  - Under the draft rule "arm-0 kept compares = 0" the run would have been NOT_ADMITTED.
  - The only arm-0 kept frame with compares is n = 8730 (block 76, its last reported frame, 17 compares).
  - The other 20 arm-0 frames with compares are each the first frame after an arm-1 → arm-0 switch, which is not kept.
  - This is a harvest-edge leak after the arm switch, not "a mode-2 submission blocked > 10 frames". The scorer keeps `frames[10:90]`, which includes the block's last reported frame.
- **m5 — The code's `spine_misal`/`spine_lost` meaning diverged from item 5's text without a record.**
  - The code in `e8404d9` (item 8's commit) had it; it was reconciled only by item 11, after the smokes.
  - Outcome unaffected (lost = 0).
- **m6 — Item 9's diagnosis ignored el = 0 mismatches already in smoke117.**
  - `log_smoke117.txt` has `SpineMismatch: sub=15 el=0 op=0x15 parts=sh`, which a dispatch's wave-size write cannot cause.
  - The `R_DISPATCH_RESET` cause was therefore visible in the first smoke. Item 10 presents "с элемента 0" as new.
  - Cost: one extra build and one extra smoke.
- **m7 — Item 14 over-states.**
  - "его цена на GuestGpu 0,61 мс на кадр (1,8 % кадра)" is the plan's self-timer. The ABBA arms were `spine=1|spine=2`, with no `spine=0` arm, so the frame-level cost of the spine is unmeasured.
  - "перед каждым draw/dispatch" holds for arm-2 frames only.
- **m8 — Item 12's "черновые мутанты перегоняются" left no artefact.**
  - `mut_spn117.draft.out.txt` dates 21:05:58, before seal 01.
  - Superseded by the sealed 104/104 run on 01r2.
- **m9 — The design disagrees with item 4 and the code on `SET_PREDICATION`.**
  - `designA4_spine.md:51` says it goes through the real handler; the code (correctly) evaluates it inline without `BufferFlushAndWait`.
  - The design was not updated.
- **m10 — The shadow's handler calls consume the real processor's one-shot log budgets.**
  - Sites: `pm4Handlers.cpp:356-358` (SPI_TMPRING), `1296-1305` (GDS_OA), `2049-2055` (`static bool logged`), `2060-2065`.
  - Under `spine`≠0 those diagnostic lines come from the plan at submission start, not from the execution point.
- **m11 — `SpineCmp` counts calls that compare nothing.**
  - `SpineCheck` adds `SpineCmp` before the `el >= m_spine_snap_count` early return.
  - The only guard is misal at `SpineFinish`, which is skipped if the plan is later lost or the submission is still pending at exit.
  - Theoretical here (lost = 0, no misal).
- **m12 — Item 2's "work, not waiting"** inside the `PipelineCache::m_mutex` holds is inferred, not measured on `d3a981a2` (see Q4).
- **m13 — The pre-seal check left no written report.** `check_spn117/` holds only scripts, fixtures and mutants; ROADMAP item 11 is the only record of its findings.
- **m14 — "перекомпилирован один graphicsRun.cpp" (item 11 (8), pred) is imprecise.**
  - Build117c recompiled 7 translation units because the version header was regenerated; only `graphicsRun.cpp`'s source changed.
  - The shader hash is unaffected.
- **m15 (info) — Windows user path in committed harness files.** Pre-existing practice.
