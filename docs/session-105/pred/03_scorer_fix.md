# Session 105, sealed addendum 03 to pred/02_m31.md: a scorer defect, fixed before re-scoring

`pred/02_m31.md` is not edited; no rule, threshold or control changes.

**The defect.** `ctx105.py` (derived from `lead105.py`) added `ctx_chk_n` and `ctx_chk_bad` to `DARK_KEYS`
(the control "instruments dark incl. `ctx_chk_n` = 0 in both arms" of P2) but NOT to `EXPECTED_LINE`, the
whitelist of fields its parser extracts. Every row therefore lacked the two keys, `kept_total` returned
`None`, and `INSTRUMENTS_DARK` failed mechanically ⇒ `abb105` printed INVALID ("P2 FAIL (run not
admitted)"). Nothing else failed (`failed: ['control:ARMING']`, whose only failing sub-check is
`INSTRUMENTS_DARK`).

**What the raw data say (checked before this text, with a separate script):** in `log_abb105.txt` both
fields are present on all 28 791 `FrameTrace-x` lines and sum to 0, as do `mw_n`, `a_hold_us`, `a_mut_us`,
`pl_em_n`, `pl_proc_n`, `sh_jobs`; no `CtxCheck:` line.

**The fix:** add `'ctx_chk_n': 'x', 'ctx_chk_bad': 'x'` to `EXPECTED_LINE` in `ctx105.py`; nothing else.
Re-score `abb105` once with the fixed scorer; the output file is new (`runs105/ctx105_score_fixed.json`),
the first output is kept.

**Disclosure:** the point estimate of the INVALID scoring (Δ`cpu_net` −62.6 µs, inside the 90 µs bound)
was seen before this addendum. The fix changes no arithmetic of the estimate; it only lets the sealed
control read the fields the seal names.
