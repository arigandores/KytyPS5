"""F23g (HPP-593): the references of docs/track-f/f23g-review.md - <commit>:<path>:<line> with the anchor (substring of the line)
and the +1 control (substring of the next line). Prints OK/FAIL per reference and ALL OK. Run from C:/kyty/KytyPS5."""
import subprocess
import sys

R = [
    ('7030111b', 'docs/ROADMAP.md', 22809, '498. **Звено F23e трека F', '(а) **Приёмка строкой. F23c ✓**'),
    ('7030111b', 'docs/ROADMAP.md', 22812, '(в) **RC1–RC5 F23d приняты как члены ступени 2', '(г) **Ступень 2 — F23f**'),
    ('7030111b', 'docs/ROADMAP.md', 22814, '(д) **Правило исхода ступени 2 (решено сейчас, читает F23h).**', '(е) **Парковка и условие переоткрытия (RC5).**'),
    ('11311fb1', 'docs/track-f/f23f/rd_f23f.py', 192, 'def run_state(nid):', 'if nid is not None:'),
    ('11311fb1', 'docs/track-f/f23f/rd_f23f.py', 207, '# pre', 'ctrl.SetFrameEvent(eid - 1, True)'),
    ('11311fb1', 'docs/track-f/f23f/rd_f23f.py', 224, "rec['bound_ok_' + arm] = bsha == sha(blob)", "rec['sha_' + arm] = shas(stt)"),
    ('11311fb1', 'docs/track-f/f23f/rd_f23f.py', 291, 'ctrl.SetFrameEvent(eid - 1, True)', 'before = bytes(ctrl.GetBufferData('),
    ('11311fb1', 'docs/track-f/f23f/sum_f23f.py', 20, 'def tot(d):', 'return sum(v for v in d.values() if v > 0)'),
    ('11311fb1', 'docs/track-f/f23f/sum_f23f.py', 48, "g_ok = h not in INVALID_G and not neg(r.get('N_def2', {}))", "n_null = tot(r.get('N_def2', {}))"),
    ('11311fb1', 'docs/track-f/f23f/sum_f23f.py', 50, "refs_eq = tot(r.get('N_mask_vs_mem', {})) == 0", "n_diff = tot(r.get('N_mask', {}))"),
    ('11311fb1', 'docs/track-f/f23f/sum_f23f.py', 56, "n_null2 = tot(r.get('N_orig_def', {})) if same_bytes else 0", 'valid = bool(a_exec and b_ok'),
    ('11311fb1', 'docs/track-f/f23f/sum_f23f.py', 63, "counters_ok = bool(dg) and dg.get('bound_ok') and n_entry > 0 and selfc == 0", 'row = dict(cap=cap'),
    ('11311fb1', 'docs/track-f/f23f.md', 27, '| Место задействовано для формы H (`n_t` > 0) на годном событии |', '| `n_t` > 0 и `n_f` > 0 на годном событии |'),
    ('11311fb1', 'docs/track-f/f23f.md', 176, '| Снимок | EID | Программа | (а) | (б) | (в) | (г) | `n_entry` |', '|---|---|---|'),
    ('11311fb1', 'docs/track-f/f23f.md', 203, '| k05 | 83214 | `be4c35a2031fd3f4` PS |', '| k05 | 83338 | `be4c35a2031fd3f4` PS |'),
    ('11311fb1', 'docs/track-f/f23f.md', 204, '| k05 | 83338 | `be4c35a2031fd3f4` PS |', '| k05 | 86604 | `0078153a1c1fb171` CS |'),
    ('11311fb1', 'docs/track-f/f23f.md', 212, '| k05 | 122458 | `be4c35a2031fd3f4` PS |', '| k05 | 125834 | `0078153a1c1fb171` CS |'),
    ('11311fb1', 'docs/track-f/f23f.md', 280, '- **`sens` > 0** на всех годных событиях с задействованным местом', '`N_diff` = 0 там не пустое.'),
    ('11311fb1', 'docs/track-f/f23f.md', 289, '`shader_data` (до исполнения — 12 байт слов счётчиков)', '22:57Z на том же событии висел'),
    ('11311fb1', 'docs/track-f/f23f.md', 299, '- **(iii)**: `N_diff` = 0 на всех годных событиях', '5 событий: `f13_rd` 1082, 2152'),
    ('11311fb1', 'docs/track-f/f23f.md', 356, '1. Второй нулевой контроль `N(orig, def)` (§5.1)', '2. 15 программ — «не определено»'),
    ('11311fb1', 'docs/track-f/f23f/sum_f23f.out.txt', 28, 'k05  83338  be4c35a2031fd3f4 ps 1 1 1 1       2334        0', 'k05  86604  0078153a1c1fb171'),
    ('11311fb1', 'docs/track-f/f23f/sum_f23f.out.txt', 36, 'k05  122458 be4c35a2031fd3f4 ps 1 1 1 1       2281        0', 'k05  125834 0078153a1c1fb171'),
    ('1ab783ef', 'docs/track-f/f23c.md', 119, 'Модель исторической формы «выборка Y читает y из результата U»', 'столбцов (94,5 %;'),
]
ok = True
for c, p, n, a, b in R:
    t = subprocess.run(['git', 'show', c + ':' + p], capture_output=True).stdout.decode('utf-8').split(chr(10))
    good = a in t[n - 1] and b in t[n]
    ok &= good
    print('%s %s:%s:%d anchor %s +1 %s' % ('OK  ' if good else 'FAIL', c, p, n, a in t[n - 1], b in t[n]))
print('refs %d' % len(R))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
