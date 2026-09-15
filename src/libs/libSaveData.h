#ifndef EMULATOR_INCLUDE_EMULATOR_LIBS_LIBSAVEDATA_H_
#define EMULATOR_INCLUDE_EMULATOR_LIBS_LIBSAVEDATA_H_

namespace Libs::SaveData {

// Gate "savepersist" (KYTY_SAVE_PERSIST): the guest's save-data memory is loaded from
// _SaveData/<title>/sce_sdmemory/memory.bin when the game sets it up and written back, debounced,
// whenever the game changes it.
void Initialize();
// Writes the memory out if it changed and the gate is on. Safe to call at any time.
void FlushMemoryPersist();

struct Lifecycle {
	static constexpr const char* name               = "SaveData";
	static constexpr auto        initialize         = Libs::SaveData::Initialize;
	static constexpr auto        shutdown           = Libs::SaveData::FlushMemoryPersist;
	static constexpr auto        emergency_shutdown = Libs::SaveData::FlushMemoryPersist;
};

} // namespace Libs::SaveData

#endif /* EMULATOR_INCLUDE_EMULATOR_LIBS_LIBSAVEDATA_H_ */
