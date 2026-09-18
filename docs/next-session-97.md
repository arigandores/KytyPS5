# Session 97 — route E, measurement M3 (continued)

**Route E's order is fixed: M1 → M2 → M3 → M4 → M5 (`docs/ROADMAP.md` §5 item 5). Session 96 did
NOT finish M3: it split both decompositions the rule names, it measured the dynamic-resolution
trap, and it found the ceiling stub cannot be an ABBA arm. `F_st` does not exist. Session 97 is
M3 again.**

Read `C:/kyty/s96/FACTS.md` **in full** first — the only source of truth for session 96 — then
`ROADMAP.md` §0.1 and §2 E, `C:/kyty/s96/README.md`, and the five sealed pre-registrations in
`C:/kyty/s96/pred/`.

**Open the report with these three numbers, every session of route E** (`ROADMAP.md:1210-1212`,
`FACTS.md` §0):

* the budget: **≤ ~3.0 µs a draw** on a median frame, **≤ ~2.3 µs** on a p99 frame (7 284 draws);
* where the path stands: **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms** (pinned p50 12.83 /
  p90 13.94 / p99 15.77);
* which of M1–M5 is still undone: **M3, M4, M5**.

**Do not promise 60 FPS.** ~15 % (8–25 %); session 96 neither raised nor lowered it (`FACTS.md` §0).

## 0. The board

| route | estimate | state |
|---|---|---|
| **P** — parallel translation | 12–25 % | CLOSED by M1 (s95) |
| **P+G** | 15–30 % | CLOSED with P |
| **F** — frame replay | 3–8 % | CLOSED by M2 (s95) |
| **G** — GPU-driven hybrid V2 | 5–12 % | **alive — not closed, not licensed; waits on M3 and M5** |
| **R1** — single-thread cleanup | ≤ 3 % | **alive** — closes with G at M3's upper branch |

**M3 is NOT closed. No admitted run produced `F_st`. The sealed rule of `ROADMAP.md:1052-1053`
was applied to no number, and no verdict on G or R1 follows from session 96** (`FACTS.md` §0.1,
§7). Do not soften this.

The rule, quoted, not paraphrased (`ROADMAP.md:1052-1053`):

> **Правило: пол + 1,66 мс (образы) + 0,49 мс (записываемые слоты) + 0,5 мс (синхронизация)
> ≥ 15,5 мс ⇒ G и R1 закрыты; ≤ 11 мс ⇒ G идёт дальше.**

Its three branches were sealed before any number (`pred/02_bindfloor.md` §2–§3):
`VERDICT_INPUT = F_st + 2.65` ms; ≥ 15.5 ⇒ G and R1 CLOSED; ≤ 11.0 ⇒ G proceeds to M5 (**a
proceed is not a licence**, `pred/02` §1); in between ⇒ nothing closes, a bindings-only arm
(`bfmode=2`) is scheduled and **M3 continues in session 97**. That sentence now describes this
session.

## 1. Blocker one — the stub is not reversible, and ABBA is required

`bindfloor` as built **cannot be an ABBA arm** (`FACTS.md` §4); `ROADMAP.md:1048` requires ABBA.
Not an argument — in `bf96b` the log ends at

    GateArm: arm=0 block=3 frame=1890  bindfloor=0 bfmode=3 bfburn=16400   <- last line of the log

1 889 flips, nothing after. The stub reuses the last materialisation of every program
(`bf_mat` 0, `bf_reuse` 10 168) and **restores nothing when the gate goes off**. **Until this is
solved `F_st` cannot be measured at all.**

Session 97 must choose, before writing code, between:

1. **making the floor reversible** — on the gate's falling edge drop every reused snapshot and
   every cached null descriptor set, so the base arm re-enters the shipped path clean; or
2. **giving M3 a different shape** — one that yields the floor without a state the base arm
   cannot return from.

The reversal has to be *proved*, not assumed: a textually identical A/A schedule on the same gate,
surviving several returns to the base arm, is the cheapest proof and the harness already supports
it (`KYTY_GATE_SCHEDULE_ABBA=1`).

## 2. Blocker two — the DRS trap is measured, and the burn is a working but calibrated answer

The trap of `ROADMAP.md:1062-1065` **fired and was measured** (`FACTS.md` §3; prediction P10 of
`pred/02` HIT): a path made twice as fast pushed the game from **2 002 Kpx to 8 037 Kpx —
4.014×, native 4K — within 30 frames**, and a linear colour target of **62.8 MiB against the
32 MiB Download ring** (`bufferCache.cpp:377`) killed the process at `textureCache.cpp:2842`.
`StreamBuffer::Map` returns null only on `mapped_size > Size()` (`streamBuffer.h:121`), so it
failed by size, not by pressure.

**The burn held it** (`FACTS.md` §4): with `bfmode=3 bfburn=16400` the floor arm's `dt_us` was
33 126 / 33 502 against the base arm's ~33 000, `bf_burn_ns` 17.53 ms a frame, `bf_dlskip` **0**,
`draws` 5 275–5 424 against the base 5 436, no crash. `pred/02` §8 says how it leaves the readout:
`F_st = (cpu_net_us − bf_burn_ns/1000) / flip`, with C9 (frame `dt` within 3 % between arms) and
C10 (`bf_burn_ns` > 0 armed, = 0 unarmed).

**But `bfburn` is calibrated against one specific gap in pace.** A floor cheaper or dearer than
the one it was fitted to will not hold the DRS step; the calibration must be re-derived for every
new floor shape, in its own arm, before the floor is read. Say so — the burn is not a solved
problem.

## 3. Already built in session 96 — do not build it again

* **Gate `pathlap`** (`KYTY_PATH_LAP`, default 0, measurement only; **requires `mutsite=1` in the
  same arm**) and its ADMITTED run `pl96a` — criterion 3 VALID, controls 7/7, 10 HIT / 2 MISS,
  instrument price +362.9 ± 80.8 µs, t = +8.98 (`FACTS.md` §2). **Both decompositions M3 names
  are split, for the first time in ~96 sessions:**
  * `mh_emit` beyond `CommitBindings` = **4 893.3 µs a flip**; EMIT 7 138.5; the chain closes at
    `EMIT / mh_emit_us` = 0.9860 (`FACTS.md` §2.1);
  * outside the render mutex = **4 620.7 µs a flip**, of which **`PrefetchComputePipelines`
    1 961.1 µs over 8 calls = 245 µs a call (42.44 %)** and **RESIDUE 1 921.6 µs (41.59 %),
    attributed by no session** (`FACTS.md` §2.2);
  * two informative misses (`FACTS.md` §2.3): the EOP labels are **cheap** — `pl_eop_ns` 43.1 µs
    a flip, 0.117 µs per label at 369 labels; vertex/index plus render-target acquisition is
    **dearer** than predicted, 2 883.4 µs.
* **Knob `bdaevery`** (`KYTY_BDA_EVERY`) and the run `bd96a` (criterion 3 VALID, controls 4 of 6 —
  §4 below). `bd96b` (`bdaevery=1`, submission granularity) was **not run**.
* **The stub `bindfloor`** with modes 1 / 2 / 3 (`pred/02` §4) and its counters `bf_n`, `bf_skip`,
  `bf_push`, `bf_pool`, `bf_mat`, `bf_reuse`, `bf_burn_ns`, `bf_dlskip`.
* **The patch turning the download-ring `EXIT` into a counted skip** under the gate (`bf_dlskip`).
* **The harness `C:/kyty/s96`**: three scorers (`pl96.py`, `bf96.py`, `bd96.py`, each verifying
  its own sealed sha256), `check_s96_counters.py` (identities I1..I9, I1 repaired under
  `pred/04`), `check_gate_order.py`, and `accept96.sh` in six steps — guards → area → summary4 →
  endpoint84 → the session's own scorer → counter identities.

**Binaries** (`FACTS.md` §1): `pl96a` and `bd96a` were accepted against `65fca20dd4bc8528…`;
`bf96b` ran on `993be4a85af569c4…`, built after them for the download-ring repair. Their
acceptances cannot be re-run against the binary installed now, and that is stated, not hidden.

## 4. The cheapest open item — re-score `bd96a` under `pred/05`, no game run

`bd96a` is VALID on criterion 3 (split −0.002 %, pairs 119/119, work −0.168 %) and its readout is
**SUPPRESSED**: sealed controls C3 and C5 failed, both by construction (`FACTS.md` §5). C3 judges
"same BDA regime" by `bda_scan`, which this knob itself multiplies (armed median 223, unarmed 50,
ratio 4.46); C5 compares `be_ns` — WALL time, including the render-mutex wait *by design* — with
a CPU-time endpoint (4 853.4 against 2 986.8).

`pred/05_bdaevery_controls.md` exists and is sealed (9 087 B, sha256 `352448ac…`, pinned at
`bd96.py:50-51`). **It has not been scored; until it is, `bd96a`'s endpoint is not a result of
session 96 and is not to be quoted** (`FACTS.md` §5). Scoring it is step 5 of `accept96.sh` on
tag `bd96a` and launches nothing.

## 5. The eight traps of session 96 that turned out to be real (`FACTS.md` §6)

1. **Gate table order is not checked by the compiler** — `KYTY_PATH_LAP` landed before
   `KYTY_FRAME_REP` while the enum had `PathLap` after `FrameRep`, silently swapping two gates
   → `python C:/kyty/s96/check_gate_order.py` must print "GATE ORDER: clean" before every build
   that touched a gate.
2. **A hook on the PM4 parse path is not under the render mutex** — `BdaEveryHook` called
   `PrepareBda()` without it while it mutates the buffer cache (`renderContext.cpp:302-304`,
   `:343`, `:356-358`) → take the lock, check re-entrancy rather than assume it.
3. **Nested spans double-count** — `pl_sub` charged ~0.6 ms of 4.05 ms twice because
   `BufferFlushLazy` calls `BufferFlush` → depth guard; found by review, not by a run.
4. **A lap can cover one call site of five** — `pl_gc` did → count the sites in the source before
   sealing a span.
5. **A span taken on another thread must never be summed** — `pl_look` was;
   `LookaheadSubmission` runs on the guest submit thread (`graphicsRun.cpp:630`), outside
   `GuestGpu::Process` → report it, never add it.
6. **A sealed identity can be unsatisfiable** — `pred/01` §5 C1 admits a block-boundary leak while
   §8 I1 demanded an exact zero of the same counters; repaired under `pred/04`, and the leak is
   **FIRST 64 / LAST 62 / MID 0**, not "last frame" → prove a new identity with a fixture that
   passes the old control and fails only the new one.
7. **A sealed control can name a quantity the instrument itself moves** — C3 and C5 of `pred/03`
   (§4) → when sealing a control, ask which side of it the knob touches.
8. **`KYTY_REC` and every other `KYTY_*` must be passed POSITIONALLY to `enter_scene.py`** — an
   export from the shell is dropped **silently** (only `KYTY_GATE_SCHEDULE` gets through), so
   `bf96a` recorded no video; the trap was written into session 96's own README and then stepped
   in.

Carried unchanged: a run that fails admission is **REPLACED**, never argued with, its contrast
quoted nowhere; a failed **control** is REPAIRED under a **NEW** sealed pre-registration; never
decide an arm fired from `counter > 0` — only from the text of `GateArm:`; a band on a counter
that read 0 prints NOT EVALUABLE, never HIT; `summary4.py`'s `cpu_net_us` IS `cpu_gpu_us` under
lite, `endpoint84.py` is the endpoint, one endpoint one t value; `guards.py` check 6 is **not** a
criterion and check 10 hashes the exe installed at that moment; patches go into a file via Write,
never a heredoc.

## 6. The port — s96 → s97

Write **`C:/kyty/s96/s97_port.py` fresh in the SOURCE directory**, modelled on
`C:/kyty/s95/s96_port.py`, which carries **five root constructs as five separate edits** and
asserts each:

1. the head of every comma-spelled `--roots` default — `arms.py:29`, `baseline.py:83`,
   `effect.py:103` (spelled `--extra-roots`): the naive rewrite drops the previous root, so the
   new root goes in FRONT and **s96 stays**; asserted against the whole expected chain;
2. `area_verdict.py:56` `range(96, 70, -1)` → `range(97, 70, -1)` — the floor 70 does **not** move;
3. `shift91.py:35` `range(96, 66, -1)` → `range(97, 66, -1)` — the floor 66 does **not** move;
4. the tuple-spelled chains of `stg92.py:44`, `bda93.py:41` and `s94lib.py:21`, repaired **BY FILE
   NAME**: a blind replace also reaches `regime94.py:9` and **swallows repair 5**, and it reaches
   the degenerate chains (`area71_extract.py:14`, `area.py:227` and ten more) that must not move;
5. `regime94.py:9` — the chain that locates its root by looking for the log itself, extended by
   one root with the fallback moved to the new harness; `import os` is **asserted, not added**.

**The LEDGER.** On `regime94.py` repairs 4 and 5 produce **byte-identical text**, so no textual
check afterwards can say which fired. The port therefore records which repair actually CHANGED
which file and asserts **repair 4 fired on exactly the three tuple files** and **repair 5 on
exactly `regime94.py`** (checks f2a/f2b; f2c proves no repair reached the twelve degenerate
chains). It also proves the collision is still real — the *naive* rewrite of `regime94.py` does
contain the broken tuple — and asserts the population of files that do.

**Diagnostic (i), fixed in s96 and to be kept fixed.** The s95 port looked for `/s95/` **with a
trailing slash**, which no root literal ever has (`C:/kyty/s95`), so it always printed a
reassuring zero. With the slash dropped the real answer is 20 files / 63 lines, of which 7 are the
live repaired chains; it now separates LIVE from port-archive files and asserts the LIVE set is
exactly the repaired chains.

Then, as every port since s83: **`gates_base.txt` byte-identical** (1 092 B, 99 names, sha256
`00c116dc…0594d8`, unchanged since s94 and verified again in s96); `gen_gates.py` in **`--check`
mode only** (it says "out of date" BY CONSTRUCTION, and `--out` without `--with` overwrites the
file); `.txt`/`.json`/`.md`/`.csv`/`.sh` byte-exact; `log_*`, `stdout_*`, `*.map` and anything
≥ 5 MB not copied — the root chains find them in s96 and earlier; the session documents and **all
five sealed `pred/*.md`** carried into `prev96/` byte-exact with sizes and sha256 asserted, the
fresh `pred/` left EMPTY; `pathlap`, `bindfloor`, `bfmode`, `bfburn`, `bdaevery` (all absent from
`gates_base.txt` today) added to the must-be-absent list, because names the schedule assigns
belong to the schedule.

**`accept97.sh` is WRITTEN NEW** — the port rewrites `.py` only, so `accept89.sh … accept96.sh`
arrive as byte copies still pointing at their own harness. **Every carried `s8x/s9x_port.py` is a
self-copy with `SRC == DST` — never run one, never copy its constants.**

## 7. Do NOT

* **Do not start writing the rewrite.** M3 is unfinished; M4 and M5 have not begun.
* **Do not re-interpret a sealed rule after seeing a number.** A change to the M3 rule or its
  branches goes into `ROADMAP.md` first, with the user's decision recorded. Same for reopening
  P or F.
* **Do not quote `F_st` or any contrast from `bf96a` or `bf96b`** — both REPLACED; `bf96a`'s arms
  drew **1× and 4.014×** the area, `bf96b` never returned to its base arm (`FACTS.md` §3, §4).
* **Do not quote `bd96a`'s endpoint** until `pred/05` is scored (§4).
* **Do not quote a `PrepareBda` number without its BDA regime** (`regime94.py`; OLD ≈ 1 060 scans
  a frame, NEW ≈ 50); do not give two t values for one endpoint.
* **A foreign game on the GPU is a hard stop** — check `nvidia-smi` BEFORE launching.
* **Do not rebuild between acceptance and the final answer** (guards check 10).
* **The video pass is a debt** (`--video`, `s20_vidglitch.py`, ≥ 3 000 frames): `bindfloor`
  reaches the renderer by design, `bf96a`'s recorder was off by trap 8, and the pass was never
  taken (`FACTS.md` §7). The picture is allowed to break — the video is evidence of WHAT broke,
  not a correctness check — and it is owed before any of this enters a rewrite.

## 8. Not closed — the full list (`FACTS.md` §7)

* **`F_st`, and therefore M3, and therefore G and R1.**
* The stub's reversibility — the blocker for M3.
* The DRS clock: `ROADMAP.md:1062-1065` now has a measurement behind it and must be solved before
  any faster path can be measured at all.
* `bd96a`'s endpoint, pending `pred/05`; `bd96b` not run; the video pass for `bindfloor`.
* New and never attacked: **`PrefetchComputePipelines`, 245 µs a call, 6.2 % of the frame**
  (`FACTS.md` §2.4) — nothing in session 96 tested whether it can be reduced — and beside it the
  **1 921.6 µs a flip of residue outside the mutex that no session has attributed**
  (`FACTS.md` §2.2).
* Carried from session 95: **M4, M5**; the BDA regime; the written `bc_ok` slots; `C_bda` in NEW;
  the GPU side of `bdaall`; the single-chunk notify; the `ObtainBuffer` ring timer;
  `pfhint`/`pfcap`/`dapin` with the pin; route B.

**The session rule stands (`ROADMAP.md` §6): a session ends with a source change that passed A/B,
or it failed. A counter is a change, and its ABBA is its A/B.**
