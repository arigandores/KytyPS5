# Session 93 — FACTS

**The single source of truth for this session's numbers is `C:/kyty/s93/FACTS.md`**, of which this
file is the record in git. `pred/01_bdacap.md` is sealed in place and was not edited. `README.md`
and `PLAN.md` inside `C:/kyty/s93` arrived from the port and still carry session 91's headings —
they are not this session's text.

Every number below is a **ratio of sums over its window** or a **paired mean over the programme's
cycles** (`summary4.build_cycles`, the conventions of sessions 91 and 92), or an exact zero where
the counter is never `Add`ed. Labels: **[M]** measured in this session; **[U]** an assumption
carried into the arithmetic and marked as such; **[I]** inference, model-dependent or between-run.

Binary under test: **`6992a96ac76e7ea9015b12d061852111d4c70fe2895784d6e9ab61a2fb9b45f1`**,
**23 628 800 B**, built twice with an identical hash. Harness `C:/kyty/s93`, ported from
`C:/kyty/s92` by `C:/kyty/s92/s93_port.py`, written fresh in the SOURCE directory; port diagnostic
clean; `gates_base.txt` **UNCHANGED** — 1092 B, 99 names, sha256 `00c116dc…0594d8`.

**One gate, ten counters. NO default moved. NOTHING SHIPPED.**

One run: **`bl93a`** (`bdacap=0|1`, `drawmerge=1` in both arms, **`KYTY_GPU_CLOCK_PIN=1`** — the
session-91 rule), **VALID**. Pre-registration `pred/01_bdacap.md` (9 836 B, sha256 `a79661bd…`)
sealed in place (`mtime − ctime` +0.002 s).

---

## 0. In one sentence

**Of the 47 607 buffer slots a flip, 37.48 % are candidates that a device address could carry, and
the ceiling of moving them is 7 198.9 µs a flip — which is LICENSED by the rule sealed before the
number, but 78 % of that ceiling is an unproven assumption and the whole of it is 48 % of the
15 000 µs that must come out.** The measured half is `Ceiling_bind` = **1 552.9 µs**; strike the
assumption and the same sealed table reads **CLOSED**. Nothing was built, nothing was shipped, no
default moved.

### 0.1 Defects of my own text, listed first

1. **Band A1 demanded an exact zero on a schedule arm, which this programme has already recorded as
   unreachable — twice.** It read **56 frames of 3651** with a non-zero class in the unarmed arm.
   **All 56 sit at distance 29 of 30 from the start of their block** — the last frame of a block,
   i.e. the reporting interval that straddles the gate flip — and the total is **0.0054 % of the
   armed value**. The instrument is sound and the band was wrong. Session 88 wrote that an exact
   zero on a schedule arm is still unreachable and that it had written it again; **this is the third
   time.**
2. **Band B3 imported a number from a different classification.** It banded `bc_ring / bb_n` at
   [0.25, 0.45] on the strength of session 86's `dm_ring / dm_bufn` = 0.3506, and read **0.0183**.
   Not a contradiction: my own order checks const-bank BEFORE ring, and const-bank is 58 % of all
   slots, so most of what session 86 counted as "ring" is counted here as `bc_cb`. **A band taken
   from another tool's partition measures the partition, not the world.**
3. **Control A3 could not fire, and I knew the reason before writing it.** It compares `bc_all_ns`
   with the shipped `bl_buf_us`, which is a `Scope` and therefore structurally 0 under lite — the
   trap session 91 recorded in its own README. **NOT EVALUABLE by construction.**
4. **`bda93.py` picks the armed arm by `bc_ok > 0`**; with the straddle of item 1 both arms
   qualified, and the tool printed **every band as NOT EVALUABLE** instead of scoring them. The
   numbers in §3 are my own computation over the same window, and the tool's defect is recorded
   rather than patched after the fact.

---

## 1. What was done, and what was NOT

| step | state |
|---|---|
| harness `C:/kyty/s93`, ported by `C:/kyty/s92/s93_port.py` (written fresh in the SOURCE dir) | **clean**; `gates_base.txt` 1092 B, 99 names, sha256 `00c116dc…0594d8`, unchanged |
| `pred/01_bdacap.md` sealed **before the emulator was opened** | 9 836 B, sha256 `a79661bd…`, `mtime − ctime` +0.002 s |
| `patch_s93.py` (the gate `bdacap` and its ten counters) | built **twice with an identical hash**: `6992a96a…`, 23 628 800 B; it is the exe installed now |
| the run **`bl93a`** | admitted in order: `guards.py --first-frame 2100` (**8 PASS / 0 FAIL**) → `area_series.py` + `area_verdict.py` → `summary4.py --blocks` → `endpoint84.py` |
| a prototype | **not built.** This session measured a ceiling; the verdict rule licenses a prototype, it does not contain one |
| defaults | **none moved.** `bdacap` 0 |

**Reading, not building, decided the subject.** The scouting that preceded `pred/01` established
that the candidate at this scale is **not** `VK_EXT_descriptor_indexing`: `descriptorIndexing`,
`runtimeDescriptorArray` and every `descriptorBinding*` feature are **not requested anywhere in the
tree** (`vulkanWindow.cpp:68-77`), whereas **`bufferDeviceAddress` IS enabled** (`:74`), a table of
device addresses for every registered buffer **already exists and is already maintained** on
registration boundaries (`bufferCache.cpp:139-145`), and the shader side already reads through it
(`spirvEmitterMemory.cpp:997-1047`). **The only missing piece is that no V# slot uses it** —
`uses_dma` is set only for variant V#s, `ReadConst` and BVH (`ResourceTracking.cpp:814, 880, 906,
960`). So the question was a ceiling, not a build.

---

## 2. What was built (no default moved)

**Gate `bdacap`** (`KYTY_BDA_CAP`, default **0**, MEASUREMENT ONLY — never shippable). Every buffer
slot built by `NativeStorageBuffer` (`descriptors.cpp:145-355`) gets exactly one class, **first
match wins**, at each of the function's four return sites:

| counter | class | why |
|---|---|---|
| `bc_null` | no buffer (address or size 0) | nothing there |
| `bc_fmt` | `resource.formatted` — a texel view | **BDA cannot express it** |
| `bc_cb` | const-bank — a uniform view | **BDA cannot express it** |
| `bc_ring` | the stream ring, including the third path where `ObtainBuffer` itself returns it (`bufferCache.cpp:1315`) | its offset is new every draw, so an address buys nothing |
| **`bc_ok`** | **anything else: a cached buffer with a stable handle** | **the candidate population** |

Plus `bc_ok_b` (their bytes), **`bc_ok_ns`** (the time `NativeStorageBuffer` itself spends on them —
the direct ceiling, not a rate times a population), `bc_all_ns` (the same timer over all five
classes), `bc_dma` (draws where at least one stage already carries `uses_dma`), and **`dm_buf1_ok`**
— of the draws differing from the previous by exactly one non-ring buffer slot, those whose
differing slot is `bc_ok`. `dm_buf1_ok` needs gate **`drawmerge`** (session 86), which is therefore
**armed in BOTH arms so its price cancels in the contrast**.

---

## 3. `bl93a` — the measurement [M]

**VALID: area split −0.000 %, pairs 121/121, work −0.034 %, 0 hang markers, guards 8 PASS / 0 FAIL.**

| class | slots a flip | share of `bb_n` |
|---|---:|---:|
| **`bc_cb`** — uniform view, **BDA cannot express it** | **27 672.5** | **58.13 %** |
| **`bc_ok`** — the candidate population | **17 844.8** | **37.48 %** |
| `bc_null` | 1 129.1 | 2.37 % |
| `bc_ring` | 871.4 | 1.83 % |
| `bc_fmt` — texel view, BDA cannot express it | 86.5 | 0.18 % |
| **sum against `bb_n` = 47 606.9** | **47 604.3** | **0.999945** |

`sl_over` = **0.000** a flip — no slot sits past index 32, so **nothing is hidden from the
comparison**.

### 3.1 The one favourable number

**`dm_buf1_ok` = 881.88 a flip against `dm_buf1_nr` = 881.93 — ratio 0.9999.** Practically every
draw that differs from its predecessor by exactly one non-ring buffer slot differs by a slot that
BDA could carry. **That is the single most favourable number of this session**, and it is the
population on which the [U] half of the ceiling is built.

---

## 4. The ceiling, by the rule sealed before the number

| term | value | status |
|---|---:|---|
| `Ceiling_bind` = `bc_ok_ns` | **1 552.9 µs a flip** | **measured directly [M]** |
| draw price = `cpu_gpu_us / draws` | 6.402 µs | **[U]** |
| `Ceiling_merge` = 881.88 × 6.402 | **5 646.0 µs a flip** | **[U]** |
| **`Ceiling_total`** | **7 198.9 µs a flip** | **LICENSED** (threshold 5 000) |

**The verdict must be read with its own arithmetic in view, and the arithmetic is not flattering.**

* **78 % of the ceiling is the [U] term**, which assumes a merged draw costs nothing — **exactly the
  assumption session 86 refused to record as a saving** (`ROADMAP.md:676-678`). **Strike it and
  1 552.9 µs remains, which by the same sealed table is CLOSED.** The verdict LICENSED therefore
  rests on a quantity nobody has measured, and saying so is the point of this paragraph.
* **`Ceiling_bind` is itself an upper bound in the safe direction**: `bc_ok_ns` brackets the whole
  function, so it includes `ObtainBuffer` and `InvalidateMemoryFromGPU` — work a converted slot
  probably still pays, because something must still register and synchronise the buffer.
* **7 198.9 µs is 48 % of the 15 000 µs that must come out.** Even realised in full, **this route
  does not reach 16 667 µs alone**, and no second lever of this size is known.

### 4.1 The instrument's own price, reported not hidden

`endpoint84`: **+574.9 ± 83.3 µs, t = +13.80** on 121 pairs; `cpu/draw` **+1.859 % ± 0.152 %,
t = +24.44**. Ten `Add`s over 47 600 slots is **≈ 12 ns a slot**. Prediction R5 (visible at
|t| ≥ 3) **HIT** — the instrument was predicted to be seen, and it was.

---

## 5. The scoreboard

**Bands: 7 scored, 5 HIT and 2 MISS.**

| band | reading | verdict |
|---|---|---|
| A2 | parts sum to the whole | **HIT** at 0.999945 |
| B1 | `bb_n` a flip ∈ [45 000, 52 000] | **HIT** at 47 606.9 |
| B2 | `draws` a flip ∈ [4 900, 5 200] | **HIT** at 5 037.1 |
| B4 | `bc_null / bb_n` < 0.10 | **HIT** at 0.0237 |
| C2 | `bc_fmt + bc_cb` > 0 | **HIT** at 27 759.0 |
| **A1** | exact zero on the unarmed arm | **MISS** — the straddle (§0.1 item 1) |
| **B3** | `bc_ring / bb_n` ∈ [0.25, 0.45] | **MISS** at 0.0183 — an imported partition (§0.1 item 2) |
| A3 | `bc_all_ns` against `bl_buf_us` | **NOT EVALUABLE by construction** (§0.1 item 3) |

**Predictions: 5, of which 4 HIT and 1 MISS.**

| # | reading | verdict |
|---|---|---|
| R1 | `bc_ok / bb_n` ∈ [0.30, 0.60] | **HIT** at 0.3748 |
| R2 | `Ceiling_bind` < `Ceiling_merge` | **HIT**, 1 553 < 5 646 |
| **R3** | `Ceiling_total` < 5 000 µs | **MISS** at 7 199 |
| R4 | `bc_dma / draws` < 0.10 | **HIT** at 0.0350 |
| R5 | the instrument is visible at \|t\| ≥ 3 | **HIT** at t = +13.80 |

**R3 was my own route being predicted to fail, and it did better than I said** — the single miss of
the prediction set is a route beating its author's pessimism, which is the one kind of miss this
record has not produced before.

**Both band misses are defects of text I wrote myself**, and **one of them repeats a defect this
record has already named twice** (the exact zero on a schedule arm). No sealed band was contradicted
by the world.

---

## 6. Traps of this session

* **An exact zero cannot be demanded on a schedule arm**: the reporting interval straddles the flip,
  and the offenders land at the last frame of the block — **check the distance from the block start
  before calling it a defect**.
* **A band imported from another tool's partition measures that partition.** `bc_ring` is 1.83 %
  here and 35 % there because const-bank is classified first.
* **A control that compares against a `Scope` column cannot fire under lite**, and this record had
  already written that down.
* **A readout that selects the armed arm by "counter > 0" fails the moment a straddle makes both
  arms non-zero** — select by magnitude or by the schedule text.
* **A foreign game on the GPU is a hard stop, not a caution**: the first attempt at this run was
  refused before launch because `utilization.gpu` read **13–18 %** against the harness's 10 % limit,
  and **guards check 0 would have failed it after twelve minutes of running**.
* Carried and still standing: `summary4.py`'s `cpu_net_us` **is** `cpu_gpu_us` under lite (read
  `endpoint84.py`); a `Scope` times only under `TimingsEnabled` and its ns column is structurally 0
  in lite; `guards.py` check 6 is not a criterion and check 10 hashes the exe installed **now**;
  `gen_gates.py --out` only with `--with`; never pipe a writing script through `head`; the port
  rewrites `.py` only, so every `.sh` in a fresh harness still points at the old one.

---

## 7. What is NOT closed

| debt | the number, as it stands | since |
|---|---|---|
| **the other 62 % of buffer slots** | **`bc_cb` alone is 58.13 %** — const-bank uniform views, which BDA cannot express. **Nobody has asked what it would take to stop binding them as uniforms**, and that is now the largest untouched share of the binding path | **93** |
| **what BDA would COST** | converting slots makes `uses_dma` true nearly everywhere; `PrepareBda` goes from **176 calls a flip** toward the draw count, and **`bda_us` is 2 181 µs today of which 1 875 is the first scanning call**. Entirely unmeasured — **and it comes straight off the ceiling above** | **93** |
| **whether a merged draw is actually free** | the **[U]** term, **78 % of the verdict** | **93** |
| the single-chunk notify | 99.9 µs a flip, untouched | 92 |
| the `ObtainBuffer` stream ring | its timer is dead in lite — the `hr_*` / `Enabled()` idiom is the fix | 90 |
| `pfhint`, `pfcap`, `dapin` re-measured with the pin | each was read at whatever rung its run happened to hold | 91 |
| route B items 2, 8, 10, 12, 3 | unchanged | 83–89 |

---

## 8. The arithmetic, said plainly

60 FPS = **16 667 µs**. Shipped base **31 642 µs = 31.60 FPS** (`acc82a`, not re-measured here).
GuestGpu is busy **97.2 %** of the frame at **6.17 µs a draw**, and the vblank plateau makes the
goal all-or-nothing: between −1.6 ms and −15.8 ms of saving the scoreboard stays at 30.0 FPS
(`ROADMAP.md:957-959`). **~15 000 µs must come out or nothing changes on screen.** Routes A, B and C
are closed at 20 838 µs / 0.7–2.5 ms / 514 µs.

**This session measured the last candidate of that scale at 7 198.9 µs, of which 5 646.0 is an
assumption — licensed to prototype, not a path to 60 FPS on its own, and the honest reading is that
no known combination of remaining levers reaches the threshold.** Nothing here removes work from the
shipped configuration, and no default moved.
