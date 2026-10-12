"""M1a: knobs.md - shipped knobs (23 FIXED rows of track F register + track S + track P) -> files at b3dc9c67."""
import subprocess, os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
GIT = 'C:/Program Files/Git/cmd/git.exe'
K = [
    ('KYTY_FIX_B1B', 'Б1а, Б1б, Ф9', 'BVH: IMAGE_BVH_INTERSECT_RAY читает узлы по адрес>>8; ограничитель KYTY_BVH_LOOP_CAP (Б1а)', 'FS1 dac02fb9'),
    ('KYTY_FIX_B4', 'Б4', 'гонка аварийного выхода FileSystem::EmergencyShutdown/CloseAll', 'FS6'),
    ('KYTY_FIX_B9A', 'Б9а', '16 неразрешённых импортов AudioPropagation', 'FS2'),
    ('KYTY_FIX_B12', 'Б12', 'SynchronizeBuffersByRegion: свидетель региона 4 МиБ vs кусок диапазона (BDA)', 'FS11'),
    ('KYTY_FIX_B13', 'Б13', 'ChangeState<Cpu,true>: порядок публикации эпох (BDA)', 'FS9'),
    ('KYTY_FIX_B24', 'Б24', 'вывод пада через поток PadOutput (замок джойстиков SDL)', 'FS7'),
    ('KYTY_FIX_B26', 'Б26б', 'S_BREV_B64, V_CMP_LE_U64', 'FS1 dac02fb9'),
    ('KYTY_S_PCW', 'Б33 (трек S)', 'запись кэша пайплайнов драйвера вне m_mutex', 'S12'),
    ('KYTY_FIX_DUALSRC', 'Б35', 'dual-source blend: включение dualSrcBlend, перепись выхода PS Location 1 -> Location 0 Index 1', 'FS1 dac02fb9'),
    ('KYTY_FIX_MINIMIZE', 'Б37', 'пересоздание swapchain при нулевом размере окна', 'FS2'),
    ('KYTY_FIX_B42', 'Б42', 'вода Sky Garden: вход PS держал память 4K-поверхности старого кадра (кэш текстур)', 'FS3'),
    ('KYTY_FIX_F8', 'Ф8', 'SDL_InitSubSystem(AUDIO) без пары при вибрации пада', 'FS7'),
    ('KYTY_FIX_F10', 'Ф10', 'IMAGE_BVH_INTERSECT_RAY: типы узлов 2–3 как треугольники (GPURT)', 'FS5'),
    ('KYTY_FIX_SVAL', 'Ф16', 'встроенная ValidateShaderSpirv без uniformBufferStandardLayout', 'FS4'),
    ('KYTY_FIX_F19', 'Ф19', 'нативное сравнение глубины (Dref) вместо фильтр-затем-сравнение', 'FS8'),
    ('KYTY_FIX_F20', 'Ф20', 'RecordBdaFault: OpAtomicOr вместо Load/Or/Store', 'FS15'),
    ('KYTY_FIX_F21', 'Ф21', 'один владелец аварийной последовательности фатала', 'FS12'),
    ('KYTY_FIX_F24', 'Ф24', 'поток JoyPump для подсистемы джойстиков SDL', 'FS14'),
    ('KYTY_FIX_F25', 'Ф25', 'EIO при двойном отказе чтения вместо 0', 'FS13'),
    ('KYTY_FIX_B36', 'Ф27', 'асинхронный писатель лога LogAsync', 'FS10'),
    ('KYTY_FIX_F29', 'Ф29', 'ProcessFaultBuffer: предел count областей', 'FS14'),
    ('KYTY_S_REPLAY', 'трек S (S-replay)', 'перестройка кэша пайплайнов из каталога повтора', 'S18'),
    ('KYTY_PVAR', 'трек P', 'P-var: шаг симуляции игры (по выбору с KYTY_GAME_PATCH, умолчание 0)', 'P23'),
    ('KYTY_GAME_PATCH', 'трек P', 'загрузчик патча игры (по выбору)', 'P23'),
]
lines = ['# Отгруженные ручки и их файлы на `b3dc9c67` (M1a, член п. 752(г)(3))', '',
         'Строки `FIXED` реестра `docs/track-f/register.md` §129 (23, все отгружены под (B)) + трек S + трек P. Файлы — `git grep -l` имени ручки на `b3dc9c67` (место чтения переменной; места вызова гейта — по имени функции гейта).', '',
         '| ручка | строка реестра | что | отгрузка | файлы с именем ручки |', '|---|---|---|---|---|']
for k, rid, what, ship in K:
    out = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'grep', '-l', '-w', k, 'b3dc9c67', '--', 'src'], capture_output=True).stdout.decode()
    fs = [l.split(':', 1)[1] for l in out.split() if ':' in l]
    lines.append('| `%s` | %s | %s | %s | %s |' % (k, rid, what, ship, ', '.join('`%s`' % f for f in fs)))
open('C:/kyty/m657/m1a/knobs.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print(len(K))
