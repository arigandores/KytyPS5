# Route A, stage 4, part 2 — the carry of the spine, a safe plan, the pass histogram (K3) and the image overlap of adjacent segments (K4); plus the micro-track re-measure arm

Session 118. Written from reading the code (HEAD `f62d537`) before any line of it. Tags: [I] read from source, [M]
measured in a named run, [U] unknown. Part 1 (session 117, `spn117`): the spine reproduces the register state before every
draw/dispatch within a submission (K5 PASS, 0 of 19.1 M compares differ); its own timer 0.61 ms a frame (a lower bound).

## 1. The carry (term C)

Route A needs the spine to CARRY the register state across submissions: the walker (or a spine thread) will not be seeded
from the real processor. Part 1 seeded at every submission start, so it never tested that. The cheapest test that needs
no new thread [I]: each `CommandProcessor` keeps its shadow processor between plans; at the start of the next plan, BEFORE
seeding, the shadow state left by the END of the previous plan of the same processor is compared member-wise
(`operator==`, as part 1) with the real state at that moment. Equal ⇒ nothing outside the packets (GuestGpu commands, the
flip path, resets done by the host) changed the processor between the two submissions, and the handlers left the same end
state. Counters `carry_cmp`, `carry_bad`, `carry_skip` (no previous complete plan); lines `SpineCarry: sub= parts= reg=`
(≤ 40). `m_num_instances` stays excluded (indirect draws). Then the plan seeds as before, so K5 keeps its meaning. Where
the spine would run in route A (GuestGpu or the walker) is a separate question, priced by part 1's walker fit.

## 2. A safe plan (ROADMAP 117 item 15 (в))

The audit found two ways a plan could change what executes [I]: (a) words read early — the predication word, the
`COND_EXEC` word, the 14-dword branch's compare word, a nested IB's contents, the `*_REG_INDIRECT` tables — may sit on a
GPU-dirty page, whose read goes down the fault path and drains the queue; (b) the real handlers `EXIT` on conditions the
spine can reach where execution would not (unknown offsets in the indirect tables, `R_CONTEXT_STATE` push/pop
imbalance, offsets past `CX_NUM`/`SH_NUM`/`UC_NUM`, a register with neither a direct nor an indirect handler).
**Rules:** (a) before any such early read the spine asks `Memory::IsGpuClean(address, size)` (on GuestGpu it is exact);
if not clean the plan stops as UNCERTAIN (`spine_uncertain`, no compares for the rest of that submission, no carry from
it); (b) before calling a register handler the spine checks the structural conditions above and stops the plan as ABORTED
instead of reaching an `EXIT`. Value-level `EXIT_NOT_IMPLEMENTED` inside individual register handlers (e.g. a register
with an unexpected value) stays a residual risk: the real processor reads the same value from the same packet a moment
later, so the spine reaches it only when execution would too — except for the early-read words, which (a) covers.
The knob comment "never changes what executes" becomes "does not change what executes except through the residual risk
above".

## 3. The slice census (terms K3, K4) — gate `slicecen`, measurement only

On the GuestGpu thread only (`GuestGpu::IsGpuThread()`; the present path also begins passes on its own buffer):
- **element**: every draw/dispatch packet (the `SpineIsElement` set) counted in `ProcessPm4Range`; a change of
  `GetGpu().GetFrameNum()` seen there closes the previous frame;
- **pass start**: `CommandBuffer::BeginRenderingImpl` (after its early return — the population `rp_begin` counts)
  records the current element index;
- **images**: every image slot of `PrepareBindings` after resolution (`image_id`, written = storage binding) and every
  colour/depth target of `AcquireRenderTargets` (written).
At frame close (the first element of the next frame): **K3** — runs of elements between consecutive pass starts (the
frame's first run from element 0; dispatches outside passes belong to the run they fall in): largest run, count of runs,
histogram `<32 / <128 / <512 / <1024 / ≥1024`; **K4** — the frame cut into W = 2 and W = 4 segments at the pass starts
nearest to the equal-element points (`k4_nocut` when too few pass starts), and for each adjacent pair: `any` =
|A ∩ B| / min(|A|, |B|) over image ids, `dep` = |(Wr_A ∩ B) ∪ (A ∩ Wr_B)| / min(|A|, |B|) (an image written in one and used
in the other — the images whose layout transitions and writes would order two contexts); the frame's max over pairs, in
permille; and `fmax` = the largest segment's share of elements. Counters `sc_frames`, `sc_el`, `sc_runs`, `k3_max`,
`k3_h0..h4`, `k4_w2_any`, `k4_w2_dep`, `k4_w2_fmax`, `k4_w4_any`, `k4_w4_dep`, `k4_w4_fmax`, `k4_nocut`, `sc_img`,
`sc_ns` (the census's own cost, raw ns). A frame's results land in the FrameTrace row of the flip after it closes (one-frame
lag; a row may carry 0 or 2 frames — the scorer uses `sc_frames`).

## 4. The re-measure arm (M)

No new code: `takelap=1 bindlap=1 pathlap=1 mutsite=1` on the same build, in its own schedule arm (the part-2 arm sets
them 0 and `spine=2 slicecen=1`; the M arm `spine=0 slicecen=0`). Report the six `AheadTake` phases (witness verify
`da_t_ver_us`), the bind split (`bl_*`), the emit parts (`pl_em_*`) and `mh_*`, per frame, frames 10–88. No verdict: a
candidate ≥ 1 ms gets a removability design with its ceiling recorded before any code.

## 5. Verdict rules (to be sealed)

Arm P, kept frames 10–88, pinned, ABBA P|M period 90 from 1800:
- **K5 (continuity of part 1):** as `spn117` (every x line of both arms; any `SpineMismatch:`/`SpineMisalign:` ⇒ FAIL).
- **C (carry):** FAIL if any `carry_bad` or `SpineCarry:` line; PASS if none and `carry_cmp` ≥ 90 % of the plans that
  had a complete predecessor (`spine_n − carry_skip`) over arm-P kept frames; else NOT_EVALUABLE.
- **Safe plan:** `spine_uncertain` + `spine_abort` ≤ 10 % of plans over arm P, else K5/C NOT_EVALUABLE (reported).
- **K3 (bounds W, never closes):** median over arm-P frames (`sc_frames` = 1) of `k3_max / sc_el` ≥ 0.25 ⇒ W ≤ 4
  (`DESIGN_82` §7 K3), else W up to 8.
- **K4:** on `dep` (writes cross the cut): median over arm-P frames of `k4_w2_dep` ≤ 300 ‰ ⇒ PASS at W = 2, else FAIL;
  the same for W = 4. `any` reported only (shared read-only images need no transition between contexts).
**Consequences:** K5 or C FAIL ⇒ stage 4 stops until the hazard the diagnostic lines name has a design; K4 FAIL at W = 2
⇒ route A closed for maximum FPS (one cut cannot coarsen further; writes crossing it order the two contexts); K4 FAIL only
at W = 4 ⇒ W = 2 is the ceiling of the route (its best case recomputed with f = 0.5 before stage 3 resumes); all PASS ⇒
stage 3 resumes (M3.2 …) with stage 5 (W = 2) as the first milestone with a gain. The M arm decides nothing by itself.
