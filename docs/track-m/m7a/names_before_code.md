# M7a (HPP-852): names fixed BEFORE the code (ROADMAP s122 item 767(g)(3))

Written before any edit of src/ in the worktree C:/kyty/m657/m7a/wt (MS1 ed94b13d); time - times.txt.

1. Fallback line of T306 (the "previous path" line, member (g)(3)): the EXISTING line of
   spirvEmitterImage.cpp (MS1, Track M M2a), unchanged text:
   `MTexOffset: shader=0x<hash16> pc=0x<pc> nonconstant offset, previous path`
   One line per IMAGE_SAMPLE_*_O instruction whose offset is not proven constant for every executing lane
   (forms `other`, `full`, `lit` at KYTY_M_T306=1). The other two lines of the theme stay as they are:
   `MTexOffset: shader=0x<hash16> pc=0x<pc> offset=0x<packed> previous path (cube|range)`.
2. Counter of those lines (read by shader_cfg_tests, no knob, process-wide, incremented in the same branch as the LOGF):
   `Spirv::MTexOffsetFallbacks()` -> {nonconstant, cube, range}.
3. Test probe (off unless a test turns it on): `Spirv::MTexOffsetRecording(bool)`, `Spirv::MTexOffsetTakeRecords()` -
   one record per emitted sample with ConstOffset: shader hash, pc (bytes), SPIR-V result id of the sample, id of the
   ConstOffset constant.
4. IR mark of the wrapper: `IR::MSampleOffsetWrapperFlags` (flags of SelectU32), `IR::IsMSampleOffsetWrapper(inst)`;
   ConstantPropagation does not fold that select by its condition.
5. Test names: `TestMWave1T306OffsetWriteMask` (extended: forms same / other / full / lit, fallback-counter members),
   `TestMWave1T306EbootPrograms` (7b4078750f32db50, b912bcf29000558d from the words of eboot.bin, path by
   `KYTY_TEST_T306_EBOOT=<dir>`; without it the test prints SKIP and does not fail).
6. KYTY_RECOMPILE line of the oracle: env `KYTY_RECOMPILE_T306=1` -> after the compile one line per record
   `recompile-t306: pc=0x<pc> x=<x> y=<y> z=<z> path=const` (decoded from the SPIR-V words of the module) and
   `recompile-t306-fallback: nonconstant=<n> cube=<n> range=<n>`.
7. Mutants (mut_m7a.py): `t306_mask` (M2c line, unchanged), `t306_full` (ConstantPropagation folds the wrapper again),
   `t306_silent` (the nonconstant branch drops the offset without the line and without the count).
