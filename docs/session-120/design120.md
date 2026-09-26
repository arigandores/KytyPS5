# Session 120 — the measurement build: R1 census (`r1cen`), R2 census (`r2cen`), same-pass census (`spcen`)

Lead's synthesis of three designs and three adversarial reviews (all SOUND_WITH_CHANGES), written before any code.
Sources, in `C:/kyty/s120/design/` (git `docs/session-120/design/`): `r1.md` + `r1_review.md`, `r2.md` +
`r2_review.md`, `spcen.md` + `spcen_review.md`. **Each instrument = its design with every REQUIRED change of its review
and the recommendations adopted below; where this file and a design differ, this file wins.** ROADMAP s120 item 2
(threshold 0.5 ms net, packages) is in force. MEASUREMENT ONLY: nothing under `src/graphics/shader/**`, no emulator
decision reads any census state, defaults 0.

## 1. Instruments, tables, order

| instrument | table entry (LAST rows, this order) | values | counters (print order after `sc_ns`) |
|---|---|---|---|
| R1 texture-memo census | `Knob::R1Census` after `Knob::Spine`; `{"KYTY_R1_CENSUS", "r1cen", 0, 2}` after the `spine` row | 0 off, 1 timers, 2 timers + shadow | R1 block first (`r1_*`) |
| R2 stage image-block census | `Knob::R2Census` after `R1Census`; `{"KYTY_R2_CENSUS", "r2cen", 0, 2}` after the `r1cen` row | 0 off, 1 census, 2 census + replay | R2 block second (`r2_*`) |
| same-pass census | `Gate::SamePassCensus` after `Gate::SliceCensus`; `{"KYTY_SAME_PASS_CENSUS", "spcen", false}` after the `slicecen` row | 0/1 | spcen block last (`sp_*`, `pl_em_sp*`, `pl_em_rt_hit*`, `bl_tr_hit*`) |

`Counter` enum entries in `frameStats.h` in the same order before `Count`; `videoOut.cpp` rows in the same order after
`{"sc_ns", …}`, all `micros = false`. The "LAST row" comments move to the new last rows. `check_gate_order.py` (s96)
after the patch and before the build. Every knob/gate is read ONCE per operation into a local (s97 tear rule).

## 2. R1 — `r1.md` + `r1_review.md` RC1–RC11, and these adopted recommendations

Adopted: `alignas(64)` on `Proof`; no `R1Begin` work on key-match lookups (draw `self` inline); `R1CenMismatch` prints
both ids (index/generation) and which desc group differs (info / view / source); `r1_nost`/`r1_nost_ns` (key misses with
`store == false`, information); an owner-thread check in `R1Arm` (a global atomic holding the owner's `&t_r1`; another
thread counts `r1_xthr` and gets `nullptr`; `r1_xthr > 0` ⇒ NOT_EVALUABLE). Not adopted: the offline LRU unit test (the
`w1` null control of RC7 runs the same helpers in-run). Level 1 is a smoke level only.

Net ceiling per table T ∈ {w4, w8, d16} (P arm, window frames; RC2–RC6):
```
t_hit  = Σ r1_hit_ns / Σ r1_hit_t          t_miss = Σ r1_mp_ns / Σ r1_mp (reported)
W_T    = Σ r1_T_q · Σ r1_mn / (Σ r1_mn − Σ r1_mp)        t_T = Σ r1_T_pns / Σ r1_T_p
A_T    = W_T · (t_T − t_hit)
L_T    = Σ r1_T_lose · max(0, min(t_T, t_miss) − t_hit)            (L_d16 = 0)
R_T    = Σ r1_T_rbns − Σ r1_T_rb · t_fast,   t_fast = Σ r1_rbf_ns / Σ r1_rbf_n
E_T    = max(0, t_ham − t_hit) · Σ r1_am_n · W_T / Σ r1_mn,   t_ham = Σ r1_ham_ns / Σ r1_ham_t
P_T    = Σ (r1_hn + r1_mn + r1_sn) · max(0, (Σ r1_T_pb_ns − Σ r1_pb0_ns) / Σ r1_pb_n)   (P_d16 = 0)
C_T    = (A_T − L_T + R_T + E_T − P_T) / N_f / 1000   µs a frame;   C_R1 = max_T C_T  (point = upper)
```
Correctness counters over ALL P rows: Σ `r1_{w4,w8,d16}_bad` > 0 or any `R1CenMismatch:` ⇒ FAIL; Σ `r1_incl` > 0,
any `r1_w1_*` ≠ 0, `r1_xthr` > 0 ⇒ NOT_EVALUABLE.

## 3. R2 — `r2.md` + `r2_review.md` C1–C10, variant C2(b), and these adopted recommendations

**C2(b) is the choice: `r2cen=1` in BOTH arms, `r2cen=2` (the replay) in P only; T\* and every R2 population come from
the M arm** (`r1cen=0`, `spcen=0` there), so R1's in-loop census never touches R2's time and no level factor is used.
Adopted: `constinit thread_local R2Table*` (no `unique_ptr` TLS guard); two `R2Log` budgets (one per tag); T# words of
an entry in one contiguous `std::array<DescriptorValue, 64>` apart from the per-slot metadata; the unreachable
`images.size() != n` exit gets its own counter `r2_odd`; the DCC-lock share of clean slots reported (information, no
formula term); C9 (no 2 KiB value-initialised array: per-slot bits only). Not adopted: moving the knob read after the
loop (C3 needs the pre-loop read).

Ceilings (M arm, window frames; S/Z/L = `r2_cl_sl`/`r2_cl_nul`/`r2_cl_lod`; constants pre-registered: B = 8.49 ns
[M s87], B_lo = 5.0 [I], T′ = 15.00 − 3.0 = 12.0 [M s88 − I], P = 15.08 [M s88], N0 = 2.0 [I], LS = 5.0 [I],
R_reset = 2.0 [I], A_tr = 1.2 [I]):
```
z̄      = Σ r2_nul_ns / Σ r2_nul_n                                      (null stamp pair)
W      = (w̄_rep − z̄)·r2_rep + (w̄_oth − z̄)·(r2_stg − r2_noimg − r2_big − r2_odd − r2_rep)
ST     = (Σ r2_st_ns / Σ r2_st_n − z̄) · (r2_stg − r2_noimg − r2_big − r2_odd − r2_rep)
T*     = (Σ r2_cl_ns over unsampled clean stages) · (S + Z) / (S_u + Z_u)
C_up   = T* − B_lo·(S+Z) + R_reset·(S+Z) − W − ST                                  (traced)
C_pt   = T* − ((B+T′)·S + (B+N0)·Z + LS·L) − W − ST − A_tr·(2S+Z)                  (play)
C_lo   = T* − ((B+T′+P)·S + (B+N0)·Z + LS·L) − W − ST − A_tr·(2S+Z)                (play)
C_rp   = ((Σ r2_rm_ns − z̄·Σ r2_rm_n) / Σ r2_rm_sl) · (S+Z) − W − ST   (P arm replay; information and sanity)
C_ext  = C_pt + r2_mx_eq·(p_c − B − T′)   (per-slot variant, information; if ≥ 500 a CLOSE says "per-slot unmeasured")
```
(all ns → µs a frame once). Sanity (else NOT_EVALUABLE): p_c = T*/(S+Z) in 25–90 ns; C_lo ≤ C_pt ≤ C_up. Correctness
over ALL rows of BOTH arms: Σ(`r2_bad` + `r2_bad_key`) > 0 or any `R2Mismatch*:` line ⇒ FAIL (the memo/texfast
invariant broken — the next session investigates correctness first).

## 4. spcen — `spcen.md` + `spcen_review.md` RC1–RC6, and these adopted recommendations

RC1: `MetaEpoch` is not a cross-thread witness (it moves only on GuestGpu or under the render mutex): a move inside the
window is bad bit M (A `0x80`, B `0x10`); the A race is decided at the slow-path entry (`t_sp_rt_stamp_race`); no
`sp_tr_race` counter. RC2: no census path calls `GetImage`/`TouchImage` — **all census image reads use
`m_slot_images.try_get`** (nullptr ⇒ a miss reason, never `operator[]`, which can `EXIT`). RC3: B slot identity carries
`metadata.kind` and `metadata.range.address` (flags widened to `uint16_t`). Adopted recommendations: F7 — the A Live
reason restates the full rtfast predicate (`fast.meta_epoch`, `source_size`, `source_first_level`, depth
`htile_clear_mask`, `view_info`) AND every memo is invalidated on an unarmed draw when `m_sp != nullptr`; F8 — `SpRtPost`
re-looks up targets with `try_get` (nullptr ⇒ bit I); on P2 the pending memo is invalidated and P2 is bad only when
`pass_before == sp.rt.pass_serial` (other restarts are `sp_rt_rst`); B slot identity includes `binding.image_view` for
`is_target && IsDepth()` slots; §5.3 lists `depth_load_clear_enable = false`; the text states the `VulkanImage`
104 → 112 B growth (both arms).

Ceilings (window frames, per frame; RC5):
```
N_A = pl_em_rt_hit_ns − pl_em_spchk_ns − sp_rt_rep_ns − sp_rt_rec_ns        (P)
N_B = bl_tr_hit_ns   − sp_tr_chk_ns   − sp_tr_rep_ns − sp_tr_rec_ns         (P)
N   = N_A + N_B                                                             (point; leans low)
Δ_A = max(0, pl_em_rt_ns(M) − pl_em_rt_ns(P));   Δ_B = max(0, 1000·(bl_tr_us(M) − bl_tr_us(P)))
N⁺  = N + Δ_A·pl_em_rt_hit_ns/pl_em_rt_ns + Δ_B·bl_tr_hit_ns/sp_tr_loop_ns (upper)
```
**Timer-read add-back (review of the spcen code, BLOCKING; recorded before the scorer is sealed; this block REPLACES
the `N⁺` line above).** Every census span pays one `NowNs` read latency z that a real memo never pays, so N counts
the census's own reads as memo cost. Per frame (P arm) the subtracted spans carry: `pl_em_spchk_ns` one per armed
draw (the extra `PathLap` mark after the check, `renderDraw.cpp` S9 `MarkSplit(PathEmSpChkNs, …)`), `sp_rt_rec_ns`
one pair per armed draw (`SpRtPost` `rec0`) plus one per pin (`SpRtAfterBegin`, counted by `sp_rt_rec`),
`sp_rt_rep_ns` one per would-hit; `sp_tr_chk_ns` one per stage (the pre-check `cb_lap(cb_transit)` to the check-end
`NowNs`), `sp_tr_rec_ns` one per stage (`SpTrPost` `rec0`), `sp_tr_rep_ns` one per would-hit. The gross terms
`pl_em_rt_hit_ns` and `bl_tr_hit_ns` carry one per would-hit, which cancels the replay's. Net bias of N:
−z·(2·`sp_rt_n` + `sp_rt_rec` + 2·`sp_tr_n`), ≈ 0.15–0.3 ms a frame. The pre-check lap also adds one read per armed
stage to `bl_tr_us(P)`, pulling Δ_B toward 0. So:
```
z̄    = Σ r2_nul_ns / Σ r2_nul_n       (P arm, window frames: r2cen=2 in P, R2PreLoop's two back-to-back NowNs on
                                        the GuestGpu thread; Σ r2_nul_n = 0 or z̄ ≤ 0 ⇒ NOT_EVALUABLE)
Z    = z̄·(2·sp_rt_n + sp_rt_rec + 2·sp_tr_n)                                (P; the census's own reads)
Δ_B′ = max(0, 1000·(bl_tr_us(M) − bl_tr_us(P)) + z̄·sp_tr_n(P))
N⁺   = N + Z + Δ_A·pl_em_rt_hit_ns/pl_em_rt_ns + Δ_B′·bl_tr_hit_ns/sp_tr_loop_ns           (upper; CLOSED uses it)
```
N stays the lean-low point (OPEN uses N, never the add-back). The scorer reports z̄, Z and Δ_B′ next to N and N⁺, and
the suite carries a mutant that drops Z (and one that uses Δ_B for Δ_B′): a fixture whose N + Δ-terms < 500 but N⁺ ≥
500 must not give CLOSED. The code alternative (an spcen-owned null pair `sp_nul_ns`/`sp_nul_n`) is NOT taken: r2cen
is armed in both arms (§3) and `r2_nul` already is an in-run pair on the same thread, so the build does not change.
**Row skew (review, BLOCKING):** `FrameTrace-x` reads every counter separately (`FS::Read`, one registry sum per
counter in print order) while GuestGpu keeps adding, so one draw's or stage's Adds can split across adjacent lines.
spcen's partitions and nestings (`spcen.md` §11 fixtures 4, 5) are tested on WINDOW sums (frames 10–88 of each
block): counts within ±2 per block window (±1 per window edge), ns nestings within the subset counter's own values
on the two edge lines of that window (a straddling event's span is at most the line it lands in); a ±1 skew between
adjacent lines that cancels over the window is ADMITTED, a persistent off-by-one (e.g. the reason index shifted)
FAILs. Never exact per frame.
Correctness over ALL P rows: Σ(`sp_rt_bad` + `sp_tr_bad`) > 0 or any `SpRtMismatch:`/`SpTrMismatch:` ⇒ FAIL;
`sp_rt_race` > 10⁻⁴·`sp_rt_would` ⇒ NOT_EVALUABLE; M-arm zeros required on window frames only (RC6).

## 5. The run (one build, one sealed run)

* Build `<sha>` from one commit carrying all three; pinned copy `C:/kyty/s120/kyty_emulator_<sha8>.exe`; installed by the
  chain; after the session `d3a981a2` is reinstalled (the defaults do not move, but the installed build is the
  program's reference).
* Unsealed smoke (disclosed): Sky Garden 180 s, the sealed schedule; purpose: every counter alive, identities close, no
  bad, no crash. Defects found go into a code fix before the seal, recorded.
* Sealed run `cen120`: Sky Garden, one attempt, 300 s hold, `KYTY_GPU_CLOCK_PIN=1`, `KYTY_GPU_MARKERS=0`, gates
  `gates_base.txt` (sha `303a7849…`), `KYTY_GATE_SCHEDULE=90+1800:<P>|<M>`, `KYTY_GATE_SCHEDULE_ABBA=1`:
  * **P** = `r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1`
  * **M** = `r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1`
  Absent from base and never named: `bindwit bindalt blmove bindfloor cbmove slicecen spine` (all 0) and `bindpack`
  (default 1); base pins `texmemo2=0 texfastcheck=0 m4baton=0 fslean=0`. The scorers assert all of it from the texts.
  One repeat `cen120r` allowed only on NOT_ADMITTED (admission, not verdict).
* Scorers (two, each sealed with fixtures + mutants, `mutlib` v4.1 FULL): `rpk120.py` (R1, R2, the image-resolve package)
  and `spc120.py` (spcen A, B, their package). Common admission as `spk118.py`: installed sha, `GateArm:` texts,
  estimator window frames 10–88 of every block (also in these derived scorers), `draws > 3000`, ≥ 30 ABBA pairs,
  STREAMS_COMPLETE, no `AsyncPipelines: skipped draw` in the window, BDA regime by `bda_scan` reported; 2SE from per-pair
  values. The P−M price of all instruments (`dt_us`, `cpu_gpu_us`) is reported, never a verdict input.

## 6. Verdict (per package; each member reported alone with the same rule, naming which carries a package)

Packages (ROADMAP s120 item 2(б)): **R = R1 + R2** (disjoint: R1 = key misses + the first re-record of their fills,
R2 = memo-hit slots of clean repeating blocks; the sum under-states the package — conservative; R3/R5 are inside R2's
removable part and are never added), with `R_pt = C_R1 + C_R2,pt`, `R_up = C_R1 + C_R2,up`, 2SE of per-pair sums;
**SP = A + B**, `SP_pt = N`, `SP_up = N⁺`.

* **FAIL** — any correctness counter of the package's members, as §2–§4: the mechanism is unsound as designed; a
  nonzero R1 or R2 bad also says the EXISTING memo may return a stale answer — the next session starts there.
* **NOT_EVALUABLE** — any admission, identity, sampler, control or sanity check of §2–§4 fails.
* **OPEN** — `X_pt ≥ 500 µs` a frame (net, measured): a speed track opens for the carrying member(s); the prototype has
  its own verify gate and ships only by ROADMAP s120 item 2(в) (sealed ABBA gain with the 2SE interval below 0, verify
  0 mismatches, video without glitches).
* **CLOSED** — `X_up + 2SE < 500 µs`: that path is recorded exhausted on Sky Garden at the 0.5 ms rule.
* **NOT_OPENED** — otherwise (border): recorded; the only admissible follow-up is a rerun, decided at the close.

A would-hit is a ceiling, not a speed-up. The A-walker debt (s119 item 5) is decided at this session's close.
