"""M1a2 (HPP-837, ROADMAP p.756(b)(1)-(6)): apply the outcomes of the M1b review to the M1a inventory.
Input: upstream.tsv / upstream_detail.tsv of M1a at KytyPS5 eee39691 (read from git, so the script is idempotent),
m1b/rc1_themes.tsv (75 themes of RC1), m1a2/signatures.tsv (mk_sig_m1a2.py), m1a2/witness.tsv (wit_m1a2.py),
m1a2/lds_m1a2.out.txt (lds_m1a2.py). Output (next to the inventory): upstream.tsv (+ column доп_тема), upstream_detail.tsv
(+ columns доп_тема, вид_RC1, сигнатура, свидетели, строка_M1a2), upstream_parts.tsv (split themes T240/T313, T185/T314),
upstream_merges.tsv (the merge 8cecaf4e). Decisions applied (p.756(b)):
 (1) RC1: 75 themes -> А-резерв, except T256 -> А (wave 1); signature column from signatures.tsv (FATAL/RT);
 (2) RC2: T021 Б -> В; T240 = decoding (Б) + new theme T313 = guard of unequal DWORD halves (А, wave 2 with T179);
     T185 = pad (Б, Ф24) + new theme T314 = compute LDS clamp (А-резерв);
 (3) RC3: merge row in upstream_merges.tsv (theme T053, class Г); column файлы = both sides of renames (git -M);
 (4) RC4: column свидетели (witness.tsv grouped by theme);
 (5) RC5: строка_M1a2 of T163, T239, T155, T178 (class Д kept);
 (6) RC6: строка_M1a2 of T021, T240, T069, T255, T007.
Read-only for git; exit 3 lock / 4 STOP. Usage: python apply_m1a2.py   (cwd anywhere)."""
import collections, csv, io, os, re, subprocess, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP present - exit 4'); sys.exit(4)
HERE = os.path.dirname(os.path.abspath(__file__))
M1 = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(M1, '..', '..', '..'))
GIT = 'C:/Program Files/Git/cmd/git.exe' if os.path.exists('C:/Program Files/Git/cmd/git.exe') else 'git'
BASE_REV = 'eee39691'


def git(*a):
    return subprocess.run([GIT, '-C', REPO] + list(a), capture_output=True).stdout.decode('utf-8', 'replace')


def tsv_text(text):
    return list(csv.DictReader(io.StringIO(text), delimiter='\t', quoting=csv.QUOTE_NONE))


def tsv_file(path):
    return tsv_text(open(path, encoding='utf-8').read())


def write_tsv(path, header, rows):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(header) + '\n')
        for r in rows:
            vals = [r[h] for h in header]
            for v in vals:
                assert '\t' not in v and '\n' not in v, (path, v[:80])
            f.write('\t'.join(vals) + '\n')


up = tsv_text(git('show', BASE_REV + ':docs/track-m/m1/upstream.tsv'))
det = tsv_text(git('show', BASE_REV + ':docs/track-m/m1/upstream_detail.tsv'))
rc1 = {r['тема']: r['вид'] for r in tsv_file(os.path.join(M1, 'm1b', 'rc1_themes.tsv'))}
sig = tsv_file(os.path.join(HERE, 'signatures.tsv'))
wit = tsv_file(os.path.join(HERE, 'witness.tsv'))
assert len(rc1) == 75, len(rc1)

# ---- (1)-(2) classes
NEW_CLASS = {t: 'А-резерв' for t in rc1}
NEW_CLASS['T256'] = 'А'
NEW_CLASS['T021'] = 'В'
EXTRA = {'57c97ebd8': 'T313:А', 'e6cb880ad': 'T314:А-резерв'}

# ---- (3) files with both sides of renames
def files_of(sha):
    out = []
    for line in git('diff-tree', '--no-commit-id', '-r', '-M', '--name-status', sha).split('\n'):
        if not line:
            continue
        parts = line.split('\t')
        for p in parts[1:]:
            if p not in out:
                out.append(p)
    return out


# ---- texts
A_RES = ('А-резерв (п. 756(б)(1)): перенос только при сигнатуре у нас (K1/K2/потеря геометрии на новом уровне) или при '
         'офлайн-свидетельстве по всей игре; поиск сигнатуры — m1a2/grep_sig_m1a2.py')
A_RES_NOSIG = ('А-резерв (п. 756(б)(1)): перенос только при свидетельстве у нас; печатающего отказа на нашем пути нет (путь '
               'картинки/данных/HLE) — переоткрытие: видимый дефект на листе, строка реестра или офлайн-свидетельство по всей игре')
LDS = ('офлайн по всей игре [c заголовков .shader_header, m1a2/lds_m1a2.py]: 190 CS-программ eboot.bin (из 5 698), наибольший LDS '
       '49 152 Б (24 программы) = maxComputeSharedMemorySize устройства (RTX 5080 Laptop, драйвер 616.56) — сверх предела 0; '
       'что игра передаёт значение заголовка без правки — [I]; триггер переноса — устройство с пределом < 49 152 Б или новая программа')
RC5 = ('кандидат против кадра ≥ 1 с; перенос — только с серией формы п. 613(г) (п. 756(б)(5): паркуется до переоткрытия Б36, Б40, '
       'Ф28 или Б32 новым свидетельством); класс Д')
RC6 = {
    'T021': ('RC6/п. 756(б)(2): Б → В. Проверка, превращающая В в В′ или Б: (1) тест вида у нас — `base_level` = 2, MIN_LOD T# = 3,0, '
             'отложенные верхние уровни: наш `minLod` (b3dc9c67 imageView.cpp:387, без прибавки `base_level`) против `base_level` + MIN_LOD '
             '(upstream) под валидацией (VUID-VkImageViewMinLodCreateInfoEXT-minLod-06456 [I]); (2) в игре — счётчик видов с '
             '`base_level` > 0 и `minLod` > 0 под замком (волна 2, п. 756(в)(3)): 0 видов ⇒ Б (расхождение недостижимо), ≥ 1 вид и '
             '(1) показывает чтение ниже `baseMipLevel` ⇒ В′ (замена нашего варианта формулой upstream)'),
    'T240': ('RC6/п. 756(б)(2): делится — T240 = декодирование R16/R16G16 (Б, наш `DecodePackedColorClear` imageInfo.h:458), '
             'T313 = защита заливки DWORD R16 с неравными половинами (А, волна 2 с T179). Проверка, снимающая или подтверждающая '
             'T313: стенд пути `ClearImageFromBuffer` (b3dc9c67 textureCache.cpp:2971) — R16, слово 0x00003c00: у нас 1,0 по всей '
             'поверхности, по upstream — отказ декодирования (заливка буфером); в игре — счётчик заливок DWORD R16/R16Unorm с '
             'неравными половинами на тегах M3: 0 ⇒ T313 — Б (недостижимо), ≥ 1 ⇒ T313 переносится по критерию до кода'),
    'T069': ('RC6: проверка, превращающая В в В′ или Б: (1) опись своим декодером транслятора программ NGG passthrough VS '
             'корпуса T1/eboot, читающих s3 сверх бита 28 до первой записи (у нас s3 = 1<<28, upstream — (1<<28)|wave_size, затем '
             'popcount начальной EXEC, cf77fb435): 0 программ ⇒ Б; (2) ≥ 1 — GPU-тест пролога при EXEC < 64 бит: ответ нашего s3 '
             'против числа активных вершин; отличие при чтении программой ⇒ В′'),
    'T255': ('RC6: проверка, превращающая В в В′ или Б: офлайн по корпусу T1 и регистрам снимков (k02–k08 хранятся, п. 748) — '
             'число draw, у которых множество экспортируемых MRT PS ≠ множеству включённых слотов `CB_SHADER_MASK` (маска с '
             'дырами ниже экспортируемой цели, где правило upstream «k-й экспорт → k-й включённый слот» и наше «гостевой индекс '
             'цели» d844f4cb расходятся): 0 ⇒ Б; ≥ 1 ⇒ пара листов этого draw с обоими правилами и семантика ISA RDNA2 [I] — '
             'видимый дефект нашего ⇒ В′'),
    'T007': ('RC6: проверка, превращающая В в В′ или Б: (1) тест транслятора/GPU-тест flat-входа PS при '
             '`PA_SU_SC_MODE_CNTL.PROVOKING_VTX_LAST` = 1 — наш ответ (вершина 0, 33ca0bfc) против провоцирующей вершины '
             '(upstream b38b7454); (2) в игре — счётчик draw с `PROVOKING_VTX_LAST` = 1 и flat-входами PS (снимки или счётчик под '
             'замком): 0 ⇒ Б; ≥ 1 и (1) различает ⇒ В′ (видимое — пара листов)'),
}
T256 = ('п. 756(б)(1): исключение RC1 — дефект кода [c отзыва M1b] (режим 6 SNORM16 распаковывается как half, '
        'spirvEmitterFlow.cpp:291); класс А, волна 1 M2a (п. 756(в)(1))')
T053 = ('п. 756(б)(3): слияние 8cecaf4e (PR #716) несёт своё содержимое разрешения — строка upstream_merges.tsv, класс Г '
        '(FindFiles `rel_path_with_name`: потребителей у нас 0 [c]; `Umount` по пути хоста: вызовов у нас 0 [c]; журнал и '
        'UTF-8 — только не-ASCII пути); судьба fileSystem.cpp — Б4 не задет (ханк `MountPoints::Umount` стр. 340, ханки Б4 стр. '
        '105–115, 303, 431–446); перенос T053 — только вместе со слиянием')
WIT_NOTE = {
    'T116': 'в upstream строка flipPendingNum печатается только при --graphics-debug-dump (a20fb7f9): читатели ослепнут без флага',
    'T017': 'строка сохранена текстом; проверка нулевого dispatch перенесена до подготовки программы',
    'T124': 'строки удалены upstream: свип Б9/Ф21 по «Relocate: unresolved PLT import» перестанет видеть заглушки',
    'T151': 'строка удалена upstream: refs_f16h.py, sweep_f17a.py её не найдут',
}
FATE = {'kept_text_upstream': 'текст сохранён в upstream', 'removed_upstream': 'удалена в upstream'}

# ---- per-theme signature and witness text
sig_by = collections.defaultdict(list)
for r in sig:
    place = r['место'].replace('b3dc9c67:src/', '')
    if r['сигнатура'] == '-':
        sig_by[r['тема']].append('печати нет @%s' % place)
    else:
        extra = '' if r['в_логе'] == '-' else ' (в лог: %s)' % r['в_логе'].split('«')[1].rstrip('»')
        sig_by[r['тема']].append('%s: «%s» @%s%s' % (r['поток'], r['сигнатура'], place, extra))
wit_by = collections.defaultdict(list)
for r in wit:
    s = r['скрипты'].split(';')
    short = ', '.join(x.replace('docs/', '') for x in s[:3]) + ('' if len(s) <= 3 else ' (+%d)' % (len(s) - 3))
    item = '«%s» — %s: %s' % (r['ключ'], FATE[r['судьба_в_upstream']], short)
    if item not in wit_by[r['тема']]:
        wit_by[r['тема']].append(item)


def theme_line(t):
    parts = []
    if t in rc1 and t != 'T256':
        parts.append(A_RES if rc1[t] in ('FATAL', 'RT') else A_RES_NOSIG)
    if t == 'T256':
        parts.append(T256)
    if t == 'T226':
        parts.append(LDS)
    if t in ('T163', 'T239', 'T155', 'T178'):
        parts.append(RC5)
    if t in RC6:
        parts.append(RC6[t])
    if t == 'T053':
        parts.append(T053)
    if t == 'T185':
        parts.append('п. 756(б)(2): делится — T185 = пад (Б, Ф24), T314 = предел LDS вычислений (А-резерв, upstream_parts.tsv)')
    return ' ‖ '.join(parts) if parts else '-'


def witness_text(t):
    items = list(wit_by.get(t, []))
    if t in WIT_NOTE:
        items.append(WIT_NOTE[t])
    return ' ‖ '.join(items) if items else '-'


# ---- upstream.tsv
counts = collections.Counter()
new_up = []
for r in up:
    k = r['sha'][:9]
    cls = NEW_CLASS.get(r['тема'], r['класс'])
    orig = [x for x in r['файлы'].split(';') if x and x != '-']
    gm = files_of(k)
    assert set(orig) <= set(gm), (k, set(orig) - set(gm))
    merged = orig + sorted(p for p in gm if p not in orig)
    new_up.append({'sha': r['sha'], 'тема': r['тема'], 'класс': cls, 'файлы': ';'.join(merged) if merged else r['файлы'],
                   'доп_тема': EXTRA.get(k, '-')})
write_tsv(os.path.join(M1, 'upstream.tsv'), ['sha', 'тема', 'класс', 'файлы', 'доп_тема'], new_up)
cls_of = {r['sha']: r['класс'] for r in new_up}
# ---- upstream_detail.tsv
hdr = list(det[0].keys()) + ['доп_тема', 'вид_RC1', 'сигнатура', 'свидетели', 'строка_M1a2']
new_det = []
for r in det:
    t = r['тема']
    d = dict(r)
    d['класс'] = cls_of[r['sha']]
    d['доп_тема'] = EXTRA.get(r['sha'][:9], '-')
    d['вид_RC1'] = rc1.get(t, '-')
    d['сигнатура'] = ' ‖ '.join(sig_by[t]) if t in sig_by else '-'
    d['свидетели'] = witness_text(t)
    d['строка_M1a2'] = theme_line(t)
    new_det.append(d)
write_tsv(os.path.join(M1, 'upstream_detail.tsv'), hdr, new_det)
# ---- upstream_parts.tsv (split themes)
PH = ['тема', 'родитель', 'sha', 'класс', 'файлы', 'ханки', 'основание', 'якорь', 'якорь_плюс1', 'суть', 'строка_M1a2']
parts = [
    dict(тема='T240', родитель='T240', sha='57c97ebd8', класс='Б',
         файлы='src/graphics/host_gpu/renderer/image/imageInfo.h;tests/ShaderRecompilerComputeTests.cpp',
         ханки='imageInfo.h @@ -390 (DecodePackedColorClear: R16Sfloat/R16G16Sfloat/R16Unorm/R16G16Unorm); тесты декодирования',
         основание='b3dc9c67:src/graphics/host_gpu/renderer/image/imageInfo.h:458',
         якорь='case vk::Format::eR16Sfloat: next.float32[0] = DecodeHalfBits(packed & 0xffffu); break;',
         якорь_плюс1='case vk::Format::eR16G16Sfloat:',
         суть='декодирование 16-битных цветовых очисток — у нас то же (992055cd)', строка_M1a2=RC6['T240']),
    dict(тема='T313', родитель='T240', sha='57c97ebd8', класс='А',
         файлы='src/graphics/host_gpu/renderer/image/imageInfo.h;tests/ShaderRecompilerComputeTests.cpp',
         ханки='imageInfo.h @@ -443 (DecodeColorDwordFill: R16Sfloat/R16Unorm — отказ при неравных половинах слова); тест заливки',
         основание='b3dc9c67:src/graphics/host_gpu/renderer/cache/textureCache.cpp:2971',
         якорь='if (!DecodePackedColorClear(image.info.pixel_format, packed_clear, clear.color)) {',
         якорь_плюс1='g_last_clear_outcome = "decode";',
         суть=('защита заливки DWORD R16 с неравными половинами: у нас `ClearImageFromBuffer` берёт младшую половину слова '
               '(imageInfo.h:458) — вся поверхность одним значением, у железа чередование [I]; upstream отказывает в декодировании'),
         строка_M1a2='п. 756(б)(2), (в)(3): класс А, волна 2 вместе с частью заливки DWORD T179 ‖ ' + RC6['T240']),
    dict(тема='T185', родитель='T185', sha='e6cb880ad', класс='Б',
         файлы='src/graphics/presentation/window/window.cpp',
         ханки='window.cpp (неоткрываемый геймпад пропускается без фатала)',
         основание='b3dc9c67:src/graphics/presentation/window/joyPump.cpp:351', якорь='', якорь_плюс1='',
         суть='пад: у нас Ф24 (FIXED, реестр §124) — открытие делает JoyPump без фатала', строка_M1a2='п. 756(б)(2): Б (Ф24)'),
    dict(тема='T314', родитель='T185', sha='e6cb880ad', класс='А-резерв',
         файлы='src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp;tests/ShaderRecompilerComputeTests.cpp',
         ханки='pipelineCache.cpp @@ -658 (GetComputeProgram: lds_size_dwords = min(…, maxComputeSharedMemorySize/4), строка GPU warning); тест ComputeLdsLimit',
         основание='b3dc9c67:src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp:5424',
         якорь='ShaderProgram PipelineCache::GetComputeProgram(const HW::ComputeShaderInfo& regs,',
         якорь_плюс1='const HW::ShaderRegisters&   sh,',
         суть=('предел LDS вычислений: у нас `lds_size_dwords = lds_size * 128` (shader.cpp:850) без зажима по пределу устройства; '
               'upstream зажимает и печатает предупреждение (T226 — запасной путь через буфер устройства)'),
         строка_M1a2='п. 756(б)(2): А-резерв ‖ ' + LDS),
]
# fill anchor of T185 from detail
d185 = [d for d in det if d['тема'] == 'T185'][0]
parts[2]['якорь'], parts[2]['якорь_плюс1'] = d185['якорь'], d185['якорь_плюс1']
write_tsv(os.path.join(M1, 'upstream_parts.tsv'), PH, parts)
# ---- upstream_merges.tsv
cc = [x for x in git('diff-tree', '--cc', '--name-only', '8cecaf4e').split('\n')[1:] if x]
MH = ['sha', 'тема', 'класс', 'файлы', 'основание', 'якорь', 'якорь_плюс1', 'суть', 'строка_M1a2']
write_tsv(os.path.join(M1, 'upstream_merges.tsv'), MH, [dict(
    sha='8cecaf4e3', тема='T053', класс='Г', файлы=';'.join(cc),
    основание='b3dc9c67:src/kernel/fileSystem.cpp:340',
    якорь='return Common::PathToGenericString(p.dir) == folder_or_point_str ||',
    якорь_плюс1='p.point == folder_or_point_str;',
    суть=('Merge PR #716 (Unicode-пути Windows), содержимое разрешения конфликта: FindFiles — `rel_path_with_name` через '
          '`lexically_relative`; `MountPoints::Umount` — сравнение пути хоста через `FixDirectorySlash`; приёмник журнала по '
          '`path.native()`; `PathFromUtf8` через u8string; `SPDLOG_WCHAR_FILENAMES` на Windows; тесты Unicode'),
    строка_M1a2=T053)])
# ---- counts
cc_cls = collections.Counter(r['класс'] for r in new_up)
th = {}
for r in new_up:
    th.setdefault(r['тема'], set()).add(r['класс'])
tc = collections.Counter(next(iter(v)) for v in th.values())
print('commits by class (row class):', dict(sorted(cc_cls.items())), 'sum', sum(cc_cls.values()))
print('themes by class (upstream.tsv):', dict(sorted(tc.items())), 'sum', sum(tc.values()))
tc2 = tc.copy()
tc2['А'] += 1
tc2['А-резерв'] += 1
print('themes by class with parts T313 (А), T314 (А-резерв):', dict(sorted(tc2.items())), 'sum', sum(tc2.values()))
print('multi-class themes', [t for t, v in th.items() if len(v) > 1])
print('rename-file fixes:', [r['sha'] for r, o in zip(new_up, up) if r['файлы'] != o['файлы']])
print('written: upstream.tsv upstream_detail.tsv upstream_parts.tsv upstream_merges.tsv')
