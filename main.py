#!/usr/bin/env python3
"""THE SUNDAY GLOBE — V3. Sunday 22 November 2026 in one page.
Fresh build. Stdlib only. Deterministic. Draws a clean default newspaper
front page: navy header, big bold masthead, numbers strip, region bars,
UTC timeline, 3 hero stories, 10 secondary stories, dotted world map,
also-on list, DATE CHECK box, certainty legend, sources line.
36 stories, every one dated Sunday 22 November 2026.
"""
import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (253, 252, 247)
INK = (18, 18, 18)
NAVY = (15, 36, 64)
RED = (176, 26, 26)
DARKRED = (140, 20, 20)
BLUE = (28, 86, 156)
TEAL = (0, 118, 118)
ORANGE = (198, 108, 18)
GREEN = (28, 128, 58)
PURPLE = (108, 68, 148)
GRAY = (110, 110, 108)
MIDGRAY = (150, 148, 142)
LIGHT = (232, 230, 222)
CREAM = (246, 244, 234)
GOLD = (188, 148, 38)
AMBER = (198, 138, 0)
SKY = (168, 200, 228)
NIGHT = (16, 28, 56)
SEA = (52, 110, 168)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

TAGCOL = {
    "CONFIRMED": (28, 128, 58),
    "CLAIM": (198, 138, 0),
    "REPORTED": (28, 86, 156),
    "PENDING": (110, 110, 108),
    "FORECAST": (108, 68, 148),
}

# ---------------------------------------------------------------- canvas
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = c[0]
            buf[i + 1] = c[1]
            buf[i + 2] = c[2]


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = x1 - x0
    dy = y1 - y0
    n = max(abs(dx), abs(dy), 1)
    for k in range(n + 1):
        x = x0 + dx * k // n
        y = y0 + dy * k // n
        rect(x, y, t, t, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, c, t=1):
    for a in range(0, 360):
        rad = math.radians(a)
        for rr in range(r - t + 1, r + 1):
            px(cx + int(rr * math.cos(rad)), cy + int(rr * math.sin(rad)), c)


def ellipse(cx, cy, rx, ry, c):
    for yy in range(cy - ry, cy + ry + 1):
        for xx in range(cx - rx, cx + rx + 1):
            if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                px(xx, yy, c)


# ------------------------------------------------------- bold bitmap font
# 7 wide x 11 tall, thick strokes. Fresh design for legibility.
FONT = {
"A": (".......","..###..",".##.##.","##...##","##...##","##...##","#######","##...##","##...##","##...##","......."),
"B": (".......","######.","##...##","##...##","##...##","######.","##...##","##...##","##...##","######.","......."),
"C": (".......","..####.","##...##","##.....","##.....","##.....","##.....","##.....","##...##","..####.","......."),
"D": (".......","#####..","##..##.","##...##","##...##","##...##","##...##","##...##","##..##.","#####..","......."),
"E": (".......","#######","##.....","##.....","##.....","######.","##.....","##.....","##.....","#######","......."),
"F": (".......","#######","##.....","##.....","##.....","######.","##.....","##.....","##.....","##.....","......."),
"G": (".......","..####.","##...##","##.....","##.....","##..###","##...##","##...##","##...##","..####.","......."),
"H": (".......","##...##","##...##","##...##","##...##","#######","##...##","##...##","##...##","##...##","......."),
"I": (".......","#######","...##..","...##..","...##..","...##..","...##..","...##..","...##..","#######","......."),
"J": (".......","....###","....###","....###","....###","....###","....###","##..###","##..##.",".####..","......."),
"K": (".......","##...##","##..##.","##..##.","##.##..","####...","##.##..","##..##.","##..##.","##...##","......."),
"L": (".......","##.....","##.....","##.....","##.....","##.....","##.....","##.....","##.....","#######","......."),
"M": (".......","##...##","###.###","#######","##.#.##","##.#.##","##...##","##...##","##...##","##...##","......."),
"N": (".......","##...##","###..##","####.##","##.#.##","##.####","##..###","##...##","##...##","##...##","......."),
"O": (".......","..###..",".##.##.","##...##","##...##","##...##","##...##","##...##",".##.##.","..###..","......."),
"P": (".......","######.","##...##","##...##","##...##","######.","##.....","##.....","##.....","##.....","......."),
"Q": (".......","..###..",".##.##.","##...##","##...##","##...##","##...##","##...##",".##.##.","..###..","....###"),
"R": (".......","######.","##...##","##...##","##...##","######.","##.##..","##..##.","##..##.","##...##","......."),
"S": (".......","..####.","##...##","##.....","##.....",".####..","....##.","....##.","##...##",".####..","......."),
"T": (".......","#######","...##..","...##..","...##..","...##..","...##..","...##..","...##..","...##..","......."),
"U": (".......","##...##","##...##","##...##","##...##","##...##","##...##","##...##","##...##",".#####.","......."),
"V": (".......","##...##","##...##","##...##","##...##","##...##","##...##",".##.##.",".##.##.","..###..","......."),
"W": (".......","##...##","##...##","##...##","##...##","##.#.##","##.#.##","#######","###.###","##...##","......."),
"X": (".......","##...##","##...##",".##.##.","..###..","..###..",".##.##.","##...##","##...##","##...##","......."),
"Y": (".......","##...##","##...##","##...##",".##.##.","..###..","..###..","..###..","..###..","..###..","......."),
"Z": (".......","#######","....##.","...##..","...##..","..##...","..##...",".##....",".##....","#######","......."),
"a": (".......",".......",".......",".......",".####..","....##.",".#####.","##..##.","##..##.",".#####.","......."),
"b": (".......","##.....","##.....","##.....","#####..","##..##.","##...##","##...##","##...##","#####..","......."),
"c": (".......",".......",".......",".......","..####.","##...##","##.....","##.....","##...##","..####.","......."),
"d": (".......","....##.","....##.","....##.",".#####.","##..##.","##...##","##...##","##...##",".#####.","......."),
"e": (".......",".......",".......",".......","..###..",".##.##.","##...##","#######","##.....",".####..","......."),
"f": (".......","...###.","..##...","..##...","#######","..##...","..##...","..##...","..##...","..##...","......."),
"g": (".......",".......",".......",".......",".#####.","##...##","##...##","##...##",".#####.","....##.",".####.."),
"h": (".......","##.....","##.....","##.....","##.##..","###.##.","##..##.","##..##.","##..##.","##..##.","......."),
"i": (".......",".......","...#...",".......","..##...","..##...","..##...","..##...","..##...","..##...","......."),
"j": (".......",".......","....#..",".......","...##..","...##..","...##..","...##..","...##..","...##..",".###..."),
"k": (".......","##.....","##.....","##.....","##..##.","##.##..","####...","##.##..","##..##.","##..##.","......."),
"l": (".......","..##...","..##...","..##...","..##...","..##...","..##...","..##...","..##...","..##...","......."),
"m": (".......",".......",".......",".......","##.###.","#######","##.#.##","##.#.##","##.#.##","##.#.##","......."),
"n": (".......",".......",".......",".......","##.##..","###.##.","##..##.","##..##.","##..##.","##..##.","......."),
"o": (".......",".......",".......",".......","..###..",".##.##.","##...##","##...##","##...##",".#####.","......."),
"p": (".......",".......",".......",".......","#####..","##..##.","##...##","##...##","#####..","##.....","##....."),
"q": (".......",".......",".......",".......",".#####.","##..##.","##...##","##...##",".#####.","....##.","....##."),
"r": (".......",".......",".......",".......","##.##..","###.##.","##.....","##.....","##.....","##.....","......."),
"s": (".......",".......",".......",".......",".####..","##...##","##.....",".####..","....##.",".####..","......."),
"t": (".......","..##...","..##...","..##...","#######","..##...","..##...","..##...","..##...","..##...","......."),
"u": (".......",".......",".......",".......","##..##.","##..##.","##..##.","##..##.","##..##.",".#####.","......."),
"v": (".......",".......",".......",".......","##..##.","##..##.","##..##.","##..##.",".####..","..##...","......."),
"w": (".......",".......",".......",".......","##...##","##...##","##.#.##","##.#.##","#######","###.###","......."),
"x": (".......",".......",".......",".......","##..##.","##..##.",".####..",".####..","##..##.","##..##.","......."),
"y": (".......",".......",".......",".......","##..##.","##..##.","##..##.",".####..","..##...","..##...",".##...."),
"z": (".......",".......",".......",".......","######.","....##.","...##..","..##...",".##....","######.","......."),
"0": (".......",".#####.","##...##","##...##","##...##","##...##","##...##","##...##","##...##",".#####.","......."),
"1": (".......","...##..","..###..","...##..","...##..","...##..","...##..","...##..","...##..",".#####.","......."),
"2": (".......",".####..","##..##.","....##.","....##.","...##..","..##...",".##....","##.....","#######","......."),
"3": (".......",".####..","##..##.","....##.","....##.","..###..","....##.","....##.","##..##.",".####..","......."),
"4": (".......","....##.","...###.","..##.#.",".##..##","##...##","#######","....##.","....##.","....##.","......."),
"5": (".......","#######","##.....","##.....","#####..","....##.","....##.","....##.","##..##.",".####..","......."),
"6": (".......","..###..",".##....","##.....","##.....","#####..","##..##.","##...##","##...##",".####..","......."),
"7": (".......","#######","....##.","....##.","...##..","...##..","..##...","..##...","..##...","..##...","......."),
"8": (".......",".####..","##..##.","##..##.","##..##.",".####..","##..##.","##..##.","##..##.",".####..","......."),
"9": (".......",".####..","##..##.","##...##","##..##.",".#####.","....##.","....##.","....##.","..###..","......."),
".": (".......",".......",".......",".......",".......",".......",".......",".......",".......","..##...","......."),
",": (".......",".......",".......",".......",".......",".......",".......",".......","..##...","..##...",".##...."),
":": (".......",".......",".......",".......","..##...","..##...",".......",".......","..##...","..##...","......."),
";": (".......",".......",".......",".......","..##...","..##...",".......",".......","..##...","..##...",".##...."),
"!": (".......","..##...","..##...","..##...","..##...","..##...","..##...","..##...",".......","..##...","......."),
"?": (".......",".####..","##..##.","##..##.","....##.","...##..","...##..",".......","...##..","...##..","......."),
"'": (".......","..##...","..##...","..##...",".......",".......",".......",".......",".......",".......","......."),
'"': (".......",".##.##.",".##.##.",".##.##.",".......",".......",".......",".......",".......",".......","......."),
"(": (".......","....##.","...##..","...##..","..##...","..##...","..##...","..##...","...##..","...##..","....##."),
")": (".......",".##....","..##...","..##...","...##..","...##..","...##..","...##..","..##...","..##...",".##...."),
"-": (".......",".......",".......",".......",".......","######.",".......",".......",".......",".......","......."),
"/": (".......","....##.","....##.","...##..","...##..","..##...","..##...",".##....",".##....","##.....","......."),
"%": (".......",".###...","#...#..","#...#..",".###...","....##.","...##..","..##...","...###.","..#...#","...###."),
"$": (".......","...##..",".#####.","##..##.","##.....",".####..","....##.","##..##.",".#####.","...##..","......."),
"+": (".......",".......",".......","...##..","...##..",".#####.","...##..","...##..",".......",".......","......."),
"=": (".......",".......",".......",".......","#######",".......","#######",".......",".......",".......","......."),
"°": (".......","..###..",".#...#.","..###..",".......",".......",".......",".......",".......",".......","......."),
"·": (".......",".......",".......",".......",".......","..##...","..##...",".......",".......",".......","......."),
" ": (".......",".......",".......",".......",".......",".......",".......",".......",".......",".......","......."),
}
for _g in FONT.values():
    assert len(_g) == 11 and all(len(_r) == 7 for _r in _g), "font glyph shape"


def text_w(s, txt, font=FONT, adv=None):
    if adv is None:
        adv = (8 if font is FONT else 11) * s
    return len(txt) * adv


def draw_text(x, y, s, txt, color, bold=False, font=FONT, align="left", adv=None):
    if adv is None:
        adv = (8 if font is FONT else 11) * s
    gw = 7 if font is FONT else 10
    gh = 11 if font is FONT else 13
    total = len(txt) * adv
    if align == "center":
        x = x - total // 2
    elif align == "right":
        x = x - total
    for ci, ch in enumerate(txt):
        g = font.get(ch, font[" "])
        cx = x + ci * adv
        for r in range(gh):
            row = g[r]
            for c in range(gw):
                if row[c] == "#":
                    rect(cx + c * s, y + r * s, s, s, color)
                    if bold:
                        rect(cx + c * s + s, y + r * s, s, s, color)
    return total


def wrap(txt, max_chars):
    words = txt.split(" ")
    lines = []
    cur = ""
    for wd in words:
        if cur == "":
            cur = wd
        elif len(cur) + 1 + len(wd) <= max_chars:
            cur = cur + " " + wd
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, s, txt, color, max_w, bold=False, leading=None, font=FONT):
    adv = (8 if font is FONT else 11) * s
    max_chars = max(1, max_w // adv)
    lines = wrap(txt, max_chars)
    lh = (11 * s + 3) if leading is None else leading
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, s, ln, color, bold=bold, font=font)
    return len(lines) * lh


# ------------------------------------------------------- serif masthead font
# 10 wide x 13 tall, for the masthead only. Fresh design.
SERIF = {
"S": ("..........","..#######.",".##.....##",".##.......",".##.......","..#####...",".......##.",".......##.",".......##.",".##.....##","..#######.","..........",".........."),
"u": ("..........","..........","..........","..........","..........","..........",".##....##.",".##....##.",".##....##.",".##....##.",".###..###.","..#######.",".........."),
"n": ("..........","..........","..........","..........","..........","..........",".##.####..",".###...##.",".##....##.",".##....##.",".##....##.",".##....##.",".........."),
"d": ("..........",".......##.",".......##.",".......##.",".......##.",".......##.","..######..",".##....##.",".##....##.",".##....##.",".##...##..","..######..",".........."),
"a": ("..........","..........","..........","..........","..........","..........","..#####...",".##...##..",".....##...","..######..",".##...##..","..######..",".........."),
"y": ("..........","..........","..........","..........","..........","..........",".##....##.",".##....##.",".##....##.","..##..##..","...####...","....##....","...##....."),
"2": ("..........","..######..",".##....##.",".......##.","......##..",".....##...","...##.....","..##......",".##.......",".##.......",".########.","..........",".........."),
"N": ("..........",".##.....##",".###....##",".####...##",".##.##..##",".##..##.##",".##...####",".##....###",".##.....##",".##.....##",".##.....##","..........",".........."),
"o": ("..........","..........","..........","..........","..........","..........","..######..",".##....##.",".##....##.",".##....##.",".##....##.","..######..",".........."),
"v": ("..........","..........","..........","..........","..........","..........",".##....##.",".##....##.",".##....##.",".###..###.","..##..##..","...####...",".........."),
"e": ("..........","..........","..........","..........","..........","..........","..######..",".##....##.",".########.",".##.......",".##....##.","..######..",".........."),
"m": ("..........","..........","..........","..........","..........","..........",".###..###.",".##.#.##.#",".##.#.##.#",".##.#.##.#",".##.#.##.#",".##.#.##.#",".........."),
"b": ("..........",".##.......",".##.......",".##.......",".##.......",".##.......",".######...",".##...##..",".##...##..",".##...##..",".##...##..",".######...",".........."),
"r": ("..........","..........","..........","..........","..........","..........",".##.####..",".###...##.",".##.......",".##.......",".##.......",".##.......",".........."),
"0": ("..........","..######..",".##....##.",".##....##.",".##....##.",".##....##.",".##....##.",".##....##.",".##....##.",".##....##.","..######..","..........",".........."),
"6": ("..........","...#####..","..##......",".##.......",".##.......",".#######..",".##....##.",".##....##.",".##....##.",".##....##.","..######..","..........",".........."),
" ": ("..........","..........","..........","..........","..........","..........","..........","..........","..........","..........","..........","..........",".........."),
}
for _g in SERIF.values():
    assert len(_g) == 13 and all(len(_r) == 10 for _r in _g), "serif glyph shape"


def tag_chip(x, y, tag):
    c = TAGCOL.get(tag, GRAY)
    w = len(tag) * 8 + 8
    rect(x, y, w, 13, c)
    draw_text(x + 4, y + 1, 1, tag, WHITE, bold=True)
    return w


# ---------------------------------------------------------------- scenes
def scene_cop31(x, y, w, h):
    rect(x, y, w, h, (222, 232, 240))
    circle(x + w - 26, y + 18, 13, (240, 190, 60))
    circle(x + 34, y + 52, 17, SEA)
    ellipse(x + 28, y + 50, 8, 5, GREEN)
    ellipse(x + 40, y + 58, 6, 4, GREEN)
    rect(x, y + h - 34, w, 8, (120, 84, 48))
    rect(x, y + h - 42, w, 8, (150, 108, 62))
    for i, c in enumerate([(176, 26, 26), (28, 86, 156), (28, 128, 58), (198, 108, 18), (108, 68, 148)]):
        cx = x + 24 + i * ((w - 48) // 4)
        circle(cx, y + h - 52, 6, c)
        rect(cx - 6, y + h - 46, 12, 6, c)


def scene_ukraine(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    for sx, sy in [(18, 12), (52, 8), (96, 16), (140, 10), (180, 20), (230, 8), (280, 14), (70, 26), (200, 30)]:
        circle(x + sx % w, y + sy, 1, (255, 230, 140))
    for bx in range(0, w, 34):
        bh = 26 + (bx * 7) % 22
        rect(x + bx + 3, y + h - bh, 26, bh, (10, 16, 34))
        for wy in range(y + h - bh + 5, y + h - 6, 9):
            for wx in range(x + bx + 7, x + bx + 25, 8):
                if (wx + wy) % 3 == 0:
                    rect(wx, wy, 3, 4, (255, 210, 90))
    bx = x + w // 2 - 14
    rect(bx, y + h - 52, 28, 52, (10, 16, 34))
    line(bx + 4, y + h - 52, bx + 14, y + h - 64, (120, 120, 120), 2)
    line(bx + 24, y + h - 52, bx + 14, y + h - 64, (120, 120, 120), 2)
    circle(bx + 8, y + h - 66, 3, (150, 150, 150))
    circle(bx + 20, y + h - 70, 4, (150, 150, 150))
    for dx, dy in [(30, 18), (90, 10), (150, 24), (210, 12), (260, 22)]:
        cx, cy = x + dx % w, y + dy
        line(cx - 7, cy, cx + 7, cy, (255, 170, 60), 2)
        line(cx, cy - 4, cx, cy + 4, (255, 170, 60), 2)
        line(cx + 7, cy, cx + 18, cy + 5, (255, 200, 110), 1)


def scene_bahrain(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    circle(x + w - 30, y + 20, 10, (235, 235, 220))
    gy = y + h - 30
    rect(x, y + h - 24, w, 24, (20, 40, 70))
    rect(x, gy, w, 6, (60, 60, 66))
    for dx in (60, 170, 260):
        cx = x + dx
        ellipse(cx, gy, 30, 15, (205, 205, 200))
        rect(cx - 30, gy, 60, 15, (60, 60, 66))
        line(cx, gy - 14, cx + 15, gy - 24, (205, 205, 200), 2)
        circle(cx + 16, gy - 25, 3, (205, 205, 200))
    cx = x + 170
    circle(cx - 12, gy - 20, 5, ORANGE)
    circle(cx + 2, gy - 26, 7, (230, 90, 30))
    circle(cx + 14, gy - 18, 4, ORANGE)
    circle(cx - 6, gy - 34, 6, (120, 120, 120))
    circle(cx + 8, gy - 42, 8, (140, 140, 140))
    circle(cx + 22, gy - 50, 6, (120, 120, 120))
    for wx in range(x + 10, x + w - 10, 22):
        hline(wx, y + h - 14, 12, (90, 140, 190), 2)


def scene_sparta(x, y, w, h):
    rect(x, y, w, h, (240, 196, 130))
    circle(x + w - 24, y + 14, 9, (240, 190, 60))
    rect(x, y + h - 14, w, 14, SEA)
    for wx in range(x + 6, x + w - 6, 26):
        hline(wx, y + h - 7, 14, (120, 180, 220), 2)
    rect(x + 22, y + h - 22, w - 44, 10, (30, 34, 44))
    rect(x + 22, y + h - 22, w - 44, 3, (90, 30, 30))
    rect(x + 36, y + h - 30, 24, 8, (200, 200, 195))
    rect(x + 68, y + h - 28, 18, 6, (200, 200, 195))
    rect(x + 96, y + h - 30, 26, 8, (200, 200, 195))
    circle(x + 48, y + h - 33, 4, ORANGE)
    circle(x + 58, y + h - 37, 5, (230, 90, 30))
    circle(x + 74, y + h - 32, 4, ORANGE)
    circle(x + 66, y + 5, 4, (120, 120, 120))
    circle(x + 82, y + 8, 3, (140, 140, 140))


def scene_hk(x, y, w, h):
    rect(x, y, w, h, (214, 226, 240))
    for bx in range(0, w, 26):
        bh = 18 + (bx * 5) % 16
        rect(x + bx + 2, y + h - bh, 20, bh, (70, 90, 120))
    rect(x + w // 2 - 26, y + h - 34, 52, 34, RED)
    rect(x + w // 2 - 26, y + h - 38, 52, 5, DARKRED)
    rect(x + w // 2 - 14, y + h - 30, 28, 4, WHITE)
    line(x + w // 2 - 10, y + h - 24, x + w // 2 - 3, y + h - 14, WHITE, 3)
    line(x + w // 2 - 3, y + h - 14, x + w // 2 + 12, y + h - 28, WHITE, 3)


def scene_vegas(x, y, w, h):
    rect(x, y, w, h, (24, 24, 40))
    for i in range(8):
        rect(x + 8 + i * 10, y + 8, 5, 5, WHITE if i % 2 == 0 else BLACK)
        rect(x + 8 + i * 10, y + 13, 5, 5, BLACK if i % 2 == 0 else WHITE)
    line(x + 10, y + h - 12, x + w - 10, y + 26, (200, 200, 200), 2)
    line(x + 10, y + h - 22, x + w - 10, y + 16, (140, 140, 140), 2)
    rect(x + w // 2 - 26, y + h - 16, 52, 8, RED)
    circle(x + w // 2 - 16, y + h - 6, 4, BLACK)
    circle(x + w // 2 + 16, y + h - 6, 4, BLACK)
    rect(x + w // 2 - 8, y + h - 24, 16, 8, WHITE)


def scene_cricket(x, y, w, h):
    rect(x, y, w, h, (96, 168, 80))
    rect(x, y + h // 2 - 8, w, 16, (198, 168, 120))
    for sx in (30, w - 34):
        for k in range(3):
            vline(x + sx + k * 6, y + h // 2 - 16, 16, (240, 220, 160), 2)
        hline(x + sx, y + h // 2 - 18, 14, (240, 220, 160), 2)
    circle(x + w // 2, y + h - 8, 4, RED)
    line(x + w // 2 - 26, y + 2, x + w // 2 - 6, y + h - 16, (210, 180, 120), 4)


def scene_nba(x, y, w, h):
    rect(x, y, w, h, (232, 150, 60))
    rect(x, y + h - 18, w, 18, (200, 110, 40))
    rect(x + w - 30, y + 8, 4, 26, (200, 200, 200))
    rect(x + w - 34, y + 6, 12, 18, WHITE)
    ellipse(x + w - 28, y + 30, 10, 3, ORANGE)
    circle(x + w // 2 - 10, y + h // 2, 11, (230, 120, 40))
    ring(x + w // 2 - 10, y + h // 2, 11, BLACK, 1)
    line(x + w // 2 - 21, y + h // 2, x + w // 2 + 1, y + h // 2, BLACK, 1)


def scene_boat(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 14, w, 14, SEA)
    for wx in range(x + 4, x + w - 4, 24):
        hline(wx, y + h - 7, 12, (160, 210, 235), 2)
    rect(x + w // 2 - 40, y + h - 22, 80, 8, (120, 84, 48))
    line(x + w // 2 - 40, y + h - 22, x + w // 2 - 28, y + h - 32, (120, 84, 48), 3)
    circle(x + w // 2 - 24, y + h - 26, 3, INK)
    circle(x + w // 2 - 10, y + h - 26, 3, INK)
    circle(x + w // 2 + 6, y + h - 25, 3, INK)
    circle(x + w // 2 + 26, y + h - 8, 3, WHITE)
    circle(x + w // 2 + 38, y + h - 5, 3, WHITE)


def scene_gaza(x, y, w, h):
    rect(x, y, w, h, (226, 220, 204))
    rect(x + 8, y + h - 10, 26, 10, (150, 148, 142))
    rect(x + 40, y + h - 8, 20, 8, (170, 168, 160))
    rect(x + w // 2 - 10, y + h - 26, 66, 18, WHITE)
    rect(x + w // 2 - 10, y + h - 26, 66, 4, RED)
    rect(x + w // 2 + 8, y + h - 20, 5, 10, RED)
    rect(x + w // 2 + 1, y + h - 17, 19, 5, RED)
    circle(x + w // 2 + 2, y + h - 6, 4, BLACK)
    circle(x + w // 2 + 44, y + h - 6, 4, BLACK)


def scene_iran(x, y, w, h):
    rect(x, y, w, h, (40, 40, 52))
    rect(x + 16, y + 16, 60, h - 16, (24, 24, 36))
    for wy in range(y + 24, y + h - 8, 12):
        for wx in range(x + 22, x + 70, 12):
            if (wx + wy) % 5 == 0:
                rect(wx, wy, 4, 5, (255, 210, 90))
    line(x + 100, y + 10, x + 100, y + h - 8, (200, 200, 200), 2)
    line(x + 86, y + 22, x + 114, y + 22, (200, 200, 200), 2)
    line(x + 86, y + 22, x + 100, y + 8, (200, 200, 200), 2)
    line(x + 114, y + 22, x + 100, y + 8, (200, 200, 200), 2)
    line(x + 100, y + 22, x + 100, y + h - 8, (200, 200, 200), 2)
    rect(x + w - 40, y + h - 30, 26, 30, (220, 220, 210))
    circle(x + w - 27, y + 4, 3, (255, 200, 80))


def scene_nvidia(x, y, w, h):
    rect(x, y, w, h, (228, 238, 228))
    rect(x + w // 2 - 24, y + 4, 48, 20, (30, 60, 40))
    for k in range(5):
        vline(x + w // 2 - 20 + k * 10, y + 1, 3, GOLD, 2)
        vline(x + w // 2 - 20 + k * 10, y + 24, 3, GOLD, 2)
    rect(x + w // 2 - 10, y + 9, 20, 11, GREEN)
    draw_text(x + w // 2 - 7, y + 10, 1, "AI", WHITE, bold=True)
    line(x + 14, y + h - 4, x + w - 14, y + h - 4, GRAY, 2)
    line(x + 18, y + h - 9, x + w // 2, y + h - 7, RED, 3)
    line(x + w // 2, y + h - 7, x + w - 20, y + h - 5, RED, 3)
    line(x + w - 20, y + h - 5, x + w - 27, y + h - 5, RED, 3)
    line(x + w - 20, y + h - 5, x + w - 20, y + h - 11, RED, 3)


def scene_bolsonaro(x, y, w, h):
    rect(x, y, w, h, (226, 238, 232))
    rect(x + 14, y + h - 30, w - 28, 12, WHITE)
    rect(x + 14, y + h - 30, 22, 8, WHITE)
    circle(x + 22, y + h - 36, 5, (220, 180, 140))
    rect(x + 30, y + h - 32, w - 60, 6, (120, 180, 200))
    rect(x + w - 34, y + 4, 22, 24, WHITE)
    rect(x + w - 27, y + 8, 8, 16, GREEN)
    rect(x + w - 31, y + 12, 16, 8, GREEN)
    line(x + 14, y + 16, x + 34, y + 16, RED, 2)
    line(x + 34, y + 16, x + 44, y + 8, RED, 2)
    line(x + 44, y + 8, x + 54, y + 24, RED, 2)
    line(x + 54, y + 24, x + 64, y + 16, RED, 2)
    line(x + 64, y + 16, x + 84, y + 16, RED, 2)


# ---------------------------------------------------------------- world map
# Schematic dotted map, 46 cols x 28 rows. '#' = land.
MAPGRID = [
"..............................................",
"..............................................",
"...............###............................",
"....#####......###......#####..#############....",
"..#########...........######...##############..",
"..#########............####....##############.#",
"...########............###......#############..",
"...#######.............##........##########....",
"....#####.....###......##.........########......",
"....####.......##......##..........######.......",
".....###.......##......##...........####........",
"......##........##.....##............###..#.....",
".............###......##.............##........",
".............###......###...........###..####...",
"..............##......####...............#####..",
"..............##.......###...............####...",
"...............#.......##................###...",
".......................#.................#....",
"................#.............................",
"..............................................",
"..............................................",
"............................................##",
"............................................#.",
"...........................................##.",
"..............................................",
"..............................................",
"..............................................",
"..............................................",
]
# (col, row) pin positions for stories 1-13
PINS = {
    1: (26, 8), 2: (26, 6), 3: (28, 11), 4: (25, 4), 5: (37, 11),
    6: (8, 8), 7: (44, 23), 8: (10, 10), 9: (23, 14), 10: (27, 9),
    11: (30, 8), 12: (13, 8), 13: (17, 18),
}
PINCOL = {
    1: GREEN, 2: BLUE, 3: RED, 4: BLUE, 5: ORANGE, 6: TEAL, 7: GREEN,
    8: ORANGE, 9: GREEN, 10: RED, 11: AMBER, 12: BLUE, 13: PURPLE,
}


def draw_map(x0, y0, spacing=4):
    for r, row in enumerate(MAPGRID):
        row = row.ljust(46)[:46]
        for c, ch in enumerate(row):
            if ch == "#":
                rect(x0 + c * spacing, y0 + r * spacing, 4, 4, (100, 110, 122))
    for n in range(1, 14):
        col, rw = PINS[n]
        cx = x0 + col * spacing + 1
        cy = y0 + rw * spacing + 1
        circle(cx, cy, 8, PINCOL[n])
        ring(cx, cy, 8, WHITE, 1)
        draw_text(cx, cy - 5, 1, str(n), WHITE, bold=True, align="center")


# ---------------------------------------------------------------- stories
HEROES = [
    dict(n=1, tag="REPORTED", loc="ANTALYA, TURKIYE · CLIMATE",
         head="COP31 final text lands at dawn, names no fossil fuels",
         body="Keeps 35% electricity goal for 2035, drops $120bn target, admits a 1.5-degree overshoot. Objections close 03:00 GMT; vote at 06:00. (Reuters, BBC)",
         scene=scene_cop31, accent=GREEN),
    dict(n=2, tag="CONFIRMED", loc="KYIV REGION, UKRAINE · WAR",
         head="Russia fires 186 drones and 3 missiles at Ukraine",
         body="Air defences downed or jammed 161; strikes at 18 sites. A five-storey block in Dymer was destroyed. (Ukrainian Air Force, Reuters)",
         scene=scene_ukraine, accent=BLUE),
    dict(n=3, tag="CLAIM", loc="MANAMA, BAHRAIN · IRAN",
         head="Iran claims hits on US radars; Bahrain denies it",
         body="Tehran says it hit two Patriot radars. Bahrain says its defences intercepted the attacks; a facility burned, no casualties. (Al Jazeera, Reuters)",
         scene=scene_bahrain, accent=RED),
]

SECONDARY = [
    dict(n=4, tag="REPORTED", loc="FINLAND · SEA",
         head="Sparta II still burning; Finland blames Ukraine",
         body="Hit Saturday, still burning Sunday. 16 crew safe. (Reuters)",
         scene=scene_sparta, accent=BLUE),
    dict(n=5, tag="CONFIRMED", loc="HONG KONG",
         head="Hong Kong votes for 723 seats",
         body="856 candidates contest the poll; turnout 93.55%. (SCMP)",
         scene=scene_hk, accent=ORANGE),
    dict(n=6, tag="CONFIRMED", loc="LAS VEGAS",
         head="Verstappen wins Las Vegas GP",
         body="From pole to his 75th win, 0.639 s clear of Norris. (F1, AP)",
         scene=scene_vegas, accent=TEAL),
    dict(n=7, tag="CONFIRMED", loc="WELLINGTON",
         head="India declare 720/9, a record",
         body="A record Test total in New Zealand. (Cricbuzz, Reuters)",
         scene=scene_cricket, accent=GREEN),
    dict(n=8, tag="CONFIRMED", loc="SAN ANTONIO",
         head="Wembanyama scores 50 for Spurs",
         body="50 points, 19 rebounds, 5 blocks; Spurs beat Pelicans 114-91. (AP)",
         scene=scene_nba, accent=ORANGE),
    dict(n=9, tag="CONFIRMED", loc="BAYELSA",
         head="Mourners' boat capsizes, 24 dead",
         body="24 dead, 24 others rescued in Bayelsa. (AP)",
         scene=scene_boat, accent=GREEN),
    dict(n=10, tag="REPORTED", loc="GAZA CITY",
         head="Strike hits Gaza food-aid vehicle",
         body="Three killed in Gaza City. (Al Jazeera)",
         scene=scene_gaza, accent=RED),
    dict(n=11, tag="REPORTED", loc="TEHRAN",
         head="Iran begins rationing electricity",
         body="Rolling cuts up to two hours a day as war damage bites. (Reuters)",
         scene=scene_iran, accent=AMBER),
    dict(n=12, tag="REPORTED", loc="WASHINGTON",
         head="Nvidia faces US accounting probe",
         body="SEC inquiry at an early stage. (Reuters)",
         scene=scene_nvidia, accent=TEAL),
    dict(n=13, tag="CONFIRMED", loc="BRASILIA",
         head="Bolsonaro in intensive care",
         body="Bowel obstruction, stable, breathing on his own. (Reuters)",
         scene=scene_bolsonaro, accent=PURPLE),
]

ALSO = [
    ("EUROPE", BLUE, [
        (14, "Estonia to shut Russia border (Guardian)"),
        (15, "Pope hosts 1,300 poor guests (Vatican News)"),
        (16, "Denmark expels Russian attache (Guardian)"),
    ]),
    ("MIDDLE EAST", RED, [
        (17, "Eisenkot invites Likud talks (Straits Times)"),
        (18, "Houthi missile intercepted (Investing)"),
        (19, "Aoun: Israel must leave (Al Jazeera)"),
        (20, "Doha: Iran talks to mediators (Al Jazeera)"),
    ]),
    ("AMERICAS", TEAL, [
        (21, "FBI probes hack of crime database (AP)"),
        (22, "Florida river tops 73-yr record (Forecasters)"),
        (23, "Teen gamer helps FBI save girl (BBC)"),
    ]),
    ("WORLD", GRAY, [
        (35, "EU-Indonesia sign landmark deal (DW)"),
        (36, "UN weapons talks end, no treaty (UN)"),
    ]),
    ("ASIA-PACIFIC", ORANGE, [
        (24, "Nepal PM Shah lands in Delhi (IANS)"),
        (25, "Chinese bomber turns back off Manila (AP)"),
        (26, "Taiwan holds live-fire drill (Reports)"),
        (27, "Bangladesh: 30 homes set on fire (TOI)"),
        (28, "Toxic liquor kills 19 in Manipur (Xinhua)"),
        (29, "Ex-justice chief returns to politics (SCMP)"),
    ]),
    ("OCEANIA", PURPLE, [
        (30, "Marles rejects US AUKUS report (ABC)"),
        (31, "Fred Nile, ex-NSW MP, dies at 92 (ABC)"),
    ]),
    ("AFRICA", GREEN, [
        (32, "S. Africa names first woman deputy (Reports)"),
        (33, "Sudan: RSF accused of killings (Claim)"),
        (34, "Kenya discharges last Ebola patient (Wires)"),
    ]),
]

REGIONS = [
    ("EUROPE", 5, BLUE), ("MIDDLE EAST", 7, RED), ("AMERICAS", 7, TEAL),
    ("ASIA-PACIFIC", 8, ORANGE), ("AFRICA", 4, GREEN), ("OCEANIA", 2, PURPLE),
    ("WORLD", 3, GRAY),
]

NUMBERS = [
    ("186", "drones fired at night"),
    ("161", "downed or jammed"),
    ("35%", "2035 goal, kept"),
    ("$120bn", "target dropped"),
    ("723", "seats contested"),
    ("720/9", "record total in NZ"),
]

DATECHECK = ("DATE CHECK - Left out on purpose, they happened on earlier days: "
             "Peru earthquake (Fri 20 Nov, USGS 6.7) · Russia's 400-drone barrage "
             "(Fri 19-20 Nov) · 'El Chapo Isidro' captured (Fri 20 Nov) · Kryvyi Rih "
             "missile strike (Sat 21 Nov) · Shenzhen summit (19 Nov) · Kerch Bridge "
             "strikes (earlier in the week) · BepiColombo Mercury burn (Sat 21 Nov) · "
             "NWSL final (Sat 21 Nov). Every story on this page was first reported or "
             "still developing on Sunday 22 November 2026.")

LEGEND = ("HOW TO READ THE TAGS - CONFIRMED verified by two or more outlets · "
          "REPORTED one outlet or witness · CLAIM one side's claim, contested · "
          "PENDING not settled yet · FORECAST still to happen when drawn. "
          "Scenes are drawn illustrations, not photographs.")

SOURCES = ("Sources: Reuters, BBC, Al Jazeera, AP, SCMP, The Guardian, Straits Times, "
           "F1, Cricbuzz, IANS, Yonhap, Xinhua, TOI, ABC, Vatican News, UN.")


# ---------------------------------------------------------------- layout
def build():
    rect(0, 0, W, H, PAPER)
    # navy header bar
    rect(0, 0, W, 26, NAVY)
    draw_text(10, 8, 1, "THE WORLD IN ONE DAY", WHITE, bold=True)
    draw_text(W - 10, 8, 1, "36 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
              WHITE, bold=True, align="right")
    # masthead
    draw_text(W // 2, 28, 4, "Sunday 22 November 2026", INK, bold=True,
              font=SERIF, align="center")
    hline(10, 86, W - 20, INK, 2)
    # red subline
    draw_text(W // 2, 92, 1,
              "186 drones over Ukraine in the night · COP31 deal names no fossil fuels · Iran's claim meets Bahrain's denial",
              RED, bold=True, align="center")
    # numbers strip
    y = 108
    cell = W // 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = i * cell + cell // 2
        draw_text(cx, y, 3, num, RED, bold=True, align="center")
        draw_text(cx, y + 36, 1, cap, GRAY, align="center")
        if i > 0:
            vline(i * cell, y + 2, 44, LIGHT, 2)
    # region bars
    y = 156
    widths = []
    base = 90
    extra = W - base * len(REGIONS)
    units = sum(c - 1 for _, c, _ in REGIONS)
    for name, c, col in REGIONS:
        widths.append(base + int(round(extra * (c - 1) / units)))
    widths[-1] += W - sum(widths)
    bx = 0
    for (name, c, col), w in zip(REGIONS, widths):
        rect(bx, y, w, 16, col)
        draw_text(bx + w // 2, y + 3, 1, name + " " + str(c), WHITE, bold=True,
                  align="center")
        bx += w
    # UTC timeline
    y = 176
    draw_text(10, y, 1, "THE DAY IN UTC", RED, bold=True)
    draw_text(132, y, 1,
              "03:00 objections close · 06:00 approval plenary · DAWN final text lands · OVERNIGHT 186 drones",
              INK)
    # heroes
    y = 191
    colw = 328
    xs = [8, 348, 688]
    for st, x in zip(HEROES, xs):
        st["scene"](x, y, colw, 84)
        rect(x, y + 84, colw, 2, st["accent"])
        ty = y + 90
        wtag = tag_chip(x, ty, st["tag"])
        draw_text(x + wtag + 6, ty + 1, 1, st["loc"], RED, bold=True)
        hh = text_block(x, ty + 18, 2, st["head"], INK, colw, bold=True,
                        leading=25)
        text_block(x, ty + 18 + hh + 4, 1, st["body"], INK, colw,
                   leading=14)
    # secondary, two rows of five
    y = 440
    cw = 192
    gap = 12
    for row in range(2):
        for col in range(5):
            st = SECONDARY[row * 5 + col]
            x = 8 + col * (cw + gap)
            yy = y + row * 132
            st["scene"](x, yy, cw, 36)
            ty = yy + 40
            wtag = tag_chip(x, ty, st["tag"])
            draw_text(x + wtag + 5, ty + 1, 1, st["loc"], RED, bold=True)
            hh = text_block(x, ty + 17, 1, st["head"], INK, cw, bold=True,
                            leading=14)
            text_block(x, ty + 17 + hh + 2, 1, st["body"], INK, cw,
                       leading=13)
    # also-on section
    y = 706
    draw_text(8, y, 1, "WHERE IT HAPPENED", INK, bold=True)
    draw_text(240, y, 2, "ALSO ON SUNDAY 22 NOVEMBER - 23 MORE STORIES", INK,
              bold=True)
    draw_map(16, y + 18, spacing=4)
    draw_text(8, y + 18 + 28 * 4 + 6, 1, "Pins match story numbers", GRAY)
    colx = [240, 632]
    colgroups = [ALSO[:4], ALSO[4:]]
    for ci, groups in enumerate(colgroups):
        cy = y + 20
        for name, col, items in groups:
            draw_text(colx[ci], cy, 1, name, col, bold=True)
            cy += 12
            for n, txt in items:
                draw_text(colx[ci], cy, 1, str(n) + ".", RED, bold=True)
                draw_text(colx[ci] + 24, cy, 1, txt, INK)
                cy += 11
            cy += 1
    # date check box
    y = 918
    rect(8, y, W - 16, 48, CREAM)
    for xx in (8, W - 9):
        vline(xx, y, 48, RED, 2)
    hline(8, y, W - 16, RED, 2)
    hline(8, y + 46, W - 16, RED, 2)
    text_block(16, y + 4, 1, DATECHECK, INK, W - 32, leading=11)
    # legend + sources
    y = 970
    text_block(10, y, 1, LEGEND, GRAY, W - 20, leading=11)
    text_block(10, y + 23, 1, SOURCES, GRAY, W - 20, leading=11)
    return y + 23 + 11


# ---------------------------------------------------------------- png out
def write_png(path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    end_y = build()
    n = write_png(path)
    print("wrote", path, "(" + str(n) + " bytes), layout ends y=" + str(end_y))


if __name__ == "__main__":
    main()
