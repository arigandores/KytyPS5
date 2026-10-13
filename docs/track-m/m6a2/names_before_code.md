# M6a2 (HPP-854) - names before code (ROADMAP p. 770 (b)-(e))

Fields appended at the END of `M5W2Stat:` (existing order unchanged): `minlod_div_x= clr_dw_div8= ao_obj_unread= inv_part_src=`.
Column appended at the END of `M5W2Clr:`: `clr_dw_div8=`.

- `minlod_div_x` (T021, divergence field of rule 767(k)): created view with min_lod > 0, base_level > 0 and
  min_lod > 256 * max(base_level, level_count - 1); level_count 0 -> 0. `minlod_div` stays (reference).
- `clr_dw_div8` (class (a3) of M5a, reference): accepted colour DWORD fill, R8Unorm (vk 9) with W != (W & 0xff) * 0x01010101,
  R8G8Unorm (vk 16) with (W & 0xffff) != (W >> 16). Not part of `clr_dw_div`.
- `ao_obj_unread` (T125, reference): object port with PCM at a queued push whose grain copy through
  Libs::LibKernel::Memory::TryReadBacking failed; counted in `ao_obj_push`, never in `ao_obj_nz`. At =1 the object grain is
  read only through that copy (no raw read); bus ports keep the raw read (the output path reads them raw already).
- `inv_part_src` (T188, reference): the pairs of `inv_part` (IsGpuModified), coverage tested against SourceRange()
  (address = info.data.address, size = source_size or info.data.size) instead of info.data.
