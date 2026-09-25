# mutlib v4.1 acceptance (2026-09-25, quick)

**Harness:** `C:/kyty/s106_stage/mutlib/mutlib.py`, sha256 **`db82ef4bcf05ddea365f50c403029bfc5d2a7a4400a12d254a6b0cc6ab3e6dde`**.
I checked the hash before and after every run; nothing changed it. `mutlib_v4.py` is still byte-identical to v4
(`b666df3594ec245f488585b93ec7282fee5bfdff16d45e34cad60b01dd9f922b`), and so is the frozen copy in
`docs/session-115/mutlib_v4/`. No game, emulator build or git operation was run. Everything was written under
`C:/kyty/s106_stage/mutlib/`: `accept41/`, `adversarial/old_work/` (the oldstyle reference runner) and the shared
memo cache `cache/`. No project scorer, suite or mutant script was edited.

**Gate.** Both heavy runs went through `accept41/gate41.py`. It requires `C:/kyty/s116/V41_GO` to be present, no
`C:/kyty/SEALED_RUN.lock`, and no other `mutlib.py` process. The runs went one at a time. A `mutlib_v4` run on obs116
(not mine) finished before my first run. During both heavy runs a game (game-Y) was using
0.9–2.7 CPU s/s out of 32 logical CPUs, which gate41 recorded in `accept41/out/heavy41.log`. The timings below
include that load.

**Verdict: PASS for all four items, with two reservations.**
(1) **The 10-minute target is not met with `--no-memo`:** the selected ttl114b seal takes **18.0 min**.
(2) **Finding F1** (below) is a selection hole of the same kind as review5 MAJOR-1, with a narrower trigger. It does
not affect the ttl114b seal.

| item | result |
|---|---|
| 1. ttl114b selected, `--control --no-memo` | **PASS**: 185 of 345 selected (12 scorer-line + 133 kill-case-changed + 40 of 200 sampled). **185 / 185 rows equal** session 114's full report (verdict + kill label). ALL KILLED, controls 3 / 3. **1 081 s = 18.0 min** |
| 2. The same with the memo on (timing only) | **PASS**: the same 185, 185 / 185 equal, ALL KILLED, controls 3 / 3. **632 s = 10.5 min** with a hot memo cache (the builder's run had filled it with the same inputs). The builder's first memo run: 910.7 s = 15.2 min |
| 3. review5 J and A, the builder's synthetic S → H / W (plus review5 I) | **PASS**: every reference verdict reproduced, and every row agrees with `adversarial/oldstyle.py` (which shares no code with mutlib) |
| 4. check112, check115, full `--control` | **PASS**: check112 24 / 24 and check115 104 / 104 rows equal their references, controls 3 / 3 each |
| extra: five new derived-suite probes on the synthetic parent | 4 of 5 are sound. **F1:** the `dupname` probe is certified ALL KILLED, but the full run and oldstyle both give SURVIVORS `['limit_gt', 'limit4']` |

## Item 1: ttl114b selected, `--no-memo` (the seal path)

Command (`accept41/heavy41.sh`, run `h1_nomemo`; 28 workers = cpu_count − 4):

```
python mutlib.py --scorer C:/kyty/s114/ttl114b.py --test C:/kyty/s114/test_ttl114b.py \
  --mutants C:/kyty/s114/mut_ttl114b_sealed.py --changed-from C:/kyty/s114/ttl114.py \
  --parent-report C:/kyty/s114/mut_ttl114.out.txt --control --no-memo \
  --work-dir C:/kyty/s106_stage/mutlib/accept41/work_h1_nomemo --cache-dir C:/kyty/s106_stage/mutlib/cache
```

The inputs had the sha256 their reports name: `ttl114.py b8459c3d…`, `ttl114b.py 5d5f2738…`, `test_ttl114.py 0edede85…`,
`test_ttl114b.py 7981778a…`, `mut_ttl114_sealed.py 03cbd889…`, `mut_ttl114b_sealed.py 015f2c55…`, the parent report
`mut_ttl114.out.txt 4ca3d496…` (mutlib 2, ALL KILLED, 342 rows) and the reference `mut_ttl114b.out.txt 3dcd1999…`
(mutlib 2, all 345, ALL KILLED).

**What was selected and why** (the dry run agrees with the builder's):

| reason | mutants | notes |
|---|---|---|
| scorer-line | 12 | anchors on the 22 changed lines of `ttl114b.py` (7 of them are also not-in-parent: new mutants) |
| kill-case-changed | 133 | 21 kill cases changed; most of the mutants come from `PENDING` (69) and `CONSTANTS` (24), then `PRED_misses_hi` 6, `S1_edge` 4, `ARMED_edge` 4, ... |
| not-in-parent | 0 | (as a first reason; the 7 new mutants are listed under scorer-line) |
| machinery-changed | 0 | the machinery is equal (73 items); 35 of the parent's 169 cases changed or were removed; 0 added |
| sampled | 40 of 200 | fraction 0.2, seed 6728139490508904953 (from the scorer's sha256) |
| **selected** | **185 of 345** | |

**An outside check of the selection** (`accept41/selcheck41.py`, which uses no mutlib code). It compares the selection
with the parent report and with session 114's full derived report. All 160 unselected mutants are KILLED in the full
derived run, each **by the same case as in the parent report**, so the vouching holds on this seal. Also, none of the
185 selected mutants has a different kill label in the full run than in the parent. The selection was conservative
here.

**Result:** `PASS: 185 mutant rows (reference 185), 185 equal (verdict + label); controls 3 of 3 survived; ALL KILLED`
(`v4check/compare_rows.py --subset`).

**Time:** wall **1 081 s (18.0 min)**, worker time 27 161 s. The two baselines took 685 s and 678 s, the controls about
620 s each. Fixture replay was on: 221 / 221 generator calls validated, 39 338 replayed. The mutant jobs add up to
23 936 s (median 8 s). 39 jobs took more than 300 s (kills by late cases, up to 628 s).

## Item 2: the same with the memo on (timing only)

Run `h2_memo`: the same command without `--no-memo`, using the shared memo cache `C:/kyty/s106_stage/mutlib/cache`.
Rows: **185 / 185 equal**, ALL KILLED, controls 3 / 3.

| run | memo cache | baseline | worker time | wall |
|---|---|---|---|---|
| accept41 h1, `--no-memo` | (not used) | 685 s | 27 161 s | **1 081 s = 18.0 min** |
| accept41 h2, memo on | hot: the builder's 17:41 run had just filled it with the same fixtures | 328 s | 12 767 s | **632 s = 10.5 min** |
| builder's run, memo on | the fixture entries were written during that run (files dated 17:47–17:53) | 752 s | 22 708 s | 910.7 s = 15.2 min |

h2 therefore shows what a **repeat** seal costs with the same inputs. For a first seal of a new derived scorer, the
builder's 15.2 min is the better estimate.

## Is a selected ABBA seal ≤ 10 min with `--no-memo`? **No: 18.0 min.**

* **The baseline alone is over the target.** The wall can never be shorter than one baseline run of the full suite, and
  without the memo that takes 685 s (11.4 min) on this machine. No selection can bring a `--no-memo` seal of a
  ttl114b-sized suite under 10 min.
* **The work above that floor:** 27 161 s of work over 28 workers is at least 970 s. The work splits by reason, in
  `--no-memo` mutant time: scorer-line 67 s; kill-case-changed 12 912 s (18 of the long jobs); **sampled 10 957 s
  (21 of the 39 long jobs)**. The 20 % sample costs about as much as the 133 required mutants.
* Only the memo gets near 10 min, and only with a hot cache (10.5 min). The project rule for derived scorers is
  `--control --no-memo` (review5 MINOR-3: the memo can change the iteration order of int sets), so today's seal path
  takes about 18 min. That is still better than a full `--no-memo` run of all 345 mutants (not measured; the full v4
  run with the memo took 20.3 min).

## Item 3: triples J, A and the synthetic S → H / W (`accept41/small41.sh`, 2 workers each)

Independent references: I reran `adversarial/oldstyle.py` (the old per-mutant loop, no code shared with mutlib) on
every triple (`accept41/out/old/`). `accept41/compare_old41.py` compares each mutlib row with oldstyle: the verdict,
and whether the kill label is the first failing case.

| run | result | agrees with oldstyle | other |
|---|---|---|---|
| J parent, full (the parent report, sealed now under v4.1) | ALL KILLED | 10 / 10 | |
| J, full | SURVIVORS `['limit_gt', 'limit4']` | 10 / 10 | |
| **J selected** (`--changed-from sc_j_parent.py --parent-report` the new parent report) | **SURVIVORS `['limit_gt', 'limit4']`** (reference); 2 scorer-line + 4 kill-case-changed (`three` → limit_gt, limit4; `cap_edge` → slow_ge; `cap_out` → slow_ret) + 1 of 4 sampled = 7 of 10 | 7 / 7 | 7 / 7 rows equal J full |
| J selected with review5's own parent report `J_parent.v4.report.txt` | the same | 7 / 7 | 7 / 7 equal to review5's J_full |
| **A**, defaults | **SURVIVORS `['tag2_equiv']`** (reference; v4 gave a false kill). Replay turned itself off: "copies files in a way that raises no audit event" | 3 / 3 | controls 3 / 3 |
| S parent, full | ALL KILLED | 10 / 10 | |
| H full / **H selected** | SURVIVORS `['limit_gt', 'limit4']` both. Selected: 0 scorer-line + 2 kill-case-changed (`three`: the helper `is_go` changed) + 2 of 8 sampled | 10 / 10, 4 / 4 | |
| W full / **W selected** | ALL KILLED both. Selected: the machinery differs at `def make` → machinery-changed, all 10 run | 10 / 10, 10 / 10 | |
| review5 I (v41check/i copy) | SURVIVORS `['tag_b', 'tag_c', 'tag_d']`, `workers: FORCED TO 1` (the CopyFile2 shim made the outside write visible) | 3 / 3 against review5's `I_copy2.old.txt` | controls 3 / 3 |

## Item 4: check112 and check115, full `--control` (2 workers)

| run | result | time |
|---|---|---|
| check112 | `PASS: 24 mutant rows (reference 24), 24 equal (verdict + label); controls 3 of 3 survived; ALL KILLED` against `accept3/check112.report.txt` | 10.9 s |
| check115 | `PASS: 104 mutant rows (reference 104), 104 equal; controls 3 of 3 survived; ALL KILLED` against `C:/kyty/s115/mut_check115.out.txt` | 165.1 s |

## Extra: five derived-suite probes (`accept41/probe41.sh`, `accept41/probe/`)

Each probe is a derived suite built from the synthetic parent suite `test_s_parent.py`, run with the derived scorer
`sc_s2.py` (only its docstring changed). The parent is the S report sealed in item 3. Each is selected twice: with the
default sample, and with `--sample 0` to show the rule alone. The reference is oldstyle on the derived triple.

| probe | the change | oldstyle survivors | v4.1 selection (rule alone) | verdict of the selected run |
|---|---|---|---|---|
| reorder | case `zero` moved first | none | nothing changed → 0 | ALL KILLED (correct) |
| lambda | `cap_out`'s check weakened inline | cap_up, high_ret | kill-case-changed `cap_up`, `high_ret` | SURVIVORS cap_up, high_ret (correct) |
| const_eq | `cap_edge`'s rows moved into a module-level constant, same values | none | kill-case-changed `cap_ge`, `cap_down` | ALL KILLED (correct) |
| const_weak | the same constant, 50 → 49 | cap_ge, cap_down | kill-case-changed `cap_ge`, `cap_down` | SURVIVORS cap_ge, cap_down (correct) |
| **dupname** | an **added** case `case('three_b', make('three', [1, 2, 3, 4]), is_go)` reuses the fixture name of case `three`, so the shared writer overwrites three's log | **limit_gt, limit4** | **nothing**: "changed or removed: none; added: ['three_b']" | **ALL KILLED: WRONG** (a full v4.1 run of the same triple gives SURVIVORS `['limit_gt', 'limit4']`, and so does `--sample 1.0`) |

### F1: two cases writing the same fixture through the writer are not linked (hole; same impact as review5 MAJOR-1)

`SuiteModel` links a writer-calling case only to cases that read `BASE` outside a writer or that use a shared fixture
object (`mutlib.py` around lines 5832–5847: `direct = ... (w['writes'] and (u['base'] or u['shares'] & w['shares'])) or
(stateful ...)`). **Two cases that both call `make()` are never linked.** A derived case, added or changed, that writes
a fixture name another case also writes therefore changes what the unchanged case reads. That case's kills stay
vouched for by the parent report, and only the 0.2 sample guards them. The README's *Limits* paragraph does not
describe this: it lists files "found by a path built from something other than BASE or a shared fixture object", but
here the path is built from `BASE`, inside the writer.

* **Trigger:** a fixture-name collision between two cases of the derived suite. That is a suite bug (the new case also
  tests the wrong fixture), and a copy-and-paste in a derived-suite generator can produce it.
* **ttl114b is not exposed.** Its suite passes 125 literal names to `make` / `variant`, with no duplicates, plus 16
  name patterns with their own prefixes. The parent and derived suites have the same name structure, and the outside
  check above (all 160 unselected mutants killed by the parent's case) confirms this seal.
* **A cheap fix:** evaluate the writer's name argument statically, as the group-name evaluation already does. Link
  every pair of writer-calling cases whose names can collide: the same literal, or a name that cannot be evaluated.
  With the link, the dependency's fingerprint also changes the victim's fingerprint, so an added colliding case is
  caught as well.

## Recommended seal command (a derived scorer with a sealed parent)

```
python C:/kyty/s106_stage/mutlib/mutlib.py --scorer <derived>.py --test test_<derived>.py \
  --mutants mut_<derived>_sealed.py --changed-from <parent>.py --parent-report mut_<parent>.out.txt \
  --control --no-memo --work-dir C:/kyty/s106_stage/mutlib/work --cache-dir C:/kyty/s106_stage/mutlib/cache \
  --out mut_<derived>.out.txt
```

For ttl114b: `--scorer C:/kyty/s114/ttl114b.py --test C:/kyty/s114/test_ttl114b.py --mutants
C:/kyty/s114/mut_ttl114b_sealed.py --changed-from C:/kyty/s114/ttl114.py --parent-report C:/kyty/s114/mut_ttl114.out.txt`
(18.0 min).

Until F1 is fixed, before sealing, check that no two cases of the derived suite pass the same fixture name to a writer
(an AST scan of `make(...)` / `variant(...)` name arguments, as in this acceptance). If they do, run the full set
(drop `--changed-from`). A scorer without a sealed parent: the same command without `--changed-from` /
`--parent-report`.

## Files

`accept41/`: `gate41.py` (the gate), `small41.sh` (items 3, 4), `heavy41.sh` (items 1, 2 and the dry run),
`probe41.sh` + `probe/test_p_*.py` (the extra probes), `compare_old41.py` (mutlib against oldstyle),
`selcheck41.py` (the outside selection check). Outputs are in `accept41/out/`: `small41.log`, `heavy41.log`,
`probe41.log`, `rep/` (small reports), `old/` (oldstyle references), `heavy/` (`ttl114b_dryrun.txt`,
`h1_nomemo.report.txt`, `h2_memo.report.txt` with their stdout / stderr) and `probe/`.
