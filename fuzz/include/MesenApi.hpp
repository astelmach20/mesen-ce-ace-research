#pragma once

#include <cstdint>
#include <cstddef>
#include "Core/Shared/SettingTypes.h"
#include "Core/Shared/CheatManager.h"
#include "Core/Shared/Interfaces/IConsole.h"
#include "Core/Debugger/ITraceLogger.h"

namespace mesen::interop {

extern "C" {
    void InitDll();
    void InitializeEmu(const char* homeFolder, void* windowHandle, void* viewerHandle, bool softwareRenderer, bool noAudio, bool noVideo, bool noInput);
    bool LoadRom(char* filename, char* patchFile);
    bool IsRunning();
    uint32_t GetProgramCounter();
    void Stop();
    void Release();
    int32_t GetStopCode();
    TimingInfo GetTimingInfo(int32_t cpuType);
    void SetEmulationFlag(int32_t flag, bool enabled);
    void SetNesConfig(NesConfig config);
    void SetCheats(CheatCode codes[], uint32_t length);
    bool GetConvertedCheat(CheatCode input, InternalCheatCode& output);

    void InitializeDebugger();
    void Pause();
    void Resume();
    void SetInputOverrides(uint32_t index, DebugControllerState state);
    bool IsDebuggerRunning();
    void GetAvailableInputOverrides(uint8_t* availableIndexes);
    void SetMemoryValue(int32_t type, uint32_t address, uint8_t value);
    void SetMemoryValues(int32_t type, uint32_t address, uint8_t* data, int32_t length);
    uint8_t GetMemoryValue(int32_t type, uint32_t address);
    void GetMemoryValues(int32_t type, uint32_t address, uint8_t* data, int32_t length);
    uint32_t GetMemorySize(int32_t type);
}

} // namespace mesen::interop
