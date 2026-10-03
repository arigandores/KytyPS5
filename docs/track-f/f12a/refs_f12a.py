# F12a (HPP-474): every reference of docs/track-f/f12a.md checked by anchor and +1 (general rule 24(1)).
# Repository refs: `git show <commit>:<path>`; external first sources: local copies under
# C:/kyty/f287/f12a/src_ext (sha256 in sha_src_ext_f12a.txt). A line matches when its text with leading
# blanks removed starts with the anchor. Prints ALL OK only if every anchor and every +1 match.
import subprocess
import sys
import zipfile

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
EXT = 'C:/kyty/f287/f12a/src_ext/'
SPV = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp'
MEM = 'src/graphics/shader/recompiler/frontend/translate/Memory.cpp'

REFS = [
    # (source, path, line, anchor, anchor of line + 1)
    ('9b6cbf7a', 'docs/ROADMAP.md', 20924, '389. **Звено F11g трека F (`HPP-469`, лид): F11f (`HPP-468`) ПРИНЯТ',
     'достижим» по типам 2–3 на всех трёх сценах множества'),
    ('e442ec59', 'docs/track-f/f11f.md', 178, '| `d11_sg` | 140 956 303 | 5 075 932 | 3 806 949 | 2 537 966 | 3 806 949 |',
     '| `d11_ef` | — (строки нет; есть только `DiagBvhNodes: mode=1 words=64 tail_bytes=320`)'),
    ('e442ec59', 'docs/track-f/f11f.md', 180, '| `d11_vw` | 45 732 598 | 938 464 | 703 848 | 469 232 | 703 848 |',
     '| `d11_bh` | 19 235 385 | 109 048 | 81 786 | 54 524 | 81 786 |'),
    ('cdf8bf9c', 'docs/track-f/f11a.md', 106, '- Лист нижнего уровня — список пар `(s26, s27)` в памяти BLAS',
     'треугольного узла, он идёт в `IMAGE_BVH_INTERSECT_RAY` (pc `0x474`)'),
    ('cdf8bf9c', SPV, 2210, 'const auto node_type = Binary(state, OpBitwiseAnd, u32t, node_lo, U(7u));',
     'const auto node_off  = Binary(state, OpBitwiseAnd, u32t, node_lo, U(~7u));'),
    ('cdf8bf9c', SPV, 2230, 'const auto is_box16 = ieq(node_type, U(4u));', 'const auto is_box32 = ieq(node_type, U(5u));'),
    ('cdf8bf9c', SPV, 2232, 'const auto is_tri   = Binary(state, OpULessThan, boolt, node_type, U(2u));',
     'const auto is_tri1  = ieq(node_type, U(1u));'),
    ('cdf8bf9c', SPV, 2381, 'const Vec3 tri_a = vsel(is_tri1, v1, v0);', 'const Vec3 tri_b = vsel(is_tri1, v3, v1);'),
    ('cdf8bf9c', SPV, 2404, 'const auto id_shift    = Binary(state, OpShiftLeftLogical, u32t, node_type, U(3u));',
     'const auto bary0       = fsub(fsub(tri_y, rz), rw);'),
    ('cdf8bf9c', SPV, 2417, 'const auto invalid_node = [&]() -> Result {',
     'return Result {U(InvalidNode), U(InvalidNode), U(InvalidNode), U(InvalidNode)};'),
    ('cdf8bf9c', SPV, 2423, 'return branch(is_box32, box32_node, [&]() -> Result {',
     'return branch(is_tri, triangle_node, invalid_node);'),
    ('cdf8bf9c', MEM, 715, 'if (stub) {', 'const IR::Value miss(0xffffffffu);'),
    ('cdf8bf9c', MEM, 888, 'const IR::U1 is_box32 = ir.IEqual(node_type, U32C(5u));',
     'const IR::U1 is_tri   = ir.ULessThan(node_type, U32C(2u));'),
    ('cdf8bf9c', MEM, 1014, 'const Vec3 tri_a = vsel(is_tri1, v1, v0);', 'const Vec3 tri_b = vsel(is_tri1, v3, v1);'),
    ('cdf8bf9c', MEM, 1057, 'ir.Select(is_box16, box16_result[index],',
     'ir.Select(is_tri, tri_result[index], U32C(InvalidNode))));'),
    ('cdf8bf9c', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 580,
     '(ShaderRecompiler::Decoder::FixB26Enabled() ? ":fixb26" : "") +',
     '(ShaderRecompiler::Decoder::FixB1BEnabled() ? ":fixb1b" : "");'),
    ('cdf8bf9c', 'src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp', 344, 'bool FixB1BEnabled() {',
     'static const bool enabled = [] {'),
    ('cdf8bf9c', 'src/generate_version.cmake', 44, 'if(SHADER_SOURCE_DIR)',
     'file(GLOB_RECURSE SHADER_SOURCES LIST_DIRECTORIES false'),
    ('cdf8bf9c', 'CMakeLists.txt', 155, '-D SHADER_SOURCE_DIR=${KYTY_SOURCE_DIR}/graphics/shader',
     '-D SHADER_CACHE_EXTRA_FILES=${KYTY_SOURCE_DIR}/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp'),
    ('cdf8bf9c', 'tests/ShaderRecompilerComputeTests.cpp', 21050,
     'AppendSMovLiteral(&code, 19, 0x81000000u); // type 8, triangle_return_mode 1 (as the game)', 'u32 vgpr = 4;'),
    ('cdf8bf9c', 'tests/ShaderRecompilerComputeTests.cpp', 21099, 'void RunB1bCases(VulkanHarness *vulkan, bool fix_on) {',
     'RunCase(vulkan, B1bBvhCase("B1bBvhNodeAddress", false, B1bWord1High,'),
    ('cdf8bf9c', MEM, 705, '// The node layouts and the intersection math follow the software fallback in the AMD GPURT',
     '// library (IntersectCommon.hlsl), which is what the closed hardware implements.'),
    ('cdf8bf9c', MEM, 909, 'for (uint32_t index = 0; index < d.size(); index++) {',
     'd[index] = load_dword(index, index < 16u ? exec : active32);'),
    ('cdf8bf9c', MEM, 1039, 'const IR::U32 id_shift    = ir.ShiftLeftLogical(node_type, U32C(3u));',
     'const IR::F32 bary0       = fsub(fsub(tri_y, rz), rw);'),
    ('cdf8bf9c', SPV, 2141, 'const auto desc0  = arg(12);', 'const auto desc1  = arg(13);'),
    ('cdf8bf9c', SPV, 2370, 'load_half(node_addr, 16u, d);', 'const auto vertex = [&](uint32_t index) {'),
    ('cdf8bf9c', 'src/common/envFlag.h', 14, '[[nodiscard]] inline bool EnvValueOn(const char* value) noexcept {',
     'if (value == nullptr || value[0] =='),
    ('3adc4573', 'docs/track-f/f3a-b1b.md', 52, '«`cs=0x380bb9d636390bae args=1,2048,1`»); волна 64',
     'В `c142_09` срабатывает каждый вызов каждого из шести диспатчей'),
    # GPURT b89f22aa (2022-09-28)
    ('file', EXT + 'IntersectCommon_b89f22a.hlsl', 690, '#if USE_HW_INTRINSIC',
     'uint2 address = CalculateRawBvh64NodePointer(bvhAddress, nodePointer);'),
    ('file', EXT + 'gpurtCpuUtils_b89f22a.h', 233, '// Triangle ID contains 4 1-byte fields, 1 per triangle:',
     '// Triangle 0 [ 7: 0]'),
    ('file', EXT + 'IntersectCommon_b89f22a.hlsl', 725, 'else if (IsTriangleNode(nodePointer))', '{'),
    ('file', EXT + 'IntersectCommon_b89f22a.hlsl', 748, '// User defined instance node or procedural node. HW returns -1',
     'return uint4(-1, -1, -1, -1);'),
    ('file', EXT + 'IntersectCommon_b89f22a.hlsl', 624, 'result.x = triangle_missed ? inf  : result.x;',
     'result.y = triangle_missed ? 1.0f : result.y;'),
    ('file', EXT + 'IntersectCommon_b89f22a.hlsl', 650,
     'result.z = asuint(baryc[(triangleId >> (triangleShift + TRIANGLE_ID_I_SRC_SHIFT)) % 4]);',
     'result.w = asuint(baryc[(triangleId >> (triangleShift + TRIANGLE_ID_J_SRC_SHIFT)) % 4]);'),
    ('file', EXT + 'Common_b89f22a.hlsl', 597, 'return (GetNodeType(pointer) <= NODE_TYPE_TRIANGLE_3);', '}'),
    ('file', EXT + 'Common_b89f22a.hlsl', 339, 'case NODE_TYPE_TRIANGLE_2:', 'offsets.x = TRIANGLE_NODE_V2_OFFSET;'),
    ('file', EXT + 'Common_b89f22a.hlsl', 344, 'case NODE_TYPE_TRIANGLE_3:', 'offsets.x = TRIANGLE_NODE_V2_OFFSET;'),
    ('file', EXT + 'gpurtCpuUtils_b89f22a.h', 228, '#define TRIANGLE_NODE_V4_OFFSET 48', '#define TRIANGLE_NODE_ID_OFFSET 60'),
    # GPURT dev 7b226d48 (2025-04-29)
    ('file', EXT + 'gpurt/src/shadersClean/common/Common.hlsl', 578, '// node type 2 -> V2, V3, V4',
     '// node type 3 -> V2, V4, V0'),
    ('file', EXT + 'gpurt/src/shadersClean/common/Common.hlsl', 400,
     'return (GetNodeType(nodePtr) <= NODE_TYPE_TRIANGLE_1);', '}'),
    ('file', EXT + 'gpurt/src/shadersClean/common/gfx10/TriangleNode1_0.hlsli', 32,
     '// Note: GPURT limits triangle compression to 2 triangles per node.',
     '// are used for sideband data.'),
    ('file', EXT + 'gpurt/src/shaders/IntersectCommon.hlsl', 867, '// User defined node. HW returns -1',
     'return uint4(-1, -1, -1, -1);'),
    # RRA 28d0a0e5
    ('file', EXT + 'rra/source/backend/bvh/node_types/triangle_node.cpp', 91,
     'case dxr::amd::NodeType::kAmdNodeTriangle2:', 'return {GetVertex(2), GetVertex(3), GetVertex(4)};'),
    ('file', EXT + 'rra/source/backend/bvh/node_types/triangle_node.cpp', 93,
     'case dxr::amd::NodeType::kAmdNodeTriangle3:', 'return {GetVertex(2), GetVertex(4), GetVertex(0)};'),
    ('file', EXT + 'rra/source/backend/bvh/node_types/triangle_node.cpp', 101,
     'const std::array<Float3, 5>& TriangleNode::GetVertices() const', '{'),
    # Mesa 8fc4981d
    ('file', EXT + 'mesa/m/src/amd/vulkan/nir/radv_nir_rt_common.c', 582,
     'const uint32_t box_sort_enable = BITFIELD_BIT(63 - 32);',
     'const uint32_t triangle_return_mode = BITFIELD_BIT(120 - 96); /* Return IJ for triangles */'),
    ('file', EXT + 'mesa/m/src/amd/vulkan/nir/radv_nir_rt_common.c', 225,
     'nir_variable *result = nir_variable_create(b->shader, nir_var_shader_temp, vec4_type, "result");',
     'nir_store_var(b, result, nir_imm_vec4(b, INFINITY, 1.0f, 0.0f, 0.0f), 0xf);'),
    ('file', EXT + 'mesa/m/src/amd/vulkan/bvh/bvh_defines.h', 68, 'struct radv_bvh_triangle_node {', 'float coords[3][3];'),
    # AMD machine-readable ISA (zip member amdgpu_isa_rdna2.xml)
    ('zip', 'amdgpu_isa_rdna2.xml', 41543, '<InstructionName>IMAGE_BVH_INTERSECT_RAY</InstructionName>',
     '<Description>Test the intersection of rays with either box nodes or triangle nodes'),
]


def text_of(src, path):
    if src == 'file':
        return open(path, 'r', encoding='utf-8', errors='replace').read()
    if src == 'zip':
        return zipfile.ZipFile(EXT + 'mri.zip').read(path).decode('utf-8', 'replace')
    out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (src, path)], capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout.decode('utf-8', 'replace')


ok = True
cache = {}
for src, path, line, a0, a1 in REFS:
    key = (src, path)
    if key not in cache:
        cache[key] = text_of(src, path)
    text = cache[key]
    if text is None:
        print('FAIL %s:%s (no such object)' % (src, path))
        ok = False
        continue
    lines = text.replace(chr(13), '').split(chr(10))
    l0 = lines[line - 1].lstrip() if line - 1 < len(lines) else ''
    l1 = lines[line].lstrip() if line < len(lines) else ''
    good0 = l0.startswith(a0)
    good1 = l1.startswith(a1)
    name = path if src in ('file', 'zip') else '%s:%s' % (src, path)
    print('%s %s:%d anchor=%s +1=%s' % ('OK  ' if good0 and good1 else 'FAIL', name.replace(EXT, 'src_ext/'), line,
                                         'ok' if good0 else 'BAD', 'ok' if good1 else 'BAD'))
    if not (good0 and good1):
        print('      got: %r | %r' % (l0[:120], l1[:120]))
    ok &= good0 and good1
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
