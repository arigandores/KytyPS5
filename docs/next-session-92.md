**Session 91 found why two knobs were unmeasurable, built the one-site fix, sealed its test — and
did not run it, because the user asked that the game not be opened in that session.** Read
`docs/ROADMAP.md` **§0.1 first — it carries a session-91 addendum** — then `C:/kyty/s91/FACTS.md`
(§0.1 first: nine defects of my own text, four of them found before any pinned run existed).

Session 91's commit is on `merge-upstream`. **Source changed and was built TWICE, NO default
changed, and the new binary was NOT installed**: `C:/kyty/build/install/kyty_emulator.exe` is
`887ede9f8323297f…`, 23 623 680 bytes; the exe in the game folder is still session 90's
`12b0940a…` until `enter_scene.py` installs the new one. Harness — **`C:/kyty/s91`**; port it to
`C:/kyty/s92` with a script written fresh in the SOURCE directory, modelled on
`C:/kyty/s90/s91_port.py` (head of every `--roots` chain; `area_verdict.py`'s `range(91, 70, -1)`).
`gates_base.txt` **unchanged** — 1092 B, 99 names, sha256 `00c116dc…0594d8`.

## 0. Read first

1. `docs/ROADMAP.md` §0.1 (the session-91 addendum), §2 D (the session-91 block), §7.
2. `C:/kyty/s91/FACTS.md` — §0.1, §4 (D1 closed), §5 (`dapin` by TB), §7 (what was built), §10.
3. `C:/kyty/s91/PLAN.md` §0 A — the mechanism and the ranked estimator list. **It exists; do not
   redo it.**
4. The three sealed files in `C:/kyty/s91/pred/`: `01_shift.md` (scored), **`02_pin.md` and
   `03_repair.md` (NOT YET RUN — they are this session's work).**

## 1. What session 91 settled

* **The game's DRS budgets against GPU timestamps, and a GPU timestamp on this emulator is the
  pacer-scaled CPU clock written by GuestGpu at PM4 PARSE** (`RELEASE_MEM data_sel=3` →
  `Sync::ReadReferenceClock` → `KernelReadTsc` × pacer speed). Anything that changes GuestGpu's wall
  time inside the frame — work OR blocking — moves the rung. Within a block the high rung costs CPU
  +0.048 % ± 0.337 % a draw and GPU +11.2 %; the A/A slope of CPU on area is reverse causation.
* **D1 (`bufimp`) is CLOSED as a frame-time regression**: in the window where the game latched both
  arms of `bim90a` LOW (n ≥ 6150), `area_verdict` is VALID and `dt` reads +13.4 %; the carrier is
  **4 609.6 µs a flip of GuestGpu blocked in forced host-read drains** (1.6 µs in the census arm),
  a number that sat on disk in the `FrameTrace-wait` site table since session 90.
* **`dapin=3` with the record path off cuts GuestGpu CPU per draw by 9.19 % (t −133) [I]; its GPU
  cost is NOT settled** — TB's bracket is [−0.16, +2.77] % because the rung carries +2.3…+3.9 %.
* **Corrections to the record:** `summary4.py`'s `cpu_net_us` IS `cpu_gpu_us` under lite (it says
  so in a NOTE); `hostread_wait_us`, `ob_stream_us`, `gpu_proc/idle/blocked` are structurally 0 in
  lite (`Scope` stamps only under `TimingsEnabled`); s90's E3 was vacuous.

## 2. What is settled — do not reopen

* Everything in `ROADMAP.md` §3, now including **D1**, **a covariate adjustment on area**, and
  **stratifying on the DRS rung**.
* Route A; route C at slot and stage granularity; the program and slot lookups; `CopyAheadResult`;
  merging draws; the whole-stage memo; removing the prefetch; hoisting `AheadTake`.

## 3. The work

### 3.1 FIRST: the pinned runs, in the order `pred/02_pin.md` §1 fixes — ask the user before opening the game

    KYTY_GATE_SCHEDULE="30+1800:dapin=0 recordthread=0|dapin=3 recordthread=0" \
      python C:/kyty/s92/enter_scene.py pin91a --gates-file C:/kyty/s92/gates_base.txt --hold 300 \
      --warmup-first --pred C:/kyty/s92/pred/02_pin.md KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1

**Keep the tags `pin91a/b/c`** — `pin91.py` keys the run type on the last letter, and the bands were
sealed for those tags. **Carry `pred/02_pin.md` and `pred/03_repair.md` into the new harness
BYTE-EXACT** (the port empties `pred/`: copy them back from `C:/kyty/s91/pred/` and check both
sha256 — `ebf4b9f0…` and `7c9fae4c…`), and do not re-seal them. Score with
`sh accept91.sh <tag>` (its `R` must point at the harness that holds the log).

* **A (`pin91a`)** — the pin's own test (R1–R3, R4' of `pred/03`) against a contrast that moved the
  rung by +28.4 pp unpinned, and `dapin`'s GPU cost at a fixed rung (E3, the ELEVENTH session of that
  debt), and TB's first out-of-sample test (E2).
* **B (`pin91b`)** — the positive control (`KYTY_GPU_CLOCK_PIN=2`): the rung must CLIMB, or A's LOW
  proves nothing.
* **C (`pin91c`)** — `bufimp=1|2` pinned: D1's whole-run effect and the `hr_*` decomposition.

**If A holds and B climbs, the pin is this programme's instrument for every rung-moving knob.** If
A fails, the rung is driven by something the pin does not touch (EOP interrupt / flip completion
instants reach the guest at REAL GPU completion, stamped with the scaled clock) — say so, and TB is
the fallback, with its CPU D labelled [I].

### 3.2 THEN: the 64 KiB split, first reading

`stg_in_b / (stg_in_b + stg_pool_b)` rides free in every arm of every run now (`pred/02` C1). It
closes the question session 90 left about D1's arithmetic — which D1's closure makes academic for
D1 but not for `ASYNC_COPY_MIN_BYTES` itself.

### 3.3 The debts, ranked

* **The `ObtainBuffer` stream ring**: 19.66 MB a flip in 13 380 copies, never timed in a
  measurement run (its timer is `TimingsEnabled`-gated). The `hr_*` idiom (`Enabled()`) is the fix.
* The per-element price of `ResourceSpecialization::operator==`; the prefetch lines a take reads;
  the 459.4 µs take; the witness share of `RebindImages`; route B items 2, 8, 10, 12, 3.

**Say the odds out loud.** 16.7 ms needs ~15 ms removed. **Session 91 removed nothing and closed
D1 with a loss.** The pin is an instrument; what it lets you measure is hundreds of microseconds.

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or
it failed.** Session 91 built its change and could not A/B it; **the pinned runs ARE that A/B.**

## 4. Do NOT

* **Do not schedule the pin as an arm** — it is read once per process; switching the clock rate
  mid-run breaks its monotonicity.
* **Do not read "0 % HIGH" as the pin working on a contrast that never moves the rung** — 22 of 27
  runs of sessions 82–90 never go HIGH.
* **Do not trust a `Scope`'s ns column in lite**; do not quote `summary4`'s `cpu_net_us`.
* **Do not let a flip-number window re-admit a refused matched subset silently** — W on `bim90a`
  was, to the digit; say so.
* **Run every new band against the record BEFORE the run** — that is how R4 was caught.
* Carried: pre-registrations sealed in place and never edited; arming proved inside the run; ratios
  of sums; `guards.py` check 10 hashes the exe installed now; check 6 is not a criterion;
  `gen_gates.py --out` only with `--with`; never pipe a writing script through `head`; the first
  entry after a fresh build hangs (`--warmup-first`); `daepceil`'s comment says "(default 1)" and it
  is 0.
