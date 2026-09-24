# Session 113 — adversarial audit, lens: INDEPENDENT RECOUNT

Auditor's own code only: nothing imported or copied from the scorers. The only scorer text I read was one line of
`shn113.py` (line 306), to get the definition `cpu_net_us = cpu_gpu_us − spin_gpu_us`. All logs were read in binary
mode (`'rb'`), streamed line by line, or for the archive in 16 MiB chunks. I did not run the game, did not build and made no git
writes. Everything I wrote is under `C:/kyty/s113/audit113/final/`.

**Bottom line: every claimed number I recounted is CONFIRMED. No deciding number differs, so there is no MAJOR
finding.** There are six INFO notes and one MINOR note (§3).

## 1. Claim-by-claim table

### Seal 01f — `vbn113m` (verdict inputs)

| Claim | Recounted | Status |
|---|---|---|
| rows 10 112 | 10 112 main / 10 112 draw / 10 112 x; n = 2…10 113 contiguous in all three streams; same n sets; no duplicate n | CONFIRMED |
| Σ`bda_nwould` 11 845 121 | 11 845 121 | CONFIRMED |
| Σ`bda_nmiss` 0 | 0 | CONFIRMED |
| Σ`bda_nxthr` 0 | 0 | CONFIRMED |
| Σ`bda_nrace` 0 | 0 | CONFIRMED |
| Σ`bda_ginv_reg` 11 683 | 11 683 | CONFIRMED |
| Σ`bgc_evict` 13 800 | 13 800 | CONFIRMED |
| Σ`prio_unsub` 57 290 | 57 290 | CONFIRMED |
| Σ`prio_stall` 0 | 0 | CONFIRMED |
| Σ`gw_idle_prio` 0 | 0 | CONFIRMED |
| median `bda_scan`, draw rows n ≥ stable_frame (396) = 1 064 | 1 064 over 9 718 rows (same for n > 396) | CONFIRMED |
| B3/B4/B5 medians (1 / 1 012 / 1) | `bda_ginv_reg` 1, `bda_nwould` 1 012, `bgc_evict` 1 | CONFIRMED |
| BAD = Σnmiss + Σnxthr = 0 → GO | 0 + 0 = 0; OLD (1 064 ≥ 500) | CONFIRMED |
| Admission inputs I could check | `ROWS`: all 15 fields on every x row. `STREAMS`: contiguous, equal counts. `ARMED`: ginv_reg > 0, nwould ≥ 1 000, Σnskip = 0. `DEFAULTS`: Σda_q_free 10 795 825, Σcspfree_hit 2 617 712, Σcspfree_bad 0. `GC_LINE`: exactly one `BufferGc:`, shift_mb=1024, trigger 8 673 610 957 < critical 13 183 326 618. `PIN_ONCE`: one `GpuClockPin: mode 1`. `NO_MARKER`: none in the log or either stdout file. `GATES`: exactly one `bdanarrow=`, ends ` bdanarrow=2`. `ENV_FORBIDDEN`/`ENV_SHIFT`: env has no schedule, checkpoints, REC or precache, and has exactly shift 1024. `BINARY`: meta sha = pinned copy = `1678d3f4…`. `PREREG`: file sha `8ef6b554…` = meta. `ATTEMPT`: 1 ok, 300.1 s. `PRE_RUN`: 0.0 | CONFIRMED |

### Seal 01e — `vbn113k`

| Claim | Recounted | Status |
|---|---|---|
| exactly one `GpuWaitSlow:` line | 1 in the log (the same line is echoed once in `stdout_vbn113k.txt`) | CONFIRMED |
| role=4 requested=329576 known=329575 current=329576 | identical text (requested **=** current) | CONFIRMED |
| frame 9672 dt_us ≈ 3 032 310 | n=9672 dt_us = 3 032 310, the run's maximum. The `GpuWaitSlow` line sits between main rows 9671 and 9672 | CONFIRMED |
| Σ`bda_nwould` 13 893 695 | 13 893 695 | CONFIRMED |
| Σnmiss 0 / Σnxthr 0 / Σnrace 3 | 0 / 0 / 3 | CONFIRMED |
| median `bda_scan` 1 064 | 1 064 (stable 265, 9 506 rows) | CONFIRMED |
| rows | 9 769, contiguous | CONFIRMED (information) |

### Seal 01d — `vbn113g/h/i/j`

| Claim | Recounted | Status |
|---|---|---|
| all NEW, median scene `bda_scan` 52–54 | 52 / 52 / 52 / 54 | CONFIRMED |
| Σ`bda_nwould` 2 350 457 | 589 457 + 590 438 + 589 112 + 581 450 = 2 350 457 | CONFIRMED |
| Σnmiss 0, Σnxthr 0, Σnrace 0 | 0, 0, 0 in each of the four | CONFIRMED |
| Σ`bda_ginv_reg` 2 349 | 588 + 590 + 589 + 582 = 2 349 | CONFIRMED |
| no markers | only `GpuClockPin:` ×1 and `Gate:` ×1 per log (no `BufferGc:` line; that build predates it) | CONFIRMED |

### Seal 02 — ABBA `shn113` (deciding numbers)

Protocol as recounted:
- Rows carry `blk=` shifted, so block b = n ∈ [1801+90b, 1890+90b]. I checked this against every `blk=` value: 90 rows per block for b ≥ 1, and the `arm=` of every row equals its `GateArm` arm.
- The `GateArm` frames are 1800+90b for all 202 lines, and their arm pattern is exactly ABBA.
- Quartet q = blocks 4q…4q+3 (arms 0,1,1,0). Quartet 0 starts at frame 1801, before 2100, so it is excluded. Quartet 50 (blocks 200–203) is incomplete, so it is excluded too (the log ends at n = 19 907).
- Pairs are (4q+1 − 4q) and (4q+2 − 4q+3). The per-block mean is taken over rows 10..89.

| Claim | Recounted | Status |
|---|---|---|
| n = 98 pairs (orientations 49/49), 196 blocks | 98 (49/49), blocks 4…199 = 196 | CONFIRMED |
| d mean `dt_us` −83.2 | −83.232 | CONFIRMED |
| 2SE 68.0 | 67.996 (SD 336.562) | CONFIRMED |
| t −2.45 | −2.448 | CONFIRMED |
| d `cpu_net_us` −83.9, 2SE 60.6 | −83.937, 2SE 60.585, t −2.771 | CONFIRMED |
| arm-0 `bda_scan` level 1 438.4 | 1 438.381 (median of 98 block means) | CONFIRMED |
| arm-1 `bda_scan` level 49.6 | 49.619 | CONFIRMED |
| arm-1 `bda_nskip` level 1.37 | 1.369 (arm-0: 0.0; arm-0 Σnskip over all scheduled rows 0) | CONFIRMED |
| P5 d `gpu_busy_us` 5.9 | 5.882 (2SE 23.8) | CONFIRMED |
| P7 d `da_miss` 0.2 | 0.236 (2SE 5.7) | CONFIRMED |
| d `da_take_us` 3.0 | 3.029 (2SE 8.8) | CONFIRMED |
| secondary (rows 60..88) d `dt_us` −28.6 / 2SE 119.2 | −28.555 / 119.201 | CONFIRMED |
| arm levels dt 30 623.9 / 30 621.0; gpu_busy 12 521.8 / 12 500.4; rec_n 10 872.5 / 10 853.9 | 30 623.88 / 30 621.01; 12 521.78 / 12 500.41; 10 872.51 / 10 853.93 | CONFIRMED (these are inside BANDS 28–40 ms, 10–16 ms and 9 000–13 000) |
| NO_CHECK / NO_XTHR: Σnwould / Σnmiss / Σnxthr over all rows 0 / 0 / 0 | 0 / 0 / 0 (Σnrace 0, Σprio_stall 0) | CONFIRMED |
| SYNC_COMPILE (arm-1 Σcs_sync_new ≤ arm-0 + 2 from frame 2100) | 0 and 0 (field present on all 19 906 rows) | CONFIRMED |
| Verdict KEEP (S1: −83.2 > −100 fails; S2: −83.2 + 68.0 < 0 passes) | same arithmetic | CONFIRMED |
| Protocol inputs | env: exact schedule `90+1800:…bdanarrow=0\|…bdanarrow=1`, ABBA=1, pin 1, markers 0, shift 1024. `gates_base.txt` sha `303a7849…` = meta gates text, and there is no `bdanarrow` in it. Prereg sha `75f34c69…` matches. 1 ok attempt, 600.2 s. One `BufferGc:` line with shift 1024. One `GpuClockPin:`. No markers | CONFIRMED |

### Video — `vid113`

| Claim | Recounted | Status |
|---|---|---|
| 3 976 frames | `ffprobe -count_packets`: 3 976; my ffmpeg decode: 3 976; `.idx`: 3 976 lines | CONFIRMED |
| 0 glitches | my own one-frame detector (160×90 gray; a frame unlike both neighbours while the neighbours are alike; thresholds 4/6/10/20): 0 candidates at every threshold. Max isolation score 0.33 | CONFIRMED |
| check113 totals (scene rows 3 692, n ≥ 276) | cspfree_hit 981 286, da_q_free 4 141 859, prio_unsub 22 455, da_guard_yield 8. Σcspfree_bad = cs_sync_new = cs_sync_wait = da_q_noguard = da_slot_bad = bda_nskip = bda_nwould = prio_stall = 0 | CONFIRMED |
| no markers / GC default | no markers in the log or stdout; one `BufferGc:` with shift_mb=0 (trigger 9 747 352 781) | CONFIRMED |

### Archive claim (ROADMAP item 18)

| Claim | Recounted | Status |
|---|---|---|
| `GpuWaitSlow` in 0 run logs of `s10[4-9]`/`s11[0-3]` except `log_vbn113k.txt` | 97 logs (15.6 GB) scanned: exactly one hit, `s113/log_vbn113k.txt` | CONFIRMED |
| in 22 logs of `s[89]*` (170 logs, 24.0 GB) | 22 logs, 1 line each | CONFIRMED |
| all with requested < current | 22 / 22 have requested < current (by 80–104; `known` = requested − 1 in all). `vbn113k` is the only case with requested = current | CONFIRMED |

## 2. Severity summary

- **MAJOR: none.** Every 01f verdict input and admission term I could recount matches. So does every 02 deciding number (n, d mean, 2SE, t, arming levels, admission counters).
- **MINOR — the archive "22 logs" are 21 distinct events.** `s98/log_trig98a.txt` and `s98/log_trig98a_a1.txt` carry the byte-identical `GpuWaitSlow` line (requested=2966 current=3056). This is almost certainly one run stored twice. "22 logs" is literally true, but it must not be quoted as 22 occurrences.
- **INFO — the KEEP verdict does not depend on how the block rows are indexed.** Moving the block window by one row either way gives d = −93.3 (2SE 64.2) or −93.2 (2SE 66.8). The whole block (rows 0..89) gives −84.4. None of these crosses S1's −100, so KEEP holds under each variant. The pair median is −106.7 and 58 of 98 pairs are negative. That median is not the preregistered estimator; it is quoted only to show that the size sits near the bar.
- **INFO — strong within-quartet order effect.** The AB pairs average −32.3 and the BA pairs −134.2. That is a drift of about +51 µs per block position. The balanced 49/49 ABBA cancels it, so it does not bias the estimate, but it explains why SD is 337 µs per pair.
- **INFO — P1 MISS is real.** The arm-0 `bda_scan` level is 1 438 in the ABBA against 1 064 in the 01f verify on the same build and the same shift. I recounted it; it is not a scorer artefact.
- **INFO — the unshifted video `vid113` ran in the natural OLD regime.** Its median scene `bda_scan` is 1 065, median `bgc_evict` 1 a flip, and Σ`bda_ginv_reg` 5 610 over 3 966 rows. This bears on the "share of natural OLD" question in seal 02 §7; it is not a claim of the session.
- **INFO — SYNC_COMPILE was never tested against a live counter.** `cs_sync_new` is 0 on every row of `shn113`, so 0 ≤ 0 + 2 holds by default.
- **INFO — CLAUDE.md is out of date.** Its state line ("installed b47b58a9, pause before 01b") no longer matches the machine. The installed `kyty_emulator.exe` is now `1678d3f4…`, the 01f/02 build. Documentation drift only, but it should be corrected at session end.

## 3. Scripts (all under `C:/kyty/s113/audit113/final/recount/`)

| Script | Purpose | Output |
|---|---|---|
| `peek.py` | print the first N lines with given prefixes (format inspection) | — |
| `rc_vbn.py <log> <stable>` | stream counts, duplicate and contiguity checks, Σ of x fields, scene medians, GpuWaitSlow/BufferGc lines, max dt | `rc_vbn113{m,k,g,h,i,j}.json`, `rc_vid113.json` |
| `markers.py <files…>` | count marker lines (GpuWaitSlow, GpuHangAbort, skipped draw, Error/Fatal/terminate/abort, MISMATCH, BdaNarrowMiss, GpuClockPin, BufferGc, GateArm, Gate:) | `markers_vbn113m.json`, `markers_rest.json` |
| `gws_pos.py <log>` | main rows around the GpuWaitSlow line | (stdout) |
| `extract_shn.py <log> <csv>` | per-flip main/draw/x fields plus the GateArm lines of the ABBA log | `shn113_rows.csv`, `shn113_rows.csv.gatearm.txt` |
| `abba_shn.py` | quartets, pairs, d mean/SD/SE/2SE/t (main and secondary), arm levels | `abba_shn113.json` |
| `abba_extra.py` | totals over all rows, SYNC_COMPILE by arm, row-index shift sensitivity | (stdout) |
| `abba_robust.py` | median and trimmed mean of d, sign count, orientation means, extremes | (stdout) |
| `vid_scene.py <log> <stable>` | video scene-row totals | (stdout) |
| `vidcheck.py <mp4>` | independent one-frame-glitch screen | (stdout) |
| `archive_gws.py <out.json> <globs…>` | chunked streaming search of the archive for GpuWaitSlow, with requested/known/current | `arch_s104_113.{json,txt}`, `arch_s8_9.{json,txt}` |
