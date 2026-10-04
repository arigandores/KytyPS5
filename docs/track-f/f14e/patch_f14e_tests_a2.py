"""F14e (HPP-505, ROADMAP s122 item 415(b)): shader_cfg_tests probes of KYTY_FIX_F19 - part A2, on top of part A
(builds against the sources without the fix too).

The manual compare of an indirect image table is not the shape SpirvManualDepthCompareCount counts: the emitter
samples every member in its own OpSwitch case, merges the texels with OpPhi and compares the merged texel once
(seen in the base SPIR-V of the probe, suite/base/spv/111.spv: OpSwitch -> 2 x OpImageSampleExplicitLod -> OpPhi ->
OpCompositeExtract -> OpFOrdLessThanEqual -> OpSelect 1.0 0.0). Part A counted 0 there and failed at =0 on the base.
A2: SpirvManualDepthComparePhiCount (the same shape with X = OpCompositeExtract P, P = OpPhi of sample results only);
a manual table is Dref 0, one merged compare, one plain sample per member.
Usage: python patch_f14e_tests_a2.py <repo root>.
"""
import sys

ROOT = sys.argv[1].rstrip('/\\')
NL = chr(10)


def patch(rel, edits):
    path = ROOT + '/' + rel
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r', '')
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            raise SystemExit('anchor count %d in %s: %r' % (n, rel, old[:120]))
        text = text.replace(old, new)
    out = text.encode('utf-8')
    if crlf:
        out = out.replace(b'\n', b'\r\n')
    open(path, 'wb').write(out)
    print('patched', rel, 'edits', len(edits), 'crlf', crlf)


def L(*lines):
    return NL.join(lines) + NL


HELPER_OLD = L(
    'F19IndirectProbe CompileF19IndirectTable(Prospero::BufferFormat root_format,',
)
HELPER_NEW = L(
    '// The manual compare of an indirect image table (F14e part A2): every member is sampled with sample_opcode in its',
    '// own OpSwitch case, the texels are merged by OpPhi and compared once - OpSelect float compare 1.0 0.0 whose',
    '// compare reads X = OpCompositeExtract P, P = OpPhi whose incoming values are all sample_opcode results.',
    'uint32_t SpirvManualDepthComparePhiCount(const std::vector<uint32_t> &binary,',
    '                                         uint32_t sample_opcode) {',
    '  std::unordered_set<uint32_t> float_types;',
    '  std::unordered_map<uint32_t, uint32_t> float_constants;',
    '  std::unordered_set<uint32_t> samples;',
    '  std::unordered_map<uint32_t, std::vector<uint32_t>> phis;',
    '  std::unordered_map<uint32_t, uint32_t> extracts;',
    '  std::unordered_map<uint32_t, uint32_t> compares;',
    '  std::vector<std::array<uint32_t, 4>> selects;',
    '  for (size_t i = 5; i < binary.size();) {',
    '    const uint32_t word_count = binary[i] >> 16u;',
    '    const uint32_t opcode = binary[i] & 0xffffu;',
    '    Check(word_count != 0u && i + word_count <= binary.size(),',
    '          "SPIR-V instruction stream is malformed");',
    '    if (opcode == 22u && word_count >= 3u && binary[i + 2u] == 32u) { // OpTypeFloat 32',
    '      float_types.insert(binary[i + 1u]);',
    '    } else if (opcode == 43u && word_count >= 4u &&',
    '               float_types.count(binary[i + 1u]) != 0u) { // OpConstant',
    '      float_constants[binary[i + 2u]] = binary[i + 3u];',
    '    } else if (opcode == sample_opcode && word_count >= 3u) {',
    '      samples.insert(binary[i + 2u]);',
    '    } else if (opcode == 245u && word_count >= 5u) { // OpPhi type result (value parent)*',
    '      auto &values = phis[binary[i + 2u]];',
    '      for (uint32_t w = 3u; w + 1u < word_count; w += 2u) {',
    '        values.push_back(binary[i + w]);',
    '      }',
    '    } else if (opcode == 81u && word_count >= 4u) { // OpCompositeExtract',
    '      extracts[binary[i + 2u]] = binary[i + 3u];',
    '    } else if (opcode >= 180u && opcode <= 191u && word_count >= 5u) {',
    '      compares[binary[i + 2u]] = binary[i + 4u];',
    '    } else if (opcode == 169u && word_count >= 6u) { // OpSelect',
    '      selects.push_back({binary[i + 1u], binary[i + 3u], binary[i + 4u], binary[i + 5u]});',
    '    }',
    '    i += word_count;',
    '  }',
    '  uint32_t count = 0;',
    '  for (const auto &select: selects) {',
    '    const auto compare = compares.find(select[1]);',
    '    const auto one = float_constants.find(select[2]);',
    '    const auto zero = float_constants.find(select[3]);',
    '    if (float_types.count(select[0]) == 0u || compare == compares.end() ||',
    '        one == float_constants.end() || one->second != 0x3f800000u ||',
    '        zero == float_constants.end() || zero->second != 0u) {',
    '      continue;',
    '    }',
    '    const auto extract = extracts.find(compare->second);',
    '    if (extract == extracts.end()) {',
    '      continue;',
    '    }',
    '    const auto phi = phis.find(extract->second);',
    '    if (phi != phis.end() && !phi->second.empty() &&',
    '        std::all_of(phi->second.begin(), phi->second.end(),',
    '                    [&](uint32_t v) { return samples.count(v) != 0u; })) {',
    '      count++;',
    '    }',
    '  }',
    '  return count;',
    '}',
    '',
    'F19IndirectProbe CompileF19IndirectTable(Prospero::BufferFormat root_format,',
)

COUNT_OLD = L(
    '  probe.manual = SpirvManualDepthCompareCount(result.spirv, OpImageSampleExplicitLod);',
)
COUNT_NEW = L(
    '  probe.manual = SpirvManualDepthComparePhiCount(result.spirv, OpImageSampleExplicitLod);',
)

CHECK_OLD = L(
    '      Check(probe.dref == 0u && probe.manual == probe.members,',
    '            "indirect comparison table must be the manual compare for every member");',
)
CHECK_NEW = L(
    '      Check(probe.dref == 0u && probe.manual == 1u && probe.plain == probe.members,',
    '            "indirect comparison table must be the manual compare for every member");',
)

patch('tests/shaderCfgTests.cpp', [(HELPER_OLD, HELPER_NEW), (COUNT_OLD, COUNT_NEW), (CHECK_OLD, CHECK_NEW)])
print('ALL OK')
