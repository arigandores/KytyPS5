# F35a (HPP-755, ROADMAP s122 item 685(v)(0)): check of the references <commit>:<path>:<line> of docs/track-f/f35a.md s0.
# Each reference: the line holds its anchor (a substring of the whole line) and the next line (+1) holds its control.
# Reads the files from git (the commit of FS11 source ee9632be), not from a working tree. Prints ALL OK only if every
# reference holds.
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = 'ee9632be'
RM = 'src/graphics/shader/recompiler/ir/passes/ResourceMaterialization.cpp'
EM = 'src/graphics/shader/recompiler/backend/spirv/spirvEmitterImage.cpp'
DS = 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
II = 'src/graphics/host_gpu/renderer/image/imageInfo.h'
SB = 'src/graphics/shader/shaderBindings.h'

# (name, path, line, anchor, control at line + 1)
REFS = [
    # R: the per-member rule of the specialization (MaterializeResources -> specialization of the T# snapshot)
    ('R1', RM, 34, 'bool FixF19Enabled() {', '// Track F, FS8a (HPP-571'),
    ('R2', RM, 39, "return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);", '}();'),
    ('R3', RM, 44, 'bool FixF19ManualDepthCompare(Prospero::BufferFormat format, bool null_descriptor) {',
     'return !null_descriptor && FindGuestDepthFormatPolicy(format) == nullptr;'),
    ('R4', RM, 48, 'void FixF19MergeIndirectTables(std::vector<ResourceSpecialization::Image>& images) {',
     'for (uint32_t root = 0; root < images.size(); root++) {'),
    ('R5', RM, 55, 'manual = manual || (image.indirect_root == root && image.manual_depth_compare);', '}'),
    ('R6', RM, 573, 'const auto  base_index = i < program.info.images.size() ? i : image.indirect_root;',
     'if (base_index >= program.info.images.size()) {'),
    ('R7', RM, 589, 'if (base.depth_compare) {', '// Preserve the compare function even for native depth images'),
    ('R8', RM, 604, 'if (FixF19Enabled()) {', '// Track F, F14e (ROADMAP s122 item 409(v)): native for every format'),
    ('R9', RM, 608, 'FixF19ManualDepthCompare(format, NullImageDescriptor(descriptor));', '} else {'),
    ('R10', RM, 610, 'image.manual_depth_compare = !NullImageDescriptor(descriptor) &&',
     'format != Prospero::BufferFormat::k32Float;'),
    ('R11', RM, 614, 'if (NullImageDescriptor(descriptor)) {', 'image.numeric_class = base.atomic ? Prospero::TextureNumericClass::Uint'),
    ('R12', RM, 697, 'exemplar = resource;', '}'),
    ('R13', RM, 709, 'if (NullImageDescriptor(next_snapshot.images[candidate])) {',
     'image.numeric_class     = image_class.numeric_class;'),
    ('R17', RM, 717, 'if (image.numeric_class != image_class.numeric_class ||',
     'image.dimension != image_class.dimension ||'),
    ('R14', RM, 729, 'if (FixF19Enabled()) {', '// Track F, F14e (ROADMAP s122 item 415(b), variant O1)'),
    ('R15', RM, 733, 'FixF19MergeIndirectTables(next_specialization.images);', '}'),
    ('R16', RM, 127, 'bool NullImageDescriptor(const DescriptorValue& descriptor) {',
     'return descriptor.dwords[0] == 0 && (descriptor.dwords[1] & 0xffu) == 0;'),
    # A: ApplyResourceSpecialization - the program.info.images the binding path receives
    ('A1', RM, 1152, 'auto images = program.info.images;', 'images.reserve(specialization.images.size());'),
    ('A2', RM, 1158, 'images.push_back(program.info.images[source.indirect_root]);', '}'),
    ('A3', RM, 1170, 'image.manual_depth_compare       = source.manual_depth_compare;',
     'image.depth_compare_op           = source.depth_compare_op;'),
    ('A4', RM, 1206, 'samplers[pair.sampler].depth_compare |= images[pair.image].depth_compare;', '}'),
    ('A5', RM, 1222, 'if (!samplers[pair.sampler].depth_compare && images[pair.image].depth_compare &&',
     '!images[pair.image].manual_depth_compare) {'),
    # E: the emitter - opcode by the root, the same opcode for every member of the table
    ('E1', EM, 605, 'const auto& image   = state.program.info.images.at(mem.resource);',
     'const auto* address = ctx.ImageAddress('),
    ('E2', EM, 683, 'const bool  manual_dref    = dref && image.manual_depth_compare;',
     'const bool  native_dref    = dref && !manual_dref;'),
    ('E3', EM, 766, 'opcode = native_dref ? spv::OpImageSampleDrefExplicitLod : spv::OpImageSampleExplicitLod;',
     '} else if (native_dref) {'),
    ('E4', EM, 768, 'opcode = spv::OpImageSampleDrefImplicitLod;', '}'),
    ('E5', EM, 800, 'const auto EmitSample = [&](uint32_t resource) {',
     'const auto            sampled = MakeSampledImage(state, resource, mem.sampler);'),
    ('E6', EM, 816, 'if (image.indirect_root != mem.resource) {', 'const auto sample = EmitSample(mem.resource);'),
    ('E7', EM, 907, 'phi_words.push_back(EmitSample(image.indirect_resources[0]));', 'phi_words.push_back(default_label);'),
    ('E8', EM, 912, 'phi_words.push_back(EmitSample(image.indirect_resources[candidate]));',
     'phi_words.push_back(labels[candidate - 1u]);'),
    # D: the binding path - the view of each member
    ('D1', DS, 4489, 'auto& binding = ResolveTextureWith(', 'program.info.images[i], snapshot.images[i],'),
    ('D2', DS, 2824, 'const bool storage = resource.written;', 'if (storage) {'),
    ('D3', DS, 2835, 'if (descriptor.IsNull() || (skip_tail_mip_storage && tail_mip_storage)) {',
     'const auto binding = storage ? TextureCache::BindingType::Storage'),
    ('D4', DS, 2885, 'auto       desc = NullTextureDesc(resource, binding);',
     'const auto id   = texture_cache.FindImage(desc);'),
    ('D5', DS, 1335, 'desc.info.pixel_format    = VulkanFormat(desc.info.guest_format);',
     'const bool native_compare = binding == TextureCache::BindingType::Texture &&'),
    ('D6', DS, 1337, 'resource.depth_compare && !resource.manual_depth_compare;', 'if (native_compare) {'),
    ('D7', DS, 1339, 'desc.info.pixel_format = vk::Format::eD32Sfloat;', '}'),
    ('D8', DS, 3072, 'auto pixel_format = surface_format.vk_format;', 'if (resource.depth_compare) {'),
    ('D9', DS, 3074, 'if (const auto* depth_format = FindGuestDepthFormatPolicy(format)) {',
     'pixel_format = depth_format->depth_attachment_format;'),
    ('D10', DS, 1325, 'desc.info.guest_format = Prospero::BufferFormat::k32Float;', 'break;'),
    ('P1', II, 193, 'inline constexpr std::array<DepthFormatPolicy, 2> DEPTH_FORMAT_POLICIES {{',
     '{Prospero::DepthFormat::kZ16,'),
    ('P2', II, 195, 'Prospero::BufferFormat::k16UNorm,', '2,'),
    ('P3', II, 200, 'Prospero::BufferFormat::k32Float,', '4,'),
    ('B1', SB, 98, '[[nodiscard]] uint64_t Base40() const {',
     'return ((fields[0] | (static_cast<uint64_t>(fields[1]) << 32u)) & 0xFFFFFFFFFFu) << 8u;'),
    ('B2', SB, 101, '[[nodiscard]] bool                   IsNull() const { return Base40() == 0; }',
     '[[nodiscard]] Prospero::BufferFormat Format() const {'),
]

cache = {}
ok = True
for name, path, line, anchor, control in REFS:
    if path not in cache:
        cache[path] = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (C, path)], capture_output=True,
                                     check=True).stdout.decode('utf-8').split('\n')
    lines = cache[path]
    a = lines[line - 1].strip() if line - 1 < len(lines) else ''
    n = lines[line].strip() if line < len(lines) else ''
    good = anchor.strip() == a or (anchor.strip() in a and len(anchor.strip()) >= 12)
    # A short control (a brace, "break;", "2,") must be the whole +1 line; a long one - a substring of it.
    c = control.strip()
    good_n = c != '' and (n == c if len(c) < 8 else c in n)
    print('%-4s %s:%s:%d anchor=%s +1=%s' % (name, C, path, line, 'ok' if good else 'BAD', 'ok' if good_n else 'BAD'))
    if not (good and good_n):
        print('     line:', a)
        print('     +1  :', n)
    ok &= good and good_n
print('ALL OK' if ok else 'NOT OK')
sys.exit(0 if ok else 1)
