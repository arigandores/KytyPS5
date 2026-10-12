"""Track M, M2b (HPP-839, ROADMAP s122 item 756(v)(2)): HLE themes T265, T272, T231 under KYTY_M_<theme> (default 0).

Usage: patch_m2b.py <source root>   (the worktree C:/kyty/m657/m2/wt or main C:/kyty/KytyPS5)
Every anchor is a sequence of whole lines and must occur exactly once; files keep their line endings (CRLF is stripped
before the search and restored after); the script writes bytes. Re-running on a patched tree fails (anchor count).
"""
import sys

ROOT = sys.argv[1].rstrip('/\\')


def load(rel):
    with open(ROOT + '/' + rel, 'rb') as f:
        raw = f.read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    return text, crlf


def save(rel, text, crlf):
    if crlf:
        text = text.replace('\n', '\r\n')
    with open(ROOT + '/' + rel, 'wb') as f:
        f.write(text.encode('utf-8'))


def L(*lines):
    return ''.join(l + '\n' for l in lines)


def replace_once(text, old, new, what):
    # old is whole lines: it must start at a line start
    count = 0
    pos = 0
    hits = []
    while True:
        i = text.find(old, pos)
        if i < 0:
            break
        if i == 0 or text[i - 1] == '\n':
            hits.append(i)
        pos = i + 1
    if len(hits) != 1:
        raise SystemExit('anchor %s: %d hits' % (what, len(hits)))
    i = hits[0]
    return text[:i] + new + text[i + len(old):]


def patch(rel, edits):
    text, crlf = load(rel)
    for what, old, new in edits:
        text = replace_once(text, old, new, rel + ':' + what)
    save(rel, text, crlf)
    print('patched', rel, len(edits), 'edits')


# ---------------------------------------------------------------- T265: libAmpr.cpp
A_INC = L('#include "common/dateTime.h"')
A_INC_N = L('#include "common/dateTime.h"',
            '#include "common/envFlag.h" // Track M, M2b (KYTY_M_T265)')
A_STD = L('#include <cstring>')
A_STD_N = L('#include <cstdlib>', '#include <cstring>')
A_MAP = L('static std::unordered_map<std::string, ResolvedPathInfo> g_resolved_paths;')
A_MAP_N = L(
    'static std::unordered_map<std::string, ResolvedPathInfo> g_resolved_paths;',
    '',
    '// Track M, M2b (T265, upstream e43aadf7; HPP-839, ROADMAP s122 item 756(v)(2)): KYTY_M_T265 (default 0), read once',
    '// per process (line MT265: mode=). At 1 the ID of a resolved path is the next value of a counter, allocated once',
    '// under g_mutex when the path enters g_resolved_paths (two paths with the same 31-bit FNV-1a of ComputeFileId then',
    '// get two IDs - at 0 the second path replaced the host path and the size of the first); 0xffffffff is never given',
    '// (ENFILE). At 0 the ID is ComputeFileId and every resolve registers the host path again, as before.',
    'static bool MT265On() {',
    '\tstatic const bool on = [] {',
    '\t\tconst bool value = Common::EnvValueOn(std::getenv("KYTY_M_T265"));',
    '\t\tLOGF("MT265: mode=%d\\n", value ? 1 : 0);',
    '\t\treturn value;',
    '\t}();',
    '\treturn on;',
    '}',
    'static uint32_t g_m265_next_file_id = 1;')
A_RES = L('\tResolvedPathInfo  info {};',
          '\tconst std::string path(guest_path);')
A_RES_N = L('\tconst bool        m265 = MT265On(); // Track M, M2b (T265)',
            '\tResolvedPathInfo  info {};',
            '\tconst std::string path(guest_path);')
A_ID = L('\t\tinfo.file_id         = AprShared::ComputeFileId(guest_path);')
A_ID_N = L('\t\t// Track M, M2b (T265; KYTY_M_T265): at 1 the ID is given below, when the path is inserted.',
           '\t\tinfo.file_id         = m265 ? 0xffffffffu : AprShared::ComputeFileId(guest_path);')
A_REG = L('\t\t\t} else if (info.result == OK) {',
          '\t\t\t\tRegisterHostPathLocked(info.file_id, info.host_path, info.file_size, info.is_dir);')
A_REG_N = L(
    '\t\t\t} else if (info.result == OK && m265) {',
    '\t\t\t\t// Track M, M2b (T265, upstream e43aadf7; KYTY_M_T265): one ID per path, allocated once under g_mutex.',
    '\t\t\t\tif (g_m265_next_file_id == 0xffffffffu) {',
    '\t\t\t\t\tinfo.result = it->second.result = LibKernel::KERNEL_ERROR_ENFILE;',
    '\t\t\t\t} else {',
    '\t\t\t\t\tinfo.file_id = it->second.file_id = g_m265_next_file_id++;',
    '\t\t\t\t\tg_files.emplace(info.file_id, info.host_path);',
    '\t\t\t\t\tg_file_sizes.emplace(info.file_id, info.is_dir ? 0 : info.file_size);',
    '\t\t\t\t}',
    '\t\t\t} else if (info.result == OK) {',
    '\t\t\t\tRegisterHostPathLocked(info.file_id, info.host_path, info.file_size, info.is_dir);')
A_FOUND = L('\t} else if (info.result == OK) {',
            '\t\tAprShared::RegisterHostPath(info.file_id, info.host_path, info.file_size, info.is_dir);')
A_FOUND_N = L('\t} else if (info.result == OK && !m265) { // Track M, M2b (T265): at 1 the path keeps its first ID',
              '\t\tAprShared::RegisterHostPath(info.file_id, info.host_path, info.file_size, info.is_dir);')

# ---------------------------------------------------------------- T272: controller.h / controller.cpp / libPad.cpp
H_DECL = L('int KYTY_SYSV_ABI PadSetLightBar(int handle, const PadLightBarParam* param);')
H_DECL_N = L(
    'int KYTY_SYSV_ABI PadSetLightBar(int handle, const PadLightBarParam* param);',
    '// Track M, M2b (T272, upstream 3c62359e; HPP-839, ROADMAP s122 item 756(v)(2)): KYTY_M_T272 (default 0), read once',
    '// per process (Initialize; line MT272: mode=). At 1 scePadGetTriggerEffectState (libPad.cpp) answers with',
    '// PadGetTriggerEffectStateM272: the state of the last effect per trigger and the trigger travel; at 0 it stays 0.',
    'bool              MT272On();',
    'int KYTY_SYSV_ABI PadGetTriggerEffectStateM272(int handle, int32_t* state);')

C_PUB = L('\tbool SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent);')
C_PUB_N = L('\tbool SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent);',
            '\tvoid GetTriggerEffectStateM272(int32_t* state); // Track M, M2b (T272)')
C_PRIV = L('\tvoid RefreshMotion();')
C_PRIV_N = L('\tvoid RefreshMotion();',
             '\t// Track M, M2b (T272; KYTY_M_T272=1 only): recompute m_m272_state from m_m272_effect and the trigger axes; the',
             '\t// caller holds m_mutex.',
             '\tvoid UpdateTriggerEffectStateM272();')
C_MEM = L('\tstd::vector<int> m_ps5_ids;',
          '};')
C_MEM_N = L('\tstd::vector<int> m_ps5_ids;',
            '\t// Track M, M2b (T272, upstream 3c62359e): the last accepted command per trigger and the reported states',
            '\t// (written at KYTY_M_T272=1 only, under m_mutex).',
            '\tPadTriggerEffectParam m_m272_effect {};',
            '\tint32_t               m_m272_state[2] {};',
            '};')
C_FN = L('void Initialize() {',
         '\tEXIT_IF(g_controller != nullptr);')
C_FN_N = L(
    '// Track M, M2b (T272, upstream 3c62359e; HPP-839, ROADMAP s122 item 756(v)(2)): KYTY_M_T272 (default 0).',
    'bool MT272On() {',
    '\tstatic const bool on = [] {',
    '\t\tconst bool value = Common::EnvValueOn(std::getenv("KYTY_M_T272"));',
    '\t\tLOGF("MT272: mode=%d\\n", value ? 1 : 0);',
    '\t\treturn value;',
    '\t}();',
    '\treturn on;',
    '}',
    '',
    '// Track M, M2b (T272, upstream 3c62359e): the libScePad trigger effect states (the values duaLib reads from a',
    '// DualSense input report; [I] for the console).',
    'enum M272TriggerState : int32_t {',
    '\tM272_TRIGGER_STATE_OFF               = 0,',
    '\tM272_TRIGGER_STATE_FEEDBACK_STANDBY  = 1,',
    '\tM272_TRIGGER_STATE_FEEDBACK_ACTIVE   = 2,',
    '\tM272_TRIGGER_STATE_WEAPON_STANDBY    = 3,',
    '\tM272_TRIGGER_STATE_WEAPON_PULLING    = 4,',
    '\tM272_TRIGGER_STATE_WEAPON_FIRED      = 5,',
    '\tM272_TRIGGER_STATE_VIBRATION_STANDBY = 6,',
    '\tM272_TRIGGER_STATE_VIBRATION_ACTIVE  = 7,',
    '};',
    '',
    '// Track M, M2b (T272, upstream 3c62359e): the state of one trigger from its last command and its travel 0..255.',
    'static int32_t M272TriggerEffectState(const PadTriggerEffectCommand& command, int value, int32_t previous) {',
    '\t// Trigger positions use nonuniform travel ranges, with endpoints at 0 and 255.',
    '\tconst int pos = value == 0 ? 0 : value == 255 ? 9 : 1 + value / 32;',
    '\tswitch (command.mode) {',
    '\t\tcase 1: // feedback: resistance from position data[0], strength data[1]',
    '\t\t\treturn command.data[1] != 0 && pos >= command.data[0] ? M272_TRIGGER_STATE_FEEDBACK_ACTIVE',
    '\t\t\t                                                      : M272_TRIGGER_STATE_FEEDBACK_STANDBY;',
    '\t\tcase 2: // weapon: resistance from data[0], released at data[1]',
    '\t\t\tif (value < command.data[0] * 32) {',
    '\t\t\t\treturn M272_TRIGGER_STATE_WEAPON_STANDBY;',
    '\t\t\t}',
    '\t\t\treturn previous == M272_TRIGGER_STATE_WEAPON_FIRED || value >= std::min(command.data[1] * 32, 254)',
    '\t\t\t           ? M272_TRIGGER_STATE_WEAPON_FIRED',
    '\t\t\t           : M272_TRIGGER_STATE_WEAPON_PULLING;',
    '\t\tcase 3: // vibration from position data[0], amplitude data[1], frequency data[2]',
    '\t\t\treturn command.data[1] != 0 && command.data[2] != 0 && pos >= command.data[0]',
    '\t\t\t           ? M272_TRIGGER_STATE_VIBRATION_ACTIVE',
    '\t\t\t           : M272_TRIGGER_STATE_VIBRATION_STANDBY;',
    '\t\tcase 4: // multiple-position feedback: strength per position',
    '\t\t\treturn command.data[pos] != 0 ? M272_TRIGGER_STATE_FEEDBACK_ACTIVE : M272_TRIGGER_STATE_FEEDBACK_STANDBY;',
    '\t\tcase 5: // slope feedback between data[0] and data[1]',
    '\t\t\treturn pos >= command.data[0] && pos < command.data[1] ? M272_TRIGGER_STATE_FEEDBACK_ACTIVE',
    '\t\t\t                                                       : M272_TRIGGER_STATE_FEEDBACK_STANDBY;',
    '\t\tcase 6: // multiple-position vibration: frequency data[0], amplitude per position',
    '\t\t\treturn command.data[0] != 0 && command.data[1 + pos] != 0 ? M272_TRIGGER_STATE_VIBRATION_ACTIVE',
    '\t\t\t                                                         : M272_TRIGGER_STATE_VIBRATION_STANDBY;',
    '\t\tdefault: return M272_TRIGGER_STATE_OFF;',
    '\t}',
    '}',
    '',
    'void Initialize() {',
    '\tEXIT_IF(g_controller != nullptr);',
    '',
    '\t(void)MT272On(); // Track M, M2b (T272): the knob is read before the guest threads exist')
C_ACT = L('\tm_gyro_timestamp = 0;',
          '\tif (g_pad_output != nullptr) {')
C_ACT_N = L('\tm_gyro_timestamp = 0;',
            '\tif (MT272On()) {',
            '\t\t// Track M, M2b (T272, upstream 3c62359e): a new active pad starts without trigger effects.',
            '\t\tm_m272_effect   = {};',
            '\t\tm_m272_state[0] = 0;',
            '\t\tm_m272_state[1] = 0;',
            '\t}',
            '\tif (g_pad_output != nullptr) {')
C_AXIS = L('\t\t\tm_state.buttons = value > 0 ? m_state.buttons | trigger : m_state.buttons & ~trigger;')
C_AXIS_N = L('\t\t\tm_state.buttons = value > 0 ? m_state.buttons | trigger : m_state.buttons & ~trigger;',
             '\t\t\tif (MT272On()) {',
             '\t\t\t\t// Track M, M2b (T272, upstream 3c62359e): every trigger event, so a fired weapon stays fired',
             '\t\t\t\t// when the game polls after the release starts.',
             '\t\t\t\tUpdateTriggerEffectStateM272();',
             '\t\t\t}')
C_RESET = L('\tm_state.motion_enabled = motion_enabled;')
C_RESET_N = L('\tm_state.motion_enabled = motion_enabled;',
              '\tif (MT272On()) {',
              '\t\tUpdateTriggerEffectStateM272(); // Track M, M2b (T272): the triggers are released',
              '\t}')
C_SET = L('\tif (effect.enable_bits == 0) {',
          '\t\treturn true;',
          '\t}',
          '\tif (g_fix_b24) {')
C_SET_N = L('\tif (MT272On()) {',
            '\t\t// Track M, M2b (T272, upstream 3c62359e; KYTY_M_T272): both commands are valid here - the request is',
            '\t\t// cached per trigger of its mask and the reported states are recomputed.',
            '\t\tCommon::LockGuard lock(m_mutex);',
            '\t\tfor (int i = 0; i < 2; i++) {',
            '\t\t\tif ((param.trigger_mask & (1u << i)) != 0) {',
            '\t\t\t\tm_m272_effect.trigger_mask |= static_cast<uint8_t>(1u << i);',
            '\t\t\t\tm_m272_effect.command[i] = param.command[i];',
            '\t\t\t}',
            '\t\t}',
            '\t\tUpdateTriggerEffectStateM272();',
            '\t}',
            '\tif (effect.enable_bits == 0) {',
            '\t\treturn true;',
            '\t}',
            '\tif (g_fix_b24) {')
C_METH = L('bool GameController::SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent) {')
C_METH_N = L(
    '// Track M, M2b (T272, upstream 3c62359e): the states of both triggers (KYTY_M_T272=1 only).',
    'void GameController::GetTriggerEffectStateM272(int32_t* state) {',
    '\tCommon::LockGuard lock(m_mutex);',
    '\tstate[0] = m_m272_state[0];',
    '\tstate[1] = m_m272_state[1];',
    '}',
    '',
    'void GameController::UpdateTriggerEffectStateM272() {',
    '\tfor (int i = 0; i < 2; i++) {',
    '\t\tm_m272_state[i] = M272TriggerEffectState(',
    '\t\t    m_m272_effect.command[i], m_state.axes[static_cast<int>(Controller::Axis::TriggerLeft) + i],',
    '\t\t    m_m272_state[i]);',
    '\t}',
    '}',
    '',
    'bool GameController::SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent) {')
C_END = L('} // namespace Libs::Controller')
C_END_N = L(
    '// Track M, M2b (T272, upstream 3c62359e; KYTY_M_T272=1 only): scePadGetTriggerEffectState - the handle first, then',
    '// the argument (libScePad codes), then the states of the last effects.',
    'int KYTY_SYSV_ABI PadGetTriggerEffectStateM272(int handle, int32_t* state) {',
    '\tif (handle != 1) {',
    '\t\treturn PAD_ERROR_INVALID_HANDLE;',
    '\t}',
    '\tif (state == nullptr) {',
    '\t\treturn PAD_ERROR_INVALID_ARG;',
    '\t}',
    '',
    '\tg_controller->GetTriggerEffectStateM272(state);',
    '',
    '\treturn OK;',
    '}',
    '',
    '} // namespace Libs::Controller')

P_GET = L('\tLOGF("\\t handle = %d\\n", handle);',
          '',
          '\tif (info == nullptr) {',
          '\t\treturn -2137653243; /* 0x80960005 */',
          '\t}')
P_GET_N = L('\tLOGF("\\t handle = %d\\n", handle);',
            '',
            '\tif (Controller::MT272On()) {',
            '\t\t// Track M, M2b (T272, upstream 3c62359e; KYTY_M_T272): the state of the last effect and the trigger travel.',
            '\t\treturn Controller::PadGetTriggerEffectStateM272(handle, info != nullptr ? info->state : nullptr);',
            '\t}',
            '',
            '\tif (info == nullptr) {',
            '\t\treturn -2137653243; /* 0x80960005 */',
            '\t}')

# ---------------------------------------------------------------- T231: libFont.cpp
F_INC = L('#include "common/common.h"',
          '#include "common/logging/log.h"')
F_INC_N = L('#include "common/common.h"',
            '#include "common/envFlag.h" // Track M, M2b (KYTY_M_T231)',
            '#include "common/logging/log.h"')
F_STD = L('#include <cstring>')
F_STD_N = L('#include <cstdlib>', '#include <cstring>')
F_DIM = L('constexpr int FONT_BITMAP_MAX_DIM                   = 128;')
F_DIM_N = L('constexpr int FONT_BITMAP_MAX_DIM                   = 128;',
            '// Track M, M2b (T231, upstream 58978d15): at KYTY_M_T231=1 TrueType glyphs are rasterized at the requested',
            '// size; the limit only rejects absurd scales.',
            'constexpr int FONT_GLYPH_MAX_DIM_M231 = 4096;')
F_FS = L('\tstd::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM> fallback_image;')
F_FS_N = L('\tstd::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM> fallback_image;',
           '\tstd::vector<uint8_t> fallback_image_m231; // Track M, M2b (T231): TrueType raster at KYTY_M_T231=1')
F_GS = L('\tstd::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM> image;')
F_GS_N = L('\tstd::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM> image;',
           '\tstd::vector<uint8_t> image_m231; // Track M, M2b (T231): TrueType raster at KYTY_M_T231=1')
F_KNOB = L('static float stb_font_pixel_height(const FontState* font) {')
F_KNOB_N = L(
    '// Track M, M2b (T231, upstream f96a14a0 + 58978d15; HPP-839, ROADMAP s122 item 756(v)(2)): KYTY_M_T231 (default 0),',
    '// read once per process (line MT231: mode=). At 1 a TrueType glyph is measured and rasterized in the em scale of',
    '// scale_w / scale_h (stbtt_ScaleForMappingEmToPixels) with no 8..128 clamp: the raster buffer grows to the glyph',
    '// box (limit FONT_GLYPH_MAX_DIM_M231) and width_byte is the glyph width; the horizontal layout uses the em scale',
    '// of scale_h. At 0 the pixel height is scale_h clamped to 8..128 over ascent - descent, as before. The VGA',
    '// fallback keeps its 128-pixel buffer at both values.',
    'static bool MT231On() {',
    '\tstatic const bool on = [] {',
    '\t\tconst bool value = Common::EnvValueOn(std::getenv("KYTY_M_T231"));',
    '\t\tLOGF("MT231: mode=%d\\n", value ? 1 : 0);',
    '\t\treturn value;',
    '\t}();',
    '\treturn on;',
    '}',
    '',
    'static float stb_font_pixel_height(const FontState* font) {')
F_MET = L('\tcode              = stb_supported_codepoint(font, code);',
          '\tconst float scale = stb_font_scale(font);',
          '',
          '\tint advance = 0;')
F_MET_N = L('\tif (MT231On()) {',
            '\t\t// Track M, M2b (T231, upstream f96a14a0; KYTY_M_T231): metrics in the em scale of scale_w / scale_h.',
            '\t\tcode                = stb_supported_codepoint(font, code);',
            '\t\tconst float scale_x = stbtt_ScaleForMappingEmToPixels(&font->font_info, font->scale_w);',
            '\t\tconst float scale_y = stbtt_ScaleForMappingEmToPixels(&font->font_info, font->scale_h);',
            '',
            '\t\tint advance = 0;',
            '\t\tint x0      = 0;',
            '\t\tint y0      = 0;',
            '\t\tint x1      = 0;',
            '\t\tint y1      = 0;',
            '\t\tstbtt_GetCodepointHMetrics(&font->font_info, static_cast<int>(code), &advance, nullptr);',
            '\t\tstbtt_GetCodepointBox(&font->font_info, static_cast<int>(code), &x0, &y0, &x1, &y1);',
            '',
            '\t\tmetrics->width                = static_cast<float>(x1 - x0) * scale_x;',
            '\t\tmetrics->height               = static_cast<float>(y1 - y0) * scale_y;',
            '\t\tmetrics->horizontal.bearing_x = static_cast<float>(x0) * scale_x;',
            '\t\tmetrics->horizontal.bearing_y = static_cast<float>(y1) * scale_y;',
            '\t\tmetrics->horizontal.advance   = static_cast<float>(advance) * scale_x;',
            '\t\tmetrics->vertical.bearing_x   = 0.0f;',
            '\t\tmetrics->vertical.bearing_y   = 0.0f;',
            '\t\tmetrics->vertical.advance     = font->scale_h;',
            '',
            '\t\treturn true;',
            '\t}',
            '',
            '\tcode              = stb_supported_codepoint(font, code);',
            '\tconst float scale = stb_font_scale(font);',
            '',
            '\tint advance = 0;')
F_IMG = L('static bool init_stb_image(std::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM>* image,',
          '                           FontTransImage* trans_image, uint32_t code, FontState* font) {',
          '\tif (image == nullptr || trans_image == nullptr || !ensure_stb_font(font)) {',
          '\t\treturn false;',
          '\t}')
F_IMG_N = L('static bool init_stb_image(std::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM>* image,',
            '                           FontTransImage* trans_image, uint32_t code, FontState* font,',
            '                           std::vector<uint8_t>* image_m231) {',
            '\tif (image == nullptr || trans_image == nullptr || !ensure_stb_font(font)) {',
            '\t\treturn false;',
            '\t}',
            '',
            '\tif (MT231On() && image_m231 != nullptr) {',
            '\t\t// Track M, M2b (T231, upstream f96a14a0 + 58978d15; KYTY_M_T231): the glyph at the requested em scale in a',
            '\t\t// buffer of its own box; width_byte is the glyph width.',
            '\t\tcode                = stb_supported_codepoint(font, code);',
            '\t\tconst float scale_x = stbtt_ScaleForMappingEmToPixels(&font->font_info, font->scale_w);',
            '\t\tconst float scale_y = stbtt_ScaleForMappingEmToPixels(&font->font_info, font->scale_h);',
            '',
            '\t\tint x0 = 0;',
            '\t\tint y0 = 0;',
            '\t\tint x1 = 0;',
            '\t\tint y1 = 0;',
            '\t\tstbtt_GetCodepointBitmapBox(&font->font_info, static_cast<int>(code), scale_x, scale_y, &x0, &y0,',
            '\t\t                            &x1, &y1);',
            '',
            '\t\tconst auto width  = static_cast<uint32_t>(std::clamp(x1 - x0, 0, FONT_GLYPH_MAX_DIM_M231));',
            '\t\tconst auto height = static_cast<uint32_t>(std::clamp(y1 - y0, 0, FONT_GLYPH_MAX_DIM_M231));',
            '\t\t// Keep at least one byte so that blank glyphs still get a valid address.',
            '\t\timage_m231->assign(std::max<size_t>(static_cast<size_t>(width) * height, 1), 0);',
            '\t\ttrans_image->address      = image_m231->data();',
            '\t\ttrans_image->width_byte   = width;',
            '\t\ttrans_image->image_width  = width;',
            '\t\ttrans_image->image_height = height;',
            '',
            '\t\tif (width == 0 || height == 0) {',
            '\t\t\treturn true;',
            '\t\t}',
            '',
            '\t\tstbtt_MakeCodepointBitmap(&font->font_info, image_m231->data(), static_cast<int>(width),',
            '\t\t                          static_cast<int>(height), static_cast<int>(width), scale_x, scale_y,',
            '\t\t                          static_cast<int>(code));',
            '',
            '\t\treturn true;',
            '\t}')
F_INIT = L('static void init_image(std::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM>* image,',
           '                       FontTransImage* trans_image, uint32_t code, const FontState* font) {')
F_INIT_N = L('static void init_image(std::array<uint8_t, FONT_BITMAP_MAX_DIM * FONT_BITMAP_MAX_DIM>* image,',
             '                       FontTransImage* trans_image, uint32_t code, const FontState* font,',
             '                       std::vector<uint8_t>* image_m231) {')
F_CALL = L('\tif (init_stb_image(image, trans_image, code, const_cast<FontState*>(font))) {')
F_CALL_N = L('\tif (init_stb_image(image, trans_image, code, const_cast<FontState*>(font), image_m231)) {')
F_C1 = L("\tinit_image(&state->fallback_image, &state->trans_image, static_cast<uint32_t>('?'), state);")
F_C1_N = L("\tinit_image(&state->fallback_image, &state->trans_image, static_cast<uint32_t>('?'), state,",
           '\t           &state->fallback_image_m231);')
F_C2 = L('\tinit_image(&glyph->image, &glyph->trans_image, code, font);')
F_C2_N = L('\tinit_image(&glyph->image, &glyph->trans_image, code, font, &glyph->image_m231);')
F_C3 = L('\tinit_image(&font->fallback_image, &font->trans_image, code, font);')
F_C3_N = L('\tinit_image(&font->fallback_image, &font->trans_image, code, font, &font->fallback_image_m231);')
F_LAY = L('\t\tconst float scale    = stb_font_scale(font);')
F_LAY_N = L('\t\t// Track M, M2b (T231, upstream f96a14a0; KYTY_M_T231): at 1 the em scale of scale_h.',
            '\t\tconst float scale    = MT231On() ? stbtt_ScaleForMappingEmToPixels(&font->font_info, font->scale_h)',
            '\t\t                                 : stb_font_scale(font);')

# ---------------------------------------------------------------- CMakeLists.txt: the stand target
M_ANCHOR = L('add_kyty_full_emulator_test(shader_cfg_tests "${KYTY_TESTS_DIR}/shaderCfgTests.cpp")')
M_ANCHOR_N = L(
    'add_kyty_full_emulator_test(shader_cfg_tests "${KYTY_TESTS_DIR}/shaderCfgTests.cpp")',
    '',
    '# Track M, M2b (HPP-839, ROADMAP s122 item 756(v)(2)): stand of the HLE themes T265, T272, T231 of upstream wave 1',
    '# (KYTY_M_T265, KYTY_M_T272, KYTY_M_T231); run by C:/kyty/m657/m2b/run_stand_m2b.py, not by ctest.',
    'add_kyty_full_emulator_test(m_wave1_hle_stand "${KYTY_TESTS_DIR}/MWave1HleStand.cpp")')


def main():
    patch('src/libs/libAmpr.cpp', [
        ('inc', A_INC, A_INC_N), ('std', A_STD, A_STD_N), ('map', A_MAP, A_MAP_N), ('res', A_RES, A_RES_N),
        ('id', A_ID, A_ID_N), ('reg', A_REG, A_REG_N), ('found', A_FOUND, A_FOUND_N)])
    patch('src/libs/controller.h', [('decl', H_DECL, H_DECL_N)])
    patch('src/libs/controller.cpp', [
        ('pub', C_PUB, C_PUB_N), ('priv', C_PRIV, C_PRIV_N), ('mem', C_MEM, C_MEM_N), ('fn', C_FN, C_FN_N),
        ('act', C_ACT, C_ACT_N), ('axis', C_AXIS, C_AXIS_N), ('reset', C_RESET, C_RESET_N), ('set', C_SET, C_SET_N),
        ('meth', C_METH, C_METH_N), ('end', C_END, C_END_N)])
    patch('src/libs/libPad.cpp', [('get', P_GET, P_GET_N)])
    patch('src/libs/libFont.cpp', [
        ('inc', F_INC, F_INC_N), ('std', F_STD, F_STD_N), ('dim', F_DIM, F_DIM_N), ('fs', F_FS, F_FS_N),
        ('gs', F_GS, F_GS_N), ('knob', F_KNOB, F_KNOB_N), ('met', F_MET, F_MET_N), ('img', F_IMG, F_IMG_N),
        ('init', F_INIT, F_INIT_N), ('call', F_CALL, F_CALL_N), ('c1', F_C1, F_C1_N), ('c2', F_C2, F_C2_N),
        ('c3', F_C3, F_C3_N), ('lay', F_LAY, F_LAY_N)])
    patch('CMakeLists.txt', [('stand', M_ANCHOR, M_ANCHOR_N)])
    print('ALL OK')


if __name__ == '__main__':
    main()
