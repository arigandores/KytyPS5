# Session 134 — the prototype `b2reuse` (B2: return the offset of the first ring copy on a repeat of the key in an interval without synchronisation) with a kill smoke, correctness smokes and the sealed ABBA `kp134`

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 122 — ЗАПИСИ ДО ДЕЙСТВИЙ" items **150** (the s133 close: `bc133` read as `B2_PASSES` (а); close
questions — R2 13.30 % outside ±5 %, the RC5 zero does not prove correctness, other parts only with a mechanism, arm 2 − arm 1 is the
price of value 2 (б); audit and process (в); 5 sessions without shipping, no new course point (г); the `mh_bind` inventory row (д); the
selection criteria (1′)/(3′)/(5′) and both pre-registered outcomes (е); debts (з)), **151** (the acceptance of the selection `HPP-202`:
the lead check (а); **the lead argument aloud — a hit is charged the class-average iteration, P(kill at the smoke) 0.45** (б); answers
(г); **the constants of the prototype (д)(1)–(7)**; the kill-at-smoke outcome (е); the chain (ж)) and **152** (holds, the form of the
kill condition, step 6 stops after the kill row, the harness port); items 55 (б), 76 (б), 77 (б), 78 (е), 83 (б), (г), 84–87, 89 (г),
105 (в), 113, 123 (в), 132 (г), 134 (з)–(к). `docs/session-134/levers134.md` (§2 the iteration price per class, §3.1 B2 — mechanism,
(1′) split, (3′), (5′) inputs, §5 the proposal and the fallback census `rbslow`); `docs/session-133/design133.md` (the 37 `Reset` sites,
generation of the interval); `docs/session-133/audit/AUDIT133.md`; `docs/session-119/designs/witness_binding.md` §2.4;
`ps5 em/CLAUDE.md` environment entries of 133 and 131; `ps5 em/docs/agent-team.md` (general rules 15–19, sections 19–21).
Code (at `016eb5ee`): `src/graphics/host_gpu/pipeline/descriptors.cpp` (`NativeStorageBuffer` :208–364, const-bank direct :252 and
aligned :314, stream slot before `ObtainBuffer` :293, `RebindBuffers` :3896–3980), `cache/bufferCache.cpp` (`ObtainBuffer` :1337–1585,
`m_gpu_modified_ranges` :1575 / `NoteGpuWrite` :1580, `HasGpuDirtyBytes` :2207–2208, reset `gpuw` :2558), `streamBuffer.cpp:304` (ring),
`commandScheduler.cpp:782` (host submit), `RbCen::Reset` sites (`pm4Handlers.cpp`, `graphicsRun.cpp:992/4045/4067/4096`,
`memory.cpp:926`, `memoryAddressSpace.inc:168`, `image.h:168`), `src/common/gates.{h,cpp}`, `src/common/frameStats.h`.

**Open the report with these numbers:** session 133 — the census `bc133` (build `cf414f46`, `rbcen=1|2`, 83 complete blocks 41 / 42,
NEW) read **`B2_PASSES`** — a candidate, not a gain: L = `rb_stream` + `rb_cbank` of arm 1 **1 133.0 ± 6.0 µs/frame [c, the UPPER bound
of what B2 can remove]**, the repeat share of COPIES 0.64658, divergence 0 / 2 341 357 with a live control 0.02753; R2 +602.2 = 13.30 %
of `bl_buf` — outside ±5 %, a band. Audit recount CONFIRMED to the tenth, 0 MAJOR / 3 MINOR. The s133-close selection (`levers134.md`):
the iteration price of the ring classes is constant, not bytes (≈ 0 ns/KB [c-OLS]; `stream` 59.7, `cbank` 69.8 ns/iteration [c]);
removable by B2 [I] upper / centre / low **440 / 312 / 118 µs/frame** — the lead says aloud that a hit is charged the class-average
iteration while a repeat is likely warm, so the centre at "upper estimates lie 2–20×" is ≈ 156 < 200: **P(kill at the smoke) 0.45**.
Nothing shipped; **sessions without shipping: 5 (129–133)**; s134 is a prototype session, so after it the count is **6 in any outcome**
(7 if s135 does not ship). Course base **51.38 %** without a new point (32 438.4 µs, arm 0 of `dd131`, `d19a4f8a` WITH the instrument,
NEW) — not the time of the installed `9235a7ac`, not a drop against 53.36 %. None of these numbers is a gain or a ceiling. 60 FPS is
not promised.

## Rule of the session

As in session 133 (items 123 (в), 134 (г), 140 (в), 150 (в)): every decision in `ROADMAP.md` before the first action; the time in a
decision header is `date -u` at writing and not later than the item's commit; **times in step rows only from `date -u` at the event;
reading an input not earlier than its commit and the `ROADMAP.md` item named as read** (general rule 19); extending a step's scope only
by a `ROADMAP.md` item before the action; commits in the shared folder only `git commit --only -- <paths>`. Before any expensive
irreversible action (full mutant run, game run) re-read the `ROADMAP.md` items written after the link was issued and the link's
comments. Counts and sha in a report come from the last output of the suite, with its path and sha256; **the first line of a suite's
output is `suite <name> sha256 <suite sha> target <name> sha256 <target sha>`** (item 150 (в), process 4). An acceptance item that creates
or cancels a link is executed in the same heartbeat before "Принято". A link with a platform `terminal access failure` comment is
re-issued by the lead at the next heartbeat, idle time in UTC in the acceptance report. Every specialist step writes `## Step N — …` in
`C:/kyty/s134/FACTS.md` BEFORE `done`, time in UTC, the scale named in every table. Mutants: the chain once at step 0 with a wall
forecast before the start; ≤ 8 workers; ONE full parser `mutlib` v4.1, cap 15 min; session budget 30 min (item 87 (б)(3)). Blocks by
`GateArm:` lines, never by `blk`; row n = F goes to the LEAVING block; window 10–88 of item 55 (б) named with its item number. The
harness checks `C:/kyty/SEALED_RUN.lock` BEFORE `procload.py` in every call; the chain call of a registered tag is verbatim from the
seal, `PLWAIT` in the log; one attempt per registered tag. **The installed build is `9235a7ac…`; every chain with the game restores it.**
While the lock exists nobody edits, commits or starts processes. Long runs in the foreground; start time and expected end in the step
comment. No agent creates user interactions. `PYTHONIOENCODING=utf-8`. Privacy grep over the whole tree before commits (the list lives
in `C:/kyty/scrub/`, never in git). A third "Доработать" is never given to one link.

## Chain (item 151 (ж)): every specialist step carries an `executionPolicy` review stage by the lead

There is no step 1 (the selection was made at the s133 close, item 151). Steps 0 and 2 start in parallel. Root `HPP-3` is `blocked` on
step 10.

## Steps

**0. Harness Engineer — port `C:/kyty/s134`** from `s133` (item 152 (г)): `gates_base.txt` with explicit `armcopy=0`, `acinline=0`,
`lwin=0`, `dispceil=0`, `protceil=0`, `rtskip=1`, `mutsite=1`, `plkstat=1`, `bindlap=1`, `pathlap=1`, `rbcen=1`, `b2reuse=0`; the chain
`go134a.sh` with the smokes `s1s134` (ABBA `b2reuse=0|1`, reference, pin, 200 s — the kill condition), `s2s134` (2, reference, 150 s),
`s3s134` (2, desert `intro_next --stable-draws 500`, 150 s), `s4s134` (3, reference, 150 s — the control), `s5s134` (2, forced OLD by
the s113 method, 150 s), `s6s134` (1, Vulkan validation, duplicate limit lifted, 150 s), `s7s134` (spare, only by a lead item), and the
registered `kp134` (ABBA `90+1800` `b2reuse=0|1`, 300 s, no video, `KYTY_GPU_MARKERS=0`; item 151 (д)(4)), `kk134` (2, 300 s), `kv134`
(1) / `kw134` (0) (video, 120 s); a smoke parser for the counters of item 151 (д)(1), the kill row of item 152 (б) and the correctness
conditions 151 (д)(3)(а)–(е), (ж), each with a fixture, ending in `ALL OK`; the fixture of the 37 `Reset` sites (item 151 (г)(3));
lock before `procload`; `PLWAIT` fixture; one attempt; restore of the installed build; refusal on `protceil` ≠ 0. ONE full chain
mutant run with the forecast. No game run.
**2. Probe Designer — design** `docs/session-134/design134.md` of `b2reuse` under item 151 (д)(1)–(3) (constants are not changed; a
deviation only as a question): the probe point per class with its code line, the table key `(vaddr, size, alignment, kind)` and entry,
the generation latch (value changes only on a reset, an interval is never split between values), "0 is the old path byte for byte",
value 2 (copy always, fresh copy into the descriptor, shadow on every insert in ordinary memory, byte check and path check on EVERY
hit), value 3 (interval reset only on `sub`), the instrument condition (a hit iteration still writes its `Stream`/`Cbank` class of
`rbcen`), the hooks alive at `b2reuse` ≥ 1 independent of `rbcen`, the refusal at `rbcen=2`, the answer to every input (5′)(а)–(ж) of
`levers134.md` §3.1, the cost at 1/2 [I], P(0) of every rare event of the reading. Questions to the lead. No game run, no emulator code.
**3. Red Team — adversarial review** `docs/session-134/design/review134.md` (SOUND / SOUND_WITH_CHANGES / UNSOUND, RCs): find a path
where a hit returns bytes the old path would not (a tracker bit, `m_gpu_modified_ranges`, epoch or CPU write without a reset); find a
consumer keyed by `(handle, offset)` that breaks on a repeated ring slot; find a way value 0 changes behaviour; check sites against
the code, not the text.
**4. Emu Engineer — code** (after the lead accepted 3): the knob as accepted, LAST knob line, `check_gate_order.py` before the build;
`git status --short -- src` empty → ONE measuring build → pinned copy `C:/kyty/s134/kyty_emulator_<sha8>.exe`; `shader_cfg_tests`
delta 0 against HANDOFF §4; NOT installed. No game run.
**5. Red Team — code review** `docs/session-134/design/codereview134.md` (PASS / PASS_WITH_FIXES / FAIL): path 0 untouched; **a line
for every writer of the tracker bits, `m_gpu_modified_ranges` and epochs, and for every consumer keyed by `(handle, offset)` — set,
`bindkey`, `ShadowQueue`** (item 151 (д)(3)(з)); a found path without a reset is MAJOR before smokes; the 37 `Reset` sites wired at
`rbcen=0`; refusal; knob order.
**6. Harness Engineer — smokes** `s1s134`…`s6s134` (after 5 and 0): **first `s1s134` and the kill row as a separate report line**
(point mean of the pairwise L reduction, SE, pairs, `b2r_hit`/`b2r_n` against 0.647, Δ `dt_us`); L reduction < 200 ⇒ stop and report,
no further smokes (item 151 (е), 152 (в)); otherwise `s2s134`…`s6s134` with each condition of item 151 (д)(3)(а), (б), (д)–(ж) as a
line. A death or hang is a finding, no repeat. Questions to the lead.
**7. Harness Engineer — scorer `kp134.py`, fixtures, the seal `pred/01_kp134.md`** (Δ by pairs, the corrected estimator of item 77 (б),
BDA of item 83 (г), DRS of item 78 (е), the reading of item 151 (д)(5) with every edge, `DEBT` for < 10 pairs, window edges, the row
Δ `kp134` / L reduction); ONE full `mutlib`. After the lead's acceptance of step 6 only.
**8. Harness Engineer — the sealed `kp134`, the registered `kk134` and videos `kv134`/`kw134`**; `s20_vidglitch` on `kv134`, frame
sheets of both for the lead; restore the installed build.
**9. Session Auditor — audit**: own recount of `kp134` (and of the `s1s134` kill row) by own parser; the correctness conditions of item
151 (д)(3) each by its log; protocol of items 150–152 and later; MAJOR/MINOR; not proven; debts; section «Процесс» (≤ 5 items);
`audit134/`, git `docs/session-134/audit/`; privacy of both trees.
**10. Roadmap Lead — close**: the reading of item 151 (д)(5) (or the kill outcome of item 151 (е)); the course row (base = arm 0 of
`kp134`, instrument named, not comparable to 51.38 %); shipping decision for step 0 of s135 or the fork "≥ 6 sessions without shipping"
to First agent; process items; documents; commit of both repositories; the chain of session 135 before closing.

**Outside the chain:** nothing (item 152 (д)).

## Must not be claimed

60 FPS; the removable 439.6 / 312.2 / 117.6 or any census or selection number (L 1 133.0, 0.647, "0.647 × L", `mh_bind` 12 223.1,
`bl_buf` 4 527.3) as a gain or a ceiling; the smoke L reduction as a speed; that ≈ 0 ns/KB is the price of the mechanism; that B2 is
correct before every condition of item 151 (д)(3) holds; OLD; other scenes beyond the desert smoke; that s134 ships anything; the arm 2
− arm 1 Δ of `bc133` as a speed; 51.38 % as the time of `9235a7ac` or as a drop against 53.36 %; rows built by `blk`; a timing number
beside another heavy job.
