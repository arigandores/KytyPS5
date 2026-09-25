# Session 117 — lock-contention tracks closed; route A (parallel command-stream processing), stage 4 part 1: the shadow spine is built and passes its sealed test (0 mismatches in 19.1 M compares; self-timed 0.61 ms a frame on GuestGpu, a lower bound); a full `mutlib` v4.1 seal run costs 42 min; the audit reopened the GuestGpu micro-track candidates; no speed-up of the game shipped

**Single source of truth for session 117.** Mirrored into git as `docs/local-session-117.md`. Harness root
`C:/kyty/s117`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 117 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–15.

**Opening and closing numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1
daguard=1 bdanarrow=0 titleasync=1`, installed build `d3a981a2…` (git `7c73f26`) — unchanged at the close (the spine
build `3cde1af8` ran the seal and was then replaced by the verified `d3a981a2`). New knob `spine` (0..2, default 0,
measurement only). 60 FPS is not promised.

---

## 1. Result

1. **`mutlib` v4.1 full `--control --no-memo` on the sealed `ttl114b` = 2 523.7 s = 42.1 min** (28 workers; v2 in
   session 114 took 68.1 min; the "≈ 20 min" of session 116 was a cached run). 345/345 killed, controls 3/3, rows equal to
   session 114's report (item 7). That is the price of one big ABBA seal.
2. **User's question "maybe stop fixing the mutex?" — yes (item 2):** sessions 106–112 removed the lock waits at
   ≈ 0.2 ms each; `obs116` showed GuestGpu busy the whole frame, the 92 % "under the render mutex" is the work itself.
   Lock-contention tracks closed unless a wait ≥ 1 ms reappears.
3. **Micro-tracks on the GuestGpu thread "exhausted by the record" (item 3) — RETRACTED by the audit (item 15):** the fine split planned for this session is
   on disk since sessions 86–89 (`AheadTake` six phases, largest 0.85 ms; `PrepareBindings` 76 % image loop; route C
   closed at slot granularity; draw merge dead; frame replay C = 0.0035) — no part ≥ 1 ms removable by a local change
   (numbers from older binaries: a limit). **The program returns to route A** (reopened for maximum FPS in session 104,
   G = 5.7 ms; best case −3…−6 ms = 10–20 % game speed [I], first gain at stage 5 after ~6–10 sessions), **stage 4
   (the shadow spine, the cheapest test able to close the route) before the rest of stage 3.** The audit found the
   citation wrong: session 89 put the witness verify at 1.03–1.06 ms (≥ 1 ms), the `mh_emit` parts were never checked for
   a removable part, image resolution (~2.6 ms) is bounded only by its repeat-skip mechanism — these candidates are
   re-measured on the current build in session 118 together with stage 4 part 2.
4. **Batching and overlap (item 6, user's question "write several patches and test them together?"):** measurement-
   only instruments go in one build / one sealed run / one scorer; shipped defaults keep one ABBA each but candidates are
   prepared together; mutation runs overlap coding and builds (only sealed game runs and timing measurements are
   exclusive); mutants by risk.
5. **The shadow spine (items 4–5, 8–10; code `e8404d9`, `fbcfd49`, `36c8350`; build `3cde1af8`):** knob `spine`
   (`KYTY_SPINE`, 0..2, default 0, latched per submission): a second `CommandProcessor`, seeded from the real one at each
   submission start, walks the submission through the SAME register handlers, follows IBs and evaluates `COND_EXEC` /
   the 14-dword branch / predication itself; mode 2 snapshots `HW::Context`/`UserConfig`/`Shader` + 8 processor registers
   (4 096 B) before every draw/dispatch and the real processor compares memcmp-first, then member-wise
   (`operator== = default` added to the 61 register types — `clang-cl` 19 has no `__builtin_clear_padding`). 17 counters
   `spine_*`. Three unsealed smoke runs found two spine defects (the dispatch's own `SetCsWaveSize(mode)`; the
   `R_DISPATCH_RESET` processor reset) — fixed, disclosed in the seal.
6. **Seal 01r2 `spn117` (items 11–14): ADMITTED, K5 PASS, K1 PASS ⇒ PART2.** Pre-seal check (agent): no blocker, three
   MAJOR fixed before the seal (the walker-fit rule could never fail; K5 lost `spine_bad` in incomplete frames; the
   meaning of `spine_misal`). Seal re-issued twice before any run (CRLF line endings from my edit scripts; the suite's
   `ALL OK` line). Sealed mutants 104/104, controls 3/3, 26 s. Run 21:14–21:20, pinned, ABBA `spine=1|spine=2`, 39 + 40
   blocks: **0 `spine_bad` / `spine_misal` / `cram_write` / mismatch lines over 19 107 669 compares** (ratio 1.0001),
   **spine 608.0 µs a frame on GuestGpu by its own timer** (bar 1 200; median 555, p99 942, max 1 155), 26 192 packets and 5 309 elements a frame (el/ops 1.00), walker fit
   (3 207 µs needed against a 32 917 µs frame without the spine). No IB, `COND_EXEC`, predication or 14-dword branch in
   Sky Garden.
7. **Session audit (item 15):** see §5.

## 2. Code

`e8404d9` (knob `spine`, 17 counters, `operator==` on the 61 register types), `fbcfd49` (wave size), `36c8350`
(`R_DISPATCH_RESET`). Build `3cde1af8` (pinned `C:/kyty/s117/kyty_emulator_3cde1af8.exe`; embedded label
`…-gfbcfd49-dirty`: built from the working tree a second before `36c8350`). Nothing under `src/graphics/shader/**`,
`hardwareContext.h` is outside the shader-cache signature. No push.

## 3. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `t0_ttl114b` | — | `mutlib` v4.1 full `--no-memo` timing on the sealed `ttl114b` (no game) | 42.1 min, 345/345 |
| `smoke117`, `smoke117b`, `smoke117c` | none (item 8) | Sky Garden 120 s, `spine=2`, unpinned | two defects found and fixed; the third clean |
| `spn117` | 01r2 | Sky Garden 300 s, pinned, ABBA `spine=1|spine=2`, build `3cde1af8` | ADMITTED, K5 PASS, K1 PASS ⇒ PART2 |

## 4. Proved, and not proved

**Proved:** a second pass over PM4 through the real register handlers reproduces the register state before every
draw/dispatch of Sky Garden within a submission; its own timer reads 0.61 ms a frame on GuestGpu and it would fit on the
walker thread even at three times that. **Not proved:** the frame-level price (the in-run control arm 2 − arm 0 shows the
self-timers missing ~0.55 ms of what they add; there was no `spine=0` arm); the carry of state across submissions (the spine is seeded at every submission start);
GPU-dependent words (none met in the scene); another scene; anything about route A's gain — the next three stage-4 terms
(K3 pass histogram, K4 image overlap, carry) are part 2.

## 5. Audit (item 15)

Two agents, own parsers. **Recount: every number of item 14 and of the score CONFIRMED**, admission 18/18, seal 01r2 hashes
match the chain's. **Protocol:** re-seals only line endings and the suite's final line; smokes disclosed; item 11's fixes
stricter, not tuned to the smokes. **MAJOR:** (1) the 0.61 ms price is a self-timed lower bound, not proved (in-run
control +1 639 ± 281 µs `dt` against +1 087 ± 27 self-timed); (2) item 7's "machine idle" is false — design, commits, a
6-s clang probe and a source patch ran during the timing (the 42.1 min is practically unaffected; the heavy build came
after); (3) item 3 mis-cited the record — the micro-track stop rule did not fire; (4) the claim "never changes what
executes" is false at `spine` 1/2 (plan-time guest reads, spine-only `EXIT` paths; not triggered in `spn117`). MINOR: the
spine code predated its item 4 by seconds (order broken); item 9's order unprovable; the pred's "all rules predate the
smokes" is wrong for parts of item 11; admission leaned on item 11's `armed` relaxation (17 compares at the block's last
frame — the estimator window should be 10–88); BDA regime NEW in both arms; the installed exe was swapped back after
scoring. **Decisions:** PART2 stands; micro-track candidates re-measured in 118; a safe plan (GPU-clean reads only,
abort instead of `EXIT`) before part 2.

## 6. Next

`docs/next-session-118.md`: ONE build and ONE sealed run (item 6): a safe spine plan first; stage 4 part 2 — K3
(elements per host render pass), K4 (image-set overlap of adjacent segments at W = 2 and 4), the carry (an unseeded spine
on the walker thread compared at submission starts); and, in its own schedule arm, the re-measure of the micro-track
candidates on the current build (witness verify, image resolution, `mh_emit` parts) for a track by the ≥ 1 ms rule.
