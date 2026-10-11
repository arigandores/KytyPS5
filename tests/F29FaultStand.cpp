// Track F, F29 fault area parse stand without the game (F44a HPP-791, ROADMAP s122 item 698(d)(1); form F43a section 3).
// Every repetition of every arm runs two stages on one layout of set bits:
//   G - the real parser: a compute pipeline from FAULT_BUFFER_PROCESS_SPV (gpu_tiler_shaders/fault_buffer_process_spv.h,
//       the words the emulator links) over a bitmap of CACHING_NUMPAGES / 8 bytes; the download buffer of the stand is
//       8 areas of 8 KiB plus a guard area of 8 KiB; the parser window is exactly area a (the form of
//       FaultManager::ProcessFaultBuffer), CACHING_NUMPAGES / 32 / 64 work groups. Before the dispatch area a is zero,
//       every other area holds a counter C_N and label records P_N + (area * 1024 + i) * 16 KiB, the guard area holds
//       the word 0xF29F29F29F29F29F (>= 2^40). After the dispatch all 9 areas and the bitmap are read back.
//   P - Libs::Graphics::ParseFaultArea of faultManager.cpp (the emulator function, not a copy) on the copy of the 9
//       areas starting at area a, clamp = Libs::Graphics::FixF29Enabled() (KYTY_FIX_F29 of this process). The visitor
//       does not call FindBuffer: it counts and classifies what was read.
// =0 and =1 are separate processes of one build (the knob is read once per process).
//
// Arms (ROADMAP s122 item 698(v)(4)):         B, layout                        a   C_N of the other areas
//   S0  0                                          -                                0   1023
//   S1  1000, one bit per word                     0                                    1023
//   S2  1023, one bit per word                     3                                    1023
//   E1  1024, one bit per word                     0                                    1023
//   O1  1100, one bit per word                     0                                    1023
//   O7  1100, one bit per word                     7                                    1023
//   D1  1120 = 35 words x 32 bits                  0                                    1023
//   L   1100, one bit per word                     0                                    5
// Layouts and the order of arms in each repetition come from splitmix64 of <seed>: a layout depends only on (seed, rep,
// arm), so the =0 and =1 processes of one seed see the same bits.
//
// Usage: f29_fault_stand <seed> <R> <out.tsv>
// Output: <out.tsv> - one row per (repetition, arm), header first; <out.tsv>.log - the emulator log (the lines
// "FixF29: overflow" of ParseFaultArea are read there); stdout - "FIXF29 env=<v> on=<0|1>", "DEVICE <name>",
// "DONE rows=<n>". Exit 0; 2 - bad arguments; 5 - Vulkan setup failed; 6 - a P read would leave the stand copy (the
// row is not written).
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/cache/faultManager.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "gpu_tiler_shaders/fault_buffer_process_spv.h"

#include <algorithm>
#include <array>
#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unordered_set>
#include <vector>

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <bcrypt.h>
#undef min
#undef max

#pragma comment(lib, "bcrypt.lib")

namespace {

using Libs::Graphics::BufferCache;

constexpr uint32_t AreaWords   = 1024;                 // MaxPageFaults of faultManager.cpp (8 KiB of uint64)
constexpr uint32_t Areas       = 8;                    // MaxPendingFaults
constexpr uint32_t CopyWords   = (Areas + 1) * AreaWords; // 8 areas + the guard area
constexpr uint64_t PageBytes   = BufferCache::CACHING_PAGESIZE;
constexpr uint64_t NumPages    = BufferCache::CACHING_NUMPAGES;
constexpr uint32_t MapWords    = static_cast<uint32_t>(NumPages / 32);
constexpr uint64_t MapBytes    = NumPages / 8;
constexpr uint64_t LabelBase   = uint64_t {1} << 36;   // P_N
constexpr uint64_t GuardWord   = 0xF29F29F29F29F29Full;
constexpr uint64_t ExitBound   = uint64_t {1} << 40;
constexpr uint32_t LastRecord  = 1023;                 // the stand's own expectation (not the emulator constant)

enum Arm : int { ARM_S0, ARM_S1, ARM_S2, ARM_E1, ARM_O1, ARM_O7, ARM_D1, ARM_L, ARM_COUNT };
const char* const ARM_NAMES[ARM_COUNT] = {"S0", "S1", "S2", "E1", "O1", "O7", "D1", "L"};
struct ArmDef {
	uint32_t bits;
	bool     dense; // 32 bits per word
	uint32_t area;
	uint64_t neighbour_count;
};
const ArmDef ARMS[ARM_COUNT] = {
    {0, false, 0, 1023},    {1000, false, 0, 1023}, {1023, false, 3, 1023}, {1024, false, 0, 1023},
    {1100, false, 0, 1023}, {1100, false, 7, 1023}, {1120, true, 0, 1023},  {1100, false, 0, 5},
};

uint64_t SplitMix(uint64_t* state) {
	uint64_t z = (*state += 0x9E3779B97F4A7C15ull);
	z          = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
	z          = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
	return z ^ (z >> 31);
}

std::string Sha256Hex(const uint8_t* data, size_t size) {
	BCRYPT_ALG_HANDLE  alg  = nullptr;
	BCRYPT_HASH_HANDLE hash = nullptr;
	uint8_t            digest[32] {};
	std::string        hex;
	if (BCryptOpenAlgorithmProvider(&alg, BCRYPT_SHA256_ALGORITHM, nullptr, 0) == 0) {
		if (BCryptCreateHash(alg, &hash, nullptr, 0, nullptr, 0, 0) == 0) {
			if (BCryptHashData(hash, const_cast<PUCHAR>(data), static_cast<ULONG>(size), 0) == 0 &&
			    BCryptFinishHash(hash, digest, sizeof(digest), 0) == 0) {
				char b[3];
				for (uint8_t v: digest) {
					std::snprintf(b, sizeof(b), "%02x", v);
					hex += b;
				}
			}
			BCryptDestroyHash(hash);
		}
		BCryptCloseAlgorithmProvider(alg, 0);
	}
	return hex;
}

std::string SortedSha(std::vector<uint64_t> values) {
	std::sort(values.begin(), values.end());
	return Sha256Hex(reinterpret_cast<const uint8_t*>(values.data()), values.size() * sizeof(uint64_t));
}

// The set bits of one (seed, rep, arm): map word index and bit mask; the expected record values page << 14.
struct Layout {
	std::vector<std::pair<uint32_t, uint32_t>> words;
	std::vector<uint64_t>                      expected;
};

Layout MakeLayout(uint64_t seed, uint32_t rep, int arm) {
	Layout   l;
	uint64_t state = seed ^ (uint64_t {rep} << 32) ^ (static_cast<uint64_t>(arm) << 8) ^ 0xF29ull;
	const auto& d  = ARMS[arm];
	const uint32_t nwords = d.dense ? d.bits / 32 : d.bits;
	std::unordered_set<uint32_t> used;
	while (l.words.size() < nwords) {
		const auto w = static_cast<uint32_t>(SplitMix(&state) % MapWords);
		if (!used.insert(w).second) {
			continue;
		}
		const uint32_t mask = d.dense ? 0xFFFFFFFFu : (1u << (SplitMix(&state) % 32));
		l.words.emplace_back(w, mask);
		for (uint32_t b = 0; b < 32; b++) {
			if ((mask >> b) & 1u) {
				l.expected.push_back((uint64_t {w} * 32 + b) * PageBytes);
			}
		}
	}
	return l;
}

// ---- minimal Vulkan compute: one device, host-visible coherent buffers, the parser pipeline ----

struct HostBuffer {
	vk::Buffer       buffer = nullptr;
	vk::DeviceMemory memory = nullptr;
	void*            mapped = nullptr;
	uint64_t         size   = 0;
};

struct Gpu {
	vk::Instance            instance = nullptr;
	vk::PhysicalDevice      physical = nullptr;
	vk::Device              device   = nullptr;
	vk::Queue               queue    = nullptr;
	uint32_t                family   = 0;
	vk::CommandPool         pool     = nullptr;
	vk::CommandBuffer       cmd      = nullptr;
	vk::Fence               fence    = nullptr;
	vk::DescriptorSetLayout set_layout = nullptr;
	vk::DescriptorPool      desc_pool  = nullptr;
	vk::DescriptorSet       set        = nullptr;
	vk::PipelineLayout      layout     = nullptr;
	vk::Pipeline            pipeline   = nullptr;
	HostBuffer              map;
	HostBuffer              download;
	std::string             name;
};

bool Ok(vk::Result r, const char* what) {
	if (r != vk::Result::eSuccess) {
		std::printf("VULKAN %s failed %d\n", what, static_cast<int>(r));
		return false;
	}
	return true;
}

bool CreateHostBuffer(Gpu* g, uint64_t size, HostBuffer* out) {
	vk::BufferCreateInfo info {};
	info.sType       = vk::StructureType::eBufferCreateInfo;
	info.size        = size;
	info.usage       = vk::BufferUsageFlagBits::eStorageBuffer;
	info.sharingMode = vk::SharingMode::eExclusive;
	if (!Ok(g->device.createBuffer(&info, nullptr, &out->buffer), "createBuffer")) {
		return false;
	}
	vk::MemoryRequirements req {};
	g->device.getBufferMemoryRequirements(out->buffer, &req);
	vk::PhysicalDeviceMemoryProperties props {};
	g->physical.getMemoryProperties(&props);
	const auto want = vk::MemoryPropertyFlagBits::eHostVisible | vk::MemoryPropertyFlagBits::eHostCoherent;
	uint32_t   type = UINT32_MAX;
	for (uint32_t i = 0; i < props.memoryTypeCount; i++) {
		if (((req.memoryTypeBits >> i) & 1u) != 0 && (props.memoryTypes[i].propertyFlags & want) == want) {
			type = i;
			break;
		}
	}
	if (type == UINT32_MAX) {
		std::printf("VULKAN no host-visible coherent memory type\n");
		return false;
	}
	vk::MemoryAllocateInfo alloc {};
	alloc.sType           = vk::StructureType::eMemoryAllocateInfo;
	alloc.allocationSize  = req.size;
	alloc.memoryTypeIndex = type;
	if (!Ok(g->device.allocateMemory(&alloc, nullptr, &out->memory), "allocateMemory") ||
	    !Ok(g->device.bindBufferMemory(out->buffer, out->memory, 0), "bindBufferMemory") ||
	    !Ok(g->device.mapMemory(out->memory, 0, VK_WHOLE_SIZE, {}, &out->mapped), "mapMemory")) {
		return false;
	}
	out->size = size;
	return true;
}

bool InitGpu(Gpu* g) {
	static vk::detail::DynamicLoader loader;
	const auto gipa = loader.getProcAddress<PFN_vkGetInstanceProcAddr>("vkGetInstanceProcAddr");
	if (gipa == nullptr) {
		std::printf("VULKAN loader not found\n");
		return false;
	}
	VULKAN_HPP_DEFAULT_DISPATCHER.init(gipa);
	vk::ApplicationInfo app {};
	app.sType            = vk::StructureType::eApplicationInfo;
	app.pApplicationName = "F29FaultStand";
	app.apiVersion       = VK_API_VERSION_1_3;
	vk::InstanceCreateInfo ii {};
	ii.sType            = vk::StructureType::eInstanceCreateInfo;
	ii.pApplicationInfo = &app;
	if (!Ok(vk::createInstance(&ii, nullptr, &g->instance), "createInstance")) {
		return false;
	}
	VULKAN_HPP_DEFAULT_DISPATCHER.init(g->instance);
	uint32_t n = 0;
	if (!Ok(g->instance.enumeratePhysicalDevices(&n, nullptr), "enumeratePhysicalDevices") || n == 0) {
		return false;
	}
	std::vector<vk::PhysicalDevice> devices(n);
	if (!Ok(g->instance.enumeratePhysicalDevices(&n, devices.data()), "enumeratePhysicalDevices")) {
		return false;
	}
	for (auto pd: devices) {
		vk::PhysicalDeviceFeatures f {};
		pd.getFeatures(&f);
		if (f.shaderInt64 != VK_TRUE) {
			continue;
		}
		uint32_t qn = 0;
		pd.getQueueFamilyProperties(&qn, nullptr);
		std::vector<vk::QueueFamilyProperties> qs(qn);
		pd.getQueueFamilyProperties(&qn, qs.data());
		for (uint32_t i = 0; i < qn; i++) {
			if (qs[i].queueFlags & vk::QueueFlagBits::eCompute) {
				g->physical = pd;
				g->family   = i;
				break;
			}
		}
		if (g->physical != nullptr) {
			break;
		}
	}
	if (g->physical == nullptr) {
		std::printf("VULKAN no compute device with shaderInt64\n");
		return false;
	}
	vk::PhysicalDeviceProperties pp {};
	g->physical.getProperties(&pp);
	g->name = pp.deviceName.data();

	float                     priority = 1.0f;
	vk::DeviceQueueCreateInfo qi {};
	qi.sType            = vk::StructureType::eDeviceQueueCreateInfo;
	qi.queueFamilyIndex = g->family;
	qi.queueCount       = 1;
	qi.pQueuePriorities = &priority;
	vk::PhysicalDeviceFeatures features {};
	features.shaderInt64 = VK_TRUE;
	vk::DeviceCreateInfo di {};
	di.sType                = vk::StructureType::eDeviceCreateInfo;
	di.queueCreateInfoCount = 1;
	di.pQueueCreateInfos    = &qi;
	di.pEnabledFeatures     = &features;
	if (!Ok(g->physical.createDevice(&di, nullptr, &g->device), "createDevice")) {
		return false;
	}
	VULKAN_HPP_DEFAULT_DISPATCHER.init(g->device);
	g->device.getQueue(g->family, 0, &g->queue);

	vk::CommandPoolCreateInfo pi {};
	pi.sType            = vk::StructureType::eCommandPoolCreateInfo;
	pi.queueFamilyIndex = g->family;
	pi.flags            = vk::CommandPoolCreateFlagBits::eResetCommandBuffer;
	if (!Ok(g->device.createCommandPool(&pi, nullptr, &g->pool), "createCommandPool")) {
		return false;
	}
	vk::CommandBufferAllocateInfo ai {};
	ai.sType              = vk::StructureType::eCommandBufferAllocateInfo;
	ai.commandPool        = g->pool;
	ai.level              = vk::CommandBufferLevel::ePrimary;
	ai.commandBufferCount = 1;
	if (!Ok(g->device.allocateCommandBuffers(&ai, &g->cmd), "allocateCommandBuffers")) {
		return false;
	}
	vk::FenceCreateInfo fi {};
	fi.sType = vk::StructureType::eFenceCreateInfo;
	if (!Ok(g->device.createFence(&fi, nullptr, &g->fence), "createFence")) {
		return false;
	}

	if (!CreateHostBuffer(g, MapBytes, &g->map) ||
	    !CreateHostBuffer(g, uint64_t {CopyWords} * sizeof(uint64_t), &g->download)) {
		return false;
	}

	const vk::DescriptorSetLayoutBinding bindings[] {
	    {0, vk::DescriptorType::eStorageBuffer, 1, vk::ShaderStageFlagBits::eCompute, nullptr},
	    {1, vk::DescriptorType::eStorageBuffer, 1, vk::ShaderStageFlagBits::eCompute, nullptr},
	};
	vk::DescriptorSetLayoutCreateInfo li {};
	li.sType        = vk::StructureType::eDescriptorSetLayoutCreateInfo;
	li.bindingCount = 2;
	li.pBindings    = bindings;
	if (!Ok(g->device.createDescriptorSetLayout(&li, nullptr, &g->set_layout), "createDescriptorSetLayout")) {
		return false;
	}
	vk::DescriptorPoolSize       ps {vk::DescriptorType::eStorageBuffer, 2};
	vk::DescriptorPoolCreateInfo dpi {};
	dpi.sType         = vk::StructureType::eDescriptorPoolCreateInfo;
	dpi.maxSets       = 1;
	dpi.poolSizeCount = 1;
	dpi.pPoolSizes    = &ps;
	if (!Ok(g->device.createDescriptorPool(&dpi, nullptr, &g->desc_pool), "createDescriptorPool")) {
		return false;
	}
	vk::DescriptorSetAllocateInfo dsai {};
	dsai.sType              = vk::StructureType::eDescriptorSetAllocateInfo;
	dsai.descriptorPool     = g->desc_pool;
	dsai.descriptorSetCount = 1;
	dsai.pSetLayouts        = &g->set_layout;
	if (!Ok(g->device.allocateDescriptorSets(&dsai, &g->set), "allocateDescriptorSets")) {
		return false;
	}
	vk::PipelineLayoutCreateInfo pli {};
	pli.sType          = vk::StructureType::ePipelineLayoutCreateInfo;
	pli.setLayoutCount = 1;
	pli.pSetLayouts    = &g->set_layout;
	if (!Ok(g->device.createPipelineLayout(&pli, nullptr, &g->layout), "createPipelineLayout")) {
		return false;
	}
	vk::ShaderModuleCreateInfo mi {};
	mi.sType    = vk::StructureType::eShaderModuleCreateInfo;
	mi.codeSize = sizeof(FAULT_BUFFER_PROCESS_SPV);
	mi.pCode    = FAULT_BUFFER_PROCESS_SPV;
	vk::ShaderModule module = nullptr;
	if (!Ok(g->device.createShaderModule(&mi, nullptr, &module), "createShaderModule")) {
		return false;
	}
	vk::ComputePipelineCreateInfo ci {};
	ci.sType        = vk::StructureType::eComputePipelineCreateInfo;
	ci.stage.sType  = vk::StructureType::ePipelineShaderStageCreateInfo;
	ci.stage.stage  = vk::ShaderStageFlagBits::eCompute;
	ci.stage.module = module;
	ci.stage.pName  = "main";
	ci.layout       = g->layout;
	const auto r    = g->device.createComputePipelines(nullptr, 1, &ci, nullptr, &g->pipeline);
	g->device.destroyShaderModule(module, nullptr);
	return Ok(r, "createComputePipelines");
}

// Stage G: the parser over the bitmap with the window = area a of the download buffer.
bool RunParser(Gpu* g, uint32_t a) {
	const vk::DescriptorBufferInfo infos[] {
	    {g->map.buffer, 0, MapBytes},
	    {g->download.buffer, uint64_t {a} * AreaWords * sizeof(uint64_t), uint64_t {AreaWords} * sizeof(uint64_t)},
	};
	std::array<vk::WriteDescriptorSet, 2> writes {};
	for (uint32_t i = 0; i < 2; i++) {
		writes[i].sType           = vk::StructureType::eWriteDescriptorSet;
		writes[i].dstSet          = g->set;
		writes[i].dstBinding      = i;
		writes[i].descriptorCount = 1;
		writes[i].descriptorType  = vk::DescriptorType::eStorageBuffer;
		writes[i].pBufferInfo     = &infos[i];
	}
	g->device.updateDescriptorSets(2, writes.data(), 0, nullptr);

	if (!Ok(g->cmd.reset({}), "resetCommandBuffer")) {
		return false;
	}
	vk::CommandBufferBeginInfo bi {};
	bi.sType = vk::StructureType::eCommandBufferBeginInfo;
	bi.flags = vk::CommandBufferUsageFlagBits::eOneTimeSubmit;
	if (!Ok(g->cmd.begin(&bi), "beginCommandBuffer")) {
		return false;
	}
	vk::MemoryBarrier host_to_shader {};
	host_to_shader.sType         = vk::StructureType::eMemoryBarrier;
	host_to_shader.srcAccessMask = vk::AccessFlagBits::eHostWrite;
	host_to_shader.dstAccessMask = vk::AccessFlagBits::eShaderRead | vk::AccessFlagBits::eShaderWrite;
	g->cmd.pipelineBarrier(vk::PipelineStageFlagBits::eHost, vk::PipelineStageFlagBits::eComputeShader, {}, 1,
	                       &host_to_shader, 0, nullptr, 0, nullptr);
	g->cmd.bindPipeline(vk::PipelineBindPoint::eCompute, g->pipeline);
	g->cmd.bindDescriptorSets(vk::PipelineBindPoint::eCompute, g->layout, 0, 1, &g->set, 0, nullptr);
	const uint64_t num_threads    = NumPages / 32;
	const uint64_t num_workgroups = (num_threads + 63) / 64;
	g->cmd.dispatch(static_cast<uint32_t>(num_workgroups), 1, 1);
	vk::MemoryBarrier shader_to_host {};
	shader_to_host.sType         = vk::StructureType::eMemoryBarrier;
	shader_to_host.srcAccessMask = vk::AccessFlagBits::eShaderWrite;
	shader_to_host.dstAccessMask = vk::AccessFlagBits::eHostRead;
	g->cmd.pipelineBarrier(vk::PipelineStageFlagBits::eComputeShader, vk::PipelineStageFlagBits::eHost, {}, 1,
	                       &shader_to_host, 0, nullptr, 0, nullptr);
	if (!Ok(g->cmd.end(), "endCommandBuffer")) {
		return false;
	}
	vk::SubmitInfo si {};
	si.sType              = vk::StructureType::eSubmitInfo;
	si.commandBufferCount = 1;
	si.pCommandBuffers    = &g->cmd;
	if (!Ok(g->device.resetFences(1, &g->fence), "resetFences") || !Ok(g->queue.submit(1, &si, g->fence), "submit") ||
	    !Ok(g->device.waitForFences(1, &g->fence, VK_TRUE, UINT64_MAX), "waitForFences")) {
		return false;
	}
	return true;
}

struct Row {
	uint32_t    rep = 0, seq = 0;
	int         arm = 0;
	uint32_t    area = 0, bits = 0, words = 0;
	uint64_t    raw = 0, raw_hi = 0, stored = 0, read = 0, read_vis = 0;
	uint64_t    out_area = 0, out_buf = 0, cls_zero = 0, cls_low = 0, cls_page = 0, cls_exit = 0;
	uint64_t    extra = 0, dup = 0, map_left = 0, nb_touched = 0;
	int         h_inproc = -1; // -1: not measured in this process
	std::string h_sha, exp_sha;
};

uint64_t Neighbour(uint32_t area, uint32_t i, uint64_t count) {
	return i == 0 ? count : LabelBase + (uint64_t {area} * AreaWords + i) * PageBytes;
}

// One repetition of one arm; false on a Vulkan failure; *escape - a P read would leave the copy.
bool RunArm(Gpu* g, uint64_t seed, uint32_t rep, uint32_t seq, int arm, bool clamp, Row* row, bool* escape) {
	const auto& d = ARMS[arm];
	const Layout l = MakeLayout(seed, rep, arm);
	row->rep   = rep;
	row->seq   = seq;
	row->arm   = arm;
	row->area  = d.area;
	row->bits  = static_cast<uint32_t>(l.expected.size());
	row->words = static_cast<uint32_t>(l.words.size());

	auto* map = static_cast<uint32_t*>(g->map.mapped);
	std::memset(map, 0, MapBytes);
	for (const auto& [w, mask]: l.words) {
		map[w] |= mask;
	}
	auto* dl = static_cast<uint64_t*>(g->download.mapped);
	for (uint32_t ar = 0; ar < Areas; ar++) {
		for (uint32_t i = 0; i < AreaWords; i++) {
			dl[ar * AreaWords + i] = ar == d.area ? 0 : Neighbour(ar, i, d.neighbour_count);
		}
	}
	for (uint32_t i = 0; i < AreaWords; i++) {
		dl[Areas * AreaWords + i] = GuardWord;
	}

	if (!RunParser(g, d.area)) {
		return false;
	}

	std::vector<uint64_t> copy(dl, dl + CopyWords);
	for (uint32_t w = 0; w < MapWords; w++) {
		row->map_left += map[w] != 0 ? 1 : 0;
	}
	for (uint32_t ar = 0; ar <= Areas; ar++) {
		if (ar == d.area) {
			continue;
		}
		for (uint32_t i = 0; i < AreaWords; i++) {
			const uint64_t want = ar == Areas ? GuardWord : Neighbour(ar, i, d.neighbour_count);
			row->nb_touched += copy[ar * AreaWords + i] != want ? 1 : 0;
		}
	}

	// G
	const uint64_t* area_ptr = copy.data() + uint64_t {d.area} * AreaWords;
	row->raw    = area_ptr[0] & 0xFFFFFFFFu;
	row->raw_hi = area_ptr[0] >> 32;
	for (uint32_t i = 1; i <= LastRecord; i++) {
		row->stored += area_ptr[i] != 0 ? 1 : 0;
	}
	const std::unordered_set<uint64_t> expected(l.expected.begin(), l.expected.end());
	std::unordered_set<uint64_t>       seen;
	const uint64_t                     first = std::min<uint64_t>(row->raw, LastRecord);
	for (uint32_t i = 1; i <= first; i++) {
		const uint64_t v = area_ptr[i];
		row->extra += expected.count(v) == 0 ? 1 : 0;
		row->dup += seen.insert(v).second ? 0 : 1;
	}

	// P (the emulator function)
	if (uint64_t {d.area} * AreaWords + row->raw >= CopyWords) {
		*escape = true;
		return true;
	}
	std::vector<uint64_t> pages;
	const auto            parse = Libs::Graphics::ParseFaultArea(
        area_ptr, clamp,
        [&](uint32_t index, uint64_t v) {
            row->read_vis++;
            if (index < AreaWords) {
                pages.push_back(v);
                return;
            }
            row->out_area++;
            if (uint64_t {d.area} * AreaWords + index >= uint64_t {Areas} * AreaWords) {
                row->out_buf++;
            }
            if (v == 0) {
                row->cls_zero++;
            } else if (v < PageBytes) {
                row->cls_low++;
            } else if (v % PageBytes == 0 && v < ExitBound) {
                row->cls_page++;
            } else {
                row->cls_exit++;
            }
        },
        {seq, d.area});
	row->read = parse.count;
	if (parse.raw != row->raw) {
		row->read = UINT64_MAX; // the function saw another counter: the identity read = count fails visibly
	}
	row->h_sha = SortedSha(pages);
	std::vector<uint64_t> exp_first = l.expected;
	row->exp_sha                    = SortedSha(exp_first);

	// h_inproc (only at =1): the same copy through the same function with clamp = false - the first min(raw, 1023)
	// records in the order read are equal. At =0 the clamped call would write overflow lines; not measured.
	if (clamp) {
		std::vector<uint64_t> unclamped;
		(void)Libs::Graphics::ParseFaultArea(area_ptr, false, [&](uint32_t index, uint64_t v) {
			if (index < AreaWords) {
				unclamped.push_back(v);
			}
		});
		row->h_inproc = unclamped == pages ? 1 : 0;
	}
	return true;
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 4) {
		std::fprintf(stderr, "usage: f29_fault_stand <seed> <R> <out.tsv>\n");
		return 2;
	}
	const uint64_t    seed     = std::strtoull(argv[1], nullptr, 10);
	const int         reps     = std::atoi(argv[2]);
	const std::string out_path = argv[3];
	if (reps <= 0) {
		return 2;
	}

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction   = Config::LogDirection::File;
	options.printf_output_file = out_path + ".log";
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	const char* env  = std::getenv("KYTY_FIX_F29");
	const bool  fix  = Libs::Graphics::FixF29Enabled();
	std::printf("FIXF29 env=%s on=%d\n", env != nullptr ? env : "(unset)", fix ? 1 : 0);

	Gpu g;
	if (!InitGpu(&g)) {
		return 5;
	}
	std::printf("DEVICE %s\n", g.name.c_str());

	FILE* out = std::fopen(out_path.c_str(), "wb");
	if (out == nullptr) {
		return 5;
	}
	std::fprintf(out, "seed\tfix\trep\tseq\tarm\tarea\tbits\twords\traw\traw_hi\tstored\tread\tread_vis\tout_area\tout_buf\t"
	                  "cls_zero\tcls_low\tcls_page\tcls_exit\textra\tdup\tmap_left\tnb_touched\th_inproc\th_sha\texp_sha\n");
	uint32_t seq  = 0;
	int      rows = 0;
	for (uint32_t rep = 0; rep < static_cast<uint32_t>(reps); rep++) {
		std::array<int, ARM_COUNT> order {};
		for (int i = 0; i < ARM_COUNT; i++) {
			order[i] = i;
		}
		uint64_t state = seed ^ (uint64_t {rep} << 40) ^ 0x5EEDull;
		for (int i = ARM_COUNT - 1; i > 0; i--) {
			const auto j = static_cast<int>(SplitMix(&state) % static_cast<uint64_t>(i + 1));
			std::swap(order[i], order[j]);
		}
		for (int arm: order) {
			Row  row;
			bool escape = false;
			++seq;
			if (!RunArm(&g, seed, rep, seq, arm, fix, &row, &escape)) {
				std::fclose(out);
				return 5;
			}
			if (escape) {
				std::printf("ESCAPE rep=%u arm=%s raw=%" PRIu64 "\n", rep, ARM_NAMES[arm], row.raw);
				std::fclose(out);
				return 6;
			}
			std::fprintf(out,
			             "%" PRIu64 "\t%d\t%u\t%u\t%s\t%u\t%u\t%u\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64
			             "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64
			             "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%d\t%s\t%s\n",
			             seed, fix ? 1 : 0, row.rep, row.seq, ARM_NAMES[arm], row.area, row.bits, row.words, row.raw,
			             row.raw_hi, row.stored, row.read, row.read_vis, row.out_area, row.out_buf, row.cls_zero,
			             row.cls_low, row.cls_page, row.cls_exit, row.extra, row.dup, row.map_left, row.nb_touched,
			             row.h_inproc, row.h_sha.c_str(), row.exp_sha.c_str());
			rows++;
		}
	}
	std::fclose(out);
	g.device.waitIdle();
	std::printf("DONE rows=%d\n", rows);
	return 0;
}
