#!/usr/bin/env python3
"""
PPU OAM Shadow Buffer ($0300-$03FF) 6502 Instruction Mapping Analyzer
Analyzes how NES sprite attributes (Y, Tile ID, Attributes, X) map to 6502 machine code.
"""

def disassemble_6502_bytes(bytes_data, base_addr=0x03D0):
    opcodes = {
        0x00: ("BRK", 1),
        0x18: ("CLC", 1),
        0x20: ("JSR $abs", 3),
        0x38: ("SEC", 1),
        0x4C: ("JMP $abs", 3),
        0x60: ("RTS", 1),
        0x85: ("STA $zp", 2),
        0x8D: ("STA $abs", 3),
        0xA0: ("LDY #$imm", 2),
        0xA2: ("LDX #$imm", 2),
        0xA9: ("LDA #$imm", 2),
        0xAD: ("LDA $abs", 3),
        0xEA: ("NOP", 1),
    }

    pc = base_addr
    idx = 0
    instructions = []

    while idx < len(bytes_data):
        op = bytes_data[idx]
        if op in opcodes:
            name, size = opcodes[op]
            if idx + size <= len(bytes_data):
                operands = bytes_data[idx+1:idx+size]
                if size == 1:
                    inst_str = f"{name}"
                elif size == 2:
                    inst_str = f"{name.replace('$imm', f'${operands[0]:02X}').replace('$zp', f'${operands[0]:02X}')}"
                elif size == 3:
                    target = operands[0] | (operands[1] << 8)
                    inst_str = f"{name.replace('$abs', f'${target:04X}')}"
                instructions.append((pc, f"${op:02X} " + " ".join(f"${b:02X}" for b in operands), inst_str))
                idx += size
                pc += size
                continue
        
        # Default single-byte mapping
        instructions.append((pc, f"${op:02X}", f"DB ${op:02X}"))
        idx += 1
        pc += 1

    return instructions

def analyze_sprite_payload():
    print("=========================================================================")
    print("  PPU OAM SPRITE BUFFER ($03D0) 6502 PAYLOAD SHAPING DEMONSTRATION")
    print("=========================================================================")
    
    # Sprite 52 ($03D0): Y=A9 (169px), Tile=03, Attr=8D, X=70
    # Sprite 53 ($03D4): Y=07, Tile=60 (96px), Attr=EA, X=EA
    oam_bytes = bytes([
        0xA9, 0x03, 0x8D, 0x70,  # Sprite 52 @ $03D0: LDA #$03; STA $0770 (Part 1)
        0x07, 0x60, 0xEA, 0xEA   # Sprite 53 @ $03D4: ...STA $0770 (Part 2); RTS; NOP; NOP
    ])
    
    print("\nPPU OAM Buffer Memory State ($03D0-$03D7):")
    for i in range(0, len(oam_bytes), 4):
        sprite_num = 52 + (i // 4)
        addr = 0x03D0 + i
        y, tile, attr, x = oam_bytes[i:i+4]
        print(f"  Sprite #{sprite_num:02d} [RAM ${addr:04X}]: Y={y:3d} (${y:02X}), Tile=${tile:02X}, Attr=${attr:02X}, X={x:3d} (${x:02X})")
        
    print("\n6502 CPU Disassembly of OAM Sprite Buffer:")
    insts = disassemble_6502_bytes(oam_bytes)
    for addr, hex_str, asm_str in insts:
        print(f"  ${addr:04X}: {hex_str:<12} -> {asm_str}")
        
    print("\nResult:")
    print("  Executing this 2-sprite sequence sets OperatingMode ($0770) = $03 (Game Over/Victory) and returns cleanly via RTS!")

if __name__ == '__main__':
    analyze_sprite_payload()
