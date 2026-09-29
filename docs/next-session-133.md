# Session 133 — one measurement: the census tag `bc133` on the game with the measurement-only knob `rbcen` 0..2 — the split of the unsplit remainder of `mh_bind` and of the `RebindBuffers` phases, plus the census of the B2 repeat of ring copies; the s134 lever is selected from its numbers at the s133 close

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" items **140** (the s132 close: no `kp132` verdict (а); shipping,
4 sessions without shipping (б); audit and process decisions (в); the course row (г); **the inventory that replaces item 76 (ж)** (д);
the s133 lever `mh_bind` and the selection at the close with both pre-registered outcomes (е); base (ж); debts (з)) and **141** (the
acceptance of the selection `HPP-190`: none passes (а); value 2 included (б); **the census constants (в)(1)–(7)**; the chain (г));
items 136 and 139 (K16 and K5 parked), 121 (1) (census numbers of R2 do not open a track), 134 (ж)(1)–(5) (selection criteria), 55 (б),
76 (б), 83 (б), 84–87, 89 (г), 105 (в), 132 (г). `docs/session-133/levers133.md` (§2 the populations of `RebindBuffers`, §3 M1 = B2,
§5 the census proposal); `docs/session-132/audit/AUDIT132.md`; `docs/session-119/designs/witness_binding.md` §2.4 (B2);
`ps5 em/CLAUDE.md` environment entries of 131 and 129; `ps5 em/docs/agent-team.md` (general rules 15–18, sections 19–20).
Code: `src/graphics/host_gpu/renderer/renderDraw.cpp` (`mh_bind` span, `PrepareGraphicsBindings` ≈ :4008–4171),
`pipeline/descriptors.cpp` (`PrepareBindings`, `FindBuffers` :4178, `PrepareBda` :4219, `RebindBuffers` :3803, const-bank copies
:247–320, `NativeUpload` :3893), `cache/bufferCache.cpp` (`ObtainBuffer` :1330–1560, stream ring :1508–1534, `SynchronizeBuffer`),
`src/common/gates.{h,cpp}`, `src/common/frameStats.h`.

**Open the report with these numbers:** session 132 — **no sealed run**: the K16 selection (`levers132.md`) and the K5 selection
(`levers132k.md`) both gave "none passes item 134 (ж)(1)–(4)"; K16 and K5 **parked, not closed**; audit recount CONFIRMED to the tenth,
0 MAJOR / 4 MINOR. Nothing shipped; **sessions without shipping: 4 (129–132)** — with the census s133 it becomes 5, said aloud. Course
base **51.38 %** without a new point (32 438.4 µs, arm 0 of `dd131`, `d19a4f8a` WITH the instrument `mutsite=1 plkstat=1`, NEW) — not
comparable to 53.36 %, not the time of the installed `9235a7ac`; remainder 15 771.4 µs. The s133 lever — `mh_bind` (draw binding
preparation): **11 286.1 µs/frame [c]** on GuestGpu (`dd131` arm 0); split in `spk118` M (`bindlap=1`): `bl_prep` 4 235.0 (`bl_res`
3 213.4), `bl_buf` 3 868.1 (81.1 ns/slot on 47 696.3 slots), `bl_img` 1 094.7, **unsplit 1 770.8**; the stream-ring copies of
`ObtainBuffer` 13 965.8 / 19 567.9 KiB per frame [c], never timed in NEW (OLD `s78`: 902.1 µs [c-OLD], not transferable). None of
these numbers is a gain or a ceiling. 60 FPS is not promised.

## Rule of the session

As in session 132 (items 123 (в), 134 (г), 140 (в)): every decision in `ROADMAP.md` before the first action; the time in a decision
header is `date -u` at writing and not later than the item's commit; extending a step's scope only by a `ROADMAP.md` item before the
action; an identity is checked at the level the design defines it (**row** for `bc133`, item 141 (в)(2)); a reading that needs a rare
event prints P(0) before data; commits in the shared folder only `git commit --only -- <paths>`. **Before any expensive irreversible
action (full mutant run, game run) re-read the `ROADMAP.md` items written after the link was issued and the link's comments** (item
140 (в), process 1). **Counts and sha in a report come from the last output of the suite, with its path and sha256** (process 3).
**An acceptance item that creates or cancels a link is executed in the same heartbeat before "Принято"** (process 2). Every specialist
step writes `## Step N — …` in `C:/kyty/s133/FACTS.md` BEFORE `done`, time in UTC, the scale named in every table. Mutants: the chain
once at step 0 with a wall forecast before the start; the part driver admits a job only if its expected wall ends before the part cap,
from the first part; ≤ 8 workers; ONE full parser `mutlib` v4.1, cap 15 min; session budget 30 min (item 87 (б)(3)). Blocks by
`GateArm:` lines, never by `blk`; row n = F goes to the LEAVING block; window 10–88 of item 55 (б) named with its item number. The
harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call; the chain call of a registered tag is verbatim from the
registration, `PLWAIT` in the log. One attempt per registered tag. **The installed build is `9235a7ac…`; every chain with the game
restores it.** While the lock exists nobody edits, commits or starts processes. Long runs in the foreground; start time and expected end
in the step comment. No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the
list lives in `C:/kyty/scrub/`, never in git). A third "Доработать" is never given to one link.

## Chain (item 23): every specialist step carries an `executionPolicy` review stage by the lead

0 and 1 start in parallel (the knob name and the counter names are constants of item 141 (в)). Root `HPP-3` is `blocked` on step 9.

## Steps

**0. Harness Engineer — port `C:/kyty/s133`** from `s132`: `gates_base.txt` with explicit `armcopy=0`, `acinline=0`, `lwin=0`,
`dispceil=0`, `protceil=0`, `rtskip=1`, `mutsite=1`, `plkstat=1`, `bindlap=1`, `pathlap=1` and `rbcen=0`; the chain `go133a.sh` with the
smokes `s1s133` (`rbcen=1`, reference, 150 s), `s2s133` (`rbcen=2`, reference, 150 s), `s3s133` (`rbcen=2`, Vulkan validation,
duplicate limit lifted), and the registered `bc133` (ABBA `90+1800` `rbcen=1|2`, reference, pin, 300 s, no video, `KYTY_GPU_MARKERS=0`;
item 141 (в)(4)); a smoke parser (counters alive, the row identity of item 141 (в)(2), `rb_b2_chk` > 0 at 2, death markers of item
89 (г) with the exclusion of item 132 (г)) with a fixture on every member ending in `ALL OK`; lock before `procload`; `PLWAIT` fixture;
one attempt; restore of the installed build; refusal on `protceil` ≠ 0. ONE full chain mutant run with the forecast. No game run.
**1. Probe Designer — design** `docs/session-133/design133.md` of the census under item 141 (в)(1)–(3): every mark site (line by line,
outside the intervals it splits), the 1/8 slot sampling and its estimator, the row identity and why the remainder must be ≤ 5 %, **the
full list of the B2 interval resets** (submission start, every synchronisation packet, every GPU and emulator write into guest memory —
each named with its code site), the shadow of the 1/16 byte check (ordinary memory, never the ring slot), "0 is the old path byte for
byte", "1/2 change no value, decision or side effect", cost at 1/2 [I]. Questions to the lead. No game run, no emulator code.
**2. Red Team — adversarial review** `docs/session-133/design/review133.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, RCs): find a guest-
memory writer or a synchronisation point the reset list misses; find a mark inside an interval it splits; find a way value 1/2 changes
behaviour; check the named sites against the code, not the text.
**3. Emu Engineer — code** (after the lead accepted 2): the knob as accepted; `check_gate_order.py` before the build; `git status
--short -- src` empty → ONE measuring build → pinned copy `C:/kyty/s133/kyty_emulator_<sha8>.exe`; `shader_cfg_tests` delta 0; NOT
installed. No game run.
**4. Red Team — code review** `docs/session-133/design/codereview133.md` (PASS / PASS_WITH_FIXES / FAIL): path 0 untouched, marks and
counters as accepted, every reset source wired, knob order, refusal.
**5. Harness Engineer — smokes** `s1s133`…`s3s133` (after 4 and 0): identity of the row as a separate report line; counters alive;
validation clean. A death or hang is a finding, no repeat. Questions to the lead.
**6. Harness Engineer — parser `bc133.py`, fixtures, the registration** `pred/01_bc133.md` (phase levels of arm 1 with SE by blocks, the
B2 shares of arm 2, the reading of item 141 (в)(6) including every edge, the row identity, window edges; BDA mode row); ONE full `mutlib`.
**7. Harness Engineer — the registered `bc133`**; restore the installed build.
**8. Session Auditor — audit**: own recount of `bc133` (levels, identity, B2 shares) by own parser; protocol; MAJOR/MINOR; not proven;
debts; section «Процесс» (≤ 5 items); `audit133/`, git `docs/session-133/audit/`.
**9. Roadmap Lead — close**: the reading of item 141 (в)(6); the course row (no new point); the re-assessment and **the selection of the
s134 mechanism at the close, before the brief** (process 4 of s132); process items; documents; commit of both repositories; the chain of
session 134 before closing.

**Outside the chain:** nothing; any off-chain task gets a formal consumer (item 73 (в)).

## Must not be claimed

60 FPS; any census level (`mh_bind` 11 286.1, `bl_buf` 3 868.1, the unsplit 1 770.8, ring 19 567.9 KiB, OLD 902.1, the [c-OLS]
regressions 274–432) as a gain or as the ceiling of a mechanism; that B2 is correct or removable; OLD numbers as NEW levels; the Δ of
arm 2 − arm 1 as a speed; the instrument cost [I] as a measurement; 51.38 % as the time of `9235a7ac` or as a drop against 53.36 %; that
K16 or K5 are closed; other scenes; rows built by `blk`; a timing number beside another heavy job.
