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

## RESUME POINT (session 113 paused 2026-09-24 before its first game run)

**Done without the game** (details: `C:/kyty/s113/FACTS.md` = `docs/local-session-113.md`; ROADMAP §0.1 "СЕССИЯ 113"
items 1–6): port `s113`; the BDA-regime mechanism (a buffer registration invalidated every region stamp; the buffer GC
runs above a device-memory threshold); the census of 579 archived runs (within a build OLD is not slower: +17 ± 84 µs);
knob `bdanarrow` (`37e0de1`) and the race-separating check (`6eb7d14`), build **`7d9fa028…`** (pinned copy
`C:/kyty/s113/kyty_emulator_7d9fa028.exe`, NOT installed; the game folder still runs `b47b58a9…`); an offline adversarial
audit (31 agents, `C:/kyty/s113/audit113pre/AUDIT113PRE.md`); **seal `pred/01b_vbn113b.md` (`120d0ad9`)** replacing the
never-run `pred/01`; scorer `vbn113b.py` (83 fixture checks; mutants on the sealed copy → `mut_vbn113b.out.txt`); chain
`go113b.sh`.

**Next, in this order:**
0. **Fast mutation harness first** (ROADMAP item 7, the user's decision: a 1.5–3 h mutant pass is not acceptable).
   A shared `mutlib.py`: stop a mutant at its FIRST failing fixture; generate the synthetic fixture logs once and only
   read them; load each mutant in-process and keep parsed rows in memory; for a derived scorer run all mutants of
   changed lines and a sample of inherited ones (the full set once, on the sealed copy); make the fixture scale a
   parameter. Target ≤ 10 min per scorer. Acceptance: identical killed/survived per mutant against the archived runs
   of `net112` (`mut_net112.out.txt`) and `vbn113b` (`mut_vbn113b.out.txt`). Then use it for `shn113` in step 3.
1. Check nothing else runs (no agents, no `tail`, GPU idle), then `bash /c/kyty/s113/go113b.sh` (in the background; it
   holds `C:/kyty/SEALED_RUN.lock`, checks and installs the pinned build, runs `vbn113` 300 s pinned with `bdanarrow=2`,
   scores it with `vbn113b.py`; on NOT_EVALUABLE (NEW regime) it repeats once as `vbn113b`). No tool calls while it runs.
2. Read `runs113/vbn113*_score.stdout.txt`; record the verdict in ROADMAP (item 7) before anything else. GO → step 3;
   NO_GO → mode 1 closed as built (the `BdaNarrowMiss:` lines name the region/buffer), write it up; INVESTIGATE → find the
   off-thread registrar; NOT_EVALUABLE twice → record and plan anew.
3. Seal 02 — the ship ABBA `bdanarrow=0|1` (600 s, pinned, main estimator frames 10–89, bar Δ`dt` ≤ −100 µs and
   2·SE < 0, admitted only in the OLD regime, one repeat on NEW) with scorer `shn113.py` (derived from `net112.py` by
   `make_shn113.py` in `C:/kyty/s106_stage/`; **it was built for build `94362eae` — re-pin `BINARY_SHA` to `7d9fa028…` and
   add `bda_nrace` to its schema by an addendum to the generator, re-run its fixtures and mutants**). Prediction P4
   (Δ ≤ −100 µs) carries LOW confidence (the census). Then the video with a check script whose fixtures use the real
   report format, committed and hashed before its run.
   **State of `shn113` at the pause** (draft, not sealed; `C:/kyty/s113/shn113_draft/`, git
   `docs/session-113/tools/shn113_draft/`; sources in `C:/kyty/s106_stage/`): 235 fixture cases ALL OK, 310/310 mutants
   killed, draft run on `net112` OK (NEW regime there, REGIME_OLD_ARM0 fails as it should); P3 band [−1500, +200], P4
   'low confidence'. Built for `94362eae` without `bda_nrace` — re-pin by an addendum to `make_shn113.py`.
   **Open decision before seal 02 (record it in ROADMAP first):** NARROW_ARMED_ARM1 requires the arm-1 level of
   `bda_nskip` ≥ 1, but OLD may coalesce to ~1 invalidation a PrepareBda-frame, so the median could sit just below 1
   and refuse a correctly armed run — read the `bda_ginv_reg` median from `vbn113` (the same count at knob 2) and set
   the term to `> 0` or `≥ 0.5` if needed (one generator line + one fixture).
4. Audit, FACTS, ROADMAP close, `next-session-114.md`, contexts, HANDOFF, commit (no push).

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
