"""S17a2 (HPP-618, ROADMAP s122 item 532(b), (g), (d)(a), (z) N2): fixes of S-replay by RC1, RC3, RC4(a) of the S17b
review and the tess round trip test. Anchors are whole lines; every anchor must match exactly once; LF in, LF out.
Usage: python patch_s17a2.py <KytyPS5 root>"""
import sys

ROOT = sys.argv[1].rstrip('/') + '/'


def patch(rel, edits):
    path = ROOT + rel
    data = open(path, 'rb').read().decode('utf-8')
    crlf = '\r\n' in data
    text = data.replace('\r\n', '\n')
    for old, new in edits:
        # whole-line anchor: old starts at a line start and ends at a line end
        hits = []
        start = 0
        while True:
            i = text.find(old, start)
            if i < 0:
                break
            if (i == 0 or text[i - 1] == '\n') and (i + len(old) == len(text) or text[i + len(old)] == '\n'):
                hits.append(i)
            start = i + 1
        if len(hits) != 1:
            sys.exit('ANCHOR FAIL %s (%d hits): %r' % (rel, len(hits), old[:120]))
        i = hits[0]
        text = text[:i] + new + text[i + len(old):]
    if crlf:
        text = text.replace('\n', '\r\n')
    open(path, 'wb').write(text.encode('utf-8'))
    print('patched', rel, len(edits))


# --- RC1: pipelineCache.h - public ReplayCloseStop next to FinishPreparation ---------------------------------------
patch('src/graphics/host_gpu/renderer/pipeline/pipelineCache.h', [(
    r'''	// Called before the guest starts, once the precache producer AND its workers have finished.
	void FinishPreparation();''',
    r'''	// Called before the guest starts, once the precache producer AND its workers have finished.
	void FinishPreparation();
	// Track S, S17a2 (ROADMAP s122 item 532(b)): the window was closed on the preparation screen. At KYTY_S_REPLAY 1 or
	// 3 stores m_precache_stop and joins the precache/rebuild thread; at 0 and 2 returns at once.
	void ReplayCloseStop();'''),
])

# --- RC1 and RC3: pipelineCache.cpp --------------------------------------------------------------------------------
patch('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', [
    (r'''	PipelineCacheLog("ShaderPreparation: ready completed={} total={} skipped={}",
	                 status.completed, status.total, status.skipped);
}''',
     r'''	PipelineCacheLog("ShaderPreparation: ready completed={} total={} skipped={}",
	                 status.completed, status.total, status.skipped);
}

// Track S, S17a2 (HPP-618, ROADMAP s122 item 532(b), RC1 of the S17b review): WindowPrepareShaders returned false (the
// window was closed on the preparation screen) and the caller (emulator.cpp, Execute) ends the process by
// std::quick_exit, which runs no destructor - ~PipelineCache never stores m_precache_stop. At KYTY_S_REPLAY 1 or 3 (the
// rebuild may run on the precache thread) this stores m_precache_stop and joins the thread: the rebuild loop stops
// before its next R-PIPE and takes its stopped branch (translation cache files of the sources it changed saved, no
// pipelines.bin, no manifest, line "ShaderReplay: rebuild ... pipelines_bin=stopped"); PrecachePipelines stops before
// its next recipe. The wait is at most one R-PIPE (or one recipe). At 0 and 2 nothing is done (the old close path).
void PipelineCache::ReplayCloseStop() {
	if (!ShaderReplay::RebuildOn()) {
		return;
	}
	const auto begin = HostMicros();
	LOGF("ShaderReplay: close stop requested precache_active=%d\n", m_precache_active.load() ? 1 : 0);
	m_precache_stop.store(true);
	if (m_precache_thread.joinable()) {
		m_precache_thread.join();
	}
	LOGF("ShaderReplay: close stop joined wait_ms=%" PRIu64 "\n", (HostMicros() - begin) / 1000u);
}'''),
    (r'''		std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}", cache.Signature());''',
     r'''		std::string manifest = fmt::format("# ShaderReplay rebuild manifest; signature {}\n", cache.Signature());'''),
])

# --- RC1: window.cpp - the close branch of the preparation loop --------------------------------------------------
patch('src/graphics/presentation/window/window.cpp', [(
    r'''				SetShaderPreparationOverlay(false);
				return false;''',
    r'''				SetShaderPreparationOverlay(false);
				// Track S, S17a2 (ROADMAP s122 item 532(b)): the caller ends the process by std::quick_exit; at
				// KYTY_S_REPLAY 1 or 3 the precache/rebuild thread is stopped and joined first (nothing at 0 and 2).
				cache.ReplayCloseStop();
				return false;'''),
])

# --- RC1 comment and RC4(a): shaderReplay.cpp ------------------------------------------------------------------------
patch('src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', [
    (r'''	// KYTY_S_REPLAY_TEST=stop: the same event a click on the close button of the window produces; the preparation loop
	// (window.cpp, WindowPrepareShaders) returns and the shutdown path stores m_precache_stop.''',
     r'''	// KYTY_S_REPLAY_TEST=stop: the same event a click on the close button of the window produces; the preparation loop
	// (window.cpp, WindowPrepareShaders) returns false after PipelineCache::ReplayCloseStop stored m_precache_stop and
	// joined the precache/rebuild thread (S17a2, item 532(b)); then the caller ends the process by std::quick_exit.'''),
    (r'''	// KYTY_S_REPLAY_TEST=canon: one canonical T# base field spoiled (a non-null T# made null) in one record - the
	// self-check below must reject it (canon_mismatch > 0, member K3).
	if (canon_stand && !g_canon_stand_done.load()) {
		for (auto& word: canonical) {
			if (word.role == ROLE_T_LO && word.value == 1u) {
				word.value = 0u;
				g_canon_stand_done.store(true);
				LOGF("ShaderReplay: stand canon applied hash=0x%016" PRIx64 "\n", plan.shader_hash);
				break;
			}
		}
	}
	// Self-check (S16a section 2.2, member K3): the canonical path gives the live specialization.
	const auto check = Run(plan, canonical, user_words, false);''',
     r'''	// KYTY_S_REPLAY_TEST=canon: one canonical T# base field spoiled (a non-null T# made null) - the self-check below must
	// reject it (canon_mismatch > 0, member K3). S17a2 (item 532(d)(a), RC4(a) of the S17b review): the stand is spent
	// only by a record whose spoiled copy the self-check rejected; when it passes (the specialization does not depend on
	// that T# being null) the word gets its canonical value back, the record is checked unspoiled and the stand spoils
	// the next suitable record. The stand line carries the outcome (rejected=1|0).
	size_t stand_word = canonical.size();
	if (canon_stand && !g_canon_stand_done.load()) {
		for (size_t i = 0; i < canonical.size(); i++) {
			if (canonical[i].role == ROLE_T_LO && canonical[i].value == 1u) {
				canonical[i].value = 0u;
				stand_word         = i;
				break;
			}
		}
	}
	// Self-check (S16a section 2.2, member K3): the canonical path gives the live specialization.
	auto check = Run(plan, canonical, user_words, false);
	if (stand_word < canonical.size()) {
		const bool rejected = !check.ok || !check.complete || !(check.specialization == live);
		LOGF("ShaderReplay: stand canon applied hash=0x%016" PRIx64 " rejected=%d\n", plan.shader_hash, rejected ? 1 : 0);
		if (rejected) {
			g_canon_stand_done.store(true);
		} else {
			canonical[stand_word].value = 1u;
			check                       = Run(plan, canonical, user_words, false);
		}
	}'''),
])

# --- N2: tests/shaderCfgTests.cpp - round trip of the tess part of the vertex key -----------------------------------
patch('tests/shaderCfgTests.cpp', [(
    r'''    Check(SR::ComputeFromKey(key, compute2, why), "replay ComputeFromKey");
    BuildStageStaticKey(compute2, again);
    Check(again == key, "replay compute key round trip");''',
    r'''    Check(SR::ComputeFromKey(key, compute2, why), "replay ComputeFromKey");
    BuildStageStaticKey(compute2, again);
    Check(again == key, "replay compute key round trip");
    // S17a2 (N2 of the S17b review): the tess branch of VertexFromKey - input -> key -> input -> key with the tess input
    // of ShaderRecompilerComputeTests (input/output control points 3, strides 124/128, domain 1, partitioning 2,
    // topology 2) and one resource; a key cut inside its tess part is rejected with why "tess".
    ShaderVertexInputInfo tess_vertex {};
    tess_vertex.tess = {.input_control_points = 3, .output_control_points = 3, .ls_stride = 124, .hs_stride = 128,
                        .domain = 1, .partitioning = 2, .output_topology = 2};
    tess_vertex.fetch_embedded = true;
    tess_vertex.fetch_attrib_reg = 2;
    tess_vertex.resources_num = 1;
    tess_vertex.resources_dst[0].register_start = 4;
    tess_vertex.resources_dst[0].registers_num = 4;
    tess_vertex.resources[0].fields[1] = 16u << 16u;
    tess_vertex.resources[0].fields[3] = 4u | (5u << 3u) | (6u << 6u) | (7u << 9u) | (77u << 12u);
    std::vector<uint32_t> tess_key;
    BuildStageStaticKey(tess_vertex, tess_key);
    ShaderVertexInputInfo tess_rebuilt {};
    Check(tess_key.size() == 7u + 1u + 7u + 13u && SR::VertexFromKey(tess_key, ShaderType::Vertex, tess_rebuilt, why),
          "replay VertexFromKey tess");
    std::vector<uint32_t> tess_again;
    BuildStageStaticKey(tess_rebuilt, tess_again);
    ShaderVertexInputInfo tess_third {};
    std::vector<uint32_t> tess_last;
    const bool tess_third_ok = SR::VertexFromKey(tess_again, ShaderType::Vertex, tess_third, why);
    BuildStageStaticKey(tess_third, tess_last);
    Check(tess_third_ok && tess_again == tess_key && tess_last == tess_key &&
              tess_rebuilt.tess.input_control_points == 3u && tess_rebuilt.tess.output_control_points == 3u &&
              tess_rebuilt.tess.ls_stride == 124u && tess_rebuilt.tess.hs_stride == 128u &&
              tess_rebuilt.tess.domain == 1u && tess_rebuilt.tess.partitioning == 2u &&
              tess_rebuilt.tess.output_topology == 2u && tess_third.tess.hs_stride == 128u,
          "replay vertex key round trip with tess");
    why.clear();
    Check(!SR::VertexFromKey(std::span(tess_key).first(9), ShaderType::Vertex, tess_rebuilt, why) && why == "tess",
          "replay VertexFromKey rejects a key cut inside its tess part");'''),
])

# --- README S17a: K1(4) row and the stop stand text --------------------------------------------------------------
patch('docs/track-s/s17a/README.md', [
    ('| К1(4) отмена по `m_precache_stop` | цикл перестройки `PipelineCache::ReplayRebuild` проверяет флаг перед каждым R-PIPE; при остановке `pipelines.bin` не пишется (`pipelines_bin=stopped`), файлы кэша трансляции сохранены по одному (каждый — своим временным файлом) |',
     '| К1(4) отмена по `m_precache_stop` | цикл перестройки `PipelineCache::ReplayRebuild` проверяет флаг перед каждым R-PIPE; при остановке `pipelines.bin` не пишется (`pipelines_bin=stopped`), файлы кэша трансляции сохранены по одному (каждый — своим временным файлом). **Поправка S17a2 (п. 532(б), RC1 S17b):** в коде S17a флаг ставил только `~PipelineCache`, которого `std::quick_exit` не исполняет, — на пути закрытия окна отмены не было (процесс снимался в любой точке цикла); с S17a2 флаг ставит и поток ждёт `PipelineCache::ReplayCloseStop` в ветви закрытия `WindowPrepareShaders` при `KYTY_S_REPLAY` ∈ {1, 3} (`docs/track-s/s17a2/README.md`) |'),
    ('выключения ставит `m_precache_stop`; `corrupt` — при загрузке испорчен байт текущего поколения ⇒ проверка суммы, откат на предыдущее.',
     'выключения ставит `m_precache_stop` (с S17a2 — `PipelineCache::ReplayCloseStop` до `std::quick_exit`; в S17a не ставил, RC1 S17b); `corrupt` — при загрузке испорчен байт текущего поколения ⇒ проверка суммы, откат на предыдущее.'),
])
print('ALL PATCHED')
