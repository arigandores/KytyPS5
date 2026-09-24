# Session 113 — "maximum FPS", track 1: the BDA regime (OLD ~1 066 scans a frame vs NEW ~52) — what chooses it at start, and can the game run in NEW

**Read first:** `ROADMAP.md` §0.1 — "СЕССИЯ 112 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–6 and **the executor's decision after
session 112**; §7 (the rows "режим BDA OLD/NEW" and "режим BDA: почему запуск остаётся в OLD", session 94); the session-94
record around `ROADMAP.md:280-300` (the `bdaall` price, OLD as the usual state); `C:/kyty/s112/FACTS.md` (git
`docs/local-session-112.md`) incl. §7; `C:/kyty/s112/audit112/AUDIT112.md` (the regime indication, `regime.py`,
`regime2.py`, `crossrun.py`); CLAUDE.md, the session-53 entry (gate `bdastamp`: `PrepareBda` scans only regions whose
`(manager, RegionManager::Epoch)` stamp moved) and the session-94 entry (`regime94.py`).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1`, build `b47b58a9…`. Session 112: `daslot=1` kept — −243.1 ± 62.6 µs against `daslot=0
daguard=0` of the same build (against session 110 unmeasured). The BDA regime is a start state: no run switched it
mid-run; OLD is the usual one (6 of 8 runs in session 94; `shp111`, `vid111`, `vid112` OLD, `net112`, `vdg112` NEW);
across runs OLD went with longer frames in 5 of 5 matched pairs (+27…+442 µs; pooled 600-s arms +207) — an indication
of the same order as every shipped gain of the last ten sessions. In session 94 one `PrepareBda` cost 2 242 µs a frame
in OLD (`a_mut_us`), and `buf_new` was 1.3–2 a frame in OLD against 0.01 in NEW. 60 FPS stays the direction without
a route with a live estimate.

## 1. The port, first

`s113_port.py` fresh in `C:/kyty/s112/` (SRC `C:/kyty/s112`, DST `C:/kyty/s113`), modelled on
`C:/kyty/s111/s112_port.py` (`fd469ad6…`). Sealed texts 67 → 70 (`01_vdg112.md`, `02_net112.md`, audit addendum
`03_audit112.md` → `prev112/pred/`). r6 gains `vdg112.py`, `net112.py` `PRED`; `check112.py` names no seal. Do not carry
`kyty_emulator_*.exe`, `fx_*`, `audit112/pkl`, `audit112/rerun`. Class the generator `make_net112.py`, the audit folder,
`check112.py`/`test_check112.py`/`mut_check112.py`. `gates.cpp` 141 entries, ABSENT 42 (+1 per new knob before the port).

## 2. Offline census — no game (ROADMAP decision after session 112, item 2a; findings recorded BEFORE any design)

Every archived log with `bda_scan` (sessions ~91–112; `C:/kyty/s9x…s112`, `log_*.txt`; stream in binary): per run —
build sha, regime (median `bda_scan` after the stable frame), the flip at which the regime is established (first
window where `bda_scan` settles), the counters that move with it (`buf_new`, `buflru_*`, `bufepoch`, `bda_skip`,
`img_new`, uploads, `prot_*`, `fbp_n`), the scene-entry time, precache mode, and `dt` level. Question 1: what differs
between OLD and NEW runs of the SAME build at the moment the regime settles. Question 2: how large the `dt` association
is within one build (not across builds). Write a script with fixtures (a synthetic OLD and NEW log) before reading
real logs; seal its rule text only if a verdict is drawn from it.

## 3. Code reading (item 2b)

`PrepareBda`, `RegionManager::Epoch` bumps, the `bdastamp` stamps, `buflru`, buffer creation/eviction: which call sites
move the epochs of ~1 000 regions every frame in OLD. Name the candidate mechanism and the counter that would prove it.

## 4. If needed: an instrument (item 2c)

A measurement gate (default 0) counting epoch bumps by call site (and `buf_new` by cause). A sealed observation of
several short entries (e.g. 8 × 150 s, pinned) to catch both regimes, scored by a derived scorer with fixtures (every
term alone, every branch, both sides of every threshold, every prediction band edge — decision after session 112,
item 3).

## 5. If the mechanism is found (item 2d)

A knob that removes the cause, safe by construction; a verify run; then the measurement — an ABBA if the knob can move
the regime mid-run, otherwise an entries-alternation design (sealed, ≥ 8 entries a side). Ship rule as usual (main
estimator frames 10–89; Δ`dt` ≤ −100 µs and 2·SE < 0), video with a check script committed before its run.

## 6. Other levers and debts

The mid-pass buffer uploads (`sync_up_kb`), `da_late`, the walker's remaining per-call excess (1.18 vs ~1.0 µs; wait vs
hold not separated), `cspfree` code debts, `dapin=1|3` under the pin, M3.2.

## 7. Traps that are live

1. During a sealed run the heartbeat makes NO tool call; every chain holds `C:/kyty/SEALED_RUN.lock`; kill stray
   `tail`/`grep` watchers (agents leave them) before a sealed run; no agent works during a sealed run.
2. `KYTY_GPU_CLOCK_PIN=1` on every sealed run, the video included.
3. IDENTITY hashes the INSTALLED exe; copy each scored build before the next build.
4. A gate-file token appended after the base's assignment of the same name is IGNORED — replace in place.
5. Levels from different BDA regimes are never compared; every number from a run carries its regime.
6. An "off" arm that still runs new code is not the old code — say what the arm is.
7. Python `Path.write_text` on Windows writes CRLF; bash heredocs with nested quotes break under the hook.

## 8. Deliverable

PLAN; records before actions; CENSUS → (CODE → TEST → VERIFY) → **adversarial audit before publishing**; one ROADMAP
edit, FACTS (`C:/kyty/s113/FACTS.md` → `docs/local-session-113.md`), `docs/next-session-114.md`, both game contexts, a
short `HANDOFF.md` block, the commit without push.

## 9. Must not be claimed

60 FPS; a game-speed figure on the unpinned default setup; any gain from Δ`cpu_net` alone; a regime effect from
between-build comparisons; safety in scenes not measured; additivity of gains.
