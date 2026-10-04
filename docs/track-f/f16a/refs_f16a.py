# F16a (HPP-518): check of the references of f16a.md (general rule 24(1)): <commit>:<path>:<line> with an anchor and the
# +1 control line.  Usage: python refs_f16a.py <code_commit>   (prints 'N of N' and 'ALL OK')
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
CODE = sys.argv[1]
DOC = 'c6083a1f'
R = 'src/graphics/host_gpu/renderer/'
REFS = [
    (DOC, 'docs/ROADMAP.md', 21926, '(ж) **Следующая итерация очереди F — F16 = Ф7 + Ф5', 'перешла в код, F16 идёт параллельно'),
    (DOC, 'docs/track-f/register.md', 156, '| Ф5 | K4 | дефект по букве п. 228(б)', '| Ф3 | K4 | наблюдение по букве'),
    (DOC, 'docs/track-f/register.md', 158, '| Ф7 | K4 | наблюдение |', '| Б9а | K4 | дефект'),
    (CODE, 'src/kernel/fileSystem.cpp', 1099, 'LOGF("\\t file not found\\n");', 'return KERNEL_ERROR_ENOENT;'),
    (CODE, 'src/kernel/fileSystem.cpp', 1091, 'LOGF("\\t KernelStat: %s\\n", path);', ''),
    (CODE, 'src/kernel/fileSystem.cpp', 475, 'if (!creat && !dir_exist && !file_exist) {', 'g_files->DeleteDescriptor(descriptor);'),
    (CODE, 'src/kernel/fileSystem.cpp', 357, 'return p.dir / rel_path;', '#else'),
    (CODE, 'src/emulator.cpp', 246, 'Libs::LibKernel::FileSystem::Mount(options.app0_dir, "/app0");',
     'Libs::LibKernel::FileSystem::Mount(options.app0_dir, "/hostapp");'),
    (CODE, 'src/emulator.cpp', 100, 'MountOrCreateDir("_DownloadData/" + title_id, "/download0");',
     'MountOrCreateDir("_TempData/" + title_id, "/temp0");'),
    (CODE, 'src/libs/agc.cpp', 3071, 'warning: size_bytes is not 256-byte aligned', '}'),
    (CODE, 'src/libs/agc.cpp', 3081, 'warning: base is not 256-byte aligned', '}'),
    (CODE, 'src/libs/agc.cpp', 3106, 'cmd[2] = (no_size ? 0 : static_cast<uint32_t>(size_bytes >> 8u));', 'cmd[3] = 0;'),
    (CODE, 'src/graphics/guest_gpu/command_processor/pm4Handlers.cpp', 1318, 'KYTY_CP_OP_PARSER(CpOpAcquireMem) {',
     'Common::RbCen::Reset'),
    (CODE, 'src/graphics/guest_gpu/command_processor/pm4Handlers.cpp', 578, 'r.round_mode               = KYTY_PM4_GET',
     'r.fmask_data_compression_disable ='),
    (CODE, 'src/graphics/guest_gpu/command_processor/pm4Handlers.cpp', 4017,
     'LOGF("warning: ignoring indirect uc reg GE_STEREO_CNTL at 0x%" PRIx32', '", value = 0x%08" PRIx32 "\\n",'),
    (CODE, 'src/graphics/presentation/window/vulkanWindow.cpp', 454,
     'LOGF("Format vk::Format::eR8G8B8A8Srgb cannot be used as texture\\n");', ''),
    (CODE, 'src/graphics/presentation/window/vulkanWindow.cpp', 467,
     'LOGF("Format vk::Format::eB8G8R8A8Srgb cannot be used as texture\\n");', ''),
    (CODE, R + 'debug.cpp', 226, 'LOGF("RenderTarget: temporary: ignoring PS5 color metadata fast_clear=%s dcc=%s "', ''),
    (CODE, R + 'debug.cpp', 246, 'LOGF("RenderTarget: temporary: ignoring PS5 color round mode\\n");', 'logged = true;'),
    (CODE, R + 'debug.cpp', 313, 'LOGF("RenderTarget: temporary: ignoring PS5 metadata addresses cmask=0x%016" PRIx64', ''),
    (CODE, R + 'colorRenderTarget.cpp', 431, 'const bool has_dcc        = rt.info.dcc_compression_enable && rt.dcc_addr.addr != 0;',
     'if (has_dcc) {'),
    (CODE, R + 'colorRenderTarget.cpp', 441, '} else if (rt.info.cmask_fast_clear_enable && rt.cmask.addr != 0 && samples == 1 &&',
     'levels == 1 && !volume && width % 1024 == 0 && height % 1024 == 0) {'),
    (CODE, R + 'cache/textureCache.cpp', 1916, 'if (metadata.clear_mask == 0 || image.info.resources.levels != 1 ||',
     'desc.info.metadata.range.size == 0 || metadata.fill_size < desc.info.metadata.range.size) {'),
    (CODE, R + 'cache/textureCache.cpp', 3204, 'void TextureCache::TrackDccFill(uint64_t address, uint64_t size, uint32_t fill_value) {', ''),
    (CODE, R + 'cache/textureCache.cpp', 3184, 'bool TextureCache::ClearMeta(uint64_t address) {', ''),
    (CODE, R + 'renderCompute.cpp', 245, 'cache.TrackDccFill(descriptor.Base48(), size, packed_clear);', ''),
    (CODE, R + 'renderCompute.cpp', 936, 'if (!indirect && (thread_group_x == 0 || thread_group_y == 0 || thread_group_z == 0)) {', ''),
    (CODE, R + 'renderCompute.cpp', 944, 'return;', '}'),
    (CODE, R + 'renderDraw.cpp', 2534, 'static bool ConsumeMetadataColorOperation(const CommandBuffer& buffer) {', ''),
    (CODE, R + 'depthRenderTarget.cpp', 277, 'const bool depth_active = dc.z_enable || dc.depth_bounds_enable ||', ''),
    (CODE, R + 'depthRenderTarget.cpp', 333, 'r = {};', 'if (!depth_active && !stencil_active) {'),
    (CODE, R + 'depthRenderTarget.cpp', 358, 'LOGF("DepthTarget: ignoring enabled depth/stencil state without a bound attachment\\n");', ''),
    (CODE, R + 'pipeline/descriptors.cpp', 3492,
     'void RenderExecutor::MaterializeDeferredDccClear(CommandBuffer& buffer, ImageId id, Image& image) {', ''),
]
cache = {}
ok = 0
for commit, path, line, anchor, plus1 in REFS:
    key = (commit, path)
    if key not in cache:
        cache[key] = subprocess.run([GIT, '-C', REPO, 'show', commit + ':' + path], capture_output=True).stdout.decode(
            'utf-8', 'replace').replace('\r\n', '\n').split('\n')
    ls = cache[key]
    a = ls[line - 1] if line - 1 < len(ls) else ''
    b = ls[line] if line < len(ls) else ''
    good = anchor in a and (plus1 in b)
    ok += good
    if not good:
        near = [i + 1 for i, x in enumerate(ls) if anchor in x][:4]
        print('FAIL %s:%s:%d anchor at %s; line: %r; +1: %r' % (commit, path, line, near, a.strip()[:80], b.strip()[:80]))
print('%d of %d' % (ok, len(REFS)))
print('ALL OK' if ok == len(REFS) else 'CHECK FAILED')
