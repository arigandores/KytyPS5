#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-2023-g1833ee28"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "1833ee2"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "1833ee280ec177b65feb6c4a97f626b0d4ce1b9f"
// Content hash of src/graphics/shader (the translator): key of the shader translation cache.
#define KYTY_SHADER_SOURCE_HASH "e248e4a81f15bab54ff50e2617334c712f054412"

/* Build provenance, shown in the window title and in crash reports. */
#if defined(KYTY_OFFICIAL_BUILD)
#define KYTY_BUILD_LABEL "Official build " KYTY_RELEASE_TAG
#elif defined(KYTY_FORK_BUILD)
#define KYTY_BUILD_LABEL "Fork build " KYTY_BUILD_REPOSITORY " " KYTY_GIT_HASH
#else
#define KYTY_BUILD_LABEL "Source build " KYTY_GIT_HASH
#endif
