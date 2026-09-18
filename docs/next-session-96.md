# Session 96 — route E, measurement M3

**Route E's order is fixed: M1 → M2 → M3 → M4 → M5 (`docs/ROADMAP.md` §5 item 5). Session 95
did M1 and M2, and each closed a route. Session 96 does M3 — the ceiling stub `bindfloor` —
and it is the first measurement of this route that can close TWO candidates at once.**

Read `docs/ROADMAP.md` §0.1 and **§2 E** first (budgets, the five measurements with their
sealed rules, the traps), then `C:/kyty/s95/FACTS.md`, `M1_RESULT.md` and the two sealed
pre-registrations in `C:/kyty/s95/pred/`.

**Open the report with these three numbers, every session of route E:**

* the budget: **≤ ~3.0 µs a draw** on a median frame, **≤ ~2.3 µs** on a p99 frame (7 284 draws);
* where the path stands: **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms** (p50 12.83,
  p90 13.94, p99 15.77 with the clock pinned);
* which of M1–M5 is still undone: **M3, M4, M5**.

**Do not promise 60 FPS.** The estimate was ~15 % (8–25 %) and session 95 did not raise it — it
removed candidates.

## 0. What session 95 settled, and what that leaves

| route | estimate before | after session 95 |
|---|---|---|
| **P** — parallel translation | 12–25 % | **CLOSED by M1** |
| **P+G** | 15–30 % | **CLOSED with P** |
| **F** — frame replay | 3–8 % | **CLOSED by M2** |
| **G** — GPU-driven hybrid V2 | 5–12 % | alive, needs M3 and M5 |
| **R1** — prior-art single-thread cleanup | ≤ 3 % | alive, closed together with G at M3's upper rule |

**M1** (no code): real, non-spin work outside the translation thread is **181 278 µs a flip =
10.88 logical CPUs at twice today's frame rate** against the rule's ~8. The unattributed CPU of
the record turned out to be **12 guest threads of the game**, each ~9 000 µs a flip, running the
game's own x86-64 code (ETW: `guest/unmapped` 69–72 % of their samples; the graphics driver is
only 1.83 % of the whole process). The second branch did NOT fire — the dearest guest thread
costs 9 003 µs a game frame against a threshold of ~12 000.

**The tension M1 left for the user.** The rule fired on its letter, but its reason — "no free
cores" — does not follow on this machine (16 cores / 32 logical): 10.88 CPUs would still leave
~17 logical processors idle at 60 FPS. The rule was applied as sealed. **If the user wants P
reopened, that is a decision about the RULE, not about the number**, and it should be taken
explicitly, in ROADMAP, before any code is written.

**M2** (gate `framerep`, ABBA, pin): coverage **C = 0.0035** against the sealed threshold 0.84.
A repair run (`fr95b`, also admitted in full, controls 7/7 and predictions 9/9) measured the
CEILING — every BDA-convertible slot masked, which is session 94's own signature:
**C_ceiling = 0.0072** against C_strict 0.0033 and C_repaired 0.0038. Masking everything that
could be canonicalised multiplies the hits by 3.23 and still lands **117× below the threshold**,
so **F is closed by the SCENE and not by the hashing.** The walk also counted what is left:
**28.41 image values and 15.32 non-ring buffer values a draw** — that is where the remaining
distinctions live, and no session has split them.

## 1. M3 — the ceiling stub `bindfloor` (1–2 sessions, ABBA, pin; THE PICTURE MAY BREAK)

**The sealed rule (`ROADMAP.md:1022-1023`), quoted, not paraphrased:**

> **Правило: пол + 1,66 мс (образы) + 0,49 мс (записываемые слоты) + 0,5 мс (синхронизация)
> ≥ 15,5 мс ⇒ G и R1 закрыты; ≤ 11 мс ⇒ G идёт дальше.**

The stub removes `AheadTake`, `MaterializeResources`, `PrepareBindings`, `Rebind*` and the
per-slot synchronisations, and binds ONE pre-built descriptor set per layout made of null
descriptors; it KEEPS the PM4 parse, the render targets, the pipeline, the emit and the record.
`F_st` is the floor it measures. Because the stub also removes the re-protect / fault cycles and
the ring copies, **`F_st` is optimistic and is therefore only good for CLOSING an option**, never
for licensing one (`judge.md` §4).

**What must be built beside it, because it has never been split:**

* the **4.05 ms outside the render mutex** — lap chains, not a guess;
* the **~5 ms of `mh_emit` beyond `CommitBindings`** (which is 2.03 ms) — the same;
* an arm with `PrepareBda` called once per submission instead of per draw, to price the
  synchronisation term of the rule rather than assume it.

**Preparation already done in session 95:** none of the cutting points were touched, but the
census sites are mapped — `MergeCostCensus` at `descriptors.cpp:3108` walks the write list in
build order and its `mc_tr/wr/em_ns` laps are at `descriptors.cpp:2933`, `:3030`, `:3059`/`:3092`;
the class point is `NoteDrawMerge` at `renderDraw.cpp:2430-2438`; the pre-class interval opens at
`renderDraw.cpp:2807-2810` (and again at `:2971` for `DrawAuto` — **two sites, not one**).

## 2. The traps that are now known to be real

* **A prediction written on `StartAddress` is void on Windows** — every thread reports
  `RtlUserThreadStart`. Session 95's M1 prediction P2 died on that and had to be answered with
  ETW instead.
* **xperf and wpa are NOT installed on this machine.** `wpr` records and `tracerpt` decodes to
  CSV (968 MB → 2.6 GB for 10 s); `C:/kyty/s95/m1_etw_parse.py` maps sampled instruction
  pointers to modules, and a sample outside every image is the GUEST's own code. That pipeline
  works and is worth reusing; symbolisation is not available.
* **Reusing another session's census inherits the reasons it masked things.** Session 94 masked
  the BDA-convertible slots for a different question; session 95 took them unmasked and put
  ring addresses back into an identity meant to be canonical. The repair measured how much that
  cost instead of arguing — do the same.
* **A scorer's dry run on the record is not a formality.** It caught two defects in `fr95.py`
  minutes before the seal: a control gated on the wrong instrument, and a band printing a
  vacuous HIT on an instrument that never fired.
* Carried: a run that fails admission is REPLACED, not discussed; a failed control is REPAIRED
  under a NEW sealed pre-registration; never decide an arm fired from `counter > 0`;
  `summary4.py`'s `cpu_net_us` IS `cpu_gpu_us` under lite; guards check 6 is not a criterion and
  check 10 hashes the exe installed at that moment — **never rebuild between acceptance and the
  final answer**; patches go into a file via Write, never through a heredoc.

## 3. The port — s95 → s96

Write `C:/kyty/s95/s96_port.py` **fresh in the SOURCE directory**, modelled on
`C:/kyty/s94/s95_port.py`, which carries FIVE root constructs and a declared deviation:

1. the heads of the comma-spelled `--roots` defaults (`arms.py:29`, `baseline.py:83`,
   `effect.py:103` — spelled `--extra-roots`): the new root goes in FRONT and `s95` stays;
2. `area_verdict.py:56` `range(95, 70, -1)` → `range(96, 70, -1)`;
3. `shift91.py:35` `range(95, 66, -1)` → `range(96, 66, -1)`;
4. the tuple-spelled chains `stg92.py:44`, `bda93.py:41` and `s94lib.py:21`, repaired BY FILE
   NAME (a blind replace reaches `area71_extract.py:14` and `area.py:227`, which are degenerate
   chains that must not move);
5. `regime94.py` — session 95 replaced its two-branch tag test with a chain that looks for the
   log itself; keep that and extend the chain with s96.

Then: `gates_base.txt` byte-identical (1092 B, 99 names, sha256 `00c116dc…0594d8`);
`gen_gates.py` in `--check` mode only (it says "out of date" BY CONSTRUCTION); **write
`accept96.sh` new**; `.txt`/`.json`/`.md`/`.csv`/`.sh` byte-exact; every carried `s8x/s9x_port.py`
is a self-copy — never run one.

## 4. Do NOT

* **Do not start writing the rewrite.** M3, M4 and M5 first.
* Do not reopen P or F by reinterpreting a sealed rule after the fact; reopen them, if at all,
  by changing the RULE in ROADMAP first, with the user's decision recorded.
* Do not quote `C` from session 95 without saying which identity carried it (strict, repaired,
  or the fully-masked ceiling).
* Do not quote a `PrepareBda` number without its regime; do not give two t values for one
  endpoint (`endpoint84.py` is the endpoint).
* A foreign game on the GPU is a hard stop — check `nvidia-smi` BEFORE launching.
* The video pass (`--video`, `s20_vidglitch.py`, ≥ 3 000 frames) is a debt after any change that
  can reach the renderer, and `bindfloor` reaches it by design.
