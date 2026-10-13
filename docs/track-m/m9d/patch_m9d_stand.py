"""M9d (HPP-869): the stands of KYTY_DIAG_T188 - tests/T188Stand.cpp (target t188_stand) and the GPU stand mode
--t188-gpu-stand of tests/ShaderRecompilerComputeTests.cpp. Exact anchors, once each. Usage: python patch_m9d_stand.py
<worktree> <dir with T188Stand.cpp, gpu_stand.inc>. Lock checked first (exit 3). Prints ALL OK."""
import os
import shutil
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/m657/STOP'):
    print('LOCK or STOP')
    sys.exit(3)
WT = sys.argv[1]
NEW = sys.argv[2]
fails = []


def rep(rel, old, new):
    path = os.path.join(WT, rel)
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    t = raw.decode('utf-8').replace('\r\n', '\n')
    n = t.count(old)
    if n != 1:
        fails.append('%s: anchor x%d: %r' % (rel, n, old[:80]))
        return
    t = t.replace(old, new)
    if crlf:
        t = t.replace('\n', '\r\n')
    open(path, 'wb').write(t.encode('utf-8'))


shutil.copyfile(os.path.join(NEW, 'T188Stand.cpp'), os.path.join(WT, 'tests/T188Stand.cpp'))
rep('CMakeLists.txt', '''add_kyty_full_emulator_test(m_wave2_diag_stand "${KYTY_TESTS_DIR}/MWave2DiagStand.cpp")
''', '''add_kyty_full_emulator_test(m_wave2_diag_stand "${KYTY_TESTS_DIR}/MWave2DiagStand.cpp")

# Track M, M9d (HPP-869, ROADMAP s122 item 785(d)): stand of the functions of KYTY_DIAG_T188 and of DiagT109 (no game, no
# GPU); run by C:/kyty/m657/m9d/run_stand_m9d.py, not by ctest. The GPU stand is --t188-gpu-stand of
# shader_recompiler_compute_tests.
add_kyty_full_emulator_test(t188_stand "${KYTY_TESTS_DIR}/T188Stand.cpp")
''')
T = 'tests/ShaderRecompilerComputeTests.cpp'
rep(T, '''  static void InitializeTexture(TextureCache &cache, ImageId id) {
    auto lock = Lock(cache);
    cache.InitializeImage(id, false);
    cache.m_page_manager.DrainDeferredProtection();
  }
''', '''  static void InitializeTexture(TextureCache &cache, ImageId id) {
    auto lock = Lock(cache);
    cache.InitializeImage(id, false);
    cache.m_page_manager.DrainDeferredProtection();
  }

  // Track M, M9d (HPP-869): the T188 GPU stand - a CPU write of the image's range, and FreeImage, under m_lock.
  static void T188InvalidateCpu(TextureCache &cache, ImageId id, uint64_t address, uint64_t size) {
    auto lock = Lock(cache);
    cache.m_slot_images[id].InvalidateCpuWrite(address, size);
  }
  static void T188Free(TextureCache &cache, ImageId id) {
    auto lock = Lock(cache);
    cache.FreeImage(id, "t188_stand", 0);
  }
''')
gpu = open(os.path.join(NEW, 'gpu_stand.inc'), encoding='utf-8').read().replace('\r\n', '\n')
rep(T, '''  void CheckHostImageAllocation() {
    constexpr const char *name = "HostImageAllocation";
''', gpu + '''  void CheckHostImageAllocation() {
    constexpr const char *name = "HostImageAllocation";
''')
rep(T, '''  if (argc == 2 && std::strcmp(argv[1], "--host-image-allocation-only") == 0) {
    VulkanHarness vulkan;
    vulkan.CheckHostImageAllocation();
    return 0;
  }
''', '''  if (argc == 2 && std::strcmp(argv[1], "--host-image-allocation-only") == 0) {
    VulkanHarness vulkan;
    vulkan.CheckHostImageAllocation();
    return 0;
  }
  if (argc == 2 && std::strcmp(argv[1], "--t188-gpu-stand") == 0) {
    // Track M, M9d (HPP-869): the GPU stand of KYTY_DIAG_T188 only (no other case of this executable runs).
    VulkanHarness vulkan;
    vulkan.CheckT188GpuStand();
    return 0;
  }
''')
if fails:
    for x in fails:
        print('FAIL', x)
    sys.exit(1)
print('ALL OK')
