# Session 122 — the bottleneck map across scenes through causal probes (a burn knob per thread)

**Read first:** `ROADMAP.md` §0.1 "СЕССИЯ 121 — ЗАПИСИ ДО ДЕЙСТВИЙ" item 9 (the audit: GuestGpu micro-tracks on Sky Garden
exhausted at 0.5 ms; the census-to-wall rule; the plan of this session) and item 8; "СЕССИЯ 120" item 3 (the scene
map's first form) and item 8(5) (A-walker parked, its reopen triggers); `C:/kyty/s121/FACTS.md` (git
`docs/local-session-121.md`); `docs/session-121/audit/why.md` (why the census price did not become a gain).

**Open the report with these numbers:** installed build `d3a981a2…` (`7c73f26`); Sky Garden ≈ 51–52 % game speed (`dt`
31.7 ms NEW / 32.6 ms OLD BDA regime); GuestGpu CPU-bound (`cpu_gpu_us` ≈ 31.9 of 32.6 ms), the record thread idle-spins
≈ 26.8 ms, the GPU busy ≈ 13.4 ms. Session 121: an 8-way texture memo removed 84 % of key misses and saved < 0.16 ms
(2SE) — census prices are not wall prices. 60 FPS is not promised.

## Rule of the session

As since session 102, with session 121's additions: every decision in `ROADMAP.md` before the first action — also a rule
constant that differs from an accepted decision, BEFORE the agent brief, with the lead as author; agent paragraphs tagged
and accepted explicitly; amendments as new items; seals with fixtures and mutants (`mutlib` v4.1 FULL; filled seal
constants re-checked by a full run); edit scripts write LF; suites end with `ALL OK`; backslashes only through files
written by Write; estimator window frames 10–88 (the arm switch lands at position 89 of the outgoing block); agent briefs
forbid open-ended `tail -F`; chain command lines plain (no `mutlib` in them); the chain repeats `procload` and the name
guard before taking the lock and installing a build; a draw-adjusted estimator (with a Δdraws guard) is pre-registered
beside the raw one; privacy grep before commits includes the user name, the e-mail and the launcher user name; foreign
applications are not named in committed text.

## Steps

0. **Harness `C:/kyty/s122`** (port s121; `go` chain with the second gate before the lock).
1. **Design in ROADMAP before code** (designer + adversarial reviewer): ONE measurement-only knob **`burn`** (default 0) —
   spin a calibrated N µs per frame on a chosen thread: GuestGpu (inside `Process`), the record thread, an M1 worker, the
   main guest thread; the value encodes thread and dose; read once per frame; counters of the burnt time. Validity: the
   burn must be pure CPU on that thread (no locks, no memory traffic beyond a register loop).
2. **Scenes:** Sky Garden (the anchor), the desert `intro_next`, and 2–3 levels with heavy effects (names from the game's
   data; entry via `KYTY_GUEST_ARGS -lvl`). Per scene ONE short sealed ABBA of two doses on the GuestGpu thread (0 | N µs)
   plus a dose on the main guest thread; `lite` counters for the classification (`cpu_gpu/dt`, `rec_spin`, `gpu_busy/dt`,
   the `dt` quantization, `semwait`, BDA regime).
3. **Reading:** d(dt)/d(burn) per thread per scene — ≈ 1 means that thread is critical and savings on it convert 1:1;
   ≈ 0 means it is not; a GPU-bound scene shows `gpu_busy/dt` ≥ 0.9 and ≈ 0 slopes on every CPU thread.
4. **Consequences fixed before the runs:** a GPU-bound scene opens a shader track there (top shaders by `KYTY_GPU_TIME`,
   the offline `KYTY_RECOMPILE` bench); a scene whose critical thread is not GuestGpu opens a track on that thread; if
   every scene is GuestGpu-bound with slope ≈ 1, the next lever is structural (the parked A-walker's reopen trigger, or
   the descriptor-heap idea as a measured bench first).
5. **Audit, close.**

## Must not be claimed

60 FPS; any census number as a speed-up; that R2 or `spcen` A could pay (parked, census numbers do not reopen them);
that `texmemo8` pays anywhere (closed at < 0.16 ms on Sky Garden); a speed number beside another heavy job.
