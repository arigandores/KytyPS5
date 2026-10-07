import os
paths = [os.environ['PAPERCLIP_RUN_SCRATCH_DIR'] + '/LogAsyncTests.cpp', 'C:/kyty/f287/f25k/LogAsyncTests.cpp',
         'C:/kyty/f287/f25k/wt/tests/LogAsyncTests.cpp']
old = '''		std::printf("  lines=%d marker=%d summary=%d\\n", got, text.find(d.marker) != std::string::npos ? 1 : 0,
		            text.find("LogAsync: full_waits=") != std::string::npos ? 1 : 0);
		CHECK(ok);
'''
new = old + '''		if (std::strcmp(d.mode, "die_exit_long") == 0) {
			// The writer asleep 8 s > the 5 s drain: the timeout branch ran and the dying thread wrote the rest.
			CHECK(Field(text, " drain_timeouts=") != UINT64_MAX && Field(text, " drain_timeouts=") >= 1);
			CHECK(Field(text, " sync_lines=") != UINT64_MAX && Field(text, " sync_lines=") >= 1);
		}
'''
for p in paths:
    t = open(p, 'rb').read().decode().replace('\r', '')
    assert t.count(old) == 1, p
    open(p, 'wb').write(t.replace(old, new).encode())
print('ok')
