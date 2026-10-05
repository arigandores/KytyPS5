## Table of tags
| tag | binary | lock (UTC) | admission | 1st scene frame | entry | dump in window | max `dt_us` window | B2 frames | hold, s | unattr. (F20a) | deaths | frames >= 1 s | glitches | video frames | skipped draw | CPU line before the tag (procload) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `f20_v25` | 2c9b69b9 | 13:07:33-13:13:59 | YES | 387 | warm | 0 | 53008 | 0 | 334.2 | 0 (0) | 0 | 0 | 0 | 9977 | 5 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v26` | 2c9b69b9 | 13:15:20-13:21:50 | YES | 332 | warm | 0 | 52985 | 0 | 334.4 | 0 (0) | 0 | 0 | 0 | 9733 | 5 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v27` | 2c9b69b9 | 13:23:12-13:29:41 | YES | 329 | warm | 0 | 53368 | 0 | 334.6 | 0 (0) | 0 | 0 | 0 | 9880 | 6 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v28` | 2c9b69b9 | 13:30:54-13:37:24 | YES | 342 | warm | 0 | 52933 | 0 | 334.4 | 0 (0) | 0 | 0 | 0 | 9844 | 0 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v29` | 2c9b69b9 | 13:38:36-13:45:00 | YES | 338 | warm | 0 | 52877 | 0 | 334.3 | 0 (0) | 0 | 0 | 0 | 9951 | 13 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v30` | 2c9b69b9 | 13:46:16-13:52:43 | YES | 325 | warm | 0 | 52531 | 0 | 334.3 | 0 (0) | 0 | 0 | 0 | 9824 | 6 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v31` | 2c9b69b9 | 14:04:13-14:10:37 | YES | 336 | warm | 0 | 55560 | 0 | 334.2 | 0 (0) | 0 | 0 | 0 | 9931 | 6 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v32` | 2c9b69b9 | 14:11:55-14:18:17 | YES | 328 | warm | 0 | 52607 | 0 | 334.4 | 0 (0) | 0 | 0 | 0 | 10028 | 30 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v33` | 2c9b69b9 | 14:19:41-14:26:15 | YES | 335 | warm | 0 | 66970 | 0 | 334.3 | 0 (1) | 0 | 0 | 0 | 9970 | 38 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v34` | 2c9b69b9 | 14:27:37-14:34:04 | YES | 326 | warm | 0 | 53450 | 0 | 334.2 | 0 (0) | 0 | 0 | 0 | 9907 | 29 | procload: clean (no process above 0.50 CPU s/s, total cap None) |
| `f20_v35` | 2c9b69b9 | 14:35:14-14:41:39 | YES | 349 | warm | 0 | 52814 | 0 | 334.5 | 1 (1) | 0 | 0 | 0 | 9895 | 0 | procload: clean (no process above 0.50 CPU s/s, total cap None) |

## Unattributed hold frames
| tag | idx | n | `dt_us` | t from the first scene frame, s | class (letter / F20a) | `PriorityStall:` lines / us |
|---|---|---|---|---|---|---|
| `f20_v33` | 2157 | 2492 | 159353 | 78.1 | B5 / pcs after S12 | 1 / 69475 |
| `f20_v35` | 8138 | 8487 | 115041 | 286.0 | nothing / nothing | 0 / 0 |

## Attributed hold frames (reference)
| tag | idx | n | `dt_us` | t, s | class | ir / gcn / pcs / trip / prio |
|---|---|---|---|---|---|---|
| `f20_v25` | 2143 | 2530 | 103015 | 78.4 | B5 | 8863 / 0 / 0 / 0 / 0 |
| `f20_v26` | 2146 | 2478 | 113410 | 79.8 | B5 | 10426 / 0 / 0 / 0 / 1 |
| `f20_v29` | 2168 | 2506 | 129327 | 79.2 | B5 | 10426 / 0 / 0 / 0 / 0 |
| `f20_v30` | 2139 | 2464 | 116080 | 77.6 | B5 | 10426 / 0 / 0 / 0 / 1 |
| `f20_v32` | 2114 | 2442 | 164548 | 76.7 | B5 | 14634 / 0 / 0 / 0 / 1 |
| `f20_v34` | 2179 | 2505 | 157641 | 79.6 | B5 | 14270 / 0 / 0 / 0 / 1 |

## Summary (series.txt)
```
BASE B2 {'warm': 28, 'b2': 0} (F20a 6 + F20c 22, item 543 (g)); B32 - the F20e series alone (item 543 (e))
SUM {'warm': 39, 'b2': 0, 'holds': 11, 'unattr': 1, 'unattr_f20a': 2}
TAGS {'made': 11, 'interference': 0, 'warm': 11, 'cold': 0, 'unread': 0, 'holds': 11, 'nohold': 0}
READING B2 (entries with >= 1 B2 frame; base 28 warm of F20a + F20c): NOT A DEFECT candidate, 0 of 39 (upper 95 % CP 0.090)
READING B32 Sky Garden, F20e alone (holds with >= 1 unattributed frame, letter): 1 of 11 holds, 95 % CP [0.002; 0.413]
READING B32 Sky Garden, F20e alone (variant F20a): 2 of 11 holds, 95 % CP [0.023; 0.518]
STOP (i) B2 warm N 39 >= 30: yes; (ii) B32 F20e: holds 11, with unattributed 1 (stop at >= 1 or 29 clean): yes; tags made 11 of 30
NEXT stop adding tags
```
