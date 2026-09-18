**Session 92 split the 174 µs pool hand-over exactly — 93.80 % of it is the condition-variable
notify — then built the fix its own sealed rule prescribed, ran it, measured 33.40 µs a flip against
a 60 µs threshold sealed BEFORE the run, and did not ship it.** `copywake` stays 0, `stglap` stays 0,
no default moved, nothing shipped. Read `docs/ROADMAP.md` first, then `C:/kyty/s92/FACTS.md` — **§0.1
first: five defects of my own text, and all four of the session's misses are among them; none of them
is the world contradicting a sealed band.**

Session 92's commits are on `merge-upstream`. **Source changed and was built twice; NO default
changed.** The installed `kyty_emulator.exe` is
**`563d8ecdafff4fcfb4cd2ba24456f326e22cd06a5bcfa852d0f06d55ed589fa3`, 23 626 240 bytes**, and was not
rebuilt after acceptance. Harness — **`C:/kyty/s92`**; port it to `C:/kyty/s93` with a script written
**fresh in the SOURCE directory**, modelled on `C:/kyty/s91/s92_port.py`. `gates_base.txt`
**unchanged** — 1092 B, 99 names, sha256 `00c116dc…0594d8`. `KYTY_GPU_CLOCK_PIN` is an ENVIRONMENT
variable (a positional token to `enter_scene.py`), read once per process, never a gate and never a
schedule arm.

## 0. Read first

1. `docs/ROADMAP.md` — where we are, §0.1 (what is PROVEN and what is NOT about 60 FPS), §3 (what is
   closed), §5 (the order of decisions), §7 (the open debts).
2. **`C:/kyty/s92/FACTS.md` — §0.1 FIRST** (the five defects), then §2 (the split), §3 (the fix),
   §4 (the scoreboard), §5 (the traps), §6 (not closed), §7 (the arithmetic).
3. **The sealed pre-registrations in `C:/kyty/s92/pred/`** — `01_stglap.md` (11 967 B, sha256
   `b0a803ac…b381c`) and `02_wake.md` (8 950 B, sha256 `84e6aaca…`). `01` §6 is the verdict rule and
   §7 the usefulness rule; `02` §§1–2 is the repair of control C2 and the demonstration that a repair
   can repeat the class it repairs; `02` §5 is the fix and its bands. **Sealed in place — do not
   edit them, and do not edit `C:/kyty/s92/FACTS.md` or `README.md` either.**
4. `C:/kyty/s92/accept92.sh` — the admission order, and its warning: **the port rewrites `.py` only**,
   so `accept91.sh`/`accept90.sh`/`accept89.sh` sit in `s92` as byte copies still pointing at the
   OLD harness. `README.md` and `PLAN.md` in `s92` still carry session 91's headings for the same
   reason; they are not session 92's text.

## 1. What session 92 settled

* **The hand-over is the notify.** `stg92a` (`stglap=0|1`, pinned, VALID: split +0.001 %, pairs
  123/123, work +0.057 %, 0.0 % HIGH): `stg_res_ns` 2.2 µs (1.18 %), `stg_lock_ns` 5.8 µs (3.13 %),
  **`stg_wake_ns` 173.5 µs (93.80 %)**, remainder 3.5 µs (1.89 %) of a 185.0 µs hand-over.
  **4.27 µs a region on 40.6 regions a flip.** Controls: C1 0.98112, C2′ t 1.40, C3 0.05749,
  C4 0.15406. The instrument is invisible: `cpu_net_us` +8.5 ± 86.9 µs, t = +0.20.
* **The batching fix that ranked first before the run is dead**: `stg_pool_n / stg_up_n` =
  **1.00005** — one pooled region per upload, nothing to batch (P4 MISS). And `stg_q / stg_pool_n` =
  **0.430** — the queue is usually empty, so "don't wake an awake pool" would rarely fire.
* **The fix was built, run and NOT shipped.** `wak92a` (`copywake=0|2`, pinned, VALID: split
  −0.002 %, pairs 124/124, work −0.042 %, 0 hang markers): `stg_pool_ns` **−33.40 ± 1.63 (2·SE),
  t = −40.97**. **33.40 < 60 ⇒ the fix is not shipped** by `pred/01` §7 / `pred/02` F3, sealed before
  the run. `copywake` stays 0.
* **Half the fix works; the other half is refuted.** `wakeN` 16.3931 → 8.4287 µs a call (−37.6 µs a
  flip, the `notify_all` → bounded `notify_one` part); **`wake1` did not move at all** (2.7513 →
  2.7931). The bounded worker spin burned **821.13 µs a flip** of worker time at 16.57 hits a flip
  and cost the serial thread `stg_lock_ns` **+1.49 µs, t = +7.91**.
* **Therefore the mechanism is NOT "waking a sleeping thread"**: with 7 workers and a usually-empty
  queue, one worker is always in `m_wake.wait`, so `notify_one` pays a kernel wake regardless.
* Identity F2 (`stg_wake1_ns + stg_waken_ns == stg_wake_ns`) = **1.000000** in both arms; F5
  (correctness) held — no lost wake-up, no `acopy=` hang marker.
* **Scoreboard: 10 predictions, 8 HIT / 2 MISS (P6 restates band B2); 23 bands, 21 HIT / 2 MISS.
  All four misses are
  defects of text I wrote myself** (P4's premise, Q3's optimism, C2's width, F1's assumed
  distribution).

## 2. What is settled — do not reopen

`ROADMAP.md` §3, plus everything session 91 closed: the pin as this programme's estimator for
rung-moving knobs; D1 (`bufimp`) as a frame-time regression; the 64 KiB split as bimodal; covariate
adjustment on area; stratifying on the rung; the estimator question itself. Route A; route C at slot
and stage granularity; the program and slot lookups; `CopyAheadResult`; merging draws; the
whole-stage memo; removing the prefetch; hoisting `AheadTake`.

**New this session, do not redo:** the split of `stg_pool_ns` (it is 93.80 % notify — measured, not
inferred); `AsyncMemcpyBatch` / "one notify an upload" (dead at `stg_pool_n / stg_up_n` = 1.00005);
"don't wake an awake pool" (dead at `stg_q / stg_pool_n` = 0.430); and the bounded worker spin
(`copywake=2`), which was built and measured at **zero effect on `wake1` and +821 µs of worker
time** — **do not build it again in another shape without first refuting the mechanism finding.**

## 3. The work — a coding session

### 3.1 FIRST: the single-chunk notify, 99.9 µs a flip

**2.75 µs a call, 36.3 calls a flip = 99.9 µs a flip**, untouched by anything session 92 built. It is
now the largest single item in the hand-over, and **its mechanism is known not to be "a sleeping
worker"** — the spin proved that. Read `common/parallelCopy.{h,cpp}` before a line is written (the
worker count `clamp(hw/2, 2, 7)`, the queue lock, `m_wake`, the job split at `CHUNK_BYTES`), and note
that a worker takes the lock twice a job.

Candidates, **none of them measured, all of them needing a mechanism named before a patch**:

1. **Fewer workers.** With 7 the pool always has a waiter; the wake is paid every time. Fewer workers
   is one knob and it changes both the wake cost and the copy latency — so it needs both endpoints.
2. **A count of awake/running workers**, so an enqueue can skip the notify when a worker is provably
   still draining. Note `stg_q / stg_pool_n` = 0.430 says the queue is usually empty — the counter
   must count *awake*, not *queued*, or it repeats the dead idea.
3. **Hand the region over without a notify and wake once before submit.** This is the only candidate
   that removes the per-region wake entirely; it is also the one that can lose a wake-up, so F5's
   correctness rule outranks its number: `WaitAsyncCopies` must still return only on an empty queue,
   and `acopy=` must never appear in `GpuWaitSlow`/`GpuHangAbort`. **A lost wake-up is a hang, not a
   slow frame** (session 58 shipped `acopyidle` for exactly that).

**Rank them, then apply the usefulness rule before building:** at 99.9 µs a flip the whole item is
above 60 µs only if a candidate takes essentially all of it. Say the predicted saving out loud, in
µs a flip, in the sealed text, before the patch.

### 3.2 THEN: `copywake=1` in isolation

The part that worked was never measured alone: **its −37.6 µs a flip is [I]**, inferred from the
`wakeN` per-call change inside the `copywake=0|2` contrast. One pinned ABBA `copywake=0|1` settles
it. It will not on its own clear 60 µs, so **measure it to know the number, and do not ship it on
that number alone** unless it is combined with §3.1's carrier.

### 3.3 The debts (`FACTS.md` §6)

* The `ObtainBuffer` stream ring: **19.66 MB a flip in 13 380 copies**, never timed in a measurement
  run — its timer is `TimingsEnabled`-gated and structurally 0 in lite. The `hr_*` / `Enabled()`
  idiom is the fix.
* `pfhint`, `pfcap` and `dapin` **with the record path ON**, each re-measured with the pin — they
  were read at whatever rung their run happened to hold.
* The per-element price of `ResourceSpecialization::operator==`; the prefetch lines a take reads; the
  459.4 µs take unsplit; the witness share of `RebindImages`; route B items 2, 8, 10, 12, 3.

### 3.4 The port — three root chains, and they are three separate edits

Port `C:/kyty/s92` → `C:/kyty/s93` with a script **written fresh in the SOURCE directory**
(`C:/kyty/s92/s93_port.py`), modelled on `C:/kyty/s91/s92_port.py`. A literal text replacement drops
the previous root out of every chain, so fix all three:

1. **the head of every `--roots` default** (`arms.py`, `baseline.py`, `effect.py`): the new root goes
   in FRONT and `s92` stays in the list;
2. **`area_verdict.py`** — `DEFAULT_CSV_ROOTS = ... range(92, 70, -1)` → `range(93, 70, -1)`;
3. **`shift91.py`** — `ROOTS = ... range(92, 66, -1)` → `range(93, 66, -1)`.

Then: `gates_base.txt` must come across **byte-identical** (1092 B, 99 names, sha256
`00c116dc…0594d8`); `gen_gates.py` in `--check` mode only; `.txt`/`.json` copied byte-exact; and
**write `accept93.sh` new** — the `.sh` files are copied verbatim and still point at the old harness.
`accept92.sh` deliberately ends at step 4 because `pin91.py` scores bands sealed for `pin91a/b/c`;
session 93 adds its own step 5 pointing at its own sealed pre-registration, not at an old scorer.

**One more tool defect to carry:** `stg92.py` scores `A1`/`A2`/`B2`/`B5`/`C1`–`C4` only when exactly
one arm is armed, so a contrast that arms `stglap` in BOTH arms reads NOT EVALUABLE and the verdict
block does not print. **Check which rows printed before reading a scoreboard.**

**Say the odds out loud.** The whole subject — hand-over plus inline memcpy — is **≈ 233 µs a flip,
0.74 % of a shipped 31 642 µs frame**. 60 FPS = 16 667 µs, so ~15 000 µs must come off. **This is
worth tens to hundreds of microseconds and it does not reach 60 FPS. Do not promise 60 FPS.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.** Measure it with `KYTY_GPU_CLOCK_PIN=1` whenever the change can move GuestGpu's wall time.

## 4. Do NOT

* **Do not ship `copywake` without a number ≥ 60 µs a flip.** The rule was sealed before the run, it
  produced the right answer at 33.40 µs, and re-reading it afterwards to let a 33 µs fix through is
  the one thing that would make the rule worthless.
* **Do not read a knob that the schedule must flip once per process.** The measurable fix and the
  unmeasurable one differ only by where the read sits — session 92's first draft cached `copywake`
  in the constructor and it was caught before the run, not by the run.
* **Do not band a quantity whose block-to-block dispersion you have not looked at.** `stg_pool_n`'s
  within-arm CV is 3.64 % / 4.00 %; a 0.5 % band on it fails about half the time whatever the gate
  does. The CV of a live counter is on disk in every archived run, contrast or no contrast.
* **`|t| < k` on its own passes by degeneracy** when one arm is a hard zero: the difference is
  constant, SE is 0, t is 0, and the control reads HIT while proving nothing. Always pair it with an
  absolute guard (C2′ = `|t| < 3` AND `|whole-arm| ≤ 5 %`).
* **A ratio of sums does not constrain the distribution behind it.** 1.2884 chunks a region turned
  out to be 11.5 % of regions at 3.47 chunks, not 28.8 % at 2 — and F1 was banded on the wrong one.
* **A loop whose only exit depends on a clock hangs wherever that clock reads 0** —
  `FrameStats::NowNs()` is Windows-only and returns 0 elsewhere (`frameStats.cpp:197-211`). Any spin
  or budget loop needs an iteration cap as well.
* **Do not quote `summary4.py`'s `cpu_net_us`** — under lite it **is** `cpu_gpu_us`, and the tool
  says so in its own NOTE. The endpoint is `endpoint84.py`.
* **`guards.py` check 6 is not a criterion** (compare the check LINES), and **check 10 hashes the exe
  installed at that moment** — never rebuild between acceptance and the final answer.
* **`gen_gates.py --out X` without `--with` ignores `--out` and overwrites `gates_base.txt`.**
* **Never pipe a writing script through `head`** — SIGPIPE kills it before it writes.
* Carried: pre-registrations sealed in place and never edited; a failed control is REPAIRED under a
  NEW sealed pre-registration, and the repair is dry-run on the record before sealing; arming proved
  inside the run; ratios of sums, never per-frame identities; a run that fails admission is REPLACED,
  not discussed, and its contrast is quoted nowhere; the first entry after a fresh build hangs
  (`--warmup-first`); a `Scope`'s ns column is structurally 0 in lite; `daepceil`'s comment still
  says "(default 1)" and it is 0.
