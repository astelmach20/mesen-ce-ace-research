#pragma once

#include <cstdint>
#include <cstddef>
#include "Core/Shared/MemoryType.h"
#include "MesenApi.hpp"

namespace mesen::nes {

enum class MemoryDomain : int32_t {
    Ram = static_cast<int32_t>(MemoryType::NesMemory),
    InternalRam = static_cast<int32_t>(MemoryType::NesInternalRam),
    PrgRom = static_cast<int32_t>(MemoryType::NesPrgRom),
    PaletteRam = static_cast<int32_t>(MemoryType::NesPaletteRam)
};

namespace addresses {
    constexpr uint16_t PAYLOAD_ENTRY = 0x03D0;
    constexpr uint16_t STAR_INVINCIBLE_TIMER = 0x079F;
    constexpr uint16_t PLAYER_STATUS = 0x0756;
    constexpr uint16_t MARKER = 0x07FF;
    constexpr uint16_t OPERMODE = 0x0770;
    constexpr uint16_t PAUSE_FLAG = 0x0776;
    constexpr uint16_t ENEMY_SLOT_FLAG_BASE = 0x000F;
    constexpr uint16_t ENEMY_SLOT_ID_BASE = 0x0016;

    constexpr uint32_t PRG_SPAWNER_MASK_OFFSET = 0x41F4;
    constexpr uint32_t PRG_GOOMBA_ID_OFFSET = 0x1F05;

    constexpr uint8_t TARGET_ENEMY_ID = 0x85;
    constexpr uint8_t UNMASKED_SPAWNER_VAL = 0xFF;
}

class MemoryAccessor {
public:
    static void write8(MemoryDomain domain, uint32_t address, uint8_t value) {
        interop::SetMemoryValue(static_cast<int32_t>(domain), address, value);
    }

    static void write_bytes(MemoryDomain domain, uint32_t address, const uint8_t* data, size_t length) {
        interop::SetMemoryValues(static_cast<int32_t>(domain), address, const_cast<uint8_t*>(data), static_cast<int32_t>(length));
    }

    [[nodiscard]] static uint8_t read8(MemoryDomain domain, uint32_t address) {
        return interop::GetMemoryValue(static_cast<int32_t>(domain), address);
    }

    static void register_cheat_override(uint16_t address, uint8_t value) {
        CheatCode code{};
        code.Type = CheatType::NesCustom;
        snprintf(code.Code, sizeof(code.Code), "%04X:%02X", address, value);
        interop::SetCheats(&code, 1);
    }
};

} // namespace mesen::nes
