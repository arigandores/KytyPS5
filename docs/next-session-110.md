# Session 110 — "maximum FPS", track 1: a guard by stall DURATION for `cspfree`, then ship it if it passes; `daslot` (tag 1) code in parallel

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 109 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–8 and **the executor's decision after
session 109**; §6; §7 (session-109 rows); `C:/kyty/s109/FACTS.md` in full (git `docs/local-session-109.md`) incl.
§7; `C:/kyty/s109/design109.md`; the sealed texts `C:/kyty/s109/pred/*` (hashes `SEALS109.txt`). Sealed texts are
immutable.

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=0`: mean frame ≈ 31.0 ms (≈ 0.54× game speed). `cspfree=1` measured Δ mean `dt` −154.1 µs (`frm109`, 2·SE
121.2) and verifies clean (`vfy109`: 0 bad in 2.06 M), but with the compute precache off it showed 17 vs 7
dispatch-time stall EVENTS (waits 12 vs 3; `ent109b`). `gpu_busy_us` +70–90 µs whenever the prefetch lock hold goes
(~2 extra mid-pass buffer uploads a flip, session-109 audit). 60 FPS stays the direction without a route with a live estimate.

## 1. The port, first

`s110_port.py` fresh in `C:/kyty/s109/` (SRC `C:/kyty/s109`, DST `C:/kyty/s110`), modelled on
`C:/kyty/s108/s109_port.py` (`14be3f9c…`). Sealed texts 52 → 57 (`01_ent109.md`, `01b_vfy109.md`, `02_ent109b.md`,
`03_frf109.md`, `04_frm109.md` + the audit addendum `05_audit109.md` → 58; check). r6 gains the session-109 scorers'
`PRED` (`ent109.py`, `vfy109.py`, `ent109b.py`, `frf109.py`, `frm109.py`). `gates_base.txt` unchanged; `gates.cpp` 139
entries (111 + 28; `cspfree` last), ABSENT 40 — +1 each for any new knob before the port. Do NOT carry
`kyty_emulator_*.exe` nor `C:/kyty/s106_stage/fx_*` (1.6 GB+). Class the one-shots (`seal109a.py`, `seal109b.py`,
`make_frm109.py`), the anchored generators (`make_ent109b.py` on `s106_stage/ent109.py`, `make_frf109.py` on the s109
`fam108.py` sha), and `audit109/`.

## 2. Stall duration (code, ROADMAP record first)

Counters (traced runs, no gate): `cs_sync_new_us` (wall on the dispatching thread inside `GetComputePipeline`'s
synchronous compile) and `cs_sync_wait_us` (wall waiting for a pending entry), plus `cs_stall_max_us` (a gauge: the
longest single stall of the frame) — so a guard can bound what a player sees, not how often. Nothing under
`src/graphics/shader/**`.

## 3. The powered guard by duration (sealed, before any ship run)

Entries ABBA as `ent109b` (8 × 150 s, `KYTY_PIPELINE_PRECACHE=gfx`, pinned; A `cspfree=0`, B `cspfree=1`). Proposed
rule to record in ROADMAP BEFORE the seal (the executor may tighten it, never loosen it after seeing data): **Σ stall
µs over B ≤ 1.25 × Σ over A + 20 000 µs, and the largest single stall in B ≤ the largest in A + 10 000 µs**, with the
positive control Σ stall over A > 0. Publish per entry: counts, Σ µs, max µs.

## 4. Ship run (only after a PASS)

A fresh sealed frame-time ABBA `cspfree=0|1` (600 s, pinned, shipping configuration), scorer from `frf109.py` via a
`make_*.py` (tag, seal), the Δ`dt` bar, video with the pin on SHIP_PENDING_VIDEO. On SHIP: ROADMAP first, default
`cspfree=1`, new build (copy the scored one first), its pinned video checked by a script pinned to its sha.
`frm109` does NOT count as the ship run (its seal said nothing ships).

## 5. Tag 1 — `daslot` (code, no run time before §3–4 are scored)

Per `design109.md` §A: publish-once hints, atomic hint/variant fields and `memo_generation`, `ahead_slots` behind an
atomic pointer under a new `ahead_queue_mutex`, a per-slot guard byte and `AheadTaking` (move `slot.taken = 1` before
the state store), `QueueDrawAhead` off `m_mutex`; knob `daslot` (0..2, 2 = verify), counters `da_guard_n`,
`da_guard_busy`, `da_q_taking_wait`, `da_hint_defer`, `da_slot_bad`. ROADMAP record before code. Build it into a
separate build dir or only after §3–4 are scored.

## 6. Debts

`gpu_busy_us` +70–90 µs when the prefetch hold goes — identified by the session-109 audit [I]: ~2 more buffer uploads
a flip land inside render passes and split them (`sync_up_kb` +250 KiB); a lever of its own (census of the causes
first). The 10 surviving mutants of the session-109 audit get their fixtures in the next derived scorers. `dapin=1|3` re-measure under the pin. M3.2.

## 7. Traps that are live

1. During a sealed run the heartbeat makes NO tool call; every run chain holds `C:/kyty/SEALED_RUN.lock`; kill
   stray `tail -F`/`grep` watchers (agents leave them) before a sealed run.
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included.
3. IDENTITY hashes the INSTALLED exe: no rebuild between a run and its scoring; copy each scored build.
4. A guard needs exposure (`KYTY_PIPELINE_PRECACHE=gfx`) and should bound DURATION, not events.
5. Frame time is vblank-quantised; gains are not additive.
6. Python `Path.write_text` on Windows writes CRLF — use `write_bytes`/`newline=''` for repo and harness files.
7. Bash heredocs with nested quotes break under the hook: put scripts in files.

## 8. Deliverable

PLAN; records before actions; CODE → TEST → VERIFY → **adversarial audit before publishing**; one ROADMAP edit, FACTS
(`C:/kyty/s110/FACTS.md` → `docs/local-session-110.md`), `docs/next-session-111.md`, both game contexts, a short
`HANDOFF.md` block, the commit without push.

## 9. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; `cspfree` safe in scenes
not measured; additivity of gains.
