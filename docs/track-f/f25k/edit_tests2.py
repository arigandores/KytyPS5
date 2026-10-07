# F25k: the latency cases read "on=" of the TestLogStall line followed by " tid=" (edit_log3.py added tid / role).
import sys
edits = [
    ('''		CHECK(text.find(" on=writer\\n") != std::string::npos);
''', '''		CHECK(text.find(" on=writer tid=") != std::string::npos);
'''),
    ('''		CHECK(text.find(" on=caller\\n") != std::string::npos);
''', '''		CHECK(text.find(" on=caller tid=") != std::string::npos);
'''),
]
for p in sys.argv[1:]:
    t = open(p, 'rb').read().decode()
    assert '\r' not in t
    for old, new in edits:
        assert t.count(old) == 1, (p, old[:50])
        t = t.replace(old, new)
    open(p, 'wb').write(t.encode())
    print('ok', p)
