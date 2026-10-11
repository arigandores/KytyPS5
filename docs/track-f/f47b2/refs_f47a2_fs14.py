# F47b2 (HPP-808): copy of refs_f47a2.py with commit ea6c6e9e -> eb7e8b91 (FS14a worktree HEAD, ROADMAP p.715(d) pre-check; FS14 not installed)
# F47a2 (HPP-807): map of the report links <commit>:<path>:<line>, form of F47a refs_f47a.py. check: every link's line contains
# its anchor and the next line, with leading whitespace removed, starts with its +1 control ('' = empty line) (git show);
# neg: every link with the anchor mutated and every link moved to line +1 must fail; text: every link written in the report
# is in the table and nothing else.
# Usage: python refs_f47a2.py check | neg | text <report.md>
import re, subprocess, sys

ROOT = 'C:/kyty/KytyPS5'
RM = 'docs/ROADMAP.md'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
FSY = 'src/kernel/fileSystem.cpp'
VO = 'src/graphics/presentation/videoOut.cpp'
# commit, path, line, anchor (substring of the line), +1 control (prefix of the next line after lstrip; '' = empty line)
REFS = [
    ('aab8eeab', RM, 24693, '708. **Звено F47c трека F (`HPP-804`, лид;', '(а) **Приёмка строкой. F47a ✓**'),
    ('aab8eeab', RM, 24695, '   (б) **Решения по RC1–RC11 F47b (все приняты) — формы членов для издания 2.**',
     '(в) **Правило исхода F47f (лид, до данных).**'),
    ('aab8eeab', RM, 24696, '   (в) **Правило исхода F47f (лид, до данных).**', '(г) **Форма серии F47d'),
    ('aab8eeab', RM, 24697, '   (г) **Форма серии F47d (Harness Engineer, замок; константы — до данных).**', '(д) **Разбор F47e'),
    ('aab8eeab', RM, 24698, '   (д) **Разбор F47e (Emu Engineer;', '(е) **Реестр §120**'),
    ('aab8eeab', RM, 24700, '   (ж) **Звенья.** F47c `HPP-804` — `done` этим пунктом.', '(з) **Априор лида [I]:**'),
    ('aab8eeab', RM, 24702, '   (и) **Не заявляется:** что блоки Б34', ''),
    ('eb7e8b91', BC, 1956, 'TraceImageUpload(vaddr, size, "owner");', 'const auto offset = buffer.Offset(vaddr);'),
    ('eb7e8b91', BC, 1962, 'TraceImageUpload(vaddr, size, "gpu-buffer");', 'const auto [buffer, offset] = ObtainBuffer('),
    ('eb7e8b91', BC, 1972, 'if (vaddr != dump_tex) {', 'ImageSource imported {};'),
    ('eb7e8b91', BC, 1975, 'TraceImageUpload(vaddr, size, "import:no-owner");', 'return imported;'),
    ('eb7e8b91', BC, 1979, 'TraceImageUpload(vaddr, size, "staging:no-owner");', ''),
    ('eb7e8b91', BC, 2015, 'std::getenv("KYTY_HOST_IMPORT_MIN_KB");', 'return (value != nullptr ? std::strtoull(value, nullptr, 10) : uint64_t {64}) * 1024u;'),
    ('eb7e8b91', BC, 2018, 'if (!m_host_import.Available() || size < min_bytes || result == nullptr) {', 'return false;'),
    ('eb7e8b91', BC, 2059, 'Common::FrameStats::Add(Common::FrameStats::Counter::ImgImports, 1);',
     'Common::FrameStats::Add(Common::FrameStats::Counter::ImgImportBytes, size);'),
    ('eb7e8b91', BC, 2118, 'Common::FrameStats::Add(Common::FrameStats::Counter::ImgImports, 1);',
     'Common::FrameStats::Add(Common::FrameStats::Counter::ImgImportBytes, size);'),
    ('eb7e8b91', 'src/common/frameStats.h', 140, 'ImgImports,        // image sources copied on the GPU from imported guest memory', 'ImgImportBytes,'),
    ('eb7e8b91', VO, 1445, 'img_imp=%llu img_imp_kb=%llu img_imp_pieces=%llu', '" img_defer=%llu img_defer_kb=%llu'),
    ('eb7e8b91', VO, 1518, 'd(FS::Counter::ImgImports), d(FS::Counter::ImgImportBytes) / 1024u,', 'd(FS::Counter::ImgImportPieces),'),
    ('eb7e8b91', 'src/graphics/host_gpu/renderer/cache/textureCache.cpp', 199, '"Kyty.{}.Image[guest=0x{:016x} size=0x{:x}', '"samples={}]",'),
    ('eb7e8b91', 'src/graphics/host_gpu/vulkanCommon.h', 36, 'if (!Config::GraphicsDebugDumpEnabled() || device == nullptr',
     'VULKAN_HPP_DEFAULT_DISPATCHER.vkSetDebugUtilsObjectNameEXT == nullptr) {'),
    ('eb7e8b91', FSY, 714, 'if (!g_stream_trace || size < (64u << 10)) {', 'return t;'),
    ('eb7e8b91', FSY, 766, 'LOGF("StreamRead: #%" PRIu64 " tid=%d dst=0x%016" PRIx64 " size=0x%" PRIx64 " %s pre[%s]',
     '"read_us=%" PRIu64 " t=%" PRIu64 " hash=0x%016" PRIx64'),
    ('eb7e8b91', FSY, 900, 'LOGF("\\tRead %u bytes from: %s\\n", bytes_read,', 'static const bool stream_trace = Common::EnvFlagOn("KYTY_STREAM_TRACE");'),
    ('eb7e8b91', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 4946,
     'PipelineCacheLog("Vulkan pipeline cache: loaded {} bytes from {}", initial_data.size(),', 'path);'),
]
cache = {}


def lines(commit, path):
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
        cache[key] = out.decode('utf-8').split('\n')
    return cache[key]


def ok_link(commit, path, line, anchor, plus1):
    L = lines(commit, path)
    if line < 1 or line > len(L) - 1:
        return False
    nxt = L[line].lstrip()
    return anchor in L[line - 1] and (nxt.startswith(plus1) if plus1 else nxt.strip() == '')


def main():
    mode = sys.argv[1]
    if mode == 'check':
        bad = 0
        for r in REFS:
            good = ok_link(*r)
            bad += not good
            print('%s %s:%s:%d' % ('ok ' if good else 'BAD', r[0], r[1], r[2]))
        print('links %d bad %d' % (len(REFS), bad))
        print('ALL OK' if bad == 0 else 'FAIL')
        return 0 if bad == 0 else 1
    if mode == 'neg':
        caught = 0
        for c, p, n, a, p1 in REFS:
            caught += (not ok_link(c, p, n, a + ' MUTANT', p1)) and (not ok_link(c, p, n + 1, a, p1))
        print('neg %d of %d caught (anchor mutant and line +1)' % (caught, len(REFS)))
        print('ALL OK' if caught == len(REFS) else 'FAIL')
        return 0 if caught == len(REFS) else 1
    if mode == 'text':
        text = open(sys.argv[2], encoding='utf-8').read()
        found = set(re.findall(r'`([0-9a-f]{8}):([^`:]+):(\d+)`', text))
        table = {(c, p, str(n)) for c, p, n, _, _ in REFS}
        extra, missing = found - table, table - found
        print('text links %d table %d extra %s missing %s' % (len(found), len(table), sorted(extra), sorted(missing)))
        print('ALL OK' if not extra and not missing else 'FAIL')
        return 0 if not extra and not missing else 1
    return 2


sys.exit(main())
