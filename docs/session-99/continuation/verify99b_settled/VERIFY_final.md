# Independent settled scorer VERIFY — final focused recheck

Verdict: **PASS for the reviewed frozen scorer and sealed-rule implementation**. Both findings from VERIFY_initial.md are corrected. Initial FAIL report/results remain unchanged. This admits the instrument/scorer to the next planned run; it does not admit a game run or provide a B/M3 result.

Frozen SHA256 verified before recheck:

- settled99.py: 383e2ff3452557069bc94f7effe8b6401a5c6b2959518b241771adaab9c87bdc
- test_settled99.py: 812b142a9793009b6dd998566b51a64556dcf2980a618f48de913c0eb9a8a93c
- pred/02_settled_bindings.md (unchanged,13461 bytes): 1d1ebf286869ab59944fe135fc5c69d1315d4c61667b6c3dd2ab3ca14839724c

1. Source selected-row replay: settled99.py:419-424 now compares the complete selector after JSON normalization, including block-key conversion and pair tuple/array conversion. Independently reran the exact original mutation through an actual synthetic pilot evaluation plus real raw replay, without mocking evaluate: untampered serialized source passes; replacing only row_ranges with {"4":[1,29]} and pinning its exact new JSON hash fails explicitly. No changed threshold, geometry or budget rule is involved.
2. Original failures remain visible: settled99.py:473-475 preserves all three original area split/pair matching/work controls and the combined old verdict. The same synthetic fixture produces three old controls, its original WORK FAIL and area INVALID remain in the output, while the independently settled pilot remains ENGINEERING_COMPLETE/LOCK and publishes no endpoint. This is diagnostic separation, not relabeling the old failure.
3. Relevant author regression tests pass2/2. Independent focused recheck assertions pass8/8 (recheck.py, recheck_results.json); actual inherited helpers were exercised and temporary artifacts stayed under this directory. The earlier full suite19/19 and finite assertions remain documented in VERIFY_initial.md. No broad repeated audit was run.

All unaffected assertions and practical limits from VERIFY_initial.md remain applicable. No game, build, new gameplay data, historical cal99a endpoint, raw overwrite or global G/R1 closure was produced. Old cal99a stays INVALID. Measurement correctness, timing, work/area admission, source pinning before a real launch and survival still require the prescribed executor/run evidence.
