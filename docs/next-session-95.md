**Session 94 closed the last candidate of the scale the goal needs. Session 93's LICENSED (7 198.9 µs,
78 % of it the assumption that a merged draw is free) did not survive measurement: moving V# slots
onto BDA enables exactly one thing — reusing the previous draw's descriptor set — and that removes at
most 197.3 µs a flip; with the slots that can actually convert (`Ceiling_bind_ro` 1 001.3 µs) the gross
ceiling is 1 198.6 µs, CLOSED by the table sealed in session 93. The naive synchronisation it would
need costs +10 807.8 µs a flip of GuestGpu CPU in the regime every launch of session 94 ran in.** Two
gates, 49 counters, two VALID runs, no default moved, nothing shipped. Read `docs/ROADMAP.md` first,
then `C:/kyty/s94/FACTS.md` — **§0.1 and §0.2 first: six defects of my own text and ~20 corrected by
an independent audit; every number reproduced.**

Session 94's commits are on `merge-upstream` (sources `4912ae5`, record after it). **Source changed and
was built twice (`patch_s94.py`, `patch_s94b.py`); NO default changed.** The installed
`kyty_emulator.exe` is **`4338ba1a300a17be170167a4291748f8a93ad282f4c1c27a4c93084752386b4e`,
23 642 624 bytes**, and was not rebuilt after acceptance. Harness — **`C:/kyty/s94`**; port it to
`C:/kyty/s95` with a script written **fresh in the SOURCE directory** (`C:/kyty/s94/s95_port.py`),
modelled on `C:/kyty/s93/s94_port.py`. `gates_base.txt` **unchanged** — 1092 B, 99 names, sha256
`00c116dc…0594d8`.

## 0. Read first

1. `docs/ROADMAP.md` — §0.1 (the table now has the BDA row), §3 (three new closed rows), §5 item 4 (е),
   §7 (the s93 debts closed, three new ones).
2. **`C:/kyty/s94/FACTS.md` — §0.1 and §0.2 FIRST**, then §2.3 (the verdict and its robustness
   table), §3.2–3.4 (where the BDA cost goes; the regime), §7 (not closed).
3. The sealed pre-registrations `C:/kyty/s94/pred/01_mergecost.md` (9 972 B, `1cff373f…`) and
   `pred/02_bdaall.md` (5 314 B, `7560a476…`). **Do not edit them, or `FACTS.md`, or `README.md`.**
4. `C:/kyty/s94/read94/` — the reading (5 readers + verifiers), the patch review (3 lenses) and the
   FACTS audit (4 auditors). The audit files are the fastest way to see what a first draft gets wrong.

## 1. Where the programme stands — say it out loud before anything else

60 FPS = 16 667 µs against a shipped 31 642 µs: ~15 000 µs must come out, and the vblank plateau pays
nothing for less. Routes A (20 838 µs floor), B (0.7–2.5 ms), C (514 µs), D1–D4 and now **BDA
(1 198.6 µs gross)** are closed. **No candidate of that scale is on the board, and no known
combination of the remaining levers reaches it.** The frame on this binary (unarmed arm of `mc94a`,
per flip): `mh_bind` 11 174, `mh_emit` 7 531, `mh_prog` 6 033, `mh_disp` 2 191, `mh_rt` 789 µs; 87 % of
a draw's timed cost lies before the point where it is known what the draw differs in, and every block
of that has been closed as a lever.

**The first thing this session does is put that to the user** — whether to continue with sub-3-ms
levers that cannot move the scoreboard on their own, or to re-scope the goal (e.g. other scenes, other
titles, correctness). If the session runs without the user, do the measurement work below and say the
odds in the first line of the report. **Do not promise 60 FPS.**

## 2. What is settled — do not reopen

`ROADMAP.md` §3, plus everything sessions 91–94 closed. **New in 94:** the BDA conversion as a route
(gross 1 198.6 µs); "a merged draw is free" (≥ ~95 % of a `dm_buf1_ok` draw survives); PrepareBda on
every draw (+10.8 ms, OLD); const-bank as a binding lever (`bc_cb_ns` 1 619.1 µs; every option < 2 000
except BDA, which closes only net). Do not re-derive P: it is 642.3 a flip, all push-descriptor
pipelines; no pooled set repeats.

## 3. The work

### 3.1 FIRST: the BDA regime — the one lever of this size still unexplained

In the OLD regime (`bda_scan` ~1 060 regions a flip, `buf_new` 1.3–2 a flip) **PrepareBda alone takes
2 242 µs a flip** (`bda94a` unarmed arm, `a_mut_us` under `mutwide=8`); in the NEW regime it scans ~50.
OLD is the common state (6 of the 8 launches checked: `stg92a`, `wak92a_warmup`, and all four of session
94; NEW: `wak92a`, `bl93a`). Every log reads 13–21 over frames 2–175, jumps to ~1 050 around frames
177–210, and a NEW launch leaves that level later (`bl93a` at frame 277). **What makes a launch leave
it is not known**; `buf_new` (which also counts temporaries) and the registration epoch
(`renderContext.cpp:342-344`: a registration change forces the next miss to rescan everything) are the
first suspects. This is a measurement, not a build: name the mechanism by reading, then count it
(which buffers are created and destroyed each frame in OLD, and by whom — GC eviction and re-creation?).
**Say the predicted saving in µs before the patch, and say it against the plateau: ~2 ms does not move
the scoreboard by itself.** If a fix is built, measure it with `KYTY_GPU_CLOCK_PIN=1`, and record the
regime of the frames before the schedule in every launch.

### 3.2 SECOND: the written bc_ok slots — 490.5 µs a flip for 1 001.7 slots, 0.49 µs each

8× the price of a read-only slot (59.3 ns). Never split: `ObtainBuffer`'s write path (`is_written`,
`ForEachUploadRange`, `RecordGpuWrite`), `InvalidateMemoryFromGPU` over written ranges
(`descriptors.cpp:333-335`), the image invalidation it can trigger. One rolling chain of `Enabled()`
marks inside the Ok return path, booked by `resource.written`, splits it.

### 3.3 The debts (`FACTS.md` §7)

* Why the other half of s93's merge population cannot reuse its set, draw by draw.
* The GPU side of `bdaall` (+4 840 µs) and its ~2 580 µs of unattributed CPU; `C_bda` in the NEW regime.
* Carried: the single-chunk notify (99.9 µs); the `ObtainBuffer` stream-ring timer (lite = 0);
  `pfhint`/`pfcap`/`dapin` with the pin and the record path on; route B items 2, 8, 10, 12, 3.

### 3.4 The port — FIVE root constructs now, each a separate edit

1. the head of every `--roots` default (`arms.py:29`, `baseline.py:83`, `effect.py:103`) — new root in
   FRONT, `s94` stays;
2. `area_verdict.py:56` `range(94, 70, -1)` → `range(95, 70, -1)`;
3. `shift91.py:35` `range(94, 66, -1)` → `range(95, 66, -1)`;
4. the tuple-spelled chains: `stg92.py:44`, `bda93.py:41`, **and `s94lib.py:21`
   `ROOTS = ('C:/kyty/s94', 'C:/kyty/s93', 'C:/kyty/s92')`** — a literal rewrite drops `s94` and makes
   `log_mc94a.txt` / `log_bda94a.txt` unreachable to `mc94.py` and `bda94.py`;
5. **`regime94.py` picks its root by tag** (`'C:/kyty/s93' if tag.startswith('bl93') else
   'C:/kyty/s94'`) — a literal rewrite points it at `s95` for the session-94 logs.
Historic windows (`ft81.py`, `inventory81.py`, `patch_context85.py`) are not touched. `gates_base.txt`
byte-identical; `gen_gates.py --check` reports "out of date" BY CONSTRUCTION (99 of 124 names pinned) —
never rerun it without `--check`. `.sh` files copy byte-exact and point at their own harness: write
`accept95.sh` new, with a step 5 pointing at session 95's own sealed pre-registration (never `mc94.py`
or `bda94.py` on a new tag — each verifies its own sha256 and keys off its own arm texts). **Every
carried `s8x/s9x_port.py` inside a harness is a self-copy (SRC == DST): never run one.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.**

## 4. Do NOT

* **Do not write or dry-run the scorer after sealing.** Session 94 did both 3–4 minutes after sealing
  and its first draft said "before". Write the scorer, dry-run it on the record with relabelled arms,
  THEN seal (the scorer gets the sha filled in after).
* **Do not decide that an arm fired from `counter > 0`** — session 94's own scorer did, in the dry run,
  on a straddle of 1.09 a flip. Decide by the GateArm text and by magnitude.
* **Do not score a band on a counter that never fired** — it prints a vacuous HIT at 0.0.
* **Do not say a thing "cannot be addressed" of today's copy of it** — say it of the bytes (the
  ring-backed cb slots are guest memory).
* **Do not quote a number without its regime** when PrepareBda is involved (OLD vs NEW), in the
  headline too.
* **Do not quote two t values for one endpoint** — `endpoint84.py` (sample SD) is the endpoint;
  `s94lib.paired` uses the population SD.
* **Do not demand an exact zero on a schedule arm** — both session-94 leaks sat at distance 29 of 30.
* A foreign game on the GPU is a hard stop (check `nvidia-smi` before launching); `summary4.py`'s
  `cpu_net_us` IS `cpu_gpu_us` under lite; guards check 6 is not a criterion and check 10 hashes the
  exe installed at that moment — never rebuild between acceptance and the final answer;
  `gen_gates.py --out X` without `--with` overwrites `gates_base.txt`; never pipe a writing script
  through `head`.
* Carried: pre-registrations sealed in place and never edited; a failed control is REPAIRED under a NEW
  sealed pre-registration; a run that fails admission is REPLACED, not discussed; the first entry after
  a fresh build hangs (`--warmup-first`); ratios of sums, never per-frame identities; a knob a schedule
  must flip cannot be read once per process.
