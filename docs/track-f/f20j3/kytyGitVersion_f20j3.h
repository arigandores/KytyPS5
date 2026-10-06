#include "cmake_config.h"

#define KYTY_GIT_VERSION "KytyPS5-2026-09-15-6a2987a-1893-g9db7938b"
// Short, human-facing commit name used in build labels.
#define KYTY_GIT_HASH "9db7938"
// Full commit identity used for compatibility checks.
#define KYTY_GIT_REVISION "9db7938baa46814e589a76dffd4e2fc571ede584"
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
