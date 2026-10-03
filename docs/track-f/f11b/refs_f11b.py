# F11b: anchor and +1 control for the document references of f11b-review.md (rule 24(1)).
import subprocess
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('18d9c792', 'docs/ROADMAP.md', 20029, '369. **Звено F10b трека F (`HPP-446`, лид): F10a (`HPP-445`) принят', '`KYTY_FIX_SVAL` (умолчание 0) с критерием «ИСПРАВЛЕНО Ф16» ниже; звенья F10c'),
    ('18d9c792', 'docs/ROADMAP.md', 20096, 'пунктом и звенья кода и прогонов. **Правило вывода Ф10 (решено сейчас, применяется лидом после прогонов F11):**', 'нарушений `size` > 0 хоть в одном теге — «дефект достижим»'),
    ('b53451c2', 'docs/ROADMAP.md', 20219, '372. **Звено F11a трека F (`HPP-455`, Emu Engineer): ответ лида на вопрос по члену (4) — вариант (в)', '`enemy_final_600.rdc`) выносится из F11a в новое звено F11a2'),
    ('8f71d516', 'docs/track-f/f11a.md', 217, 'циклом в эмиттере нет. Счётчики ГП живут в хвосте буфера промахов и обнуляются вместе с ним (`m_fault_buffer.Fill`,', '`faultManager.cpp:93`). Хостовые `uint64_t` накопители'),
    ('8f71d516', 'docs/track-f/f11a.md', 224, '(б) **GPU-тест** `shader_recompiler_compute_tests --diag-bvh-only`', 'вызовы с указателем каждого типа и один с `ptr >> 3 = N + 5`'),
    ('8f71d516', 'docs/track-f/f11a.md', 90, '- **Определение проекта [I]:** нарушение `size` — исполнение с 32-битным указателем, где `ptr >> 3`', '`size64 = слово2 | (слово3 & 0x3ff) << 32`. Единица `numNodes` в PAL — [U].'),
    ('8f71d516', 'docs/track-f/f11a.md', 210, 'против формы трека «код — `main`» (п. 228(в)). **(М3, предлагается)** коммит диагностики в `main`,', 'до любой сборки отгрузки. Если между ними транслятор не менялся'),
    ('8f71d516', 'docs/track-f/f11a.md', 168, '`GroupNonUniformBallot` в модуле уже бывает', '`EmitDiagTrap` — то же для одного слова `traps` (дорожки с `active`).'),
    ('8f71d516', 'docs/track-f/f11a.md', 309, '4. Тип 6 (§0 п. 5)', '5. Часть `S_TRAP` (§7): 14 из 538 в T1, 20 из 5 698'),
    ('8f71d516', 'docs/track-f/f11a.md', 306, '3. Сцена без BVH и положительный контроль: если `enemy_final` даст `lanes = 0`', 'Нужна ли поправка лида (сцена без исполнений BVH выбывает из множества сцен правила)'),
    ('3adc4573', 'docs/track-f/f3d.md', 30, '| `f3d_a1` | `big_hand_pirate_island` | 1 |', '| `f3d_a2` | `big_hand_pirate_island` | 1 |'),
    ('3adc4573', 'docs/track-f/f3d.md', 36, '| `f3d_c1` | `big_hand_pirate_island` | 0 | контроль | **CONTROL RETURNS** |', '| `f3d_c2` | `voxel_world` | 0 |'),
]
ok = True
for c, p, n, a, b in REFS:
    lines = subprocess.run(['git', '-C', REPO, 'show', c + ':' + p], capture_output=True).stdout.decode('utf-8').split('\n')
    la = lines[n - 1] if n - 1 < len(lines) else ''
    lb = lines[n] if n < len(lines) else ''
    r = (a in la) and (b in lb)
    ok &= r
    print(('OK  ' if r else 'BAD ') + c + ':' + p + ':' + str(n))
print('ALL OK' if ok else 'FAIL')
