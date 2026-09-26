# Session 120 — one measurement build, one sealed run: the R1 texture-memo track OPENS (C_R1 = 658.8 ± 9.1 µs a frame, an 8-way memo of 4 096 entries; honest ceiling ≈ 0.33–0.62 ms, realizable ≈ 0.25–0.50 ms); R2 and the same-pass render-target memo A are systematic borders (parked, not exhausted); the transit skip B is CLOSED; the track threshold is now 0.5 ms net; no speed-up shipped

**Single source of truth for session 120.** Mirrored into git as `docs/local-session-120.md`. Harness root
`C:/kyty/s120`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 120 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–8.

**Opening and closing numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1
daguard=1 bdanarrow=0 titleasync=1 spine=0 slicecen=0` (new, all 0: `r1cen`, `r2cen`, `spcen`), installed build
`d3a981a2…` (git `7c73f26`) at the close — unchanged. Game speed ≈ 52 % (`dt` ≈ 31.7 ms uninstrumented). 60 FPS is not
promised.

---

## 1. Result

1. **Threshold (item 2, after the user's question):** a speed track opens at a MEASURED net ceiling ≥ 0.5 ms a frame
   (was 1 ms) with every `*_bad` = 0; candidates on one path may form a package; shipping unchanged (sealed ABBA gain
   with its 2SE interval below 0, verify 0 mismatches, video clean). Item 3: a bottleneck map across scenes is planned
   (session 122 by item 8). The user's rule, recorded in `CLAUDE.md`/`AGENTS.md`: a user's question is not a decision.
2. **Design (item 4):** three designs + three adversarial reviews (all SOUND_WITH_CHANGES) → `design120.md`. Knob `r1cen`
   (tag-only shadow of 4-/8-way and direct-16 K memos with the real hit's proof, a `w1` null control), knob `r2cen`
   (stage image-block repeat, census in BOTH arms, T* from M), gate `spcen` (same-pass render-target memo A and transit
   skip B evaluated without acting, per-image state serial).
3. **Code (item 5):** three implementation agents in sequence, three code reviewers (R1 PASS, R2 PASS, spcen
   PASS_WITH_FIXES — two spec fixes: timer-read add-back in `N⁺`, row-skew tolerance on window sums), one lead patch
   (`patch_spcen_c`: the stamp race is decided by the first slow-path entry; built before its ROADMAP line — audit
   MINOR-1). Commit `0310cbb`, build **`15cdbfc6…`** (the rebuild at the commit), 160 new `FrameTrace-x` counters.
4. **Unsealed smoke `smk120`** (180 s, disclosed): every identity closed, 0 correctness counts, `w1` = 0, M-arm zeros;
   drafts R1 615.9, R2 444.1, A 315.5, B −9.8.
5. **Scorers (item 6):** `rpk120.py` (R1, R2, package R) and `spc120.py` (A, B, package SP), writer → adversarial check →
   fixer each; member verdicts carry their own consequences; row-skew tolerance ±8 per block window (the lead's decision;
   not needed in the run — residuals 1–2). Seal 01 (`13181a8`): pred `d20cd3de…`, `mutlib` v4.1 FULL on the sealed
   copies 489/489 and 281/281, controls 3/3.
6. **Sealed run `cen120`** (11:48–11:54, pinned, BDA NEW, 38 pairs, both scorers ADMITTED, every correctness counter 0):

| member / package | verdict | point | upper | 2SE |
|---|---|---:|---:|---:|
| R1 (w8; d16 621.7, w4 540.7) | **OPEN** | **658.8** | 658.8 | 9.1 |
| R2 | NOT_OPENED | 435.2 | 1 067.6 | 12.7 |
| package R | OPEN (subsumed by R1) | 1 093.9 | 1 726.4 | 15.0 |
| spcen A | NOT_OPENED | 340.2 | 686.9 | 7.3 |
| spcen B | **CLOSED** | −8.1 | 177.9 | 3.9 |
| package SP | NOT_OPENED | 332.1 | 864.9 | 10.6 |

   R1 terms (w8): W 1 258.7 would-hits a frame, t_T 516.6 ns, t_hit 19.2 ns; A 626.1 − L 33.1 + R 81.1 + E 28.4 − P 43.7.
   The instruments' own price P−M: `dt_us` +2 766 ± 138 µs (report only).
7. **Audit (item 8):** recount CONFIRMED to 1e-13 µs (bootstrap: R1 below 500 in 0 of 2 000); protocol HOLDS (10 MINOR);
   closure holds narrowly — R1's ceiling is loose (honest ≈ 0.33–0.62 ms, realizable ≈ 0.25–0.50), the shape stays w8,
   package R adds nothing to R1, R2 and A are systematic borders (parked by the rule, not exhausted), B is exhausted
   narrowly (GuestGpu CPU, Sky Garden, standalone). A-walker (s119 debt): parked, not refuted.

## 2. Code

`0310cbb` (emulator, MEASUREMENT ONLY, defaults 0): `descriptors.cpp` (R1 census around `ResolveTextureWith` and
`RebindImages`; R2 census in `PrepareBindings`; spcen B in `CommitBindings`), `renderDraw.cpp` (spcen A around
`AcquireRenderTargets` and both `BeginRendering` sites), `render.h`, `image.cpp`/`vma.cpp`/`graphicContext.h`
(per-image state serial, always counted), `context.cpp` (pass-begin serial), `frameStats.h`, `videoOut.cpp`,
`gates.h`/`gates.cpp` (`Knob::R1Census`, `Knob::R2Census`, `Gate::SamePassCensus`). Nothing under
`src/graphics/shader/**`.

## 3. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `smk120` | none | Sky Garden 180 s, the sealed schedule | clean; drafts as above |
| `cen120` | 01 | 300 s, pinned, ABBA P `r1cen=2 r2cen=2 spcen=1` / M `r1cen=0 r2cen=1 spcen=0` (+ `bindlap pathlap mutsite` both) | ADMITTED; R1 OPEN |

## 4. Proved, and not proved

**Proved (Sky Garden, one run):** a texture memo of the same 4 096 entries, 8-way LRU instead of direct-mapped, would
have turned ≈ 1 259 key misses a frame into hits with the real hit's proof (0 disagreements with the fresh resolution);
the measured net ceiling of that is 658.8 ± 9.1 µs a frame. The transit skip B cannot pay 0.5 ms. **Not proved:** any
speed-up (a would-hit is a ceiling); the realizable gain (≈ 0.25–0.50 ms [I]); R2 and A either way (systematic borders);
another scene.

## 5. Deviations and traps (disclosed)

Agents edited the lead's `design120.md`, `pred` and ROADMAP item 4 (accepted in items 5–6); item 4 was amended in place
(`3086142`); `patch_spcen_c` built 30 s before item 5 recorded it and unreviewed; `go120a.sh` `$HOME` edit after the
smoke; `enter_scene.py` `Path.home()` edit after `seal120.py` (re-hashed before the run); a usage-limit gap 05:50–08:51
(scorer writers restarted on partial files); a leftover `tail -f` (pid 28716) killed. **Traps:** heredoc through the
command hook ate backslashes again (a one-off copy script) — files with backslashes only through Write;
`smoke120.py` grouped rows by the `blk` label (rows before the schedule also carry `blk=0`) — build blocks from
`GateArm:` lines; a scorer on the smoke must use `--draft`.

## 6. Next

`docs/next-session-121.md`: the R1 prototype — an 8-way texture memo with its own verify gate, one sealed ABBA; the
bottleneck map across scenes follows in session 122.
