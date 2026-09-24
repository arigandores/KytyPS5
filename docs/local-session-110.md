# Session 110 — SHIPPED `cspfree=1`: the walker's compute prefetch takes no lock on a (source, specialization) hit — Δ mean frame ≈ −200 µs at the pin (pooled, full block; the sealed window read −418.7); the duration guard passes

**Single source of truth for session 110.** Mirrored into git as `docs/local-session-110.md`. Harness root
`C:/kyty/s110`. Everything below is measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0` and now **`cspfree=1`**.
Arm 0 of `shp110` (today's defaults before the change): median of block means `dt_us` ≈ 31.0 ms (≈ 0.54× game
speed). 60 FPS is not promised.

---

## 1. Result

1. **Port** `C:/kyty/s109/s110_port.py` (`544b231d…`, 2 143 lines): `PORT DIAGNOSTIC: clean; carried=9057 ledger=75
   skipped=62`; 58 sealed texts (56 in `prev109/pred`); `gates.cpp` 139 entries (111 + 28), ABSENT 40.
2. **Stall-duration instrument** (record `1d9dcf0`, code `3d8af4c`, build `b3f7a2c9…`): in
   `PipelineCache::GetComputePipeline` the wall of a synchronous compile (from the "not found" branch, lock held, to
   the return) and of a wait for a pending entry; counters `cs_sync_new_us`, `cs_sync_wait_us` (`FrameTrace-x`, raw
   µs) and a log line per stall `CsStall: kind=new|wait us=<N> id=<id> hash=0x<hash>` (always on, ≤ 4 096 a process).
   Main `FrameTrace` line unchanged; nothing under `src/graphics/shader/**`.
3. **`stl110`** (sealed `pred/01_stl110.md` `e2055106…`, 8 entries A B B A A B B A, `cspfree=0|1`, compute precache off,
   pinned): **NOT_ADMITTED** — `STALL_SYNC` failed in all eight entries: 1–2 stalls of every entry happen at startup,
   before the first `FrameTrace-x` row (e.g. a ~12.5 ms wait for shader `0x5c118936…`, id 497, in both arms), and no
   row reports that interval's counters. A scorer defect. The decision numbers seen while diagnosing (D_A 44 401, D_B
   42 427, M_A 14 206, M_B 12 334 µs) were not used (ROADMAP item 4, before the re-run).
4. **`stl110b`** (sealed `pred/02_stl110b.md` `0299b403…`, the same rule, `STALL_SYNC` counting only lines after the first
   row; 8 new entries; ADMITTED): **PASS — D_A 19 569, D_B 10 878 µs (bound 44 461); M_A 12 293, M_B 1 619 µs (bound
   22 293)**; events S_A 15, S_B 16 (the `ent109b` count difference did not reproduce).
5. **`shp110`** (sealed `pred/03_shp110.md` `4f02d284…`, ABBA `cspfree=0|1`, 600 s, pinned, 96 pairs, ADMITTED): **SHIP —
   Δ mean `dt` −418.7 µs (2·SE 135.3, t −6.19)**; Δ`cpu_net` −302.1 (t −4.48); `da_walk_us` −55.3; `gpu_busy_us` +32.2
   (t 2.00); `cspfree_hit` 266 a flip, `cspf_have` 0; H1 H2 H4 H5 H6 HIT, **H3 MISS** (the gain exceeds [−300, 0] and is
   2.7× `frm109`'s −154.1). Video `vsh110` (pinned, `cspfree=1` in the gate text): 4 008 frames, 0 glitches ⇒ SHIP.
   **Size corrected by the audit (§7 item 1):** the sealed window (frames 60–88 of each block) caught arm-independent
   ~48 ms hitches mostly in arm-0 tails; over the full block `shp110` −233.1 (2·SE 56.6) and `frm109` −171.3 (2·SE
   70.3) agree; **pooled −202 ± 45 µs ≈ +0.65 % game speed at the pin**. SHIP holds under every window. Seal 02's
   predictions: L1–L4 HIT, **L5 MISS** (D_B/D_A 0.556).
6. **Default `cspfree=1`** (ROADMAP item 6 first; `0776f6a`); **build
   `072861c89193c3726232e44e78be4f36172254af826394b56c8bf671ef609c21`**, installed; video `vid110` (pinned, `cspfree`
   absent from the gate text): 4 004 frames, 0 glitches, `cspfree_hit` 265.8 a flip, `cspfree_bad` 0 — `check110.py`
   (`2efd7414…`) PASS. The session-109 audit's `cspfree` code debts (a skip after an entry's retirement; "moved" on a null
   source; raw pointers in a thread-local memo) stay debts: a change after the measurement would need a new one.

## 2. Harness

`C:/kyty/s110`: `stl110.py`/`stl110b.py` (from `ent109b.py` by `make_stl110.py`/`make_stl110b.py`; fixtures
`test_stl110.py`/`test_stl110b.py` by `make_test_stl110.py`/`make_stl110b.py`; 41 / 43 mutants killed incl. the six
`ent`-lineage audit survivors of session 109), `shp110.py` (from `frf109.py` by `make_shp110.py`; 152 fixtures, 155
mutants killed incl. the four `frm`-lineage survivors; on the sealed copy only `CONSTANTS` differs — it pins the
unsealed generator output), `check110.py`, `go110.sh`, `go110b.sh`, `go110c.sh`, `go110v.sh` (each holds the sealed-run
lock), scored-build copies `kyty_emulator_b3f7a2c9.exe` (in s110) and `kyty_emulator_2f593229.exe` (in s109).

## 3. Source, builds, provenance

Commits: `9031f17` (session 109 close), `1d9dcf0` (records), `3d8af4c` (instrument), `94e4ba0` (seal 01 + port),
`016722c` (NOT_ADMITTED record + seal 02), `30d33db` (stl110b PASS), `c512a98` (seal 03), `0776f6a` (SHIP + default),
`f1de07a` (build video), the session commit. Builds: `b3f7a2c9…` (`3d8af4c`; stl110, stl110b, shp110, vsh110),
`072861c8…` (`0776f6a`; installed; vid110). Labels `-dirty` = the `nlohmann_json` submodule's deleted PNGs only; not
bit-reproducible. No push.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `stl110_1..8` | duration guard, entries ABBA, precache off | NOT_ADMITTED (scorer's STALL_SYNC) |
| `stl110b_1..8` | the same rule, corrected term, new entries | PASS: D 10.9 vs 19.6 ms, max 1.6 vs 12.3 ms |
| `shp110` | ship ABBA `cspfree=0|1`, 600 s | SHIP: Δ`dt` −418.7 (2·SE 135.3) |
| `vsh110` | video, `cspfree=1` gate text | 4 008 frames, 0 glitches |
| `vid110` | video of build `072861c8`, default | 4 004 frames, 0 glitches; `check110` PASS |

## 5. Next

The walker's remaining hold of `PipelineCache::m_mutex` is `QueueDrawAhead` (tag 1). Session 111: a sealed
observation under the new defaults (`plkstat=1`) to see the contention left, then `daslot` (per-slot synchronisation
of the M1 table, `design109.md` §A) behind a knob with a verify mode, sealed ABBA and video. Plan:
`docs/next-session-111.md`.

## 6. Proved, and not proved

**Measured.** At the pin in Sky Garden, `cspfree=1` shortens the mean frame by ≈ 200 µs (pooled over `shp110` and
`frm109`, full block, −202 ± 45); with the compute precache off it adds +0.33 ms of post-load stall per 150 s entry and
the duration rule passed (the rule is dominated by one arm-independent startup race — weak, audit §7 item 2); with the
precache on there are 0 stalls. **Not measured.** The gain without the pin.
**Not proved.** Safety in scenes not measured; additivity; 60 FPS.

## 7. Adversarial audit

One agent, three lenses, sealed as `pred/04_audit110.md` (`983b97ed…`). **Recount CONFIRMED**, **Protocol HOLDS**, **Code NOT REFUTED**. Findings: (1) **MAJOR** — the size −418.7 is inflated by the estimator's window (frames 60–88): full block −233.1 / −171.3, pooled −202 ± 45 µs; SHIP holds under every window — quote ≈ −200 µs; future seals pre-register the full block; (2) **MAJOR** — the D/M duration rule is dominated by one arm-independent startup race (shader 497, frame 3) and fails 12 % of the time with no effect; the conclusion stands (post-load +0.33 ms per entry; 0 stalls with the precache on); (3) MINOR — seal 02's predictions unscored (L5 MISS), L5's band set after `stl110`'s numbers were seen; `check110.py` gaps (pin mode 2, `cspf_have`, env) — none changes a verdict; `cspfree` code debts perf-only. Report: `C:/kyty/s110/audit110/AUDIT110.md`.
