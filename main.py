#!/usr/bin/env python3
"""THE SUNDAY GLOBE - one front page for Sunday 22 November 2026.

Draws a newspaper front page summing up the day's world news, grouped by
theme (CLIMATE, CONFLICT, SPORT, POLITICS, TECH, WORLD), in pure Python
standard library only. Writes $MAKEFUN_OUTPUT_DIR/entry.png, 1024x1024,
deterministic: two runs produce byte-identical output.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---- palette: warm parchment paper, deep pine-teal ink, ochre accent ----
PAPER = (246, 237, 216)
PAPER2 = (240, 228, 200)
INK = (26, 34, 46)
TEAL = (15, 61, 62)
TEAL_LT = (31, 94, 90)
OCHRE = (192, 122, 31)
CRIMSON = (169, 39, 30)
RULE = (120, 96, 64)
SKY = (178, 205, 214)
SKY2 = (214, 228, 226)
NIGHT = (16, 28, 52)
NIGHT2 = (30, 46, 84)
SEA = (64, 128, 150)
SEA_DK = (38, 92, 116)
SAND = (226, 205, 158)
WHITE = (252, 250, 244)
GREY = (110, 108, 96)

# theme colours: each theme gets its own banner colour
THEME = {
    "CLIMATE": (47, 122, 78),
    "CONFLICT": (179, 39, 30),
    "SPORT": (30, 95, 168),
    "POLITICS": (168, 106, 18),
    "TECH": (107, 76, 154),
    "WORLD": (62, 107, 122),
}


def hsl(h, s, l):
    """Golden-angle hue -> RGB, used so every story gets its own colour."""
    h = h % 360.0
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = l - c / 2.0
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


def story_color(n):
    """Unique colour per story number: golden-angle steps around the wheel."""
    return hsl(n * 137.508, 0.62, 0.42)


# ---- 5x7 bitmap font, drawn fresh here. Thin single-cell strokes.
# V is drawn wide and open (10001 ... 00100) so it never reads as U.
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
    "V": ("10001", "10001", "10001", "10001", "01010", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("00100", "00100", "11110", "00100", "00100", "00100", "00011"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "00000", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10001", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
}

FONT.update({
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
})


# ---- canvas and drawing primitives ----
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
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if filled:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r:
                        self.set(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        # filled triangle by scanline interpolation
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / float(by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / float(cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / float(cy - ay)
            xb = ax + (cx - ax) * t2
            lo = int(min(xa, xb))
            hi = int(max(xa, xb))
            for x in range(lo, hi + 1):
                self.set(x, y, c)

    def dot_grid(self, x0, y0, x1, y1, step, c, stagger=True):
        row = 0
        y = y0
        while y <= y1:
            off = (step // 2) if (stagger and row % 2) else 0
            x = x0 + off
            while x <= x1:
                self.fill(x, y, 2, 2, c)
                x += step
            y += step
            row += 1


# ---- text ----
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, c, align="l"):
    w = text_w(s, scale)
    if align == "c":
        x -= w // 2
    elif align == "r":
        x -= w
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g is None:
            g = FONT[" "]
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    cv.fill(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return w


def wrap_text(s, scale, maxw):
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, c, maxw, lh=None):
    if lh is None:
        lh = 7 * scale + 3
    for ln in wrap_text(s, scale, maxw):
        draw_text(cv, x, y, ln, scale, c)
        y += lh
    return y


def chip(cv, x, y, n, color, scale=2):
    """Numbered story chip: coloured disc with the story number."""
    r = 9
    cv.circle(x + r, y + r, r, color)
    cv.circle(x + r, y + r, r, WHITE, filled=False)
    label = str(n)
    ls = 1 if len(label) == 1 else 1
    tw = text_w(label, ls)
    draw_text(cv, x + r - tw // 2, y + r - 3, label, ls, WHITE)


def small_chip(cv, x, y, n, color):
    """Small numbered disc for the text-only list (radius 5)."""
    cv.circle(x + 5, y + 5, 5, color)
    label = str(n)
    tw = text_w(label, 1)
    draw_text(cv, x + 5 - tw // 2, y + 2, label, 1, WHITE)


# ---- PNG encoder (pure python, deterministic) ----
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ---- the day's news: 36 stories, grouped by theme ----
# regions must sum to 36: EUROPE 9, MIDDLE EAST 7, AMERICAS 8,
# ASIA-PACIFIC 5, OCEANIA 5, AFRICA 1, WORLD 1.
REGIONS = [
    ("EUROPE", 9, (30, 95, 168)),
    ("MIDDLE EAST", 7, (179, 39, 30)),
    ("AMERICAS", 8, (168, 106, 18)),
    ("ASIA-PACIFIC", 5, (107, 76, 154)),
    ("OCEANIA", 5, (62, 107, 122)),
    ("AFRICA", 1, (47, 122, 78)),
    ("WORLD", 1, (90, 96, 96)),
]

STATS = [
    ("~200", "at the COP31 talks"),
    ("03:00", "GMT objections close"),
    ("400+", "drones at Ukraine"),
    ("110", "missiles, same night"),
    ("7", "killed in Kyiv"),
    ("2", "US bases in Bahrain"),
]

# heroes: n, theme, kicker, headline, body, outlet, scene
HEROES = [
    (1, "CLIMATE", "ANTALYA, TURKIYE - CLIMATE",
     "COP31 climate talks close in on a final deal",
     "A new package lands after a fight over fossil fuels; objections close "
     "03:00 GMT.",
     "Reuters, BBC", "cop31"),
    (2, "CONFLICT", "KYIV, UKRAINE - WAR",
     "400 drones, 110 missiles hit Ukraine",
     "One of the war's largest overnight attacks; at least seven killed "
     "in Kyiv.",
     "Al Jazeera", "kyiv"),
    (3, "CONFLICT", "MANAMA, BAHRAIN - IRAN WAR",
     "Iran strikes US bases in Bahrain",
     "An industrial site burns, no injuries; tankers are hit in Hormuz.",
     "Al Jazeera, CNA", "bahrain"),
]

# secondary: n, theme, place, kicker, headline, body, outlet, scene
SECONDARY = [
    (4, "CONFLICT", "GULF OF FINLAND", "SHIP ABLAZE",
     "Russian ship ablaze",
     "Finland blames Ukraine. 16 crew safe.",
     "Reuters, BBC", "sparta"),
    (5, "CONFLICT", "KRYVYI RIH", "2 DEAD, 60 HURT",
     "Strike hits Zelenskyy's city",
     "Russian strike on the central Ukrainian city.",
     "Al Jazeera", "kryvyi"),
    (6, "WORLD", "BAYELSA, NIGERIA", "24 DEAD",
     "Mourners' boat capsizes",
     "Passengers were going to a funeral.",
     "Sky News", "boat"),
    (7, "POLITICS", "JERUSALEM", "COALITION TALKS",
     "Eisenkot invites Likud to talks",
     "He seeks the broadest possible government.",
     "Straits Times", "talks"),
    (8, "CONFLICT", "GAZA", "3 KILLED",
     "Strike hits food aid vehicle",
     "Three Palestinians die in an air attack.",
     "Al Jazeera, Reuters", "aid"),
    (9, "CONFLICT", "SINALOA, MEXICO", "11 DEAD",
     "'El Chapo Isidro' captured",
     "FBI top-ten fugitive held after a shoot-out.",
     "Sky News, BBC", "sinaloa"),
    (10, "CLIMATE", "TEHRAN, IRAN", "POWER CUTS",
     "Iran to ration electricity",
     "War damage hits the energy network.",
     "Straits Times", "power"),
    (11, "TECH", "WASHINGTON", "SEC PROBE",
     "Nvidia faces US accounting probe",
     "The SEC inquiry is at an early stage.",
     "Straits Times", "nvidia"),
    (12, "WORLD", "BRASILIA, BRAZIL", "BOLSONARO: ICU",
     "Bolsonaro in intensive care",
     "Stable, breathing on his own.",
     "Al Jazeera, Reuters", "bolsonaro"),
    (13, "POLITICS", "CANBERRA", "AUKUS ROW",
     "Marles rejects US AUKUS report",
     "He says the budget office is wrong.",
     "ABC", "marles"),
]

# also-on: text-only list, grouped by theme. n, theme, text, lon, lat
ALSO_GROUPS = [
    ("SPORT", [
        (22, "Rugby: England beat New Zealand 31-7 (Reuters)", 174.8, -41.3),
        (23, "Rugby: France beat Argentina to reach final (Reuters)", 2.3, 48.9),
        (24, "Arsenal 2-2 Newcastle, Leeds win 4-1 (BBC)", -0.1, 51.5),
        (25, "Football: Liverpool host Man Utd today (AJ) FORECAST", -3.0, 53.4),
        (26, "Tennis: Zverev v Alcaraz in ATP final (TOI) FORECAST", 7.7, 45.1),
        (28, "Cricket: India 720/9, record in NZ (AP)", 174.8, -41.3),
        (29, "F1: Verstappen wins wild Las Vegas GP (AP)", -115.1, 36.2),
    ]),
    ("POLITICS & POWER", [
        (14, "US: FBI looks into apparent hack of crime database (BBC)", -77.0, 38.9),
        (16, "Denmark expels Russian attache over rapper plot (Guardian)", 10.0, 56.0),
        (17, "Bangladesh: 30 Awami League homes set on fire (TOI)", 90.4, 23.8),
        (21, "EU-Indonesia sign deal after 10 years (DW)", 106.8, -6.2),
        (27, "Hong Kong: 856 vie for 723 seats (China Daily)", 114.2, 22.3),
        (36, "Moldova: reports a Russian airspace breach (Kyiv Ind.)", 28.9, 47.0),
    ]),
    ("CONFLICT & CRISIS", [
        (30, "Iraq: power station fire, 4 dead (State media)", 44.4, 33.3),
        (31, "India: toxic liquor kills 19 in Manipur (Xinhua)", 93.9, 24.7),
        (33, "UN: autonomous weapons talks end, no treaty (UN)", 6.1, 46.2),
        (34, "Houthi missile 'intercepted' (Investing) CLAIM", 44.2, 15.3),
        (35, "Aoun: Israel must leave, state to hold arms (AJ)", 35.5, 33.9),
    ]),
    ("PEOPLE & PLACES", [
        (15, "US: teen gamer and mum help FBI save a girl (BBC)", -95.0, 39.0),
        (18, "Australia: Fred Nile, ex-NSW MP, dies at 92 (ABC)", 151.2, -33.9),
        (19, "Bystanders save driver from car fire (ABC)", 151.0, -34.0),
        (20, "Melbourne: 70 years since the 1956 Games (ABC)", 145.0, -37.8),
        (32, "Florida river tops 73-yr record (Forecasters)", -81.7, 27.9),
    ]),
]

# map pins for stories 1-13: n, lon, lat
PINS = [
    (1, 30.7, 36.9), (2, 30.5, 50.4), (3, 50.6, 26.2),
    (4, 24.0, 59.8), (5, 33.4, 47.9), (6, 6.3, 4.9),
    (7, 35.2, 31.8), (8, 34.5, 31.5), (9, -107.4, 24.8),
    (10, 51.4, 35.7), (11, -122.0, 37.4), (12, -47.9, -15.8),
    (13, 149.1, -35.3),
]

# dotted world map: land as lon/lat boxes
LAND = [
    (-168, 18, -52, 71), (-58, 60, -20, 83), (-80, -55, -35, 12),
    (-10, 36, 40, 70), (-18, -35, 52, 35), (40, 5, 180, 75),
    (95, -10, 140, 5), (113, -39, 154, -11),
]


# ---- detailed scene drawings ----
def flame(cv, x, y, s, c1, c2):
    """A flame: outer triangle in c1, inner in c2."""
    cv.tri(x, y, x - s, y + s * 2, x + s, y + s * 2, c1)
    cv.tri(x, y + s, x - s // 2, y + s * 2, x + s // 2, y + s * 2, c2)


def smoke(cv, x, y, c):
    cv.circle(x, y, 5, c)
    cv.circle(x + 7, y - 6, 6, c)
    cv.circle(x + 14, y - 12, 7, c)


def scene_cop31(cv, x, y, w, h):
    # Antalya summit hall: pale sky, sun, globe, long table, delegates, clock
    cv.fill(x, y, w, h, SKY2)
    cv.fill(x, y + h - 26, w, 26, (196, 172, 120))
    cv.circle(x + w - 34, y + 22, 13, (240, 196, 80))
    cv.circle(x + 46, y + 44, 26, SEA)
    cv.circle(x + 38, y + 38, 9, (96, 168, 96))
    cv.circle(x + 54, y + 52, 8, (96, 168, 96))
    cv.circle(x + 46, y + 56, 5, (96, 168, 96))
    # long table with papers on it
    cv.fill(x + 70, y + h - 52, w - 140, 8, (122, 84, 48))
    cv.fill(x + 74, y + h - 44, 6, 18, (90, 62, 34))
    cv.fill(x + w - 80, y + h - 44, 6, 18, (90, 62, 34))
    cv.fill(x + 100, y + h - 58, 26, 6, WHITE)
    cv.fill(x + 150, y + h - 58, 26, 6, WHITE)
    cv.fill(x + 200, y + h - 58, 26, 6, (230, 220, 190))
    # delegates seated behind the table, each a different colour
    cols = [(179, 39, 30), (30, 95, 168), (47, 122, 78),
            (168, 106, 18), (107, 76, 154), (62, 107, 122)]
    for i, c in enumerate(cols):
        dx = x + 92 + i * 30
        cv.circle(dx, y + h - 62, 7, c)
        cv.fill(dx - 7, y + h - 56, 14, 6, c)
    # wall clock showing 03:00
    cx, cy = x + w - 52, y + 52
    cv.circle(cx, cy, 20, WHITE)
    cv.circle(cx, cy, 20, INK, filled=False)
    cv.line(cx, cy, cx, cy - 13, INK)
    cv.line(cx, cy, cx + 11, cy, INK)
    cv.set(cx, cy, CRIMSON)
    # red flag with the deadline
    cv.fill(x + 8, y + 8, 92, 16, CRIMSON)
    draw_text(cv, x + 12, y + 12, "03:00 GMT", 1, WHITE)


def scene_kyiv(cv, x, y, w, h):
    # night over Kyiv: dark sky, moon, stars, skyline, drone trails, blasts
    cv.fill(x, y, w, h, NIGHT)
    cv.circle(x + w - 40, y + 24, 12, (238, 230, 190))
    for sx, sy in [(30, 18), (70, 34), (120, 14), (180, 30), (230, 16),
                   (260, 40), (20, 52), (150, 48)]:
        cv.set(x + sx, y + sy, WHITE)
        cv.set(x + sx + 1, y + sy, WHITE)
    # skyline with lit windows
    base = y + h - 34
    bx = x + 6
    heights = [46, 62, 38, 70, 52, 44, 66, 40, 58, 48]
    for i, hh in enumerate(heights):
        bw = 26
        cv.fill(bx, base - hh, bw, hh + 34, (10, 18, 36))
        for wy in range(base - hh + 8, base + 22, 12):
            for wx in range(bx + 5, bx + bw - 4, 9):
                if (wx * 7 + wy * 3) % 5 < 2:
                    cv.fill(wx, wy, 3, 4, (240, 196, 80))
        bx += bw + 3
    # drone trails: dashed diagonals with a drone dot at the end
    for tx, ty, ln in [(40, 20, 70), (140, 8, 90), (230, 26, 60)]:
        for k in range(0, ln, 10):
            cv.fill(x + tx + k, y + ty + k // 2, 5, 2, (220, 220, 220))
        cv.circle(x + tx + ln, y + ty + ln // 2, 3, WHITE)
    # two explosion bursts: spiky starbursts, not round suns
    for ex, ey in [(x + 90, y + h - 58), (x + 240, y + h - 70)]:
        for a in range(12):
            ang = a * math.pi / 6.0
            ln = 22 if a % 2 == 0 else 13
            cv.line(ex, ey, ex + int(ln * math.cos(ang)),
                    ey + int(ln * math.sin(ang)), (250, 190, 60))
        cv.tri(ex - 12, ey + 6, ex + 12, ey + 6, ex, ey - 14,
               (240, 120, 30))
        cv.tri(ex - 8, ey + 8, ex + 10, ey + 2, ex + 2, ey - 8,
               (250, 200, 60))
        cv.circle(ex, ey, 4, (255, 240, 160))
    cv.fill(x, y + h - 8, w, 8, (10, 18, 36))


def scene_bahrain(cv, x, y, w, h):
    # Bahrain coast at dawn: sky, sun, sea, tanker, burning port building
    cv.fill(x, y, w, h, (232, 214, 176))
    cv.circle(x + w - 36, y + 22, 12, (240, 196, 80))
    cv.fill(x, y + 62, w, h - 62, SEA)
    for wy in range(y + 70, y + h - 6, 10):
        for wx in range(x + 6, x + w - 10, 26):
            cv.hline(wx, wy, 14, (120, 180, 196), 2)
    # port building on the left, windows dark, roof alight
    cv.fill(x + 14, y + 26, 74, 44, (214, 196, 164))
    cv.fill(x + 14, y + 26, 74, 6, (160, 120, 84))
    for wx in range(x + 22, x + 80, 16):
        for wy in range(y + 36, y + 62, 12):
            cv.fill(wx, wy, 7, 7, (60, 60, 66))
    flame(cv, x + 30, y + 6, 7, (240, 120, 30), (250, 200, 60))
    flame(cv, x + 62, y + 10, 6, (240, 120, 30), (250, 200, 60))
    smoke(cv, x + 46, y - 2, (120, 120, 120))
    # tanker: tapered bow, containers on deck, white bridge, funnel flame
    hx, hy = x + 120, y + 68
    cv.fill(hx, hy, 160, 18, (24, 34, 48))
    cv.tri(hx + 160, hy, hx + 186, hy + 9, hx + 160, hy + 18,
           (24, 34, 48))
    cv.fill(hx, hy, 160, 4, CRIMSON)
    cv.fill(hx + 8, hy - 10, 26, 10, (200, 90, 40))
    cv.fill(hx + 38, hy - 10, 26, 10, (60, 140, 90))
    cv.fill(hx + 68, hy - 10, 26, 10, (200, 160, 60))
    cv.fill(hx + 120, hy - 22, 34, 22, WHITE)
    for wy in range(hy - 18, hy - 2, 7):
        cv.fill(hx + 126, wy, 6, 4, (30, 60, 90))
    cv.fill(hx + 100, hy - 14, 12, 14, (60, 60, 66))
    flame(cv, hx + 106, hy - 26, 5, (240, 120, 30), (250, 200, 60))
    smoke(cv, hx + 106, hy - 34, (110, 110, 110))
    # missile arcs overhead
    for mx in (x + 150, x + 210, x + 260):
        cv.line(mx, y + 14, mx + 22, y + 34, (240, 240, 240))
        cv.circle(mx + 24, y + 36, 2, (255, 220, 120))


def mini_sparta(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (206, 224, 228))
    cv.fill(x, y + h - 22, w, 22, SEA)
    for wx in range(x + 4, x + w - 8, 18):
        cv.hline(wx, y + h - 16, 10, WHITE, 2)
    cv.fill(x + 40, y + h - 44, 120, 16, (30, 40, 56))
    cv.fill(x + 40, y + h - 44, 120, 3, CRIMSON)
    cv.fill(x + 130, y + h - 62, 26, 18, WHITE)
    cv.fill(x + 60, y + h - 56, 10, 12, (70, 70, 78))
    cv.vline(x + 152, y + h - 62, 18, INK)
    cv.fill(x + 152, y + h - 62, 14, 8, (30, 95, 168))
    flame(cv, x + 80, y + h - 56, 6, (240, 120, 30), (250, 200, 60))
    flame(cv, x + 110, y + h - 58, 5, (240, 120, 30), (250, 200, 60))
    flame(cv, x + 96, y + h - 66, 4, (240, 120, 30), (250, 200, 60))
    smoke(cv, x + 95, y + h - 46, (120, 120, 120))


def mini_kryvyi(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (226, 214, 186))
    cv.fill(x + 10, y + 18, 46, h - 18, (120, 110, 96))
    cv.fill(x + 62, y + 8, 52, h - 8, (96, 88, 78))
    cv.fill(x + 120, y + 22, 44, h - 22, (140, 128, 110))
    for wx in range(x + 16, x + 50, 12):
        for wy in range(y + 26, y + h - 6, 12):
            cv.fill(wx, wy, 5, 6, (240, 200, 90))
    for wx in range(x + 70, x + 106, 12):
        for wy in range(y + 16, y + h - 6, 12):
            cv.fill(wx, wy, 5, 6, (240, 200, 90))
    for ex, ey in [(x + 88, y + 26), (x + 150, y + 34)]:
        for a in range(10):
            ang = a * math.pi / 5.0
            ln = 15 if a % 2 == 0 else 9
            cv.line(ex, ey, ex + int(ln * math.cos(ang)),
                    ey + int(ln * math.sin(ang)), (250, 190, 60))
        cv.tri(ex - 9, ey + 5, ex + 9, ey + 5, ex, ey - 10,
               (240, 120, 30))
        cv.circle(ex, ey, 3, (255, 240, 160))


def mini_boat(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (200, 222, 226))
    cv.fill(x, y + h - 30, w, 30, SEA)
    for wx in range(x + 4, x + w - 8, 20):
        cv.hline(wx, y + h - 22, 12, WHITE, 2)
        cv.hline(wx + 8, y + h - 12, 12, (150, 200, 210), 2)
    # capsized hull, keel up
    cv.fill(x + 60, y + h - 52, 80, 10, (120, 70, 40))
    cv.tri(x + 60, y + h - 52, x + 140, y + h - 52, x + 100, y + h - 38,
           (120, 70, 40))
    cv.fill(x + 92, y + h - 60, 16, 8, (90, 50, 30))
    # lifebuoy ring
    cv.circle(x + 34, y + h - 26, 9, (240, 240, 240))
    cv.circle(x + 34, y + h - 26, 9, CRIMSON, filled=False)
    cv.circle(x + 34, y + h - 26, 4, SEA)
    cv.circle(x + 160, y + 16, 8, (240, 196, 80))


def mini_talks(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (232, 222, 196))
    cv.fill(x + 20, y + h - 34, 160, 8, (122, 84, 48))
    cv.fill(x + 26, y + h - 26, 6, 26, (90, 62, 34))
    cv.fill(x + 168, y + h - 26, 6, 26, (90, 62, 34))
    for i, c in enumerate([(30, 95, 168), (179, 39, 30), (47, 122, 78),
                           (168, 106, 18)]):
        dx = x + 44 + i * 38
        cv.circle(dx, y + h - 46, 7, c)
        cv.fill(dx - 7, y + h - 40, 14, 6, c)
    # two small flags behind the table
    cv.vline(x + 30, y + 8, 34, INK)
    cv.fill(x + 30, y + 8, 20, 12, (30, 95, 168))
    cv.vline(x + 150, y + 8, 34, INK)
    cv.fill(x + 150, y + 8, 20, 12, WHITE)
    cv.fill(x + 150, y + 12, 20, 4, (30, 95, 168))


def mini_aid(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (228, 214, 180))
    cv.fill(x, y + h - 20, w, 20, (190, 170, 130))
    # aid truck: container with a red cross, cab, wheels
    cv.fill(x + 24, y + 18, 96, 34, WHITE)
    cv.fill(x + 24, y + 18, 96, 4, CRIMSON)
    cv.fill(x + 62, y + 26, 8, 18, CRIMSON)
    cv.fill(x + 56, y + 31, 20, 8, CRIMSON)
    cv.fill(x + 120, y + 26, 34, 26, (200, 90, 40))
    cv.fill(x + 128, y + 30, 18, 10, SKY)
    cv.circle(x + 44, y + h - 22, 8, INK)
    cv.circle(x + 136, y + h - 22, 8, INK)
    cv.circle(x + 44, y + h - 22, 3, GREY)
    cv.circle(x + 136, y + h - 22, 3, GREY)
    # dust puffs behind the truck
    cv.circle(x + 170, y + h - 34, 6, (200, 180, 140))
    cv.circle(x + 182, y + h - 40, 5, (200, 180, 140))


def mini_sinaloa(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (238, 222, 178))
    cv.circle(x + w - 26, y + 16, 11, (240, 196, 80))
    cv.tri(x + 6, y + h - 8, x + 70, y + h - 8, x + 38, y + 18,
           (150, 110, 60))
    cv.tri(x + 60, y + h - 8, x + 130, y + h - 8, x + 95, y + 26,
           (120, 88, 48))
    cv.tri(x + 120, y + h - 8, x + 190, y + h - 8, x + 155, y + 34,
           (150, 110, 60))
    cv.fill(x, y + h - 8, w, 8, (110, 82, 46))
    # sheriff star on the ridge
    sx, sy = x + 100, y + h - 30
    cv.circle(sx, sy, 7, (240, 196, 80))
    cv.fill(sx - 2, sy - 6, 4, 12, (240, 196, 80))
    cv.fill(sx - 6, sy - 2, 12, 4, (240, 196, 80))


def mini_power(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, NIGHT)
    cv.circle(x + w - 28, y + 16, 10, (238, 230, 190))
    for sx, sy in [(20, 14), (60, 26), (120, 12), (160, 30)]:
        cv.set(x + sx, y + sy, WHITE)
    # pylon: two legs, two crossarms, hanging wires
    cv.line(x + 62, y + h - 6, x + 80, y + 10, (150, 150, 150))
    cv.line(x + 102, y + h - 6, x + 84, y + 10, (150, 150, 150))
    cv.line(x + 71, y + h - 6, x + 80, y + 10, (150, 150, 150))
    cv.line(x + 93, y + h - 6, x + 84, y + 10, (150, 150, 150))
    cv.hline(x + 58, y + 18, 48, (150, 150, 150), 3)
    cv.hline(x + 66, y + 30, 32, (150, 150, 150), 3)
    cv.line(x + 58, y + 18, x + 12, y + 8, (120, 120, 120))
    cv.line(x + 106, y + 18, x + 166, y + 6, (120, 120, 120))
    cv.circle(x + 58, y + 21, 2, (240, 196, 80))
    cv.circle(x + 106, y + 21, 2, (240, 196, 80))
    # dark block, one lit window
    cv.fill(x + 130, y + h - 34, 50, 34, (10, 18, 36))
    cv.fill(x + 142, y + h - 26, 8, 8, (240, 196, 80))
    cv.fill(x + 160, y + h - 26, 8, 8, (30, 30, 40))


def mini_nvidia(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (224, 232, 226))
    # chip
    cv.fill(x + 16, y + 16, 34, 34, (30, 40, 56))
    cv.fill(x + 26, y + 26, 14, 14, (80, 200, 120))
    for px in range(x + 20, x + 46, 8):
        cv.vline(px, y + 10, 6, (120, 120, 120))
        cv.vline(px, y + 50, 6, (120, 120, 120))
    # rising chart line
    pts = [(70, 52), (95, 44), (118, 48), (142, 30), (168, 18)]
    for i in range(len(pts) - 1):
        cv.line(x + pts[i][0], y + pts[i][1], x + pts[i + 1][0],
                y + pts[i + 1][1], (30, 120, 60))
    for px, py in pts:
        cv.circle(x + px, y + py, 3, (30, 120, 60))
    # magnifier
    cv.circle(x + 150, y + 44, 12, (60, 60, 66), filled=False)
    cv.line(x + 159, y + 53, x + 170, y + 64, (60, 60, 66))


def mini_bolsonaro(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (226, 236, 232))
    # wall cross sign
    cv.fill(x + 14, y + 12, 26, 26, WHITE)
    cv.fill(x + 24, y + 16, 6, 18, CRIMSON)
    cv.fill(x + 18, y + 22, 18, 6, CRIMSON)
    # bed with patient
    cv.fill(x + 60, y + h - 30, 110, 6, (90, 110, 130))
    cv.fill(x + 64, y + h - 24, 6, 24, (70, 90, 110))
    cv.fill(x + 160, y + h - 24, 6, 24, (70, 90, 110))
    cv.fill(x + 66, y + h - 40, 30, 10, WHITE)
    cv.circle(x + 76, y + h - 44, 7, (220, 190, 150))
    cv.fill(x + 96, y + h - 36, 56, 6, (120, 160, 190))
    # monitor with heartbeat line
    cv.fill(x + 128, y + 12, 52, 26, (20, 30, 40))
    cv.line(x + 132, y + 26, x + 142, y + 26, (80, 200, 120))
    cv.line(x + 142, y + 26, x + 148, y + 16, (80, 200, 120))
    cv.line(x + 148, y + 16, x + 154, y + 32, (80, 200, 120))
    cv.line(x + 154, y + 32, x + 162, y + 26, (80, 200, 120))
    cv.line(x + 162, y + 26, x + 176, y + 26, (80, 200, 120))


def mini_marles(cv, x, y, w, h, ac):
    cv.fill(x, y, w, h, (198, 220, 226))
    cv.fill(x, y + h - 26, w, 26, SEA_DK)
    for wx in range(x + 4, x + w - 8, 20):
        cv.hline(wx, y + h - 18, 12, (120, 180, 196), 2)
    # submarine
    cv.fill(x + 40, y + 22, 110, 20, (30, 40, 56))
    cv.circle(x + 40, y + 32, 10, (30, 40, 56))
    cv.circle(x + 150, y + 32, 10, (30, 40, 56))
    cv.fill(x + 84, y + 10, 20, 12, (30, 40, 56))
    cv.vline(x + 98, y + 4, 8, (30, 40, 56), 2)
    for wx in range(x + 56, x + 140, 14):
        cv.circle(wx, y + 32, 3, (120, 180, 196))
    # bubbles
    cv.circle(x + 170, y + 14, 3, WHITE)
    cv.circle(x + 178, y + 8, 2, WHITE)


SCENES = {
    "cop31": scene_cop31, "kyiv": scene_kyiv, "bahrain": scene_bahrain,
    "sparta": mini_sparta, "kryvyi": mini_kryvyi, "boat": mini_boat,
    "talks": mini_talks, "aid": mini_aid, "sinaloa": mini_sinaloa,
    "power": mini_power, "nvidia": mini_nvidia, "bolsonaro": mini_bolsonaro,
    "marles": mini_marles,
}


# ---- page layout ----
def draw_header(cv):
    draw_text(cv, 8, 8, "THE WORLD IN ONE DAY", 1, TEAL)
    draw_text(cv, 1016, 8, "36 STORIES - SUNDAY 22 NOVEMBER 2026", 1, TEAL,
              align="r")
    cv.hline(8, 18, 1008, RULE, 1)


def draw_masthead(cv):
    title = "THE SUNDAY GLOBE"
    draw_text(cv, 512, 22, title, 6, INK, align="c")
    cv.hline(8, 68, 1008, INK, 2)
    cv.hline(8, 72, 1008, CRIMSON, 3)
    sub = ("COP31 deal in sight  -  Russia's 400-drone barrage  -  "
           "Iran hits US bases")
    draw_text(cv, 512, 76, sub, 2, CRIMSON, align="c")


def draw_stats(cv):
    y0, y1 = 98, 135
    cw = 1008 // 6
    for i, (num, lab) in enumerate(STATS):
        x = 8 + i * cw
        draw_text(cv, x + cw // 2, y0, num, 4, CRIMSON, align="c")
        draw_text(cv, x + cw // 2, y0 + 29, lab, 1, GREY, align="c")
        if i:
            cv.vline(x, y0 + 2, y1 - y0 - 4, RULE, 1)
    cv.hline(8, y1, 1008, INK, 1)


def draw_regions(cv):
    y = 139
    seg = 1008 // 7
    for i, (name, count, col) in enumerate(REGIONS):
        x = 8 + i * seg
        cv.fill(x, y, seg - 2, 14, col)
        draw_text(cv, x + (seg - 2) // 2, y + 4, "%s %d" % (name, count),
                  1, WHITE, align="c")


def draw_hero(cv, x, w, hero):
    n, theme, kicker, head, body, outlet, scene = hero
    ac = story_color(n)
    tc = THEME[theme]
    y = 157
    # detailed scene
    cv.fill(x, y, w, 96, PAPER2)
    SCENES[scene](cv, x, y, w, 96)
    cv.fill(x, y + 96, w, 1, INK)
    # theme ribbon
    y = 253
    cv.fill(x, y, w, 14, tc)
    draw_text(cv, x + 6, y + 4, theme, 1, WHITE)
    draw_text(cv, x + w - 6, y + 4, "TOP STORY" if n == 1 else "REPORTED",
              1, WHITE, align="r")
    # kicker with number chip
    y = 271
    chip(cv, x, y, n, ac)
    draw_text(cv, x + 24, y + 6, kicker, 1, CRIMSON)
    # headline, new scale-3 hierarchy
    y = 292
    for ln in wrap_text(head, 3, w):
        draw_text(cv, x, y, ln, 3, INK)
        y += 22
    # body
    y += 2
    for ln in wrap_text(body, 2, w):
        draw_text(cv, x, y, ln, 2, INK)
        y += 16
    draw_text(cv, x, y + 2, "(%s)" % outlet, 1, GREY)


def draw_secondary(cv, x, y, w, item):
    n, theme, place, tag, head, body, outlet, scene = item
    ac = story_color(n)
    tc = THEME[theme]
    # mini scene with tag label
    cv.fill(x, y, w, 52, PAPER2)
    SCENES[scene](cv, x, y, w, 52, ac)
    cv.fill(x, y, len(tag) * 6 + 10, 11, tc)
    draw_text(cv, x + 5, y + 2, tag, 1, WHITE)
    cv.fill(x, y + 52, w, 1, INK)
    # place line with number chip
    chip(cv, x, y + 56, n, ac)
    draw_text(cv, x + 22, y + 61, "%s - %s" % (place, theme), 1, GREY)
    # headline, two lines at scale 2
    hy = y + 74
    for ln in wrap_text(head, 2, w)[:2]:
        draw_text(cv, x, hy, ln, 2, INK)
        hy += 17
    # body, two lines at scale 1
    by = y + 108
    full = "%s (%s)" % (body, outlet)
    for ln in wrap_text(full, 1, w)[:2]:
        draw_text(cv, x, by, ln, 1, INK)
        by += 10


def draw_map(cv):
    y0 = 678
    draw_text(cv, 8, y0, "WHERE IT HAPPENED", 2, INK)
    draw_text(cv, 1016, y0, "PINS 1-13, EACH IN ITS OWN COLOUR", 1, GREY,
              align="r")
    mx0, mx1 = 8, 1016
    my0, my1 = 694, 774
    cv.fill(mx0, my0, mx1 - mx0, my1 - my0, (233, 226, 204))
    # dotted continents on an even pixel grid, so the dots read as land
    # instead of vertical stripes (the band is far wider than it is tall)
    step = 6
    row = 0
    py = my0 + 2
    while py < my1:
        off = step // 2 if row % 2 else 0
        px = mx0 + off
        while px < mx1:
            lon = (px - mx0) / float(mx1 - mx0) * 360.0 - 180.0
            lat = 80.0 - (py - my0) / float(my1 - my0) * 136.0
            for (lo0, la0, lo1, la1) in LAND:
                if lo0 <= lon <= lo1 and la0 <= lat <= la1:
                    cv.fill(px, py, 3, 3, (150, 128, 84))
                    break
            px += step
        py += step
        row += 1
    # also-on locations as small coloured dots
    for group in ALSO_GROUPS:
        for (n, _txt, lon, lat) in group[1]:
            px = mx0 + int((lon + 180) / 360.0 * (mx1 - mx0))
            py = my0 + int((80 - lat) / 136.0 * (my1 - my0))
            cv.fill(px - 1, py - 1, 3, 3, story_color(n))
    # numbered pins for stories 1-13, nudged where they would collide
    nudge = {1: (-24, 8), 2: (10, -12), 3: (0, 12), 4: (-16, -10),
             5: (10, 18), 7: (-16, 4), 8: (26, -2), 10: (16, -12)}
    for (n, lon, lat) in PINS:
        px = mx0 + int((lon + 180) / 360.0 * (mx1 - mx0))
        py = my0 + int((80 - lat) / 136.0 * (my1 - my0))
        dx, dy = nudge.get(n, (0, 0))
        cx, cy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            cv.line(px, py, cx, cy, INK)
        chip(cv, cx - 9, cy - 9, n, story_color(n))


def draw_also(cv):
    y0 = 780
    draw_text(cv, 8, y0, "ALSO ON THIS SUNDAY - 23 MORE STORIES", 2, INK)
    cv.hline(8, y0 + 16, 1008, INK, 1)
    cols = [(8, [ALSO_GROUPS[0], ALSO_GROUPS[1]]),
            (516, [ALSO_GROUPS[2], ALSO_GROUPS[3]])]
    gtheme = {"SPORT": "SPORT", "POLITICS & POWER": "POLITICS",
              "CONFLICT & CRISIS": "CONFLICT", "PEOPLE & PLACES": "WORLD"}
    for (cx, groups) in cols:
        y = y0 + 20
        for (gname, items) in groups:
            draw_text(cv, cx, y, gname, 1, THEME[gtheme[gname]])
            y += 10
            for (n, txt, _lon, _lat) in items:
                small_chip(cv, cx, y, n, story_color(n))
                draw_text(cv, cx + 14, y + 2, "%d. %s" % (n, txt), 1, INK)
                y += 10
            y += 2


def draw_bottom(cv):
    y = 960
    cv.fill(8, y, 1008, 28, PAPER2)
    cv.hline(8, y, 1008, CRIMSON, 2)
    cv.hline(8, y + 27, 1008, CRIMSON, 2)
    cv.vline(8, y, 28, CRIMSON, 2)
    cv.vline(1014, y, 28, CRIMSON, 2)
    msg = ("DATE CHECK - Left out on purpose: the Peru earthquake (20 Nov), "
           "Russian missiles landing in Poland (19 Nov), the Kerch Bridge "
           "strikes (earlier this week), the Shenzhen summit (19 Nov). Every "
           "story here was first reported on Sunday 22 November 2026.")
    yy = y + 4
    for ln in wrap_text(msg, 1, 992):
        draw_text(cv, 16, yy, ln, 1, INK)
        yy += 10
    src = ("Sources: Reuters, BBC, Al Jazeera, DW, Straits Times, Sky News, "
           "CNA, ABC, TOI, Guardian, Kyiv Ind. Every story names its outlet; "
           "pictures drawn in code.")
    draw_text(cv, 8, 992, src, 1, GREY)


def build():
    cv = Canvas(W, H, PAPER)
    draw_header(cv)
    draw_masthead(cv)
    draw_stats(cv)
    draw_regions(cv)
    hx = [8, 348, 688]
    for i, hero in enumerate(HEROES):
        draw_hero(cv, hx[i], 328, hero)
    sx = [8, 212, 416, 620, 824]
    for row in range(2):
        for col in range(5):
            item = SECONDARY[row * 5 + col]
            draw_secondary(cv, sx[col], 422 + row * 128, 196, item)
    draw_map(cv)
    draw_also(cv)
    draw_bottom(cv)
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    cv = build()
    path = os.path.join(out, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
