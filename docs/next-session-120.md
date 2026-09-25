# Session 120 — after route A: one measurement build that turns the GuestGpu micro-track ceilings into measurements (texture-memo conflicts R1, same-pass render-target memo `spcen`, stage image-block repeat R2)

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 119 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–5 (item 4: route A closed for maximum FPS,
G₂ = 2 216.5 µs; item 2: the removability designs and the rule for this session; item 5: the audit — the window rule
for derived scorers, and the variant A-walker as an open debt in §7, decided only after this session's outcome);
`C:/kyty/s119/FACTS.md` (git `docs/local-session-119.md`); `docs/session-119/designs/witness_binding.md` and
`emit_parts.md` (file:line of every span and candidate).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1 bdanarrow=0 titleasync=1 spine=0 slicecen=0`, installed build `d3a981a2…` (`7c73f26`),
game speed ≈ 52 % (`dt` ≈ 31.7 ms). Route A is closed for maximum FPS (session 119: the W = 2 tax 1.65 ms ate the
parallel half). By code reading no GuestGpu micro-track candidate has a removable part proved ≥ 1 ms [I]: image-resolve
package R1 + R5 + R2/R3 1.2–1.9 ms upper [I] (R1 texture-memo conflicts 0.70–0.90), render-target memo within an open
pass 0.9–1.1 ms, with the commit-side transit skip 1.3–1.5 ms [I]. 60 FPS stays the direction without a route with a
live estimate.

## Rule of the session

As since session 102: every decision in `ROADMAP.md` before the first action; a sealed consequence is never set aside;
seals with fixtures and mutants (`mutlib` v4.1 frozen, FULL runs `--control --no-memo --work-dir/--cache-dir
C:/kyty/s120/...`); edit scripts write LF; suites end with `ALL OK`; patches with backslashes only through files written
by the Write tool (the command hook mangles heredoc backslashes — session 119); measurement-only instruments batched
into one build and one sealed run; nothing under `src/graphics/shader/**`; audit before closing.

## Steps

0. **Harness `C:/kyty/s120`** (port s119 files; pinned `kyty_emulator_d3a981a2.exe`).
1. **Design in ROADMAP before code** (from the two design reports; each instrument measurement-only, default 0):
   - **R1 census** in the texture memo of `ResolveTextureWith`: per lookup, a tag-only shadow of a 4-way and an 8-way
     table of the same 4 096 entries and of a 16 K-slot direct table — would it have hit where the real table missed;
     and the miss path's own time, live in `KYTY_FRAME_TRACE=lite`. The ceiling of R1 = (misses a bigger table would
     have hit) × (measured miss time − hit time).
   - **gate `spcen`**: per draw, the condition of the render-target memo within an open pass (same targets, the new
     image-state counter unmoved, not a depth clear, not a sampled depth target) evaluated WITHOUT acting; the time of
     `AcquireRenderTargets` and of the `CommitBindings` transit loop booked into separate would-hit counters; beside a
     would-hit the full work runs and `sp_rt_bad`/`sp_tr_bad` count any difference of its result (must stay 0).
   - **R2 counter**: stages whose image block repeats the previous draw's (images only), and their resolve time.
   - Optionally the knob that skips the session-74 census probe in `CleanBackingPage` (traced runs only), to measure
     how much of `da_t_ver` is the probe — measurement hygiene, not a player-visible gain.
   Rules written before code: a speed track opens only for a candidate whose MEASURED removable time is ≥ 1 ms a frame
   with every `*_bad` = 0; else the GuestGpu micro-tracks in Sky Garden are recorded as exhausted and the next session
   decides what remains (e.g. another scene, or the GPU side).
2. **Code, one build, an unsealed smoke (disclosed), a derived scorer + fixtures + mutants, a pre-seal check agent, the
   seal, `mutlib` v4.1, ONE sealed pinned 300-s ABBA run** (arm P: the census instruments on; arm M: off — the ABBA also
   prices the instruments).
3. **Consequences fixed before the run.** Audit, close; if a track opens, its design and first seal go into
   `next-session-121.md`.

## Must not be claimed

60 FPS; any gain from a census (a would-hit is a ceiling, not a speed-up); that route A could still pay at W = 4 (K4
failed at W = 4 in session 118) or at W = 2 (G₂ < 3 ms in session 119); a speed number beside another heavy job.
