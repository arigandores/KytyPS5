# Session 99 — M3 bindings-only preparation (WIP, no game launch)

This is the session's source of truth. Work is unfinished: the user has authorised preparation,
code and offline checks, and explicitly forbidden game launches until their later signal.

## 0. Three opening numbers

Budget <=~3.0 us/draw, <=~2.3 us at p99 (7284 draws); reference CPU path 6.4 us/draw,
31.6 ms/frame, GPU busy 12.8 ms. M3 remains GAP; M4 and M5 are undone, in that order.
No claim of 60 FPS, speedup, renderer correctness or a new B endpoint is made.

## 1. Preparation established

Mode2 previously ignored bfburn: BindFloorBurnSlice returned unless mode==3. This is now
repaired to allow mode2/3, with no change to mode0/1 or zero-budget behaviour. Three new
positive counters distinguish real mode2 resource acquisition: bf_live_ahead, bf_live_mat,
bf_live_memo. Failure and frozen reuse do not count; counters print zero when inactive.

The code was built once by the parent, only with C:/kyty/build_local.cmd, exit 0. Warnings
were present; the build was not warning-free. The new executable is 23739904 bytes, SHA256
ee9cc8ab1f5d25384dedb02a6a6abfca2aa7692585fcaddc74950721afc7a160, copied byte-exact to
C:/kyty/s99/kyty_emulator_s99.exe. The game-folder exe stays the previously installed
9aa93e73673e8c5377636d698c355febc99d5c3b9064a259011fa16fb1df1dbc. No game was launched.

A fresh independent C++ reviewer (verify99, no conversation fork, not a code author) found
no reproducible defect in the seven-file diff. This is static VERIFY, not runtime proof.

## 2. Port and provenance

Fresh C:/kyty/s98/s99_port.py created the s99 harness. Independent fresh reviewer
verify_port99 reconstructed the transformation without running/importing the port:
1399 files (406 Python, 993 non-Python), 35 ledger entries; five root constructs, 10
sealed texts, 18 live PRED constants in 10 files and 15 historical log lookups all PASS.
gates_base is unchanged: 1092 bytes, 99 unique names, SHA256
00c116dcad0cdff62f96f5ec4a72faa7e9ed5210e8304380a098a280900594d8.
Evidence: port99_diagnostics.txt, port99_ledger.json, verify_port99/result.json.

Port's first attempt FAILED its own assertion: Windows backslashes prevented the global root
replacement. Fixed canonicalization before creating the successful destination. The incomplete
first destination was preserved as C:/kyty/s99-port-first-attempt after deletion was rejected
by automatic approval review. This failure is recorded, not hidden as a successful first run.

## 3. Parent's independent raw-number check

recount99.py imports no historical scorer. It parses raw FrameTrace/GateArm records, forms T*
and block pairs, and writes recount99.json. Results:

| raw source | recomputed value |
|---|---:|
| bf98a, 128 paired armed blocks | 14.274068801724138 ms |
| bf98c, 122 paired armed blocks | 12.825411375615765 ms |
| rv98a completed falling edges | 432 |
| rv98a_warmup completed falling edges | 425 (426 announced, final incomplete excluded) |
| full-floor global input min/max, +2.2535 | 15.078911375615764 / 16.527568801724136 ms |

Thus the previous GAP and 857 completed edges are reproduced. Published three-decimal old
summary endpoints remain 14.274 / 12.825. These are old data; they do not prove mode2 reversible.
Raw SHA256 values are in recount99.json.

## 4. Rule/scorer status

The new rule has been sealed and verified offline. Its intent is an explicitly limited
diagnostic: both mode2 instruments are required, with new C4_B and measured-burn subtraction;
global G/R1 remain GAP regardless of HIGH/LOW/GAP of the bindings-only residual. Mode2 retains
work G may remove, and no finite pessimism bound for the instrument has been proved. The
descriptive returned-work contrast is B-F, not F-B, and includes clears/cache/binary changes.

The rule was sealed after 18 initial tests: pred/01_bindings_only.md, 10848 bytes, SHA256
8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d. Historical dry runs reproduced
14.274 / 12.825 ms, 10/10 and VALID on both; rv98a reproduced 11/11 and 857 edges.

The fresh scorer VERIFY returned CODE despite those 18 passing tests. Reproducible defects:
live-counter darkness and required-field completeness were checked only after n=2100;
an existing area CSV could mask a 100% raw-area change; metadata arms could contradict the
schedule; and a short raw record could claim a full hold using metadata alone. The inherited
launcher also continued to a counted process after a failed warmup. Evidence is preserved in
verify_scorer99/counterexamples*. The sealed text was not relaxed or edited. Repairs and final independent re-verification passed; these failures are not erased by later passing tests.

The parent's first launcher repair passed six tests but the fresh reviewer found more missed
fatal spellings and stdout-only markers. Version 2 shares run_safety99.failure_marker with the
scorer and scans both saved streams; it stops before the counted process on failed/short/dead
warmup, absent log/stdout or failure markers. Eight tests execute the actual loop AST with a
mocked attempt function; no emulator imports or launches occur. This is distinct from the
initial port's byte-exact status: enter_scene.py now has an explicit session-99 follow-on patch.

## 5. Still required after user's signal

Install the saved new binary (no rebuild just for a git label), preflight the GPU and workload,
then obey the sealed sequence with one executor: separate calibration and counted a/c runs,
no retries after failures; video >=3000 frames and recovery review. There is currently no B_a,
B_c, C9 calibration, mode2 hazard-rate proof, A/B performance acceptance or mode2 video.
M3 remains open, and M4/M5 have not started. Side fixes (BVH/OIT loop caps and cross-queue
latch change) were not taken in this preparation.

## 6. Final offline VERIFY — preparation only

Frozen scorer tests: 23/23 PASS. Fresh verifier's separate counterexamples and positive
components: 20/20 PASS (including raw-area regeneration and real calibration replay).
Harness: 8/8 AST tests, with all previously failing markers stopping before counted.
The initial CODE reports remain; final report is verify_scorer99/FINAL_REVIEW.md.
The parent read the actual final outputs, checked the frozen hashes and independently
recomputed the old key numbers. No code change followed the C++ build.

Duration admission now requires the whole raw record's dt sum to be at least the claimed
actual hold. This is a necessary consistency check, not an independent proof of hold timing;
post-stable durations are reported, not a new deciding tolerance. The old bf98c record has
post-stable 300.094190 s versus metadata 300.1 s (5.810 ms difference, one flip 33.516 ms).
No arbitrary threshold was retrofitted. Calibration/measurement data do not yet exist.

The initial 18 tests missed real defects. Final tests cover those counterexamples, but do not
prove runtime correctness, a mode2 hazard rate, a performance win or 60 FPS. The proof of
mode3 on the old binary has not been transferred to mode2. The necessary next action is the
user's signal permitting game execution; no launch is queued or running.

Source changes and reviewable harness snapshots are saved as a WIP commit (hash recorded in
the final response and the emulator-folder HANDOFF/AGENTS/CLAUDE). No push. The unrelated
nlohmann_json submodule modifications are excluded.
