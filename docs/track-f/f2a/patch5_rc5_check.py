# F2a (HPP-307) patch 5 (test-only): --fix-b26-only also checks RC5 of the F1b review - the
# translation cache signature and directory carry "fixb26" exactly when KYTY_FIX_B26 is on.
import sys
sys.path.insert(0, 'C:/kyty/f287/f2a')
import patchlib

T = 'C:/kyty/KytyPS5/tests/ShaderRecompilerComputeTests.cpp'

patchlib.apply(T, [
    (['#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"'],
     ['#include "graphics/host_gpu/renderer/pipeline/shaderTranslationCache.h"'], 'after'),
    (['    CheckB26Decode(fix_on);'],
     ['    CheckB26Decode(fix_on);',
      '    {',
      '      // RC5 of the F1b review: =1 and =0 never share a signature or a directory.',
      '      const ShaderTranslationCache cache("PPSA21564");',
      '      const auto directory = Common::PathToString(cache.Directory());',
      '      const bool signed_fix = cache.Signature().find(":fixb26") != std::string::npos;',
      '      const bool folder_fix = directory.find("fixb26") != std::string::npos;',
      '      std::printf("[b26]     cache dir=%s fixb26_in_signature=%d fixb26_in_dir=%d\\n",',
      '                  directory.c_str(), signed_fix ? 1 : 0, folder_fix ? 1 : 0);',
      '      Require("B26Cache", "translation cache key", cache.Enabled() && signed_fix == fix_on &&',
      '                                                     folder_fix == fix_on,',
      '              "fixb26 token of the signature or directory does not follow the knob");',
      '    }'], 'replace'),
])
