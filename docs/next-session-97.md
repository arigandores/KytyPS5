# Session 97 — route E, measurement M3 (continued)

**Route E's order is fixed: M1 → M2 → M3 → M4 → M5 (`ROADMAP.md` §5 item 5). Session 96 did NOT
finish M3: it split both decompositions the rule names, measured the DRS trap and the rule's
synchronisation term, and found the ceiling stub cannot be an ABBA arm. `F_st` does not exist.
Session 97 is M3 again.**

Read `C:/kyty/s96/FACTS.md` **in full** first — the only source of truth for session 96 — then
`ROADMAP.md` §0.1 and §2 E, `C:/kyty/s96/README.md`, and the five sealed pre-registrations in
`C:/kyty/s96/pred/`.

**Open the report with these three numbers, every session of route E** (`ROADMAP.md:1210-1212`,
`FACTS.md` §0):

* budget **≤ ~3.0 µs a draw** on a median frame, **≤ ~2.3 µs** on a p99 frame (7 284 draws);
* today **6.4 µs a draw, 31.6 ms a frame, GPU busy 12.8 ms** (pinned p50 12.83 / p90 13.94 /
  p99 15.77);
* of M1–M5 still undone: **M3, M4, M5**.

**Do not promise 60 FPS.** ~15 % (8–25 %); session 96 neither raised nor lowered it (`FACTS.md` §0).

## 0. The board

| route | estimate | state |
|---|---|---|
| **P** — parallel translation | 12–25 % | CLOSED by M1 (s95) |
| **P+G** | 15–30 % | CLOSED with P |
| **F** — frame replay | 3–8 % | CLOSED by M2 (s95) |
| **G** — GPU-driven hybrid V2 | 5–12 % | **alive — not closed, not licensed; waits on M3 and M5** |
| **R1** — single-thread cleanup | ≤ 3 % | **alive** — closes with G at M3's upper branch |

**M3 is NOT closed. No admitted run produced `F_st`. The sealed rule of `ROADMAP.md:1052-1053` was
applied to no number, and no verdict on G or R1 follows from session 96** (`FACTS.md` §0.1, §7).
Do not soften this. The rule, quoted, not paraphrased:

> **Правило: пол + 1,66 мс (образы) + 0,49 мс (записываемые слоты) + 0,5 мс (синхронизация)
> ≥ 15,5 мс ⇒ G и R1 закрыты; ≤ 11 мс ⇒ G идёт дальше.**

Its three branches were sealed before any number (`pred/02_bindfloor.md` §2–§3):
`VERDICT_INPUT = F_st + 2.65` ms; ≥ 15.5 ⇒ G and R1 CLOSED; ≤ 11.0 ⇒ G proceeds to M5 (**a proceed
is not a licence**, `pred/02` §1); in between ⇒ nothing closes, a bindings-only arm (`bfmode=2`) is
scheduled and **M3 continues in session 97**. That sentence now describes this session.


### 0.1 An observation about the order itself — a QUESTION for the user, not a decision

The rigid order M1 → M2 → M3 → M4 → M5 (`ROADMAP.md` §5 item 5) was fixed when all five options
were alive. M1 and M2 killed P, P+G and F. Of the three measurements left, **only M3 and M5 can
decide anything about the two survivors:**

| | its sealed rule | what it can still close |
|---|---|---|
| **M3** | `F_st + 2.65 ≥ 15.5 ms ⇒ G and R1 closed; ≤ 11 ms ⇒ G proceeds` (`ROADMAP.md:1052-1053`) | **G, R1** |
| M4 | *"смысловое время > 8 мс или > 20 % кусков требуют последовательности ⇒ **P закрыт**"* (`ROADMAP.md:1076`) | **P — and P was closed by M1 in session 95** |
| M5 | `> +6 % на топ-позициях GPU ⇒ G закрыт` (`ROADMAP.md:1078`) | **G** |

**M4's sealed rule closes an option that is already closed.** Its other product — `f`, the worker
slowdown, measured on the s64 `shadowResolve.cpp` infrastructure (`judge.md:123`) — is also a
parallelism quantity, and parallelism is what M1 closed.

**This is not a licence to skip M4.** Dropping a step from a rigid order is a change to the plan,
and by this programme's own rule that is the user's decision, recorded in `ROADMAP.md` before it is
acted on — exactly like the session-95 question of whether to reopen P (`ROADMAP.md:1024-1027`).
Session 97 should **put the question to the user and proceed in the sealed order until answered**.

M5 is a bench with **no game run** (`ROADMAP.md:1077`), so it costs no emulator time and can be
taken in any session, including alongside M3 work.

## 1. Blocker one — the stub is not reversible, and ABBA is required

`bindfloor` as built **cannot be an ABBA arm** (`FACTS.md` §4); `ROADMAP.md:1048` requires ABBA.
Not an argument — `bf96b`'s log ends at

    GateArm: arm=0 block=3 frame=1890  bindfloor=0 bfmode=3 bfburn=16400   <- last line of the log

1 889 flips, nothing after. The stub reuses the last materialisation of every program (`bf_mat` 0,
`bf_reuse` 10 168) and **restores nothing when the gate goes off**. **Until this is solved `F_st`
cannot be measured at all.** Decide before writing code between **(1) making the floor reversible**
— on the falling edge drop every reused snapshot and every cached null descriptor set, so the base
arm re-enters the shipped path clean — and **(2) giving M3 a different shape**, one that yields the
floor without a state the base arm cannot return from. The reversal must be *proved*: a textually
identical A/A schedule on the same gate, surviving several returns to the base arm, is the cheapest
proof and the harness already supports it (`KYTY_GATE_SCHEDULE_ABBA=1`).

## 2. Blocker two — the DRS trap is measured; the burn works but is calibrated

The trap of `ROADMAP.md:1062-1065` **fired and was measured** (`FACTS.md` §3; P10 of `pred/02`,
HIT): a path made twice as fast pushed the game from **2 002 Kpx to 8 037 Kpx — 4.014×, native 4K —
within 30 frames**, and a linear colour target of **62.8 MiB against the 32 MiB Download ring**
(`bufferCache.cpp:377`) killed the process at `textureCache.cpp:2842`. `StreamBuffer::Map` returns
null only on `mapped_size > Size()` (`streamBuffer.h:121`) — it failed by size, not by pressure.

**The burn held it** (`FACTS.md` §4): with `bfmode=3 bfburn=16400` the floor arm's `dt_us` was
33 126 / 33 502 against the base arm's ~33 000, `bf_burn_ns` 17.53 ms a frame, `bf_dlskip` **0**,
`draws` 5 275–5 424 against the base 5 436, no crash. `pred/02` §8 removes it from the readout —
`F_st = (cpu_net_us − bf_burn_ns/1000) / flip`, with C9 (frame `dt` within 3 % between arms) and
C10 (`bf_burn_ns` > 0 armed, = 0 unarmed). **But `bfburn` is fitted to one specific gap in pace**:
a floor cheaper or dearer will not hold the DRS step, so it must be re-calibrated for every new
floor shape, in its own arm, before the floor is read. Not a solved problem — say so.

## 3. Already built in session 96 — do not build it again

* **Gate `pathlap`** (`KYTY_PATH_LAP`, default 0, measurement only; **requires `mutsite=1` in the
  same arm**), ADMITTED run `pl96a`: criterion 3 VALID, controls 7/7, 10 HIT / 2 MISS, price
  +362.9 ± 80.8 µs, t = +8.98 (`FACTS.md` §2). **Both decompositions M3 names are split, first time
  in ~96 sessions:** `mh_emit` beyond `CommitBindings` = **4 893.3 µs a flip** (EMIT 7 138.5,
  `EMIT / mh_emit_us` = 0.9860 — the chain closes, §2.1); outside the render mutex = **4 620.7 µs a
  flip**, of which **`PrefetchComputePipelines` 245 µs a call over 8 calls (42.44 %)** and
  **RESIDUE 1 921.6 µs (41.59 %) attributed by no session** (§2.2). Two misses (§2.3): the EOP
  labels are **cheap** (43.1 µs a flip, 0.117 µs per label at 369 labels), vertex/index plus
  render-target acquisition **dearer** (2 883.4 µs).
* **Knob `bdaevery`** (`KYTY_BDA_EVERY`) and the ADMITTED run `bd96a` (§4).
* **The stub `bindfloor`**, modes 1 / 2 / 3 (`pred/02` §4), counters `bf_n`, `bf_skip`, `bf_push`,
  `bf_pool`, `bf_mat`, `bf_reuse`, `bf_burn_ns`, `bf_dlskip`; and **the patch turning the
  download-ring `EXIT` into a counted skip** under the gate (`bf_dlskip`).
* **The harness `C:/kyty/s96`**: three scorers (`pl96.py`, `bf96.py`, `bd96.py`, each verifying its
  own sealed sha256), `check_s96_counters.py` (identities I1..I9, I1 repaired under `pred/04`),
  `check_gate_order.py`, `accept96.sh` in six steps — guards → area → summary4 → endpoint84 → the
  session's own scorer → counter identities.

**Binaries** (`FACTS.md` §1): `pl96a` and `bd96a` were accepted against `65fca20dd4bc8528…`;
`bf96b` ran on `993be4a85af569c4…`, built after them for the download-ring repair. Their
acceptances cannot be re-run against the binary installed now, and that is stated, not hidden.

## 4. `bd96a` is DONE — the synchronisation term, at one of its two granularities

`bd96a` is VALID on criterion 3 (split −0.002 %, pairs 119/119, work −0.168 %) and, under the
repaired controls of `pred/05_bdaevery_controls.md` (9 087 B, sha256 `352448ac…`), **ADMITTED,
controls 6/6** (`FACTS.md` §5). An extra `PrepareBda` at every end-of-pipe label write costs
**+2 893.6 ± 93.2 µs a flip (2·SE), t = +62.08 on 119 pairs — 5.8× the "+0,5 мс (синхронизация)"
the rule assumes**; 611.84 calls a flip, `be_ns` 4 853.4 µs = 7.93 µs a call **including the
render-mutex wait, by design**. Both sealed controls were defects of the text and both repairs are
strictly stronger (`FACTS.md` §5.1): C3 judged the regime by `bda_scan`, which the knob itself
multiplies ×9.28, so no run of it could pass; C5 compared WALL with CPU time in the wrong
direction.

**Owed here: `bd96b`, the SUBMISSION granularity** (`bdaevery=1`, ~8 calls a flip), pre-registered
in `pred/03` §6 as P4, P5, P8 and never run. **Which granularity M3 is entitled to use is the
user's decision and cannot be taken until both numbers exist.**

## 5. The eight traps of session 96 that turned out to be real (`FACTS.md` §6)

1. **Enum↔table order is not checked by the compiler** — `KYTY_PATH_LAP` landed before
   `KYTY_FRAME_REP` while the enum had `PathLap` after `FrameRep`, silently swapping two gates →
   `check_gate_order.py` must print "GATE ORDER: clean" before every build that touched a gate.
2. **A hook on the PM4 parse path is not under the render mutex** — `BdaEveryHook` called
   `PrepareBda()` without it while it mutates the buffer cache (`renderContext.cpp:302-304`,
   `:343`, `:356-358`) → take the lock, check re-entrancy rather than assume it.
3. **Nested spans double-count** — `pl_sub` charged ~0.6 ms of 4.05 ms twice, `BufferFlushLazy`
   calling `BufferFlush` → depth guard.
4. **A lap can cover one call site of five** — `pl_gc` did → count the sites before sealing a span.
5. **A span taken on another thread must never be summed** — `pl_look` was; `LookaheadSubmission`
   runs on the guest submit thread (`graphicsRun.cpp:630`), outside `GuestGpu::Process`.
6. **A sealed identity can be unsatisfiable** — `pred/01` §5 C1 admits a block-boundary leak, §8 I1
   demanded an exact zero of the same counters; repaired under `pred/04`, leak **FIRST 64 / LAST 62
   / MID 0** → prove a new identity with a fixture passing the old control and failing only it.
7. **A sealed control can name a quantity the instrument itself moves** — C3/C5 of `pred/03` (§4)
   → when sealing a control, ask which side of it the knob touches.
8. **`KYTY_REC` and every `KYTY_*` go POSITIONALLY to `enter_scene.py`** — an export from the shell
   is dropped **silently** (only `KYTY_GATE_SCHEDULE` passes), so `bf96a` recorded no video; the
   trap was in session 96's own README and was stepped in anyway.

Carried: a failed run is **REPLACED**, never argued with; a failed **control** is REPAIRED under a
**NEW** sealed pre-registration; an arm fired only if the text of `GateArm:` says so, never
`counter > 0`; a band on a counter that read 0 prints NOT EVALUABLE, never HIT; `summary4.py`'s
`cpu_net_us` IS `cpu_gpu_us` under lite and `endpoint84.py` is the endpoint; `guards.py` check 6 is
**not** a criterion; patches go into a file via Write, never a heredoc.

## 6. The port — s96 → s97

Write **`C:/kyty/s96/s97_port.py` fresh in the SOURCE directory**, modelled on
`C:/kyty/s95/s96_port.py`, which carries **five root constructs as five separate edits**, each
asserted:

1. the head of every comma-spelled `--roots` default — `arms.py:29`, `baseline.py:83`,
   `effect.py:103` (spelled `--extra-roots`): the naive rewrite drops the previous root, so the new
   root goes in FRONT and **s96 stays**; asserted against the whole expected chain;
2. `area_verdict.py:56` `range(96, 70, -1)` → `range(97, 70, -1)` — the floor 70 does **not** move;
3. `shift91.py:35` `range(96, 66, -1)` → `range(97, 66, -1)` — the floor 66 does **not** move;
4. the tuple-spelled chains of `stg92.py:44`, `bda93.py:41`, `s94lib.py:21`, repaired **BY FILE
   NAME**: a blind replace also reaches `regime94.py:9` and **swallows repair 5**, and it reaches
   the degenerate chains (`area71_extract.py:14`, `area.py:227` and ten more) that must not move;
5. `regime94.py:9` — the chain that locates its root by looking for the log itself, extended by one
   root with the fallback moved to the new harness; `import os` is **asserted, not added**.

**The LEDGER.** On `regime94.py` repairs 4 and 5 produce **byte-identical text**, so no textual
check afterwards can say which fired. The port records which repair actually CHANGED which file and
asserts **repair 4 fired on exactly the three tuple files** and **repair 5 on exactly
`regime94.py`** (f2a/f2b; f2c proves no repair reached the twelve degenerate chains); it also
proves the collision is still real — the *naive* rewrite of `regime94.py` does contain the broken
tuple — and asserts the population of files that do.

**Diagnostic (i), fixed in s96, keep it fixed.** The s95 port searched for `/s95/` **with a trailing
slash**, which no root literal has (`C:/kyty/s95`), so it always printed a reassuring zero. Without
it the real answer is 20 files / 63 lines, 7 of them the live repaired chains; it now separates LIVE
from port-archive files and asserts the LIVE set is exactly the repaired chains.

Then, as every port since s83: **`gates_base.txt` byte-identical** (1 092 B, 99 names, sha256
`00c116dc…0594d8`, unchanged since s94); `gen_gates.py` **`--check` only** (it says "out of date" BY
CONSTRUCTION; `--out` without `--with` overwrites the file); `.txt`/`.json`/`.md`/`.csv`/`.sh`
byte-exact; `log_*`, `stdout_*`, `*.map` and anything ≥ 5 MB not copied; the session documents and
**all five sealed `pred/*.md`** into `prev96/` byte-exact with sizes and sha256 asserted, the fresh
`pred/` left EMPTY; `pathlap`, `bindfloor`, `bfmode`, `bfburn`, `bdaevery` added to the
must-be-absent list, because names the schedule assigns belong to the schedule. **`accept97.sh` is
WRITTEN NEW** — the port rewrites `.py` only. **Every carried `s8x/s9x_port.py` is a self-copy with
`SRC == DST` — never run one, never copy its constants.**

## 7. Do NOT

* **Do not start writing the rewrite.** M3 is unfinished; M4 and M5 have not begun.
* **Do not re-interpret a sealed rule after seeing a number.** A change to the M3 rule or its
  branches goes into `ROADMAP.md` first, with the user's decision recorded. Same for reopening P/F.
* **Do not quote `F_st` or any contrast from `bf96a` or `bf96b`** — both REPLACED; `bf96a`'s arms
  drew **1× and 4.014×** the area, `bf96b` never returned to its base arm.
* **Do not treat the label granularity as the rule's synchronisation term** — `bd96b` was never run
  and the choice is the user's (§4).
* **Do not quote a `PrepareBda` number without its BDA regime** (`regime94.py`; OLD ≈ 1 060 scans a
  frame, NEW ≈ 50); never two t values for one endpoint.
* **A foreign game on the GPU is a hard stop** — check `nvidia-smi` BEFORE launching.
* **Do not rebuild between acceptance and the final answer** (guards check 10).
* **The video pass is a debt** (`--video`, `s20_vidglitch.py`, ≥ 3 000 frames): `bindfloor` reaches
  the renderer by design, `bf96a`'s recorder was off by trap 8, the pass was never taken. The
  picture is allowed to break — the video is evidence of WHAT broke, not a correctness check — and
  it is owed before any of this enters a rewrite.

## 8. Not closed — the full list (`FACTS.md` §7)

* **`F_st`, and therefore M3, and therefore G and R1.**
* The stub's reversibility (§1) — the blocker for M3.
* The DRS clock (§2): now backed by a measurement, and it must be solved before any faster path can
  be measured at all.
* `bd96b` — the submission granularity — not run; the video pass for `bindfloor` — not taken.
* New and never attacked: **`PrefetchComputePipelines`, 245 µs a call, 6.2 % of the frame** (§2.4),
  and beside it the **1 921.6 µs a flip of residue outside the mutex that no session has
  attributed** (§2.2).
* Carried from session 95: **M4, M5**; the BDA regime; the written `bc_ok` slots; `C_bda` in NEW;
  the GPU side of `bdaall`; the single-chunk notify; the `ObtainBuffer` ring timer;
  `pfhint`/`pfcap`/`dapin` with the pin; route B.

**The session rule stands (`ROADMAP.md` §6): a session ends with a source change that passed A/B,
or it failed. A counter is a change, and its ABBA is its A/B.**
