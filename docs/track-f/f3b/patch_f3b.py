# F3b (HPP-340, ROADMAP p.259(e)(3)): V1 under KYTY_FIX_B1B - BVH descriptor base = 40-bit field << 8.
# Whole-line anchors; CRLF-safe (strip \r before search, restore after); writes bytes.
import os, sys

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
ROOT = "C:/kyty/KytyPS5/"
NL = chr(10)


def patch(rel, edits):
    path = ROOT + rel
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", NL)
    lines = text.split(NL)
    for anchor, new_lines, mode in edits:
        hits = [i for i, l in enumerate(lines) if l == anchor]
        assert len(hits) == 1, (rel, anchor, len(hits))
        i = hits[0]
        if mode == "after":
            lines[i + 1:i + 1] = new_lines
        elif mode == "before":
            lines[i:i] = new_lines
        elif mode == "replace":
            lines[i:i + 1] = new_lines
    out = NL.join(lines)
    if crlf:
        out = out.replace(NL, "\r\n")
    open(path, "wb").write(out.encode("utf-8"))
    print("patched", rel, "crlf" if crlf else "lf", len(edits), "edits")


T = chr(9)

# 1. ShaderDecoder.h - declaration next to FixB26Enabled.
patch("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h", [
    ("Opcode GateFixB26(Opcode opcode);", [
        "// Track F, F3b (HPP-340, ROADMAP p.259(e)(3)): KYTY_FIX_B1B, default ON (unset or empty = on; 0, false,",
        "// off, no = off, as Common::EnvValueOn). On: IMAGE_BVH_INTERSECT_RAY takes the BVH descriptor base as",
        "// the 40-bit field base_address (dword0, dword1[7:0]) in 256-byte units, i.e. field << 8 (PAL",
        "// sq_bvh_rsrc_t; the game builds it with S_BFE_U64 X, 0x00280008). Off: the address is computed",
        "// exactly as before the fix (dword0 | (dword1 & 0xffff) << 32, no shift). Read once per process;",
        "// the translation cache keys the value in its signature and directory (shaderTranslationCache.cpp).",
        "bool   FixB1BEnabled();",
    ], "after"),
])

# 2. ShaderDecoder.cpp - definition after GateFixB26.
patch("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp", [
    ("Opcode GateFixB26(Opcode opcode) {", [], "after"),  # anchor check only
])
src = open(ROOT + "src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp", "rb").read()
crlf = b"\r\n" in src
text = src.decode("utf-8").replace("\r\n", NL)
old = NL.join([
    "Opcode GateFixB26(Opcode opcode) {",
    T + "if ((opcode == Opcode::S_BREV_B64 || opcode == Opcode::V_CMP_LE_U64) && !FixB26Enabled()) {",
    T + T + "return Opcode::UNSUPPORTED;",
    T + "}",
    T + "return opcode;",
    "}",
    "",
])
assert text.count(old) == 1
new = old + NL.join([
    "bool FixB1BEnabled() {",
    T + "static const bool enabled = [] {",
    T + T + "const char* value = std::getenv(\"KYTY_FIX_B1B\");",
    T + T + "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
    T + "}();",
    T + "return enabled;",
    "}",
    "",
    "",
])
text = text.replace(old, new)
if crlf:
    text = text.replace(NL, "\r\n")
open(ROOT + "src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp", "wb").write(text.encode("utf-8"))
print("patched ShaderDecoder.cpp definition")

# 3. Memory.cpp (KYTY_BVH_NATIVE=0 path) - comment and base.
patch("src/graphics/shader/recompiler/frontend/translate/Memory.cpp", [
    (T + "//   dword0        = base_address[31:0]", [
        T + "//   dword0        = base_address[31:0]   (KYTY_FIX_B1B=1: base_address[39:0] is the BVH",
        T + "//   dword1[7:0]   = base_address[39:32]   address >> 8, PAL sq_bvh_rsrc_t, 40 bits)",
    ], "replace"),
    (T + "//   dword1[15:0]  = base_address[47:32]", [
        T + "//   (KYTY_FIX_B1B=0, before the fix: dword0 | dword1[15:0] << 32 as a byte address)",
    ], "replace"),
    (T + T + "const IR::U64 base64 = ir.ConstructU64(desc0, ir.BitwiseAnd(desc1, U32C(0xffffu)));", [
        T + T + "// Track F, F3b: the base is the 40-bit field base_address in 256-byte units (<< 8);",
        T + T + "// KYTY_FIX_B1B=0 keeps the pre-fix byte address.",
        T + T + "const IR::U64 base64 =",
        T + T + "    Decoder::FixB1BEnabled()",
        T + T + "        ? IR::U64(ir.Emit(IR::ValueOpcode::ShiftLeftLogical64,",
        T + T + "                          {ir.ConstructU64(desc0, ir.BitwiseAnd(desc1, U32C(0xffu))), U32C(8u)}))",
        T + T + "        : ir.ConstructU64(desc0, ir.BitwiseAnd(desc1, U32C(0xffffu)));",
    ], "replace"),
])

# 4. spirvEmitterMemory.cpp (default native path) - include and base.
patch("src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", [
    ("#include \"graphics/shader/recompiler/backend/spirv/SpirvEmitter.h\"", [
        "#include \"graphics/shader/recompiler/frontend/decode/ShaderDecoder.h\"",
    ], "after"),
    (T + T + "const auto base = DeviceAddressFromWords(state, desc0, Binary(state, OpBitwiseAnd, u32t, desc1, U(0xffffu)));", [
        T + T + "// Track F, F3b (ROADMAP p.259(e)(3)): base_address is a 40-bit field in 256-byte units",
        T + T + "// (dword0, dword1[7:0]) -> << 8; KYTY_FIX_B1B=0 keeps the pre-fix byte address (same ids).",
        T + T + "uint32_t base = 0;",
        T + T + "if (Decoder::FixB1BEnabled()) {",
        T + T + T + "const auto field = DeviceAddressFromWords(state, desc0, Binary(state, OpBitwiseAnd, u32t, desc1, U(0xffu)));",
        T + T + T + "base             = Binary(state, OpShiftLeftLogical, addrt, field, ConstantDeviceAddress(state, 8));",
        T + T + "} else {",
        T + T + T + "base = DeviceAddressFromWords(state, desc0, Binary(state, OpBitwiseAnd, u32t, desc1, U(0xffffu)));",
        T + T + "}",
    ], "replace"),
])

# 5. shaderTranslationCache.cpp - token in signature and directory.
patch("src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp", [
    (T + "// translations of =1 and =0 never share a signature or a directory.", [
        T + "// translations of =1 and =0 never share a signature or a directory.",
        T + "// Track F, F3b (ROADMAP p.259(e)(3)): KYTY_FIX_B1B=1 (the default) adds \":fixb1b\" the same way;",
        T + "// with KYTY_FIX_B26 the four combinations get four distinct signatures and directories.",
    ], "replace"),
    (T + "                            (ShaderRecompiler::Decoder::FixB26Enabled() ? \":fixb26\" : \"\");", [
        T + "                            (ShaderRecompiler::Decoder::FixB26Enabled() ? \":fixb26\" : \"\") +",
        T + "                            (ShaderRecompiler::Decoder::FixB1BEnabled() ? \":fixb1b\" : \"\");",
    ], "replace"),
])
print("ALL OK")
