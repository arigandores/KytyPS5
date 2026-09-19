# Independent VERIFY 99: CODE

Reviewed the sealed 10848-byte preregistration with SHA256
`8b816528b78a1730c052d7fdbc414d7b00ef3b9c4df25ab2e7016b23d9d4b14d`,
the new scorers and necessary inherited implementation. No author conclusions or FACTS were read.
No game, launch harness or build was executed. Outputs were confined to this directory.

## Blocking findings

1. **Failed warmup still launches counted process.** `C:/kyty/s99/enter_scene.py:605-608`
   unconditionally continues after a warmup, regardless of its outcome/hold_exit.
   With `--warmup-first --attempts 1`, an entry failure still reaches another `attempt()`
   at line 602. An ErrorDeviceLost also changes the cache at lines 600-601. This violates
   sealed section 2's stop-on-failure/no-replacement protocol. Static reproduction suffices;
   no launch was attempted.

2. **Live DARK structure is not checked over the inherited R4' domain.**
   `bf99.py:143,169-172` applies DARK_B only at n>=2100. Inherited rv98 R4' examines
   earlier scheduled blocks, but its DARK98 does not include the new live counters.
   `counterexamples.py` inserts bf_live_mat=1000000 at n1900, block3, unarmed idx10.
   All protocol, new core and selected rv controls still PASS. Sealed section 3 requires
   applying inherited DARK structure to the new fields too.

3. **Full-log integrity fields can be missing and silently read as zero.**
   `bf99.py:146` checks presence only in the endpoint window, whereas rv98.py:427-430
   defaults absent full-log integrity values to zero and checks only global presence.
   Removing bf_mixed from n1900 passes protocol, every core control and every deciding
   rv control. The same gap applies to other full-log witnesses. This violates the sealed
   missing-fields refusal and full-log frame integrity requirements.

4. **Criterion 3 can belong to stale cached data.** `bf99.py:207-214` calls inherited
   legacy scoring without establishing that area_<tag>.csv was generated from the current
   raw log. `calibration_binding` reuses this at line 269; `m3_99.py` directly invokes bf99.
   Independent reproduction: create valid area CSV, double all armed raw rt_kpx values,
   leave CSV untouched. Criterion3 remains VALID and inherited kept controls remain 4/4.
   Regenerate CSV from the same raw file and criterion3 becomes INVALID. accept99 refreshes
   the measurement CSV but does not protect direct scorer or calibration replay paths.

5. **Explicitly inconsistent metadata is accepted.** `bf99.protocol` validates schedule
   against env/actual arms, but ignores the metadata arms list. The fixture with reversed
   mode3 metadata arms and a mode2 schedule returns protocol=[] and all core/rv PASS.
   Sealed section 3 explicitly refuses inconsistent metadata.

Additionally, survival has no raw-log duration/hold-anchor check: protocol and inherited R1
only validate metadata hold_s/hold_exit. The fixture with 134.4 seconds of reported dt and
claimed 300-second hold passes survival. Real metadata has stable_frame, which could anchor
the promised log evidence. This is a verification gap against section 3's metadata AND log
evidence requirement; the exact timing tolerance should remain tied to the sealed protocol.

## Checks that passed

- All 18 supplied offline tests passed (`test_results.txt`). They do not cover the defects above.
- New endpoint subtracts burn in mode2; actual paired-block estimator reproduces the old raw
  endpoints: bf98a 14.274068801724138 ms, 128 pairs; bf98c 12.825411375615763 ms, 122 pairs.
- Raw rv98a and warmup reproduced 432+425=857 falling edges and all selected R controls.
- Protocol enforces calibration hold180/no warmup/initial12000 and measurement hold300/
  warmup+attempt1 metadata labels, mode2/clear0/latch1/pin1, pinned binary/pre-registration,
  schedule period/start/ABBA; controls enforce >=10 pairs and rv >=30 falls.
- m3 requires both instruments and has no subtraction fallback, no global closure/licence.
- Mechanics-only is explicitly non-admitting. Counterexamples were evaluated as components;
  no fixture was presented as real ADMITTED measurement.
- Reviewed scorer paths read canonical raw logs; the new paths use no --log override and
  calibration artifacts use exclusive creation. accept99 is scoring-only.

Reproductions and raw fixture logs are in `counterexamples.py`, `counterexamples.txt`, and
the corresponding *_rv.txt / area_*_legacy.txt files. Historical recount is in
`old_raw_recount.py` and `old_raw_recount.txt`.
