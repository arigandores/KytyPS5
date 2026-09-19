"""Finalize the parent-owned narrative once both independently checked numbers exist."""
import json
from pathlib import Path

root = Path('C:/kyty/s99')
repo = Path('C:/kyty/KytyPS5')
scores = [json.loads((root / 'settled_runs' / f'{tag}_score.json').read_text(encoding='utf-8')) for tag in ('bf99g', 'bf99h')]
for score in scores:
    assert score['status'] == 'ADMITTED_SETTLED_MEASUREMENT'
    assert all(score['technical'].values()) and all(score['strict'].values())
    parent = json.loads((root / 'settled_runs' / f"{score['tag']}_parent_recount.json").read_text(encoding='utf-8'))
    assert abs(parent['B_cpu_ms'] - score['endpoints']['B_cpu_ms']) < 1e-10
values = [score['endpoints']['B_cpu_ms'] for score in scores]
assert min(values) >= 15.5
table = ['| independent confirmation | CPU endpoint ms | wall compatibility ms | work difference | technical / strict | pairs / falls |',
         '|---|---:|---:|---:|---|---|']
for score in scores:
    table.append(f"|{score['tag']} ({score['instrument']})|{score['endpoints']['B_cpu_ms']:.9f}|"
                 f"{score['endpoints']['B_wall_compatibility_ms']:.9f}|{score['metrics']['work_pct']:+.9f}%|"
                 f"{len(score['technical'])}/{len(score['technical'])} + 6/6 PASS|88 / 45|")
text = (root / 'FACTS_cont99.draft.md').read_text(encoding='utf-8')
replacements = {
    'FINAL_RESULTS_TABLE': '\n'.join(table) + '\n\nBoth confirmations ran900.3s without recording; each retains2552 rows/arm and44 AB +44 BA pairs.',
    'COMBINED_VERDICT': '**Combined: HIGH, DIAGNOSTIC ONLY**: min(B_a,B_c)=30.049869086ms >=15.5ms.\nThe requested bindings-only pair is measured on both instruments; no global M3 closure follows.',
    'FINAL_C_STATUS': 'admitted independent confirmation from exacteng99c2 LOCK',
    'FINAL_C_REVIEW': 'fresh verify99_c_raw independently confirmed c and the limited combined HIGH',
    'FINAL_PROVED': 'both bindings-only CPU endpoints, fixed-population admission, direct GC checks,\nand non-reproduction of the reported late artifacts in the separate no-floor visual control',
}
for marker, value in replacements.items():
    assert text.count(marker) == 1, marker
    text = text.replace(marker, value)
assert 'FINAL_' not in text
(root / 'FACTS.md').write_text(text, encoding='utf-8', newline='\n')
(repo / 'docs/local-session-99.md').write_text(text, encoding='utf-8', newline='\n')
archived_readme = (repo / 'docs/session-99/README.md').read_text(encoding='utf-8')
current = '''# Session 99 — bindings-only pair measured; limited HIGH diagnostic

Current source of truth: FACTS.md (mirrored in repo docs/local-session-99.md).
Both new no-record confirmations passed: bf99g(a)30.049869ms and bf99h(c)37.367904ms,
each900.3s,88 pairs and45 falling edges. Global M3 remains GAP, G/R1 unlicensed;
M4/M5 follow the user's existing order. No FPS improvement or60FPS is claimed.

The user's bf99e glitch report was checked separately: normal recorded vis99base900.3s,
17802 decoded frames,0 detector events; bf99e18037/185. The user saw no glitches in control.
Exact cause of the experimental-floor effects remains open; see VISUAL99.md.

Installed binary34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f,
23743488 bytes. Final entry point settled99_norec.py under immutable pred05. Pred01..05
and all old failures remain unchanged. No more game runs are queued for this session.

Run provenance and independently verified results: settled_runs/, verify99_confirm_raw/,
verify99_c_raw/, verify99_visual_raw/; root raw checks: parent_recount99.py.
All instructions below are HISTORICAL, superseded by current FACTS and the sealed addenda.
Next broader-M3 plan: C:/kyty/KytyPS5/docs/next-session-100.md.

'''
(root / 'README.md').write_text(current + '## Archived preparation instructions (superseded)\n\n' + archived_readme,
                              encoding='utf-8', newline='\n')
print('FACTS.md and repo mirror identical; README current preamble replaced.')
