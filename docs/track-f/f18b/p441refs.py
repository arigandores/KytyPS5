# p441refs.py - F18b (HPP-536): every <commit>:<path>:<line> reference of the item, anchor and +1 control.
import subprocess, sys
GIT = "C:/Program Files/Git/cmd/git.exe"
K = "C:/kyty/KytyPS5"
S = "C:/kyty/KytyPS5/3rdparty/SDL2"
BS = chr(92)
R = [
    (K, "66da0c76", "docs/ROADMAP.md", 22312, "(е) **Следующая итерация очереди F — F18 = Ф8", "(ж) **Таблица строк K1–K4 без исхода"),
    (K, "98f11816", "docs/track-f/f18a.md", 7, "**Кандидат исхода для F18b (не вердикт; правило — п. 433(е)).**", ""),
    (K, "98f11816", "docs/track-f/f18a.md", 43, "### 1.3 Путь отказа: утечка С2 переворачивает счётчик", ""),
    (K, "98f11816", "docs/track-f/f18a.md", 158, "**Новая строка [c лога]:** в 9 логах все три выходных порта не открылись", ""),
    (K, "98f11816", "docs/track-f/f18a.md", 173, "## 4. Проект стенда `KYTY_TEST_AUDIOLOSS=<с>[:<режим>]`", ""),
    (K, "98f11816", "docs/track-f/f18a.md", 192, "## 5. Проект правки `KYTY_FIX_F8` (умолчание 0; чтение раз на процесс)", ""),
    (K, "98f11816", "docs/track-f/f18a.md", 238, "| `f8_n0` — естественное воспроизведение |", "| `f8_n1` | `KYTY_FIX_F8=1`, стенда нет |"),
    (K, "95440108", "src/libs/controller.cpp", 145, "if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {", "return false;"),
    (K, "95440108", "src/libs/audio.cpp", 435, "if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {", 'LOGF("AudioOut: SDL audio init failed: %s' + BS + 'n", SDL_GetError());'),
    (K, "95440108", "src/libs/audio.cpp", 833, "if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {", 'LOGF("AudioIn: SDL init failed: %s' + BS + 'n", SDL_GetError());'),
    (K, "95440108", "src/libs/audio.cpp", 855, "SDL_QuitSubSystem(SDL_INIT_AUDIO);", "port->audio_device = 0;"),
    (K, "95440108", "src/libs/controller.cpp", 500, 'LOGF("Controller: disconnect of unknown id %d ignored' + BS + 'n", id);', "return;"),
    (K, "95440108", "src/libs/controller.cpp", 765, "SDL_GameControllerClose(pad);", "}"),
    (S, "4b69833b", "src/SDL.c", 119, "static Uint8 SDL_SubsystemRefCount[32];", ""),
    (K, "95440108", "src/graphics/presentation/window/window.cpp", 380, "SDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id));", "}"),
    (K, "95440108", "src/graphics/presentation/window/window.cpp", 749, "case SDL_CONTROLLERDEVICEREMOVED:", "case SDL_CONTROLLERDEVICEREMAPPED: {"),
    (K, "98f11816", "docs/track-f/register.md", 144, "| Б24 | K2 (на удержании) |", "| Б5 | K3 |"),
    (K, "98f11816", "docs/track-f/register.md", 175, "| Ф8 | K4 | наблюдение (последняя с. 105) |", "| Б22 | K5 |"),
]
ok = True
n = 0
for repo, c, p, ln, a, nx in R:
    t = subprocess.run([GIT, "-C", repo, "show", c + ":" + p], capture_output=True).stdout.decode("utf-8").split("\n")
    L = t[ln - 1].strip() if ln - 1 < len(t) else None
    N = t[ln].strip() if ln < len(t) else None
    good = L is not None and L.startswith(a) if a.startswith("|") or a.startswith("#") or a.startswith("**") or a.startswith("case") or a.startswith("if") or a.startswith("LOGF") or a.startswith("static") or a.startswith("SDL") else (L is not None and a in L)
    good = good and ((N == "") if nx == "" else (N is not None and N.startswith(nx)))
    n += 1
    print(("OK  " if good else "BAD ") + c + ":" + p + ":" + str(ln))
    ok &= good
print("refs %d of %d" % (sum(1 for _ in R) if ok else -1, n))
print("ALL OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
