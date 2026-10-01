# F2a: pinned references <commit>:<path>:<line>, anchor (whole line) and control +1.
import subprocess
C = 'ba3be480'
R = [
 ('src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp', 'bool FixB26Enabled() {'),
 ('src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp', 'Opcode GateFixB26(Opcode opcode) {'),
 ('src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h', 'bool   FixB26Enabled();'),
 ('src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h', '\tS_BREV_B64,'),
 ('src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp', '    {0x0cu, Opcode::S_BREV_B64},'),
 ('src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp', '\tinst.opcode    = GateFixB26(Detail::LookupOpcode(SOP1_OPS, opcode));'),
 ('src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp', '    {0xe2u, Opcode::V_CMP_EQ_U64, false},  {0xe3u, Opcode::V_CMP_LE_U64, false},'),
 ('src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp', '\t\treturn GateFixB26(Detail::LookupOpcode(VOPC_OPS, opcode));'),
 ('src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp', '\tinst.opcode    = GateFixB26(Detail::LookupOpcode(VOPC_OPS, opcode));'),
 ('src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp', '\tconst auto* info = Detail::FindOpcode(VOPC_OPS, opcode);'),
 ('src/graphics/shader/recompiler/frontend/translate/Scalar.cpp', '\t\tcase O::S_BREV_B64: {'),
 ('src/graphics/shader/recompiler/frontend/translate/Vector.cpp', '\t\tcase O::V_CMP_LE_U64: {'),
 ('src/graphics/shader/recompiler/frontend/translate/Translate.cpp', 'std::array<IR::U32, 2> Translator::ReadU32Pair(const Decoder::Operand& operand) {'),
 ('src/graphics/shader/recompiler/frontend/translate/Compare.cpp', '\tconst auto masked = ir.LogicalAnd(ir.GetExec(), value);'),
 ('src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', '\t                            (ShaderRecompiler::Decoder::FixB26Enabled() ? ":fixb26" : "");'),
 ('src/graphics/host_gpu/renderer/pipeline/computePretranslation.h', '\t\t\t\tLOGF("CsPretranslate: skipped hash=%016" PRIx64 " reason=%s\\n", job->key.hash, error.what());'),
 ('src/graphics/host_gpu/renderer/pipeline/computePretranslation.h', '\t\t\t\tif (result && !stopping && !job->discard && cost <= limits.ready_bytes) {'),
 ('src/graphics/host_gpu/renderer/pipeline/computePretranslation.h', '\t\t\t\t\tLOGF("CsPretranslate: ready hash=%016" PRIx64 " us=%" PRIu64 " kb=%zu ready_kb=%zu\\n",'),
 ('src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp', '\t[[noreturn]] void Fail(uint32_t pc, const std::string& reason) const {'),
 ('tests/ShaderRecompilerComputeTests.cpp', 'TestCase B26ScalarBrevB64() {'),
 ('tests/ShaderRecompilerComputeTests.cpp', 'TestCase B26VectorCmpLeU64(u32 wave_size) {'),
 ('tests/ShaderRecompilerComputeTests.cpp', 'void CheckB26Decode(bool fix_on) {'),
 ('tests/ShaderRecompilerComputeTests.cpp', 'static int RunB26DecodePass(const char *eboot_path) {'),
 ('tests/ShaderRecompilerComputeTests.cpp', '  if (argc == 2 && std::strcmp(argv[1], "--fix-b26-only") == 0) {'),
]
ok = True
for path, anchor in R:
    lines = subprocess.run(['git', 'show', '%s:%s' % (C, path)], capture_output=True).stdout.decode('utf-8').split('\n')
    hits = [i for i, l in enumerate(lines) if l == anchor]
    if len(hits) != 1:
        ok = False
        print('FAIL', path, repr(anchor), len(hits))
        continue
    i = hits[0]
    print('`%s:%s:%d` | %s | +1: %s' % (C, path, i + 1, anchor.strip()[:90], lines[i + 1].strip()[:70]))
print('ALL OK' if ok else 'FAILED')
