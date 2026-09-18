**Session 94 closed the last candidate of the scale the goal needs, and the user's decision after it is
ROUTE E — THE REWRITE of the translation layer. Session 95 does not write a line of that rewrite: it
runs the first two of the five measurements that decide WHICH rewrite is worth attempting (ROADMAP
§2 E). M1 is hours and no code; M2 is this session's A/B'd source change.** Read `docs/ROADMAP.md`
first — **§0.1's decision paragraph, §2 E (budgets, the five measurements with their sealed rules,
the traps), §5 item 5 (the order is M1 → M2 → M3 → M4 → M5)** — then `C:/kyty/s94/FACTS.md` (§0.1,
§0.2, §2.3, §3.2–3.4, §7) and the four analyses plus the judge in `C:/kyty/s94/rewrite94/`.

**Start the report with three numbers, every session of route E:** the budget (≤ ~3.0 µs a draw on a
median frame, ≤ ~2.3 µs on a p99 frame of 7 284 draws), where the CPU path stands today (6.4 µs a
draw; 31.6 ms a frame against a GPU busy 12.8 ms), and which of M1–M5 is still undone. **Do not
promise 60 FPS: the estimate is ~15 % (8–25 %), and it does not rise with the speed of the executor —
it is held by the unknowns, not by typing.**

Session 94's commits are on `merge-upstream`: `4912ae5` (sources before the runs), `7d03f93` (results
and record), plus the route-E edit of the ROADMAP. **No default changed; nothing shipped.** The
installed `kyty_emulator.exe` is
**`4338ba1a300a17be170167a4291748f8a93ad282f4c1c27a4c93084752386b4e`, 23 642 624 bytes**, not rebuilt
after acceptance. Harness — **`C:/kyty/s94`**; port it to `C:/kyty/s95` with a script written **fresh
in the SOURCE directory** (`C:/kyty/s94/s95_port.py`), modelled on `C:/kyty/s93/s94_port.py`.
`gates_base.txt` **unchanged** — 1092 B, 99 names, sha256 `00c116dc…0594d8`.

## 1. M1 — where the process's CPU goes (hours, NO code, do it first)

The programme has never looked outside the GuestGpu thread. Known [M, `mc94a` unarmed arm]: the
process burns **7.5–8 logical CPUs** (`cpu_proc` median 265 625 µs a flip, quantised in 15 625 µs
steps); GuestGpu 32.4 ms of it, the record thread 30.5 ms **of which 27.3 ms is spin**, M1 workers
~26.8 ms, main 9.2 ms, present 1.1 ms — **148–166 ms a flip are unattributed**; guest threads take
~13.8 ms a flip of page-fault time (`fault_us` 15.0 ms all threads, 1.1 on main, 0.1 on GuestGpu).

* **Method:** 30 s of settled Sky Garden (`enter_scene.py … --hold 300` is enough; no gate needed),
  and per-thread CPU deltas — PowerShell `Get-Process kyty_emulator | %{ $_.Threads }` sampled twice
  and differenced, or ETW (`wpr -start CPU`) for a real sample profile. Map thread ids to names
  through the log's `thread create:` lines. Report: work vs spin per thread, per game frame.
* **The sealed rule (ROADMAP §2 E):** real (non-spin) work outside translation above ~8 logical CPUs
  at twice the frame rate ⇒ **route P is closed**; any guest thread costing more than ~12 ms per game
  frame ⇒ **60 FPS is out of reach altogether** and the programme's answer is final.
* Cheap and worth taking in the same pass: how much of the record thread's 27.3 ms spin is real, and
  whether the ~40 submits a frame serialise anything.

## 2. M2 — frame-to-frame repetition of a draw's CONTENT (the session's A/B'd change)

**Nobody has measured it.** What exists: a whole stage's bindings repeat the PREVIOUS DRAW's in
2.06 % of stages, slots in 64.2 % (s84); the M1 job key repeats between frames 3 times in 9 460
(0.03 %, s66) — **but that key carries per-object and per-frame pointers**, so it says nothing about
content; s57's `e9` compared with the last set of the same layout and found `e9_full` = 0 because
stream-ring offsets differ every draw; s62 found 84 % of ring copies byte-identical.

* **What to count:** per draw, a canonical content hash — pipeline (or its layout definition), image
  views and layouts, samplers, non-ring buffer identity (handle + guest range, NOT the ring offset),
  the SRT/shader-data payload by CONTENT (a hash of the bytes, not the pointer). Then, per flip: how
  many of this frame's draws have a hash present in the previous frame's multiset (and in N−2, N−3 —
  double-buffered per-frame allocators favour N−2), and what share of the frame's draw time those
  draws carry. **Draw numbering is not stable (s66), so align by multiset membership, never by index.**
* Report both the cheap ceiling (identity only) and the honest one (payload content), because the
  proof that bytes are unchanged is what killed every replay idea so far: content checking cost 4.2 ms
  per 15 MB (s62), and ~2.8 ring ranges a draw (~20 MB a frame) are per-object payload that moves.
* **The sealed rule:** the share of GuestGpu draw time covered by a repeating template < **0.84** ⇒
  **route F (frame replay) is closed permanently.**
* Gate name suggestion `framerep`, default 0, MEASUREMENT ONLY, ABBA with `KYTY_GPU_CLOCK_PIN=1`, the
  census priced as its own instrument (session 94's cost +1 774 µs for a cheaper census — expect more,
  and keep the hash out of the timed brackets if anything else is being timed).

## 3. If M1 and M2 both leave route P alive, M3 is next (1–2 sessions)

The ceiling stub `bindfloor` (picture allowed to break, never shipped): skip `AheadTake`,
`MaterializeResources`, `PrepareBindings`, `Rebind*` and the per-slot syncs; bind one prebuilt
null-filled set per layout; keep PM4 parsing, render targets, pipeline, emit and record. Add lap
chains that split **the 4.05 ms outside the render mutex** and **the ~5 ms of `mh_emit` beyond
CommitBindings** — both have never been split. Sealed rule in ROADMAP §2 E.

## 4. Carried debts (not this session unless M1/M2 finish early)

* **The BDA regime** (`bda_scan` ~1 060 vs ~50 a flip): in OLD, PrepareBda alone costs 2 242 µs a
  flip, and OLD is the common launch state. Why a launch leaves it is unknown.
* The written bc_ok slots (490.5 µs a flip, 0.49 µs each, 8× a read-only slot).
* Why the other half of s93's merge population cannot reuse its set; the GPU side of `bdaall`
  (+4 840 µs); `C_bda` in the NEW regime; the single-chunk notify (99.9 µs); the `ObtainBuffer` ring
  timer (lite = 0); `pfhint`/`pfcap`/`dapin` with the pin; route B items 2, 8, 10, 12, 3.
* **The DRS clock floor** (ROADMAP §2 E traps): before ANY rewrite makes the CPU faster, the game
  must be kept off the 4K step, or no GPU budget is meaningful. Days of work; predict with the s91 pin.

## 5. The port — FIVE root constructs, each a separate edit

1. the `--roots` heads (`arms.py:29`, `baseline.py:83`, `effect.py:103`) — new root in FRONT, `s94`
   stays; 2. `area_verdict.py:56` `range(94, 70, -1)` → `range(95, …)`; 3. `shift91.py:35`
   `range(94, 66, -1)` → `range(95, …)`; 4. the tuple chains `stg92.py:44`, `bda93.py:41` **and
   `s94lib.py:21`** (`ROOTS = ('C:/kyty/s94', 'C:/kyty/s93', 'C:/kyty/s92')` — a literal rewrite drops
   `s94` and hides `log_mc94a.txt`); 5. **`regime94.py` picks its root by tag** and must keep pointing
   at `C:/kyty/s94` for session-94 tags. `gates_base.txt` byte-identical; `gen_gates.py --check` says
   "out of date" BY CONSTRUCTION — never rerun it without `--check`. Write `accept95.sh` new (the
   `.sh` files are byte copies pointing at their own harness), with step 5 on session 95's own sealed
   pre-registration. **Every carried `s8x/s9x_port.py` inside a harness is a self-copy: never run one.**

The rule is unchanged: **the session ends with a source change that was A/B'd on this machine, or it
failed.** M2's census is that change.

## 6. Do NOT

* **Do not start writing the rewrite before M1–M5 have closed what they can.** This programme's upper
  estimates have overshot 2–20× six times.
* **Do not write or dry-run the scorer after sealing** (session 94 did, and its first draft said
  otherwise); do not decide that an arm fired from `counter > 0`; do not score a band on a counter
  that never fired.
* **Do not quote a PrepareBda number without its regime**, and do not quote two t values for one
  endpoint (`endpoint84.py` is the endpoint).
* **Do not demand an exact zero on a schedule arm** (both session-94 leaks sat at distance 29 of 30).
* A foreign game on the GPU is a hard stop; `summary4.py`'s `cpu_net_us` IS `cpu_gpu_us` under lite;
  guards check 6 is not a criterion and check 10 hashes the exe installed at that moment — never
  rebuild between acceptance and the final answer; `gen_gates.py --out X` without `--with` overwrites
  `gates_base.txt`; never pipe a writing script through `head`.
* Carried: pre-registrations sealed in place and never edited; a failed control is REPAIRED under a
  NEW sealed pre-registration; a run that fails admission is REPLACED, not discussed; the first entry
  after a fresh build hangs (`--warmup-first`); ratios of sums, never per-frame identities.
