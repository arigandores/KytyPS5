# Sealed pre-registration 01 — session 106, track 1 item 2: where the +196 µs of GuestGpu time off-CPU under `dawalk=1` goes

**Immutable once written.** The decision, the instrument and this run were recorded in `docs/ROADMAP.md` §0.1
("СЕССИЯ 106 — ЗАПИСИ ДО ДЕЙСТВИЙ", items 1–3, commit `276437f`) before any code. This text fixes the run and
the rule. Nothing ships from this run.

## 0. Why

Exploratory re-reading of `dwk104` (not a test; `C:/kyty/s105/explore106_dwk104.py`, the `dwk104.py` blocks and
quartets, 92 pairs, its numbers reproduced): **D = Δ`dt` − Δ`cpu_net` = +192.5 µs (SE 30.8, t 6.25)** — the
GuestGpu thread's wall that is not its CPU grows 866 → ~1 058 µs a flip when `dawalk=1`.

## 1. What is tested

Source `d6b23c0`, build `d23094dfe42478f8a40907741120837c4cf952ff16b830c1e6e55697dc177db3`: `KYTY_GPU_WALL=1`
(measurement only, read once, no gate) arms `FrameTrace-x` counters `gw_idle_ns/_n` (waiting for work in
`ThreadRun`), `gw_blk_ns/_n` (all queues blocked), `gw_flip_ns/_n` (`FlipQueue::Wait` on the GuestGpu thread),
`gw_proc_ns/_n` (`GuestGpu::Process`), `gw_cmd_ns/_n` (queued commands). Gate `plkstat=1` in BOTH arms gives the
`PipelineCache::m_mutex` waits (`pl_prog/pipe/cs_wait_us`). Both instruments' own cost is in both arms.

## 2. The run — one, nothing else on the machine (no builds, compiles, scorers, agents), one repeat allowed only on
a fatal marker

`gw106`: `python C:/kyty/s106/enter_scene.py gw106 --hold 600 --attempts 1 --gates-file C:/kyty/s106/gates_base.txt
--pred C:/kyty/s106/pred/01_gwall.md "KYTY_GATE_SCHEDULE=90+1800:dawalk=0 dawalklead=1 plkstat=1|dawalk=1 dawalklead=1 plkstat=1"
KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1` (installs the build above;
`gates_base.txt` sha256 `303a7849…`). Repeat tag `gw106b` under the same text.

## 3. Admission (scorer `gw106.py`, derived from `dwk104.py` by `make_gw106.py`, run on two synthetic fixtures before
this seal — one planting the effect in R, one in the flip wait; each named its term)

The `dwk104` integrity and controls unchanged (pairs ≥ 60, bands, work split, area verdict and selection, pin
once, two record threads, no checkpoint line, no GpuHangAbort, no fatal marker incl. `AsyncPipelines: skipped
draw`, `KYTY_GPU_CHECKPOINTS` absent, identity of the installed exe), the `dwk104` arming (arm 0 walk dark, arm 1
armed, skip/posts identity ±1 %, drops ≤ 5 %, walks ±5 %, `mw_n`/`a_hold_us`/`a_mut_us`/`pl_em_n`/`pl_proc_n`/`sh_jobs`
dark), plus `GWALL_ARMED` (`gw_proc_n` ≥ 1 in both arms) and `PLKSTAT_ARMED` (`pl_prog_n` ≥ 1 in both arms);
`KYTY_GPU_WALL=1` in the launch environment.

## 4. Decomposition (per pair, arm 1 − arm 0, µs a flip)

`D = dt − cpu_net`; `idle = gw_idle_ns/1000`; `blk = gw_blk_ns/1000`; `flip = gw_flip_ns/1000`;
`lock = pl_prog_wait_us + pl_pipe_wait_us + pl_cs_wait_us`; `R = D − idle − blk − flip − lock` (other waits,
preemption, the loop outside the spans). Reported: `gw_proc`, `gw_cmd`, `uncovered = dt − idle − blk − proc − cmd`.

## 5. Rule

**R0:** D is reproduced if mean ΔD − 2 SE > 0; otherwise "D NOT REPRODUCED" and nothing is named. A term among
{idle, blk, flip, lock, R} is **NAMED** if its mean Δ ≥ ΔD / 2 and its t ≥ 3; none ⇒ **DIFFUSE**. Consequences
(ROADMAP item 3): a named term with a lever in the tree ⇒ a candidate by the Δ`dt` bar this session; R named,
DIFFUSE, or no lever ⇒ thread-placement candidates (`dapin=3`, a walker-only pin) recorded in ROADMAP before code.

## 6. Predictions (published whether hit or miss, no decision weight)

G1 ΔD in [+100, +300] · G2 arm-0 D level in [600, 1 100] · G3 ΔR ≥ ΔD/2 (preemption / other waits carry it) ·
G4 Δlock in [0, +100] · G5 Δflip in [−50, +50] · G6 Δ`dt` in [−450, −100].

## 7. Must not be claimed

A speedup (nothing ships); 60 FPS; that a named term is removable before a candidate is measured; any split of R.
