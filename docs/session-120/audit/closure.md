# Session 120 audit — lens: CLOSURE AND INTERPRETATION

Read-only audit (no file edited, nothing built, the game not run, nothing committed). Sources read: ROADMAP s120
items 1–7 (commits `996d565` … `096dcfc`), `design/design120.md`, `r1.md`, `r1_review.md`, `pred/01_cen120.md`,
`SEALS120.txt`, `runs120/rpk120_cen120.{txt,json}`, `runs120/spc120_cen120.{txt,json}`, `go120a.log`,
`docs/session-120/impl_report.md` (review notes), `LOOP_STATE.md`, ROADMAP s119 item 5 (A-walker debt), and the source
at HEAD (`descriptors.cpp` memo hit/miss/store paths, `MemoTextureWay`/`MemoResourceKey` of `texmemo2`, `RebindImages`
texfast eligibility), plus `docs/PLAN_82_bind.md` and `docs/local-session-56.md` for the history of `texmemo2`.

Numbers below are the sealed scorer outputs unless marked [I] (my inference/arithmetic).

## 0. Verdict of this lens

| sealed item | scorer verdict | does it hold? | how narrowly |
|---|---|---|---|
| R1 member | OPEN, `C_R1` = 658.8 ± 9.1 µs (w8) | **HOLDS** (sealed rule applied correctly: point ≥ 500, all bad = 0, `w1` = 0) | **narrowly as a ceiling**: after the known-sign corrections the honest net ceiling is ≈ 0.33–0.62 ms, central ≈ 0.48–0.52 ms [I]; realizable gain ≈ 0.25–0.50 ms [I] |
| R2 member | NOT_OPENED (pt 435.2, up 1 067.6, lo −36.8) | HOLDS | border is **systematic** (spread 1 104 µs from [I] constants vs 2SE 12.7) — a rerun cannot resolve it |
| package R | OPEN 1 093.9 ± 15.0 | holds arithmetically | **vacuous**: adds nothing beyond R1 OPEN; licenses nothing for R2 |
| spcen A | NOT_OPENED (N_A 340.2, N⁺_A 686.9) | HOLDS | border is systematic; the add-back point N_A + Z_A = 468.3 is just under 500 — A is a genuine border, not "below" |
| spcen B | CLOSED (−8.1; upper 177.9 + 2SE 3.9 = 181.8 < 500) | **HOLDS ROBUSTLY** | even the GROSS would-hit transit time (G_B 403.6, warm-corrected G_B⁺ 434.7) is < 500 |
| package SP | NOT_OPENED (332.1 / 864.9) | HOLDS | as A |

Item 7's numbers are all faithful to the scorer outputs (checked one by one). Its **interpretive clauses** are not all
faithful (MAJOR 2, MINOR 1–3).

## 1. R1 — is `C_T` an honest upper bound?

### 1.1 What the sealed number is made of (w8, µs a frame, P arm, 3 001 window frames)

`A` 626.1 (= W 1 258.7 would-hits × (t_T 516.6 − t_hit 19.2) ns) − `L` 33.1 + `R` 81.1 + `E` 28.4 − `P` 43.7 = **658.8**.
So ≈ 95 % of the ceiling is `A`: the whole measured miss price of each would-hit lookup, minus a hot hit price.
Per would-hit the ceiling is 523 ns — i.e. the table saves the entire miss path plus a re-record, and pays a hit of
19 ns. Everything that can be wrong with the bound is in the two prices, not in the count (the count is exact:
full-proof, 0 bad on ≈ 1.9 M pre-half w8 would-hits [I: 629/frame × 3 001], `w1` null control 0, `r1_incl` 0,
`r1_xthr` 0).

### 1.2 Terms that make the real gain smaller than `C_T` (all of known sign; none priced in `C_T`)

| # | effect | sign on real gain | size, µs a frame [I] | basis |
|---|---|---|---|---|
| a | **t_hit measured hot.** `t_hit` is the mean over a 1/8 random sample of ALL real hits (≈ 46 k, overwhelmingly hot entries). A would-hit hits an entry that the direct table evicted — its image lines and its ~650-B memo slot are colder. | − | **≥ 40** (lower bound: the census's own warming control says touching the candidate's image lines lowers the miss price by `warm_ns` = 31.6 ns; the would-hit's hit tail reads the same lines: 31.6 × 1 259 = 39.8) to ≈ 130 (≈ 100 ns incl. the cold slot) | `warm_ns` from rpk120; r1.md §5.5 lists it as an unpriced minus |
| b | **emit of a would-hit copies the ~584-B desc from a cold slot**; the miss path's desc is hot on the stack. Emit is outside both intervals by design, so this asymmetry is not in `t_T − t_hit`. | − | 0–50 | r1.md §2.2 ("emit … paid on both paths") |
| c | **E carries census pollution.** `t_ham` (hit right after a stored miss) follows `R1Miss` (XXH3 digest of 73 words + 4 table fills in 1.9 MB) — the implementation review (impl_report NB, r1 review) says E is biased upward. | − | 0–28.4 (`C_noE` = 630.4) | impl_report REVIEW r1 NB |
| d | **t_T inflated by P-arm pollution.** The P arm carries all three instruments (+2 682 µs `cpu_gpu_us`, +8.1 %); their tables (R1 1.9 MB, R2 replay, spcen) evict lines the miss path needs. No level-1 (timers only) run exists to compare, so this was never gauged. | − | 0–60 (≤ ~10 % of A) | price line; design recommended a level-1 comparison, not done |
| e | **t_hit lowered by R2 replay/census warming the memo lines in P** (impl_report NB line 214: "a lean toward OPEN of unknown size"). | − | 0–15 | impl_report |
| f | **probe under-priced.** `P` = 43.7 is a sub-nanosecond op (0.94 ns/lookup) measured by rdtsc pairs minus a null pair on self-sampled HITS only; unserialized rdtsc hides short ops; the LRU `use` write on every hit is not in the timed span; key misses scan all 8 ways. | − | 0–45 | impl_report §3 "probes reused for the LRU update" |
| g | **R counted as an upper** (the first re-record after a would-hit fill is booked as avoided even if `bind_stamp` moved and the kept view would be re-recorded anyway). | − | 0–40 (of 81.1) | r1.md §5.5 |
| h | **losses' own re-records not charged** (a lost hit is a store ⇒ `fast_view` reset ⇒ a re-record). ≈ 66 losses a frame [I: 33.1/(516.6−19.2)]. | − | 0–10 | — |

Terms that could make the real gain LARGER than `C_T`: census pollution inflating `t_hit` (reviewer's arithmetic
bound ≤ ~5 µs), and R2's population growing once R1 turns misses into hits (not R1's own gain). Both small.

**Conclusion.** `C_T` IS an honest upper bound in direction: every material unpriced effect lowers the real gain.
It is a **loose** one: the corrections sum to −40 … −330 µs, so the **honest net ceiling is ≈ 0.33–0.62 ms, central
≈ 0.48–0.52 ms [I]** — at the 0.5-ms line, not comfortably above it. The sealed OPEN holds (the rule is "point ≥ 500",
and the point is 658.8); what the close must not do is read 658.8 as the expected size of the win.

### 1.3 The table shape: 8-way vs direct 16 K

The census favours w8 on every axis it measures: more would-hits (1 258.7 vs 1 021.9 — conflict misses dominate,
not capacity), a higher `C` after subtracting a measured probe (658.8 vs 621.7). The d16 figure has `P = 0` and
**no footprint term at all**: 16 384 × ~650-B entries ≈ 10.6 MB vs 2.7 MB today, read by ≈ 46 k hits a frame; a
footprint penalty of 1 ns a hit (−46 µs) already exceeds the 37-µs gap. So d16 is dominated, not a fallback.

### 1.4 Likely real gain and detectability

Realizable gain of a real 8-way memo on the timed (census-free) arm: **≈ 0.25–0.50 ms, central ≈ 0.35–0.40 ms [I]**
(honest ceiling minus implementation friction: set index, 8-way compact tag scan, LRU writes on 46 k hits). This is
consistent with the lead's "about half" (≈ 0.33).

Detectability by one sealed ABBA with 2SE(dt) ≈ 0.14–0.18 ms (SE ≈ 0.07–0.09): the ship rule needs the upper end
of the interval below 0, i.e. `est < −2SE`; power = Φ(g/SE − 2):

| true gain g | power (SE 0.07 … 0.09) |
|---|---|
| 0.15 ms | 38–54 % |
| 0.25 ms | 79–95 % |
| 0.35 ms | 94–99 % |
| 0.40 ms | ≈ 99 % |

So a prototype at the central estimate is detectable with high probability; a disappointing one (≤ 0.2 ms) has a
coin-flip chance of shipping even if real. The prototype's pre-registration should state this prediction and power
before the run, and name what a null ABBA would mean (the ceiling was loose, not the mechanism wrong).

## 2. Packages

**Package R OPEN adds nothing beyond R1 OPEN.** The package rule (item 2(б)) exists for the case where no member
reaches 500 but the sum does; here R1 alone reaches it, and the scorer (by the pre-registered rule "never a
NOT_OPENED member") names only R1 as open. The package licenses no R2 work. Moreover `R_pt` = 1 093.9 adds a
measured term (C_R1) to a **play-constant** term (C_R2,pt uses B, T′, N0, LS, A_tr — all [I] or older [M]); it is not a
ceiling of any single mechanism and should not be quoted as "the R track's ceiling" (item 7 bolds it as a result).
The disjointness claim (R1 = key misses + first re-record; R2 = memo-hit slots of clean repeating blocks) holds for
the census; in a real implementation they are **not additive in the other direction** either — R1 converts misses
into hits and so enlarges R2's clean-block population (the design's "the sum under-states" note). Fine as stated.

**Package SP**: NOT_OPENED with N⁺ 864.9 — of which B contributes at most 177.9 and at point −8.1. B's CLOSED as a
member therefore removes essentially nothing from the package.

## 3. spcen

### 3.1 B — CLOSED is sound

`N_B⁺ + 2SE` = 177.9 + 3.9 = 181.8 < 500. More decisively, **the gross would-hit time itself** — the whole transit
time of the stages the memo would skip, before any check cost is subtracted — is `G_B` = 403.6, warm-corrected
`G_B⁺` = 434.7. No cheaper check, no better implementation can take more than the gross; the closure does not
depend on the check-cost model, the add-back Z_B (154.9) or the Δ_B′ correction (31.1).

**What exactly is recorded exhausted** (item 7(в) should say this, narrowly): skipping the per-stage image
transitions of `CommitBindings` on draws inside an open render pass, **as a GuestGpu-thread CPU saving, on Sky
Garden, at the 0.5-ms net rule, as a standalone track**. Not covered: (i) the GPU-side cost of the barriers themselves
(irrelevant in Sky Garden, where GPU is 12.6–12.8 of 31.6 ms, but it becomes a different path in any GPU-bound scene
the s121 map finds); (ii) other scenes; (iii) B as a ≤ 0.18-ms package addend to A (see 3.2).

### 3.2 A — NOT_OPENED is correct, but the item-7 reading of it is not

`N_A` = 340.2 is the design's **lean-low** point: it subtracts the census's own timer reads, `Z_A` = 128.1, that a
real memo never pays (design120 §4, the blocking review of the spcen code). The add-back point is `N_A + Z_A` =
**468.3**; the upper, which also restores the warm-cache delta (`Δ_A` unclamped 297.0 µs × r_A 0.736 = 218.7), is
**686.9**. 2SE is 7.3. So A lies between 468 and 687 with the uncertainty entirely **systematic** — it is at least as
likely above 500 as below. "A упирается в цену собственной проверки" (item 7(б)) is true of the gross-vs-net gap
(G_A 1 001 − N_A 340 ≈ 0.66 ms of check/replay/record, of which 0.13 ms is census timer reads), but it reads like a
closure, which the sealed consequence does not grant.

### 3.3 The structural consequence for R2 and A

The sealed NOT_OPENED consequence is "the only admissible follow-up is a rerun, decided at the close". For both R2
(spread 1 104 µs vs 2SE 12.7) and A (spread 347 µs vs 2SE 7.3) a rerun of the same instrument **cannot** move the
verdict: the border is made by constants and bias terms, not noise. Hence (a) "no rerun" is the right decision; (b) the
correct reason is "a rerun cannot resolve a systematic border", not "below threshold"; (c) under the program's rule
"a sealed consequence is never set aside" both are now **parked by the rule, not exhausted** — any different
instrument or prototype for A or R2 is a new decision that must be recorded as such (and justify itself against the
"only a rerun" consequence of seal 01). For future seals: a NOT_OPENED rule should distinguish noise borders (rerun
helps) from systematic borders (only a sharper instrument helps) before the run.

## 4. Fidelity of ROADMAP item 7 to the sealed consequences

* Numbers: all match `rpk120_cen120.txt` / `spc120_cen120.txt` (R1 658.8 ± 9.1; d16 621.7; w4 540.7; no-E 630.4;
  t_hit 19.2; t_miss 539; ≈ 1 259 would-hits; R2 435.2/1 067.6/−36.8; R 1 093.9 ± 15.0; A 340.2/686.9; B −8.1/177.9;
  SP 332.1/864.9; price +2 766 ± 138; 38 pairs; admitted; zeros).
* (а) R1: faithful ("трек скорости R1 … собственный проверочный гейт; отгрузка — только по п. 2(в); «попало бы» —
  потолок"). **Deviation:** "или прямая 16 К, если прототип покажет, что цена пробы съедает разницу" — the sealed
  consequence (pred 01) names "the argmax table shape of R1" = w8; d16 is not supported by the census (§1.3). A switch
  to d16 would need its own recorded decision and its own measurement including the footprint.
* (б) "R2 и пакет SP — записаны NOT_OPENED, повтор не назначается": **allowed in substance** (a rerun is admissible,
  not obligatory), but (i) the rule says it is decided *at the close*, and item 7 is written "до аудита" — premature by
  one step; (ii) the reasons given misstate the numbers: R2 is not "ниже порога" (its upper is 1 067.6, double the
  line; the point is below); A is at a systematic border 468–687, not "limited" in a closing sense; (iii) A as a
  member is folded into "пакет SP", while pred 01 gives each member its own consequence line.
* (в) B exhausted: faithful; should carry the narrow scope of §3.1 ("на потоке GuestGpu").
* Package R OPEN is presented as a result in bold; it has no consequence of its own (§2).
* Missing at the close (due by item 4/design120 §6): the A-walker decision (§6 below).

## 5. What the R1 prototype session must do to avoid the known traps

1. **Verify gate against a fresh full resolution, never against the direct memo.** On the gained population (hits
   of the new table that a direct-mapped index would have missed), comparing with the direct memo is vacuous — the
   direct memo has no answer there. Mirror the census's bad check: identify gained hits (a direct-mapped shadow index,
   or the census's tag idiom), run the real miss path, and require `store ∧ id == id′ ∧ digest(desc) == digest′`
   (the full `R1DescDigest` field list, not a memcmp of `ImageDesc`, which has padding); count `*_bad`, log ≤ 40
   `…Mismatch:` lines; the verify arm runs the miss path (FindImage side effects) and is **never a timed arm**.
2. **texfast semantics.** `memo_index` must stay `< TextureSlots` and address the `Texture` entry of the way
   (`set·8 + way`); `version++` and `fast_view = nullptr` must happen on every store into a way, including a victim
   eviction, so that `RebindImages` eligibility (`slot->valid ∧ slot->version == binding.memo_version ∧
   slot->image_id == binding.image_id`, descriptors.cpp ~3600) and the shadowresolve query (~3840) stay correct.
   A would-hit returns the way's own `version` (texfast then keeps its view — that is the R term).
3. **Gate flips across ABBA blocks.** Read the gate once per operation (s97 tear rule). Switching layout (direct
   index ↔ set index) must invalidate the memo (`valid = false`, `version++`) and hence all recorded `fast_view`s; any
   `PreparedBindings`/draw-ahead state carrying a `memo_index`/`memo_version` of the other layout must fail
   eligibility by the version bump. Add a control counter for "eligible under a stale layout" that must read 0.
4. **texmemo2.** It already is a 2-way LRU over the same 4 096 entries (`MemoTextureWay`, `texture_ways` with a 64-bit
   hash + `use` = 16 B/way) bundled with the `MemoResourceKey` cache (1 024 × 80 B, rejected by PLAN_82 as "more memory
   work than the hash"; s56 measured the bundle "0 %" by the since-withdrawn inter-run method). Do not reuse the
   bundle: keep the XXH3 resource key, use compact 32-bit tags + `use` in one 64-B line per 8-way set (the layout
   whose probe the census priced; the `TextureWay` layout would be 2 lines/set), make the new gate mutually exclusive
   with `texmemo2` (both write `texture_ways`/clocks), keep `texmemo2=0` pinned and asserted. Note `r1cen`/`r2cen`
   force themselves off under `texmemo2` — reusing that flag silences the censuses.
5. **GC / freed images / longer residency.** Entries hold `ImageId` (index + generation), not a pin; `try_get` catches
   freed and reused slots. Longer residency raises `texmemo_stale` and the exposure named at the memo comment ("an
   overlap view could be superseded by a later exact image") — exactly what the verify gate must catch; report
   `texmemo_stale` per arm. The hit tail does `TouchImage`/`tick_accessed_last` like the miss path, so GC order should
   not move; the DCC adoption is conditional on the hit path and unconditional on the miss path (the "black cutscene
   frames" history) — the video check is mandatory, and a verify counter on adoption outcome is cheap insurance.
6. **Measure without any census.** The census price in P was +2.77 ms; timed arms: `r1cen=0 r2cen=0 spcen=0`, clock
   pin, window 10–88, NEW BDA regime reported, no agents during the run.
7. **Arming proofs** (as s74 `da_cl_drop`): `tex_hits` +≈ 1 259/frame, `texmemo_collide` −≈ 1 259, `texfast_rec`
   down by ≈ the w8 `rb` count, the new table's own `hit_gained` counter > 0 only in the armed arm.
8. **Pre-register the prediction and power** (§1.4): central ≈ 0.35 ms, range 0.25–0.50; a null result means the
   ceiling was loose, and the ceiling's decomposition (§1.2) says where.
9. **Do not pivot to d16** without a recorded decision and a measured footprint.

## 6. The A-walker debt (s119 item 5) — recommendation

**Recommendation: decide it at this close as "not scheduled — parked, not refuted", with written reopen triggers;
do not open it as a live track and do not build its kill-test instrument now.**

Reasons:
1. **Its margin is small and both kill conditions lean against it.** Walker-G₂ = 3 484.7 µs against a 3 000 bar
   (≈ 3.5–3.6 ms at the corrected 10–88 window [I]) leaves ≈ 0.5 ms for two unmeasured costs that the s119 audit
   itself calls adverse: (i) the residual plan intake on GuestGpu must be ≤ 485 µs — with ≈ 5 000 draws+dispatches a
   frame that is ≈ 97 ns per operation, about one cross-core cache-line transfer, while a plan must carry register
   deltas for each element; (ii) the tax of a WRITING second context must be ≤ 1 645 µs, the measured tax of a
   READING shadow thread — a writing context does the same reads plus stores and a larger footprint, so its tax is
   expected ≥ the reading one. The joint condition is really `intake + (write tax − 1 645) ≤ 485`.
2. **Cost/benefit versus the open alternatives.** Its kill test needs a writing-context instrument (a large part of
   route A stage 3) and an off-thread spine; the full route is stages 3–6, the largest and riskiest code in the
   programme, for a ceiling that is itself partly [I]. The R1 track (≈ 0.35 ms expected, cheap, one gate) and the
   s121 scene map (which can change where any effort should go) are both cheaper and more informative now.
3. **Rules.** The debt is not a sealed consequence, so parking it sets nothing aside; the s119 sealed closure (A in
   the spine-on-GuestGpu model) stays as is.

Reopen triggers to record with the decision (before any action): (a) the s121 map finds a CPU-bound scene where the
recomputed walker-G₂ ≥ 4.5 ms (a margin ≥ 1.5 ms that absorbs an intake of a few lines per operation and a writing tax
~1.3× the reading one) [threshold is my proposal]; or (b) the GuestGpu micro-tracks are exhausted and no candidate
≥ 0.5 ms remains. If it is ever reopened, the first step is the cheapest measured lower bound — an offline
producer/consumer benchmark of plan intake with the spine's measured per-element plan sizes (no game run): a lower
bound above 485 µs kills it without building the writing context.

## 7. Findings

### MAJOR

* **MAJOR 1 — R1 OPEN holds, but only narrowly as a ceiling.** `C_R1` = 658.8 is an upper bound in direction; the
  unpriced terms of known sign (hot `t_hit` — lower bound −40 µs from the census's own `warm_ns`; cold-slot emit;
  E's census pollution −28; P-arm pollution of `t_T`; R2 warming of memo lines; under-priced probe/LRU writes; R as
  an upper) put the honest net ceiling at ≈ 0.33–0.62 ms, central ≈ 0.5 ms, and the realizable gain at ≈ 0.25–0.50
  ms. The close and the prototype's pre-registration must carry this range and the ABBA power (§1.4), not 658.8 or
  "half of 658.8" alone.
* **MAJOR 2 — item 7(б) turns two systematic borders into quasi-closures.** R2 (point 435, upper 1 068) is called
  "below the threshold" and A (add-back point 468, upper 687) "limited by its own check"; both are NOT_OPENED with a
  systematic spread that no rerun can resolve. The sealed consequence grants neither closure nor a new instrument;
  the close should record them as "parked by the rule, not exhausted; a rerun cannot resolve; any other follow-up is
  a new recorded decision", with the numbers of §3.2–3.3.

### MINOR

* **MINOR 1 — d16 as a fallback (item 7(а)) is unsupported and departs from "the argmax table shape".** d16 has
  fewer would-hits and no footprint term (10.6 MB vs 2.7 MB); a 1-ns/hit penalty erases the 37-µs gap.
* **MINOR 2 — package R OPEN is vacuous and its 1 093.9 mixes a measured term with play constants.** It should be
  recorded as subsumed by R1 OPEN and not quoted as a track ceiling.
* **MINOR 3 — "повтор не назначается" is recorded before the audit** while the rule places the decision at the close;
  harmless in substance (the decision is right), wrong in order. A as a member is folded into "пакет SP".
* **MINOR 4 — B's exhausted scope should be written narrowly** (GuestGpu CPU, Sky Garden, standalone; GPU-side
  barrier cost and other scenes not covered).
* **MINOR 5 — the level-1 pollution check the R1 review recommended was never run** (smoke used the sealed schedule),
  so P-arm pollution of `t_T`/`t_hit` is ungauged; it is one of the looseness terms of MAJOR 1.
* **MINOR 6 (seal hygiene, outside this lens but seen)** — `SEALS120.txt` notes that `enter_scene.py` was edited
  after `seal120.py` ran and re-hashed before the run; behaviour-neutral by its own note, but a sealed file changed
  after sealing should be disclosed in the close as such.
