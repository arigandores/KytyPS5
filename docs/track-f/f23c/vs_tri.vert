#version 450
// F23c (HPP-587): full-screen triangle; location 0 = (u, v, 0, 1), u and v in [0, 1] over the target
// (stands in for the guest VS 0xa356f0ca70df2e47, whose output 0 is the video texture coordinate).
layout(location = 0) out vec4 o_param0;
void main() {
	vec2 uv = vec2(float((gl_VertexIndex << 1) & 2), float(gl_VertexIndex & 2));
	o_param0 = vec4(uv, 0.0, 1.0);
	gl_Position = vec4(uv * 2.0 - 1.0, 0.0, 1.0);
}
