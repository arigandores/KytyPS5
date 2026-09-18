**Session 93 measured the ceiling of the last candidate at the scale the goal needs — moving V#
buffer slots onto the device-address table that already exists — and got 7 198.9 µs a flip, which
is LICENSED by the rule sealed before the number. Read the rest of that sentence before acting on
it: 5 646.0 µs of the 7 198.9 is an [U] assumption that a merged draw costs nothing, the measured
part is 1 552.9 µs, and by the same sealed table 1 552.9 µs is CLOSED.** One gate, ten counters, one
run, no default moved, nothing shipped. Read `docs/ROADMAP.md` first, then `C:/kyty/s93/FACTS.md` —
**§0.1 first: four defects of my own text, and both band misses are among them; neither is the world
contradicting a sealed band.**

Session 93's commits are on `merge-upstream`. **Source changed and was built twice; NO default
changed.** The installed `kyty_emulator.exe` is
**`6992a96ac76e7ea9015b12d061852111d4c70fe2895784d6e9ab61a2fb9b45f1`, 23 628 800 bytes**, and was not
rebuilt after acceptance. Harness — **`C:/kyty/s93`**; port it to `C:/kyty/s94` with a script written
**fresh in the SOURCE directory**, modelled on `C:/kyty/s92/s93_port.py`. `gates_base.txt`
**unchanged** — 1092 B, 99 names, sha256 `00c116dc…0594d8`. `KYTY_GPU_CLOCK_PIN` is an ENVIRONMENT
variable (a positional token to `enter_scene.py`), read once per process, never a gate and never a
schedule arm.

## 0. Read first

1. `docs/ROADMAP.md` — where we are, §0.1 (what is PROVEN and what is NOT about 60 FPS), §3 (what is
   closed), §5 (the order of decisions), §7 (the open debts). **§957-959 is the vblank plateau and
   it is the reason a partial win is worth zero FPS.**
2. **`C:/kyty/s93/FACTS.md` — §0.1 FIRST** (the four defects of my own text), then §1 (the
   instrument), §2 (the measurement and the ceiling), §3 (the scoreboard), §4 (the traps), §5 (not
   closed), §6 (the arithmetic).
3. **The sealed pre-registration `C:/kyty/s93/pred/01_bdacap.md`** (9 836 B, sha256 `a79661bd…`,
   `mtime − ctime` +0.002 s). **§1 is what the session may NOT claim** (it does not measure what BDA
   would cost — read it before quoting the ceiling as a saving); §2 is the classification; §6 is the
   verdict rule with its three thresholds; §7 the predictions. **Sealed in place — do not edit it,
   and do not edit `C:/kyty/s93/FACTS.md` or `README.md` either.**
4. `C:/kyty/s93/accept93.sh` — the admission order, and its standing warning: **the port rewrites
   `.py` only**, so the older `accept*.sh` files sit in the harness as byte copies still pointing at
   the OLD harness. `README.md` and `PLAN.md` in `s93` still carry session 91's headings for the
   same reason; they are not session 93's text.

## 1. What session 93 settled

* **The subject is not descriptor indexing.** `descriptorIndexing`, `runtimeDescriptorArray` and
  every `descriptorBinding*` feature are **not requested anywhere in the tree**
  (`vulkanWindow.cpp:68-77`). **`bufferDeviceAddress` IS enabled** (`:74`), the address table
  **already exists and is already maintained** on registration boundaries (`bufferCache.cpp:139-145`),
  and the shader side already reads through it (`spirvEmitterMemory.cpp:997-1047`). **The only
  missing piece is that no V# slot uses it** (`ResourceTracking.cpp:814, 880, 906, 960`).
* **The classification, `bl93a` (`bdacap=0|1`, `drawmerge=1` in both arms, pinned, VALID: split
  −0.000 %, pairs 121/121, work −0.034 %, 0 hang markers, guards 8 PASS / 0 FAIL):**
  `bc_cb` **27 672.5 a flip (58.13 %)**, `bc_ok` **17 844.8 (37.48 %)**, `bc_null` 1 129.1 (2.37 %),
  `bc_ring` 871.4 (1.83 %), `bc_fmt` 86.5 (0.18 %); sum against `bb_n` = 47 606.9 reads
  **0.999945**. `sl_over` = **0.000** — nothing hidden past index 32.
* **`dm_buf1_ok` = 881.88 against `dm_buf1_nr` = 881.93 — ratio 0.9999.** Practically every draw
  that differs from its predecessor by exactly one non-ring buffer slot differs by a slot BDA could
  carry. It is the most favourable number of the session and it is the population the [U] half rests
  on.
* **The ceiling: `Ceiling_bind` = `bc_ok_ns` = 1 552.9 µs a flip [M]; `Ceiling_merge` = 881.88 ×
  6.402 = 5 646.0 µs [U]; `Ceiling_total` = 7 198.9 µs ⇒ LICENSED** against the 5 000 µs threshold.
  **78 % of that is the [U] term. Strike it and 1 552.9 µs remains, which the same sealed table
  reads as CLOSED.** `Ceiling_bind` is itself an upper bound: `bc_ok_ns` brackets the whole function
  and so includes `ObtainBuffer` and `InvalidateMemoryFromGPU`, work a converted slot probably still
  pays.
* **The instrument's price was predicted visible and was visible:** `endpoint84` **+574.9 ± 83.3 µs,
  t = +13.80** on 121 pairs; `cpu/draw` +1.859 % ± 0.152 %, t = +24.44; ten `Add`s over 47 600 slots
  ≈ 12 ns a slot.
* **Scoreboard: 7 bands scored, 5 HIT / 2 MISS; 5 predictions, 4 HIT / 1 MISS.** A1 MISS (an exact
  zero demanded on a schedule arm — **the third time this record has written that defect**), B3 MISS
  (a band imported from session 86's partition, 0.0183 against [0.25, 0.45]), A3 NOT EVALUABLE by
  construction (it compares against a `Scope`, structurally 0 under lite). **R3 MISS at 7 199 — I
  predicted my own route would fail and it did better than I said.**

## 2. What is settled — do not reopen

`ROADMAP.md` §3, plus everything sessions 91 and 92 closed: the pin as this programme's estimator
for rung-moving knobs; D1 (`bufimp`) as a frame-time regression; the 64 KiB split as bimodal;
covariate adjustment on area; stratifying on the rung; the estimator question itself. Route A; route
C at slot and stage granularity; the program and slot lookups; `CopyAheadResult`; the whole-stage
memo; removing the prefetch; hoisting `AheadTake`. The split of `stg_pool_ns` (93.80 % notify);
`AsyncMemcpyBatch` / "one notify an upload"; "don't wake an awake pool"; the bounded worker spin.

**New this session, do not redo:** the classification of buffer slots (it is measured, not inferred
— `bc_cb` 58.13 %, `bc_ok` 37.48 %); the search for `VK_EXT_descriptor_indexing` (it is not
requested and it is not the lever); and **do not re-derive `Ceiling_bind`** — 1 552.9 µs is a direct
timer, not a rate times a population.

## 3. The work — a measuring session before any prototype

### 3.1 FIRST: what a merged draw actually costs — the [U] term, 78 % of the verdict

**`Ceiling_merge` = 5 646.0 µs is `dm_buf1_ok` × (`cpu_gpu_us` / `draws`) and it assumes a merged
draw costs nothing — the same assumption session 86 refused to record as a saving**
(`ROADMAP.md:676-678`). **Until that is measured, the verdict LICENSED rests on nothing**, and the
only defensible number from session 93 is 1 552.9 µs, which is CLOSED.

This is the first work of the session, and it is a measurement, not a build. Name the mechanism
before the patch: a draw that disappears into its predecessor does not remove `cpu_gpu_us / draws`
of work — it removes whatever is *per-draw* and keeps whatever is *per-slot* and *per-state*. The
question to put a number on is **what fraction of 6.402 µs survives a merge**, measured, not
assumed. `drawmerge` (session 86) is already in the tree and already armed in both arms of `bl93a`;
read what it counts before writing a line.

**Say the predicted number out loud, in µs a flip, in the sealed text, before the patch** — and say
what reading would turn the session-93 verdict from LICENSED to MARGINAL or CLOSED, because that is
the decision this measurement exists to make.

### 3.2 SECOND: `bc_cb` — 58.13 % of the slots, and nobody has asked the question

**Const-bank uniform views are the largest untouched share of the binding path: 27 672.5 slots a
flip, 58.13 % of `bb_n`.** BDA cannot express them — they need a real descriptor — and that is
exactly why they were counted. **Nobody has asked what it would take to stop binding them as
uniforms.** `KYTY_CBANK_COPY` has been shipped since session 20; start by reading why const-bank
exists at all and what a storage-buffer view would cost in the shader (alignment classes, the
`packed_stride` bits), and only then decide whether there is a measurable question here or a closed
one. **Do not build. Establish whether there is a ceiling worth measuring.**

### 3.3 THIRD: what BDA would COST — the term that comes straight off the ceiling

Converting slots makes `uses_dma` true nearly everywhere. **`PrepareBda` goes from 176 calls a flip
(`bc_dma` = 176.17, 3.50 % of draws) toward the draw count, and `bda_us` is 2 181 µs a flip today,
of which 1 875 µs is the first scanning call of the frame** (`renderContext.cpp:299-378`, gate
`bdasplit`). **This is entirely unmeasured and it subtracts from the ceiling, not from the frame.**
A ceiling quoted without it is a ceiling quoted dishonestly. `bdasplit` already exists — the debt is
a measurement, not an instrument.

### 3.4 The debts (`FACTS.md` §5)

* The single-chunk notify: **99.9 µs a flip**, 2.75 µs a call on 36.3 calls, untouched by anything
  session 92 built, and its mechanism is known NOT to be "a sleeping worker".
* The `ObtainBuffer` stream ring — its timer is `TimingsEnabled`-gated and structurally 0 in lite;
  the `hr_*` / `Enabled()` idiom is the fix.
* `pfhint`, `pfcap` and `dapin` re-measured **with the pin**, each with the record path ON — they
  were read at whatever rung their run happened to hold.
* Route B items 2, 8, 10, 12 and the corrected 3.

### 3.5 The port — FOUR root chains, and they are four separate edits

Port `C:/kyty/s93` → `C:/kyty/s94` with a script **written fresh in the SOURCE directory**
(`C:/kyty/s93/s94_port.py`), modelled on `C:/kyty/s92/s93_port.py`. **The copy of `s93_port.py` that
now sits inside `s93` is a self-copy no-op** — the port that carried it rewrote its own `SRC` and
`DST` to the same path, so its `BROKEN_HEAD == FIXED_HEAD` and its `range()` repairs replace a string
with itself. **Write a new one; do not run that copy.**

A literal `s93` → `s94` replacement drops the previous root out of every chain, so fix all four:

1. **the head of every `--roots` default** (`arms.py:29`, `baseline.py:83`, `effect.py:103`): the new
   root goes in FRONT and `s93` stays in the list;
2. **`area_verdict.py:56`** — `DEFAULT_CSV_ROOTS = ... range(93, 70, -1)` → `range(94, 70, -1)`;
3. **`shift91.py:35`** — `ROOTS = ... range(93, 66, -1)` → `range(94, 66, -1)`;
4. **the hard-coded root tuples in `find_log`** — `stg92.py:44`
   `('C:/kyty/s93', 'C:/kyty/s92', 'C:/kyty/s91', 'C:/kyty/s90')` and **the same construct in
   `bda93.py:41`** `('C:/kyty/s93', 'C:/kyty/s92', 'C:/kyty/s91')`. **Both exist — I checked.** A
   literal rewrite turns the head into `s94` and **drops `s93`, i.e. makes `log_bl93a.txt`
   unreachable to exactly the two tools that read it.** (`bda93.py:23` also carries a plain
   `ROOT = 'C:/kyty/s93'`, which the ordinary `.py` literal rewrite handles correctly — it is not a
   chain.) Historic ranges that name a FIXED archive window (`ft81.py`, `inventory81.py`,
   `patch_context85.py`) are **not** touched.

Then: `gates_base.txt` must come across **byte-identical** (1092 B, 99 names, sha256
`00c116dc…0594d8`); `gen_gates.py` in `--check` mode only; `.txt`/`.json`/`.md`/`.csv`/`.sh` copied
byte-exact; and **write `accept94.sh` new** — the `.sh` files are copied verbatim and still point at
the old harness. **`accept93.sh` deliberately ends at step 4** and says why in its own text: an old
scorer (`pin91.py`, `stg92.py`) keys its expectations off the tags of its own session and verifies
the sha256 of its own sealed pre-registration, so calling one on a new tag "fails loudly at best and
silently mis-scores at worst". Session 94 adds its own step 5 pointing at its own sealed
pre-registration, never at `bda93.py`.

**One more tool defect to carry:** **`bda93.py` selects the armed arm by `bc_ok > 0`**, so the
straddle at the block boundary made both arms qualify and the tool printed **every band as NOT
EVALUABLE** instead of scoring them. **Check which rows printed before reading a scoreboard**, and
select the armed arm by magnitude or by the schedule text.

**Say the odds out loud.** 60 FPS = 16 667 µs against a shipped 31 642 µs frame, so **~15 000 µs must
come out, and the vblank plateau pays nothing for less**. **The best measured candidate on the board
gives 7 199 µs — 48 % of what is needed — and 5 646 of those 7 199 are an assumption.** Even
realised in full this route does not reach the threshold alone, and no second lever of this size is
known. **Do not promise 60 FPS.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.** Measure it with `KYTY_GPU_CLOCK_PIN=1` whenever the change can move GuestGpu's wall time.

## 4. Do NOT

* **Do not demand an exact zero on a schedule arm.** The reporting interval straddles the gate flip;
  session 93's 56 offending frames of 3651 **all sat at distance 29 of 30 from the start of their
  block** and totalled 0.0054 % of the armed value. **Check the distance from the block start before
  calling it a defect** — this programme has now written this trap three times.
* **Do not take a band from another tool's classification.** `bc_ring` is 1.83 % under session 93's
  order and 35 % under session 86's, because const-bank is checked first and const-bank is 58 % of
  everything. **A band imported from another partition measures that partition, not the world.**
* **Do not write a control that compares against a `Scope` column under lite.** A `Scope` times only
  under `TimingsEnabled`; its ns column is structurally 0, and such a control is NOT EVALUABLE by
  construction, not failed by the run. This record had already written that down before session 93
  wrote A3.
* **Do not select the armed arm by "counter > 0".** One straddled frame makes both arms non-zero and
  the whole scoreboard goes quiet. Select by magnitude or by the schedule text.
* **A foreign game on the GPU is a hard stop, not a caution.** `utilization.gpu` at 13–18 % against
  the harness's 10 % limit refused session 93's first launch, and guards check 0 would have failed
  the run **after twelve minutes**. Check before launching, not after.
* **Do not quote `summary4.py`'s `cpu_net_us`** — under lite it **is** `cpu_gpu_us`, and the tool
  says so in its own NOTE. The endpoint is `endpoint84.py`.
* **`guards.py` check 6 is not a criterion** (compare the check LINES), and **check 10 hashes the exe
  installed at that moment** — never rebuild between acceptance and the final answer.
* **`gen_gates.py --out X` without `--with` ignores `--out` and overwrites `gates_base.txt`.**
* **Never pipe a writing script through `head`** — SIGPIPE kills it before it writes.
* **Do not quote 7 198.9 µs as a saving, and do not quote it without its [U] label.** 5 646.0 of it
  assumes a merged draw is free; that assumption is §3.1's work, and until §3.1 has a number the
  only defensible figure is 1 552.9 µs, which the sealed table calls CLOSED.
* Carried: pre-registrations sealed in place and never edited; a failed control is REPAIRED under a
  NEW sealed pre-registration, and the repair is dry-run on the record before sealing; arming proved
  inside the run; ratios of sums, never per-frame identities; a run that fails admission is REPLACED,
  not discussed, and its contrast is quoted nowhere; the first entry after a fresh build hangs
  (`--warmup-first`); `|t| < k` alone passes by degeneracy when one arm is a hard zero — pair it with
  an absolute guard; a ratio of sums does not constrain the distribution behind it; a knob a schedule
  must flip cannot be read once per process; `daepceil`'s comment still says "(default 1)" and it
  is 0.
