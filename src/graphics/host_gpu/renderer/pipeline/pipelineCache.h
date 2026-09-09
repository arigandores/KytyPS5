#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINECACHE_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINECACHE_H_

#include "common/abi.h"
#include "common/assert.h"
#include "common/common.h"
#include "common/threads.h"
#include "graphics/host_gpu/renderer/renderTarget.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/shader.h"

#include <cstddef>
#include <filesystem>
#include <memory>
#include <span>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <atomic>
#include <condition_variable>
#include <deque>
#include <functional>
#include <mutex>
#include <thread>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;
struct RenderColorInfo;
struct RenderDepthInfo;
class CommandBuffer;

namespace HW {
class Context;
class Shader;
class UserConfig;
struct ComputeShaderInfo;
} // namespace HW

#pragma pack(push, 1)

struct PipelineStaticParameters {
	bool                       negative_one_to_one      = false;
	bool                       depth_clip_enable        = true;
	vk::PrimitiveTopology      topology                 = vk::PrimitiveTopology::ePointList;
	bool                       primitive_restart_enable = false;
	uint32_t                   samples                  = 1;
	bool                       sample_shading_enable    = false;
	bool                       depth_bounds_test_enable = false;
	float                      depth_min_bounds         = 0.0f;
	float                      depth_max_bounds         = 0.0f;
	bool                       stencil_test_enable      = false;
	PipelineStencilStaticState stencil_front;
	PipelineStencilStaticState stencil_back;
	uint32_t                   color_mask[RENDER_COLOR_ATTACHMENTS_MAX]           = {};
	bool                       cull_front                                         = false;
	bool                       cull_back                                          = false;
	bool                       face                                               = false;
	bool                       provoking_vtx_last                                 = false;
	vk::PolygonMode            polygon_mode                                       = vk::PolygonMode::eFill;
	uint8_t                    color_srcblend[RENDER_COLOR_ATTACHMENTS_MAX]       = {};
	uint8_t                    color_comb_fcn[RENDER_COLOR_ATTACHMENTS_MAX]       = {};
	uint8_t                    color_destblend[RENDER_COLOR_ATTACHMENTS_MAX]      = {};
	uint8_t                    alpha_srcblend[RENDER_COLOR_ATTACHMENTS_MAX]       = {};
	uint8_t                    alpha_comb_fcn[RENDER_COLOR_ATTACHMENTS_MAX]       = {};
	uint8_t                    alpha_destblend[RENDER_COLOR_ATTACHMENTS_MAX]      = {};
	bool                       separate_alpha_blend[RENDER_COLOR_ATTACHMENTS_MAX] = {};
	bool                       blend_enable[RENDER_COLOR_ATTACHMENTS_MAX]         = {};
	bool                       blend_bypass[RENDER_COLOR_ATTACHMENTS_MAX]         = {};

	bool operator==(const PipelineStaticParameters& other) const noexcept;
};

#pragma pack(pop)

static_assert(std::is_trivially_copyable_v<PipelineStaticParameters>);
static_assert(std::is_standard_layout_v<PipelineStaticParameters>);
static_assert(alignof(PipelineStaticParameters) == 1);
static_assert(sizeof(PipelineStaticParameters) == 166);

struct PipelineRenderingState {
	std::array<vk::Format, RENDER_COLOR_ATTACHMENTS_MAX> color_formats {};
	vk::Format                                           depth_format   = vk::Format::eUndefined;
	vk::Format                                           stencil_format = vk::Format::eUndefined;
	uint32_t                                             color_count    = 0;

	bool operator==(const PipelineRenderingState&) const = default;
};

struct PipelineVertexInputState {
	struct Binding {
		uint32_t stride                           = 0;
		bool     instance                         = false;
		bool     operator==(const Binding&) const = default;
	};
	struct Attribute {
		uint32_t offset                             = 0;
		uint8_t  binding                            = 0;
		bool     operator==(const Attribute&) const = default;
	};

	std::array<Binding, ShaderVertexInputInfo::RES_MAX>   bindings {};
	std::array<Attribute, ShaderVertexInputInfo::RES_MAX> attributes {};
	uint8_t                                               binding_count   = 0;
	uint8_t                                               attribute_count = 0;

	bool operator==(const PipelineVertexInputState&) const = default;
};

struct ShaderProgram {
	uint64_t         id     = 0;
	vk::ShaderModule module = nullptr;

	explicit operator bool() const { return id != 0 && module != nullptr; }
};

class PipelineCache {
public:
	explicit PipelineCache(GraphicContext& graphics);
	~PipelineCache();
	KYTY_CLASS_NO_COPY(PipelineCache);
	void Save();

	struct Pipeline {
		vk::PipelineLayout      pipeline_layout       = nullptr;
		vk::Pipeline            pipeline              = nullptr;
		vk::DescriptorSetLayout descriptor_set_layout = nullptr;
		bool                    uses_push_descriptors = false;
	};

	struct GraphicsPrograms {
		ShaderProgram vertex;
		ShaderProgram pixel;
	};

	GraphicsPrograms
	GetGraphicsPrograms(const HW::VertexShaderInfo& vertex_regs,
	                    const HW::PixelShaderInfo& pixel_regs, const HW::ShaderRegisters& sh,
	                    const HW::Context& context, const HW::UserConfig& user_config,
	                    std::span<const Prospero::ColorComponentMapping, 8> target_export_mapping,
	                    bool pixel_active, ShaderVertexInputInfo& vertex_info,
	                    ShaderPixelInputInfo& pixel_info);
	ShaderProgram GetComputeProgram(const HW::ComputeShaderInfo& regs,
	                                const HW::ShaderRegisters&   sh,
	                                ShaderComputeInputInfo&      input_info);

	// nullptr: the pipeline is still being compiled by a worker thread (KYTY_ASYNC_PIPELINES); the
	// caller skips the draw and retries with the next one that needs the same pipeline.
	Pipeline*
	CreateGraphicsPipeline(std::span<const RenderColorInfo> colors, const RenderDepthInfo& depth,
	                       const ShaderVertexInputInfo& vs_input_info, CommandBuffer& command,
	                       const ShaderPixelInputInfo* ps_input_info,
	                       vk::PrimitiveTopology topology, bool primitive_restart_enable,
	                       const ShaderProgram& vertex_program, const ShaderProgram& pixel_program);
	Pipeline& CreateComputePipeline(const ShaderComputeInputInfo& input_info,
	                                const ShaderProgram&          compute_program);
	// PM4 lookahead (KYTY_ASYNC_COMPUTE): translates the program of a future dispatch and queues
	// its pipeline compile to the worker pool; CreateComputePipeline waits for it if it is still
	// compiling when the dispatch arrives.
	void PrefetchComputePipeline(const HW::ComputeShaderInfo& regs, const HW::ShaderRegisters& sh,
	                             ShaderComputeInputInfo input_info);
	// Block until every queued graphics pipeline has been compiled.
	void WaitForPendingPipelines();
	// Pipelines whose compilation has not finished yet.
	[[nodiscard]] uint32_t PendingPipelineCount() const {
		return m_pending_pipelines.load(std::memory_order_relaxed);
	}

private:
	struct ProgramCache;

	struct GraphicsPipelineKey {
		PipelineRenderingState   rendering;
		uint64_t                 vs_shader_id = 0;
		uint64_t                 ps_shader_id = 0;
		PipelineVertexInputState vertex_input;
		PipelineStaticParameters static_params;

		bool operator==(const GraphicsPipelineKey& other) const {
			return rendering == other.rendering && vs_shader_id == other.vs_shader_id &&
			       ps_shader_id == other.ps_shader_id && vertex_input == other.vertex_input &&
			       static_params == other.static_params;
		}
	};

	struct PipelineKeyHash {
		static void Mix(std::size_t& hash, std::size_t value) {
			hash ^= value + static_cast<std::size_t>(0x9e3779b97f4a7c15ull) + (hash << 6u) +
			        (hash >> 2u);
		}

		static void MixStaticParams(std::size_t& hash, const PipelineStaticParameters& params) {
			const auto* bytes = reinterpret_cast<const uint8_t*>(&params);
			for (std::size_t i = 0; i < sizeof(params); i++) {
				Mix(hash, bytes[i]);
			}
		}

		static void MixRendering(std::size_t& hash, const PipelineRenderingState& rendering) {
			Mix(hash, rendering.color_count);
			for (uint32_t i = 0; i < rendering.color_count; i++) {
				Mix(hash, static_cast<uint32_t>(rendering.color_formats[i]));
			}
			Mix(hash, static_cast<uint32_t>(rendering.depth_format));
			Mix(hash, static_cast<uint32_t>(rendering.stencil_format));
		}
	};

	struct GraphicsPipelineKeyHash {
		std::size_t operator()(const GraphicsPipelineKey& key) const {
			std::size_t hash = 0;
			PipelineKeyHash::MixRendering(hash, key.rendering);
			PipelineKeyHash::Mix(hash, key.vs_shader_id);
			PipelineKeyHash::Mix(hash, key.ps_shader_id);
			PipelineKeyHash::Mix(hash, key.vertex_input.binding_count);
			for (uint32_t i = 0; i < key.vertex_input.binding_count; i++) {
				PipelineKeyHash::Mix(hash, key.vertex_input.bindings[i].stride);
				PipelineKeyHash::Mix(hash, key.vertex_input.bindings[i].instance);
			}
			PipelineKeyHash::Mix(hash, key.vertex_input.attribute_count);
			for (uint32_t i = 0; i < key.vertex_input.attribute_count; i++) {
				PipelineKeyHash::Mix(hash, key.vertex_input.attributes[i].offset);
				PipelineKeyHash::Mix(hash, key.vertex_input.attributes[i].binding);
			}
			PipelineKeyHash::MixStaticParams(hash, key.static_params);
			return hash;
		}
	};

	GraphicContext&               m_graphics;
	std::unique_ptr<ProgramCache> m_program_cache;
	vk::PipelineCache             m_driver_cache = nullptr;
	std::filesystem::path         m_driver_cache_path;
	// ready: the worker finished CreatePipelineInternal (release); the draw path reads the
	// pipeline handles only after observing it (acquire).
	struct GraphicsPipelineEntry: Pipeline {
		std::atomic<bool> ready {false};
	};
	// Looks the pipeline up or queues its creation; `queued` = this call queued it. Called with
	// m_mutex held; the entry may not be ready yet.
	GraphicsPipelineEntry* CreateGraphicsPipelineLocked(
	    std::span<const RenderColorInfo> colors, const RenderDepthInfo& depth,
	    const ShaderVertexInputInfo& vs_input_info, CommandBuffer& command,
	    const ShaderPixelInputInfo* ps_input_info, vk::PrimitiveTopology topology,
	    bool primitive_restart_enable, const ShaderProgram& vertex_program,
	    const ShaderProgram& pixel_program, bool& queued);
	std::condition_variable m_ready_cv; // signalled (under m_job_mutex) when a pipeline is ready
	std::unordered_map<GraphicsPipelineKey, std::unique_ptr<GraphicsPipelineEntry>,
	                   GraphicsPipelineKeyHash>
	    m_graphics_pipelines;
	// Worker pool for asynchronous pipeline compilation.
	std::vector<std::thread>          m_workers;
	std::mutex                        m_job_mutex;
	std::condition_variable           m_job_cv;
	std::condition_variable           m_idle_cv;
	std::deque<std::function<void()>> m_jobs;
	uint32_t                          m_jobs_active  = 0;
	bool                              m_stop_workers = false;
	std::atomic<uint32_t>             m_pending_pipelines {0};
	// (vs, ps) pairs with at least one finished pipeline: the driver has compiled both modules,
	// so further state permutations are cheap re-links (~0.2 ms) and are created synchronously —
	// only the first pipeline of a new shader pair goes to the worker pool (170-700 ms).
	std::unordered_set<uint64_t>      m_ready_shader_pairs;
	static uint64_t ShaderPairKey(uint64_t vs_id, uint64_t ps_id) {
		return vs_id * 0x9e3779b97f4a7c15ull ^ (ps_id + 0x7f4a7c159e3779b9ull);
	}
	void StartWorkers();
	void StopWorkers();
	void WorkerLoop();
	void EnqueueJob(std::function<void()> job);
	struct ComputePipelineEntry: Pipeline {
		std::atomic<bool> ready {false};
	};
	std::unordered_map<uint64_t, std::unique_ptr<ComputePipelineEntry>> m_compute_pipelines;
	Common::Mutex m_mutex;
	uint64_t      m_driver_cache_saved_us    = 0;
	uint32_t      m_driver_cache_unsaved     = 0;

	void InitializeDriverCache();
	bool WriteDriverCache();
	void MaybeWriteDriverCache();
};

void LogPipelineTrace(const char* phase, uint64_t vertex_program_id, uint64_t pixel_program_id);
void CreatePipelineInternal(
    GraphicContext& graphics, PipelineCache::Pipeline& pipeline,
    const PipelineRenderingState& rendering, const PipelineVertexInputState& vertex_input,
    const ShaderVertexInputInfo& vs_input_info, const ShaderProgram& vertex_program,
    const ShaderPixelInputInfo* ps_input_info, const ShaderProgram& pixel_program,
    const PipelineStaticParameters& static_params, vk::PipelineCache driver_cache);
void CreatePipelineInternal(GraphicContext& graphics, PipelineCache::Pipeline& pipeline,
                            const ShaderComputeInputInfo& input_info,
                            vk::ShaderModule compute_module, vk::PipelineCache driver_cache);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_PIPELINECACHE_H_
