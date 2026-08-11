#pragma once

#include <vector>
#include <cstdint>

namespace mesen::ace {

class Payload6502 {
public:
    Payload6502() = default;

    static Payload6502 create_minimal_2sprite_oam_payload() {
        Payload6502 payload;
        // Sprite #52 ($03D0): Y=169 ($A9), Tile=$03, Attr=$8D, X=112 ($70)
        // Sprite #53 ($03D4): Y=7 ($07), Tile=$60 (RTS), Attr=$EA (NOP), X=$EA (NOP)
        // 6502 Code: LDA #$03; STA $0770; RTS; NOP; NOP
        payload.m_bytes = {
            0xA9, 0x03,        // LDA #$03
            0x8D, 0x70, 0x07,  // STA $0770 (Set OperatingMode to 0x03 = Game Over / Victory)
            0x60,              // RTS (Clean return to Main Engine Loop ExecuteObjects)
            0xEA, 0xEA         // NOP, NOP padding
        };
        return payload;
    }

    static Payload6502 create_game_over_routine() {
        Payload6502 payload;
        payload.m_bytes = {
            0xA9, 0x03,        // LDA #$03
            0x8D, 0x70, 0x07,  // STA $0770 (Set OperatingMode to 0x03 = Game Over)
            0x68,              // PLA
            0x68,              // PLA
            0x4C, 0x82, 0x80   // JMP $8082 (Jump to OperModeExecutionTree)
        };
        return payload;
    }

    const uint8_t* data() const { return m_bytes.data(); }
    size_t size() const { return m_bytes.size(); }
    const std::vector<uint8_t>& bytes() const { return m_bytes; }

private:
    std::vector<uint8_t> m_bytes;
};

} // namespace mesen::ace
