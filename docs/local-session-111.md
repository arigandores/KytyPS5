# Session 111 — SHIPPED `daslot=1`: the walker's M1 queue no longer takes `PipelineCache::m_mutex` — Δ mean frame −231 ± 82 µs at the pin against `daslot=0` of the same build (≈ +0.73 % game speed); against the session-110 build unmeasured (audit)

**Single source of truth for session 111.** Mirrored into git as `docs/local-session-111.md`. Harness root
`C:/kyty/s111`. Everything below is measured unless marked otherwise.

> AUDIT: §7.

**Opening numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1` and now
**`daslot=1`**. `shp111` block levels: arm 0 (today before the change) mean `dt_us` 31 458.8 (≈ 0.530× game speed), arm 1
31 247.5 (≈ 0.533×). 60 FPS is not promised.

---

## 1. Result

1. **Port** `C:/kyty/s110/s111_port.py` (`060f9348…`, 2 587 lines): 79 files, carried 7 234, skipped 2 104; 62 sealed
   texts landed (`prev110/pred` 60); ledger `port111_ledger.json`.
2. **Records before action** (`1f488f7`): the `obs111` rule (tag 1 ≥ 100 µs a flip ⇒ build `daslot`) and the `daslot`
   protocol written before its code (ROADMAP §0.1 "СЕССИЯ 111" items 1–3).
3. **Code** (`690c40e` knob and protocol, `dc1136b` counter `da_q_free`, `6b340d7` counters `da_chk_ok`/`da_chk_bad`;
   patch `docs/session-111/tools/patch_s111.py`): per-slot guard byte (`TryGuardSlot` 64 spins / `GuardSlot` /
   `UnguardSlot`), new slot state `AheadTaking` (a draw takes Ready → Taking under the guard, verifies and copies outside
   it, publishes Ready/Empty; `taken = 1` before publishing), hints and variants published once (compiled SRT,
   `Fingerprint` and `ClassOf` first; atomic fields; the walker reads a hint under a seqlock and never calls `ClassOf`),
   atomic `memo_generation` and `ahead_slots` pointer, new `ahead_queue_mutex` around every `QueueAhead`. Knob
   **`daslot`** (`KYTY_DRAW_AHEAD_SLOT`, 0..2, LAST knob row): 0 — `QueueDrawAhead` under `m_mutex` (plus the guards),
   1 — only `ahead_queue_mutex`, 2 — 1 plus a slot-key check at every take (`da_slot_bad`, `DaSlotVerify: MISMATCH`).
   Guards and publish-once are unconditional. Counters (`FrameTrace-x`, raw): `da_q_free`, `da_guard_busy`,
   `da_q_taking`, `da_hint_defer`, `da_hint_torn`, `da_slot_bad`, `da_chk_ok`, `da_chk_bad`. Nothing under
   `src/graphics/shader/**`. Build `c8235c90…` (`6b340d7`).
4. **`obs111`** (sealed `pred/01_obs111.md` `98531828…`, 300 s, pinned, `plkstat=1`, build `072861c8`): **BUILD_DASLOT** —
   GuestGpu's contended wall at `m_mutex` 236.1 µs a flip (239.7 contended acquisitions), **tag 1 (`QueueDrawAhead`)
   232.6 µs = 98.5 %**, tag 2 = 0 (`cspfree` took the prefetch out entirely); the walker's `QueueDrawAhead` holds 965.6
   µs a flip (1 080 calls × 0.89 µs); spin share ≥ 0.70; P1–P5 HIT.
5. **`vds111`** (sealed `pred/02_vds111.md` `0dadb4f7…`): **NOT_ADMITTED (GATES, ARMED)** — my gate file appended
   ` smemocheck=1` after the base's `smemocheck=0`; the loader takes the FIRST assignment, so the check never armed
   (`da_chk_ok` 0). The scorer caught it as designed. Not read (ROADMAP item 4, before the re-run).
6. **`vds111b`** (sealed `pred/02b_vds111b.md` `a4043073…`, replaces 02; `gates_slot2b.txt` with the in-place replacement;
   300 s, pinned): **GO** — `da_chk_ok` 60 770 502, `da_chk_bad` 0, `da_slot_bad` 0, mismatch lines 0, `da_q_free` 7 820 081,
   `da_guard_busy` 1, `da_q_taking` 2, `da_hint_defer` 278, `da_hint_torn` 0, `cspfree_bad` 0.
7. **`shp111`** (sealed `pred/03_shp111.md` `594e2402…`, ABBA `daslot=0|1`, 600 s, pinned, 94 pairs, ADMITTED): **SHIP —
   main estimator (frames 10–89) Δ mean `dt` −230.7 µs (2·SE 81.8, t −5.64)**; secondary window 60–88 −231.5 (2·SE 102.7);
   Δ`cpu_net` −234.5 (t −6.08); `da_walk_us` −162.1 (t −29.3); `da_queue_us` 1 334 → 1 191; `da_take_us` +8.6 (n.s.);
   `da_late` +5.3 a flip (5.4 → 10.7, t 33.9); `gpu_busy_us` +22.4 (t 1.97); `da_q_free` 1 077.1 a flip in arm 1, 0 in
   arm 0; `da_guard_busy` 0.0; K1–K6 HIT. Video `vss111` (pinned, `daslot=1` in the gate text): 3 944 frames, 0 glitches.
8. **Default `daslot=1`** (ROADMAP item 5 first; `38d8f86`); **build
   `0c8a13f28245ea879c25725ebf4258a944308d24f7c6c11fd4bee95ec3814c8c`**, installed; video `vid111` (pinned, `daslot` and
   `cspfree` absent from the gate text): 4 023 frames, 0 glitches, `da_q_free` 1 122.0 a flip, `da_slot_bad` 0,
   `cspfree_hit` 265.8, `cs_sync_new`/`cs_sync_wait` 0 — `check111.py` (`1f740594…`) PASS (ROADMAP item 6, `c314429`).

## 2. Harness

`C:/kyty/s111`: `obs111.py` (78 fixtures, 91 mutants killed), `vds111.py` (44 fixtures, 32 mutants), `vds111b.py` (from
`vds111.py` by `make_vds111b.py`; its fixtures include the `vds111` defect), `shp111.py` (from `shp110.py` by
`make_shp111.py`; 180 fixtures, 209 mutants; on the sealed copy only `CONSTANTS` differs, by design), `check111.py` (from
`s110/check110.py` by `make_check111.py`), chains `go111.sh`, `go111b.sh`, `go111v.sh` (each holds the sealed-run lock),
gate files `gates_obs111.txt`, `gates_slot1.txt`, `gates_slot2.txt` (defective), `gates_slot2b.txt`; scored-build copies
`kyty_emulator_c8235c90.exe`, `kyty_emulator_0c8a13f2.exe`.

## 3. Source, builds, provenance

Commits: `6d8f690` (session 110 close), `1f488f7` (records), `690c40e` (code), `dc1136b`, `6b340d7` (counters), `d6c1264`
(seals 01/02 + port), `be8d862` (seal 03), `27aa877` (obs111/vds111 + seal 02b), `38d8f86` (SHIP + default), `c314429`
(build video), the session commit. Builds: `c8235c90…` (`6b340d7`; vds111, vds111b, shp111, vss111), `0c8a13f2…`
(`38d8f86`; installed; vid111). `obs111` ran on `072861c8…` (session 110). Not bit-reproducible. No push.

## 4. Runs

| tag | what | outcome |
|---|---|---|
| `obs111` | contention census, `plkstat=1`, 300 s | BUILD_DASLOT: tag 1 232.6 µs = 98.5 % |
| `vds111` | verify `daslot=2` + `smemocheck` (appended, wrong) | NOT_ADMITTED (check off) |
| `vds111b` | verify, in-place gate file | GO: 60.8 M checks, 0 bad |
| `shp111` | ship ABBA `daslot=0|1`, 600 s | SHIP: Δ`dt` −230.7 (2·SE 81.8) |
| `vss111` | video, `daslot=1` gate text | 3 944 frames, 0 glitches |
| `vid111` | video of build `0c8a13f2`, default | 4 023 frames, 0 glitches; `check111` PASS |

## 5. Next

The audit's MAJOR: arm 0 was slowed by the new protocol inside the walker's `m_mutex` hold, so the gain against the
session-110 code is unmeasured. Session 112: knob `daguard` (at `daslot=0` the M1 queue, holding both `m_mutex` and
`ahead_queue_mutex`, skips the slot guards and the seqlock — safe by construction), a verify run with arm transitions
in the shipped mode, and the ABBA `daslot=0 daguard=0 | daslot=1` with the rule recorded in ROADMAP (decision after
session 111). Plus the code debts (`GuardSlot` yield, `ahead_threads` size race, comments) and the scorer rules.
Plan: `docs/next-session-112.md`.

## 6. Proved, and not proved

**Measured.** At the pin in Sky Garden, taking the walker's M1 queue off `m_mutex` shortens the mean frame by 230.7 µs
(main estimator; the secondary window agrees); the verify run found 0 key mismatches and 0 re-materialization
mismatches over 60.8 M takes; videos clean.
**Not proved.** The gain against the session-110 build (arm 0 carried the new protocol inside the walker's `m_mutex`
hold — audit MAJOR; model ≈ −100…−200 µs); that the guard/seqlock protocol is race-free (the audit found no race; the
verify run sampled one scene at 42.2 ms a flip, not the shipped mode); anything off the pin, in other scenes, or
additively with earlier gains; 60 FPS.

## 7. Audit

One agent, three lenses; sealed addendum `pred/04_audit111.md` (`83358a9c…`); report and scripts
`C:/kyty/s111/audit111/` (`AUDIT111.md`).

* **Recount — CONFIRMED.** Every number reproduced by own parsers. The window does not matter this time: full block
  −233.3 (2·SE 81.3), thirds −193 / −218 / −275, flips capped at 34.5 ms −216; long flips land evenly (57 vs 51). GPU
  2 325 / 2 325 MHz, throttle mask equal, CPU clocks equal, DRS area 2 001.7 / 2 001.3. Mechanism: the one-vblank share
  11.33 → 12.62 % (−222 of −231 µs). Arm 1 burns +4.8 % process CPU (threads run instead of waiting).
* **Protocol — HOLDS.** Records before actions; 22 seal hashes match, each committed before its run; only
  `ScheduleWakeup` and the heartbeat inside the three sealed windows; fixture suites reproduce.
* **Code — NOT REFUTED.** No race at `daslot=1`; no `Taking` leak, no ABA, no use after free.

Findings: **MAJOR** — arm 0 is not the pre-session code (walker time per `QueueDrawAhead` 1.007–1.032 µs before the
session, 1.237 in arm 0); quote −231 ± 82 µs against the same build's `daslot=0`, unmeasured against session 110.
**MINOR** — `vds111b` predictions D1–D5 unscored (all HIT); `check111.py`/`make_check111.py`/`go111v.sh` outside git and
SEALS111 (hashes added, marked post-run), no fixtures, stale docstring; the verify run was not in the shipped mode;
`shp111.py` red on its own `CONSTANTS` fixture by design; 5 of 12 new mutants survive (threshold edges); `GuardSlot`
never yields; `Taking` skip does not advance `walk`/`uses`, `da_late` 5.4 → 10.7; stale `m_mutex` comments; the old
`ahead_threads` size race.
