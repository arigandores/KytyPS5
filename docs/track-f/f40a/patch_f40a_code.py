# F40a (HPP-770): code of KYTY_FIX_F24 (variant B, ROADMAP s122 item 692(v)) - window.cpp (WindowCreate, GameEventController),
# hostInput.cpp (bounded wait), controller.cpp (stop first, no delete after an expired stop), vulkanWindow.cpp (video-only
# quit at =1), new files joyPump.h / joyPump.cpp (copied from the run folder). CRLF-safe: \r removed before the search and
# restored if the file had it; whole-line anchors, each must match exactly once. Usage: patch_f40a_code.py <repo root> <src dir of the new files>
import os
import shutil
import sys

ROOT = sys.argv[1]
NEW = sys.argv[2]


def patch(rel, pairs):
    path = os.path.join(ROOT, rel)
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            raise SystemExit('ANCHOR x%d in %s: %r' % (n, rel, old[:80]))
        text = text.replace(old, new)
    if crlf:
        text = text.replace('\n', '\r\n')
    open(path, 'wb').write(text.encode('utf-8'))
    print('patched', rel, 'crlf' if crlf else 'lf')


W = 'src/graphics/presentation/window/window.cpp'

patch(W, [
    ('#include "graphics/presentation/window/hostInput.h"\n',
     '#include "graphics/presentation/window/hostInput.h"\n'
     '#include "graphics/presentation/window/joyPump.h"\n'),
    # add event
    ('\tif (f.added) {\n'
     '\t\tauto* pad = SDL_GameControllerOpen(f.id);\n',
     '\tif (f.added && JoyPump::Enabled()) {\n'
     '\t\t// Track F, F40a (KYTY_FIX_F24=1, RC2): JoyPump opens new pads by instance id after its own SDL_JoystickUpdate\n'
     '\t\t// (docs/track-f/f40a.md s0.4); the add event of the main thread is only logged.\n'
     '\t\tJoyPump::NoteAddEvent(f.id);\n'
     '\t} else if (f.added) {\n'
     '\t\tauto* pad = SDL_GameControllerOpen(f.id);\n'),
    # removal: the close goes to JoyPump at =1
    ('\t\tController::Disconnect(f.id);\n'
     '\t\tSDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id));\n',
     '\t\tController::Disconnect(f.id);\n'
     '\t\tif (JoyPump::Enabled()) {\n'
     '\t\t\tJoyPump::PostClose(f.id); // Track F, F40a: the close is a JoyPump task (s0.4)\n'
     '\t\t} else {\n'
     '\t\t\tSDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id));\n'
     '\t\t}\n'),
    # WindowCreate
    ('\tif (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {\n'
     '\t\tEXIT("%s\\n", SDL_GetError());\n'
     '\t}\n'
     '\tHostInputInit();\n',
     '\t// Track F, F40a (HPP-770, ROADMAP s122 item 692(v)): KYTY_FIX_F24, read once here before the SDL init. At 1 the main\n'
     '\t// thread initializes only the video subsystem and waits while JoyPump initializes the game controllers - every\n'
     '\t// joystick window, timer and COM apartment belongs to JoyPump (variant B, docs/track-f/f40a.md s0.1).\n'
     '\tJoyPump::ReadKnob();\n'
     '\tif (JoyPump::Enabled()) {\n'
     '\t\tconst auto main_tid = static_cast<uint64_t>(SDL_ThreadID());\n'
     '\t\tSDL_SetHint(SDL_HINT_AUTO_UPDATE_JOYSTICKS, "0");\n'
     '\t\tif (SDL_InitSubSystem(SDL_INIT_VIDEO) < 0) {\n'
     '\t\t\tEXIT("%s\\n", SDL_GetError());\n'
     '\t\t}\n'
     '\t\tstd::string error;\n'
     '\t\tif (!JoyPump::Start(main_tid, &error)) {\n'
     '\t\t\tEXIT("%s\\n", error.c_str());\n'
     '\t\t}\n'
     '\t} else if (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) {\n'
     '\t\tEXIT("%s\\n", SDL_GetError());\n'
     '\t}\n'
     '\tHostInputInit();\n'),
])

patch('src/graphics/presentation/window/hostInput.cpp', [
    ('#include "common/logging/log.h"\n'
     '#include "libs/controller.h"\n',
     '#include "common/logging/log.h"\n'
     '#include "graphics/presentation/window/joyPump.h"\n'
     '#include "libs/controller.h"\n'),
    ('#include <algorithm>\n'
     '#include <array>\n',
     '#include <algorithm>\n'
     '#include <array>\n'
     '#include <atomic>\n'),
    ('bool HostInputWaitEvent(SDL_Event* event) {\n'
     '\tif (!g_mouse.enabled || SDL_GetKeyboardFocus() == nullptr) {\n',
     '// Track F, F40a (KYTY_FIX_F24=1, RC1, ROADMAP s122 item 692(v)(3); docs/track-f/f40a.md s0.3): with\n'
     '// SDL_HINT_AUTO_UPDATE_JOYSTICKS=0 SDL has no polling interval, and an event posted by another thread between the\n'
     '// queue check and the wakeup window publication of SDL_WaitEventTimeout_Device is not woken. The wait is bounded as\n'
     '// SDL bounds it at =0: 1 ms while JoyPump has a pad open, else 3000 ms; the main thread does not call\n'
     '// SDL_NumJoysticks. A 0 return is "no event" (the loop goes round); a wait error is a line, not a fatal.\n'
     'static bool HostInputWaitEventF24(SDL_Event* event) {\n'
     '\tconst int bound_ms = JoyPump::OpenPads() > 0 ? 1 : 3000;\n'
     '\tif (!g_mouse.enabled || SDL_GetKeyboardFocus() == nullptr) {\n'
     '\t\tCenterMouseStick();\n'
     '\t\tSDL_ClearError();\n'
     '\t\tif (SDL_WaitEventTimeout(event, bound_ms) != 0) {\n'
     '\t\t\treturn true;\n'
     '\t\t}\n'
     '\t\tif (SDL_GetError()[0] != \'\\0\') {\n'
     '\t\t\tstatic std::atomic<uint32_t> logged {0};\n'
     '\t\t\tif (logged.fetch_add(1, std::memory_order_relaxed) < 32) {\n'
     '\t\t\t\tLOGF("FixF24: wait error \\"%s\\"\\n", SDL_GetError());\n'
     '\t\t\t}\n'
     '\t\t}\n'
     '\t\treturn false;\n'
     '\t}\n'
     '\n'
     '\tconst int timeout_ms = std::min(PollMouse(SDL_GetTicks64()), bound_ms);\n'
     '\tSDL_ClearError();\n'
     '\tif (SDL_WaitEventTimeout(event, timeout_ms) != 0) {\n'
     '\t\treturn true;\n'
     '\t}\n'
     '\tif (SDL_GetError()[0] != \'\\0\') {\n'
     '\t\tEXIT("%s\\n", SDL_GetError());\n'
     '\t}\n'
     '\treturn false;\n'
     '}\n'
     '\n'
     'bool HostInputWaitEvent(SDL_Event* event) {\n'
     '\tif (JoyPump::Enabled()) {\n'
     '\t\treturn HostInputWaitEventF24(event);\n'
     '\t}\n'
     '\tif (!g_mouse.enabled || SDL_GetKeyboardFocus() == nullptr) {\n'),
])

patch('src/libs/controller.cpp', [
    ('#include "common/threads.h"\n'
     '#include "kernel/pthread.h"\n',
     '#include "common/threads.h"\n'
     '#include "graphics/presentation/window/joyPump.h" // Track F, F40a (KYTY_FIX_F24)\n'
     '#include "kernel/pthread.h"\n'),
    ('void Shutdown() {\n'
     '\tEmergencyShutdown();\n'
     '\tdelete g_controller;\n'
     '\tg_controller = nullptr;\n',
     'void Shutdown() {\n'
     '\tEmergencyShutdown();\n'
     '\t// Track F, F40a (KYTY_FIX_F24, RC4): after an expired JoyPump stop the object stays until the process ends - a JoyPump\n'
     '\t// returning from an OS call must not reach freed memory (docs/track-f/f40a.md s0.4). At =0 Exited() is true.\n'
     '\tif (Libs::Graphics::JoyPump::Exited()) {\n'
     '\t\tdelete g_controller;\n'
     '\t\tg_controller = nullptr;\n'
     '\t}\n'),
    ('void EmergencyShutdown() {\n'
     '\tif (g_haptics != nullptr) {\n',
     'void EmergencyShutdown() {\n'
     '\t// Track F, F40a (KYTY_FIX_F24=1, RC4, ROADMAP s122 item 692(v)(6)): JoyPump is stopped first - after the flag it\n'
     '\t// runs no task and calls neither Controller nor SDL; the wait is at most T_JP = 2 s ("FixF24: pump_stop_expired").\n'
     '\tif (Libs::Graphics::JoyPump::Enabled()) {\n'
     '\t\tLibs::Graphics::JoyPump::Stop();\n'
     '\t}\n'
     '\tif (g_haptics != nullptr) {\n'),
])

patch('src/graphics/presentation/window/vulkanWindow.cpp', [
    ('#include "graphics/presentation/window/windowInternal.h"\n',
     '#include "graphics/presentation/window/joyPump.h"\n'
     '#include "graphics/presentation/window/windowInternal.h"\n'),
    ('\tSDL_QuitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER);\n',
     '\tif (JoyPump::Enabled()) {\n'
     '\t\t// Track F, F40a (KYTY_FIX_F24=1, s0.4): the joystick subsystem was initialized on JoyPump (its windows, timers and\n'
     '\t\t// COM apartment); it is not torn down from this thread and stays until the process ends, as on the quick_exit path.\n'
     '\t\tSDL_QuitSubSystem(SDL_INIT_VIDEO);\n'
     '\t} else {\n'
     '\t\tSDL_QuitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER);\n'
     '\t}\n'),
])

for name in ('joyPump.h', 'joyPump.cpp'):
    dst = os.path.join(ROOT, 'src/graphics/presentation/window', name)
    if os.path.exists(dst):
        raise SystemExit('EXISTS ' + dst)
    shutil.copyfile(os.path.join(NEW, name), dst)
    print('new', dst)
print('ALL OK')
