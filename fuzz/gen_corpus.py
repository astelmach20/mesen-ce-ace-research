#!/usr/bin/env python3
"""Generate mutated NES ROMs derived from Super Mario Bros. (Japan, USA).nes

Strategies:
  1. Header-only mutations (mapper ID, NES 2.0 fields, mirroring, battery, sizes)
  2. PRG mutations (random byte flips, reset-vector redirects, chunk overwrites)
  3. CHR mutations
  4. Combined header+PRG mutations
"""

import os
import random
import struct
import sys
import zlib

SEED_ROM = "smb_mapper99.nes"
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "corpus"
COUNT = int(sys.argv[2]) if len(sys.argv) > 2 else 800
random.seed(0xBADC0DE)

os.makedirs(OUT_DIR, exist_ok=True)
data = bytearray(open(SEED_ROM, "rb").read())
assert data[:4] == b"NES\x1a"

header = data[:16]
prg = bytearray(data[16:16 + 0x8000])
chr_ = bytearray(data[16 + 0x8000:])

# Interesting mapper IDs to bias toward (common/complex mappers + homebrew with RAM)
INTERESTING_MAPPERS = [
    0, 1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 21, 22, 23, 24,
    25, 26, 28, 30, 31, 32, 33, 34, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
    75, 76, 77, 78, 79, 80, 82, 85, 87, 88, 90, 91, 92, 93, 94, 95, 96, 97, 99,
    100, 101, 105, 108, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122,
    123, 124, 125, 126, 127, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
    150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164,
    165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179,
    180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194,
    195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
    210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224,
    225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
    240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254,
    255, 268, 384, 423, 430,
]


def make_header(mapper, prg_count=2, chr_count=1, mirror=1, battery=0, trainer=0,
                nes20=False, submapper=0):
    h = bytearray(b"NES\x1a")
    h += bytes([prg_count, chr_count])
    b6 = (mirror & 1) | (battery << 1) | (trainer << 2) | ((mapper & 0x0F) << 4)
    if nes20:
        b7 = 0x08 | ((mapper >> 4) & 0x0F)
        b8 = (submapper << 4) | ((mapper >> 8) & 0x0F)
        b9 = 0
    else:
        b7 = ((mapper >> 4) & 0x0F) << 4
        b8 = 0
        b9 = 0
    h += bytes([b6, b7, b8, b9])
    h += bytes([0, 0, 0, 0, 0, 0])  # bytes 10-15
    return h


def save(name, h, prg_data, chr_data, trainer=None):
    out = bytearray(h)
    if trainer is not None:
        out += trainer
    out += prg_data
    out += chr_data
    path = os.path.join(OUT_DIR, name)
    with open(path, "wb") as f:
        f.write(out)
    return path


def mutate_prg(d, flips):
    p = bytearray(d)
    for _ in range(flips):
        off = random.randrange(len(p))
        p[off] ^= 1 << random.randrange(8)
    return p


def redirect_reset(d):
    p = bytearray(d)
    # Reset vector is at $7FFC/$7FFD in PRG (mapped to $FFFC/$FFFD).
    # Redirect into the middle of PRG so random data executes as code.
    target = random.randrange(0x200, 0x7800) & 0xFFFE
    p[0x7FFC] = target & 0xFF
    p[0x7FFD] = target >> 8
    # Also scramble NMI/IRQ vectors
    for v in (0x7FFA, 0x7FFE):
        t = random.randrange(0x100, 0x7F00) & 0xFFFE
        p[v] = t & 0xFF
        p[v + 1] = t >> 8
    return p


def chunk_overwrite(d):
    p = bytearray(d)
    start = random.randrange(0, len(p) - 0x40)
    length = random.choice([0x10, 0x40, 0x100, 0x400, 0x1000])
    p[start:start + length] = bytes(random.randrange(256) for _ in range(length))
    return p


names = set()


def unique_name(tag, i):
    n = f"{tag}_{i:05d}.nes"
    names.add(n)
    return n


i = 0

# 1) Header mapper mutations (keep original PRG/CHR)
for m in INTERESTING_MAPPERS:
    if i >= COUNT:
        break
    h = make_header(m)
    save(unique_name("map", i), h, prg, chr_)
    i += 1

# 2) NES 2.0 header variants
nes20_fields = [
    (2, 1, 0),        # normal
    (2, 1, 0x0F),     # PRG size exponent mode
    (0xFF, 0xFF, 0),  # huge counts
    (2, 0, 0),        # no CHR ROM
    (1, 1, 0),        # small PRG
    (0, 0, 0),        # zero
]
while i < COUNT and i < 200:
    prg_count, chr_count, b9 = random.choice(nes20_fields)
    mapper = random.choice(INTERESTING_MAPPERS)
    h = make_header(mapper, prg_count=prg_count, chr_count=chr_count, nes20=True)
    h[9] = b9
    h[10] = random.choice([0, 1, 0x0F, 0xF0, 0xFF])  # PRG RAM sizes
    h[11] = random.choice([0, 1, 0x0F, 0xF0, 0xFF])  # CHR RAM sizes
    save(unique_name("nes20", i), h, prg, chr_)
    i += 1

# 3) PRG mutations
while i < COUNT and i < 500:
    variant = random.randrange(3)
    if variant == 0:
        p = mutate_prg(prg, random.choice([1, 2, 4, 8, 16, 32]))
    elif variant == 1:
        p = redirect_reset(prg)
    else:
        p = chunk_overwrite(prg)
    h = make_header(random.choice([0, 0, 0, 1, 2, 4, 7]))
    save(unique_name("prg", i), h, p, chr_)
    i += 1

# 4) CHR mutations
while i < COUNT and i < 600:
    c = bytearray(chr_)
    for _ in range(random.choice([4, 16, 64, 256])):
        c[random.randrange(len(c))] = random.randrange(256)
    h = make_header(random.choice([0, 0, 1, 2, 4]))
    save(unique_name("chr", i), h, prg, c)
    i += 1

# 5) Combined mapper + PRG mutations
while i < COUNT:
    m = random.choice(INTERESTING_MAPPERS)
    variant = random.randrange(3)
    if variant == 0:
        p = mutate_prg(prg, random.choice([2, 8, 16]))
    elif variant == 1:
        p = redirect_reset(prg)
    else:
        p = chunk_overwrite(prg)
    h = make_header(m)
    save(unique_name("comb", i), h, p, chr_)
    i += 1

print(f"generated {i} mutants in {OUT_DIR}")
