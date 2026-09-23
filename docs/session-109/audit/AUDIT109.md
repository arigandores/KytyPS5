# AUDIT109 — adversarial audit of session 109 (RECOUNT · PROTOCOL · CODE)

Independent parsers only (`audit109/parse_log.py` streams the raw `log_<tag>.txt`; no session scorer imported). Scripts
and outputs: `C:/kyty/s109/audit109/` (`recount_ent.py`, `recount_frm.py`, `allfields.py`, `rp_reasons.py`,
`load_phase.py`, `protocol_checks.py`, `mtime_scan.py`, `newmut.py`, `*.txt`). Nothing built, run or edited outside it.

## Verdicts
- **RECOUNT — CONFIRMED.** Every claimed number reproduces exactly (table). The ent109b FAIL is rule-robust but only
  moderately significant, and the count does not show harm (MAJOR-2). gpu_busy "cause [U]" is answerable (MAJOR-3).
- **PROTOCOL — HOLDS, with reporting and fixture defects.** Records precede actions, seals precede runs, all hashes match,
  pin on all 18 runs, nothing wrote under `C:/kyty` or the game folder during any sealed window. pred/04 predictions
  were never scored and are misreported (MAJOR-1). frm109 is a legitimate measurement, not rule-shopping, provided
  it is never used as ship evidence (MINOR-4).
- **CODE — NOT REFUTED.** No data race, wrong-id path or first-contact hole found in `cspfree`; four MINOR items (6–9).

## Recount (own parsers)
| run | claim | recount |
|---|---|---|
| ent109 | FAIL, S_A 12, S_B 34; A 2/2/4/4, B 9/7/9/9 | identical; new A 5 / B 32, wait A 7 / B 2; 4 935–5 000 contiguous rows/entry, 0 missing fields; exact one-sided p (binomial on 46 events) 0.0008 |
| ent109b | FAIL, S_A 7, S_B 17; new 4/5, wait 3/12 | identical (A 3/2/1/1, B 3/5/3/6); p: binomial 0.032 (two-sided 0.064), entry permutation 3/70 = 0.043, pooled with ent109-A (19/8 entries vs 17/4) 0.058 (binomial) / 0.038 (495-split permutation); waits alone 0.018 |
| vfy109 | GO; bad 0, moved 0, hit 1.0000 (n≥2100), cspf_new 76 | identical: 2 055 914/2 055 914; identities look = hit+src_miss+spec_miss+mat_fail and look = have+new hold exactly (2 572 064); sync 1+2 |
| frm109 | ADMITTED, 96 pairs; Δdt −154.1 (2SE 121.2, t −2.54); Δcpu_net −54.8; da_walk −36.1; gpu_busy +70.6 (t 4.63); hit 266, have 0 | identical. Δdt: sign-flip p 0.012, bootstrap95 [−270, −36], Wilcoxon p 0.004, 63/96 pairs < 0 (sign p 0.003), 10 %-trimmed −175, **median pair −16**, drop 5 most negative → −94. cs_sync_* = 0 in both arms, all rows (SYNC_COMPILE has no exposure with precache on) |
| frm109 vblank histogram (kept rows, 2 784/arm) | — | 1 vbl 13.11 % → 14.26 %, 2 vbl 86.53 % → 85.17 %, 3 vbl 0.36 % → 0.57 %: the whole Δ is +32 one-vblank flips (−191 µs) partly paid back by +6 three-vblank flips (+36) |
| fam108 (s108) | Δdt −141.8, gpu_busy +87.5 t 4.5 | −141.8; +87.5 (t 4.54), same histogram signature (13.25 → 13.97 % one-vblank) |

## Findings
**MAJOR-1 (protocol/reporting) — pred/04's own predictions were never evaluated; ROADMAP item 8 cites the wrong set.**
`frm109.py` is `frf109.py` with four literals changed (verified by diff), so it scores pred/03's G1–G6. pred/04 §4
seals M1–M4. Scored by hand: M1 HIT (−154.1 ∈ [−250, −30]), M2 HIT, M3 HIT (266.0), **M4 MISS (Δda_walk_us −36.1,
2SE 13.4, vs ≤ −100)**. Item 8 (uncommitted ROADMAP) says "G1–G6 HIT" — predictions of a run that never happened —
and omits the miss. The miss is informative: the walker saves only 36 µs; the −154 µs is GuestGpu's contention wait,
not walker time. Correction: replace "G1–G6 HIT" with "M1–M3 HIT, M4 MISS (−36.1)"; derived scorers must print the
predictions of the seal they pin. The other seals' predictions are published nowhere either (ROADMAP §0.1 items
3/6 carry none); scored here: pred/01 E1 HIT (12), **E2 MISS**, E3 HIT (clr 146–153, skip ≥ 1.27 M), E4 HIT
(276 vs 303, −8.9 %); pred/01b V1–V5 HIT (sync 3); pred/02 E1 HIT (7), **E2 MISS**, E3 HIT (303 vs 304), E4 HIT.

**MAJOR-2 (recount/interpretation) — the ent109b FAIL is correct by the rule but the rule counts events, not harm.**
(a) Evidence for the [I] hypothesis, not proof: after load (frame ≥ level+30) every wait sits in a flip where the
walker queued a new pipeline (`cspf_new`); P(wait | such flip) = B 6/14 vs A 1/17 (ent109b, Fisher one-sided p 0.021;
pooled with ent109-A 4/32, p 0.031); new permutations themselves are equal (B 16 vs A 18; whole-run 303 vs 304).
Same direction in frm109: da_late +0.4/flip (t 2.37), da_queue_us +14 (t 3.9) — GuestGpu reaches helper-produced
work earlier. The walker's extra cost on a miss is one µs-scale unlocked materialization, so "walker later" is
implausible; "GuestGpu earlier" fits. Direct timing is unavailable: the `AsyncCompute: … queued` budget
(`pipelineCache.cpp:5342-5343`, 2 048 calls) is spent only by locked calls, so arm A stops logging by flip ≈ 44 while
arm B logs the load — no cross-arm comparison is possible from these logs. (b) Harm: B's post-load waits cost +16.7 ms
in 3/6 flips (vs the median of the 10 flips before); new-pipeline flips *without* a wait cost as much in both arms
(A mean +14.0 ms, up to +75 ms; B +20.7 ms; not translation — 0 `Shaders:` lines in any stdout — so the hitch is the
scene event, not the wait). Per new-pipeline flip: A 13.2 ms vs B 15.3 ms extra — no demonstrated duration penalty. (c) Precision of item 6: B's excess is split evenly (load-phase waits B 6 / A 2;
post-load B 6 / A 1, up to frame 1 091), not "mostly at load". Keep the FAIL (the rule is the rule); record p ≈ 0.03–0.06.

**MAJOR-3 (recount) — gpu_busy_us +70.6 is real extra GPU work with an identifiable source; "[U]" should be [I].**
Paired deltas over all counters (`allfields.txt`, `rp_reasons.txt`), same sign in frm109 and fam108: render-pass
`end_buf_upload` / `restart_buf_upload` +1.73 (t 6.2) / +2.99 (t 11.2) per flip — the only moving pass reasons;
`sync_up_kb` +252 / +276 KiB (t 9.2 / 8.7), `sync_ups` +2.3 / +3.7, `stg_pool_b` +252 / +271 KB, `pb_refault` +3.4 /
+4.5, `fw_refault` +3.1 / +4.2, `prot_ro_pages` +58 / +60; draws (+1.2 ± 14.5), dispatches, img_up_kb flat.
Independent of Kyty's timestamps: nvidia-smi (`gpuclk_frm109.csv`, blocks aligned via `stable_s`) shows utilization
+0.42…+0.58 pp (t 3.2–4.2) and board power +0.15…+0.22 W (t 3.6–4.5) in arm 1 at 0…+1 s alignment, SM clock flat
(|t| < 1.2); the signal vanishes at −2 s misalignment. Mechanism [I]: GuestGpu, freed from the walker's lock, reaches
draws while the guest is still writing their buffers (refaults up), so ~2 more buffer uploads per flip land inside a
render pass and split it (store + reload of 4K attachments). Not a timestamp artefact. It is a GPU cost that grows
with CPU speed; harmless while GPU busy is 12.5 of 31 ms.

**MINOR-4 (protocol) — frm109 is legitimate, with one guard owed.** Recorded (item 7, `ee686cc` 23:15:30) before the
run (23:15:34), nothing ships, default unchanged, scorer byte-derived. But item 7 and pred/04 are one commit (pred/04
mtime 23:13:27), so "recorded before this text" is not evidenced; the chain log carries "VERDICT: SHIP_PENDING_VIDEO".
Owed: a ROADMAP line that any `cspfree` ship needs a fresh sealed frame-time ABBA of the guarded build — frm109 only sizes.
**MINOR-5 (scorers/fixtures)** 30 new mutants (`newmut.py`/`newmut.txt`; all 4 suites re-run ALL OK first):
**10 survive.** ent109.py (ent109b.py shares the code): PIN_ONCE counts only `mode 1` lines (a stray `mode 2` passes);
removing `fatal` from MARKERS survives (`--- Fatal Error ---` contains no other token); GATES_ARM tail vs substring;
ATTEMPT hold at 80 % instead of 95 %; ORDER with duplicate stamps; PRECACHE first vs last line. frm109.py: keep window
shifted by one (59..87), `pstdev` SE, mean instead of median levels, `GpuWaitSlow:` dropped from FATAL. None changes a
session verdict (checked by hand: one pin line each, no markers in log or stdout — stdout holds only 16 identical
`0xe06d7363` C++-throw lines per run in every arm — hold ≥ 150.0 s, distinct increasing stamps, all 18 gate texts =
`gates_base.txt` (303a7849…) + token), but the fixture claims "every term has its own failing fixture" overstate.
ent/vfy scorers also read markers from `_kyty` only, not `stdout_<tag>.txt` where VEH prints.
**MINOR-6 (code, perf-only) — TOCTOU.** `Restamp` (5251) precedes `MaterializeUnlocked` (5263); a drop by GuestGpu in
between (3498) yields a hit on the retired source's old id and skips a prefetch the dispatch then compiles
synchronously. Memory-safe (`retired_sources` never cleared, 4307). Re-check the mirror after the materialization.
**MINOR-7 (code) — verify can hide a disagreement.** Mode 2 counts `moved` when `FreeSourceFor` returns nullptr after a
hit with a different id (5298-5302); count it separately.
**MINOR-8 (code, latent).** The `thread_local` memo keeps raw `const SourceEntry*` of one `ProgramCache` while its
stamps are process-global; safe only while one `PipelineCache` lives per process (true today). `GetCompiledSrt`
(SrtWalker.cpp:1812-1823) is an unsynchronized lazy `shared_ptr` init: every unlocked caller must keep the
`srt_compiled != nullptr` precondition (4196; M1's is 2548).
**MINOR-9 (code) — logging budget** (see MAJOR-2a) makes `AsyncCompute:` lines arm-dependent.

## Code review notes (what was checked, no defect)
Unlocked `MaterializeResources` touches: the plan (immutable after insert; `srt_compiled` written once, only
under `m_mutex` for compute, never reset), `thread_local` scratch (SrtWalker.cpp:2202-2221,
ResourceMaterialization.cpp:320), per-thread `PersistentLive/Clean` tables (pipelineCache.cpp:523-556), a per-call
`ShaderReadCache`, per-thread FrameStats shards, `std::call_once` native code (off unless `KYTY_SRT_NATIVE=1`). The
walker is not the GPU thread, so `IsGpuCleanRange` fails (memory.cpp:1031-1037) identically in both paths. Memo key =
Get's `lookup_key` fields built from the same by-value `input_info` before Get (3286-3290); ids stored are exactly
those Get returned at cursor 0; permutations are an append-only deque (1971); drop moves `programs_epoch`;
`m_compute_pipelines` is erased only in the destructor (4349) ⇒ a hit implies the locked path would have been "have"
⇒ no skipped first contact (empirically: equal `cspf_new`, bad/moved 0 on 2.06 M). v2 (`bc7d66f`) bumps the creation
count at all three emplace sites (5365, 5449, 6119); closed as designed.
