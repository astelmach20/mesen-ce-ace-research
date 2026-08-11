#pragma once

#include <filesystem>
#include <fstream>
#include <array>
#include <cstdint>
#include <string_view>
#include <iostream>

#include "Core/NES/NesConsole.h"
#include "Core/NES/BaseNesPpu.h"
#include "Core/Shared/Emulator.h"

extern std::unique_ptr<Emulator> _emu;

namespace mesen::gfx {

struct RGBColor {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};
};

class FrameExporter {
public:
    static constexpr std::array<RGBColor, 64> NES_SYSTEM_PALETTE = {{
        {124,124,124},{0,0,252},{0,0,188},{68,40,188},{148,0,132},{168,0,32},{168,16,0},{136,20,0},
        {80,48,0},{0,120,0},{0,104,0},{0,88,0},{0,64,88},{0,0,0},{0,0,0},{0,0,0},
        {188,188,188},{0,120,248},{0,88,248},{104,68,252},{216,0,204},{228,0,88},{248,56,0},{228,92,16},
        {172,124,0},{0,184,0},{0,168,0},{0,168,68},{0,136,136},{0,0,0},{0,0,0},{0,0,0},
        {248,248,248},{60,188,252},{104,136,252},{152,120,248},{248,120,248},{248,88,152},{248,120,88},{252,160,68},
        {248,184,0},{184,248,24},{88,216,84},{88,248,152},{0,232,216},{120,120,120},{0,0,0},{0,0,0},
        {252,252,252},{164,228,252},{184,184,248},{216,184,248},{248,184,248},{248,164,192},{240,208,176},{252,224,168},
        {248,216,120},{216,248,120},{184,248,184},{184,248,216},{0,252,252},{248,216,248},{0,0,0},{0,0,0}
    }};

    static bool export_ppm(const std::filesystem::path& destination) {
        if (!_emu) return false;
        auto* console = static_cast<NesConsole*>(_emu->GetConsole().get());
        if (!console) return false;
        auto* ppu = console->GetPpu();
        if (!ppu) return false;

        uint16_t* buffer = ppu->GetScreenBuffer(false, false);
        if (!buffer) return false;

        std::ofstream file(destination, std::ios::binary);
        if (!file.is_open()) return false;

        file << "P6\n256 240\n255\n";
        for (size_t i = 0; i < 256 * 240; ++i) {
            uint8_t color_index = buffer[i] & 0x3F;
            const auto& rgb = NES_SYSTEM_PALETTE[color_index];
            file.put(static_cast<char>(rgb.r));
            file.put(static_cast<char>(rgb.g));
            file.put(static_cast<char>(rgb.b));
        }
        return file.good();
    }
};

} // namespace mesen::gfx
