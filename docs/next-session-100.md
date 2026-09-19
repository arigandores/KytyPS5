# Session 100 — route E, M3: the wide rule after the finished bindings-only arm

**Order M3 → M4 → M5 stays** (the user's decision, session 97). Read `ROADMAP.md` **first**, as the
standing context demands: §0.1 (session-99 addendum, from line 328), §2 E (M3; the session-99 block at
1152), **the sealed M3 rule at 1081–1082**, §4 (1237–1250), §5 item 5 (1319–1334), §6 (1338–1347), §7
(1404–1409). Then `C:/kyty/s99/FACTS.md` in full (in git `docs/local-session-99.md`), then
`C:/kyty/s99/README.md`, `RUN_STATUS99_B.md`, `VISUAL99.md`, and the five sealed rules
`C:/kyty/s99/pred/01_bindings_only.md` (10 848 B), `02_settled_bindings.md` (13 461 B),
`03_image_lifetime_diagnostic.md` (4 724 B), `04_gc_audit.md` (7 835 B),
`05_observer_separation.md` (8 583 B) — all five together exist only in `C:/kyty/s99/pred/`; in git they
are split between `docs/session-99/` and `docs/session-99/continuation/`. **Sealed texts are immutable:**
a correction goes into a new sealed addendum, never into the file. HANDOFF §3 is frozen history, not a plan.

**Open the report with the three numbers:** budget ≤ ~3.0 µs a draw (median) / ≤ ~2.3 µs (p99, 7 284
draws); the carried reference path is 6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms — **session 99
measured no new baseline**; undone: **M3 (GAP), M4, M5**; chance ~15 % (8…25 %). **Do not promise 60 FPS.**

## 0. Where M3 stands

* **Global M3 is GAP and session 99 did not move it.** Session 98's full floor: `F_a` = 14.274 ms
  (`bf98a`), `F_c` = 12.825 ms (`bf98c`, without the M1 workers), with the user's constant
  **2.2535 = 1.66 (images) + 0.49 (writable slots) + 0.1035 (submission sync, `bd96b` +103.5 µs)**
  ⇒ VERDICT_INPUT **15.078…16.527 ⇒ GAP**. CLOSE needs min + 2.2535 ≥ **15.5** (missed by **0.42 ms**),
  PROCEED needs max + 2.2535 ≤ **11.0**. The superseded 2.65 prints beside (15.475 / 16.924 — also GAP).
  The L3 bound printed beside those runs is **1.578 ms** (`bf98a`) / **1.577 ms** (`bf98c`).
* **Session 99 finished the gap branch's bindings-only arm (`bfmode=2`) on both instruments.**
  `bf99g` (a): **B_a = 30.049869 ms**; `bf99h` (c): **B_c = 37.367904 ms**, both on the CPU-burn clock —
  the endpoint is the **median of the retained armed block means of
  `(cpu_gpu_us − spin_gpu_us − bf_burn_cpu_ns/1000)/1000`**. The wall variants **30.596798 / 37.984520**
  print beside and decide nothing. Each run: 900.3 s, **45 falling edges, 88 pairs**, 2 552 rows an arm
  (44 AB + 44 BA), controls **43/43** and **44/44** technical plus **6/6** strict, work **−0.245536 %** /
  **+0.105147 %**. The parent recounted the raw personally.
* **Verdict of that arm: HIGH, DIAGNOSTIC ONLY, addend 0** (`min(B) ≥ 15.5`;
  `combined99_score.json`, SHA `293373ff…`: `{"status":"DIAGNOSTIC_ONLY","diagnostic":"HIGH",
  "addend_ms":0,"bindings_only_measurement_complete":true}`).
* **What HIGH does not do.** `pred/02` §6: *"Every branch leaves global G/R1 alive/unlicensed and prior
  global M3 state unchanged"*; `pred/01` §4's table says the same branch by branch and adds *"No
  available outcome here produces global CLOSE, PROCEED-to-M5, or 60 FPS. M3 stays open."* The
  lower-bound condition **`min(B_i − P_i) ≥ 15.5` is NOT available**: no finite bound **P** on the
  pessimistic work this instrument retains or adds (its own new counters included) has been proved.
  Mode 2 deliberately keeps **real materialisation and real clears**; in the seal's own words, *"the
  wider G removes materialization; R1 is not constrained to preserve its current algorithm"*. Zero
  addend is **an explicitly optimistic CPU screen**, not a rewrite budget, and it does not assert that
  the preserved materialisation already contains **all** the old 1.66 + 0.49. **M4 and M5 are not
  started and are not silently advanced.**
* **Selector fixed before any data; the burn frozen before the deciding run:** **period 90, start 1800,
  n ≥ 2100, idx 60..88 inclusive (29 rows), complete original ABBA quartets 4k..4k+3** (an incomplete
  quartet is dropped whole — no re-pairing, no posthoc window), plus a direct GC audit. **T\* no longer
  trims the endpoint population** (`settled99_norec.py` keeps `scheduled[60:89]` as is) — it survives
  only as the latch-leakage / darkness structure of `pred/02` §3. Burn LOCK a = **17800**: the TUNE
  chain ran on the pre-GC binary `2a6bb538…` (`eng99a1` 20000 → TUNE 19100; `eng99a2` 19100 → TUNE
  17800; `eng99a3` at 17800 gave **no LOCK**, image proxy R6′ = 52 > 50), and `eng99a4` is a **fresh
  reset pilot under `pred/04` with no source JSON**, which LOCKed 17800 as an open engineering prior —
  `pred/04` §4 rejects a1/a2/a3 as identities, so they cannot be replayed into acceptance. Burn LOCK
  c = **10200** (`eng99c1` C9 FAIL 15.35058 % → TUNE; `eng99c2` LOCK). `aa99plain` gave **AA_PASS**.
* **Failures stay failures, and are not rescued by a new window, normalisation or relaxed limit:**
  `cal99a` NOT ADMITTED (work −4.097420 %, **17 < 30** falls, C5 0.040974 > 0.02); `bf99e` (with
  recording) NOT MEASUREMENT (work −0.710639 %), **no B may be extracted from it**. Report-only FAILs
  **inside the admitted runs** must stay visible in the write-up: whole-window work −1.490551 % /
  −1.292076 %, `reported_old_area_verdict = INVALID`, the bf96-era C1 leak 0.004638 / 0.004407 vs
  ≤ 0.001, C4, **the sealed C8 (armed `cpu_gpu_us` +2 238.3 / +2 577.6 µs a flip ABOVE unarmed) and its
  T\*-trimmed repair C8″ (+2 478.6 / +2 746.9); C8′ — the same subtraction over the whole window —
  PASSES, and the form that decides here is the new CPU one, `technical.C8_CPU`**, C6 (1064 / 1065),
  s98 `rv98` R3 (R3′ passes), image R6/R6′ (`bf99g` 54/64 both FAIL; `bf99h` R6 45 PASS, R6′ 54 FAIL).
  Both `*_score.json` close their bf96-era block with the old scorer's own line **`CONTROLS FAILED /
  NOT ADMISSIBLE — no number of section 9 may be published (criterion 3 INVALID; controls failed: C4,
  C8'')`** — quote it **with**, never instead of, the 43/43 + 44/44 + 6/6 of the sealed settled scorer.
* **The image-birth proxy FAILs already have a measured explanation, and it is not a loss:** `life99a`
  (`pred/03`, 300.1 s, `KYTY_IMAGE_LIFETIME_TRACE=1`, diagnostic only, no CPU endpoint, on
  `2a6bb538…`) traced **64 121 events — 32 652 creates, 31 469 frees, ZERO armed-interior frees**: the
  mechanism R6/R6′ were built to catch did not happen; the excess recovery births are new BC5/BC4
  signatures and recreations whose GC deletion happened before the current floor interval. That is why
  R6/R6′ are report-only and why `pred/04`'s direct audit replaced the invalid proxy for future data.
  **Do not re-open image births as an unexplained failure.** The audit's own admission rule for future
  data (`pred/04`): five fields present and non-negative on every row, `checks > 0`, `hold > 0` on each
  retained armed block, **bad = critical = evict = 0 over the entire raw log**, `BindFloorGcAudit:
  mode1` in the log — and it **checks a subset of hold states, not the full base/pending
  implementation**: targeted mechanism coverage, not an identity-complete proof of cache correctness.
* **Correctness, as far as it is established:** `bf99e` (destructive floor) **185 detector events /
  18 037 frames — 174 map to arm-1 rows, 11 to arm-0 rows**, and the audit's caveats travel with the
  number (the arm label *"is not proof that each image's content was generated wholly under that arm"*;
  the count is *"a count of qualifying three-frame centers, not 185 independent incidents"*). The
  ordinary recorded control `vis99base` (900.3 s): **17 802 decoded frames, 0 events**, all 178 gate
  assignments 0; the parent inspected the fixed 450 / 825 / 900 s frames and **did not see** the
  reported effects; the user saw no glitches during the run. **That is non-reproduction without the
  floor — not the cause, not per-pixel identity, not an exhaustive defect count**, and it does not
  separate the normal renderer from the recording path; the last 8 presents (17795..17802) have no
  `FrameTrace` row. A diagnostic floor is not an optimisation that preserves the picture.
* **Provenance:** installed exe **`34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f`**
  (23 743 488 B); `gates_base.txt` **1 092 B / 99 names / `00c116dc…0594d8`**; commits `a3558a2` →
  `b129fbb` → final **`3ac7ccdc101ef54b9d9a96234514ac783af7cccb`**, no push, branch `merge-upstream`.
  CPU/GC observers default off, GC policy unchanged, nothing shipped. After the checks only stale
  `Session100 → 99` comments were edited; the executable code was not rebuilt, and rebuilding for a
  comment or a build label is still forbidden. `eng99a1/a2/a3` ran on `2a6bb538…`, not on the installed
  binary — only `eng99a4` onwards used it.
* **Built in session 99 — do not build it again.** Two default-off **environment variables** (read once
  a process, not gates, so they cannot tear); the game-context `CLAUDE.md` env list still ends at
  session 98 and must be extended this session. **`KYTY_BIND_FLOOR_CPU=1`** (`descriptors.cpp:3305`)
  samples the same `ThreadCpuNs(Gpu)` that feeds `cpu_gpu_us` around each real burn slice:
  `bf_burn_cpu_ns` (the endpoint's subtrahend), `bf_burn_cpu_n`, `bf_burn_cpu_bad` (must be 0),
  `bf_burn_probe_ns` (wall bounds around the two queries — the ≈1.7 ms indicator of §1, and it bounds
  **the queries only**); log line `BindFloorCpu: mode1`. **`KYTY_BIND_FLOOR_GC_AUDIT=1`**
  (`textureCache.cpp:3266`), per GC call, collection policy unchanged: `bf_igc_checks`, `bf_igc_hold`,
  `bf_igc_bad`, `bf_igc_critical`, `bf_igc_evict`; log line `BindFloorGcAudit: mode1`. Plus the three
  armed-mode-2 live witnesses `bf_live_ahead` / `bf_live_mat` / `bf_live_memo`. Twelve counters,
  all printed including zeros (`frameStats.h:1613-1646`).

## 1. First: write and seal the rule of the wide M3 — before any new number

**Order of work: §5's port comes first.** The scorer dry-run below and every path in §2 live under
`C:/kyty/s100`, which does not exist until the port has run, and the carried scorers hard-refuse any
root but their own.

**Ask the user at the start, then keep working while the answer comes: (a) may the emulator be
launched at all this session** — session 99 began under an explicit ban until a further signal
(`pred/01` §0) and that permission does not carry over; **(b) which constant the wide rule uses;
(c) whether any §3 side item is taken.** Everything in §1 and all of §5 can be prepared without an
answer; nothing in §2 may start without (a). Still owed beyond (a)–(c): `PrefetchComputePipelines`
(§3), the DRS-clock question (§3), and how session 100 satisfies ROADMAP §6 (§6).

The rule being widened is the sealed one, quoted rather than paraphrased (`ROADMAP.md:1081-1082`):

> **Правило: пол + 1,66 мс (образы) + 0,49 мс (записываемые слоты) + 0,5 мс (синхронизация) ≥ 15,5 мс
> ⇒ G и R1 закрыты; ≤ 11 мс ⇒ G идёт дальше.**

Its synchronisation term is the user's session-98 choice (`ROADMAP.md:1325-1327`). **A change to that
rule, to its branches or to its constant goes into `ROADMAP.md` first, with the user's decision
recorded, before it is acted on.**

The arm is finished; what is missing is a rule that can say anything **global**. In a new sealed
pre-registration, before a single number exists, state which of these the session takes:

1. an explicit, defensible **finite bound P** per instrument (how it is *measured*, not asserted),
   which makes `min(B_i − P_i) ≥ 15.5` usable; or
2. an **operation-level accounting** that restores the missing real work — the seal's own wording:
   *"restoring missing real work needs a new operation-level accounting"*; or
3. a rule that **honestly leaves the global GAP** if neither can be proved, and names what follows
   instead of inventing a fourth screen. (**M4**, `ROADMAP.md:1166-1169`: mark the mutations inside the
   six `MutScope` sites, `mh_rt`, `mh_prog`, `mh_disp` as semantic or bookkeeping and count the 32/64-draw
   chunks — *rule: semantic time > 8 ms or > 20 % of chunks need sequence ⇒ **P** closed* — and P was
   already closed by M1 in session 95; the user was asked exactly this in session 97 and kept the
   order. **M5**, `ROADMAP.md:1170-1171`: `KYTY_RECOMPILE` + `rd_cs_time.py`, a bench with **no game
   run** — *rule: > +6 % at the GPU's top positions ⇒ **G** closed* — which `ROADMAP.md:1334` forbids
   taking before M3 and M4 close. Leaving M3 at GAP and starting M4 is a **user** decision.)

The seal must carry: the quantity and the inequality; the population and the instrument(s); the
controls, limits and trim; and a **G/R1 outcome table** for every branch (precedent: session 96 §3 and
`pred/01` §4). **Decide which constant the wide rule uses** — 2.2535 (sealed, full floor) or 0 (the
explicitly optimistic CPU screen of `pred/01` §4). **2.65 is superseded, not a live option**: the user
decided the submission granularity at the start of session 98 and 2.2535 replaced it; it may still be
printed beside a number for continuity, but reinstating it is a new user decision written into
`ROADMAP.md` first. The three may not be merged silently.

**Dry-run the new scorer on the existing logs and fixtures before sealing** (session-97 trap: a sealed
control can be unsatisfiable for the instrument it scores). No existing scorer fits as is: `bf99.py` is
sealed to `pred/01` and pins `BINARY_SHA = ee9cc8ab…`, a binary no longer installed;
`settled99_norec.py` is sealed to `pred/05` and additionally hard-codes
`KYTY_SETTLED_SOURCE_TAG == 'eng99a4'` with a literal `CARRY_ARTIFACT_SHA`, so it is pinned to session
99's a-chain **by name**, not merely by seal.

**Second decision in the same seal: observation against the guest frame.** The CPU-probe indicator of
**≈1.7 ms per retained armed block row** (`bf99g` 1.73714, `bf99h` 1.78290) bounds **the two queries
only** — query tails, `NowNs`/`Add`/branch work stay inside `cpu_gpu_us`, and the five GC-audit counter
updates are observable overhead. It is **not** the instrument's total cost and may **not** be silently
deducted. The two queries and the cross-counter snapshot are **not atomic against the guest frame**.
Decide either the **synchronous guest Flip/Done identity observer** already sealed as the escalation in
`pred/05` (that branch was never entered, because work PASSED and `aa99plain` gave AA_PASS), or a
proved bound on the possible offset. **Name the denominator explicitly: neither GC calls
(`bf_igc_checks`) nor `fbp_n` may become one.** Do not choose a new settled interval or washout from
data already seen. The inter-binary difference `B − F` is a descriptive contrast across binaries and
clear modes only — it is not a materialisation timer and selects no branch.

**Decide before the seal, not after:** whether a binary change is needed (an L3 shortcut counter, the
guest-flip observer, new counters). If yes — `check_gate_order.py` is mandatory after any gate patch
and **before** the build, and it must be decided whether the new name enters `gates_base.txt` (pinned
byte-exact) or stays absent and lives only in schedule arms.

## 2. Then the run(s)

Only after the rule is sealed, the scorer dry-run is done, the correct binary is installed and
`nvidia-smi` is clean. Known-good shape, copied from `settled_runs/bf99g_launch.json` — the
placeholders are bare tokens on purpose, because a token-initial `<` is a PowerShell parse error:

```powershell
python -u C:/kyty/s100/enter_scene.py TAG --hold 900 --attempts 1 --no-install `
  --gates-file C:/kyty/s100/gates_base.txt --pred C:/kyty/s100/pred/NN_wide_rule.md `
  "KYTY_GATE_SCHEDULE=90+1800:BASEARM|ARMEDARM" KYTY_GATE_SCHEDULE_ABBA=1 `
  KYTY_GPU_CLOCK_PIN=1 KYTY_BIND_FLOOR_LATCH=1 KYTY_BIND_FLOOR_CLEAR=0 `
  KYTY_GPU_MARKERS=0 KYTY_GPU_CHECKPOINTS=0 KYTY_BIND_FLOOR_CPU=1 KYTY_BIND_FLOOR_GC_AUDIT=1 `
  KYTY_SETTLED_SOURCE_TAG=LOCKTAG KYTY_SETTLED_SOURCE_SHA256=SHA `
  KYTY_SETTLED_AA_TAG=AATAG KYTY_SETTLED_AA_SHA256=SHA
```

* Session-99 arms, for reference only: a = `bindfloor=0 drawahead=1 bfmode=2 bfburn=17800` |
  `bindfloor=1 drawahead=1 bfmode=2 bfburn=17800`; c = the same with `bfburn=10200` and
  `drawahead=0` **in the armed arm only**. `bindfloor`/`bfmode`/`bfburn` are **not** in
  `gates_base.txt` — they exist only inside the schedule arms.
* **Sequence:** pilot `--hold 300` (≈300.1 s measured; ≥ 8 falls, ≥ 10 pairs) → TUNE/LOCK (**≤ 3
  engineering settings per instrument**) → a **fresh** `--hold 900` confirmation per instrument
  (≈900.3 s; ≥ 30 falls, ≥ 30 pairs). `--hold` is an int — `--hold 300.1` is an argparse error. Freeze
  the rule before the launch; a calibration is a distinct pre-registered step, **never a retry**, and a
  run is never re-scored into admission.
* **Limits unchanged:** work |Δ| < 0.5 %, area < 1 %, pair matching ≥ 90 %, C5 ≤ 0.02, C9 ≤ 3 %, CPU
  rounding allowance 1 000 ns per retained armed row. Not a single threshold may be widened.
* **If the entry hangs it is an ENTRY failure, not a floor hang** — recorded separately, and it still
  stops the sequence (`pred/01` §2). `pred/02` §5 allows at most **two further isolated entry attempts
  under the distinct tags `TAG_entry1` / `TAG_entry2`** — same fixed protocol, budget and source, **no
  cache-policy change to obtain success**; repeated or floor-phase hangs need a diagnosed and fixed
  cause before any further run, and two emulator processes may never run at once. Entries hang
  historically at 6.67 % (§3), and the first entry after a new build hangs by itself — count it as
  warm-up.
* **Acceptance:** `accept99.sh` covers only `bf99.py` and **the settled family has no acceptance
  script**, so `accept100.sh` has to be written by hand. The port rewrites `.py` only and copies `.sh`
  byte-exact, so an `accept99.sh` will arrive in `s100` still carrying `R=C:/kyty/s99` inside it — **do
  not run it**. Its shape is the five steps: `guards.py TAG --first-frame 2100` (reported; check 6 is
  not a criterion) · `area_series.py` + `area_verdict.py` (criterion 3) · `summary4.py --blocks` +
  `endpoint84.py` (reported only) · the session's own new scorer · the counter identities it carries.
* **Recount the endpoint with a fresh independent script** in the shape of `parent_recount99.py` (it
  re-reads the raw log, rebuilds the 90-frame blocks from 1801, applies idx60..88 over complete
  quartets and subtracts `bf_burn_cpu_ns`; see `settled_runs/bf99g_parent_recount.json`).
  `endpoint84.py` and `shift91.py` are **reported-only** component readouts — `endpoint84`'s
  `cpu_net_us` is `cpu_gpu_us − spin_gpu_us` with no burn term and a different population — and
  `summary4.py`'s `cpu_net_us` **is** `cpu_gpu_us` under lite.
* `KYTY_REC` must be **absent entirely** on CPU runs: the scorer refuses the run if the key is present
  at any value, and `KYTY_REC=0` really does record — into a file named `0`; only an empty value is
  treated as off by the emulator. (`pred/05` §2's "empty or 0 is not a valid way to disable it" is a
  protocol rule, not a statement about the code.) Recording also displaced the asynchronous observation
  boundary in `bf99e`. If anything can reach the renderer, run a separate video pass of ≥ 3 000 frames
  (`--video`, `C:/kyty/scripts/s51_vidglitch.py`).
* One executor owns the launch, the GPU, the log and the caches; **nothing else may run on the machine
  during a hold** (in session 98 review agents' dry runs really did fail guards check 6 of `rv98a`).

## 3. Side items, not route E (ask the user whether to take any)

* **The ENTRY hang: a BVH traversal, `cs=0x380bb9d636390bae`** — 13 compute programs traverse with no
  step bound, the game's invalid-TLAS `S_TRAP` is translated as a no-op; historically **6.67 %** of
  entries. The design is ready and nothing is built: `C:/kyty/s98/design98/loops.md` —
  `KYTY_BVH_LOOP_CAP` (default 0, plan 65536), in the translation-cache signature with a separate cache
  directory, trip counters in the fault-buffer tail. **A correctness bug for every user of the
  emulator, not route E.** Cost: one cold retranslation per cap value; one extra live u32 touches the
  3.8 ms lighting CS **5323** — check registers/SASS offline first; the trip readback lags 1–3 flips;
  too low a cap cuts legitimate traversals in the BASE arm. `KYTY_LOOP_LIMIT` is **not** a substitute
  (122 shaders / 478 loops, pollutes the cache, no trip counter).
* **OIT resolve `cs=0x657ad04626bf9d55`** and the hash probes `81f39ef2…` / `e4c97c75…` — the same
  uncapped shape; the floor-edge hang itself was closed in practice by the frame latch.
* **An L3 counter** of the compute-clear shortcuts **actually taken** in the base arm would tighten the
  crude ≤ 1.58 ms bound. Needs a new binary, so it cannot serve the session-98 numbers retroactively.
* **The cross-queue ACB tear:** at every edge one ACB submission (`queue=39`, 14 operations,
  `seq = s_flip + 1`) still executes under the old value (`bf_xover_acb` 866 against 865 arm changes);
  it hung nothing in 857 falls. The fix needs the flip-bearing DCB known at ENQUEUE (a PM4 scan).
  Only `bindfloor` is op-latched — any other gate read twice inside one operation can tear, and none
  has been audited.
* **`PrefetchComputePipelines`: 1 961.1 µs a flip over 8 calls = 245 µs a call, 42.44 % of the time
  outside the mutex, 6.2 % of the 31.6 ms frame**, never measured before session 96 and still attacked
  by nobody; and 1 921.6 µs (41.59 %) outside the mutex is attributed to nobody at all. Outside the
  sealed M1–M5 order ⇒ a user decision.
* **The DRS clock debt** (ROADMAP §7): the floor/multiplier of the guest-visible `data_sel=3` clock is
  still "days of work", while `ROADMAP.md:1094` demands route E settle the DRS clocks **before**
  measuring anything. `KYTY_GPU_CLOCK_PIN=1` did **not** settle it in `bf99g`/`bf99h` — the session-91
  pin at pacer speed 1.0 supplies no floor or multiplier at all (`ROADMAP.md:1176-1177`); all those runs
  show is that the DRS step stayed **matched between the arms** (C9 0.369 % / 0.517 % against the 3 %
  limit, area split +0.001 % / −0.001 %). Decide explicitly whether the pin alone still suffices.

## 4. Traps of session 99 that turned out to be real

1. **The GC age clock advances per GC call**, not per guest or presentation frame; a recycle pool
   changes reuse, not the Insert count. A GC-call count must never become a frame denominator (it
   tracked work to −0.7156 % vs −0.7106 % in `bf99e` — a coincidence of ratio, not a unit).
2. **The MP4 is encoded at 60 fps while the `.idx` maps real elapsed time** (`vis99base` 296.7 s of
   playback ↔ 917.981 s indexed). Compare raw/index clocks, never playback minutes. A sleeping or prone
   Astro is ordinary idle animation, not a defect.
3. **Recording displaces the asynchronous observation boundary**: `bf99e` had 52 retained BASE rows with
   `draws < 10` against 0 in its no-record pilot, yet `rec_n`, `cpu_record_us` and `rec_work_us` all sum
   to **0 even there** — so those counters cannot measure the cost of recording and **causation is not
   proved**. An ordinary `RecordThread` is a normal backend thread and is allowed.
4. **Two CPU queries plus a cross-counter snapshot are not an atomic per-guest-frame observer**, and the
   ≈1.7 ms indicator bounds the queries only (see §1).
5. **`eng99a1/a2/a3` ran on `2a6bb538…`, not on the installed `34206e3f…`** — never say the a-chain
   TUNE happened on the installed exe.
6. The final 8 presents of `vis99base` (17795..17802) have **no** `FrameTrace` row.
7. `cal99a`'s arm-age transient is **exploratory only and licenses nothing**: ages 0..1 −13.9699 %,
   2..5 **−40.9097 %**, 6..14 −5.8370 %, 15..29 +0.1755 %, 30..59 +0.1841 %; even 6..59 is still
   −0.874619 %, and T\* removes 87 of 1 714 rows (5.076 %) **without** removing the discrepancy. It does
   **not** license picking age ≥ 15 after seeing these data.
8. One of the 12 CPU groups in `cal99a`'s guards sat −11.3 % from its arm median (4.257 vs 4.799 cores)
   and was never explained; no foreign process was identified.
9. Carried and still real: after a GPU hang the GPU keeps executing **~60 s to the TDR** whatever
   `KYTY_GPU_HANG_ABORT_S` says, the desktop freezes and the dead process holds `_kyty.txt`
   (`enter_scene.py` waits up to 180 s); **`KYTY_GPU_MARKERS=2` is the first tool for any hang**, not
   `KYTY_GPU_CHECKPOINTS=1` (which changes the run and itself hung the entry in `hg97a`); the frame
   latch moves the edge into idx0 of the new block, which is what the darkness and leakage structure
   **T\* = {last row of the old block, idx0, idx1 of the new}** is defined on; the floor snapshot is
   the **FIRST** materialisation of the process; the counter row of the flip a process dies in is never
   written.
10. Carried harness rules: **all `KYTY_*` go POSITIONALLY to `enter_scene.py`** (exported ones are
    dropped; only `KYTY_GATE_SCHEDULE` survives from the shell, and positional pairs win), use
    `--attempts 1` (the default is 3); `gen_gates.py` only with `--check` — a bare run, or `--out`
    **without** `--with`, overwrites `gates_base.txt`, while `--with` **without** `--out` writes
    nothing at all and says so on stderr (the session-70 trap the script was fixed to refuse loudly),
    and `--with --out <path>` writes only that path; **never rebuild between acceptance and the final
    answer** (guards check 10 hashes the exe installed *now*); inter-run comparisons of `cpu/draw`,
    `cpu_gpu_us` and FPS are **not measurements**, and the vblank plateau quantises `dt_us` to
    1/2/3 × 16 666.7 µs, so **16.7…33.3 ms all read 30.0 FPS** and anything past 33.3 ms reads 20.0.
11. Never call `finalize99.py` / `finalize_cal99a.py`. `docs/session-99/` is a **partial** archive; the
    working copy is `C:/kyty/s99`, and nothing in that archive authorises a game run.

## 5. The port — do this first

* **Write `s100_port.py` fresh in the SOURCE folder `C:/kyty/s99/`** (`SRC = C:/kyty/s99`,
  `DST = C:/kyty/s100`), modelled on `C:/kyty/s98/s99_port.py` — five root constructs, the ledger, the
  diagnostics. **Never run a carried `*_port.py`:** every `s8x/s9x_port.py` inside `C:/kyty/s99` was
  rewritten by its own port to `SRC == DST`, i.e. a self-copy no-op naming the wrong sessions
  (`C:/kyty/s99/s99_port.py` is exactly that).
* Preconditions asserted before a single byte is written: `DST` absent, `SRC/prev99` absent, all repair
  anchors preflighted. `gates_base.txt` **byte-identical (1 092 B / 99 names / `00c116dc…0594d8`)**,
  the sha asserted before the walk, after `gen_gates.py --check` and again on the destination copy.
* **Sealed texts grow 10 → 15:** the ten of sessions 96–98 (now in `s99/prev98/pred/`) plus session 99's
  own five → `s100/prev99/pred/`, byte-exact with size and sha asserted. A fresh `s100/pred/` is created
  **empty** and asserted empty; `accept100.sh`, the new scorers and README/FACTS/PLAN are asserted
  absent from the destination root.
* Five root constructs plus repair 6 advance by one: the COMMA chain 25 → **26 roots** (`s100…s75`);
  `area_verdict.py` `range(100,70,-1)`; `shift91.py` `range(100,66,-1)`; the TUPLES construct is
  **three** files together — `s94lib.py` 9 roots (`s100…s92`), `bda93.py` 10 roots (`s100…s91`),
  `stg92.py` 11 roots (`s100…s90`); `regime94.py` 8 roots (`s100…s93`) plus the `s100` fallback; the 18
  sealed-path constants repointed to `prev99/pred/`, every `*_SHA` untouched. `ABSENT` stays the same
  **33 names** (`gates.cpp` has 132 `{"KYTY_*","name"}` entries, 132 − 99) — session 99 added
  environment variables only, no gates.
* **New repair work the old port does not cover:** `settled99.py`, `settled99_gc.py` and
  `settled99_norec.py` use `ROOT = Path('C:/kyty/s99')` with `PRED = ROOT / 'pred/NN_….md'`, and
  `bf99.py:29` writes `PRED = Path('C:/kyty/s99/pred/01_bindings_only.md')` — the `Path()` wrapper and
  the `ROOT /` form both escape the port's `const()` regex `^NAME\s*=\s*'([^']*)'`, so without new code
  they silently point at the empty `C:/kyty/s100/pred/`, and merely adding them to REPOINT raises
  `('missing string constant', 'PRED')`. By contrast `rv98.py`'s `sys.path.insert(0, 'C:/kyty/s99')`
  and its `PRED*` literals are ordinary string constants already handled by `naive()` + repair 6 —
  nothing new is needed there, and an explicit anchor would trip `assert out.count(before) == 1`.
* Decide the `SKIP_DIR` additions on what is actually **carried** after the per-file ≥ 5 MiB skip:
  `fixtures` 22.59, `read91` 8.35, `video99_comparison` 7.81, `r6_raw` 5.54 (of 20.75),
  `video99_preview` 5.15, `video99_full` 3.87, `work99_raw` 2.14 (of 8.10) MiB. `verify_scorer99` is
  134.6 MiB on disk but carries only 1.00 MiB — leave it alone.
* Session-99 diagnostics to compare against: `PRECONDITIONS PASS: 5 root constructs; 10 sealed texts;
  18 live paths; gates 1092 B / 99 names` and `PORT DIAGNOSTIC: clean; carried=1399 ledger=35
  skipped=30`.
* **What must not be repeated is the completed calibration and confirmation campaign of the
  bindings-only arm** — not the port and not the scorers: a new rule needs its own scorer and its own
  offline tests.

## 6. Working procedure and the session's deliverable

PLAN with a measurable question first, then CODE → TEST → a fresh VERIFY, if code or data are really
needed. Use the permission already given inside its own scope and do not re-negotiate preparation that
is already done — but **a game launch is not covered by it** (§1). A new rule means a new
pre-registration and new tags; the old seals stay untouched. One executor owns the GPU, the log and the
caches; no background build, scorer or review during a hold; build only through `build_local.cmd`.
**ROADMAP §6 expects the session to end with a source change that passed A/B** — decide and state at
the start how session 100 satisfies it (for example the sealed rule **plus** the counter or observer
patch with its own ABBA), or renegotiate it with the user consciously instead of drifting into a
session of pure deliberation. At the end: one edit to ROADMAP, then FACTS (`C:/kyty/s100/FACTS.md`,
mirrored into git as `docs/local-session-100.md`), `docs/next-session-101.md`, and both game contexts —
**including their environment-variable list, which still stops at session 98** — and the mandatory
commit without push; do not capture the unrelated dirty `3rdparty/nlohmann_json`.

## 7. Must not be claimed

Global M3 is closed, HIGH is a CLOSE, or anything reached PROCEED-to-M5 · G or R1 is closed or licensed
(and the mirror error: that 60 FPS is proved unreachable) · the bindings-only floor is an architectural
lower bound, or `B − F` is a materialisation timer · `B_c − B_a` is the cost of the M1 workers (in mode
2 the `c` instrument is a **different acquisition implementation**, not the removal of dead workers) ·
the mode-2 floor is proved reversible or hang-free (the 857-edge proof is mode 3 / clear 1 on another
binary; 45 edges are not 857, and no mode-2 hazard rate exists) · 2.2535 or 2.65 added to B_a/B_c, or
the zero addend proving that the preserved materialisation already contains **all** the old 1.66 + 0.49
· the ≈1.7 ms probe is the instrument's full cost or may be deducted · the wall-burn endpoint decides
anything · GC calls, fault calls or playback minutes are a guest-frame denominator · recording is the
proved cause of `bf99e`'s work deficit · any correctness claim beyond non-reproduction without the
floor (not the corrupting operation, not per-pixel identity, not "**all** late frames are clean" — the
three fixed inspected frames showed no corresponding effects) · nulled bindings are a shippable
optimisation · `cal99a`, `bf99e` or `eng99a3` can be re-admitted or rescued · the M3 synchronisation
granularity is still open (decided in session 98: submission, +103.5 µs ⇒ 2.2535; `ROADMAP.md:1409`
still lists it as open and is stale) · M4/M5 may be advanced to evade M3, or the M3 → M4 → M5 order is
the agent's to revisit. **And no frame-rate gain, no speedup, no 60 FPS.**
