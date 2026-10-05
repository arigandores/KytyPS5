P = 'C:/kyty/KytyPS5/tests/shaderCfgTests.cpp'
u = open(P, 'rb').read().decode('utf-8')
old = '''        EncodeMimg1(8, 0, 2, 1), // sampled image s[8:15], sampler s[4:7]
        EncodeMimg0(0x08, 0xf),
        EncodeMimg1(8, 0, 0, 1), // keep sample live in storage view
        EncodeSopp(0x01),
    };
    auto user_data = ImageTestUserData();
'''
new = '''        EncodeMimg1(8, 0, 2, 1), // sampled image s[0:7], sampler s[8:11]
        EncodeMimg0(0x08, 0xf),
        EncodeMimg1(8, 0, 0, 1), // keep sample live in storage view
        EncodeSopp(0x01),
    };
    auto user_data = ImageTestUserData();
    // s[7] is both the metadata address dword of the T# s[0:7] and the type dword of the V# s[4:7]; a word with two
    // roles cannot be canonical for both (the self-check rejects it), so the fixture keeps it 0.
    user_data[7] = 0;
'''
assert u.count(old) == 1
u = u.replace(old, new)
open(P, 'wb').write(u.encode('utf-8'))
print('p5 OK')
