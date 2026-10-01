# F4a (HPP-335, Emu Engineer): row B35, ROADMAP s122 p.254(zh)(1) - KYTY_FIX_DUALSRC enables dualSrcBlend at device
# creation when the physical device supports it; default 0. Whole-line anchors; CR stripped on read, LF written.
import sys

sys.path.insert(0, 'C:/kyty/f287/f2a')
from patchlib import apply  # noqa: E402

SRC = 'C:/kyty/KytyPS5/src/graphics/presentation/window/vulkanWindow.cpp'

anchor = [
    '\tgraphics.sample_rate_shading_enabled                 = true;',
    '\tdevice_features.shaderInt64 = VK_TRUE;',
]
new = [
    '\t// Track F, F4 (HPP-335, ROADMAP s122 p.254(zh)(1), row B35): pipelines with SRC1 blend factors',
    '\t// (recipe 1592: SRC1_ALPHA / ONE_MINUS_SRC1_ALPHA) are created without dualSrcBlend. KYTY_FIX_DUALSRC',
    '\t// (Common::EnvFlagOn: unset, "", 0/false/off/no = OFF; default OFF) enables it when supported; OFF leaves',
    '\t// device_features as before. Outside the translation cache signature (not under src/graphics/shader).',
    '\t{',
    '\t\tconst bool dual_src_supported = supported_features2.features.dualSrcBlend == VK_TRUE;',
    '\t\tconst bool dual_src_enabled   = dual_src_supported && Common::EnvFlagOn("KYTY_FIX_DUALSRC");',
    '\t\tif (dual_src_enabled) {',
    '\t\t\tdevice_features.dualSrcBlend = VK_TRUE;',
    '\t\t}',
    '\t\tLOGF("DualSrcBlend: supported=%d enabled=%d' + chr(92) + 'n", dual_src_supported ? 1 : 0,',
    '\t\t     dual_src_enabled ? 1 : 0);',
    '\t}',
]
apply(SRC, [(anchor, new, 'after')])
