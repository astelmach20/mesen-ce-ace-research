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

    /// Build SMB1 Immediate "GAME OVER" Screen Trigger Payload (15 bytes):
    /// Cleans 6502 stack, sets OperatingMode = $03 (Game Over Mode),
    /// and jumps directly to SMB1 OperModeExecutionTree ($8082) to render "GAME OVER".
    static Payload6502 create_game_over_routine() {
        std::vector<uint8_t> bytes = {
            0xA9, 0x03, 0x8D, 0x70, 0x07,  // LDA #$03; STA $0770 (OperatingMode = $03 Game Over)
            0x68, 0x68,                    // PLA; PLA (Clean 6502 call stack)
            0xA9, 0x85, 0x8D, 0xFF, 0x07,  // LDA #$85; STA $07FF (Marker assertion = $85)
            0x4C, 0x82, 0x80               // JMP $8082 (Jump to SMB1 Main Execution Tree)
        };
        return Payload6502(std::move(bytes), "15-byte 6502 Immediate Game Over Screen Routine");
    }

private:
    std::vector<uint8_t> m_bytes;
    std::string m_description;
};

} // namespace mesen::ace
