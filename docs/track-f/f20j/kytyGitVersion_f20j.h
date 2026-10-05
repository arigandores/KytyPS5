#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1891-g0df13a66"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "0df13a6"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "0df13a665a68434fd3b8bca2849d2b41c34b561a"
// Content hash of src/graphics/shader (the translator): key of the shader translation cache.
#define KYTY_SHADER_SOURCE_HASH "9177b4267de1fb8bac7d1113afd8733210addfac"

/* Build provenance, shown in the window title and in crash reports. */
#if defined(KYTY_OFFICIAL_BUILD)
#define KYTY_BUILD_LABEL "Official build " KYTY_RELEASE_TAG
#elif defined(KYTY_FORK_BUILD)
#define KYTY_BUILD_LABEL "Fork build " KYTY_BUILD_REPOSITORY " " KYTY_GIT_HASH
#else
#define KYTY_BUILD_LABEL "Source build " KYTY_GIT_HASH
#endif
