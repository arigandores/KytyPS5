# Session 118 — route A (parallel command-stream processing), stage 4 part 2: the spine's safe plan and carry pass (0 of 25 904 plans), the slice census gives K3 0.16 and K4 W = 2 47 ‰ PASS / W = 4 325 ‰ FAIL ⇒ W = 2 is the route's ceiling; G₂ at the measured f = 0.555 is 2.3–4.8 ms [I] and is re-measured before stage 3; arm M re-measured the GuestGpu micro-track levels; no speed-up of the game shipped

**Single source of truth for session 118.** Mirrored into git as `docs/local-session-118.md`. Harness root
`C:/kyty/s118`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 118 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–6.

**Opening and closing numbers:** Sky Garden, defaults `dawalk=1 dabatch=8 ctxtick=1 dapin=3 cspfam=0 cspfree=1 daslot=1
daguard=1 bdanarrow=0 titleasync=1 spine=0`, installed build `d3a981a2…` (git `7c73f26`) — unchanged at the close (the
measurement build `321175ab` ran the seal and was then replaced by the verified `d3a981a2`). New gate `slicecen`
(measurement only, default 0). 60 FPS is not promised.

---

## 1. Result

1. **One build, one sealed run, two schedule arms (item 1):** arm P = route A stage 4 part 2 (`spine=2` with the carry
   check and the safe plan, gate `slicecen`); arm M = the re-measure of the GuestGpu micro-track candidates the
   session-117 audit reopened (`takelap bindlap pathlap mutsite`), so the instruments do not measure each other.
2. **Design (item 2, `docs/session-118/designA4_part2.md`, recorded before code):** carry checked without a new thread
   (the shadow processor lives between plans; before seeding the next plan of the same processor its end state is
   compared member-wise with the real one); safe plan (early reads only from GPU-clean pages else UNCERTAIN; the
   structural `EXIT` conditions of the handlers checked first, the plan ABORTED instead); the slice census K3 (element
   runs between host render-pass starts) and K4 (images written in one segment and used in the adjacent one, `dep`,
   at W = 2 and 4, bar 300 ‰). Rules and consequences recorded before code.
3. **Smokes (unsealed, disclosed):** `smoke118` found a carry defect of the instrument — the submission-level
   `reset_processor` reset the real processor but not the shadow (fixed `970e8ce`); `smoke118b` clean, K4 W = 4 317 ‰ at
   the bar; the pre-seal check (agent, `docs/session-118/check/PRESEAL.md`) found the census over-counting against its own
   design (depth target written on every draw, the shared null image counted, slot index without generation) — fixed
   in `7bc87cd` AFTER the smoke had shown W = 4 at the bar (disclosed in the seal; the rule and bar unchanged);
   `smoke118c` on the fixed build (draft mutants ran on the machine during it): W = 4 325 ‰.
4. **Seal 01 `spk118` (`201ca03`):** scorer with 125 fixtures, 125 mutants all killed by the frozen `mutlib` v4.1
   `--control --no-memo` (controls 3/3, 44 s). Run 23:05–23:11, pinned, ABBA P|M from frame 1800, 41 + 40 blocks:
   **ADMITTED ⇒ W2_CEILING.** K5 PASS (0 `spine_bad`/`spine_misal`/`cram_write`, `spine_cmp` 5 308.8 of 5 308.9 elements a
   frame), C PASS (`carry_cmp` 8 of 8 plans a frame, `carry_skip` 0 %), safe plan 0 aborts / 0 uncertain over 25 904 plans;
   K3 median largest-run share 0.162 (W up to 8); **K4 W = 2 median `dep` 47 ‰ (p90 48) PASS; W = 4 325 ‰ (p90 325, 75.1 %
   of frames above 300) FAIL.** The scene is bimodal: W = 4 block medians 325 ‰ in 33 of 41 blocks, 90 ‰ in 8 (blocks
   23–28, 59–64). Spine plan `spine_ns` 959 µs a frame (own timer, a lower bound).
5. **Arm M levels (pinned, BDA regime NEW, a frame):** witness verify `da_t_ver` 1 211 µs (prefetch A 653, take 462);
   `bl_prep` 4 235, `bl_buf` 3 868, `bl_res` 3 213, `bl_img` 1 095; `mh_bind` 10 969, `mh_prog` 6 662, `mh_emit` 7 426
   (com 2 376, rt 1 565, vtx 1 363, rec 1 226, pipe 745). Levels, not removable parts.
6. **W = 2 best case (items 5–6):** item 5 recomputed it as sealed with f = 0.5: from the session-104 members X =
   `cpu_net` − `S_ctx` = 13 286 µs, G₂ = 0.5·X − spine 1 085 − T₂ = 5 558 − T₂ ⇒ [3 026; 5 558] µs for T₂ ∈ [0; T4 = 2 532].
   The audit (MAJOR, both agents) showed the same run measured the larger half of the W = 2 cut at `k4_w2_fmax` 555 ‰
   (the cut follows pass starts): **G₂ = 0.445·X − 1 085 − T₂ = 4 827 − T₂ ⇒ [2 295; 4 827] µs [I]**, break-even
   T₂ = 1.83 ms, where T₂ is expected ⇒ **G₂ is re-measured on the current build in session 119** under the rule fixed in
   item 6 (f₂ = 0.555; spine = max(the walk proxy, 959 µs); G₂ < 3 000 ⇒ route A closed for maximum FPS; ≥ 3 000 ⇒
   stage 3 resumes).
7. **Session audit (item 6):** see §5.

## 2. Code

`14f08b2` (carry check `carry_*`, safe plan `spine_unc` and structural pre-checks, gate `slicecen` with 20 counters
`sc_*`/`k3_*`/`k4_*`, hooks in `BeginRenderingImpl`, `PrepareBindings`, `AcquireRenderTargets`), `970e8ce` (the
submission-level reset also resets the shadow), `7bc87cd` (census: no null images, depth written only when written, key
with slot generation). Build `321175ab` (pinned `C:/kyty/s118/kyty_emulator_321175ab.exe`; built from the working tree a
moment before `7bc87cd`). Nothing under `src/graphics/shader/**`. No push.

## 3. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `smoke118` | none | Sky Garden 180 s, P|M from 900, build `c41290d0`, unpinned | carry defect of the instrument found, fixed |
| `smoke118b` | none | same, build `8bd4c930` | clean; K4 W = 4 317 ‰ |
| `smoke118c` | none | same, build `321175ab` (draft mutants running) | clean; K4 W = 4 325 ‰ |
| `spk118` | 01 | Sky Garden 300 s, pinned, ABBA P|M from 1800, build `321175ab` | ADMITTED ⇒ W2_CEILING |

## 4. Proved, and not proved

**Proved (Sky Garden, one entry):** the spine's plan never needed to abort or read a GPU-dirty word; the shadow
processor's state at the end of one plan equals the real processor's state at the start of the next plan of the same
processor, for every plan; cut at host render-pass starts into two element-balanced halves, the frame's halves share few
written images (47 ‰); into four they do not (325 ‰ in the dominant scene mode). **Not proved:** the carry on another
thread (tested on GuestGpu); the W = 2 tax T₂ and today's `S`/`S_ctx` (G₂ is [I] from session-104 members); any gain of
route A; images written through buffers (invisible to the census); another scene.

## 5. Audit (item 6)

Two agents, own parsers (`C:/kyty/s118/audit118/`, git `docs/session-118/audit/`). **Recount: every number of item 5 and
of the score CONFIRMED** (12 sealed hashes match; 9 148 rows of each kind, no duplicates or mislabels; 41 + 40 blocks).
**Protocol and code CONFIRMED:** item 4 before the fix, the fix before the build, seal and its mutants before the run,
the pre-registration unchanged, no heavy work during the run, the disclosures true; W2_CEILING applied as sealed; the
census indices aligned, `AttachmentWriteAspects()` covers depth and stencil, the record packing cannot overflow, gate and
knob inert at 0, nothing under `src/graphics/shader/**`. **MAJOR:** item 5 used f = 0.5 while the run measured 0.555 —
the G₂ rule for session 119 fixed in item 6 before its seal. **MINOR:** T₂ = T4 is not conservative in Sky Garden (one
reader taxed as much as four in session 64); the session-104 members came from build `16ef56b6` with `dawalk=0`;
`bl_img` 1.09 ms added to the candidates; the pre-seal "~4.5 % two-frame rows" does not hold here — `sc_frames` is always
1 in arm P, `k4_wW_n` tears instead (0.3 % at W = 2, 7.1 % at W = 4, dropped equally in both scene modes); "8 of 8 plans"
includes about one trivially equal compare a frame after a reset on both sides; item 1's "one build" became three, each
recorded first; the choice to re-measure was made after the outcome (recorded before acting); the census cannot see
buffer writes, clears or copies (a downward bias of `dep`, immaterial at 47 against 300 ‰); after reinstalling
`d3a981a2` a re-score of `spk118` fails `installed_now` — pass `installed_sha`.

## 6. Next

`docs/next-session-119.md`: two sealed ABBA runs with zero emulator code re-measure G₂ at W = 2 (`mutwide=0|15`,
`shadowresolve=0|1`; rule of items 5–6, f₂ = 0.555); removability designs with ceilings for the arm-M candidates ≥ 1 ms
by code reading.
