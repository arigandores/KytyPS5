import sys
p = sys.argv[1]
t = open(p, encoding='utf-8').read()
old_main = '''int main(int argc, char** argv) {
	if (argc != 2) {
		std::fprintf(stderr, "usage: t188_stand <log file>\\n");
		return 2;
	}
'''
new_main = '''// The cls arm (driver: KYTY_DIAG_T188=2, KYTY_DIAG_T188_CLS="<ClassKey(Fields())>,zz,1"): the list is read once by the
// static initialization; the class of Fields() is listed, that of Fields(4) is not - its closure counts tint_skip_cls.
int ArmCls() {
	const bool listed = T::ClassListed(T::ClassKey(Fields()));
	const bool other  = T::ClassListed(T::ClassKey(Fields(4)));
	Reset(2);
	T::ImageState s;
	(void)T::NoteInvalidate(s, Geo(), Fields(4), true, T::Writer::St, A + 0x4000, 0x1000, false, true);
	const auto plan = T::CloseUpload(s, Geo(), Fields(4), T::Close::Smp, 0, 3, 0, 0, true, false, true);
	const bool ok = T::g_mode == 2 && listed && !other && T::Read(T::C::tint_skip_cls) == 1 && plan.mask == 0;
	std::printf("T188Stand: cls listed=%d other=%d skip_cls=%llu mask=%u ok=%d\\n", listed ? 1 : 0, other ? 1 : 0,
	            static_cast<unsigned long long>(T::Read(T::C::tint_skip_cls)), plan.mask, ok ? 1 : 0);
	return 0;
}

int main(int argc, char** argv) {
	if (argc != 2 && !(argc == 3 && std::strcmp(argv[2], "cls") == 0)) {
		std::fprintf(stderr, "usage: t188_stand <log file> [cls]\\n");
		return 2;
	}
'''
assert t.count(old_main) == 1, t.count(old_main)
t = t.replace(old_main, new_main)
old = '''	const int env_mode = T::g_mode;
	T::PrintModeLine();
'''
new = '''	const int env_mode = T::g_mode;
	T::PrintModeLine();
	if (argc == 3) {
		(void)ArmCls();
		std::fflush(stdout);
		Log::Flush();
		Log::DrainForExit();
		std::_Exit(0);
	}
'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new)
open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('ok')
