"""Track M, M6a2 (HPP-854, ROADMAP s122 item 770(b)-(e)): stand tests/MWave2DiagStand.cpp for the M6a2 fields.
Usage: patch_m6a2_stand.py <source root>. Whole-line anchors, each exactly once.
- the pure and audio arms bring up guest memory (Memory lifecycle + KernelMapNamedFlexibleMemory) and keep the object
  PCM there (the object grain is read through TryReadBacking since M6a2);
- pure: ao_obj_unread (unreadable pointer 0x1000), clr_dw_div8 (R8Unorm and R8G8Unorm, >= 1 and 0 each),
  minlod_div_x (cases (2, 2, 384) and (1, 3, 768)), inv_part_src;
- audio: push 4 - the object port points to 0x1000: at =1 ao_obj_unread 1, ao_obj_nz 0, process alive; at =0 all 0.
"""
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from patch_m6a2 import apply, t  # noqa: E402

S = []

# includes
S.append(([
    '#include "common/threads.h"',
], [
    '#include "common/threads.h"',
    '#include "kernel/memory.h"',
]))

# Field()
S.append(([
    t(1, 'if (f == "pushes") return t.pushes;'),
], [
    t(1, 'if (f == "pushes") return t.pushes;'),
    t(1, 'if (f == "minlod_div_x") return t.minlod_div_x;'),
    t(1, 'if (f == "clr_dw_div8") return t.clr_dw_div8;'),
    t(1, 'if (f == "ao_obj_unread") return t.ao_obj_unread;'),
    t(1, 'if (f == "inv_part_src") return t.inv_part_src;'),
]))

# guest memory helper before ArmPure
S.append(([
    '// ------------------------------------------------------------------------------------------------ pure',
    'int ArmPure() {',
    t(1, 'const std::vector<float>   f_nz {0.0f, 0.0f, 0.25f, 0.0f};'),
    t(1, 'const std::vector<float>   f_z(4, 0.0f);'),
    t(1, 'const std::vector<int16_t> s_nz {0, 0, 0, 7};'),
    t(1, 'const std::vector<int16_t> s_z(4, 0);'),
], [
    '// M6a2: guest memory for object PCM (the object grain is read through TryReadBacking since M6a2). One flexible',
    '// mapping of 256 KiB, CPU read/write, handed out in 4 KiB-aligned pieces.',
    'uint8_t* GuestAlloc(size_t size) {',
    t(1, 'static uint8_t* base = nullptr;'),
    t(1, 'static size_t   used = 0;'),
    t(1, 'constexpr size_t TOTAL = 0x40000;'),
    t(1, 'if (base == nullptr) {'),
    t(2, 'void*     addr = nullptr;'),
    t(2, 'const int rc   = Libs::LibKernel::Memory::KernelMapNamedFlexibleMemory(&addr, TOTAL, 0x3, 0, "m6a2stand");'),
    t(2, 'if (rc != 0 || addr == nullptr) {'),
    t(3, 'std::printf("MStand: m6 guest map failed rc=%d\\n", rc);'),
    t(3, 'std::fflush(stdout);'),
    t(3, 'std::_Exit(3);'),
    t(2, '}'),
    t(2, 'base = static_cast<uint8_t*>(addr);'),
    t(2, 'std::memset(base, 0, TOTAL);'),
    t(1, '}'),
    t(1, 'const size_t aligned = (size + 0xfffu) & ~size_t {0xfff};'),
    t(1, 'if (used + aligned > TOTAL) {'),
    t(2, 'std::printf("MStand: m6 guest memory exhausted\\n");'),
    t(2, 'std::fflush(stdout);'),
    t(2, 'std::_Exit(3);'),
    t(1, '}'),
    t(1, 'uint8_t* p = base + used;'),
    t(1, 'used += aligned;'),
    t(1, 'return p;'),
    '}',
    '',
    'template <typename V>',
    'V* GuestCopy(const std::vector<V>& v) {',
    t(1, 'auto* p = reinterpret_cast<V*>(GuestAlloc(v.size() * sizeof(V)));'),
    t(1, 'std::memcpy(p, v.data(), v.size() * sizeof(V));'),
    t(1, 'return p;'),
    '}',
    '',
    '// M6a2: a pointer no guest mapping covers (and no host page either) - the guarded reader refuses it.',
    'const void* const UNREADABLE = reinterpret_cast<const void*>(uintptr_t {0x1000});',
    '',
    '// ------------------------------------------------------------------------------------------------ pure',
    'int ArmPure() {',
    t(1, '// M6a2: the PCM of every object case lives in guest memory; bus cases keep host memory (raw read).'),
    t(1, 'const float*   f_nz = GuestCopy(std::vector<float> {0.0f, 0.0f, 0.25f, 0.0f});'),
    t(1, 'const float*   f_z  = GuestCopy(std::vector<float>(4, 0.0f));'),
    t(1, 'const int16_t* s_nz = GuestCopy(std::vector<int16_t> {0, 0, 0, 7});'),
    t(1, 'const int16_t* s_z  = GuestCopy(std::vector<int16_t>(4, 0));'),
    t(1, 'const std::vector<float> hf_nz {0.0f, 0.0f, 0.25f, 0.0f};'),
    t(1, 'const std::vector<float> hf_z(4, 0.0f);'),
]))

# T125 pure cases
S.append(([
    t(1, 'Check("ao_obj_nz_float", [&] { D::NoteAudioPort(true, f_nz.data(), 0x100, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 1}, {"ao_bus_push", 0}, {"ao_bus_nz", 0}});'),
    t(1, 'Check("ao_obj_zero_float", [&] { D::NoteAudioPort(true, f_z.data(), 0x100, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}});'),
    t(1, 'Check("ao_obj_nz_int16", [&] { D::NoteAudioPort(true, s_nz.data(), 0x101, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 1}});'),
    t(1, 'Check("ao_obj_zero_int16", [&] { D::NoteAudioPort(true, s_z.data(), 0x101, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}});'),
    t(1, 'Check("ao_bus_nz", [&] { D::NoteAudioPort(false, f_nz.data(), 0x100, 4); },'),
    t(1, '      {{"ao_bus_push", 1}, {"ao_bus_nz", 1}, {"ao_obj_push", 0}, {"ao_obj_nz", 0}});'),
    t(1, 'Check("ao_bus_zero", [&] { D::NoteAudioPort(false, f_z.data(), 0x100, 4); },'),
    t(1, '      {{"ao_bus_push", 1}, {"ao_bus_nz", 0}});'),
], [
    t(1, 'Check("ao_obj_nz_float", [&] { D::NoteAudioPort(true, f_nz, 0x100, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 1}, {"ao_obj_unread", 0}, {"ao_bus_push", 0}, {"ao_bus_nz", 0}});'),
    t(1, 'Check("ao_obj_zero_float", [&] { D::NoteAudioPort(true, f_z, 0x100, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}, {"ao_obj_unread", 0}});'),
    t(1, 'Check("ao_obj_nz_int16", [&] { D::NoteAudioPort(true, s_nz, 0x101, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 1}, {"ao_obj_unread", 0}});'),
    t(1, 'Check("ao_obj_zero_int16", [&] { D::NoteAudioPort(true, s_z, 0x101, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}, {"ao_obj_unread", 0}});'),
    t(1, '// M6a2 (item 770(g)): an unreadable object pointer - counted, not read, the process lives.'),
    t(1, 'Check("ao_obj_unread", [&] { D::NoteAudioPort(true, UNREADABLE, 0x100, 4); },'),
    t(1, '      {{"ao_obj_push", 1}, {"ao_obj_unread", 1}, {"ao_obj_nz", 0}});'),
    t(1, 'Check("ao_bus_nz", [&] { D::NoteAudioPort(false, hf_nz.data(), 0x100, 4); },'),
    t(1, '      {{"ao_bus_push", 1}, {"ao_bus_nz", 1}, {"ao_obj_push", 0}, {"ao_obj_nz", 0}, {"ao_obj_unread", 0}});'),
    t(1, 'Check("ao_bus_zero", [&] { D::NoteAudioPort(false, hf_z.data(), 0x100, 4); },'),
    t(1, '      {{"ao_bus_push", 1}, {"ao_bus_nz", 0}});'),
]))

# T313 + T179 cases: add clr_dw_div8 0 to every old case, then 4 new cases
OLD_CLR = [
    ('clr_r16f_lo_ne_hi', 'eR16Sfloat', '0x00003c00u', '1'),
    ('clr_r16f_lo_eq_hi', 'eR16Sfloat', '0x3c003c00u', '0'),
    ('clr_r16unorm_lo_ne_hi', 'eR16Unorm', '0x0000ffffu', '1'),
    ('clr_rgba16f_nz', 'eR16G16B16A16Sfloat', '0x3c003c00u', '1'),
    ('clr_rgba16f_zero', 'eR16G16B16A16Sfloat', '0u', '0'),
    ('clr_rgba16unorm_nz', 'eR16G16B16A16Unorm', '1u', '1'),
    ('clr_rg32f_nz', 'eR32G32Sfloat', '0x3f800000u', '1'),
    ('clr_rgba8_nz', 'eR8G8B8A8Unorm', '0xffffffffu', '0'),
]
old_lines = []
new_lines = []
for name, f, w, div in OLD_CLR:
    head = 'Check("%s", [&] { D::NoteClearDword(fmt(vk::Format::%s), %s); },' % (name, f, w)
    old_lines += [t(1, head), t(1, '      {{"clr_dw", 1}, {"clr_dw_div", %s}});' % div)]
    new_lines += [t(1, head), t(1, '      {{"clr_dw", 1}, {"clr_dw_div", %s}, {"clr_dw_div8", 0}});' % div)]
new_lines += [
    t(1, '// M6a2 (item 770(v)): class (a3) of M5a - R8Unorm without a repeated byte, R8G8Unorm with lo != hi.'),
    t(1, 'Check("clr_r8_div8", [&] { D::NoteClearDword(fmt(vk::Format::eR8Unorm), 0x00ff00ffu); },'),
    t(1, '      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 1}});'),
    t(1, 'Check("clr_r8_rep", [&] { D::NoteClearDword(fmt(vk::Format::eR8Unorm), 0x7f7f7f7fu); },'),
    t(1, '      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 0}});'),
    t(1, 'Check("clr_rg8_div8", [&] { D::NoteClearDword(fmt(vk::Format::eR8G8Unorm), 0x00001234u); },'),
    t(1, '      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 1}});'),
    t(1, 'Check("clr_rg8_rep", [&] { D::NoteClearDword(fmt(vk::Format::eR8G8Unorm), 0x12341234u); },'),
    t(1, '      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 0}});'),
]
S.append((old_lines, new_lines))

# T021
S.append(([
    t(1, 'Check("minlod_div", [&] { D::NoteMinLodView(3 * 256, 1, 3); }, {{"minlod_views", 1}, {"minlod_div", 1}});'),
    t(1, 'Check("minlod_base0", [&] { D::NoteMinLodView(3 * 256, 0, 3); }, {{"minlod_views", 1}, {"minlod_div", 0}});'),
    t(1, 'Check("minlod_inside", [&] { D::NoteMinLodView(2 * 256, 1, 3); }, {{"minlod_views", 1}, {"minlod_div", 0}});'),
    t(1, 'Check("minlod_zero", [&] { D::NoteMinLodView(0, 1, 3); }, {{"minlod_views", 0}, {"minlod_div", 0}});'),
], [
    t(1, '// M6a2 (item 770(b)): minlod_div_x - case (B 1, count 3, M 768) both 1; case (B 2, count 2, M 384) div 1, x 0.'),
    t(1, 'Check("minlod_div", [&] { D::NoteMinLodView(3 * 256, 1, 3); },'),
    t(1, '      {{"minlod_views", 1}, {"minlod_div", 1}, {"minlod_div_x", 1}});'),
    t(1, 'Check("minlod_div_not_x", [&] { D::NoteMinLodView(384, 2, 2); },'),
    t(1, '      {{"minlod_views", 1}, {"minlod_div", 1}, {"minlod_div_x", 0}});'),
    t(1, 'Check("minlod_base0", [&] { D::NoteMinLodView(3 * 256, 0, 3); },'),
    t(1, '      {{"minlod_views", 1}, {"minlod_div", 0}, {"minlod_div_x", 0}});'),
    t(1, 'Check("minlod_inside", [&] { D::NoteMinLodView(2 * 256, 1, 3); },'),
    t(1, '      {{"minlod_views", 1}, {"minlod_div", 0}, {"minlod_div_x", 0}});'),
    t(1, 'Check("minlod_zero", [&] { D::NoteMinLodView(0, 1, 3); },'),
    t(1, '      {{"minlod_views", 0}, {"minlod_div", 0}, {"minlod_div_x", 0}});'),
]))

# T188
S.append(([
    t(1, 'Check("inv_part_off", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x11000, 0x100); },'),
    t(1, '      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 1}});'),
    t(1, 'Check("inv_part_base", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x10000, 0x100); },'),
    t(1, '      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 0}});'),
    t(1, 'Check("inv_cover", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0xf000, 0x8000); },'),
    t(1, '      {{"inv_gpu", 1}, {"inv_part", 0}, {"inv_off", 0}});'),
    t(1, 'Check("inv_not_gpu", [&] { D::NoteInvalidateImage(false, 0x10000, 0x4000, 0x11000, 0x100); },'),
    t(1, '      {{"inv_gpu", 0}, {"inv_part", 0}, {"inv_off", 0}});'),
], [
    t(1, 'Check("inv_part_off", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x4000, 0x11000, 0x100); },'),
    t(1, '      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 1}, {"inv_part_src", 1}});'),
    t(1, 'Check("inv_part_base", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x4000, 0x10000, 0x100); },'),
    t(1, '      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 0}, {"inv_part_src", 1}});'),
    t(1, 'Check("inv_cover", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x4000, 0xf000, 0x8000); },'),
    t(1, '      {{"inv_gpu", 1}, {"inv_part", 0}, {"inv_off", 0}, {"inv_part_src", 0}});'),
    t(1, 'Check("inv_not_gpu", [&] { D::NoteInvalidateImage(false, 0x10000, 0x4000, 0x4000, 0x11000, 0x100); },'),
    t(1, '      {{"inv_gpu", 0}, {"inv_part", 0}, {"inv_off", 0}, {"inv_part_src", 0}});'),
    t(1, '// M6a2 (item 770(d)): source_size 0x1000 < data size 0x4000 - the write covers the source, not the data.'),
    t(1, 'Check("inv_src_cover", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x1000, 0x10000, 0x1000); },'),
    t(1, '      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 0}, {"inv_part_src", 0}});'),
]))

# audio arm: guest PCM buffers and push 4
S.append(([
    t(1, 'std::vector<float> obj_nz(256, 0.0f);'),
    t(1, 'std::vector<float> bus_nz(256 * 3, 0.0f);'),
    t(1, 'std::vector<float> obj_z(256, 0.0f);'),
    t(1, 'std::vector<float> bus_z(256 * 3, 0.0f);'),
    t(1, 'obj_nz[255]  = 0.5f;'),
    t(1, 'bus_nz[100]  = -0.25f;'),
], [
    t(1, '// M6a2: the object PCM lives in guest memory (read through TryReadBacking); bus PCM stays in host memory.'),
    t(1, 'auto*              obj_nz = reinterpret_cast<float*>(GuestAlloc(256 * sizeof(float)));'),
    t(1, 'auto*              obj_z  = reinterpret_cast<float*>(GuestAlloc(256 * sizeof(float)));'),
    t(1, 'std::vector<float> bus_nz(256 * 3, 0.0f);'),
    t(1, 'std::vector<float> bus_z(256 * 3, 0.0f);'),
    t(1, 'obj_nz[255]  = 0.5f;'),
    t(1, 'bus_nz[100]  = -0.25f;'),
]))
S.append(([
    t(1, '// push 1: both nonzero; push 2: both zero; push 3: a fresh object port without PCM (the old ports keep zeros).'),
    t(1, 'struct Want {'),
    t(2, 'uint64_t obj_push, obj_nz, obj_nopcm, bus_push, bus_nz, pushes;'),
    t(1, '};'),
    t(1, 'const Want wants[3] = {{1, 1, 0, 1, 1, 1}, {1, 0, 0, 1, 0, 1}, {1, 0, 1, 1, 0, 1}};'),
    t(1, 'for (int i = 0; i < 3; i++) {'),
    t(2, 'if (i == 0) {'),
    t(3, 'set_pcm(obj, obj_nz.data());'),
    t(3, 'set_pcm(bus, bus_nz.data());'),
    t(2, '} else if (i == 1) {'),
    t(3, 'set_pcm(obj, obj_z.data());'),
    t(3, 'set_pcm(bus, bus_z.data());'),
    t(2, '} else {'),
], [
    t(1, '// push 1: both nonzero; push 2: both zero; push 3: a fresh object port without PCM (the old ports keep zeros);'),
    t(1, '// M6a2 push 4: the first object port points to an unreadable address (ao_obj_unread 1 at =1; alive at 0 and 1).'),
    t(1, 'struct Want {'),
    t(2, 'uint64_t obj_push, obj_nz, obj_nopcm, bus_push, bus_nz, pushes, obj_unread;'),
    t(1, '};'),
    t(1, 'const Want wants[4] = {{1, 1, 0, 1, 1, 1, 0}, {1, 0, 0, 1, 0, 1, 0}, {1, 0, 1, 1, 0, 1, 0}, {1, 0, 1, 1, 0, 1, 1}};'),
    t(1, 'for (int i = 0; i < 4; i++) {'),
    t(2, 'if (i == 0) {'),
    t(3, 'set_pcm(obj, obj_nz);'),
    t(3, 'set_pcm(bus, bus_nz.data());'),
    t(2, '} else if (i == 1) {'),
    t(3, 'set_pcm(obj, obj_z);'),
    t(3, 'set_pcm(bus, bus_z.data());'),
    t(2, '} else if (i == 3) {'),
    t(3, 'set_pcm(obj, UNREADABLE);'),
    t(2, '} else {'),
]))
S.append(([
    t(2, 'const Want w      = knob != 0 ? wants[i] : Want {0, 0, 0, 0, 0, 0};'),
    t(2, 'const Want d {after.ao_obj_push - before.ao_obj_push, after.ao_obj_nz - before.ao_obj_nz,'),
    t(2, '              after.ao_obj_nopcm - before.ao_obj_nopcm, after.ao_bus_push - before.ao_bus_push,'),
    t(2, '              after.ao_bus_nz - before.ao_bus_nz, after.pushes - before.pushes};'),
    t(2, 'const bool ok = rc == 0 && std::memcmp(&w, &d, sizeof(Want)) == 0;'),
    t(2, 'std::printf("MStand: m6 arm=audio push=%d knob=%d rc=%d d_obj_push=%llu d_obj_nz=%llu d_obj_nopcm=%llu "'),
    t(2, '            "d_bus_push=%llu d_bus_nz=%llu d_pushes=%llu match=%d\\n",'),
    t(2, '            i + 1, knob, rc, static_cast<unsigned long long>(d.obj_push),'),
    t(2, '            static_cast<unsigned long long>(d.obj_nz), static_cast<unsigned long long>(d.obj_nopcm),'),
    t(2, '            static_cast<unsigned long long>(d.bus_push), static_cast<unsigned long long>(d.bus_nz),'),
    t(2, '            static_cast<unsigned long long>(d.pushes), ok ? 1 : 0);'),
], [
    t(2, 'const Want w      = knob != 0 ? wants[i] : Want {0, 0, 0, 0, 0, 0, 0};'),
    t(2, 'const Want d {after.ao_obj_push - before.ao_obj_push, after.ao_obj_nz - before.ao_obj_nz,'),
    t(2, '              after.ao_obj_nopcm - before.ao_obj_nopcm, after.ao_bus_push - before.ao_bus_push,'),
    t(2, '              after.ao_bus_nz - before.ao_bus_nz, after.pushes - before.pushes,'),
    t(2, '              after.ao_obj_unread - before.ao_obj_unread};'),
    t(2, 'const bool ok = rc == 0 && std::memcmp(&w, &d, sizeof(Want)) == 0;'),
    t(2, 'std::printf("MStand: m6 arm=audio push=%d knob=%d rc=%d d_obj_push=%llu d_obj_nz=%llu d_obj_nopcm=%llu "'),
    t(2, '            "d_bus_push=%llu d_bus_nz=%llu d_pushes=%llu d_obj_unread=%llu match=%d\\n",'),
    t(2, '            i + 1, knob, rc, static_cast<unsigned long long>(d.obj_push),'),
    t(2, '            static_cast<unsigned long long>(d.obj_nz), static_cast<unsigned long long>(d.obj_nopcm),'),
    t(2, '            static_cast<unsigned long long>(d.bus_push), static_cast<unsigned long long>(d.bus_nz),'),
    t(2, '            static_cast<unsigned long long>(d.pushes), static_cast<unsigned long long>(d.obj_unread), ok ? 1 : 0);'),
]))

# main: guest memory for pure and audio
S.append(([
    t(1, 'subsystems.Initialize<Loader::Timer::Lifecycle>();'),
], [
    t(1, 'subsystems.Initialize<Loader::Timer::Lifecycle>();'),
    t(1, 'if (arm == "pure" || arm == "audio") {'),
    t(2, 'subsystems.Initialize<Libs::LibKernel::Memory::Lifecycle>(); // M6a2: guest memory for object PCM'),
    t(1, '}'),
]))


def main():
    root = sys.argv[1].rstrip('/')
    apply(root, 'tests/MWave2DiagStand.cpp', S)
    print('ALL OK')


if __name__ == '__main__':
    main()
