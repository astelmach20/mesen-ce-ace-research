#!/usr/bin/env python3
"""
Programmatic Vector & PNG Diagram Generator for MesenCE SMB1 ACE Research
Renders precise, publication-grade architectural diagrams with exact assembly,
memory addresses, and crisp modern dark-mode vector typography.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_hero_diagram(output_png):
    # Width 1200, Height 630 (16:9 standard)
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color='#0A0A0C')
    draw = ImageDraw.Draw(img)

    # Load system fonts
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 22)
        font_bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 15)
        font_main = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 13)
        font_small = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 11)
        font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
        font_code_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
    except Exception:
        font_title = font_bold = font_main = font_small = font_code = font_code_bold = ImageFont.load_default()

    # Draw Subtle Background Grid
    grid_color = '#141419'
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Diagram Title
    draw.text((40, 25), "MOS 6502 JumpEngine Execution Flow & Direct RAM Redirection", fill='#FFFFFF', font=font_title)
    draw.text((40, 55), "SMB1 Enemy Object Dispatcher ($C882) -> JumpEngine ($8E04) -> NES RAM ($03D0)", fill='#888899', font=font_main)

    # Function to draw rounded rect with border
    def draw_box(box, bg='#121218', border='#2A2A36', radius=8):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg, outline=border, width=1)

    # 1. Box: Enemy Object Dispatcher ($C882)
    b1 = (40, 100, 310, 320)
    draw_box(b1, bg='#12131C', border='#3B82F6')
    draw.rectangle([40, 100, 310, 130], fill='#1E293B')
    draw.text((52, 107), "Enemy Dispatcher ($C882)", fill='#60A5FA', font=font_bold)
    
    code1 = [
        "LDX ObjectOffset",
        "LDA #$00",
        "LDY Enemy_ID,x",
        "CPY #$15",
        "BCC JmpEO  (index=0)",
        "TYA",
        "SBC #$14  (index=ID-$14)",
        "JmpEO: JSR $8E04"
    ]
    for i, line in enumerate(code1):
        color = '#38BDF8' if 'JSR' in line or 'SBC' in line else '#94A3B8'
        draw.text((52, 140 + i*21), line, fill=color, font=font_code)

    # 2. Box: JumpEngine ($8E04) & Off-By-One Discovery
    b2 = (350, 100, 680, 320)
    draw_box(b2, bg='#13121E', border='#8B5CF6')
    draw.rectangle([350, 100, 680, 130], fill='#2E1065')
    draw.text((362, 107), "JumpEngine ($8E04) Offset Base", fill='#C084FC', font=font_bold)
    
    code2 = [
        "ASL / TAY   (index * 2)",
        "PLA / STA $04  (JSR low)",
        "PLA / STA $05  (JSR high)",
        "INY / LDA ($04),y -> $06",
        "INY / LDA ($04),y -> $07",
        "JMP ($0006)",
        "",
        "Pushed JSR Base: $C891",
        "(Not labeled $C892!)"
    ]
    for i, line in enumerate(code2):
        color = '#F472B6' if '$C891' in line or 'JMP' in line else '#CBD5E1'
        draw.text((362, 140 + i*20), line, fill=color, font=font_code)

    # 3. Box: Target Address Calculation
    b3 = (720, 100, 1160, 320)
    draw_box(b3, bg='#0F1715', border='#10B981')
    draw.rectangle([720, 100, 1160, 130], fill='#064E3B')
    draw.text((732, 107), "Target Address Calculation", fill='#34D399', font=font_bold)

    calc_lines = [
        ("Enemy ID:", "$85  (133 decimal)"),
        ("Index (ID - $14):", "$85 - $14 = $71  (113)"),
        ("ROM Table Offset:", "2 * 113 + 1 = 227"),
        ("Lookup Pointer:", "ROM16[$C891 + 227]"),
        ("ROM Bytes @ $C974:", "D0 03 (little-endian)"),
        ("DISPATCH TARGET:", "$03D0  (NES RAM!)")
    ]
    for i, (label, val) in enumerate(calc_lines):
        draw.text((732, 142 + i*28), label, fill='#94A3B8', font=font_main)
        color = '#10B981' if '$03D0' in val else '#E2E8F0'
        font_use = font_code_bold if '$03D0' in val else font_code
        draw.text((880, 142 + i*28), val, fill=color, font=font_use)

    # Connectors between top boxes
    draw.line([(310, 210), (350, 210)], fill='#3B82F6', width=2)
    draw.polygon([(345, 205), (352, 210), (345, 215)], fill='#3B82F6')

    draw.line([(680, 210), (720, 210)], fill='#8B5CF6', width=2)
    draw.polygon([(715, 205), (722, 210), (715, 215)], fill='#8B5CF6')

    # Arrow down to RAM Execution
    draw.line([(940, 320), (940, 370)], fill='#10B981', width=3)
    draw.polygon([(933, 365), (940, 375), (947, 365)], fill='#10B981')

    # 4. Box: In-Game RAM Execution ($03D0) & 60-Byte Visual Payload
    b4 = (40, 375, 1160, 580)
    draw_box(b4, bg='#111827', border='#3B82F6')
    draw.rectangle([40, 375, 1160, 405], fill='#1E3A8A')
    draw.text((52, 382), "NES Internal RAM Execution Landing ($03D0) — 60-Byte Visual Payload Routine", fill='#93C5FD', font=font_bold)

    payload_steps = [
        ("1. Vblank Wait", "BIT $2002; BPL -3", "Synchronizes CPU writes safely with PPU vertical blanking"),
        ("2. Palette Overwrite", "STA $2006 ($3F00); STA $2007", "Overwrites PPU palette memory ($3F00-$3F1F) with dynamic HSV colors"),
        ("3. PPU Reset", "STA $2006 ($2000)", "Restores PPU address registers back to nametable for normal rendering"),
        ("4. State Mutators", "STA $079F=#$FF; STA $0756=#$02", "Sets Star Invincibility timer to 255 and promotes Mario to Fire Mario"),
        ("5. Marker Assertion", "STA $07FF=#$85; RTS", "Asserts diagnostic marker byte ($85) and cleanly returns to game engine")
    ]

    for i, (title, asm, desc) in enumerate(payload_steps):
        y = 418 + i*31
        draw.text((52, y), title, fill='#F59E0B', font=font_bold)
        draw.text((220, y), asm, fill='#38BDF8', font=font_code_bold)
        draw.text((500, y), desc, fill='#94A3B8', font=font_main)

    img.save(output_png, quality=95)
    print(f"Generated hero diagram: {output_png}")


def create_comparison_diagram(output_png):
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color='#0A0A0C')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 22)
        font_bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 16)
        font_main = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 13)
        font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
        font_code_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
    except Exception:
        font_title = font_bold = font_main = font_code = font_code_bold = ImageFont.load_default()

    # Draw Subtle Background Grid
    grid_color = '#141419'
    for x in range(0, width, 40):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # Title
    draw.text((40, 25), "Super Mario Bros. Arbitrary Code Execution: Exploit Vector Comparison", fill='#FFFFFF', font=font_title)
    draw.text((40, 55), "Legacy Multi-Stage TAS ACE (2024) vs Direct Single-Step RAM Jump Primitive (2026)", fill='#888899', font=font_main)

    def draw_box(box, bg='#121218', border='#2A2A36', radius=8):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg, outline=border, width=1)

    # Left Panel: Published 2024 TAS ACE
    b_left = (40, 100, 580, 580)
    draw_box(b_left, bg='#1A1113', border='#EF4444')
    draw.rectangle([40, 100, 580, 135], fill='#7F1D1D')
    draw.text((56, 110), "Legacy Published TAS ACE (2024 — TASVideos #8991S)", fill='#FCA5A5', font=font_bold)

    left_steps = [
        ("Trigger Vector:", "World $16 Bowser fireball kill"),
        ("1st Landing Target:", "End of Level Loader routine ($9E...)"),
        ("2nd Stage Redirection:", "Gameplay mode 4 dispatch table"),
        ("Execution Primitive:", "Open-bus CPU fetch + RTI stack trick"),
        ("Payload Target:", "NES RAM at $0181"),
        ("Hardware Prerequisite:", "SMB3 Cartridge Swap Required"),
        ("Prerequisite Notes:", "Pre-populated RAM state from SMB3 TAS"),
        ("Complexity Level:", "High (Multi-stage + Cartridge swap)")
    ]

    for i, (label, val) in enumerate(left_steps):
        y = 155 + i*51
        draw_box((56, y, 564, y+43), bg='#261215', border='#451A1D')
        draw.text((70, y+6), label, fill='#F87171', font=font_bold)
        color = '#FCA5A5' if 'Required' in val or 'Multi-stage' in val else '#E2E8F0'
        draw.text((70, y+23), val, fill=color, font=font_main)

    # Right Panel: This Research Discovery (2026)
    b_right = (620, 100, 1160, 580)
    draw_box(b_right, bg='#0F1D18', border='#10B981')
    draw.rectangle([620, 100, 1160, 135], fill='#064E3B')
    draw.text((636, 110), "Direct Single-Step RAM Jump Primitive (2026 Research)", fill='#6EE7B7', font=font_bold)

    right_steps = [
        ("Trigger Vector:", "World $4B (75) Bowser fireball kill (ID $85)"),
        ("1st Landing Target:", "Direct NES RAM at $03D0"),
        ("2nd Stage Redirection:", "None (Direct 1-step RAM jump)"),
        ("Execution Primitive:", "JumpEngine $C891 effective base offset"),
        ("Payload Target:", "NES RAM at $03D0"),
        ("Hardware Prerequisite:", "Self-Contained (Zero Cartridge Swap)"),
        ("Prerequisite Notes:", "Native in-game Enemy ID calculation"),
        ("Complexity Level:", "Single-Step Direct Execution")
    ]

    for i, (label, val) in enumerate(right_steps):
        y = 155 + i*51
        draw_box((636, y, 1144, y+43), bg='#112A22', border='#134E3A')
        draw.text((650, y+6), label, fill='#34D399', font=font_bold)
        color = '#6EE7B7' if '$03D0' in val or 'Self-Contained' in val or 'Single-Step' in val else '#E2E8F0'
        draw.text((650, y+23), val, fill=color, font=font_main)

    img.save(output_png, quality=95)
    print(f"Generated comparison diagram: {output_png}")

if __name__ == '__main__':
    out_dir = "/Users/andrewstelmach/Desktop/smb1-ace-research/docs/assets"
    os.makedirs(out_dir, exist_ok=True)
    create_hero_diagram(os.path.join(out_dir, "hero_ace_diagram.png"))
    create_comparison_diagram(os.path.join(out_dir, "vector_comparison_diagram.png"))
