# refs144a.py - Session Auditor s144 step 3 (HPP-333), general rule 24 (1): the map of the pinned references of AUDIT144.md.
# Every reference <commit>:<path>:<line> is checked against `git show <commit>:<path>`: the anchor text on the line and the
# control text on the next line (+1). READ ONLY. Usage: python refs144a.py
import subprocess

GIT = 'C:/Program Files/Git/cmd/git.exe'
KY = 'C:/kyty/KytyPS5'
EM = 'C:/kyty/KytyPS5/ps5 em'
RM = 'docs/ROADMAP.md'
W = 'src/graphics/presentation/window/'
REFS = [
    (KY, 'bacd57cc', RM, 13337, '254. **Закрытие с. 143', 'записью № 1592'),
    (KY, 'bacd57cc', RM, 13404, '(е) **Форма W до отгрузки исправления Б35', 'с `KYTY_PIPELINE_PRECACHE=0`'),
    (KY, 'bacd57cc', RM, 13413, '**Пара разных сессий (решение):**', 'сборке `9235a7ac`'),
    (KY, 'bacd57cc', RM, 13431, '(и) **Аудит (п. 253) и «Процесс»', 'принят, применение — «Процесс» 3'),
    (KY, 'bacd57cc', RM, 13446, '(к) **Цель с. 144', 'W; W стоят из-за состояния кэша'),
    (KY, 'bacd57cc', RM, 13478, '255. **Закрытие с. 143 — факт исполнения', '(а) **Порядок (общее правило 25):**'),
    (KY, 'bacd57cc', RM, 13487, '(б) **sha256 файлов инструкций', '`35b22988` → `4ed1877f`'),
    (KY, 'bacd57cc', RM, 13899, '264. **Приёмка шага 0 с. 144', 'действует; ответы лида'),
    (KY, 'bacd57cc', RM, 13981, '266. **Приёмка шага 1 с. 144', 'исполняются процедурой шага 2'),
    (KY, 'bacd57cc', RM, 13993, '(б) **RC1 принят', '`gate144.py` считает'),
    (KY, 'bacd57cc', RM, 14008, '(д) **RC4 принят:**', 'V `v143_01…06, 09, 10` строкой'),
    (KY, 'bacd57cc', RM, 14011, '(е) **RC5 принят:**', 'и в пулы холодных входов'),
    (KY, 'bacd57cc', RM, 14025, '(и) **Процесс (к аудиту с. 144, не решение):** Red Team записал', 'процессов под замком не запускал'),
    (KY, 'bacd57cc', RM, 14093, '(е) **Процесс (к аудиту с. 144, не решение):** комментарий лида `HPP-346` 06:53:40Z', 'правила «лид не пишет под замком»'),
    (KY, 'bacd57cc', RM, 14125, '(г) **Процесс (к аудиту с. 144, не решение):** три записи файлов под чужим замком', '5 и 40 с; `mkpred_p8b.py`'),
    (KY, 'bacd57cc', RM, 14133, '270. **Приёмка шага 2 с. 144', 'листы 12 V просмотрены лидом'),
    (KY, 'bacd57cc', RM, 14143, 'в нём 1 строка `[Vulkan][E]` (байт 288 182 942', 'VUID-VkSwapchainCreateInfoKHR-imageExtent-01689'),
    (KY, 'bacd57cc', RM, 14158, '(г) **Вопрос 1 исполнителя (`w144_09`)', '`SDL_WINDOWEVENT_MINIMIZED` [c, (а)]'),
    (KY, 'bacd57cc', RM, 14171, '(е) **Процесс (к аудиту с. 144, не решение):** 5 отказов BUSY', 'посторонняя нагрузка), ≈ 8 мин'),
    (KY, '4fc501f4', W + 'window.cpp', 422, 'EXIT_IF(new_width == 0 || new_height == 0);', 'Common::LockGuard lock(mutex);'),
    (KY, '4fc501f4', W + 'window.cpp', 466, 'case SDL_WINDOWEVENT_MINIMIZED:', 'minimized'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 353, 'void RecoverSwapchain(Swapchain::Status status) {', 'LOGF("Recovering Vulkan swapchain%s'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 356, 'swapchain.Recreate(status == Swapchain::Status::SurfaceLost);', 'frames.SetFormat(swapchain.Format());'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 397, 'EXIT_IF(graphics.screen_width == 0);', 'EXIT_IF(graphics.screen_height == 0);'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 402, 'm_extent = surface.capabilities.currentExtent;', 'if (m_extent.width == std::numeric_limits<uint32_t>::max()) {'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 449, 'create_info.imageExtent      = m_extent;', 'create_info.imageArrayLayers = 1;'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 472, 'RequireVulkanSuccess(graphics.device.createSwapchainKHR(&create_info, nullptr, &m_handle),', '"vkCreateSwapchainKHR");'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 567, 'void Swapchain::Recreate(bool surface_lost) {', 'Destroy();'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 578, 'm_window.RefreshSurfaceCapabilities();', 'Create();'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 732, 'case vk::Result::eErrorOutOfDateKHR:', 'LOGF("vkQueuePresentKHR returned vk::Result::eErrorOutOfDateKHR'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 881, 'for (uint32_t attempt = 0; attempt < 2; attempt++) {', 'const auto trace_start'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 927, 'if (status != Swapchain::Status::Success) {', 'm_impl->RecoverSwapchain(status);'),
    (KY, '4fc501f4', W + 'swapchain.cpp', 945, 'LOGF("Vulkan presentation retry exhausted; dropping frame', 'm_impl->frames.Release(&frame, reuse);'),
    (KY, '4fc501f4', W + 'vulkanWindow.cpp', 105, 'RequireVulkanSuccess(physical_device.getSurfaceCapabilitiesKHR(surface, &r.capabilities),', '"vkGetPhysicalDeviceSurfaceCapabilitiesKHR");'),
    (KY, '4fc501f4', W + 'vulkanWindow.cpp', 911, 'if (error) {', 'EXIT_COLOR(severity_style, "[Vulkan][%s][%u]: %s'),
    (KY, '4fc501f4', W + 'vulkanWindow.cpp', 1249, 'void WindowContext::RefreshSurfaceCapabilities() {', 'EXIT_IF(graphic_ctx.physical_device == nullptr || surface == nullptr);'),
    (KY, '4fc501f4', 'src/graphics/host_gpu/vulkanCommon.cpp', 119, 'void RequireVulkanSuccess(vk::Result result, const char* operation) {', 'if (result != vk::Result::eSuccess) {'),
    (EM, 'a41019e', 'docs/agent-team.md', 144, '27. **Звено трека вне цепочки сессии', 'пишет файлов — первая строка'),
    (EM, 'a41019e', 'docs/agent-team.md', 151, '28. **Поиск по файловой системе', 'звена: исполнитель перед сдачей'),
]
cache = {}
ok = True
for k, (root, rev, path, line, anchor, plus1) in enumerate(REFS, 1):
    key = (root, rev, path)
    if key not in cache:
        r = subprocess.run([GIT, '-C', root, 'show', '%s:%s' % (rev, path)], capture_output=True)
        cache[key] = r.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')
    ls = cache[key]
    a = line <= len(ls) and anchor in ls[line - 1]
    b = line < len(ls) and plus1 in ls[line]
    ok &= a and b
    name = ('ps5-em@' if root == EM else '') + '%s:%s:%d' % (rev, path, line)
    print('REF %2d %s anchor %s +1 %s%s' % (k, name, 'ok' if a else 'MISSING', 'ok' if b else 'MISSING',
                                           '' if (a and b) else '   line: %r / next: %r' % (ls[line - 1][:90] if line <= len(ls) else None, ls[line][:90] if line < len(ls) else None)))
print('REFS %d: %s' % (len(REFS), 'ALL OK' if ok else 'PROBLEMS'))
