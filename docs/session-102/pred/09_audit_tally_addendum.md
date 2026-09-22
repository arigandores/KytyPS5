# Sealed addendum 09 to pred/08 — session 102: the lens tally of pred/08 §0 is wrong in one place; the withdrawal stands

**Immutable once written.** `pred/08_audit_addendum.md` (6 464 B, `ee7e3397…`) is NOT edited.

`pred/08` §0 says "Protocol: REFUTED. Fidelity: REFUTED." The audit workflow was interrupted by a usage
limit after three of its five lenses had returned (recount, protocol, claims); on resume, the harness
re-ran every lens after the first failed one, so **the protocol and claims lenses each ran twice**:

| lens | run 1 | run 2 |
|---|---|---|
| recount | NOT REFUTED | — (cached) |
| instrument | — (limit) | NOT REFUTED |
| fidelity | — (limit) | **REFUTED** |
| protocol | **REFUTED** | **NOT REFUTED** |
| claims | NOT REFUTED | NOT REFUTED |

Both protocol runs report the same decisive defect — `pred/02` changed the verdict composition and was
not recorded in `ROADMAP.md` first — and differ only in whether they call it refuting. `pred/08` quoted
run 1 without saying a run 2 existed. **Correct tally: one lens REFUTED in both of its runs' senses
(fidelity), one lens split (protocol, REFUTED then NOT REFUTED on the same defect), three NOT REFUTED.**
All seven reports are archived verbatim in `C:/kyty/s102/audit102/audit_<lens>_run<k>.txt`.

**The withdrawal of "M5 closes G" stands on two independent grounds, neither of which depends on the
tally:** fidelity's defects B1–B3 (the pixel-shader fault store, the doubled table reads — V2 prices
machinery the seals did not name), and the recording defect A, which the executor applies as
withdrawing a licence by the precedent of sessions 100 and 101 (`ROADMAP.md` §0.1, §5 item 5), whether
or not an auditor labels it refuting.

**A second correction, of scope:** X and Y are computed over **eight** items (S2–S7, S9, S10; S1 and S8
fail V-e for V2), L and V2s/A over all ten. Over the same eight items L = 1.0277 (Δ 90 % CI
[0.0239, 0.0331]) and V2s/A = 1.0653. Neither moves a branch of `pred/02` §3 (L stays below 6 %).
