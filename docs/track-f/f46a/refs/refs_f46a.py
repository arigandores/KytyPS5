# Track F, F46a (HPP-798): the map of the report's links <commit>:<path>:<line> (general rule 24(1)): each link has an
# anchor - a substring of that line - and the +1 control - a substring of the next line. Modes:
#   python refs_f46a.py find  - prints the TSV (commit, path, line, anchor, next) from the anchors below (first match
#                               of the anchor in `git show <commit>:<path>`; an anchor that is not found or found twice
#                               is an error) into refs_f46a.tsv
#   python refs_f46a.py check - reads refs_f46a.tsv and checks every link against git (anchor in the line, the +1
#                               substring in the next line); prints links N bad K and ALL OK / FAILED
#   python refs_f46a.py neg   - the negative control: every link shifted by +1 must fail (caught N of N)
#   python refs_f46a.py text <report.md> - every `<commit>:<path>:<line>` of the report is in the TSV (missing 0)
import os
import re
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, 'refs_f46a.tsv')
C = '1398d44d'
DH = 'src/graphics/host_gpu/renderer/diagF5.h'
DC = 'src/graphics/host_gpu/renderer/diagF5.cpp'
TH = 'src/graphics/host_gpu/renderer/cache/textureCache.h'
TC = 'src/graphics/host_gpu/renderer/cache/textureCache.cpp'
DS = 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
VW = 'src/graphics/presentation/window/vulkanWindow.cpp'
TS = 'tests/ShaderRecompilerComputeTests.cpp'
# (path, anchor, +1 substring)
ANCHORS = [
    (DH, '	F26TintApplied,', '	F26TintSkip,'),
    (DH, 'enum class DccApplyResult : uint8_t { Cleared, Declined, Dropped };', 'enum class F26Site : uint8_t'),
    (DH, 'struct FirstExecLine {', '	uint64_t n       = 0;'),
    (DH, '[[nodiscard]] TintResult F26TintAt(uint32_t mode, uint64_t key, uint64_t address, bool removes_mark,',
     'vk::ClearColorValue& clear);'),
    (DC, '    "f26_tint_applied",      // Track F, F46a (item 702(e)(4))', '    "f26_tint_skip",'),
    (DC, 'std::string FormatDccStaleApply(const DccApplyLine& line) {', 'return fmt::format("DiagF5Ev: dcc_stale_apply'),
    (DC, 'std::string FormatFirstExec(const FirstExecLine& line) {', 'return fmt::format("DiagF5Ev: f26_first_exec'),
    (DC, 'bool NoteFirstExec(const FirstExecLine& line) {', 'if (line.n == 0 || line.n > 256)'),
    (DC, 'uint32_t ParseTintMode(const char* value) {', 'if (value == nullptr) {'),
    (DC, 'uint64_t ParseTintDcc(const char* value) {', 'if (value == nullptr || value[0] == 0) {'),
    (DC, 'static const uint32_t mode = ParseTintMode(std::getenv("KYTY_F26_TINT"));', 'return mode;'),
    (DC, 'static const uint64_t key = ParseTintDcc(std::getenv("KYTY_F26_TINT_DCC"));', 'return key;'),
    (DC, 'bool LogF26TintMode() {', 'static std::atomic<bool> logged {false};'),
    (DC, 'TintResult F26TintAt(uint32_t mode, uint64_t key, uint64_t address, bool removes_mark, vk::Format format,',
     'vk::ClearColorValue& clear) {'),
    (DC, 'if (!DccFixedClearSupported(format) || vk::componentCount(format) < 3) {', 'return TintResult::Skip;'),
    (DC, 'TintResult F26Tint(uint64_t address, bool removes_mark, vk::Format format, vk::ClearColorValue& clear) {',
     'const auto result = F26TintAt('),
    (TH, 'enum class F26Site : uint8_t; // Track F, F46a (diagF5.h)', '} // namespace DiagF5'),
    (TH, '	struct F26Deferred {', 'uint64_t n        = 0;'),
    (TH, '	std::unordered_map<uint64_t, F26Deferred>         m_f26_marks;', 'm_f26_marks_count {0};'),
    (TH, '	std::unordered_map<uint64_t, std::vector<uint64_t>> m_f26_first;', 'm_f26_first_count {0};'),
    (TC, 'F26DropLocked(metadata->first, DiagF5::F26Site::Delete, metadata->second.clear_mask);', '}'),
    (TC, '	F26Scope(DiagF5::DccSite site, TextureCache* cache): m_site(site), m_cache(cache) {}', '~F26Scope() {'),
    (TC, '	[[nodiscard]] bool KeptNow() const {', 'return m_fix && m_probe.bucket_stale && !m_probe.exact_stale'),
    (TC, '			m_cache->F26MarkLocked(m_line.dcc, {.n = n, .image = m_line.image, .dcc = m_line.dcc});', '}'),
    (TC, '			m_cache->F26ArmFirstExecLocked(m_line.dcc, n);', '}'),
    (TC, '	F26Scope f26 {DiagF5::DccSite::Prepare, this};', 'auto& image            = m_slot_images[id];'),
    (TC, '				(void)DiagF5::F26Tint(desc.info.metadata.range.address,',
     'f26.KeptNow() || F26HasMarkLocked(desc.info.metadata.range.address), view.format,'),
    (TC, '		F26ExecLocked(desc.info.metadata.range.address, image.info.data.address, DiagF5::F26Site::Prepare,',
     'f5id_mask0 & ~metadata.clear_mask);'),
    (TC, 'F26DropLocked(desc.info.metadata.range.address, DiagF5::F26Site::Retype, metadata.clear_mask);', '}'),
    (TC, 'F26DropLocked(metadata->first, DiagF5::F26Site::Retype, metadata->second.clear_mask);', '}'),
    (TC, '			F26DropLocked(address, DiagF5::F26Site::Fill, found->second.clear_mask);', '}'),
    (TC, '	F26Scope   f26 {DiagF5::DccSite::Adopt, this};', 'const bool f5id     = DiagF5Id::On();'),
    (TC, '		f26.Deferred();', '} else {'),
    (TC, 'void TextureCache::F26MarkLocked(uint64_t address, const F26Deferred& mark) {',
     'if (m_f26_marks.contains(address)) [[unlikely]] {'),
    (TC, 'void TextureCache::F26ArmFirstExecLocked(uint64_t address, uint64_t n) {', 'm_f26_first[address].push_back(n);'),
    (TC, 'void TextureCache::F26ExecLocked(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers) {',
     'if (m_f26_marks_count.load(std::memory_order_relaxed) != 0) {'),
    (TC, 'void TextureCache::F26Exec(uint64_t address, uint64_t image_address, DiagF5::F26Site site, uint32_t layers) {',
     'if (m_f26_marks_count.load(std::memory_order_relaxed) == 0 &&'),
    (TC, 'void TextureCache::F26Declined(uint64_t address, uint64_t image_address, uint32_t layers) {',
     'if (m_f26_marks_count.load(std::memory_order_relaxed) == 0) {'),
    (TC, 'void TextureCache::F26DropLocked(uint64_t address, DiagF5::F26Site site, uint32_t layers) {',
     'const auto found = m_f26_marks.find(address);'),
    (TC, 'bool TextureCache::F26HasMark(uint64_t address) {', 'if (m_f26_marks_count.load(std::memory_order_relaxed) == 0) {'),
    (TC, '			F26DropLocked(metadata->first, DiagF5::F26Site::Unmap, metadata->second.clear_mask);', '}'),
    (DS, '	F26ApplyScope(TextureCache& cache, const Image& image)', ': m_cache(cache), m_on(DiagF5::FixF26On()'),
    (DS, '			m_cache.F26Declined(m_address, m_image, m_layers);', '}'),
    (DS, '	F26ApplyScope f26_apply {cache, image};', 'Session 124'),
    (DS, '		(void)DiagF5::F26Tint(address, cache.F26HasMark(address), clear_format, clear);', '}'),
    (DS, '	cache.F26Exec(address, image.info.data.address, DiagF5::F26Site::Mat, mask);', 'Session 124'),
    (VW, '	(void)DiagF5::LogF26TintMode();', ''),
    (TS, '  static void F16kEraseMeta(TextureCache &cache, uint64_t address) {', 'std::lock_guard lock(cache.m_lock);'),
    (TS, '          const char *t1 = "F46a T1 alias: the mark of `pending` removed by another image\'s clear";',
     'const auto n1 = adopt(t1);'),
    (TS, '            const char *t2 = "F46a T2 a new fill, the next clear: the first execution after the event at =0";',
     'const auto lines = F16kCount("DiagF5Ev:");'),
    (TS, '            const char *t3 = "F46a T3 a mark dropped by a new fill (site=fill) and by UnmapMemory (site=unmap)";',
     'dimage.info.metadata = dmeta0;'),
    (TS, '            const char *t4 = "F46a T4 a prepare event: no f26_first_exec on the event itself, one at the next clear";',
     'const auto lines = F16kCount("DiagF5Ev:");'),
    (TS, '            const char *t5 = "F46a T5 prepare kept why=decode: the mark of `dcc`, executed by MaterializeDeferredDccClear";',
     'auto no_register = desc;'),
    (TS, '        constexpr uint64_t tk = 0x571006000ull;', 'const TCase tcases[] = {'),
    (TS, '        Require(name, "Z f26_first_exec lines", firsts == (!id ? 0u : f26 ? 4u : 2u),', 'fmt::format('),
]


def show(commit, path):
    out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
    return out.decode('utf-8').replace('\r\n', '\n').split('\n')


def find():
    rows = []
    bad = 0
    cache = {}
    for path, anchor, nxt in ANCHORS:
        lines = cache.setdefault(path, show(C, path))
        hits = [i for i, l in enumerate(lines) if anchor in l]
        if len(hits) != 1:
            print('ANCHOR %s hits %d: %s' % (path, len(hits), anchor))
            bad += 1
            continue
        i = hits[0]
        if nxt and nxt not in lines[i + 1]:
            print('NEXT %s:%d: %r not in %r' % (path, i + 1, nxt, lines[i + 1]))
            bad += 1
            continue
        rows.append('\t'.join([C, path, str(i + 1), anchor.strip(), nxt.strip()]))  # anchors without edge blanks
    open(TSV, 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('found', len(rows), 'bad', bad)
    print('ALL OK' if bad == 0 else 'FAILED')


def rows():
    out = []
    for l in open(TSV, encoding='utf-8').read().split('\n'):
        if l:
            c, p, n, a, x = l.split('\t')
            out.append((c, p, int(n), a, x))
    return out


def ok(c, p, n, a, x, cache):
    lines = cache.setdefault((c, p), show(c, p))
    return n >= 1 and n < len(lines) and a in lines[n - 1] and (x in lines[n] if x else True)


def check():
    cache = {}
    rs = rows()
    bad = [r for r in rs if not ok(*r, cache)]
    for r in bad:
        print('BAD', r[:3])
    print('links', len(rs), 'bad', len(bad))
    print('ALL OK' if not bad else 'FAILED')


def neg():
    cache = {}
    rs = rows()
    caught = sum(1 for (c, p, n, a, x) in rs if not ok(c, p, n + 1, a, x, cache))
    print('neg shifted +1 caught', caught, 'of', len(rs))
    print('ALL OK' if caught == len(rs) else 'FAILED')


def text(report):
    t = open(report, encoding='utf-8').read()
    have = {(c, p, n) for (c, p, n, a, x) in rows()}
    found = re.findall(r'([0-9a-f]{8}):((?:src|tests)/[\w/.\-]+):(\d+)', t)
    missing = [f for f in found if (f[0], f[1], int(f[2])) not in have]
    for m in missing:
        print('MISSING', ':'.join(m))
    print('text links', len(found), 'missing', len(missing))
    print('ALL OK' if not missing and found else 'FAILED')


if __name__ == '__main__':
    {'find': find, 'check': check, 'neg': neg}.get(sys.argv[1], lambda: text(sys.argv[2]))()
