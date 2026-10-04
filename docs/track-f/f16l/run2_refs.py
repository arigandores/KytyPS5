# F16l (HPP-584): every <commit>:<path>:<line> of docs/track-f/f16l-review.md - the line holds the anchor; prints the
# line and +1. Exit 0 and "ALL OK" only when all anchors hold.
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
R = 'src/graphics/host_gpu/renderer/'
REFS = [
    ('c0789a34', 'docs/ROADMAP.md', 22766, '(з) **Критерий кода F16k (до кода):**'),
    ('b6858d6d', 'docs/ROADMAP.md', 22788, '(б) **Поправки буквы п. 492, принятые как решение лида'),
    ('b6858d6d', 'docs/ROADMAP.md', 22789, '(в) **Правило чтения к поправкам'),
    ('859d2ed8', 'docs/track-f/f16i-review.md', 55, '**RC3. Счётчик исполнения правки'),
    ('810909e3', R + 'pipeline/descriptors.cpp', 3922,
     'if (color.image_id && color.desc.info.metadata.kind == ImageMetadataKind::Cmask) {'),
    ('810909e3', R + 'pipeline/descriptors.cpp', 3938, 'DiagF5::On() ? &f5_cmu : nullptr);'),
    ('810909e3', R + 'pipeline/descriptors.cpp', 3955, 'if (DiagF5::On() && b42.kind == FixB42Kind::Hit) [[unlikely]] {'),
    ('810909e3', R + 'pipeline/descriptors.cpp', 3973,
     ': f5_info.metadata.kind != ImageMetadataKind::None ? DiagF5::Counter::CmaskFceMeta'),
    ('810909e3', R + 'pipeline/descriptors.cpp', 3883,
     'const auto since = std::max(before.fill_seq, DiagF5Id::FillSeq(e.dcc));'),
    ('810909e3', R + 'pipeline/descriptors.cpp', 6706,
     'DiagF5Id::NoteBind(image.info.data.address, DiagF5Id::BindKind::Texture'),
    ('810909e3', R + 'cache/textureCache.cpp', 1889, 'm_decide(fce && DiagF5::FixCmuOn())'),
    ('810909e3', R + 'cache/textureCache.cpp', 1898, 'if (m_decide && DiagF5::On()) [[unlikely]] {'),
    ('810909e3', R + 'cache/textureCache.cpp', 3511,
     'if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {'),
    ('810909e3', R + 'cache/bufferCache.cpp', 2866, 'if (DiagF5::ExactRingOn()) [[unlikely]] {'),
    ('810909e3', R + 'cache/bufferCache.cpp', 2899, 'if (ring->second.count > ExactRing::K && oldest > since) {'),
    ('810909e3', R + 'diagF5.cpp', 586, 'static const bool on = FixCmuOn() || DiagF5Id::On();'),
    ('810909e3', R + 'diagF5.cpp', 637, 'DiagF5Ev: cmask_fce n={} present={} gpu={}'),
    ('810909e3', R + 'diagF5.cpp', 865, 'const bool known = before.type == MetaType::PendingDcc'),
    ('810909e3', R + 'diagF5.cpp', 972, 'IdClose(s, i, "exit", frame);'),
    ('810909e3', R + 'diagF5.cpp', 998, 'const bool id_cs  = cnt[kImgClear] + cnt[kMetaClear]'),
    ('810909e3', R + 'diagF5.h', 26, '#include "graphics/host_gpu/renderer/image/imageInfo.h"'),
    ('810909e3', 'CMakeLists.txt', 156, 'graphics/host_gpu/renderer/image/imageInfo.h'),
    ('a6114045', 'docs/track-f/f16f/runs/f5_ef/read.json', 106, '"cmask_fce_meta": 20163'),
    ('a6114045', 'docs/track-f/f16f/f16f_read.py', 101, "return re.compile(tag + rb': frame=(\\d+)'"),
]

ok = True
for commit, path, line, anchor in REFS:
    text = subprocess.run([GIT, '-C', REPO, 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout
    lines = text.decode('utf-8').split('\n')
    cur = lines[line - 1] if line - 1 < len(lines) else ''
    nxt = lines[line] if line < len(lines) else ''
    hit = anchor in cur
    ok &= hit
    print(f"{'OK ' if hit else 'BAD'} {commit}:{path}:{line}")
    print(f"    {cur.strip()[:150]}")
    print(f"    +1 {nxt.strip()[:150]}")
print(f'{len(REFS)} refs')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
