"""F16k2 (HPP-590, ROADMAP s122 item 496(b)(1)-(6)): the new cases of the test site --f16k-only.

    python p_tests2.py <repo root>

tests/ShaderRecompilerComputeTests.cpp, CheckF16k: names and the no-hit line form; K8 (RC4: a CPU-modified CMASK page
without a crossing GPU write - why=cpu, f5cmu_exact_cpu); K7 (RC5: an FCE acquisition without a B42 hit - kept_applied
and the line cmask_fce_nohit with KYTY_FIX_F5CMU, the old decision and no line without it); D18 (RC1: wr_after=large),
D19 (RC2: cpu_mod by the CPU write epoch since the fill), D20 (RC3: stamp_late); Z (f5cmu_exact_cpu). LF in, LF out;
every anchor is whole lines and occurs exactly once.
"""
import sys

ROOT = sys.argv[1]
P = ROOT + "/tests/ShaderRecompilerComputeTests.cpp"
data = open(P, "rb").read()
if b"\r" in data:
    raise SystemExit("CR in " + P)
T = data.decode("utf-8")


def sub(old, new):
    global T
    n = T.count(old)
    if n != 1:
        raise SystemExit("anchor count %d for %r" % (n, old[:100]))
    T = T.replace(old, new)


# ---- names and the no-hit line form
sub("                  std::string(DiagF5::CmuWhyName(W::NoLayer)) == \"nolayer\" &&\n",
    "                  std::string(DiagF5::CmuWhyName(W::NoLayer)) == \"nolayer\" &&\n"
    "                  std::string(DiagF5::CmuWhyName(W::Cpu)) == \"cpu\" &&\n")
sub("                  std::string(DiagF5::Name(C::CmaskRtBucketOnly)) == \"cmask_rt_bucket_only\",\n",
    "                  std::string(DiagF5::Name(C::CmaskRtBucketOnly)) == \"cmask_rt_bucket_only\" &&\n"
    "                  std::string(DiagF5::Name(C::F5CmuExactCpu)) == \"f5cmu_exact_cpu\",\n")
sub("      F16kOk(\"pure helpers (ScanReason R1-R4, names, StaleBucketOnly, event line)\");\n",
    "      F16kOk(\"pure helpers (ScanReason R1-R4, names, StaleBucketOnly, event line)\");\n"
    "      // Track F, F16k2 (RC5, item 496(b)(5)): the line of a decision without a B42 hit (no `applied`, b42 none / drawn).\n"
    "      const auto nohit = DiagF5::FormatCmuNoHit(5, {.present = 7, .gpu = 9, .image = 0x10, .cmask = 0x20, .width = 1024,\n"
    "                                                    .height = 1024, .applied = true,\n"
    "                                                    .event = {F::KeptApplied, W::None}},\n"
    "                                                false);\n"
    "      const auto nohit_cpu = DiagF5::FormatCmuNoHit(6, {.present = 1, .gpu = 2, .image = 0x10, .cmask = 0x20, .width = 8,\n"
    "                                                        .height = 8, .applied = false,\n"
    "                                                        .event = {F::ExactStale, W::Cpu}},\n"
    "                                                    true);\n"
    "      Require(name, \"no-hit line form\",\n"
    "              nohit == \"DiagF5Ev: cmask_fce_nohit n=5 b42=none present=7 gpu=9 image=0x0000000000000010 \"\n"
    "                       \"cmask=0x0000000000000020 extent=1024x1024 fix=kept_applied\" &&\n"
    "                  nohit_cpu == \"DiagF5Ev: cmask_fce_nohit n=6 b42=drawn present=1 gpu=2 image=0x0000000000000010 \"\n"
    "                               \"cmask=0x0000000000000020 extent=8x8 fix=exact_stale why=cpu\",\n"
    "              \"the no-hit line: \" + nohit + \" | \" + nohit_cpu);\n"
    "      F16kOk(\"F16k2 pure helpers (why=cpu, f5cmu_exact_cpu, no-hit line form)\");\n")

# ---- K8 (RC4)
sub("        int writes; // 0 none, 1 neighbour, 2 crossing, 3 nine neighbours, 4 neighbour + no packed decoding\n",
    "        int writes; // 0 none, 1 neighbour, 2 crossing, 3 nine neighbours, 4 neighbour + no packed decoding,\n"
    "                    // 5 a CPU write on the page of the fill (F16k2, RC4)\n")
sub("          {\"K5 kept without a clear (decode refused)\", 4, \"kept\", false, false, \"decode\", {{C::F5CmuKept, 1}}},\n",
    "          {\"K5 kept without a clear (decode refused)\", 4, \"kept\", false, false, \"decode\", {{C::F5CmuKept, 1}}},\n"
    "          {\"K8 CPU-modified CMASK page, no crossing GPU write: why=cpu\", 5, \"exact_stale\", false, false, \"cpu\",\n"
    "           {{C::F5CmuExactStale, 1}, {C::F5CmuExactCpu, 1}}},\n")
sub("        } else if (k.writes == 3) {\n"
    "          for (uint32_t i = 0; i < 9; i++) {\n"
    "            BTA::F16kNoteGpuWrite(buffers, meta + 0x2000 + i * 0x100, 0x100);\n"
    "          }\n"
    "        }\n",
    "        } else if (k.writes == 3) {\n"
    "          for (uint32_t i = 0; i < 9; i++) {\n"
    "            BTA::F16kNoteGpuWrite(buffers, meta + 0x2000 + i * 0x100, 0x100);\n"
    "          }\n"
    "        } else if (k.writes == 5) {\n"
    "          buffers.InvalidateMemory(meta + 0x100, 4); // a CPU write on the page of the fill, announced as a fault would\n"
    "        }\n")
sub("        for (const auto counter : {C::F5CmuKept, C::F5CmuKeptApplied, C::F5CmuExactStale, C::F5CmuFallback}) {\n",
    "        for (const auto counter :\n"
    "             {C::F5CmuKept, C::F5CmuKeptApplied, C::F5CmuExactStale, C::F5CmuFallback, C::F5CmuExactCpu}) {\n")
sub("        F16kOk(k.stage);\n      }\n      // K6: a draw-path acquisition",
    "        F16kOk(k.stage);\n      }\n"
    "      // F16k2: K8 left the CMASK page CPU-modified - a read acquisition uploads it again (K6 sees GPU writes only).\n"
    "      (void)buffers.ObtainBuffer(meta, 0x10000, false, false);\n"
    "      Require(name, \"K8 CPU-clean again\", !buffers.IsRegionCpuModified(meta, 0x10000),\n"
    "              \"the metadata range is still CPU-modified after a read acquisition\");\n"
    "      // K6: a draw-path acquisition")

# ---- K7 (RC5)
sub("    // ---- D: F26 at the DCC sites and the reasons of branch 2 (item 492(g)(2), (5))\n",
    "    // ---- K7 (Track F, F16k2, RC5, ROADMAP s122 item 496(b)(5)): an FCE acquisition without a B42 hit - a 1024x1024\n"
    "    // target carries CMASK metadata from its registers, so FixB42Probe answers None (cmask_fce_meta) and no cmask_fce\n"
    "    // line is printed; a PendingDcc fill of 0 at its CMASK address and a neighbour write in the bucket: with\n"
    "    // KYTY_FIX_F5CMU the fill is kept and cleared (kept_applied) and the line cmask_fce_nohit is printed; without it the\n"
    "    // old decision (the fill is dropped) and no line.\n"
    "    {\n"
    "      constexpr uint64_t color = base + 0x1000000;\n"
    "      constexpr uint64_t meta = base + 0x1600000;\n"
    "      RenderContext context(m_runtime_context);\n"
    "      auto &scheduler = context.GetCommandScheduler();\n"
    "      HW::Context registers{};\n"
    "      HW::UserConfig user_config{};\n"
    "      HW::Shader shaders{};\n"
    "      registers.SetColorBase(0, {.addr = color});\n"
    "      registers.SetColorInfo(0, {.cmask_fast_clear_enable = true,\n"
    "                                 .format = Prospero::ChannelLayout::k8_8_8_8,\n"
    "                                 .channel_type = Prospero::ChannelType::kUNorm,\n"
    "                                 .channel_order = Prospero::ChannelOrder::kStandard});\n"
    "      registers.SetColorAttrib2(0, {.height = 1023, .width = 1023});\n"
    "      registers.SetColorAttrib3(0, {.tile_mode = Prospero::TileMode::kRenderTarget, .dimension = 1,\n"
    "                                    .metadata_pipe_aligned = true});\n"
    "      registers.SetColorCmask(0, {.addr = meta});\n"
    "      registers.SetColorClearWord0(0, {.word0 = 0xff000000u});\n"
    "      registers.SetColorClearWord1(0, {.word1 = 0});\n"
    "      registers.SetRenderTargetMask(0x0f);\n"
    "      scheduler.Begin(registers, user_config, shaders);\n"
    "      context.MapMemory(base, allocation_size);\n"
    "      auto &cache = context.GetTextureCache();\n"
    "      auto &executor = context.GetRenderExecutor();\n"
    "      auto &buffers = context.GetBufferCache();\n"
    "      RenderColorInfo target{};\n"
    "      RTA::ResolveRenderColorTarget(executor, scheduler.Current(), target, 0);\n"
    "      Require(name, \"K7 target\",\n"
    "              target.image_id && target.desc.info.metadata.kind == ImageMetadataKind::Cmask &&\n"
    "                  target.desc.info.metadata.range.address == meta && target.desc.info.metadata.range.size == 0x2000,\n"
    "              fmt::format(\"the 1024x1024 CMASK target (kind {} size 0x{:x})\",\n"
    "                          static_cast<int>(target.desc.info.metadata.kind), target.desc.info.metadata.range.size));\n"
    "      const auto tid = target.image_id;\n"
    "      (void)buffers.ObtainBuffer(meta, 0x10000, false, false);\n"
    "      Require(name, \"K7 CPU-clean metadata\", !buffers.IsRegionCpuModified(meta, 0x10000),\n"
    "              \"the metadata range is still CPU-modified after a read acquisition\");\n"
    "      TTA::F16kEraseMeta(cache, meta);\n"
    "      cache.TrackDccFill(meta, 0x2000, 0);\n"
    "      BTA::F16kNoteGpuWrite(buffers, meta, 0x2000);\n"
    "      cache.StampPendingDccFill();\n"
    "      BTA::F16kNoteGpuWrite(buffers, meta + 0x2000, 0x100); // a neighbour in the 64 KB bucket, no overlap\n"
    "      const auto lines = F16kCount(\"DiagF5Ev:\");\n"
    "      const auto before = F16kRead();\n"
    "      RTA::MaterializeColorClears(executor, scheduler.Current());\n"
    "      const auto after = cache.QueryMetaFill(meta, tid);\n"
    "      const bool applied = after.found && after.cmask && after.fill_value == 0 && after.clear_mask != UINT32_MAX;\n"
    "      Require(name, \"K7 decision\", applied == cmu,\n"
    "              fmt::format(\"applied {} != expected {} (fill 0x{:x} mask 0x{:x})\", applied, cmu, after.fill_value,\n"
    "                          after.clear_mask));\n"
    "      F16kDelta(\"K7 decision\", before,\n"
    "                {{C::CmaskFce, f5 ? 1u : 0u}, {C::CmaskFceMeta, f5 ? 1u : 0u}, {C::CmaskFceB42, 0},\n"
    "                 {C::CmaskFceUnapplied, 0}, {C::F5CmuKept, cmu && f5 ? 1u : 0u},\n"
    "                 {C::F5CmuKeptApplied, cmu && f5 ? 1u : 0u}, {C::F5CmuExactStale, 0}, {C::F5CmuFallback, 0},\n"
    "                 {C::F5CmuExactCpu, 0}});\n"
    "      if (f5 && cmu) {\n"
    "        const auto line = F16kLast(\"DiagF5Ev: cmask_fce_nohit \");\n"
    "        Require(name, \"K7 no-hit line\",\n"
    "                F16kCount(\"DiagF5Ev:\") == lines + 1 && F16kField(line, \"b42\") == \"none\" &&\n"
    "                    F16kField(line, \"fix\") == \"kept_applied\" && F16kField(line, \"why\") == \"<none>\" &&\n"
    "                    F16kField(line, \"applied\") == \"<none>\" && F16kField(line, \"n\") != \"<none>\" &&\n"
    "                    F16kField(line, \"image\") == fmt::format(\"0x{:016x}\", color) &&\n"
    "                    F16kField(line, \"cmask\") == fmt::format(\"0x{:016x}\", meta) &&\n"
    "                    F16kField(line, \"extent\") == \"1024x1024\" && F16kField(line, \"present\") != \"<none>\" &&\n"
    "                    F16kField(line, \"gpu\") != \"<none>\",\n"
    "                \"the no-hit line: \" + line);\n"
    "      } else {\n"
    "        Require(name, \"K7 no line without KYTY_FIX_F5CMU and KYTY_DIAG_F5\", F16kCount(\"DiagF5Ev:\") == lines,\n"
    "                \"a DiagF5Ev line of a decision without a B42 hit: \" + F16kLast(\"DiagF5Ev:\"));\n"
    "      }\n"
    "      F16kOk(\"K7 FCE acquisition without a B42 hit: kept_applied and cmask_fce_nohit / old decision, no line\");\n"
    "      RTA::ResetBindings(executor);\n"
    "      context.UnmapMemory(base, allocation_size);\n"
    "      scheduler.Finish();\n"
    "    }\n"
    "\n"
    "    // ---- D: F26 at the DCC sites and the reasons of branch 2 (item 492(g)(2), (5))\n")

# ---- D18-D20 (RC1-RC3)
sub("      // D17: the refused entry and the buffer size in the KYTY_DIAG_F5ID side of TryConsumeComputeMetaClear\n",
    "      // D18-D20 (Track F, F16k2, ROADMAP s122 item 496(b)(1)-(3)): wr_after=large, cpu_mod by the CPU write epoch since\n"
    "      // the fill, stamp_late. The FCE scan of D11 (slot 1 = `plain`, a DCC address with no entry: R5).\n"
    "      {\n"
    "        constexpr uint64_t dx_large = base + 0xec0000;\n"
    "        constexpr uint64_t dx_cpu = base + 0xed0000;\n"
    "        constexpr uint64_t dx_nofill = base + 0xee0000;\n"
    "        constexpr uint64_t dx_late = base + 0xef0000;\n"
    "        const auto scan2 = [&](uint64_t dcc_address, uint32_t frame) {\n"
    "          registers.SetColorDccAddr(1, {.addr = dcc_address});\n"
    "          GpuTimeProfiler::SetFrame(frame);\n"
    "          RTA::MaterializeColorClears(executor, scheduler.Current());\n"
    "          return F16kLast(\"DiagF5Id: fce \");\n"
    "        };\n"
    "        for (const auto a : {dx_large, dx_cpu, dx_nofill}) {\n"
    "          (void)buffers.ObtainBuffer(a, 0x10000, false, false); // a 64 KB read acquisition uploads (as D0)\n"
    "        }\n"
    "        Require(name, \"D18 CPU-clean ranges\",\n"
    "                !buffers.IsRegionCpuModified(dx_large, 0x1000) && !buffers.IsRegionCpuModified(dx_cpu, 0x1000) &&\n"
    "                    !buffers.IsRegionCpuModified(dx_nofill, 0x1000),\n"
    "                \"a range is still CPU-modified after a read acquisition\");\n"
    "        const auto fce0 = F16kCount(\"DiagF5Id: fce \");\n"
    "        // D18: a GPU write of 16 MB + 1 before the fill is not after it (none); one after the fill - large\n"
    "        BTA::F16kNoteGpuWrite(buffers, base, 0x1000001);\n"
    "        stamp_fill(dx_large, 0x1000, 0);\n"
    "        TTA::F16kEraseMeta(cache, dx_large); // no entry: R5, `since` from the module's stamp\n"
    "        const auto g1 = scan2(dx_large, 6000);\n"
    "        BTA::F16kNoteGpuWrite(buffers, base, 0x1000001); // 16 MB + 1 after the fill\n"
    "        const auto g2 = scan2(dx_large, 6001);\n"
    "        // D19: cpu_mod - no CPU write after the fill: 0; a CPU write after the fill and a read acquisition that uploads\n"
    "        // it (CPU-clean again): 1; no fill stamped at the address: 1\n"
    "        stamp_fill(dx_cpu, 0x1000, 0);\n"
    "        TTA::F16kEraseMeta(cache, dx_cpu);\n"
    "        const auto c1 = scan2(dx_cpu, 6002);\n"
    "        buffers.InvalidateMemory(dx_cpu + 0x10, 4);\n"
    "        (void)buffers.ObtainBuffer(dx_cpu, 0x10000, false, false);\n"
    "        const bool clean_again = !buffers.IsRegionCpuModified(dx_cpu, 0x1000);\n"
    "        const auto c2 = scan2(dx_cpu, 6003);\n"
    "        const auto c3 = scan2(dx_nofill, 6004);\n"
    "        if (id) {\n"
    "          Require(name, \"D18 wr_after=large\",\n"
    "                  F16kField(g1, \"dcc\") == fmt::format(\"0x{:016x}\", dx_large) && F16kField(g1, \"wr_after\") == \"none\" &&\n"
    "                      F16kField(g2, \"dcc\") == fmt::format(\"0x{:016x}\", dx_large) &&\n"
    "                      F16kField(g2, \"wr_after\") == \"large\",\n"
    "                  \"the fce lines: \" + g1 + \" | \" + g2);\n"
    "          F16kOk(\"D18 wr_after=large after a GPU write of 16 MB + 1 (none before the fill)\");\n"
    "          Require(name, \"D19 cpu_mod by the CPU write epoch since the fill\",\n"
    "                  clean_again && F16kField(c1, \"dcc\") == fmt::format(\"0x{:016x}\", dx_cpu) &&\n"
    "                      F16kField(c1, \"cpu_mod\") == \"0\" && F16kField(c2, \"dcc\") == fmt::format(\"0x{:016x}\", dx_cpu) &&\n"
    "                      F16kField(c2, \"cpu_mod\") == \"1\" &&\n"
    "                      F16kField(c3, \"dcc\") == fmt::format(\"0x{:016x}\", dx_nofill) && F16kField(c3, \"cpu_mod\") == \"1\",\n"
    "                  fmt::format(\"clean again {} | {} | {} | {}\", clean_again, c1, c2, c3));\n"
    "          F16kOk(\"D19 cpu_mod: 0 without a CPU write, 1 after a CPU write and its upload, 1 without a fill\");\n"
    "        } else {\n"
    "          Require(name, \"D18-D19 nothing with KYTY_DIAG_F5ID off\", F16kCount(\"DiagF5Id: fce \") == fce0,\n"
    "                  \"an fce line with the knob off\");\n"
    "          F16kOk(\"D18-D19 no fce line with KYTY_DIAG_F5ID off\");\n"
    "        }\n"
    "        // D20: stamp_late - a fill whose dispatch returned before StampPendingDccFill (the end of DispatchDirect calls\n"
    "        // F5IdNoteStampLate): counted once; a stamped fill: not counted; TrackDccFill over a stamp not taken: counted.\n"
    "        cache.StampPendingDccFill();\n"
    "        const auto late0 = DiagF5Id::Count(\"stamp_late\");\n"
    "        cache.TrackDccFill(dx_late, 0x1000, 0);\n"
    "        cache.F5IdNoteStampLate();\n"
    "        cache.F5IdNoteStampLate();\n"
    "        const auto late1 = DiagF5Id::Count(\"stamp_late\") - late0;\n"
    "        cache.TrackDccFill(dx_late + 0x1000, 0x1000, 0); // over the stamp counted above: not again\n"
    "        cache.StampPendingDccFill();\n"
    "        cache.F5IdNoteStampLate();\n"
    "        const auto late2 = DiagF5Id::Count(\"stamp_late\") - late0;\n"
    "        cache.TrackDccFill(dx_late + 0x2000, 0x1000, 0);\n"
    "        cache.TrackDccFill(dx_late + 0x3000, 0x1000, 0); // finds a stamp not taken and not counted\n"
    "        cache.StampPendingDccFill();\n"
    "        const auto late3 = DiagF5Id::Count(\"stamp_late\") - late0;\n"
    "        Require(name, \"D20 stamp_late\", late1 == (id ? 1u : 0u) && late2 == late1 && late3 == (id ? 2u : 0u),\n"
    "                fmt::format(\"late {} {} {}\", late1, late2, late3));\n"
    "        if (id) {\n"
    "          (void)DiagF5Id::ServiceAt(8000, true); // >= 600 frames before the sum line of S3 (frame 9000)\n"
    "          const auto sum = F16kLast(\"DiagF5Id: sum \");\n"
    "          const auto at_late = sum.find(\" stamp_late=\");\n"
    "          Require(name, \"D20 stamp_late in the sum line\",\n"
    "                  F16kField(sum, \"stamp_late\") == std::to_string(late0 + 2) && at_late != std::string::npos &&\n"
    "                      at_late > sum.find(\" overflow_cs=\") && at_late < sum.find(\" marks=\"),\n"
    "                  \"sum: \" + sum);\n"
    "        }\n"
    "        F16kOk(\"D20 stamp_late: once per stamp not taken, the last counter of the sum line\");\n"
    "      }\n"
    "      // D17: the refused entry and the buffer size in the KYTY_DIAG_F5ID side of TryConsumeComputeMetaClear\n")

# ---- Z
sub("                              g(C::F5CmuFallback) == 0),\n",
    "                              g(C::F5CmuFallback) == 0 && g(C::F5CmuExactCpu) == 0),\n")
sub("      Require(name, \"Z identity kept_applied <= kept\", g(C::F5CmuKeptApplied) <= g(C::F5CmuKept), \"kept_applied > kept\");\n",
    "      Require(name, \"Z identity kept_applied <= kept\", g(C::F5CmuKeptApplied) <= g(C::F5CmuKept), \"kept_applied > kept\");\n"
    "      Require(name, \"Z identity exact_cpu <= exact_stale (F16k2)\", g(C::F5CmuExactCpu) <= g(C::F5CmuExactStale),\n"
    "              \"f5cmu_exact_cpu > f5cmu_exact_stale\");\n")

open(P, "wb").write(T.encode("utf-8"))
print("P_TESTS2 OK")
