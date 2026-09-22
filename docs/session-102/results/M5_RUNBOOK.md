# M5 runbook: from the capture to the verdict

Sealed protocol: `C:/kyty/s102/pred/01_m5_bench.md` (sha256 `cf3c353f…`) as amended by
`C:/kyty/s102/pred/02_m5_addendum.md` (sha256 `ced6d410…`). Every tool below checks both hashes
and refuses to run if either one differs. This runbook sets no rule of its own. Where it says STOP,
the sealed texts do not allow a restart, and any further step is a decision for the user.

This runbook starts **after** the capture exists: `enter_scene.py m5cap102 …` with `--emu-arg=--rd`,
`KYTY_DMA_LAYOUT=1 KYTY_GPU_CLOCK_PIN=1 KYTY_RD_TIME=<s> KYTY_RD_FLIPS=2`, the gate `bdaall=1`, and no
`KYTY_GPU_CHECKPOINTS`, `KYTY_GPU_TIME` or `KYTY_REC` (pred/01 s4). No step below launches the game or
builds anything.

## 0. Before any step

* `CAP` is the exact `.rdc` written by the m5cap102 run in
  `C:/Users/<user>/OneDrive/Desktop/ps5 em/_RenderDoc/`. Match its timestamp against
  `C:/kyty/s102/log_m5cap102.txt`, and do not assume the newest file is the right one. Do not use the
  session-49 capture `kyty_1789223444252358_capture.rdc`, which is for mechanics only.
* `LOG` is `C:/kyty/s102/log_m5cap102.txt`. It is V-a's input and must contain `DmaLayout: mode 1`
  and `GpuClockPin: mode 1`.
* `OUT` is `C:/kyty/s102/m5/real/`, a new directory. No tool overwrites a file there, so a second
  attempt always needs new file names.
* Keep the GPU idle. `m5_run.py` refuses to start while `kyty_emulator.exe` or `qrenderdoc.exe` is
  running. It records `nvidia-smi --query-compute-apps` before the run. On this driver every
  process reads `[N/A]` memory, so **a human** checks that list and closes any game, emulator or GPU
  compute load first. It also logs clocks, temperature, power and throttle reasons every 5 s to
  `<out>.gpuclk.csv`.
* No other heavy job may run on this machine while `equal` or `bench` runs.
* Run all commands from Git Bash:

```bash
CAP="C:/Users/<user>/OneDrive/Desktop/ps5 em/_RenderDoc/kyty_<id>_capture.rdc"
LOG=C:/kyty/s102/log_m5cap102.txt
OUT=C:/kyty/s102/m5/real
mkdir -p $OUT
python C:/kyty/s102/test_m5_102.py | tail -1        # expect: 132 passed, 0 failed
sha256sum C:/kyty/s102/pred/01_m5_bench.md C:/kyty/s102/pred/02_m5_addendum.md   # cf3c353f…, ced6d410…
```

## 1. find: which module every draw and dispatch runs (≈ 3–5 min)

```bash
python C:/kyty/s102/m5_run.py find --cap "$CAP" --out $OUT/find_m5cap102.json --timeout 7200
```

The tool computes the capture's sha256 (≈ 15 s for 5.7 GB), opens the capture (10–25 s), maps
modules from structured data (seconds), and cross-checks that mapping by replay on ≈ 350 events at
0.2–0.7 s each. Module dumps go to `$OUT/modules/`. The session-49 capture took 149–175 s.

Check: `complete: true`, `sd_verify.mismatches == 0` (otherwise the tool falls back to replay mode,
≈ 1.5 h, which is still valid), and `capture_sha256` recorded.

On failure (crash, killed at timeout, `complete: false`): this step is not a measurement. Run it
again with a **new** `--out` name.

## 2. plan: link modules to items, list arms B / A / V1 / V2 / V2s, run V-f (≈ 1 min)

```bash
python C:/kyty/s102/m5_plan.py --find $OUT/find_m5cap102.json \
    --recompile C:/kyty/s102/m5/recompile.json --out $OUT/plan_m5cap102.json
```

By default the planner scans `…/ps5 em/_ShaderCache/PPSA21564`, the translation cache that the
**capture run itself wrote**, with signature prefix `KytySC3:2db9065a`. It merges `m5/regs.json` and
`m5/layout_check.json` into the plan (reported only). It runs `spirv-val` twice on every module of
every arm:

* the deciding command of pred/02 s1: `--target-env vulkan1.3 --uniform-buffer-standard-layout`;
* pred/01's original command, which is reported only.

Read the printed table:

| what | expect | if not |
|---|---|---|
| `present` items | ≥ 7 carrying ≥ 60 % of 4 508 µs (V-b) and ≥ 7 for capture acceptance (pred/01 s4) | **STOP.** Coverage is not a technical failure, so pred/01 s4 allows no retake. Report V-a/V-b; a retake is the user's decision. |
| arms | `B 0`, and `A`, `V1`, `V2`, `V2s` each with the same number of replacements | a missing variant module fails V-e for that item (it is reported, not repaired) |
| `x-norc` column / `WARNING: excluded modules whose cache permutation was never recompiled` | empty | **STOP before `equal`.** See §2a. |
| `spirv-val, deciding command` | `0 of N modules fail` | V-f will FAIL, and the bench is INVALID whatever it measures. **STOP** and report. |
| `spirv-val, pred/01 command` | the PS modules fail (the const-bank `cbuffers[]`) | expected (pred/02 s1); reported, never deciding |
| `note:` lines | "matches several permutations" for S6 (identical A bytes for p0/p1) | harmless |

### 2a. A permutation cached by the capture run that `m5_recompile.py` never built

`m5/recompile.json` was built before the capture, from the cache files that existed then. If the
capture run cached a **new** permutation of an item, the new file or new index shows up as
`excluded_not_recompiled`. Its module is excluded from V-c, but because arm A was never built for it,
not because arm A failed to reproduce it. That is a gap in the harness. It is **not** "a module no
permutation reproduces" (pred/01 V-c).

At this point no timing exists, so filling the gap does not touch any measurement. Still, the way to
fill it is a decision for the user or orchestrator:

* `m5_recompile.py` rewrites `m5/recompile.json` and `m5/regs.json` **in place**, and the plan pins
  `recompile.json` by sha256. To fill the gap: run `m5_recompile.py` again with the original kept as
  its `--baseline`, confirm that every old A/V1/V2/V2s module is byte-identical, then make a **new**
  plan file.
* Otherwise, accept the exclusion. The report must say that the excluded share includes permutations
  that were never built.

Either way, record the choice in `FACTS.md` **before** step 3.

## 3. equal: V-e, amended by pred/02 s2 (≈ 5–15 min)

```bash
python C:/kyty/s102/m5_run.py equal --cap "$CAP" --plan $OUT/plan_m5cap102.json \
    --out $OUT/equal_m5cap102.json --timeout 7200
```

For every included item the tool does the following, with **only that item** replaced, at its last
event:

* It replays arm A **three** times (A1, A2, A3) and records the differing bytes of each pair.
* It reads V1, V2 and V2s once each and compares them with A1.
* If a variant binds a resource that A does not (for example the V2 fault buffer of a CS item), it
  reads that resource under A three more times, so that E always covers exactly the outputs being
  compared.

The rule: a *repeatable* item (all three pairs 0) passes only if the variant is bit-equal to A1.
Otherwise the item passes only if the variant's differing bytes are ≤ 2·E; this is reported as
"within replay noise", never as "equal". The scorer judges again from the raw counts.

Time estimate: the capture opens in 25–40 s including its sha256. Each item needs 6–9 SetFrameEvent
calls plus readback of every bound target (4K RGBA16F is ≈ 66 MB a read). The session-49 capture
took 6–7 s per item, and 4K targets will take longer.

Check: `complete: true`; every item has `reference_replays: 3` and no `error`; the log line of every
item says `REPEATABLE` or `replay-nondeterministic, E = …`.

On failure:

* **Crash or kill** (`complete: false`): restart from scratch **once**, with a new `--out`
  (`equal_m5cap102_r2.json`). Keep the crashed file and report it. A second crash means STOP: V-e
  cannot be evaluated, so M5 is NOT DECIDED this session.
* **Item-level `error`** (a replacement not in effect, no output bound, or a build failure): this is
  deterministic and is a result. Do not restart; the scorer counts it as a V-e failure for that item.
* **Never** re-run a completed equality file, whatever it shows.

## 4. bench: five arms, R = 20, one automatic extension (≈ 10–25 min, 4-hour cap)

```bash
python C:/kyty/s102/m5_run.py bench --cap "$CAP" --plan $OUT/plan_m5cap102.json \
    --out $OUT/bench_m5cap102.json \
    --env RD_AUTO_EXTEND=1 --env RD_EQUAL=$OUT/equal_m5cap102.json --timeout 21600
```

Do not pass `RD_ROUNDS`, `RD_EXT_ROUNDS` or `RD_ARMS`: the defaults are the sealed values, R = 20,
extension +20, and arms B A V1 V2 V2s. If any of them is changed, the scorer fails V-g, or reports
`EXTENSION REQUIRED` for a short extension. Never pass `RD_ALLOW_BUILD_FAIL`: its build errors
fail V-g. Never pass `RD_FORCE_EXTEND` either; it is honoured only on a `--mechanics` plan.

What the bench does, in order:

1. It checks the capture's sha256, opens the capture, and checks the md5 of every original module.
2. It builds every module of every arm, and refuses to time if any build fails.
3. It checks that each replacement is in effect at each module's first event, and refuses to time if
   one is not.
4. It makes two warm-up fetches with arm B, which are discarded.
5. It runs rounds 0–19. Round `r` uses sequence `r mod 10` of `m5_102.DESIGN`: rotations 0–4 of
   `[B, A, V1, V2, V2s]`, then their reverses 0–4. Each round's sequence is recorded.
6. It makes the interim decision with the scorer's own `decide()`. If the result is INCONCLUSIVE, it
   runs rounds 20–39 as the extension, in the same process.

The JSON is rewritten after every fetch.

Time estimate:

* Open plus sha256: ≈ 40 s.
* Builds: ≈ 10–60 s.
* Replacement check: ≈ 4 arms × ~16 modules × 0.2–0.7 s.
* One measurement: replace (~16 modules, 1–3 s) + fetch (≈ 0.6–1 s) + remove (1–3 s).
* One round: ≈ 15–35 s. 20 rounds: ≈ 5–12 min. The extension adds as much again.
* The 10-min fetch trigger of the 4-hour rule is not expected to fire. If it does, R drops by the
  rule in `m5_102.rounds_after_time_rule` to the largest number of rounds that fits, preferring whole
  cycles of 10 and never going below 8. The drop is recorded as a `rounds_drop` decision.

Check: `complete: true`, `replacement_check_ok: true`, `build_errors: []`, 20 main rounds, and either
20 extension rounds or an interim decision that was not INCONCLUSIVE.

On failure (pred/01 s6 V-g: "A bench that crashes may be restarted from scratch once; a completed
bench is never re-run"):

* **Crash, kill at timeout, or `complete: false`**: restart **from scratch once** with a new `--out`
  (`bench_m5cap102_r2.json`) and the same plan and equality file. Keep the crashed JSON and report it.
  A second crash means STOP: V-g fails and M5 is NOT DECIDED this session.
* **qrenderdoc hangs after the JSON says `complete: true`**: this is a known RenderDoc exit hang,
  not a crash. `m5_run.py` kills it at `--timeout`; otherwise run `taskkill //F //IM qrenderdoc.exe`.
  The bench stands.
* **Refusal before timing** (build failure, replacement not in effect, original module md5
  mismatch, seal mismatch): this is deterministic and not a crash. STOP and report; the result is
  INVALID (V-g). A harness fix followed by a new bench is the user's decision.
* **The main rounds completed but the extension could not run in-process** (the scorer says
  `EXTENSION REQUIRED` and the bench has no extension rounds, for example because `RD_EQUAL` was
  missing): append the extension in a new process. The bench records it as `extension_new_process`.

```bash
python C:/kyty/s102/m5_run.py bench --cap "$CAP" --plan $OUT/plan_m5cap102.json \
    --out $OUT/bench_m5cap102_ext.json --env RD_RESUME=$OUT/bench_m5cap102.json --timeout 21600
```

* **Never** re-run a completed bench, and never re-run one because of anything it measured.

## 5. scorer: the verdict (seconds)

```bash
python C:/kyty/s102/m5_102.py --plan $OUT/plan_m5cap102.json --bench $OUT/bench_m5cap102.json \
    --equal $OUT/equal_m5cap102.json --capture-log $LOG --out $OUT/m5_102_result.json
```

If the extension ran in a new process, pass `--bench $OUT/bench_m5cap102_ext.json`.

The scorer checks both seals and the file identity: the plan's sha256 must equal the bench's and the
equality file's `plan_sha256`, and the plan must carry both seal hashes. It then applies V-a to V-g
and computes X = S[V2]/S[A], Y = S[V2]/S[V2s] and L = S[V1]/S[A]. Each ratio drops the items that
fail V-e for its variant; for Y, an item that fails for V2 **or** V2s is dropped. The 90 % bootstrap
uses 20 000 resamples, seed 102, and the same round indices for all three statistics.

| status / verdict | meaning (pred/02 s3) | what to publish |
|---|---|---|
| `CLOSE-strict` | CI_lo(L−1) > 0.06 | G CLOSED. It holds on a component every G implementation pays. |
| `CLOSE-machinery` | CI_lo(X−1) > 0.06 and CI_lo(Y−1) > 0.06 | G CLOSED *with today's BDA machinery*. Name (i) the V2-only BDA machinery and (ii) `LDG.E.STRONG.SM`. Reopening G is the user's decision and must be recorded in ROADMAP.md first. |
| `NOT CLOSED` | (CI_hi(X−1) ≤ 0.06 or CI_hi(Y−1) ≤ 0.06) and CI_hi(L−1) ≤ 0.06 | M5 does not close G. G survives UNLICENSED; this is not evidence that the price is ≤ 6 %. |
| `… (decided at the point after extension)` | INCONCLUSIVE, then the points over 40 rounds decided | publish with that label |
| `EXTENSION REQUIRED` | INCONCLUSIVE and fewer than 20 extension rounds | see §4, RD_RESUME |
| `V2 INVALID - M5 NOT DECIDED this session` | V2 V-e failures above 40 % of the valid A-arm time | no verdict |
| `INVALID` / `NOT EVALUABLE (…)` | a control failed or could not be evaluated, or X, Y or L has no item left | no verdict; publish the reason |

Whatever the verdict, publish:

* X, Y, L, V2s/A and A/B with their intervals;
* every per-item ratio (B/A, V1/A, V2/A, V2s/A, V2/V2s);
* the V-e table, naming every "within replay noise" item;
* P1–P4, where a MISS is published and never repaired;
* register counts and SASS counts, which are reported and never decide.

Things no outcome may be used to claim are listed in pred/01 s8. Above all: no speedup and no
frame-rate gain.

## Wall-time summary

| step | expected | mechanics (session 49 capture, 3 modules) |
|---|---|---|
| find | 3–5 min (1.5 h if the sd mapping falls back to replay) | 149–175 s |
| plan | ≈ 1 min | ~2 s (7 modules) |
| equal | 5–15 min | 38 s for 2 items |
| bench (20 + 20 rounds) | 10–25 min | 46 s for 1 + 1 rounds |
| scorer | seconds | <1 s |
