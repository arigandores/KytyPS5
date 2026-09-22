# Session 103 — route E after M5: the user's decision on G first, then the correctness code the programme owes

**Read first:** `ROADMAP.md` §0.1 (the session-102 addition), §2 E (M5 and its result), §5 item 5,
§7 (the session-102 rows); then `C:/kyty/s102/FACTS.md` in full — **including §9** — (in git
`docs/local-session-102.md`), `C:/kyty/s102/README.md`, and the sealed texts `pred/01`–`09` of
`C:/kyty/s102` (hashes in `SEALS102.txt`; `08_audit_addendum.md` withdrew "M5 closes G", `09` corrects
its lens tally and states that X and Y are over eight items).
**Sealed texts are immutable:** a correction goes into a new sealed addendum, never into the file.

**Open the report with the three numbers** (`ROADMAP.md` §5 item 5): budget ≤ ~3.0 µs a draw (median) /
≤ ~2.3 µs (p99, 7 284 draws); the carried reference path is 6.4 µs a draw, 31.6 ms a frame, GPU busy
12.8 ms; **M1–M5 are all done** (M4 removed by the user, M3 a final GAP, M5 measured). **Do not promise
60 FPS.** The ~15 % (8…25 %) estimate included G; if the user closes G, say which estimate replaces it
and label it [I] — do not derive a 60 FPS statement from M5 (`pred/01` §8).

## 0. The decision is recorded: G stays alive behind M5′ — and the standing rule that recorded it

**Standing delegation (the user, after session 102):** programme decisions are the executor's, taken
by the goal and **recorded in `ROADMAP.md` before the first action on them**; an unrecorded decision is
void; the user is not asked. Read `ROADMAP.md` §0.1 (the delegation and the decision), §6 (the rule).

Session 102 measured M5: today's emitter's BDA path costs **X = +42 %** and **Y = +33 %** at equal load
granularity on eight of the ten top shaders (S1, S8 fail V-e), and the unavoidable const-bank →
global-load step **L = +2.1 %** over all ten. The audit withdrew "M5 closes G". **Recorded decision (b):
G stays alive and unlicensed behind M5′** — the BDA path as G would build it, priced by one ratio X′
with threshold +6 % (rule in `ROADMAP.md` §0.1, written before any work on it). **Do not change that rule
without recording the change in ROADMAP first.**

## 1. One translator change, one cold session: the entry hang, the deferred sites, and the M5′ switch

**`KYTY_BVH_LOOP_CAP`, minimal variant** (FACTS §5; design `C:/kyty/s101/design98/loops.md`): the
`KYTY_LOOP_LIMIT` machinery bounded for `{380bb9d636390bae}` (the only shader the GPU named in entry
hangs, twice), one shared budget per invocation, `EmitReturn` on abort (not a bare `OpReturn`), a
signature token for any override, optionally a trip counter in the fault-buffer tail. Leave
`5323c4ef4f785055` out of the set. **Fold in the 15 deferred presence-only sites under
`src/graphics/shader/**`** (FACTS §3) — one translator change, one cold run for both.

* Before the build: `KYTY_RECOMPILE` + `s16_sass.py`/`m5_sass_full.py` on `380bb9d6` (three
  permutations) and on `5323c4ef` — registers and spills unchanged on 5323, spirv-val with
  `--uniform-buffer-standard-layout`.
* Seal the entry series before it runs: ≥ 45 entries (P(0 hangs | 6.67 %) = 0.045), preferably 67;
  rule "0 `GpuHangAbort` before `GateArm` across the series"; every trip followed by survival; zero
  trips on entries without a hang (else the cap cuts legitimate work); worst entry frame well under TDR.
  The first run after the build is cold (translation, pipelines.bin) — a declared warm-up, not an entry.
* **Video pass is owed** (the cap reaches the renderer): `--rec`, `s20_vidglitch.py`, ≥ 3 000 frames.
* ROADMAP §6: this is a real-path change with its own sealed A/B-equivalent (the series).

**In the same translator change: the M5′ switch** (default off, in the translation-cache signature when
on; the rule of `ROADMAP.md` §0.1): vector BDA loads when the base alignment class and the immediate
prove 8/16-byte alignment; **no fault-buffer store in pixel shaders**; one page-table read per lookup
(the null base as a constant, not a re-read of entry 0); `NonWritable`/`Restrict` on read-only pointers;
no reloads after stores. Build arm **V2′** with the session-102 harness (`C:/kyty/s102/m5_recompile.py`,
`m5_sass_full.py`, `M5_RUNBOOK.md`) on the session-102 capture `kyty_1790110985179586` **if arm A still
reproduces its modules for ≥ 7 items carrying ≥ 60 % of the weight** (V-c; S1 already used BDA in A, so
expect S1 to drop). Seal the M5′ protocol before any timing (arms B, A, V1, V2′; R = 20; the §0.1
verdict). **No game run is needed if the capture is reusable.** Watch registers/spills on every item
(the register trap of `5323c4ef4f785055` applies to any emitter change).

## 2. The port, first

Write `s103_port.py` **fresh in `C:/kyty/s102/`** (`SRC = C:/kyty/s102`, `DST = C:/kyty/s103`), modelled on
`C:/kyty/s101/s102_port.py`. **Never run a carried `*_port.py`.** Advance: the COMMA chain 28 → 29 roots
(`s103…s75`); `area_verdict.py` `range(103,70,-1)`; `shift91.py` `range(103,66,-1)`; `s94lib.py` 12 roots,
`bda93.py` 13, `stg92.py` 14; `regime94.py` 11 roots plus the `s103` fallback; r6 grows **13 → 16 files and 22 → 27
constants**: `m5_102.py` `PRED` + `ADDENDUM` (the second is not a `PRED*` name; `m5_plan.py` and
`m5_rdlib.py` import it), `dab102.py` `PRED` + `PRED05`, `ckpt102.py` `PRED` — all repointed to
`prev102/pred/`; **`m5_recompile.py:41` `PRED = ROOT + '/pred/01_m5_bench.md'` is an r7 expression path**
(a live tool M5′ would need); `s102_port.py`'s `NEW_SESSION` tuple names `m5_102.py` and
`accept102.sh`, which now exist in the source — replace it with session-103 names; `accept102.sh`
carries `R=C:/kyty/s102` (a carried shell script, never run). Sealed texts grow **21 → 30** (nine
session-102 texts; the s100/s101 `03_audit_addendum.md` collision is already handled; check no s102
name collides). `ABSENT` becomes **36 names** (add
`dabatch`); assert `gates_base.txt` still 1 092 B / 99 names / `00c116dc…0594d8` and `gates.cpp` yields
**135** entries (111 gates + 24 knobs). The session-102 archive scorers (`m5_102.py`, `dab102.py`,
`ckpt102.py`) are pinned to their own seals, tags and binary: carry, never run.

## 3. Traps that are live

1. `KYTY_GPU_CHECKPOINTS=0` is harmless **only on binaries ≥ `346ba4f6…`**; on any older binary it still
   turns checkpoints on. In measuring runs, still do not pass it at all.
2. Presence-only switches survive in the translator tree until §1 lands: `KYTY_SRT_VERIFY=0`,
   `KYTY_BVH_STUB=0`, `KYTY_SAMPLE_LOD0=0` are ON.
3. `gates_base.txt` pins `recordthread=1`: an environment `KYTY_RECORD_THREAD=0` is overridden at the
   next command buffer (session 102's capture retry).
4. `enter_scene.py` takes emulator flags only as `--emu-arg=--rd` (argparse rejects `--emu-arg --rd`).
5. A start-up crash `commandRecorder.cpp:326` happened once under `--rd`; undiagnosed.
6. RenderDoc `EventGPUDuration` per event is not additive (30–54 % of PS readings are 0); whole-frame
   and item-sum estimators differ by a few percent.
7. Never rebuild between a measurement and its acceptance; `--attempts 1`; `--out` never overwrites; all
   `KYTY_*` positionally to `enter_scene.py`.
8. Any seal that changes the **composition** of a verdict — not only a number — is a rule change:
   ROADMAP first.

## 4. Deliverable

PLAN with a measurable question, record any rule or constant change in `ROADMAP.md` first, CODE → TEST
→ a fresh VERIFY → **an adversarial audit before publishing**. One executor owns the GPU, the log and the
caches; build only through `build_local.cmd`; `check_gate_order.py` after any gate/knob patch and before
the build. At the end: one edit to ROADMAP, then FACTS (`C:/kyty/s103/FACTS.md`, mirrored as
`docs/local-session-103.md`), `docs/next-session-104.md`, both game contexts including the
environment-variable list, and the mandatory commit without push; do not capture the dirty
`3rdparty/nlohmann_json`.

## 5. Must not be claimed

That M5 closed G or licensed it (the recorded decision is (b): G alive behind M5′) · that X is G's intrinsic
price · that the presence class is fully fixed · that the checkpoint fix is a speedup · that `dabatch`'s
saving was measured at 1024 (it was extrapolated from the pilot) · that the capture retry ran without the
record thread · that M5 ran without a game run · **any frame-rate gain, speedup or 60 FPS.**
