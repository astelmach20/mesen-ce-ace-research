#pragma once

#include <vector>
#include <cstdint>
#include <string>
#include <string_view>
#include <array>

namespace mesen::ace {

class Payload6502 {
public:
    explicit Payload6502(std::vector<uint8_t> bytes, std::string description = "")
        : m_bytes(std::move(bytes)), m_description(std::move(description)) {}

    [[nodiscard]] const std::vector<uint8_t>& bytes() const noexcept { return m_bytes; }
    [[nodiscard]] size_t size() const noexcept { return m_bytes.size(); }
    [[nodiscard]] const uint8_t* data() const noexcept { return m_bytes.data(); }
    [[nodiscard]] std::string_view description() const noexcept { return m_description; }

    /// Build the SMB1 Instant Victory / Game Completion ACE payload (18 bytes):
    /// - Sets OperatingMode = $02 (Victory / Ending sequence)
    /// - Sets WorldEndRoutineTask = $01 (Triggers Princess Cutscene & Credits)
    /// - Asserts diagnostic marker byte ($07FF = $85)
    /// - Jumps directly to SMB1 Victory Dispatch ($E525)
    static Payload6502 create_instant_win_routine() {
        std::vector<uint8_t> bytes = {
            0xA9, 0x02, 0x8D, 0x70, 0x07,  // LDA #$02; STA $0770 (OperatingMode = Victory)
            0xA9, 0x01, 0x8D, 0x1B, 0x07,  // LDA #$01; STA $071B (WorldEndRoutineTask = 1)
            0xA9, 0x85, 0x8D, 0xFF, 0x07,  // LDA #$85; STA $07FF (Marker assertion = $85)
            0x4C, 0x25, 0xE5               // JMP $E525 (SMB1 Victory Dispatch Routine)
        };
        return Payload6502(std::move(bytes), "18-byte 6502 Instant Game Completion & Princess Cutscene Routine");
    }

    /// Build the standard SMB1 60-byte visual ACE payload (rainbow colors & state mutation)
    static Payload6502 create_rainbow_visual_routine() {
        std::vector<uint8_t> bytes = {
            0x2C, 0x02, 0x20,                               // BIT $2002 (Wait for VBLANK)
            0x10, 0xFB,                                     // BPL -5
            0xA9, 0x3F, 0x8D, 0x06, 0x20,                   // STA $2006 (PPU Addr High = $3F)
            0xA9, 0x00, 0x8D, 0x06, 0x20,                   // STA $2006 (PPU Addr Low = $00)
            0xA4, 0x09,                                     // LDY $09 (Frame counter)
            0xA2, 0x20,                                     // LDX #$20 (32 colors)
            0x98, 0x4A, 0x4A, 0x29, 0x0F, 0x18, 0x69, 0x20, // Palette rainbow calculation
            0x8D, 0x07, 0x20,                               // STA $2007 (Write color)
            0xC8, 0xCA, 0xD0, 0xF1,                         // INY / DEX / BNE loop
            0xA9, 0x20, 0x8D, 0x06, 0x20,                   // STA $2006 (Restore PPU Addr High = $20)
            0xA9, 0x00, 0x8D, 0x06, 0x20,                   // STA $2006 (Restore PPU Addr Low = $00)
            0xA9, 0xFF, 0x8D, 0x9F, 0x07,                   // STA $079F (StarInvincibleTimer = 255)
            0xA9, 0x02, 0x8D, 0x56, 0x07,                   // STA $0756 (PlayerStatus = Fire Mario)
            0xA9, 0x85, 0x8D, 0xFF, 0x07,                   // STA $07FF (Marker assertion = $85)
            0x60                                            // RTS
        };
        return Payload6502(std::move(bytes), "60-byte 6502 Rainbow Palette & State ACE Routine");
    }

private:
    std::vector<uint8_t> m_bytes;
    std::string m_description;
};

} // namespace mesen::ace
