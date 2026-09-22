# Sealed addendum 06 to pred/04 — session 102: the entry-failure clause pred/04 omitted, written after an ENTRY failure and before any admitted run

**Immutable once written.** `pred/04_checkpoints_fix.md` (4 221 B, `c131852e…`) is NOT edited.

`ckpt102` attempt 1 hung on ENTRY, before the scene was stable: `GpuHangAbort: role=4 requested=5219
known=5218 … after=8s` at about 13–20 s, `nvlddmkm` event 153 at 22:48:11 (the TDR), no settled frame
exists, so no quantity of pred/04 §2 items 3–5 was measured. This has the signature of the historical
entry hang of the programme (role=4, requested − known = 1; 6.67 % of entries, the uncapped BVH
traversal `380bb9d6…` named in sessions 98 and 100), which session 102 does not touch.

pred/04 carries no entry-failure clause; its siblings do (pred/03 §4, and every session-99–101 seal):
**an entry hang is an ENTRY failure, recorded separately, and ONE further isolated attempt is taken
under the same protocol and budget, named `<tag>_entry1`, never a re-score.** That clause is adopted
here for pred/04: the witness is `ckpt102_entry1`, with the identical command line of pred/04 §1 and the
tag changed. If it also fails on entry, the witness is NOT taken this session and the fix is reported
as verified only at the log level (the two lines below), not by pred/04 §2.

Reported from the failed attempt, deciding nothing: its log already carries
`Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)` (once), no `GPU checkpoints mode=` line, and
`RecordThread: started`, i.e. pred/04 §2 items 1 and 2 held before the hang.
