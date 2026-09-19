# Independent sealed acceptance: bf99g (a)

PASS: bf99g is ADMITTED_SETTLED_MEASUREMENT under immutable pred05. This is a CPU diagnostic only; no paired a/c verdict yet, global M3 remains GAP and G/R1 unlicensed. No source code, rule, raw input, or existing score was edited; no build/game was launched.

Independent computation is `recount.py`: separate raw parser, original GateArm indices, fixed idx60..88, complete original quartets only, no re-pairing/reuse. The existing scorer was replayed separately for all inherited technical controls and immutable source04/AA provenance; its status was not used as a substitute for the independent population/endpoint calculation.

| Claim | Evidence (paths relative to C:/kyty/s99) | Independent result |
|---|---|---|
| Seal/source pins match | pred/05_observer_separation.md:32; bf99g.json:63 | pred05 fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0; source artifact 9f021e8bcc080f03a3309c851629f01c49b7f54868dd75b2a62b6ee28e175e8e; source scorer be2a9a317fded5ee3ee6b421312d60e3fb6e9cd22c643eb3b7ec89a1258adef6; AA artifact 3c8c8ed44a93ad1d9295016e0e5cdc7602f142d6be443ad6863e292b1068a55e |
| Identity, continuity, survival | log_bf99g.txt:18298; bf99g.json:341; bf99g_independent.json:15 | main/draw/x each18199 rows n2..18200, no gap/duplicate/order/arm error; 183 GateArm blocks; hold900.3s, raw913.338114s; no fatal marker |
| Fixed comparable population | log_bf99g.txt:517665 and :2686465; bf99g_independent.json:31 | blocks4..179; 88 disjoint pairs,44 AB/44 BA,2552 rows/arm. Initial quartet and incomplete terminal quartet wholly excluded; no internal exclusions |
| Work and area PASS | same raw rows; bf99g_independent.json:35 | draws5058.672805643→5046.251959248; work−0.2455356745% (<0.5%); area2007.777547070→2007.797586639, +0.0009980971% (<1%); match88/88 with original per-pair0.5% band; C5 PASS |
| C9 PASS | same raw rows; bf99g_independent.json:44 | dt_U50153.817006270/dt_A49968.867946708us; mismatch0.3687636766% (<=3%) |
| Falls/latch PASS | log_bf99g.txt:479140; bf99g_independent.json:24 | 45 completed falling edges;91 bf_edge, all idx0; required>=30 falls and>=30pairs |
| CPU observer and direct GC PASS | log_bf99g.txt:16542 and :479162; bf99g_independent.json:75 | CPU burn149439288233ns,42402603samples,bad0; wall145002647934ns; GC checks145873/hold65404/bad0/critical0/evict0; every deciding armed block hold>=229 |
| Integrity and buffer recovery PASS | bf99g_independent.json:510 | mixed/defer_force/trig_*/dlskip/clr_skip/skip_drop/gm_ops totals0; buffer recovery medians2/4 <=50. Image birth proxies retain FAIL54/64 (>50), reported-only under pred04; they are not relabelled PASS |
| All shared technical requirements pass on fresh replay | replay_bf99g.json:27 |43/43 technical,6/6 strict, errors[]; unchanged pred04 source replays LOCK17800; AA is revalidated from raw, not accepted from its label |
| Endpoint independently matches | bf99g_independent.json:531 | B_cpu=30.049869086206897ms; B_wall compatibility=30.596798362068967ms. Formula subtracts bf_burn_cpu_ns, not wall burn, from cpu_gpu_us−spin_gpu_us. No observer residual is silently subtracted |

Retained armed means: CPU burn18.298962102ms, wall17.759118371ms, difference+0.539843732ms; query indicator1.750204699ms. Reported xover/xover_acb/defer totals92 each are not zero or proof of cross-queue correctness.

A/A independently has22 balanced pairs,work+0.0348287818%,area+0.0136191459%,dt mismatch0.1029276103%,match22/22; actual floor/burn/edges0 (12 label-only pseudo falls are not floor falls). Independent source eng99a4 has22pairs,12 actual falls,work−0.0236501815%,area−0.0151021327%,dt mismatch0.0042254799%,match22/22. Neither is a B observation.

Historical whole-window criterion3 remains INVALID (work−1.491% in replay_bf99g.json); it is displayed separately as pred02 requires, not substituted for the predeclared settled deciding population. Image R6/R6' FAIL54/64 likewise remains visible. No correctness, regression, or cause claim follows from admission.

Raw SHA256: log_bf99g.txt a9422bebb226a27771c81efd5c54f37e52312a9ccd28db7dceedada0de4560f8; stdout_bf99g.txt1499066fbdbc1936699c2a346db97144e9aa9a4be08856fe009e429cb262734e; bf99g.json f127acbd3a8021bfabec03a566901a7ddffb4ca811a3309f72a0ced8437915d5. The fresh replay checks unchanged raw before/after. Pred01 hash8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d; pred02 hash1d1ebf286869ab59944fe135fc5c69d1315d4c61667b6c3dd2ab3ca14839724c; pred04 hasha93f4b6b1068cb34b06d02301d5c35f09483ef60f546f7669b03e193aeee611b. These seals were read, not changed.

All host analysis subprocesses launched by this reviewer have finished. c was not checked and requires its own data and verification.
