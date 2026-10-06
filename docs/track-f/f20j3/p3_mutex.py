# F20j3 (HPP-646): part 3 of patch_f20j3.py - std mutexes on the in-scope paths become Common::DiagB32::TrackedMutex
# (item 574(g)(1): the contended acquisition is marked W:emu_mutex with the last owner as peer). The declaration line is
# found by a whole-line regex (exactly one in the file); the std type is replaced, the rest of the line is kept.
# Exceptions (cv mutexes, guest-visible layouts, out-of-scope threads, knobs, startup / shutdown, the instrument itself)
# - the table of waits_f20j3.py.

WRAP = [
    ('src/common/logging/log.cpp', 'g_logger_mutex', None),
    ('src/common/parallelCopy.cpp', 'm_signal_mutex', None),
    ('src/graphics/guest_gpu/graphicsRun.cpp', 'g_baton_mutex', None),
    ('src/graphics/host_gpu/graphicContext.h', 'm_format_properties_mutex', None),
    ('src/graphics/host_gpu/graphicContext.h', 'm_image_format_properties_mutex', None),
    ('src/graphics/host_gpu/memoryTracker.h', 'm_region_mutex', None),
    ('src/graphics/host_gpu/pageManager.cpp', 'region_mutex', None),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.h', 'm_pending_host_reads_mutex', None),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.h', 'm_streamed_mutex', None),
    ('src/graphics/host_gpu/renderer/cache/hostImport.h', 'm_mutex', None),
    ('src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'seen_mutex', None),
    ('src/graphics/host_gpu/renderer/cache/textureCache.cpp', 'g_pend_mutex', None),
    ('src/graphics/host_gpu/renderer/commandScheduler.cpp', 'mutex', 2),
    ('src/graphics/host_gpu/renderer/commandScheduler.h', 'm_timestamp_mutex', None),
    ('src/graphics/host_gpu/renderer/gpuTimeProfiler.h', 'm_mutex', None),
    ('src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'g_gds_keys_mutex', None),
    ('src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'm', None),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'mutex', 2),
    ('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ahead_queue_mutex', None),
    ('src/graphics/host_gpu/renderer/pipeline/shaders.cpp', 'mutex', None),
    ('src/graphics/host_gpu/renderer/renderContext.h', 'm_mapped_ranges_mutex', None),
    ('src/graphics/host_gpu/vma.cpp', 'g_recycle_mutex', None),
    ('src/graphics/presentation/systemOverlay.cpp', 'g_visibility_mutex', None),
    ('src/graphics/presentation/systemOverlay.cpp', 'g_input_mutex', None),
    ('src/kernel/fileSystem.cpp', 'g_stream_mutex', None),
    ('src/kernel/memory.cpp', 'g_memory_operation_mutex', None),
    ('src/kernel/memoryAddressSpace.inc', 'm_mutex', 2),
    ('src/kernel/pthread.cpp', 'g_pthread_keys_mutex', None),
    ('src/kernel/pthread.cpp', 'mutex', None),  # TimeFreezeState (host, static)
    ('src/kernel/syncOnAddress.cpp', 'mutex', None),
    ('src/libs/agc.cpp', 'g_register_defaults_mutex', None),
    ('src/libs/agc.cpp', 'g_workload_stream_mutex', None),
    ('src/libs/ajm.cpp', 'g_ajm_instances_mutex', None),
    ('src/libs/audio.cpp', 'g_frozen_devices_mutex', None),
    ('src/libs/audio.cpp', 'g_sdl_audio_mutex', None),
    ('src/libs/avPlayer.cpp', 'lifecycle_mutex', None),
    ('src/libs/avPlayer.cpp', 'mutex', [(2, None)]),
    ('src/libs/controller.cpp', 'm_mutex', [(1, None)]),
    ('src/libs/dialog.cpp', 'g_error_mutex', None),
    ('src/libs/ime.cpp', 'g_mutex', None),
    ('src/libs/libAmpr.cpp', 'g_mutex', None),
    ('src/libs/libAmpr.cpp', 'g_command_buffer_mutex', None),
    ('src/libs/libAmpr.cpp', 'g_amm_auto_pool_mutex', None),
    ('src/libs/libFont.cpp', 'g_glyph_mutex', None),
    ('src/libs/libFont.cpp', 'g_writing_mutex', None),
    ('src/libs/libHmd2.cpp', 'g_reprojection_mutex', None),
    ('src/libs/libJson2.cpp', 'g_object_snapshot_mutex', None),
    ('src/libs/libKernel.cpp', 'g_fiber_owner_mutex', None),
    ('src/libs/libNet.cpp', 'g_np_auth_request_mutex', None),
    ('src/libs/libUlt.cpp', 'mutex', [(0, 'Ult'), (2, None)]),
    ('src/libs/libUlt.cpp', 'g_ult_mutex', None),
    ('src/libs/libVideoDec2.cpp', 'g_decoder_mutex', None),
    ('src/libs/network.cpp', 'g_np_request_mutex', None),
    ('src/libs/videoDec2Decoder.cpp', 'g_picture_mutex', None),
    ('src/libs/videoDec2Decoder.cpp', 'm_mutex', None),
]

for path, name, mode in WRAP:
    wrap_mutex(path, name, mode)
    if not path.endswith('.inc'):  # memoryAddressSpace.inc is included by memory.cpp (which gets the include)
        add_include(path)

# Lock sites that name the std type explicitly: the template argument goes (deduced - TrackedMutex for a wrapped mutex).
ctad('src/graphics/guest_gpu/graphicsRun.cpp', 'g_baton_mutex', 2)
ctad('src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 'g_gds_keys_mutex', 2)
ctad('src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ahead_queue_mutex', 1)
ctad('src/kernel/memory.cpp', 'g_memory_operation_mutex', 33)
ctad('src/kernel/pthread.cpp', 'mutex', 8)
ctad('src/libs/audio.cpp', 'g_frozen_devices_mutex', 3)
ctad('src/libs/audio.cpp', 'g_sdl_audio_mutex', 1)
ctad('src/libs/libJson2.cpp', 'g_object_snapshot_mutex', 2)

# dialog.cpp passes the lock of g_error_mutex by reference: the parameter type follows the wrapped type.
edit('src/libs/dialog.cpp', '''static void SetStatus(int status, std::unique_lock<std::mutex>& lock) {
''', '''static void SetStatus(int status, std::unique_lock<Common::DiagB32::TrackedMutex<std::mutex>>& lock) {
''')

# RecordersMutex returns the mutex by reference: the return type follows the wrapped type.
CR3 = 'src/graphics/host_gpu/renderer/commandRecorder.cpp'
edit(CR3, '''std::mutex&                     RecordersMutex() {
	static std::mutex mutex;
	return mutex;
}
''', '''// Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, item 574(g)(1)): the recorder list mutex is tracked.
Common::DiagB32::TrackedMutex<std::mutex>& RecordersMutex() {
	static Common::DiagB32::TrackedMutex<std::mutex> mutex;
	return mutex;
}
''')
