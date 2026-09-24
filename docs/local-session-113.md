# Session 113 — the BDA regime explained; knob `bdanarrow` built, verified in a forced OLD regime (0 misses) and KEPT at 0 (−83.2 ± 68.0 µs, below the −100 bar); the fast mutation harness `mutlib` v2; one 3-s stall diagnosed as a wait on an unsubmitted tick; no speed-up shipped

**Single source of truth for session 113.** Mirrored into git as `docs/local-session-113.md`. Harness root
`C:/kyty/s113`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 113 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–22 (item 9 was retracted by
item 10; item 22 carries the audit's errata to items 13–21).

**Opening numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1 daguard=1`;
installed build at the start `b47b58a9…` (session 112). **Closing:** the same defaults plus `bdanarrow=0`; installed
build **`1678d3f4…`** (video `vid113` PASS). 60 FPS is not promised.

---

## 1. Result

1. **The BDA regime** (offline, `C:/kyty/s106_stage/bda113/MECHANISM.md`, census of 579 archived runs): OLD = a full
   re-walk of all ~1 016 four-MiB regions after each buffer registration, because `PrepareBda` invalidated every region
   stamp when the registration epoch moved; the buffer GC evicts idle buffers (and they are re-created) only while
   device-local usage is above a trigger fixed in the constructor (budget − 1 GiB − 0.6·8 GiB = 9 296 MiB here). Which
   side a run lands on depends on its usage after the level load (hypothesis H2: the number of 256-MiB VMA blocks; H3 —
   another budget — refuted: the budget was identical in all entries of the day). Today: OLD 1 entry of 7 (`vbn113c`),
   plus `vid113` (natural OLD at the end of the session).
2. **Knob `bdanarrow`** (`KYTY_BDA_NARROW_STAMPS`, 0..2, default 0): 0 today; 1 marks stale only the stamps of the
   registered buffer's regions; 2 = 0 plus the check of what 1 would skip. The check was made exact (`56a4b4f`: the stamp
   read under the same region lock as the dirty bits).
3. **Verify (seals 01b–01f).** 01b (`vbn113`, `vbn113b`) and 01d (`vbn113g..j`): NEW regime ⇒ NOT_EVALUABLE; 01c
   (`vbn113c`, OLD): 13.79 M checks, 0 misses, 3 races ⇒ INVESTIGATE ⇒ the exact check. The GC-trigger measurement env
   **`KYTY_BUFFER_GC_TRIGGER_SHIFT_MB`** (`967d1aa`, default 0; 1024 = trigger −1 GiB) forces OLD. 01e (`vbn113k`): forced
   OLD worked, BAD 0 over 13.9 M, **NOT_ADMITTED** by one `GpuWaitSlow`. 01f (`vbn113m`, build `1678d3f4`): **GO** — forced
   OLD, 11 845 121 would-skip regions, `bda_nmiss` 0, `bda_nxthr` 0, `bda_nrace` 0 (in this one 300-s entry).
4. **ABBA (seal 02, `shn113`, 600 s, pinned, forced OLD in both arms): KEEP `bdanarrow=0`.** Admitted (98 pairs);
   **Δ`dt` = −83.2 ± 68.0 µs** (2·SE, t −2.45; main estimator rows 10..89); Δ`cpu_net` −83.9 ± 60.6; Δ`gpu_busy` +5.9 ±
   23.8. S2 met, S1 (≤ −100) not ⇒ KEEP. The 2·SE band of the saving (15–151 µs) straddles the bar; only the point estimate
   is below it. Point estimate ≈ 0.27 % of game speed in a forced OLD regime at a pinned clock (band 0.05–0.50 %).
5. **The 3-s stall (`vbn113k`, frame 9 672, `dt` 3.03 s):** `GpuWaitSlow role=4 requested=329576 known=329575
   current=329576` — a thread outside the frame-trace roles (by code, the priority-operation thread — an inference by
   elimination) waited 2.975 s on the recording tick, which was not submitted for ≈ 3 s; the submit history ended at the
   previous tick, the submit backlog was 0, GPU utilisation 0 % for ~2.5 s. New in form: the 21 earlier `GpuWaitSlow`
   events (sessions 80–98, 22 files) had `requested < current` and all ended in `GpuHangAbort`; none in sessions 104–112.
   Instrument `623009f` (no behaviour change): queue site of priority operations, `prio_unsub`, `prio_stall`
   (`PriorityStall:` lines), `gw_idle_prio` (`GpuIdlePrio:` lines). In `vbn113m` and `vid113`: `prio_stall` 0,
   `gw_idle_prio` 0, `prio_unsub` ≈ 5.7 a frame. Cause not found (session 114, step 1).
6. **`mutlib` v2** (`C:/kyty/s106_stage/mutlib/mutlib.py` sha `877eb53a…`): fast mutation harness, accepted on six suites
   with the old verdicts (net112 277/277 in 21 min with the parse memo, 33 min without; shn113 310/310 in 34 min); fresh
   review: 2 MAJOR + 6 MINOR holes with no trigger in today's suites ⇒ derived scorers run `--control --no-memo` (item 15);
   v3 is a debt. Mutants this session: vbn113d 43/43, vbn113e 51/51, vbn113f 54/54, shn113 315/315 (+2/2 draft-only),
   check113 31/31.
7. **Video `vid113`** (build `1678d3f4`, defaults, pinned, 120 s): PASS — 3 976 frames, 0 one-frame glitches;
   `BufferGc … shift_mb=0`, `bda_nskip`/`bda_nwould` 0, `prio_stall` 0.

## 2. Harness (`C:/kyty/s113`)

Seals `pred/01b…02` and `SEALS113.txt`; scorers `vbn113b/c/d/e/f.py`, `shn113.py`, `check113.py` with `test_*`, `mut_*`,
`make_*` (the generators after item 16 assert whole-line anchors); chains `go113b…h.sh`; build copies
`kyty_emulator_7d9fa028/5ba0e188/cf22e223/1678d3f4.exe`; `runs113/` (scores); `audit113pre/` (pre-run audit),
`audit113/` (mid-session audit), `audit113/final/` (session audit: `RECOUNT.md`, `PROTOCOL.md`, `CODE.md`, `CLAIMS.md`);
`mutlib` in `C:/kyty/s106_stage/mutlib` (archived in git `docs/session-113/mutlib`).

## 3. Source, builds, provenance

Code commits: `37e0de1`, `6eb7d14` (knob `bdanarrow`, check), `56a4b4f` (exact check), `967d1aa` (GC-trigger env),
`623009f` (stall instrument). Builds: `7d9fa028` (6eb7d14), `5ba0e188` (56a4b4f), `cf22e223` (967d1aa), **`1678d3f4`**
(623009f, installed). Records and seals: `docs/ROADMAP.md` items 1–22, `docs/session-113/`. No push.

## 4. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `vbn113`, `vbn113b` | 01b | verify `bdanarrow=2`, build `7d9fa028` | NOT_EVALUABLE (NEW) |
| `vbn113c` | 01c | verify, relaunched until OLD | OLD; 13.79 M checks, 0 miss, 3 race ⇒ INVESTIGATE |
| `vbn113g`–`j` | 01d | exact check, build `5ba0e188` | NOT_EVALUABLE ×4 (NEW); 2.35 M checks, 0/0/0 |
| `vbn113k` | 01e | forced OLD, build `cf22e223` | NOT_ADMITTED (`GpuWaitSlow`, 3-s stall); BAD 0 over 13.9 M |
| `vbn113m` | 01f | forced OLD + stall instrument, build `1678d3f4` | **GO**; 11.85 M, 0/0/0 |
| `shn113` | 02 | ABBA `bdanarrow=0\|1`, 600 s, forced OLD | **KEEP** (−83.2 ± 68.0 µs) |
| `vid113` | check113 | video of the installed build, defaults | **PASS** (3 976 frames, 0 glitches) |

## 5. Proved, and not proved

**Proved:** what makes a run OLD (GC above the trigger + global stamp invalidation); that mode 1 skipped no needed
synchronization in one forced-OLD 300-s entry of this scene (0 misses on 11.8 M); that the extra walk costs 83.2 ± 68.0
µs a frame at a pinned clock in a forced OLD regime (below the ship bar by the point estimate).
**Not proved:** that mode 1 is safe elsewhere (its correctness conditions: registrations serialized with the walk; the
check ran on arm-2 history); the share of the natural OLD regime; the cause of the 3-s stall; anything about 60 FPS.

## 6. Audits

Pre-run (`audit113pre/AUDIT113PRE.md`, 31 agents): MAJOR (races inflate `bda_nmiss`) fixed by the exact check. Session
audit (`audit113/final/`): no MAJOR — recount CONFIRMED, protocol HOLDS, code NOT REFUTED, 11 MINOR claim errata recorded
in ROADMAP item 22.

## 7. Next

`docs/next-session-114.md`: (1) the stall — catch the site, then a fix as a knob; (2) `mutlib` v3; (3) the next speed
track chosen by the rule (candidate: the queue-to-run latency of priority operations).
