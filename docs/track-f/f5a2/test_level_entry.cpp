// F5a2 (HPP-366, ROADMAP s122 item 280(v)): test of the KYTY_TEST_MINIMIZE arm predicate (RC2 of F5b) on the real
// header src/graphics/presentation/window/testMinimizeLine.h.  Build: build_test_level_entry.cmd.  Exit 0 and the last
// line "ALL OK" - every case matched.
#include "graphics/presentation/window/testMinimizeLine.h"

#include <cstdio>
#include <string>
#include <string_view>

using Libs::Graphics::TestMinimizeIsLevelEntry;

static int g_fail = 0;
static int g_cases = 0;

static void Case(const char* name, std::string_view text, bool want) {
	g_cases++;
	const bool got = TestMinimizeIsLevelEntry(text);
	std::printf("%-44s want=%d got=%d %s\n", name, want ? 1 : 0, got ? 1 : 0, got == want ? "ok" : "FAIL");
	if (got != want) {
		g_fail++;
	}
}

int main() {
	// The two guest lines of log_w144_00 / log_v144_09 (F5b RC2): empty name first, then the level.
	Case("empty name, newline", "Level has started: \n", false);
	Case("level name, newline", "Level has started: underwater_aerial_garden\n", true);
	Case("level name rocket_hourglass", "Level has started: rocket_hourglass\n", true);
	// Item 280(v) cases: empty name, name, name with trailing blanks.
	Case("empty name, no newline", "Level has started: ", false);
	Case("name, no newline", "Level has started: x", true);
	Case("name with trailing spaces", "Level has started: rocket_hourglass   \n", true);
	Case("name with trailing CR LF", "Level has started: rocket_hourglass\r\n", true);
	Case("blanks only (spaces, tab, CR)", "Level has started:   \t \r\n", false);
	Case("name after extra spaces", "Level has started:    sky_garden\n", true);
	// The name must be on the same line as the prefix.
	Case("empty line, text on next line", "Level has started: \nsomething else\n", false);
	// Several lines in one write: any entry line with a name arms.
	Case("empty then named in one text", "Level has started: \nLevel has started: sky_garden\n", true);
	Case("named then empty in one text", "Level has started: sky_garden\nLevel has started: \n", true);
	// Prefix inside a longer line (the guest may prefix its log lines).
	Case("prefixed named line", "[game] Level has started: sky_garden\n", true);
	Case("prefixed empty line", "[game] Level has started: \n", false);
	// No prefix / prefix without the trailing space.
	Case("no prefix", "Level loaded: sky_garden\n", false);
	Case("prefix without space", "Level has started:\n", false);
	Case("empty text", "", false);
	std::printf("cases=%d fail=%d\n", g_cases, g_fail);
	if (g_fail == 0) {
		std::printf("ALL OK\n");
		return 0;
	}
	return 1;
}
