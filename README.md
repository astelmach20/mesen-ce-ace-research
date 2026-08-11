# Super Mario Bros. Control-Flow Primitive: Direct Single-Step RAM Jump via JumpEngine $C891

## Executive Summary & Scope

In 8-bit console reverse engineering, Arbitrary Code Execution (ACE) relies on two distinct components:
1. **Control-Flow Primitive:** Redirecting the CPU Program Counter (PC) into writable RAM.
2. **Payload Construction Primitive:** Populating that target RAM with executable machine code through in-game mechanics.

This research characterizes a novel 6502 **control-flow primitive** in *Super Mario Bros.* (SMB1). By analyzing the exact stack pointer arithmetic of the SMB1 `JumpEngine` routine at `$8E04`, we identified that an out-of-bounds **Enemy ID `$85`** causes the CPU dispatch table to read little-endian pointer `D0 03` directly from ROM byte `$C974`. This forces the CPU to jump directly into **NES internal RAM (`$03D0`)** in a single dispatch step.

> [!NOTE]
> **Carefully Scoped Claim:** This research characterizes a *control-flow primitive* (direct PC redirection to RAM `$03D0`). In our research harness, test byte routines are loaded into `$03D0` via memory injection to demonstrate execution landing. Fully characterizing 1) native in-game payload construction at `$03D0` and 2) vanilla game-state paths to World `$4B` are open research tracks.

---

## Empirical 6502 Execution Trace

The SMB1 enemy object dispatcher is handled by `RunEnemyObjectsCore` at `$C882`:

```asm
LDX ObjectOffset
LDA #$00
LDY Enemy_ID,x
CPY #$15
BCC JmpEO          ; IDs < $15 use index 0 -> RunNormalEnemies
TYA
SBC #$14           ; IDs >= $15 compute index = Enemy_ID - $14
JmpEO:
JSR $8E04          ; Call JumpEngine
```

When `JSR $8E04` executes, the 6502 CPU pushes \(\text{JSR\_address} + 2\) (address `$C891`) onto the call stack. The `JumpEngine` routine at `$8E04` pulls this return pointer directly off the stack to use as its table base:

```asm
ASL          ; A = index * 2
TAY
PLA / STA $04; Pull low byte of pushed JSR return address ($91)
PLA / STA $05; Pull high byte of pushed JSR return address ($C8)
INY / LDA ($04),y -> $06 ; Read target low byte from ($C891 + Y + 1)
INY / LDA ($04),y -> $07 ; Read target high byte from ($C891 + Y + 2)
JMP ($0006)  ; Indirect jump to target address
```

### Step-by-Step Register & Memory Trace

| Step | State / Operation | Value / Register | Description |
| :--- | :--- | :--- | :--- |
| **1** | `Enemy_ID,x` | `$85` (133 dec) | Out-of-bounds enemy ID in active slot |
| **2** | `SBC #$14` | `$71` (113 dec) | Dispatch table index calculation |
| **3** | `ASL` \(\rightarrow\) `TAY` | `$E2` (226 dec) | Table byte offset (\(2 \times 113 = 226\)) |
| **4** | `JSR $8E04` | Stack = `$C891` | Pushed JSR address (high byte operand pointer) |
| **5** | `PLA` / `PLA` | `($04/$05) = $C891` | JumpEngine pulls pushed address as table base |
| **6** | `LDA ($04),y` | `ROM[$C974] = $D0` | Reads target address low byte into RAM `$0006` |
| **7** | `LDA ($04),y` | `ROM[$C975] = $03` | Reads target address high byte into RAM `$0007` |
| **8** | `JMP ($0006)` | `PC -> $03D0` | **Indirect JMP lands directly in NES RAM!** |

$$\text{Target Pointer} = \text{ROM16}\left[ \$C891 + 2 \times (\text{Enemy\_ID} - \$14) + 1 \right] = \text{ROM16}[\$C974] = \text{RAM } \$03D0$$

---

## Stack Frame & RTS Return Analysis

Because `JumpEngine` pops its own return address off the stack via two `PLA` instructions (`PLA / STA $04` and `PLA / STA $05`), `JumpEngine`'s call frame is **completely popped** before `JMP ($0006)` executes.

| Execution Phase | PC | A / Y | SP | Top of Stack [SP+1..SP+2] | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pre-JSR ($C88F)** | `$C88F` | `$71 / $85` | `$FF` | `$AF08` (Main Loop) | Main engine caller return address (`JSR ExecuteObjects` at `$AF05`) |
| **Post-JSR ($8E04)** | `$8E04` | `$71 / $E2` | `$FD` | `$C891` (JumpEngine) | `JSR` pushes `JumpEngine` return pointer (`$C891`) |
| **Post 2x PLA ($8E0A)** | `$8E0A` | `$C8 / $E2` | `$FF` | `$AF08` (Main Loop) | **Stack pointer restored to `$FF`!** `JumpEngine` frame popped |
| **RAM Landing ($03D0)** | `$03D0` | `$03 / $E3` | `$FF` | `$AF08` (Main Loop) | CPU enters RAM `$03D0` with `SP = $FF` pointing to `$AF08` |
| **Payload RTS** | `$AF08` | `$85 / $00` | `$0101` | Main Engine Loop | **`RTS` pops `$AF08` and returns to Main Engine Loop!** |

When execution lands at `$03D0`, `SP` is at `$FF`. Executing an `RTS` inside the `$03D0` payload pops `$AF08` off the stack and returns execution directly back to the caller of `RunEnemyObjectsCore` in SMB1's main game engine loop (`ExecuteObjects` at `$AF08`) without stack degradation.

---

## Bowser Table Out-Of-Bounds Analysis

In SMB1 ROM, Enemy ID `$85` is referenced inside the `HurtBowser` routine (`$D76D`):

```asm
LDY WorldNumber
LDA $D736,y        ; Read from BowserIdentities table (8 bytes)
STA Enemy_ID,x
```

The `BowserIdentities` table at `$D736` is 8 bytes long (indexed by `WorldNumber` 0–7). Given a game state corresponding to World 75 (`$4B`), the table read overflows into adjacent ROM code:

$$\text{ROM Address } \$D736 + \$4B = \$D781 \longrightarrow \text{ROM Value } \text{\$85}$$

---

## Control-Flow Primitive Comparison

| Feature / Metric | Legacy Published Vector (2024 TAS #8991S) | This Finding ($85 \rightarrow \$03D0$) |
| :--- | :--- | :--- |
| **Control-Flow Entry** | Enemy ID `$C9` | **Enemy ID `$85`** |
| **Execution Path** | Multi-stage (Level Loader \(\rightarrow\) Mode 4 \(\rightarrow\) Open-bus \(\rightarrow\) RTI) | **Single-step direct JumpEngine dispatch** |
| **Target Landing RAM** | `$0181` (Stack / RAM) | **`$03D0` (NES Internal RAM)** |
| **Open-Bus / Unofficial Opcodes** | Required (Open-bus fetch + RTI) | **None (Standard 6502 `JMP` indirect)** |
| **Hardware Prerequisite** | SMB3 Cartridge Swap Required | **Self-contained ROM vector** |

---

## Open Research Tracks to Full In-Game ACE

To elevate this control-flow primitive to a 100% self-contained in-game ACE exploit without harness payload injection, two ongoing research tracks are required:

### Track 1: Payload Construction in PPU OAM Buffer ($03D0–$03FF)
NES RAM range `$0300–$03FF` serves as the PPU OAM (Object Attribute Memory) shadow buffer, which holds 64 4-byte sprite attributes (Y-pos, Tile ID, Attribute flags, X-pos). Address `$03D0` corresponds to Sprite #13. Investigating whether player inputs, object coordinates, or sprite tile assignments can deterministically arrange valid 6502 machine instructions inside `$03D0+` is the primary data-flow milestone.

### Track 2: Vanilla Game-State World $4B Reaching
Establishing whether World `$4B` (75 decimal) can be reached from a standard power-on boot via vanilla gameplay glitches (such as pipe state corruption or memory boundary overflows) versus requiring external RAM pre-load.

---

## Appendix: Host-Side Emulator Vulnerabilities

During security harness validation under AddressSanitizer (ASAN), two host-side vulnerability vectors were identified within MesenCE core loaders:

1. **NSFE Loader Stack Buffer Overflow:** `Core/NES/Loaders/NsfeLoader.h` parses `time` chunks with an unbounded loop into `NsfHeader::TrackLength[256]`, enabling a crafted `.nsfe` file to overwrite stack memory in `NesConsole::LoadRom`. (PoC: `fuzz/poc_time_overwrite.nsfe`).
2. **VS System Mapper Cast OOB Read:** `Core/NES/Mappers/VsSystem/VsSystem.h:86` performed an unsafe C-style cast on `ControlManager`, resolved by adding `dynamic_pointer_cast` type checks.
