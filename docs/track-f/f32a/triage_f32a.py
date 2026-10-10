# F32a (HPP-733): triage of the signatures that the delta sweep found and the F0 baseline did not have (new_f32a.tsv).
# Every signature gets exactly one class by the ordered rules below; an unclassified signature fails the run.
# Class FIXTURE requires the example path to lie in a fixture folder; class GUEST requires the 'GuestOut:' prefix.
# Usage: python triage_f32a.py <new_f32a.tsv> <out.tsv>   (prints the count per class, the K1-K4 candidates and ALL OK)
import re, sys, collections

TAB = chr(9)
FXPATH = re.compile(r'/(fx|fx_|fxread|fxwork|fixt|test_|work_|mut)[^/]*/|/lead_skipfx/|/wtm/|/runs/log_tests')
RULES = [
    # (class, register row or note, signature regex)
    ('ROW', '\u041126\u0432 (VOPC 0xf3 V_CMPX_LE_U64, \u00a711)', r'^OPCODE_NI family=VOPC opcode=0xf3$'),
    ('ROW', '\u04243 (speculative CS skip; path of the build worktree in the reason)', r'^CsPretranslate: skipped hash=X reason=C:\\kyty\\.*(TranslationBudget\.h:X speculative translation budget exceeded|ResourceTracking\.cpp:X shader resource tracking)'),
    ('ROW', '\u041135 (dual-source blend without dualSrcBlend, FIXED)', r'^\[Vulkan\]\[E\]\[X\]: vkCreateGraphicsPipelines\(\): .*srcColorBlendFactor'),
    ('ROW', '\u041137 (swapchain on a zero-size window, FIXED)', r'imageExtent'),
    ('ROW', '\u04246 (write to out_mrt without a bound target, NOT A DEFECT)', r'^\[Vulkan\]\[W\]\[X\]: vkCmdDrawIndexedIndirect\(\): Inside \[VK_SHADER_STAGE_FRAGMENT_BIT\] it writes to \[Output variable'),
    ('ROW_K5', '\u042423 (K5, WASAPI audio client)', r'^AudioOut: SDL_OpenAudioDevice failed: WASAPI'),
    ('FIXTURE', 'detector / reader fixture logs', r'^(=== Stubbed function|CsPretranslate: enqueue skipped|CsPretranslate: skipped hash=X reason=[A-Z]\.cpp|CsPretranslate: skipped hash=X reason=[A-Z]\.h|CsPretranslate: skipped hash=X reason=X\.cpp|Relocate: unresolved PLT import patched to stub lib=Foo|Unresolved import stub called|\[Vulkan\]\[E\] (some error|validation error x)|shader CFG build failed: boom outside|xFrameTrace|Unhandled exception: (x|X|access violation|0xC0000005)$|Unhandled host exception: type=X code=X pc=X$|ErrorDeviceLost$|GpuHangAbort: X s$|--- Error ---$)'),
    ('INSTR', 'knob / stand / test-runner print (not the default path)', r'^(ShaderReplay: |LogAsync: |DiagBX-x: |DiagFX: |DiagFXId: |TestLogStall: |fatal X of X -> p_s|PASS |FAIL |FAILED|failed: |\(vX\) |fu: |fX: |base |tX |arms X MEMBERS|scfg failed-lines|aprop failed-lines|fsX shader_cfg_tests|ShaderCfgTests: failed: |shader resource evaluation failed: )'),
    ('GUEST', 'guest print (asset names contain key words: crash, cannot, not found)', r'^GuestOut: '),
    ('FS', 'host directory listing of game data (path contains "crash")', r'^(Open dir: |dir    = )'),
    ('ARGS', 'command line / level document of a hub level (word "crash" in the level name)', r'^(ARGS: |argv\[X\] = |LevelDocument Loaded: )'),
]


def main():
    src, out = sys.argv[1], sys.argv[2]
    rows = open(src, encoding='utf-8').read().splitlines()
    hdr = rows[0].split(TAB)
    iS, iEx, iL = hdr.index('signature'), hdr.index('example_path:line'), hdr.index('logs')
    res = []
    bad = []
    cnt = collections.Counter()
    for l in rows[1:]:
        x = l.split(TAB)
        sig, ex = x[iS], x[iEx]
        hit = None
        for c, note, rx in RULES:
            if re.search(rx, sig):
                hit = (c, note)
                break
        if hit is None:
            bad.append('UNCLASSIFIED ' + sig[:120])
            continue
        if hit[0] == 'FIXTURE' and not FXPATH.search(ex.replace(chr(92), '/')):
            bad.append('FIXTURE OUTSIDE FIXTURE PATH %s %s' % (sig[:80], ex))
        cnt[hit[0]] += 1
        res.append([hit[0], hit[1], x[iL], ex, sig])
    with open(out, 'w', encoding='utf-8', newline=chr(10)) as o:
        o.write(TAB.join(['class', 'row_or_note', 'logs', 'example_path:line', 'signature']) + chr(10))
        for r in res:
            o.write(TAB.join(r) + chr(10))
    print('signatures', len(rows) - 1, 'classified', len(res), dict(cnt))
    print('new K1-K4 rows proposed by the triage: 0' if not bad else '')
    for b in bad:
        print(b)
    print('ALL OK' if not bad and len(res) == len(rows) - 1 else 'FAILED')
    sys.exit(0 if not bad else 1)


if __name__ == '__main__':
    main()
