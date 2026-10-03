#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1992-gc01451b0"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "c01451b"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "c01451b051bd13a0a0deb14b79892daa16779d45"
// Content hash of src/graphics/shader (the translator): key of the shader translation cache.
#define KYTY_SHADER_SOURCE_HASH "23f2e9d0a210e47e1f500eba542cd9c2b2c4795d"

/* Build provenance, shown in the window title and in crash reports. */
#if defined(KYTY_OFFICIAL_BUILD)
#define KYTY_BUILD_LABEL "Official build " KYTY_RELEASE_TAG
#elif defined(KYTY_FORK_BUILD)
#define KYTY_BUILD_LABEL "Fork build " KYTY_BUILD_REPOSITORY " " KYTY_GIT_HASH
#else
#define KYTY_BUILD_LABEL "Source build " KYTY_GIT_HASH
#endif
