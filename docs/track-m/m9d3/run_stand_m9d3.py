"""M9d3 (HPP-876): copy of m657/m9d2/run_stand_m9d2.py with WANT_PURE 51 and the T109Stat names + zx_narrow_vi
bias_narrow_vi narrow_cd (built by mk_m9d3.py). Was:
M9d2 (HPP-874): copy of m657/m9d/run_stand_m9d.py with WANT_PURE 45 -> 49. Was:
M9d (HPP-869, ROADMAP s122 item 785(d)): driver of the KYTY_DIAG_T188 stands of a build directory.
  pure      t188_stand.exe <log>: "total=N match=N END" with N = WANT_PURE; the log holds "T188: mode=0 cls=all k=4" once
            and the exit lines of case rb_bad_none with the field names of T188Stat / T188Img / T109Stat in the order of
            design s.4.4 / s.4.5 / s.8.3.
  cls       t188_stand.exe <log> cls with KYTY_DIAG_T188=2 KYTY_DIAG_T188_CLS="<key>,zz,1": the arm line
            "T188Stand: cls ... ok=1" and the log line "T188: mode=2 cls=2 k=4".
  gpu1/gpu0 shader_recompiler_compute_tests.exe --t188-gpu-stand with KYTY_IMAGE_DETILE_FUSE=1 / 0: "total=16 ok=16 END".
  gpuv      the same with the Khronos validation layer (VK_INSTANCE_LAYERS): ok=16 and 0 validation lines naming
            vkCmdClearColorImage or vkCmdCopyImageToBuffer (g4 is caught here).
Usage: python run_stand_m9d.py <build dir> <out dir> [arm ...] (default: all). Every KYTY_* of the environment is removed.
Lock and STOP are checked first (exit 3). Prints one line per arm and ALL OK / FAIL. Processes at IDLE priority."""
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
WANT_PURE = 51  # M9d3: + t109_cd16, t109_cd1 (ROADMAP s122 item 789(v)(3)); M9d2: 49
WANT_GPU = 16
IDLE = 0x40
VK_LAYER_PATH = 'C:/VulkanSDK/1.4.357.0/Bin'

STAT = ('part part_st part_fill part_copy part_unk part_off part_synced part_dlmem reopen ep_new ep_prop prop_merge '
        'w_mipal w_inmip w_other w_bytes img_bytes img_bytes_unsync img_full_unsync in_pass in_pass_unsync cl_smp cl_rt '
        'cl_rtclr cl_dt cl_sto cl_clrop cl_oth cl_vo cl_cover cl_cmp cl_msaa cl_free cl_commit cl_copydst cl_skip '
        'cl_none open ep_pend pend_done pend_drop pend_free pend_open lost_bytes lost_pend_bytes w_ovf sync_full '
        'sync_part dl_mem ep_bad lock_bad tint_ep tint_mips tint_bytes tint_part_mips tint_skip_fmt tint_skip_vol '
        'tint_skip_cls tint_skip_cpu tint_skip_ovf tint_bad tint_rb_req tint_rb0_ok tint_rb0_bad tint_rb0_none '
        'tint_rb0_nofmt tint_rb1_ok tint_rb1_over tint_rb1_bad tint_rb1_none').split()
IMG_HEAD = 'key fmt tile w h levels layers cmp samples usage vol'.split()
IMG = ('ev ev_st ev_fill ev_copy ev_off ev_synced ev_dlmem ep_new ep_prop cl_smp cl_rt cl_rtclr cl_vo cl_commit cl_free '
       'lost_bytes lost_pend_bytes img_bytes tint_ep tint_mips tint_bytes tint_skip tint_rb0_ok tint_rb0_bad '
       'tint_rb1_ok tint_rb1_over tint_rb1_bad').split()
T109 = 'd32 zx_d32 zx_narrow bias_d32 bias_narrow ovr_w ovr_vpc zx_narrow_vi bias_narrow_vi narrow_cd'.split()


def env_clean(extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_') and not k.startswith('VK_')}
    env.update(extra)
    return env


def run(cmd, out_path, extra, cwd, timeout=300):
    with open(out_path, 'wb') as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env_clean(extra), cwd=cwd, timeout=timeout,
                            creationflags=IDLE).returncode
    return rc, open(out_path, 'rb').read().decode('utf-8', 'replace')


def names(line, prefix_skip):
    return [kv.split('=', 1)[0] for kv in line.split()[prefix_skip:] if '=' in kv]


def arm_pure(b, o):
    log = o + '/pure_log.txt'
    if os.path.exists(log):
        os.remove(log)
    rc, out = run([b + '/t188_stand.exe', log], o + '/pure_out.txt', {}, b)
    text = open(log, 'rb').read().decode('utf-8', 'replace') if os.path.exists(log) else ''
    lines = text.splitlines()
    ok = rc == 0 and ('T188Stand: total=%d match=%d END' % (WANT_PURE, WANT_PURE)) in out
    mode = [l for l in lines if l.startswith('T188: ')]
    ok_mode = mode == ['T188: mode=0 cls=all k=4']
    stat = [l for l in lines if l.startswith('T188Stat: when=exit ')]
    img = [l for l in lines if l.startswith('T188Img: when=exit ')]
    t109 = [l for l in lines if l.startswith('T109Stat: when=exit ')]
    ok_stat = len(stat) == 1 and names(stat[0], 2) == STAT
    ok_img = len(img) == 1 and names(img[0], 2) == IMG_HEAD + IMG
    ok_t109 = len(t109) == 1 and names(t109[0], 2) == T109
    good = ok and ok_mode and ok_stat and ok_img and ok_t109
    m = re.search(r'total=(\d+) match=(\d+) END', out)
    print('pure rc=%d %s mode_line=%d stat_names=%d img_names=%d t109_names=%d -> %s' % (
        rc, m.group(0) if m else 'no END', ok_mode, ok_stat, ok_img, ok_t109, 'OK' if good else 'FAIL'))
    return good


def arm_cls(b, o):
    log = o + '/cls_log.txt'
    if os.path.exists(log):
        os.remove(log)
    key = '5e06245183e5ff80'  # ClassKey(Fields()) of T188Stand.cpp (usage 1) - printed by the pure arm's T188Img line
    rc, out = run([b + '/t188_stand.exe', log, 'cls'], o + '/cls_out.txt',
                  {'KYTY_DIAG_T188': '2', 'KYTY_DIAG_T188_CLS': key + ',zz,1'}, b)
    text = open(log, 'rb').read().decode('utf-8', 'replace') if os.path.exists(log) else ''
    mode = [l for l in text.splitlines() if l.startswith('T188: ')]
    good = rc == 0 and 'ok=1' in ''.join(l for l in out.splitlines() if l.startswith('T188Stand: cls ')) and \
        mode == ['T188: mode=2 cls=2 k=4']
    print('cls rc=%d mode_line=%s -> %s' % (rc, mode, 'OK' if good else 'FAIL'))
    return good


def arm_gpu(b, o, tag, extra):
    rc, out = run([b + '/shader_recompiler_compute_tests.exe', '--t188-gpu-stand'], o + '/%s_out.txt' % tag, extra, b)
    good = rc == 0 and ('T188Gpu: total=%d ok=%d END' % (WANT_GPU, WANT_GPU)) in out
    bad = [l for l in out.splitlines() if l.startswith('T188Gpu: member=') and l.endswith('ok=0')]
    vlines = [l for l in out.splitlines() if 'Validation' in l or 'VUID' in l]
    vhit = [l for l in vlines if 'vkCmdClearColorImage' in l or 'vkCmdCopyImageToBuffer' in l]
    if tag == 'gpuv':
        good = good and len(vhit) == 0
    print('%s rc=%d ok16=%d failed_members=%s validation_lines=%d clear_or_copy=%d -> %s' % (
        tag, rc, 1 if ('ok=%d END' % WANT_GPU) in out else 0, [l.split()[1] for l in bad], len(vlines), len(vhit),
        'OK' if good else 'FAIL'))
    return good


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        return 3
    b = os.path.abspath(sys.argv[1]).replace(os.sep, '/')
    o = os.path.abspath(sys.argv[2]).replace(os.sep, '/')
    arms = sys.argv[3:] or ['pure', 'cls', 'gpu1', 'gpu0', 'gpuv']
    os.makedirs(o, exist_ok=True)
    ok = True
    for arm in arms:
        if os.path.exists(LOCK) or os.path.exists(STOP):
            print('LOCK or STOP before', arm)
            return 3
        if arm == 'pure':
            ok &= arm_pure(b, o)
        elif arm == 'cls':
            ok &= arm_cls(b, o)
        elif arm == 'gpu1':
            ok &= arm_gpu(b, o, 'gpu1', {'KYTY_IMAGE_DETILE_FUSE': '1'})
        elif arm == 'gpu0':
            ok &= arm_gpu(b, o, 'gpu0', {'KYTY_IMAGE_DETILE_FUSE': '0'})
        elif arm == 'gpuv':
            ok &= arm_gpu(b, o, 'gpuv', {'VK_LAYER_PATH': VK_LAYER_PATH,
                                         'VK_INSTANCE_LAYERS': 'VK_LAYER_KHRONOS_validation',
                                         'VK_LOADER_LAYERS_ENABLE': '*validation'})
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
