import subprocess, sys
# (commit, path, line, anchor, plus1) - rule 24(1): anchor at line, control +1
REFS = [
    ('357d53ab', 'docs/ROADMAP.md', 19852, '366. **Звено F7c трека F (`HPP-399`, лид): F7b (`HPP-398`) принят', 'Б39 в реестр — только после враждебного отзыва Red Team'),
    ('465f0d8e', 'docs/track-f/f7d-review.md', 3, '**Вердикт: SOUND_WITH_CHANGES — 6 RC, все текстовые', 'Вывод (2) F7b годится для **материала пола**'),
    ('465f0d8e', 'docs/track-f/register.md', 155, '| Б26 | K4 | наблюдение по букве п. 228(б)', '| Ф5 | K4 | дефект по букве п. 228(б)'),
    ('465f0d8e', 'docs/track-f/f7d-review.md', 50, '**RC1 — строка `НЕ ДЕФЕКТ` должна ограничить объём', 'Что не так: вывод F7b'),
    ('465f0d8e', 'docs/track-f/f7d-review.md', 124, 'Если лид хочет покрыть освещение пола:', 'список CS (SPIR-V, привязанные образы и буферы), образ `6687` после 3455'),
    ('465f0d8e', 'docs/ROADMAP.md', 20089, '**Звено F11a** (Emu Engineer, `blocked` на F10c — один исполнитель, Ф16 раньше Ф10)', 'на настоящих данных — посещения узлов обхода по типам 0–7'),
]
ok = True
for c, p, n, a, b in REFS:
    L = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', f'{c}:{p}'], capture_output=True).stdout.decode('utf-8').split('\n')
    r = a in L[n - 1] and b in L[n]
    print(('OK  ' if r else 'FAIL'), f'{c}:{p}:{n}')
    ok &= r
print(f'{sum(1 for _ in REFS)} refs')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
