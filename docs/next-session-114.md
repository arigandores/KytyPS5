# Session 114 — correctness first: the 3-second stall (a wait on an unsubmitted tick), then `mutlib` v3, then the next speed track

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 113 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 11–22 (item 18: the stall; item 21: the
close; item 22: the session audit) and §7 (the rows «ожидание неподанного тика», «`mutlib` v3», «`bdastamp` дыра общего
региона»); `C:/kyty/s113/FACTS.md` (git `docs/local-session-113.md`); `C:/kyty/s113/audit113/final/` (the session audit);
`C:/kyty/s106_stage/mutlib/README.md` and `review3/` (the v2 holes).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1 bdanarrow=0`, installed build `1678d3f4…` (video `vid113` 3 976 frames, 0 glitches).
Session 113: `bdanarrow=1` verified (forced OLD, 0 misses on 11.8 M would-skip regions) and **kept at 0** — Δ`dt`
−83.2 ± 68.0 µs in a forced OLD regime, the ship bar −100 not met. One 3-s freeze (`vbn113k`): the priority-operation
thread waited 2.975 s on the recording (unsubmitted) tick while the GPU idled — not seen in the other runs of the day,
new in form against the archive. 60 FPS stays the direction without a route with a live estimate.

## Rule of the session

As every session since 102: decisions recorded in `ROADMAP.md` before the first action; a seal per run; fixtures on
every term and edge; mutants through `mutlib` (v2 until v3 is accepted; derived scorers `--control --no-memo`, item 15);
generators use whole-line anchors (item 16); nothing else on the machine during a sealed chain; audit before closing.

## Steps

0. **Harness root `C:/kyty/s114`**, copy what the steps need (enter_scene.py, gates files, the pinned exe
   `kyty_emulator_1678d3f4.exe`), check `C:/kyty/SEALED_RUN.lock` is absent.
1. **The stall (correctness first).** Facts: role=4 (the priority-operation thread, `commandScheduler.cpp` —
   `PriorityOperationsThread`), `requested` = `current` (the recording tick), history ending at `current − 1`, submit
   backlog 0, GPU utilisation 0 % for ~2.5 s. The instrument (`623009f`) names the queue site of a stalled priority
   operation (`PriorityStall: … site=+0x…`) and GuestGpu's idle entries with a pending unsubmitted priority operation
   (`GpuIdlePrio:`); in `vbn113m` and `vid113`: `prio_stall` 0, `gw_idle_prio` 0, `prio_unsub` ≈ 5.7 a frame.
   (a) Offline: list every `DeferPriorityOperation` caller (`sync.cpp` EOP/labels, `bufferCache.cpp` stale-read and
   readback prefetch, `textureCache.cpp` image download) and every path after which GuestGpu can wait (idle without a
   timeout, `graphicsRun.cpp:~685`; the 100-ms blocked sleep; the `else if (complete)` branches that run the GC with no
   flush after it) — which of them can leave a priority operation on the recording tick with nothing to submit it?
   (b) A catch run: a seal for N entries (e.g. 4 × 300 s, forced OLD as in 01f, where the stall was seen) whose only
   purpose is the `PriorityStall:` site; admission without `NO_MARKER` (the stall IS the event sought).
   (c) The fix as a knob (default 0 first, own seal): submit the recording buffer when a priority operation sits on it
   and GuestGpu is about to wait (or when the priority thread's wait passes a bound) — verified by the counters and a
   pinned ABBA for price.
2. **`mutlib` v3** (offline, a workflow is fine outside sealed runs): MAJOR-1 (memo key vs a result carrying the file
   path), MAJOR-2 (a second mutant collection), the MINOR fixes from `review3/`; the draft-only-mutant rule of item 20
   (a marker in the mutant script for unfilled-seal anchors). Accept on the six suites plus the session-113 ones.
3. **The next speed track**, chosen by the rule and recorded before action. Candidates with evidence today:
   (a) the latency of priority operations (EOP interrupts, readbacks) — `prio_unsub` ≈ 5.7 a frame start on the
   unsubmitted tick, so each waits for the next submit (lazy flush window `KYTY_EOP_FLUSH_US` 300 µs); measure the
   queue-to-run delay per site before any change; (b) the remaining `PipelineCache::m_mutex` contention after
   `daslot`/`cspfree`; (c) ROADMAP §1 phases (`mh_bind`, `mh_emit`, `mh_prog`).

## Must not be claimed

60 FPS; that the stall's cause is known before the site is caught; that `bdanarrow=1` gains in the natural regime or in
other scenes.
