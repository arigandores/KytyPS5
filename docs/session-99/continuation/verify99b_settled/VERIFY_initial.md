# Independent settled scorer VERIFY — first frozen revision

Scope: sealed pred/02 plus settled99.py, its tests and dependencies needed to understand the new paths. No FACTS, author analysis, draft or old cal99a endpoint read/computation. No game/build or old raw mutation. All reviewer outputs are in this directory.

Verdict: **FAIL pending one reproduced source-replay CODE correction**. Author suite 19/19 passes; independent focused cases expose the missing selected-row replay comparison. The prior cal99a remains INVALID; no new game evidence or B was used. All endpoint numbers in reviewer cases are synthetic fixtures only.

Hashes SHA256 at frozen review:

- pred/02_settled_bindings.md, 13461 bytes: 1d1ebf286869ab59944fe135fc5c69d1315d4c61667b6c3dd2ab3ca14839724c
- settled99.py: 1ab9a9463974ff2127cb131328b0e05d02453b410827ea86d380113462dd3eb3
- test_settled99.py: c4ed29847da147cf5f6d14f1e86757f591b0c4567a4d1ce78d79df6d7ae1aeb2

## Reproduced defect

settled99.py:416-417 compares replay metrics/technical/strict/decision, but not selection. A synthetic pilot was evaluated through the actual pipeline and inherited helpers, producing ENGINEERING_COMPLETE/LOCK. Its JSON replay passed. Only selection.row_ranges was then changed to {"4":[1,29]}, its exact JSON SHA pinned in confirmation metadata, and source_check still returned errors=[]. This violates sealed section 4's requirement to store selected rows and independently reproduce the source from raw. Exact JSON hashing proves which bytes were pinned, not that those bytes accurately describe selection. Fix should compare JSON-normalized selection/row_ranges, accounting for dict key conversion to strings. See independent_cases.py and independent_results.json.

## Other assertions

1. Selector 195-226 matches the fixed original quartets: on 82-block fixture chosen blocks are exactly4..79, pairs(4,5)..(78,79), each29 rows idx60..88. Original numbering retained; endpoint quartets omitted together; no pair reuse. Whole internal missing block fails via inherited EDGE and missing individual internal row via INTERNAL_ROWS_COMPLETE.
2. FULL_ROW_IDENTITY260-267 checks all rows, including block0 excluded from deciding geometry. Independent arm/blk corruption on1801 fails; missing early observer field fails FULL_SCHEMA; early CPU leakage fails DARK.
3. population229-257 uses attachment-weighted raw rt_kpx/rt_att, identical fixed retained pair sets for split/work/C5/C9 and endpoints. Per-pair area tolerance is0.5 percent, matching area_verdict.py; aggregate split<1%, match>=90%, work<0.5%, C5<=2%, C9<=3%.
4. analyze276-333 rejects negative CPU fields, any bad pair, missing CPU sum/count, aggregate CPU excess beyond1000ns/retained armed row, and leakage outside old T* structure/0.001 ratio. C8 and B use CPU burn; wall endpoint is separately named compatibility. Synthetic CPU22ms/wall18ms proves clocks stay distinct; no invented probe correction.
5. pilot path never returns endpoints. Work/area/C5/C9 are strict diagnostics and do not turn technical pilot failure into success. dt<=1% with strict failure branches CAUSAL_TEST, preventing burn tuning to hide work mismatch. Ties round away from zero; opposite sign midpoint; max3 settings, <=30000 no clamp.
6. source_check384-421 correctly requires a preceding ENGINEERING_COMPLETE pilot, correct instrument/round, exact launch tag/hash, source raw/meta/stdout hash set, TUNE for next pilot and LOCK for confirmation, exact budget and re-evaluation. Changed raw bytes are rejected. Selected rows omitted from replay comparison is the single reproduced admission-provenance gap.
7. protocol84-192 verifies new binary/seal/baseline gates, positional metadata env settings, period90/start1800 ABBA and raw arm announcements, stream completeness/duplicates, CPU/latch/clear/pin evidence, both log and stdout safety markers, phase-specific hold and one surviving attempt, necessary raw duration consistency. Baseline gates pins fslean=0 and m4baton=0.
8. entry_history45-81 enforces suffix bound1/2, sole failed predecessor attempt, no GateArm in predecessor raw, unchanged schedule/arms/binary/gates/hold/cmdline/rule and all KYTY config except recording destination. Missing predecessor artifacts fail; predecessor raw/stdout/meta hashes are recorded.
9. full_reversibility351-360 keeps inherited R checks and required edge minimum8/30; evaluate457-469 retains old technical C3'/C6'/C7 independently of new settled population. legacy_state restores mutable module state. Original old control PASS/FAIL lines and area INVALID are retained. Reporting limitation: detailed original criterion3 raw area/work/pair control lines are filtered out, leaving raw aggregate values and combined area verdict.
10. evaluate429-483 rejects changed seal/root/raw inputs, admits confirmation only with all technical+strict controls, and exposes endpoints only on admitted measurement. --out525 uses exclusive x create; main reads inputs and inherited area regeneration uses a temporary new CSV. No existing raw/CSV overwritten. --combine re-evaluates input tags and leaves global M3 GAP/G/R1 unlicensed; no old addend or route closure.

## Practical limits

This is finite static/synthetic verification, not proof of emulator operation, actual prelaunch chronology, hardware clock accuracy, hold survival or pilot admission. The source JSON metadata is the record of launch pinning; runtime executor must actually freeze/pin it before launch. No launcher/build or historical13-scorer full audit was attempted. The old area helper regenerates a temporary raw series; new selection never reads pre-existing CSV. Shared trace atomics can straddle rows as documented by the sealed rule. The normal stdout field completeness requirement is applied to raw trace streams; stdout is independently required and scanned for forbidden markers.
