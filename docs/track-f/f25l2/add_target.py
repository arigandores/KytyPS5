import sys
p = sys.argv[1]
b = open(p, 'rb').read()
anchor = b'target_include_directories(f25l_probe PRIVATE ${inc_headers})\n'
assert b.count(anchor) == 1, 'anchor'
if b'f25l2_probe' in b:
    print('already')
    sys.exit(0)
add = (b'# F25l2 (HPP-683, Red Team): probe only, not committed\n'
       b'add_executable(f25l2_probe EXCLUDE_FROM_ALL "${KYTY_TESTS_DIR}/F25l2Probe.cpp")\n'
       b'target_link_libraries(f25l2_probe common fmt::fmt)\n'
       b'target_include_directories(f25l2_probe PRIVATE ${inc_headers})\n')
open(p, 'wb').write(b.replace(anchor, anchor + add))
print('ok')
