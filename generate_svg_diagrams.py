#!/usr/bin/env python3
"""
Native SVG Vector Diagram Generator for MesenCE SMB1 ACE Research.
Outputs resolution-independent SVG vector graphics.
"""

import os

def create_hero_svg(output_svg):
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #0A0A0C; }
      .grid { stroke: #141419; stroke-width: 1; }
      .title { fill: #FFFFFF; font-family: -apple-system, 'Inter', sans-serif; font-size: 22px; font-weight: 700; }
      .subtitle { fill: #888899; font-family: -apple-system, 'Inter', sans-serif; font-size: 13px; }
      .box-hdr-1 { fill: #1E293B; }
      .box-hdr-2 { fill: #2E1065; }
      .box-hdr-3 { fill: #064E3B; }
      .box-hdr-4 { fill: #1E3A8A; }
      .txt-bold { font-family: -apple-system, 'Inter', sans-serif; font-size: 15px; font-weight: 600; }
      .txt-code { font-family: 'JetBrains Mono', 'Menlo', monospace; font-size: 12.5px; }
      .txt-code-bold { font-family: 'JetBrains Mono', 'Menlo', monospace; font-size: 13px; font-weight: 600; }
    </style>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" class="bg" />

  <!-- Grid -->
  <g class="grid">
    <path d="M 40 0 V 630 M 80 0 V 630 M 120 0 V 630 M 160 0 V 630 M 200 0 V 630 M 240 0 V 630 M 280 0 V 630 M 320 0 V 630 M 360 0 V 630 M 400 0 V 630 M 440 0 V 630 M 480 0 V 630 M 520 0 V 630 M 560 0 V 630 M 600 0 V 630 M 640 0 V 630 M 680 0 V 630 M 720 0 V 630 M 760 0 V 630 M 800 0 V 630 M 840 0 V 630 M 880 0 V 630 M 920 0 V 630 M 960 0 V 630 M 1000 0 V 630 M 1040 0 V 630 M 1080 0 V 630 M 1120 0 V 630 M 1160 0 V 630" />
  </g>

  <!-- Header -->
  <text x="40" y="45" class="title">MOS 6502 JumpEngine Execution Flow &amp; Direct RAM Redirection</text>
  <text x="40" y="70" class="subtitle">SMB1 Enemy Object Dispatcher ($C882) → JumpEngine ($8E04) → NES RAM ($03D0)</text>

  <!-- 1. Box: Dispatcher -->
  <rect x="40" y="100" width="270" height="220" rx="8" fill="#12131C" stroke="#3B82F6" stroke-width="1.5" />
  <rect x="40" y="100" width="270" height="32" rx="8" class="box-hdr-1" />
  <text x="52" y="121" class="txt-bold" fill="#60A5FA">Enemy Dispatcher ($C882)</text>
  <text x="52" y="152" class="txt-code" fill="#94A3B8">LDX ObjectOffset</text>
  <text x="52" y="172" class="txt-code" fill="#94A3B8">LDA #$00</text>
  <text x="52" y="192" class="txt-code" fill="#94A3B8">LDY Enemy_ID,x</text>
  <text x="52" y="212" class="txt-code" fill="#94A3B8">CPY #$15</text>
  <text x="52" y="232" class="txt-code" fill="#94A3B8">BCC JmpEO  (index=0)</text>
  <text x="52" y="252" class="txt-code" fill="#94A3B8">TYA</text>
  <text x="52" y="272" class="txt-code" fill="#38BDF8">SBC #$14  (index=ID-$14)</text>
  <text x="52" y="292" class="txt-code" fill="#38BDF8">JmpEO: JSR $8E04</text>

  <!-- 2. Box: JumpEngine -->
  <rect x="350" y="100" width="330" height="220" rx="8" fill="#13121E" stroke="#8B5CF6" stroke-width="1.5" />
  <rect x="350" y="100" width="330" height="32" rx="8" class="box-hdr-2" />
  <text x="362" y="121" class="txt-bold" fill="#C084FC">JumpEngine ($8E04) Offset Base</text>
  <text x="362" y="152" class="txt-code" fill="#CBD5E1">ASL / TAY   (index * 2)</text>
  <text x="362" y="172" class="txt-code" fill="#CBD5E1">PLA / STA $04  (JSR low)</text>
  <text x="362" y="192" class="txt-code" fill="#CBD5E1">PLA / STA $05  (JSR high)</text>
  <text x="362" y="212" class="txt-code" fill="#CBD5E1">INY / LDA ($04),y -&gt; $06</text>
  <text x="362" y="232" class="txt-code" fill="#CBD5E1">INY / LDA ($04),y -&gt; $07</text>
  <text x="362" y="252" class="txt-code" fill="#F472B6">JMP ($0006)</text>
  <text x="362" y="282" class="txt-code-bold" fill="#F472B6">Pushed JSR Base: $C891 (Not $C892!)</text>

  <!-- 3. Box: Calculation -->
  <rect x="720" y="100" width="440" height="220" rx="8" fill="#0F1715" stroke="#10B981" stroke-width="1.5" />
  <rect x="720" y="100" width="440" height="32" rx="8" class="box-hdr-3" />
  <text x="732" y="121" class="txt-bold" fill="#34D399">Target Address Calculation</text>

  <text x="732" y="155" class="subtitle">Enemy ID:</text>
  <text x="890" y="155" class="txt-code" fill="#E2E8F0">$85  (133 decimal)</text>

  <text x="732" y="183" class="subtitle">Index (ID - $14):</text>
  <text x="890" y="183" class="txt-code" fill="#E2E8F0">$85 - $14 = $71  (113)</text>

  <text x="732" y="211" class="subtitle">ROM Table Offset:</text>
  <text x="890" y="211" class="txt-code" fill="#E2E8F0">2 * 113 + 1 = 227</text>

  <text x="732" y="239" class="subtitle">Lookup Pointer:</text>
  <text x="890" y="239" class="txt-code" fill="#E2E8F0">ROM16[$C891 + 227]</text>

  <text x="732" y="267" class="subtitle">ROM Bytes @ $C974:</text>
  <text x="890" y="267" class="txt-code" fill="#E2E8F0">D0 03 (little-endian)</text>

  <text x="732" y="295" class="subtitle">DISPATCH TARGET:</text>
  <text x="890" y="295" class="txt-code-bold" fill="#10B981">$03D0  (NES RAM!)</text>

  <!-- Connections -->
  <path d="M 310 210 H 350" stroke="#3B82F6" stroke-width="2" marker-end="url(#arr-blue)" />
  <path d="M 680 210 H 720" stroke="#8B5CF6" stroke-width="2" marker-end="url(#arr-purple)" />
  <path d="M 940 320 V 375" stroke="#10B981" stroke-width="3" />

  <!-- 4. Box: Payload -->
  <rect x="40" y="375" width="1120" height="205" rx="8" fill="#111827" stroke="#3B82F6" stroke-width="1.5" />
  <rect x="40" y="375" width="1120" height="32" rx="8" class="box-hdr-4" />
  <text x="52" y="396" class="txt-bold" fill="#93C5FD">NES Internal RAM Execution Landing ($03D0) — 18-Byte Instant Victory Payload Routine</text>

  <text x="52" y="435" class="txt-bold" fill="#F59E0B">1. OperatingMode = Victory</text>
  <text x="320" y="435" class="txt-code-bold" fill="#38BDF8">LDA #$02; STA $0770</text>
  <text x="610" y="435" class="subtitle">Shifts main game loop into Victory / End-Game state ($02)</text>

  <text x="52" y="470" class="txt-bold" fill="#F59E0B">2. WorldEndRoutineTask = 1</text>
  <text x="320" y="470" class="txt-code-bold" fill="#38BDF8">LDA #$01; STA $071B</text>
  <text x="610" y="470" class="subtitle">Triggers Princess cutscene task dispatcher</text>

  <text x="52" y="505" class="txt-bold" fill="#F59E0B">3. Diagnostic Marker</text>
  <text x="320" y="505" class="txt-code-bold" fill="#38BDF8">LDA #$85; STA $07FF</text>
  <text x="610" y="505" class="subtitle">Asserts diagnostic marker byte ($85)</text>

  <text x="52" y="540" class="txt-bold" fill="#F59E0B">4. Victory Dispatch Jump</text>
  <text x="320" y="540" class="txt-code-bold" fill="#38BDF8">JMP $E525</text>
  <text x="610" y="540" class="subtitle">Jumps directly into SMB1 victory &amp; princess credits routine</text>
</svg>
"""
    with open(output_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated SVG Hero diagram: {output_svg}")

if __name__ == '__main__':
    out_dir = "docs/assets"
    os.makedirs(out_dir, exist_ok=True)
    create_hero_svg(os.path.join(out_dir, "hero_ace_diagram.svg"))
