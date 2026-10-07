import sys
p = sys.argv[1]
b = open(p, 'rb').read()
anchor = b'target_compile_definitions(log_async_tests PRIVATE KYTY_LOG_ASYNC_TESTS=1)\n'
assert b.count(anchor) == 1, 'anchor'
add = (b'# F25l (HPP-679, Red Team): probe only, not committed\n'
       b'add_executable(f25l_probe EXCLUDE_FROM_ALL "${KYTY_TESTS_DIR}/F25lProbe.cpp")\n'
       b'target_link_libraries(f25l_probe common fmt::fmt)\n'
       b'target_include_directories(f25l_probe PRIVATE ${inc_headers})\n')
open(p, 'wb').write(b.replace(anchor, anchor + add))
print('ok')
