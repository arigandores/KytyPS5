**Session 91 found why two knobs were unmeasurable, built a one-site fix, and ran it: the game's DRS
budgets against GPU timestamps, a GPU timestamp on this emulator is the pacer-scaled CPU clock
written by GuestGpu at PM4 parse, and pinning that clock (`KYTY_GPU_CLOCK_PIN`) holds the rung —
adopted by a rule sealed before the runs.** Read `docs/ROADMAP.md` **§0.1 (the session-91 addendum)
first**, then `C:/kyty/s91/FACTS.md` (§0.1 first: ten defects of my own text, none of them the world
contradicting a sealed band).

Session 91's commits are on `merge-upstream`. **Source changed and was built twice; NO default
changed.** The installed `kyty_emulator.exe` is **`887ede9f8323297f…`, 23 623 680 bytes**, installed by
`pin91a` and not rebuilt since. Harness — **`C:/kyty/s91`**; port it to `C:/kyty/s92` with a script
written fresh in the SOURCE directory, modelled on `C:/kyty/s90/s91_port.py` (head of every
`--roots` chain; `area_verdict.py`'s `range(91, 70, -1)`). `gates_base.txt` **unchanged** — 1092 B,
99 names, sha256 `00c116dc…0594d8`. `KYTY_GPU_CLOCK_PIN` is an ENVIRONMENT variable (a positional
token to `enter_scene.py`), never a gate and never a schedule arm.

## 0. Read first

1. `docs/ROADMAP.md` §0.1 (session-91 addendum), §2 D (the session-91 block), §5 item 4, §7.
2. `C:/kyty/s91/FACTS.md` — §0.1, §8 (the pinned runs), §9.1 (the scoreboard), §10.
3. `C:/kyty/s91/PLAN.md` §0 A — the mechanism and why covariate adjustment and rung stratification
   were rejected. **It exists; do not redo it.**
4. `C:/kyty/s91/README.md` — the traps, above all: **`summary4.py`'s `cpu_net_us` is `cpu_gpu_us`
   under lite**; **a `Scope`'s ns column is 0 in lite**; **blocked time is invisible to `cpu_*_us`**.

## 1. What session 91 settled

* **The estimator that survives a DRS shift is the pin.** Mode 1 held the contrasts that failed
  admission in sessions 88 and 90 at 0.00 % HIGH (split +0.001 %, 110/110; +0.002 %, 123/123); mode 2,
  the positive control, sent the game to **native 3840×2160 in 100 % of flips** — the top of the
  ladder is 4K, not the 2432×1368 the record called "HIGH".
* **`dapin`'s GPU cost, eleventh session: +0.817 %, t +11.2 with the record path off** — the record
  thread is not the carrier; CPU −8.67 % a draw.
* **D1 is closed as a regression over the whole run at a fixed rung: `dt` +11.48 %, t +84.7.** The
  carrier: forced host-read drains (3.8 ms of GuestGpu a flip) and guest threads stalled 10.9 ms a
  flip in `SendCommandSync`.
* **The 64 KiB split is bimodal**: 46.7 % of upload regions, 3.41 % of the bytes, 48 µs inline on
  GuestGpu. **Handing the other ~40 regions to the copy pool costs GuestGpu 174 µs a flip.**
* TB (the total effect with a rung bracket, `shift91.py`) is the fallback for runs already on disk;
  its CPU brackets missed the pinned values by 0.22 and 0.27 pp — its CPU D is [I].

## 2. What is settled — do not reopen

`ROADMAP.md` §3, now including **D1**, **covariate adjustment on area**, **stratifying on the rung**,
and **the estimator question itself**. Route A; route C at slot and stage granularity; the program
and slot lookups; `CopyAheadResult`; merging draws; the whole-stage memo; removing the prefetch;
hoisting `AheadTake`.

## 3. The work — a coding session

### 3.1 FIRST: the pool hand-over, 174 µs a flip on GuestGpu

`CopyGuestToStaging` hands every ≥ 64 KiB region to `AsyncMemcpy`, which splits it into 1 MiB jobs
and queues them; `stg_pool_ns` says the GuestGpu thread pays **174 µs a flip for ~40 regions (22 MB)**
— 4.3 µs a region, more than the 48 µs of inline memcpy the pool exists to avoid. **Read before you
build:** `common/parallelCopy.{h,cpp}` (`AsyncMemcpy`, the job split, the queue lock, the wake, the
worker count `clamp(hw/2, 2, 7)`), and what `stg_pool_ns` actually brackets (it is the whole
`CopyGuestToStaging` call on the pooled branch, including `TryGetBackingPointer`). Candidates to
rank before a line is written: batch the whole upload's regions into one queue operation; raise the
job size; wake one worker per upload instead of per job; lower `ASYNC_COPY_MIN_BYTES` only if the
inline side is cheaper per byte. **Split `stg_pool_ns` first** — one mark between
`TryGetBackingPointer` and `AsyncMemcpy` — so the fix aims at the right line.

### 3.2 THEN: re-measure the rung-moving knobs WITH the pin

`pfhint`, `pfcap` and `dapin` (record path ON — the shipped configuration) were each measured at
whatever rung their run happened to hold. One pinned ABBA each; their defaults stay unless the
pinned contrast reverses the shipped decision.

### 3.3 The debts

* The `ObtainBuffer` stream ring: 19.66 MB a flip in 13 380 copies, never timed in a measurement run
  (its timer is `TimingsEnabled`-gated). The `hr_*` idiom (`Enabled()`) is the fix.
* The per-element price of `ResourceSpecialization::operator==`; the prefetch lines a take reads; the
  459.4 µs take; the witness share of `RebindImages`; route B items 2, 8, 10, 12, 3.

**Say the odds out loud.** 16.7 ms needs ~15 ms removed. The largest unshipped lever session 91
found is 174 µs. **Expect hundreds of microseconds, not milliseconds, and do not promise 60 FPS.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.** Measure it with the pin whenever the change can move GuestGpu's wall time.

## 4. Do NOT

* **Do not schedule the pin as an arm** — it is read once per process.
* **Do not trust an absolute-area band without running it on the record first**; the fragment rule
  "`rt_att` < 25 % of p50" misses one-vblank fragments carrying 25–35 % of the attachments.
* **Do not read "0 % HIGH" as evidence on a contrast that never moves the rung**; the pin's own
  evidence is `pin91a` + `pin91b`.
* **Do not quote `summary4`'s `cpu_net_us`**, and do not band a `Scope`'s ns column in lite.
* Carried: pre-registrations sealed in place and never edited; arming proved inside the run; ratios
  of sums; `guards.py` check 10 hashes the exe installed now; check 6 is not a criterion;
  `gen_gates.py --out` only with `--with`; never pipe a writing script through `head`; the first
  entry after a fresh build hangs (`--warmup-first`); `daepceil`'s comment says "(default 1)" and it
  is 0.
