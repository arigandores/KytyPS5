import collections, struct, sys
sys.path.insert(0, 'C:/kyty/s288/s17c')
import s17c_read as R, tc_s17c
G = 'C:/kyty/s288/s17c'
IMG = ['numeric_class','dimension','mip_count','conversion_format','shader_swizzle','indirect_root','indirect_mapping_offset','indirect_search_iterations']
def fields(spec):
    nb = struct.unpack_from('<I', spec, 0)[0]; out = {}
    for i in range(nb):
        w = struct.unpack_from('<3I', spec, 4 + 12 * i)
        for j, n in enumerate(['packed_stride','descriptor_format','descriptor_swizzle']): out['buf%d.%s' % (i, n)] = w[j]
    o = 4 + 12 * nb; ni = struct.unpack_from('<I', spec, o)[0]; o += 4
    for i in range(ni):
        b = spec[o + 44 * i: o + 44 * (i + 1)]
        w = struct.unpack_from('<8I', b, 0)
        for j, n in enumerate(IMG): out['img%d.%s' % (i, n)] = w[j]
        out['img%d.cube' % i] = b[32]; out['img%d.manual_depth_compare' % i] = b[33]
        out['img%d.depth_compare_op' % i] = struct.unpack_from('<I', b, 36)[0]; out['img%d.fmask' % i] = b[40]
    return out
