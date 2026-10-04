# F19c2 (HPP-559, ROADMAP s122 item 460(v)(2), (4)): two new cases of the F19c stand tests/B24PadStand.cpp (target
# b24_pad_stand, the same controller.cpp of the build, not a copy):
#   dd   - KYTY_FIX_B24=1: X holds SDL_LockJoysticks 300 ms while PadOutput applies a vibration; two threads released by
#          one barrier call Controller::EmergencyShutdown at the same time; "both_returned=1" when both came back; then
#          Controller::Shutdown. One cycle per process (the driver runs 1 000 processes).
#   trig - positive control of the trigger effect path (N2 of F19d): the virtual pad has vendor_id 0x054C / product_id
#          0x0CE6; the pad type SDL reports is printed; X holds the lock 3000 ms, Y calls PadSetTriggerEffect twice (A, B)
#          200 ms after X has it; walls, the SendEffect count after the unlock, the last payload vs the payload of B.
# Every case: a crash prints a marker line (terminate=1 / abort=1) and exits 3, with no dialog.
# Anchors are whole lines / whole blocks, each must occur exactly once; CRLF-safe; indentation: 4 spaces -> 1 tab.
# Usage: python patch_f19c2_stand.py <repo root>
import re
import sys

root = sys.argv[1].rstrip('/')
path = root + '/tests/B24PadStand.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
s = raw.decode('utf-8').replace('\r\n', '\n')


def tabs(block):
    out = []
    for line in block.split('\n'):
        m = re.match(r'^( {4})+', line)
        if m:
            k = len(m.group(0)) // 4
            line = '\t' * k + line[4 * k:]
        out.append(line)
    return '\n'.join(out)


edits = []

# 1. header: the new cases
edits.append((
    "// Exit 0 unless the arguments are bad (2) or SDL fails to start (4).\n",
    r'''// Exit 0 unless the arguments are bad (2) or SDL fails to start (4).
//
// F19c2 (HPP-559, ROADMAP s122 item 460(v)(2), (4)) - two more cases; driver docs/track-f/f19c2/run_stand_f19c2.py:
//   dd   - KYTY_FIX_B24=1, RC1 of the F19d review: X holds SDL_LockJoysticks DD_HOLD_MS; one PadSetVibration puts
//          PadOutput into its application (it waits for the lock); DD_WRITE_MS later two threads released by one barrier
//          call Controller::EmergencyShutdown at the same time; "both_returned=1" when both came back; then
//          Controller::Shutdown (a third EmergencyShutdown and the deletes). One cycle per process.
//   trig - the trigger effect path (N2 of F19d): the virtual pad has vendor_id 0x054C / product_id 0x0CE6 (pad_type is
//          the SDL_GameControllerGetType value, pad_type_ps5 whether it is SDL_CONTROLLER_TYPE_PS5); X holds the lock
//          HOLD_MS, Y calls PadSetTriggerEffect with effect A then effect B Y_DELAY_MS after X has it (walls); after the
//          unlock - the SendEffect count, and the last payload compared with the payload of B sent again with the lock
//          free (A sent again too: the two payloads must differ). "sent=" is in the PadTriggerEffect: lines.
// A crash of a stand process (std::terminate, abort) prints terminate=1 / abort=1 and exits 3 without a dialog.
'''))

# 2. includes
edits.append((
    "#include <cstring>\n",
    "#include <csignal>\n#include <cstring>\n#include <exception>\n#include <mutex>\n"))
edits.append((
    "#include <thread>\n",
    "#include <thread>\n#include <vector>\n"))

# 3. globals after the effect counter
edits.append((
    "std::atomic<uint64_t> g_effect_calls {0};\n",
    tabs(r'''std::atomic<uint64_t> g_effect_calls {0};
// F19c2: the last SendEffect payload of the virtual pad; vendor / product of the next attach (0 - as F19c).
std::mutex           g_effect_mutex;
std::vector<uint8_t> g_effect_last;
Uint16               g_vp_vendor  = 0;
Uint16               g_vp_product = 0;
''')))

# 4. SendEffect callback keeps the payload
edits.append((
    tabs(r'''int SDLCALL VpSendEffect(void* /*userdata*/, const void* /*data*/, int /*size*/) {
    g_effect_calls.fetch_add(1);
    return 0;
}
'''),
    tabs(r'''int SDLCALL VpSendEffect(void* /*userdata*/, const void* data, int size) {
    {
        std::lock_guard lock(g_effect_mutex);
        const auto*     bytes = static_cast<const uint8_t*>(data);
        g_effect_last.assign(bytes, bytes + (size > 0 ? size : 0));
    }
    g_effect_calls.fetch_add(1);
    return 0;
}
''')))

# 5. vendor / product of the virtual pad
edits.append((
    "\tdesc.SendEffect = VpSendEffect;\n",
    "\tdesc.SendEffect = VpSendEffect;\n\tdesc.vendor_id  = g_vp_vendor;\n\tdesc.product_id = g_vp_product;\n"))

# 6. the new cases, before the end of the anonymous namespace
edits.append((
    "} // namespace\n\nint main(int argc, char** argv) {\n",
    tabs(r'''// F19c2: a crash is counted by the driver - a marker line and exit 3, no dialog (the std::terminate handler is per
// thread in the MSVC runtime: every stand thread that calls into controller.cpp sets it).
[[noreturn]] void OnTerminate() {
    std::printf("terminate=1\n");
    std::fflush(stdout);
    std::_Exit(3);
}

void OnAbort(int /*sig*/) {
    std::printf("abort=1\n");
    std::fflush(stdout);
    std::_Exit(3);
}

void InstallCrashMarkers() {
#ifdef _MSC_VER
    _set_abort_behavior(0, _WRITE_ABORT_MSG | _CALL_REPORTFAULT);
#endif
    std::signal(SIGABRT, OnAbort);
    std::set_terminate(OnTerminate);
}

constexpr uint32_t DD_HOLD_MS  = 300;
constexpr uint32_t DD_WRITE_MS = 20;

// Case dd (F19c2, item 460(v)(2)).
void DoubleShutdownCase() {
    std::atomic<bool>     locked {false};
    std::atomic<uint64_t> unlock_us {0};
    std::thread           x([&] {
        std::set_terminate(OnTerminate);
        SDL_LockJoysticks();
        locked.store(true);
        std::this_thread::sleep_for(std::chrono::milliseconds(DD_HOLD_MS));
        unlock_us.store(NowUs());
        SDL_UnlockJoysticks();
    });
    while (!locked.load()) {
        std::this_thread::yield();
    }
    Vibrate(0x12, 0x34);
    std::this_thread::sleep_for(std::chrono::milliseconds(DD_WRITE_MS));
    std::atomic<int>  ready {0};
    std::atomic<bool> go {false};
    uint64_t          start[2] = {};
    uint64_t          done[2]  = {};
    const auto        caller   = [&](int k) {
        std::set_terminate(OnTerminate);
        ready.fetch_add(1);
        while (!go.load()) {
        }
        start[k] = NowUs();
        Controller::EmergencyShutdown();
        done[k] = NowUs();
    };
    std::thread a(caller, 0);
    std::thread b(caller, 1);
    while (ready.load() != 2) {
        std::this_thread::yield();
    }
    go.store(true);
    a.join();
    b.join();
    x.join();
    std::printf("both_returned=1\n");
    const uint64_t first = start[0] < start[1] ? start[0] : start[1];
    const uint64_t last  = start[0] < start[1] ? start[1] : start[0];
    std::printf("call_a_wall_us=%llu\ncall_b_wall_us=%llu\nstart_skew_us=%llu\ncalls_started_before_unlock=%d\n",
                static_cast<unsigned long long>(done[0] - start[0]), static_cast<unsigned long long>(done[1] - start[1]),
                static_cast<unsigned long long>(last - first), last < unlock_us.load() ? 1 : 0);
}

std::vector<uint8_t> EffectLast() {
    std::lock_guard lock(g_effect_mutex);
    return g_effect_last;
}

// Waits up to 1 s for the SendEffect count to reach n; returns the time it was seen (0 if never).
uint64_t WaitEffects(uint64_t n) {
    const uint64_t t0 = NowUs();
    while (NowUs() - t0 < 1000000) {
        if (g_effect_calls.load() >= n) {
            return NowUs();
        }
        std::this_thread::sleep_for(std::chrono::microseconds(200));
    }
    return 0;
}

// Effect A - left trigger, effect B - right trigger (mode 1, as case ii): different payloads.
Controller::PadTriggerEffectParam TriggerParam(bool right) {
    Controller::PadTriggerEffectParam p {};
    const int                         k = right ? 1 : 0;
    p.trigger_mask                      = right ? 0x02 : 0x01;
    p.command[k].mode                   = 1;
    p.command[k].data[0]                = right ? 3 : 2;
    p.command[k].data[1]                = right ? 7 : 5;
    return p;
}

// Case trig (F19c2, item 460(v)(4)).
void TriggerCase() {
    auto* pad = SDL_GameControllerFromInstanceID(g_connected_id);
    const int type = pad != nullptr ? static_cast<int>(SDL_GameControllerGetType(pad)) : -1;
    std::printf("pad_vendor=0x%04x\npad_product=0x%04x\npad_type=%d\npad_type_ps5=%d\n",
                pad != nullptr ? SDL_GameControllerGetVendor(pad) : 0, pad != nullptr ? SDL_GameControllerGetProduct(pad) : 0,
                type, type == static_cast<int>(SDL_CONTROLLER_TYPE_PS5) ? 1 : 0);
    const auto a_param = TriggerParam(false);
    const auto b_param = TriggerParam(true);
    std::atomic<bool>     locked {false};
    std::atomic<uint64_t> unlock_us {0};
    std::atomic<uint64_t> calls_before_unlock {0};
    std::thread           x([&] {
        SDL_LockJoysticks();
        locked.store(true);
        std::this_thread::sleep_for(std::chrono::milliseconds(HOLD_MS));
        calls_before_unlock.store(g_effect_calls.load());
        unlock_us.store(NowUs());
        SDL_UnlockJoysticks();
    });
    while (!locked.load()) {
        std::this_thread::yield();
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(Y_DELAY_MS));
    uint64_t wall_a = 0;
    uint64_t wall_b = 0;
    bool     ok_a   = false;
    bool     ok_b   = false;
    std::thread y([&] {
        std::set_terminate(OnTerminate);
        uint64_t t0 = NowUs();
        ok_a        = Controller::PadSetTriggerEffect(PAD_HANDLE, &a_param) == 0;
        wall_a      = NowUs() - t0;
        t0          = NowUs();
        ok_b        = Controller::PadSetTriggerEffect(PAD_HANDLE, &b_param) == 0;
        wall_b      = NowUs() - t0;
    });
    y.join();
    const uint64_t y_done_us = NowUs();
    x.join();
    const uint64_t seen = WaitEffects(1);
    std::this_thread::sleep_for(std::chrono::milliseconds(300));
    const uint64_t             calls_after = g_effect_calls.load();
    const std::vector<uint8_t> last        = EffectLast();
    // The payloads of A and B with the lock free (the reference for "last applied = last written").
    Controller::PadTriggerEffectParam ref = a_param;
    Controller::PadSetTriggerEffect(PAD_HANDLE, &ref);
    const bool                 seen_a = WaitEffects(calls_after + 1) != 0;
    const std::vector<uint8_t> pa     = EffectLast();
    ref                               = b_param;
    Controller::PadSetTriggerEffect(PAD_HANDLE, &ref);
    const bool                 seen_b = WaitEffects(calls_after + 2) != 0;
    const std::vector<uint8_t> pb     = EffectLast();
    std::printf("wall_trig_a_us=%llu\nwall_trig_b_us=%llu\ntrig_ok=%d\ny_done_before_unlock=%d\n",
                static_cast<unsigned long long>(wall_a), static_cast<unsigned long long>(wall_b), ok_a && ok_b ? 1 : 0,
                y_done_us < unlock_us.load() ? 1 : 0);
    std::printf("effect_calls_before_unlock=%llu\neffect_calls_after_unlock=%llu\neffect_latency_us=%lld\n",
                static_cast<unsigned long long>(calls_before_unlock.load()), static_cast<unsigned long long>(calls_after),
                seen == 0 ? -1LL : static_cast<long long>(seen - unlock_us.load()));
    std::printf("ref_seen=%d\npayload_size=%d\nlast_eq_b=%d\na_ne_b=%d\n", seen_a && seen_b ? 1 : 0,
                static_cast<int>(last.size()), !last.empty() && last == pb ? 1 : 0, pa != pb ? 1 : 0);
}

} // namespace

int main(int argc, char** argv) {
''')))

# 7. arguments
edits.append((
    tabs(r'''    if (argc != 2 || (std::strcmp(argv[1], "i") != 0 && std::strcmp(argv[1], "ii") != 0 && std::strcmp(argv[1], "iii") != 0)) {
        std::fprintf(stderr, "usage: b24_pad_stand i|ii|iii\n");
        return 2;
    }
    const std::string mode = argv[1];
'''),
    tabs(r'''    if (argc != 2 || (std::strcmp(argv[1], "i") != 0 && std::strcmp(argv[1], "ii") != 0 && std::strcmp(argv[1], "iii") != 0 &&
                      std::strcmp(argv[1], "dd") != 0 && std::strcmp(argv[1], "trig") != 0)) {
        std::fprintf(stderr, "usage: b24_pad_stand i|ii|iii|dd|trig\n");
        return 2;
    }
    const std::string mode = argv[1];
    InstallCrashMarkers();
''')))

# 8. trig attaches a pad with the DualSense vendor / product
edits.append((
    tabs(r'''    const bool connected = AttachConnected();
    std::printf("connected=%d\n", connected ? 1 : 0);
'''),
    tabs(r'''    if (mode == "trig") {
        g_vp_vendor  = 0x054C;
        g_vp_product = 0x0CE6;
    }
    const bool connected = AttachConnected();
    std::printf("connected=%d\n", connected ? 1 : 0);
''')))

# 9. dispatch and teardown
edits.append((
    tabs(r'''        if (mode == "iii") {
            ChurnCase();
        } else {
            HoldCase(mode == "ii");
        }
    }
    Controller::TestHidLossWindow(false);
    PrintStats();
    Controller::EmergencyShutdown();
'''),
    tabs(r'''        if (mode == "iii") {
            ChurnCase();
        } else if (mode == "dd") {
            DoubleShutdownCase();
        } else if (mode == "trig") {
            TriggerCase();
        } else {
            HoldCase(mode == "ii");
        }
    }
    Controller::TestHidLossWindow(false);
    PrintStats();
    if (mode == "dd") {
        // F19c2: the two emergency exits already ran - the normal teardown (a third EmergencyShutdown, the deletes).
        Controller::Shutdown();
    } else {
        Controller::EmergencyShutdown();
    }
''')))

for old, new in edits:
    n = s.count(old)
    if n != 1:
        sys.exit('anchor count %d: %r' % (n, old[:90]))
    s = s.replace(old, new)

out = s.replace('\n', '\r\n') if crlf else s
open(path, 'wb').write(out.encode('utf-8'))
print('patched', path, 'crlf' if crlf else 'lf')
