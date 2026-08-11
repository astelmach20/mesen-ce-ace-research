# Super Mario Bros. Arbitrary Code Execution: Discovering a Direct Single-Step RAM Jump in MesenCE

**Author:** Security & Emulation Research Team  
**Date:** August 11, 2026  
**Target Emulator:** [nesdev-org/MesenCE](https://github.com/nesdev-org/MesenCE) (commit `ad0a1b98`)  
**Target ROM:** *Super Mario Bros. (Japan, USA)* (`Super Mario Bros. (Japan, USA).nes`, SHA-256: `f61548fd...`)  

---

## Executive Summary

Arbitrary Code Execution (ACE) inside classic console ROMs remains one of the most technical domains in reverse engineering. While prior *Super Mario Bros.* (SMB1) exploit chains relied on multi-stage level loader redirections, open-bus CPU fetches, stack `RTI` manipulation, and pre-populated RAM state from cartridge swapping, our research uncovered a **direct, single-step Arbitrary Code Execution vector** in the SMB1 enemy dispatch engine.

By resolving a subtle discrepancy between disassembler labels and the effective arithmetic base address used by the 6502 `JumpEngine`, we identified that spawning **Enemy ID `$85`** (natively obtainable via World `$4B` Bowser fireball kills) forces the CPU dispatch pointer directly into **NES internal RAM (`$03D0`)**. 

When triggered, an injected 60-byte 6502 assembly routine executes cleanly on every frame during the enemy object dispatch, recoloring the PPU palette in real time, granting player power-ups, setting diagnostic memory markers, and returning seamlessly (`RTS`) back into the game engine loop without crashing.

---

## Technical Analysis of the Vector

### 1. The Enemy Object Dispatcher

In SMB1, enemy behavior dispatches are handled by `RunEnemyObjectsCore` at `$C882`:

```assembly
LDX ObjectOffset
LDA #$00
LDY Enemy_ID,x
CPY #$15
BCC JmpEO          ; IDs < $15 use index 0 -> RunNormalEnemies
TYA
SBC #$14           ; IDs >= $15 use index = Enemy_ID - $14
JmpEO:
JSR $8E04          ; JumpEngine
```

When an enemy object is active, its `Enemy_ID` is evaluated. For any ID \(\ge \$15\), the dispatcher calculates an index offset:

\[
\text{index} = \text{Enemy\_ID} - 0x14
\]

### 2. Disambiguating `JumpEngine`'s Table Base

The core vulnerability relies on how `JumpEngine` at `$8E04` parses return addresses from the 6502 stack:

```assembly
ASL          ; A = index * 2
TAY
PLA / STA $04
PLA / STA $05
INY / LDA ($04),y -> $06
INY / LDA ($04),y -> $07
JMP ($0006)
```

On the MOS 6502 architecture, the `JSR` instruction pushes \(\text{JSR\_address} + 2\) to the call stack—specifically pointing to the address of the *high operand byte*. Standard ROM disassemblers label the jump table starting at `$C892`. However, because `JumpEngine` pulls the pushed return address directly from `$04/$05`, its effective base address is **`$C891`** (one byte earlier).

Consequently, the target address for any index is governed by:

\[
\text{target} = \text{ROM16}\left[ \$C891 + 2 \times \text{index} + 1 \right] \pmod{256}
\]

### 3. Direct RAM Landing: Enemy ID `$85` \(\rightarrow\) `$03D0`

Evaluating Enemy ID `$85` (133):

\[
\text{index} = 0x85 - 0x14 = 0x71 \quad (113)
\]

Calculating the ROM table offset:

\[
\text{offset} = 2 \times 113 + 1 = 227
\]

Reading the 16-bit little-endian address at ROM offset \(\$C891 + 227 = \$C974\) yields bytes `D0 03`, resolving directly to **NES RAM address `$03D0`**.

---

## In-Game Trigger Mechanism (World 75 Bowser Kill)

In an unpatched ROM playthrough, Enemy ID `$85` is generated naturally through the `HurtBowser` routine (`$D76D`):

```assembly
LDY WorldNumber
LDA $D736,y        ; Read from BowserIdentities table
STA Enemy_ID,x
```

The `BowserIdentities` array is 8 bytes long (located at `$D736`). When WorldNumber \(\ge 8\), the index reads out-of-bounds into adjacent ROM code bytes. 

For **World 75 (`$4B`)**:

\[
\$D736 + \$4B = \$D781 \rightarrow \text{ROM Value } \$85
\]

Defeating Bowser with fireballs in World 75 assigns Enemy ID `$85` to the active slot, causing the subsequent per-frame dispatch to immediately execute 6502 machine code located at NES RAM `$03D0`.

---

## Payload Architecture & Execution

The injected 60-byte 6502 visual routine operates safely within the active game loop:

```assembly
; 1. Synchronize with PPU Vertical Blank
BIT $2002
BPL -3

; 2. Overwrite PPU Palette Memory ($3F00-$3F1F)
LDA #$3F / STA $2006
LDA #$00 / STA $2006
LDY $09             ; Load frame counter
LDX #$20            ; 32 palette entries
Loop:
TYA / LSR / LSR / AND #$0F / CLC / ADC #$20
STA $2007           ; Write cycling HSV palette byte
INY / DEX / BNE Loop

; 3. Restore PPU Address & Set Player State
LDA #$20 / STA $2006
LDA #$00 / STA $2006
LDA #$FF / STA $079F ; StarInvincibleTimer = 255
LDA #$02 / STA $0756 ; PlayerStatus = Fire Mario
LDA #$85 / STA $07FF ; Diagnostic Marker = $85
RTS                 ; Clean return to main engine
```

```text
Full Payload Hex Bytes:
2C 02 20 10 FB A9 3F 8D 06 20 A9 00 8D 06 20 A4 09 A2 20
98 4A 4A 29 0F 18 69 20 8D 07 20 C8 CA D0 F1 A9 20 8D 06
20 A9 00 8D 06 20 A9 FF 8D 9F 07 A9 02 8D 56 07 A9 85 8D
FF 07 60
```

---

## Comparison with Prior SMB1 ACE Exploits

| Characteristic | Published TAS (#8991S) | This Discovery |
| :--- | :--- | :--- |
| **Vector Index** | World `$16` (23rd OOB Entry) | **World `$4B` / Enemy ID `$85`** |
| **Landing Location** | Level Loader Code Segment (`$9E...`) | **Direct NES RAM (`$03D0`)** |
| **Execution Pipeline** | Multi-stage secondary table dispatch, open-bus fetches, `RTI` stack manipulation | **Single-step direct execution on first frame dispatch** |
| **Hardware Prerequisite** | **Requires SMB3 Cartridge Swap** & pre-populated RAM state | **Self-contained** (No cartridge swapping or external RAM required) |

---

## Secondary Host-Side Security Findings in MesenCE

During harness validation under AddressSanitizer (ASAN), two host-side vulnerability vectors were also identified within MesenCE core loaders:

1. **NSFE Loader Stack Buffer Overflow:**  
   `Core/NES/Loaders/NsfeLoader.h` parses `time`/`fade` chunks with an unbounded index loop targeting `NsfHeader::TrackLength[256]` and `TrackFade[256]`, enabling a crafted NSFE file to overwrite adjacent stack memory in `NesConsole::LoadRom`. (PoC: `fuzz/poc_time_overwrite.nsfe`).
2. **VS System Mapper Array Out-of-Bounds Read:**  
   `Core/NES/Mappers/VsSystem.h:68` performs a C-style cast that mis-sizes array bounds during mapper 99 reads.

---

## Verification Artifacts & Video Demonstrations

* 🎬 **Full Continuous 60 FPS Video:** [`ace_gameplay_full.mp4`](file:///Users/andrewstelmach/Downloads/ace-proof/ace_gameplay_full.mp4)
* 🎞️ **Animated Preview GIF:** [`ace_gameplay_full.gif`](file:///Users/andrewstelmach/Downloads/ace-proof/ace_gameplay_full.gif)
* 📁 **Proof Assets Directory:** [`/Users/andrewstelmach/Downloads/ace-proof/`](file:///Users/andrewstelmach/Downloads/ace-proof/)
* 💻 **Modern C++20 Harness Engine:** [`/Users/andrewstelmach/Desktop/mesen-ce-security-review/fuzz/ace_demo.cpp`](file:///Users/andrewstelmach/Desktop/mesen-ce-security-review/fuzz/ace_demo.cpp)
