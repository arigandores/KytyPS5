## 6. Executor variants and the decisions of items 362, 371, 374 (g) and 377 (ROADMAP "SESSION 122" item 371, KytyPS5 dcc6cbf8; item 362, KytyPS5 a1f02bd5; item 374 (g), KytyPS5 704c13d2; item 377, KytyPS5 a387a2d4)

Item 371 (the review S9r, HPP-432, docs/track-s/s9r-review.md at df2b3179: SOUND_WITH_CHANGES, RC1 - RC6 accepted):
- (b) RC3 - DECIDED: ">= 3 000 frames" and "0 one-frame glitches" are not members of the reading of the repeat of integrity
  (item 355 (g)); the video member of a pi arm = the video read by the detector (haze not None) with frames after frame 1 002;
  the video frames, the present rows and the one-frame glitches are data per arm; the word of seal 05b is printed beside as the
  executor variant with "DIFFERS (video rule)".  The other members of the readable arm (admission, identities, entry, death
  markers, the W hold of 300 s) by the letter, unchanged.
- (v) the amendment of the U reading of item 355 (e) (RC2) - DECIDED: the lower bound of the screen (progress elapsed_ms, the
  --timeout on a timeout outcome); > 180 s - the kill member, "screen > N s (lower bound)"; an arm with neither both lines nor
  a bound > 180 s is not an S-cat member: UNDETERMINED with >= 1 such arm and < 2 failing; the letter word printed beside with
  "DIFFERS (screen undetermined)"; an arm with a death marker still stops the series (item 355 (k)).
  Executor variant (a question to the lead, printed beside): "< 2 failing" is read here as < 2 failing MEMBER arms (a
  non-member's failure does not count, by "is not an S-cat member"); the reading that counts a failing arm without a screen
  measure among the failing is printed beside ("executor variant ...", "DIFFERS (a failing arm without a screen measure)").
  Neither reading can turn a kill into ALIVE_BY_PROBE_5.
- (g) RC1 - the guard s10/IN_ARM and the admission row installed_before in the harness and the scorer (section 1; its sha by
  item 374 (g), below);
  RC4 - the data per U arm; RC5 - the sheet of a long series; RC6 - this seal line: the line "Cache test mode: prepare-cold"
  was not observed on a real run; the first U is also the check of the gate; a gate refusal on u_1 - stop of the U series and a
  question to the lead, the attempt a form interference, not an S-cat arm, a repeat only by a lead item.
- Item 374 (g) (FS3d HPP-450; the lead comment 088c2da9 to this link): FS3 installed 2026-10-03T07:11:12Z, the admission row
  installed_before = 540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1 - INST_WANT of go_s9.sh and a constant of
  its own INST_WANT of sc_s9.py; the u binary line and BIN_U (the pinned copy C:/kyty/p283/bin/kyty_emulator_4aa62e95.exe by sha)
  do not change - the binary of the u arms and the installed binary are different constants.
- Item 377 (the review of S9b, rework 1): (b) seal 06 is not changed, this edition 06b replaces it; fixtures of both outcomes
  (sc_s9: A3, F7, F7b - 540c035a passes, 4aa62e95 fails that row only; go_s9: G23, GL1, GL5b, GL10, GL12, GL12b - the installed
  = INST_WANT runs the arm with the s / u binary and returns the installed build, the installed = the u stand-in -> rc 1 inside
  the lock, nothing installed); mutants --only of the row, the constants and the seal path (section 5), the counted full run of
  S9b not repeated.  (v) "< 2 failing" of item 371 (v) = failing S-cat MEMBERS - the executor variant above is the letter; the
  other reading stays a reference line with "DIFFERS (a failing arm without a screen measure)" and gives no word; the scorer
  code does not change by (v).
- (e)(2) this link ran no command longer than 60 s while a run series of another track was going (its runs link in_progress
  with an executionRunId); the waits are rows of s9b/times.txt.

Item 362 (unchanged; the questions V1 - V10 of the S9 report and of seal 05_s section 6):
- V1 (the cold gate in the form C5) - DECIDED by item 362 (b): KYTY_PIPELINE_PRECACHE=0 stops the recipe writer
  (4fc501f4:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5858), so in the form C5 the member ">= 1 new recipe" is
  replaced by ">= 1 in-game creation after the line Level has started: L"; the members new permutation and skipped draw by the
  letter; in the form APP the whole gate by the letter (T2_GATE_READING = p362; the letter and the executor variant beside).
- V2 (T-4 under PRECACHE=0), V3 (the T2 list), V4 (the U list), V5 (the export), V6 (t2_cs0 right after t2_1), V7 (f3b3aa3b
  with snap0 for c5_0 and T2), V8 (holds and timeouts: pi 300 / 480, c5_0 and T2 100 / 480, u 100 / 600), V10 (the screen time
  from the Popen, an upper bound by one poll of 0.5 s) - accepted by item 362 (g), as in seal 05b.
- V9 (READ_3) - DECIDED by item 362 (v): READ_3 needs the loaded member of (2) on both R, else READ_OTHER; a series in pi_r0
  and in a W arm with none in pi_r1 is READ_3 with a note; the executor's reading (no loaded member) printed beside.

## 7. Not claimed (item 355 (m), item 362 (z), item 371 (z))

- FIXED B33; that the event of pcw_int is an effect of the game or a defect; that the cache write causes the entry freezes; where
  the warmth of the driver lives; that the salt without precache neutralises the driver cache before the C5 reading; that the
  replaced member of the gate equals the recipe member in strength; that the gate prepare-cold fires on a real run; that the
  corpus or the catalogue is complete; that the .xz files hold no entry of a T2 level ([I]); that the entry freezes are caused by
  the shaders; that shaders get faster on the GPU; that the harness runs the S10 path inside the lock without an error (the path
  inside the lock ran on fixtures only); no number is a gain; 60 FPS is not promised; goal (B) does not change.
