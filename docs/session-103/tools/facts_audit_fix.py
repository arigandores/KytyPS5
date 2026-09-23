p = 'C:/kyty/s103/FACTS.md'
b = open(p, encoding='utf-8').read()


def rep(old, new):
    global b
    assert b.count(old) == 1, (old[:80], b.count(old))
    b = b.replace(old, new)


rep("# Session 103 — the BVH loop cap stops the entry hang (0 of 67) but its series is NOT ACCEPTED by one sealed item; M5′ CLOSES G; the presence class is fixed in the translator",
    "# Session 103 — the BVH loop cap: 0 entry hangs in 67 but its series is NOT ACCEPTED (A3); M5′ CLOSES G on an upper bound; the presence class is fixed in the translator")
rep("""> **AUDIT: see §8** (written after the adversarial audit; any withdrawal is recorded there and in a
> sealed addendum).""", """> **This report was written after a four-lens adversarial audit** (§8; sealed `pred/04_audit_addendum.md`,
> 4 345 B, `cdc9bab4…`). Recount NOT REFUTED; code REFUTED narrowly on one descriptive claim (withdrawn:
> "trips always cover whole dispatches"); fidelity NOT REFUTED on the CLOSE but REFUTED on its size
> (**X′ is an upper bound**); protocol NOT REFUTED with one MAJOR disclosure (**the M5′ offline builds ran
> during the sealed series**).""")
rep("""trips in 7 entries** (05, 22, 30, 32, 36, 42, 49; 2 875 168 invocations, always whole dispatches
   over a few consecutive readbacks), worst frame 0.347 s.""", """trips in 7 entries** (05, 22, 30, 32, 36, 42, 49; 2 875 168 invocations over a few consecutive
   readbacks, all in frames 188–197 — the level-entry transition — often but NOT always whole
   dispatches), worst frame 0.347 s.""")
rep("""   Outside trip episodes `bl_near` = 0 in all 67 entries. Historical entry-hang rate 6.67 % ⇒
   ≈ 4.5 hangs expected; P(0 | 6.67 %) = 0.0098.""", """   Outside trip episodes `bl_near` = 0 in all 67 entries (a post-hoc slicing, not a sealed item).
   Historical entry-hang rate 6.67 % ⇒ ≈ 4.5 hangs expected; P(0 | 6.67 %) = 0.0098 — but `pred/01` §4
   licenses a rate statement only for an ACCEPTED series, so none is claimed. **Disclosed (audit, MAJOR):
   the M5′ offline builds (tests exe, spirv-val, pipestat driver compiles, nvdisasm) ran during up to 53
   of the 67 counted entries and the video pass, against the seal's "GPU otherwise idle".**""")
rep("""3. **M5′ (sealed `pred/02` + `pred/03`): G CLOSED.** X′ = S[V2′]/S[A] = **1.2934** (90 % CI of
   X′ − 1: [0.2910, 0.2946]) over eight items (S1, S8 fail V-e for V2′), every control V-a…V-g PASS;
   L = V1/A = 1.0201 ([0.0182, 0.0230], all ten); A/B = 1.0027. The rule (ROADMAP §0.1, recorded
   before any work): CI_lo(X′ − 1) > 0.06 ⇒ G CLOSED.""", """3. **M5′ (sealed `pred/02` + `pred/03`): G CLOSED by the recorded rule — on an UPPER bound.** X′ =
   S[V2′]/S[A] = **1.2934** (90 % CI of X′ − 1: [0.2910, 0.2946], bench noise only) over eight items
   (S1, S8 fail V-e for V2′), every control V-a…V-g PASS; L = V1/A = 1.0201 ([0.0182, 0.0230], all ten);
   A/B = 1.0027. The rule (ROADMAP §0.1, recorded before any work): CI_lo(X′ − 1) > 0.06 ⇒ G CLOSED.
   The audit showed V2′ still carries removable machinery (the page-crossing slow path, the per-group
   dword fallback, the run-time alignment test on PER-LANE addresses, repeated page lookups); its
   estimate for G without them is **1.09–1.17 [I]**, still above 1.06 — the CLOSE rests on that
   inference, and it covers G with a page-table BDA path only.""")
rep("""**Inference, not proven:** every trip episode spends whole dispatches (every invocation of 2 048
groups × 64), consistent with invalid acceleration-structure data during level load; the abort
path flushes the BDA fault page, which lets the host cache the missing page, and the episodes end
within ~5 readbacks — a mechanism the uncapped shader, which never returned, could not reach.""", """**Withdrawn by the audit:** "every trip episode spends whole dispatches" — entries 22, 30 and 49 have
readbacks that are not multiples of a dispatch (`ent103_30`: 149 536 = 2 336.5 groups of 64, so in
some groups one wave tripped and the other finished), and with it the inference "invalid
acceleration-structure data during level load". What stands: all trips fall in frames 188–197 (the
level-entry transition, before the scene is stable at 285–333) and the episodes end within a few
readbacks. Whether the abort's BDA fault flush (which the uncapped shader never reached) is what ends
them is **not shown**; the fault-bit store it goes through is non-atomic (pre-existing).""")
rep("""## 8. Adversarial audit

(pending)""", """## 8. Adversarial audit (sealed `pred/04_audit_addendum.md`)

Four lenses, each told to refute, reports in `C:/kyty/s103/audit103/`:
* **Recount — NOT REFUTED.** Own code reproduced every number of §2–§3 to 4 decimals, the item↔event
  map (3 355 events), the Williams order of all 20 rounds, and found no FrameTrace-x line lost around
  the trips. Observed: V2′ has more zero-duration events than A (the excess is not shifted between
  events: +2 784 µs on item events vs +2 822 µs whole capture); round 0's ratio 1.2165 is an outlier
  (the median is unaffected); on S1 V2′ flips one byte of an 8 MiB buffer bound in both arms (probably
  the fault buffer — a real read fault, inferred).
* **Code — REFUTED narrowly** on "trips always whole dispatches" (withdrawn above); no code defect
  invalidates a verdict. Minor: the tail copy is not ordered against later atomics (per-readback
  attribution can split, totals exact); `bl_*` read 0 without FrameTrace or with `fslean=1`; 32-bit
  wrap stops the counters; a set entry without a fault binding would trip uncounted; `strtoul`
  parsing (`=true` turns the cap off, `=1` aborts at the first header); `KYTY_LOOP_LIMIT` is replaced
  by the cap for capped programs.
* **Fidelity — NOT REFUTED on the CLOSE, REFUTED on its size** (§1 item 3). Removing the slow path and
  the dword fallback in the SPIR-V: S4/S5/S8 128 → 96 registers, PS binaries −29…−36 %. Per-lane
  alignment branch confirmed in S7's SASS (`@P0 LDG.E.128` / `@!P0` three `LDG.E` for a 12-byte
  stride). Lookups repeated per block (S4 63 lookups for 16 V#s). The rule's explicit items are met
  (null base read once, no `STRONG`, no PS `STG`, `.CONSTANT` loads).
* **Protocol — NOT REFUTED**, one MAJOR (the builds during the series, §1 item 1) and minors: the
  cap/env code was written (not only drafted) before the ROADMAP record but first built after it; the
  M5′ amendment changed "constant null base" to "once per invocation" and silently dropped "no reloads
  after stores" (both bias toward CLOSE); the keep-ON decision is not a breach but its rate sentence
  over-reached (withdrawn); the M5′ scorer checks `pred/02` and its parents, not `pred/03`; the pre-fix
  identity sweep's output was overwritten (the "13 programs differed" statement has no artefact).""")
rep("""**Proved.** 0 entry hangs in 67 entries with the cap (rate < 6.67 % at ~99 % confidence); the cap
trips in episodes of whole dispatches and the entries survive. The BDA path with the recorded G
properties costs +29 % on eight top Sky Garden shaders (> +6 % ⇒ G CLOSED by the recorded rule).""", """**Observed/measured.** 0 entry hangs in 67 counted entries with the cap (no rate is licensed: the
series is NOT ACCEPTED, and the M5′ builds ran during it); the cap tripped in 7 entries during the
level-entry transition and every entry survived. V2′ — the BDA path with the recorded G properties
plus removable machinery — costs +29.3 % on eight top Sky Garden shaders: an upper bound; G CLOSED by
the recorded rule, resting on the inference (1.09–1.17 [I]) that G without the artefacts still exceeds
+6 %. **ROADMAP §6:** the session's one real-path change did not pass its sealed A/B-equivalent.""")
rep("""**Not proved.** That the cap is accepted (A3 failed); that the hang mechanism is the one inferred;""",
    """**Not proved.** That the cap is accepted (A3 failed); what the hang mechanism is;""")
open(p, 'w', encoding='utf-8').write(b)
print('ok')
