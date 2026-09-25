# Audit 119 — adversarial check of the CLOSURE of route A (G₂ = 2 216,5 µs < 3 000)

Lens: try to refute "route A closed for maximum FPS" (ROADMAP 119 item 4, `docs/ROADMAP.md:2483-2497`). Nothing was
run, built or edited; the logs were read in binary mode by my own parser (no code shared with `g2_119.py`), kept in the
session scratchpad (`closure_parse.py`, `spin_check.py`, `blocks_dump.py`).

**VERDICT: HOLDS_NARROWLY.** The sealed rule is applied exactly as sealed, every term is reproduced to 0,01 µs, and no
single measured uncertain term moved to its A-favourable end reaches 3 000 µs (closest: T₂ − 2SE − `sh_push` ⇒ 2 907,8;
f = 0,5 ⇒ 2 850,6). But the margin is thin and model-dependent: 8 of the 15 two-term combinations of the sealed uncertain terms
cross the bar, the sealed "ceiling" already sits at 3 724,2, and one **structural** term the route's own design left open
— where the spine runs — flips the verdict alone (spine off GuestGpu's critical path ⇒ G₂ = 3 484,7). The closure stands
as a sealed-rule outcome; the substantive sentence in item 4 is stronger than the evidence (MAJOR E1 below).

---

## 0. Reproduction (CONFIRMED)

- sha256 of `pred/01_g2_119.md` (e22c96a7…), `g2_119.py` (2f089ef5…), `test_g2_119.py`, `mut_g2_119.py`,
  `make_g2_119.py`, `go119a.sh`, `gates_base.txt` (303a7849…), the pinned and the installed exe (d3a981a2…),
  `a104.py` (dfa2313a…) and `mut_g2_119.out.txt` all equal `SEALS119.txt`. Order: pred mtime 00:01, seal commit
  `3aaddb6` 00:29:24, runs 00:30–00:41 (`go119a.log`), score 00:41:40, item 4 commit `e0be82b` 00:42:11.
- My parser with the scorer's geometry (block b = frames 1801+90b … 1890+90b, kept idx 60..88, blocks 4..83, pairs
  inside complete quartets; `g2_119.py:331-357`): 40 pairs in each run, and

| term | scorer | independent |
|---|---:|---:|
| `cpu_net` (sh119 arm 0) | 30 252,5 | 30 252,52 |
| T₂ = d `cpu_net` (sh119) | 1 645,4 ± 157,4 | 1 645,39 ± 157,40 |
| T₂ on `dt_us` | 1 767,0 ± 177,1 | 1 767,04 ± 177,12 |
| `sh_push` (arm 1) | 533,8 | 533,81 |
| `S_lo` / `S_raw` | 13 193,2 / 21 642,3 | 13 193,19 / 21 642,34 |
| `P_mw` | 61,8 ± 155,6 | 61,80 ± 155,63 |
| `T_in` ⇒ dI | 124 956 ⇒ 494,8 | 124 955,6 ⇒ 494,8 |
| `E_rec` / `E_com` | 1 246,0 / 2 299,9 | 1 245,95 / 2 299,90 |
| spine proxy (mut arm 0) | 1 268,2 | 1 268,17 |

  G₂ = 30 252,5 − [18 724,2 + 0,555·11 528,3] − 1 268,2 − 1 645,4 = **2 216,5** (CONFIRMED). Margin to the bar 783,5 µs;
  every µs removed from `S_ctx` is worth 0,445 µs of G₂.

## 1. (a) Each uncertain term at its A-favourable end, one at a time

| term moved (all else central) | G₂ µs | flips? |
|---|---:|---|
| `P_mw` → `P_mw` + 2SE (217,4) | 2 285,8 | no |
| dI doubled (989,6) | 2 436,7 | no |
| C_TS at this run's upper bound 4,81 ns (§3) | 2 263,8 | no |
| `E_move` = `E_rec` + `E_com` (3 545,9) | 2 743,6 | no |
| T₂ − `sh_push` (1 111,6) | 2 750,4 | no |
| **T₂ − 2SE − `sh_push` (954,2)** | **2 907,8** | no — 92 µs short |
| **f = 0,5** | **2 850,6** | no — 149 µs short |
| f = 0,564 (p90) | 2 112,8 | no (against A) |
| spine = 959 | 2 525,7 | no |
| S_raw workload-matched (21 387,4, §6) | 2 330,0 | no |
| **spine off GuestGpu's critical path (0)** | **3 484,7** | **YES** — see E1 |

Break-evens (single term): `S_ctx` −1 760,6 µs; spine ≤ 484,7 µs; T₂ ≤ 861,9 µs; f ≤ 0,4870 (impossible at W = 2:
f = max(f_max, 1/W) ≥ 0,5); `W_E` ≥ 2 876,2 µs; C_TS ≥ 18,05 ns.

**No single measured term flips it; f alone cannot flip it by construction.** Pairs of the sealed terms that do flip
(8 of the 15 pairs among P, dI, E, T^, f 0,5, spine 959): dI×2 + T^ 3 127,9; dI×2 + f 0,5 3 098,0;
E + T^ 3 434,8; E + f 0,5 3 442,8; **E + spine 959 3 052,7**; T^ + f 0,5 3 541,8; **T^ + spine 959 3 216,9**;
**f 0,5 + spine 959 3 159,8**; and every pair with spine 0. Pairs that do not: P+dI 2 506,0; P+E 2 812,8; P+T^ 2 977,0;
P+f 2 928,4; P+spine959 2 595,0; dI+E 2 963,8; dI+spine959 2 745,9. With the artefact-free tax T₂ − `sh_push` (1 111,6,
no −2SE) the pairs with f 0,5 (3 384,5), E (3 277,5) and spine 959 (3 059,6) also flip.
The sealed ceiling G₂^ = 3 724,2 (`g2_119.py:842-848`) is itself above the bar — the rule says it decides nothing, and
that rule was followed.

## 2. (b) Is one read-only shadow reader a fair stand-in for a second WRITING context?

Code facts: the reader re-runs, for **every** draw, the read-only part of binding resolution
(`shadowResolve.cpp:172-219`), taking `TextureCache::m_lock` (a `TrackingSpinLock`) per image probe
(`textureCache.cpp:2162-2167`) and reading the buffer cache **without** a lock (`shadowResolve.h:26-27`); GuestGpu
builds a per-draw job and pushes it into a Vyukov ring (`descriptors.cpp:2742-2818`, `shadowResolve.cpp:59-77, 221-240`),
timed as `sh_push_us`.

Quantified parts, both from `sh119` (independent parser):
- **Inflates T₂ (for A): `sh_push` 533,8 µs = 32 % of T₂** — job copy + ring push + seq_cst fence per draw, a pure probe
  artefact no segment/DCB design pays; plus ≈ 4 `NowNs` per draw only in arm 1 (≈ 40–80 µs, partly outside the timed
  span). **Yes, it inflates T₂.**
- **Deflates T₂ (against A): d `spin_gpu_us` = +104,0 ± 3,7 µs** (2 405 more contended acquisitions a frame). `cpu_net` =
  `cpu_gpu_us − spin_gpu_us` (`g2_119.py:30, :367-368`) and `spin_gpu_us` is exactly the GuestGpu spin on
  `TrackingSpinLock` (`regionManager.h:40-75`, `LockSpinGpuNs`), so the lock-contention part of the reader's tax is
  subtracted out of T₂ by definition (d `cpu_gpu_us` = 1 749,4).

Net of the two quantified parts: T₂_fair = 1 749,4 − 533,8 = **1 215,6 µs ⇒ G₂ = 2 646,3** (margin 354).

Unquantified, for A: the reader touches 100 % of draws in lockstep with GuestGpu (the very image records and lock line
GuestGpu just used), while a W = 2 second context resolves only its ≈ 44,5 % segment. Unquantified, against A: a writing
context takes the mutating paths under `m_lock` (`FindTexture`, `TouchImage`, `ConfigureImageSource`), needs locks the
buffer cache does not have today, and shares pipeline-cache, descriptor-heap, stream-ring and tick state the reader never
touches. **The direction is not established.** The pre-registration's "the direction is unfavourable to A and
unmeasured" (`pred/01_g2_119.md:81`) asserts a direction; the only measured pieces point the other way by ≈ 430 µs.
If the tax lands only on the critical path's share (25 122/30 252 = 0,83) — unmeasured, stated for scale — T₂ ⇒ 1 366,
G₂ ⇒ 2 495.

## 3. (c) Cross-run constants

- **`W_E` (s101, 1 115,6):** to flip alone it must be 2 876,2 µs; `W_E` is the write-list + emit INSIDE
  `CommitBindings`, whose whole this run measures as `E_com` = 2 299,9. Physically bounded ⇒ at most 2 743,6.
  **Cannot flip.** (Scaled to this run's `E_com` it would be ≈ 1 133 — irrelevant.)
- **`C_TS` (s96, 3,96 ns):** to flip alone it must be 18,05 ns (4,56×). This run bounds it: the cross-run instrument
  price A12 = 1 205,4 µs covers ≥ 250 541 counted GuestGpu timestamps in mut arm 0 (pathlap 91 472 + plkstat 30 762 +
  amut/MutexMark 128 307, HoldLap not counted) ⇒ **C_TS ≤ 4,81 ns**; even counting only pathlap + plkstat, ≤ 9,86 ns.
  **Cannot flip.**
- **Harder bound on the whole instrument correction:** if every µs of arm-1 instrument price (A12 + `P_mw` = 1 267,2)
  sat inside `a_mut_us`, S_now ≥ 20 375,1 ⇒ **G₂ ≤ 2 532,7**. The sealed ceiling's P+2SE and 2·dI (S_now^ 20 435,3) are
  already about that generous.
- **Jointly** (`W_E` = `E_com`): needs C_TS ≥ 8,57 ns — above the full-census bound 4,81, below the partial one; not
  plausible with one `NowNs` implementation. **The cross-run constants cannot carry a flip.**

## 4. (d) The rule, as sealed — CONFIRMED

ROADMAP 118 item 6 (`ROADMAP.md:2412-2415`) and 119 item 1 (`:2438-2441`): G₂ = `cpu_net` − [`S_ctx` +
0,555·(`cpu_net` − `S_ctx`)] − spine − T₂; spine = max(run (1a) = `mut119` arm-0 proxy, 959); T₂ from
`shadowresolve=0|1`; central decides, ceiling decides nothing; NOT_EVALUABLE on a non-admitted run or area Δ > 3 %.
The scorer implements exactly this (`g2_119.py:106-111, 795-798, 814-815, 830-849, 883`); both runs ADMITTED first
time (40 pairs each, all checks PASS), area cross-run 0,002 %; the A4 MISS is a prediction without weight. The spine
proxy from the instrumented run (1 268,2) equals the uninstrumented one (1 266,8) within 1,4 µs — the disclosed risk
(1 369 vs 1 289 in the smokes) did not materialise. **Applied as sealed.**

## 5. (e) Is anything stated more strongly than the evidence?

**E1 — MAJOR: the spine is charged additively to GuestGpu's critical path, while the route's own design leaves its
placement open and prefers the walker.** The G formula is session 104's (`s104/pred/02_a_stage1.md` §5.3), where the
spine was the PM4 walk ON GuestGpu (`dawalk=0`). Since then: route A's stage 4 is "shadow spine fused with the walker"
(`s104_designA/review.md:56`); DESIGN_82 makes the spine its own thread feeding W record contexts
(`DESIGN_82_parallel.md:73-95`); s117 "in route A the spine may run there (the walker already decodes every submission
at enqueue)" (`docs/session-117/designA4_spine.md:84-86`) and measured the walker fit 3 207 vs 32 917 µs
(`ROADMAP.md:2256-2257`); s118 built the carry check precisely because "the walker (or a spine thread) will not be
seeded" and calls the placement "a separate question" (`docs/session-118/designA4_part2.md:9, 17`); C PASSED in
`spk118`. The charged value itself is walker-thread time (`pred/01_g2_119.md:34`). With the spine off the contexts'
critical path the same measured terms give **G₂ = 3 484,7 ≥ 3 000 ⇒ stage 3 would resume**; the verdict survives only
if the walker-placed spine leaves ≥ 484,7 µs of residual critical-path cost (pipeline fill, M1 cooling on a busier
walker — s59/60 saw moving the walk off-thread cool M1 by as much as it saved —, uncertain-plan fallbacks). That
residual is unmeasured. The procedural closure stands (sealed consequence, rule followed); the sentence "маршрут A
(параллельная обработка потока команд) закрыт для максимума FPS" (`ROADMAP.md:2491-2492`) should be scoped: *closed under
the sealed s104 model that charges a PM4-walk-sized spine to GuestGpu's critical path*. A reopening would need
evidence, not argument: a measured residual < 485 µs for a walker-side spine.

**E2 — MINOR: "потолок G₂^ 3 724,2 (все неопределённые члены в пользу A)"** (`ROADMAP.md:2489-2490`, also
`g2_119.py:47-48`). The ceiling moves P, dI, E and T₂ but holds f at 0,555 and the spine at max(proxy, 959) = 1 268,2
— its A-unfavourable choice. With f = 0,5 and spine = 959 (the measured lower bound) the all-A ceiling is **4 768,4**;
with the spine off the critical path, 5 727,4. No effect on the verdict (the ceiling decides nothing), but the label
overstates robustness.

**E3 — MINOR: "налог … 861,9 мкс, измерен вдвое больше"** (`ROADMAP.md:2490`). True for raw T₂ (1 645,4 / 861,9 =
1,91×). Without the per-draw push artefact the measured contention tax is 1 111,6 (1,29×), at −2SE 954,2 (1,11×),
with the spine excluded from `cpu_net` added back 1 215,6 (1,41×).

**E4 — MINOR: scope.** One scene (Sky Garden), one build, pinned GPU clock; s64 measured a lower one-reader tax in the
desert (+4,3 % vs +6,3 %). The sealed rule text itself has no scene qualifier, so item 4 follows it; the micro-track
sentence of the same item does carry "в Sky Garden". Also the closure is carried entirely by the s118 W = 4 K4 FAIL
(median `dep` 325 ‰ vs 300 ‰): with f = 0,30 the same s119 terms give G₄ = 5 156 (T = T₂) or 4 270 (T = s104's 2 532),
both ≥ 3 000. That FAIL is directionally robust (the census misses buffer writes, s118 audit — `dep` biased low).

**E5 — MINOR: the Amdahl form is conservative against A and unmeasured.** T = `S_ctx` + f·(`cpu_net` − `S_ctx`) lets no
serial section overlap the other context's parallel work. If serial sections of the two contexts interleave under
locks (DESIGN_82's L0–L8), the makespan's lower bound is max(`S_ctx`, 0,555·`cpu_net`) = 18 724 µs, far below the model's
25 122; if stream order forces them to serialise end-to-end, the model is about right. `S` also counts read-mostly
lock-held time (`pl_prog_hold` 4 674,6 µs under `PipelineCache::m_mutex`) as serial. None of this is a refutation — it
is the program's standing model (`ROADMAP.md:20-23, 49-52`) — but "closed" is a statement about that model.

**E6 — MINOR: what item 4 says the closure means.** "после закрытия A … остаются только кандидаты с потолком ~1 мс"
(`ROADMAP.md:2496-2497`) is true, but omits that A's own central estimate (2,2 ms ≈ 7 % game speed) exceeds every
remaining candidate's ceiling; A is closed by the s104 cost bar (3–5 enabler sessions before any gain), not because its
modelled gain is smaller than the alternatives.

**E7 — MINOR: stale status lines.** `ROADMAP.md:39` still says "для «максимума FPS» A переоткрыт и прошёл этап 1, G =
5,7 мс" and the §2 A header `:2552` "переоткрыт в с. 104 и идёт этапами" — contradict item 4 (to fix at session close).

## 6. Population sensitivity (MINOR, does not flip)

Levels are medians of block means in a two-mode scene (per-block draws 4 744–5 279). A one-frame window shift
(frames 1860+90b…) moves `S_raw` by −233 (21 409,1) and gives G₂ = 2 321,5. The medians pick `S_raw` from blocks with
≈ 1 % more draws than `cpu_net`'s (mut arm-1 draws level 5 061,8 vs sh arm-0 5 013,0; paired d draws is only 3,4) —
the area control (Σkpx/Σatt ≈ 2 007 in every block) cannot see this. Workload-matched `S_raw` (linear fit at 5 013
draws) 21 387,4 ⇒ G₂ 2 330,0; means instead of medians 2 278,8; `S_raw` = arm-0 level + paired d 2 286,6. Range
2 216–2 330: all < 3 000.

## 7. Findings

| # | class | claim | evidence |
|---|---|---|---|
| R | CONFIRMED | every G₂ term and the verdict reproduce to 0,01 µs; hashes match the seal; order seal → runs → score → item 4 | §0; `SEALS119.txt`; `go119a.log`; `git log` |
| D | CONFIRMED | the sealed rule is applied as sealed (formula, f₂, spine max, T₂, central decides, no NOT_EVALUABLE trigger) | `ROADMAP.md:2412-2415, 2438-2441`; `g2_119.py:795-883`; score txt |
| A | CONFIRMED | no single measured uncertain term flips (max 2 907,8 for T₂−2SE−push; 2 850,6 for f 0,5); f cannot flip at W = 2 | §1 |
| C | CONFIRMED | cross-run constants cannot flip: `W_E` needs 2 876 > `E_com` 2 299,9; C_TS needs 18,05 ns vs ≤ 4,81 ns bound from A12 | §3 |
| E1 | MAJOR | closure depends on charging the spine additively to GuestGpu; the route's design leaves it on the walker; spine off the critical path ⇒ G₂ 3 484,7 | §5 E1; review.md:56; designA4_spine.md:84-86; designA4_part2.md:9,17 |
| A2 | MINOR | 8 of 15 two-term combinations of sealed uncertain terms cross the bar; sealed ceiling 3 724,2 > bar | §1 |
| B1 | MINOR | `sh_push` (533,8 = 32 % of T₂) inflates the tax; spin subtraction deflates it by 104,0; fair G₂ 2 646,3; "direction unfavourable to A" is unmeasured | §2; `descriptors.cpp:2742-2818`; `regionManager.h:40-75`; `g2_119.py:367-368` |
| E2 | MINOR | "ceiling = all uncertain terms in favour of A" is false (f, spine held); all-A ceiling 4 768,4 | `ROADMAP.md:2489-2490`; `g2_119.py:47-48, 848` |
| E3 | MINOR | "tax measured twice the break-even" holds only for raw T₂ (1,91×); artefact-free 1,29× | §5 E3 |
| E4 | MINOR | Sky-Garden-only, one build; closure carried by the W = 4 K4 FAIL (G₄ ≥ 4 270 otherwise) | §5 E4 |
| E5 | MINOR | Amdahl no-overlap form and lock-held reads in `S` are conservative against A, unmeasured | §5 E5 |
| E6 | MINOR | item 4 omits that A's central (2,2 ms) exceeds each remaining candidate (~1 ms) | `ROADMAP.md:2496-2497` |
| E7 | MINOR | stale route-A status at `ROADMAP.md:39` and `:2552` | §5 E7 |
| P | MINOR | median levels in a two-mode scene: G₂ 2 216–2 330 across estimators | §6 |

**Bottom line.** Refuting the closure through the measurements fails: the numbers are right, the rule was followed,
and the pre-registered uncertainties one at a time stay under 3 000. What does reach 3 000 is either a pair of them or
the spine's placement — a design question the route itself had not closed. Record the closure as *route A closed for
maximum FPS under the sealed s104 model (spine on GuestGpu's critical path, Amdahl without overlap), Sky Garden, W = 2
ceiling of `spk118`*; correct the "all uncertain terms" label of G₂^; and write down that the only live reopening path is
a measured walker-side spine residual below 485 µs.
