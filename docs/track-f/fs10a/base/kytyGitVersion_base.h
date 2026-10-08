#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1900-g11164d72"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "11164d7"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "11164d7258899f9450f2b06149197e94f57d4b21"
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
