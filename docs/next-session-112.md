# Session 112 — "maximum FPS", track 1: what `daslot=1` really gains against the pre-session code (`daguard`), and the `daslot` debts

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 111 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–7 and **the executor's decision after
session 111**; §7 (session-111 rows); `C:/kyty/s111/FACTS.md` (git `docs/local-session-111.md`) incl. §7;
`C:/kyty/s111/audit111/AUDIT111.md` (MAJOR-1, the code notes); the sealed texts `C:/kyty/s111/pred/*` (`SEALS111.txt`).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1`. Shipped in session 111: `daslot=1` — Δ mean frame −231 ± 82 µs at the pin **against `daslot=0` of
the same build** (≈ +0.73 % game speed); the audit showed arm 0 was slowed by the new protocol inside the walker's
`m_mutex` hold (walker time per `QueueDrawAhead` call 1.0 → 1.24 µs), so the gain against the session-110 code is
unmeasured (model ≈ −100…−200). 60 FPS stays the direction without a route with a live estimate.

## 1. The port, first

`s112_port.py` fresh in `C:/kyty/s111/` (SRC `C:/kyty/s111`, DST `C:/kyty/s112`), modelled on
`C:/kyty/s110/s111_port.py` (`060f9348…`). Sealed texts 62 → 67 (`01_obs111.md`, `02_vds111.md`, `02b_vds111b.md`,
`03_shp111.md` + the audit addendum `04_audit111.md` → `prev111/pred/`). r6 gains `obs111.py`, `vds111.py`,
`vds111b.py`, `shp111.py` `PRED`. `gates_base.txt` unchanged; `gates.cpp` 140 entries (`daslot` default 1), ABSENT 41
(+1 per new knob before the port). Do not carry `kyty_emulator_*.exe`, `fx_*` fixture dirs, `audit111/*.pkl`. Class the
generators (`make_shp111.py`, `make_vds111b.py`, `make_check111.py`), the one-shots and `audit111/`.

## 2. Code (ROADMAP record before code — already made: decision after session 111, items 1 and 3)

1. Knob **`daguard`** (`KYTY_DRAW_AHEAD_GUARD`, 0..1, default 1, LAST knob row). `QueueDrawAhead` reads `daslot` and
   `daguard` once; when `daslot == 0 && daguard == 0` it holds `m_mutex` (as today) and passes "no guards" down:
   `QueueAhead` still takes `ahead_queue_mutex`, `QueueAheadSource` skips `GuardSlot`/`UnguardSlot`, hints are read
   directly (their writers hold `m_mutex`). Safety argument in the patch header: guard takers are only
   `QueueAheadSource` (serialized by `ahead_queue_mutex`) and `AheadTake` (holder of `m_mutex`); workers only CAS the
   state. Counter `da_q_noguard` (calls in that mode) — the arming proof of arm A.
2. `GuardSlot`: N spins (e.g. 256) then `SwitchToThread`; count `da_guard_yield`.
3. `ahead_threads` resized and its size read under the same lock (the old race).
4. Comments: `plan_fingerprint`/`plan_class`/`taken`/`pixel` now protected by publish-once / the guard / `Taking`;
   `gates.h` "today" for `daslot=0` → "the pre-session lock". `check_gate_order.py` before the build. Nothing under
   `src/graphics/shader/**`.

## 3. Runs (each with its own seal; the scorers derived by `make_*.py`, fixtures incl. one per threshold edge; every
sealed prediction printed with HIT/MISS; `CONSTANTS` accepts the sealed values)

1. **Verify `vdg112`** (300 s, pinned): schedule `90+1800: daslot=0 daguard=0 smemocheck=1 | daslot=1 smemocheck=1`
   (ABBA) — the shipped mode and the transitions. GO: `da_chk_bad` 0, mismatch lines 0, checks/hits ≥ 0.99 in both arms,
   `da_q_noguard` > 0 only in arm 0, `da_q_free` > 0 only in arm 1. The gate file of the check: `smemocheck=1` replaces
   the base's `smemocheck=0` IN PLACE (the loader takes the first assignment — session 111's trap); the scorer's GATES
   term tests it.
2. **ABBA `net112`** (600 s, pinned, main estimator frames 10–89, secondary 60–88): arm A `daslot=0 daguard=0`, arm B
   `daslot=1`. Rule (ROADMAP, decision after session 111, item 1): keep `daslot=1` unless B is worse with 2·SE
   excluding 0; then default `daslot=0 daguard=0`, a new build and its video. The quoted size of session 111's gain
   against the pre-session profile is Δ(B − A), with the residual (GuestGpu's guards in `AheadTake`, `ahead_queue_mutex`,
   publish-once) named. Predictions to seal: arm-A walker time per `QueueDrawAhead` call in [0.95, 1.10] µs; Δ mean `dt`
   in [−300, 0]; …
3. The build of §2 changes the shipped binary (yield, race fix): its video with the pin and a check script **with
   fixtures, committed and hashed in SEALS before its run**.

## 4. Other levers and debts

The mid-pass buffer uploads (`sync_up_kb` +161 at `daslot=1`, +213 at `cspfree=1`; render-pass splits) — a census of
which buffers and why synchronous. `da_late` doubling at `daslot=1` (5.4 → 10.7 a flip) and the `Taking` skip not
advancing `walk`/`uses`. The BDA regime (OLD ~1 466 vs NEW ~55 scans a flip) is a startup state that makes every
between-run comparison unreadable — a census of what decides it would make cross-build comparisons possible.
`cspfree` code debts. `dapin=1|3` under the pin. M3.2.

## 5. Traps that are live

1. During a sealed run the heartbeat makes NO tool call; every chain holds `C:/kyty/SEALED_RUN.lock`; kill stray
   `tail`/`grep` watchers before a sealed run.
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included.
3. IDENTITY hashes the INSTALLED exe; copy each scored build before the next build.
4. A gate-file token appended after the base's assignment of the same name is IGNORED (first assignment wins) —
   replace in place (session 111 `vds111`).
5. A knob whose "off" arm still runs new code is not "today": say what arm A is, measure against it (session 111 MAJOR).
6. The main estimator is frames 10–89 (or the full block); do not add gains.
7. Python `Path.write_text` on Windows writes CRLF; bash heredocs with nested quotes break under the hook.

## 6. Deliverable

PLAN; records before actions; CODE → TEST → VERIFY → **adversarial audit before publishing**; one ROADMAP edit, FACTS
(`C:/kyty/s112/FACTS.md` → `docs/local-session-112.md`), `docs/next-session-113.md`, both game contexts, a short
`HANDOFF.md` block, the commit without push.

## 7. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; a gain against a
different build from within-run numbers; safety in scenes not measured; additivity of gains.
