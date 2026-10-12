"""patch_f47g2.py - track F, F47g2 (HPP-828, ROADMAP s122 item 742(v)): the hooks of RC1-RC3 of the review F47h in the
emulator sources outside diagF47Dt.{h,cpp} (those two and the stand are copied whole).

    python patch_f47g2.py <worktree root>

Anchors are WHOLE lines (CR stripped before the search, the original line ending restored); every anchor must occur
exactly the expected number of times, else nothing is written and the script exits 1. Writes LF / CRLF as found."""
import sys

ROOT = sys.argv[1].rstrip('/\\')

F_RUN = 'src/graphics/guest_gpu/graphicsRun.cpp'
F_VO = 'src/graphics/presentation/videoOut.cpp'
F_DS = 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
F_TC = 'src/graphics/host_gpu/renderer/cache/textureCache.cpp'
F_TH = 'src/graphics/host_gpu/renderer/cache/textureCache.h'


def flip_hook(path, var):
    return [
        '\t// Track F, F47g2 (HPP-828, RC1 of F47h): KYTY_DIAG_F47DT - the draws parsed so far land in the show of this flip',
        '\t// (measurement only: a counter and a line).',
        '\tif (DiagF47Dt::On()) {',
        '\t\tDiagF47Dt::NoteFlip(%d, %s);' % (path, var),
        '\t}',
    ]


# (file, kind, anchor lines, expected count, new lines, occurrence-specific variants)
# kind 'after': insert new lines after the anchor block; 'replace': replace the anchor block.
EDITS = [
    (F_RUN, 'after_each', ['\t                                         m_flip.flip_arg);'], 3,
     [flip_hook(0, 'request'), flip_hook(1, 'request'), flip_hook(2, 'request')]),
    (F_RUN, 'after', ['\tm_renderer.GetVideoOut().PrepareFlip(request_id, CurrentBuffer());'], 1,
     flip_hook(3, 'request_id')),
    (F_VO, 'after', ['#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"'], 1,
     ['#include "graphics/host_gpu/renderer/diagF47Dt.h" // Track F, F47g2 (KYTY_DIAG_F47DT)']),
    (F_VO, 'after', ['\tGraphics::GpuTimeProfiler::SetFrame(static_cast<uint32_t>(r.cfg->flip_status.count));'], 1,
     ['\t// Track F, F47g2 (HPP-828, RC1 of F47h): KYTY_DIAG_F47DT - the n of this request (measurement only: a line).',
      '\tif (Graphics::DiagF47Dt::On()) {',
      '\t\tGraphics::DiagF47Dt::NoteShown(r.cfg->flip_status.count, r.id);',
      '\t}']),
    (F_DS, 'after', ['#include "graphics/host_gpu/renderer/debug.h"'], 1,
     ['#include "graphics/host_gpu/renderer/diagF47Dt.h" // Track F, F47g2 (KYTY_DIAG_F47DT)']),
    (F_DS, 'after', ['\t\t\t\tstream.CopyFrom(command, *buffer, offset, stream_offset, size,',
                     '\t\t\t\t                vk::AccessFlagBits::eShaderWrite | vk::AccessFlagBits::eTransferWrite,',
                     '\t\t\t\t                vk::AccessFlagBits::eHostWrite, vk::AccessFlagBits::eShaderRead,',
                     '\t\t\t\t                vk::AccessFlagBits::eUniformRead | vk::AccessFlagBits::eShaderRead);'], 1,
     ['\t\t\t\t// Track F, F47g2 (HPP-828, RC3 of F47h): KYTY_DIAG_F47DT - the GPU writes this ring range after the submit',
      '\t\t\t\t// (measurement only: a note).',
      '\t\t\t\tif (DiagF47Dt::On()) {',
      '\t\t\t\t\tDiagF47Dt::NoteRingGpuCopy(&stream, stream_offset, size, stream.Generation());',
      '\t\t\t\t}']),
    (F_TC, 'replace', ['\t\tDiagF47Dt::NoteImageUpload(UINT32_MAX, image.SourceRange().address, image.SourceRange().size,',
                       '\t\t                           image.source_first_level, levels - image.source_first_level, 0, true);'], 1,
     ['\t\t// F47g2 (HPP-828, RC2 of F47h): the id of this image (the record of value (ii) is per image).',
      '\t\tconst auto f47dt_id = IdOfImageForDiag(image);',
      '\t\tDiagF47Dt::NoteImageUpload(f47dt_id.index, f47dt_id.generation, image.SourceRange().address,',
      '\t\t                           image.SourceRange().size, image.source_first_level,',
      '\t\t                           levels - image.source_first_level, 0, true);']),
    (F_TC, 'replace', ['\t\t\tDiagF47Dt::NoteImageUpload(id.index, image.SourceRange().address, image.SourceRange().size, first_level,',
                       '\t\t\t                           image.info.resources.levels - first_level, image.pending_levels, false);'], 1,
     ['\t\t\tDiagF47Dt::NoteImageUpload(id.index, id.generation, image.SourceRange().address, image.SourceRange().size,',
      '\t\t\t                           first_level, image.info.resources.levels - first_level, image.pending_levels,',
      '\t\t\t                           false); // F47g2 (HPP-828, RC2 of F47h): the slot generation of the id']),
    (F_TH, 'after', ['\t[[nodiscard]] const Image& PeekImage(ImageId id) const { return m_slot_images[id]; }'], 1,
     ['\t// Track F, F47g2 (HPP-828, RC2 of F47h): the id of an image by its address (KYTY_DIAG_F47DT reads only; one pass',
      '\t// over the slots, no touch).',
      '\t[[nodiscard]] ImageId IdOfImageForDiag(const Image& image) const {',
      '\t\tImageId found {};',
      '\t\tm_slot_images.ForEach([&](ImageId id, const Image& candidate) {',
      '\t\t\tif (&candidate == &image) {',
      '\t\t\t\tfound = id;',
      '\t\t\t}',
      '\t\t});',
      '\t\treturn found;',
      '\t}']),
]


def load(rel):
    raw = open(ROOT + '/' + rel, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    return text.split('\n'), crlf


def find_all(lines, block):
    n = len(block)
    return [i for i in range(len(lines) - n + 1) if lines[i:i + n] == block]


def main():
    files = {}
    ok = True
    for rel, kind, anchor, count, new in EDITS:
        if rel not in files:
            files[rel] = load(rel)
        lines, _ = files[rel]
        hits = find_all(lines, anchor)
        if len(hits) != count:
            print('ANCHOR %s: %d hits, expected %d: %s' % (rel, len(hits), count, anchor[0].strip()[:90]))
            ok = False
            continue
        for k, i in reversed(list(enumerate(hits))):
            add = new[k] if kind == 'after_each' else new
            if kind == 'replace':
                lines[i:i + len(anchor)] = add
            else:
                lines[i + len(anchor):i + len(anchor)] = add
        print('OK %s %s x%d' % (rel, kind, count))
    if not ok:
        print('FAILED - nothing written')
        return 1
    for rel, (lines, crlf) in files.items():
        data = '\n'.join(lines)
        if crlf:
            data = data.replace('\n', '\r\n')
        open(ROOT + '/' + rel, 'wb').write(data.encode('utf-8'))
        print('written %s (%s)' % (rel, 'CRLF' if crlf else 'LF'))
    print('ALL OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
