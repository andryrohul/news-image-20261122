#!/usr/bin/env python3
"""THE SUNDAY WORLD - Sunday 22 November 2026 in one image.

A broadsheet front page drawn entirely in code with the Python standard
library only. No network, no files read, no timestamps: the same bytes
come out of every run. Writes $MAKEFUN_OUTPUT_DIR/entry.png (1024x1024).
"""
import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
PAPER2 = (244, 238, 222)
INK = (24, 24, 30)
INK2 = (70, 66, 60)
RED = (178, 30, 30)
REDDK = (140, 20, 20)
NAVY = (16, 36, 64)
GOLD = (176, 132, 30)
WHITE = (255, 255, 255)
SKY = (158, 198, 226)
SKYDK = (70, 110, 150)
NIGHT = (18, 28, 52)
SEA = (64, 130, 168)
SAND = (232, 214, 176)
GREY = (210, 206, 196)
GREYDK = (150, 144, 132)


def hsv(h, s, v):
    """One hue to RGB, all channels 0..255. h in degrees."""
    h = h % 360.0
    c = v * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0.0
    elif h < 120:
        r, g, b = x, c, 0.0
    elif h < 180:
        r, g, b = 0.0, c, x
    elif h < 240:
        r, g, b = 0.0, x, c
    elif h < 300:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def accent(n):
    """Story n (1..38) gets its own hue, spread round the wheel."""
    return hsv((n - 1) * (360.0 / 38.0) + 8.0, 0.78, 0.82)


def tint(c, f):
    """Mix colour c toward white by f (0..1)."""
    return (int(c[0] + (255 - c[0]) * f), int(c[1] + (255 - c[1]) * f),
            int(c[2] + (255 - c[2]) * f))


def shade(c, f):
    """Mix colour c toward black by f (0..1)."""
    return (int(c[0] * (1 - f)), int(c[1] * (1 - f)), int(c[2] * (1 - f)))


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, int(x))
        y0 = max(0, int(y))
        x1 = min(self.w, int(x + w))
        y1 = min(self.h, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x0, x1, y, c, t=1):
        for t2 in range(t):
            for x in range(int(x0), int(x1) + 1):
                self.set(x, int(y) + t2, c)

    def vline(self, x, y0, y1, c, t=1):
        for t2 in range(t):
            for y in range(int(y0), int(y1) + 1):
                self.set(int(x) + t2, y, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = x1 - x0
        dy = y1 - y0
        n = max(abs(dx), abs(dy), 1)
        for i in range(n + 1):
            x = int(round(x0 + dx * i / n))
            y = int(round(y0 + dy * i / n))
            if t > 1:
                self.fill(x - t // 2, y - t // 2, t, t, c)
            else:
                self.set(x, y, c)

    def rect(self, x, y, w, h, c, t=1):
        self.hline(x, x + w - 1, y, c, t)
        self.hline(x, x + w - 1, y + h - 1, c, t)
        self.vline(x, y, y + h - 1, c, t)
        self.vline(x + w - 1, y, y + h - 1, c, t)

    def circle(self, cx, cy, r, c, fill=True):
        r = int(r)
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            if fill:
                self.hline(cx - dx, cx + dx, cy + dy, c)
            else:
                self.set(cx - dx, cy + dy, c)
                self.set(cx + dx, cy + dy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-int(ry), int(ry) + 1):
            f = 1.0 - (dy * dy) / max(1.0, ry * ry)
            dx = int(rx * math.sqrt(max(0.0, f)))
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def poly(self, pts, c):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0 = max(0, int(math.ceil(min(ys))))
        y1 = min(self.h - 1, int(math.floor(max(ys))))
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, y0p = pts[i]
                x1, y1p = pts[(i + 1) % n]
                if (y0p <= y < y1p) or (y1p <= y < y0p):
                    t = (y - y0p) / (y1p - y0p)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(int(math.ceil(xs[k])), int(math.floor(xs[k + 1])), y, c)

    def tri(self, a, b, cc, c):
        self.poly([a, b, cc], c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for a in range(360):
                x = int(round(cx + rr * math.cos(math.radians(a))))
                y = int(round(cy + rr * math.sin(math.radians(a))))
                self.set(x, y, c)


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ------------------------------------------------------------- vector font
# 5x7 bitmap glyphs, '#' = on. Written fresh for this entry.
FONT = {
"A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
"B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
"C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
"D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
"E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
"F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
"G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
"H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
"I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
"J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
"K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
"L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
"M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
"N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
"O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
"P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
"Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
"R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
"S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
"T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
"U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
"V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
"W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
"X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
"Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
"Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
"0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
"1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
"2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
"3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
"4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
"5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
"6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
"7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
"8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
"9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
}

FONT.update({
"a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
"b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
"c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
"d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
"e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
"f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
"g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
"h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
"i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
"j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
"k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
"l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
"m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
"n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
"o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
"p": ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
"q": ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
"r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
"s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
"t": ("01000", "01000", "11110", "01000", "01000", "01001", "00110"),
"u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
"v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
"w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
"x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
"y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
"z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
" ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
"!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
"?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
"-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
"'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
'"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
"(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
"/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
"%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
"&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
"+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
"=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
"*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
"#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
"@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
"_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
"[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
"]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
"<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
"$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
"|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
})


def _glyph_span(ch):
    g = FONT.get(ch)
    if g is None:
        return 0, 5
    lo, hi = 5, -1
    for row in g:
        for i, c in enumerate(row):
            if c == "1":
                lo = min(lo, i)
                hi = max(hi, i)
    if hi < 0:
        return 0, 0
    return lo, hi


def text_width(s, size):
    """Width in px of string s at cap-height size."""
    u = size / 7.0
    w = 0.0
    for ch in s:
        lo, hi = _glyph_span(ch)
        if hi < 0:
            w += 3.0 * u
        else:
            w += (hi - lo + 2) * u
    return w - u if s else 0.0


def draw_text(cv, x, y, s, size, color, align="left"):
    """Draw string s, top-left (x, y), cap height = size px."""
    if align == "center":
        x = x - text_width(s, size) / 2.0
    elif align == "right":
        x = x - text_width(s, size)
    u = size / 7.0
    cx = float(x)
    bw = max(1, int(math.ceil(u)))
    # No bolding: strokes stay one cell wide so the text reads light.
    # Tiny pin numbers were never bolded either.
    wdt = bw
    for ch in s:
        g = FONT.get(ch)
        lo, hi = _glyph_span(ch)
        if g is not None and hi >= 0:
            for r in range(7):
                row = g[r]
                for ci in range(lo, hi + 1):
                    if row[ci] == "1":
                        px = int(round(cx + (ci - lo) * u))
                        py = int(round(y + r * u))
                        cv.fill(px, py, wdt, bw, color)
        cx += (hi - lo + 2) * u if hi >= 0 else 3.0 * u
    return cx


def wrap(s, size, maxw):
    """Greedy word wrap to a list of lines fitting maxw px."""
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_lines(cv, x, y, lines, size, color, lh=None, align="left"):
    if lh is None:
        lh = int(size * 1.18)
    for ln in lines:
        draw_text(cv, x, y, ln, size, color, align)
        y += lh
    return y


def chip(cv, x, y, n, c, d=20):
    """Numbered story chip: filled circle, white number."""
    cv.circle(x + d // 2, y + d // 2, d // 2, c)
    cv.circle(x + d // 2, y + d // 2, d // 2 - 2, c)
    num = str(n)
    sz = 11 if len(num) == 1 else 9
    draw_text(cv, x + d // 2, y + d // 2 - sz // 2 + 1, num, sz, WHITE, "center")


def flame(cv, x, y, s, c1=(232, 110, 20), c2=(245, 190, 40)):
    """A flame of height s, base at (x, y)."""
    cv.poly([(x, y), (x + s * 0.22, y - s * 0.55), (x + s * 0.42, y - s * 0.28),
             (x + s * 0.55, y - s * 0.85), (x + s * 0.75, y - s * 0.35),
             (x + s * 0.95, y - s * 0.55), (x + s, y)], c1)
    cv.poly([(x + s * 0.3, y), (x + s * 0.42, y - s * 0.3),
             (x + s * 0.55, y - s * 0.12), (x + s * 0.68, y - s * 0.38),
             (x + s * 0.72, y)], c2)


def smoke(cv, x, y, c=(150, 144, 132)):
    cv.circle(x, y, 5, c)
    cv.circle(x + 7, y - 6, 6, c)
    cv.circle(x + 14, y - 13, 7, c)
    cv.circle(x + 22, y - 20, 6, tint(c, 0.35))


def burst(cv, cx, cy, r, c1=(245, 190, 40), c2=(232, 110, 20)):
    """Explosion starburst: 8 spikes + centre."""
    for k in range(8):
        a = math.radians(k * 45 + 12)
        a2 = math.radians(k * 45 + 34)
        cv.tri((cx, cy),
               (int(cx + r * math.cos(a)), int(cy + r * math.sin(a))),
               (int(cx + r * 0.45 * math.cos(a2)), int(cy + r * 0.45 * math.sin(a2))), c1)
    cv.circle(cx, cy, max(3, r // 3), c2)


def waves(cv, x, y, w, c, n=3):
    for k in range(n):
        xx = x + k * (w // n)
        cv.line(xx, y + 4, xx + 8, y, c, 2)
        cv.line(xx + 8, y, xx + 16, y + 4, c, 2)

# ------------------------------------------------------------ hero scenes
def scene_cop31(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, (214, 232, 240))
    cv.circle(x + w - 34, y + 20, 13, (245, 196, 66))
    for k in range(8):
        a = math.radians(k * 45)
        cv.line(x + w - 34 + int(17 * math.cos(a)), y + 20 + int(17 * math.sin(a)),
                x + w - 34 + int(23 * math.cos(a)), y + 20 + int(23 * math.sin(a)),
                (245, 196, 66), 2)
    cv.circle(x + 34, y + 26, 20, SEA)
    cv.ellipse(x + 28, y + 22, 9, 5, (96, 168, 92))
    cv.ellipse(x + 40, y + 32, 8, 4, (96, 168, 92))
    cv.fill(x + 6, y + h - 26, w - 12, 20, (120, 84, 52))
    cv.fill(x + 6, y + h - 30, w - 12, 5, (150, 112, 72))
    for i, dc in enumerate([(178, 30, 30), (30, 90, 160), (30, 120, 70),
                            (176, 132, 30), (120, 60, 140)]):
        dx = x + 22 + i * (w - 44) // 4
        cv.circle(dx, y + h - 40, 7, dc)
        cv.fill(dx - 7, y + h - 33, 14, 8, dc)
        cv.fill(dx - 10, y + h - 26, 20, 4, WHITE)
    cv.fill(x + w // 2 - 26, y + h - 24, 52, 14, WHITE)
    cv.rect(x + w // 2 - 26, y + h - 24, 52, 14, INK)
    draw_text(cv, x + w // 2, y + h - 22, "DEAL", 10, REDDK, "center")
    cv.line(x + 60, y + 8, x + 96, y + 8, c, 2)
    cv.line(x + 104, y + 8, x + 118, y + 8, c, 2)


def scene_kyiv(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, NIGHT)
    for sx, sy in [(14, 10), (60, 18), (120, 8), (200, 14), (260, 9), (300, 20),
                   (90, 26), (170, 6), (235, 24)]:
        cv.circle(x + sx, y + sy, 1, WHITE)
    for bx, bw, bh in [(8, 46, 34), (60, 38, 46), (104, 52, 30), (162, 40, 50),
                       (208, 48, 36), (262, 44, 42)]:
        cv.fill(x + bx, y + h - bh, bw, bh, (10, 16, 32))
        for wy in range(y + h - bh + 5, y + h - 4, 9):
            for wx in range(x + bx + 5, x + bx + bw - 4, 10):
                cv.fill(wx, wy, 3, 4, (245, 196, 66))
    burst(cv, x + 84, y + h - 52, 14)
    burst(cv, x + 232, y + h - 44, 11, (255, 220, 90), (245, 140, 30))
    smoke(cv, x + 84, y + h - 66)
    smoke(cv, x + 232, y + h - 58)
    cv.line(x + 150, y + 12, x + 190, y + 34, (255, 220, 90), 2)
    cv.line(x + 196, y + 38, x + 226, y + 56, (255, 220, 90), 2)
    for dx, dy in [(30, 22), (150, 10), (270, 16), (110, 30)]:
        cv.circle(x + dx, y + dy, 3, WHITE)
        cv.circle(x + dx, y + dy, 1, INK)
        cv.line(x + dx - 12, y + dy, x + dx - 4, y + dy, (200, 200, 210), 1)
    cv.line(x + 12, y + 30, x + 40, y + 30, (255, 120, 90), 2)
    cv.line(x + 46, y + 30, x + 58, y + 30, (255, 120, 90), 2)


def scene_bahrain(cv, x, y, w, h, c):
    # Pale sky, bright turquoise sea: ship, port and flames stay apart.
    cv.fill(x, y, w, h, (208, 228, 240))
    cv.circle(x + w - 28, y + 16, 11, (245, 196, 66))
    cv.fill(x, y + h - 20, w, 20, (84, 168, 198))
    waves(cv, x + 8, y + h - 12, w - 16, WHITE)
    # Port building, light stone with dark windows, on the left.
    cv.fill(x + 10, y + h - 56, 76, 36, (228, 212, 182))
    cv.rect(x + 10, y + h - 56, 76, 36, (150, 130, 100))
    cv.fill(x + 18, y + h - 48, 10, 10, (60, 70, 90))
    cv.fill(x + 34, y + h - 48, 10, 10, (60, 70, 90))
    cv.fill(x + 50, y + h - 48, 10, 10, (60, 70, 90))
    cv.fill(x + 18, y + h - 32, 10, 8, (60, 70, 90))
    cv.fill(x + 66, y + h - 32, 10, 8, (60, 70, 90))
    flame(cv, x + 20, y + h - 54, 24)
    flame(cv, x + 54, y + h - 54, 18)
    smoke(cv, x + 28, y + h - 76)
    # Tanker, dark navy hull with white bridge and red stripe, right.
    cv.poly([(x + w - 168, y + h - 38), (x + w - 24, y + h - 38),
             (x + w - 36, y + h - 16), (x + w - 156, y + h - 16)], (28, 44, 70))
    cv.line(x + w - 164, y + h - 28, x + w - 28, y + h - 28, (200, 60, 50), 2)
    cv.fill(x + w - 150, y + h - 52, 30, 14, WHITE)
    cv.rect(x + w - 150, y + h - 52, 30, 14, INK)
    cv.fill(x + w - 146, y + h - 48, 6, 6, SKYDK)
    cv.fill(x + w - 134, y + h - 48, 6, 6, SKYDK)
    cv.fill(x + w - 112, y + h - 50, 8, 12, (60, 60, 66))
    flame(cv, x + w - 108, y + h - 38, 16)
    smoke(cv, x + w - 100, y + h - 62)
    cv.line(x + 120, y + 12, x + 150, y + 12, c, 2)
    cv.line(x + 156, y + 12, x + 168, y + 12, c, 2)


# ------------------------------------------------------- secondary scenes
def scene_sparta(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x, y + h - 14, w, 14, SEA)
    waves(cv, x + 4, y + h - 8, w - 8, tint(SEA, 0.4))
    cv.fill(x + 10, y + h - 30, 44, 12, (60, 60, 66))
    cv.fill(x + 14, y + h - 40, 18, 10, (200, 60, 40))
    cv.fill(x + 34, y + h - 40, 16, 10, (40, 90, 160))
    flame(cv, x + 16, y + h - 30, 16)
    smoke(cv, x + 20, y + h - 48)
    cv.circle(x + w - 12, y + 8, 2, INK)
    cv.line(x + w - 26, y + 8, x + w - 14, y + 8, INK, 1)


def scene_kryvyi(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x + 6, y + 8, 18, h - 16, (90, 88, 96))
    cv.fill(x + 28, y + 14, 18, h - 22, (70, 68, 76))
    cv.fill(x + 48, y + 6, 14, h - 14, (110, 106, 114))
    for bx in (6, 28, 48):
        for wy in range(y + 12, y + h - 8, 8):
            cv.fill(x + bx + 4, wy, 4, 4, (245, 196, 66))
    burst(cv, x + 37, y + 20, 10)
    smoke(cv, x + 37, y + 6)
    cv.line(x + 4, y + h - 4, x + w - 4, y + h - 4, INK2, 2)


def scene_bayelsa(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x, y + h - 16, w, 16, SEA)
    waves(cv, x + 4, y + h - 9, w - 8, tint(SEA, 0.4))
    cv.poly([(x + 10, y + h - 14), (x + 54, y + h - 14),
             (x + 48, y + h - 26), (x + 16, y + h - 26)], (120, 70, 40))
    cv.circle(x + 18, y + h - 12, 3, (240, 200, 170))
    cv.circle(x + 46, y + h - 10, 3, (240, 200, 170))
    cv.ring(x + w - 12, y + 10, 7, RED, 2)
    cv.line(x + 8, y + 10, x + 20, y + 10, c, 2)
    cv.line(x + 24, y + 10, x + 32, y + 10, c, 2)


def scene_jerusalem(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x + 8, y + h - 22, w - 16, 18, (226, 214, 186))
    cv.circle(x + w // 2, y + h - 22, 9, (176, 132, 30))
    for cx in (16, 26, 38, 48):
        cv.fill(x + cx, y + h - 20, 3, 16, (176, 132, 30))
    cv.circle(x + 20, y + 8, 4, (60, 60, 90))
    cv.circle(x + 44, y + 8, 4, (90, 60, 60))
    cv.fill(x + 16, y + 12, 8, 10, (60, 60, 90))
    cv.fill(x + 40, y + 12, 8, 10, (90, 60, 60))
    cv.line(x + 24, y + 16, x + 40, y + 16, INK, 2)
    cv.line(x + 30, y + 4, x + 36, y + 4, c, 2)
    cv.line(x + 40, y + 4, x + 46, y + 4, c, 2)


def scene_gaza(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x, y + h - 8, w, 8, SAND)
    cv.fill(x + 6, y + 16, 30, 14, (200, 190, 170))
    cv.fill(x + 36, y + 20, 12, 10, (150, 40, 40))
    cv.circle(x + 14, y + 32, 4, INK)
    cv.circle(x + 30, y + 32, 4, INK)
    cv.circle(x + 42, y + 32, 4, INK)
    cv.fill(x + 8, y + 8, 10, 8, (176, 132, 30))
    cv.fill(x + 20, y + 8, 10, 8, (120, 140, 90))
    cv.line(x + 52, y + 8, x + 52, y + 22, INK, 2)
    cv.fill(x + 52, y + 4, 12, 8, WHITE)
    cv.line(x + 55, y + 6, x + 61, y + 6, RED, 2)
    cv.line(x + 58, y + 5, x + 58, y + 9, RED, 2)
    cv.line(x + 6, y + 36, x + 16, y + 36, c, 2)
    cv.line(x + 20, y + 36, x + 28, y + 36, c, 2)


def scene_sinaloa(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.poly([(x, y + h), (x + 18, y + 12), (x + 36, y + h)], (150, 110, 70))
    cv.poly([(x + 28, y + h), (x + 50, y + 6), (x + 64, y + h)], (120, 88, 56))
    cv.fill(x + 46, y + 4, 3, 4, WHITE)
    cv.fill(x + 8, y + 8, 20, 7, (40, 44, 52))
    cv.fill(x + 28, y + 10, 6, 5, (40, 44, 52))
    cv.line(x + 4, y + 8, x + 34, y + 8, INK, 2)
    cv.line(x + 14, y + 4, x + 14, y + 16, INK, 1)
    for k in range(5):
        a = math.radians(k * 72 - 90)
        cv.line(x + w - 12, y + h - 12,
                x + w - 12 + int(9 * math.cos(a)), y + h - 12 + int(9 * math.sin(a)),
                GOLD, 2)
    cv.circle(x + w - 12, y + h - 12, 3, GOLD)
    cv.line(x + 8, y + h - 6, x + 20, y + h - 6, c, 2)
    cv.line(x + 24, y + h - 6, x + 32, y + h - 6, c, 2)


def scene_tehran(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.line(x + 12, y + h, x + 20, y + 6, INK, 2)
    cv.line(x + 28, y + h, x + 20, y + 6, INK, 2)
    cv.line(x + 8, y + 14, x + 32, y + 14, INK, 2)
    cv.line(x + 12, y + 24, x + 28, y + 24, INK, 2)
    cv.line(x + 4, y + 10, x + 12, y + 6, INK, 1)
    cv.line(x + 36, y + 10, x + 28, y + 6, INK, 1)
    cv.fill(x + 38, y + 12, 20, h - 18, (70, 68, 76))
    for wy in range(y + 16, y + h - 6, 8):
        cv.fill(x + 42, wy, 4, 4, (90, 88, 96))
    cv.circle(x + w - 8, y + 10, 6, (200, 200, 190))
    cv.line(x + w - 12, y + 6, x + w - 4, y + 14, RED, 2)
    cv.line(x + w - 4, y + 6, x + w - 12, y + 14, RED, 2)


def scene_nvidia(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x + 8, y + 10, 24, 24, (30, 40, 50))
    cv.fill(x + 14, y + 16, 12, 12, c)
    for k in range(3):
        cv.fill(x + 4, y + 16 + k * 7, 4, 3, GOLD)
        cv.fill(x + 32, y + 16 + k * 7, 4, 3, GOLD)
    cv.ring(x + 44, y + 28, 10, INK, 2)
    cv.line(x + 51, y + 35, x + 58, y + 42, INK, 3)
    cv.line(x + 14, y + h - 6, x + 24, y + h - 12, RED, 2)
    cv.line(x + 24, y + h - 12, x + 34, y + h - 6, RED, 2)
    cv.line(x + 34, y + h - 6, x + 44, y + h - 14, RED, 2)
    cv.line(x + 44, y + h - 14, x + 44, y + h - 18, RED, 2)
    cv.line(x + 40, y + h - 15, x + 44, y + h - 18, RED, 2)
    cv.line(x + 48, y + h - 15, x + 44, y + h - 18, RED, 2)


def scene_bolsonaro(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x + 6, y + 6, 34, h - 12, WHITE)
    cv.rect(x + 6, y + 6, 34, h - 12, INK)
    cv.fill(x + 18, y + 8, 10, 10, RED)
    cv.fill(x + 21, y + 5, 4, 16, WHITE)
    cv.fill(x + 15, y + 11, 16, 4, WHITE)
    for wy in range(y + 22, y + h - 6, 8):
        cv.fill(x + 10, wy, 8, 5, SKYDK)
        cv.fill(x + 24, wy, 8, 5, SKYDK)
    cv.fill(x + 44, y + h - 14, 18, 8, (120, 140, 160))
    cv.circle(x + 48, y + h - 16, 3, (240, 200, 170))
    cv.fill(x + 44, y + h - 22, 18, 3, WHITE)
    cv.line(x + 46, y + 10, x + 50, y + 14, c, 2)
    cv.line(x + 50, y + 14, x + 54, y + 8, c, 2)
    cv.line(x + 54, y + 8, x + 58, y + 12, c, 2)


def scene_aukus(cv, x, y, w, h, c):
    cv.fill(x, y, w, h, tint(c, 0.82))
    cv.fill(x, y + h - 14, w, 14, SEA)
    waves(cv, x + 4, y + h - 8, w - 8, tint(SEA, 0.4))
    cv.ellipse(x + 30, y + h - 20, 22, 8, (50, 56, 64))
    cv.fill(x + 24, y + h - 30, 10, 8, (50, 56, 64))
    cv.line(x + 28, y + h - 30, x + 28, y + h - 36, INK, 2)
    cv.circle(x + 14, y + h - 20, 2, (245, 196, 66))
    cv.fill(x + 44, y + 6, 18, 22, WHITE)
    cv.rect(x + 44, y + 6, 18, 22, INK)
    cv.line(x + 48, y + 12, x + 58, y + 24, RED, 2)
    cv.line(x + 58, y + 12, x + 48, y + 24, RED, 2)
    cv.line(x + 8, y + 10, x + 18, y + 10, c, 2)
    cv.line(x + 22, y + 10, x + 30, y + 10, c, 2)

# ------------------------------------------------------ also-on pictograms
# Each draws a different tiny picture in a 14x14 box at (x, y).
def ic_db(cv, x, y, c):
    cv.ellipse(x + 7, y + 3, 6, 3, c)
    cv.fill(x + 1, y + 3, 12, 8, c)
    cv.ellipse(x + 7, y + 11, 6, 3, shade(c, 0.25))
    cv.line(x + 4, y + 6, x + 10, y + 6, WHITE, 1)
    cv.line(x + 9, y + 1, x + 6, y + 7, (245, 190, 40), 2)
    cv.line(x + 6, y + 7, x + 9, y + 7, (245, 190, 40), 2)
    cv.line(x + 9, y + 7, x + 5, y + 13, (245, 190, 40), 2)


def ic_game(cv, x, y, c):
    cv.fill(x + 1, y + 4, 12, 7, c)
    cv.circle(x + 4, y + 7, 2, WHITE)
    cv.fill(x + 9, y + 6, 3, 1, WHITE)
    cv.fill(x + 10, y + 7, 1, 3, WHITE)
    cv.circle(x + 7, y + 2, 3, RED)
    cv.circle(x + 7, y + 2, 1, WHITE)


def ic_plane_out(cv, x, y, c):
    cv.tri((x + 1, y + 7), (x + 12, y + 3), (x + 9, y + 8), c)
    cv.tri((x + 1, y + 7), (x + 9, y + 8), (x + 6, y + 12), c)
    cv.line(x + 10, y + 11, x + 13, y + 11, RED, 2)
    cv.line(x + 13, y + 8, x + 13, y + 14, RED, 2)
    cv.line(x + 13, y + 8, x + 10, y + 9, RED, 2)
    cv.line(x + 13, y + 14, x + 10, y + 13, RED, 2)


def ic_house_fire(cv, x, y, c):
    cv.tri((x, y + 7), (x + 7, y + 1), (x + 14, y + 7), c)
    cv.fill(x + 2, y + 7, 10, 6, shade(c, 0.15))
    cv.fill(x + 6, y + 10, 3, 3, WHITE)
    flame(cv, x + 8, y + 6, 6)


def ic_candle(cv, x, y, c):
    cv.fill(x + 5, y + 6, 4, 7, WHITE)
    cv.rect(x + 5, y + 6, 4, 7, INK)
    cv.line(x + 7, y + 6, x + 7, y + 4, INK, 1)
    flame(cv, x + 5, y + 4, 5)
    cv.fill(x + 3, y + 13, 8, 1, GOLD)


def ic_car_fire(cv, x, y, c):
    cv.fill(x + 1, y + 8, 12, 4, c)
    cv.fill(x + 3, y + 5, 8, 3, c)
    cv.circle(x + 4, y + 12, 2, INK)
    cv.circle(x + 10, y + 12, 2, INK)
    flame(cv, x + 9, y + 5, 6)


def ic_rings(cv, x, y, c):
    cv.ring(x + 3, y + 4, 2, (40, 90, 180), 1)
    cv.ring(x + 7, y + 4, 2, (20, 20, 20), 1)
    cv.ring(x + 11, y + 4, 2, RED, 1)
    cv.ring(x + 5, y + 8, 2, GOLD, 1)
    cv.ring(x + 9, y + 8, 2, (30, 140, 70), 1)
    cv.line(x + 7, y + 11, x + 7, y + 13, c, 1)


def ic_deal(cv, x, y, c):
    cv.fill(x + 1, y + 3, 8, 10, WHITE)
    cv.rect(x + 1, y + 3, 8, 10, INK)
    cv.line(x + 3, y + 6, x + 7, y + 6, c, 1)
    cv.line(x + 3, y + 9, x + 7, y + 9, c, 1)
    cv.line(x + 9, y + 10, x + 11, y + 12, (30, 140, 70), 2)
    cv.line(x + 11, y + 12, x + 14, y + 7, (30, 140, 70), 2)
    cv.fill(x + 11, y + 1, 3, 3, RED)


def ic_rugby(cv, x, y, c):
    cv.ellipse(x + 7, y + 8, 6, 4, c)
    cv.line(x + 2, y + 8, x + 12, y + 8, WHITE, 1)
    cv.line(x + 3, y + 2, x + 3, y + 6, INK, 1)
    cv.line(x + 11, y + 2, x + 11, y + 6, INK, 1)
    cv.line(x + 3, y + 2, x + 11, y + 2, INK, 1)


def ic_trophy(cv, x, y, c):
    cv.fill(x + 4, y + 2, 6, 6, GOLD)
    cv.fill(x + 6, y + 8, 2, 3, GOLD)
    cv.fill(x + 4, y + 11, 6, 2, GOLD)
    cv.line(x + 2, y + 3, x + 4, y + 3, GOLD, 2)
    cv.line(x + 10, y + 3, x + 12, y + 3, GOLD, 2)
    cv.ellipse(x + 11, y + 12, 3, 2, c)


def ic_soccer(cv, x, y, c):
    cv.circle(x + 7, y + 7, 6, WHITE)
    cv.ring(x + 7, y + 7, 6, INK, 1)
    cv.poly([(x + 7, y + 4), (x + 10, y + 6), (x + 9, y + 10),
             (x + 5, y + 10), (x + 4, y + 6)], INK)
    cv.fill(x + 2, y + 2, 4, 2, c)
    cv.fill(x + 8, y + 2, 4, 2, c)


def ic_clock_ball(cv, x, y, c):
    cv.circle(x + 7, y + 7, 6, WHITE)
    cv.ring(x + 7, y + 7, 6, c, 1)
    cv.line(x + 7, y + 7, x + 7, y + 3, INK, 1)
    cv.line(x + 7, y + 7, x + 10, y + 7, INK, 1)
    cv.circle(x + 7, y + 7, 1, RED)


def ic_tennis(cv, x, y, c):
    cv.circle(x + 10, y + 10, 3, (200, 220, 60))
    cv.ring(x + 10, y + 10, 3, INK, 1)
    cv.ellipse(x + 5, y + 5, 4, 5, c)
    cv.ring(x + 5, y + 5, 4, INK, 1)
    cv.line(x + 5, y + 5, x + 5, y + 5, INK, 1)
    cv.line(x + 7, y + 9, x + 11, y + 13, INK, 2)


def ic_ballot(cv, x, y, c):
    cv.fill(x + 2, y + 6, 10, 7, c)
    cv.fill(x + 4, y + 3, 6, 3, shade(c, 0.2))
    cv.line(x + 5, y + 9, x + 7, y + 11, WHITE, 2)
    cv.line(x + 7, y + 11, x + 11, y + 7, WHITE, 2)


def ic_cricket(cv, x, y, c):
    cv.line(x + 3, y + 2, x + 7, y + 9, (200, 170, 110), 3)
    cv.line(x + 7, y + 9, x + 9, y + 12, (200, 170, 110), 3)
    cv.line(x + 11, y + 5, x + 11, y + 12, GOLD, 1)
    cv.line(x + 13, y + 5, x + 13, y + 12, GOLD, 1)
    cv.circle(x + 4, y + 12, 2, RED)


def ic_racecar(cv, x, y, c):
    cv.fill(x + 1, y + 7, 12, 4, c)
    cv.fill(x + 4, y + 4, 6, 3, c)
    cv.circle(x + 4, y + 11, 2, INK)
    cv.circle(x + 10, y + 11, 2, INK)
    cv.fill(x + 11, y + 1, 3, 3, INK)
    cv.fill(x + 11, y + 1, 1, 1, WHITE)
    cv.fill(x + 13, y + 3, 1, 1, WHITE)


def ic_factory(cv, x, y, c):
    cv.fill(x + 1, y + 7, 12, 6, (110, 110, 118))
    cv.fill(x + 2, y + 4, 3, 3, (110, 110, 118))
    cv.fill(x + 8, y + 3, 3, 4, (110, 110, 118))
    flame(cv, x + 5, y + 7, 7)
    smoke(cv, x + 3, y + 3)


def ic_bottle(cv, x, y, c):
    cv.fill(x + 5, y + 1, 4, 3, c)
    cv.fill(x + 3, y + 4, 8, 9, c)
    cv.fill(x + 5, y + 7, 4, 4, WHITE)
    cv.tri((x + 7, y + 2), (x + 2, y + 12), (x + 12, y + 12), (245, 190, 40))
    cv.line(x + 7, y + 5, x + 7, y + 9, INK, 1)
    cv.line(x + 5, y + 10, x + 9, y + 10, INK, 1)


def ic_flood(cv, x, y, c):
    cv.fill(x + 2, y + 2, 8, 5, (200, 120, 60))
    cv.tri((x + 1, y + 7), (x + 6, y + 2), (x + 11, y + 7), (200, 120, 60))
    cv.fill(x + 1, y + 9, 12, 4, SEA)
    waves(cv, x + 1, y + 10, 12, tint(SEA, 0.4), 1)
    cv.line(x + 3, y + 1, x + 2, y + 3, SKYDK, 1)
    cv.line(x + 11, y + 1, x + 10, y + 3, SKYDK, 1)


def ic_robot(cv, x, y, c):
    cv.fill(x + 3, y + 2, 8, 7, c)
    cv.fill(x + 5, y + 9, 4, 3, c)
    cv.circle(x + 5, y + 5, 1, WHITE)
    cv.circle(x + 9, y + 5, 1, WHITE)
    cv.line(x + 5, y + 7, x + 9, y + 7, INK, 1)
    cv.line(x + 7, y + 2, x + 7, y + 1, INK, 1)
    cv.line(x + 2, y + 12, x + 12, y + 12, RED, 2)
    cv.line(x + 2, y + 12, x + 5, y + 12, RED, 2)


def ic_missile(cv, x, y, c):
    cv.tri((x + 10, y + 1), (x + 13, y + 6), (x + 7, y + 6), c)
    cv.fill(x + 7, y + 6, 6, 5, c)
    cv.line(x + 4, y + 11, x + 7, y + 11, (245, 190, 40), 2)
    cv.line(x + 2, y + 12, x + 5, y + 12, (245, 190, 40), 2)
    cv.line(x + 1, y + 2, x + 5, y + 6, RED, 2)
    cv.line(x + 5, y + 6, x + 1, y + 10, RED, 2)


def ic_cedar(cv, x, y, c):
    cv.tri((x + 7, y + 1), (x + 2, y + 7), (x + 12, y + 7), c)
    cv.tri((x + 7, y + 4), (x + 3, y + 10), (x + 11, y + 10), c)
    cv.fill(x + 6, y + 10, 2, 3, (120, 84, 52))
    cv.line(x + 2, y + 13, x + 12, y + 13, (120, 84, 52), 1)


def ic_coins(cv, x, y, c):
    cv.ellipse(x + 5, y + 9, 5, 2, GOLD)
    cv.ellipse(x + 5, y + 7, 5, 2, GOLD)
    cv.ellipse(x + 5, y + 5, 5, 2, GOLD)
    cv.line(x + 10, y + 2, x + 10, y + 8, RED, 2)
    cv.line(x + 10, y + 8, x + 7, y + 5, RED, 2)
    cv.line(x + 10, y + 8, x + 13, y + 5, RED, 2)


def ic_swim(cv, x, y, c):
    cv.circle(x + 4, y + 4, 2, (240, 200, 170))
    cv.line(x + 4, y + 6, x + 9, y + 8, (240, 200, 170), 2)
    cv.line(x + 9, y + 8, x + 12, y + 6, (240, 200, 170), 2)
    cv.line(x + 9, y + 8, x + 13, y + 10, (240, 200, 170), 2)
    cv.fill(x + 1, y + 10, 12, 3, SEA)
    waves(cv, x + 1, y + 11, 12, tint(SEA, 0.4), 1)


def ic_breach(cv, x, y, c):
    cv.tri((x + 1, y + 5), (x + 10, y + 2), (x + 8, y + 6), c)
    cv.tri((x + 1, y + 5), (x + 8, y + 6), (x + 5, y + 9), c)
    for k in range(4):
        cv.line(x + 11 + k * 0, y + 1 + k * 3, x + 13, y + 2 + k * 3, RED, 1)
    cv.line(x + 12, y + 1, x + 12, y + 13, RED, 1)


ICONS = {14: ic_db, 15: ic_game, 16: ic_plane_out, 17: ic_house_fire,
         18: ic_candle, 19: ic_car_fire, 20: ic_rings, 21: ic_deal,
         22: ic_rugby, 23: ic_trophy, 24: ic_soccer, 25: ic_clock_ball,
         26: ic_tennis, 27: ic_ballot, 28: ic_cricket, 29: ic_racecar,
         30: ic_factory, 31: ic_bottle, 32: ic_flood, 33: ic_robot,
         34: ic_missile, 35: ic_cedar, 36: ic_coins, 37: ic_swim,
         38: ic_breach}

# -------------------------------------------------------------------- data
HEROES = [
    {"n": 1, "kicker": "CLIMATE - ANTALYA - REPORTED",
     "lines": ["COP31 NEARS", "FINAL DEAL"],
     "body": "200 nations race to a deal after a fossil-fuel row. (Reuters, BBC)",
     "scene": scene_cop31},
    {"n": 2, "kicker": "WAR - KYIV, UKRAINE - REPORTED",
     "lines": ["400 DRONES,", "110 MISSILES", "HIT UKRAINE"],
     "body": "One of the largest overnight attacks; 7 killed. (Al Jazeera)",
     "scene": scene_kyiv},
    {"n": 3, "kicker": "WAR - BAHRAIN - REPORTED",
     "lines": ["IRAN HITS", "US BASES IN", "BAHRAIN"],
     "body": "Site burns, no injuries; tankers hit in Hormuz. (Al Jazeera, CNA)",
     "scene": scene_bahrain},
]

SECONDARY = [
    {"n": 4, "head": "SPARTA II BURNS IN THE GULF",
     "body": "Suspected drone strike; Finland blames Ukraine. 16 crew safe. (Reuters, BBC)",
     "scene": scene_sparta},
    {"n": 5, "head": "STRIKE HITS ZELENSKYY'S HOME CITY",
     "body": "2 dead, 60 hurt in Kryvyi Rih strike. (Al Jazeera)",
     "scene": scene_kryvyi},
    {"n": 6, "head": "BOAT OF MOURNERS CAPSIZES",
     "body": "24 dead as boat carrying funeral mourners capsizes. (DW, Sky News)",
     "scene": scene_bayelsa},
    {"n": 7, "head": "EISENKOT INVITES LIKUD TO TALKS",
     "body": "He seeks the broadest possible government. (Straits Times)",
     "scene": scene_jerusalem},
    {"n": 8, "head": "STRIKE HITS FOOD AID VEHICLE",
     "body": "3 Palestinians die as strike hits food aid vehicle. (Al Jazeera, Reuters)",
     "scene": scene_gaza},
    {"n": 9, "head": "'EL CHAPO ISIDRO' CAPTURED",
     "body": "11 dead: 7 gunmen, 4 soldiers. (Sky News, BBC)",
     "scene": scene_sinaloa},
    {"n": 10, "head": "IRAN TO RATION ELECTRICITY",
     "body": "War damage hits energy network. (Straits Times)",
     "scene": scene_tehran},
    {"n": 11, "head": "NVIDIA FACES US ACCOUNTING PROBE",
     "body": "SEC inquiry is at an early stage. (Straits Times)",
     "scene": scene_nvidia},
    {"n": 12, "head": "BOLSONARO IN INTENSIVE CARE",
     "body": "Stable, breathing on his own. (Al Jazeera)",
     "scene": scene_bolsonaro},
    {"n": 13, "head": "MARLES REJECTS US AUKUS REPORT",
     "body": "He says the US budget office is wrong. (ABC)",
     "scene": scene_aukus},
]

ALSO = [
    (14, "FBI crime database hack probed (BBC)"),
    (15, "Teen gamer + mum help FBI save girl (BBC)"),
    (16, "Denmark expels Russian attache (Guardian)"),
    (17, "30 Awami League homes burned (TOI)"),
    (18, "Fred Nile, ex-NSW MP, dies at 92 (ABC)"),
    (19, "Bystanders save driver from car fire (ABC)"),
    (20, "Melbourne: 70 yrs since 1956 Games (ABC)"),
    (21, "EU-Indonesia sign deal after 10 yrs (DW)"),
    (22, "Rugby: England beat NZ 31-7 (Reuters)"),
    (23, "France beat Argentina, reach final (Reuters)"),
    (24, "Arsenal 2-2 Newcastle; Leeds win 4-1 (BBC)"),
    (25, "Liverpool host Man Utd today (AJ) FORECAST"),
    (26, "Zverev v Alcaraz in ATP final (TOI) FORECAST"),
    (27, "Hong Kong: 856 vie for 723 seats (China Daily)"),
    (28, "Cricket: India 720/9, record in NZ (AP)"),
    (29, "F1: Verstappen wins wild Las Vegas GP (AP)"),
    (30, "Iraq power station fire: 4 dead (State media)"),
    (31, "Toxic liquor kills 19 in Manipur (Xinhua)"),
    (32, "Florida river tops 73-yr record (Forecasters)"),
    (33, "Autonomous weapons talks end, no treaty (UN)"),
    (34, "Houthi missile 'intercepted' (Investing) CLAIM"),
    (35, "Aoun: Israel must leave, state to hold arms (AJ)"),
    (36, "President warns of 'silent economic war' (AJ)"),
    (37, "Lewis Pugh swims Hormuz as tanker hit (BBC)"),
    (38, "Moldova: Russian airspace breach (Kyiv)"),
]

# (lon, lat, dx, dy) pin positions on the map band
PINS = {
    1: (30.7, 36.9, 0, -9), 2: (30.5, 50.4, 11, -6), 3: (50.6, 26.2, 0, 9),
    4: (24.0, 59.8, -13, -8), 5: (33.4, 47.9, 13, 7), 6: (6.3, 4.9, 0, 0),
    7: (35.2, 31.8, -11, 7), 8: (34.5, 31.5, 9, -11), 9: (-107.4, 24.8, 0, 0),
    10: (51.4, 35.7, 11, -9), 11: (-77.0, 38.9, 0, -9), 12: (-47.9, -15.8, 0, 0),
    13: (149.1, -35.3, 0, 0), 14: (-98.0, 39.5, -15, 7), 15: (-87.0, 41.8, 13, -11),
    16: (12.6, 55.7, -9, -11), 17: (90.4, 23.8, 0, 0), 18: (151.2, -33.9, 0, -11),
    19: (115.9, -31.9, 0, 0), 20: (145.0, -37.8, 9, 9), 21: (106.8, -6.2, 0, 0),
    22: (-0.1, 51.5, -11, 9), 23: (2.35, 48.85, 9, -9), 24: (0.5, 51.5, 13, 11),
    25: (-3.0, 53.4, -13, -11), 26: (7.7, 45.07, 11, 9), 27: (114.2, 22.3, 0, 0),
    28: (174.8, -41.3, 0, 0), 29: (-115.14, 36.17, 0, 9), 30: (47.8, 30.5, -9, 11),
    31: (93.9, 24.8, -11, -9), 32: (-81.7, 28.0, 0, 0), 33: (6.14, 46.2, -11, 11),
    34: (46.7, 24.7, 9, -7), 35: (35.5, 33.9, -15, -9), 36: (53.0, 34.5, 9, 9),
    37: (56.3, 26.6, 0, -11), 38: (28.9, 47.0, -9, -11),
}

# Land as lon/lat boxes (lon0, lon1, lat0, lat1), drawn as a dot grid so
# the continents read as a newspaper dot map. Boxes overlap on purpose.
LAND = [
    (-168, -95, 55, 72), (-125, -67, 30, 55), (-117, -87, 15, 32),
    (-60, -20, 60, 83), (-79, -34, -56, -10), (-72, -38, -10, 11),
    (-11, 30, 36, 55), (5, 30, 55, 70), (-6, 2, 50, 59),
    (-17, 35, -35, 5), (-17, 32, 5, 32), (33, 51, 10, 32),
    (35, 60, 12, 32), (43, 60, 36, 42), (40, 100, 50, 72),
    (100, 180, 50, 72), (60, 100, 30, 50), (68, 90, 8, 35),
    (95, 108, 8, 30), (100, 122, 20, 40), (122, 141, 30, 45),
    (95, 105, 5, 20), (113, 154, -40, -10), (130, 150, -10, -2),
    (166, 178, -47, -34),
]

REGIONS = [("EUROPE", 11, (30, 90, 160)), ("MIDDLE EAST", 9, (178, 60, 30)),
           ("AMERICAS", 7, (30, 140, 70)), ("ASIA-PACIFIC", 5, (200, 120, 20)),
           ("OCEANIA", 4, (90, 60, 140)), ("AFRICA", 1, (180, 140, 20)),
           ("WORLD", 1, (100, 100, 100))]

DATE_CHECK = ("DATE CHECK - Wires read up to 00:50 UTC, Sunday 22 November 2026: "
              "every story here was reported or still developing on 22 November "
              "in at least one time zone. Left out as other days' news: the Peru "
              "earthquake (20 Nov), missiles in Poland (19 Nov), the Kerch Bridge "
              "strikes (earlier this week) and the Shenzhen summit (19 Nov).")


# -------------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, PAPER)
    cv.fill(0, 0, W, 6, RED)

    # masthead
    draw_text(cv, W // 2, 10, "THE SUNDAY WORLD", 33, INK, "center")
    cv.fill(W // 2 - 210, 50, 420, 2, RED)
    draw_text(cv, W // 2, 56, "SUNDAY 22 NOVEMBER 2026", 16, REDDK, "center")
    draw_text(cv, 14, 24, "SUNDAY EDITION", 12, INK2)
    draw_text(cv, W - 14, 24, "ONE DAY, WHOLE WORLD", 12, INK2, "right")

    # count strip
    cv.fill(0, 76, W, 20, NAVY)
    draw_text(cv, W // 2, 80, "38 STORIES - 7 REGIONS - EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
              13, WHITE, "center")

    # UTC timeline strip
    draw_text(cv, 10, 100, "SUNDAY IN UTC", 13, INK)
    bx0, bx1, by = 168, 1010, 110
    cv.line(bx0, by, bx1, by, INK2, 2)
    for hr in (0, 6, 12, 18, 24):
        tx = bx0 + (bx1 - bx0) * hr // 24
        cv.vline(tx, by - 4, by + 4, INK2, 2)
        draw_text(cv, tx, 116, "%02d" % hr, 9, INK2, "center")
    mx = bx0 + (bx1 - bx0) * 3 // 24
    cv.circle(mx, by, 5, RED)
    cv.circle(mx, by, 2, WHITE)
    draw_text(cv, mx + 10, 98, "03:00 GMT - COP31 OBJECTION DEADLINE", 11, REDDK)

    # heroes: three columns
    for i, st in enumerate(HEROES):
        x = 8 + i * 342
        w = 324
        y0 = 126
        c = accent(st["n"])
        cv.fill(x, y0, w, 4, c)
        cv.fill(x, y0 + 4, w, 232, WHITE)
        cv.rect(x, y0 + 4, w, 232, GREYDK)
        chip(cv, x + 8, y0 + 12, st["n"], c, 22)
        draw_text(cv, x + 36, y0 + 14, st["kicker"], 11, shade(c, 0.35))
        yy = y0 + 34
        for ln in st["lines"]:
            draw_text(cv, x + 10, yy, ln, 26, INK)
            yy += 30
        st["scene"](cv, x + 10, y0 + 126, w - 20, 76, c)
        bl = wrap(st["body"], 11, w - 20)
        draw_lines(cv, x + 10, y0 + 206, bl[:2], 11, INK2, 13)

    # region strip
    cv.fill(0, 362, W, 22, PAPER2)
    total = 0.0
    parts = []
    for name, cnt, col in REGIONS:
        parts.append((name + " " + str(cnt), col))
        total += text_width(name + " " + str(cnt), 12) + 26
    xx = (W - total) / 2.0
    for label, col in parts:
        cv.fill(int(xx), 363, 10, 10, col)
        draw_text(cv, xx + 14, 362, label, 12, INK)
        xx += text_width(label, 12) + 26

    # secondary: 2 columns x 5 rows, each with its own mini scene
    sec_y = 384
    row_h = 49
    for idx, st in enumerate(SECONDARY):
        col = idx % 2
        row = idx // 2
        x = 8 + col * 506
        y = sec_y + row * row_h
        c = accent(st["n"])
        cv.fill(x, y + 3, 62, 42, tint(c, 0.85))
        cv.rect(x, y + 3, 62, 42, tint(c, 0.4))
        st["scene"](cv, x, y + 3, 62, 42, c)
        chip(cv, x + 2, y + 4, st["n"], c, 17)
        draw_text(cv, x + 70, y + 4, st["head"], 15, INK)
        bl = wrap(st["body"], 11, 502 - 70)
        draw_lines(cv, x + 70, y + 23, bl[:2], 11, INK2, 13)

    # map band: dotted world map, continents as a lon/lat dot grid
    cv.fill(0, 629, W, 104, (226, 236, 242))
    draw_text(cv, 10, 634, "WHERE IT HAPPENED - 38 STORIES, 38 PINS, EACH IN ITS OWN COLOUR",
              12, INK)

    def mx(lon):
        return 8 + (lon + 180.0) / 360.0 * 1008

    def my(lat):
        return 654 + (75.0 - lat) / 130.0 * 76

    for lon0, lon1, lat0, lat1 in LAND:
        lon = lon0
        row = 0
        while lon <= lon1:
            lat = lat0
            # Stagger alternate rows by half a step so the dots read as
            # a dot texture, not vertical stripes.
            off = 1.5 if (row % 2) else 0.0
            while lat <= lat1:
                cv.fill(int(mx(lon + off)), int(my(lat)), 3, 2, (198, 176, 128))
                lat += 5
            lon += 3
            row += 1
    for n in range(1, 39):
        lon, lat, dx, dy = PINS[n]
        px = int(mx(lon)) + dx
        py = int(my(lat)) + dy
        c = accent(n)
        cv.circle(px, py, 8, c)
        cv.ring(px, py, 8, WHITE, 1)
        draw_text(cv, px, py - 4, str(n), 9 if n >= 10 else 10, WHITE, "center")

    # also-on list: 2 columns x 13 rows, every row with its own pictogram
    draw_text(cv, 10, 739, "ALSO ON THIS SUNDAY - 25 MORE STORIES, EACH WITH ITS OWN PICTURE",
              14, INK)
    cv.fill(10, 757, 1004, 2, RED)
    for i, (n, txt) in enumerate(ALSO):
        col = i // 13
        row = i % 13
        x = 8 + col * 506
        y = 762 + row * 14.6
        c = accent(n)
        # Fixed 20px icon gutter; text starts at a fixed x after it.
        cv.fill(x, int(y), 20, 14, tint(c, 0.85))
        ICONS[n](cv, x + 3, int(y), c)
        draw_text(cv, x + 26, int(y) + 1, str(n) + ". " + txt, 12, INK)

    # date-check box
    cv.rect(8, 956, 1008, 44, RED, 2)
    lines = wrap(DATE_CHECK, 12, 988)
    yy = 961
    for ln in lines[:3]:
        draw_text(cv, 16, yy, ln, 12, INK)
        yy += 13
    draw_text(cv, 16, 961, "DATE CHECK", 12, RED)

    # sources, with clear bottom padding inside the page
    draw_text(cv, 10, 1005, "Sources: Reuters, BBC, Al Jazeera, DW, Straits Times, Sky News, "
              "CNA, ABC, TOI, Guardian, Kyiv Ind. Art: original, drawn in code.",
              10, INK2)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    sys.stdout.write("wrote %s (%d bytes)\n" % (path, len(data)))


if __name__ == "__main__":
    main()
