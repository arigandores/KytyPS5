# Session 94 — FACTS

**The single source of truth for this session's numbers is `C:/kyty/s94/FACTS.md`**, of which this
file is the record in git. `pred/01_mergecost.md` and `pred/02_bdaall.md` are sealed in place in
`C:/kyty/s94/pred/` and were not edited. `README.md` and `PLAN.md` in `C:/kyty/s94` are this
session's own (the carried session-91 texts were replaced).

Binary under test: **`4338ba1a300a17be170167a4291748f8a93ad282f4c1c27a4c93084752386b4e`**,
**23 642 624 B**, commit **`4912ae5`** (sources, committed before the first launch), installed by the
harness for both runs and not rebuilt afterwards. Harness `C:/kyty/s94`, ported from `C:/kyty/s93`
by `C:/kyty/s93/s94_port.py`, written fresh in the SOURCE directory; port diagnostic clean;
`gates_base.txt` **UNCHANGED** — 1092 B, 99 names, sha256 `00c116dc…0594d8`.

**Two gates, 49 counters, both gates default 0. NO default moved. NOTHING SHIPPED.**
Two runs, both **VALID**, both with **`KYTY_GPU_CLOCK_PIN=1`**:
`mc94a` (`mergecost=0|1`) and `bda94a` (`bdaall=0|1`).
Pre-registrations sealed in place before the emulator was opened, never edited:
`pred/01_mergecost.md` (9 972 B, sha256 `1cff373f…`, `mtime − ctime` +0.003 s) and
`pred/02_bdaall.md` (5 314 B, sha256 `7560a476…`, +0.000 s).

Labels: **[M]** measured in this session (ratio of sums over n ≥ 2100, blk ≥ 1, or a paired ABBA
mean); **[R]** read in the source; **[I]** inference. Endpoints are `endpoint84.py`'s (sample SD);
the scorers' `s94lib.paired` uses the population SD and prints slightly larger t.

**This text was rewritten after an independent audit (4 auditors, `read94/audit.*.md`): every
number reproduced from the logs; the defects were in the text — listed in §0.2.**

---

## 0. In one sentence

**Session 93's LICENSED does not survive measurement. The only thing moving V# slots onto BDA
enables — reusing the previous draw's descriptor set — removes at most 197.3 µs a flip (everything
after the class point of every draw whose set could be reused), not the 5 646.0 µs assumed [U]; the
gross ceiling is 1 198.6 µs, CLOSED by the table sealed in session 93. And the naive way of doing it
(PrepareBda wherever a slot converts) COSTS +10 807.8 µs a flip of GuestGpu CPU in the regime every
launch of this binary ran in.** The "at most" rests on one [R] premise: the 4.37 µs a draw that
precede the class point survive any merge (§2.3).

## 0.1 Defects of my own text and tools

1. **The brief asked for the predicted number "before the patch"; it was sealed after.** The
   instrument was built and then changed by an independent review before sealing
   (`patch_s94b.py`). No number from it existed when `pred/01` was sealed — the emulator had not
   been launched — and `pred/01` §0 says so.
2. **R5 missed.** `pred/01` R5 said `mc_p_ok / mc_ok` ≤ 0.45 ("more than half of s93's population
   cannot reuse the set"); it read **0.4835**. I wrote 0.45 from a reading that ≥ 51.6 % of
   `dm_buf1_nr` also differ in a ring slot — but that is not a bound on P, because the census masks a
   convertible slot even when the ring serves it (`mc_mask_x` 1 828.8 a flip). The band was built on
   an argument that did not apply.
3. **The dry run caught my scorer repeating session 93's defect — AFTER sealing, not before.**
   `mc94.py` decided "bdacap fired in the unarmed arm" from `bc_ok > 0`, which a straddle makes true
   (1.09 a flip in `bl93a`'s unarmed arm); and bands on counters that never fired printed a vacuous
   HIT at 0.0. Both were repaired (`fix_scorers94.py`, `fix_scorers94b.py`) **3–4 minutes after the
   pre-registrations were sealed** (17:24:44 / 17:25:09 → 17:28:15–17:28:42), before the commit
   (17:30:02) and before the first launch (17:30:15) — so blind to the data, but the first draft of
   this file said "before sealing", which was false. The scorers themselves were written after
   sealing, since they embed the sealed sha256.
4. **B8 missed, and it was a defect of my text, not the world surprising me.** I predicted the BDA
   regime of `bl93a` (NEW). The record already held OLD launches of the same scene (`stg92a`,
   `wak92a_warmup`) and `pred/02` §0 itself cites the variation. All four launches of this session
   were OLD (§3.4).
5. **Two procedural deviations from `pred/02` §3, neither changing an outcome:** the regime check
   uses the **mean** of `buf_new` where the sealed text said medians (OLD by either: median 1.0,
   `bda_scan` median 1 068); and the regime was printed by the scorer AFTER `accept94.sh` had
   already printed the contrasts (steps 2–4), not "before any contrast is read".
6. **R7/R8 were scored on the unarmed arm**, while `pred/01` §6's heading says "armed arm". In the
   armed arm they read 1 622.0 µs and 0.0560 — both HIT either way.

## 0.2 What the audit corrected in the first draft of this file

The counter count (53 → **49**); the scorer-repair timing (0.1.3); the claim that "exactly the
ring-free half of s93's population can reuse the set and the other half never can" (retracted —
426.0 vs 426.3 is two differently defined counters agreeing, their intersection was never counted);
"87 % of what a draw costs on GuestGpu" (it is 86.8 % of the timed bracket, 64.6–68.0 % of
`cpu_gpu_us / draws`); the survival share (a borrowed denominator — §2.3); "ring entries are 74.8 %
of not-P" (74.8 % of ALL commits; **85.8 % of not-P**); "94 % of ring slots are const-bank copies
(s93)" (this session's own [I] lower bound, ≥ 93.9 %, across two partitions); **"the ring-backed
cb half cannot be reached through the table" (wrong — its bytes are guest memory, §4)**; "costs 2–6 %
GPU" (two shaders on a bench, not a frame); the dynamic-offset closure argued from an irrelevant
population; the regime "from the first frame" and "a launch state" (§3.4); the regime qualifier
missing from the headline; `bda_all_n` "+ 213.9 dispatch" (the dispatches are INSIDE 5 042.2); the
bdaall mechanism sentence (it pointed at re-uploaded bytes; the cost is re-protection — §3.2);
"+12.7 ms on guest threads" (all threads); the fault-buffer pass "15.8 µs" (CPU only); the
scoreboard counting scorer rows instead of sealed items; unreported guard warnings; last-digit
double rounding (1 658.3, 549.8, 961.8).

---

## 1. The instrument (`patch_s94.py` + `patch_s94b.py`, reviewed before any run)

**Gate `mergecost`** (`KYTY_MERGE_COST`). A draw is armed when the gate was on at its entry. Its
**pre-class** time runs from right after the render mutex to just before `NoteDrawMerge`; its
**post-class** time from just after `NoteDrawMerge` to the exit of `ExecutePreparedDraw`, minus the
census's own time (both census costs are outside both intervals; the `cb_timed` laps the gate adds
are inside post, ~30 ns a draw). After `CommitBindings` is timed (transitions `mc_tr`, write list
`mc_wr`, emit `mc_em`), a **post-conversion signature** is built from the writes: every
**statically convertible** buffer slot (not texel, not const-bank, not written, not atomic —
`BdaConvertible`; the backend rejects writable FLAT/GLOBAL addresses, `SpirvEmitter.cpp:312-313`, a
missing feature rather than an impossibility) is masked; everything else is kept, plus the layout
DEFINITION (stages, kinds, counts, push-descriptor flag, push stages — one `VkPipelineLayout` exists
per pipeline, so its handle would have meant "same pipeline"). **P** = same signature as the
previous armed graphics commit AND the same scheduler tick (a new command buffer has no set bound).
A foreign bind within one tick (`blitHelper.cpp:184-187`) is invisible — it can only overcount P,
the conservative direction for CLOSED. Reasons for not-P are counted separately (`mc_d_*`).

**Gate `bdaall`** (`KYTY_BDA_ALL`). `PrepareBda` on every draw and dispatch where no stage has
`uses_dma` but some stage has a convertible slot — exactly where the conversion would set `uses_dma`.
It changes WHEN guest writes are synchronised and therefore which slots take the stream ring.

**Under `bdacap`:** `bc_cb_ns`, `bc_ok_w` / `bc_ok_w_ns`. **In every run:** `fbp_n` / `fbp_ns`.

## 2. `mc94a` — what a merged draw costs

`mergecost=0|1` with `bdacap=1 drawmerge=1 mutsite=1` in both arms, period 30 from 1800, ABBA, pin 1.
**VALID:** split +0.001 %, pairs 115/115, work +0.131 %; 0 hang markers; guards 7 PASS / 0 FAIL /
3 WARN — check 0 (`tabtip.exe` on an idle GPU), check 3b (viewport low mode 5.48 % apart, advisory)
and check 5 ("heavy" 5.44 pp, expected when GuestGpu's speed moves); checks 8/9 SKIP (no video — not
required by the sealed admission). **Controls 7/7 HIT** — among them **C1 = 0.9967**: my stamps
against mutsite's independent chain, Σ(`mc_pre+mc_dm+mc_post+mc_sig`) / Σ(`mh_pro..mh_emit`), band
[0.95, 1.02]; and C2: `mc_p_eq` = 0.00 ≤ `dm_same+dm_push`+0.5. C4 leak: 55 unarmed frames, **all at
distance 29 of 30** (straddle), 4.4·10⁻⁵ of the armed value.

### 2.1 The anatomy of a draw (armed arm, per flip)

| | µs a flip | per draw |
|---|---:|---:|
| `mc_n` draws that reached the class point | 5 027.8 | |
| **pre-class** (mutex → class point) | **21 954.8** | **4.367 µs** |
| post-class (class point → exit) | 3 351.5 | 0.667 µs |
| … of which CommitBindings tr / wr / em | 961.8 / 626.2 / 446.6 | 0.405 µs a commit |
| pre share of the timed bracket (pre + post) | **86.8 %** | |
| pre share of `cpu_gpu_us / draws` (6.418 unarmed / 6.762 armed) | 68.0 % / 64.6 % | |
| NoteDrawMerge (`mc_dm_ns`) | 510.1 | 101.5 ns |
| the signature census (`mc_sig_ns`) | 1 658.3 | 0.330 µs |

**Most of a draw's cost lies before the point where it is known what the draw differs in.** The
pre-class time also carries the bdacap and mutsite stamps (armed in both arms). `mc_pkt` 5 008.3 of
5 027.8 commits take the recpack path: the Vulkan calls are on the record thread.

### 2.2 How many draws could reuse the previous set once the slots are addresses

| | per flip | share of 5 027.8 commits |
|---|---:|---:|
| **P** | **642.3** | **12.78 %** |
| … P on a push-descriptor pipeline (`mc_p_push`) | 642.3 | **100 % of P** |
| … P with the same VkPipeline (`mc_p_pipe`) | 502.3 | 78.2 % of P |
| … P and every masked entry equal too — the set equal TODAY (`mc_p_eq`) | 0.00 | |
| `mc_ok` — armed draws drawmerge classified `dm_buf1_ok` (s93's population) | 881.15 | |
| … of them P (`mc_p_ok`) | **426.0 (48.35 %)** | |

Why not P (a commit may carry several; shares of the 4 385.5 not-P commits): **ring entry 3 761.6
(85.8 %)**, flattened-SRT / shader-data upload 3 505.8 (79.9 %), image 645.1, layout/shape 549.8,
other kept buffer 483.3, command buffer 25.2, sampler 13.3. **Only ring and/or SRT differ: 2 900.8.**
Commits carrying a ring entry: 4 114.2 (81.8 % of all); an SRT/shader-data upload: 3 820.0 (76.0 %).

**No pooled descriptor set is P** — all 642.3 are push-descriptor pipelines — as session 57's
`e9_full` = 0 already said for pooled sets. Just over half of s93's merge population (455.1 a flip)
cannot reuse its set; why, draw by draw, was not recorded.

### 2.3 The verdict, by the rule sealed before the number (`pred/01` §5)

| term | value | status |
|---|---:|---|
| `Ceiling_bind_ro` = `bc_ok_ns` − `bc_ok_w_ns` (unarmed arm) | **1 001.3 µs** | [M] |
| `M_set` = `mc_wr_p_ns` + `mc_em_p_ns` — what reusing the set removes | **48.1 µs** | [M] |
| `M_hi` = `mc_post_p_ns` — EVERYTHING after the class point of every P draw | **197.3 µs** | [M] |
| `M_hi` / s93's `Ceiling_merge` [U] 5 646.0 | **0.0349** | |
| **`Ceiling_total_M`** = `Ceiling_bind_ro` + `M_hi` | **1 198.6 µs ⇒ CLOSED** | gross |
| (with `M_set`: 1 049.4 µs) | | |

**What "at most" means, said precisely.** `M_hi` is generous PER DRAW (it removes the whole tail of a
P draw, even its draw record) but it covers only the draws whose set could be reused — which is the
one thing a BDA conversion enables. It is not the ceiling of every conceivable merge, and it rests on
the [R] premise that the pre-class work survives (each of its blocks has been closed as a lever by
routes A, C and D). The robustness of CLOSED under other readings [M values, I combinations]:

| reading | total µs | table |
|---|---:|---|
| sealed: `Ceiling_bind_ro` + `M_hi` | 1 198.6 | CLOSED |
| + all post-class time of P draws OR s93's population (476.8) | 1 478.1 | CLOSED |
| `bc_ok_ns` with the written slots kept (1 491.8) + `M_hi` | 1 689.1 | CLOSED |
| 1 491.8 + 476.8 | 1 968.6 | CLOSED by 31 µs |
| s93's `Ceiling_bind` 1 552.9 + 476.8 | 2 029.7 | MARGINAL |
| 1 001.3 + ALL post-class time of ALL draws (3 351.5) | 4 352.8 | MARGINAL |

The last row would need every draw's whole emit to vanish, including draws whose sets differ in a
ring or SRT offset — which is route B9 (dynamic offsets), closed in session 59 at 0.3–0.45 ms
(absolute top 650 µs: 1 198.6 + 650 = 1 848.6, CLOSED); this run's own analogue is 2 900.8 ring/SRT-
only commits × 0.213 µs of write+emit ≈ 619 µs [I] → 1 818, CLOSED.

**The survival share.** Against the draw's own measured bracket, `mc_post_pok_ns` / (`mc_pre_ok_ns` +
`mc_post_ok_ns`) = 128.96 / 2 547.2 = 5.06 %, so **≥ ~95 % of a `dm_buf1_ok` draw survives** (a lower
bound, since `mc_post_pok_ns` is all of the post-class time); against `cpu_gpu_us / draws` it is
97.7–97.8 %. Session 93 assumed 0 %.

**`Ceiling_bind` fell by a third on a population nobody had counted:** of `bc_ok_ns` 1 491.8 µs (this
run's unarmed arm; s93 read 1 552.9 on another binary), **490.5 µs belong to the 1 001.7 bc_ok slots
a flip that are WRITTEN or atomic — 5.6 % of the slots at 0.490 µs each**, against 59.3 ns for a
read-only one. On this backend a written slot cannot move onto BDA (no store path), so s93's ceiling
counted about a third of its value on slots that cannot convert [M on this binary, OLD regime; s93's
binary had no `bc_ok_w`].

### 2.4 The instrument's price, reported not hidden

`endpoint84`: **+1 773.9 ± 139.7 µs, t = +25.39** on 115 pairs; `cpu/draw` +5.365 % ± 0.367 %.

## 3. `bda94a` — what BDA would COST

`bdaall=0|1` with `bdacap=1 mutwide=8` in both arms, period 30 from 1800, ABBA, pin 1.
**VALID:** split −0.005 %, pairs 107/107, work −0.321 %; 0 hang markers; guards 8 PASS / 1 FAIL /
1 WARN / 2 SKIP — the FAIL is check 6 (cores; 2 of 43 groups off their arm median), **which is not a
criterion**; the WARN is check 0 (`tabtip.exe`, GPU idle at 1.0 %); checks 8/9 SKIP (no video).
**Controls 4/4 HIT:** D1 (`bda_n − bda_all_n` armed vs `bda_n` unarmed) +0.27 %; D2 leak: 51 unarmed
frames, all at distance 29; D3 `a_mut_n / bda_n` = 1.0000 / 1.0001; D4 work −0.32 %.

### 3.1 The numbers (per flip)

| | unarmed | armed | Δ |
|---|---:|---:|---:|
| `bda_n` PrepareBda calls | 177.9 | 5 220.5 | = `bda_all_n` 5 042.2, **of which 213.9 dispatches** |
| misses (`bda_n − bda_hit`) | 23.4 | 372.2 | ×15.9 |
| **PrepareBda whole-call wall time (`a_mut_us`, mutwide=8)** | **2 242.4 µs** | **13 013.7 µs** | **+10 771.3** |
| **`prot_gpu_us` — VirtualProtect on GuestGpu** | **1 680.8** | **7 107.0** | **+5 426.3** |
| `prot_gpu_pages` | 6 654.9 | 21 814.5 | ×3.28 |
| `stg_pool_ns` — handing regions to the copy pool | 184.5 µs | 1 724.7 µs | +1 540.1 |
| `pb_wait_gpu_us` — apply-lock wait on GuestGpu | 136.4 | 1 129.3 | +992.9 |
| `stg_in_ns` — inline memcpy on GuestGpu | 44.3 µs | 115.0 µs | +70.7 |
| `sync_up_kb` uploaded (96 % via the pool, off GuestGpu) | 23 079 | 77 441 | ×3.36 |
| `end_buf_upload` pass ends / all `restarts` | 20.5 / 64.3 | 200.9 / 240.1 | +180.5 / +175.8 |
| `ob_stream` ring copies | 13 289.8 | 4 408.8 | −8 881 |
| `fw_n` write faults (all threads) / `fw_win_recent` / `fw_refault` | 1 272.1 / 45.8 / 11.9 | 2 491.2 / 1 006.3 / 185.0 | +1 219 / +960.5 / +173.1 |
| `fault_us` (all threads; GuestGpu's share +160) | 15 075 | 27 735 | +12 660 |
| `gpu_busy_us` | 12 644 | 17 484 | +4 840 (not decomposed) |
| `fbp_n` / `fbp_ns` ProcessFaultBuffer (CPU call only) | 2.00 / 13.2 µs | 6.99 / 29.0 µs | +15.8 µs |

**Endpoints (ABBA, 107 pairs):** **`C_bda` = cpu_net_us +10 807.8 ± 106.0 µs, t = +203.9**
(`endpoint84`); `C_bda_dt` = dt_us +10 868.6 ± 109.2, t = +199.0.

### 3.2 Where it goes

The extra GuestGpu time sits inside PrepareBda: paired `a_mut_us` +10 773 ± 65 against `C_bda`
+10 808 (a wall-clock rdtsc interval against thread CPU time; the remainder is a net of opposing
effects outside it, plus the armed arm's 5 042 extra MutScope stamps). **Half of it is re-arming
page protection** (`prot_gpu_us` +5 426), then the pool hand-off (+1 540) and the apply-lock wait
(+993); the inline memcpy is +71; ~2 580 µs are unattributed. The cycle behind it [R + M]:
`SynchronizeBuffer` consumes the dirty bits and re-arms write protection
(`bufferCache.cpp:2878-2880`); called on every draw, it re-protects pages the guest is still
writing, so the same threads fault again in a window they already faulted this frame
(`fw_win_recent` 45.8 → 1 006.3, `fw_refault` 11.9 → 185.0), and the next draw's call re-protects and
re-uploads. The fault time lands mostly on other threads (+12.5 ms), outside `C_bda`. The GPU side of
the extra fault-buffer passes is inside `gpu_busy_us` and was not separated.

### 3.3 Verdict (`pred/02` §5), IN THE OLD REGIME

Net ceiling = 1 198.6 − 10 868.6 = **−9 670.0 µs ⇒ CLOSED**; the bind-only route = 1 001.3 −
10 868.6 = **−9 867.3 µs: the naive conversion loses ~10 ms a flip in the OLD regime.**

**What this does NOT close [I]:** `bdaall` prices the naive design (PrepareBda's global scan wherever
a slot converts). A design that synchronises only the converted buffers — which `ObtainBuffer`
already does per slot — would not pay `C_bda`, but it would keep that sync inside the 1 001.3 µs it
hoped to save. **The gross ceiling 1 198.6 µs is CLOSED either way.** And `C_bda` in the NEW regime is
not measured: the re-protect → re-fault cycle does not depend on the regime [I — write faults read
1 266.7 in `bl93a` (NEW) and 1 272.1 here], its size may.

### 3.4 The regime is a state a launch does or does not leave

| log | before the schedule (300–1799) | window n ≥ 2100 |
|---|---|---|
| `bl93a` (s93) | `bda_scan` median 51, but 21.7 % of frames 300–999 at the ~1 060 level | 51 |
| `mc94a_warmup`, `mc94a`, `bda94a_warmup`, `bda94a` | 1 065–1 068, 93–99 % of frames at that level | 1 065–1 069 (unarmed) |

Every log reads 13–21 over frames 2–175 and jumps to ~1 050 around frames 177–210; `bl93a` left that
level at frame 277 and (mostly) stayed out; this session's four launches never left it, and neither
did `stg92a` or `wak92a_warmup`, while `wak92a` did. **So OLD is the common state and NEW the
exception**, and it is not a code change (`wak92a_warmup` and `wak92a` share a binary). In `bda94a`
the unarmed arm stayed at 1 068 while the armed arm read 2 295–2 317: no carry-over. What makes a
launch leave the level is not known.

## 4. §3.2 of the brief — `bc_cb`: the binding cost measured, no rule sealed for it

* **Why const-bank exists [R]:** a storage-buffer read pays `robustBufferAccess2`'s bounds check
  (IADD+LOP3+ISETP+LDG); a uniform array is read by LDC with none. Session 18 measured two pixel
  shaders on a RenderDoc bench −2 % and −6 % with it (never a whole frame, and the GPU is not the
  bottleneck: `gpu_busy_us` 12.8 ms of 32.7). Compute is excluded (CS 5323 128 → 177 registers).
  `KYTY_CBANK_COPY` (s20) forces 16-byte alignment and copies misaligned ranges into the ring —
  ~7 840–7 861 copies a flip.
* **Each cb slot is bound TWICE** — as a storage buffer in `Buffers` and as a uniform in
  `ConstBuffers` (`BindingLayout.cpp:85-94`, CommitBindings) [R].
* **Measured now:** `bc_cb_ns` = **1 619.1 µs a flip over 27 704.9 slots, 58.4 ns a slot** [M]
  (draw and dispatch slots together). The commit-side write list and emit of ALL descriptor kinds of
  armed graphics commits is 626.2 + 446.6 = 1 072.8 µs [M]; their sum, ~2 692 µs, is a rough ceiling
  for any change to how cb slots are bound — rough because it leaves out per-slot `FindBuffers`
  (unmeasured under lite) and dispatch commits, and adds two arms.
* **The options:** (a) a storage view instead of the uniform — removes only the duplicate
  descriptor (≤ its share of 1 072.8 µs) and loses LDC; cannot be flipped by a schedule (read once,
  in the cache signature). (b) BDA — **the ring-backed cb slots are NOT out of reach**: their bytes
  are guest memory (alignment copies, `descriptors.cpp:229-310`, or small CPU-dirty ranges,
  `bufferCache.cpp:1288-1315`), which the table maps once synchronised — `bdaall` itself cut
  `ob_stream` 13 290 → 4 409 and `bc_ring` 853.5 → 12.5. So (b)'s gross ceiling is ~2 692 µs, in the
  MARGINAL band of the borrowed table, and it closes only **net**: of the sync cost priced in §3
  (+10.8 ms in the OLD regime, or the per-slot sync it would keep) and of the GPU cost of LDC → LDG.
  (c) dynamic offsets — closed by session 59 (0.3–0.45 ms, top 650 µs; push-descriptor layouts cannot
  hold dynamic descriptors, s58). (d) dropping the STORAGE duplicate for scalar-only V#s (keeps LDC)
  — not examined before; ≤ the duplicate's share of 1 072.8 µs, CLOSED.
* **What `bc_cb` does to set reuse:** ring entries (≥ 93.9 % of them const-bank served by the ring,
  this session's [I] across two partitions) are 85.8 % of the not-P reasons — but SRT/shader-data
  uploads, which have nothing to do with const-bank, are 79.9 %, so removing every cb ring entry would
  still leave most sets different.
* **No rule was sealed for §3.2**; the reading above borrows session 93's table and says so.

## 5. Scoreboard (counted by sealed item, not by scorer row)

* **`pred/01`: controls 7/7 HIT; predictions 10, 9 HIT, 1 MISS** (R5, §0.1.2). Points against
  outcomes: R1 0.04 → 0.128; R2 60 → 48.1 µs; R3 200 → 197.3 µs; R7, R8, R9, R10 (+1 773.9, inside
  [+300, +3 000]) within their bands; R4 CLOSED; R6 ring the most frequent reason at 0.748 of all
  commits.
* **`pred/02`: controls 4/4 HIT; predictions 8, 7 HIT, 1 MISS** (B8, §0.1.4). Points: B1 4 300 →
  5 042.2; **B5 +2 500 → +10 807.8 (4.3× the point, 90 % of the band's top)**; B6 +3 000 → +10 868.6;
  B2, B3, B4, B7 HIT.
* **Session total: controls 11/11; predictions 16 of 18.** Both misses are defects of my own text.

## 6. Traps of this session

* **A scorer can repeat the defect it was written to avoid.** Deciding an arm "fired" from
  `counter > 0` failed on a straddle of 1.09 a flip. Decide by the GateArm text and by magnitude,
  and **write and dry-run the scorer on the record (arms relabelled) BEFORE sealing** — this session
  did it 3–4 minutes after, and said otherwise in its first draft.
* **A band on a counter that never fired scores a vacuous HIT at 0.0.**
* **"Same pipeline layout" by handle means "same pipeline" here** — one `VkPipelineLayout` per
  pipeline; set compatibility is by definition.
* **A class decided per draw is not a property of the slot** — mask convertible slots by what the
  shader could do, and label them by what the draw did.
* **"Cannot be addressed" must be said of the BYTES, not of today's copy of them** (the ring-backed
  cb slots).
* **The BDA regime is a state a launch does or does not leave** (OLD is the common one); record the
  frames before the schedule and say which regime every number belongs to — in the headline too.
* **A written slot costs 8× a read-only one** (0.490 µs vs 59.3 ns) — a population-weighted price
  hides it.
* **Two estimators of one endpoint give two t values** (sample vs population SD): quote one.
* Carried: no exact zero on a schedule arm (both leaks sat at distance 29 of 30); `summary4.py`'s
  `cpu_net_us` IS `cpu_gpu_us` under lite; guards check 6 is not a criterion and check 10 hashes the
  exe installed now; never rebuild between acceptance and the final answer.

## 7. Not closed

* **`C_bda` in the NEW regime**, and **what makes a launch leave the OLD level** (`bda_scan` ~1 060 →
  ~50; `buf_new` ~1.3–2 → ~0.01 a flip) — in the OLD regime PrepareBda alone takes 2 242 µs a flip
  (`a_mut_us`, unarmed arm), and NEW is the exception.
* **The written bc_ok slots: 490.5 µs a flip for 1 001.7 slots, 0.49 µs each** — the most expensive
  slot class per unit on the binding path, never split (ObtainBuffer's write path,
  `InvalidateMemoryFromGPU`, `RecordGpuWrite`).
* **Why the other half of s93's merge population cannot reuse its set**, draw by draw
  (`mc_ok_ring`-style counter).
* The GPU side of the bdaall contrast (`gpu_busy_us` +4 840) and its ~2 580 µs of unattributed CPU.
* Carried: the single-chunk notify (99.9 µs, s92); the `ObtainBuffer` stream-ring timer (lite = 0);
  `pfhint`/`pfcap`/`dapin` re-measured with the pin and the record path on; route B items 2, 8, 10,
  12 and the corrected 3.

## 8. Target arithmetic

60 FPS = 16 667 µs; shipped base 31 642 µs = 31.60 FPS; **~15 000 µs must come out and the vblank
plateau pays nothing for less.** The last candidate of that scale on the board — V# slots onto BDA
— measured **1 198.6 µs gross (8 % of what is needed); its naive form costs +10.8 ms a flip in the
OLD regime, the state launches usually stay in.** No known route and no known combination of routes
reaches 16 667 µs. **Do not promise 60 FPS.**
