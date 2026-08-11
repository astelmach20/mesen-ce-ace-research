#!/usr/bin/env python3
"""
Ultra-High-DPI (4K / 3x Retina) Programmatic Diagram Generator
Renders 3600x1890 pixel crisp, ultra-sharp vector diagrams for high-DPI displays.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_hero_diagram(output_png):
    # 3x Retina Scale: 3600 x 1890
    scale = 3
    width, height = 1200 * scale, 630 * scale
    img = Image.new('RGB', (width, height), color='#0A0A0C')
    draw = ImageDraw.Draw(img)

    # Load high-res system fonts
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 24 * scale)
        font_bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 15 * scale)
        font_main = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 13 * scale)
        font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12.5 * scale)
        font_code_bold = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13.5 * scale)
    except Exception:
        font_title = font_bold = font_main = font_code = font_code_bold = ImageFont.load_default()

    # Subtle Background Grid
    grid_color = '#141419'
    for x in range(0, width, 40 * scale):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=scale)
    for y in range(0, height, 40 * scale):
        draw.line([(0, y), (width, y)], fill=grid_color, width=scale)

    # Diagram Title
    draw.text((40 * scale, 25 * scale), "MOS 6502 JumpEngine Execution Flow & Direct RAM Redirection", fill='#FFFFFF', font=font_title)
    draw.text((40 * scale, 60 * scale), "SMB1 Enemy Object Dispatcher ($C882) -> JumpEngine ($8E04) -> NES RAM ($03D0)", fill='#888899', font=font_main)

    def draw_box(box, bg='#121218', border='#2A2A36', radius=8*scale):
        x1, y1, x2, y2 = [v * scale for v in box]
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg, outline=border, width=2 * scale)

    # 1. Box: Enemy Object Dispatcher ($C882)
    b1 = (40, 100, 310, 320)
    draw_box(b1, bg='#12131C', border='#3B82F6')
    draw.rectangle([40 * scale, 100 * scale, 310 * scale, 132 * scale], fill='#1E293B')
    draw.text((52 * scale, 107 * scale), "Enemy Dispatcher ($C882)", fill='#60A5FA', font=font_bold)
    
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
        draw.text((52 * scale, (140 + i*21) * scale), line, fill=color, font=font_code)

    # 2. Box: JumpEngine ($8E04) & Off-By-One Discovery
    b2 = (350, 100, 680, 320)
    draw_box(b2, bg='#13121E', border='#8B5CF6')
    draw.rectangle([350 * scale, 100 * scale, 680 * scale, 132 * scale], fill='#2E1065')
    draw.text((362 * scale, 107 * scale), "JumpEngine ($8E04) Offset Base", fill='#C084FC', font=font_bold)
    
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
        draw.text((362 * scale, (140 + i*20) * scale), line, fill=color, font=font_code)

    # 3. Box: Target Address Calculation
    b3 = (720, 100, 1160, 320)
    draw_box(b3, bg='#0F1715', border='#10B981')
    draw.rectangle([720 * scale, 100 * scale, 1160 * scale, 132 * scale], fill='#064E3B')
    draw.text((732 * scale, 107 * scale), "Target Address Calculation", fill='#34D399', font=font_bold)

    calc_lines = [
        ("Enemy ID:", "$85  (133 decimal)"),
        ("Index (ID - $14):", "$85 - $14 = $71  (113)"),
        ("ROM Table Offset:", "2 * 113 + 1 = 227"),
        ("Lookup Pointer:", "ROM16[$C891 + 227]"),
        ("ROM Bytes @ $C974:", "D0 03 (little-endian)"),
        ("DISPATCH TARGET:", "$03D0  (NES RAM!)")
    ]
    for i, (label, val) in enumerate(calc_lines):
        draw.text((732 * scale, (142 + i*28) * scale), label, fill='#94A3B8', font=font_main)
        color = '#10B981' if '$03D0' in val else '#E2E8F0'
        font_use = font_code_bold if '$03D0' in val else font_code
        draw.text((890 * scale, (142 + i*28) * scale), val, fill=color, font=font_use)

    # Connectors
    draw.line([(310 * scale, 210 * scale), (350 * scale, 210 * scale)], fill='#3B82F6', width=3 * scale)
    draw.polygon([(343 * scale, 204 * scale), (352 * scale, 210 * scale), (343 * scale, 216 * scale)], fill='#3B82F6')

    draw.line([(680 * scale, 210 * scale), (720 * scale, 210 * scale)], fill='#8B5CF6', width=3 * scale)
    draw.polygon([(713 * scale, 204 * scale), (722 * scale, 210 * scale), (713 * scale, 216 * scale)], fill='#8B5CF6')

    # Arrow down to RAM Execution
    draw.line([(940 * scale, 320 * scale), (940 * scale, 370 * scale)], fill='#10B981', width=4 * scale)
    draw.polygon([(930 * scale, 363 * scale), (940 * scale, 375 * scale), (950 * scale, 363 * scale)], fill='#10B981')

    # 4. Box: NES RAM Execution ($03D0)
    b4 = (40, 375, 1160, 580)
    draw_box(b4, bg='#111827', border='#3B82F6')
    draw.rectangle([40 * scale, 375 * scale, 1160 * scale, 408 * scale], fill='#1E3A8A')
    draw.text((52 * scale, 383 * scale), "NES Internal RAM Execution Landing ($03D0) — 60-Byte Visual Payload Routine", fill='#93C5FD', font=font_bold)

    payload_steps = [
        ("1. Vblank Wait", "BIT $2002; BPL -3", "Synchronizes CPU writes safely with PPU vertical blanking"),
        ("2. Palette Overwrite", "STA $2006 ($3F00); STA $2007", "Overwrites PPU palette memory ($3F00-$3F1F) with dynamic HSV colors"),
        ("3. PPU Reset", "STA $2006 ($2000)", "Restores PPU address registers back to nametable for normal rendering"),
        ("4. State Mutators", "STA $079F=#$FF; STA $0756=#$02", "Sets Star Invincibility timer to 255 and promotes Mario to Fire Mario"),
        ("5. Marker Assertion", "STA $07FF=#$85; RTS", "Asserts diagnostic marker byte ($85) and cleanly returns to game engine")
    ]

    for i, (title, asm, desc) in enumerate(payload_steps):
        y = (420 + i*31) * scale
        draw.text((52 * scale, y), title, fill='#F59E0B', font=font_bold)
        draw.text((220 * scale, y), asm, fill='#38BDF8', font=font_code_bold)
        draw.text((510 * scale, y), desc, fill='#94A3B8', font=font_main)

    img.save(output_png, quality=98)
    print(f"Generated 4K Hero diagram (3600x1890): {output_png}")


def create_comparison_diagram(output_png):
    scale = 3
    width, height = 1200 * scale, 630 * scale
    img = Image.new('RGB', (width, height), color='#0A0A0C')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 24 * scale)
        font_bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 16 * scale)
        font_main = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 13 * scale)
    except Exception:
        font_title = font_bold = font_main = ImageFont.load_default()

    grid_color = '#141419'
    for x in range(0, width, 40 * scale):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=scale)
    for y in range(0, height, 40 * scale):
        draw.line([(0, y), (width, y)], fill=grid_color, width=scale)

    draw.text((40 * scale, 25 * scale), "Super Mario Bros. Arbitrary Code Execution: Exploit Vector Comparison", fill='#FFFFFF', font=font_title)
    draw.text((40 * scale, 60 * scale), "Legacy Multi-Stage TAS ACE (2024) vs Direct Single-Step RAM Jump Primitive (2026)", fill='#888899', font=font_main)

    def draw_box(box, bg='#121218', border='#2A2A36', radius=8*scale):
        x1, y1, x2, y2 = [v * scale for v in box]
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg, outline=border, width=2 * scale)

    # Left Panel: Published 2024 TAS ACE
    b_left = (40, 100, 580, 580)
    draw_box(b_left, bg='#1A1113', border='#EF4444')
    draw.rectangle([40 * scale, 100 * scale, 580 * scale, 137 * scale], fill='#7F1D1D')
    draw.text((56 * scale, 110 * scale), "Legacy Published TAS ACE (2024 — TASVideos #8991S)", fill='#FCA5A5', font=font_bold)

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
        y = (155 + i*51)
        draw_box((56, y, 564, y+43), bg='#261215', border='#451A1D')
        draw.text((70 * scale, (y+6) * scale), label, fill='#F87171', font=font_bold)
        color = '#FCA5A5' if 'Required' in val or 'Multi-stage' in val else '#E2E8F0'
        draw.text((70 * scale, (y+23) * scale), val, fill=color, font=font_main)

    # Right Panel: This Research Discovery (2026)
    b_right = (620, 100, 1160, 580)
    draw_box(b_right, bg='#0F1D18', border='#10B981')
    draw.rectangle([620 * scale, 100 * scale, 1160 * scale, 137 * scale], fill='#064E3B')
    draw.text((636 * scale, 110 * scale), "Direct Single-Step RAM Jump Primitive (2026 Research)", fill='#6EE7B7', font=font_bold)

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
        y = (155 + i*51)
        draw_box((636, y, 1144, y+43), bg='#112A22', border='#134E3A')
        draw.text((650 * scale, (y+6) * scale), label, fill='#34D399', font=font_bold)
        color = '#6EE7B7' if '$03D0' in val or 'Self-Contained' in val or 'Single-Step' in val else '#E2E8F0'
        draw.text((650 * scale, (y+23) * scale), val, fill=color, font=font_main)

    img.save(output_png, quality=98)
    print(f"Generated 4K Comparison diagram (3600x1890): {output_png}")

if __name__ == '__main__':
    out_dir = "/Users/andrewstelmach/Desktop/smb1-ace-research/docs/assets"
    os.makedirs(out_dir, exist_ok=True)
    create_hero_diagram(os.path.join(out_dir, "hero_ace_diagram.png"))
    create_comparison_diagram(os.path.join(out_dir, "vector_comparison_diagram.png"))
