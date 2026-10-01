import subprocess
BS=chr(92)
R=[('ba3be480','src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp',329,'bool FixB26Enabled() {'),
('ba3be480','src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp',337,'Opcode GateFixB26(Opcode opcode) {'),
('ba3be480','src/graphics/shader/recompiler/frontend/decode/ScalarAluOps.cpp',150,'inst.opcode    = GateFixB26(Detail::LookupOpcode(SOP1_OPS, opcode));'),
('ba3be480','src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp',372,'return GateFixB26(Detail::LookupOpcode(VOPC_OPS, opcode));'),
('ba3be480','src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp',1115,'if (!SupportsVopcSdwa(inst.opcode)) {'),
('ba3be480','src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp',1147,'if (inst.opcode == Opcode::UNSUPPORTED) {'),
('ba3be480','src/graphics/shader/recompiler/frontend/decode/VectorAluOps.cpp',1539,'inst.opcode    = GateFixB26(Detail::LookupOpcode(VOPC_OPS, opcode));'),
('ba3be480','src/graphics/shader/recompiler/frontend/translate/Scalar.cpp',172,'case O::S_BREV_B64: {'),
('ba3be480','src/graphics/shader/recompiler/frontend/translate/Vector.cpp',109,'case O::V_CMP_LE_U64: {'),
('ba3be480','src/graphics/shader/recompiler/frontend/translate/Compare.cpp',11,'const auto masked = ir.LogicalAnd(ir.GetExec(), value);'),
('ba3be480','src/graphics/shader/recompiler/frontend/translate/Translate.cpp',451,'std::array<IR::U32, 2> Translator::ReadU32Pair(const Decoder::Operand& operand) {'),
('ba3be480','src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',578,'(ShaderRecompiler::Decoder::FixB26Enabled() ? ":fixb26" : "");'),
('ba3be480','src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp',595,r'LOGF("Shader translation cache: %s\n", Common::PathToString(m_directory).c_str());'),
('ba3be480','src/graphics/host_gpu/renderer/pipeline/computePretranslation.h',232,r'LOGF("CsPretranslate: skipped hash=%016" PRIx64 " reason=%s\n", job->key.hash, error.what());'),
('ba3be480','src/graphics/host_gpu/renderer/pipeline/computePretranslation.h',242,'if (result && !stopping && !job->discard && cost <= limits.ready_bytes) {'),
('ba3be480','src/graphics/host_gpu/renderer/pipeline/computePretranslation.h',255,r'LOGF("CsPretranslate: ready hash=%016" PRIx64 " us=%" PRIu64 " kb=%zu ready_kb=%zu\n",'),
('ba3be480','src/graphics/shader/recompiler/frontend/translate/Dispatch.cpp',15,'EXIT("unsupported decoded instruction: %s", Decoder::InstructionToString(inst).c_str());'),
('a78a0ea0','tests/ShaderRecompilerComputeTests.cpp',20884,'code.push_back(EncodeVopc(0xe3, 4, 2)); // 0: 31 <= lane'),
('a78a0ea0','tests/ShaderRecompilerComputeTests.cpp',32062,'CheckImageTransitionState(vulkan.RuntimeRenderer());'),
]
ok=True
for c,p,n,a in R:
    t=subprocess.run(['git','-C','C:/kyty/KytyPS5','show',c+':'+p],capture_output=True,text=True,encoding='utf-8').stdout.split('\n')
    line=t[n-1].strip(); nxt=t[n].strip()
    good= line==a
    ok&=good
    print(('OK ' if good else 'BAD'),'%s:%s:%d'%(c,p,n),'| anchor:',line[:110],'| +1:',nxt[:80])
print('ALL OK' if ok else 'FAIL')
