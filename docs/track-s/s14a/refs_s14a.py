# S14a: reference map of the design - <commit>:<path>:<line>, anchor and the +1 control (general rule 24(1)).
# "gen <commit>": resolves every anchor text to its line in the pinned commit (must be unique) and writes refs_s14a.tsv;
# "check": verifies line, anchor and +1 of every row of refs_s14a.tsv against git.
import subprocess, sys, os
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
REPO='C:/kyty/KytyPS5'; GIT='C:/Program Files/Git/cmd/git.exe'
P='src/graphics/host_gpu/renderer/pipeline/'
REFS=[('src/libs/agc.cpp',['int KYTY_SYSV_ABI AgcCreateShader(Shader** dst, void* header, const volatile void* code) {',
        'map.hash                = ShaderComputeHash(const_cast<const void*>(code), h->shader_size);','*dst = h;',
        'int KYTY_SYSV_ABI AgcCreateInterpolantMapping(ShaderRegister* regs, const Shader* gs,',
        'int KYTY_SYSV_ABI AgcCreateInterpolantMapping2(ShaderRegister* regs, const Shader* gs,']),
      (P+'pipelineCache.cpp',['int AsyncPipelinesMode() {','uint32_t AsyncPipelineWaitUs() {','uint32_t AsyncPipelineThreads() {',
        'struct ProgramKey {','struct Permutation {','Permutation CompilePermutation(const ShaderParams&                          params,',
        'ShaderProgram Get(const ShaderParams& params, InputInfo& input_info,','Compile(const ShaderParams& params, InputInfo& input_info, uint32_t& push_data_cursor,',
        'auto translated = prepared ? std::move(*prepared) :','entry->second.permutations.push_back(CompilePermutation(',
        'LOGF("AvTrace: shader %s hash=0x%016" PRIx64 " translate_us=%" PRIu64 " compile_us=%" PRIu64',
        'if (AsyncPipelinesMode() != 0 && !m_ready_shader_pairs.contains(pair_key)) {','const auto queued_at = HostMicros();|0',
        'LOGF("AvTrace: pipeline gfx vs=%" PRIu64 " ps=%" PRIu64 " us=%" PRIu64|0',
        'void PipelineCache::TraceShaderRegistration(const Shader& header, const ShaderMappedData& mapped) {',
        'if (ComputePretranslation::Enabled() && mapped.type == Prospero::ShaderBinaryType::kCs &&',
        'if (!known) { m_program_cache->pretranslation.Enqueue({code, mapped.code_size_bytes / 4}, mapped.hash,',
        '// exactly three sites - Compile, LoadFromTranslationCache and Resolve - and each calls this on']),
      (P+'computePretranslation.h',['// One-shot CPU IR cache. It never touches Vulkan, live descriptors, the ordinary ProgramCache,',
        'bool Enqueue(std::span<const uint32_t> code, uint64_t hash,','std::optional<ShaderRecompiler::TranslateResult> Take(',
        'Common::ScopedFatalInterceptor recover([](const char* file, int line, std::string_view text) {']),
      ('src/graphics/shader/shader.cpp',['static bool ShaderGetStaticVertexInputInfo(uint64_t shader_addr, const HW::UserSgprInfo& user_sgpr,',
        'const auto* attrib = reinterpret_cast<const uint32_t*>(','static void ShaderGetStaticInputInfoPS(',
        'ps_info.vs_export_count      = sh.GetExportCount();','ps_info.interpolator_settings[i] = sh.ps_interpolator_settings[i];',
        'ps_info.target_export_mapping[i] = sh.target_output_mode[i] != 0',
        'void BuildStageStaticKey(const ShaderVertexInputInfo& info, std::vector<uint32_t>& key) {',
        'void BuildStageStaticKey(const ShaderPixelInputInfo& info, std::vector<uint32_t>& key) {']),
      (P+'shaderTranslationCache.cpp',['const std::string_view translator_hash = KYTY_SHADER_SOURCE_HASH;',
        'm_signature = std::string("KytySC") + std::to_string(FORMAT_VERSION) + ":" +']),
      ('src/graphics/host_gpu/renderer/renderDraw.cpp',['const bool allow_pipeline_wait =','LOGF("AsyncPipelines: skipped draw %s frame=%d vs=0x%016" PRIx64 " ps=0x%016" PRIx64']),
      ('src/graphics/presentation/videoOut.cpp',['if ((r.incomplete && hold_incomplete) || r.skip_ceil) {','m_presenter.Discard(*r.frame);'])]
def show(c,p): return subprocess.run([GIT,'-C',REPO,'show','%s:%s'%(c,p)],capture_output=True).stdout.decode('utf-8','replace').split('\n')
mode=sys.argv[1]; D='C:/kyty/s288/s14a/'
if mode=='gen':
    c=sys.argv[2]; rows=[]; bad=0
    for p,ls in REFS:
        L=[x.strip() for x in show(c,p)]
        for a in ls:
            pick=None
            if '|' in a[-3:]: a,pick=a.rsplit('|',1); pick=int(pick)
            hits=[i for i,x in enumerate(L) if x==a]
            if not hits or (len(hits)>1 and pick is None): print('NOT UNIQUE',p,a,hits); bad+=1; continue
            i=hits[pick or 0]
            rows.append('%s\t%s\t%d\t%s\t%s'%(c[:8],p,i+1,L[i],L[i+1]))
    open(D+'refs_s14a.tsv','w',encoding='utf-8',newline='\n').write('\n'.join(rows)+'\n')
    for r in rows:
        f=r.split('\t'); print(f[1].split('/')[-1],f[2],'|',f[3][:70],'|+1|',f[4][:60])
    print('rows',len(rows),'bad',bad)
else:
    ok=True; n=0
    for r in open(D+'refs_s14a.tsv',encoding='utf-8').read().split('\n'):
        if not r: continue
        c,p,ln,a,b=r.split('\t'); L=show(c,p); ln=int(ln); n+=1
        good = L[ln-1].strip()==a and L[ln].strip()==b
        ok &= good
        if not good: print('FAIL',c,p,ln)
    print('refs',n,'ALL OK' if ok else 'FAILED'); sys.exit(0 if ok else 1)
