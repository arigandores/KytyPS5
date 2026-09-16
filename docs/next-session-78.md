# Session 78 — the prompt

Session 77's commit is on `merge-upstream`. The installed binary's **executable code is identical
to session 76's `79680f59`** — only comments changed — but the **exe hash is not reproducible
across links** (the PDB GUID is regenerated), so read the binary each run records in its
`<tag>.json`. Harness — **`C:/kyty/s77`**, port it to `C:/kyty/s78`.

You are the orchestrator. The programme's goal is **60 FPS in Sky Garden** (today 31.23).

Session 77 localised a shipped win for the first time, re-measured both shipped gates, and then
found something that reaches back through the whole programme: **the stand has a between-run
variance nobody has measured, and it is three to five times the error bar every shipped figure is
printed with.** Read `C:/kyty/s77/FACTS.md` §3 before anything else.

## 0. Read first

1. `C:/kyty/s77/FACTS.md` in full — especially **§3 (the error bars)** and **§2 (the localisation
   and its three caveats)**.
2. `C:/kyty/s77/README.md` — "Standing traps".
3. `C:/kyty/s77/PREDICTIONS.md` — **50 056 bytes. CHECK THE BYTE COUNT.** Reading it through the
   rtk-rewritten shell returns 46 171 bytes and silently drops the last section, which is the one
   carrying the retractions. An auditor did exactly that and took a retracted figure for the
   conclusion.

**Harness:** port `C:/kyty/s77` → `C:/kyty/s78`, roots rewritten, `.txt`/`.json` **byte-exact**.
`gates_base.txt` pins the same **99 names — 83 gates and 16 knobs, 1092 bytes**.

## 1. THE RULE SESSION 77 ESTABLISHED — read before planning any ABBA

**Two runs agreeing is not a tight estimate.** `cap76a` and `cap76b` agreed to 0.167 pp against a
combined 2·SE of 0.225; adding a third valid run gave Q = 16.8 on 2 df. Across three area-valid
runs per gate:

    pfhint  -257.3 / -690.2 / -734.3 us   RE -565 us [-824, -305]   I^2 94.6 %   tau 223 us
    pfcap   -294.1 / -238.2 / -381.8 us   RE -307 us [-392, -222]   I^2 65.7 %   tau  61 us

against within-run 2·SE of 88–134 and 80–93 µs. **A single-run figure is good to a factor of two at
best. Take at least three area-valid runs and pool with random effects.** Do not drop the run that
disagrees — that is the move session 76 was condemned for, and session 77 declined to repeat it.

**Everything else from session 76 still holds**, in particular: run `area_verdict.py` before
quoting anything; never substitute a criterion that fails; confirm arming by a counter in the run;
start the schedule at 1800 and analyse from 2100.

## 2. What is settled — do not reopen

* **`pfcap` = 0.31 ms [0.22, 0.39]**, **`pfhint` = 0.56 ms [0.31, 0.82]**, three area-valid runs
  each. **Do not add them.**
* **The cap is closed at both ends.** 512 releases 83.95 % against a pre-registered 88 % bar;
  4096 buys nothing. The full curve is in FACTS §7.
* **W4 is not a lever on the 0.98 ms** — `daprefetch` gates only the eleven-vector block, which
  closes before `VerifyWitness` is called. The brief's distance ordering was also inverted.
* **The GPU axis is worth ~8–10 µs of wall.** Not until CPU is below ~18 ms.
* **The localisation itself:** the whole −397 µs is inside the render mutex, −260 µs in
  `mh_bind_us`, −180 µs in `mh_prog_us` of which −70 µs inside `AheadTake`. The instrument
  reconciles to 0.1 µs. **The per-vector attribution is NOT established.**

## 3. The work, by prize

### 3.1 The variable behind τ — the biggest item on the list

Until it is found, no figure in the programme's table means what it says. Excluded already: the
DRS rung, thermal state, the `pfcap` state, biased pair-dropping, per-pair covariates, and pace
(raised and withdrawn as division bias — `dt_us` contains `cpu_gpu_us`).

**The harness records no CPU-side telemetry at all.** Every `gpuclk_<tag>.csv` column is
nvidia-smi: SM clock, memory clock, GPU utilisation, power, temperature. There is no CPU core
clock, no package power, no CPU temperature, no C-state or boost residency. **That is the first
place to look, and adding it costs no game time.**

### 3.2 Which of the eleven vectors buys the −260 µs

The phase split is measured; the per-vector account is an interpretation that three numbers cannot
identify. **A knob taking a bitmask of which of the eleven vectors to prefetch** is a few lines,
its arming proof is `da_pf_b` splitting by mask, and it turns the localisation into a measurement.
This is the cheapest real experiment on the list.

### 3.3 Replicate the localisation, without the instrumentation confound

`cap77a` is the only run carrying `mutsite=1 pxstat=1`, it carries ~0.4–0.6 ms/frame of timers
**inside the path under test** — more than the 0.386 ms effect — and it is the largest of the three
`pfcap` readings. "It cancels in both arms" covers an additive main effect, not an interaction with
prefetch timeliness. **Re-take `pfcap=192|1024` at `mutsite=0 pxstat=0` and compare the effect
size**; repeat the localisation once.

### 3.4 `mh_bind_us` — 10.5 ms a frame, never attacked

The largest phase inside the render mutex, and a prefetch aimed at nothing but its inputs just
bought 260 µs of it. Note the shape of the target: `px_on_bind_us` covers 6.0 ms of the 10.5 and
carries only −82 of the −260 µs, so **68 % of the delta is outside `PrepareGraphicsBindings`.**

### 3.5 Free, and already paid for

* **The release curve inverts to the per-vector size distribution.** `curve77a` measured
  `min(total, cap)` at eight caps; nothing else in the record gives the size histogram of the
  eleven vectors, and §3.2 needs it.
* **An early abort on the rung.** It is decided in the first ~600 settled flips and holds; a void
  run costs 6 minutes and an abort would save 4.5. Only ever to ABORT on a bad start, never to
  ACCEPT on a good one.
* **`aa77a`** — pre-registered in session 77, never taken.
* **The entry hang** (`curve77a` attempt 1): not the session-58 `acopyidle` mode, not a backlog,
  unexplained. `KYTY_GPU_CHECKPOINTS=1` would name the operation.

## 4. Do NOT

**New, from session 77:**

* **Do not quote a gate from fewer than three area-valid runs**, and pool them with random effects.
* **Do not read a large document through the rtk-rewritten shell without checking its byte count.**
* **Do not assume instrumentation cancels because it is in both arms.** It cancels as an additive
  main effect, not as an interaction with the mechanism under test.
* **Do not trust a count check to confirm an attribution.** `11×8+11×3+11×1+11×1` and
  `11×3+11×1+11×9` both sum to 143; only the `min()` operand distinguishes the instantiations.
* **Do not quote the wall over all blocks while deciding validity on matched pairs.**
* **`gen_gates.py --with` is `nargs='*'`, not `append`.** Write `--with a=1 b=1`.
* **Write each prediction to its own timestamped file before the run that tests it** — a single
  appended file cannot evidence its own ordering.

**Carried, all in force:** never compare between runs; confirm arming by a counter; start at 1800,
analyse from 2100; a subtraction of two ABBAs from two runs is not a measurement; check what a gate
leaves running; `PATCH_DRY=1` checks anchors, not compilation; do not rebuild between the
acceptance run and the final answer; a counter's name is not its attribution; never ship
`dawitloop` or `dawitness=0`; do not add a Knob enum entry anywhere but immediately before `Count`;
do not run other work on the machine during a measuring run; write the prediction down first and
have an independent agent attack the result afterwards — that is what caught session 77 five times.

## 5. The arithmetic

**Today** (`acc77a`): CPU **31 327 µs**, GPU **14 507 µs**, wall **32 025 µs**, **31.23 FPS**.

| article | axis | measured | state |
|---|---|---:|---|
| `dawitptr` + `daepceil` | CPU | 0.33 ms | shipped s72 — one run, interval too narrow |
| `imgfuse` (C1) | GPU / CPU | 1.268 / 0.182 ms | shipped s73 — same caveat |
| `dawitcp` (W7) | CPU | 0.19–0.23 ms | shipped s73 — same caveat |
| `dawitcg` (W8) | CPU | 0.31–0.32 ms | shipped s74 — same caveat |
| **`pfcap` 192 → 1024** | CPU | **0.31 ms [0.22, 0.39]** | 3 valid runs, I² = 66 % |
| **`pfhint` 0 → 1** | CPU | **0.56 ms [0.31, 0.82]** | 3 valid runs, I² = 95 % |
| both together | CPU | NOT MEASURED | do not add |
| where the `pfcap` gain lands | — | bind −260, prog −180 (take −70) | measured, one run, no replication |
| which vector buys it | — | NOT ESTABLISHED | §3.2 |
| **between-run τ** | — | **223 µs / 61 µs** | **§3.1 — the variable is NOT IDENTIFIED** |
| `mh_bind_us` | CPU | 10.5 ms/frame | §3.4 — never attacked |
| C2 / GPU axis | GPU | ~8–10 µs of wall | closed for now |
| M4 | — | tops out at 44.6 FPS | only serialiser (3) left |

**The honest statement of the task.** Two gates are shipped and one is localised, but the session
that did it also showed that the programme's measuring stand is looser than its own error bars
admit. **60 FPS still needs the CPU path to keep giving, and the next real gain is probably in
`mh_bind_us` — but nothing on the list can be trusted to better than a factor of two until the
variable behind τ is found, and the harness cannot even see the CPU.**
