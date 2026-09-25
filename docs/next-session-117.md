# Session 117 — the `--no-memo` timing of `mutlib` v4.1, then a sealed fine split of `AheadTake` and `mh_bind`, then the next speed track by the ceiling rule

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 116 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–7 (item 6: the phase split; item 7: the audit
— T1 withdrawn, the timing gap); `C:/kyty/s116/FACTS.md` (git `docs/local-session-116.md`); `C:/kyty/s116/runs116/
obs116.score.txt` (the report).

**Open the report with these numbers:** Sky Garden, pinned, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0
cspfree=1 daslot=1 daguard=1 bdanarrow=0 titleasync=1`, installed build `d3a981a2…` (`7c73f26`). Session 116: `obs116`
ADMITTED — `dt` 31 650 µs (game speed 52.7 %), render mutex 92.3 % of the GuestGpu CPU: `mh_bind` 10.7 ms, `mh_emit`
7.5 ms, `mh_prog` 6.7 ms (of which `AheadTake` 3.0 ms), `mh_disp` 2.3 ms; program-memo misses worth only 0.45–0.65 ms.
60 FPS stays the direction without a route with a live estimate.

## Rule of the session

As since session 102: every decision in `ROADMAP.md` before the first action (also every change to a running workflow,
and every stage a workflow drops — the audit-116 MAJOR); a sealed consequence is never set aside after its outcome; seals
with fixtures and mutants — `mutlib` v4.1 frozen `docs/session-116/mutlib_v41/`, FULL runs only (`--control --no-memo
--work-dir C:/kyty/s117/work*`), `--changed-from` barred; a sealed chain refuses while any `mutlib.py` process lives;
never two heavy jobs at once; audit before closing. Speed claims only from a pinned ABBA with an idle machine.

## Steps

0. **Harness root `C:/kyty/s117`**: port `enter_scene.py`, `gates_base.txt`, `run_safety99.py`, `procload.py`,
   the pinned exe `kyty_emulator_d3a981a2.exe`. **Time one full v4.1 run** `--control --no-memo --workers 2` on the sealed
   `ttl114b` (`C:/kyty/s114`), machine idle (procload), nothing else running; record the wall time in ROADMAP — the only
   quotable figure for "one ABBA seal" (item 7 (2)). If it exceeds 40 min, record the plan for seals (workers, suite size)
   before the first ABBA seal.
1. **Seal 01 `fin117` — the fine split (observation, no speed verdict):** derive from `obs116` (whole-line generator
   anchors) a scorer that adds the existing counters of the two candidates: **`AheadTake`** — `da_take_us`, `da_hit`/
   `da_stale`/`da_late`/`da_miss`, the witness loops (`da_runs`, `da_runs_clean`, `da_singles`, `da_cl_*`), `srt_miss`;
   **`mh_bind`** — `bindlap=1` (`bl_prep/res/img/buf/smp/wit/rsv/tr/wr/em/sd_us` with `_n`), with `mutsite=1`, `pathlap`
   off if `bindlap` sits inside its spans (check the code first and record). Admission as in `obs116`; one 300-s entry,
   pinned, no video. Before the seal: an independent read-only check of the draft (identities of the new counters, the
   known trap that `bindlap`'s own marks sit inside `mh_bind`, the instruments' cost — report it as a limit).
2. **Track by the ceiling rule:** a candidate is a track only if its measured ceiling is **≥ 1 ms per frame** (the part
   that a change could remove, not the whole phase); record the ceiling arithmetic in ROADMAP before any code. Candidates
   known from history: the M1 witness check (session 72: clean loop 1.03 ms, live loop 0.90 ms before `dawitcg`),
   the bind floor (M3 closed with GAP in session 101 — do not reopen without a new mechanism), `mh_emit` com/rt.
3. If a track passes: the code behind a knob (default = today), its verify mode, a sealed pinned ABBA (the v4.1 full
   mutation run first), video on SHIP. If none passes: record that the GuestGpu thread has no ≥ 1-ms part left on this
   scene and plan the next measurement (BDA OLD, another scene, or the GPU side).
4. F2 (the flip mutex held ~2.4 ms per flip) stays a correctness debt.

## Must not be claimed

60 FPS; any speed number measured beside another heavy job; that the `obs116` shares hold in BDA OLD; a "≈ 20 min seal"
before step 0 measures it.
