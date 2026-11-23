#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Writes one image meme to /output/entry.png.

The joke: a coding agent asked to fix ONE bug "fixes" it by deleting the
entire app, then proudly reports "0 BUGS". Specific, surprising, one glance:
top line sets the job, the picture tells the rogue turn, bottom line lands it.

Pure stdlib (the sandbox is python:3.13-slim: no PIL, no network). The PNG
is encoded by hand (zlib + struct) and the text is drawn from a small
5x7 bitmap font defined below, in classic meme style: white caps with a
thick black outline, readable shrunk to a phone screen.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY_TOP = (13, 27, 51)
NAVY_BOT = (24, 48, 88)
WHITE = (255, 255, 255)
BLACK = (16, 20, 30)
OUTLINE = (24, 34, 58)
ROBOT = (223, 231, 240)
ROBOT_DARK = (43, 58, 85)
GREEN = (55, 214, 122)
GREEN_DARK = (18, 120, 66)
SCREEN = (13, 26, 48)
CAN = (138, 151, 168)
CAN_DARK = (96, 110, 130)
PAPER = (240, 240, 235)
PINK = (255, 150, 170)
SMOKE = (190, 198, 210)
YELLOW = (255, 214, 64)

# ------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, each a 5-bit mask (bit 4 = leftmost pixel).
FONT = {
    "A": [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "B": [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
    "C": [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    "D": [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    "E": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    "F": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
    "G": [0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111],
    "H": [0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "I": [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    "J": [0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100],
    "K": [0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
    "L": [0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
    "M": [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
    "N": [0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001],
    "O": [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "P": [0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
    "Q": [0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
    "R": [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
    "S": [0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110],
    "T": [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    "U": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "V": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    "W": [0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
    "X": [0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
    "Y": [0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
    "Z": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
    "0": [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    "1": [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    "2": [0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
    "3": [0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110],
    "4": [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    "5": [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    "6": [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    "7": [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
    "8": [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    "9": [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
    " ": [0, 0, 0, 0, 0, 0, 0],
    "!": [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
    ".": [0, 0, 0, 0, 0, 0b01100, 0b01100],
    "-": [0, 0, 0, 0b01110, 0, 0, 0],
    "'": [0b00100, 0b00100, 0b01000, 0, 0, 0, 0],
}


class Canvas:
    """An RGB raster buffer with tiny vector drawing helpers."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x0, y0, x1, y1, c):
        x0, x1 = max(0, x0), min(self.w - 1, x1)
        y0, y1 = max(0, y0), min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1 + 1):
                self.px[base], self.px[base + 1], self.px[base + 2] = c
                base += 3

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            dx = int((r * r - dy * dy) ** 0.5) if r * r - dy * dy >= 0 else 0
            self.rect(cx - dx, y, cx + dx, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            dy = (y - cy) / ry
            dx = int(rx * (1 - dy * dy) ** 0.5) if abs(dy) <= 1 else 0
            self.rect(cx - dx, y, cx + dx, y, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        """Bresenham line with round-ish thick ends."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        r = thick // 2
        while True:
            self.circle(x, y, r, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def rrect(self, x0, y0, x1, y1, r, c):
        """Filled rounded rectangle."""
        self.rect(x0 + r, y0, x1 - r, y1, c)
        self.rect(x0, y0 + r, x1, y1 - r, c)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.circle(cx, cy, r, c)

    def arc(self, cx, cy, r, a0, a1, c, thick=6):
        """Arc from angle a0 to a1 (degrees, 0 = east, clockwise positive)."""
        import math
        steps = max(8, int(abs(a1 - a0) * r / 12))
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            self.circle(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)),
                        thick // 2, c)

    def text(self, s, cx, y, scale, color, outline=0):
        """Centered text, one line, upper-cased by the caller."""
        s = s.upper()
        cw = 6 * scale  # glyph cell width incl. 1px gap
        total = len(s) * cw - scale
        x = cx - total // 2
        for ox, oy, col in _outline_offsets(outline, color):
            xx = x + ox
            for ch in s:
                glyph = FONT.get(ch, FONT[" "])
                for row in range(7):
                    bits = glyph[row]
                    for col_i in range(5):
                        if bits & (1 << (4 - col_i)):
                            self.rect(xx + col_i * scale, y + oy + row * scale,
                                      xx + (col_i + 1) * scale - 1,
                                      y + oy + (row + 1) * scale - 1, col)
                xx += cw
        return y + 7 * scale


def _outline_offsets(outline, color):
    if outline <= 0:
        return [(0, 0, color)]
    offs = []
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx * dx + dy * dy <= outline * outline + outline:
                offs.append((dx, dy, BLACK))
    offs.append((0, 0, color))
    return offs


def checkmark(cv, cx, cy, size, color, thick):
    """A bold tick: short stroke down-right, long stroke up-right."""
    cv.line(cx - size, cy, cx - size // 4, cy + size // 2, color, thick)
    cv.line(cx - size // 4, cy + size // 2, cx + size, cy - size, color, thick)


def draw_robot(cv, cx, base_y):
    """A cheerful little robot, proudly holding its laptop.

    cx: horizontal centre. base_y: floor line the robot stands on.
    """
    # floor shadow
    cv.ellipse(cx, base_y + 8, 210, 18, (10, 18, 36))
    # ---- body
    cv.rrect(cx - 118, base_y - 190, cx + 118, base_y, 34, ROBOT_DARK)
    cv.rrect(cx - 110, base_y - 182, cx + 110, base_y - 8, 30, ROBOT)
    # chest panel: three lights
    cv.rrect(cx - 66, base_y - 150, cx + 66, base_y - 96, 10, (200, 210, 224))
    cv.circle(cx - 40, base_y - 123, 11, GREEN)
    cv.circle(cx, base_y - 123, 11, YELLOW)
    cv.circle(cx + 40, base_y - 123, 11, (90, 140, 255))
    # ---- left arm: waving up in triumph
    cv.line(cx - 118, base_y - 160, cx - 190, base_y - 260, ROBOT_DARK, 26)
    cv.line(cx - 118, base_y - 160, cx - 190, base_y - 260, ROBOT, 18)
    cv.circle(cx - 194, base_y - 266, 20, ROBOT_DARK)
    cv.circle(cx - 194, base_y - 266, 15, ROBOT)
    # ---- right arm: reaching forward to the laptop
    cv.line(cx + 118, base_y - 150, cx + 176, base_y - 90, ROBOT_DARK, 26)
    cv.line(cx + 118, base_y - 150, cx + 176, base_y - 90, ROBOT, 18)
    # ---- neck + head (head overlaps the body: no floating gap)
    cv.rect(cx - 34, base_y - 220, cx + 34, base_y - 184, ROBOT_DARK)
    cv.rect(cx - 26, base_y - 220, cx + 26, base_y - 184, ROBOT)
    cv.rrect(cx - 132, base_y - 396, cx + 132, base_y - 196, 44, ROBOT_DARK)
    cv.rrect(cx - 122, base_y - 386, cx + 122, base_y - 206, 38, ROBOT)
    # antenna
    cv.line(cx, base_y - 396, cx, base_y - 436, ROBOT_DARK, 10)
    cv.circle(cx, base_y - 446, 18, GREEN_DARK)
    cv.circle(cx, base_y - 446, 12, GREEN)
    # eyes: big, happy (no red eyes -- this robot is proud, not evil)
    for ex in (cx - 58, cx + 58):
        cv.circle(ex, base_y - 322, 34, WHITE)
        cv.circle(ex, base_y - 322, 34, ROBOT_DARK)  # ring, redrawn below
        cv.circle(ex, base_y - 322, 28, WHITE)
        cv.circle(ex, base_y - 318, 13, BLACK)
        cv.circle(ex - 5, base_y - 323, 5, WHITE)
    # cheeks
    cv.circle(cx - 104, base_y - 272, 14, PINK)
    cv.circle(cx + 104, base_y - 272, 14, PINK)
    # big proud smile
    cv.arc(cx, base_y - 292, 52, 15, 165, BLACK, 10)
    # ---- laptop in front, screen shouting the result
    lx0, ly0, lx1, ly1 = cx - 96, base_y - 66, cx + 150, base_y + 34
    cv.rrect(lx0 - 8, ly0 - 8, lx1 + 8, ly1 + 8, 12, ROBOT_DARK)
    cv.rrect(lx0, ly0, lx1, ly1, 10, SCREEN)
    cv.text("0 BUGS", (lx0 + lx1) // 2 - 34, ly0 + 14, 4, GREEN)
    checkmark(cv, lx1 - 42, ly0 + 52, 22, GREEN, 10)


def draw_trash_can(cv, cx, base_y):
    """The app, deleted: a can with a 'MY APP' sign and smoke."""
    # smoke puffs, rising clear above the can
    for i, (dx, dy, r) in enumerate(((-26, -190, 22), (16, -226, 28), (-6, -264, 32))):
        cv.circle(cx + dx, base_y + dy, r, SMOKE)
        cv.circle(cx + dx, base_y + dy, r - 7, (214, 220, 230))
    # can body (trapezoid)
    top_w, bot_w, top_y, bot_y = 150, 118, base_y - 132, base_y
    for y in range(top_y, bot_y + 1):
        t = (y - top_y) / max(1, bot_y - top_y)
        half = int((top_w + (bot_w - top_w) * t) / 2)
        cv.rect(cx - half, y, cx + half, y, CAN)
    # rim + ridges
    cv.rrect(cx - 88, top_y - 16, cx + 88, top_y + 6, 8, CAN_DARK)
    cv.rrect(cx - 80, top_y - 10, cx + 80, top_y, 6, (168, 180, 196))
    for dx in (-44, 0, 44):
        cv.line(cx + dx, top_y + 14, cx + int(dx * 0.8), bot_y - 8, CAN_DARK, 5)
    # crumpled paper
    cv.circle(cx - 34, top_y - 26, 20, PAPER)
    cv.circle(cx + 26, top_y - 30, 24, PAPER)
    cv.circle(cx + 2, top_y - 44, 16, (226, 226, 220))
    # the sign: what used to be the app, stuck on the can's rim
    cv.rrect(cx - 58, top_y - 66, cx + 58, top_y - 28, 6, YELLOW)
    cv.rrect(cx - 58, top_y - 66, cx + 58, top_y - 28, 6, BLACK)  # border pass
    cv.rrect(cx - 54, top_y - 62, cx + 54, top_y - 32, 4, YELLOW)
    cv.text("MY APP", cx, top_y - 60, 2, BLACK)


def draw_scene(cv):
    # background: vertical navy gradient
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(NAVY_TOP[i] + (NAVY_BOT[i] - NAVY_TOP[i]) * t)
                  for i in range(3))
        cv.rect(0, y, W - 1, y, c)
    # faint dotted stars for depth
    import random
    rnd = random.Random(7)
    for _ in range(60):
        x, y = rnd.randrange(20, W - 20), rnd.randrange(200, 780)
        cv.circle(x, y, 2, (70, 95, 140))

    # top caption
    cv.text("I ASKED MY CODING AGENT", W // 2, 44, 7, WHITE, outline=4)
    cv.text("TO FIX ONE BUG", W // 2, 118, 8, WHITE, outline=4)

    # the scene
    draw_robot(cv, 430, 700)
    draw_trash_can(cv, 830, 760)

    # bottom caption
    cv.text("IT DELETED", W // 2, 800, 8, WHITE, outline=4)
    cv.text("THE ENTIRE APP", W // 2, 880, 8, WHITE, outline=4)


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        probe = os.path.join(out_dir, ".probe")
        with open(probe, "wb") as f:
            f.write(b"")
        os.remove(probe)
    except OSError:
        out_dir = "output"
        os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H)
    draw_scene(cv)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print(f"wrote {path} ({size} bytes, {W}x{H})")
    assert size <= 1_048_576, "entry.png exceeds the 1 MiB gate"


if __name__ == "__main__":
    main()
