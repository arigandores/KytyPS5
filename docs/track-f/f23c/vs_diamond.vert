#version 450
// F23c (HPP-587): a diamond (two triangles with edges at 45 degrees) - partial quads with helper invocations on every
// edge; location 0 = (u, v, 0, 1) of the same mapping as vs_tri.vert; pixels outside keep the clear value.
layout(location = 0) out vec4 o_param0;
const vec2 P[6] = vec2[6](vec2(-0.93, 0.01), vec2(0.02, -0.91), vec2(0.95, 0.03),
                          vec2(-0.93, 0.01), vec2(0.95, 0.03), vec2(0.01, 0.97));
void main() {
	vec2 p = P[gl_VertexIndex];
	o_param0 = vec4(p * 0.5 + 0.5, 0.0, 1.0);
	gl_Position = vec4(p, 0.0, 1.0);
}
