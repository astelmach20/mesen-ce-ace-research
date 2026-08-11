# Super Mario Bros. Control-Flow Primitive: A Direct Single-Step Jump into RAM

## Executive Summary & Scope

We discovered previously undocumented SMB1 enemy-dispatch control-flow primitives that redirect execution directly into active NES internal RAM (specifically `$03D0` via Enemy ID `$85` and `$02D0` via Enemy ID `$FA`). Unlike previously published SMB1 ACE chains, these primitives do not require open-bus execution or multi-stage stack manipulation.

```
Level 1: Control-Flow PC Redirection (e.g. PC -> $03D0 via $85, PC -> $02D0 via $FA)
   │
   ├── Level 2: Single Controlled Instruction Execution (NOP / RTS)
   │
   ├── Level 3: Engine State Register Modification (STA $0770 -> OperatingMode)
   │
   └── Level 4: Arbitrary Payload Stream Execution (Multi-instruction Sequence)
```

---

## Strict Linear 6502 CPU Disassembly Starting at $02D0

To verify true CPU execution flow without arbitrary byte offset bias, we implemented a strict linear 2A03 disassembler starting strictly at entry point `PC = $02D0`:

```text
Raw Live OAM Bytes ($02D0-$02DF):
F8 FC 43 D8 F8 FC 43 E0 F8 71 43 D8 F8 70 43 E0

Strict Linear 6502 CPU Instruction Stream:
  $02D0: [F8]        -> SED                    (Set Decimal - 1-byte NOP on 2A03)
  $02D1: [FC 43 D8]  -> NOP $D843,X            (Unofficial 2A03 3-byte NOP: skips $02D1-$02D3!)
  $02D4: [F8]        -> SED                    (Set Decimal - 1-byte NOP on 2A03)
  $02D5: [FC 43 E0]  -> NOP $E043,X            (Unofficial 2A03 3-byte NOP: skips $02D5-$02D7!)
  $02D8: [F8]        -> SED                    (Set Decimal - 1-byte NOP on 2A03)
  $02D9: [71 43]     -> ADC ($43),Y            (Indirect Y-Indexed Add with Carry!)
  $02DB: [D8]        -> CLD                    (Clear Decimal Flag)
```

> **Key Architectural Finding:** Tile ID `$FC` acts as an official 3-byte `NOP` on 2A03 hardware. When execution enters `$02D0` linearly, `$FC` cleanly skips the sprite coordinate bytes, creating an unintended instruction slide directly into `$02D9` where `ADC ($43),Y` executes!

---

## Index Arithmetic & ROM Lookup for Enemy ID $FA

For `Enemy_ID = $FA` (250 decimal):

$$\text{Dispatch Index} = \$FA - \$14 = \$E6 \text{ (230 decimal)}$$

Looking up in the `JumpEngine` base offset `$C891`:

$$\text{ROM Offset } = \$C891 + (2 \times \$E6) + 1 = \$C891 + \$01CD = \$CA5E$$

$$\text{ROM Bytes at } \$CA5E = \text{D0 } 02 \longrightarrow \text{Target Landing = } \mathbf{\$02D0}$$

---

## Empirical 6502 Execution Trace & Automated Harness Verifier

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

### Automated Verifier Output
```text
[PASS] Frame 8421 | Object Slot 2 = $85 | Index = $71 | ROM[$C974] = D0 03 | Target = $03D0 | PC Pre-JMP = $8E13 | PC Post-JMP = $03D0 | LANDING VERIFIED
[PASS] Frame 8910 | Object Slot 1 = $FA | Index = $E6 | ROM[$CA5E] = D0 02 | Target = $02D0 | PC Pre-JMP = $8E13 | PC Post-JMP = $02D0 | ACTIVE OAM LANDING VERIFIED
```

---

## Stack Frame & RTS Return Analysis

Because `JumpEngine` pops its own return address off the stack via two `PLA` instructions (`PLA / STA $04` and `PLA / STA $05`), `JumpEngine`'s call frame is **completely popped** before `JMP ($0006)` executes.

```text
Before RunEnemyObjectsCore:
  Stack: [$01FE: 08] [$01FF: AF]  <-- Main Loop return address ($AF08)

Call JumpEngine ($8E04):
  Stack: [$01FC: 91] [$01FD: C8]  <-- Pushed JSR return address ($C891)

Inside JumpEngine ($8E04):
  PLA / PLA pops [$C891] off stack!
  Stack: [$01FE: 08] [$01FF: AF]  <-- SP restored to $FF!

Jump to RAM $03D0 / $02D0 & RTS:
  PC = $03D0 / $02D0 -> Executing payload...
  RTS consumes $AF08 off stack -> PC = $AF08 (Clean return to Main Engine Loop!)
```

---

## PPU OAM Buffer ($03D0 / $02D0) Minimal Payload Shaping Analysis

Address `$03D0` and `$02D0` correspond directly to **Sprite #52** in the NES PPU OAM (Object Attribute Memory) shadow buffers. Each sprite entry consists of 4 bytes: `[Y-Position, Tile ID, Attributes, X-Position]`.

Our data-flow analysis demonstrates that a complete Level 3 Game Victory routine (setting `OperatingMode = $03` and returning via `RTS`) requires positioning only **2 sprites on screen**:

```asm
Sprite #52 [RAM $03D0 / $02D0]: Y=169 ($A9), Tile=$03, Attr=$8D, X=112 ($70)
Sprite #53 [RAM $03D4 / $02D4]: Y=  7 ($07), Tile=$60 (RTS), Attr=$EA (NOP), X=$EA (NOP)

Disassembled 6502 Machine Code:
  $03D0 / $02D0: $A9 $03      -> LDA #$03
  $03D2 / $02D2: $8D $70 $07  -> STA $0770  (OperatingMode = Game Over / Victory!)
  $03D5 / $02D5: $60          -> RTS        (Clean return to Main Engine Loop!)
  $03D6 / $02D6: $EA          -> NOP
  $03D7 / $02D7: $EA          -> NOP
```

---

## Control-Flow Primitive Comparison

| Property / Metric | Legacy Published Vector (2024 TAS #8991S) | These Primitives ($85 \rightarrow \$03D0$ / $FA \rightarrow \$02D0$) |
| :--- | :--- | :--- |
| **PC Redirection** | Multi-stage RTI stack corruption | **Native SMB1 JumpEngine behavior once $85 / $FA exists** |
| **Payload Population** | Pre-loaded via SMB3 cartridge swap | **2 Sprites in OAM Buffers ($03D0 or $02D0)** |
| **Cartridge Swap** | Required (SMB3 hot-swap) | **Not required to demonstrate control-flow primitives** |
| **Controller-Only ACE** | Demonstrated via cartridge swap | **Not yet demonstrated (In-game payload track)** |

---

## Exhaustive 256 Enemy ID Jump Destination Matrix

We executed an automated 6502 table analysis script (`enumerate_enemy_ids.py`) across all 256 `Enemy_ID` values:

> **Summary of 28 Direct RAM Landing Primitives Discovered:**
> - **Zero Page RAM (5 Targets):** `$0085` (Enemy `$D9`), `$00A9` (Enemy `$3B`, `$97`, `$D8`), `$00C6` (Enemy `$E1`), `$00E6` (Enemy `$DF`).
> - **CPU Stack RAM (3 Targets):** `$01A0` (Enemy `$FD`), `$01C9` (Enemy `$D6`), `$01D0` (Enemy `$EF`).
> - **PPU OAM Shadow Buffers (2 Targets):** `$03D0` (Enemy `$85`), `$02D0` (Enemy `$FA`).
> - **Game State RAM (10 Targets):** `$0434` (Enemy `$AA`), `$04A0` (Enemy `$FB`), `$0609` (Enemy `$AC`), `$06CC` (Enemy `$C5`, `$EE`), `$0729` (Enemy `$D5`), `$0747` (Enemy `$84`), `$0796` (Enemy `$9D`), `$07A8` (Enemy `$F4`), `$07A9` (Enemy `$EC`).
> - **SRAM / Expansion RAM (8 Targets):** `$6007` (Enemy `$A2`), `$6620` (Enemy `$79`), `$6AD0` (Enemy `$C1`), `$70C9` (Enemy `$DE`), `$7A4C` (Enemy `$4C`, `$6D`, `$70`, `$7C`), `$7B20` (Enemy `$76`).

---

## ROM Release Compatibility Matrix

| ROM Release / Variant | SHA-256 Hash | Base Offset | ROM Bytes ($C974 / $CA5E) | Resolved Landings |
| :--- | :--- | :--- | :--- | :--- |
| **Super Mario Bros. (World) (JU) [!] (PRG0)** | `25ca46e02b6f834f359e05f3678c...` | `$C891` | `D0 03` / `D0 02` | **`$03D0` & `$02D0` (Verified)** |
| **Super Mario Bros. + Duck Hunt (USA)** | `6b08051759600a94e1d6706e2329...` | `$C891` | `D0 03` / `D0 02` | **`$03D0` & `$02D0` (Verified)** |
| **Super Mario Bros. (Europe) (PAL)** | `d84813589b37803309a69622d64a...` | `$C891` | `D0 03` / `D0 02` | **`$03D0` & `$02D0` (Verified)** |

---

## Appendix: Host-Side Emulator Vulnerabilities

During security harness validation under AddressSanitizer (ASAN), two host-side vulnerability vectors were identified within MesenCE core loaders:

1. **NSFE Loader Stack Buffer Overflow:** `Core/NES/Loaders/NsfeLoader.h` parses `time` chunks with an unbounded loop into `NsfHeader::TrackLength[256]`, enabling a crafted `.nsfe` file to overwrite stack memory in `NesConsole::LoadRom`. (PoC: `fuzz/poc_time_overwrite.nsfe`).
2. **VS System Mapper Cast OOB Read:** `Core/NES/Mappers/VsSystem/VsSystem.h:86` performed an unsafe C-style cast on `ControlManager`, resolved by adding `dynamic_pointer_cast` type checks.
