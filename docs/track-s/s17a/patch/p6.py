P = 'C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
t = open(P, 'rb').read().decode('utf-8')
old = '''	for (const auto& [id, s]: sources) {
		if (!s->used.empty()) {
			m_replay_rebuilt[id] = s->used;
		}
	}
'''
new = '''	{
		// Under m_mutex: ProgramCache::ReplayAdopt reads the map under it (KYTY_SHADER_PREPARE=0 lets the guest start
		// while this thread still runs).
		Common::LockGuard lock(m_mutex);
		for (const auto& [id, s]: sources) {
			if (!s->used.empty()) {
				m_replay_rebuilt[id] = s->used;
			}
		}
	}
'''
assert t.count(old) == 1
t = t.replace(old, new)
open(P, 'wb').write(t.encode('utf-8'))
print('p6 OK')
