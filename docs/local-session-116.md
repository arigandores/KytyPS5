# Session 116 — `mutlib` v4.1 accepted for FULL runs only (the selective path stays barred; the speed work on `mutlib` stops at ~20 min per seal, `--no-memo` not yet timed); seal 01 `obs116` ADMITTED: the first clean phase split of GuestGpu on `d3a981a2`; the program-memo track (T1) withdrawn by the audit; no speed-up of the game shipped

**Single source of truth for session 116.** Mirrored into git as `docs/local-session-116.md`. Harness root
`C:/kyty/s116`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 116 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–7.

**Opening and closing numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1
daguard=1 bdanarrow=0 titleasync=1`, installed build `d3a981a2…` (git `7c73f26`, session 115) — unchanged. No code change
to the emulator this session. 60 FPS is not promised.

---

## 1. Result

1. **`mutlib` v4.1** (items 1, 5; workflow `wf_3f827fc9-c5a`; sha `db82ef4b…`, frozen `docs/session-116/mutlib_v41/`):
   `--changed-from` requires `--parent-report` and selects mutants on changed scorer lines, mutants whose kill case in the
   parent's sealed report changed (AST of the case and everything it reaches), mutants absent from the report, a full run
   when shared machinery changed, plus a 20 % sample; fixture replay turns itself off on `copy2`/`copytree`/`move`/`ctypes`.
   Acceptance PASS (`ttl114b`: 185 of 345 selected, 185/185 rows equal to the full report of session 114; triples J, A,
   synthetic, `check112`/`check115` equal). Review: **the selective path is unsafe in general** (MAJOR-1: a fixture
   forgotten on a threshold shift stays "vouched for" — the `twocmp` triple: full run → survivor, selection → ALL KILLED;
   six more probes give a false ALL KILLED). **Decision:** v4.1 for FULL runs only (`--control --no-memo`),
   `--changed-from` barred, the speed work on `mutlib` stops.
2. **Seal 01 `obs116`** (items 2–4; seal `0e1013c`, sealed mutants 145/145 `e3041bd`; chain 19:08–19:14): **ADMITTED**
   (23/23 admission checks, idle CPU 4 %, GPU 1 %, 9 498 scene rows from frame 432, 300.6 s, BDA NEW — median `bda_scan`
   56). Pre-seal check (item 3) found a BLOCKER (emit identity tolerance 4 fails by chance — the flip reads counters one by
   one, skew up to ±60) → tolerance 256 on the sum, holds 16; the median-difference check added then dropped before the
   seal (item 4: 1.7–3.9 % chance refusals, redundant).
3. **The phase split** (item 6; with `mutsite`+`pathlap`+`KYTY_GPU_WALL`, per frame): `dt` 31 650 µs (game speed 52.7 %),
   `cpu_gpu` 30 994 µs, GuestGpu busy the whole frame (`gw_idle` 28 µs). Render mutex held 28 592 µs = 92.3 %:
   **`mh_bind` 10 662 (34.4 %; 2.09 µs per draw)**, **`mh_emit` 7 477 (24.1 %; com 2 275, rt 1 600, vtx 1 403, rec 1 280,
   pipe 762)**, **`mh_prog` 6 711 (21.7 %)** of which **`da_take_us` 3 002 (44.7 %)**, `mh_disp` 2 342 (8.7 µs per
   dispatch), `mh_rt` 798, `mh_pro` 338, `mh_tail` 263; outside the mutex: named 700, residue 2 055 (6.6 %). Cost per
   operation 5.74 µs (5 129 draws + 268 dispatches). Cross-checks: hold/`a_hold` 0.997, emit split/`mh_emit` 0.985,
   `pl_proc`/`gw_proc` 1.000. Program memo: `pmemo_hit` 6 812, `pmemo_miss` 2 206 per frame (24.5 % of 9 018 STAGE
   lookups), check 433 µs.
4. **Session audit** (item 7): recount CONFIRMED (own parsers, all numbers). **MAJOR (recount):** the T1 ceiling of item 6
   ("most of 6.7 ms") is refuted — a miss adds only `PrepareProgram` + memo store + key + `programs.find`; a hit still pays
   the check, `m_mutex` and `ProgramCache::Get` including `AheadTake`; regression over rows gives a miss premium of
   0.20–0.29 µs ⇒ all misses ≈ **0.45–0.65 ms** per frame, below the 1-ms bar ⇒ **T1 withdrawn**. **MAJOR (protocol):**
   the full `--no-memo` v4.1 timing (item 1 (г)) was dropped by the workflow without a record; "ABBA seal ≈ 20 min" is a
   cached v4 run on an intermediate build ⇒ must be measured before the next ABBA seal. MINOR: seal 01 and its mutants not
   recorded as their own item (now in item 7); `mutlib` timings under foreign load; sealed texts labelled "DRAFT".
   Foreign game names redacted from the archive (except the sealed amendment text of session 115 — its hash stands).

## 2. Code

No emulator code. Harness `C:/kyty/s116`: `obs116.py` (9f3683c0), `test_obs116.py`, `mut_obs116.py`, `go116a.sh`,
`gates_obs116.txt`, `procload.py` (refuses while any `mutlib.py` process lives), `SEALS116.txt`, `runs116/`. mutlib v4.1
frozen `docs/session-116/mutlib_v41/` (db82ef4b). Commits: `9687fd2` … `ac949b8`. No push.

## 3. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `obs116` | 01 | Sky Garden 300 s, `d3a981a2`, pinned, `mutsite=1 pathlap=1`, `KYTY_GPU_WALL=1`, no video | ADMITTED |

## 4. Proved, and not proved

**Proved:** where the GuestGpu CPU time of a Sky Garden frame goes on `d3a981a2` in BDA NEW (above, three instruments
agree within 1.5 %); program-memo misses cannot buy ≥ 1 ms. **Not proved:** the instruments' own cost (`pathlap`,
`KYTY_GPU_WALL` unmeasured; `mutsite` ≈ 0.10 ms from session 69); the split in BDA OLD; the time of a full `--no-memo`
v4.1 run; any game speed effect.

## 5. Next

`docs/next-session-117.md`: (0) time one full v4.1 `--control --no-memo` run on `ttl114b` on an idle machine; (1) a
sealed fine split of `AheadTake` (3.0 ms) and `mh_bind` (10.7 ms) with the existing `da_*` and `bindlap` (`bl_*`)
counters on the `obs116` scheme; (2) the track by the ceiling rule (≥ 1 ms), recorded before code.
