# F2a (HPP-307) patch 4 (test-only): --b26-pass translates with 16 and 32 user SGPRs (the real count
# of the registration is not in the logs; 57c4d5848e02ecdc reads s20/s21 before writing them).
import sys
sys.path.insert(0, 'C:/kyty/f287/f2a')
import patchlib

T = 'C:/kyty/KytyPS5/tests/ShaderRecompilerComputeTests.cpp'

patchlib.apply(T, [
    (['    for (const uint32_t wave : {32u, 64u}) {'],
     ['    for (const uint32_t user_count : {16u, 32u}) {',
      '    for (const uint32_t wave : {32u, 64u}) {'], 'replace'),
    (['      options.user_data = std::span(user_data).first(16);'],
     ['      options.user_data = std::span(user_data).first(user_count);'], 'replace'),
    (['      std::printf("B26Pass: translate hash=%016llx wave=%u %s\\n",',
      '                  static_cast<unsigned long long>(blob.hash), wave,',
      '                  verdict.c_str());',
      '    }'],
     ['      std::printf("B26Pass: translate hash=%016llx wave=%u user_sgprs=%u %s\\n",',
      '                  static_cast<unsigned long long>(blob.hash), wave, user_count,',
      '                  verdict.c_str());',
      '    }',
      '    }'], 'replace'),
    (['// translation budget) for the wave sizes 32 and 64. The registration info of the real shaders',
      '// (threads, user SGPR count) is not in the logs: threads 64x1x1 and 16 user SGPRs are assumptions,',
      '// so the translation verdict is a prediction, the UNSUPPORTED list is not.'],
     ['// translation budget) for the wave sizes 32 and 64 and 16 or 32 user SGPRs. The registration info',
      '// of the real shaders (threads, user SGPR count) is not in the logs: threads 64x1x1 and the user SGPR',
      '// counts are assumptions, so the translation verdict is a prediction, the UNSUPPORTED list is not.'],
     'replace'),
])
