// F23c (HPP-587, ROADMAP s122 item 493(g)(1)): historical control H - headless Vulkan runner for the reference PS
// 0xe197e307a5f2cb39 as translated by main (KytyPS5 SPIR-V interface: push constant block of 32 u32 "vsharp",
// set 0: binding 51 storage buffer, 54 sampled image, 95 sampler, 101 uniform buffer; input location 0 vec4,
// BaryCoordKHR, HelperInvocation, SubgroupLocalInvocationId; output location 0 vec4).
// One process = one set of inputs (texture, sampler, constants, geometry, target format); every --job creates its
// own shader module and graphics pipeline from a SPIR-V file, draws once into a freshly cleared target and writes
// the raw target bytes to a file. Equal inputs for all jobs of a process by construction.
// Diagnostic tool of track F, not emulator code; not installed anywhere.
//
// hrun.exe --vs vs.spv --tex tex.r8 --texw W --texh H --rtw RW --rth RH --fmt 32|16 --filter nearest|linear
//          --cbw <float> [--dev N] [--validate] --job ps.spv out.bin <flags> [--job ...]
//   flags: 0 - default pipeline, 1 - VK_PIPELINE_CREATE_DISABLE_OPTIMIZATION_BIT
#include <vulkan/vulkan.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <chrono>
#include <string>
#include <vector>

static int g_validation_errors = 0;

#define VK_CHECK(x)                                                                    \
	do {                                                                               \
		VkResult r_ = (x);                                                             \
		if (r_ != VK_SUCCESS) {                                                        \
			std::fprintf(stderr, "FAIL %s -> %d (line %d)\n", #x, (int)r_, __LINE__); \
			std::exit(10);                                                             \
		}                                                                              \
	} while (0)

static std::vector<char> ReadFile(const char* path) {
	FILE* f = std::fopen(path, "rb");
	if (f == nullptr) {
		std::fprintf(stderr, "FAIL cannot open %s\n", path);
		std::exit(11);
	}
	std::fseek(f, 0, SEEK_END);
	long n = std::ftell(f);
	std::fseek(f, 0, SEEK_SET);
	std::vector<char> d(static_cast<size_t>(n));
	if (n > 0 && std::fread(d.data(), 1, d.size(), f) != d.size()) {
		std::fprintf(stderr, "FAIL short read %s\n", path);
		std::exit(11);
	}
	std::fclose(f);
	return d;
}

static VKAPI_ATTR VkBool32 VKAPI_CALL DebugCb(VkDebugUtilsMessageSeverityFlagBitsEXT sev, VkDebugUtilsMessageTypeFlagsEXT,
                                              const VkDebugUtilsMessengerCallbackDataEXT* data, void*) {
	if (sev & VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT) {
		g_validation_errors++;
		std::printf("VALIDATION ERROR: %s\n", data->pMessage);
	} else if (sev & VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT) {
		std::printf("VALIDATION WARNING: %s\n", data->pMessage);
	}
	return VK_FALSE;
}

struct Job {
	std::string ps;
	std::string out;
	int         flags = 0;
};

struct Buffer {
	VkBuffer       buf = VK_NULL_HANDLE;
	VkDeviceMemory mem = VK_NULL_HANDLE;
	VkDeviceSize   size = 0;
};

static VkPhysicalDeviceMemoryProperties g_memprops;

static uint32_t FindMem(uint32_t bits, VkMemoryPropertyFlags want) {
	for (uint32_t i = 0; i < g_memprops.memoryTypeCount; i++) {
		if ((bits & (1u << i)) && (g_memprops.memoryTypes[i].propertyFlags & want) == want) {
			return i;
		}
	}
	std::fprintf(stderr, "FAIL no memory type\n");
	std::exit(12);
}

static Buffer MakeBuffer(VkDevice dev, VkDeviceSize size, VkBufferUsageFlags usage) {
	Buffer             b;
	VkBufferCreateInfo ci {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
	ci.size  = size;
	ci.usage = usage;
	VK_CHECK(vkCreateBuffer(dev, &ci, nullptr, &b.buf));
	VkMemoryRequirements req;
	vkGetBufferMemoryRequirements(dev, b.buf, &req);
	VkMemoryAllocateInfo ai {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
	ai.allocationSize  = req.size;
	ai.memoryTypeIndex = FindMem(req.memoryTypeBits, VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT);
	VK_CHECK(vkAllocateMemory(dev, &ai, nullptr, &b.mem));
	VK_CHECK(vkBindBufferMemory(dev, b.buf, b.mem, 0));
	b.size = size;
	return b;
}

static void ImageBarrier(VkCommandBuffer cb, VkImage img, VkImageLayout from, VkImageLayout to, VkAccessFlags src_a,
                         VkAccessFlags dst_a, VkPipelineStageFlags src_s, VkPipelineStageFlags dst_s) {
	VkImageMemoryBarrier b {VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER};
	b.srcAccessMask       = src_a;
	b.dstAccessMask       = dst_a;
	b.oldLayout           = from;
	b.newLayout           = to;
	b.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	b.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	b.image               = img;
	b.subresourceRange    = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1};
	vkCmdPipelineBarrier(cb, src_s, dst_s, 0, 0, nullptr, 0, nullptr, 1, &b);
}

int main(int argc, char** argv) {
	std::string      vs_path, tex_path, filter = "nearest";
	uint32_t         texw = 0, texh = 0, rtw = 0, rth = 0;
	int              fmt_bits = 32, dev_index = -1;
	bool             validate = false;
	float            cbw      = 0.0f;
	std::vector<Job> jobs;
	for (int i = 1; i < argc; i++) {
		std::string a = argv[i];
		auto        next = [&]() -> const char* {
            if (i + 1 >= argc) {
                std::fprintf(stderr, "FAIL missing value for %s\n", a.c_str());
                std::exit(2);
            }
            return argv[++i];
		};
		if (a == "--vs") vs_path = next();
		else if (a == "--tex") tex_path = next();
		else if (a == "--texw") texw = static_cast<uint32_t>(std::atoi(next()));
		else if (a == "--texh") texh = static_cast<uint32_t>(std::atoi(next()));
		else if (a == "--rtw") rtw = static_cast<uint32_t>(std::atoi(next()));
		else if (a == "--rth") rth = static_cast<uint32_t>(std::atoi(next()));
		else if (a == "--fmt") fmt_bits = std::atoi(next());
		else if (a == "--filter") filter = next();
		else if (a == "--cbw") cbw = static_cast<float>(std::atof(next()));
		else if (a == "--dev") dev_index = std::atoi(next());
		else if (a == "--validate") validate = true;
		else if (a == "--job") {
			Job j;
			j.ps    = next();
			j.out   = next();
			j.flags = std::atoi(next());
			jobs.push_back(j);
		} else {
			std::fprintf(stderr, "FAIL unknown argument %s\n", a.c_str());
			return 2;
		}
	}
	if (vs_path.empty() || tex_path.empty() || texw == 0 || texh == 0 || rtw == 0 || rth == 0 || jobs.empty() ||
	    (fmt_bits != 32 && fmt_bits != 16) || (filter != "nearest" && filter != "linear")) {
		std::fprintf(stderr, "FAIL bad arguments\n");
		return 2;
	}
	const VkFormat rt_format = fmt_bits == 32 ? VK_FORMAT_R32G32B32A32_SFLOAT : VK_FORMAT_R16G16B16A16_SFLOAT;
	const uint32_t rt_bpp    = fmt_bits == 32 ? 16u : 8u;
	std::vector<char> tex = ReadFile(tex_path.c_str());
	if (tex.size() != static_cast<size_t>(texw) * texh) {
		std::fprintf(stderr, "FAIL texture size %zu != %u x %u\n", tex.size(), texw, texh);
		return 2;
	}

	// Instance
	VkApplicationInfo app {VK_STRUCTURE_TYPE_APPLICATION_INFO};
	app.pApplicationName = "f23c_hrun";
	app.apiVersion       = VK_API_VERSION_1_3;
	std::vector<const char*> layers, iext;
	if (validate) {
		layers.push_back("VK_LAYER_KHRONOS_validation");
		iext.push_back(VK_EXT_DEBUG_UTILS_EXTENSION_NAME);
	}
	VkInstanceCreateInfo ici {VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
	ici.pApplicationInfo        = &app;
	ici.enabledLayerCount       = static_cast<uint32_t>(layers.size());
	ici.ppEnabledLayerNames     = layers.data();
	ici.enabledExtensionCount   = static_cast<uint32_t>(iext.size());
	ici.ppEnabledExtensionNames = iext.data();
	VkInstance inst;
	VK_CHECK(vkCreateInstance(&ici, nullptr, &inst));
	VkDebugUtilsMessengerEXT messenger = VK_NULL_HANDLE;
	if (validate) {
		auto fn = reinterpret_cast<PFN_vkCreateDebugUtilsMessengerEXT>(vkGetInstanceProcAddr(inst, "vkCreateDebugUtilsMessengerEXT"));
		VkDebugUtilsMessengerCreateInfoEXT mci {VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT};
		mci.messageSeverity = VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT;
		mci.messageType     = VK_DEBUG_UTILS_MESSAGE_TYPE_GENERAL_BIT_EXT | VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT |
		                  VK_DEBUG_UTILS_MESSAGE_TYPE_PERFORMANCE_BIT_EXT;
		mci.pfnUserCallback = DebugCb;
		VK_CHECK(fn(inst, &mci, nullptr, &messenger));
	}

	// Physical device
	uint32_t ndev = 0;
	VK_CHECK(vkEnumeratePhysicalDevices(inst, &ndev, nullptr));
	std::vector<VkPhysicalDevice> devs(ndev);
	VK_CHECK(vkEnumeratePhysicalDevices(inst, &ndev, devs.data()));
	int pick = dev_index;
	for (uint32_t i = 0; i < ndev; i++) {
		VkPhysicalDeviceDriverProperties drv {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DRIVER_PROPERTIES};
		VkPhysicalDeviceProperties2      p2 {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2};
		p2.pNext = &drv;
		vkGetPhysicalDeviceProperties2(devs[i], &p2);
		const auto& p = p2.properties;
		std::printf("device %u: %s type %d vendor 0x%04x device 0x%04x api %u.%u.%u driverVersion 0x%08x driverName '%s' driverInfo '%s'\n", i,
		            p.deviceName, (int)p.deviceType, p.vendorID, p.deviceID, VK_API_VERSION_MAJOR(p.apiVersion), VK_API_VERSION_MINOR(p.apiVersion),
		            VK_API_VERSION_PATCH(p.apiVersion), p.driverVersion, drv.driverName, drv.driverInfo);
		if (pick < 0 && p.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU) pick = static_cast<int>(i);
	}
	if (pick < 0 || pick >= static_cast<int>(ndev)) {
		std::fprintf(stderr, "FAIL no device picked\n");
		return 3;
	}
	VkPhysicalDevice phys = devs[static_cast<size_t>(pick)];
	vkGetPhysicalDeviceMemoryProperties(phys, &g_memprops);
	{
		VkPhysicalDeviceVulkan12Properties p12 {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_PROPERTIES};
		VkPhysicalDeviceVulkan11Properties p11 {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_PROPERTIES};
		p11.pNext = &p12;
		VkPhysicalDeviceProperties2 p2 {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2};
		p2.pNext = &p11;
		vkGetPhysicalDeviceProperties2(phys, &p2);
		std::printf("picked device %d: subgroupSize %u fragment-subgroup %d ballot %d signedZeroInfNanPreserveF32 %d\n", pick, p11.subgroupSize,
		            (p11.subgroupSupportedStages & VK_SHADER_STAGE_FRAGMENT_BIT) ? 1 : 0,
		            (p11.subgroupSupportedOperations & VK_SUBGROUP_FEATURE_BALLOT_BIT) ? 1 : 0, p12.shaderSignedZeroInfNanPreserveFloat32 ? 1 : 0);
	}

	// Device
	uint32_t nq = 0;
	vkGetPhysicalDeviceQueueFamilyProperties(phys, &nq, nullptr);
	std::vector<VkQueueFamilyProperties> qf(nq);
	vkGetPhysicalDeviceQueueFamilyProperties(phys, &nq, qf.data());
	uint32_t qfam = UINT32_MAX;
	for (uint32_t i = 0; i < nq; i++) {
		if (qf[i].queueFlags & VK_QUEUE_GRAPHICS_BIT) {
			qfam = i;
			break;
		}
	}
	float                   prio = 1.0f;
	VkDeviceQueueCreateInfo qci {VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
	qci.queueFamilyIndex = qfam;
	qci.queueCount       = 1;
	qci.pQueuePriorities = &prio;
	VkPhysicalDeviceFragmentShaderBarycentricFeaturesKHR bary {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FRAGMENT_SHADER_BARYCENTRIC_FEATURES_KHR};
	bary.fragmentShaderBarycentric = VK_TRUE;
	VkPhysicalDeviceVulkan13Features f13 {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES};
	f13.pNext            = &bary;
	f13.dynamicRendering = VK_TRUE;
	VkPhysicalDeviceVulkan12Features f12 {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES};
	f12.pNext                       = &f13;
	f12.uniformBufferStandardLayout = VK_TRUE;
	VkPhysicalDeviceFeatures2 f2 {VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2};
	f2.pNext                              = &f12;
	const char*        dext[]             = {VK_KHR_FRAGMENT_SHADER_BARYCENTRIC_EXTENSION_NAME};
	VkDeviceCreateInfo dci {VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
	dci.pNext                   = &f2;
	dci.queueCreateInfoCount    = 1;
	dci.pQueueCreateInfos       = &qci;
	dci.enabledExtensionCount   = 1;
	dci.ppEnabledExtensionNames = dext;
	VkDevice dev;
	VK_CHECK(vkCreateDevice(phys, &dci, nullptr, &dev));
	VkQueue queue;
	vkGetDeviceQueue(dev, qfam, 0, &queue);

	VkCommandPoolCreateInfo cpci {VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
	cpci.flags            = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
	cpci.queueFamilyIndex = qfam;
	VkCommandPool pool;
	VK_CHECK(vkCreateCommandPool(dev, &cpci, nullptr, &pool));
	VkCommandBufferAllocateInfo cbai {VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
	cbai.commandPool        = pool;
	cbai.level              = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
	cbai.commandBufferCount = 1;
	VkCommandBuffer cb;
	VK_CHECK(vkAllocateCommandBuffers(dev, &cbai, &cb));
	auto submit_wait = [&]() {
		VkSubmitInfo si {VK_STRUCTURE_TYPE_SUBMIT_INFO};
		si.commandBufferCount = 1;
		si.pCommandBuffers    = &cb;
		VK_CHECK(vkQueueSubmit(queue, 1, &si, VK_NULL_HANDLE));
		VK_CHECK(vkQueueWaitIdle(queue));
	};
	VkCommandBufferBeginInfo cbbi {VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
	cbbi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;

	// Texture (R8_UNORM, NV12 bytes as one image of W x 1.5H rows, as the reference PS samples it)
	VkImageCreateInfo tci {VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO};
	tci.imageType     = VK_IMAGE_TYPE_2D;
	tci.format        = VK_FORMAT_R8_UNORM;
	tci.extent        = {texw, texh, 1};
	tci.mipLevels     = 1;
	tci.arrayLayers   = 1;
	tci.samples       = VK_SAMPLE_COUNT_1_BIT;
	tci.tiling        = VK_IMAGE_TILING_OPTIMAL;
	tci.usage         = VK_IMAGE_USAGE_SAMPLED_BIT | VK_IMAGE_USAGE_TRANSFER_DST_BIT;
	tci.initialLayout = VK_IMAGE_LAYOUT_UNDEFINED;
	VkImage texImg;
	VK_CHECK(vkCreateImage(dev, &tci, nullptr, &texImg));
	VkMemoryRequirements treq;
	vkGetImageMemoryRequirements(dev, texImg, &treq);
	VkMemoryAllocateInfo tai {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
	tai.allocationSize  = treq.size;
	tai.memoryTypeIndex = FindMem(treq.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
	VkDeviceMemory texMem;
	VK_CHECK(vkAllocateMemory(dev, &tai, nullptr, &texMem));
	VK_CHECK(vkBindImageMemory(dev, texImg, texMem, 0));
	{
		Buffer st = MakeBuffer(dev, tex.size(), VK_BUFFER_USAGE_TRANSFER_SRC_BIT);
		void*  p  = nullptr;
		VK_CHECK(vkMapMemory(dev, st.mem, 0, st.size, 0, &p));
		std::memcpy(p, tex.data(), tex.size());
		vkUnmapMemory(dev, st.mem);
		VK_CHECK(vkBeginCommandBuffer(cb, &cbbi));
		ImageBarrier(cb, texImg, VK_IMAGE_LAYOUT_UNDEFINED, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 0, VK_ACCESS_TRANSFER_WRITE_BIT,
		             VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT);
		VkBufferImageCopy r {};
		r.imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1};
		r.imageExtent      = {texw, texh, 1};
		vkCmdCopyBufferToImage(cb, st.buf, texImg, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, 1, &r);
		ImageBarrier(cb, texImg, VK_IMAGE_LAYOUT_TRANSFER_DST_OPTIMAL, VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL, VK_ACCESS_TRANSFER_WRITE_BIT,
		             VK_ACCESS_SHADER_READ_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_FRAGMENT_SHADER_BIT);
		VK_CHECK(vkEndCommandBuffer(cb));
		submit_wait();
		vkDestroyBuffer(dev, st.buf, nullptr);
		vkFreeMemory(dev, st.mem, nullptr);
	}
	VkImageViewCreateInfo tvci {VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO};
	tvci.image            = texImg;
	tvci.viewType         = VK_IMAGE_VIEW_TYPE_2D;
	tvci.format           = VK_FORMAT_R8_UNORM;
	tvci.subresourceRange = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1};
	VkImageView texView;
	VK_CHECK(vkCreateImageView(dev, &tvci, nullptr, &texView));
	VkSamplerCreateInfo sci {VK_STRUCTURE_TYPE_SAMPLER_CREATE_INFO};
	sci.magFilter    = filter == "linear" ? VK_FILTER_LINEAR : VK_FILTER_NEAREST;
	sci.minFilter    = sci.magFilter;
	sci.mipmapMode   = VK_SAMPLER_MIPMAP_MODE_NEAREST;
	sci.addressModeU = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
	sci.addressModeV = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
	sci.addressModeW = VK_SAMPLER_ADDRESS_MODE_CLAMP_TO_EDGE;
	sci.maxLod       = 0.0f;
	VkSampler sampler;
	VK_CHECK(vkCreateSampler(dev, &sci, nullptr, &sampler));

	// Constant buffer (binding 101, 64 KiB): vsharp[16] & 255 = 0 is the byte offset of the texture width (float)
	Buffer ubo = MakeBuffer(dev, 65536, VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT);
	{
		void* p = nullptr;
		VK_CHECK(vkMapMemory(dev, ubo.mem, 0, ubo.size, 0, &p));
		std::memset(p, 0, 65536);
		std::memcpy(p, &cbw, 4);
		vkUnmapMemory(dev, ubo.mem);
	}
	Buffer ssbo = MakeBuffer(dev, 256, VK_BUFFER_USAGE_STORAGE_BUFFER_BIT);
	{
		void* p = nullptr;
		VK_CHECK(vkMapMemory(dev, ssbo.mem, 0, ssbo.size, 0, &p));
		std::memset(p, 0, 256);
		vkUnmapMemory(dev, ssbo.mem);
	}
	uint32_t push[32] = {};

	// Target
	VkImageCreateInfo rci = tci;
	rci.format            = rt_format;
	rci.extent            = {rtw, rth, 1};
	rci.usage             = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_TRANSFER_SRC_BIT;
	VkImage rtImg;
	VK_CHECK(vkCreateImage(dev, &rci, nullptr, &rtImg));
	VkMemoryRequirements rreq;
	vkGetImageMemoryRequirements(dev, rtImg, &rreq);
	VkMemoryAllocateInfo rai {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
	rai.allocationSize  = rreq.size;
	rai.memoryTypeIndex = FindMem(rreq.memoryTypeBits, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT);
	VkDeviceMemory rtMem;
	VK_CHECK(vkAllocateMemory(dev, &rai, nullptr, &rtMem));
	VK_CHECK(vkBindImageMemory(dev, rtImg, rtMem, 0));
	VkImageViewCreateInfo rvci = tvci;
	rvci.image                 = rtImg;
	rvci.format                = rt_format;
	VkImageView rtView;
	VK_CHECK(vkCreateImageView(dev, &rvci, nullptr, &rtView));
	Buffer readback = MakeBuffer(dev, static_cast<VkDeviceSize>(rtw) * rth * rt_bpp, VK_BUFFER_USAGE_TRANSFER_DST_BIT);

	// Descriptors (set 0 of the KytyPS5 PS interface)
	VkDescriptorSetLayoutBinding binds[4] = {
	    {51, VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1, VK_SHADER_STAGE_FRAGMENT_BIT, nullptr},
	    {54, VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, 1, VK_SHADER_STAGE_FRAGMENT_BIT, nullptr},
	    {95, VK_DESCRIPTOR_TYPE_SAMPLER, 1, VK_SHADER_STAGE_FRAGMENT_BIT, nullptr},
	    {101, VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1, VK_SHADER_STAGE_FRAGMENT_BIT, nullptr},
	};
	VkDescriptorSetLayoutCreateInfo dslci {VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
	dslci.bindingCount = 4;
	dslci.pBindings    = binds;
	VkDescriptorSetLayout dsl;
	VK_CHECK(vkCreateDescriptorSetLayout(dev, &dslci, nullptr, &dsl));
	VkPushConstantRange        pcr {VK_SHADER_STAGE_FRAGMENT_BIT, 0, 128};
	VkPipelineLayoutCreateInfo plci {VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
	plci.setLayoutCount         = 1;
	plci.pSetLayouts            = &dsl;
	plci.pushConstantRangeCount = 1;
	plci.pPushConstantRanges    = &pcr;
	VkPipelineLayout layout;
	VK_CHECK(vkCreatePipelineLayout(dev, &plci, nullptr, &layout));
	VkDescriptorPoolSize       psz[4] = {{VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, 1},
                                   {VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE, 1},
                                   {VK_DESCRIPTOR_TYPE_SAMPLER, 1},
                                   {VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1}};
	VkDescriptorPoolCreateInfo dpci {VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
	dpci.maxSets       = 1;
	dpci.poolSizeCount = 4;
	dpci.pPoolSizes    = psz;
	VkDescriptorPool dpool;
	VK_CHECK(vkCreateDescriptorPool(dev, &dpci, nullptr, &dpool));
	VkDescriptorSetAllocateInfo dsai {VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO};
	dsai.descriptorPool     = dpool;
	dsai.descriptorSetCount = 1;
	dsai.pSetLayouts        = &dsl;
	VkDescriptorSet ds;
	VK_CHECK(vkAllocateDescriptorSets(dev, &dsai, &ds));
	VkDescriptorBufferInfo sbi {ssbo.buf, 0, VK_WHOLE_SIZE};
	VkDescriptorBufferInfo ubi {ubo.buf, 0, VK_WHOLE_SIZE};
	VkDescriptorImageInfo  ii {VK_NULL_HANDLE, texView, VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL};
	VkDescriptorImageInfo  si {sampler, VK_NULL_HANDLE, VK_IMAGE_LAYOUT_UNDEFINED};
	VkWriteDescriptorSet   w[4] = {};
	for (int k = 0; k < 4; k++) {
		w[k].sType           = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET;
		w[k].dstSet          = ds;
		w[k].dstBinding      = binds[k].binding;
		w[k].descriptorCount = 1;
		w[k].descriptorType  = binds[k].descriptorType;
	}
	w[0].pBufferInfo = &sbi;
	w[1].pImageInfo  = &ii;
	w[2].pImageInfo  = &si;
	w[3].pBufferInfo = &ubi;
	vkUpdateDescriptorSets(dev, 4, w, 0, nullptr);

	std::vector<char>        vs_code = ReadFile(vs_path.c_str());
	VkShaderModuleCreateInfo smci {VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
	smci.codeSize = vs_code.size();
	smci.pCode    = reinterpret_cast<const uint32_t*>(vs_code.data());
	VkShaderModule vsm;
	VK_CHECK(vkCreateShaderModule(dev, &smci, nullptr, &vsm));
	// Vertex count by the VS file name: the full-screen triangle VS draws 3 vertices, the diamond VS 6.
	const uint32_t vcount = vs_path.find("diamond") != std::string::npos ? 6u : 3u;

	for (size_t j = 0; j < jobs.size(); j++) {
		std::vector<char>        ps_code = ReadFile(jobs[j].ps.c_str());
		VkShaderModuleCreateInfo pmci {VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
		pmci.codeSize = ps_code.size();
		pmci.pCode    = reinterpret_cast<const uint32_t*>(ps_code.data());
		VkShaderModule psm;
		VK_CHECK(vkCreateShaderModule(dev, &pmci, nullptr, &psm));
		VkPipelineShaderStageCreateInfo st[2] = {};
		st[0].sType  = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
		st[0].stage  = VK_SHADER_STAGE_VERTEX_BIT;
		st[0].module = vsm;
		st[0].pName  = "main";
		st[1].sType  = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO;
		st[1].stage  = VK_SHADER_STAGE_FRAGMENT_BIT;
		st[1].module = psm;
		st[1].pName  = "main";
		VkPipelineVertexInputStateCreateInfo   vi {VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};
		VkPipelineInputAssemblyStateCreateInfo ia {VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO};
		ia.topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST;
		VkViewport                        vp {0.0f, 0.0f, static_cast<float>(rtw), static_cast<float>(rth), 0.0f, 1.0f};
		VkRect2D                          sc {{0, 0}, {rtw, rth}};
		VkPipelineViewportStateCreateInfo vps {VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO};
		vps.viewportCount = 1;
		vps.pViewports    = &vp;
		vps.scissorCount  = 1;
		vps.pScissors     = &sc;
		VkPipelineRasterizationStateCreateInfo rs {VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO};
		rs.polygonMode = VK_POLYGON_MODE_FILL;
		rs.cullMode    = VK_CULL_MODE_NONE;
		rs.frontFace   = VK_FRONT_FACE_COUNTER_CLOCKWISE;
		rs.lineWidth   = 1.0f;
		VkPipelineMultisampleStateCreateInfo ms {VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO};
		ms.rasterizationSamples = VK_SAMPLE_COUNT_1_BIT;
		VkPipelineColorBlendAttachmentState cba {};
		cba.colorWriteMask = 0xf;
		VkPipelineColorBlendStateCreateInfo cbs {VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO};
		cbs.attachmentCount = 1;
		cbs.pAttachments    = &cba;
		VkPipelineRenderingCreateInfo prci {VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO};
		prci.colorAttachmentCount    = 1;
		prci.pColorAttachmentFormats = &rt_format;
		VkGraphicsPipelineCreateInfo gpci {VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};
		gpci.pNext               = &prci;
		gpci.flags               = jobs[j].flags == 1 ? VK_PIPELINE_CREATE_DISABLE_OPTIMIZATION_BIT : 0;
		gpci.stageCount          = 2;
		gpci.pStages             = st;
		gpci.pVertexInputState   = &vi;
		gpci.pInputAssemblyState = &ia;
		gpci.pViewportState      = &vps;
		gpci.pRasterizationState = &rs;
		gpci.pMultisampleState   = &ms;
		gpci.pColorBlendState    = &cbs;
		gpci.layout              = layout;
		VkPipeline pipe;
		auto       t0 = std::chrono::steady_clock::now();
		VK_CHECK(vkCreateGraphicsPipelines(dev, VK_NULL_HANDLE, 1, &gpci, nullptr, &pipe));
		auto t1 = std::chrono::steady_clock::now();

		VK_CHECK(vkBeginCommandBuffer(cb, &cbbi));
		ImageBarrier(cb, rtImg, VK_IMAGE_LAYOUT_UNDEFINED, VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL, 0, VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
		             VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT);
		VkRenderingAttachmentInfo att {VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO};
		att.imageView   = rtView;
		att.imageLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL;
		att.loadOp      = VK_ATTACHMENT_LOAD_OP_CLEAR;
		att.storeOp     = VK_ATTACHMENT_STORE_OP_STORE;
		att.clearValue.color.float32[0] = -7.0f;
		att.clearValue.color.float32[1] = -7.0f;
		att.clearValue.color.float32[2] = -7.0f;
		att.clearValue.color.float32[3] = -7.0f;
		VkRenderingInfo ri {VK_STRUCTURE_TYPE_RENDERING_INFO};
		ri.renderArea           = sc;
		ri.layerCount           = 1;
		ri.colorAttachmentCount = 1;
		ri.pColorAttachments    = &att;
		vkCmdBeginRendering(cb, &ri);
		vkCmdBindPipeline(cb, VK_PIPELINE_BIND_POINT_GRAPHICS, pipe);
		vkCmdBindDescriptorSets(cb, VK_PIPELINE_BIND_POINT_GRAPHICS, layout, 0, 1, &ds, 0, nullptr);
		vkCmdPushConstants(cb, layout, VK_SHADER_STAGE_FRAGMENT_BIT, 0, 128, push);
		vkCmdDraw(cb, vcount, 1, 0, 0);
		vkCmdEndRendering(cb);
		ImageBarrier(cb, rtImg, VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
		             VK_ACCESS_TRANSFER_READ_BIT, VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT);
		VkBufferImageCopy r {};
		r.imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1};
		r.imageExtent      = {rtw, rth, 1};
		vkCmdCopyImageToBuffer(cb, rtImg, VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL, readback.buf, 1, &r);
		VkMemoryBarrier hb {VK_STRUCTURE_TYPE_MEMORY_BARRIER};
		hb.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT;
		hb.dstAccessMask = VK_ACCESS_HOST_READ_BIT;
		vkCmdPipelineBarrier(cb, VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_HOST_BIT, 0, 1, &hb, 0, nullptr, 0, nullptr);
		VK_CHECK(vkEndCommandBuffer(cb));
		submit_wait();
		void* p = nullptr;
		VK_CHECK(vkMapMemory(dev, readback.mem, 0, readback.size, 0, &p));
		FILE* f = std::fopen(jobs[j].out.c_str(), "wb");
		if (f == nullptr || std::fwrite(p, 1, static_cast<size_t>(readback.size), f) != readback.size) {
			std::fprintf(stderr, "FAIL write %s\n", jobs[j].out.c_str());
			return 13;
		}
		std::fclose(f);
		vkUnmapMemory(dev, readback.mem);
		std::printf("job %zu: ps %s flags %d pipeline %.1f ms -> %s (%llu bytes)\n", j, jobs[j].ps.c_str(), jobs[j].flags,
		            std::chrono::duration<double, std::milli>(t1 - t0).count(), jobs[j].out.c_str(), (unsigned long long)readback.size);
		vkDestroyPipeline(dev, pipe, nullptr);
		vkDestroyShaderModule(dev, psm, nullptr);
	}
	vkDeviceWaitIdle(dev);
	vkDestroyShaderModule(dev, vsm, nullptr);
	vkDestroyDescriptorPool(dev, dpool, nullptr);
	vkDestroyPipelineLayout(dev, layout, nullptr);
	vkDestroyDescriptorSetLayout(dev, dsl, nullptr);
	vkDestroyImageView(dev, rtView, nullptr);
	vkDestroyImage(dev, rtImg, nullptr);
	vkFreeMemory(dev, rtMem, nullptr);
	vkDestroyImageView(dev, texView, nullptr);
	vkDestroyImage(dev, texImg, nullptr);
	vkFreeMemory(dev, texMem, nullptr);
	vkDestroySampler(dev, sampler, nullptr);
	for (Buffer* b : {&ubo, &ssbo, &readback}) {
		vkDestroyBuffer(dev, b->buf, nullptr);
		vkFreeMemory(dev, b->mem, nullptr);
	}
	vkDestroyCommandPool(dev, pool, nullptr);
	vkDestroyDevice(dev, nullptr);
	if (messenger != VK_NULL_HANDLE) {
		auto fn = reinterpret_cast<PFN_vkDestroyDebugUtilsMessengerEXT>(vkGetInstanceProcAddr(inst, "vkDestroyDebugUtilsMessengerEXT"));
		fn(inst, messenger, nullptr);
	}
	vkDestroyInstance(inst, nullptr);
	std::printf("validation errors %d\n", g_validation_errors);
	std::printf("DONE\n");
	return g_validation_errors == 0 ? 0 : 20;
}
