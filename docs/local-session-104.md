# Session 104 — the vblank plateau does not hold the mean; `dawalk=1` SHIPPED (−0.46 ms CPU, −0.27 ms mean frame a flip); route A passes its kill-or-go (G = 5.7 ms) and proceeds by stages; the shader seed is rebuilt

**Single source of truth for session 104.** Mirrored into git as `docs/local-session-104.md`.
Harness root `C:/kyty/s104`. Everything below is measured unless marked otherwise.

> **Written after a three-lens adversarial audit** (§8; sealed `pred/04_audit_addendum.md`, `d44b5975…`):
> recount NOT REFUTED; protocol REFUTED narrowly (MAJOR: an agent read files during the `reg104` screen);
> the plateau claim PARTLY REFUTED — the Sky Garden conclusion stands, the stated mechanism, the desert
> evidence and "savings convert ~1:1" are corrected below.
> A fourth lens on the final texts (claims, sealed `pred/05_claims104_addendum.md`) REFUTED ten presentation
> points narrowly (withdrawn claims not struck through in ROADMAP, [I] tags, the pin qualifier, session-60
> numbers, disclosures); all corrected before publication.

**The numbers the session opens with** (session 103's series, scene window of 67 entries): `dt_us`
median 33.5 ms, `cpu_gpu_us` 32.9 ms, `gpu_busy_us` 12.6 ms; frames on 2/3/1 vblanks = 79.3/20.1/0.5 %
(the audit: those short entries include unsettled early frames — steady windows of runs without recording or
instruments have ≤ 1.3 % three-vblank and 9–14 % one-vblank frames; with recording `vid103` has 7.2 %, and the
instrumented `sh104` middle third 5.1 %).
**60 FPS stays the direction but has no route with a live estimate; the work is on "maximum FPS"**
(game speed = flips per second / 60).

---

## 1. Result

1. **The vblank plateau does not hold the MEAN frame time in Sky Garden** (a correction to ROADMAP §4,
   recorded in §0.1 before acting, and corrected by the audit). The vblank tick quantises single
   intervals and the median, while the mean follows the GuestGpu thread's work: earlier Sky Garden
   steady windows 31.15–31.83 ms with 9.7–13.5 % one-vblank intervals (`pl96a`, `dab102a`,
   `ckpt102_entry1`); draws per interval grow with its length (2 884 / 5 252 / 7 376 for 1/2/3 vblanks);
   across 351 ABBA blocks dt − GuestGpu CPU stays 0.70–0.84 ms while CPU goes 30.1 → 35.2 ms, with no
   plateau at 33.3 ms. **Mechanism (as the audit found it, not as first written):** GuestGpu does wait on
   the flip — `R_WAIT_FLIP_DONE` once a frame with two display buffers, so it runs at most ~2 flips ahead —
   but that wait has slack while per-frame work exceeds ~20 ms [I] (peak `lat_us` 19.6–20.3 ms in steady windows). The first
   write-up credited the 16-deep flip queue and cited desert runs whose windows mix a 60 FPS phase with the
   scene; both are withdrawn. Consequences: **route V closed while per-frame work > ~20 ms** (it would
   reopen below); **game speed is measured by Δ`dt` directly** — the ratio Δdt/Δcpu_net is 0.58 in
   `dwk104` (95 % CI 0.43–0.70; +196 µs of GuestGpu off-CPU time, cause not isolated) and 1.02 in `sh104`.
2. **`dawalk=1` SHIPPED as the default** (the PM4 look-ahead walk of the M1 draw-ahead moved off the
   GuestGpu thread; the gate existed since session 59, default 0). Sealed ABBA `dwk104` (`pred/03`, 600 s,
   pinned, 92 pairs, every control PASS): **Δ`cpu_net_us` = −458.5 µs** (2·SE 114.6, t −8.00), **Δ mean
   `dt_us` = −265.9 µs** (2·SE 114.5, t −4.65); arm levels `dt_us` 32 162 → 31 618, `cpu_net_us`
   31 243 → 30 744. The cost it brings, as predicted: `da_take_us` +414.7, `da_miss` +219.1 a flip,
   `da_late` +8.1, `da_hit` −231.5. Video `vwk104` (gate text `dawalk=1`, recorded) 3 886 frames, 0
   one-frame glitches ⇒ scorer verdict SHIP. New build `61ae7347…` (`44f01b4`): video `vid104` with the
   compiled default (no `dawalk` in the gate file; `da_wjobs` ≈ 8 a flip) 3 917 frames, 0 glitches.
   **≈ +0.8 % game speed in Sky Garden, from Δdt** (−265.9 µs of 32 162; ABBA with the GPU clock pinned — on
   the default unpinned setup, where the DRS step moves, not tested). **ROADMAP §6: an A/B-passed
   real-path change.** Afterwards `gates_base.txt` of the harness pins `dawalk=1` (a one-pin byte edit,
   1 092 B / 99 names, sha256 `303a7849…`; `pred/03` §5 named `gen_gates.py`, which today writes all 135
   names and would change the harness composition — disclosed in `pred/04`); `gates_base.json` was rewritten
   too, and the archived scorers pin `GATES_SHA` `00c116dc…` as well as the installed exe, so they no longer
   admit this session's runs.
3. **Route A, Stage 1 "kill or go" (sealed `pred/02`): A PROCEEDS BY STAGES.** `mut104` INVALID (11
   `AsyncPipelines: skipped draw` in one frame ≈ 2 330: a new pipeline permutation compiled; the sealed
   control NO_FATAL_MARKER), the one allowed repeat `mut104b` ADMITTED, `sh104` ADMITTED. **G (central)
   = 5 683 µs ≥ 3 000** (G^ = 7 629): `S_now` 20 073 µs (session 83: 20 838), `S_ctx` 17 690, the W = 4
   concurrency tax **T4 = +2 532.5 µs** (t 32.5; session 64 had 1.3–2.0 ms), spine 1 085. The rule
   decides on the central G (`a104.py verdict()`); the scorer's printed line "RULE (G^ < 3000 …)" is a
   stale string.
4. **Regression screen `reg104` (sealed `pred/01`): none** — mean `dt_us` 31.15 ms (−2.1 % vs
   `ckpt102_entry1`), CPU per draw 6.113 µs (−2.2 %), inter-run. **Disclosed (audit, MAJOR): a design-review
   agent was reading and scanning files during the run**, against the seal's "no other work"; the run
   also had the (then) incompatible seed, 21 `AsyncPipelines: skipped draw` and one held flip (the
   marker that made `mut104` INVALID; `pred/01` has no such control) and one 212.9 ms hitch. Load could
   only push it slower; the reading stands.
5. **The shader seed (session 103's regression) is rebuilt**: 512 shaders / 638 recipes (was 380 / 438)
   from the translation cache after runs covering the intro, the desert (`intro_next`, the session-38
   key route) and Sky Garden; a cold check with the local cache moved aside logs `ShaderSeed: installed
   (512 shaders)` and `PipelinePrecache: 638 recipes -> 517 graphics + 121 compute pipelines queued, 0
   skipped`; the local cache (1 001 files) restored afterwards.

## 2. Route V and the plateau (reading, no run)

The present thread sleeps to the next 60 Hz tick, runs `VblankBegin()`, `m_flip_queue.Flip(0)` (the
front Ready request is presented), `VblankEnd()`. GuestGpu reserves a flip slot per flip packet (it
would block only with 16 pending — never here) and **waits on `R_WAIT_FLIP_DONE` once a frame for the
display buffer it is about to reuse (two buffers)** — the audit's correction. The steady-state `vid103`
(3 489 frames): vblanks 1/2/3 = 5.0/87.6/7.2 %, mean `dt_us` 33.8 ms (with video recording), GuestGpu busy
97.3 %. Long intervals carry more draws because a busy thread's work accumulates in them.

## 3. `dawalk`

`dawalk` (`KYTY_DRAW_AHEAD_WALK`) walks the guest's PM4 at submission on the `DrawAheadWalk` thread and
queues M1 materialisations ahead of GuestGpu; `dawalklead=1` keeps it at most one submission ahead. In
sessions 59–60 it was measured without ABBA or clock pin (with `dawalklead=2` −0.3…−1.4 % CPU a draw,
with lead 1 +2.4 / −0.4 / −1.6 %, inside ±1.4 % resolution) and left 0. Arming in `dwk104` arm 1: `da_wskip` 21 330 vs `da_wjobs` 21 339 (identity
−0.04 %), no drops, walks per flip equal in both arms.

## 4. Route A, Stage 1

`C:/kyty/s104_designA/review.md` (in git `docs/session-104/designA_review.md`): best case 1.2–1.26×
game speed [I], 10+ sessions, the strongest prior against it the concurrency tax. Stage 1 measured the
two uncertain terms: `S_now` (serial floor today) and T4 (tax of four concurrent readers of the
caches, measured with read-only probes — contexts that WRITE would pay more, not measured). G ≥ 3 ms,
so A proceeds: Stage 2 was `dawalk` (shipped above); Stage 3 (the enabler at N = 1) is next.

## 5. Source, builds, provenance

* Commits: `06eef00` (decisions 1–4), `d0502da` (`pred/01`), `0eeefd5` (route-A rule, `dawalk` stage),
  `dbd6538` (`pred/02`, `pred/03`, scorers pinned), `8b107cd` (results + ship decision), `44f01b4`
  (`dawalk` default 1), and the session commit. No push.
* Binaries: `16ef56b6…` (all measurement runs), `61ae7347…` (the ship build; `vid104` only).
* `check_gate_order.py` clean. `gates_base.txt` now pins `dawalk=1` (1 092 B, 99 names, sha256
  `303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf`; before: `00c116dc…`) — the next port
  asserts the new hash.

## 6. Harness

`C:/kyty/s104`, ported by a fresh `C:/kyty/s103/s104_port.py`: `PRECONDITIONS PASS: 5 root constructs;
35 sealed texts (34 land in prev103/pred, 1 stays in carried prev100/pred); 27 live paths (16 files) +
9 expression paths (7 files); gates 1092 B / 99 names; gates.cpp 135 entries (111 gates + 24 knobs);
ABSENT 36` → `PORT DIAGNOSTIC: clean; carried=4725 ledger=54 skipped=210`. New: `a104.py` +
`test_a104.py` (65), `dwk104.py` + `test_dwk104.py` (40), `go104.sh`, `go104b.sh`,
`gates_dawalk1.txt`, `gates_nodawalk.txt`, the seed artefacts (`seed_new/`, `seed_previous/`).

## 7. Runs

| tag | what | outcome |
|---|---|---|
| `reg104` | regression screen (`pred/01`) | no regression |
| `seed104` | intro + desert key route (seed coverage) | reached `intro_next` |
| `seedcheck` | cold start with the new seed | 512 installed, 638/638, 0 skipped |
| `sh104` | Stage 1b `shadowresolve=0|4` | ADMITTED, T4 +2 532 µs |
| `mut104` | Stage 1a `mutwide=0|15` | INVALID (skipped draws) |
| `mut104b` | the allowed repeat | ADMITTED ⇒ G 5 683 µs, A proceeds |
| `dwk104` | Stage 2 `dawalk=0|1` | ADMITTED, SHIP pending video |
| `vwk104` | video, gate text `dawalk=1` | 3 886 frames, 0 glitches ⇒ SHIP |
| `vid104` | video, new build, compiled default | 3 917 frames, 0 glitches |

## 8. Adversarial audit (sealed `pred/04_audit_addendum.md`)

* **Recount — NOT REFUTED** (six claims, own code): every number of §1–§7 to 4 decimals; the dwk104
  gain comes from the one-vblank share and fewer > 40 ms frames (row medians 33.27 vs 33.26 ms);
  order carry-over −576 vs −341 (cancelled by ABBA); G likely conservative (≈ 600 µs of instrument time
  left in S_raw).
* **Protocol — REFUTED narrowly:** MAJOR `reg104` overlapped an agent's file scans (§1 item 4); minors:
  `<fill>` fields in `pred/02`/`03`; the stale "RULE (G^ …)" label; the `mut104` repeat chosen after the
  invalid run's G was printed (same direction); `gates_base.txt` edited by hand instead of `gen_gates.py`;
  the scorers' IDENTITY hashes the installed exe, so after the ship build they no longer admit these runs;
  `go104.sh` did not check results between runs. ROADMAP-first and seal-before-run hold for every
  decision-bearing run.
* **Plateau — PARTLY REFUTED:** the Sky Garden conclusion stands (stronger); the mechanism, the desert
  evidence and "~1:1" are corrected (§1 item 1); route V's closure stands with its regime bound.

## 9. Proved, and not proved

**Measured.** `dawalk=1` lowers GuestGpu CPU by 458.5 µs and the mean frame by 265.9 µs a flip in Sky
Garden (pinned, ABBA); it is the default. Route A's kill-or-go term G = 5.7 ms (≥ 3 ms). The seed is
restored. In Sky Garden the mean frame follows GuestGpu work without a 33.3 ms plateau. **Not proved.**
That route A will reach G (a model ceiling); the write-side concurrency tax; the cause of the +196 µs
off-CPU time under `dawalk=1`; the plateau statement below ~20 ms of work (there the double buffer probably
binds [I]); the gain on the unpinned default setup;
any 60 FPS statement.
