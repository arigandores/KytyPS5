#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1961-g68602c4f"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "68602c4"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "68602c4f301e8d424af0581d11039437ec4a958f"
// Content hash of src/graphics/shader (the translator): key of the shader translation cache.
#define KYTY_SHADER_SOURCE_HASH "56189185f9e9f9a0ea5174f3f85206e6d099db3d"

/* Build provenance, shown in the window title and in crash reports. */
#if defined(KYTY_OFFICIAL_BUILD)
#define KYTY_BUILD_LABEL "Official build " KYTY_RELEASE_TAG
#elif defined(KYTY_FORK_BUILD)
#define KYTY_BUILD_LABEL "Fork build " KYTY_BUILD_REPOSITORY " " KYTY_GIT_HASH
#else
#define KYTY_BUILD_LABEL "Source build " KYTY_GIT_HASH
#endif
