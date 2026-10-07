# F25k: t_in_queue by a scope guard (an exception out of the locked region - bad_alloc of push_back - must not leave the
# flag set: the thread's later lines would go to t_nested forever and Drain / Flush would skip). Usage: edit_log2.py <log.cpp>...
import sys
old = '''		{
			std::unique_lock lock(s.mu);
			t_in_queue = true;
			if (s.closed) {
				t_in_queue = false;
				return;
			}
			if (!t_writer && s.pending != 0 && s.pending + n > s.limit) {
				const auto t0 = NowNs();
				s.full_waits++;
				s.cv_space.wait(lock, [&] { return s.closed || s.pending == 0 || s.pending + n <= s.limit; });
				s.full_wait_ns += NowNs() - t0;
				if (s.closed) {
					t_in_queue = false;
					return;
				}
			}
			s.q.push_back(std::move(line));
			s.pending += n;
			g_pending_bytes.fetch_add(n, std::memory_order_relaxed);
			s.max_pending = std::max(s.max_pending, s.pending);
			s.lines++;
			s.bytes += n;
			notify     = s.writer_waiting;
			t_in_queue = false;
		}
'''
new = '''		{
			std::unique_lock lock(s.mu);
			// t_in_queue is set while this thread holds s.mu; the guard clears it on every exit of the scope (also an
			// exception of push_back), before the lock is released (declared after it).
			struct InQueue {
				InQueue() { t_in_queue = true; }
				~InQueue() { t_in_queue = false; }
				InQueue(const InQueue&)            = delete;
				InQueue& operator=(const InQueue&) = delete;
			} in_queue;
			if (s.closed) {
				return;
			}
			if (!t_writer && s.pending != 0 && s.pending + n > s.limit) {
				const auto t0 = NowNs();
				s.full_waits++;
				s.cv_space.wait(lock, [&] { return s.closed || s.pending == 0 || s.pending + n <= s.limit; });
				s.full_wait_ns += NowNs() - t0;
				if (s.closed) {
					return;
				}
			}
			s.q.push_back(std::move(line));
			s.pending += n;
			g_pending_bytes.fetch_add(n, std::memory_order_relaxed);
			s.max_pending = std::max(s.max_pending, s.pending);
			s.lines++;
			s.bytes += n;
			notify = s.writer_waiting;
		}
'''
for p in sys.argv[1:]:
    t = open(p, 'rb').read().decode()
    assert '\r' not in t
    assert t.count(old) == 1, p
    open(p, 'wb').write(t.replace(old, new).encode())
    print('ok', p)
