# Session 121 — the R1 prototype: an 8-way texture memo (knob `texmemo8`) is CORRECT (seal 01 `vfy121` PASS: 0 mismatches on ~3.1 M verifications, 0 video glitches) and fully armed (key misses −84 %), but it does NOT pay: seal 02 `shp121` NO_SHIP, Δ`dt_us` +1.3 ± 154.3 µs; the R1 track is closed; the census price of a miss was inflated; the GuestGpu micro-tracks on Sky Garden are exhausted at 0.5 ms; no speed-up shipped

**Single source of truth for session 121.** Mirrored into git as `docs/local-session-121.md`. Harness root
`C:/kyty/s121`. Decisions: `docs/ROADMAP.md` §0.1 "СЕССИЯ 121 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1–9.

**Opening and closing numbers:** Sky Garden, defaults as in session 120 plus `texmemo8=0` (new, measurement only),
installed build `d3a981a2…` (git `7c73f26`) at the close — unchanged. Game speed ≈ 51–52 % (`dt` ≈ 32.6 ms in the OLD BDA
regime, ≈ 31.7 in NEW). 60 FPS is not promised.

---

## 1. Result

1. **Design (items 1–2):** designer + adversarial reviewer (SOUND_WITH_CHANGES, RC1–RC8) → knob `texmemo8` 0..3: 1 = 512
   sets × 8 ways of the same 4 096 entries, tags + LRU in one 64-B line per set, the full hit proof unchanged; 2 = plus a
   VERIFY of every gained hit against a fresh full resolution; 3 = plus a positive control (tautological — it proves the
   counter path; the offline unit test proves that `tm8_bad` can fire).
2. **Code (item 3, `5e8e1d2`, build `0bd21ec2`):** 31 `tm8_*` counters, `renderMemo8.h` (pure set logic), the miss path in
   a force-inlined lambda (byte-identical block, script-checked), an offline unit test against a brute-force LRU (10⁶
   operations, 14/14 header mutants killed). The code review found `Tm8::Find`/`Tick` out of line on every P lookup —
   fixed (`always_inline`), checked by a scan of call targets in the machine code.
3. **Two seals (items 4–7):** seal 01 `vfy121` (the verify run, PASS rule sealed before it) and seal 02 `shp121` (the
   ship ABBA). Scorers by writer → pre-seal check → fixer agents; `mutlib` v4.1 FULL 297/297 and 344/344 (after a
   repair of the seal-02 suite: the filled constants had left two branches without a killing fixture, 342/344 on the
   first run).
4. **Seal 01 `vfy121` — PASS** (16:48–16:53, NEW BDA, 4 × 16 blocks): 0 correctness counts on all rows, 0 mismatch
   lines, ~1.56 M + 1.56 M verified gained hits in modes 2 and 3, the control alive, video 7 604 frames with 0 glitches;
   arming mode 1 vs 0: `tex_hits` +1 388, key misses 1 419 → 201.
5. **Seal 02 `shp121` — NO_SHIP** (17:19–17:24, OLD BDA in both arms, 44 pairs, ADMITTED):

| quantity | P (`texmemo8=1`) − M (`texmemo8=0`) |
|---|---:|
| Δ`dt_us` | **+1.3 ± 154.3 µs** (upper +155.6) |
| Δ`cpu_gpu_us` | −4.2 ± 139.1 µs |
| game speed | 51.12 % in both arms |
| `tex_hits` | +1 434 a frame |
| key misses | 1 662 → 274 (−84 %) |
| `texfast_rec` | −1 192 a frame |

6. **Audit (item 9):** recount CONFIRMED to 1e-9 (bootstrap 95 % [−143; +143]); protocol HOLDS (MAJOR-1: the +300 arming
   floor was set in the lead's brief and recorded later under the agent's name); closure holds with wording fixes: the
   gain is ≤ 0.16 ms at 2SE (post-hoc draw-adjusted −98 ± 105 µs, not a verdict); the census's miss price (~497 ns) was
   inflated 2–20× (latency displacement in memory-bound code + the census's own pollution); the 8-way overhead is
   secondary; the "not on the critical path" candidate is refuted (`cpu_gpu_us` 31.9 of 32.6 ms).

## 2. Code

`5e8e1d2` (emulator, knob default 0 = today's direct memo byte-for-byte): `descriptors.cpp` (`ResolveTextureWith`,
`RebindImages` placement check), `renderMemo.h` (set lines inline), new `renderMemo8.h`, `frameStats.h`, `videoOut.cpp`,
`gates.h`/`gates.cpp` (`Knob::TexMemo8`, LAST). Nothing under `src/graphics/shader/**`.

## 3. Runs

| tag | seal | what | outcome |
|---|---|---|---|
| `vfy121` | 01 | 240 s, 4 arms `texmemo8=2|1|0|3` with `texfastcheck=1`, video | PASS |
| `shp121` | 02 | 300 s, pinned, ABBA `texmemo8=1|0` | NO_SHIP, Δ +1.3 ± 154.3 µs |

(Before `vfy121` four chain requests stopped at the gate without a game launch: a foreign busy process 13:17–16:05, a
leftover agent `tail -F` whose command line held `mutlib`, a browser spike at the second check, and the lead's own
command line containing `mutlib`; the 16:31 attempt had already installed `0bd21ec2` before refusing.)

## 4. Proved, and not proved

**Proved (Sky Garden):** an 8-way memo of the same 4 096 entries is correct (0 mismatches against a fresh full
resolution over ~3.1 M checks) and removes 84 % of the key misses — and that saves less than 0.16 ms a frame (2SE),
point estimate 0. A census price measured inside a heavily instrumented arm is not a wall price. **Not proved:** the
exact split between census inflation and 8-way overhead; any gain in the NEW BDA regime by ABBA (the only NEW evidence
is `vfy121`, flat, not ABBA); another scene.

## 5. Traps (disclosed)

Rule constants that differ from an accepted decision must reach ROADMAP before the agent brief (MAJOR-1); agents leave
`tail -F` monitors that block the chain gate; a command line containing `mutlib` blocks the name guard — keep chain
command lines plain; a filled seal constant can leave mutants unkilled — test such branches by calling the function
with the constant as an argument; the arm switch lands at position 89 of the outgoing block (not 0–2).

## 6. Next

`docs/next-session-122.md`: the bottleneck map across scenes through causal probes — one measurement-only burn knob per
thread, a two-dose ABBA per scene, `lite` classification; the map picks the next lever.
