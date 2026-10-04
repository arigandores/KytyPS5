#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1879-g3904522d"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "3904522"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "3904522da9cf29a8c22c19fcb8f8a8e3ed35b791"
// Content hash of src/graphics/shader (the translator): key of the shader translation cache.
#define KYTY_SHADER_SOURCE_HASH "26ce5fc78ea3b20be537c7696be041f5e97d9e58"

/* Build provenance, shown in the window title and in crash reports. */
#if defined(KYTY_OFFICIAL_BUILD)
#define KYTY_BUILD_LABEL "Official build " KYTY_RELEASE_TAG
#elif defined(KYTY_FORK_BUILD)
#define KYTY_BUILD_LABEL "Fork build " KYTY_BUILD_REPOSITORY " " KYTY_GIT_HASH
#else
#define KYTY_BUILD_LABEL "Source build " KYTY_GIT_HASH
#endif
