P = 'C:/kyty/KytyPS5/tests/shaderCfgTests.cpp'
t = open(P, 'rb').read().decode('utf-8')
old = '''    constexpr uint32_t MimgDimCube = 3;
    const uint32_t shader[] = {
        EncodeMimg0(0x20, 0xf, false, MimgDimCube),
        EncodeMimg1(0, 0, 1, 0), // image_sample cube (T# s[4:11], S# s[0:3])
        EncodeMimg0(0x60, 0x3, false, MimgDimCube),
        EncodeMimg1(8, 0, 1, 4), // image_get_lod cube
        0xbf810000u,
    };
    auto user_data = ImageTestUserData(Prospero::ImageType::kCube);
'''
new = '''    const uint32_t shader[] = {
        EncodeMubuf0(0x0c),
        EncodeMubuf1(0, 0, 1), // buffer load s[0:3]
        EncodeMubuf0(0x0c),
        EncodeMubuf1(1, 0, 1), // same buffer
        EncodeMubuf0(0x1d),
        EncodeMubuf1(0, 1, 1), // keep both loads live in s[4:7]
        EncodeMimg0(0x20, 0xf),
        EncodeMimg1(8, 0, 2, 1), // sampled image s[8:15], sampler s[4:7]
        EncodeMimg0(0x08, 0xf),
        EncodeMimg1(8, 0, 0, 1), // keep sample live in storage view
        EncodeSopp(0x01),
    };
    auto user_data = ImageTestUserData();
'''
assert t.count(old) == 1
t = t.replace(old, new)
t = t.replace('''  // (1) Descriptors inline in user data (the cube sample of TestNewShaderRecompilerCubeSampleCoordinates;
  // ImageTestUserData: T# bases 0x1000 + 0x100 * start), memory reads answer 0.''',
              '''  // (1) Descriptors inline in user data (the shader of TestResourceTrackingRealDensePatching; ImageTestUserData:
  // T# bases 0x1000 + 0x100 * start), memory reads answer 0.''')
open(P, 'wb').write(t.encode('utf-8'))
print('tests4 patched OK')
