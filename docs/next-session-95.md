# Session 95 — route E, measurements M1 and M2

**The user's decision after session 94: the programme goes to ROUTE E, the rewrite of the translation
layer (`docs/ROADMAP.md` §0.1, §2 E, §5 item 5). Session 95 writes NOT ONE LINE of that rewrite. It
runs the first two of the five measurements that decide WHICH rewrite is worth attempting: M1 (where
the process's CPU goes — hours, no code) and M2 (frame-to-frame repetition of a draw's CONTENT — the
session's A/B'd source change). Between them they can close route P or route F outright.**

Read `docs/ROADMAP.md` first — §0.1's decision paragraph, **§2 E** (budgets, the five measurements
with their sealed rules, the traps), §5 item 5 — then `C:/kyty/s94/FACTS.md` (§0.1, §0.2, §2.1–2.3,
§3.2–3.4, §7) and `C:/kyty/s94/rewrite94/judge.md` §§1–4 (the four analyses are beside it).

**Open the report with these three numbers, every session of route E:**

* the budget: **≤ ~3.0 µs a draw** on a median frame, **≤ ~2.3 µs** on a p99 frame (7 284 draws);
* where the path stands: **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms** (p50 12.83, p90 13.94,
  p99 15.77 with the clock pinned);
* which of M1–M5 is still undone.

**Do not promise 60 FPS.** The estimate is ~15 % (8–25 %) and it does not rise with the speed of the
executor — it is held by the unknowns, not by the typing.

Session 94's commits on `merge-upstream`: `4912ae5` (sources), `7d03f93` (results and record),
`462d8c6` (route E). **No default changed, nothing shipped.** The installed `kyty_emulator.exe` is
**`4338ba1a300a17be170167a4291748f8a93ad282f4c1c27a4c93084752386b4e`, 23 642 624 bytes**, not rebuilt
after acceptance. Harness `C:/kyty/s94` → port to `C:/kyty/s95` (§5 below).

---

## 1. M1 — where the process's CPU goes (do this FIRST; hours, no code, no rebuild)

Route P (parallel translation) assumes there are free cores. **Nobody has ever looked.** What the
disk already says (`log_mc94a.txt`, unarmed arm, n ≥ 2100, 3 480 flips, per flip):

| | µs a flip | note |
|---|---:|---|
| `cpu_proc_us` — the whole process | **247 261** | 7.55 logical CPUs at 32.75 ms a flip |
| GuestGpu (`cpu_gpu_us`) | 32 356 | the translation thread, 98.8 % busy |
| record thread (`cpu_record_us`) | 29 913 | **of which `rec_spin_us` 26 797 is spin** |
| M1 draw-ahead workers (`da_work_us`) | 26 690 | 4 workers, `dathreads=4` |
| main guest thread (`cpu_main_us`) | 9 202 | |
| present (`cpu_present_us`) | 1 082 | |
| **attributed** | **99 243** | |
| **UNATTRIBUTED** | **≈ 148 000 (4.5 logical CPUs)** | who? |
| page faults, all threads (`fault_us` / `faults`) | 14 956 / 1 279 | main 1 108, GuestGpu 97 — so **~13.8 ms lands elsewhere** |

**Step 0 (free):** reproduce that table from the log, and do the same on `log_bda94a.txt`. Nothing
below is worth doing if it does not reproduce.

**Step 1 — per-thread CPU deltas (PowerShell, no code).** Launch the settled scene and sample the
live process twice, 30 s apart, in the steady window:

```powershell
$p = Get-Process kyty_emulator
$a = $p.Threads | Select-Object Id, TotalProcessorTime, ThreadState, WaitReason
Start-Sleep -Seconds 30
$b = (Get-Process kyty_emulator).Threads | Select-Object Id, TotalProcessorTime, ThreadState, WaitReason
# difference by Id, print µs per game frame (divide by the flips in those 30 s, from the log)
```

Launch with `python C:/kyty/s95/enter_scene.py m1probe --gates-file C:/kyty/s95/gates_base.txt
--hold 300 --warmup-first KYTY_GPU_CLOCK_PIN=1` and sample while it holds. **Thread ids are not
names** (the log's `thread create:` lines print `id = -1`), so classify by magnitude and by count:
GuestGpu ≈ 32 ms a frame, record ≈ 30, four equal ~6–7 ms threads are the M1 workers, and the rest
are the game's own threads plus the driver's. Report the distribution, not a single sum.

**Step 2 — spin versus work (ETW, if available; check `where wpr` and `where xperf` first).**

```
wpr -start CPU -filemode
… 20 s of the settled scene …
wpr -stop C:/kyty/s95/cpu.etl
xperf -i C:/kyty/s95/cpu.etl -o C:/kyty/s95/cpu.csv -a cpuprofile
```

What is needed from it: per-thread CPU split by module (`kyty_emulator.exe` vs the Vulkan driver vs
`ntoskrnl`), and whether the big unattributed block is spinning (`WaitReason`/`Sleep`/`YieldProcessor`
stacks) or real work. If ETW is unavailable, say so and fall back to Step 1 plus the emulator's own
sampler (`KYTY_SAMPLE_GPU=main`), and record that the answer is weaker.

**The sealed rule (ROADMAP §2 E), written before the numbers:**

* real, non-spin work outside translation **above ~8 logical CPUs at twice the frame rate** ⇒
  **route P is CLOSED** (there are no free cores to move the work onto);
* any single guest thread costing **more than ~12 ms per game frame** ⇒ **60 FPS is out of reach for
  every route**, and that is the programme's answer;
* otherwise: record how many cores are genuinely free, because that number is the `W` of route P's
  own arithmetic (`DESIGN_82_parallel.md` §1).

M1 needs no gate, no build and no pre-registration — but **write its rule into the session's report
BEFORE the numbers**, and keep the run tag and window.

---

## 2. M2 — frame-to-frame repetition of a draw's CONTENT (the session's A/B'd change)

**Never measured.** What exists: a whole stage's bindings repeat the PREVIOUS DRAW's in 2.06 % of
stages, slots in 64.2 % (s84); the M1 job key repeats between frames 3 times in 9 460 (0.03 %, s66)
— **but that key carries per-object and per-frame pointers**; `e9_full` = 0 against the last set of
the same layout (s57) because ring offsets differ every draw; 84 % of ring copies are byte-identical
(s62, `cbstat`). **None of that is the question.** The question is: does draw *i* of frame N do the
same WORK as some draw of frame N−1 — same pipeline, same views, samplers and buffer identities,
same payload bytes — so that its translation could be replayed instead of recomputed?

### 2.1 The instrument (gate `framerep`, `KYTY_FRAME_REP`, default 0, MEASUREMENT ONLY)

Reuse session 94's machinery — it already builds a canonical signature of a draw's descriptor set:

* **Where:** `MergeCostCensus` (`descriptors.cpp`, after `CommitBindings` is timed) already walks the
  write list in build order and masks entries. Add a second, cheaper walk (or a second hash over the
  same walk) that produces **H_ident**: pipeline layout definition + every image view and layout +
  every sampler + every non-ring buffer's `{handle, guest range}`, with **stream-ring entries replaced
  by a fixed marker** (their offset is fresh every draw by construction) and **flattened-SRT /
  shader-data descriptors replaced by a hash of their PAYLOAD BYTES** (hook `NativeUpload`,
  `descriptors.cpp:1229`, called at `:1890` and `:1893` — it has the span it copies; keep the hash in
  `PreparedBindings`).
* **H_full** = H_ident ⊕ the `shader_data` dwords (push data) ⊕ the draw arguments (index/vertex
  count, instance count, first index/vertex, indirect address) ⊕ the vertex/index buffer identities.
* **Frame rotation on the GuestGpu thread only:** `m_context.GetGpu().GetFrameNum()` is available at
  the draw site; when it changes, rotate three hash multisets (N−1, N−2, N−3 — double-buffered
  per-frame allocators favour N−2). No cross-thread state, no locks.
* **Per draw, count a hit** when the hash is present in the multiset of N−1 (and separately N−2, N−3),
  consuming one occurrence. **Never align by draw index — session 66 recorded that draw numbering is
  not stable.**

**Counters** (all raw counts/ns, `Enabled()`-based so they live under lite):

| | meaning |
|---|---|
| `fr_n` | draws the census saw |
| `fr_id1` / `fr_id2` / `fr_id3` | H_ident present in N−1 / N−2 / N−3 |
| `fr_full1` / `fr_full2` / `fr_full3` | H_full present in the same |
| `fr_id_ns` / `fr_full_ns` | the draws' own time (pre+post class, the s94 brackets) for the hits |
| `fr_all_ns` | the same time over all `fr_n` draws — the denominator of the sealed rule |
| `fr_pay_same` | hits where the SRT/shader-data payload bytes were identical too |
| `fr_ring` | hits that carry at least one stream-ring entry (they need a re-upload even when replayed) |
| `fr_sig_ns` | the census's own time, subtracted from the draw brackets exactly as `mc_sig_ns` is |
| `fr_bad` | walk out of bounds (must read 0) |

**Cost control:** one hash over ~20–60 words a draw ≈ 0.1–0.3 µs, i.e. ~0.5–1.5 ms a flip in the armed
arm. Keep it OUT of the timed brackets (session 94's pattern), and expect the ABBA endpoint to show
it: session 94's cheaper census cost +1 774 µs.

### 2.2 The run

One ABBA contrast, period 30 from 1800, `KYTY_GATE_SCHEDULE_ABBA=1`, **`KYTY_GPU_CLOCK_PIN=1`**:

```
framerep=0 mergecost=1 bdacap=1 drawmerge=1 | framerep=1 mergecost=1 bdacap=1 drawmerge=1
```

`mergecost`, `bdacap` and `drawmerge` in BOTH arms give the per-draw time brackets and cancel.
Tag `fr95a`. Admission in order, no optional stopping: `guards.py --first-frame 2100` (check 6 is not
a criterion; check 10 hashes the exe installed at that moment) → `area_series.py` + `area_verdict.py`
(split < 1.0 %, pairs ≥ 90 %, work < 0.5 %) → `summary4.py --blocks` (its `cpu_net_us` IS
`cpu_gpu_us` under lite — not quoted) → `endpoint84.py` → the session's own scorer. **A run that
fails admission is replaced, not discussed.**

### 2.3 The verdict rule — seal it before the run

**Coverage** `C` = `fr_id_ns` / `fr_all_ns` (and the stricter `fr_full_ns` / `fr_all_ns`), the share of
GuestGpu draw time carried by draws whose work repeats a draw of the previous frame.

* **C < 0.84 ⇒ route F (frame replay) is CLOSED permanently.** The arithmetic behind the threshold,
  written out: to reach 16.7 ms from 31.6, ~15 ms must go; a replayed draw is not free (session 62:
  proving bytes unchanged cost 4.2 ms per 15 MB; ~2.8 ring ranges a draw, ~20 MB a frame, are payload
  that moves every frame), so at a replay price of 1.0–1.5 µs against today's 6.4 µs the covered share
  must exceed ~55–61 % just to break even, and 0.84 is where it survives a 30 % error in the replay
  price — which this programme's upper estimates have needed six times.
* **C ≥ 0.84 ⇒ F goes to a prototype in session 96** on the cheapest slice (one render pass), with a
  mandatory verify mode in the style of `smemocheck`.
* Report `fr_full` beside `fr_id` and `fr_pay_same`: they separate "same resources, different
  constants" (which dynamic offsets or push constants could still serve) from "same everything".

**Controls that can fail** (at least three, each with a band sealed before the run):

* the census's walk is consistent: `fr_bad` / `fr_n` ≤ 0.001;
* `fr_n` against `mc_n` (session 94's counter at the same site) within 0.5 %;
* hits must not exceed the population: `fr_full1` ≤ `fr_id1` ≤ `fr_n` on the run sums;
* the leak: the unarmed arm's `fr_n` ≤ 0.1 % of the armed arm's, and **any non-zero frame is checked
  for its distance from the block start before it is called a defect** (both session-94 leaks sat at
  distance 29 of 30);
* a replication that can fail: `fr_id1` ≥ the number of draws whose slots all repeated the previous
  DRAW (s84's 2.06 % of stages is a different statistic — do not import it as a band).

### 2.4 The pre-registration

Seal `C:/kyty/s95/pred/01_framerep.md` **before the emulator is opened**, and — the trap session 94
fell into — **write and dry-run the scorer on the record (arms relabelled) BEFORE sealing**, then fill
its `PRED_SHA` in. It must contain: the mechanism, the instrument, the arms and the admission, the
controls above, the verdict rule of §2.3, the predictions with point estimates and bands, and the odds
said out loud.

---

## 3. If time remains (in this order)

1. **M3's preparation only** — read `renderDraw.cpp`/`descriptors.cpp` for where a `bindfloor` stub
   would cut, and write down the lap chains that would split the **4.05 ms outside the render mutex**
   and the **~5 ms of `mh_emit` beyond CommitBindings** — both have never been split. Do not build it
   this session unless M1 and M2 are finished and accepted.
2. The carried debts (`FACTS.md` §7): the BDA regime (OLD costs 2 242 µs a flip of PrepareBda alone,
   and OLD is the common launch state); the written bc_ok slots (490.5 µs a flip, 0.49 µs each);
   `C_bda` in the NEW regime; the single-chunk notify (99.9 µs); the `ObtainBuffer` ring timer;
   `pfhint`/`pfcap`/`dapin` with the pin; route B items 2, 8, 10, 12, 3.
3. **The DRS clock floor** (ROADMAP §2 E traps) — not a measurement but a prerequisite of every
   rewrite: before any faster CPU path, the game must be kept off the 4K step (at halved clocks it
   went to native 4K in 100 % of flips, GPU 20.0 ms against 12.1). Days of work; predict with the s91
   pin; it is NOT part of session 95.

---

## 4. The port — FIVE root constructs, each a separate edit

Write `C:/kyty/s94/s95_port.py` **fresh in the SOURCE directory**, modelled on
`C:/kyty/s93/s94_port.py`:

1. the heads of the `--roots` defaults (`arms.py:29`, `baseline.py:83`, `effect.py:103`): the new root
   goes in FRONT and `s94` stays;
2. `area_verdict.py:56` `range(94, 70, -1)` → `range(95, 70, -1)`;
3. `shift91.py:35` `range(94, 66, -1)` → `range(95, 66, -1)`;
4. the tuple-spelled chains `stg92.py:44`, `bda93.py:41` **and `s94lib.py:21`**
   (`ROOTS = ('C:/kyty/s94', 'C:/kyty/s93', 'C:/kyty/s92')`) — a literal rewrite drops `s94` and hides
   `log_mc94a.txt` / `log_bda94a.txt` from `mc94.py`, `bda94.py` and the new scorer;
5. **`regime94.py` picks its root by tag** (`'C:/kyty/s93' if tag.startswith('bl93') else
   'C:/kyty/s94'`) — it must keep pointing at `C:/kyty/s94` for session-94 tags.

Then: `gates_base.txt` byte-identical (1092 B, 99 names, sha256 `00c116dc…0594d8`); `gen_gates.py` in
`--check` mode only, and it says "out of date" BY CONSTRUCTION (99 of 124 names pinned) — never rerun
it without `--check`; `.txt`/`.json`/`.md`/`.csv`/`.sh` byte-exact; **write `accept95.sh` new** (the
`.sh` files are byte copies pointing at their own harness) with a step 5 on session 95's own sealed
pre-registration — never `mc94.py`/`bda94.py`/`bda93.py` on a session-95 tag, each verifies its own
sha256 and keys off its own arm texts. **Every carried `s8x/s9x_port.py` inside a harness is a
self-copy (SRC == DST): never run one.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.** M2's census is that change; M1 is free and comes first.

---

## 5. Do NOT

* **Do not start writing the rewrite.** M1–M5 first; this programme's upper estimates have overshot
  2–20× six times.
* **Do not write or dry-run the scorer after sealing** (session 94 did, 3–4 minutes after, and its
  first draft claimed otherwise).
* **Do not decide that an arm fired from `counter > 0`** — a straddle of 1.09 a flip defeated exactly
  that test inside session 94's own scorer. Decide by the GateArm TEXT and by magnitude.
* **Do not score a band on a counter that never fired** — it prints a vacuous HIT at 0.0.
* **Do not align frames by draw index** (draw numbering is not stable, s66), and **do not import a
  band from another tool's partition** (s84's 2.06 %, s57's `e9`, s62's `cb_same` all measure
  different populations).
* **Do not quote a PrepareBda number without its regime**; do not quote two t values for one endpoint
  (`endpoint84.py` is the endpoint).
* **Do not demand an exact zero on a schedule arm.**
* A foreign game on the GPU is a hard stop (check `nvidia-smi` BEFORE launching); `summary4.py`'s
  `cpu_net_us` IS `cpu_gpu_us` under lite; guards check 6 is not a criterion and check 10 hashes the
  exe installed at that moment — **never rebuild between acceptance and the final answer**;
  `gen_gates.py --out X` without `--with` overwrites `gates_base.txt`; never pipe a writing script
  through `head`; patches go into a file via Write (CRLF), never through a heredoc.
* Carried: pre-registrations sealed in place and never edited; a failed control is REPAIRED under a
  NEW sealed pre-registration; a run that fails admission is REPLACED, not discussed; the first entry
  after a fresh build hangs (`--warmup-first`); ratios of sums, never per-frame identities; a knob a
  schedule must flip cannot be read once per process; the video pass (`--video`, `s20_vidglitch.py`,
  ≥ 3 000 frames) is a debt after any change that can reach the renderer.
