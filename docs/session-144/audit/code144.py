# code144.py - Session Auditor s144 step 3 (HPP-333), ROADMAP item 270 (g)(3): the swapchain size path of the installed
# build's source (commit 4fc501f4): quoted lines with their numbers and git grep counts over src/. READ ONLY (git show / grep).
import subprocess, re

GIT = 'C:/Program Files/Git/cmd/git.exe'
KY = 'C:/kyty/KytyPS5'
REV = '4fc501f4'
W = 'src/graphics/presentation/window/'


def show(path):
    r = subprocess.run([GIT, '-C', KY, 'show', '%s:%s' % (REV, path)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace').replace('\r', '').split('\n')


def quote(path, a, b):
    ls = show(path)
    for i in range(a, b + 1):
        print('  %s:%s:%d | %s' % (REV, path, i, ls[i - 1].replace('\t', '    ')))


def grep(pat, fixed=True):
    r = subprocess.run([GIT, '-C', KY, 'grep', '-n', '-F' if fixed else '-E', '-e', pat, REV, '--', 'src'], capture_output=True)
    out = [x for x in r.stdout.decode('utf-8', 'replace').splitlines() if x.strip()]
    print('GREP %r in %s:src: %d lines' % (pat, REV, len(out)))
    for x in out[:12]:
        print('   ' + x[:200].replace('\t', ' '))
    return out


r = subprocess.run([GIT, '-C', KY, 'show', '-s', '--format=%H %ci %s', REV], capture_output=True)
print('REV ' + r.stdout.decode('utf-8', 'replace').strip()[:160])
print('--- (a) the window event: only a log line')
quote(W + 'window.cpp', 421, 426)
quote(W + 'window.cpp', 457, 474)
print('--- (b) present: OutOfDate -> Status::Recreate -> RecoverSwapchain -> continue (2 attempts, no wait)')
quote(W + 'swapchain.cpp', 727, 739)
quote(W + 'swapchain.cpp', 881, 889)
quote(W + 'swapchain.cpp', 927, 930)
quote(W + 'swapchain.cpp', 945, 946)
quote(W + 'swapchain.cpp', 353, 358)
print('--- (c) Recreate: Destroy, RefreshSurfaceCapabilities, Create')
quote(W + 'swapchain.cpp', 567, 580)
quote(W + 'vulkanWindow.cpp', 1249, 1252)
quote(W + 'vulkanWindow.cpp', 103, 106)
print('--- (d) Create: where the extent comes from')
quote(W + 'swapchain.cpp', 391, 410)
quote(W + 'swapchain.cpp', 443, 449)
quote(W + 'swapchain.cpp', 472, 474)
print('--- (e) a validation error is fatal')
quote(W + 'vulkanWindow.cpp', 903, 914)
print('--- (f) searches over src/')
for p in ('SDL_WINDOWEVENT_MINIMIZED', 'SDL_WINDOWEVENT_RESTORED', 'SDL_WINDOW_MINIMIZED', 'SDL_GetWindowFlags', 'Recovering Vulkan swapchain', 'currentExtent',
          'minImageExtent', 'SDL_Vulkan_GetDrawableSize', 'SDL_GetWindowSize', 'RecoverSwapchain', 'Recreate(', 'RefreshSurfaceCapabilities',
          'SDL_WaitEvent', 'imageExtent', 'presentation retry exhausted'):
    grep(p)
grep(r'(extent|m_extent)\.(width|height) == 0', fixed=False)
grep(r'static .*RequireVulkanSuccess|void RequireVulkanSuccess', fixed=False)
print('ALL DONE')
