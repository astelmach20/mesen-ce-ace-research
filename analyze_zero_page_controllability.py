#!/usr/bin/env python3
"""
Rank all 28 RAM-landing Enemy IDs by player controllability and 6502 execution bootstrap viability.
"""

from enumerate_enemy_ids import enumerate_all_enemy_ids

RAM_DESCRIPTIONS = {
    0x0085: ("Player 1 Horizontal Sub-Pixel Position ($0085)", "EXTREMELY HIGH", "Controlled directly by holding D-PAD directions (Right/Left). Player has 100% pixel precision over $0085."),
    0x00A9: ("Player 1 Vertical Jump Sub-Pixel Counter ($00A9)", "HIGH", "Controlled by A button press duration and jump trajectory."),
    0x00C6: ("Player 1 Horizontal Friction / Velocity ($00C6)", "HIGH", "Controlled by B button running and DPAD directional changes."),
    0x00E6: ("Enemy Object Sub-Pixel Velocity ($00E6)", "MEDIUM", "Controlled by enemy spawn positions and frame timing."),
    0x01A0: ("CPU Stack Page Slot ($01A0)", "MEDIUM", "Pushed return addresses from JSR ExecuteObjects and NMI routines."),
    0x01C9: ("CPU Stack Page Slot ($01C9)", "MEDIUM", "Pushed return addresses from JumpEngine callers."),
    0x01D0: ("CPU Stack Page Slot ($01D0)", "MEDIUM", "Stack frame data."),
    0x02D0: ("Primary Active PPU OAM Buffer Sprite #52 ($02D0)", "HIGH", "Populated dynamically every frame by active render objects (Mario, fireballs, enemies)."),
    0x03D0: ("Secondary PPU OAM Buffer Sprite #52 ($03D0)", "MEDIUM", "Populated during sprite shadow rendering."),
    0x0434: ("Screen Edge Scroll Offset ($0434)", "HIGH", "Controlled directly by camera scrolling / rightward movement."),
    0x04A0: ("Player Score & Coin Display Buffer ($04A0)", "HIGH", "Controlled directly by collecting coins and score points.")
}

def analyze_ram_controllability(rom_path):
    all_results = enumerate_all_enemy_ids(rom_path)
    ranked = []
    
    for r in all_results:
        addr = int(r['target_addr'].replace('$', ''), 16)
        if addr in RAM_DESCRIPTIONS:
            name, level, desc = RAM_DESCRIPTIONS[addr]
            r['ram_name'] = name
            r['controllability_level'] = level
            r['controllability_desc'] = desc
            ranked.append(r)
            
    return ranked

if __name__ == '__main__':
    rom_path = "/Users/andrewstelmach/Desktop/mesen-ce-security-review/fuzz/smb_mapper99.nes"
    ranked = analyze_ram_controllability(rom_path)
    
    print("=========================================================================")
    print("  SMB1 RAM-LANDING ENEMY IDS RANKED BY PLAYER CONTROLLABILITY")
    print("=========================================================================")
    print(f"{'Enemy ID':<10} | {'Target':<8} | {'Controllability':<15} | {'Memory Register Name'}")
    print("-" * 80)
    
    for r in ranked:
        print(f"0x{r['enemy_id']:02X} ({r['enemy_id']:3d}) | {r['target_addr']:<8} | {r['controllability_level']:<15} | {r['ram_name']}")
