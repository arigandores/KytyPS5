# Session 121 — the R1 prototype: an 8-way texture memo of 4 096 entries with its own verify gate, one sealed ABBA

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 120 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 2 (threshold 0.5 ms net; shipping by 2(в)), 7
(the verdict: R1 OPEN, table w8) and 8 (the audit: the shape is w8, the ceiling is loose, the prototype's traps, A-walker
parked, the session order); `C:/kyty/s120/FACTS.md` (git `docs/local-session-120.md`); `docs/session-120/design/r1.md`
and `r1_review.md` (the memo's sites, its proof, the census); `docs/session-120/audit/closure.md` (the prototype's
recommendations).

**Open the report with these numbers:** Sky Garden, pinned, defaults as in session 120, installed build `d3a981a2…`
(`7c73f26`), game speed ≈ 52 % (`dt` ≈ 31.7 ms). Seal 01 `cen120` of session 120: an 8-way memo of the same 4 096
entries would have hit ≈ 1 259 of ≈ 1 772 key misses a frame; net ceiling 658.8 ± 9.1 µs a frame; the audit's honest
ceiling ≈ 0.33–0.62 ms and realizable gain ≈ 0.25–0.50 ms (central 0.35–0.40). 60 FPS is not promised.

## Rule of the session

As since session 102: every decision in `ROADMAP.md` before the first action — also before a one-line code change
(audit 120 MINOR-1); paragraphs written by agents in ROADMAP/pred are tagged with their author and accepted by an explicit
line; amendments are new items; a sealed consequence is never set aside; seals with fixtures and mutants (`mutlib` v4.1
frozen, FULL runs); edit scripts write LF; suites end with `ALL OK`; backslashes only through files written by Write;
estimator window frames 10–88; privacy grep before commits includes the user name, e-mail and `<launcher user name>`; after `mutlib` a
pause before a sealed run.

## Steps

0. **Harness `C:/kyty/s121`** (port s120: `enter_scene.py` with `Path.home()` and a NEUTRAL launcher user name,
   `procload.py`, `go` chain with the name/pred guards, `gates_base.txt`).
1. **Design in ROADMAP before code** (workflow: designer + adversarial reviewer; `docs/session-121/design121.md`):
   - a gate (e.g. `texmemo8`, default 0, read once per `ResolveTextureWith` call) that switches the texture memo to 512
     sets × 8 ways of the same `Texture` entries; the set/way probe on compact 32-bit tags + LRU use in one 64-B line per
     set (the layout whose probe the census priced), the full proof (`resource_key`, 32-byte T#, liveness) unchanged;
     `memo_index = set*8 + way < TextureSlots`; every store, including a victim eviction, bumps `version` and resets
     `fast_view` (texfast eligibility and `shadowresolve` stay correct); invalidate the whole memo (valid = false,
     version++) when the gate flips; mutually exclusive with `texmemo2` (pinned 0, asserted); `r1cen`/`r2cen` off under
     it;
   - a VERIFY mode: every gained hit (a hit the direct index would have missed) is compared with a fresh full resolution
     (store, id, the full desc digest — never against the direct memo); `*_bad` counters and ≤ 40 mismatch lines; the
     verify arm is never timed;
   - arming proven by counters (`tex_hits` up and `texmemo_collide` down by about the census's 1 259 a frame,
     `texfast_rec` down, `texmemo_stale` per arm), the probe price reported;
   - pre-registered prediction ≈ 0.35 ms (range 0.25–0.50) with the power statement (0.25 ms: 79–95 %; 0.15 ms:
     38–54 %), and the shipping rule of item 2(в).
2. **Code, one build, an unsealed smoke with the verify mode (disclosed): 0 mismatches, arming counters as predicted;
   video of the gate-on arm (`KYTY_REC`) checked for one-frame glitches.**
3. **Scorer + fixtures + mutants, a pre-seal check agent, the seal, `mutlib` v4.1 FULL, ONE sealed pinned 300-s ABBA
   `texmemo8=0|1`** with `r1cen=0 r2cen=0 spcen=0`, window 10–88; the consequence fixed before the run: SHIP (the default
   moves to 1) only if the 2SE interval of Δ`dt_us` lies below 0, verify 0 mismatches and the video is clean; else the
   track closes with its measured number.
4. **Audit, close.** Session 122: the bottleneck map across scenes (ROADMAP s120 item 3, moved by item 8).

## Must not be claimed

60 FPS; the census's 658.8 µs as a speed-up; any gain from R2 or A (parked borders); that B's GPU-side barrier cost is
closed (only its GuestGpu CPU cost on Sky Garden is); a speed number beside another heavy job.
