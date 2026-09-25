# PRESEAL check: g2_119 (session 119, route A at W = 2, the G2 re-measure)

Adversarial pre-seal check by an agent. No game or emulator was run, nothing was built, and no existing file was edited.
Everything I ran was either read-only or isolated in my own scratchpad:
- the fixture suite, as a copy whose `BASE` points at scratch;
- the scorer's `--draft` path on the two unsealed smokes;
- a regeneration of the scorer into scratch;
- 8 probe mutants of my own, each in its own scratch folder.

I did NOT run `mut_g2_119.py`. `work_mut119/` was not empty, and the draft loop (`python mut_g2_119.py`, pid 15644,
started 23:38:30) was still running. At 23:56 it was on mutant #31 of 34 (`rule_le`).

**Verdict line: BLOCKERS: 0. MAJOR: 1 (procedural and conditional: go119a/procload cannot see the draft mutant loop).
MINOR: 17.**

## 1. The derivation (a104.py → g2_119.py)

**Confirmed:**
- `make_g2_119.py` regenerated into scratch gives a byte-identical file: sha256 `8b3e5853…7c84` (g2_119.py as it is now).
- The source is `a104.py` sha256 `dfa2313a…2b16`, as the docstring states.
- The normalised diff shows 49 whole-line edits and nothing else.

Each required change is present and correct:

| requirement | where | status |
|---|---|---|
| F₂ = 0.555 (ROADMAP 118 item 6) | g2_119.py:106, used in `g_of` default and in `kill_t4` (:854) | OK |
| sensitivity 0.564 (spk118 p90) | :107, :836, :849 | OK |
| spine = max(mut119 arm-0 `da_walk_us − da_queue_us`, 959) | :108, :814-815 (None when the mut level is missing ⇒ G None ⇒ NOT_EVALUABLE) | OK |
| T₂ from `shadowresolve=0\|1` | :97 (SH_ARMS), :101-102 schedule, :819-820 | OK |
| exactly one worker line `worker 0` | :758 `sorted(...) == [0]` | OK |
| `da_wjobs` out of both darkness checks | :736, :761 | OK |
| build `d3a981a2…0f64` | :85; installed exe = pinned copy = this sha (checked) | OK |
| `gates_base.txt` `303a7849…cbbf` | :88; file sha matches | OK |
| RULE print on the central G₂ | :1002 | OK |
| tags / paths | :81-82, :87, :100, :102 | OK |

`ENV_EXPECTED` + `ENV_PRESENT` (:163-167) are exactly the `KYTY_*` set of `smk119s.json` / `smk119m.json`.
`enter_scene.py` strips every inherited `KYTY_*` (:535) except `KYTY_GATE_SCHEDULE`, and sets the fixed five plus the
positional ones. Both schedule strings in `go119a.sh` equal `RUNS[...]['schedule']` exactly (string compare). The smokes
also give `RECORD_THREAD_TWO` = 2 and `PIN_ONCE` on this build. The bands hold with wide margins (smoke levels: `dt`
32 762–34 489, `rec_n` ≈ 10 935, `gpu_busy` 12 906–13 333).

**Left unchanged but broken or misleading at `dawalk=1`:**

- **MINOR — `G_spine_pref` (g2_119.py:839, printed :990-994) is meaningless at `dawalk=1`.**
  - `pl_pref_us` on GuestGpu is now 1.2 µs a flip (smk119m), so the "pref-based spine" is −1 651 µs.
  - The CENTRAL line then prints `pref spine: 5049.4`, a G₂ above the bar, right next to the deciding G₂ = 2 029.
  - s104 §5.4 defined this term under `dawalk=0`.
  - Fix: relabel it "n/a at dawalk=1" or drop it (whole-line edit, before the seal).
- **MINOR — the docstring still names the s104 runs and ROADMAP item.**
  - :30-33 give `cpu_net = sh104 …`, `S_raw = mut104 …`, `P_mw … of mut104`, `T_in … (mut104 arm 1)`.
  - :49 cites "ROADMAP s0.1 item 6"; the rule is now ROADMAP 118 item 6 / 119 item 1.
  - The pre-registration calls this docstring part of "the full rule set" (pred:17-18).
  - Stale comments: :124 (EXPECTED_LINE "verified on log_reg104.txt, 16ef56b6"; the smokes now verify d3a981a2) and
    :851 ("T4 at which the ceiling…", though the code computes the central).
- **MINOR — `spine_sh_arm0` (:816), the uninstrumented proxy, is computed but never printed.**
  - In the smokes it is 1 289 against the rule's mut arm-0 1 369 µs. `plkstat` also times the walker's
    `m_mutex` holds.
  - The rule names run (1a) (ROADMAP 118 item 6), so the scorer is right. Print the sh value for the report.
- **MINOR — A8's lower bound (959) is vacuous**, because the spine is ≥ 959 by construction (:909).

## 2. Draft scoring of the unsealed smokes

Command: `python g2_119.py --mut smk119m --sh smk119s --root C:/kyty/s119 --draft --start 900 --first 1200` (7 s,
rc 0).

**Expected draft failures only:**
- `PAIRS`: 22 pairs from 180 s.
- `PREREG_PINNED`: the smokes carry no prereg.
- protocol: schedule start 900 and hold 180.

Every other integrity check and control passes on both runs: SCHEMA, FIELD_ORIGIN, RAW_CONTIGUITY, GATEARM, ROW_ARMS,
AB_BA_BALANCED, STREAMS_COMPLETE, NO_FLOOR, MARKERS_OFF, NO_RECORDING, BINARY_SEALED, DURATION, BANDS, WORK_SPLIT (mut
0.068 %, sh 0.0008 %), AREA_VERDICT, AREA_SELECTED (split 0.003 / 0.010 %, match 100 %), PIN_ONCE, RECORD_THREAD_TWO,
no checkpoint, no fatal marker, no hang.

**The arming checks pass for real reasons, not vacuously.** Each darkness sum is over present fields; a missing field
returns None and fails the check.

| check | smoke values |
|---|---|
| MW_DARK_ARM0 | kept totals 0 against 6 736 483 |
| MW_IDENTITY_ARM1 | −0.26 % |
| AMUT_ARMED | `a_mut_us` 13 619 / 22 504, `a_mut_n` 60 207 / 70 050 |
| MUTSITE_HOLD_IDENTITY | `a_hold_n` = `mh_n + mh_disp_n` exactly (5 321.19 / 5 351.59) |
| PLKSTAT_IDENTITIES | `pl_prog_n/mh_n` −0.39 %, `pl_cs_n` = `dispatches` = 268 |
| PATHLAP_ARMED | `pl_em_n/mh_draws` +0.001 %, `pl_pref_n` 8, emit chain 0.985 / 0.985 |
| OTHER_INSTRUMENTS_DARK | `sh_jobs` 0 while `da_wjobs` 8 / `da_wskip` 8, which the old check would have failed |
| SH_DARK_ARM0 | 0 against 3 209 083 |
| SH_JOBS_PER_DRAW | 0.996 |
| SH_NO_DROP | 0 |
| SH_ONE_WORKER | `[0]`, log only, not duplicated in stdout |
| INSTRUMENTS_DARK (sh) | every `mh_*`/`pl_*`/`a_*` level 0 |

**Draft arithmetic.** It reproduces every number the pre-registration discloses:
- T₂ +1 983.1 ± 414.7;
- `cpu_net` 31 695.0;
- `S_lo` 13 619.4, `S_raw` 22 504.2, `P_mw` +17.9 ± 452.5;
- spine 1 369.4;
- `E_rec` 1 267.4, `E_com` 2 350.5;
- **G₂ 2 028.8**, G₂^ 3 989.0, kill-T₂ 1 011.9, H/M 0.731, cross-run area 0.014 %.

**The production path would not refuse a correct 300-s run.**
- Geometry: the draft (start 900, first 1200) rejects blocks 0–2 and excludes quartet 0. Production (1800 / 2100) does
  exactly the same.
- Expected pairs, from the smokes' post-stable frame rate: 29.34 fps (sh) ⇒ last frame ≈ 9 081 ⇒ **38 pairs**; 28.58
  fps (mut) ⇒ ≈ 8 855 ⇒ **36 pairs**. Both clear the bar of 30 with 6–8 pairs to spare.
- DURATION includes the entry frames, so it is ≥ 300 s.
- `hold_s` 300 and `attempts == ['attempt 1']` both come from go119a's arguments.
- `runs119/` is created by go119a before scoring.
- The only realistic refusal is a fatal marker such as `AsyncPipelines: skipped draw` (mut104's cause). The one allowed
  repeat covers it.

## 3. Fixtures and mutants

The suite, run as an isolated copy with `--real`: **81 fixtures (76 synthetic + 5 real), 0 failed, ALL OK** (44 s).

**Coverage of the changed members:**

| member | fixtures |
|---|---|
| spine max, both sides | proxy 1 300 > 959 via the recount; proxy 700 ⇒ 959 |
| the sh-walk exclusion | sh proxy 8 000 does not enter |
| F in the recount | typed independently as 0.555 |
| f_sens | recounted |
| the bar | exactly 3 000 ⇒ proceeds; 2 999.999 ⇒ closed |
| ceiling not deciding | covered |
| area | +2.9 % evaluable / +3.1 % not |
| pairs | 30 ⇒ ADMITTED / 28 ⇒ PAIRS |
| worker lines | 0, 1 and 2 lines, and `worker 1` alone |
| `da_wjobs` = 8 | admitted in both runs |
| s104 schedule, binary and tag | refused |

All 34 listed mutants have unique anchors. By reading, each one is killed by a named fixture.

**My 8 probe mutants** (isolated scratch copies, each with its own `BASE`): 2 killed, **6 SURVIVED**.

| probe | result | finding |
|---|---|---|
| spine read from mut **arm 1** | killed | Only by generator noise (≈ 0.8 µs): `generate()` gives `da_walk_us` no arm dependence. MINOR: make the walk arm-dependent. |
| ceiling spine forced to 959 | killed | — |
| **sh darkness without `mw_n`** (:761) | SURVIVED | MINOR: only `a_hold_us` is perturbed (test:451). Likewise `a_mut_us`, `pl_em_n`, `pl_proc_n`, `pl_prog_n` are unguarded on a changed line. Low real risk, because GATEARM + gate sha fix the sh arm texts. |
| **sh darkness without `a_mut_us`** | SURVIVED | Same as the row above. |
| **SH_ONE_WORKER with `set()`** (:758) | SURVIVED | MINOR: no fixture for a duplicated `worker 0 started` line. |
| **area check without `abs`** (:875) | SURVIVED | MINOR: the code is correct, but only the positive side is tested (test:323-331). Add sh area −3.1 % ⇒ NOT_EVALUABLE. This is a verdict line. |
| **A11b reverted to `>= 3000`** (:915-916) | SURVIVED | MINOR: predictions are checked by count only (test:288). No decision weight, but the discriminating prediction's direction is unguarded. |
| **sh tag regex widened** (:102) | SURVIVED | MINOR: only the mut tag is tested (test:571). This one fails safe: no such log under the production root. |

Mutants that also survive but fail safe (the production run would refuse rather than mis-score): `PRODUCTION_ROOT`,
`PRED`, `GATES_FILE`. The tests override them.

## 4. The pre-registration (pred/01_g2_119.md)

It states the rule, F₂, the 0.564 sensitivity, the spine term, T₂, the bar, the NOT_EVALUABLE conditions (either run
INVALID after its one repeat; cross-run area > 3 %) and what must not be claimed. The smoke disclosure is honest and
reproduces exactly (§2), including A4's miss, G₂ ≈ 2 029, kill-T₂ ≈ 1 012 and the mutants running during the smokes.

**Nothing was tuned after the smokes.** The timeline:

| time | event |
|---|---|
| 23:30:00 | ROADMAP item 1 commit `fe8faf6` |
| 23:32:31 / :33 | `make_g2_119.py` / `g2_119.py` (unchanged since) |
| 23:37:31 | `test_g2_119.py` |
| 23:38:30 | `mut_g2_119.py` |
| 23:38:45 → 23:45:49 | the smokes |
| 23:46:23 | `pred/01_g2_119.md` |

The pre-registration's predictions equal `predictions()` in the scorer, and the bands and population are unchanged from
s104.

MINOR corrections:
- pred:22 says **"mutants (33)"**; `MUTANTS` has **34**.
- pred:88-89, Known limits: "leaves the walk inside `cpu_net − S_ctx` (a double count against route A, as in session
  104)" is **false at `dawalk=1`**.
  - The walk now runs on the walker thread; GuestGpu's `pl_pref_us` is 1.2 µs.
  - So it is not inside `cpu_net`, and that conservative margin does not exist.
  - The spine is simply charged as new serial work.
- pred:40 says "`obs116`/`spk118` on this build read ≈ 33 000 …". But `obs116`'s `dt` is 31 650 (s116 FACTS), and
  `spk118` ran on 321175ab, not this build. Cite the smokes instead (32 762–34 489, ≈ 10 935, 12 906–13 333).
- The pre-registration says the population is "session 104's". s104 §3 expected ≈ 42 pairs, but at today's ~29 fps it
  is 36–38. State that.
- Disclose that the spine proxy comes from the instrumented mut arm 0 (1 369), against the sh arm 0's 1 289.

## 5. go119a.sh

**Confirmed:**
- Tags `sh119|sh119b|mut119|mut119b`; the schedules are byte-equal to the scorer's.
- The lock: checked, then taken atomically with noclobber, removed by the trap.
- The pinned copy is sha-checked before and after install.
- `--pred C:/kyty/s119/pred/01_g2_119.md`, `--gates-file`, `--attempts 1`, `--hold 300`, `--no-install`.
- `KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0` are positional.
- No `--rec`, no `KYTY_GPU_CHECKPOINTS`, stale artefacts moved, `runs119/` created.
- The env the sealed run will carry is exactly `ENV_EXPECTED` + `ENV_PRESENT`, as the smokes show.

**MAJOR (procedural, conditional): the exclusivity gate cannot see the draft mutant loop, which is running now.**
- `procload.py` matches only `mutlib` by name (:28-38).
- Its per-process rate skips any process that is not in both 10-s snapshots (:54 `key not in a`). Each
  `test_g2_119.py` child is new and lives about 44 s, while the parent `mut_g2_119.py` is idle, so a single sample misses
  the loop about 1 time in 4. The `--wait-s 1800` retry loop simply waits for such a miss.
- The aggregate CPU check (< 15 %) cannot see one busy core of 32 (≈ 3 %).
- If go119a is launched while this loop (or any sequential test loop) lives, a sealed timing run can share the machine.
  s103 and s104 treated that as MAJOR.
- Fix: confirm the loop has ended before launch, and add a name guard to go119a, e.g. refuse while any process command
  line matches `mut_g2_119|test_g2_119|mut_.*\.py`.

MINOR:
- The scorer's `tag_re` accepts `_entry1`, but go119a cannot launch such a tag, and the pre-registration does not say
  how an entry hang is handled. s104 §2 did.
- go119a does not check that `sha256(pred/01)` equals the scorer's filled `PRED_SHA` before launching. An unsealed or
  edited pre-registration would only surface at scoring, as a wasted INVALID run.

**BLOCKERS: 0**
