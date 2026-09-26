# History rewrite of 2026-09-26 (personal identifiers removed before publishing)

The 330 commits on `merge-upstream` after `fork/merge-upstream` (`244d7ad`) were rewritten locally with `git filter-repo`
before the first push since 2026-09-15: the local Windows user name in paths became `<user>`, the launcher user name
`Player`, name fragments `<name>`/`<surname>`, the name of another application `<foreign app>`. Source code under `src/`
is byte-identical; 184 files of docs/harness copies differ in 340 lines. Consequences: (1) commit hashes quoted in
`docs/ROADMAP.md`, the session reports and the local harness logs are the OLD hashes — this table maps them; (2) the
sha256 values in the archived `SEALS*.txt` refer to the unscrubbed originals kept under the local harness roots
(`C:/kyty/s1NN/`), so a scrubbed archived copy may not match its sealed hash.

| old | new | subject |
|---|---|---|
| `013b81aee6c6` | `ab1c207380a7` | Rewrite docs/next-session-100.md as the session-100 brief |
| `016722cdc25a` | `30c6ddf764f3` | Session 110: stl110 NOT_ADMITTED (STALL_SYNC counted startup stalls before the first row - |
| `01f0c791780f` | `c501d4076d5a` | Session 108: powered guard failed its rule (cs_sync_new 6 vs 3+2) - cspfam default back to |
| `0310cbb4c2a4` | `06887762290a` | s120: measurement build - r1cen (R1 texture-memo census), r2cen (R2 stage image-block cens |
| `04a21f0de762` | `1160e195d2c5` | Session 117: ROADMAP item 7 - full mutlib v4.1 --no-memo run on sealed ttl114b takes 42.1  |
| `04a64bee775e` | `26dfceb82073` | Session 113: vbn113c INVESTIGATE (OLD at the first entry: 13.8 M checks, 0 misses, 3 races |
| `04ccab50c69a` | `58d09950f346` | Session 113: seal pred/01e_vbn113e (c082d54a) - verify of bdanarrow=2 in a forced OLD regi |
| `0522971649fa` | `0df0f640e5c3` | Session 113: ROADMAP item 10 - the session audit (recount CONFIRMED, protocol HOLDS, code  |
| `06ce5344e59a` | `872c7410cf09` | Session 109: seal pred/01_ent109.md (e2627de0) - powered guard as an ABBA of entries; scor |
| `06eef00b0cc4` | `fe774bc080f1` | Session 104: record the executor's decisions BEFORE acting - the vblank plateau does not h |
| `0776f6a41294` | `1a085a047a2b` | Session 110: shp110 SHIP - knob cspfree default 1 (d mean dt -418.7 us at the pin, 2SE 135 |
| `083a73d7a7fc` | `65fcbf9ba661` | Session 107: dab107 KEEP dabatch=8 (dabatch=2 worse: d dt +281 us) |
| `096dcfcd4ae8` | `ee488bfde5d6` | s120 item 7: seal 01 cen120 verdict - R1 OPEN 658.8 us (w8), package R OPEN 1093.9, R2 NOT |
| `09b65e7c4776` | `0ac5a22f93ee` | Session 117: ROADMAP item 1 - order; full --no-memo v4.1 timing on sealed ttl114b first; f |
| `09da5dea7564` | `fded60eb2b06` | Session 117: ROADMAP item 11 - pre-seal check of spn117 (no blocker): walker-fit rule fixe |
| `0a106f254b47` | `55636ad37c06` | s121 seal 01 (vfy121): pred f681d4db, verify scorer vfy121 with 444 fixtures and 297 mutan |
| `0beedaf4f409` | `c875fd46449e` | ROADMAP: session 115 item 2 - build (ring fix + titleasync default 1) and seal 01 chk115 d |
| `0d35faa40af9` | `6b30d363e0ce` | Session 102: record the M5 operationalisation in ROADMAP and seal pred/01, BEFORE the capt |
| `0dea739b1240` | `0197d3fbeceb` | Session 113: video check check113 (from check112 by make_check113; 31/31 mutants killed) a |
| `0e1013cc1392` | `d74f63b9a5a1` | Session 116: seal pred/01_obs116 - clean GuestGpu phase split on d3a981a2 (mutsite+pathlap |
| `0eeefd528c61` | `c5b45f25d3cc` | Session 104: record the route-A decision (kill-or-go stage 1 with a written rule) and the  |
| `10e8a98a684c` | `471c07787dbc` | Session 102: stamp the session commit hash into the report |
| `11ae1da0d046` | `9baada38b119` | Session 115: ROADMAP item 11 - session audit: seal 01 PASS recount CONFIRMED; MAJOR P1 (a  |
| `11e4eaa90f52` | `6429862bdccd` | Session 103: stamp the session commit hash into the report |
| `130744bbc1c3` | `8aa2a110f170` | Session 102: env-flag value parsing, knob dabatch, host key KYTY_DMA_LAYOUT, M5 recompile  |
| `13181a8b03dc` | `8a50b5706773` | s120 seal 01 (cen120): pred d20cd3de, scorers rpk120/spc120 with fixtures and mutants, mut |
| `1380150f3d07` | `a71c6199b59c` | Session 114: ROADMAP item 5 - build 916f6489; design of seal 01 ctl114 (stall control) and |
| `14db6c789828` | `5665e794f773` | Session 103: BVH loop cap (default ON for 380bb9d6), 15 translator env sites read their va |
| `14f08b24ed36` | `99f2797742d7` | Session 118: stage 4 part 2 instruments (measurement only, defaults unchanged) - spine car |
| `1713c6dc233a` | `86ab563f3887` | Session 114: titleasync back to default 0 in source (ROADMAP item 15; installed build 916f |
| `175b873fec74` | `2b3a39e3982a` | Session 114: titleasync default 1 (seal 02b SHIP, ROADMAP item 9); KYTY_PREPARE_HOLD_MS an |
| `17baed5a0edd` | `7b44e66ed35e` | Session 117: seal 01 spn117 (shadow spine K5/K1 observation; build 3cde1af8; 101 fixtures, |
| `1918dd6eeb87` | `5e6e0cee24e2` | Session 113: ROADMAP item 12 - the user's correction: the fast mutation harness now, befor |
| `1b31ae268a19` | `8a0311184930` | Session 117 close: ROADMAP item 15 (audit: recount CONFIRMED; MAJOR - spine price a self-t |
| `1c6eb389ec45` | `b05204bb945b` | Session 109: seal pred/01b_vfy109 (f626da41), 02_ent109b (bf8adcd1), 03_frf109 (8f44107f); |
| `1d9dcf0c7778` | `012f5243ed9c` | Session 110: ROADMAP records before action (stall-duration counters and CsStall lines; the |
| `1e1e4acc069d` | `01b8b23f20e2` | Session 107: seal pred/02_dabatch2.md, scorer dab107.py with five-branch non-draft fixture |
| `1f488f77832a` | `48f54bc25c0d` | Session 111: ROADMAP records before action (obs111 observation rule; daslot protocol writt |
| `1fc0e1500fc7` | `389f88559de6` | Session 102: seal the M5 addendum and the two candidate pre-registrations BEFORE any run |
| `201ca030d006` | `a99ed40f2f87` | Session 118: seal 01 spk118 (build 321175ab) and its mutlib v4.1 tally |
| `20e7b31e3f72` | `f3c4dc283db0` | Session 109: ROADMAP records before code - knob cspfree (walker compute prefetch without t |
| `22d5ad481033` | `095bb3cc73a4` | Session 108: ROADMAP item 7 - audit (guard without power) and the powered guard test rule, |
| `22d90a368867` | `65bb5e0693fe` | Session 114: ROADMAP item 8 - seal 02 ttl114 NOT_ADMITTED (TITLE_ARMED: arm-1 wall 21.4 us |
| `276437fd6bc2` | `b27adc64db94` | Session 106: ROADMAP records before action (dwk104 re-analysis, KYTY_GPU_WALL instrument,  |
| `27aa877a585a` | `bf2c184d43b2` | Session 111: obs111 BUILD_DASLOT (tag 1 232.6 us/flip, 98.5 %); vds111 NOT_ADMITTED (gate  |
| `27b492de254f` | `49dd0eb0953a` | Session 103: record the executor's decisions (BVH loop cap default ON, entry-series rule,  |
| `296d92c34afa` | `87d5d40487e0` | ROADMAP: session 116 item 3 - obs116 pre-seal check (BLOCKER: emit identity tolerance 4 fa |
| `2f1ca0491e24` | `a9e3d7be3740` | ROADMAP s122 item 1: order and scope (burn-knob scene bottleneck map), recorded before any |
| `3086142fbbf1` | `2921e261f2af` | ROADMAP s120 items 4 (member consequences) and 6 (scorers before the seal: row-skew tolera |
| `30d33db41401` | `99162771e45b` | Session 110: stl110b PASS - cspfree adds no dispatch-time stall duration (D 10.9 vs 19.6 m |
| `328d4cc171ab` | `903a8cc73b68` | Session 114: ROADMAP item 14 - seal 03b KEEP_1 (boot fatal identical at titleasync 0 and 1 |
| `36522d228e31` | `8cd8222aecf1` | Session 114: knob titleasync (ROADMAP item 2, default 0) - UpdateTitle posts the title to  |
| `36c8350ca042` | `f604adc2fc57` | Session 117: spine applies R_DISPATCH_RESET (CommandProcessor::Reset) on the shadow proces |
| `37aa33f7d046` | `8d2a2f8f6af7` | Session 113: ROADMAP item 16 - a lost B1 edge fixture in the sealed test_vbn113d (prefix a |
| `37e0de19997f` | `1f5ac038da74` | Session 113: knob bdanarrow - BDA region stamps invalidated per registered buffer instead  |
| `38a5f300b6b1` | `b8f549312d75` | Session 114 close docs: local-session-114 (FACTS), next-session-115 plan (ring ownership f |
| `38bfda2f6517` | `a3beab8bbfc8` | Session 105: candidate 1 dawalklead=2 KEEP (dt -61 us, t -1.06); record the route-A M3.1 b |
| `38d8f86032d6` | `aff2c6aaadfb` | Session 111: vds111b GO, shp111 SHIP - knob daslot default 1 (d mean dt -230.7 us on frame |
| `38dd1af8ee1d` | `73742acc6ca0` | Session 114 closed (ROADMAP item 16: mutlib v3 verdict moves to session 115); session 115  |
| `38fe0378991b` | `bec969e696f7` | Session 113: ROADMAP item 14 - the exact knob-2 check design (stamp read under the region  |
| `391f8d75fd97` | `f8500cbb0579` | Session 112: seal pred/01_vdg112 (e4029a49) - verify of daguard with arm transitions; scor |
| `3931e6579b7f` | `43d950ba7e2f` | Session 113: census of 579 archived runs (OLD 289 / NEW 221): within a build OLD is not sl |
| `3aaddb6014e4` | `a17be8af1d51` | Session 119: seal 01 g2_119 (G2 re-measure at W = 2 on d3a981a2) and its mutlib v4.1 tally |
| `3ac7ccdc101e` | `638bd87e7d4b` | Complete session 99 bindings-only measurements and visual control |
| `3c988bb7ebf2` | `9935b00c2e7a` | Session 108: ROADMAP item 6 - new build fc78c564 video PASS; desert smoke rule recorded be |
| `3cb0786bed79` | `8188f101484e` | Session 115: mutants of sealed check115 104/104, controls 3/3 (mutlib v3 frozen, --no-memo |
| `3cc53a210c3f` | `3f3890b1a554` | Session 108: ROADMAP records before action (knob cspfam, sync-compile guard, run and admis |
| `3d54b85c1918` | `43ca99e71334` | ROADMAP: session 115 item 5 - pre-seal check of chk115 (BLOCKER: the control never prints  |
| `3d8af4cb7dde` | `6094e771d2d7` | Session 110: stall duration on the dispatch - cs_sync_new_us / cs_sync_wait_us and a CsSta |
| `3db48c15c9e9` | `b68df1ff07b8` | Session 114: seal pred/03b_bootctl114 - control boots boot114b (default 1) and boot114c (t |
| `418e491ef297` | `3ce2018bd89a` | Session 105: seal addendum 03 (ctx105 scorer whitelist defect) BEFORE re-scoring abb105 |
| `43c1633a3ae3` | `b61fa6f74995` | Session 113: seal pred/02_shn113 (75f34c69) - ABBA bdanarrow=0/1 in a forced OLD regime on |
| `447d089f5fec` | `809f57d5d035` | Session 114: mutants of sealed bootctl114 25/25 killed, controls 3/3 |
| `44f01b4175b8` | `da1e8e5959bc` | Session 104: ship dawalk=1 (PM4 look-ahead walk off the GuestGpu thread) as the default |
| `460a61a8af6c` | `0b0a5b07f84c` | Session 112: vdg112 GO (61.5 M checks, 0 bad), net112 KEEP daslot=1 - session 111's gain a |
| `46989bbd5fdd` | `8ca40da91fcb` | Session 113: ROADMAP item 21 - seal 02 shn113 KEEP bdanarrow=0 (d dt -83.2 +- 68.0 us, S1  |
| `4763c49c01c5` | `302ca1b09fa3` | Session 105: route A M3.1 - the command buffer names its owner and tick; knob ctxtick (def |
| `482a8245af65` | `35d3c65cda64` | Session 117: seal 01r spn117 re-issued before any run (LF line endings; mutlib refused CRL |
| `498d17f85e8d` | `7a35788e5298` | Session 114: mutants of sealed ttl114 342/342 killed, controls 3/3 survive |
| `49a13e758840` | `2d25a4d7d487` | Session 106: seal pred/01_gwall.md (432e3c5b), scorer gw106.py with fixtures, port s106_po |
| `4a44d0f3e800` | `3d222690bc59` | Session 113: shn113 draft archived (235 fixture cases, 310/310 mutants, built for 94362eae |
| `4a87d30019af` | `d4171a24a36b` | Session 103: the BVH loop cap (0 entry hangs in 67, series NOT ACCEPTED on A3, kept ON), M |
| `4bfaf5c395a8` | `2f7f77287433` | Session 114: ROADMAP item 4 - titleasync review: C1 MAJOR (startup park lost -> concurrent |
| `4d4a11388724` | `47ec17fd23d4` | s120: designs, adversarial reviews and design120.md synthesis (docs only) |
| `4ed221984933` | `5007deed49fc` | Session 103: seal the M5' protocol (pred/02) BEFORE any timing |
| `503a8bf08ac4` | `6d0b2a8f0732` | Session 115: the presentation record ring keeps one producer - no main-thread present duri |
| `505c589b7a54` | `4cbc951d8132` | Session 113: ROADMAP item 5 - offline pre-run audit (knob 1 not refuted; MAJOR: races infl |
| `509fff5ff1af` | `ad961f8d07b1` | Session 116 close: FACTS (local-session-116), plan of session 117 (v4.1 --no-memo timing,  |
| `514806388217` | `c0d7d5dec628` | Session 101: stamp the session commit hash into the report |
| `530f6aaa57fc` | `c32de0b74499` | s121 item 2: texmemo8 design accepted (8-way texture memo, verify and positive-control mod |
| `5389e16dd082` | `86958cc089cd` | s121 item 6: seal 01 vfy121 PASS (0 mismatches on ~1.55M verified gained hits, 0 video gli |
| `55188780a7d3` | `0abbd4eb0666` | Session 102: seal addendum 07 (one technical retry of the M5 capture, KYTY_RECORD_THREAD=0 |
| `55a7916340b0` | `5ddb3c367470` | Session 113: seal pred/01c_vbn113c - OLD verify of bdanarrow mode 2, relaunched until OLD  |
| `5609d472de64` | `2b3c38a61055` | Session 111 close: audit addendum pred/04 (83358a9c), FACTS, ROADMAP (item 7, addition, de |
| `56a4b4fae2dd` | `25b6e18e4d85` | Session 113: exact bdanarrow knob-2 check - the region stamp is read under the region lock |
| `5758a67410bf` | `c8b05eca5b49` | Session 114: ROADMAP item 10 - deterministic boot check: KYTY_PREPARE_HOLD_MS (main thread |
| `57701065d0c4` | `884b65791df7` | Session 109: knob cspfree - the walker's compute prefetch without m_mutex on a (source, sp |
| `593aa7fefc34` | `b18f8d860537` | Session 113 close: bdanarrow verified (forced OLD, 0 misses) and kept at 0 (d dt -83.2 +-  |
| `5a8970ce3312` | `d580777ddb88` | Session 113: ROADMAP records before action - the BDA regime mechanism (global stamp invali |
| `5c6eea303dbc` | `6d9c33a6a77e` | s120 item 4: measurement build design (r1cen, r2cen, spcen), verdict rules at 0.5 ms net,  |
| `5e8e1d289e94` | `507b65983eda` | s121: knob texmemo8 - 8-way texture memo (512 sets x 8 ways of the same 4096 entries) with |
| `600b500824dc` | `852bf55ae3f6` | Session 105 close: audit addendum, FACTS, ROADMAP decision after 105, plan 106 |
| `600ca26452f7` | `ae6d6e6e44d9` | Session 109: ent109 FAIL (S_A 12, S_B 34) - prefetch skip per shader family closed (v1 and |
| `60a60bfe81f0` | `b9e568b7c1c1` | s121 item 7: seal-02 fixture-suite repair (two survivors left by the filled seal constants |
| `60bf3d905048` | `0e3522c3bc67` | Session 108 close: audit addendum (guard without power), powered guard -> cspfam rollback, |
| `623009f88b27` | `789a22fbd870` | Session 113: priority-operation stall instrument (ROADMAP item 18, no behaviour change) -  |
| `6339dc897407` | `c0d6a360baeb` | ROADMAP s121 item 1: order and scope (R1 prototype texmemo8 with verify mode, one sealed A |
| `6408ee2beb8f` | `f79f8d834e14` | ROADMAP s120 item 8: do not spell the launcher user name (privacy hygiene) |
| `64a076261656` | `af2e71e78764` | Session 100: stamp the session commit hash into the report |
| `6705036947c6` | `9c2c00bce19d` | Session 101: measure two halves of the M3 subtrahend; the margin is WITHDRAWN |
| `68e5272f10d3` | `bed66f0f1d73` | Session 114: ROADMAP item 2 - the 3-s stall mechanism (present thread holds VideoOutConfig |
| `690c40e146a6` | `7d415514f356` | Session 111: knob daslot - the M1 queue off PipelineCache::m_mutex (per-slot guards, Takin |
| `697f39c2aabe` | `d714aa886363` | Session 114: mutants of sealed ttl114b - see tally in runs/mut_ttl114b.out.txt |
| `6b340d748e66` | `e491947d1c91` | Session 111: counters da_chk_ok / da_chk_bad (smemocheck checks of M1 takes) - the arming  |
| `6ccd8966a651` | `abcb564fc1a0` | Session 113: seal pred/01d_vbn113d - the exact-check verify (build 5ba0e188), relaunch unt |
| `6ce3e0dc5eb6` | `417e423e988f` | Session 113: seal pred/01f_vbn113f (8ef6b554) - the forced-OLD verify again on build 1678d |
| `6d8f6902b493` | `1186344a241a` | Session 110 close: audit addendum pred/04 (983b97ed), FACTS, ROADMAP (item 8, addition, de |
| `6db6787fcabb` | `c3ba88a85f77` | Session 113: mutlib v1 (db8703bd) + acceptance report archived |
| `6db82e727fb0` | `c9a8f3239df2` | ROADMAP: session 115 item 7 - go115a refused again (own v4 light checks); load gate of the |
| `6e046e507e04` | `90e0353ba19b` | Session 115: ROADMAP item 10 - mutlib v4 accepted for FULL runs (ttl114b 20 min vs ~70, ne |
| `6eb7d1415bba` | `1f2f25e7b1d8` | Session 113: bdanarrow knob-2 check separates races from misses - the region stamp is re-r |
| `6f26e6cf328d` | `80987fb647b6` | Session 117: seal 01r2 spn117 ADMITTED - K5 PASS (0 mismatches in 19.1M compares), K1 PASS |
| `6f691cb325a9` | `b70bea29a8c0` | ROADMAP s120 item 2: track threshold 1 ms -> 0.5 ms net measured ceiling (packages allowed |
| `704da6d36635` | `425ed0ec4a25` | ROADMAP: session 115 item 9 - F2 measured offline (flip mutex held 2.4 ms/flip, GuestGpu n |
| `710a15101d1e` | `76ac0f30375b` | Session 102: M5 measured and it does NOT close G; checkpoint-presence fix accepted; dabatc |
| `710e12c8eb94` | `80f182879808` | ROADMAP: session 116 item 2 - obs116 observation seal design (mutsite+pathlap+KYTY_GPU_WAL |
| `72d5fa2b4233` | `f8ed4ffe73fc` | WIP session 108 paused by the user: document the pause and the 103-108 cycle |
| `72e1c6aa910f` | `221032b23322` | Session 113: vbn113 and vbn113b NOT_EVALUABLE (both NEW; usage below the GC threshold) - t |
| `74913f106b60` | `6682360a644f` | s121 seal 02 (shp121): pred 3b951163, VFY_SCORER_SHA 43359b14, suite repaired (item 7), mu |
| `74e2ad72fdca` | `1724605b58dd` | Session 114: titleasync review fixes (ROADMAP item 4) - async title only once the SDL main |
| `76851b4b3b6b` | `c6432448e2c3` | Session 115 closed: local-session-115 (FACTS), next-session-116 plan (mutlib v4.1 test-awa |
| `7789c6a2ff86` | `8df511cd3b34` | ROADMAP: session 114 item 11 - PresentOverlap detector scope defect (UpdateTitle park insi |
| `7975fef2da09` | `1b26ebd1f58d` | Record the user's three decisions after session 101, BEFORE they are acted on |
| `7bc87cd275dd` | `acc777fa194b` | Session 118: slice census over-counts fixed before the seal (ROADMAP 118 item 4) |
| `7c73f26a7c46` | `baa345e24f6f` | Session 115: titleasync default 1 in the ring-fix build (ROADMAP 115 item 2; kept only on  |
| `7c8ec57f3759` | `74596d4d157b` | Session 102: seal addendum 05 to the dabatch pre-registration BEFORE any run |
| `7e62f3b9bc00` | `6763a13eac0c` | s121 close: item 9 (audit: recount CONFIRMED, protocol holds, closure holds with wording f |
| `7e892d5da1e3` | `0ddca1eeb1ec` | Session 112: knob daguard (at daslot 0 the M1 queue, holding m_mutex and ahead_queue_mutex |
| `7f0951f7f434` | `200cc3ec9e38` | s122 item 2: burn knob design accepted (per-thread calibrated CPU burn), scenes, reading r |
| `7f61398546bc` | `c1e810066259` | Session 113: ROADMAP item 15 - mutlib v2 accepted (six suites, net112 21 min, shn113 34 mi |
| `7fab116e1436` | `3efa04214862` | ROADMAP: session 115 item 3 - user instruction: let the v3 acceptance finish, then mutlib  |
| `81c6a895d082` | `54704c97a012` | Session 117: seal 01r2 spn117 (the suite prints ALL OK, the mutlib contract); ROADMAP item |
| `85a62bba6fa1` | `6e0426cc9d85` | s120 close: item 8 (audit: recount CONFIRMED, protocol holds, closure narrow; R1 shape w8, |
| `8694fbd5f4f8` | `41effbd77cbf` | WIP s122: knob burn (per-thread calibrated CPU burn for the scene bottleneck map) - implem |
| `8736198dadf8` | `bfacddeec564` | Session 106: knob dabatch default 64 -> 8 (pred/02_dabatch.md SHIP: d mean dt -169.3 us, 2 |
| `87f1c2bcca9c` | `b884884e9ba7` | Session 107 close: audit addendum, FACTS, ROADMAP decision after 107, plan 108 |
| `89c095eac148` | `d73d48954431` | Record the user's standing delegation and the executor's decision on G after session 102,  |
| `8a9de7b913e1` | `be5d1b017d30` | Session 100: measure the M3 addend; the sealed rule returns CLOSE |
| `8ab9b5d09119` | `b41759eea965` | Session 106: gw106 result (NAMED lock_wait_us, +616 us) and candidate dabatch=64/8 recorde |
| `8acab293aef4` | `dd3c36a8bfe0` | Session 112: seal pred/02_net112 (f5269a7b) - ABBA daslot=1 daguard=1 / daslot=0 daguard=0 |
| `8b107cdcc4ec` | `abdeb9725ade` | Session 104: record the stage results and the decision to ship dawalk=1 BEFORE changing th |
| `8c42ff98309b` | `1c37bd83f848` | ROADMAP s121 item 4: two seals - verify run vfy121 (PASS rule sealed before it) and ship A |
| `8f8a5f15331a` | `c192b11276d7` | ROADMAP s120 item 3: next session is a bottleneck map across scenes (GPU- vs CPU-bound), s |
| `9031f1702e80` | `82b27ab3870d` | Session 109 close: audit addendum pred/05 (fd27a2f8), FACTS, ROADMAP (items 8-9, addition, |
| `92fce7e592b1` | `2a13b02cffc2` | Session 106: seal pred/02_dabatch.md (bde73d27), scorer dab106.py with fixture, run chain |
| `942fd2fd5e5f` | `969f6d19bdaa` | Session 113: seal pred/01_vbn113 (e6b7b397) - verify of bdanarrow mode 2 (OLD regime requi |
| `94dfa2493563` | `9fb9c0967400` | Session 114: ROADMAP item 13 - go114d: vid114 PASS, boot114 FATAL commandRecorder.cpp:326  |
| `94e4ba0153e7` | `25c424d6b941` | Session 110: seal pred/01_stl110.md - the duration guard of cspfree (entries ABBA); scorer |
| `967d1aa4ddec` | `f6b687023676` | Session 113: KYTY_BUFFER_GC_TRIGGER_SHIFT_MB (measurement only, ROADMAP item 17) - lowers  |
| `9687fd2f4f2c` | `99fb6d5be250` | ROADMAP: session 116 item 1 - order and mutlib v4.1 scope (test-aware --changed-from with  |
| `968ff0afab39` | `8a254eed5cb1` | Session 118: ROADMAP item 4 - pre-seal check of spk118 (no blocker): census over-counts fi |
| `970e8ced8b4e` | `aa172587c684` | Session 118: the submission-level processor reset also resets the spine's shadow (term C,  |
| `9807fe218195` | `80170f642fc0` | Session 117: ROADMAP item 6 - batch measurement-only instruments per build/run, overlap mu |
| `996d565b43df` | `96c31b83aab9` | Session 120: ROADMAP item 1 - order and scope (one measurement build: R1 census, gate spce |
| `99acf705d4a9` | `eb9ed708e39c` | Session 114: seal pred/03_vid114 - the checks of the default titleasync=1 on build 8d7ba8f |
| `9a49f88d8a5b` | `e0da6195b65e` | Session 103: seal the BVH loop-cap entry series (pred/01) and its scorer BEFORE any run of |
| `9b2cd6581157` | `930970e82791` | Session 113: ROADMAP item 7 - the user's decision: a fast shared mutation harness (first-f |
| `9b8212f4e191` | `a7d5bc4d6190` | Session 103: seal addendum 03 to the M5' protocol (a reported STL number corrected, P4' an |
| `9d7712ccf753` | `35b266fbd8d3` | Session 114: windowInternal.h back to LF (the titleasync commit carried the working copy's |
| `9f5acea00881` | `598c36dba16a` | Session 113: mutants of sealed vbn113e 51/51 killed, controls 3/3 survive (mutlib v2, 36 s |
| `a0790c4fdb00` | `0df110fad1e3` | Session 113: ROADMAP item 13 - mutlib v1 accepted on six suites (net112 13 min vs 1h45, sh |
| `a14a2c65116b` | `543b24f2acf4` | s121 item 8: seal 02 shp121 NO_SHIP - delta dt +1.3 +- 154.3 us (44 pairs, fully armed: ke |
| `a25c4536fdb7` | `c72853f92dbc` | Session 107: plkstat holder/spin instrument and knob cspmemo (compute-prefetch memo on the |
| `a2e80961b29b` | `2d8f676da283` | Session 113: ROADMAP item 19 - 01f GO (forced OLD: 11.8M would-skip regions, 0 miss / 0 xt |
| `a3558a235218` | `e97825e56c76` | WIP сессия 99: подготовка bindings-only M3 без запуска игры |
| `a3ff539b346d` | `6a34ff13eb10` | Session 103: entry series NOT ACCEPTED (A3); record the decision to keep the cap ON by def |
| `a4307876f4d6` | `85d236357863` | Session 117: ROADMAP item 3 - fin117 not built (split on disk since s86-89); micro-tracks  |
| `a74205e98155` | `5030bc20f833` | Session 114: the PresentOverlap detector covers the swapchain work only - left before Upda |
| `a74ef6262464` | `79c62b0ec284` | Session 107: ROADMAP records before action (holder/spin instrument under plkstat, knob csp |
| `a8c856c30560` | `9245570b6f6b` | ROADMAP 118 item 5: spk118 ADMITTED => W2_CEILING; G2 re-measure decided before stage 3 |
| `aad6f6b661f1` | `621022d6df74` | Session 118: ROADMAP item 3 - smoke118 (not quoted): carry mismatch once a frame from the  |
| `ac949b8cb620` | `9c2b96532a40` | Session 116: ROADMAP item 7 - session audit (obs116 recount CONFIRMED; MAJOR: T1 ceiling r |
| `ade1cb6b2199` | `92d3fdd19a2d` | Session 113: mutants of sealed shn113 315/315 killed (controls 3/3 survive), the 2 unfille |
| `af5572e04681` | `b63c45cf04bb` | Session 100 correction: the CLOSE of M3 is WITHDRAWN; M3 stays GAP |
| `b110592e680c` | `a3bb29ea4562` | Session 119: ROADMAP item 3 - pre-seal check of g2_119 (no blocker): chain name guard and  |
| `b129fbbd0bd7` | `c8204c99e639` | WIP сессия 99: cal99a не допущен, последовательность остановлена |
| `b12d6b515a52` | `6b5842f4800b` | Session 112: ROADMAP records before the runs (vdg112 verify with transitions; net112 arms: |
| `b1f0c26be326` | `c197f5d02e79` | Session 114: ROADMAP item 7 - seal 01 ctl114 PASS (titleasync=0 freezes 3.03 s with the ex |
| `b3ed6047ad14` | `4e1894e402ad` | Session 106: dab106 SHIP (d dt -169.3 us, video clean) - decision recorded before the defa |
| `b885fd4ee76d` | `24f21722e3f4` | Session 113: seal pred/01b_vbn113b (120d0ad9) replacing the never-run pred/01 - race-separ |
| `b8fa868e7d89` | `4032d3459356` | Session 115: seal 01 amendment 1 - load gate --max-rate 1.5 --max-total 4 for the function |
| `ba07f759af56` | `e7462aa27165` | Session 114: ROADMAP item 1 - order (stall first, mutlib v3, next speed track); step 1(a)  |
| `ba0d59c34756` | `8a19055f8e22` | Session 107: obs107 result (walker holds 98.6 % of contended wall; cspmemo closed by VERIF |
| `bc739b3097bb` | `18157aa51771` | Session 114: mutants of sealed check114 93/93 killed, controls 3/3 survived (mutlib v2 fro |
| `bc7d66f8ee8b` | `9431c0d1bf4c` | Session 109: cspfam v2 - compute-pipeline creation count joins the family table stamps; co |
| `bcb98400253f` | `223dcaa2d619` | ROADMAP: session 114 item 12 - pre-seal audit of check114 (no BLOCKER; M1 counter blind be |
| `bd0dc57b66c4` | `4769fc4bc572` | Session 118: ROADMAP item 2 + design of stage 4 part 2 (carry, safe plan, slice census K3/ |
| `bd52f86fa7f6` | `518aa8db8560` | Session 109: ROADMAP records before action (cspfam v2 creation-count stamp, powered ABBA o |
| `bd6c2789b848` | `beb3ca6a8aae` | Session 117: seal 01r2 mutants 104/104 (mutlib v4.1, controls 3/3) |
| `be8d862728f7` | `7228714b0fc4` | Session 111: seal pred/03_shp111 (594e2402) - the ship ABBA of daslot, main estimator fram |
| `beaef5161c25` | `a1bcd345b9f2` | Session 117: ROADMAP item 5 - spine verify by full snapshots and member-wise equality (no  |
| `bfad956c7c0d` | `52fc12a0c64b` | Session 116: ROADMAP item 6 - obs116 ADMITTED: GuestGpu phase split (bind 34 %, emit 24 %, |
| `bfff4c341e6b` | `f16834b24c3c` | Session 105: seal candidate 1 (dawalklead=2 under dawalk=1, ship bar on mean dt) and its s |
| `c01e89f24b47` | `ee6fea3e76ad` | Session 119 close: ROADMAP item 5 (audit), FACTS, next-session-120 |
| `c3144290f9a4` | `f7d6f906ca90` | Session 111: build 0c8a13f2 (daslot default 1) video vid111 PASS (4 023 frames, 0 glitches |
| `c512a985ba59` | `afba06e298f1` | Session 110: seal pred/03_shp110 (4f02d284) - the ship ABBA of cspfree; scorer shp110.py ( |
| `c5cb87457207` | `18d2465c1486` | Session 115: seal pred/01_chk115 - ring-fix build d3a981a2 (titleasync default 1): vid115  |
| `c8e0fda8dfb2` | `9d1195c58c28` | Session 113: mutants of sealed vbn113f 54/54 killed, controls 3/3 survive |
| `ca067a35e398` | `2b137d5583a8` | Session 114: ROADMAP item 6 - user allows game runs again; rule for foreign load before se |
| `cd403db5b5c8` | `bc8763dd7d9a` | Session 102: seal addendum 06 (entry-failure clause for pred/04) after ckpt102 hung on ent |
| `ceec841973f7` | `b439bccd5fe9` | Session 116: ROADMAP item 5 - mutlib v4.1 accepted for FULL runs (ttl114b selected 18 min  |
| `d0502dae6476` | `a7560dc97afb` | Session 104: seal the regression screen reg104 before the run |
| `d611c204dde9` | `8a4c77da54f6` | Session 112 close: audit addendum pred/03 (32d27a4a), FACTS, ROADMAP (item 6, addition, de |
| `d6b23c01e41f` | `c6330e94a446` | Session 106: KYTY_GPU_WALL=1 measurement-only wall accounting of the GuestGpu thread |
| `d6c1264c9a39` | `4802ce4de2d7` | Session 111: seal pred/01_obs111 (98531828) and pred/02_vds111 (0dadb4f7); scorers obs111  |
| `d75fda32066f` | `95b6f86b7640` | Session 113: ROADMAP item 20 - shn113 mutants: the two unfilled-seal mutants run on the dr |
| `d7bd4821045d` | `ba467d1fe616` | Session 106 close: audit addendum, FACTS, ROADMAP decision after 106, plan 107 |
| `d8308f155e59` | `68c0796f9314` | ROADMAP: session 116 item 4 - drop id_emit_med before sealing (2-4% chance refusals, redun |
| `d93e814977cc` | `99e76b5ba53e` | Session 113: ROADMAP item 17 - 01d read NOT_EVALUABLE x4 (all NEW, admitted; 0 miss/xthr/r |
| `dbd653896dc8` | `29b1d2f3aed9` | Session 104: seal stage 1 of route A (mut104/sh104, central-G rule as recorded) and the da |
| `dc1136b5f564` | `6742ce0d377d` | Session 111: counter da_q_free (QueueDrawAhead calls without m_mutex) - the arming proof o |
| `de2b7dc9e47f` | `b5dae944fbe1` | Session 113 PAUSED before its first game run: ROADMAP item 6 (state, debts), FACTS (WIP),  |
| `de9c75475b68` | `41cf2de1593c` | Session 105: ctxtick default 1 after the sealed M3.1 acceptance (pred/02_m31); built as 81 |
| `df081a1d68dc` | `e6f571851199` | Session 114: ROADMAP item 3 - user instruction: no game runs until the user allows; seals  |
| `e0be82bc6661` | `54a901c05caa` | ROADMAP 119 item 4: g2_119 ADMITTED - G2 = 2 216.5 us < 3 000 => route A closed for maximu |
| `e3041bdd8c69` | `45b5b4657070` | Session 116: mutants of sealed obs116 145/145, controls 3/3 (mutlib v4 frozen, 55 s) |
| `e344e34b9d1b` | `96261e42636a` | Session 113: ROADMAP item 18 - 01e NOT_ADMITTED (one GpuWaitSlow: a 3 s wait on the unsubm |
| `e3a764bdb937` | `9e0583661758` | Session 105: M3.1 accepted (P1-P4); record the decision ctxtick default 1 BEFORE the code  |
| `e64fb4242596` | `a686a5b05f23` | Session 107: record - obs107 merges observation and verify (cspmemo=3), before its seal |
| `e687a78bc1b2` | `e046ce06b9ee` | Session 108 resumed: seal pred/01_cspfam.md (a40cf056), fixtures 103 cases, s108 port, run |
| `e68bb6ed061c` | `1a07b95f7c85` | Session 115: ROADMAP item 4 - mutlib v3 accepted (11 suites, 1225/1225 rows equal to v2) w |
| `e68f1ccbac56` | `4c93f5447d93` | Session 100: stamp the correction commit hash |
| `e725c59b4c5b` | `4dc6203d8f9d` | Session 114: seal pred/02b_ttl114b (1f1b4b8b) - ABBA titleasync=0/1 again with the TITLE_A |
| `e8404d9d0b24` | `41fa73f9c3f9` | Session 117: knob "spine" (measurement only, default 0) - shadow spine of route A stage 4: |
| `e862f5b72b8f` | `8b19339319b1` | Session 117: ROADMAP item 2 - lock-contention tracks closed; stop rule for micro-tracks on |
| `ea40fa82f15d` | `486f1241d16b` | Session 115: ROADMAP item 8 - seal 01 chk115 PASS: ring fix holds a 10-s preparation (over |
| `ea7c698970eb` | `05c4472035a7` | ROADMAP s121 item 5: arming floor +300 (was +800), RC8 ceiling in shp121, chain gate shp12 |
| `eccc6ea72c0e` | `c8b843492026` | Session 104: dawalk=1 shipped (-265.9 us mean frame, pinned ABBA), the vblank plateau does |
| `ed570ed7def9` | `8f917538fb64` | Session 114: seal pred/01_ctl114 (ac16a32a) - the titleasync positive control (KYTY_MAIN_S |
| `ee686cccf17a` | `74f7907c3a29` | Session 109: vfy109 GO, ent109b FAIL (S_A 7, S_B 17) - cspfree not shipped; seal pred/04_f |
| `eed387bb1faf` | `47fae0448207` | Session 108: fam108 SHIP - knob cspfam default 4 (d mean dt -141.8 us at the pin, 2SE 107. |
| `eedff9d60978` | `e787215dba3e` | Session 107: seal pred/01_obs107.md (85a65121), scorer obs107.py with nine-branch fixtures |
| `f11dda771c5f` | `b97e36fb0a28` | Session 118 close: ROADMAP item 6 (audit), FACTS, next-session-119 |
| `f1a47b8854af` | `a298a2cb65d6` | Session 119: ROADMAP item 2 - removability designs by reading (no candidate proved >= 1 ms |
| `f1de07af470d` | `4cefa0b9f4ef` | Session 110: build 072861c8 (cspfree default 1) video vid110 PASS (4 004 frames, 0 glitche |
| `f3642d07e6b3` | `96cbebec1ef6` | ROADMAP: session 115 item 6 - go115a refused on foreign load (<foreign app>, 30 min), seal |
| `f3b74f0775b2` | `a9170cd24847` | Session 114: ROADMAP item 15 - session audit (all numbers CONFIRMED; MAJOR P1: item 13 set |
| `f4c2f54b26f8` | `868e937afb8b` | Session 105: seal the M3.1 acceptance (pred/02_m31) and its scorers BEFORE the runs |
| `f505e50743b9` | `28fc040b9cc9` | Session 113: mutants of the sealed vbn113b.py - output archived and hashed in SEALS113 (po |
| `f62d53779ce5` | `3b8edf175cc3` | Session 118: ROADMAP item 1 - one build, one sealed run, two arms (P: safe spine plan, K3, |
| `f6f063d88e5e` | `3d6f3c031e4e` | Session 114: seal pred/02_ttl114 (02b11e87) - ABBA titleasync=0/1 on build 916f6489, SHIP  |
| `f987d9b7dc5c` | `ee534e750c41` | Session 113 resumed: ROADMAP item 8 - order on resuming (go113b.sh first while the machine |
| `f9e19f7a1357` | `de0e41969e91` | Session 108: knob cspfam (compute-prefetch skip per shader family) and the sync-compile gu |
| `fbcfd4978dd7` | `31381f874bc7` | Session 117: spine repeats the dispatch's wave-size write (DispatchDirect/Indirect SetCsWa |
| `fdc031fc5a65` | `883f7fcc2d79` | Session 114: ROADMAP item 9 - seal 02b ttl114b SHIP titleasync=1 (d dt -43.5 +- 73.2 us, S |
| `fe8faf6954c3` | `f565f55ac098` | Session 119: ROADMAP item 1 - order and scope (G2 re-measure at W = 2, zero code; removabi |
| `ff672e66cbdf` | `3cb8f17f7642` | Session 117: ROADMAP item 4 + design of the shadow spine (route A stage 4 part 1: K5 repro |
