# F0 (HPP-289): builds docs/track-f/register.md from the sweep (agg_f0.json, logsigs_f0.pkl). Sums, scene counts and the
# ranking order are computed and asserted here; code references are located by anchor in `git show <commit>:<path>`.
import os, re, sys, json, pickle, hashlib, subprocess, collections

OUT = 'C:/kyty/f287/f0'
REPO = 'C:/kyty/KytyPS5'
DOC = REPO + '/docs/track-f/register.md'
GIT = 'C:/Program Files/Git/cmd/git.exe'
CODE = '26457dd7'
NL = chr(10)
recs = json.load(open(OUT + '/agg_f0.json', encoding='utf-8'))
LS = pickle.load(open(OUT + '/logsigs_f0.pkl', 'rb'))
uniq = [r for r in recs if not r['dup_of']]
CHECKS = []   # (name, ok)


def check(name, ok):
    CHECKS.append((name, bool(ok)))
    assert ok, name


def tag(p):
    return p.replace('C:/kyty/', '')


def fmt(n):
    return '{:,}'.format(n).replace(',', ' ')


# ---------------------------------------------------------------- references (general rule 24(1))
_files = {}


def gitfile(commit, path):
    k = (commit, path)
    if k not in _files:
        b = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True).stdout
        _files[k] = b.decode('utf-8', 'replace').split(NL)
    return _files[k]


REFMAP = []


def ref(commit, path, anchor, occ=0, short=None):
    lines = gitfile(commit, path)
    hits = [i for i, l in enumerate(lines) if anchor in l]
    assert len(hits) > occ, ('anchor not found', path, anchor)
    i = hits[occ]
    plus1 = anchor in lines[i + 1] if i + 1 < len(lines) else False
    REFMAP.append((commit, path, i + 1, anchor, 'OK', 'NOT OK' if not plus1 else 'OK(!)'))
    assert not plus1, ('+1 control failed', path, anchor)
    return '`%s:%s:%d` «%s»' % (commit, path, i + 1, short or anchor[:40])


R = 'src/graphics/host_gpu/renderer/'
SR = 'src/graphics/shader/recompiler/'
ref_skip = ref(CODE, R + 'pipeline/computePretranslation.h', 'LOGF("CsPretranslate: skipped hash=%016" PRIx64 " reason=%s', short='CsPretranslate: skipped')
ref_interc = ref(CODE, R + 'pipeline/computePretranslation.h', 'Common::ScopedFatalInterceptor recover', short='ScopedFatalInterceptor')
ref_miss = ref(CODE, R + 'pipeline/computePretranslation.h', 'LOGF("CsPretranslate: miss hash=', short='CsPretranslate: miss')
ref_take = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'prepared = pretranslation.Take(params.code', short='pretranslation.Take')
ref_norm = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'ShaderRecompiler::TranslateProgram(params.code, options);', short='TranslateProgram(params.code')
ref_enq = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'if (ComputePretranslation::Enabled() && mapped.type == Prospero::ShaderBinaryType::kCs', short='mapped.type == Prospero::ShaderBinaryType::kCs')
ref_cfgexit = ref(CODE, SR + 'frontend/cfg/ShaderCFG.cpp', 'EXIT("shader CFG build failed: %s"', short='shader CFG build failed')
ref_sop1 = ref(CODE, SR + 'frontend/decode/ScalarAluOps.cpp', '"SOP1 opcode is not implemented"', short='SOP1 opcode is not implemented')
ref_vopc = ref(CODE, SR + 'frontend/decode/VectorAluOps.cpp', '"VOPC opcode is not implemented"', short='VOPC opcode is not implemented')
ref_vop2 = ref(CODE, SR + 'frontend/decode/VectorAluOps.cpp', '"VOP2 opcode is not implemented"', short='VOP2 opcode is not implemented')
ref_trip = ref(CODE, R + 'cache/faultManager.cpp', 'LOGF("BvhLoopCapTrip: trips=+%u', short='BvhLoopCapTrip:')
ref_prio = ref(CODE, R + 'commandScheduler.cpp', 'LOGF("PriorityStall: tick=', short='PriorityStall:')
ref_skipd = ref(CODE, R + 'renderDraw.cpp', 'LOGF("AsyncPipelines: skipped draw %s', short='AsyncPipelines: skipped draw')
ref_held = ref(CODE, 'src/graphics/presentation/videoOut.cpp', 'held (incomplete frame)', short='held (incomplete frame)')
ref_mwd = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'void PipelineCache::MaybeWriteDriverCache() {', short='MaybeWriteDriverCache')
ref_mwd_c = ref(CODE, R + 'pipeline/pipelineCache.cpp', '// Called with m_mutex held right after a new pipeline was created.', short='Called with m_mutex held')
ref_20s = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'if (now - m_driver_cache_saved_us < 20000000u) {', short='20000000u')
ref_saved = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'PipelineCacheLog("Vulkan pipeline cache: saved {} bytes', short='pipeline cache: saved')
ref_csstall = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'LOGF("CsStall: kind=%s', short='CsStall:')
ref_stubcall = ref(CODE, 'src/loader/runtimeLinker.cpp', 'LOGF("Unresolved import stub called [%u]: patch_vaddr', short='Unresolved import stub called')
ref_reloc = ref(CODE, 'src/loader/runtimeLinker.cpp', 'LOGF("Relocate: unresolved PLT import patched to stub', short='unresolved PLT import patched')
ref_stubbed = ref(CODE, 'src/loader/runtimeLinker.cpp', 'LOGF("=== Stubbed function, returning OK', short='=== Stubbed function')
ref_kread = ref(CODE, 'src/kernel/fileSystem.cpp', 'LOGF("KernelRead: direct read failed', short='KernelRead: direct read failed')
ref_mfiles = ref(CODE, 'src/kernel/fileSystem.cpp', 'm_files[index] == nullptr', short='m_files[index] == nullptr')
ref_late = ref(CODE, 'src/graphics/presentation/window/window.cpp', 'LOGF("MainTaskLate: us=%llu', short='MainTaskLate:')
ref_meta = ref(CODE, R + 'debug.cpp', 'ignoring PS5 color metadata', short='ignoring PS5 color metadata')
ref_round = ref(CODE, R + 'debug.cpp', 'ignoring PS5 color round mode', short='ignoring PS5 color round mode')
ref_maddr = ref(CODE, R + 'debug.cpp', 'ignoring PS5 metadata addresses', short='ignoring PS5 metadata addresses')
ref_depth = ref(CODE, R + 'depthRenderTarget.cpp', 'ignoring enabled depth/stencil state without a bound attachment', short='without a bound attachment')
ref_zero = ref(CODE, R + 'renderCompute.cpp', 'skipping zero-sized dispatch', short='skipping zero-sized dispatch')
ref_stereo = ref(CODE, 'src/graphics/guest_gpu/command_processor/pm4Handlers.cpp', 'ignoring indirect uc reg GE_STEREO_CNTL', short='GE_STEREO_CNTL')
ref_align = ref(CODE, 'src/libs/agc.cpp', 'size_bytes is not 256-byte aligned', short='size_bytes is not 256-byte aligned')
ref_restr = ref(CODE, SR + 'ir/passes/ResourceTracking.cpp', 'shader resource tracking: hash=0x', short='shader resource tracking')
ref_budget = ref(CODE, SR + 'TranslationBudget.h', 'speculative translation budget exceeded', short='budget exceeded')
ref_disp = ref(CODE, SR + 'ShaderRecompiler.cpp', 'CFG dispatcher fallback: stage=', short='CFG dispatcher fallback')
ref_noop = ref(CODE, R + 'pipeline/pipelineCache.cpp', 'accepting EXEC_ON_NOOP', short='accepting EXEC_ON_NOOP')
ref_dcc = ref(CODE, R + 'cache/textureCache.cpp', 'stale pending DCC fill ignored', short='stale pending DCC fill')
ref_recorder = ref(CODE, R + 'commandRecorder.cpp', 'm_producer != self', short='m_producer != self')
ref_ctrl = ref(CODE, 'src/graphics/presentation/window/window.cpp', 'SDL_GameControllerClose', short='SDL_GameControllerClose')
ref_p228 = ref('beb36ab0', 'docs/ROADMAP.md', '228. **Трек F', short='Трек F')
DOCS = '455b3a25'
ref_p229 = ref(DOCS, 'docs/ROADMAP.md', '(б) **Граница с треком F (п. 228).**', short='Граница с треком F')
ref_p231 = ref(DOCS, 'docs/ROADMAP.md', '(г) **Новые и изменённые строки (Б) по классам**', short='Новые и изменённые строки (Б)')
ref_p231d = ref(DOCS, 'docs/ROADMAP.md', '(д) **p форм на установленной сборке**', short='p форм на установленной сборке')
ref_b32 = ref(DOCS, 'docs/ROADMAP.md', '**Б32 | K3 |', short='Б32')
ref_b33 = ref(DOCS, 'docs/ROADMAP.md', '(1) **Б33 — K3 на удержании', short='Б33 — K3 на удержании')
ref_b34 = ref(DOCS, 'docs/ROADMAP.md', '(2) **Б34 — наблюдение', short='Б34 — наблюдение')
ref_b1b231 = ref(DOCS, 'docs/ROADMAP.md', 'класс K4 не меняется, пометка', short='класс K4 не меняется')
ref_rcl1 = ref(DOCS, 'docs/ROADMAP.md', '(б) **Поправка лида RC-L1', short='RC-L1')
ref_f1rc1 = ref(DOCS, 'docs/track-f/f1-review.md', 'RC1. Без сцены-свидетеля', short='RC1. Без сцены-свидетеля')
ref_f1rc2 = ref(DOCS, 'docs/track-f/f1-review.md', 'RC2. Критерий (е)(3)', short='RC2. Критерий (е)(3)')
INV = {}
for rid in ['Б1а', 'Б1б', 'Б2', 'Б3а', 'Б3б', 'Б4', 'Б5', 'Б5а', 'Б6', 'Б7', 'Б8', 'Б9', 'Б10', 'Б11', 'Б12', 'Б13', 'Б14', 'Б15', 'Б16',
            'Б17', 'Б18', 'Б19', 'Б20', 'Б22', 'Б24', 'Б25', 'Б26', 'Б27', 'Б28', 'Б29', 'Б30', 'Б31']:
    INV[rid] = ref('2c65eb41', 'docs/session-141/inventory141.md', '| %s |' % rid, short=rid)
check('inventory rows located by anchor: 32', len(INV) == 32)

# local files outside git: anchor must be in the named line and absent from the next one
LOCAL = [
    ('C:/kyty/s142/FACTS.md', 4, '9235a7ac61f1affb'), ('C:/kyty/s142/FACTS.md', 25, 'Б20'), ('C:/kyty/s142/FACTS.md', 219, 'маркеров смерти 0'),
    ('C:/kyty/s142/FACTS.md', 221, 'форма Б5а'),
    ('C:/kyty/s142/log_c142_01.txt', 350295, 'CsStall: kind=wait us=689831'),
    ('C:/kyty/s142/log_c142_02.txt', 9989, 'opcode=0x21'), ('C:/kyty/s142/log_c142_02.txt', 15230, 'size_bytes is not'),
    ('C:/kyty/s142/log_c142_02.txt', 30109, 'file not found'), ('C:/kyty/s142/log_c142_02.txt', 207786, 'skipping zero-sized dispatch'),
    ('C:/kyty/s142/log_c142_02.txt', 269177, 'BvhLoopCapTrip:'), ('C:/kyty/s142/log_c142_02.txt', 490948, 'shader resource tracking'),
    ('C:/kyty/s142/log_c142_02.txt', 557303, 'Vulkan pipeline cache: saved 90629860 bytes'),
    ('C:/kyty/s142/log_c142_03.txt', 239572, 'Unresolved import stub called'), ('C:/kyty/s142/log_c142_05.txt', 414100, 'KernelRead: direct read failed'),
    ('C:/kyty/s142/log_c142_09.txt', 206646, 'BvhLoopCapTrip:'), ('C:/kyty/s131/log_dds131.txt', 718963, 'm_files[index] == nullptr'),
    ('C:/kyty/log_s14_s42_merged_cold.txt', 4407364, 'too many objects/batches'), ('C:/kyty/s59/log_sig1.txt', 627192, 'too many objects/batches'),
]
LOCMAP = []
by = collections.defaultdict(list)
for p, n, a in LOCAL:
    by[p].append((n, a))
for p, lst in by.items():
    want = {n: a for n, a in lst}
    top = max(want) + 1
    got = {}
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for i, line in enumerate(fh, 1):
            h.update(line)
            if i in want or i - 1 in want:
                got[i] = line.decode('utf-8', 'replace')
    for n, a in lst:
        # the +1 control is skipped when the next line legitimately repeats the anchor (repeated log lines)
        ok = a in got.get(n, '')
        plus1 = a in got.get(n + 1, '')
        LOCMAP.append((p, n, a, 'OK' if ok else 'NOT OK', 'NOT OK' if not plus1 else 'repeats', h.hexdigest()))
        assert ok, ('local anchor', p, n, a)
check('local references by anchor: %d of %d' % (len(LOCMAP), len(LOCAL)), all(x[3] == 'OK' for x in LOCMAP) and len(LOCMAP) == len(LOCAL))

# ---------------------------------------------------------------- sweep numbers
def band(s):
    if s is None:
        return 'без номера'
    return 'до с. 50' if s < 50 else 'с. 50–102' if s < 103 else 'с. 103–112' if s < 113 else 'с. 113–127' if s < 128 else 'с. 128–141' if s < 142 else 'с. 142'


BANDS = ['без номера', 'до с. 50', 'с. 50–102', 'с. 103–112', 'с. 113–127', 'с. 128–141', 'с. 142']
bandn = collections.Counter(band(r['session']) for r in uniq)
check('unique logs by band sum = unique logs', sum(bandn.values()) == len(uniq))
check('aggregated = unique + duplicates', len(recs) == len(uniq) + sum(1 for r in recs if r['dup_of']))
N128 = sum(1 for r in uniq if r['session'] is not None and r['session'] >= 128)
N142 = [r for r in uniq if r['session'] == 142]
check('s142 logs = 12', len(N142) == 12)
check('s128+ = bands 128-141 + 142', N128 == bandn['с. 128–141'] + bandn['с. 142'])


def sigrow(label, prefixes, exclude=()):
    logs = []
    lines = 0
    for r in uniq:
        hit = [(k, v) for k, v in LS[r['path']].items() if any(k.startswith(p) for p in prefixes) and not any(x in k for x in exclude)]
        if hit:
            n = sum(v[0] for k, v in hit)
            lines += n
            first = min(hit, key=lambda kv: kv[1][1])
            logs.append((r, n, first[1][1]))
    ss = [r['session'] for r, n, l in logs if r['session'] is not None]
    lv = collections.Counter()
    for r, n, l in logs:
        for L in r['levels']:
            lv[L] += 1
    ex = None
    if logs:
        ex = max(logs, key=lambda x: (x[0]['session'] if x[0]['session'] is not None else -1, x[0]['path']))
    return {'label': label, 'logs': len(logs), 'lines': lines, 'first': min(ss) if ss else None, 'last': max(ss) if ss else None,
            's128': sum(1 for s in ss if s >= 128), 's142': sum(1 for s in ss if s == 142), 'levels': lv,
            'ex': ('`C:/kyty/%s:%d` (sha256 `%s…`)' % (tag(ex[0]['path']), ex[2], ex[0]['sha256'][:16])) if ex else '—', 'set': logs}


b = lambda s: s.encode('latin1')
SIGS = [
    ('`--- Fatal Error ---` (маркер смерти п. 218(д)(2))', [b('--- Fatal Error')], 'Б4, Б18, Б23; до с. 103 — закрытые'),
    ('`--- Error ---` (п. 218(д)(2))', [b('--- Error ---')], 'последняя с. 102; Б25 и закрытые'),
    ('`Error: condition (…) is true in …` / `Assertion failed`', [b('Error: condition'), b('Assertion failed')], 'Б4 (`fileSystem.cpp`), Б18 (`commandRecorder.cpp`)'),
    ('`GpuHangAbort:` (п. 128(г))', [b('GpuHangAbort')], 'Б1а; после с. 102 — только фикстуры `fx/hang`'),
    ('`ErrorDeviceLost` (п. 128(г))', [b('vkWaitSemaphores failed: ErrorDeviceLost'), b('vkQueueSubmit failed: ErrorDeviceLost')], 'с. 128 — `protceil=1` (Б23); раньше — закрытые'),
    ('`Unhandled host exception:` (п. 128(г))', [b('Unhandled host exception')], 'последняя с. 59 (Б25)'),
    ('`There are too many objects/batches in this scene.`', [b('There are too many objects')], 'Б25: 2 лога (с. 42 и с. 59)'),
    ('`[Vulkan][E]`', [b('[Vulkan][E]')], 'последняя с. 38; закрыты'),
    ('`[Vulkan][W]` (все формы; основная — запись в `out_mrt_N` без привязанной цели)', [b('[Vulkan][W]')], 'Ф6', ),
    ('`opcode is not implemented` SOP1 `0x21`', [b('OPCODE_NI family=SOP1 opcode=0x21')], 'Б26'),
    ('`opcode is not implemented` SOP1 `0x0c`', [b('OPCODE_NI family=SOP1 opcode=0x0c')], 'Б26'),
    ('`opcode is not implemented` VOPC `0xe3`', [b('OPCODE_NI family=VOPC opcode=0xe3')], 'Б26'),
    ('`opcode is not implemented` прочих семейств (VOP2, VOP1, VOP3, MIMG, SMEM, …)', [b('OPCODE_NI')], 'Б7: 0 логов', ),
    ('`CsPretranslate: skipped … shader resource tracking`', [b('CsPretranslate: skipped hash=X reason=C:\\kyty\\KytyPSX\\src\\graphics\\shader\\recompiler\\ir\\passes\\ResourceTracking')], 'Ф3'),
    ('`CsPretranslate: skipped … speculative translation budget exceeded`', [b('CsPretranslate: skipped hash=X reason=C:\\kyty\\KytyPSX\\src\\graphics/shader/recompiler/TranslationBudget')], 'Ф3'),
    ('`CsPretranslate CFG dispatcher fallback … failure=StructuredControlFlow`', [b('CsPretranslate CFG dispatcher fallback')], 'Ф3'),
    ('`=== Stubbed function`', [b('=== Stubbed function')], 'Б9: 0 логов — маркер ред. 2 не срабатывал ни разу'),
    ('`Unresolved import stub called` (любая библиотека)', [b('Unresolved import stub called')], 'Б9а (AudioPropagation, с. 142); Json2 — с. 45'),
    ('`Relocate: unresolved PLT import patched to stub` (все библиотеки)', [b('Relocate: unresolved PLT import')], 'Б9'),
    ('`BvhLoopCapTrip:`', [b('BvhLoopCapTrip')], 'Б1б'),
    ('`PriorityStall:` (ожидание > 50 мс)', [b('PriorityStall:')], 'Б3б'),
    ('`AsyncPipelines: skipped draw`', [b('AsyncPipelines: skipped draw')], 'Б5'),
    ('`MainTaskLate:`', [b('MainTaskLate:')], 'Б24 (≥ 1 с — 5 логов с. 113+, см. §3.6)'),
    ('`CsStall: kind=wait`', [b('CsStall: kind=wait')], 'Б5 (ожидание трансляции CS)'),
    ('`KernelRead: direct read failed … reading through a host buffer`', [b('KernelRead: direct read failed')], 'Ф4'),
    ('`file not found` (`KernelStat`)', [b('file not found')], 'Ф7'),
    ('`warning: size_bytes / base is not 256-byte aligned`', [b('warning: size_bytes is not'), b('warning: base is not')], 'Ф7'),
    ('`warning: ignoring indirect uc reg GE_STEREO_CNTL`', [b('warning: ignoring indirect uc reg')], 'Ф5'),
    ('`RenderTarget: temporary: ignoring PS5 color metadata … dcc=true`', [b('RenderTarget: temporary: ignoring PSX color metadata')], 'Ф5'),
    ('`RenderTarget: temporary: ignoring PS5 metadata addresses`', [b('RenderTarget: temporary: ignoring PSX metadata addresses')], 'Ф5'),
    ('`RenderTarget: temporary: ignoring PS5 color round mode`', [b('RenderTarget: temporary: ignoring PSX color round mode')], 'Ф5'),
    ('`DepthTarget: ignoring enabled depth/stencil state without a bound attachment`', [b('DepthTarget: ignoring enabled')], 'Ф5'),
    ('`GraphicsRenderDispatchDirect: skipping zero-sized dispatch`', [b('GraphicsRenderDispatchDirect: skipping zero-sized')], 'Ф5'),
    ('`Format vk::Format::… cannot be used as texture`', [b('Format vk::Format')], 'Ф7 (свойство хоста)'),
    ('`LossWin: overflow kind=open`', [b('LossWin: overflow')], 'инструмент `armcopy` (с. 131), не умолчание'),
    ('`TextureCache: failed to map reusable download buffer`', [b('TextureCache: failed to map')], 'инструмент `bf96a` (с. 96)'),
    ('`AudioOut: SDL_QueueAudio failed: Invalid audio device ID`', [b('AudioOut: SDL_QueueAudio failed')], 'Ф8; последняя с. 105'),
    ('`Controller: disconnect of unknown id … ignored`', [b('Controller: disconnect')], 'Б24 (рядом)'),
    ('`Skipping unsupported GE shader draw`', [b('Skipping unsupported GE shader draw')], 'закрыто с. 47; последняя с. 32'),
    ('`warning: executing wave64 compute shader`', [b('warning: executing wave')], 'последняя с. 67'),
    ('`unsupported_reason=` / `failure=StructuredControlFlow` (CFG)', [b('unsupported_reason='), b('entry_block=')], 'последняя с. 59'),
    ('`vkQueuePresentKHR returned … eErrorOutOfDateKHR`', [b('vkQueuePresentKHR returned')], 'последняя с. 49'),
    ('`shader IR validation failed`', [b('shader IR validation failed')], 'с. 30'),
]
SIGROWS = []
for s in SIGS:
    excl = ()
    if s[0].startswith('`opcode is not implemented` прочих'):
        excl = (b'family=SOP1 opcode=0x21', b'family=SOP1 opcode=0x0c', b'family=VOPC opcode=0xe3')
    row = sigrow(s[0], s[1], excl)
    row['to'] = s[2]
    SIGROWS.append(row)
SG = {r['label']: r for r in SIGROWS}
g = lambda pre: [r for r in SIGROWS if r['label'].startswith(pre)][0]
check('B7: no other opcode family in any log', g('`opcode is not implemented` прочих')['logs'] == 0)
check('B9 marker "=== Stubbed function": 0 logs', g('`=== Stubbed function`')['logs'] == 0)
check('[Vulkan][E] last session < 113', (g('`[Vulkan][E]`')['last'] or 0) < 113)

# levels with the opcode profile / stalls / skipped draw / cold-entry K3
op = g('`opcode is not implemented` SOP1 `0x21`')
LV_OP = sorted(op['levels'])
census = [r for r in N142 if '/log_c142_' in r['path']]
check('s142 census logs = 10', len(census) == 10)
k3w_lv = sorted(r['levels'][-1] for r in census if r['scenes'][-1]['k3w'] > 0)
k2_census = sum(1 for r in census if r['scenes'][-1]['k2'])
check('B5 form on s142 census = 7 of 10', len(k3w_lv) == 7)
check('B5a form on s142 census = 0 of 10', k2_census == 0)
skip142 = sum(1 for r in census if r['met'].get('skip_n', 0) > 0)
check('skipped draw on s142 census = 10 of 10', skip142 == 10)
trip142 = sorted(r['levels'][-1] for r in N142 if r['met'].get('trip_n', 0) > 0)
check('BvhLoopCapTrip on s142 = 2 levels', trip142 == ['big_hand_pirate_island', 'voxel_world'])
trip_all = g('`BvhLoopCapTrip:`')
k3h142 = [(r, r['scenes'][-1]) for r in census if r['scenes'][-1]['k3h'] > 0]
check('K3 on hold on s142 census: 3 logs, 4 frames', len(k3h142) == 3 and sum(s['k3h'] for r, s in k3h142) == 4)
pw = sum(s['p_w'] for r in N142 if not r['validation'] for s in r['scenes'])
pfw = sum(s['pf_w'] for r in N142 if not r['validation'] for s in r['scenes'])
ph = sum(s['p_h'] for r in N142 if not r['validation'] for s in r['scenes'])
pfh = sum(s['pf_h'] for r in N142 if not r['validation'] for s in r['scenes'])
check('s142 stalls after the first scene frame all inside frames >= 100 ms', pw == pfw and ph == pfh and pw + ph == 23)
stall_lv = set()
for r in uniq:
    if r['validation'] or r['session'] is None or r['session'] < 113:
        continue
    for s in r['scenes']:
        if s['p_w'] + s['p_h'] > 0:
            stall_lv.add(s['level'])
sg128 = [r for r in uniq if r['session'] is not None and 128 <= r['session'] < 142 and not r['validation']]
sg_ent = sum(1 for r in sg128 for s in r['scenes'] if s['level'] == 'underwater_aerial_garden' and s['first_n'] is not None)
sg_k3h = sum(1 for r in sg128 for s in r['scenes'] if s['level'] == 'underwater_aerial_garden' and s['first_n'] is not None and s['k3h'] > 0)
intro113 = sum(1 for r in uniq if r['session'] is not None and r['session'] >= 113 and not r['validation'] for s in r['scenes'] if s['level'] == 'intro_next' and s['first_n'] is not None)
intro_all = sum(1 for r in uniq if 'intro_next' in r['levels'])
death142 = sum(1 for r in N142 if any(k.startswith((b'--- Fatal', b'--- Error', b'GpuHangAbort', b'Unhandled host exception')) or b'ErrorDeviceLost' in k for k in LS[r['path']]))
check('death markers on s142 = 0 of 12', death142 == 0)
vke142 = sum(r['vk_e'] for r in N142)
check('[Vulkan][E] on s142 = 0', vke142 == 0)
stub142 = [r for r in N142 if any(k.startswith(b'Unresolved import stub called') for k in LS[r['path']])]
check('stub called on s142: 1 log (timestop_casino)', len(stub142) == 1 and stub142[0]['levels'] == ['timestop_casino'])
prof = collections.Counter()
for r in uniq:
    p = tuple(sorted((k.decode('latin1').replace('OPCODE_NI ', ''), v[0]) for k, v in LS[r['path']].items() if k.startswith(b'OPCODE_NI')))
    if p:
        prof[p] += 1
P9614 = (('family=SOP1 opcode=0x0c', 1), ('family=SOP1 opcode=0x21', 96), ('family=VOPC opcode=0xe3', 4))
prof142 = sum(1 for r in N142 if tuple(sorted((k.decode('latin1').replace('OPCODE_NI ', ''), v[0]) for k, v in LS[r['path']].items() if k.startswith(b'OPCODE_NI'))) == P9614)
check('profile 96/1/4 on s142 = 12 of 12', prof142 == 12)
check('profile counts sum = logs with any opcode line', sum(prof.values()) == sum(1 for r in uniq if any(k.startswith(b'OPCODE_NI') for k in LS[r['path']])))

# ---------------------------------------------------------------- register rows
# key1: 1 = K1/K2 on entry or hold; 2 = K3; 3 = K1/K2 outside entry and hold; 4 = K4; 5 = K5
# tp: seconds (finite) | None; tpc: 0 finite, 1 [U] or not finite on defaults, 2 needs the user
S = lambda r: '`C:/kyty/%s`' % tag(r)
ROWS = []


def row(**k):
    ROWS.append(k)


row(id='Б5а', cls='K4 (п. 231(д): 0/10 на `9235a7ac`; в ред. 2 — K2 на входе)', key1=4, kind='дефект (форма на `2baf8742`); ведёт трек S', scenes=1, tp=None, tpc=1, P=0.3,
    what='холодный вход Atlantis: 1,39 с без нового показанного кадра после первого кадра сцены',
    status='открыт, ведёт трек S (' + ref_p229 + ', ' + ref_p231d + '); на `9235a7ac` форма (кадр ≥ 1 с после первого кадра сцены) — 0 из 10 холодных входов переписи с. 142 [c] (максимум 816 566 мкс, `bumper_enemy_snowy_canyon` n 204); Atlantis на `9235a7ac` не входил — p на установленной сборке для Atlantis [U]',
    ev=INV['Б5а'] + '; `C:/kyty/s142/FACTS.md:221` «форма Б5а»; `ana_f0.out.txt` (3), (7)',
    mech='кадр входа содержит синхронную трансляцию шейдеров обычного пути (' + ref_norm + ') и удержанный неполный флип (' + ref_held + '); что держит именно 1,39 с на Atlantis — не названо',
    game='да', user='нет', nogame='нет',
    crit='холодный стенд (копия кэшей без шейдеров и пайплайнов Atlantis, п. 228(в)): на `9235a7ac` — p по ≥ 2 холодным входам Atlantis; на сборке правки N ≥ ln 0,05 / ln(1 − p) холодных входов Atlantis без кадра ≥ 1 с после первого кадра сцены (при p = 0,9 — 2); контроль `KYTY_FIX_<ИМЯ>=0` воспроизводит; видео входа 120 с без новых K1/K2')
row(id='Б25', cls='K1 (на удержании)', key1=1, kind='дефект', scenes=1, tp=None, tpc=1, P=0.05,
    what='гостевой assert «There are too many objects/batches in this scene.» и access violation гостя на интро',
    status='открыт; свип: 2 лога из %d с входом `intro_next` — `C:/kyty/log_s14_s42_merged_cold.txt:4407364` (с. 42) и `C:/kyty/s59/log_sig1.txt:627192` (с. 59), оба с тем же `pc=0x00000009004a020e` [c]; на с. 113–141 — 0 из %d входов `intro_next` [c]; на `9235a7ac` p [U]' % (intro_all, intro113),
    ev=INV['Б25'] + '; `ana_f0.out.txt` (2f)',
    mech='не назван (гостевой счётчик объектов/батчей; что его переполняет — [U])', game='да', user='нет', nogame='нет',
    crit='сначала p: серия входов `intro_next` с удержанием ≥ 90 с на `9235a7ac`; N ≥ ln 0,05 / ln(1 − p) входов без assert на сборке правки; при p = 0 на ≥ 60 входах — кандидат «ТУПИК (нет воспроизведения)»')
row(id='Б24', cls='K2 (на удержании)', key1=1, kind='дефект', scenes=1, tp=None, tpc=2, P=0.2,
    what='остановка главного потока 23,8 с при отключении HID-устройства на удержании `intro_next`',
    status='открыт; `MainTaskLate` ≥ 1 с на с. 113+ — 5 логов: `ctl114a`, `ctl114b` (внесённый сон, инструмент), `boot115a`, `boot115c` (10,3 с и 10,3 с — происхождение в F0 не разобрано), `edes122` [c]; на с. 128+ — 0 из %d логов [c]' % N128,
    ev=INV['Б24'] + '; `ana_f0.out.txt` (6)',
    mech='удаление устройства обрабатывается на главном потоке: ' + ref_ctrl + ' (атрибуция документа с. 122, не доказана)', game='да', user='да', nogame='нет',
    crit='серия отключений HID на удержании без кадра ≥ 1 с, N по p на отключение; по п. 228(д) — «ТУПИК», если стенда отключения без пользователя нет')
row(id='Б5', cls='K3', key1=2, kind='дефект; ведёт трек S', scenes=3 + len(k3w_lv), tp=20, tpc=0, P=0.4,
    what='первый (холодный) вход уровня: кадры ≥ 100 мс в окне входа — синхронная трансляция шейдеров, ожидание трансляции CS, пропуск draw до готовности пайплайна и удержанные флипы',
    status='открыт, ведёт трек S (п. 229(б)); на `9235a7ac` [c]: кадр ≥ 100 мс в окне входа — %d из 10 холодных входов переписи с. 142 (%s), максимум 816 566 мкс; `AsyncPipelines: skipped draw` — 10 из 10; в интервале крупнейших кадров — дамп IR трансляции обычного пути (15 647 … 74 097 строк между соседними `FrameTrace`) и `CsStall: kind=wait` до 689 831 мкс (`C:/kyty/s142/log_c142_01.txt:350295`); тёплой базы для 10 новых уровней нет' % (len(k3w_lv), ', '.join('`%s`' % x for x in k3w_lv)),
    ev=INV['Б5'] + '; `ana_f0.out.txt` (7); `ctx_f0.out.txt`; `s142_f0.out.txt`',
    mech=ref_norm + ' (трансляция на обычном пути), ' + ref_csstall + ', ' + ref_skipd + ', ' + ref_held,
    game='да', user='нет', nogame='нет',
    crit='уровень-свидетель из переписи с. 142 на холодном стенде (копия кэшей до входа, п. 228(в)): максимум `dt` окна входа ≤ максимума тёплой базы того же уровня + допуск, названный лидом до кода; N ≥ 2 холодных входа на уровень (p = 7/10 ⇒ ln 0,05 / ln 0,3 = 3 входа на набор); видео 0 глитчей, 0 `[Vulkan][E]`; контроль `=0` даёт прежние кадры')
row(id='Б3б', cls='K4 (п. 231(г)(4)); вариант исполнителя — K3-симптом [c]', key1=4, kind='дефект (симптом строк Б33, Б1б, Б5, Б2)', scenes=len(stall_lv), tp=120, tpc=0, P=0.3,
    what='ожидания `PriorityStall:` > 50 мс: кадр, в интервале которого стоит строка, длится ≥ 100 мс',
    status='открыт; проверка, которой не было в ред. 2 [c]: на с. 142 после первого кадра сцены — %d ожиданий в окне входа и %d на удержании, все %d в кадрах ≥ 100 мс; из них 12 — кадры срабатывания ограничителя BVH (Б1б), 3 на удержании — кадры сохранения кэша пайплайнов (Б33); на с. 128–141: 88 ожиданий после первого кадра сцены, 21 в кадрах ≥ 100 мс' % (pw, ph, pw + ph),
    ev=INV['Б3б'] + '; `ana_f0.out.txt` (4), (7)',
    mech=ref_prio + ' — печать ожидания; причина ожидания — у строки-причины', game='да', user='нет', nogame='нет',
    crit='отдельной итерации не предлагается: после правки строки-причины — 0 строк `PriorityStall:` в кадрах ≥ 100 мс на входах её критерия')
row(id='Б33', cls='K3 (на удержании; строка лида п. 231(г)(1))', key1=2, kind='дефект; ведёт трек S', scenes=3, tp=200, tpc=0, P=0.6,
    what='кадры 115–152 мс на удержании холодного первого входа; **атрибуция F0 [c]: сохранение кэша пайплайнов драйвера (≈ 90 МБ, 80–93 мс по `save_us`) в середине уровня под `m_mutex`**',
    status='открыт, ведёт трек S (' + ref_b33 + '; происхождение там [U]); атрибуция F0 — вход трека S; на `9235a7ac` [c]: 6 сохранений в середине уровня в 3 из 10 логов переписи (`big_hand_pirate_island` ×3, `timestop_casino` ×2, `ice_iceberg` ×1), 5 из 6 — в кадре ≥ 100 мс (165 920, 149 651, 151 746, 115 028, 131 181 мкс; шестой 93 171); четыре из них — все 4 кадра K3 удержания переписи с. 142, пятый (n 795) — в окне входа; в 3 из 4 прочитанных интервалов есть и дамп трансляции шейдера — доли не разделены; в 65 логах с. 128–141 сохранений в середине уровня нет (только стартовое, кадр n 2 ≈ 20 мс)',
    ev=ref_b33 + '; `C:/kyty/s142/log_c142_02.txt:557303` (sha256 `bb6655d3d30c0bc7…`) «saved 90629860 bytes … (92638 us)» → `FrameTrace` n 1358 `dt_us` 149 651; `save_f0.out.txt`; `ctx_f0.out.txt`',
    mech=ref_mwd_c + ', ' + ref_mwd + ', ' + ref_20s + ' (раз в 20 с при новых пайплайнах — весь блоб синхронно), ' + ref_saved,
    game='да', user='нет', nogame='частично: правка и тест пути записи без игры; доказательство кадров — с игрой',
    crit='холодный стенд (копия кэшей до входа): `big_hand_pirate_island` 120 с на сборке правки — 0 кадров ≥ 100 мс, в интервале которых стоит строка `Vulkan pipeline cache: saved`, при ≥ 1 сохранении в середине уровня; файл кэша после прогона читается следующей загрузкой (строка загрузки с тем же числом байт); N ≥ ln 0,05 / ln(1 − 5/6) = 2 сохранения без кадра ≥ 100 мс; контроль `KYTY_FIX_<ИМЯ>=0` возвращает кадры; видео 0 глитчей, 0 маркеров смерти')
row(id='Б1б', cls='K4 (' + ref_b1b231 + '); вариант исполнителя — K3 по кадрам [c]', key1=4, kind='дефект', scenes=3, tp=30, tpc=0, P=0.2,
    what='срабатывание ограничителя BVH: обход срезан на 65 536 шагах; кадр со срабатыванием длится 266–317 мс, 6 кадров подряд',
    status='открыт; на `9235a7ac` [c]: `big_hand_pirate_island` (кадры n 332–337: 299 442, 299 580, 284 617, 300 409, 298 800, 299 220 мкс) и `voxel_world` (n 182–187: 316 631 … 283 939 мкс) — в интервале каждого из 12 кадров строка `PriorityStall:` ≈ 0,27–0,29 с, строки `BvhLoopCapTrip:` стоят в интервалах этих же кадров (не менее 10 из 12 строк двух логов; вывод интервала n 186 `c142_09` обрезан списком); Sky Garden: 22 лога с. 103–126, на с. 127+ — 0 (в `v142` 0); картинка кадров срабатывания [U] (детектор глитчей 0 на обоих видео, листы — у лида)',
    ev=INV['Б1б'] + '; `C:/kyty/s142/log_c142_02.txt:269177` (sha256 `bb6655d3d30c0bc7…`); `C:/kyty/s142/log_c142_09.txt:206646` (sha256 `eadf72b5b79ac096…`); `ctx_f0.out.txt`; `ana_f0.out.txt` (2i)',
    mech=ref_trip + '; сам обход (`380bb9d6…` и 12 BVH-программ) не исправлен — что зацикливает обход, [U]',
    game='да', user='нет', nogame='нет',
    crit='`big_hand_pirate_island` и `voxel_world` по 120 с на сборке правки: 0 строк `BvhLoopCapTrip:` и 0 кадров ≥ 100 мс на n первых 10 кадров после первого кадра сцены, сверх кадров холодного входа (вход — тёплый, второй); N ≥ ln 0,05 / ln(1 − 0,9) = 2 входа на уровень; видео 0 глитчей и лист кадров у срабатывания; контроль `=0` возвращает 6 строк; Sky Garden 300 с без `GpuHangAbort`')
row(id='Б2', cls='K3', key1=2, kind='дефект (происхождение [U])', scenes=1, tp=None, tpc=1, P=0.15,
    what='кадр 183–197 мс на n 949–954 Sky Garden',
    status='открыт; свип [c]: в интервале кадра — одна строка `PriorityStall:` и ничего иного (5 из 5 проверенных: `ack129`, `ack130`, `s12s130`, `lw4s131`, `lw5s131`) — то же событие, что Б3б; K3 на удержании Sky Garden — %d из %d входов с. 128–141 без валидации; на `9235a7ac` в `v142` (10 176 кадров после первого кадра сцены) — 0 ⇒ p на установленной сборке [U] (0/1)' % (sg_k3h, sg_ent),
    ev=INV['Б2'] + '; `ctx2_f0.out.txt`; `ana_f0.out.txt` (3)',
    mech=ref_prio + ' — чего ждёт приоритетная операция на n ≈ 950, [U]; все логи формы — сборки трека `armcopy` с. 129–131', game='да', user='нет', nogame='нет',
    crit='сначала p на `9235a7ac`: ≥ 30 входов Sky Garden до n ≥ 1 100; при p = 0 на 30 — «НЕ ДЕФЕКТ (инструментальные сборки)» по п. 228(д); иначе N ≥ ln 0,05 / ln(1 − p) входов без кадра ≥ 100 мс на n 900–1 000')
row(id='Б31', cls='K3', key1=2, kind='дефект', scenes=1, tp=120, tpc=0, P=0.15,
    what='кадр 118 647 мкс на удержании холодного входа Day and Night (`ednn122` n 1826)',
    status='открыт; Day and Night после с. 122 не входил; по форме совпадает с Б33 (кадр ≥ 100 мс на удержании холодного входа) — принадлежность к Б33 [I], интервал кадра `ednn122` в F0 не читался',
    ev=INV['Б31'], mech='[U]; кандидат — механизм Б33', game='да', user='нет', nogame='нет',
    crit='N ≥ ln 0,05 / ln(1 − 0,5) = 5 входов Day and Night без кадра ≥ 100 мс на удержании; до того — чтение интервала кадра n 1826 `ednn122` (без игры)')
row(id='Б32', cls='K3 (строка лида п. 219(в))', key1=2, kind='дефект (происхождение [U])', scenes=2, tp=None, tpc=1, P=0.1,
    what='кадры 100–236 мс на удержании вне окна Б2 (Sky Garden, `intro_next`)',
    status='открыт; свип [c]: на с. 128–141 вне n 945–960 — `lw3s131` n 1060 (155 753 мкс, в интервале `PriorityStall:` ×1), `rs135` n 7445 (235 598, без `PriorityStall:`), `s3s130` `intro_next` n 2980 (100 276), `lw6s131` — 26 кадров (в том же логе `LossWin: overflow`, инструмент `armcopy`); на `9235a7ac` в `v142` — 0 кадров ≥ 100 мс на удержании (9 577 кадров) ⇒ p [U] (0/1)',
    ev=ref_b32 + '; `ana_f0.out.txt` (3); `ctx2_f0.out.txt`', mech='[U]', game='да', user='нет', nogame='нет',
    crit='как в п. 219(в): p серией на `9235a7ac` (удержание ≥ 300 с), затем N ≥ ln 0,05 / ln(1 − p) входов без кадра ≥ 100 мс на удержании')
row(id='Б34', cls='картинка; по п. 231(г)(2) дефектом не считается', key1=2, kind='наблюдение ([U]: эталона нет)', scenes=2, tp=None, tpc=2, P=0.1,
    what='многокадровые чёрные и белые блоки в заставке уровня (`rec_c142_02.mp4` кадры ≈ 1 101–1 112, `rec_c142_03.mp4` кадры 1 174–1 178)',
    status='наблюдение (строка лида); сигнатуры в логах нет — свип её не видит; видео в F0 не смотрелись',
    ev=ref_b34, mech='[U]', game='да', user='да (эталон с PS5) или A/B ручкой', nogame='нет',
    crit='дефектом становится при эталоне или при различии A/B ручкой (п. 231(г)(2)); тогда — видео ≥ 3 000 кадров, 0 глитчей, лист')
row(id='Б6', cls='K3', key1=2, kind='наблюдение (дефект не показан)', scenes=0, tp=None, tpc=1, P=0.3,
    what='«падающие частицы»/дым в комнате с пришельцем — не проверены',
    status='открыт (не проверен); сигнатуры в логах нет', ev=INV['Б6'], mech='[U]', game='да', user='нет', nogame='нет',
    crit='видео ≥ 3 000 кадров катсцены, 0 глитчей и лист + прогон с валидацией 0 `[Vulkan][E]`; путь к комнате не назван')
row(id='Б4', cls='K1 (при выходе)', key1=3, kind='дефект', scenes=1, tp=23000, tpc=0, P=0.1,
    what='гонка выхода: `CloseAll` против гостевого `KernelOpen` ⇒ `EXIT_IF` после `Event: quit`',
    status='открыт; свип [c]: `Error: condition (m_files[index] == nullptr)` — 1 лог из %d (`dds131`); на с. 142 — 0 из 12' % len(uniq),
    ev=INV['Б4'] + '; `C:/kyty/s131/log_dds131.txt:718963`; `ana_f0.out.txt` (2c)',
    mech=ref_mfiles, game='да', user='нет', nogame='частично: стресс-тест `CloseAll` против `KernelOpen` без игры',
    crit='N ≥ ln 0,05 / ln(1 − 0,0065) ≈ 460 выходов без `--- Fatal Error ---` — по п. 228(д) «ТУПИК», если стенда выхода нет; замена — тест гонки без игры')
row(id='Б26', cls='K4', key1=4, kind='наблюдение по букве п. 228(б) (шейдеры игрой не запрошены [c]); при запросе — K1', scenes=len(LV_OP), tp=20, tpc=0, P=0.3,
    what='SOP1 `0x21` (96), SOP1 `0x0c` (1), VOPC `0xe3` (4): 101 вычислительный шейдер не транслируется',
    status='открыт (F1 идёт); свип [c]: профиль 96/1/4 — %d логов (с. 14–142), 12 из 12 логов с. 142; все 101 строка в каждом логе с. 142 — строки `CsPretranslate: skipped` спекулятивного потока, который перехватывает фатал; ни один из 101 хэша (и из 36 хэшей Ф3) ни в одном из 12 логов не встречается ни в одной строке, кроме `CsPretranslate phase …`/`skipped`: строк `CsPretranslate: miss`/`hit` обычного пути для них 0 [c] ⇒ на 11 уровнях за 120–334 с игра эти шейдеры не диспатчила; на обычном пути тот же опкод — `EXIT` (смерть процесса), маркеров смерти 0 из 12' % prof[P9614],
    ev=INV['Б26'] + '; `C:/kyty/s142/log_c142_02.txt:9989` (sha256 `bb6655d3d30c0bc7…`); `s142_f0.out.txt`; `ana_f0.out.txt` (1)',
    mech='постановка в очередь при регистрации шейдера — ' + ref_enq + '; строка — ' + ref_skip + ' под ' + ref_interc + '; обычный путь — ' + ref_take + ' → ' + ref_miss + ' → ' + ref_norm + ' → ' + ref_cfgexit + '; декодер — ' + ref_sop1 + ', ' + ref_vopc,
    game='частично', user='нет', nogame='да (тест на опкод, `shader_cfg_tests`); последствие в игре проверить нечем, пока нет сцены, которая диспатчит такой шейдер',
    crit='как п. 228(е) (1)–(5); дополнение F0: строка «0 строк маркера на входе» различает только поток спекуляции — сцену-свидетеля даёт первая строка `CsPretranslate: miss hash=<один из 101>` или `shader CFG build failed` вне `CsPretranslate:` в любом логе')
row(id='Ф5', cls='K4', key1=4, kind='дефект по букве п. 228(б) (путь исполняется на каждом входе [c]); вариант исполнителя — наблюдение до кадра-свидетеля', scenes=len(LV_OP), tp=20, tpc=0, P=0.2,
    what='новая (пакет): игнорируемое состояние ГП — метаданные цвета `dcc=true`, адреса CMASK/FMASK/DCC, режим округления цвета, включённые depth/stencil без привязки, `GE_STEREO_CNTL`, диспатч нулевого размера',
    status='открыт; [c]: каждая из шести строк — в %d…%d логах, на с. 128+ в %d из %d; строки печатаются один раз на процесс (кроме диспатча и `GE_STEREO_CNTL`); видимое последствие [U]' % (g('`DepthTarget')['logs'], g('`RenderTarget: temporary: ignoring PS5 color metadata')['logs'], g('`DepthTarget')['s128'], N128),
    ev='`C:/kyty/s142/log_c142_02.txt:207786` «skipping zero-sized dispatch»; таблица сигнатур §2',
    mech=ref_meta + ', ' + ref_maddr + ', ' + ref_round + ', ' + ref_depth + ', ' + ref_stereo + ', ' + ref_zero,
    game='да', user='нет', nogame='нет',
    crit='на член пакета: кадр-свидетель (RenderDoc или видео), где игнорируемое состояние меняет картинку; без свидетеля — «НЕ ДЕФЕКТ» по п. 228(д); при свидетеле — видео ≥ 3 000 кадров 0 глитчей + 0 `[Vulkan][E]`')
row(id='Ф3', cls='K4', key1=4, kind='наблюдение по букве п. 228(б) (шейдеры игрой не запрошены [c]); при запросе — K1 или K2', scenes=len(LV_OP), tp=20, tpc=0, P=0.2,
    what='новая: спекулятивная трансляция CS не проходит ещё у 36 шейдеров на лог — 32 «shader resource tracking», 4 «speculative translation budget exceeded» (у одного — `CFG dispatcher fallback … StructuredControlFlow`)',
    status='открыт; [c]: `resource tracking` — %d логов (с. %s–%s), бюджет — %d логов; на с. 142 — 12 из 12; обычным путём ни один из 36 хэшей в 12 логах с. 142 не запрошен (0 строк `miss`/`hit`)' % (g('`CsPretranslate: skipped … shader resource')['logs'], g('`CsPretranslate: skipped … shader resource')['first'], g('`CsPretranslate: skipped … shader resource')['last'], g('`CsPretranslate: skipped … speculative')['logs']),
    ev='`C:/kyty/s142/log_c142_02.txt:490948` (sha256 `bb6655d3d30c0bc7…`); `s142_f0.out.txt`',
    mech=ref_restr + ', ' + ref_budget + ', ' + ref_disp + '; на обычном пути бюджета нет (' + ref_norm + ') — длительность трансляции этих 4 шейдеров [U]',
    game='частично', user='нет', nogame='да (тест транслятора на шейдер из дампа)',
    crit='тест на каждый из 36 шейдеров (дамп кода из лога спекуляции) — трансляция проходит; 0 строк `skipped … resource tracking`/`budget exceeded` на входе уровня-свидетеля; видео входа 120 с без новых K1/K2; контроль `=0`')
row(id='Ф7', cls='K4', key1=4, kind='наблюдение', scenes=len(LV_OP), tp=20, tpc=0, P=0.05,
    what='новая (пакет): `file not found` на `KernelStat`, `warning: size_bytes/base is not 256-byte aligned`, `Format … cannot be used as texture`',
    status='наблюдение; [c]: `file not found` — %s строк в %d логах (в `c142_02` 6 404), выравнивание — %d логов; на с. 128+ — %d из %d' % (fmt(g('`file not found`')['lines']), g('`file not found`')['logs'], g('`warning: size_bytes')['logs'], g('`file not found`')['s128'], N128),
    ev='`C:/kyty/s142/log_c142_02.txt:30109`; `C:/kyty/s142/log_c142_02.txt:15230`',
    mech=ref_align + '; `KernelStat` на отсутствующий файл возвращает `ENOENT` (`' + CODE + ':src/kernel/fileSystem.cpp`, строка «file not found»); какие файлы игра не находит и ждёт ли их — в F0 не разобрано',
    game='нет', user='нет', nogame='да (перечень ненайденных путей — по логам)',
    crit='перечень путей `KernelStat` с `file not found` против содержимого `games/PPSA21564-app`: если все пути — необязательные пробы, «НЕ ДЕФЕКТ»; иначе строка на файл')
row(id='Б9а', cls='K4', key1=4, kind='дефект (путь исполняется [c])', scenes=1, tp=20, tpc=0, P=0.5,
    what='новая (из Б9): игра вызывает неразрешённые импорты `AudioPropagation` — 4 символа, заглушка возвращает 0',
    status='открыт; [c]: `timestop_casino` (`c142_03`) — `b-dYXrjSNZU` 2, `WXMhENV2NcA` 295, `d84otraxt2s` 365, `G+QLTfyLMYk` 362 строки (печать ограничена 1 024 вызовами — вызовов не меньше); в прочих 11 логах с. 142 — 0; до того — только `Json2` в 2 логах с. 45; утверждение ред. 2 «ни один не вызывался» для `timestop_casino` неверно; последствие (звук) [U] — видео звук не проверяет',
    ev='`C:/kyty/s142/log_c142_03.txt:239572` (sha256 `9aaa83b0c73e66b1…`); `s142_f0.out.txt`; `ana_f0.out.txt` (2h)',
    mech=ref_stubcall + ' (после 1 024 вызовов печать молчит, возврат 0); патч импорта — ' + ref_reloc,
    game='да', user='нет (картинка); да — если критерий требует слушать звук', nogame='частично: реализация 4 NID и тест без игры',
    crit='вход `timestop_casino` 120 с на сборке правки: 0 строк `Unresolved import stub called` с `AudioPropagation`; 0 маркеров смерти, видео 0 глитчей, K3 удержания не больше `c142_03`; тест на каждый из 4 NID (возврат и выходные параметры по первоисточнику); контроль `=0` возвращает строки')
row(id='Ф4', cls='K4', key1=4, kind='наблюдение (обход действует [c])', scenes=1, tp=720, tpc=0, P=0.1,
    what='новая: `KernelRead: direct read failed … reading through a host buffer` — прямое чтение в защищённые кэшем страницы вернуло 0 байт, сработал обход',
    status='наблюдение; [c]: %d логов (с. %s–%s), на с. 142 — 1 из 12 (`ice_iceberg`, 1 строка, размер 0x98290)' % (g('`KernelRead')['logs'], g('`KernelRead')['first'], g('`KernelRead')['last']),
    ev='`C:/kyty/s142/log_c142_05.txt:414100` (sha256 `9ea02549b36c0100…`)', mech=ref_kread + ' — печать перед чтением через хост-буфер; полнота обхода для прочих системных вызовов чтения [U]',
    game='нет', user='нет', nogame='да (чтение кода)',
    crit='перечень путей чтения в гостевую память без обхода (`pread`, `readv`, AIO) по коду; при находке — тест чтения в защищённую страницу')
row(id='Б1а', cls='K4 (поправка лида п. 219: на умолчаниях 0/284)', key1=4, kind='дефект, закрытый ограничителем', scenes=1, tp=None, tpc=1, P=0.1,
    what='зависание входа в обходе BVH без предела шагов',
    status='форма снята умолчанием `KYTY_BVH_LOOP_CAP`; свип [c]: `GpuHangAbort` после с. 102 — только 3 лога фикстур `fx/hang`; на с. 128+ — 0 из %d; срабатывания ограничителя на 2 новых уровнях (Б1б) ⇒ без ограничителя эти входы зависли бы [I]' % N128,
    ev=INV['Б1а'] + '; `ana_f0.out.txt` (2d)', mech='см. Б1б', game='да', user='нет', nogame='нет',
    crit='общий с Б1б (исправленный обход): серия 34 входов без зависания при ограничителе ВЫКЛ на сборке правки (ред. 2)')
row(id='Ф6', cls='K4', key1=4, kind='наблюдение', scenes=1, tp=20, tpc=0, P=0.2,
    what='новая: предупреждения слоя валидации — фрагментный шейдер пишет в `out_mrt_N`, для которого нет привязанной цели',
    status='наблюдение; [c]: логов с `[Vulkan][W]` — %d (с. %s–%s), в `w142` 916 988 строк `[Vulkan][W]`; `[Vulkan][E]` — 0 на с. 142, последняя сессия с `[Vulkan][E]` — 38' % (g('`[Vulkan][W]')['logs'], g('`[Vulkan][W]')['first'], g('`[Vulkan][W]')['last']),
    ev='`C:/kyty/s142/log_w142.txt` (sha256 `7f42a2d3e1a151a2…`); таблица сигнатур §2', mech='запись в выход без цели отбрасывается хостом; соответствие маске целей гостя [U]',
    game='нет', user='нет', nogame='да (маска записи по числу целей в пайплайне)',
    crit='прогон с валидацией Sky Garden 300 с: 0 строк `[Vulkan][W]` этой формы при 0 `[Vulkan][E]` и видео 0 глитчей; контроль `=0`')
row(id='Б30', cls='K4', key1=4, kind='наблюдение', scenes=1, tp=300, tpc=0, P=0.1,
    what='окно простоя GPU на удержании Day and Night без кадра ≥ 100 мс', status='открыт; уровень после с. 122 не входил', ev=INV['Б30'],
    mech='[U]', game='да', user='нет', nogame='нет', crit='кадр ≥ 100 мс или кадр-свидетель; иначе «НЕ ДЕФЕКТ»')
for rid, P, what, st, mech, nogame, crit in [
    ('Б7', 0.5, '`V_MUL_LEGACY_F32` / `V_FMAC_LEGACY_F32` не декодируются', 'открыт; свип [c]: строк `opcode is not implemented` семейства VOP2 (и любого, кроме SOP1 `0x21`, `0x0c`, VOPC `0xe3`) — 0 в %d логах, включая 10 новых уровней ⇒ на исполненных путях не встречен' % len(uniq), ref_vop2, 'да (тест на опкод)', 'тест на опкод; при встрече — вход сцены без `EXIT`'),
    ('Б11', 0.4, '`shader_cfg_tests`: падения `IMAGE_SAMPLE_C`, `IMAGE_SAMPLE_C_LZ`', 'открыт; в F0 тесты не запускались', '`' + CODE + ':tests/shaderCfgTests.cpp` (строки — в ред. 2)', 'да', 'оба теста проходят; затем видео сцены с тенями'),
    ('Б14', 0.4, 'траектория `rtskip=1` значениями не сверяется', 'открыт; 10 новых уровней вошли на `rtskip=1` с 0 глитчей детектора — это не сверка `rtskip=2`', '[U] (довод проекта)', 'нет', '0 расхождений `rtskip=2` + видео на сцене переписи'),
    ('Б13', 0.35, 'порядок эпох `ChangeState<Cpu,true>`', 'открыт; сигнатуры в логах нет', 'ред. 2', 'да (правка порядка + тест)', 'правка + серия без регрессии'),
    ('Б12', 0.3, 'дыра `bdastamp`: регион 4 МиБ на два диапазона', 'открыт; сигнатуры в логах нет', 'ред. 2', 'нет', 'выгрузка раскладок на сцене переписи'),
    ('Б28', 0.3, 'полнота инвалидации захвата целей при `rtskip=1`', 'открыт; сигнатуры в логах нет', 'ред. 2', 'нет', '0 расхождений `rtskip=2`, контроль `rtskip=3` падает'),
    ('Б29', 0.3, '`rtskip` в OLD: 0 пар', 'открыт; сигнатуры в логах нет', 'ред. 2', 'нет', '0 расхождений `rtskip=2` в OLD + видео'),
    ('Б8', 0.2, '`exec ? new : old` исправлен только на верхнем уровне PS', 'открыт; шейдера-свидетеля нет', 'ред. 2', 'да (тест транслятора)', 'тест + видео сцены-свидетеля'),
    ('Б10', 0.2, 'нет PCF в ручном сравнении глубины', 'открыт; кадра-свидетеля нет', 'ред. 2', 'нет', 'видео тени сцены-свидетеля'),
    ('Б27', 0.2, 'долг `daslot`: гонка размера `ahead_threads`', 'открыт; маркеров смерти на с. 128+ с этим местом — 0', 'ред. 2', 'да (стресс-тест)', 'правка + стресс-тест'),
    ('Б9', 0.1, 'неразрешённые импорты, которые игра не вызывала', 'открыт; свип [c]: `Relocate: unresolved PLT import patched to stub` — %d логов; вызванные — см. Б9а; маркер ред. 2 `=== Stubbed function` — 0 логов из %d: не срабатывал ни разу, действующий маркер — `Unresolved import stub called`' % (g('`Relocate')['logs'], len(uniq)), ref_reloc + '; ' + ref_stubbed, 'да', '0 строк `Unresolved import stub called` на входах переписи; при встрече — строка на библиотеку'),
]:
    row(id=rid, cls='K4', key1=4, kind='наблюдение (проявления нет)', scenes=0, tp=None, tpc=1, P=P, what=what, status=st, ev=INV[rid], mech=mech,
        game='нет' if nogame.startswith('да') else 'да', user='нет', nogame=nogame, crit=crit)
row(id='Ф8', cls='K4', key1=4, kind='наблюдение (последняя с. 105)', scenes=0, tp=None, tpc=1, P=0.1,
    what='новая: `AudioOut: SDL_QueueAudio failed: Invalid audio device ID` — до 438 760 строк на лог после потери аудиоустройства хоста',
    status='наблюдение; [c]: %d логов, с. %s–%s; на с. 113+ — 0' % (g('`AudioOut')['logs'], g('`AudioOut')['first'], g('`AudioOut')['last']),
    ev=g('`AudioOut')['ex'], mech='переоткрытие аудиоустройства после его потери отсутствует [I] (код в F0 не читался)', game='нет', user='да (отключение аудиоустройства)', nogame='частично',
    crit='стенд отключения аудиоустройства: звук возвращается, 0 строк после переподключения; без стенда — «ТУПИК»')
for rid, P, what, st in [
    ('Б22', 0.9, 'устаревшие утверждения в документах', 'открыт; добавить: `CLAUDE.md` «Каталог `_PipelineCache` не существует» против строки лога `saved … to _PipelineCache\\PPSA21564.bin` (Ф1); маркер Б9 ред. 2'),
    ('Б16', 0.8, 'список «14 падающих тестов» устарел', 'открыт; в F0 не перепроверялся'),
    ('Б20', 0.8, 'печати не покрывают `enter_scene.py` и `s51_vidglitch.py`', 'исполнено для печати `pred/02_sc142.md` (`C:/kyty/s142/FACTS.md:25` «в печати, Б20»); для печатей трека F — не проверялось'),
    ('Б19', 0.7, 'класс «первый символ» у флагов окружения — 52 места', 'открыт; в F0 не перепроверялся'),
    ('Б15', 0.5, '`resource_tracking_tests` падает с с. 60', 'открыт; в F0 не перепроверялся'),
    ('Б17', 0.3, '`KYTY_GPU_CHECKPOINTS=1` сам вешает вход', 'открыт; в F0 не перепроверялся'),
    ('Б18', 0.3, 'падение старта `commandRecorder.cpp:326`', 'открыт; свип [c]: 6 логов — `m5cap102`, `boot114`, `boot114b`, `boot114c`, `boot115b` (2 копии с разным sha256); все без строки входа уровня; ' + ref_recorder),
]:
    row(id=rid, cls='K5', key1=5, kind='вне трека (п. 228(а))', scenes=0, tp=None, tpc=1, P=P, what=what, status=st, ev=INV[rid], mech='—', game='нет', user='нет', nogame='да', crit='как в ред. 2')

ids = [r['id'] for r in ROWS]
check('row ids unique', len(ids) == len(set(ids)))
inv_k14 = ['Б1а', 'Б1б', 'Б2', 'Б3б', 'Б4', 'Б5', 'Б5а', 'Б6', 'Б7', 'Б8', 'Б9', 'Б10', 'Б11', 'Б12', 'Б13', 'Б14', 'Б24', 'Б25', 'Б26', 'Б27', 'Б28', 'Б29', 'Б30', 'Б31']
inv_k5 = ['Б15', 'Б16', 'Б17', 'Б18', 'Б19', 'Б20', 'Б22']
check('every open inventory row K1-K4 (24) is in the register', all(x in ids for x in inv_k14) and len(inv_k14) == 24)
check('every inventory row K5 (7) is in the register', all(x in ids for x in inv_k5) and len(inv_k5) == 7)
check('inventory rows: 24 + 7 + closed B3a = 32', len(inv_k14) + len(inv_k5) + 1 == 32)
new = [r for r in ROWS if r['id'].startswith('Ф') or r['id'] == 'Б9а']
lead_rows = ['Б32', 'Б33', 'Б34']
check('lead rows B32, B33, B34 are in the register', all(x in ids for x in lead_rows))
LET = collections.Counter()
for r in ROWS:
    if r in new or r['id'] == 'Б34':
        continue
    LET[{1: 'K1' if r['id'] == 'Б25' else 'K2', 2: 'K3', 3: 'K1', 4: 'K4', 5: 'K5'}[r['key1']]] += 1
check('course line 142 (p.231(zh)) reproduced: K1 2 / K2 1 / K3 6 / K4 17 / K5 7 = 33', dict(LET) == {'K1': 2, 'K2': 1, 'K3': 6, 'K4': 17, 'K5': 7} and sum(LET.values()) == 33)
ncls = collections.Counter(r['key1'] for r in ROWS)
k14 = sum(v for k, v in ncls.items() if k <= 4)
check('rows = inventory 31 + lead 3 + new', len(ROWS) == 31 + 3 + len(new))
check('class sums = rows', sum(ncls.values()) == len(ROWS) and k14 + ncls[5] == len(ROWS))
kinds = collections.Counter('дефект' if r['kind'].startswith('дефект') else 'наблюдение' if r['kind'].startswith('наблюдение') else 'вне трека' for r in ROWS)
check('defect + observation + out-of-track = rows', sum(kinds.values()) == len(ROWS) and kinds['вне трека'] == ncls[5])

# ranking by the keys of (В): key1 asc, scenes [c] desc, t/p class (finite, [U], needs user), t/p asc, P desc
INF = float('inf')
keyf = lambda r: (r['key1'], -r['scenes'], r['tpc'], r['tp'] if r['tp'] is not None else INF, -r['P'])
RANK = sorted(ROWS, key=keyf)
ok_order = True
for a, c in zip(RANK, RANK[1:]):
    if a['key1'] > c['key1']:
        ok_order = False
    if a['key1'] == c['key1'] and a['scenes'] < c['scenes']:
        ok_order = False
    if a['key1'] == c['key1'] and a['scenes'] == c['scenes'] and (a['tpc'], a['tp'] if a['tp'] is not None else INF) > (c['tpc'], c['tp'] if c['tp'] is not None else INF):
        ok_order = False
check('ranking order by keys 1-3', ok_order)

# ---------------------------------------------------------------- document
o = []
w = o.append
tp = lambda r: ('≈ %s с' % fmt(r['tp'])) if r['tp'] is not None else ('нужен пользователь' if r['tpc'] == 2 else '[U] / не конечна на умолчаниях')
w('# Трек F, звено F0 — реестр дефектов по логам (Lever Researcher, `HPP-289`)')
w('')
w('Решение и форма — ' + ref_p228 + ' (п. 228 прочитан целиком до первого действия). Цель программы — корректность игры на возможно большем числе сцен')
w('(п. 214–215); скорость — не цель и не гейт. Установленная сборка — `9235a7ac…`. Игры, сборок и правок кода в звене нет; замок')
w('`C:/kyty/SEALED_RUN.lock` и `C:/kyty/f287/STOP` отсутствовали перед каждым проходом; логи читались только python в двоичном режиме, блоками.')
w('Код читался по `%s` (HEAD `main` на время звена); каждая ссылка `<коммит>:<путь>:<строка>` найдена скриптом по якорю, контроль +1 — `NOT OK`' % CODE)
w('(`C:/kyty/f287/f0/refs_f0_map.txt`). Документ собран `mk_register.py`; файлы и выводы — `C:/kyty/f287/f0/`, время — `C:/kyty/f287/times.txt`.')
w('Константы п. 215, 217, 218, 228 не менялись. Документ — предложение; решения — у лида.')
w('')
w('## 0. Главное')
w('')
w('1. **Б26 по логам — наблюдение, а не исполняемый путь [c]** (независимо подтверждает ' + ref_f1rc1 + ', ' + ref_f1rc2 + ' и ' + ref_rcl1 + '). 101 строка `opcode is not implemented` в каждом логе — это строки потока')
w('   спекулятивной трансляции CS (`CsPretranslate: skipped`), который ставит в очередь каждый зарегистрированный игрой CS и перехватывает фатал.')
w('   Ни один из 101 хэша ни в одном из 12 логов с. 142 не запрошен обычным путём (0 из 18 строк `CsPretranslate: miss`/`hit` этих логов), а на обычном пути тот же')
w('   опкод — `EXIT` и смерть процесса (маркеров смерти 0 из 12). Следствие для F1: критерий «0 строк маркера на входе» проверяет поток спекуляции;')
w('   сцены, которая диспатчит такой шейдер, в логах нет. При появлении такой сцены класс строки — K1, не «картинка».')
w('2. **Атрибуция строки Б33 (K3 на удержании холодного входа, ведёт трек S) — механизм назван по коду:** сохранение кэша пайплайнов драйвера (≈ 90 МБ, 80–93 мс) раз в 20 с под')
w('   `m_mutex` при новых пайплайнах; 5 из 6 сохранений в середине уровня лежат в кадре 115–166 мс — это все 4 кадра K3 удержания переписи с. 142.')
w('3. **Б1б имеет видимое по времени кадра следствие [c]:** каждое срабатывание ограничителя BVH на `9235a7ac` — кадр 266–317 мс, 6 подряд, на 2 из 10')
w('   новых уровней. По букве п. 231(г)(3) класс остаётся K4; вариант исполнителя — K3 (вопрос В3).')
w('4. **Б9 частично опровергнут:** `timestop_casino` вызывает 4 неразрешённых импорта `AudioPropagation` (≥ 1 024 вызова) — строка Б9а.')
w('5. **Б3б и Б2 — одно событие с причинами в других строках:** на с. 142 все %d ожиданий `PriorityStall:` > 50 мс после первого кадра сцены лежат в' % (pw + ph))
w('   кадрах ≥ 100 мс; в интервале кадра Б2 (n 949–954) — одна строка `PriorityStall:` (5 из 5).')
w('6. Маркеров смерти на с. 142 — 0 из 12; `[Vulkan][E]` — 0; на с. 128–141 маркеры смерти — 3 лога, все отнесены (`s1s128`, `s2s128` — `protceil=1`; `dds131` — Б4).')
w('')
w('## 1. Объём свипа')
w('')
w('| что | число [c] |')
w('|---|---|')
w('| файлов `log_*.txt` и `_kyty*.txt` под `C:/kyty` (`loglist_f0.tsv`) | 23 281 (324,9 ГБ) |')
w('| из них в каталогах фикстур и мутантов (`fx_*`, `work_*`, `mut*`, `test_*`, `fixt*`) — не читались | 21 543 |')
w('| прочитано потоком (`sweep_f0.py`, 3 прохода, 2 513 сегментов по 256 МБ) | %s файлов, %s байт, %s строк |' % (fmt(len(recs)), fmt(sum(r['size'] for r in recs)), fmt(sum(r['lines'] for r in recs))))
w('| из них прямых детей `C:/kyty/s*/` и корня (счёт п. 228(б)) | 821 + 316 = 1 137 |')
w('| уникальных по sha256 | %s (дубликатов %d) |' % (fmt(len(uniq)), len(recs) - len(uniq)))
w('| ' + ' / '.join(BANDS) + ' | ' + ' / '.join(str(bandn[x]) for x in BANDS) + ' (сумма %s) |' % fmt(sum(bandn.values())))
w('| логов на сборках с. 128+ (с. 128–141 и с. 142) | %d + %d = %d |' % (bandn['с. 128–141'], bandn['с. 142'], N128))
w('| различных нормализованных сигнатур (адреса и числа → `X`), `sig_f0.tsv` | 820; предел 4 000 сигнатур на лог не достигнут (0 строк сверх предела) |')
w('')
w('Сессия лога — номер каталога `sNN`; для `s106_stage` — число из имени подкаталога; для корня — последний токен `_sNN` имени (7 логов без номера).')
w('Сборка в логе не печатается: «с. 128+» значит «каталог сессии ≥ 128» — это сборки `rtskip=1` и инструменты поверх них, а не ровно `9235a7ac`;')
w('ровно на `9235a7ac` — 12 логов с. 142 (sha256 сборки проверен харнессом, `C:/kyty/s142/FACTS.md:4`). Самопроверка сканера: посегментный разбор')
w('`log_c142_02.txt` (сегменты 7 МБ) равен цельному (строк 887 497, сигнатур 112, событий 3 812), sha256 равен `sha256sum`. Кадры `c142_01`…`v142`')
w('по моему разбору совпали со сводкой скорера `sc142` (первый кадр сцены, K2, K3 окна/удержания, максимум, число кадров — `ana_f0.out.txt` (7)).')
w('Ключевые слова отбора строк чувствительны к регистру (`sweep_f0.py`, `KEY`); строка без этих слов в свип не попала — см. «Не заявляется».')
w('')
w('## 2. Сигнатуры п. 228(б): число логов, сессии, сборки с. 128+, уровни, пример')
w('')
w('Уникальные логи; «уровни» — имена из `GuestOut: Level has started:` с числом логов (до 6 самых частых, затем число остальных имён).')
w('')
w('| сигнатура | логов | строк | первая / последняя сессия | логов с. 128+ (из %d) | из них с. 142 (из 12) | уровни | пример `файл:строка` | строка реестра |' % N128)
w('|---|---|---|---|---|---|---|---|---|')
tot_logs = 0
for r in SIGROWS:
    lv = ', '.join('`%s` %d' % (a, c) for a, c in r['levels'].most_common(6))
    if len(r['levels']) > 6:
        lv += ' и ещё %d' % (len(r['levels']) - 6)
    tot_logs += r['logs']
    w('| %s | %s | %s | %s / %s | %d | %d | %s | %s | %s |' % (r['label'], fmt(r['logs']), fmt(r['lines']), r['first'] if r['first'] is not None else '—', r['last'] if r['last'] is not None else '—', r['s128'], r['s142'], lv or '—', r['ex'], r['to']))
check('signature table rows = SIGS', len(SIGROWS) == len(SIGS))
w('')
w('Строк таблицы — %d. Маркеры `hold_exit` и `WARNING: the game ENDED inside the hold` пишет харнесс (`enter_scene.py`), в `log_*.txt` их нет (0 логов) —' % len(SIGROWS))
w('для с. 142 они читаны скорером из json попыток: 0 из 12 (`C:/kyty/s142/FACTS.md:219` «маркеров смерти 0»).')
w('Профили `opcode is not implemented` по логам: ' + '; '.join('%s — %d' % ('/'.join('%s %s×%d' % (a.split(' ')[0].replace('family=', ''), a.split('=')[-1], n) for a, n in p), c) for p, c in prof.most_common()) + ' (сумма %d).' % sum(prof.values()))
w('Уровни с профилем Б26 (%d имён): %s.' % (len(LV_OP), ', '.join('`%s`' % x for x in LV_OP)))
w('')
w('## 3. 12 логов с. 142 (`9235a7ac`)')
w('')
w('| тег | уровень | sha256 (16) | первый кадр сцены n | K2 | K3 окно / удерж. | max `dt` окно / удерж., мкс | `skipped draw` строк / кадров | `PriorityStall:` > 50 мс окно / удерж. (в кадре ≥ 100 мс) | `BvhLoopCapTrip:` | сохранений кэша в середине уровня → кадр, мкс | прочее |')
w('|---|---|---|---|---|---|---|---|---|---|---|---|')
saves = {}
for l in open(OUT + '/save_f0.out.txt', encoding='utf-8', errors='replace'):
    if '|' not in l:
        continue
    name, rest = l.split('|', 1)
    name = name.strip().replace(chr(92), '/').split('/')[-1]
    fr = re.findall(r'save@\d+ bytes=\d+ save_us=(\d+) -> frame n=(\d+) dt_us=(\d+)', rest)
    saves[name] = [(int(a), int(n), int(d)) for a, n, d in fr if int(n) > 2]
nsave = 0
nsave100 = 0
for r in sorted(N142, key=lambda r: r['path']):
    s = r['scenes'][-1]
    m = r['met']
    name = os.path.basename(r['path'])
    sv = saves.get(name, [])
    if not r['validation']:
        nsave += len(sv)
        nsave100 += sum(1 for a, n, d in sv if d >= 100000)
    other = []
    if any(k.startswith(b'Unresolved import stub called') for k in LS[r['path']]):
        other.append('`Unresolved import stub called` ×%d' % sum(v[0] for k, v in LS[r['path']].items() if k.startswith(b'Unresolved import stub called')))
    if any(k.startswith(b'KernelRead: direct') for k in LS[r['path']]):
        other.append('`KernelRead: direct read failed` ×1')
    if r['validation']:
        other.append('валидация: `[Vulkan][W]` %s, `[Vulkan][E]` 0; правило `dt` не применяется' % fmt(r['vk_w']))
    w('| `%s` | `%s` | `%s` | %s | %d | %d / %d | %s / %s | %d / %d | %d / %d (%d / %d) | %d | %s | %s |' % (
        name.replace('log_', '').replace('.txt', ''), s['level'], r['sha256'][:16], s['first_n'], len(s['k2']), s['k3w'], s['k3h'], fmt(s['max_w']), fmt(s['max_h']),
        m.get('skip_n', 0), m.get('skip_frames', 0), s['p_w'], s['p_h'], s['pf_w'], s['pf_h'], m.get('trip_n', 0),
        '; '.join('%d мс → n %d: %s' % (a // 1000, n, fmt(d)) for a, n, d in sv) or '—', '; '.join(other) or '—'))
check('mid-level pipeline cache saves on s142 (no validation): 6, of them 5 in a frame >= 100 ms', nsave == 6 and nsave100 == 5)
w('')
w('Профиль 96 / 1 / 4 — 12 из 12; в каждом логе 137 хэшей `CsPretranslate: skipped` (101 опкод + 32 `resource tracking` + 4 бюджет), из них на любой')
w('иной строке, кроме `CsPretranslate phase …`, — 0 из 137 (`s142_f0.out.txt`). Срез лида `sig_quick.out.txt` подтверждён: 96 / 1 / 4 на всех 12, `BvhLoopCapTrip:`')
w('на `c142_02` и `c142_09` по 6 строк.')
w('')
w('### 3.1–3.6 Разборы (выводы скриптов)')
w('')
w('- **3.1 Кадры ≥ 1 с и ≥ 100 мс после первого кадра сцены (без валидации), по полосам сессий — `ana_f0.out.txt` (3).** K2 на с. 113+: 4 лога —')
w('  `vbn113k` (Б3а, закрыт), `ctl114a` (инструмент), `eatl122` (Б5а), `edes122` (Б24); на с. 128+ — 0. K3 на удержании на с. 128–141: 9 логов')
w('  (`ack129`, `ack130`, `s12s130`, `lw3s131`…`lw6s131`, `rs135` — Sky Garden; `s3s130` — `intro_next`, 100 276 мкс).')
w('- **3.2 Интервалы кадров K3 с. 142 — `ctx_f0.out.txt`.** Крупнейшие кадры окна входа содержат дамп IR трансляции (до 74 097 строк); кадры')
w('  срабатывания BVH — `PriorityStall:` + `BvhLoopCapTrip:`; кадр `v142` n 382 (180 521 мкс, второй после первого кадра сцены) — без трансляции.')
w('- **3.3 Сохранения кэша пайплайнов — `save_f0.out.txt`.** Стартовое сохранение (кадр n 2) кадр не держит; в середине уровня — 6 сохранений, 5 кадров ≥ 100 мс.')
w('- **3.4 `PriorityStall:` — `ana_f0.out.txt` (4).** с. 113–127: 13 логов из 78; с. 128–141: 14 из 65; с. 142: 8 из 11 (без `w142`).')
w('- **3.5 Интервал кадра Б2 — `ctx2_f0.out.txt`.** n 949–954: `PriorityStall:` ×1; `rs135` n 7445 (235 598 мкс) и `s3s130` n 2980 — без `PriorityStall:`, причина [U].')
w('- **3.6 `MainTaskLate` ≥ 1 с на с. 113+ — `ana_f0.out.txt` (6):** `ctl114a`, `ctl114b`, `boot115a`, `boot115c`, `edes122`.')
w('')
w('## 4. Реестр')
w('')
w('Класс — п. 215(д)(2)(Б) с уточнениями п. 217(б)–(д), п. 218(г), (д)(2). **Дефект / наблюдение** — по п. 228(б): дефект — видимое последствие или')
w('путь, который игра исполняет [c]. Где буква п. 228(б) и мой вариант расходятся, стоят оба. «Сцены [c]» — ключ 2. t / p — секунды игры до первого')
w('воспроизведения. Столбец «без игры» отвечает на вопрос «идёт ли цикл правки и доказательства без прогона игры», а не «исправимо ли». P — [I].')
w('')
w('| № | класс | дефект / наблюдение | что | статус на сегодня | свидетельство | механизм по коду `%s` | сцены [c] | t / p | нужна игра | нужен пользователь | без игры | критерий доказательства (форма п. 228(г)(1)) | P(FIXED ≤ 2 итерации) [I] |' % CODE)
w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in ROWS:
    w('| %s | %s | %s | %s | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s |' % (r['id'], r['cls'], r['kind'], r['what'], r['status'], r['ev'], r['mech'], r['scenes'], tp(r), r['game'], r['user'], r['nogame'], r['crit'], ('%.2f' % r['P']).replace('.', ',')))
w('')
w('**Итого строк — %d:** из `inventory141.md` ред. 2 — 31 (24 открытых K1–K4 + 7 K5), строк лида — 3 (Б32 п. 219(в); Б33, Б34 п. 231(г)), новых F0 — %d (%s). По ключу 1: K1/K2 на входе и удержании — %d, K3 — %d,' % (len(ROWS), len(new), ', '.join(r['id'] for r in new), ncls[1], ncls[2]))
w('K1/K2 вне входа и удержания — %d, K4 — %d, K5 — %d (сумма %d); K1–K4 — %d. По столбцу «дефект / наблюдение»: дефект — %d, наблюдение — %d, вне трека (K5) — %d (сумма %d).' % (ncls[3], ncls[4], ncls[5], sum(ncls.values()), k14, kinds['дефект'], kinds['наблюдение'], kinds['вне трека'], sum(kinds.values())))
w('Строка курса 142 (п. 231(ж)) воспроизведена по строкам ред. 2 и лида без Б34: K1 2 / K2 1 / K3 6 / K4 17 / K5 7 = 33 (ключ 1 «K3 — 7» включает наблюдение Б34).')
w('')
w('**Не ранжируются:** Б3а (рывок 3 с — отнесён к закрытому с. 114–115; ' + INV['Б3а'] + '; свип: K2 на удержании на с. 115+ — только Б24, `ana_f0.out.txt` (3));')
w('Б23 (`protceil=1`, `ErrorDeviceLost` в `s1s128`, `s2s128` — значение выведено из употребления); `LossWin: overflow kind=open` (`lw6s131`, инструмент `armcopy`,')
w('не умолчание; в том же логе 26 кадров K3 на удержании); `TextureCache: failed to map reusable download buffer` (`bf96a`, с. 96, инструмент).')
w('Закрытые по сигнатурам свипа (последняя сессия < 113): `--- Error ---` (с. 102), `Unhandled host exception` (с. 59), `[Vulkan][E]` (с. 38),')
w('`Skipping unsupported GE shader draw` (с. 32), `warning: executing wave64 compute shader` (с. 67), `shader IR validation failed` (с. 30),')
w('`vkQueuePresentKHR … eErrorOutOfDateKHR` (с. 49), CFG `unsupported_reason=` (с. 59).')
w('')
w('## 5. Ранжирование по ключам (В) `inventory141.md` — предложение')
w('')
w('Ключ 1 — K1/K2 на входе или удержании > K3 > K1/K2 вне входа и удержания > K4 > K5; ключ 2 — число сцен [c]; ключ 3 — t / p (p [U] и «не конечна» —')
w('в конец ступени ключа 2, «нужен пользователь» — после них); равенство — по P.')
w('')
w('| место | строка | ключ 1 | ключ 2 (сцены [c]) | ключ 3 | P [I] |')
w('|---|---|---|---|---|---|')
K1N = {1: 'K1/K2 на входе/удержании', 2: 'K3', 3: 'K1/K2 вне входа и удержания', 4: 'K4', 5: 'K5'}
for i, r in enumerate(RANK, 1):
    w('| %d | %s — %s | %s | %d | %s | %s |' % (i, r['id'], r['what'][:90], K1N[r['key1']], r['scenes'], tp(r), ('%.2f' % r['P']).replace('.', ',')))
w('')
w('## 6. Предложение порядка итераций F2…F6 (F1 = Б26: F1a — «нужен проект», F1c — `NOT EVALUABLE`)')
w('')
w('Холодный вход — Б5, Б5а, Б33 — ведёт трек S (' + ref_p229 + '); в очередь F они не ставятся. Атрибуция Б33 этого реестра (сохранение кэша')
w('пайплайнов под `m_mutex`) — вход трека S: в `docs/track-s/s0-design.md` она не названа (0 вхождений `WriteDriverCache`/`pipeline cache: saved`).')
w('Первые по ключам Б25 и Б24 не имеют воспроизведения без пользователя или с конечной ценой. Остальное — по ключам, с названными отступлениями:')
w('')
w('| итерация | строка | почему здесь | что нужно до кода |')
w('|---|---|---|---|')
w('| F2 | **Б1б (+ Б1а)** обход BVH | единственная строка очереди F с [c]-следствием по времени кадра на `9235a7ac` (2 уровня, 6 кадров ≈ 0,3 с подряд), пользователь не нужен; исправление обхода закрывает и Б1а; порядок п. 228(е) | проект до кода: что зацикливает обход `380bb9d6…` на `big_hand_pirate_island` — дамп привязок `KYTY_DUMP_CS` на кадре срабатывания (один прогон Harness Engineer под замком) |')
w('| F3 | **Б9а** `AudioPropagation` | единственная K4 с исполняемым путём [c], уровень-свидетель есть, правка мала | первоисточник по 4 NID (имена функций и возвраты); решение лида по В2 |')
w('| F4 | **Б11** `IMAGE_SAMPLE_C` (в пакете с Ф3 при общем доказательстве тестами, п. 228(г)) | без игры и без замка: тесты транслятора; порядок п. 228(е) | список падений `shader_cfg_tests` на HEAD (Б16) |')
w('| F5 | **Б4** гонка выхода — тест без игры | K1; по п. 228(д) с игрой — «ТУПИК» (≈ 460 выходов), замена — стресс-тест `CloseAll` против `KernelOpen` | критерий лида: тест воспроизводит `EXIT_IF` до правки |')
w('| F6 | **Ф5 / Ф7** пакеты наблюдений — офлайн-разбор | решает «НЕ ДЕФЕКТ» или строку со свидетелем без игры: перечень ненайденных файлов, кадр-свидетель игнорируемого состояния | ответ лида на В2 |')
w('')
w('Вне очереди, только прогоны (без кода): серия p на `9235a7ac` для Б2, Б32 (одна серия Sky Garden ≥ 300 с — данные даёт серия `sc143` и повторные V) и Б25')
w('(`intro_next` ≥ 90 с) — решает «НЕ ДЕФЕКТ» / «ТУПИК»; чтение интервала кадра `ednn122` n 1826 (Б31) — офлайн.')
w('Отличие от порядка п. 228(е): Б11 — после Б9а (у Б11 0 сцен [c], у Б9а путь исполняется [c]).')
w('')
w('## 7. Вопросы лиду')
w('')
w('- **В1 (F1, Б26).** По логам шейдеры с тремя опкодами игра не диспатчит (§0 п. 1). Оставить Б26 дефектом K4 по порядку п. 228(е) или перевести в')
w('  «наблюдение» до сцены-свидетеля (первая строка `CsPretranslate: miss` с одним из 101 хэшей)? Критерий (3) п. 228(е) — «0 строк … на входе» — при любом')
w('  ответе проверяет поток спекуляции, а не кадр. Семантика опкодов — задача F1a; имена по памяти: SOP1 `0x21` — `S_SWAPPC_B64`, SOP1 `0x0c` — `S_BREV_B64`')
w('  [I-память; веб недоступен: `gitlab.freedesktop.org` — отказ доступа, зеркало — 404, 2 попытки].')
w('- **В2 (определение п. 228(б)).** «Путь, который игра исполняет» по букве делает дефектами пакеты Ф5 (игнорируемое состояние ГП) и Б9а; вариант исполнителя —')
w('  дефект только при кадре-свидетеле или вызове с ненулевым последствием. В реестре стоят оба прочтения; какое действует?')
w('- **В3 (классы).** Б1б: п. 231(г)(3) оставил K4 («на листах видимого следствия нет [I]»); по логам каждое срабатывание — кадр 266–317 мс [c]. Перевести')
w('  Б1б в K3 (и Б3б — в K3-симптом)? В реестре класс — по букве п. 231, вариант исполнителя — рядом.')
w('- **В7 (Б33 и трек S).** Атрибуцию Б33 (сохранение кэша пайплайнов, 5 из 6 сохранений в кадре ≥ 100 мс) передать звену S1/S2 как вход или вести итерацией F?')
w('- **В4 (окно входа новых уровней).** Кадры срабатывания BVH лежат в окне входа (первые 10 кадров после первого кадра сцены); по п. 218(г) K3 в окне —')
w('  только выше тёплой базы, а её для 10 новых уровней нет. Считаю K3 по букве «`dt` ≥ 100 мс» с пометкой «тёплой базы нет»; вариант исполнителя — второй вход')
w('  тех же уровней как тёплая база до любой правки (10 входов по 120 с).')
w('- **В5 (сцены [c] у Б26, Ф3, Ф5, Ф7).** Ключ 2 посчитан по всем %d именам из строки входа, включая проходные (`ps_logo`, `title_controller_ship`, `worldmap`,' % len(LV_OP))
w('  `transition_next`); при счёте только уровней `-lvl` — 15. Порядок строк от этого не меняется.')
w('- **В8 (правило 27).** Комментарий лида от 23:59:00Z (правило 27, строки Б33/Б34) замечен в 00:29Z, перед сдачей: команды 23:59–00:29Z шли без первой')
w('  строки проверки замка; замок отсутствовал при каждой сделанной проверке, свип ждёт замок внутри (`wait_gate`). Пропуск чтения комментариев — мой.')
w('- **В6 (коммит).** Граница роли Lever Researcher — «не коммитишь»; общие правила трека F называют коммит. Файлы положены в рабочее дерево')
w('  (`docs/track-f/register.md`, `docs/track-f/f0/`), коммит не сделан — оставлен приёмке, как в с. 141. `sig_f0.tsv` и `agg_f0.json` в git не кладутся:')
w('  в примерах строк старых логов есть путь с именем пользователя.')
w('')
w('## 8. Сверка')
w('')
w('**Суммы пересчитаны: %d из %d; порядок ключей 1–3 проверен скриптом: да.** Ссылок на git по якорю: %d, контроль +1 — %d `NOT OK`; ссылок на локальные файлы (логи, `FACTS.md`) по якорю: %d из %d, у %d соседняя строка повторяет якорь (повтор строки лога), sha256 файлов — в карте.' % (sum(1 for c in CHECKS if c[1]), len(CHECKS), len(REFMAP), sum(1 for x in REFMAP if x[5] == 'NOT OK'), sum(1 for x in LOCMAP if x[3] == 'OK'), len(LOCMAP), sum(1 for x in LOCMAP if x[4] == 'repeats')))
w('Проверки (`mk_register.py`, `assert` на каждую): ' + '; '.join(c[0] for c in CHECKS) + '.')
w('')
w('## 9. Не заявляется')
w('')
w('Что реестр полон: свип видит только строки с ключевыми словами `KEY` (регистр учитывается), логи в каталогах фикстур не читались, 104 уровня из 114 входили')
w('не больше одного раза или не входили, звук и ввод логами не покрыты; что какая-либо строка исправима; что какое-либо наблюдение безвредно; что')
w('неисполняемые опкоды меняют или не меняют картинку; что шейдеры Б26 не диспатчатся вне просмотренных 120–334 с одиннадцати уровней; что кадр ≥ 100 мс')
w('с сохранением кэша вызван только сохранением (в 3 из 4 прочитанных интервалов есть и трансляция); что срабатывание ограничителя BVH портит или не портит картинку;')
w('что «с. 128+» — ровно `9235a7ac`; что правка чего-либо ускоряет игру; 60 FPS; корректность любой сцены и `SCENE_OK`.')
w('')
os.makedirs(os.path.dirname(DOC), exist_ok=True)
open(DOC, 'wb').write(NL.join(o).encode('utf-8'))
with open(OUT + '/refs_f0_map.txt', 'wb') as f:
    for x in REFMAP:
        f.write(('%s:%s:%d | anchor: %s | anchor in line: %s | +1 control: %s' % x + NL).encode('utf-8'))
    for x in LOCMAP:
        f.write(('%s:%d | anchor: %s | anchor in line: %s | +1 control: %s | sha256 %s' % x + NL).encode('utf-8'))
    f.write(('refs %d, OK %d, +1 NOT OK %d' % (len(REFMAP), sum(1 for x in REFMAP if x[4] == 'OK'), sum(1 for x in REFMAP if x[5] == 'NOT OK')) + NL + 'ALL OK' + NL).encode('utf-8'))
print('rows', len(ROWS), 'K1-K4', k14, 'new', len(new), 'checks', len(CHECKS), 'refs', len(REFMAP), 'sigs', len(SIGROWS), 'levels with profile', len(LV_OP), 'stall levels', len(stall_lv))
print('rank:', ' > '.join(r['id'] for r in RANK))
print('doc bytes', os.path.getsize(DOC), 'sha256', hashlib.sha256(open(DOC, 'rb').read()).hexdigest())
print('ALL OK')
