# M5′ runbook: from the session-102 capture to the M5′ verdict

Sealed protocol: `C:/kyty/s103/pred/02_m5p_bench.md` (sha256 `4035a9b0…`, **decisive**), which
inherits V-a…V-g, the estimator and the shader set from session 102's
`C:/kyty/s103/prev102/pred/01_m5_bench.md` (`cf3c353f…`) as amended by
`C:/kyty/s103/prev102/pred/02_m5_addendum.md` (`ced6d410…`) §1, §2, §5. Every tool below checks all
three hashes and refuses to run if any one differs. This runbook sets no rule of its own. Where it
says STOP, the sealed texts do not allow a restart; any further step is recorded in `ROADMAP.md`
first (the executor's standing rule).

Adapted from `M5_RUNBOOK.md` (session 102). **No game run**: M5′ uses the session-102 capture
(accepted under V-a in session 102). No step below launches the game or builds anything.

| tool | role | differs from session 102 |
|---|---|---|
| `m5p_recompile.py` | arms A / V1 / V2p offline → `m5p/recompile.json`, `m5p/regs.json`, `m5p/layout_check.json` | arms; cache = the snapshot; sealed exe; LDG variants |
| `rd_m5_find.py` | module of every draw / dispatch (via `m5p_run.py find`) | **unchanged** (no arm, no seal dependency) |
| `m5p_plan.py` | items ↔ captured modules, arms B / A / V1 / V2p, V-f | arms; three seals; default `--cache-dir` = snapshot; records the recompile inputs |
| `rd_m5p_equal.py` | V-e: three A replays, V1 and V2p against A1 (via `m5p_run.py equal`) | three seals; variants fixed to V1, V2p; sealed capture sha256 enforced |
| `rd_m5p_bench.py` | the timing bench (via `m5p_run.py bench`) | four arms, Williams design `r mod 4`; arm set fixed; sealed capture sha256 enforced |
| `m5p_103.py` | the scorer | X′ = V2p/A decides; CLOSED / PASSES; seed 103 |

"V2p" in every file name, JSON key and log line is the seal's **V2′**.

## 0. Before any step

* **The GPU must be idle.** The automated game series of this session must have finished.
  `m5p_run.py` refuses to start while `kyty_emulator.exe` or `qrenderdoc.exe` is running. It records
  `nvidia-smi --query-compute-apps` before the run; on this driver every process reads `[N/A]`
  memory, so **a human** checks that list and closes any game, emulator or GPU compute load first.
  It logs clocks, temperature, power and throttle reasons every 5 s to `<out>.gpuclk.csv`.
* No other heavy job may run on this machine while `equal` or `bench` runs.
* `CAP` is the session-102 capture, sealed by sha256 in new §2 (`rd_m5p_equal.py` and
  `rd_m5p_bench.py` refuse any other file on a non-mechanics plan).
* `LOG` is V-a's input: **`C:/kyty/s102/log_m5cap102b.txt`** — the retry that wrote the capture
  (`log_m5cap102.txt` is the crashed first attempt; session 102 scored with `…102b`). It carries
  `DmaLayout: mode 1` and `GpuClockPin: mode 1`.
* `OUT` is `C:/kyty/s103/m5p/real/`, a new directory. No tool overwrites a file there, so a second
  attempt always needs new file names.
* **`m5p/recompile.json` must exist and must not change afterwards** (the plan pins it by sha256;
  `m5p_recompile.py` refuses to rebuild over it without `--overwrite`). Its summary (last lines of
  `m5p/m5p_recompile.stdout.txt`) must show: `A_not_identical_to_stored: []` with
  `A_identical_to_stored` = `A_modules` = 16, `spirv_val_fail: []`, `crosscheck_fail: []`,
  `V2p_not_uses_dma: []`, `layout_bad: []`, `manifest_mismatch: []`, `baseline_changed: []` (A and V1
  byte-identical to session 102's modules). Anything else: **STOP before `find`** and record it.
* Run all commands from Git Bash:

```bash
CAP="C:/Users/<user>/OneDrive/Desktop/ps5 em/_RenderDoc/kyty_1790110985179586_capture.rdc"
LOG=C:/kyty/s102/log_m5cap102b.txt
OUT=C:/kyty/s103/m5p/real
mkdir -p $OUT
python C:/kyty/s103/test_m5p_103.py | tail -1          # expect: N passed, 0 failed
sha256sum C:/kyty/s103/pred/02_m5p_bench.md C:/kyty/s103/prev102/pred/01_m5_bench.md \
          C:/kyty/s103/prev102/pred/02_m5_addendum.md    # 4035a9b0…, cf3c353f…, ced6d410…
sha256sum C:/kyty/build/shader_cfg_tests.exe            # e7a15418…
```

## 1. find: which module every draw and dispatch runs (≈ 3 min)

New §3: `find` is run afresh on this capture (the session-102 `find` file is not reused).

```bash
python C:/kyty/s103/m5p_run.py find --cap "$CAP" --out $OUT/find_m5p103.json --timeout 7200
```

The capture's sha256 (≈ 15 s for 5.7 GB), open (10–25 s), structured-data mapping (seconds), and a
replay cross-check on ≈ 350 events. Module dumps go to `$OUT/modules/`. Session 102: 180 s,
11 138 events, 367 modules, 0 mismatches.

Check: `complete: true`, `sd_verify.mismatches == 0` (otherwise the tool falls back to replay mode,
≈ 1.5 h, still valid), `capture_sha256` = `92a10b3c…`.

On failure (crash, killed at timeout, `complete: false`): not a measurement; run it again with a
**new** `--out` name.

## 2. plan: link modules to items, arms B / A / V1 / V2p, V-f (≈ 1 min)

```bash
python C:/kyty/s103/m5p_plan.py --find $OUT/find_m5p103.json --out $OUT/plan_m5p103.json
```

Defaults: `--recompile C:/kyty/s103/m5p/recompile.json`, `--cache-dir
C:/kyty/cache_snap/PPSA21564_2db9065a` (the snapshot, new §2 — **never the live `_ShaderCache`**, which
another translator has overwritten), `--regs m5p/regs.json`, `--layout m5p/layout_check.json`
(both reported only). It runs `spirv-val` twice on every module of every arm: the deciding command
`--target-env vulkan1.3 --uniform-buffer-standard-layout` and 102 pred/01's original command
(reported only).

| what | expect | if not |
|---|---|---|
| `capture … sha256` line | `92a10b3c…` with no "NOT the sealed capture" | **STOP**: wrong `find` input. |
| `present` items | ≥ 7 carrying ≥ 60 % of 4 508 µs (V-b); session 102: all 10 | **STOP.** Coverage is not a technical failure; report V-a/V-b. |
| arms | `B 0`, and `A`, `V1`, `V2p` each with the same number of replacements (session 102: 14) | a missing variant module fails V-e for that item (reported, not repaired) |
| `x-norc` column / `WARNING: excluded modules whose cache permutation was never recompiled` | empty | **STOP before `equal`.** See §2a. |
| `WARNING: recompile inputs are not the sealed ones` | absent | **STOP**: the scorer would fail IDENTITY. Fix the input (`--cache-dir`, recompile.json) and make a **new** plan file. |
| `spirv-val, deciding command` | `0 of N modules fail` | V-f FAILS and the bench is INVALID whatever it measures. **STOP** and report. |
| `spirv-val, 102 pred/01 command` | the PS modules fail (const-bank `cbuffers[]`) | expected (102 pred/02 §1); reported, never deciding |
| `note:` lines | "matches several permutations" for S6 (identical A bytes for p0/p1) | harmless |

### 2a. A permutation cached by the capture run that `m5p_recompile.py` never built

`m5p_recompile.py` builds every permutation of every current-signature cache file of the ten items in
the snapshot (taken before any session-103 game run; its ten items' cache files are byte-identical to
the ones session 102 recompiled), so this gap is not expected — session 102 had none on this capture. If it appears anyway, it is a harness gap, not "a module no permutation reproduces"
(102 pred/01 V-c). No timing exists yet, so filling it touches no measurement, but the choice is
recorded in `ROADMAP.md` / `FACTS.md` **before** step 3: either rebuild (`m5p_recompile.py --baseline
<kept copy of the old recompile.json> --overwrite`, confirm every old A/V1/V2p module byte-identical,
make a **new** plan file) or accept the exclusion and say that the excluded share includes
never-built permutations.

## 3. equal: V-e for V1 and V2p (≈ 3–5 min)

New §3: equality is run afresh on this capture for V1 and V2p.

```bash
python C:/kyty/s103/m5p_run.py equal --cap "$CAP" --plan $OUT/plan_m5p103.json \
    --out $OUT/equal_m5p103.json --timeout 7200
```

For every included item, with **only that item** replaced, at its last event: arm A is replayed
**three** times (A1, A2, A3) and the differing bytes of each pair are recorded; V1 and V2p are read
once each and compared with A1; a resource bound under a variant only (the BDA fault buffer of a
V2p module, which V2p still declares) is read under A three more times so E covers exactly the
compared outputs. A repeatable item (all three pairs 0) passes only bit-equal to A1; otherwise it
passes only at ≤ 2·E differing bytes, reported as "within replay noise", never "equal". The scorer
judges again from the raw counts. Do not pass `RD_VARIANTS` (a non-mechanics plan refuses any set
other than V1, V2p) or `RD_SHA=0` (refused). Session 102: 144 s for ten items with three variants.

Check: `complete: true`; every item has `reference_replays: 3` and no `error`; every item's log line
says `REPEATABLE` or `replay-nondeterministic, E = …`.

On failure:

* **Crash or kill** (`complete: false`): restart from scratch **once**, with a new `--out`
  (`equal_m5p103_r2.json`). Keep the crashed file and report it. A second crash: **STOP** — V-e cannot
  be evaluated, M5′ is NOT DECIDED this session.
* **Item-level `error`** (replacement not in effect, no output bound, build failure): deterministic, a
  result. Do not restart; the scorer counts it as a V-e failure of that item.
* **Never** re-run a completed equality file, whatever it shows.

## 4. bench: four arms, R = 20, one automatic extension (≈ 10 min, +10 min if extended; 4-hour cap)

```bash
python C:/kyty/s103/m5p_run.py bench --cap "$CAP" --plan $OUT/plan_m5p103.json \
    --out $OUT/bench_m5p103.json \
    --env RD_AUTO_EXTEND=1 --env RD_EQUAL=$OUT/equal_m5p103.json --timeout 21600
```

Do not pass `RD_ROUNDS`, `RD_EXT_ROUNDS` or `RD_ARMS`: the defaults are the sealed R = 20, extension
+20, and the arm set B A V1 V2p (a non-mechanics plan refuses any other arm set; a changed R fails
V-g in the scorer; a short extension reads `EXTENSION REQUIRED`). Never pass `RD_ALLOW_BUILD_FAIL`
(its build errors fail V-g) or `RD_FORCE_EXTEND` (honoured only on a mechanics plan).

What the bench does, in order:

1. It checks all three seals and the plan's three seal hashes, computes the capture's sha256 and
   refuses anything but `92a10b3c…`, opens the capture, and checks the md5 of every original module.
2. It builds every module of every arm, and refuses to time if any build fails.
3. It checks that each replacement is in effect at each module's first event, and refuses to time if
   one is not.
4. Two warm-up fetches with arm B, discarded.
5. Rounds 0–19. Round `r` uses `m5p_103.DESIGN[r mod 4]`, the Williams design `[B A V1 V2p]`,
   `[A V2p B V1]`, `[V1 B V2p A]`, `[V2p V1 A B]` (five full cycles). Each round's sequence is recorded.
6. The interim decision with the scorer's own `m5p_103.decide()`. If INCONCLUSIVE, rounds 20–39 run
   as the extension, same design, same process.

The JSON is rewritten after every fetch.

Time estimate (session 102 on this capture: fetch 0.42 s, replace 3.7 s, remove 3.7 s median; 14
replacements an arm): one round ≈ 3 × 7.9 s + 0.5 s ≈ 24 s; 20 rounds ≈ 8 min; plus open + sha256
(≈ 40 s) and the replacement check (≈ 3 × 14 × 1.3 s ≈ 55 s). The 10-minute fetch trigger of the
4-hour rule is not expected to fire; if it does, R drops by `m5p_103.rounds_after_time_rule` (whole
cycles of 4 preferred, never below 8) and the drop is recorded as a `rounds_drop` decision.

Check: `complete: true`, `replacement_check_ok: true`, `build_errors: []`, 20 main rounds, and either
20 extension rounds or an interim decision that was not INCONCLUSIVE.

On failure (102 pred/01 §6 V-g: "A bench that crashes may be restarted from scratch once; a completed
bench is never re-run"):

* **Crash, kill at timeout, or `complete: false`**: restart **from scratch once** with a new `--out`
  (`bench_m5p103_r2.json`) and the same plan and equality file. Keep the crashed JSON and report it. A
  second crash: **STOP** — V-g fails and M5′ is NOT DECIDED this session.
* **qrenderdoc hangs after the JSON says `complete: true`**: a known RenderDoc exit hang, not a crash.
  `m5p_run.py` kills it at `--timeout`; otherwise `taskkill //F //IM qrenderdoc.exe`. The bench stands.
* **Refusal before timing** (seal, plan seals, capture sha256, arm set, build failure, replacement not
  in effect, original module md5): deterministic, not a crash. **STOP** and report; the result is
  INVALID (V-g). A harness fix followed by a new bench is recorded in `ROADMAP.md` first.
* **Main rounds completed but the extension could not run in-process** (the scorer says `EXTENSION
  REQUIRED` and the bench has no extension rounds, e.g. `RD_EQUAL` was missing): append the extension
  in a new process; it is recorded as `extension_new_process`.

```bash
python C:/kyty/s103/m5p_run.py bench --cap "$CAP" --plan $OUT/plan_m5p103.json \
    --out $OUT/bench_m5p103_ext.json --env RD_RESUME=$OUT/bench_m5p103.json --timeout 21600
```

* **Never** re-run a completed bench, and never re-run one because of anything it measured.

## 5. scorer: the verdict (seconds)

```bash
python C:/kyty/s103/m5p_103.py --plan $OUT/plan_m5p103.json --bench $OUT/bench_m5p103.json \
    --equal $OUT/equal_m5p103.json --capture-log $LOG --out $OUT/m5p_103_result.json \
    | tee $OUT/m5p_103_result.stdout.txt
```

If the extension ran in a new process, pass `--bench $OUT/bench_m5p103_ext.json`. P4′ reads the
session-102 plan and bench from `C:/kyty/s102/m5/real/` by default (`--prev102-plan`,
`--prev102-bench`; reporting only).

The scorer checks the three seals and the file identity: the plan's sha256 must equal the bench's
and the equality file's `plan_sha256`; the plan must carry the three seal hashes; and the plan's
recompile inputs must be the sealed ones (test recompiler `e7a15418…`, cache dir = the snapshot,
signature `KytySC3:2db9065a`). It then applies V-a…V-g (V-a also requires the bench's capture sha256
to be the sealed `92a10b3c…`) and computes **X′ = median_r S[V2p]/S[A]** over the items passing V-e
for V2p (deciding), **L = median_r S[V1]/S[A]** over the items passing V-e for V1 and **A/B** over the
A-valid items (both reported), with the 90 % percentile bootstrap: 20 000 resamples, **seed 103**,
the same round indices for all three.

| status / verdict | meaning (new §0) | what to publish |
|---|---|---|
| `VALID` / `CLOSED` | CI_lo(X′ − 1) > 0.06 | **G CLOSED.** Not about CPU, P, F or R1. |
| `VALID` / `PASSES` | CI_hi(X′ − 1) ≤ 0.06 | **G's GPU side PASSES**; the next decision becomes a slice prototype of G's CPU side. Not a licence for G, nothing about 60 FPS. |
| `… (decided at the point after extension (40 rounds))` | the interval straddled; after the extension the point decides (X′ − 1 > 0.06 ⇒ CLOSED, else PASSES) | publish with that label |
| `EXTENSION REQUIRED` | INCONCLUSIVE and fewer than 20 extension rounds | see §4, RD_RESUME |
| `M5' NOT DECIDED (V2p fails V-e for more than 40 % of the valid A-arm time)` | the V2p V-e failures carry > 40 % of the valid A time | no verdict |
| `INVALID` / `NOT EVALUABLE (…)` | a control or the identity failed or could not be evaluated, or X′ has no item left | no verdict; publish the reason |

Whatever the verdict, publish (new §4, §5):

* X′, L and A/B with their intervals (and the extension points if it ran);
* every per-item ratio (B/A, V1/A, V2p/A);
* the V-e table, naming every "within replay noise" item;
* P1′–P4′ — a MISS is published and never repaired;
* registers, local memory, SASS counts and LDG variants of every module of A, V1, V2p
  (`m5p/regs.json`, `m5p/m5p_recompile.stdout.txt`), reported and never deciding.

Never claim (new §6): that M5′ measured G's full price (SRT chasing, formats, VS/mesh and the CPU
side are not priced) · that a PASS licenses G or says anything about 60 FPS · that a CLOSE is about
CPU, P, F or R1 · that `KYTY_BDA_LEAN` is a shippable path (no fault reporting in PS; measurement
only) · that the run-time alignment test is free · **any speedup or frame-rate gain.**

## Wall-time summary

| step | expected | session 102 on the same capture |
|---|---|---|
| m5p_recompile (offline, before everything) | ≈ 10–20 min | — |
| find | ≈ 3 min (1.5 h if the sd mapping falls back to replay) | 180 s |
| plan | ≈ 1 min | — |
| equal | ≈ 2–5 min | 144 s (three variants) |
| bench (20 + 20 rounds) | ≈ 10 min + 10 min | 936 s (five arms, 20 rounds) |
| scorer | seconds | — |
