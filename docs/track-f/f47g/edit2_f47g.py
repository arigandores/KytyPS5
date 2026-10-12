"""Draft edit 2 of F47g: SRT guest-now by re-materialization (NotePsRuntime) and the cmp rule of the img line."""
import sys

D = sys.argv[1]
R = D + '/src/graphics/host_gpu/renderer/'


def rep(path, old, new):
    t = open(path, encoding='utf-8').read()
    assert t.count(old) == 1, (path, t.count(old), old[:70])
    open(path, 'wb').write(t.replace(old, new).encode('utf-8'))


# header: NotePsRuntime
rep(R + 'diagF47Dt.h',
    '// Called by PipelineCache::CreateGraphicsPipelineLocked with the finished key (thread-local copy).\n',
    '// Called by ProgramCache::Get for the pixel stage with the resource plan of the program (nullptr: not known yet),\n'
    '// the program address and the user data the materialization reads (thread-local copy for the next OnDraw).\n'
    'void NotePsRuntime(const void* resource_plan, uint64_t shader_base, const uint32_t* user_data, size_t count);\n'
    '// Called by PipelineCache::CreateGraphicsPipelineLocked with the finished key (thread-local copy).\n')

C = R + 'diagF47Dt.cpp'
rep(C, '#include "graphics/shader/shaderBindings.h"\n',
    '#include "graphics/shader/shaderBindings.h"\n'
    '#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"\n'
    '#include "graphics/shader/recompiler/ir/passes/SrtWalker.h"\n')

# the thread-local PS runtime and the two readers of the re-materialization
rep(C, '// The pipeline key of the draw being prepared on this thread.\n',
    '// The PS runtime of the draw being prepared on this thread (ProgramCache::Get, pixel stage).\n'
    'struct PsRuntime {\n'
    '\tbool                  valid       = false;\n'
    '\tconst void*           plan        = nullptr;\n'
    '\tuint64_t              shader_base = 0;\n'
    '\tstd::vector<uint32_t> user_data;\n'
    '};\n'
    'thread_local PsRuntime t_ps;\n'
    '\n'
    '// Readers of the re-materialization: the guest backing as it is now, no read cache, no counters (the reader of the\n'
    '// draw path, ReadShaderLiveMemory, reads the same backing through a per-call page cache; its clean twin reads only\n'
    '// GPU-clean words). A word that cannot be read fails the materialization.\n'
    'bool ReadLiveForDiag(void* /*userdata*/, uint64_t address, uint32_t* value) {\n'
    '\treturn value != nullptr && Libs::LibKernel::Memory::TryReadBacking(address, value, sizeof(*value));\n'
    '}\n'
    'bool ReadCleanForDiag(void* /*userdata*/, uint64_t address, uint32_t* value) {\n'
    '\treturn value != nullptr && Libs::LibKernel::Memory::TryReadGpuCleanBacking(address, value, sizeof(*value));\n'
    '}\n'
    '\n'
    '// The pipeline key of the draw being prepared on this thread.\n')

rep(C, 'void NoteGraphicsKey(const PipelineStaticParameters& params, const PipelineRenderingState& rendering) {\n',
    'void NotePsRuntime(const void* resource_plan, uint64_t shader_base, const uint32_t* user_data, size_t count) {\n'
    '\tif (!On()) {\n'
    '\t\treturn;\n'
    '\t}\n'
    '\tt_ps.valid       = true;\n'
    '\tt_ps.plan        = resource_plan;\n'
    '\tt_ps.shader_base = shader_base;\n'
    '\tt_ps.user_data.assign(user_data, user_data + count);\n'
    '}\n'
    '\n'
    'void NoteGraphicsKey(const PipelineStaticParameters& params, const PipelineRenderingState& rendering) {\n')

# consume t_ps at the top of OnDraw
rep(C, '\tconst bool key_valid = t_key.valid;\n'
       '\tt_key.valid          = false;\n',
    '\tconst bool key_valid = t_key.valid;\n'
    '\tt_key.valid          = false;\n'
    '\tconst PsRuntime ps_rt = t_ps;\n'
    '\tt_ps.valid           = false;\n')

# the srt line: + the re-materialization of the draw's plan against guest memory now
old_srt_start = '\t// (c) the flattened SRT (what SMEM loads of the PS read)\n'
old_srt_end = '\t// (g) raw guest register words, last write before this draw\n'
t = open(C, encoding='utf-8').read()
i = t.index(old_srt_start)
j = t.index(old_srt_end)
new_srt = '''	// (c) the flattened SRT (what SMEM loads of the PS read) and the descriptors: the draw's snapshot against a fresh
	// materialization of the same plan from guest memory now (value (i) of the SMEM / user-data inputs).
	if (pixel != nullptr) {
		std::string given;
		const bool  ring = ring_hash(pixel->flattened_srt, &given);
		std::string fresh_s;
		if (!ps_rt.valid || ps_rt.plan == nullptr) {
			fresh_s = "fresh=unmeasured:no_plan";
		} else if (ps_rt.user_data != resources.user_data) {
			fresh_s = "fresh=unmeasured:user_data_differs";
		} else {
			ShaderRecompiler::IR::ResourceSnapshot       fresh;
			ShaderRecompiler::IR::ResourceSpecialization fresh_spec;
			const ShaderRecompiler::IR::SrtRuntime       rt {
			          .user_data                  = std::span<const uint32_t>(ps_rt.user_data),
			          .shader_base                = ps_rt.shader_base,
			          .read_memory                = &ReadLiveForDiag,
			          .userdata                   = nullptr,
			          .read_specialization_memory = &ReadCleanForDiag,
            };
			const bool ok = ShaderRecompiler::IR::MaterializeResources(
			    *static_cast<const ShaderRecompiler::IR::ResourcePlan*>(ps_rt.plan), rt, fresh, fresh_spec);
			if (!ok) {
				fresh_s = "fresh=fail";
			} else {
				fresh_s = fmt::format(
				    "fresh=ok fh={} same_srt={} same_img={} same_buf={} same_smp={} same_ud={}",
				    fresh.flattened_srt.empty()
				        ? std::string("-")
				        : fmt::format("{:016x}", Hash(reinterpret_cast<const uint8_t*>(fresh.flattened_srt.data()),
				                                      fresh.flattened_srt.size() * 4u)),
				    fresh.flattened_srt == resources.flattened_srt ? 1 : 0, fresh.images == resources.images ? 1 : 0,
				    fresh.buffers == resources.buffers ? 1 : 0, fresh.samplers == resources.samplers ? 1 : 0,
				    fresh.user_data == resources.user_data ? 1 : 0);
			}
		}
		const std::string snaph =
		    resources.flattened_srt.empty()
		        ? std::string("-")
		        : fmt::format("{:016x}", Hash(reinterpret_cast<const uint8_t*>(resources.flattened_srt.data()),
		                                      resources.flattened_srt.size() * 4u));
		const std::string sdh =
		    pixel->shader_data.empty()
		        ? std::string("-")
		        : fmt::format("{:016x}", Hash(reinterpret_cast<const uint8_t*>(pixel->shader_data.data()),
		                                      pixel->shader_data.size() * 4u));
		LOGF("F47dt: kind=srt n=%u d=%u words=%zu snaph=%s given=%s gvh=%s %s shader_data=%zu sdh=%s\\n", n, d,
		     resources.flattened_srt.size(), snaph.c_str(),
		     ring ? "ring_copy" : (pixel->flattened_srt.buffer ? "other" : "none"), ring ? given.c_str() : "-",
		     fresh_s.c_str(), pixel->shader_data.size(), sdh.c_str());
	}
'''
t = t[:i] + new_srt + t[j:]
open(C, 'wb').write(t.encode('utf-8'))

# cmp rule of the img line = the reader's rule (convenience only)
rep(C, '''		const int c = one(rec.cur);
		const int p = rec.has_prev ? one(rec.prev) : 1;
		cmp         = (c == 2 || p == 2) ? "ne" : ((c == 1 && p == 1) ? "eq" : "und");
''', '''		// ne only when the last upload covers every level (no pending levels) and differs; a differing earlier part
		// of a completed deferred upload, or a partial last upload, is "und" (which levels changed is not known).
		const int  c       = one(rec.cur);
		const int  p       = rec.has_prev ? one(rec.prev) : 1;
		const bool partial = rec.cur.pending != 0;
		cmp = (c == 2 && !partial) ? "ne" : ((c == 1 && p == 1 && !partial) ? "eq" : "und");
''')

# patch script: the NotePsRuntime hook in ProgramCache::Get
P = D + '/patch_f47g.py'
rep(P, "# 3. shaders.cpp",
    "# 2b. pipelineCache.cpp - the PS runtime of the draw (ProgramCache::Get, pixel stage).\n"
    "edit('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [\n"
    "    ('\\t\\t    .read_specialization_memory = ReadShaderGuestMemory,\\n'\n"
    "     '\\t\\t};\\n'\n"
    "     '\\t\\tpg_mark(Common::FrameStats::Counter::ProgLapLocalNs);\\n',\n"
    "     '\\t\\t    .read_specialization_memory = ReadShaderGuestMemory,\\n'\n"
    "     '\\t\\t};\\n'\n"
    "     '\\t\\t// Track F, F47g (HPP-824): KYTY_DIAG_F47DT - the plan, base and user data of the PS (measurement only).\\n'\n"
    "     '\\t\\tif (DiagF47Dt::On() && stage == ShaderType::Pixel) {\\n'\n"
    "     '\\t\\t\\tDiagF47Dt::NotePsRuntime(entry != programs.end() ? &entry->second.resource_plan : nullptr,\\n'\n"
    "     '\\t\\t\\t                         params.Base(), params.user_data.data(), params.user_data.size());\\n'\n"
    "     '\\t\\t}\\n'\n"
    "     '\\t\\tpg_mark(Common::FrameStats::Counter::ProgLapLocalNs);\\n'),\n"
    "])\n\n# 3. shaders.cpp")
print('edit2 ok')
