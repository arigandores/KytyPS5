P = 'C:/kyty/KytyPS5/tests/shaderCfgTests.cpp'
t = open(P, 'rb').read().decode('utf-8')
old = '''    const uint32_t shader[] = {
        EncodeSmem0(0x00, 0, 4), 0u,                    // s_load_dword s0
        EncodeSmem0(0x08, 1, 4), 0u,                    // s_buffer_load_dword s1
        EncodeMubuf0(0x0c, 4),   EncodeMubuf1(0, 0, 1), // buffer_load_dword v0
        EncodeMimg0(0x00, 0xf),  EncodeMimg1(4, 0, 0, 1), // image_load v4
        EncodeMimg0(0x20, 0xf),  EncodeMimg1(3, 0, 0, 1), // image_sample v3
        0xbf810000u,
    };
    auto user_data = ImageTestUserData();
'''
new = '''    constexpr uint32_t MimgDimCube = 3;
    const uint32_t shader[] = {
        EncodeMimg0(0x20, 0xf, false, MimgDimCube),
        EncodeMimg1(0, 0, 1, 0), // image_sample cube (T# s[4:11], S# s[0:3])
        EncodeMimg0(0x60, 0x3, false, MimgDimCube),
        EncodeMimg1(8, 0, 1, 4), // image_get_lod cube
        0xbf810000u,
    };
    auto user_data = ImageTestUserData(Prospero::ImageType::kCube);
'''
assert t.count(old) == 1
t = t.replace(old, new)
t = t.replace('// (1) Descriptors inline in user data (ImageTestUserData: T# bases 0x1000 + 0x100 * start), memory reads answer 0.',
              '// (1) Descriptors inline in user data (the cube sample of TestNewShaderRecompilerCubeSampleCoordinates;\n'
              '  // ImageTestUserData: T# bases 0x1000 + 0x100 * start), memory reads answer 0.')
open(P, 'wb').write(t.encode('utf-8'))
print('tests3 patched OK')
