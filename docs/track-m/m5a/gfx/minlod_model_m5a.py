import os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK'); sys.exit(3)
# T021 model (no game, no GPU): the Vulkan minLod each side writes for a sampled view, and the lowest image level the
# view can then read, under the ABSOLUTE reading of VkImageViewMinLodCreateInfoEXT::minLod (VUID-...-minLod-06456:
# "less or equal to the index of the last mipmap level accessible to the view"; vuid_m5a.out.txt).
#  ours  (dd73d04d descriptors.cpp:1952, imageView.cpp:387): minLod = min(M/256, count-1)
#  upstr (f38d738ee descriptors.cpp TextureViewInfo + imageView.cpp FindView): rel = M - 256*B if M > 256*B else 0;
#        minLod = B + rel/256 if rel else none
#  hardware (T# BASE_LEVEL = B, MIN_LOD = M, same frame as Vulkan minLod per radv [I]): lowest level = max(B, M/256)
# Deferred-mip clamp of ours (textureCache.cpp:2662-2670): rel = pending - B (whole levels) passed the same way.
def lowest(base, minlod):
    return base if minlod is None else max(base, minlod)

rows = 0; diff_tsharp = 0; diff_defer = 0
print('T# path: B count M/256 | ours_minLod upstream_minLod | lowest level ours / upstream / hw')
for B in range(0, 4):
    for count in range(1, 6):
        last = B + count - 1
        for M4 in range(0, 4 * last + 1):   # M in quarter levels, M <= last level (upstream EXITs above)
            M = M4 * 64
            if M == 0 or count <= 1:
                continue                      # ours applies MIN_LOD only for view_levels > 1 and M != 0
            ours = min(M / 256.0, count - 1.0)
            rel = M - 256 * B
            up = (B + rel / 256.0) if rel > 0 else None
            hw = max(B, M / 256.0)
            lo, lu = lowest(B, ours), lowest(B, up)
            rows += 1
            if abs(lo - hw) > 1e-9:
                diff_tsharp += 1
                if diff_tsharp <= 12:
                    print('  B=%d count=%d M=%.2f | ours %.2f upstream %s | lowest ours %.2f upstream %s hw %.2f' % (
                        B, count, M / 256.0, ours, 'none' if up is None else '%.2f' % up, lo,
                        '%.2f' % lu, hw))
            assert abs(lu - hw) < 1e-9
print('T# cases', rows, 'ours differs from hw', diff_tsharp)
# check: every differing case has B > 0 and M/256 > count-1
bad = 0
for B in range(0, 4):
    for count in range(2, 6):
        for M4 in range(1, 4 * (B + count - 1) + 1):
            M = M4 * 64
            ours = min(M / 256.0, count - 1.0)
            if abs(max(B, ours) - max(B, M / 256.0)) > 1e-9 and not (B > 0 and M / 256.0 > count - 1):
                bad += 1
print('differing cases outside {B>0 and M/256 > count-1}:', bad)
print('deferred-mip path: pending levels P (top P levels absent), view base B')
for P in range(1, 4):
    for B in range(0, 3):
        for count in range(1, 6):
            rel = P - B if P > B else 0
            if rel == 0 or rel >= count:
                continue  # ours completes the upload instead (textureCache.cpp:2666)
            ours = min(rel, count - 1)
            reads_pending = max(B, ours) < P
            if reads_pending:
                diff_defer += 1
                print('  P=%d B=%d count=%d: ours minLod %d -> lowest level %d < P=%d (pending level readable)' % (
                    P, B, count, ours, max(B, ours), P))
print('deferred cases reading a pending level', diff_defer, '- all need P >= 2; default KYTY_MIP_DEFER_LEVELS = 1 '
      '(textureCache.cpp:327)')
print('DONE')
