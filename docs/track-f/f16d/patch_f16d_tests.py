# Track F, F16d (HPP-521): the test site of KYTY_DIAG_F5 / KYTY_DIAG_F6 in tests/ShaderRecompilerComputeTests.cpp
# (mode --diag-f5-only of shader_recompiler_compute_tests). python patch_f16d_tests.py <repo root> [--check]
# Whole-line anchors, each exactly once; LF output (write_bytes).
import os
import sys

ROOT = sys.argv[1]
CHECK = "--check" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
PATH = "tests/ShaderRecompilerComputeTests.cpp"

METHOD = open(os.path.join(HERE, "new", "test_method.inc"), "rb").read().decode("utf-8").replace("\r\n", "\n")
METHOD_LINES = METHOD.rstrip("\n").split("\n") + [""]

EDITS = [
    ("after", ['#include "graphics/host_gpu/renderer/depthRenderTarget.h"'], [
        '#include "graphics/host_gpu/renderer/diagF5.h"',
        '#include "common/envFlag.h"',
    ]),
    ("after", ["  static TileManager &Tiler(TextureCache &cache) { return cache.m_tiler; }"], [
        "",
        "  // Track F, F16d (HPP-521): the private cache sites of KYTY_DIAG_F5, driven under the cache lock as their callers do.",
        "  static void F16dPrepareDccClear(TextureCache &cache, ImageId id, const TextureCache::ImageDesc &desc) {",
        "    auto lock = Lock(cache);",
        "    cache.PrepareDccClear(id, desc);",
        "  }",
        "  static void F16dPrepareCmaskClear(TextureCache &cache, ImageId id, const TextureCache::ImageDesc &desc) {",
        "    auto lock = Lock(cache);",
        "    cache.PrepareCmaskClear(id, desc);",
        "  }",
        "  static Image &F16dImage(TextureCache &cache, ImageId id) { return cache.m_slot_images[id]; }",
        "  static void F16dSetCmaskMeta(TextureCache &cache, uint64_t address, uint32_t fill_value, uint32_t clear_mask,",
        "                               uint64_t fill_size) {",
        "    std::lock_guard lock(cache.m_lock);",
        "    auto &metadata = cache.m_surface_metas[address];",
        "    metadata.type = TextureCache::MetaDataInfo::Type::CMask;",
        "    metadata.fill_value = fill_value;",
        "    metadata.clear_mask = clear_mask;",
        "    metadata.fill_size = fill_size;",
        "  }",
    ]),
    ("after", [
        "  static void MaterializeColorClears(RenderExecutor& executor, CommandBuffer& command) {",
        "    executor.MaterializeBoundTargetDccClears(command);",
        "  }",
    ], [
        "  // Track F, F16d (HPP-521): MaterializeDeferredDccClear and the meta-clear shortcut with the KYTY_DIAG_F5 list.",
        "  static void F16dMaterialize(RenderExecutor &executor, CommandBuffer &command, ImageId id) {",
        "    executor.MaterializeDeferredDccClear(command, id);",
        "  }",
        "  static bool F16dMetaClear(RenderExecutor &executor, const ShaderComputeInputInfo &input,",
        "                            const CommandBuffer &buffer, DiagF5::CsRefusals *refusals) {",
        "    return executor.TryConsumeComputeMetaClear(input, buffer, refusals);",
        "  }",
    ]),
    ("before", ["  void CheckCmaskRegisterClear() {"], METHOD_LINES),
    ("before", ['  if (argc == 2 && std::strcmp(argv[1], "--cmask-clear-only") == 0) {'], [
        '  if (argc == 2 && std::strcmp(argv[1], "--diag-f5-only") == 0) {',
        "    // Track F, F16d (HPP-521): the KYTY_DIAG_F5 / KYTY_DIAG_F6 test site; run with the knobs unset, 0 and 1.",
        "    VulkanHarness vulkan;",
        "    vulkan.CheckDiagF5F6();",
        '    std::printf("DiagF5F6 test site: ALL OK\\n");',
        "    return 0;",
        "  }",
    ]),
]


def find_block(lines, block):
    n = len(block)
    return [i for i in range(len(lines) - n + 1) if lines[i:i + n] == block]


full = os.path.join(ROOT, PATH)
raw = open(full, "rb").read()
crlf = b"\r\n" in raw
lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
ok = True
for kind, anchor, new in EDITS:
    hits = find_block(lines, anchor)
    if len(hits) != 1:
        print("ANCHOR %s x%d: %r" % (kind, len(hits), anchor[0][:90]))
        ok = False
        continue
    i = hits[0]
    if kind == "after":
        lines[i + len(anchor):i + len(anchor)] = new
    else:
        lines[i:i] = new
out = "\n".join(lines)
if crlf:
    out = out.replace("\n", "\r\n")
if ok and not CHECK:
    open(full, "wb").write(out.encode("utf-8"))
print("%s %s (%d edits)" % ("checked" if CHECK else "patched", PATH, len(EDITS)))
print("PATCH OK" if ok else "PATCH FAILED")
sys.exit(0 if ok else 1)
