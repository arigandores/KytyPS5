# Track F, F46a (HPP-798, ROADMAP s122 item 702(e)(5)): the test site of the mark M1 by metadata address, the line
# f26_first_exec and KYTY_F26_TINT in tests/ShaderRecompilerComputeTests.cpp (CheckF16k, mode --f16k-only), on top of
# the F16o2 test site. Usage: python p_f46a_tests.py <repo root> [--check]. Anchors are whole lines, each exactly once.
import os
import sys

ROOT = sys.argv[1]
CHECK = '--check' in sys.argv
P = 'tests/ShaderRecompilerComputeTests.cpp'
EDITS = []


def edit(old, new):
    EDITS.append((old, new))


# ---- test access: the marks by address; the test's direct erase also forgets the marks / armed events of the address
edit('''  static void F16kEraseMeta(TextureCache &cache, uint64_t address) {
    std::lock_guard lock(cache.m_lock);
    cache.m_surface_metas.erase(address);
  }
  // Track F, F16o2 (HPP-599): the number of deferred marks (KYTY_FIX_F26).
  static size_t F16o2Marks(TextureCache &cache) {
    std::lock_guard lock(cache.m_lock);
    return cache.m_f26_deferred.size();
  }
''', '''  static void F16kEraseMeta(TextureCache &cache, uint64_t address) {
    std::lock_guard lock(cache.m_lock);
    cache.m_surface_metas.erase(address);
    // Track F, F46a (HPP-798): the test's direct erase (a scenario boundary, not an emulator path) also forgets the mark
    // M1 and the armed f26_first_exec events of the address, without a line.
    if (cache.m_f26_marks.erase(address) != 0) {
      cache.m_f26_marks_count.fetch_sub(1, std::memory_order_relaxed);
    }
    if (const auto found = cache.m_f26_first.find(address); found != cache.m_f26_first.end()) {
      cache.m_f26_first_count.fetch_sub(static_cast<uint32_t>(found->second.size()), std::memory_order_relaxed);
      cache.m_f26_first.erase(found);
    }
  }
  // Track F, F16o2 (HPP-599): the number of deferred marks (KYTY_FIX_F26); Track F, F46a: keyed by metadata address.
  static size_t F16o2Marks(TextureCache &cache) {
    std::lock_guard lock(cache.m_lock);
    return cache.m_f26_marks.size();
  }
''')

# ---- the tint knobs as the code reads them
edit('''    const bool ring = cmu || id || f26;
''', '''    const bool ring = cmu || id || f26;
    // Track F, F46a (item 702(e)(4)): KYTY_F26_TINT / KYTY_F26_TINT_DCC as the code reads them ("1" / "2"; a hex key).
    const char *tint_env = std::getenv("KYTY_F26_TINT");
    const uint32_t tint_mode = tint_env == nullptr                 ? 0u
                               : std::string(tint_env) == "1" ? 1u
                               : std::string(tint_env) == "2" ? 2u
                                                              : 0u;
    const char *tint_key_env = std::getenv("KYTY_F26_TINT_DCC");
    const uint64_t tint_key = tint_key_env == nullptr ? 0u : std::strtoull(tint_key_env, nullptr, 16);
''')
edit('''                f5 ? 1 : 0, cmu ? 1 : 0, knob ? 1 : 0, id ? 1 : 0, f26 ? 1 : 0, ring ? 1 : 0);
''', '''                f5 ? 1 : 0, cmu ? 1 : 0, knob ? 1 : 0, id ? 1 : 0, f26 ? 1 : 0, ring ? 1 : 0);
    std::printf("[f16k]    F46a knobs: KYTY_F26_TINT=%u KYTY_F26_TINT_DCC=0x%016llx\\n", tint_mode,
                static_cast<unsigned long long>(tint_key));
''')

# ---- the mode line F26Tint
edit('''      F16kOk("F16o mode line FixF26");
''', '''      F16kOk("F16o mode line FixF26");
      // Track F, F46a (item 702(e)(4)): "F26Tint: mode=<m> dcc=0x<key>" once when KYTY_F26_TINT is 1 or 2.
      const bool t1 = DiagF5::LogF26TintMode();
      const bool t2 = DiagF5::LogF26TintMode();
      const auto tline = fmt::format("F26Tint: mode={} dcc=0x{:016x}", tint_mode, tint_key);
      Require(name, "F46a mode line F26Tint",
              DiagF5::F26TintMode() == tint_mode && DiagF5::F26TintDcc() == tint_key && t1 == (tint_mode != 0) && !t2 &&
                  F16kCount("F26Tint:") == (tint_mode != 0 ? 1u : 0u) &&
                  F16kExact(tline.c_str()) == (tint_mode != 0 ? 1u : 0u),
              "F26Tint: is missing, repeated, printed with its knob off, or the knob read differs");
      F16kOk("F46a mode line F26Tint");
''')

# ---- the names: two more rows after f26_deferred_declined
edit('''                  static_cast<uint32_t>(C::F26Fallback) + 2 == static_cast<uint32_t>(C::Count) && // F16o2: +1 row
''', '''                  static_cast<uint32_t>(C::F26Fallback) + 4 == static_cast<uint32_t>(C::Count) && // F16o2 +1, F46a +2
''')
edit('''                  static_cast<uint32_t>(C::F26DeferredDeclined) + 1 == static_cast<uint32_t>(C::Count),
''', '''                  static_cast<uint32_t>(C::F26DeferredDeclined) + 3 == static_cast<uint32_t>(C::Count), // F46a: +2 rows
''')

# ---- the dcc_stale_apply line form: the result enum and the site field (Track F, F46a)
edit('''      const auto da1 = DiagF5::FormatDccStaleApply({.n = 4, .present = 7, .gpu = 9, .image = 0x10, .dcc = 0x20,
                                                     .cleared = true, .layers = 1});
      const auto da2 = DiagF5::FormatDccStaleApply({.n = 5, .present = 1, .gpu = 2, .image = 0x10, .dcc = 0x20,
                                                     .cleared = false, .layers = 0});
''', '''      // Track F, F46a (item 702(e)(2)): `result` is an enum, the line ends with site=.
      const auto da1 = DiagF5::FormatDccStaleApply({.n = 4, .present = 7, .gpu = 9, .image = 0x10, .dcc = 0x20,
                                                     .result = DiagF5::DccApplyResult::Cleared, .layers = 1});
      const auto da2 = DiagF5::FormatDccStaleApply({.n = 5, .present = 1, .gpu = 2, .image = 0x10, .dcc = 0x20,
                                                     .result = DiagF5::DccApplyResult::Declined, .layers = 0,
                                                     .site = DiagF5::F26Site::Mat});
''')
edit('''                     "result=cleared layers=0x00000001" &&
''', '''                     "result=cleared layers=0x00000001 site=prepare" &&
''')
edit('''                         "dcc=0x0000000000000020 result=declined layers=0x00000000" &&
''', '''                         "dcc=0x0000000000000020 result=declined layers=0x00000000 site=mat" &&
''')

# ---- the F46a pure helpers
edit('''      F16kOk("F16o2 pure helpers (why=deferred, f26_deferred_declined last, dcc_stale_apply line form)");
    }
''', '''      F16kOk("F16o2 pure helpers (why=deferred, f26_deferred_declined last, dcc_stale_apply line form)");
      // Track F, F46a (item 702(e)(2)-(4)): the names (the tint counters are the last rows), the results and sites of
      // dcc_stale_apply, the line f26_first_exec and the pure tint decision F26TintAt (the m2 mutant - the key ignored -
      // tints "another address").
      {
        using R = DiagF5::DccApplyResult;
        using S = DiagF5::F26Site;
        Require(name, "F46a names",
                std::string(DiagF5::Name(C::F26TintApplied)) == "f26_tint_applied" &&
                    std::string(DiagF5::Name(C::F26TintSkip)) == "f26_tint_skip" &&
                    static_cast<uint32_t>(C::F26TintApplied) == static_cast<uint32_t>(C::F26DeferredDeclined) + 1 &&
                    static_cast<uint32_t>(C::F26TintSkip) + 1 == static_cast<uint32_t>(C::Count) &&
                    std::string(DiagF5::DccApplyResultName(R::Cleared)) == "cleared" &&
                    std::string(DiagF5::DccApplyResultName(R::Declined)) == "declined" &&
                    std::string(DiagF5::DccApplyResultName(R::Dropped)) == "dropped" &&
                    std::string(DiagF5::F26SiteName(S::Prepare)) == "prepare" &&
                    std::string(DiagF5::F26SiteName(S::Mat)) == "mat" &&
                    std::string(DiagF5::F26SiteName(S::Fill)) == "fill" &&
                    std::string(DiagF5::F26SiteName(S::Unmap)) == "unmap" &&
                    std::string(DiagF5::F26SiteName(S::Delete)) == "delete" &&
                    std::string(DiagF5::F26SiteName(S::Retype)) == "retype" &&
                    std::string(DiagF5::F26SiteName(S::Remark)) == "remark",
                "a name of F46a");
        const auto dd = DiagF5::FormatDccStaleApply({.n = 6, .present = 3, .gpu = 4, .image = 0x10, .dcc = 0x20,
                                                     .result = R::Dropped, .layers = 0xffffffffu, .site = S::Unmap});
        const auto fe = DiagF5::FormatFirstExec({.n = 7, .present = 8, .dcc = 0x20, .image = 0x30, .site = S::Mat});
        Require(name, "F46a line forms",
                dd == "DiagF5Ev: dcc_stale_apply n=6 present=3 gpu=4 image=0x0000000000000010 dcc=0x0000000000000020 "
                      "result=dropped layers=0xffffffff site=unmap" &&
                    fe == "DiagF5Ev: f26_first_exec n=7 present=8 dcc=0x0000000000000020 image=0x0000000000000030 "
                          "site=mat",
                "the F46a lines: " + dd + " | " + fe);
        using TR = DiagF5::TintResult;
        const std::array<float, 4> seed{0.25f, 0.5f, 0.75f, 0.125f};
        struct TCase {
          const char *what;
          uint32_t mode;
          uint64_t address;
          bool removes;
          vk::Format format;
          TR result;
        };
        constexpr uint64_t tk = 0x571006000ull;
        const TCase tcases[] = {
            {"mode 0", 0, tk, true, vk::Format::eA2B10G10R10UnormPack32, TR::None},
            {"mode 3", 3, tk, true, vk::Format::eA2B10G10R10UnormPack32, TR::None},
            {"mode 2, the key, rgb10a2", 2, tk, false, vk::Format::eA2B10G10R10UnormPack32, TR::Applied},
            {"mode 2, another address", 2, tk + 0x1000, false, vk::Format::eA2B10G10R10UnormPack32, TR::None},
            {"mode 2, the key, rgba16f", 2, tk, false, vk::Format::eR16G16B16A16Sfloat, TR::Applied},
            {"mode 2, the key, b10g11r11", 2, tk, false, vk::Format::eB10G11R11UfloatPack32, TR::Applied},
            {"mode 2, the key, bgra8 srgb", 2, tk, false, vk::Format::eB8G8R8A8Srgb, TR::Applied},
            {"mode 2, the key, r8: no encoding", 2, tk, false, vk::Format::eR8Unorm, TR::Skip},
            {"mode 2, the key, rg16: no encoding", 2, tk, false, vk::Format::eR16G16Unorm, TR::Skip},
            {"mode 2, the key, rgba32 uint: no encoding", 2, tk, false, vk::Format::eR32G32B32A32Uint, TR::Skip},
            {"mode 1, the key, no mark", 1, tk, false, vk::Format::eA2B10G10R10UnormPack32, TR::None},
            {"mode 1, the key, a mark", 1, tk, true, vk::Format::eA2B10G10R10UnormPack32, TR::Applied},
            {"mode 1, another address, a mark", 1, tk + 0x1000, true, vk::Format::eA2B10G10R10UnormPack32, TR::None},
        };
        for (const auto &t : tcases) {
          vk::ClearColorValue c{};
          c.float32 = seed;
          const auto result = DiagF5::F26TintAt(t.mode, tk, t.address, t.removes, t.format, c);
          const bool magenta = c.float32[0] == 1.0f && c.float32[1] == 0.0f && c.float32[2] == 1.0f && c.float32[3] == 1.0f;
          const bool same = c.float32[0] == seed[0] && c.float32[1] == seed[1] && c.float32[2] == seed[2] &&
                            c.float32[3] == seed[3];
          Require(name, "F46a F26TintAt", result == t.result && (t.result == TR::Applied ? magenta : same),
                  fmt::format("{}: result {} magenta {} unchanged {}", t.what, static_cast<int>(result), magenta, same));
        }
        F16kOk("F46a pure helpers (names, dcc_stale_apply dropped / site, f26_first_exec line, F26TintAt)");
      }
    }
''')

# ---- D4: a declined mark stays; the cleared adoption is the first execution after its event; site=mat
edit('''            Require(name, a.stage, TTA::F16o2Marks(cache) == 0, "the deferred mark was not taken");
            if (marked) {
              const auto line = F16kLast("DiagF5Ev: dcc_stale_apply ");
              Require(name, a.stage,
                      F16kCount("DiagF5Ev:") == mlines + 1 && F16kField(line, "n") == adopt_n &&
''', '''            // Track F, F46a (item 702(e)(2)-(3)): a declined mark stays (a later clear of the address takes it); the
            // cleared adoption is the first execution after its event (KYTY_DIAG_F5ID, f26_first_exec site=mat).
            Require(name, a.stage, TTA::F16o2Marks(cache) == (marked && !cleared ? 1u : 0u),
                    "the mark after the materialization (taken when cleared, kept when declined)");
            const size_t first = id && kept && cleared ? 1 : 0;
            if (first != 0) {
              const auto fline = F16kLast("DiagF5Ev: f26_first_exec ");
              Require(name, a.stage,
                      F16kField(fline, "n") == adopt_n && F16kField(fline, "site") == "mat" &&
                          F16kField(fline, "image") == fmt::format("0x{:016x}", plain) &&
                          F16kField(fline, "dcc") == fmt::format("0x{:016x}", pending),
                      "the f26_first_exec line: " + fline);
            }
            if (marked) {
              const auto line = F16kLast("DiagF5Ev: dcc_stale_apply ");
              Require(name, a.stage,
                      F16kCount("DiagF5Ev:") == mlines + 1 + first && F16kField(line, "n") == adopt_n &&
                          F16kField(line, "site") == "mat" &&
''')
edit('''              Require(name, a.stage, F16kCount("DiagF5Ev:") == mlines, "a dcc_stale_apply line without a mark");
''', '''              Require(name, a.stage, F16kCount("DiagF5Ev:") == mlines + first, "a dcc_stale_apply line without a mark");
''')

# ---- the F46a site block after the D4 loop
edit('''          F16kOk(a.stage);
        }
        m = {};
        check("D5 R1 no image", !cache.FindDccSurfaceImage(base + 0x1800000, base + 0x1c00000, &m) && m.why == M::R1,
''', '''          F16kOk(a.stage);
        }
        // ---- F46a (Track F, HPP-798, ROADMAP s122 item 702(e)(2)-(5)): the mark M1 by metadata address, the line
        // f26_first_exec and KYTY_F26_TINT at the sites (the D4 cases above check adoption + MaterializeDeferredDccClear,
        // site=mat). T1 alias: an adoption of `pending` by the plain image leaves the mark (=1 with KYTY_DIAG_F5); ANOTHER
        // image - the DCC target `did` through a descriptor with its metadata at `pending` - executes the fill and removes
        // it (result=cleared, image = the target; the m1 mutant - a mark by ImageId - keeps it). T2: a new fill and the
        // target's clear - the first execution after the adoption's event at =0 (the event dropped the fill). T3: a mark
        // dropped by a new fill (site=fill) and by UnmapMemory (site=unmap). T4: a prepare event - kept_applied at =1
        // (its in-call clear) / the fill dropped at =0 - prints no f26_first_exec on the event itself (the m3 mutant);
        // the next clear after a new fill prints it. T5: a prepare event kept why=decode (code 0x20 without a valid
        // register word) leaves the mark at `dcc`; MaterializeDeferredDccClear of the target executes it (site=mat).
        // KYTY_F26_TINT: each call's f26_tint_applied delta follows the arm's mode / key (the m2 mutant - the key ignored -
        // tints the executions at `pending` in the arms keyed by `dcc` and back).
        {
          const bool k5 = f26 && f5;
          auto &dimage = TTA::F16dImage(cache, did);
          const auto dmeta0 = dimage.info.metadata;
          auto alias = desc;
          alias.info.metadata.range.address = pending;
          const auto hex = [](uint64_t value) { return fmt::format("0x{:016x}", value); };
          // The expected f26_tint_applied of one call: `exec` - it executes the fill at `address`; `removes` - it removes
          // an F26 mark of the address (mode 1).
          const auto tint = [&](uint64_t address, bool exec, bool removes) -> uint64_t {
            return exec && tint_mode != 0 && address == tint_key && (tint_mode == 2 || removes) ? 1u : 0u;
          };
          const auto event_n = [&]() {
            return f5 ? F16kField(F16kLast("DiagF5Ev: dcc_stale "), "n") : std::string("-");
          };
          const auto adopt = [&](const char *stage) {
            stamp_fill(pending, msize, 0x40404040u);
            BTA::F16kNoteGpuWrite(buffers, pending + msize, 0x100);
            m = {};
            const bool adopted = cache.AdoptPendingDccForTexture(pid, pending, &m);
            Require(name, stage, adopted == f26 && TTA::F16o2Marks(cache) == (k5 ? 1u : 0u),
                    fmt::format("adopted {} marks {} (expected {} {})", adopted, TTA::F16o2Marks(cache), f26,
                                k5 ? 1 : 0));
            return event_n();
          };
          const auto first_line = [&](const char *stage, const std::string &n, uint64_t dcc_address, uint64_t image,
                                      const char *site) {
            const auto line = F16kLast("DiagF5Ev: f26_first_exec ");
            Require(name, stage,
                    F16kField(line, "n") == n && F16kField(line, "dcc") == hex(dcc_address) &&
                        F16kField(line, "image") == hex(image) && F16kField(line, "site") == site &&
                        F16kField(line, "present") != "<none>",
                    "the f26_first_exec line: " + line);
            std::printf("[f16k]      %s\\n", line.c_str());
          };
          const auto apply_line = [&](const char *stage, const std::string &n, const char *result, uint64_t dcc_address,
                                      uint64_t image, const char *layers, const char *site) {
            const auto line = F16kLast("DiagF5Ev: dcc_stale_apply ");
            Require(name, stage,
                    F16kField(line, "n") == n && F16kField(line, "result") == result &&
                        F16kField(line, "dcc") == hex(dcc_address) && F16kField(line, "image") == hex(image) &&
                        F16kField(line, "layers") == layers && F16kField(line, "site") == site &&
                        F16kField(line, "present") != "<none>" && F16kField(line, "gpu") != "<none>",
                    "the dcc_stale_apply line: " + line);
            std::printf("[f16k]      %s\\n", line.c_str());
          };
          // T1
          const char *t1 = "F46a T1 alias: the mark of `pending` removed by another image's clear";
          const auto n1 = adopt(t1);
          {
            const auto lines = F16kCount("DiagF5Ev:");
            const auto before = F16kRead();
            TTA::F16dPrepareDccClear(cache, did, alias);
            const auto after = cache.QueryMetaFill(pending, did);
            const size_t first = id && f26 ? 1 : 0;
            F16kDelta(t1, before,
                      {{C::F26KeptApplied, k5 ? 1u : 0u},
                       {C::F26DeferredDeclined, 0},
                       {C::F26TintApplied, tint(pending, f26, k5)},
                       {C::F26TintSkip, 0}});
            Require(name, t1,
                    TTA::F16o2Marks(cache) == 0 && F16kCount("DiagF5Ev:") == lines + (k5 ? 1 : 0) + first &&
                        after.found &&
                        (f26 ? (after.clear_mask & 1u) == 0 && after.fill_value == 0x40404040u : after.clear_mask == 0),
                    fmt::format("marks {} lines +{} (expected +{}) mask 0x{:x} fill 0x{:x}", TTA::F16o2Marks(cache),
                                F16kCount("DiagF5Ev:") - lines, (k5 ? 1 : 0) + first, after.clear_mask,
                                after.fill_value));
            if (k5) {
              apply_line(t1, n1, "cleared", pending, color, "0x00000001", "prepare");
            }
            if (first != 0) {
              first_line(t1, n1, pending, color, "prepare");
            }
            F16kOk(t1);
          }
          // T2
          {
            const char *t2 = "F46a T2 a new fill, the next clear: the first execution after the event at =0";
            const auto lines = F16kCount("DiagF5Ev:");
            const auto before = F16kRead();
            cache.TrackDccFill(pending, msize, 0x40404040u);
            cache.StampPendingDccFill();
            TTA::F16dPrepareDccClear(cache, did, alias);
            const auto after = cache.QueryMetaFill(pending, did);
            const size_t first = id && !f26 ? 1 : 0;
            F16kDelta(t2, before,
                      {{C::F26KeptApplied, 0}, {C::F26TintApplied, tint(pending, true, false)}, {C::F26TintSkip, 0}});
            Require(name, t2, F16kCount("DiagF5Ev:") == lines + first && after.found && (after.clear_mask & 1u) == 0,
                    fmt::format("lines +{} (expected +{}) found {} mask 0x{:x}", F16kCount("DiagF5Ev:") - lines, first,
                                after.found, after.clear_mask));
            if (first != 0) {
              first_line(t2, n1, pending, color, "prepare");
            }
            F16kOk(t2);
          }
          // T3
          {
            const char *t3 = "F46a T3 a mark dropped by a new fill (site=fill) and by UnmapMemory (site=unmap)";
            dimage.info.metadata = dmeta0;
            pimage0.info.metadata = pmeta0;
            TTA::F16kEraseMeta(cache, pending);
            const auto n3 = adopt(t3);
            auto lines = F16kCount("DiagF5Ev:");
            cache.TrackDccFill(pending, msize, 0x40404040u);
            cache.StampPendingDccFill();
            Require(name, t3, TTA::F16o2Marks(cache) == 0 && F16kCount("DiagF5Ev:") == lines + (k5 ? 1 : 0),
                    fmt::format("fill: marks {} lines +{}", TTA::F16o2Marks(cache), F16kCount("DiagF5Ev:") - lines));
            if (k5) {
              apply_line(t3, n3, "dropped", pending, plain, "0xffffffff", "fill");
            }
            pimage0.info.metadata = pmeta0;
            TTA::F16kEraseMeta(cache, pending);
            const auto n3b = adopt(t3);
            lines = F16kCount("DiagF5Ev:");
            cache.UnmapMemory(pending, msize);
            Require(name, t3,
                    TTA::F16o2Marks(cache) == 0 && F16kCount("DiagF5Ev:") == lines + (k5 ? 1 : 0) &&
                        !cache.QueryMetaFill(pending, pid).found,
                    fmt::format("unmap: marks {} lines +{}", TTA::F16o2Marks(cache), F16kCount("DiagF5Ev:") - lines));
            if (k5) {
              apply_line(t3, n3b, "dropped", pending, plain, "0xffffffff", "unmap");
            }
            pimage0.info.metadata = pmeta0;
            TTA::F16kEraseMeta(cache, pending);
            F16kOk(t3);
          }
          // T4
          {
            const char *t4 = "F46a T4 a prepare event: no f26_first_exec on the event itself, one at the next clear";
            const auto lines = F16kCount("DiagF5Ev:");
            const auto firsts = F16kCount("DiagF5Ev: f26_first_exec ");
            auto before = F16kRead();
            stamp_fill(dcc, msize, 0);
            BTA::F16kNoteGpuWrite(buffers, dcc + msize, 0x100);
            TTA::F16dPrepareDccClear(cache, did, desc);
            const auto n4 = event_n();
            F16kDelta(t4, before,
                      {{C::F26KeptApplied, k5 ? 1u : 0u},
                       {C::F26TintApplied, tint(dcc, f26, true)},
                       {C::F26TintSkip, 0}});
            Require(name, t4,
                    F16kCount("DiagF5Ev:") == lines + (f5 ? 1 : 0) &&
                        F16kCount("DiagF5Ev: f26_first_exec ") == firsts && TTA::F16o2Marks(cache) == 0 &&
                        (!f5 || F16kField(F16kLast("DiagF5Ev: dcc_stale "), "fix") == (f26 ? "kept_applied" : "off")),
                    "an f26_first_exec line on the event itself, a mark of kept_applied, or not the expected event: " +
                        F16kLast("DiagF5Ev:"));
            const auto lines2 = F16kCount("DiagF5Ev:");
            before = F16kRead();
            cache.TrackDccFill(dcc, msize, 0);
            cache.StampPendingDccFill();
            TTA::F16dPrepareDccClear(cache, did, desc);
            const size_t first = id ? 1 : 0;
            F16kDelta(t4, before,
                      {{C::F26KeptApplied, 0}, {C::F26TintApplied, tint(dcc, true, false)}, {C::F26TintSkip, 0}});
            Require(name, t4, F16kCount("DiagF5Ev:") == lines2 + first,
                    fmt::format("next clear: lines +{} (expected +{})", F16kCount("DiagF5Ev:") - lines2, first));
            if (first != 0) {
              first_line(t4, n4, dcc, color, "prepare");
            }
            F16kOk(t4);
          }
          // T5
          {
            const char *t5 = "F46a T5 prepare kept why=decode: the mark of `dcc`, executed by MaterializeDeferredDccClear";
            auto no_register = desc;
            no_register.info.metadata.dcc_clear_register_valid = false;
            const auto lines = F16kCount("DiagF5Ev:");
            auto before = F16kRead();
            stamp_fill(dcc, msize, 0x20202020u);
            BTA::F16kNoteGpuWrite(buffers, dcc + msize, 0x100);
            TTA::F16dPrepareDccClear(cache, did, no_register);
            const auto n5 = event_n();
            F16kDelta(t5, before, {{C::F26KeptApplied, 0}, {C::F26TintApplied, 0}, {C::F26TintSkip, 0}});
            Require(name, t5,
                    TTA::F16o2Marks(cache) == (k5 ? 1u : 0u) && F16kCount("DiagF5Ev:") == lines + (f5 ? 1 : 0) &&
                        (!f5 || (F16kField(F16kLast("DiagF5Ev: dcc_stale "), "fix") == (f26 ? "kept" : "off") &&
                                 F16kField(F16kLast("DiagF5Ev: dcc_stale "), "why") == (f26 ? "decode" : "<none>"))),
                    fmt::format("marks {}: ", TTA::F16o2Marks(cache)) + F16kLast("DiagF5Ev:"));
            const auto lines2 = F16kCount("DiagF5Ev:");
            before = F16kRead();
            RTA::F16dMaterialize(executor, scheduler.Current(), did);
            const size_t first = id && f26 ? 1 : 0;
            F16kDelta(t5, before,
                      {{C::F26KeptApplied, k5 ? 1u : 0u},
                       {C::F26DeferredDeclined, 0},
                       {C::DccMatCleared, f5 && f26 ? 1u : 0u},
                       {C::F26TintApplied, tint(dcc, f26, k5)},
                       {C::F26TintSkip, 0}});
            Require(name, t5, TTA::F16o2Marks(cache) == 0 && F16kCount("DiagF5Ev:") == lines2 + (k5 ? 1 : 0) + first,
                    fmt::format("materialize: marks {} lines +{} (expected +{})", TTA::F16o2Marks(cache),
                                F16kCount("DiagF5Ev:") - lines2, (k5 ? 1 : 0) + first));
            if (k5) {
              apply_line(t5, n5, "cleared", dcc, color, "0x00000001", "mat");
            }
            if (first != 0) {
              first_line(t5, n5, dcc, color, "mat");
            }
            F16kOk(t5);
          }
          dimage.info.metadata = dmeta0;
          pimage0.info.metadata = pmeta0;
          TTA::F16kEraseMeta(cache, pending);
        }
        m = {};
        check("D5 R1 no image", !cache.FindDccSurfaceImage(base + 0x1800000, base + 0x1c00000, &m) && m.why == M::R1,
''')

# ---- Z: the identities with the F46a events
edit('''      // Track F, F16o2 (item 507(b)(4)): f26_kept_applied + f26_deferred_declined <= f26_kept.
      Require(name, "Z identity f26_kept_applied + f26_deferred_declined <= f26_kept",
              g(C::F26KeptApplied) + g(C::F26DeferredDeclined) <= g(C::F26Kept),
              "f26_kept_applied + f26_deferred_declined > f26_kept");
''', '''      // Track F, F16o2 (item 507(b)(4)) and Track F, F46a (item 702(e)(2)): a declined mark stays and a later clear of the
      // address may take it - f26_kept_applied <= f26_kept and f26_deferred_declined <= f26_kept (the sum may exceed).
      Require(name, "Z identity f26_kept_applied <= f26_kept, f26_deferred_declined <= f26_kept",
              g(C::F26KeptApplied) <= g(C::F26Kept) && g(C::F26DeferredDeclined) <= g(C::F26Kept),
              "f26_kept_applied > f26_kept or f26_deferred_declined > f26_kept");
      // Track F, F46a (item 702(e)(4)): the tint counters only with KYTY_F26_TINT; the site's formats all have the
      // encoding (no skip).
      Require(name, "Z f26_tint_* only with KYTY_F26_TINT",
              (tint_mode != 0 || (g(C::F26TintApplied) == 0 && F16kCount("F26Tint:") == 0)) && g(C::F26TintSkip) == 0,
              fmt::format("f26_tint_applied {} f26_tint_skip {} F26Tint lines {}", g(C::F26TintApplied),
                          g(C::F26TintSkip), F16kCount("F26Tint:")));
''')
edit('''        uint64_t cleared = 0, declined = 0;
        for (const auto &line : DiagF5::RecentLines()) {
          if (line.rfind("DiagF5Ev: dcc_stale_apply ", 0) == 0) {
            const auto result = F16kField(line, "result");
            cleared += result == "cleared" ? 1 : 0;
            declined += result == "declined" ? 1 : 0;
            continue;
          }
''', '''        uint64_t cleared = 0, declined = 0, dropped = 0;
        for (const auto &line : DiagF5::RecentLines()) {
          if (line.rfind("DiagF5Ev: dcc_stale_apply ", 0) == 0) {
            const auto result = F16kField(line, "result");
            cleared += result == "cleared" ? 1 : 0;
            declined += result == "declined" ? 1 : 0;
            dropped += result == "dropped" ? 1 : 0; // Track F, F46a
            continue;
          }
''')
edit('''        Require(name, "Z print identity dcc_stale lines by fix, dcc_stale_apply lines by result = f26_*",
                !f5 ? all == 0 && cleared == 0 && declined == 0
                : f26 ? all == 9 && off == 0 && kept == g(C::F26Kept) &&
                            kept_applied + cleared == g(C::F26KeptApplied) &&
                            declined == g(C::F26DeferredDeclined) && adopt_applied == 0 && cleared == 1 &&
                            declined == 1 && exact_stale == g(C::F26ExactStale) && fallback == g(C::F26Fallback)
                      : all == 9 && off == all && cleared == 0 && declined == 0,
                fmt::format("lines {} off {} kept {} kept_applied {} (adopt {}) exact_stale {} fallback {} cleared {} "
                            "declined {}",
                            all, off, kept, kept_applied, adopt_applied, exact_stale, fallback, cleared, declined));
''', '''        // Track F, F46a: the F46a block adds 5 events (T1, T3 x 2, T4, T5), 2 cleared (T1, T5), 2 dropped (T3).
        Require(name, "Z print identity dcc_stale lines by fix, dcc_stale_apply lines by result = f26_*",
                !f5 ? all == 0 && cleared == 0 && declined == 0 && dropped == 0
                : f26 ? all == 14 && off == 0 && kept == g(C::F26Kept) &&
                            kept_applied + cleared == g(C::F26KeptApplied) &&
                            declined == g(C::F26DeferredDeclined) && adopt_applied == 0 && cleared == 3 &&
                            declined == 1 && dropped == 2 && exact_stale == g(C::F26ExactStale) &&
                            fallback == g(C::F26Fallback)
                      : all == 14 && off == all && cleared == 0 && declined == 0 && dropped == 0,
                fmt::format("lines {} off {} kept {} kept_applied {} (adopt {}) exact_stale {} fallback {} cleared {} "
                            "declined {} dropped {}",
                            all, off, kept, kept_applied, adopt_applied, exact_stale, fallback, cleared, declined,
                            dropped));
        // Track F, F46a (item 702(e)(3)): f26_first_exec only with KYTY_DIAG_F5ID - at =1 D4, T1, T4, T5; at =0 T2, T4.
        const auto firsts = F16kCount("DiagF5Ev: f26_first_exec ");
        Require(name, "Z f26_first_exec lines", firsts == (!id ? 0u : f26 ? 4u : 2u),
                fmt::format("f26_first_exec lines {} (expected {})", firsts, !id ? 0 : f26 ? 4 : 2));
''')


def main():
    full = os.path.join(ROOT, P)
    raw = open(full, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    for old, new in EDITS:
        n = text.count(old)
        if n != 1:
            print('ANCHOR count %d: %r' % (n, old[:120]))
            sys.exit(3)
        text = text.replace(old, new)
    if crlf:
        text = text.replace('\n', '\r\n')
    if CHECK:
        print('CHECK OK tests', len(EDITS), 'edits')
        return
    open(full, 'wb').write(text.encode('utf-8'))
    print('PATCHED tests', len(EDITS), 'edits')


if __name__ == '__main__':
    main()
