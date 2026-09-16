layout(local_size_x = 8, local_size_y = 8) in;

layout(set = 0, binding = 0, std430) readonly buffer Input { uint data[]; } input_buffer;
#ifdef TARGET_IMAGE
// Session 73, C1 (gate "imgfuse"): the destination is the image itself. No format qualifier -
// shaderStorageImageWriteWithoutFormat is required of the device (vulkanWindow.cpp:350-353) and
// enabled (:643), and the UINT view the host binds (R8/R16/R32/R32G32/R32G32B32A32_UINT, one per
// element size) truncates the uvec4. A e2DArray view of the whole mip level means the shader's z
// coordinate IS the array layer, which the two tiler families that put the layer in surface_z and
// the seven that do not both get right.
layout(set = 0, binding = 1) writeonly uniform uimage2DArray output_image;
#else
layout(set = 0, binding = 1, std430) buffer Output { uint data[]; } output_buffer;
#endif

layout(set = 0, binding = 2, std140) uniform Push {
	uint src_base;
	uint dst_base;
	uint width;
	uint height;
	uint depth;
	uint surface_z;
	uint pitch_bytes;
	uint slice_bytes;
	uint blocks_per_row;
	uint blocks_per_slice;
	uint tail_x;
	uint tail_y;
	uint tail;
	uint base_layer; // session 73: destination array layer; the mip level is the view
} params;

#ifdef TARGET_IMAGE
void store_element(uint src, ivec3 coord) {
	uvec4 value = uvec4(0u);
	if (ELEMENT_BYTES >= 4) {
		// ELEMENT_BYTES is a specialization constant and is one of 1/2/4/8/16, so these are
		// constant-folded; no dynamic vector indexing is needed.
		value.x = input_buffer.data[src >> 2];
		if (ELEMENT_BYTES >= 8) { value.y = input_buffer.data[(src + 4u) >> 2]; }
		if (ELEMENT_BYTES >= 16) {
			value.z = input_buffer.data[(src + 8u) >> 2];
			value.w = input_buffer.data[(src + 12u) >> 2];
		}
	} else {
		// The scratch path needed atomicAnd/atomicOr here because two invocations shared a dword.
		// An R8_UINT / R16_UINT image has one texel per store: the read-modify-write disappears.
		uint mask = ELEMENT_BYTES == 1 ? 0xffu : 0xffffu;
		value.x   = (input_buffer.data[src >> 2] >> ((src & 3u) * 8u)) & mask;
	}
	imageStore(output_image, coord, value);
}
#else
void copy_element(uint src, uint dst) {
	if (ELEMENT_BYTES >= 4) {
		for (uint i = 0; i < ELEMENT_BYTES; i += 4) {
			output_buffer.data[(dst + i) >> 2] = input_buffer.data[(src + i) >> 2];
		}
	} else {
		uint mask = ELEMENT_BYTES == 1 ? 0xffu : 0xffffu;
		uint value = (input_buffer.data[src >> 2] >> ((src & 3u) * 8u)) & mask;
		uint shift = (dst & 3u) * 8u;
		atomicAnd(output_buffer.data[dst >> 2], ~(mask << shift));
		atomicOr(output_buffer.data[dst >> 2], value << shift);
	}
}
#endif

void main() {
	uvec3 p = gl_GlobalInvocationID;
	if (p.x >= params.width || p.y >= params.height || p.z >= params.depth) {
		return;
	}

	uvec3 extent = block_extent();
	uvec3 swizzle = p;
	uvec3 block = uvec3(0);
	if (params.tail != 0) {
		swizzle.xy += uvec2(params.tail_x, params.tail_y);
	} else {
		block = p / extent;
	}

	uint block_index = block.z * params.blocks_per_slice +
	                   block.y * params.blocks_per_row + block.x;
	uint tiled = block_index * BLOCK_BYTES +
	             block_offset(uvec3(swizzle.xy, swizzle.z + params.surface_z));
#ifdef TARGET_IMAGE
	// Detile direction only: the image variant is never used to tile. p.z is 0 for every
	// non-volume surface (GpuTileInfo::depth is set above 1 only for volumes, which the host
	// predicate excludes), so the coordinate is (x, y, layer).
	store_element(params.src_base + tiled,
	              ivec3(int(p.x), int(p.y), int(params.base_layer + p.z)));
#else
	uint linear = p.z * params.slice_bytes + p.y * params.pitch_bytes +
	              p.x * ELEMENT_BYTES;
	if (TILE == 0) {
		copy_element(params.src_base + tiled, params.dst_base + linear);
	} else {
		copy_element(params.src_base + linear, params.dst_base + tiled);
	}
#endif
}
