# F12d (HPP-477, ROADMAP s122 item 391(v)): KYTY_FIX_F10 (default 0) - IMAGE_BVH_INTERSECT_RAY treats node types 2
# and 3 as triangles, type 2 = (V2, V3, V4), type 3 = (V2, V4, V0), V4 = dwords 12..14 (F12a 08bd2a87 section 6), in the
# native SPIR-V path (spirvEmitterMemory.cpp) and the IR path (Memory.cpp); =0 keeps the pre-fix lines in the else
# branch; variant token :fixf10 last (shaderTranslationCache.cpp). Usage: python patch_f12d_src.py <root>.
# Anchors are whole lines (sequences of whole lines); CR is stripped before the search and restored after.
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
T = "\t"


def patch(rel, edits):
    path = ROOT / rel
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    lines = raw.replace("\r\n", "\n").split("\n")
    for old, new in edits:
        hits = [i for i in range(len(lines) - len(old) + 1) if lines[i:i + len(old)] == old]
        if len(hits) != 1:
            raise SystemExit("ANCHOR %s: %r matches %d times" % (rel, old[0][:90], len(hits)))
        lines[hits[0]:hits[0] + len(old)] = new
    text = "\n".join(lines)
    if crlf:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))
    print("patched", rel, "edits", len(edits))


# --- ShaderDecoder.h: declaration after FixB1BEnabled.
patch("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h", [
    (["bool   FixB1BEnabled();"],
     ["bool   FixB1BEnabled();",
      "// Track F, F12d (HPP-477, ROADMAP p.391(v)): KYTY_FIX_F10, default OFF (unset, empty, 0, false, off, no = off, as",
      "// Common::EnvValueOn). On: IMAGE_BVH_INTERSECT_RAY treats node types 2 and 3 as triangles, as the GPURT software",
      "// path of the instruction does (b89f22aa IsTriangleNode / CalcTriangleVertexOffsets): type 2 = (V2, V3, V4), type",
      "// 3 = (V2, V4, V0), V4 at node dwords 12..14. Off: types 2 and 3 answer 0xffffffff x4 exactly as before the fix.",
      "// Read once per process; the translation cache keys the value in its signature and directory",
      "// (shaderTranslationCache.cpp).",
      "bool   FixF10Enabled();"]),
])

# --- ShaderDecoder.cpp: definition after FixB1BEnabled.
patch("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp", [
    (["bool FixB1BEnabled() {",
      T + "static const bool enabled = [] {",
      T + T + "const char* value = std::getenv(\"KYTY_FIX_B1B\");",
      T + T + "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
      T + "}();",
      T + "return enabled;",
      "}"],
     ["bool FixB1BEnabled() {",
      T + "static const bool enabled = [] {",
      T + T + "const char* value = std::getenv(\"KYTY_FIX_B1B\");",
      T + T + "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
      T + "}();",
      T + "return enabled;",
      "}",
      "",
      "bool FixF10Enabled() {",
      T + "static const bool enabled = Common::EnvValueOn(std::getenv(\"KYTY_FIX_F10\"));",
      T + "return enabled;",
      "}"]),
])

# --- shaderTranslationCache.cpp: token :fixf10 last.
patch("src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp", [
    ([T + "// with KYTY_FIX_B26 the four combinations get four distinct signatures and directories.",
      T + "const std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +",
      T + "                            (ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? \":bdalean\" : \"\") +",
      T + "                            (ShaderRecompiler::Decoder::FixB26Enabled() ? \":fixb26\" : \"\") +",
      T + "                            (ShaderRecompiler::Decoder::FixB1BEnabled() ? \":fixb1b\" : \"\");"],
     [T + "// with KYTY_FIX_B26 the four combinations get four distinct signatures and directories.",
      T + "// Track F, F12d (ROADMAP p.391(v)): KYTY_FIX_F10=1 (default 0) adds \":fixf10\" last, so =0 and =1 never",
      T + "// share a signature or a directory.",
      T + "const std::string variant = ShaderRecompiler::Spirv::Emitter::BvhLoopCapSignatureToken() +",
      T + "                            (ShaderRecompiler::Spirv::Emitter::BdaLeanEnabled() ? \":bdalean\" : \"\") +",
      T + "                            (ShaderRecompiler::Decoder::FixB26Enabled() ? \":fixb26\" : \"\") +",
      T + "                            (ShaderRecompiler::Decoder::FixB1BEnabled() ? \":fixb1b\" : \"\") +",
      T + "                            (ShaderRecompiler::Decoder::FixF10Enabled() ? \":fixf10\" : \"\");"]),
])

# --- spirvEmitterMemory.cpp (native path, the default KYTY_BVH_NATIVE).
patch("src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", [
    ([T + "const auto is_box16 = ieq(node_type, U(4u));",
      T + "const auto is_box32 = ieq(node_type, U(5u));",
      T + "const auto is_tri   = Binary(state, OpULessThan, boolt, node_type, U(2u));",
      T + "const auto is_tri1  = ieq(node_type, U(1u));"],
     [T + "const auto is_box16 = ieq(node_type, U(4u));",
      T + "const auto is_box32 = ieq(node_type, U(5u));",
      T + "// Track F, F12d (ROADMAP p.391(v)): KYTY_FIX_F10=1 - node types 2 and 3 are triangles too (GPURT b89f22aa",
      T + "// IsTriangleNode, F12a section 1.2); =0 keeps the pre-fix lines (same calls, same ids).",
      T + "const bool fix_f10  = Decoder::FixF10Enabled();",
      T + "uint32_t   is_tri   = 0;",
      T + "if (fix_f10) {",
      T + T + "is_tri = Binary(state, OpULessThan, boolt, node_type, U(4u));",
      T + "} else {",
      T + T + "is_tri = Binary(state, OpULessThan, boolt, node_type, U(2u));",
      T + "}",
      T + "const auto is_tri1  = ieq(node_type, U(1u));"]),
    ([T + T + "const Vec3 v3    = vertex(3);",
      T + T + "const Vec3 tri_a = vsel(is_tri1, v1, v0);",
      T + T + "const Vec3 tri_b = vsel(is_tri1, v3, v1);",
      T + T + "const Vec3 tri_c = v2;",
      T + T + "const Vec3 e1    = vsub(tri_b, tri_a);"],
     [T + T + "const Vec3 v3    = vertex(3);",
      T + T + "Vec3       tri_a {};",
      T + T + "Vec3       tri_b {};",
      T + T + "Vec3       tri_c {};",
      T + T + "if (fix_f10) {",
      T + T + T + "// Type 0 = (V0, V1, V2), 1 = (V1, V3, V2), 2 = (V2, V3, V4), 3 = (V2, V4, V0) (GPURT b89f22aa",
      T + T + T + "// CalcTriangleVertexOffsets; F12a section 1.2); V4 is dwords 12..14 of the 16 loaded above.",
      T + T + T + "const auto is_tri2  = ieq(node_type, U(2u));",
      T + T + T + "const auto is_tri3  = ieq(node_type, U(3u));",
      T + T + T + "const auto is_tri23 = lor(is_tri2, is_tri3);",
      T + T + T + "const auto is_tri12 = lor(is_tri1, is_tri2);",
      T + T + T + "const Vec3 v4       = vertex(4);",
      T + T + T + "const Vec3 a01      = vsel(is_tri1, v1, v0);",
      T + T + T + "tri_a               = vsel(is_tri23, v2, a01);",
      T + T + T + "const Vec3 b012     = vsel(is_tri12, v3, v1);",
      T + T + T + "tri_b               = vsel(is_tri3, v4, b012);",
      T + T + T + "const Vec3 c013     = vsel(is_tri3, v0, v2);",
      T + T + T + "tri_c               = vsel(is_tri2, v4, c013);",
      T + T + "} else {",
      T + T + T + "tri_a = vsel(is_tri1, v1, v0);",
      T + T + T + "tri_b = vsel(is_tri1, v3, v1);",
      T + T + T + "tri_c = v2;",
      T + T + "}",
      T + T + "const Vec3 e1    = vsub(tri_b, tri_a);"]),
])

# --- Memory.cpp (IR path, KYTY_BVH_NATIVE=0).
patch("src/graphics/shader/recompiler/frontend/translate/Memory.cpp", [
    (["//   triangle node (types 0 and 1): {t_num, t_denom, i_num, j_num} as raw floats, a miss is",
      "//     encoded as {+inf, 1.0, ...};"],
     ["//   triangle node (types 0 and 1; KYTY_FIX_F10=1: types 0..3): {t_num, t_denom, i_num, j_num} as",
      "//     raw floats, a miss is encoded as {+inf, 1.0, ...};"]),
    ([T + "const IR::U1 is_box16 = ir.IEqual(node_type, U32C(4u));",
      T + "const IR::U1 is_box32 = ir.IEqual(node_type, U32C(5u));",
      T + "const IR::U1 is_tri   = ir.ULessThan(node_type, U32C(2u));"],
     [T + "const IR::U1 is_box16 = ir.IEqual(node_type, U32C(4u));",
      T + "const IR::U1 is_box32 = ir.IEqual(node_type, U32C(5u));",
      T + "// Track F, F12d (ROADMAP p.391(v)): KYTY_FIX_F10=1 - node types 2 and 3 are triangles too (GPURT b89f22aa",
      T + "// IsTriangleNode, F12a section 1.2); =0 keeps the pre-fix lines.",
      T + "const bool   fix_f10 = Decoder::FixF10Enabled();",
      T + "IR::U1       is_tri;",
      T + "if (fix_f10) {",
      T + T + "is_tri = ir.ULessThan(node_type, U32C(4u));",
      T + "} else {",
      T + T + "is_tri = ir.ULessThan(node_type, U32C(2u));",
      T + "}"]),
    ([T + "const Vec3 v3    = vertex(3);",
      T + "const Vec3 tri_a = vsel(is_tri1, v1, v0);",
      T + "const Vec3 tri_b = vsel(is_tri1, v3, v1);",
      T + "const Vec3 tri_c = v2;"],
     [T + "const Vec3 v3    = vertex(3);",
      T + "Vec3       tri_a {};",
      T + "Vec3       tri_b {};",
      T + "Vec3       tri_c {};",
      T + "if (fix_f10) {",
      T + T + "// Type 2 = (v2, v3, v4), type 3 = (v2, v4, v0), v4 = dwords 12..14 (GPURT b89f22aa",
      T + T + "// CalcTriangleVertexOffsets; F12a section 1.2).",
      T + T + "const IR::U1 is_tri2  = ir.IEqual(node_type, U32C(2u));",
      T + T + "const IR::U1 is_tri3  = ir.IEqual(node_type, U32C(3u));",
      T + T + "const IR::U1 is_tri23 = ir.LogicalOr(is_tri2, is_tri3);",
      T + T + "const IR::U1 is_tri12 = ir.LogicalOr(is_tri1, is_tri2);",
      T + T + "const Vec3   v4       = vertex(4);",
      T + T + "const Vec3   a01      = vsel(is_tri1, v1, v0);",
      T + T + "tri_a                 = vsel(is_tri23, v2, a01);",
      T + T + "const Vec3   b012     = vsel(is_tri12, v3, v1);",
      T + T + "tri_b                 = vsel(is_tri3, v4, b012);",
      T + T + "const Vec3   c013     = vsel(is_tri3, v0, v2);",
      T + T + "tri_c                 = vsel(is_tri2, v4, c013);",
      T + "} else {",
      T + T + "tri_a = vsel(is_tri1, v1, v0);",
      T + T + "tri_b = vsel(is_tri1, v3, v1);",
      T + T + "tri_c = v2;",
      T + "}"]),
])
print("ALL OK")
