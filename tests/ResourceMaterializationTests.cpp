#include "graphics/shader/recompiler/ir/ShaderIR.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"

#include <cstdio>
#include <cstdlib>
#include <memory>
#include <chrono>
#include <bit>
#include <functional>

namespace {

void Check(bool value, const char *text) {
  if (!value) {
    std::fprintf(stderr, "ResourceMaterializationTests: failed: %s\n", text);
    std::abort();
  }
}

bool RejectSpecializationRead(void *userdata, uint64_t, uint32_t *) {
  ++*static_cast<uint32_t *>(userdata);
  return false;
}

Libs::Graphics::ShaderRecompiler::IR::Block &
AddValueBlock(Libs::Graphics::ShaderRecompiler::IR::Program &program) {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  auto block = std::make_unique<Block>();
  auto *result = block.get();
  program.blocks.push_back(result);
  program.block_info.push_back({.id = 0});
  program.block_storage.push_back(std::move(block));
  return *result;
}

Libs::Graphics::ShaderRecompiler::IR::ResourcePlan SrtPlan(uint64_t address) {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  Program program;
  program.stage = Libs::Graphics::ShaderType::Compute;
  program.srt_plan_complete = true;
  program.resource_tracking_complete = true;
  auto &value_block = AddValueBlock(program);

  MemoryInfo memory;
  memory.kind = ResourceKind::ScalarAddress;
  memory.planning_only = true;
  program.memory_info.push_back(memory);
  const auto low = Value(static_cast<uint32_t>(address));
  const auto high = Value(static_cast<uint32_t>(address >> 32u));
  auto &handle =
      value_block.AppendNewInst(ValueOpcode::GetAddressResource, {low, high});
  auto &raw = value_block.AppendNewInst(
      ValueOpcode::LoadAddressU32,
      {Value(&handle), Value(0u), Value(0u), Value(true)});
  raw.SetFlags(MemoryFlags{.index = 0, .pc = 0x40});
  program.srt_reads.push_back({Value(&raw), 0});

  auto &srt = value_block.AppendNewInst(ValueOpcode::GetSrtResource);
  auto &flat = value_block.AppendNewInst(ValueOpcode::ReadConst,
                                         {Value(&srt), Value(0u)});
  DescriptorSource source;
  source.dwords[0] = Value(&flat);
  source.dwords[1] = Value(0u);
  source.dword_count = 2;
  program.descriptor_sources.push_back(source);
  return ExtractResourcePlan(program);
}

Libs::Graphics::ShaderRecompiler::IR::ResourcePlan UnbasedFlatPlan() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  Program program;
  program.stage = Libs::Graphics::ShaderType::Compute;
  program.srt_plan_complete = true;
  program.resource_tracking_complete = true;
  AddValueBlock(program);
  program.info.uses_dma = true;
  return ExtractResourcePlan(program);
}

Libs::Graphics::ShaderRecompiler::IR::ResourcePlan UserDataBufferPlan() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  Program program;
  program.stage = Libs::Graphics::ShaderType::Compute;
  program.srt_plan_complete = true;
  program.resource_tracking_complete = true;
  auto &value_block = AddValueBlock(program);

  auto &user_data = value_block.AppendNewInst(
      ValueOpcode::GetUserData, {Value(static_cast<ScalarReg>(0))});
  DescriptorSource source;
  source.dwords[0] = Value(&user_data);
  source.dwords[1] = Value(0u);
  source.dwords[2] = Value(0u);
  source.dwords[3] = Value(0u);
  source.dword_count = 4;
  program.descriptor_sources.push_back(source);
  program.info.buffers.push_back({.source = 0});
  return ExtractResourcePlan(program);
}

Libs::Graphics::ShaderRecompiler::IR::ResourcePlan MixedSamplerPlan() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  Program program;
  program.stage = Libs::Graphics::ShaderType::Compute;
  program.srt_plan_complete = true;
  program.resource_tracking_complete = true;
  AddValueBlock(program);

  const auto AddSource = [&program](uint32_t dword_count, uint32_t first) {
    DescriptorSource source;
    source.dword_count = dword_count;
    source.dwords[0] = Value(first);
    for (uint32_t i = 1; i < dword_count; i++) {
      source.dwords[i] = Value(0u);
    }
    program.descriptor_sources.push_back(source);
    return static_cast<uint32_t>(program.descriptor_sources.size() - 1u);
  };

  const auto image0 = AddSource(8, 0);
  const auto image1 = AddSource(8, 0);
  const auto sampler0 = AddSource(4, 0x11111111u);
  const auto sampler1 = AddSource(4, 0x22222222u);
  program.info.images.push_back(
      {.source = image0,
       .resource_class = ImageResourceClass::Sampled,
       .numeric_class = Libs::Graphics::Prospero::TextureNumericClass::Float,
       .dimension =
           Libs::Graphics::ShaderRecompiler::Decoder::ImageDimension::Dim2D});
  program.info.images.push_back(
      {.source = image1,
       .resource_class = ImageResourceClass::Sampled,
       .numeric_class = Libs::Graphics::Prospero::TextureNumericClass::Float,
       .dimension =
           Libs::Graphics::ShaderRecompiler::Decoder::ImageDimension::Dim2D,
       .conversion_format =
           Libs::Graphics::Prospero::BufferFormat::k8_8_8_8UNorm});
  program.info.samplers.push_back({.source = sampler0});
  program.info.samplers.push_back({.source = sampler1});
  program.info.sampled_pairs.push_back({.image = 0, .sampler = 0});
  program.info.sampled_pairs.push_back({.image = 0, .sampler = 1});
  program.info.sampled_pairs.push_back({.image = 1, .sampler = 1});
  return ExtractResourcePlan(program);
}

void TestMappedSrtUsesDirectReaderByDefault() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  uint32_t dword = 0x12345678;
  auto plan = SrtPlan(reinterpret_cast<uint64_t>(&dword));
  uint32_t specialization_reads = 0;
  const SrtRuntime runtime{.userdata = &specialization_reads,
                           .read_specialization_memory =
                               RejectSpecializationRead};
  ResourceSnapshot snapshot;
  ResourceSpecialization specialization;
  Check(MaterializeResources(plan, runtime, snapshot, specialization),
        "mapped SRT stage materialization failed");
  Check(specialization_reads == 0,
        "ordinary SRT read used the specialization reader");
  Check(snapshot.flattened_srt.size() == 1 &&
            snapshot.flattened_srt[0] == dword,
        "cache rematerialization did not use the direct reader by default");
  const auto saved = snapshot;
  auto other_plan = UserDataBufferPlan();
  ResourceSnapshot other_snapshot;
  ResourceSpecialization other_specialization;
  const std::array<uint32_t, 1> user_data{0x4000};
  Check(MaterializeResources(other_plan, {.user_data = user_data}, other_snapshot,
                             other_specialization) && other_snapshot.flattened_srt.empty(),
        "switching SRT plans retained a stale flat array");
  dword = 0x87654321;
  Check(MaterializeResources(plan, runtime, snapshot, specialization) &&
            snapshot.flattened_srt == std::vector<uint32_t>{dword} &&
            saved.flattened_srt == std::vector<uint32_t>{0x12345678},
        "SRT scratch cached a guest value or aliased an earlier result");
}

void TestIntegerRuntimeValueFollowsSrtReads() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  auto plan = SrtPlan(0x10000);
  const auto root = plan.descriptor_sources.front().dwords[0];
  Check(ValidateRuntimeValue(plan, root, RuntimeValueType::Integer),
        "integer SRT read was rejected");

  Block values;
  auto &comparison = values.AppendNewInst(ValueOpcode::FPOrdLessThanEqual32,
                                          {Value::F32(1.f), Value::F32(0.f)});
  auto &selection = values.AppendNewInst(
      ValueOpcode::SelectU32, {Value(&comparison), Value(1u), Value(0u)});
  plan.srt_reads[0].value = Value(&selection);
  Check(ValidateRuntimeValue(plan, root),
        "ordinary SRT validation rejected a floating-point dependency");
  Check(!ValidateRuntimeValue(plan, root, RuntimeValueType::Integer),
        "integer SRT validation missed a hidden floating-point dependency");

  auto &first =
      values.AppendNewInst(ValueOpcode::ReadFirstLane, {root, Value(true)});
  Check(!ValidateRuntimeValue(plan, Value(&first), RuntimeValueType::Integer),
        "read-first-lane lost integer-only SRT validation");

  auto &active = values.AppendNewInst(ValueOpcode::ReadFirstLane,
                                      {Value(&selection), Value(&comparison)});
  Check(!ValidateRuntimeValue(plan, Value(&active), RuntimeValueType::Integer),
        "floating-point execution mask was accepted as integer-only");

  auto &lane = values.AppendNewInst(
      ValueOpcode::GetBuiltin,
      {Value(static_cast<uint32_t>(StageInputKind::LocalInvocationId)),
       Value(0u)});
  auto &mask =
      values.AppendNewInst(ValueOpcode::INotEqual32, {Value(&lane), Value(0u)});
  selection.SetArg(0, Value(&mask));
  active.SetArg(1, Value(&mask));
  Check(ValidateRuntimeValue(plan, Value(&active), RuntimeValueType::Integer),
        "nonuniform integer execution mask was rejected");
  auto &float_value =
      values.AppendNewInst(ValueOpcode::BitCastU32F32, {Value::F32(1.f)});
  selection.SetArg(2, Value(&float_value));
  Check(!ValidateRuntimeValue(plan, Value(&active), RuntimeValueType::Integer),
        "floating-point inactive arm was accepted as integer-only");

  plan.srt_reads[0].value = Value(&first);
  Check(!ValidateRuntimeValue(plan, root, RuntimeValueType::Integer),
        "cyclic SRT read-first-lane dependency was accepted");
}

void TestUnbasedFlatCacheHitMaterializes() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  auto plan = UnbasedFlatPlan();
  ResourceSnapshot snapshot;
  ResourceSpecialization specialization;
  Check(MaterializeResources(plan, {}, snapshot, specialization),
        "unbased FLAT stage materialization failed");
  Check(snapshot.buffers.empty() && snapshot.images.empty(),
        "unbased FLAT plan produced unexpected descriptors");
}

void TestFailedMaterializationPreservesPriorStage() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  auto plan = UserDataBufferPlan();
  ResourceSnapshot snapshot;
  snapshot.user_data.push_back(0xfeedbeefu);
  ResourceSpecialization specialization;
  specialization.buffers.push_back({.packed_stride = 7});
  Check(!MaterializeResources(plan, {}, snapshot, specialization),
        "missing runtime user data did not reject the cached stage");
  Check(snapshot.user_data == std::vector<uint32_t>{0xfeedbeefu} &&
            specialization.buffers.size() == 1 &&
            specialization.buffers[0].packed_stride == 7,
        "failed cache materialization changed its destinations");
}

void TestMixedSamplerDuplicatesTheCorrectSnapshot() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  auto plan = MixedSamplerPlan();
  ResourceSnapshot snapshot;
  ResourceSpecialization specialization;
  Check(MaterializeResources(plan, {}, snapshot, specialization),
        "mixed sampler materialization failed");
  Check(snapshot.samplers.size() == 3,
        "mixed sampler materialization appended unrelated samplers");
  Check(snapshot.samplers[2] == snapshot.samplers[1] &&
            snapshot.samplers[2] != snapshot.samplers[0],
        "point sampler variant duplicated the wrong runtime descriptor");
}

void TestDepthComparisonFormatsAndSharedSampler() {
  using namespace Libs::Graphics;
  using namespace ShaderRecompiler::IR;
  const auto build = [](Prospero::BufferFormat format, bool null_image, bool shared) {
    Program program;
    program.stage = ShaderType::Compute;
    program.srt_plan_complete = true;
    program.resource_tracking_complete = true;
    AddValueBlock(program);
    for (uint32_t i = 0; i < (shared ? 2u : 1u); ++i) {
      DescriptorSource source;
      source.dword_count = 8;
      for (auto& word : source.dwords) word = Value(0u);
      source.dwords[0] = Value(null_image && i == 0 ? 0u : 0x1000u + i * 0x100u);
      source.dwords[1] = Value(static_cast<uint32_t>(i == 0 ? format : Prospero::BufferFormat::k32Float) << 20u);
      source.dwords[3] = Value(DstSel(4, 4, 4, 4) |
          (static_cast<uint32_t>(Prospero::ImageType::kColor2D) << 28u));
      program.descriptor_sources.push_back(source);
      ImageResource image;
      image.source = i;
      image.resource_class = ImageResourceClass::Sampled;
      image.numeric_class = Prospero::TextureNumericClass::Float;
      image.dimension = ShaderRecompiler::Decoder::ImageDimension::Dim2D;
      image.depth_compare = true;
      image.read = true;
      program.info.images.push_back(image);
      program.info.sampled_pairs.push_back({.image = i, .sampler = 0});
    }
    DescriptorSource sampler;
    sampler.dword_count = 4;
    for (auto& word : sampler.dwords) word = Value(0u);
    sampler.dwords[0] = Value(3u << 12u); // less-or-equal
    program.info.samplers.push_back({.source = static_cast<uint32_t>(program.descriptor_sources.size())});
    program.descriptor_sources.push_back(sampler);
    return program;
  };
  for (const auto format : {Prospero::BufferFormat::k16UNorm,
                           Prospero::BufferFormat::k8_8_8_8UNorm,
                           Prospero::BufferFormat::k32Float}) {
    auto program = build(format, false, false);
    auto plan = ExtractResourcePlan(program);
    ResourceSnapshot snapshot;
    ResourceSpecialization specialization;
    Check(MaterializeResources(plan, {}, snapshot, specialization), "depth format materialization failed");
    Check(specialization.images[0].manual_depth_compare == (format != Prospero::BufferFormat::k32Float) &&
          specialization.images[0].depth_compare_op == 3u,
          "depth comparison format or compare function was lost");
  }
  auto program = build(Prospero::BufferFormat::k8_8_8_8UNorm, false, true);
  auto plan = ExtractResourcePlan(program);
  ResourceSnapshot snapshot;
  ResourceSpecialization specialization;
  Check(MaterializeResources(plan, {}, snapshot, specialization), "shared depth sampler materialization failed");
  ApplyResourceSpecialization(program, specialization);
  Check(program.info.images[0].manual_depth_compare && program.info.images[1].manual_depth_compare &&
        program.info.images[1].depth_compare_op == 3u && !program.info.samplers[0].depth_compare,
        "shared color/depth sampler changed the native image's compare function to Never");
  auto null_program = build(Prospero::BufferFormat::k32Float, true, false);
  auto null_plan = ExtractResourcePlan(null_program);
  Check(MaterializeResources(null_plan, {}, snapshot, specialization) &&
        !specialization.images[0].manual_depth_compare && specialization.images[0].depth_compare_op == 3u,
        "null depth descriptor lost its native comparison specialization");
}

void TestCompiledSrtSharedExpressionsKeepRuntimeReads() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  Program program;
  program.stage = Libs::Graphics::ShaderType::Compute;
  program.srt_plan_complete = true;
  program.resource_tracking_complete = true;
  auto &block = AddValueBlock(program);
  MemoryInfo memory;
  memory.kind = ResourceKind::ScalarAddress;
  memory.planning_only = true;
  program.memory_info.push_back(memory);
  for (uint32_t i = 0; i < 2; ++i) {
    auto &data = block.AppendNewInst(ValueOpcode::GetUserData,
                                    {Value(static_cast<ScalarReg>(0))});
    auto &sum = block.AppendNewInst(ValueOpcode::IAdd32,
                                   {Value(&data), Value(7u)});
    auto &address = block.AppendNewInst(ValueOpcode::GetAddressResource,
                                       {Value(&sum), Value(0u)});
    auto &read = block.AppendNewInst(ValueOpcode::LoadAddressU32,
        {Value(&address), Value(0u), Value(0u), Value(true)});
    read.SetFlags(MemoryFlags{.index = 0, .pc = 0x40});
    DescriptorSource source;
    source.dword_count = 2;
    source.dwords[0] = Value(&sum);
    source.dwords[1] = Value(&read);
    program.descriptor_sources.push_back(source);
  }
  auto plan = ExtractResourcePlan(program);
  struct Reader { uint32_t calls = 0, word = 0; uint64_t address = 0; } reader;
  const auto read = +[](void *opaque, uint64_t address, uint32_t *word) {
    auto &state = *static_cast<Reader *>(opaque);
    ++state.calls;
    state.address = address;
    *word = state.word;
    return true;
  };
  uint32_t data = 0;
  const uint32_t sources[] = {0, 1};
  std::vector<DescriptorValue> values;
  std::vector<uint32_t> flat;
  std::vector<uint8_t> active;
  const SrtRuntime runtime{std::span(&data, 1), 0, read, &reader};
  for (const auto input : {0xfffffffdu, 0x1000u}) {
    data = input;
    reader.calls = 0;
    ++reader.word;
    Check(EvaluateRuntimeSources(plan, sources, runtime, values, flat,
                                 plan.clean_flat_slots, active),
          "shared SRT expressions failed");
    const auto sum = static_cast<uint32_t>(input + 7u);
    Check(values.size() == 2 && values[0].dwords[0] == sum &&
          values[1].dwords[0] == sum && values[0].dwords[1] == reader.word &&
          values[1].dwords[1] == reader.word && reader.address == (sum & ~3u),
          "shared SRT expression lost overflow or retained a previous runtime value");
    const bool verifying = std::getenv("KYTY_SRT_VERIFY") != nullptr &&
        (std::getenv("KYTY_SRT_COMPILED") == nullptr ||
         std::getenv("KYTY_SRT_COMPILED")[0] != '0');
    Check(reader.calls == (verifying ? 4u : 2u),
          "separate SRT memory reads were coalesced");
  }
}

void TestCompiledScalarAddressPlan() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  Program program;
  program.srt_plan_complete = true;
  program.resource_tracking_complete = true;
  auto &block = AddValueBlock(program);
  auto &low = block.AppendNewInst(ValueOpcode::GetUserData,
      {Value(static_cast<ScalarReg>(0))});
  auto &high = block.AppendNewInst(ValueOpcode::GetUserData,
      {Value(static_cast<ScalarReg>(1))});
  auto &address = block.AppendNewInst(ValueOpcode::GetAddressResource,
      {Value(&low), Value(&high)});
  std::vector<uint32_t> sources;
  for (uint32_t i = 0; i < 128; ++i) {
    MemoryInfo memory;
    memory.kind = ResourceKind::ScalarAddress;
    memory.planning_only = true;
    memory.offset = static_cast<uint32_t>(-5);
    program.memory_info.push_back(memory);
    auto &read = block.AppendNewInst(ValueOpcode::LoadAddressU32,
        {Value(&address), Value(i * 4u + 3u), Value(0u), Value(true)});
    read.SetFlags(MemoryFlags{.index = i, .pc = 0x40});
    DescriptorSource source;
    source.dword_count = 1;
    source.dwords[0] = Value(&read);
    sources.push_back(i);
    program.descriptor_sources.push_back(source);
  }
  auto plan = ExtractResourcePlan(program);
  struct Reader { uint64_t first = 0; uint32_t calls = 0, salt = 0; bool fail = false; } reader;
  const auto read = +[](void *opaque, uint64_t address, uint32_t *word) {
    auto &state = *static_cast<Reader *>(opaque);
    Check(address == state.first + (state.calls++ % 128u) * 4u,
          "scalar address plan changed masking, signed offset or read order");
    *word = static_cast<uint32_t>(address) ^ state.salt;
    return !state.fail;
  };
  uint32_t data[2] = {0, 0};
  const SrtRuntime runtime{data, 0, read, &reader};
  std::vector<DescriptorValue> values;
  std::vector<uint32_t> flat;
  std::vector<uint8_t> active;
  const auto evaluate = [&] {
    reader.calls = 0;
    Check(EvaluateRuntimeSources(plan, sources, runtime, values, flat,
                                 plan.clean_flat_slots, active),
          "scalar address plan evaluation failed");
    Check(values.size() == 128, "scalar address plan lost sources");
    for (uint32_t i = 0; i < 128; ++i) {
      Check(values[i].dwords[0] == (reader.fail ? 0u :
          (static_cast<uint32_t>(reader.first + i * 4u) ^ reader.salt)),
          "scalar address plan kept stale memory or lost read failure");
    }
  };
  for (const auto base : {uint64_t{0x1003}, uint64_t{0xabc100000007},
                         uint64_t{0xffff000100000009}}) {
    data[0] = static_cast<uint32_t>(base);
    data[1] = static_cast<uint32_t>(base >> 32u);
    reader.first = (base & 0x0000fffffffffffcull) - 8;
    ++reader.salt;
    evaluate();
    reader.fail = true;
    evaluate();
    reader.fail = false;
  }
  if (const auto *setting = std::getenv("KYTY_SRT_BENCH")) {
    const auto iterations = std::strtoul(setting, nullptr, 10);
    const auto start = std::chrono::steady_clock::now();
    for (unsigned long i = 0; i < iterations; ++i) {
      ++reader.salt;
      evaluate();
    }
    const auto ns = std::chrono::duration<double, std::nano>(
        std::chrono::steady_clock::now() - start).count();
    std::printf("SrtBench: iterations=%lu ns_per_128_reads=%.1f\n", iterations, ns / iterations);
  }
}

void TestSrtNativeArithmetic() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  using Op = ValueOpcode;
  struct Case { Op op; bool wide; std::function<uint64_t(uint64_t,uint64_t)> eval; };
  const Case cases[] = {
    {Op::IAdd32,false,[](auto a,auto b){return uint32_t(a+b);}},
    {Op::IAdd64,true,[](auto a,auto b){return a+b;}},
    {Op::ISub32,false,[](auto a,auto b){return uint32_t(a-b);}},
    {Op::ISub64,true,[](auto a,auto b){return a-b;}},
    {Op::IMul32,false,[](auto a,auto b){return uint32_t(a*b);}},
    {Op::IMul64,true,[](auto a,auto b){return a*b;}},
    {Op::BitwiseAnd32,false,[](auto a,auto b){return uint32_t(a&b);}},
    {Op::BitwiseAnd64,true,[](auto a,auto b){return a&b;}},
    {Op::BitwiseOr32,false,[](auto a,auto b){return uint32_t(a|b);}},
    {Op::BitwiseXor32,false,[](auto a,auto b){return uint32_t(a^b);}},
    {Op::ShiftLeftLogical32,false,[](auto a,auto b){return uint32_t(a)<<(b&31);}},
    {Op::ShiftLeftLogical64,true,[](auto a,auto b){return a<<(b&63);}},
    {Op::ShiftRightLogical32,false,[](auto a,auto b){return uint32_t(a)>>(b&31);}},
    {Op::ShiftRightLogical64,true,[](auto a,auto b){return a>>(b&63);}},
    {Op::ShiftRightArithmetic32,false,[](auto a,auto b){return uint32_t(std::bit_cast<int32_t>(uint32_t(a))>>(b&31));}},
    {Op::ShiftRightArithmetic64,true,[](auto a,auto b){return uint64_t(std::bit_cast<int64_t>(a)>>(b&63));}},
    {Op::IEqual32,false,[](auto a,auto b){return uint32_t(a)==uint32_t(b);}},
    {Op::INotEqual32,false,[](auto a,auto b){return uint32_t(a)!=uint32_t(b);}},
    {Op::ULessThan32,false,[](auto a,auto b){return uint32_t(a)<uint32_t(b);}},
    {Op::UGreaterThan32,false,[](auto a,auto b){return uint32_t(a)>uint32_t(b);}},
    {Op::UMin32,false,[](auto a,auto b){return std::min(uint32_t(a),uint32_t(b));}},
  };
  Program program;
  program.srt_plan_complete = program.resource_tracking_complete = true;
  auto &block = AddValueBlock(program);
  Value data[4];
  for (uint32_t i=0;i<4;++i) data[i] = Value(&block.AppendNewInst(Op::GetUserData,
      {Value(static_cast<ScalarReg>(i))}));
  const auto a64 = Value(&block.AppendNewInst(Op::CompositeConstructU64,{data[0],data[2]}));
  const auto b64 = Value(&block.AppendNewInst(Op::CompositeConstructU64,{data[1],data[3]}));
  std::vector<uint32_t> sources;
  const auto add = [&](Value root, bool wide) {
    DescriptorSource source;
    source.dword_count = wide ? 2 : 1;
    source.dwords[0] = wide ? Value(&block.AppendNewInst(Op::CompositeExtractU64,{root,Value(0u)})) : root;
    if (wide) source.dwords[1] = Value(&block.AppendNewInst(Op::CompositeExtractU64,{root,Value(1u)}));
    sources.push_back(static_cast<uint32_t>(program.descriptor_sources.size()));
    program.descriptor_sources.push_back(source);
  };
  for (const auto &c: cases) {
    add(Value(&block.AppendNewInst(c.op,{c.wide?a64:data[0],c.wide?b64:data[1]})),c.wide);
  }
  const auto extracted = Value(&block.AppendNewInst(Op::BitFieldUExtract,{data[0],Value(3u),Value(17u)}));
  add(Value(&block.AppendNewInst(Op::IAdd32,{extracted,data[1]})),false);
  add(Value(&block.AppendNewInst(Op::SelectU32,{data[2],data[0],data[1]})),false);
  add(Value(&block.AppendNewInst(Op::BitwiseNot32,{data[0]})),false);
  auto plan = ExtractResourcePlan(program);
  uint32_t words[4]{};
  const SrtRuntime runtime{.user_data=words};
  std::vector<DescriptorValue> values;
  std::vector<uint32_t> flat;
  std::vector<uint8_t> active;
  uint64_t seed=0x483912abcdef1234ull;
  for (uint32_t pass=0;pass<2048;++pass) {
    for (auto &word: words) { seed^=seed<<13; seed^=seed>>7; seed^=seed<<17; word=uint32_t(seed); }
    if (pass<128) { words[0]=pass&1?0xffffffffu:0; words[1]=pass/2; words[2]=pass&1?0xffffffffu:0; }
    Check(EvaluateRuntimeSources(plan,sources,runtime,values,flat,plan.clean_flat_slots,active),
          "native arithmetic plan evaluation failed");
    const uint64_t a=uint64_t(words[0])|(uint64_t(words[2])<<32);
    const uint64_t b=uint64_t(words[1])|(uint64_t(words[3])<<32);
    for (size_t i=0;i<std::size(cases);++i) {
      const auto expected=cases[i].eval(a,b);
      Check(values[i].dwords[0]==uint32_t(expected) &&
            (!cases[i].wide || values[i].dwords[1]==uint32_t(expected>>32)),
            "native arithmetic differs from host arithmetic");
    }
    const auto offset=std::size(cases);
    Check(values[offset].dwords[0]==uint32_t(((words[0]>>3)&0x1ffffu)+words[1]),
          "native execution did not resume after portable node range");
    Check(values[offset+1].dwords[0]==(words[2]?words[0]:words[1]) &&
          values[offset+2].dwords[0]==~words[0], "native select/not mismatch");
  }
}

void TestSrtReaderExceptionUnwinds() {
  using namespace Libs::Graphics::ShaderRecompiler::IR;
  struct ReadException {};
  bool reject = true;
  auto plan = SrtPlan(0x10000);
  const auto read = +[](void *opaque, uint64_t, uint32_t *word) {
    if (*static_cast<bool *>(opaque)) throw ReadException{};
    *word = 123;
    return true;
  };
  const SrtRuntime runtime{.read_memory = read, .userdata = &reject};
  const uint32_t sources[] = {0};
  std::vector<DescriptorValue> values;
  std::vector<uint32_t> flat;
  std::vector<uint8_t> active;
  bool caught = false;
  try {
    (void)EvaluateRuntimeSources(plan, sources, runtime, values, flat,
                                 plan.clean_flat_slots, active);
  } catch (const ReadException &) {
    caught = true;
  }
  Check(caught, "SRT reader exception did not unwind to its caller");
  reject = false;
  Check(EvaluateRuntimeSources(plan, sources, runtime, values, flat,
                                plan.clean_flat_slots, active) &&
        values[0].dwords[0] == 123,
        "SRT evaluation did not recover after a reader exception");
}

} // namespace

namespace Common {

int DbgExitHandler(const char *, int, std::string_view) { std::abort(); }

int DbgExitHandler(const char *, int, fmt::text_style, std::string_view) {
  std::abort();
}

int DbgExitIfHandler(const char *, const char *, int) { return 1; }

void DbgExit(int) { std::abort(); }

} // namespace Common

int main() {
  TestMappedSrtUsesDirectReaderByDefault();
  TestIntegerRuntimeValueFollowsSrtReads();
  TestUnbasedFlatCacheHitMaterializes();
  TestFailedMaterializationPreservesPriorStage();
  TestMixedSamplerDuplicatesTheCorrectSnapshot();
  TestDepthComparisonFormatsAndSharedSampler();
  TestCompiledSrtSharedExpressionsKeepRuntimeReads();
  TestCompiledScalarAddressPlan();
  TestSrtReaderExceptionUnwinds();
  TestSrtNativeArithmetic();
  std::puts("ResourceMaterializationTests: all cases passed");
  return 0;
}

// Keep this focused standalone target self-contained by amalgamating its small
// typed-IR implementation set.
#include "graphics/shader/recompiler/ir/Block.cpp"
#include "graphics/shader/recompiler/ir/Program.cpp"
#include "graphics/shader/recompiler/ir/Type.cpp"
#include "graphics/shader/recompiler/ir/Value.cpp"
#include "graphics/shader/recompiler/ir/opcodes/ValueOpcodes.cpp"
