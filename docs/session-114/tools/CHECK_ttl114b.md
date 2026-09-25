# CHECK - adversarial check of the ttl114b draft (seal 02b, session 114, ROADMAP item 8)

Checked on 2026-09-25. No game run, no build, no git write, no full mutation run. I ran the fixture suite on the draft
scorer and on three cap mutants I made by hand, and regenerated the draft twice. All my files are in `check/`, and I
deleted the fixture folders afterwards (4 x 4.0 GB).

The files on disk match the drafting report:

| file | sha256 | bytes |
|---|---|---|
| `ttl114b.py` | `4ec1a45203c98a86c18130a32c68af0dec4af7d3657344f509287b60c7ee41a0` | 51250 |
| `test_ttl114b.py` | `7981778aeb1fa7d6fb625991f739a3993b4e14499a3cac0cc1b33bb5098c8928` | 92927 |
| `mut_ttl114b.py` | `79009aa3dcc9cf153c35d11c25268bf19056d42c4ec024a991f2a35b524c4b0d` | 44784 |
| `make_ttl114b.py` | `a6342c6c89f516c3ca63a812101a77bc4a09a2cb09598481c2b023e4f91cc745` | |
| inputs `C:/kyty/s114/{ttl114,test_ttl114,mut_ttl114}.py` | `b8459c3d…` / `0edede85…` / `951783ba…`: equal to the pins in the generator and to `SEALS114.txt` seal 02 | |

**Verdict: PASS.** I found no MAJOR or MINOR defect. Six INFO notes are in section 6.

## 1. The scorer: `ttl114.py` → `ttl114b.py`, whole diff (difflib and `diff`, 7 hunks)

| change | lines (new) | allowed by item 8 / the brief? |
|---|---|---|
| New seal-02b header paragraph in the docstring. The old first line continues unchanged at :12. | 1-12 | Yes: docstring only. Its facts match `runs114/ttl114_score.json`: walls `[168467.85, 21420.96]` ns, NOT_ADMITTED on TITLE_ARMED alone. "ROADMAP s0.1" is correct: the session-114 records sit under `### 0.1`. |
| `sealed to pred/02b_ttl114b.md` | 17 | Yes (the pre-registration) |
| Usage lines are now `ttl114b.py ttl114b` / `ttl114b.py <tag>` | 25-26 | Docstring only. See INFO-1. |
| `TITLE_ARMED (... <= TITLE_WALL_MAX_NS = 60 000 ns and` | 45 | Yes |
| `PRED = 'C:/kyty/s114/pred/02b_ttl114b.md'`; `PRED_SHA = None` / `PRED_BYTES = None` with the comment `# filled by the executor when pred/02 is sealed` | 66-68 | Yes. The text is byte-equal to the draft `ttl114_draft/ttl114.py:56-57` (I checked). |
| `TITLE_WALL_MAX_NS = 60000  # ... (s114 item 8)` | 86 | Yes |
| P2 `'arm-1 per-call wall of UpdateTitle <= 60 us a call (titleasync=1 posts without waiting)'`, `us[1], None, 60` | 788-789 | Yes |

Nothing else differs. The following are unchanged: SHIP_US 50.0, S2_US 200.0, SIZE_LABEL, the TITLE_ARMED expression
(`walls[1] <= TITLE_WALL_MAX_NS` and strictly below arm 0, :524), TITLE_COUNTED, DEFAULTS_ON, the schema, ENV_EXPECTED,
ARMS / SCHEDULE, TAG_RE `ttl114b?(?:_entry1)?`, the video pass, `must_not_be_claimed`, and every message (`out['scorer']
= 'ttl114.py'`, the summary header, "size into ttl114.py", the tag refusal). The summary's cap line prints the constant
(:864), so it now reads 60000. I found no other literal 20 000 / 20 µs in the scorer. The two `(s114 item 5)` comments
left on SHIP_US / S2_US belong to the rule, which does not move.

## 2. Fixtures: `test_ttl114.py` → `test_ttl114b.py`

- The case lists are identical: 249 cases, same names, same order, no duplicates. I compared the two suite outputs line
  by line. The only differing line is `REFUSE_out_exists`, whose text contains the fixture path (`ttl114_draft` →
  `ttl114b_draft`).
- **My run of the draft**, `python -B test_ttl114b.py ttl114b.py check/fx_base`, printed **249 cases, ALL OK**, rc 0,
  in 5 min 57 s. Its output equals the draft's `test_ttl114b.out.txt` apart from the `rc=` line I appended.
- Every fixture that depends on the cap or the band moved, and each keeps its intent:

| case | old | new | intent kept |
|---|---|---|---|
| PRED_BANDS P2 | `[None, 20]` | `[None, 60]` | yes. `pred_values` compares all seven bands exactly, so any P2-band mutant fails every case that calls it. |
| TITLE_ARMED_edge | 20000 → PENDING, P2 20 hit | 60000 → PENDING, P2 60 hit | yes (the edge passes) |
| TITLE_ARMED_out | 20001 → KEEP_NA, TITLE_ARMED alone, P2 20.001 miss | 60001, same outcome | yes |
| TITLE_ARMED_percall | 30000 / 2 calls = 15000 (raw above the cap) | 90000 / 2 = 45000 (raw 90000 above 60000) | yes |
| TITLE_ARMED_percall_out | 40002 / 2 = 20001 | 120002 / 2 = 60001 | yes |
| PRED_edges_hi / PRED_misses_hi | arm-1 wall 20000 / 20001 | 60000 / 60001 (P2 60 / 60.001) | yes |
| LEVEL_median outlier (arm 1, block 17) | 2 000 000 | 7 000 000 | yes. Recomputed: (7e6 + 109·3000)/110 = 66 609.09 over 109/110 = 67 220.2 ns a call, above 60 000 (P2 67.2 misses). The old value would read 21 348.6: above the old cap, below the new one. |
| pred_good summary cap line | `(arm-1 cap 20000 ns)` | `(arm-1 cap 60000 ns)` | yes |
| CONSTANTS PRED | `pred/02_ttl114.md` | `pred/02b_ttl114b.md` | yes. CONSTANTS does not compare TITLE_WALL_MAX_NS, and never did. PRED_SHA/BYTES are still accepted as "both None or a sha and a size". |

- I checked every other value that touches the cap and none of them falls between the two caps: the good run's 3000;
  500 (PRED_edges_lo / misses_lo); 15000 / 15001 (equal / below / arm0_faster); 3000/0.9875 = 3038 (TITLE_COUNTED);
  3100 (lag0); a full-block level of 224 889 (lag1, still above 60000). So no unchanged fixture tests anything
  different under the new cap.
- **The cap edges catch a moved cap on their own, not only through the summary line.** I made three mutants by hand
  and ran the plain suite on each. The plain suite does not stop at the first failure, so it lists every failing case.

| cap mutant | failing cases (all of them) |
|---|---|
| 59999 | PENDING (summary line), **PRED_edges_hi, TITLE_ARMED_edge** |
| 60001 | PENDING, **PRED_misses_hi, TITLE_ARMED_out, TITLE_ARMED_percall_out** |
| 20000 (ttl114's cap) | PENDING, **PRED_edges_hi, TITLE_ARMED_edge, TITLE_ARMED_percall** |

  This settles the drafter's open point: the `--only` run showed only the first killer, PENDING.

## 3. Mutants: `mut_ttl114.py` (draft list, 344) → `mut_ttl114b.py` (347)

I checked this with my own script, `check/check_mut.py` (output in `check_mut.out.txt`). It extracts the mutant dicts
without the generator's code.

- The sealed list `mut_ttl114_sealed.py` (342) is the draft list without CONST_pred_sha_prefilled and
  CONST_pred_bytes_prefilled. The other 342 entries are byte-equal to the draft list's.
- Four names were dropped, and each was replaced one-for-one by a renamed mutant making the same edit on the new value:
  TITLE_WALL_MAX_19999 → _59999, _20001 → _60001, PRED_P2_hi_19 → _hi_59, _hi_21 → _hi_61.
- Five mutants kept their names but have new anchors: TITLE_WALL_MAX_in_us (60000 → 60), PRED_P2_arm0, PRED_P2_bounded,
  CONST_pred_shn113 and CONST_pred_ctl114 (on the new PRED).
- Three were added beyond the brief: TITLE_WALL_MAX_20000, PRED_P2_hi_20 and CONST_pred_ttl114. Each restores one of
  ttl114's values.
- The other 335 are byte-equal to the draft list's. For each of them, the anchor occurs exactly once in `ttl114b.py`,
  on the same line as in `ttl114.py` under the difflib line map (multi-line anchors checked line by line). **No anchor
  moved onto another line.** This matters because an anchor such as "(s114 item 5)" would have landed on S2_US.
- The two draft-only seal mutants apply again: `PRED_SHA = None          #` and `PRED_BYTES = None        #` each occur
  once. Like seal 02, they will not apply to the sealed copy, and the executor drops them there.
- Every mutated scorer compiles.
- The `--only` output (`mut_only.out.txt`: mutlib v2 `877eb53a`, which is the frozen copy in SEALS114): 102 of 102
  killed, 0 by a crash, controls 3 of 3 survived, baseline survived. I cross-checked the selection against the sealed
  run `C:/kyty/s114/mut_ttl114.out.txt`, and for the two draft-only mutants against the draft run
  `ttl114_draft/mut_ttl114.draft.out.txt`:
  - All 38 mutants whose first killer there was a changed case (CONSTANTS, LEVEL_median, PRED_edges_hi,
    PRED_misses_hi) are in the selection.
  - None of the 344 had TITLE_ARMED_edge, _out, _percall or _percall_out as first killer.
  - For every selected mutant that existed before, the first killer is unchanged. The new names are killed by PENDING
    or CONSTANTS, like their ttl114 counterparts.
- The 245 mutants that were not re-run: the scorer change only affects a wall in (20 000, 60 000] ns or a P2 value in
  (20, 60] µs, and no unchanged fixture produces one (section 2). I also went through the title, wall, level and schema
  mutants that were not re-run. They act on the counted-call check, the schema, gate texts or labels, not on the wall
  value against the cap. The full run on the sealed copy remains the executor's.

## 4. Generator `make_ttl114b.py`

- Its inputs are pinned by their full sha256 and checked for CR. Every anchor is asserted to end with a newline, start
  at a line start, occur exactly once in the current text and differ from its replacement. Replaced lines must be ≤ 120
  characters or no longer than the line they replace. There are forbidden-leftover and required-once lists, and a
  `compile()` of each output.
- On the mutant list, it asserts 344 → 347, the name sets, that unchanged mutants are byte-equal, that every anchor
  occurs once in `ttl114b.py`, and that the changed mutants compile.
- **Byte-reproducible:** I ran it twice into `check/regen1` and `check/regen2`, changing only OUT. Both runs gave the
  three outputs byte-equal to the draft's, with the same sha256 and sizes. The outputs are LF-only, UTF-8 without BOM,
  and end with a newline. The longest line is 121 characters, and it is an unchanged sealed line in both files.

## 5. State

- Machine before my runs: no `kyty_emulator` running, CPU ≈ 0 %, GPU 0 %. The chain `go114b.sh` had finished
  (`[03:14:12] done`).
- `pred/02b_ttl114b.md` does not exist yet (expected: this is a draft).
- Nothing outside `C:/kyty/s114/ttl114b_draft/` was written.
- My leftovers in `check/`: outputs, `check_mut.py`, `make_regen{1,2}.py` and `regen{1,2}/`, and the three
  `ttl114b_cap*.py` mutants.

## 6. INFO

1. **Usage lines.** They now name `ttl114b.py ttl114b`. This is docstring only: no behaviour, fixture or mutant depends
   on it. It departs from the literal wording of brief rule (4), but the drafter's reading holds: kept as is, the usage
   would tell the executor to run the old sealed scorer. I recommend keeping it.
2. **Messages keep ttl114's names.** `out['scorer']` is `'ttl114.py'`, and the summary header starts `ttl114.py <tag>`,
   even though the file is `ttl114b.py`. The brief requires this, and `pred_good` and the SEAL_msg/TAG_msg mutants
   depend on it. The scorer's identity in the result is `scorer_sha256` of the file that ran. pred/02b should say so, so
   that nobody reads `'ttl114.py'` in `ttl114b_score.json` as the old scorer.
3. **P2's text is not checked by any fixture** (only its band and value; P6's text is checked). This gap is inherited
   from ttl114 and was not introduced here. I read the text myself (:788) and it is correct: "<= 60 us".
4. **The three added mutants are beyond the brief.** They strengthen the suite: they prove it tells ttl114b from
   ttl114. All three were killed. The only-list also includes TITLE_ARMED_cap_on_arm0 (killed by SHIP).
5. **The header's sentence "its pre-registration and its cap updated"** leaves out the usage lines, which were also
   updated. This is cosmetic.
6. **pred/02b must restate the rule unchanged**: S1 ≤ +50, S2 Δ+2·SE ≤ +200, control 01 PASS (in text only, as ttl114's
   MINOR-1), video. It must also state the new arming (60 000 ns and strictly below arm 0) and P2 ≤ 60 µs, and say
   honestly that the cap was chosen after ttl114's walls were seen, as ROADMAP item 8 records.
