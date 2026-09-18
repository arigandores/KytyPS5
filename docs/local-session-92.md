# Session 92 — FACTS

**The single source of truth for this session's numbers is `C:/kyty/s92/FACTS.md`**, of which this
file is the record in git. `pred/01_stglap.md` and `pred/02_wake.md` are sealed in place and were
not edited. `README.md` and `PLAN.md` inside `C:/kyty/s92` arrived from the port and still carry
session 91's headings — they are not this session's text.

Every number below is a **ratio of sums over its window** or a **paired mean over the programme's
cycles** (`summary4.build_cycles`, the same conventions as session 91), or an exact zero where the
counter is never `Add`ed. Labels: **[M]** measured in this session; **[I]** inference,
model-dependent or between-run.

Two binaries, and "the binary under test" would have been wrong: the measurement `stg92a` ran on
**`f1dfc3e842e4cf2403e3ed76d76f9836e58c749e1415fe50d4562b9ab5a1a1fb`** (23 624 704 B, the gate only),
the fix `wak92a` on **`563d8ecdafff4fcfb4cd2ba24456f326e22cd06a5bcfa852d0f06d55ed589fa3`**,
**23 626 240 B**, built twice with an identical hash; it is the exe installed in the game folder
now. Harness `C:/kyty/s92`, ported from `C:/kyty/s91` by `C:/kyty/s91/s92_port.py`, written fresh in
the SOURCE directory; port diagnostic clean; `gates_base.txt` **UNCHANGED** — 1092 B, 99 names,
sha256 `00c116dc…0594d8`.

**One gate, one knob, twelve counters. NO default moved. NOTHING SHIPPED.**

Runs: **`stg92a`** (measurement, `stglap=0|1`) and **`wak92a`** (the fix, `copywake=0|2`), **both
with `KYTY_GPU_CLOCK_PIN=1`** — the session-91 rule that any knob able to move GuestGpu's wall time
is measured with the clock pinned — and **both VALID**. Pre-registrations `pred/01_stglap.md`
(11 967 B, sha256 `b0a803ac…b381c`) and `pred/02_wake.md` (8 950 B, sha256 `84e6aaca…`) sealed in
place (`mtime − ctime` +0.003 / +0.002 s).

---

## 0. In one sentence

**The 174 µs a flip that GuestGpu pays to hand ~40 upload regions to the copy pool is 93.80 % one
thing — the condition-variable notify — and the fix that this run's own numbers prescribed was
built, run, and measured at 33.40 µs a flip, which is below the 60 µs usefulness threshold sealed
before the run, so `copywake` stays 0 and nothing was shipped.** The split is exact and the fix
works in the part it was designed for (`wakeN` 16.39 → 8.43 µs a call), but the half built on the
"sleeping worker" model — a bounded worker spin — removed nothing, burned 821 µs a flip of worker
time, and made the serial path measurably worse (`stg_lock_ns` +1.49 µs, t = +7.91). The largest
item left is the **single-chunk notify: 2.75 µs a call, 36.3 calls a flip = 99.9 µs a flip**, and it
is untouched.

### 0.1 Defects of my own text, listed first

1. **Band C2 was narrower than the quantity's own noise, and it failed.** `pred/01` §5 banded the
   arms' `stg_pool_n` at ≤ 0.5 %; `stg92a` read **0.599 %**. `stg_pool_n` has a block-to-block CV of
   **3.64 % / 4.00 % WITHIN an arm**, so at ~124 blocks two arms differ by ~0.47 % as one standard
   error. I dry-ran B1–B4 on the archive and printed C1–C4 as NOT EVALUABLE because the archive has
   no `stglap` contrast — **but `stg_pool_n` is live in every run and its dispersion was on disk the
   whole time.** Fifth band of this class in the programme.
2. **The first repair of C2 repeated the class it was written to fix.** `|t| < 3` alone read HIT on
   `pin91c`, where arm 1 stages nothing: the paired difference is the constant −100 %, its SE is 0,
   t comes out 0 — **a pass by degeneracy**. Caught only by dry-running the repair on the record.
   C2′ is `|t| < 3` **AND** `|whole-arm| ≤ 5 %`; it MISSES `pin91a` and `pin91c` and HITS `stg92a`.
3. **F1 was written on an assumption I labelled a bound and then banded as a measurement.** From
   `stg_chunks / stg_pool_n` = 1.2884 I inferred "~28.8 % of regions carry ≥ 2 chunks" and banded
   `stg_waken_n / stg_pool_n` at [0.25, 0.33]. Measured: **0.1151** — **11.5 % of the regions, at
   3.47 chunks each.** The ratio of sums never constrained the shape of the distribution.
4. **The fix `pred/01` §6 named for the measured carrier was refuted by the same run's own
   numbers** (§3.1). Naming a fix before the number did not stop me naming the wrong one; it did
   stop the number choosing its own fix.
5. `stg92.py` scores `A1`/`A2`/`B2`/`B5`/`C1`–`C4` only when exactly one arm is armed. `wak92a` arms
   `stglap` in BOTH arms on purpose, so those rows read NOT EVALUABLE there and the §6 verdict block
   does not print. **That is the tool being honest, not a failure** — but the tool was written for
   one contrast shape and silently does not cover the other.

---

## 1. What was done, and what was NOT

| step | state |
|---|---|
| harness `C:/kyty/s92`, ported by `C:/kyty/s91/s92_port.py` (written fresh in the SOURCE dir) | **clean**; `gates_base.txt` 1092 B, 99 names, sha256 `00c116dc…0594d8`, unchanged |
| `pred/01_stglap.md` sealed **before the emulator was opened** | 11 967 B, sha256 `b0a803ac…b381c`, `mtime − ctime` +0.003 s |
| `patch_s92.py` (the gate `stglap` and its six counters) | built; `stg92a` run on that build |
| `pred/02_wake.md` sealed **after `stg92a` and before the emulator was opened again** | 8 950 B, sha256 `84e6aaca…`, `mtime − ctime` +0.002 s |
| `patch_s92b.py` (the knob `copywake`, the spin, the six branch counters) | built **twice with an identical hash**: `563d8ecd…`, 23 626 240 B; `wak92a` run on it, and it is the exe installed now |
| **the runs `stg92a` and `wak92a`** | both admitted: `area_verdict` VALID, `guards` compared line by line, `summary4 --blocks`, `endpoint84` |
| the fix | **built, run, measured — and NOT shipped, by the rule sealed before the run** |
| defaults | **none moved.** `stglap` 0, `copywake` 0 |

`accept92.sh` is new and deliberately ends at step 4: `accept91.sh`, `accept90.sh` and `accept89.sh`
arrived in `C:/kyty/s92` as **byte copies still pointing at `C:/kyty/s91`** (resp. s90, s89) —
the port rewrites `.py` only, never `.sh`. Running `pin91.py` on a session-92 tag would score bands
sealed for `pin91a/b/c` and produce garbage, so it is absent by design, not by omission.

---

## 2. What was built (no default moved)

**Gate `stglap`** (`KYTY_STAGE_LAP`, default **0**, MEASUREMENT ONLY — never shippable) splits the
session-91 timer `stg_pool_ns` — the whole `CopyGuestToStaging` call, `bufferCache.cpp:1055-1057`,
left untouched as the whole against which the parts are checked — into:

| counter | what it brackets |
|---|---|
| `stg_res_ns` | `TryGetBackingPointer` |
| `stg_lock_ns` | `CopyPool::Enqueue` from entry to the end of its `lock_guard` |
| `stg_wake_ns` | the notify that follows that block |
| `stg_q` | `PendingAsyncCopies()` sampled BEFORE the enqueue (atomic load, no lock; a SUM over regions) |
| `stg_up_n` | calls of `UploadCopies` in which at least one region went to the pool |
| `stg_chunks` | `ceil(size / CHUNK_BYTES)` summed over pooled regions |

**Knob `copywake`** (`KYTY_COPY_WAKE`, default **0**, limit 2):

* **1** = at most `max(1, min(chunks, workers))` × `notify_one` instead of `notify_all` on a
  multi-chunk enqueue (kills the thundering herd);
* **2** = that, plus a bounded worker spin (`WORKER_SPIN_NS` 20 µs, with `SPIN_ITERATION_CAP` as a
  backstop) before the worker returns to `m_wake.wait`.

Its six counters, under the same gate: `stg_wake1_ns`/`_n` (the `chunks == 1` notify),
`stg_waken_ns`/`_n` (the multi-chunk notify), `stg_spin_ns`, `stg_spin_hit`.

**The knob is read at EVERY decision, not once per process** — that is what makes it a schedule arm,
and the within-run ABBA is the only A/B this programme accepts. **The first draft cached it in the
constructor; that would have made the fix unmeasurable, and it was caught before the run.**

---

## 3. `stg92a` — where the 174 µs go [M]

**VALID: area split +0.001 %, pairs 123/123, work +0.057 %, 0.0 % HIGH** (the pin holding the rung,
as session 91 adopted it).

| phase | µs a flip | share of `stg_pool_ns` |
|---|---:|---:|
| `stg_res_ns` — `TryGetBackingPointer` | 2.2 | 1.18 % |
| `stg_lock_ns` — under the queue lock | 5.8 | 3.13 % |
| **`stg_wake_ns` — the notify** | **173.5** | **93.80 %** |
| unnamed remainder | 3.5 | 1.89 % |

**Verdict by the rule sealed before the number (`pred/01` §6): carrier = `wake`, f_wake = 0.9380 ≥
0.55.** The notify costs **4.27 µs a region, on 40.6 regions a flip**; the armed arm's whole
hand-over is 185.0 µs.

All **18 bands HIT with C2′ substituted**: C1 `(res + lock + wake)/pool` = **0.98112**, C2′ t 1.40
with whole-arm 0.599 %, C3 (work) 0.05749, C4 (bytes) 0.15406. **The instrument's own price is not
detectable**: `cpu/draw` −0.005 % ± 0.126 %, t = −0.08; `cpu_net_us` +8.5 ± 86.9 µs, t = +0.20 (P5
HIT).

### 3.1 The two numbers that killed the fix that ranked first before the run

* `stg_pool_n / stg_up_n` = **1.00005** — **one pooled region per upload, so there is nothing to
  batch.** The `AsyncMemcpyBatch` that `pred/01` §6 named for the `lock` carrier, and the "at most
  one notify an upload" half it named for the `wake` carrier, are both no-ops. **P4 (≥ 3 regions an
  upload) is a MISS at 1.00005, and it takes the batching fix down with it.**
* `stg_q / stg_pool_n` = **0.430** — the queue is usually empty when a region arrives, so
  "do not wake a pool that is already awake" would rarely fire.

**Naming a fix before the number did not protect me from naming the wrong one. It did protect the
number:** the batching fix would have been built on a prediction the run refuted.

### 3.2 The control that failed, and its repair

C2 read 0.599 % against ≤ 0.5 % and MISSED. Under `pred/01` §5 no number of §6 may be published
until the instrument is repaired **under a new sealed pre-registration**; `pred/02` §§1–2 is that
repair, and the argument for it was made **without using the verdict it would license**: paired over
123 blocks the arms' `stg_pool_n` differ by −0.509 % ± 0.363 (SE), t = −1.40, against a within-arm
CV of 3.64 % / 4.00 %. C2′ = (`|t| < 3`) AND (`|whole-arm| ≤ 5 %`), dry-run on everything on disk
with two arms and a live `stg_pool_n`:

| run | whole-arm | paired | t | old band | **C2′** |
|---|---:|---:|---:|---|---|
| `stg92a` (arms differ only by the gate) | −0.591 % | −0.509 % ± 0.363 | −1.40 | MISS | **HIT** |
| `pin91a` (`dapin=0\|3` — a real path difference) | +9.793 % | +10.043 % ± 0.669 | +15.01 | MISS | **MISS** |
| `pin91c` (`bufimp=1\|2` — arm 1 stages nothing) | −100.000 % | −100.000 % ± 0.000 | ∞ | MISS | **MISS** |

**C2′ can fail, and it fails on both runs whose arms really do take different paths.** f_wake =
0.9380 is 0.39 absolute above its 0.55 threshold and C2's 0.6 % could not have moved it — but that
is an argument made *after* the fact and is not why the control was repaired.

---

## 4. `wak92a` — the fix measured [M]

**VALID: area split −0.002 %, pairs 124/124, work −0.042 %, 0 hang markers** (F5, correctness,
outranks every number here: `WaitAsyncCopies` still returns only on an empty queue and no `acopy=`
marker appeared in `GpuWaitSlow` / `GpuHangAbort` — **a lost wake-up is a hang, not a slow frame**).

| quantity | `copywake=0` | `copywake=2` | paired difference |
|---|---:|---:|---|
| `stg_pool_ns` a flip | 191.60 µs | 158.22 µs | **−33.40 ± 1.63 (2·SE), t = −40.97** |
| `stg_wake_ns` a flip | 177.26 | 142.56 | −34.73 ± 1.55, t = −44.82 |
| `stg_lock_ns` a flip | 8.02 | 9.50 | **+1.49 ± 0.38, t = +7.91** |
| `wake1` per call (chunks = 1) | 2.7513 µs | 2.7931 µs | **unchanged** |
| **`wakeN` per call (chunks > 1)** | **16.3931 µs** | **8.4287 µs** | **halved** |
| `stg_spin_ns` a flip (all workers) | 0.02 µs | **821.13 µs** | the spin's price |
| `stg_spin_hit` a flip | 0.0008 | 16.57 | — |
| `cpu_net_us` (`endpoint84`) | — | — | **−51.3 ± 82.3 µs, t = −1.25** |

Identity F2 — `stg_wake1_ns + stg_waken_ns == stg_wake_ns` — reads **1.000000** in both arms.

### 4.1 The verdict, by the usefulness rule sealed in `pred/01` §7 and repeated as `pred/02` F3

**33.40 µs < 60 µs ⇒ THE FIX IS NOT SHIPPED. `copywake` stays 0.**

The threshold was set before the run against the harness's own integral resolution, and the run
confirmed the reasoning it was built on: at 33 µs the integral endpoint reads **t = −1.25 and cannot
see it** (Q4 HIT — the endpoint moves only above ~130 µs; F4's disagreement clause never fired
because `stg_pool_ns` did not fall by ≥ 120 µs).

### 4.2 What the split says that the total does not

* **All of the saving is the broadcast.** `wakeN` fell 16.39 → 8.43 µs a call — **−37.6 µs a flip**
  — while `wake1` did not move at all (2.7513 → 2.7931). **Part 1 of the fix works and costs
  nothing.**
* **The spin did nothing and was not free.** 821 µs a flip of worker time, 16.57 hits a flip, and
  the price it was built to remove — the single-chunk notify — **did not fall at all**. It also cost
  the serial thread: `stg_lock_ns` +1.49 µs a flip at t = +7.91, despite `m_pending` being given its
  own cache line.
* **Therefore the mechanism is NOT "waking a sleeping thread".** With 7 workers and a usually-empty
  queue, some worker is always in `m_wake.wait`, so `notify_one` pays a kernel wake whether or not
  this particular worker spun. The spin cannot help, and its 40 % hit rate bought no latency that
  GuestGpu could see.
* **`copywake=1` alone is the part worth anything, and it was NOT measured in isolation — its
  −37.6 µs is [I].**

---

## 5. The scoreboard

**Predictions: 10, of which 8 HIT and 2 MISS** — P6 is not independent, it restates band B2, and
an earlier count of this scoreboard said 9 by quietly dropping it.

| # | reading | verdict |
|---|---|---|
| P1 | the carrier is `lock` or `wake`, not `res` | **HIT** (f_wake 0.9380) |
| P2 | remainder `r` < 0.40 | **HIT** at 0.0189 |
| P3 | `stg_q / stg_pool_n` < 1.0 | **HIT** at 0.430 |
| **P4** | ≥ 3 pooled regions an upload | **MISS** at 1.00005 |
| P5 | the instrument is invisible at \|t\| ≥ 3 | **HIT** (t = +0.20) |
| Q1 | `stg_waken_ns` < `stg_wake1_ns` | **HIT** |
| Q2 | the multi-chunk branch ≥ 2× the single-chunk one per call | **HIT** at 5.96× |
| **Q3** | the fix removes ≥ 60 µs a flip | **MISS** at 33.40 |
| Q4 | the endpoint moves only above ~130 µs | **HIT** |

(`pred/01` P6 — `stg_chunks / stg_pool_n` < 1.60 — restates band B2 and is counted there, HIT at
1.2884, not a tenth prediction.)

**Bands: 23, of which 21 HIT and 2 MISS** — `stg92a` **18/18 with C2′ substituted** (C2 as
originally written MISSED, §0.1 item 1), `wak92a` **F2 / F4 / F5 HIT and F1 MISS** (§0.1 item 3).

**Both prediction misses and both band misses are defects of text I wrote myself** — P4's premise,
Q3's optimism, C2's width, F1's assumed distribution. **That is four of four.** No sealed band was
contradicted by the world; all four were contradicted by me.

---

## 6. Traps of this session

* **A band on a quantity whose own block-to-block CV you have not looked at is a band you cannot
  read** — and the CV of a live counter is on disk in every archived run, contrast or no contrast.
* **`|t| < k` alone passes by degeneracy when one arm is a hard zero** (a constant difference ⇒
  SE 0 ⇒ t 0). Pair it with an absolute guard.
* **A ratio of sums does not constrain the distribution behind it**: 1.2884 chunks a region is
  11.5 % of regions at 3.47 chunks, not 28.8 % at 2.
* **A knob that a schedule must flip cannot be read once per process.** The measurable fix and the
  unmeasurable one differ only by where the read sits.
* **A loop whose only exit depends on a clock hangs wherever that clock reads 0** —
  `FrameStats::NowNs()` is Windows-only and returns 0 elsewhere (`frameStats.cpp:197-211`).
* **A spin that "hits" 40 % of the time can still buy nothing**: the thing it removes must be the
  thing that is actually paid.
* **The tool that scores a sealed text is written for one contrast shape**; run it on the other and
  it goes quiet rather than wrong — **check which rows printed**.
* Carried and still standing: `summary4.py`'s `cpu_net_us` **is** `cpu_gpu_us` under lite (read
  `endpoint84.py`); a `Scope` times only under `TimingsEnabled` and its ns column is structurally 0
  in lite; `guards.py` check 6 is not a criterion and check 10 hashes the exe installed **now**;
  `gen_gates.py --out` only with `--with`; never pipe a writing script through `head`; the port
  rewrites `.py` only, so every `.sh` in a fresh harness still points at the old one.

---

## 7. What is NOT closed

| debt | the number, as it stands | since |
|---|---|---|
| ~~where the 174 µs pool hand-over goes~~ | **CLOSED: 93.80 % is the notify** (res 1.18 %, lock 3.13 %, remainder 1.89 %) | 91 → **92** |
| **the single-chunk notify** | **2.75 µs a call, 36.3 calls a flip = 99.9 µs a flip, untouched by anything this session built.** Its mechanism is NOT "a sleeping worker" — with 7 workers one is always waiting. Candidates nobody has measured: fewer workers; a count of awake workers so an enqueue can skip the notify; handing the region over without a notify and waking once before submit | **92** |
| **`copywake=1` in isolation** | the part that worked, never measured alone — **−37.6 µs is [I]** | **92** |
| the `ObtainBuffer` stream ring | 19.66 MB a flip in 13 380 copies; its timer is dead in lite — the `hr_*` (`Enabled()`) idiom is the fix | 90 |
| `pfhint`, `pfcap`, `dapin` with the record path ON | each was read at whatever rung its run happened to hold; one pinned ABBA each | 91 |
| the per-element price of `ResourceSpecialization::operator==` | a counter on the vector lengths | 90 |
| prefetch lines read (s89), the 459.4 µs take unsplit (s89), the witness share of `RebindImages` (s88), route B items 2, 8, 10, 12, 3 | unchanged | 83–89 |

---

## 8. The arithmetic, said plainly

60 FPS = **16 667 µs**. Shipped base **31 642 µs = 31.60 FPS** (`acc82a`, not re-measured here). The
entire hand-over is **185–192 µs a flip — 0.6 % of the frame**. The ceiling of the whole subject,
including the inline memcpy, is **≈ 233 µs — 0.74 %**.

**This session measured a 174 µs object exactly, built the fix its own rule prescribed, ran it, got
33.4 µs, and did not ship it. That is the correct outcome of the rule, and it does not move the
frame.** Nothing here removes work from the shipped configuration, and no default moved.
