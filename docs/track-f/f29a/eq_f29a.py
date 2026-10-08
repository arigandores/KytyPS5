"""F29a (HPP-699, ROADMAP s122 item 638(g)(1)): the functions of the BDA stamp path are the same text at the FS10 worktree
commit (dc5d4712, the source of the installed FS10 abfded5e) and at main (the commit given). A function is cut from its
signature line to the matching closing brace; whole files are compared where named. ASCII code.

    python eq_f29a.py <fs10 commit> <main commit> <out.txt>
"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
RC = 'src/graphics/host_gpu/renderer/renderContext.cpp'
MT = 'src/graphics/host_gpu/memoryTracker.cpp'
MTH = 'src/graphics/host_gpu/memoryTracker.h'
RMH = 'src/graphics/host_gpu/regionManager.h'
FUNCS = [
    (RC, 'void RenderContext::PrepareBda() {'),
    (RC, 'void RenderContext::MapMemory(uint64_t vaddr, uint64_t size) {'),
    (RC, 'void RenderContext::UnmapMemory(uint64_t vaddr, uint64_t size) {'),
    (BC, 'void BufferCache::SynchronizeBuffersInRange(uint64_t vaddr, uint64_t size) {'),
    (BC, 'void BufferCache::SynchronizeBuffersByRegion(uint64_t scan_begin, uint64_t scan_end) {'),
    (BC, 'void BufferCache::SynchronizeBuffersOfDirtyRanges() {'),
    (BC, 'void BufferCache::SynchronizeBuffersOfDirtyRangesBatched(PageManager::PassScope& pass) {'),
    (BC, 'void BufferCache::MarkBdaRegions(uint64_t vaddr, uint64_t size) {'),
    (BC, 'bool BufferCache::DirtyRangesTouchBuffers(uint64_t* range_address, uint64_t* range_size, uint64_t* buffer_address,'),
    (BC, 'void BufferCache::ChangeRegister(BufferId id) {'),
    (MT, 'void MemoryTracker::CollectCpuModifiedRanges(uint64_t vaddr, uint64_t size,'),
    (MT, 'MemoryTracker::RegionStamp MemoryTracker::CollectCpuModifiedRangesStamped(uint64_t vaddr, uint64_t size,'),
    (MTH, '[[nodiscard]] RegionStamp RegionWriteStamp(uint64_t index) const noexcept {'),
    (RMH, 'void ChangeState(uint64_t vaddr, uint64_t size) {'),
]
FILES = ['src/graphics/host_gpu/rangeSet.h', 'src/graphics/host_gpu/regionDefinitions.h']


def show(commit, path):
    r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')


def cut(text, sig):
    lines = text.split('\n')
    hits = [i for i, l in enumerate(lines) if l.strip() == sig.strip()]
    if len(hits) != 1:
        return None, len(hits)
    i = hits[0]
    depth = 0
    started = False
    out = []
    for j in range(i, len(lines)):
        out.append(lines[j])
        for ch in lines[j]:
            if ch == '{':
                depth += 1
                started = True
            elif ch == '}':
                depth -= 1
        if started and depth == 0:
            return '\n'.join(out), i + 1
    return None, -1


def main(a, b, out_path):
    out = []
    ok = True
    for path, sig in FUNCS:
        ta, tb = show(a, path), show(b, path)
        fa, la = cut(ta, sig)
        fb, lb = cut(tb, sig)
        if fa is None or fb is None:
            ok = False
            out.append('FAIL %s %s: not cut (%s / %s)' % (path, sig[:60], la, lb))
            continue
        same = fa == fb
        ok &= same
        out.append('%s %s :: %s  %s:%d (%d lines) vs %s:%d' % ('SAME' if same else 'DIFF', path, sig[:70], a, la,
                                                              fa.count('\n') + 1, b, lb))
    for path in FILES:
        same = show(a, path) == show(b, path)
        ok &= same
        out.append('%s %s (whole file)' % ('SAME' if same else 'DIFF', path))
    out.append('FS10 %s = main %s on the BDA stamp path: %s' % (a, b, 'ALL OK' if ok else 'DIFFERS'))
    txt = '\n'.join(out) + '\n'
    open(out_path, 'w', encoding='ascii', newline='\n').write(txt)
    sys.stdout.write(txt)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:4]))
