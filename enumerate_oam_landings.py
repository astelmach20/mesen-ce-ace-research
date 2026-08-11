#!/usr/bin/env python3
"""
Filter 256 SMB1 Enemy ID table specifically for targets landing inside the
256-byte PPU OAM Buffer Page ($0200-$02FF).
"""

from enumerate_enemy_ids import enumerate_all_enemy_ids

def find_all_oam_page_landings(rom_path):
    all_results = enumerate_all_enemy_ids(rom_path)
    oam_landings = []
    
    for r in all_results:
        addr = int(r['target_addr'].replace('$', ''), 16)
        if 0x0200 <= addr <= 0x02FF:
            sprite_index = (addr - 0x0200) // 4
            byte_in_sprite = (addr - 0x0200) % 4
            byte_names = ["Y-Position", "Tile ID", "Attributes", "X-Position"]
            r['sprite_index'] = sprite_index
            r['offset_in_sprite'] = byte_names[byte_in_sprite]
            oam_landings.append(r)
            
    return oam_landings

if __name__ == '__main__':
    rom_path = "/Users/andrewstelmach/Desktop/mesen-ce-security-review/fuzz/smb_mapper99.nes"
    oam_landings = find_all_oam_page_landings(rom_path)
    
    print("=========================================================================")
    print("  SMB1 ENEMY IDS LANDING INSIDE PPU OAM BUFFER PAGE ($0200-$02FF)")
    print("=========================================================================")
    print(f"{'Enemy ID':<10} | {'Index':<6} | {'ROM Offset':<10} | {'Bytes':<8} | {'Target':<8} | {'Sprite #':<10} | {'Byte Offset'}")
    print("-" * 80)
    
    for r in oam_landings:
        print(f"0x{r['enemy_id']:02X} ({r['enemy_id']:3d}) | 0x{r['index']:02X}   | {r['rom_offset']:<10} | {r['pointer_bytes']:<8} | {r['target_addr']:<8} | Sprite #{r['sprite_index']:<2d} | {r['offset_in_sprite']}")
