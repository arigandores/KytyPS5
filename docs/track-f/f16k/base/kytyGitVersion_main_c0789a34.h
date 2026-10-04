#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-2225-gc0789a34-dirty"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "c0789a3-dirty"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "c0789a34c2acfe3f8d455801ff7a16643e894ff6"
// Content hash of src/graphics/shader (the translator): key of the shader translation cache.
#define KYTY_SHADER_SOURCE_HASH "a54ae4bd03a673fe35ae89bad218132257b11383"

/* Build provenance, shown in the window title and in crash reports. */
#if defined(KYTY_OFFICIAL_BUILD)
#define KYTY_BUILD_LABEL "Official build " KYTY_RELEASE_TAG
#elif defined(KYTY_FORK_BUILD)
#define KYTY_BUILD_LABEL "Fork build " KYTY_BUILD_REPOSITORY " " KYTY_GIT_HASH
#else
#define KYTY_BUILD_LABEL "Source build " KYTY_GIT_HASH
#endif
