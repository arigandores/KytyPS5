# Session 132 — one lever: a PROTOTYPE of a K16 mechanism inside the dispatch span, with self-check and the sealed ABBA `kp132`; the mechanism is chosen by the selection of step 1 (Lever Researcher) from the phase census of `dd131`; K5 is the fallback

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 134 (the close of 131: the L verdict and `armcopy` (а); the K16
verdict and the three dose calibrations (б); shipping (в); audit decisions, the identity-level rule, the scope-extension rule,
privacy (г); process items (д); the course (е); **the re-assessment and the selection criteria (ж)(1)–(5)**; **the prototype
constants (з)(1)–(7)**; debts (и); the chain (к)); items 124–125 (the census `dc_ph_*`, `dc_prot`, instrument `mutsite=1 plkstat=1`),
132 (г) (the shutdown-race exclusion of the death-marker guard — carried into the s132 seals), 127 (the `rtskip` self-check pattern),
97 (е) (the `armcopy` prototype constants — the template of item 134 (з)), 84–87, 83 (г), 77 (б), 78 (е), 66 (а), 55 (б).
`docs/session-131/audit/AUDIT131.md`; `docs/local-session-131.md` (§9.6 — the census table); `docs/session-131/dd131.md` §2 (the span
line by line), §5 (the census phases), §5.5 (what the census can and cannot say); `ps5 em/CLAUDE.md` environment entries of 131
(`lwin`, `dispceil`, `dc_*`), 127 (`rtskip`), 129 (`armcopy`); `ps5 em/docs/agent-team.md` (rules 15–16, section 19).
Code: `src/graphics/host_gpu/renderer/renderCompute.cpp` (`DispatchDirect` span `:286`–`~HoldLap`), `renderContext.cpp` (`PrepareBda`),
`cache/bufferCache.cpp` (`RebindBuffers`, `ObtainBuffer`, `SynchronizeBuffer`), `pipeline/pipelineCache.cpp` (`GetComputeProgram`,
`ProgramCache::Get`), `pageManager.cpp` (`Protect`), `src/common/gates.{h,cpp}`, `src/common/frameStats.h`.

**Open the report with these numbers:** session 131 — L **`NOT_RESOLVED`** (ΣH = 0 at `armcopy=2` in `lw1s131`/`lw2s131`/`lw5s131`,
20 921 rows; controls alive) ⇒ `armcopy` stays **`ARMCOPY_INCORRECT`**, track L parked; `dd131` **`K16_OPEN`** (NEW, 41 pairs, Δ `dt_us`
+1 990.8 ± 179.5, adjusted +2 043.4 ± 146.8, low +1 811.3; OLD 0 pairs `DEBT`; dose delivery 1.01146; slope 0.83 — a calibration,
not a gain); audit CONFIRMED to the digit, 0 MAJOR / 2 MINOR. Nothing shipped; **sessions without shipping: 3 (129–131)**. Course base
**51.38 %** (32 438.4 µs, arm 0 of `dd131`, `d19a4f8a` WITH the instrument `mutsite=1 plkstat=1` and the census, NEW) — not comparable
to 53.36 %, not the time of the installed `9235a7ac`; remainder 15 771.4 µs. The census of arm 0 (µs/frame, [c], not a ceiling):
span 2 466.4 on 268 dispatches; `bda` 896.8 (≈ 4 `PrepareBda` per frame), `buf` 506.6, `prog` 376.1 (`pl_cs_hold` 340.1, no
contention), `prep` 202.1, `com` 164.7, `img` 106.0; subset `dc_prot` 655.7. 60 FPS is not promised.

## Rule of the session

As in session 131 (items 123 (в), 134 (г)): every decision in `ROADMAP.md` before the first action; the time in a decision header is
`date -u` at writing and not later than the item's commit; **extending a step's scope beyond its assignment only by a `ROADMAP.md`
item before the action** (a comment is not enough); **an identity is checked at the level the design defines it (row / block /
log)** — another level is a row that names its level; a track whose reading needs a rare event prints the expected count and P(0)
before data (item 134 (д)(1)); commits in the shared folder only `git commit --only -- <paths>`. Every specialist step writes
`## Step N — …` in `C:/kyty/s132/FACTS.md` BEFORE `done`, time in UTC, the scale named in every table. Mutants: the chain once at
step 0 with a wall forecast before the start; the part driver admits a job only if its expected wall under load ends before the
part cap, from the first part; ≤ 8 workers; ONE full scorer `mutlib` v4.1, cap 15 min; session budget 30 min by item 87 (б)(3).
A regime with 0 pairs prints `DEBT`. Blocks by `GateArm:` lines, never by `blk`; row n = F goes to the LEAVING block. Window 10–88 of
item 55 (б) named with its item number. The harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call; the chain
call of a sealed tag is verbatim from the seal, `PLWAIT` in the log. One attempt per registered tag. **The installed build is
`9235a7ac…`; every chain with the game restores it.** While the lock exists nobody edits, commits or starts processes. Long runs in the
foreground; start time and expected end in the step comment. No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy
grep over the whole tree before commits (the list lives in `C:/kyty/scrub/`, never in git). A third "Доработать" is never given to
one link.

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

0, 0п and 1 start in parallel. The lead accepts step 1 with a NEW `ROADMAP.md` item naming the mechanism, the knob name and the target
phase (or, if no candidate passes item 134 (ж)(1)–(4), cancelling steps 2–8 and setting K5). Root `HPP-3` is `blocked` on step 10.

## Steps

**0. Harness Engineer — port `C:/kyty/s132`** from `s131`: `gates_base.txt` with explicit `armcopy=0`, `acinline=0`, `lwin=0`,
`dispceil=0`, `protceil=0`, `rtskip=1`, `mutsite=1`, `plkstat=1` and the new knob `=0` (its name a constant filled by fixture after the
lead accepts step 1); the chain `go132a.sh` with the smokes `s1s132` (ABBA `90+1800` `<knob>=0|1`, reference, 150 s — the kill
condition of item 134 (з)(2) from the census `dc_ph_*` by pairs), `s2s132` (2, reference, 150 s), `s3s132` (2, desert `--level
intro_next --stable-draws 500`, 150 s), `s4s132` (3, reference, 150 s), `s5s132` (1, Vulkan validation, duplicate limit lifted),
`s6s132` (reserve, registered only if the lead names it); the sealed `kp132` (item 134 (з)(4)), the registered `kk132` (2, reference,
300 s), the videos `kv132` (1) / `kw132` (0); a smoke parser (kill condition, `<p>_bad`/`<p>_chk`, control alive, death markers with
the exclusion of item 132 (г)) with a fixture on every member ending in `ALL OK`; lock before `procload`; `PLWAIT` fixture; one
attempt; restore of the installed build; refusal on `protceil` ≠ 0. ONE full chain mutant run with the forecast. No game run.
**0п. Session Auditor — privacy** (item 134 (г)(2)): replace the two remaining names of foreign applications in
`docs/next-session-79.md` by the neutral word; add them to `C:/kyty/scrub/checks.txt` (outside git); replace the second `gh` account
in `ps5 em/INDEX.md` by a neutral line (private repository `ps5-em`); `git grep` over both trees; one commit per repository with
explicit paths; no history rewrite, no push. The system-browser process name is NOT replaced (item 134 (г)(1)).
**1. Lever Researcher — selection of the K16 mechanism** (item 134 (ж)): document `levers` on the task and a copy
`docs/session-132/levers132.md`: from the census of `dd131` (arm 0 rows of `C:/kyty/s131/log_dd131.txt`, `docs/local-session-131.md`
§9.5–9.6, existing counters of the log — e.g. `bda_*`, `sync_up_kb`, `prot_gpu_ro_*`, `acopy_wait_us`, `stg_pool_*`, `pl_cs_*`) and the
code of the span (`dd131.md` §2), ≤ 3 candidate mechanisms, each with: the target part and its arm-0 level [c]/[M]; the removability
argument by code (what exactly is not done, and why the result is the same); the check against §3 "Что закрыто" (novelty in one line
with the item); the self-check at 2 and the positive control at 3; correctness risk; sessions to ship; the expected Δ at slope 0.75–0.90
[I]. A recommendation, or "none passes (1)–(4)" aloud. External sources read-only. No game run, no code.
**2. Probe Designer — design** `docs/session-132/design132.md` of the accepted mechanism under item 134 (з)(1)–(7) and the item of
step 1's acceptance: sites, the latch, the state of the mechanism and its invalidation (every source named), values 0..3, counters,
refusals, "0 is the old path byte for byte", the kill-condition phase, the self-check and why the positive control must fire, P(0)
of the rare-event readings, cost at 1/2. Questions to the lead. No game run, no emulator code.
**3. Red Team — adversarial review** `docs/session-132/design/review132.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, RCs): build an
input where 1 gives a different result from 0 that 2 does not catch; build a dead positive control; check the named sources against
the code, not the text.
**4. Emu Engineer — code** (after the lead accepted 3): the knob as accepted; `check_gate_order.py` before the build; `git status
--short -- src` empty → ONE measuring build → pinned copy `C:/kyty/s132/kyty_emulator_<sha8>.exe`; `shader_cfg_tests` delta 0; NOT
installed. No game run.
**5. Red Team — code review** `docs/session-132/design/codereview132.md` (PASS / PASS_WITH_FIXES / FAIL): path 0 untouched, the
mechanism and the self-check as accepted, every invalidation source wired, knob order, refusals.
**6. Harness Engineer — smokes** `s1s132`…`s5s132` (after 5 and 0): the kill condition of item 134 (з)(2) as a separate report line;
conditions 134 (з)(3)(а), (б), (д), (е). A death or hang is a finding, no repeat. Questions to the lead.
**7. Harness Engineer — scorer, fixtures, the seal** `pred/01_kp132.md` (both estimators, every window edge, every outcome of item 134
(з)(5) incl. `DEBT` for 0 pairs; BDA and DRS; census rows Δ by phase); ONE full `mutlib`; `SEALS132.txt`.
**8. Harness Engineer — the sealed `kp132`**, then `kk132` and the videos `kv132`/`kw132` (`s51_vidglitch.py`, sheets for the lead);
restore the installed build.
**9. Session Auditor — audit**: own recount of `kp132` (both estimators, base) and of the correctness conditions (з)(3); protocol;
MAJOR/MINOR; not proven; debts; section «Процесс» (≤ 5 items); `audit132/`, git `docs/session-132/audit/`.
**10. Roadmap Lead — close**: the `K16P_*` verdict and shipping decision (step 0 of s133 on `GAIN` ∧ correctness); the course row;
the re-assessment; process items; documents; commit of both repositories; the chain of session 133 before closing.

**Outside the chain:** nothing; any off-chain task gets a formal consumer (item 73 (в)).

## Must not be claimed

60 FPS; that `armcopy=1` loses guest writes or does not; that the `s10s130` event was P8 or a loss; the calibration Δ of `dd131`, its
slope, the prior 2 120 or any census number as a gain or as the ceiling of a mechanism; the expected Δ of the selection ([I]) as a
measurement; linearity of the dose; OLD for K16; 51.38 % as the time of `9235a7ac` or as a drop against 53.36 %; other scenes; rows
built by `blk`; a timing number beside another heavy job.
