# F9e2c (HPP-436, ROADMAP s122 item 357(g)(1)-(4)): KYTY_FIX_B42 M2c - a CMask entry is armed only by the clear-mask bits
# of the view layers [base_layer, base_layer + layer_count) of color.desc.view_info (what PrepareCmaskClear can consume,
# textureCache.cpp:2008-2010 of 2da00d80), not by the whole mask (RC1 of F9f2, 4256e8cf:docs/track-f/f9f2-review.md).
# Only descriptors.cpp. Anchors are whole lines / blocks, each must occur exactly once; all checked before writing; LF out.
# Usage: python patch_f9e2c.py <repo root>
import sys

root = sys.argv[1]
path = root + '/src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')

NL = chr(10)
TAB = chr(9)

edits = []

# 1. Header comment: the CMask arming member.
old1 = NL.join([
    '// PendingDcc fill or (F9e2b, RC2: a re-fill of a live target after its first clear) as a CMask entry with clear-mask',
    '// bits set (`rearm`), and the target was not acquired as a draw-path colour target after that fill (F9e2b, RC1: the',
])
new1 = NL.join([
    '// PendingDcc fill or (F9e2b, RC2: a re-fill of a live target after its first clear) as a CMask entry with clear-mask',
    '// bits set (`rearm`; F9e2c, RC1 of F9f2: only the bits of the view layers count - the ones PrepareCmaskClear can',
    '// consume; a fill of 0 sets the whole mask and a clear drops only the view layers), and the target was not acquired',
    '// as a draw-path colour target after that fill (F9e2b, RC1: the',
])
edits.append((old1, new1))

# 2. The arming member in FixB42Probe.
old2 = NL.join([
    TAB + 'const auto fill  = cache.QueryMetaFill(rt.cmask.addr, color.image_id);',
    TAB + 'const bool armed = fill.pending || (fill.cmask && fill.clear_mask != 0);',
])
new2 = NL.join([
    TAB + 'const auto fill  = cache.QueryMetaFill(rt.cmask.addr, color.image_id);',
    TAB + '// F9e2c: the layer bits of the view FindRenderTarget gets below - as PrepareCmaskClear reads them (no bits where',
    TAB + '// it returns without a clear).',
    TAB + 'const auto& view       = color.desc.view_info;',
    TAB + 'const bool  view_ok    = view.base_level == 0 && view.base_layer < 32 && view.layer_count <= 32 - view.base_layer;',
    TAB + 'const auto  layer_bits = !view_ok ? 0u',
    TAB + '                                  : (view.layer_count >= 32 ? UINT32_MAX : (1u << view.layer_count) - 1u)',
    TAB + '                                        << view.base_layer;',
    TAB + 'const bool armed = fill.pending || (fill.cmask && (fill.clear_mask & layer_bits) != 0);',
])
edits.append((old2, new2))

for old, new in edits:
    n = text.count(old)
    assert n == 1, ('anchor count', n, old[:80])

for old, new in edits:
    text = text.replace(old, new, 1)

if crlf:
    text = text.replace('\n', '\r\n')
open(path, 'wb').write(text.encode('utf-8'))
print('PATCH OK', path, 'crlf' if crlf else 'lf')
