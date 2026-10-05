#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1883-gd6ee2dc8"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "d6ee2dc"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "d6ee2dc886c98b80ab36231519dec9f7356a4691"
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
