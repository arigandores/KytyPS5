# F20j3 (HPP-646): part 2 of patch_f20j3.py - the wait sites (item 574(g)(1)-(2)). Included by patch_f20j3.py (exec).
# Every mark: one over the whole wait loop, begun only on the blocking path (one test of g_on at =0), BeginWReg (a
# registered thread only), ended after the loop with the waker of the waited object; peer - the role thread that
# advances the condition by the code (or 0).

D = 'Common::DiagB32::'

# ---------------------------------------------------------------------------------------------------- includes
for p in ['src/common/threads.cpp', 'src/graphics/host_gpu/renderer/commandRecorder.cpp',
          'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'src/common/parallelCopy.cpp',
          'src/graphics/host_gpu/pageManager.cpp', 'src/graphics/host_gpu/vma.cpp',
          'src/graphics/presentation/window/screenshot.cpp', 'src/graphics/presentation/window/hostInput.cpp',
          'src/kernel/syncOnAddress.cpp', 'src/libs/libKernel.cpp', 'src/libs/libC.cpp', 'src/libs/avPlayer.cpp',
          'src/libs/audio.cpp', 'src/libs/libAudio2.cpp', 'src/libs/libUlt.cpp', 'src/libs/network.cpp',
          'src/graphics/host_gpu/regionManager.h']:
    add_include(p)

# ---------------------------------------------------------------------------------------------------- GuestGpu
G = 'src/graphics/guest_gpu/graphicsRun.cpp'
edit(G, '''	std::binary_semaphore done {0};
	SendCommand([operation = std::move(command), &done]() mutable {
		operation();
		done.release();
	});
	done.acquire();
}
''', '''	std::binary_semaphore done {0};
	SendCommand([operation = std::move(command), &done]() mutable {
		operation();
		Common::DiagB32::NoteSignal(&done); // Track F, F20j3: the releaser of the caller (GuestGpu)
		done.release();
	});
	// Track F, F20j3 (KYTY_DIAG_B32 W:gpu_cmd, item 574(g)(1)): the caller waits until GuestGpu ran the command.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::GpuCmd, &done, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), 0);
	}
	done.acquire();
	b32.EndSig(&done);
}
''')

edit(G, '''void GuestGpu::WaitForIdle() {
	Common::LockGuard lock(m_queue_mutex);
	while (m_processing || !m_commands.empty() || m_submission_count != 0) {
		m_idle.Wait(&m_queue_mutex);
	}
}
''', '''void GuestGpu::WaitForIdle() {
	Common::LockGuard lock(m_queue_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:gpu_wait, item 574(g)(1), (a)(4)): the caller (AgcSuspendPoint -> Done) waits for
	// GuestGpu to drain - one mark over the loop (the 10 ms poll wakeups of CondVar::Wait stay inside it); waker - the
	// last m_idle signaller, peer - GuestGpu.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && (m_processing || !m_commands.empty() || m_submission_count != 0)) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::GpuWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), 0);
	}
	while (m_processing || !m_commands.empty() || m_submission_count != 0) {
		m_idle.Wait(&m_queue_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(m_idle.B32Waker(b32.SinceNs()), false);
	}
}
''')

edit(G, '''		SetThreadDescription(GetCurrentThread(), L"M4Baton");
		g_baton_thread = true;
''', '''		SetThreadDescription(GetCurrentThread(), L"M4Baton");
		g_baton_thread = true;
		if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j3: the relay's slot - the peer of W:relay
			Common::DiagB32::RegisterRole("Relay");
		}
''')

edit(G, '''			{
				std::lock_guard<std::mutex> lock(mutex);
				has_job = false;
				done    = true;
			}
			to_owner.notify_one();
''', '''			{
				std::lock_guard<std::mutex> lock(mutex);
				has_job = false;
				done    = true;
			}
			Common::DiagB32::NoteSignal(&to_owner); // Track F, F20j3: the waker of W:relay
			to_owner.notify_one();
''')

edit(G, '''	relay->to_relay.notify_one();
	{
		std::unique_lock<std::mutex> lock(relay->mutex);
		relay->to_owner.wait(lock, [relay] { return relay->done; });
	}
''', '''	relay->to_relay.notify_one();
	{
		std::unique_lock<std::mutex> lock(relay->mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:relay, item 574(a)(4)): GuestGpu parks while the relay runs its range.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on && !relay->done) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Relay, relay, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Relay), 0);
		}
		relay->to_owner.wait(lock, [relay] { return relay->done; });
		b32.EndSig(&relay->to_owner);
	}
''')

# ---------------------------------------------------------------------------------------------------- video out
V = 'src/graphics/presentation/videoOut.cpp'
edit(V, '''		if (total_wait > 0) {
			const auto remaining_us =
			    (static_cast<uint64_t>(total_wait) * 1000000u + frequency - 1) / frequency;
			Common::Thread::SleepMicro(static_cast<uint32_t>(
			    std::clamp<uint64_t>(remaining_us, 1, std::numeric_limits<uint32_t>::max())));
		}
''', '''		if (total_wait > 0) {
			const auto remaining_us =
			    (static_cast<uint64_t>(total_wait) * 1000000u + frequency - 1) / frequency;
			// Track F, F20j3 (KYTY_DIAG_B32 W:vo_pace, item 574(g)(1)): the present thread's own vblank pacing sleep.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::VoPace, this, 0, remaining_us);
			}
			Common::Thread::SleepMicro(static_cast<uint32_t>(
			    std::clamp<uint64_t>(remaining_us, 1, std::numeric_limits<uint32_t>::max())));
			b32.End(0, false);
		}
''')

edit(V, '''	std::vector<Graphics::Presenter::Frame*> frames;
	m_mutex.Lock();
	while (m_processing && !m_requests.empty() && m_requests.front().cfg == &cfg) {
		m_done_cond_var.Wait(&m_mutex);
	}
''', '''	std::vector<Graphics::Presenter::Frame*> frames;
	m_mutex.Lock();
	// Track F, F20j3 (KYTY_DIAG_B32 W:flip_cancel, item 574(a)(4)): Close waits for the present of its front request.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && m_processing && !m_requests.empty() && m_requests.front().cfg == &cfg) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::FlipCancel, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (m_processing && !m_requests.empty() && m_requests.front().cfg == &cfg) {
		m_done_cond_var.Wait(&m_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(m_done_cond_var.B32Waker(b32.SinceNs()), false);
	}
''')

edit(V, '''void FlipQueue::WaitForSubmitSlot() {
	Common::LockGuard lock(m_mutex);
	while (m_requests.size() + m_cpu_requests.size() >= VIDEO_OUT_FLIP_QUEUE_CAPACITY) {
		if (m_requests.empty()) {
			EXIT("video-out queue is saturated by CPU flips queued behind the current EOP\\n");
		}
		m_submit_slot_cond_var.Wait(&m_mutex);
	}
}
''', '''void FlipQueue::WaitForSubmitSlot() {
	Common::LockGuard lock(m_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:flip_slot, item 574(a)(4)): GuestGpu waits for the present thread to free a slot.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && m_requests.size() + m_cpu_requests.size() >= VIDEO_OUT_FLIP_QUEUE_CAPACITY) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::FlipSlot, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (m_requests.size() + m_cpu_requests.size() >= VIDEO_OUT_FLIP_QUEUE_CAPACITY) {
		if (m_requests.empty()) {
			EXIT("video-out queue is saturated by CPU flips queued behind the current EOP\\n");
		}
		m_submit_slot_cond_var.Wait(&m_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(m_submit_slot_cond_var.B32Waker(b32.SinceNs()), false);
	}
}
''')

edit(V, '''	while (has_request()) {
		m_done_cond_var.Wait(&m_mutex);
	}
}
''', '''	// Track F, F20j3 (KYTY_DIAG_B32 W:flip_done, item 574(a)(4)): WaitFlipDone waits until the request is presented.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && has_request()) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::FlipDone, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (has_request()) {
		m_done_cond_var.Wait(&m_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(m_done_cond_var.B32Waker(b32.SinceNs()), false);
	}
}
''')

edit(V, '''	m_mutex.Lock();
	if (m_requests.empty()) {
		m_submit_cond_var.WaitFor(&m_mutex, micros);

		if (m_requests.empty()) {
''', '''	m_mutex.Lock();
	if (m_requests.empty()) {
		// Track F, F20j3 (KYTY_DIAG_B32 W:flip_req, item 574(a)(4)): the present thread waits for a flip request; peer -
		// GuestGpu (it supplies the GPU flip requests), waker - the last m_submit_cond_var signaller (Complete).
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::FlipReq, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), micros);
		}
		const bool b32_got = m_submit_cond_var.WaitFor(&m_mutex, micros);
		if (b32.Active()) [[unlikely]] {
			b32.End(m_submit_cond_var.B32Waker(b32.SinceNs()), !b32_got);
		}

		if (m_requests.empty()) {
''')

edit(V, '''	Common::LockGuard lock(ctx->mutex);
	const auto        count = ctx->vblank_status.count;
	while (ctx->opened && ctx->vblank_status.count == count) {
		ctx->vblank_cond.Wait(&ctx->mutex);
	}

	return OK;
''', '''	Common::LockGuard lock(ctx->mutex);
	const auto        count = ctx->vblank_status.count;
	// Track F, F20j3 (KYTY_DIAG_B32 W:vblank, item 574(a)(4)): the guest waits for the next vblank (VblankEnd of the
	// present thread signals) - a wait the guest asked for (GUEST_SLEEP kind group, item 574(d)).
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && ctx->opened) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Vblank, ctx, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
	}
	while (ctx->opened && ctx->vblank_status.count == count) {
		ctx->vblank_cond.Wait(&ctx->mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(ctx->vblank_cond.B32Waker(b32.SinceNs()), false);
	}

	return OK;
''')

# ---------------------------------------------------------------------------------------------------- swapchain frame pool
S = 'src/graphics/presentation/window/swapchain.cpp'
edit(S, '''		while (m_free.empty()) {
			m_available.Wait(&m_mutex);
		}
		auto* frame = m_free.front();
''', '''		// Track F, F20j3 (KYTY_DIAG_B32 W:frame_pool, item 574(g)(1)): PrepareFrame (GuestGpu) waits for the present
		// thread to return a prepared frame.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on && m_free.empty()) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::FramePool, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);
		}
		while (m_free.empty()) {
			m_available.Wait(&m_mutex);
		}
		if (b32.Active()) [[unlikely]] {
			b32.End(m_available.B32Waker(b32.SinceNs()), false);
		}
		auto* frame = m_free.front();
''')

# ---------------------------------------------------------------------------------------------------- command scheduler
CS = 'src/graphics/host_gpu/renderer/commandScheduler.cpp'
edit(CS, '''		const auto t0 = Common::FrameStats::NowNs();
		m_drained.wait(lock, [this, target] { return m_submitted >= target; });
''', '''		const auto t0 = Common::FrameStats::NowNs();
		// Track F, F20j3 (KYTY_DIAG_B32 W:asub_drain, item 574(g)(1)): the caller waits for the async submitter.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::ASubDrain, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::ASubmit), 0);
		}
		m_drained.wait(lock, [this, target] { return m_submitted >= target; });
		b32.EndSig(&m_drained);
''')

edit(CS, '''				std::unique_lock lock(m_mutex);
				m_available.wait(lock, [this] { return !m_queue.empty(); });
				record = std::move(m_queue.front());
''', '''				std::unique_lock lock(m_mutex);
				// Track F, F20j3 (KYTY_DIAG_B32 W:asub_idle, item 574(g)(1)): the async submitter waits for work.
				Common::DiagB32::Mark b32;
				if (Common::DiagB32::g_on && m_queue.empty()) [[unlikely]] {
					b32.BeginWReg(Common::DiagB32::Wait::ASubIdle, this, 0, 0);
				}
				m_available.wait(lock, [this] { return !m_queue.empty(); });
				b32.EndSig(&m_available);
				record = std::move(m_queue.front());
''')

edit(CS, '''	m_operation_available.wait(lock,
	                           [this] { return m_operation_state == OperationState::Closed; });
	lock.unlock();
	operation();
}

void CommandScheduler::DeferPriorityOperation(Common::UniqueFunction<void>&& operation) {
''', '''	// Track F, F20j3 (KYTY_DIAG_B32 W:ops_wait, item 574(g)(1)): the caller waits for the operations to close.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::OpsWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::POps), 0);
	}
	m_operation_available.wait(lock,
	                           [this] { return m_operation_state == OperationState::Closed; });
	b32.EndSig(&m_operation_available);
	lock.unlock();
	operation();
}

void CommandScheduler::DeferPriorityOperation(Common::UniqueFunction<void>&& operation) {
''')

edit(CS, '''	m_operation_available.wait(lock,
	                           [this] { return m_operation_state == OperationState::Closed; });
	lock.unlock();
	operation();
}

bool CommandScheduler::UnsubmittedPriorityOperation(uint64_t* tick, const void** site) {
''', '''	// Track F, F20j3 (KYTY_DIAG_B32 W:ops_wait, item 574(g)(1)): the caller waits for the operations to close.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::OpsWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::POps), 0);
	}
	m_operation_available.wait(lock,
	                           [this] { return m_operation_state == OperationState::Closed; });
	b32.EndSig(&m_operation_available);
	lock.unlock();
	operation();
}

bool CommandScheduler::UnsubmittedPriorityOperation(uint64_t* tick, const void** site) {
''')

edit(CS, '''void CommandScheduler::PriorityOperationsThread(std::stop_token stop) {
	while (!stop.stop_requested()) {
		PendingOperation operation;
		{
			std::unique_lock lock(m_operation_mutex);
			m_operation_available.wait(lock, [this, &stop] {
				return stop.stop_requested() || !m_priority_operations.empty();
			});
''', '''void CommandScheduler::PriorityOperationsThread(std::stop_token stop) {
	if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j3: the slot of the priority operations thread (peer POps)
		Common::DiagB32::RegisterRole("POps");
	}
	while (!stop.stop_requested()) {
		PendingOperation operation;
		{
			std::unique_lock lock(m_operation_mutex);
			// Track F, F20j3 (KYTY_DIAG_B32 W:ops_idle, item 574(g)(1)): the thread waits for a priority operation.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on && m_priority_operations.empty()) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::OpsIdle, this, 0, 0);
			}
			m_operation_available.wait(lock, [this, &stop] {
				return stop.stop_requested() || !m_priority_operations.empty();
			});
			b32.EndSig(&m_operation_available);
''')

edit(CS, '''	std::unique_lock lock(m_operation_mutex);
	m_operation_available.wait(
	    lock, [this] { return m_priority_operations.empty() && !m_priority_active; });
}
''', '''	std::unique_lock lock(m_operation_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:ops_wait, item 574(g)(1)): the caller waits for the priority operations.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::OpsWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::POps), 0);
	}
	m_operation_available.wait(
	    lock, [this] { return m_priority_operations.empty() && !m_priority_active; });
	b32.EndSig(&m_operation_available);
}
''')

edit(CS, '''	std::unique_lock lock(m_operation_mutex);
	m_operation_available.wait(lock, [this, tick] {
		const bool active_before_or_at = m_priority_active && m_priority_active_tick <= tick;
		const bool queued_before_or_at =
		    !m_priority_operations.empty() && m_priority_operations.front().tick <= tick;
		return !active_before_or_at && !queued_before_or_at;
	});
}
''', '''	std::unique_lock lock(m_operation_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:ops_wait, item 574(g)(1)): the caller waits for the priority operations <= tick.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::OpsWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::POps), tick);
	}
	m_operation_available.wait(lock, [this, tick] {
		const bool active_before_or_at = m_priority_active && m_priority_active_tick <= tick;
		const bool queued_before_or_at =
		    !m_priority_operations.empty() && m_priority_operations.front().tick <= tick;
		return !active_before_or_at && !queued_before_or_at;
	});
	b32.EndSig(&m_operation_available);
}
''')

# ---------------------------------------------------------------------------------------------------- command recorder
CR = 'src/graphics/host_gpu/renderer/commandRecorder.cpp'
edit(CR, '''				std::unique_lock lock(m_mutex);
				m_waiters.fetch_add(1, std::memory_order_seq_cst);
				m_progress.wait_for(lock, WaitSlice, [this, head, want] {
					const auto in_use = head - m_tail.load(std::memory_order_acquire);
					return m_capacity - in_use >= want;
				});
				m_waiters.fetch_sub(1, std::memory_order_seq_cst);
''', '''				std::unique_lock lock(m_mutex);
				m_waiters.fetch_add(1, std::memory_order_seq_cst);
				// Track F, F20j3 (KYTY_DIAG_B32 W:rec_wait, item 574(g)(1)): the producer waits for the record thread.
				Common::DiagB32::Mark b32;
				if (Common::DiagB32::g_on) [[unlikely]] {
					b32.BeginWReg(Common::DiagB32::Wait::RecWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Record), 0);
				}
				m_progress.wait_for(lock, WaitSlice, [this, head, want] {
					const auto in_use = head - m_tail.load(std::memory_order_acquire);
					return m_capacity - in_use >= want;
				});
				b32.EndSig(&m_progress);
				m_waiters.fetch_sub(1, std::memory_order_seq_cst);
''')

edit(CR, '''		m_waiters.fetch_add(1, std::memory_order_seq_cst);
		while (m_tail.load(std::memory_order_seq_cst) < target) {
			m_progress.wait_for(lock, WaitSlice);
		}
		m_waiters.fetch_sub(1, std::memory_order_seq_cst);
''', '''		m_waiters.fetch_add(1, std::memory_order_seq_cst);
		// Track F, F20j3 (KYTY_DIAG_B32 W:rec_wait, item 574(g)(1)): the drain waits for the record thread - one mark
		// over the loop of WaitSlice waits.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on && m_tail.load(std::memory_order_seq_cst) < target) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::RecWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Record), 0);
		}
		while (m_tail.load(std::memory_order_seq_cst) < target) {
			m_progress.wait_for(lock, WaitSlice);
		}
		b32.EndSig(&m_progress);
		m_waiters.fetch_sub(1, std::memory_order_seq_cst);
''')

edit(CR, '''				std::unique_lock lock(m_mutex);
				while (!m_stop.load(std::memory_order_acquire) &&
				       m_head.load(std::memory_order_seq_cst) == tail) {
					m_pending.wait_for(lock, SleepSlice);
				}
''', '''				std::unique_lock lock(m_mutex);
				// Track F, F20j3 (KYTY_DIAG_B32 W:rec_idle, item 574(g)(1)): the record thread waits for records; peer -
				// GuestGpu (the producer).
				Common::DiagB32::Mark b32;
				if (Common::DiagB32::g_on) [[unlikely]] {
					b32.BeginWReg(Common::DiagB32::Wait::RecIdle, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), 0);
				}
				while (!m_stop.load(std::memory_order_acquire) &&
				       m_head.load(std::memory_order_seq_cst) == tail) {
					m_pending.wait_for(lock, SleepSlice);
				}
				b32.EndSig(&m_pending);
''')

note_before(CR, 'm_pending.notify_all();', '&m_pending', 1)
note_before(CR, 'm_pending.notify_one();', '&m_pending', 1)
note_before(CR, 'm_progress.notify_all();', '&m_progress', 1)
note_before(CS, 'm_available.notify_one();', '&m_available', 2)
note_before(CS, 'm_drained.notify_all();', '&m_drained', 1)
note_before(CS, 'm_operation_available.notify_all();', '&m_operation_available', 3)
note_before(CS, 'm_operation_available.notify_one();', '&m_operation_available', 1)

# ---------------------------------------------------------------------------------------------------- pipeline cache
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
edit(PC, '''void PipelineCache::WaitForPendingPipelines() {
	std::unique_lock<std::mutex> lock(m_job_mutex);
	m_idle_cv.wait(lock, [this] { return m_jobs.empty() && m_jobs_active == 0; });
}
''', '''void PipelineCache::WaitForPendingPipelines() {
	std::unique_lock<std::mutex> lock(m_job_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:pipe_wait, item 574(g)(1)): the caller waits for the pipeline workers (no peer -
	// the workers are not registered).
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::PipeWait, this, 0, 0);
	}
	m_idle_cv.wait(lock, [this] { return m_jobs.empty() && m_jobs_active == 0; });
	b32.EndSig(&m_idle_cv);
}
''')

edit(PC, '''		{
			std::unique_lock<std::mutex> lock(m_job_mutex);
			m_ready_cv.wait_for(lock, std::chrono::microseconds(AsyncPipelineWaitUs()),
			                    [entry] { return entry->ready.load(std::memory_order_acquire); });
		}
''', '''		{
			std::unique_lock<std::mutex> lock(m_job_mutex);
			// Track F, F20j3 (KYTY_DIAG_B32 W:pipe_wait, item 574(g)(1)): the bounded wait for an async pipeline.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::PipeWait, entry, 0, AsyncPipelineWaitUs());
			}
			m_ready_cv.wait_for(lock, std::chrono::microseconds(AsyncPipelineWaitUs()),
			                    [entry] { return entry->ready.load(std::memory_order_acquire); });
			b32.EndSig(&m_ready_cv);
		}
''')

edit(PC, '''	{
		std::unique_lock<std::mutex> lock(m_job_mutex);
		m_ready_cv.wait(lock, [pending] { return pending->ready.load(std::memory_order_acquire); });
	}
''', '''	{
		std::unique_lock<std::mutex> lock(m_job_mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:pipe_wait, item 574(g)(1)): a dispatch waits for its compute pipeline.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::PipeWait, pending, 0, 0);
		}
		m_ready_cv.wait(lock, [pending] { return pending->ready.load(std::memory_order_acquire); });
		b32.EndSig(&m_ready_cv);
	}
''')
note_before(PC, 'm_ready_cv.notify_all();', '&m_ready_cv', 4)
note_before(PC, 'm_idle_cv.notify_all();', '&m_idle_cv', 1)

# ---------------------------------------------------------------------------------------------------- parallel copy, page manager, vma
PCO = 'src/common/parallelCopy.cpp'
edit(PCO, '''		Work();
		std::unique_lock lock(m_mutex);
		m_finished.wait(lock, [&] { return m_pending.load(std::memory_order_acquire) == 0; });
	}
''', '''		Work();
		std::unique_lock lock(m_mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:pcopy, item 574(g)(1)): the caller waits for the copy workers (not registered).
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::PCopy, this, 0, 0);
		}
		m_finished.wait(lock, [&] { return m_pending.load(std::memory_order_acquire) == 0; });
		b32.EndSig(&m_finished);
	}
''')
note_before(PCO, 'm_finished.notify_all();', '&m_finished', 1)

PM = 'src/graphics/host_gpu/pageManager.cpp'
edit(PM, '''		{
			std::unique_lock lock(queue_mutex);
			drain_cv.wait(lock, [this] { return inflight.load(std::memory_order_acquire) == 0; });
		}
''', '''		{
			std::unique_lock lock(queue_mutex);
			// Track F, F20j3 (KYTY_DIAG_B32 W:pm_drain, item 574(g)(1)): the caller waits for the protect workers.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::PmDrain, this, 0, 0);
			}
			drain_cv.wait(lock, [this] { return inflight.load(std::memory_order_acquire) == 0; });
			b32.EndSig(&drain_cv);
		}
''')
note_before(PM, 'drain_cv.notify_all();', '&drain_cv', 1)

edit(PM, '''	explicit SpinGuard(std::atomic_flag& lock): m_lock(lock) {
		while (m_lock.test_and_set(std::memory_order_acquire)) {
			std::atomic_signal_fence(std::memory_order_seq_cst);
		}
	}
''', '''	explicit SpinGuard(std::atomic_flag& lock): m_lock(lock) {
		// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): a contended spin of a registered thread (no owner field).
		Common::DiagB32::Mark b32;
		while (m_lock.test_and_set(std::memory_order_acquire)) {
			if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::Spin, &lock, 0, 0);
			}
			std::atomic_signal_fence(std::memory_order_seq_cst);
		}
		b32.End(0, false);
	}
''')

edit(PM, '''		namespace FS  = Common::FrameStats;
		const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
		uint32_t   spins = 0;
		do {
''', '''		namespace FS  = Common::FrameStats;
		const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
		uint32_t   spins = 0;
		// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): the apply lock is held across VirtualProtect.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Spin, &lock, 0, 0);
		}
		do {
''')
edit(PM, '''		} while (m_lock->test_and_set(std::memory_order_acquire));
		if (t0 != 0) {
			const auto ns = FS::NowNs() - t0;
			m_wait_ns     = ns;
''', '''		} while (m_lock->test_and_set(std::memory_order_acquire));
		b32.End(0, false);
		if (t0 != 0) {
			const auto ns = FS::NowNs() - t0;
			m_wait_ns     = ns;
''')

VM = 'src/graphics/host_gpu/vma.cpp'
edit(VM, '''	void Flush() {
		std::unique_lock lock(m_mutex);
		m_drained.wait(lock, [this] { return m_queue.empty() && !m_running; });
	}
''', '''	void Flush() {
		std::unique_lock lock(m_mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:vma_flush, item 574(g)(1)): the caller waits for the VMA worker (not registered).
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::VmaFlush, this, 0, 0);
		}
		m_drained.wait(lock, [this] { return m_queue.empty() && !m_running; });
		b32.EndSig(&m_drained);
	}
''')
note_before(VM, 'm_drained.notify_all();', '&m_drained', 1)

# ---------------------------------------------------------------------------------------------------- region tracking spin lock
RM = 'src/graphics/host_gpu/regionManager.h'
edit(RM, '''			while (m_lock.test_and_set(std::memory_order_acquire)) {
				if (m_owner.load(std::memory_order_relaxed) == thread) {
					EXIT("recursive region tracking lock while contended\\n");
				}
''', '''			// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): a contended spin; peer - the owner's slot.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::Spin, this,
				              Common::DiagB32::SlotOfOsTid(m_owner.load(std::memory_order_relaxed)), 0);
			}
			while (m_lock.test_and_set(std::memory_order_acquire)) {
				if (m_owner.load(std::memory_order_relaxed) == thread) {
					EXIT("recursive region tracking lock while contended\\n");
				}
''')
edit(RM, '''					std::atomic_signal_fence(std::memory_order_seq_cst);
				}
			}
			if (t0 != 0) {
''', '''					std::atomic_signal_fence(std::memory_order_seq_cst);
				}
			}
			b32.EndWithPeer(false);
			if (t0 != 0) {
''')

# ---------------------------------------------------------------------------------------------------- recording, main thread
SC = 'src/graphics/presentation/window/screenshot.cpp'
edit(SC, '''		std::unique_lock lock(m_rec_mutex);
		// Backpressure: the encoder keeps up at 60 fps; a deep backlog means it does not.
		m_rec_cv.wait(lock, [&] { return m_rec_queue.size() < 8; });
''', '''		std::unique_lock lock(m_rec_mutex);
		// Backpressure: the encoder keeps up at 60 fps; a deep backlog means it does not.
		// Track F, F20j3 (KYTY_DIAG_B32 W:rec_queue, item 574(g)(1)): KYTY_REC only; the encoder thread is not registered.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on && m_rec_queue.size() >= 8) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::RecQueue, this, 0, 0);
		}
		m_rec_cv.wait(lock, [&] { return m_rec_queue.size() < 8; });
		b32.EndSig(&m_rec_cv);
''')
note_before(SC, 'm_rec_cv.notify_all();', '&m_rec_cv', 3)

W = 'src/graphics/presentation/window/window.cpp'
edit(W, '''	Common::LockGuard lock(main_task_mutex);
	while (main_tasks_run < ticket) {
		main_task_done.Wait(&main_task_mutex);
	}
}
''', '''	Common::LockGuard lock(main_task_mutex);
	// Track F, F20j3 (KYTY_DIAG_B32 W:main_task, item 574(g)(1)): the caller waits for the main thread to run its task.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && main_tasks_run < ticket) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::MainTask, &main_task_done, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Main), 0);
	}
	while (main_tasks_run < ticket) {
		main_task_done.Wait(&main_task_mutex);
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(main_task_done.B32Waker(b32.SinceNs()), false);
	}
}
''')

edit(W, '''		if (!HostInputWaitEvent(&loop.event)) {
			continue;
		}
		ProcessEvent(timer.GetTimeS());
''', '''		// Track F, F20j3 (KYTY_DIAG_B32 W:main_idle, item 574(g)(1)): the main thread waits for an SDL event.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::MainIdle, &loop, 0, 0);
		}
		const bool b32_event = HostInputWaitEvent(&loop.event);
		b32.End(0, false);
		if (!b32_event) {
			continue;
		}
		ProcessEvent(timer.GetTimeS());
''')

# ---------------------------------------------------------------------------------------------------- kernel: event flag / sema spins, rwlock, once, join, wait on address
EF = 'src/kernel/eventFlag.cpp'
SPIN_BODY = '''		m_mutex.Unlock();
		Common::Thread::SleepMicro(10);
		m_mutex.Lock();
	}
'''


def spin_edit(path, head, cond):
    old = head + '\t while (' + cond + ') {\n' + SPIN_BODY
    old = old.replace('\t while', '\twhile')
    new = (head + '\t// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): a 10 us sleep loop of the emulator object.\n'
           '\tCommon::DiagB32::Mark b32;\n'
           '\tif (Common::DiagB32::g_on && (' + cond + ')) [[unlikely]] {\n'
           '\t\tb32.BeginWReg(Common::DiagB32::Wait::Spin, this, 0, 0);\n'
           '\t}\n'
           '\twhile (' + cond + ') {\n' + SPIN_BODY + '\tb32.End(0, false);\n')
    edit(path, old, new)


spin_edit(EF, 'KernelEventFlagPrivate::~KernelEventFlagPrivate() {\n\tCommon::LockGuard lock(m_mutex);\n\n', 'm_status != Status::Set')
edit(EF, '''	m_status = Status::Deleted;

	m_cond_var.SignalAll();

	while (m_waiting_threads > 0) {
		m_mutex.Unlock();
		Common::Thread::SleepMicro(10);
		m_mutex.Lock();
	}
}
''', '''	m_status = Status::Deleted;

	m_cond_var.SignalAll();

	// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): a 10 us sleep loop of the emulator object.
	Common::DiagB32::Mark b32_w;
	if (Common::DiagB32::g_on && m_waiting_threads > 0) [[unlikely]] {
		b32_w.BeginWReg(Common::DiagB32::Wait::Spin, this, 0, 0);
	}
	while (m_waiting_threads > 0) {
		m_mutex.Unlock();
		Common::Thread::SleepMicro(10);
		m_mutex.Lock();
	}
	b32_w.End(0, false);
}
''')
spin_edit(EF, 'void KernelEventFlagPrivate::Set(uint64_t bits) {\n\tCommon::LockGuard lock(m_mutex);\n\n\tEXIT_NOT_IMPLEMENTED(m_status == Status::Deleted);\n\n', 'm_status != Status::Set')
spin_edit(EF, 'void KernelEventFlagPrivate::Clear(uint64_t bits) {\n\tCommon::LockGuard lock(m_mutex);\n\n\tEXIT_NOT_IMPLEMENTED(m_status == Status::Deleted);\n\n', 'm_status != Status::Set')
spin_edit(EF, 'void KernelEventFlagPrivate::Cancel(uint64_t bits, int* num_waiting_threads) {\n\tCommon::LockGuard lock(m_mutex);\n\n\tEXIT_NOT_IMPLEMENTED(m_status == Status::Deleted);\n\n', 'm_status != Status::Set')
edit(EF, '''	m_status = Status::Canceled;
	m_bits   = bits;

	m_cond_var.SignalAll();

	while (m_waiting_threads > 0) {
		m_mutex.Unlock();
		Common::Thread::SleepMicro(10);
		m_mutex.Lock();
	}
''', '''	m_status = Status::Canceled;
	m_bits   = bits;

	m_cond_var.SignalAll();

	// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): a 10 us sleep loop of the emulator object.
	Common::DiagB32::Mark b32_w;
	if (Common::DiagB32::g_on && m_waiting_threads > 0) [[unlikely]] {
		b32_w.BeginWReg(Common::DiagB32::Wait::Spin, this, 0, 0);
	}
	while (m_waiting_threads > 0) {
		m_mutex.Unlock();
		Common::Thread::SleepMicro(10);
		m_mutex.Lock();
	}
	b32_w.End(0, false);
''')

SE = 'src/kernel/semaphore.cpp'
spin_edit(SE, 'KernelSemaPrivate::~KernelSemaPrivate() {\n\tCommon::LockGuard lock(m_mutex);\n\n', 'm_status != Status::Set')
edit(SE, '''	m_cond_var.SignalAll();

	while (!m_waiting_threads.empty()) {
		m_mutex.Unlock();
		Common::Thread::SleepMicro(10);
		m_mutex.Lock();
	}
}
''', '''	m_cond_var.SignalAll();

	// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): a 10 us sleep loop of the emulator object.
	Common::DiagB32::Mark b32_w;
	if (Common::DiagB32::g_on && !m_waiting_threads.empty()) [[unlikely]] {
		b32_w.BeginWReg(Common::DiagB32::Wait::Spin, this, 0, 0);
	}
	while (!m_waiting_threads.empty()) {
		m_mutex.Unlock();
		Common::Thread::SleepMicro(10);
		m_mutex.Lock();
	}
	b32_w.End(0, false);
}
''')

PT = 'src/kernel/pthread.cpp'
edit(PT, '''		if (timeout_us != nullptr) {
			if (*timeout_us > 0) {
				mutex->cv.wait_for(lock, std::chrono::microseconds(*timeout_us));
			}
			return ETIMEDOUT;
		}
		return EDEADLK;
''', '''		if (timeout_us != nullptr) {
			if (*timeout_us > 0) {
				// Track F, F20j3 (KYTY_DIAG_B32 W:mutex, item 574(g)(1)): a timed lock of an owned error-check mutex
				// sleeps its timeout (no peer: the owner is this thread).
				Common::DiagB32::Mark b32;
				if (Common::DiagB32::g_on) [[unlikely]] {
					b32.BeginWReg(Common::DiagB32::Wait::Mutex, mutex, 0, static_cast<uint64_t>(*timeout_us));
				}
				mutex->cv.wait_for(lock, std::chrono::microseconds(*timeout_us));
				b32.End(0, true);
			}
			return ETIMEDOUT;
		}
		return EDEADLK;
''')

edit(PT, '''	bool writer_wait_registered = false;

	for (;;) {
		{
			std::unique_lock lock(rwlock->m);
''', '''	bool writer_wait_registered = false;
	// Track F, F20j3 (KYTY_DIAG_B32 W:rwlock, item 574(g)(1)): from the first blocking pass to the return; peer - the
	// writer's slot (0 if readers hold it).
	Common::DiagB32::Mark b32;

	for (;;) {
		{
			std::unique_lock lock(rwlock->m);
''')

edit(PT, '''			if (has_timeout) {
				const auto now = std::chrono::steady_clock::now();
				if (*timeout_us == 0 || now >= deadline) {
					unregister_writer_wait();
					return KERNEL_ERROR_ETIMEDOUT;
				}

				const auto remaining = deadline - now;
				const auto poll = (remaining < std::chrono::microseconds(SIGNAL_APC_POLL_MICROS)
''', '''			if (Common::DiagB32::g_on && !b32.Active() && !(has_timeout && *timeout_us == 0)) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::Rwlock, rwlock,
				              rwlock->writer != nullptr ? rwlock->writer->b32_slot1.load(std::memory_order_relaxed) : 0,
				              has_timeout ? static_cast<uint64_t>(*timeout_us) : 0);
			}
			if (has_timeout) {
				const auto now = std::chrono::steady_clock::now();
				if (*timeout_us == 0 || now >= deadline) {
					unregister_writer_wait();
					return KERNEL_ERROR_ETIMEDOUT;
				}

				const auto remaining = deadline - now;
				const auto poll = (remaining < std::chrono::microseconds(SIGNAL_APC_POLL_MICROS)
''')

edit(PT, '''				case PTHREAD_ONCE_WAIT:
					once->state = PTHREAD_ONCE_WAIT;
					while (once->state == PTHREAD_ONCE_WAIT) {
''', '''				case PTHREAD_ONCE_WAIT:
					once->state = PTHREAD_ONCE_WAIT;
					// Track F, F20j3 (KYTY_DIAG_B32 W:once, item 574(g)(1)): another thread runs the init routine.
					if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {
						b32.BeginWReg(Common::DiagB32::Wait::Once, once, 0, 0);
					}
					while (once->state == PTHREAD_ONCE_WAIT) {
''')
edit(PT, '''	auto* once = static_cast<PthreadOnce*>(once_control);

	{
		std::unique_lock lock(g_pthread_once_mutex);
''', '''	auto* once = static_cast<PthreadOnce*>(once_control);
	Common::DiagB32::Mark b32; // Track F, F20j3 (W:once below; ended by the destructor on every return)

	{
		std::unique_lock lock(g_pthread_once_mutex);
''')
note_before(PT, 'g_pthread_once_cv.notify_all();', '&g_pthread_once_cv', 1)
edit(PT, '''run_init:
	init_routine();
''', '''run_init:
	b32.End(0, false); // Track F, F20j3: this thread runs the routine itself - not a wait
	init_routine();
''')

edit(PT, '''	int result = pthread_join(thread->p, value);

	if (PRINT_NAME_ENABLED) {
''', '''	// Track F, F20j3 (KYTY_DIAG_B32 W:join, item 574(g)(1)): peer - the joined thread's slot.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Join, thread, thread->b32_slot1.load(std::memory_order_relaxed), 0);
	}
	int result = pthread_join(thread->p, value);
	b32.End(0, false);

	if (PRINT_NAME_ENABLED) {
''')

SO = 'src/kernel/syncOnAddress.cpp'
edit(SO, '''	PortableWaiter waiter;
	auto           entry      = RegisterPortableWaiter(address, &waiter);
	bool           first_wait = true;
	int            result     = OK;

	while (ReadWord(address) == expected && !waiter.wake_requested) {
''', '''	PortableWaiter waiter;
	auto           entry      = RegisterPortableWaiter(address, &waiter);
	bool           first_wait = true;
	int            result     = OK;
	// Track F, F20j3 (KYTY_DIAG_B32 W:addr, item 574(g)(1)): the guest wait on an address; waker - the last signaller of
	// the waiter's condition (WakePortable).
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && ReadWord(address) == expected && !waiter.wake_requested) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Addr, const_cast<T*>(address), 0, 0);
	}

	while (ReadWord(address) == expected && !waiter.wake_requested) {
''')
edit(SO, '''		first_wait = false;
	}

	UnregisterPortableWaiter(address, entry, &waiter);
	return result;
''', '''		first_wait = false;
	}
	if (b32.Active()) [[unlikely]] {
		b32.End(waiter.condition.B32Waker(b32.SinceNs()), result == KERNEL_ERROR_ETIMEDOUT);
	}

	UnregisterPortableWaiter(address, entry, &waiter);
	return result;
''')

# ---------------------------------------------------------------------------------------------------- libs (guest HLE)
LK = 'src/libs/libKernel.cpp'
edit(LK, '''static bool FiberWaitAndEnterRunning(FiberObject* fiber, uint32_t* observed_state) {
	const auto start = std::chrono::steady_clock::now();
	uint32_t   spin  = 0;
	auto&      state = fiber->state;
	auto       ref   = std::atomic_ref<uint32_t>(state);
''', '''static bool FiberWaitAndEnterRunning(FiberObject* fiber, uint32_t* observed_state) {
	const auto start = std::chrono::steady_clock::now();
	uint32_t   spin  = 0;
	auto&      state = fiber->state;
	auto       ref   = std::atomic_ref<uint32_t>(state);
	// Track F, F20j3 (KYTY_DIAG_B32 W:fiber, item 574(g)(1)): the bounded (5 ms) wait for a running fiber; ended by the
	// destructor on every return.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Fiber, fiber, 0, 5000);
	}
''')
edit(LK, '''	uint32_t waited  = 0;
	auto     current = g_kernel_aio_state[id].load(std::memory_order_acquire);
	while (current == KERNEL_AIO_STATE_PROCESSING) {
''', '''	uint32_t waited  = 0;
	auto     current = g_kernel_aio_state[id].load(std::memory_order_acquire);
	// Track F, F20j3 (KYTY_DIAG_B32 W:aio, item 574(g)(1)): a 10 us sleep loop until the request is done.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on && current == KERNEL_AIO_STATE_PROCESSING) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Aio, &g_kernel_aio_state[id], 0, usec != nullptr ? *usec : 0);
	}
	while (current == KERNEL_AIO_STATE_PROCESSING) {
''')

LC = 'src/libs/libC.cpp'
edit(LC, '''	{
		std::unique_lock lock(g_execute_once_mutex);
		while (*flag == once_running) {
''', '''	{
		std::unique_lock lock(g_execute_once_mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:once, item 574(g)(1)): another thread runs the routine.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on && *flag == once_running) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Once, flag, 0, 0);
		}
		while (*flag == once_running) {
''')
note_before(LC, 'g_execute_once_cv.notify_all();', '&g_execute_once_cv', 1)

AV = 'src/libs/avPlayer.cpp'
edit(AV, '''		std::unique_lock lock(mutex);
		available.wait(lock, [&] {
			return stop || bytes + size <= capacity || (queue.empty() && bytes == 0);
		});
''', '''		std::unique_lock lock(mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:av, item 574(g)(1)): the demuxer waits for queue room.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Av, this, 0, 0);
		}
		available.wait(lock, [&] {
			return stop || bytes + size <= capacity || (queue.empty() && bytes == 0);
		});
		b32.EndSig(&available);
''')
edit(AV, '''		std::unique_lock lock(mutex);
		available.wait(lock, [&] { return stop || finished || !queue.empty(); });
''', '''		std::unique_lock lock(mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:av, item 574(g)(1)): a decoder waits for a packet.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Av, this, 0, 0);
		}
		available.wait(lock, [&] { return stop || finished || !queue.empty(); });
		b32.EndSig(&available);
''')
edit(AV, '''		std::unique_lock lock(mutex);
		available.wait(lock, [&] { return stop || !queue.empty(); });
''', '''		std::unique_lock lock(mutex);
		// Track F, F20j3 (KYTY_DIAG_B32 W:av, item 574(g)(1)): a consumer waits for a frame.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Av, this, 0, 0);
		}
		available.wait(lock, [&] { return stop || !queue.empty(); });
		b32.EndSig(&available);
''')
note_before(AV, 'available.notify_all();', '&available', 8)
edit_n(AV, '''	void Notify() { available.notify_all(); }
''', '''	void Notify() {
		Common::DiagB32::NoteSignal(&available); // Track F, F20j3
		available.notify_all();
	}
''', 2)

AU = 'src/libs/audio.cpp'
edit(AU, '''		const auto wait_start      = LibKernel::KernelGetProcessTime();
		while (SDL_GetQueuedAudioSize(port->audio_device) > min_queued_size) {
''', '''		const auto wait_start      = LibKernel::KernelGetProcessTime();
		// Track F, F20j3 (KYTY_DIAG_B32 W:audio, item 574(g)(1)): a blocking output waits for the SDL queue to drain.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Audio, port, 0, 200000);
		}
		while (SDL_GetQueuedAudioSize(port->audio_device) > min_queued_size) {
''')
edit(AU, '''				SDL_ClearQueuedAudio(port->audio_device);
				break;
			}
			Common::Thread::SleepMicro(1000);
		}
	}
''', '''				SDL_ClearQueuedAudio(port->audio_device);
				break;
			}
			Common::Thread::SleepMicro(1000);
		}
		b32.End(0, false);
	}
''')
edit(AU, '''	if (blocking && max_wait_time != 0 && !any_port_has_device) {
		Common::Thread::SleepMicro(max_wait_time);
	}
''', '''	if (blocking && max_wait_time != 0 && !any_port_has_device) {
		// Track F, F20j3 (KYTY_DIAG_B32 W:audio, item 574(g)(1)): the output pacing sleep without a device.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Audio, this, 0, max_wait_time);
		}
		Common::Thread::SleepMicro(max_wait_time);
		b32.End(0, false);
	}
''')
edit(AU, '''	Common::Thread::SleepMicro(wait_time);
	uint32_t frames = snapshot.samples_num;
	bool     failed = false;
	if (dest != nullptr) {
		if (snapshot.audio_device != 0) {
			while (!snapshot.asynchronous &&
			       SDL_GetQueuedAudioSize(snapshot.audio_device) <
			           frames * snapshot.bytes_per_frame &&
			       SDL_GetAudioDeviceStatus(snapshot.audio_device) == SDL_AUDIO_PLAYING) {
				Common::Thread::SleepMicro(1000);
			}
''', '''	// Track F, F20j3 (KYTY_DIAG_B32 W:audio, item 574(g)(1)): the input pacing sleep.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Audio, this, 0, wait_time);
	}
	Common::Thread::SleepMicro(wait_time);
	b32.End(0, false);
	uint32_t frames = snapshot.samples_num;
	bool     failed = false;
	if (dest != nullptr) {
		if (snapshot.audio_device != 0) {
			// Track F, F20j3 (KYTY_DIAG_B32 W:audio): the wait for captured data.
			Common::DiagB32::Mark b32_q;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32_q.BeginWReg(Common::DiagB32::Wait::Audio, this, 0, 0);
			}
			while (!snapshot.asynchronous &&
			       SDL_GetQueuedAudioSize(snapshot.audio_device) <
			           frames * snapshot.bytes_per_frame &&
			       SDL_GetAudioDeviceStatus(snapshot.audio_device) == SDL_AUDIO_PLAYING) {
				Common::Thread::SleepMicro(1000);
			}
			b32_q.End(0, false);
''')
edit(AU, '''		if (blocking == 1) {
			auto wait_time = port->data_delay / 8;
			while (first_data->state != Audio3dData::State::Empty) {
				Common::Thread::SleepMicro(wait_time);
			}
		}
''', '''		if (blocking == 1) {
			auto wait_time = port->data_delay / 8;
			// Track F, F20j3 (KYTY_DIAG_B32 W:audio, item 574(g)(1)): a blocking push waits for the playback thread.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::Audio, port, 0, 0);
			}
			while (first_data->state != Audio3dData::State::Empty) {
				Common::Thread::SleepMicro(wait_time);
			}
			b32.End(0, false);
		}
''')

A2 = 'src/libs/libAudio2.cpp'
edit(A2, '''	for (;;) {
		// Only a synchronous submission carrying PCM to a real device can rely on the SDL queue for
''', '''	// Track F, F20j3 (KYTY_DIAG_B32 W:audio, item 574(g)(1)): from the first full-queue pass to the return (destructor).
	Common::DiagB32::Mark b32;
	for (;;) {
		// Only a synchronous submission carrying PCM to a real device can rely on the SDL queue for
''')
edit(A2, '''		if (blocking == 0) {
			return AUDIO_OUT2_ERROR_NOT_READY;
		}

		Common::Thread::SleepMicro(sleep_micros);
	}
''', '''		if (blocking == 0) {
			return AUDIO_OUT2_ERROR_NOT_READY;
		}

		if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Audio, &g_audioout2_context_mutex, 0, 0);
		}
		Common::Thread::SleepMicro(sleep_micros);
	}
''')
edit(A2, '''				g_audioout2_context_mutex.Unlock();
				audioout2_queue_context_audio(ctx, blocking != 0);
				return OK;
''', '''				g_audioout2_context_mutex.Unlock();
				b32.End(0, false); // Track F, F20j3: the wait ends; the queueing below is not a wait
				audioout2_queue_context_audio(ctx, blocking != 0);
				return OK;
''')

UL = 'src/libs/libUlt.cpp'
edit(UL, '''	state->waiters++;
	state->available.wait(lock, [&] { return !state->alive || state->resources >= num_resource; });
	state->waiters--;
''', '''	state->waiters++;
	// Track F, F20j3 (KYTY_DIAG_B32 W:ult, item 574(g)(1)): the ULT semaphore wait.
	Common::DiagB32::Mark b32;
	if (Common::DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(Common::DiagB32::Wait::Ult, state.get(), 0, 0);
	}
	state->available.wait(lock, [&] { return !state->alive || state->resources >= num_resource; });
	b32.EndSig(&state->available);
	state->waiters--;
''')
note_before(UL, 'state->available.notify_all();', '&state->available', 2)

NW = 'src/libs/network.cpp'
edit(NW, '''			if (timeout < 0) {
				g_epoll_changed.wait(lock, ready);
			} else {
				g_epoll_changed.wait_for(lock, std::chrono::microseconds(timeout), ready);
			}
''', '''			// Track F, F20j3 (KYTY_DIAG_B32 W:net, item 574(g)(1)): epoll wait without registrations.
			Common::DiagB32::Mark b32;
			if (Common::DiagB32::g_on) [[unlikely]] {
				b32.BeginWReg(Common::DiagB32::Wait::Net, slot, 0, timeout < 0 ? 0 : static_cast<uint64_t>(timeout));
			}
			if (timeout < 0) {
				g_epoll_changed.wait(lock, ready);
			} else {
				g_epoll_changed.wait_for(lock, std::chrono::microseconds(timeout), ready);
			}
			b32.EndSig(&g_epoll_changed);
''')
note_before(NW, 'g_epoll_changed.notify_all();', '&g_epoll_changed', 3)
edit(NW, '''	if (descriptors.empty()) {
		Sleep(host_timeout_ptr == nullptr ? INFINITE :
		      static_cast<DWORD>(host_timeout.tv_sec * 1000 + host_timeout.tv_usec / 1000));
	} else
''', '''	if (descriptors.empty()) {
		// Track F, F20j3 (KYTY_DIAG_B32 W:net, item 574(g)(1)): select without descriptors is a sleep.
		Common::DiagB32::Mark b32;
		if (Common::DiagB32::g_on) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Net, nullptr, 0, 0);
		}
		Sleep(host_timeout_ptr == nullptr ? INFINITE :
		      static_cast<DWORD>(host_timeout.tv_sec * 1000 + host_timeout.tv_usec / 1000));
		b32.End(0, false);
	} else
''')

# ---------------------------------------------------------------------------------------------------- Common::Thread start / join
TC2 = 'src/common/threads.cpp'
edit(TC2, '''Thread::Thread(thread_func_t func, void* arg)
    : m_thread(std::make_unique<ThreadPrivate>(func, arg)) {
	while (!m_thread->started) {
		Common::Thread::SleepMicro(1000);
	}
}
''', '''Thread::Thread(thread_func_t func, void* arg)
    : m_thread(std::make_unique<ThreadPrivate>(func, arg)) {
	// Track F, F20j3 (KYTY_DIAG_B32 W:spin, item 574(g)(1)): the creator waits for the new thread to start.
	DiagB32::Mark b32;
	if (DiagB32::g_on && !m_thread->started) [[unlikely]] {
		b32.BeginWReg(DiagB32::Wait::Spin, this, 0, 0);
	}
	while (!m_thread->started) {
		Common::Thread::SleepMicro(1000);
	}
	b32.End(0, false);
}
''')
edit(TC2, '''	EXIT_IF(m_thread->finished || m_thread->auto_delete);

	m_thread->m_thread.join();

	m_thread->finished = true;
''', '''	EXIT_IF(m_thread->finished || m_thread->auto_delete);

	// Track F, F20j3 (KYTY_DIAG_B32 W:join, item 574(g)(1)).
	DiagB32::Mark b32;
	if (DiagB32::g_on) [[unlikely]] {
		b32.BeginWReg(DiagB32::Wait::Join, this, 0, 0);
	}
	m_thread->m_thread.join();
	b32.End(0, false);

	m_thread->finished = true;
''')
