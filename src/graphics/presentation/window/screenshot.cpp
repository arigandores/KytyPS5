#include "graphics/presentation/window/screenshot.h"

#include "common/logging/log.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/renderer/render.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

namespace Libs::Graphics {

namespace {

constexpr const char* REQUEST_FILE = "_screenshot.req";

double NowSeconds() {
	return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch())
	    .count();
}

// --- minimal PNG writer (stored deflate blocks, no compression) ---------------------------------

uint32_t Crc32(const uint8_t* data, size_t size, uint32_t crc = 0) {
	static const auto table = [] {
		std::array<uint32_t, 256> t {};
		for (uint32_t n = 0; n < 256; n++) {
			uint32_t c = n;
			for (int k = 0; k < 8; k++) {
				c = (c & 1u) != 0 ? 0xedb88320u ^ (c >> 1u) : c >> 1u;
			}
			t[n] = c;
		}
		return t;
	}();
	crc ^= 0xffffffffu;
	for (size_t i = 0; i < size; i++) {
		crc = table[(crc ^ data[i]) & 0xffu] ^ (crc >> 8u);
	}
	return crc ^ 0xffffffffu;
}

void PutU32(std::vector<uint8_t>& out, uint32_t v) {
	out.push_back(static_cast<uint8_t>(v >> 24u));
	out.push_back(static_cast<uint8_t>(v >> 16u));
	out.push_back(static_cast<uint8_t>(v >> 8u));
	out.push_back(static_cast<uint8_t>(v));
}

void Chunk(std::vector<uint8_t>& out, const char* type, const std::vector<uint8_t>& data) {
	PutU32(out, static_cast<uint32_t>(data.size()));
	std::vector<uint8_t> body(type, type + 4);
	body.insert(body.end(), data.begin(), data.end());
	out.insert(out.end(), body.begin(), body.end());
	PutU32(out, Crc32(body.data(), body.size()));
}

bool WritePng(const std::string& path, const std::vector<uint8_t>& rgb, uint32_t width,
              uint32_t height) {
	// Raw scanlines with filter byte 0.
	std::vector<uint8_t> raw;
	raw.reserve((static_cast<size_t>(width) * 3 + 1) * height);
	for (uint32_t y = 0; y < height; y++) {
		raw.push_back(0);
		const auto* row = rgb.data() + static_cast<size_t>(y) * width * 3;
		raw.insert(raw.end(), row, row + static_cast<size_t>(width) * 3);
	}
	// zlib stream: header, stored blocks of at most 65535 bytes, adler32.
	std::vector<uint8_t> z;
	z.reserve(raw.size() + raw.size() / 65535 * 5 + 16);
	z.push_back(0x78);
	z.push_back(0x01);
	size_t   pos = 0;
	uint32_t a = 1, b = 0;
	for (const auto byte: raw) {
		a = (a + byte) % 65521u;
		b = (b + a) % 65521u;
	}
	while (pos < raw.size()) {
		const auto n     = static_cast<uint16_t>(std::min<size_t>(65535, raw.size() - pos));
		const bool final = pos + n == raw.size();
		z.push_back(final ? 1 : 0);
		z.push_back(static_cast<uint8_t>(n & 0xffu));
		z.push_back(static_cast<uint8_t>(n >> 8u));
		z.push_back(static_cast<uint8_t>(~n & 0xffu));
		z.push_back(static_cast<uint8_t>((~n >> 8u) & 0xffu));
		z.insert(z.end(), raw.begin() + static_cast<std::ptrdiff_t>(pos),
		         raw.begin() + static_cast<std::ptrdiff_t>(pos + n));
		pos += n;
	}
	PutU32(z, (b << 16u) | a);

	std::vector<uint8_t> png {0x89, 'P', 'N', 'G', 0x0d, 0x0a, 0x1a, 0x0a};
	std::vector<uint8_t> ihdr;
	PutU32(ihdr, width);
	PutU32(ihdr, height);
	ihdr.push_back(8); // bit depth
	ihdr.push_back(2); // RGB
	ihdr.push_back(0);
	ihdr.push_back(0);
	ihdr.push_back(0);
	Chunk(png, "IHDR", ihdr);
	Chunk(png, "IDAT", z);
	Chunk(png, "IEND", {});

	std::ofstream file(std::filesystem::path(path), std::ios::binary);
	if (!file) {
		return false;
	}
	file.write(reinterpret_cast<const char*>(png.data()), static_cast<std::streamsize>(png.size()));
	return static_cast<bool>(file);
}

// Converts one texel of the presentation format to 8-bit RGB. Returns false for unknown formats.
bool TexelToRgb(vk::Format format, const uint8_t* texel, uint8_t* rgb) {
	switch (format) {
		case vk::Format::eR8G8B8A8Unorm:
		case vk::Format::eR8G8B8A8Srgb:
			rgb[0] = texel[0];
			rgb[1] = texel[1];
			rgb[2] = texel[2];
			return true;
		case vk::Format::eB8G8R8A8Unorm:
		case vk::Format::eB8G8R8A8Srgb:
			rgb[0] = texel[2];
			rgb[1] = texel[1];
			rgb[2] = texel[0];
			return true;
		case vk::Format::eA2B10G10R10UnormPack32:
		case vk::Format::eA2R10G10B10UnormPack32: {
			uint32_t v = 0;
			std::memcpy(&v, texel, 4);
			const auto c0 = static_cast<uint8_t>((v & 0x3ffu) >> 2u);
			const auto c1 = static_cast<uint8_t>(((v >> 10u) & 0x3ffu) >> 2u);
			const auto c2 = static_cast<uint8_t>(((v >> 20u) & 0x3ffu) >> 2u);
			if (format == vk::Format::eA2B10G10R10UnormPack32) {
				rgb[0] = c0;
				rgb[1] = c1;
				rgb[2] = c2;
			} else {
				rgb[0] = c2;
				rgb[1] = c1;
				rgb[2] = c0;
			}
			return true;
		}
		case vk::Format::eR16G16B16A16Sfloat: {
			for (int i = 0; i < 3; i++) {
				uint16_t h = 0;
				std::memcpy(&h, texel + i * 2, 2);
				const uint32_t sign = (h >> 15u) & 1u;
				const uint32_t exp  = (h >> 10u) & 0x1fu;
				const uint32_t man  = h & 0x3ffu;
				float          f    = 0.0f;
				if (exp == 0) {
					f = static_cast<float>(man) / 1024.0f / 16384.0f;
				} else if (exp == 31) {
					f = 1.0f;
				} else {
					f = (1.0f + static_cast<float>(man) / 1024.0f) *
					    static_cast<float>(1u << exp) / 32768.0f;
				}
				if (sign != 0) {
					f = 0.0f;
				}
				rgb[i] = static_cast<uint8_t>(std::clamp(f, 0.0f, 1.0f) * 255.0f + 0.5f);
			}
			return true;
		}
		default: return false;
	}
}

uint32_t BytesPerTexel(vk::Format format) {
	return format == vk::Format::eR16G16B16A16Sfloat ? 8u : 4u;
}

} // namespace

ScreenshotGrabber::ScreenshotGrabber(GraphicContext& graphics, CommandScheduler& scheduler)
    : m_graphics(graphics), m_scheduler(scheduler) {
	if (const char* value = std::getenv("KYTY_SHOT_TIMES"); value != nullptr) {
		std::string text(value);
		size_t      pos = 0;
		while (pos < text.size()) {
			const auto comma = text.find(',', pos);
			const auto item  = text.substr(pos, comma == std::string::npos ? std::string::npos : comma - pos);
			if (!item.empty()) {
				m_times.push_back(std::strtod(item.c_str(), nullptr));
			}
			if (comma == std::string::npos) {
				break;
			}
			pos = comma + 1;
		}
		std::sort(m_times.begin(), m_times.end());
	}
	if (const char* value = std::getenv("KYTY_REC"); value != nullptr && value[0] != 0) {
		m_rec_path = value;
	}
}

ScreenshotGrabber::~ScreenshotGrabber() {
	for (auto& slot: m_rec_slots) {
		if (slot.pending) {
			FlushVideoSlot(slot);
		}
	}
	if (m_rec_pipe != nullptr) {
		_pclose(m_rec_pipe);
		m_rec_pipe = nullptr;
	}
	if (m_rec_index != nullptr) {
		std::fclose(m_rec_index);
		m_rec_index = nullptr;
	}
}

bool ScreenshotGrabber::Poll() {
	const bool shot = PollScreenshot();
	return shot || m_rec_frame;
}

bool ScreenshotGrabber::PollScreenshot() {
	m_presents++;
	const auto now = NowSeconds();
	if (m_first_present_s < 0.0) {
		m_first_present_s = now;
	}
	m_output.clear();
	m_rec_frame = !m_rec_path.empty();
	if (m_next_time < m_times.size() && now - m_first_present_s >= m_times[m_next_time]) {
		m_next_time++;
		m_output = "_shot_" + std::to_string(m_presents) + ".png";
		return true;
	}
	// The request file is checked every 8 presents (~130 ms).
	if ((m_presents & 7u) != 0) {
		return false;
	}
	std::error_code ec;
	if (!std::filesystem::exists(REQUEST_FILE, ec)) {
		return false;
	}
	{
		std::ifstream file(REQUEST_FILE);
		std::string   line;
		if (file && std::getline(file, line)) {
			while (!line.empty() && (line.back() == '\r' || line.back() == ' ')) {
				line.pop_back();
			}
			m_output = line;
		}
	}
	std::filesystem::remove(REQUEST_FILE, ec);
	if (m_output.empty()) {
		m_output = "_shot_" + std::to_string(m_presents) + ".png";
	}
	return true;
}


void ScreenshotGrabber::Record(CommandBuffer& command, const VulkanImage& source) {
	if (m_rec_frame) {
		RecordVideoFrame(command, source);
	}
	if (m_output.empty()) {
		return;
	}
	m_pending = false;
	m_format  = source.format;
	m_width   = source.extent.width;
	m_height  = source.extent.height;
	uint8_t probe[8] {};
	uint8_t rgb[3] {};
	if (!TexelToRgb(m_format, probe, rgb)) {
		LOGF("Screenshot: unsupported presentation format %d\n", static_cast<int>(m_format));
		return;
	}
	const uint64_t size = static_cast<uint64_t>(m_width) * m_height * BytesPerTexel(m_format);
	m_buffer.reset();
	m_buffer = std::make_unique<Buffer>(m_graphics, m_scheduler, MemoryUsage::Download, 0,
	                                    vk::BufferUsageFlagBits::eTransferDst, size);

	vk::BufferImageCopy region {};
	region.bufferOffset                    = 0;
	region.bufferRowLength                 = 0;
	region.bufferImageHeight               = 0;
	region.imageSubresource.aspectMask     = vk::ImageAspectFlagBits::eColor;
	region.imageSubresource.mipLevel       = 0;
	region.imageSubresource.baseArrayLayer = 0;
	region.imageSubresource.layerCount     = 1;
	region.imageExtent                     = {m_width, m_height, 1};
	auto vk_command                        = command.Handle();
	vk_command.copyImageToBuffer(source.image, vk::ImageLayout::eTransferSrcOptimal,
	                             m_buffer->Handle(), 1, &region);
	vk::BufferMemoryBarrier to_host {};
	to_host.sType               = vk::StructureType::eBufferMemoryBarrier;
	to_host.srcAccessMask       = vk::AccessFlagBits::eTransferWrite;
	to_host.dstAccessMask       = vk::AccessFlagBits::eHostRead;
	to_host.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	to_host.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	to_host.buffer              = m_buffer->Handle();
	to_host.offset              = 0;
	to_host.size                = size;
	vk_command.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer, vk::PipelineStageFlagBits::eHost,
	                           vk::DependencyFlags {}, 0, nullptr, 1, &to_host, 0, nullptr);
	m_pending = true;
}

void ScreenshotGrabber::RecordVideoFrame(CommandBuffer& command, const VulkanImage& source) {
	uint8_t probe[8] {};
	uint8_t rgb[3] {};
	if (!TexelToRgb(source.format, probe, rgb)) {
		m_rec_frame = false;
		return;
	}
	auto& slot = m_rec_slots[m_rec_next % m_rec_slots.size()];
	if (slot.pending) {
		FlushVideoSlot(slot); // ring wrapped before the GPU finished: wait for it
	}
	m_format = source.format;
	m_width  = source.extent.width;
	m_height = source.extent.height;
	const uint64_t size = static_cast<uint64_t>(m_width) * m_height * BytesPerTexel(m_format);
	if (slot.buffer == nullptr || slot.buffer->Size() < size) {
		slot.buffer = std::make_unique<Buffer>(m_graphics, m_scheduler, MemoryUsage::Download, 0,
		                                       vk::BufferUsageFlagBits::eTransferDst, size);
	}
	vk::BufferImageCopy region {};
	region.imageSubresource.aspectMask = vk::ImageAspectFlagBits::eColor;
	region.imageSubresource.layerCount = 1;
	region.imageExtent                 = {m_width, m_height, 1};
	auto vk_command                    = command.Handle();
	vk_command.copyImageToBuffer(source.image, vk::ImageLayout::eTransferSrcOptimal,
	                             slot.buffer->Handle(), 1, &region);
	vk::BufferMemoryBarrier to_host {};
	to_host.sType               = vk::StructureType::eBufferMemoryBarrier;
	to_host.srcAccessMask       = vk::AccessFlagBits::eTransferWrite;
	to_host.dstAccessMask       = vk::AccessFlagBits::eHostRead;
	to_host.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	to_host.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
	to_host.buffer              = slot.buffer->Handle();
	to_host.size                = size;
	vk_command.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer, vk::PipelineStageFlagBits::eHost,
	                           vk::DependencyFlags {}, 0, nullptr, 1, &to_host, 0, nullptr);
	slot.present = m_presents;
	slot.time_s  = NowSeconds();
	slot.pending = true;
}

// Called after the present was submitted: stores its tick in the newest slot and flushes the
// oldest one (two presents back), which the GPU has normally finished by now.
void ScreenshotGrabber::FinishVideoFrame(uint64_t tick) {
	auto& slot = m_rec_slots[m_rec_next % m_rec_slots.size()];
	if (!slot.pending) {
		return;
	}
	slot.tick = tick;
	m_rec_next++;
	auto& oldest = m_rec_slots[(m_rec_next + 1u) % m_rec_slots.size()];
	if (oldest.pending && m_scheduler.IsFree(oldest.tick)) {
		FlushVideoSlot(oldest);
	}
}

void ScreenshotGrabber::FlushVideoSlot(RecSlot& slot) {
	slot.pending = false;
	m_scheduler.Wait(slot.tick);
	slot.buffer->Invalidate(0, slot.buffer->Size());
	const auto     mapped = slot.buffer->Mapped();
	const uint32_t bpp    = BytesPerTexel(m_format);
	// Fixed output geometry (the presented image changes size between videos, logos and the game);
	// nearest sampling with a fractional step.
	constexpr uint32_t out_w = 960;
	constexpr uint32_t out_h = 540;
	if (m_rec_pipe == nullptr) {
		const auto cmd = std::string("ffmpeg -hide_banner -loglevel error -y -f rawvideo -pix_fmt rgb24 -s ") +
		                 std::to_string(out_w) + "x" + std::to_string(out_h) +
		                 " -r 60 -i - -c:v h264_nvenc -preset p4 -cq 24 -g 60 -pix_fmt yuv420p"
		                 " -movflags +frag_keyframe+empty_moov \"" +
		                 m_rec_path + "\"";
		m_rec_pipe  = _popen(cmd.c_str(), "wb");
		m_rec_index = std::fopen((m_rec_path + ".idx").c_str(), "w");
		LOGF("Recording: %s %ux%u (source %ux%u) first present=%u pipe=%s\n", m_rec_path.c_str(), out_w,
		     out_h, m_width, m_height, slot.present, m_rec_pipe != nullptr ? "ok" : "FAILED");
		if (m_rec_pipe == nullptr) {
			m_rec_path.clear();
			return;
		}
	}
	m_rec_rgb.resize(static_cast<size_t>(out_w) * out_h * 3);
	for (uint32_t y = 0; y < out_h; y++) {
		const auto  sy  = static_cast<size_t>(static_cast<uint64_t>(y) * m_height / out_h);
		const auto* row = mapped.data() + sy * m_width * bpp;
		auto*       out = m_rec_rgb.data() + static_cast<size_t>(y) * out_w * 3;
		for (uint32_t x = 0; x < out_w; x++) {
			const auto sx = static_cast<size_t>(static_cast<uint64_t>(x) * m_width / out_w);
			TexelToRgb(m_format, row + sx * bpp, out + static_cast<size_t>(x) * 3);
		}
	}
	std::fwrite(m_rec_rgb.data(), 1, m_rec_rgb.size(), m_rec_pipe);
	std::fflush(m_rec_pipe);
	if (m_rec_index != nullptr) {
		std::fprintf(m_rec_index, "%u %u %.3f\n", m_rec_frames, slot.present, slot.time_s - m_first_present_s);
		std::fflush(m_rec_index);
	}
	m_rec_frames++;
}

void ScreenshotGrabber::Finish(uint64_t tick) {
	if (m_rec_frame) {
		FinishVideoFrame(tick);
	}
	if (!m_pending || m_buffer == nullptr) {
		return;
	}
	m_pending = false;
	m_scheduler.Wait(tick);
	m_buffer->Invalidate(0, m_buffer->Size());
	const auto     mapped = m_buffer->Mapped();
	const uint32_t bpp    = BytesPerTexel(m_format);
	uint32_t       factor = 1;
	while (m_width / factor > 1920) {
		factor++;
	}
	const uint32_t       out_w = m_width / factor;
	const uint32_t       out_h = m_height / factor;
	std::vector<uint8_t> rgb(static_cast<size_t>(out_w) * out_h * 3);
	for (uint32_t y = 0; y < out_h; y++) {
		for (uint32_t x = 0; x < out_w; x++) {
			const auto* texel =
			    mapped.data() + (static_cast<size_t>(y) * factor * m_width + static_cast<size_t>(x) * factor) * bpp;
			TexelToRgb(m_format, texel, rgb.data() + (static_cast<size_t>(y) * out_w + x) * 3);
		}
	}
	const bool ok = WritePng(m_output, rgb, out_w, out_h);
	LOGF("Screenshot: %s %ux%u (source %ux%u format %d) present=%u %s\n", m_output.c_str(), out_w,
	     out_h, m_width, m_height, static_cast<int>(m_format), m_presents, ok ? "ok" : "FAILED");
	std::printf("Screenshot: %s %s\n", m_output.c_str(), ok ? "ok" : "FAILED");
	std::fflush(stdout);
	m_shots++;
	m_buffer.reset();
}

} // namespace Libs::Graphics
