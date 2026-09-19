# Independent focused VERIFY — pred04 / settled99_gc

**Final verdict: PASS after the root's runtime-marker parser correction.** The original frozen scorer had one real integration defect; that failure and the exact original scorer are retained below. No game or build was run and no production source/scorer/test/rule file was edited by this reviewer.

## Reviewed freeze

- `pred/04_gc_audit.md`: 7,835 bytes, SHA256 `a93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b` (unchanged).
- Final `settled99_gc.py`: SHA256 `be2a9a317fded5ee3ee6b421312d60e3fb6e9cd22c643eb3b7ec89a1258adef6`.
- Final `test_settled99_gc.py`: SHA256 `c1bde31f312f08f116e3ea08f44923c9c5a636118e45d9456eaad6b3ae1d483e`.
- Previously verified `settled99.py`: SHA256 `383e2ff3452557069bc94f7effe8b6401a5c6b2959518b241771adaab9c87bdc`.
- Required new binary pin in rule/scorer: `34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f`. This review verifies agreement of the pins, not installation by the launch executor.

Byte snapshots and sizes/hashes are in `frozen/` and `frozen_hashes.json`. The originally submitted scorer was `6d242596de76023c1dbdcab9a58bfbe5ed690ce340734e972b6115aa60c2f804`; original tests were `fcbab5e0fe50c0d8a6f8c6c06ca45a590cd72ff2351e8d8e8836cbbf2065410a`.

## Actual defect found and closed

`C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/cache/textureCache.cpp:3268` emits `BindFloorGcAudit: mode1` with no space. The original `settled99_gc.py:150` regex required a space between `mode` and the number. A correct real log was therefore guaranteed to fail protocol admission. The old test fixture inserted a space and hid the mismatch.

The root changed the regex to `mode\s*(\d+)\b` and the fixture to the real C++ string. C++, binary and sealed pred04 were unchanged. The independent reproduction obtains the marker directly from the actual C++ format string. The exact old scorer is reconstructed by reversing only that regex correction and verified against its original SHA256 before execution. On the same otherwise-valid synthetic log:

- Original scorer returns exactly `log mode/pin evidence missing/wrong` (`actual_marker_protocol_failure.json`).
- Fixed scorer returns no protocol errors (`actual_marker_protocol_fixed.json`).

This is a parser repair to implement pred04's specified `mode1`, not a change of controls or interpretation of collected game data.

## Focused review results

1. **Required fields / complete log.** `settled99_gc.py:27–28` adds all five IGC fields to REQUIRED. `evaluate:476` scans the full raw log, then `analyze:271–288` tests missing fields, nonnegative values, positive total checks, whole-log zero bad/critical/evict, and positive hold in every retained armed block. Violations before the endpoint window are therefore not hidden by selection. The positive-hold check uses retained rows, which is conservative against a vacuous block with observations only outside its endpoint sample.

2. **Image proxy replacement is explicit and narrow.** `evaluate:481–486` preserves full original reversibility text, extracts only `R6`/`R6'` into the separate reported-image-proxy dictionary, and adds every remaining result to deciding technical controls. Original R6/R6' calculations are unchanged in `full_reversibility:369`. Buffer `R7` and `R7'` remain required. Direct IGC violations veto regardless of low image-birth counts.

3. **Pins, environment and runtime evidence.** `protocol:90–110` enforces the new binary/pred pins and env audit=1, CPU=1, latch=1, clear=0 and previous environment constraints. ImageLife env presence is rejected even with value 0; raw and stdout ImageLife output also reject (:134, :189). Actual GC runtime evidence is required (:150, :177) and now parses the C++ string.

4. **Fresh campaign and no old replay.** `identity:38` accepts only a4/a5/a6, c1/c2/c3 and new confirmations with existing bounded entry suffixes. a1/a2/a3 including entry suffixes reject before scoring. `source_check:402–428` requires a4/c1 to start at 17800 with no source; next pilots retain immediate-predecessor/TUNE source chains and confirmations require LOCK. Existing exact launch-source pin, raw hash/identity, replay and normalized selection comparison remain in :411–442. `recommendation:389` exhausts at a6/c3, preserving three settings per branch.

5. **Unchanged prior machinery.** The diff against verified settled99.py leaves selection geometry, retained indices, balanced pairing, strict work/area/C5/C9 limits, CPU endpoints, legacy checks, retry provenance, video-related legacy controls, and source replay mechanics unchanged except the explicitly reviewed reset ordinals/budget and new pins. Admission still requires all technical controls and no protocol errors (:500); confirmation additionally requires all strict controls (:506). Mechanics fixtures remain NOT_MEASUREMENT and cannot produce admitted B endpoints.

## Independent executions

`verify_cases.py` records **40 expected outcomes confirmed** in `independent_results.json`. It uses the existing synthetic fixture as input scaffolding, applies reviewer-selected mutations, and executes the actual scorer and real legacy helper pipeline; these are not game results.

- High image births: all technical/strict controls pass and pilot logic reaches LOCK, while original image `R6=false`, `R6'=false` and FAIL text stay visible (`high_birth_mechanics.json`). Fixture remains mechanics-only.
- Bad clock, critical override and held eviction at n=1813 (outside retained endpoint rows), each with zero image births: analysis rejects and full pipeline returns INVESTIGATE.
- Missing and negative values for each of the five fields on an early row reject.
- Zero checks globally, and zero hold in one retained armed block, reject.
- High buffer births with zero image births: both deciding R7 and R7' fail and full pipeline returns INVESTIGATE.
- Old a1/a2/a3 identities and entry suffixes reject; new branch resets require the new budget and reject an old source.
- Audit env missing/wrong and ImageLife env value0 reject.
- Actual C++ runtime marker reproduces the original failure and passes on the final frozen parser.

No author FACTS, diagnostic output or author interpretation was read outside the explicitly requested sealed pred04. This verifies the targeted new scorer behavior and integration with the previously reviewed scorer; it does not establish GC completeness beyond the declared current-slice subset, calibrate a burn, admit a pilot, close M3/G/R1, or authorize unreviewed data repairs.
