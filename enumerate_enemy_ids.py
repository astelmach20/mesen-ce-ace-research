#!/usr/bin/env python3
"""
Exhaustive 256 Enemy ID Dispatch Destination Enumerator for Super Mario Bros. (SMB1)
Calculates exact JumpEngine ($8E04) destination addresses for all 256 Enemy_ID values
and classifies target memory domains (RAM, Stack, OAM, Zero Page, ROM Gadget).
"""

import sys
import os

def load_smb1_prg(rom_path):
    with open(rom_path, 'rb') as f:
        data = f.read()
    # Check INES header
    if data[:4] == b'NES\x1a':
        header_size = 16
        prg_size = data[4] * 16384
        prg_data = data[header_size:header_size + prg_size]
    else:
        prg_data = data

    # SMB1 has 32KB PRG (0x8000 bytes) mapped from CPU $8000 to $FFFF
    if len(prg_data) < 0x8000:
        raise ValueError(f"PRG ROM size {len(prg_data)} is smaller than 32KB")
    
    # If PRG is larger than 32KB (e.g. Mapper 99), use the first 32KB bank
    return prg_data[:0x8000]

def cpu_addr_to_prg_offset(cpu_addr):
    return cpu_addr - 0x8000

def classify_address(target_addr):
    if 0x0000 <= target_addr <= 0x00FF:
        return "Zero Page RAM ($0000-$00FF)"
    elif 0x0100 <= target_addr <= 0x01FF:
        return "CPU Stack RAM ($0100-$01FF)"
    elif 0x0200 <= target_addr <= 0x02FF:
        return "PPU OAM Sprite Buffer ($0200-$02FF)"
    elif 0x0300 <= target_addr <= 0x03FF:
        return "PPU OAM Shadow Buffer ($0300-$03FF)"
    elif 0x0400 <= target_addr <= 0x07FF:
        return "Game State Internal RAM ($0400-$07FF)"
    elif 0x2000 <= target_addr <= 0x5FFF:
        return "PPU / APU / MMIO Registers ($2000-$5FFF)"
    elif 0x6000 <= target_addr <= 0x7FFF:
        return "SRAM / Expansion RAM ($6000-$7FFF)"
    elif 0x8000 <= target_addr <= 0xFFFF:
        return "PRG-ROM Code / Data ($8000-$FFFF)"
    else:
        return "Unmapped Address Space"

def enumerate_all_enemy_ids(rom_path):
    prg = load_smb1_prg(rom_path)
    base_addr = 0xC891
    base_offset = cpu_addr_to_prg_offset(base_addr)

    results = []
    
    for enemy_id in range(256):
        if enemy_id < 0x15:
            index = 0
        else:
            index = enemy_id - 0x14
            
        lookup_offset = base_offset + (2 * index) + 1
        
        if lookup_offset + 1 < len(prg):
            low_byte = prg[lookup_offset]
            high_byte = prg[lookup_offset + 1]
            target_addr = low_byte | (high_byte << 8)
        else:
            low_byte = high_byte = 0
            target_addr = 0
            
        category = classify_address(target_addr)
        results.append({
            'enemy_id': enemy_id,
            'index': index,
            'rom_offset': f"${base_addr + 2*index + 1:04X}",
            'pointer_bytes': f"{low_byte:02X} {high_byte:02X}",
            'target_addr': f"${target_addr:04X}",
            'category': category
        })
        
    return results

if __name__ == '__main__':
    rom_path = sys.argv[1] if len(sys.argv) > 1 else "smb_mapper99.nes"
    results = enumerate_all_enemy_ids(rom_path)
    
    print(f"=========================================================================")
    print(f"  SMB1 256 ENEMY ID JUMPENGINE DESTINATION ENUMERATION MATRIX")
    print(f"=========================================================================")
    print(f"{'Enemy ID':<10} | {'Index':<6} | {'ROM Offset':<10} | {'Bytes':<8} | {'Target':<8} | {'Category'}")
    print("-" * 75)
    
    ram_targets = []
    for r in results:
        print(f"0x{r['enemy_id']:02X} ({r['enemy_id']:3d}) | 0x{r['index']:02X}   | {r['rom_offset']:<10} | {r['pointer_bytes']:<8} | {r['target_addr']:<8} | {r['category']}")
        if "RAM" in r['category']:
            ram_targets.append(r)
            
    print("\n" + "="*75)
    print(f"SUMMARY OF DIRECT RAM LANDING PRIMITIVES DETECTED ({len(ram_targets)} TOTAL):")
    print("="*75)
    for r in ram_targets:
        print(f"  Enemy ID 0x{r['enemy_id']:02X} ({r['enemy_id']:3d}) -> Index 0x{r['index']:02X} -> Target {r['target_addr']} [{r['category']}]")
