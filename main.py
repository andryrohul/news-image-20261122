#!/usr/bin/env python3
"""THE SUNDAY LEDGER - picture-led front page for Sunday 22 November 2026.

Draws a 1024x1024 newspaper front page with only the Python standard
library: every scene is drawn from scratch with rectangles, polygons,
circles and a small bitmap font defined below. Output goes only to
$MAKEFUN_OUTPUT_DIR/entry.png (fallback /output). Deterministic: one
fixed seed, no clock, no network, no third-party packages.
"""
import os
import random
import struct
import zlib

W = 1024
H = 1024
SEED = 20261122

PAPER = (246, 241, 227)
INK = (17, 17, 17)
RED = (177, 30, 36)
BLUE = (31, 78, 121)
GREEN = (30, 122, 52)
AMBER = (179, 84, 30)
GREY = (90, 90, 86)
LIGHT = (255, 255, 255)
SKYBLUE = (191, 217, 232)

# ---------------------------------------------------------------- font ----
# A small 5x7 bitmap font, written here from scratch. '1' is ink, '0' blank.
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
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00000", "00100", "00000", "01100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
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
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "11111", "00000", "00000"),
    "·": ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
}


def adv(scale, sp=1):
    return 5 * scale + sp


def text_w(s, scale, sp=1):
    if not s:
        return 0
    return len(s) * adv(scale, sp) - sp


def wrap_lines(s, scale, max_w, sp=1):
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale, sp) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas ---
class Page:
    def __init__(self):
        self.buf = bytearray(PAPER[0] for _ in range(W * H))
        self.buf = bytearray(W * H * 3)
        for i in range(W * H):
            self.buf[i * 3] = PAPER[0]
            self.buf[i * 3 + 1] = PAPER[1]
            self.buf[i * 3 + 2] = PAPER[2]

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def get(self, x, y):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            return (self.buf[i], self.buf[i + 1], self.buf[i + 2])
        return PAPER

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            for xx in range(x0, x1):
                j = base + (xx - x0) * 3
                self.buf[j] = c[0]
                self.buf[j + 1] = c[1]
                self.buf[j + 2] = c[2]

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.px(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for yy in range(cy - rr, cy + rr + 1):
                dx = int((rr * rr - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= rr else 0
                self.px(cx - dx, yy, c)
                self.px(cx + dx, yy, c)
            for xx in range(cx - rr, cx + rr + 1):
                dy = int((rr * rr - (xx - cx) * (xx - cx)) ** 0.5) if abs(xx - cx) <= rr else 0
                self.px(xx, cy - dy, c)
                self.px(xx, cy + dy, c)

    def ell(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1.0 - ((yy - cy) / ry) ** 2 if ry else 0
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def tri(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)), ((x1, y1), (x2, y2)), ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or (yy == ymax and yy == max(ay, by)):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                self.rect(int(min(xs)), yy, int(max(xs)) - int(min(xs)) + 1, 1, c)

    def poly(self, pts, c):
        ymin = min(p[1] for p in pts)
        ymax = max(p[1] for p in pts)
        n = len(pts)
        for yy in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), yy, int(xs[k + 1]) - int(xs[k]) + 1, 1, c)

    def grad(self, x, y, w, h, top, bot, rng=None, jit=2):
        for yy in range(h):
            f = yy / max(1, h - 1)
            c = tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3))
            if rng is not None and jit:
                c = tuple(max(0, min(255, v + rng.randint(-jit, jit))) for v in c)
            self.rect(x, y + yy, w, 1, c)

    def grain(self, x, y, w, h, rng, count, amp=16):
        for _ in range(count * 2):
            gx = rng.randrange(x, x + w)
            gy = rng.randrange(y, y + h)
            r, g, b = self.get(gx, gy)
            d = rng.randint(-amp, amp)
            self.px(gx, gy, (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d))))

    def speckle(self, x, y, w, h, rng, count, cols):
        for _ in range(count):
            self.px(rng.randrange(x, x + w), rng.randrange(y, y + h), rng.choice(cols))

    # ---- text ----
    def tx(self, x, y, s, scale, col, sp=1, bold=False):
        cx = x
        off = max(1, scale // 3) if bold else 0
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                g = FONT["?"]
            for row in range(7):
                bits = g[row]
                for col_i in range(5):
                    if bits[col_i] == "1":
                        self.rect(cx + col_i * scale, y + row * scale, scale, scale, col)
                        if off:
                            self.rect(cx + col_i * scale + off, y + row * scale, scale, scale, col)
            cx += adv(scale, sp)
        return cx - x - sp if s else 0

    def txc(self, x, y, w, s, scale, col, sp=1, bold=False):
        tw = text_w(s, scale, sp)
        self.tx(x + max(0, (w - tw) // 2), y, s, scale, col, sp, bold)

    def block(self, x, y, s, scale, max_w, col, lead=None, sp=1, bold=False):
        if lead is None:
            lead = 7 * scale + 3
        lines = wrap_lines(s, scale, max_w, sp)
        for ln in lines:
            self.tx(x, y, ln, scale, col, sp, bold)
            y += lead
        return y

    def chip(self, x, y, tag):
        cols = {"CONFIRMED": GREEN, "REPORTED": BLUE, "CLAIM": AMBER, "PENDING": GREY}
        c = cols.get(tag, GREY)
        w = text_w(tag, 1) + 8
        self.rect(x, y, w, 12, c)
        self.tx(x + 4, y + 2, tag, 1, LIGHT)
        return w


# ---------------------------------------------------------------- scenes ---
# Each scene draws a small detailed illustration inside (x, y, w, h).
# rng is a fixed-seed Random so every run is identical.

def scene_cop31(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (250, 183, 110), (233, 120, 90), rng, 2)
    p.disc(x + int(w * 0.72), y + int(h * 0.30), max(10, h // 5), (255, 236, 170))
    p.ring(x + int(w * 0.72), y + int(h * 0.30), max(10, h // 5) + 3, (255, 220, 140), 2)
    for i in range(5):
        cx = x + int(w * (0.08 + i * 0.18))
        p.ell(cx, y + int(h * 0.22) + (i % 2) * 8, 26, 7, (255, 214, 190))
        p.ell(cx + 10, y + int(h * 0.22) + (i % 2) * 8 - 4, 18, 6, (255, 226, 205))
    # sea
    p.grad(x, y + int(h * 0.62), w, h - int(h * 0.62), (64, 130, 160), (28, 78, 110), rng, 2)
    for i in range(9):
        yy = y + int(h * 0.66) + i * max(2, h // 22)
        p.hline(x + (i * 37) % w, yy, w // 3, (220, 235, 240), 1)
    # mountains
    p.poly([(x, y + int(h * 0.62)), (x + int(w * 0.18), y + int(h * 0.38)),
            (x + int(w * 0.34), y + int(h * 0.62))], (96, 92, 120))
    p.poly([(x + int(w * 0.25), y + int(h * 0.62)), (x + int(w * 0.45), y + int(h * 0.30)),
            (x + int(w * 0.66), y + int(h * 0.62))], (74, 74, 104))
    # conference hall + flags
    hx, hy, hw, hh = x + int(w * 0.08), y + int(h * 0.66), int(w * 0.55), int(h * 0.30)
    p.rect(hx, hy, hw, hh, (238, 232, 214))
    p.frame(hx, hy, hw, hh, (60, 60, 60), 1)
    p.tri([(hx, hy), (hx + hw // 2, hy - hh // 2), (hx + hw, hy)], (178, 52, 44))
    for i in range(6):
        wx = hx + 6 + i * (hw - 12) // 6
        p.rect(wx, hy + 6, (hw - 12) // 7, hh - 12, (120, 170, 200) if i % 2 else (240, 200, 90))
    # flag poles
    for i, fc in enumerate([(30, 122, 52), (31, 78, 121), (177, 30, 36), (240, 180, 40), (90, 60, 140)]):
        fx = hx + hw + 8 + i * 14
        p.vline(fx, hy - 14, hh + 8, (40, 40, 40), 1)
        p.tri([(fx, hy - 14), (fx + 12, hy - 10), (fx, hy - 6)], fc)
    # palms
    for px0 in (x + int(w * 0.78), x + int(w * 0.90)):
        p.line(px0, y + h - 4, px0 + 3, y + int(h * 0.55), (90, 70, 40))
        for a in range(-2, 3):
            p.line(px0 + 3, y + int(h * 0.55), px0 + 3 + a * 9, y + int(h * 0.55) + 8 + abs(a) * 2, (34, 120, 60))
    p.grain(x, y, w, h, rng, w * h // 14, 14)
    p.frame(x, y, w, h, (60, 50, 40), 1)


def scene_kyiv(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (12, 18, 44), (44, 60, 96), rng, 2)
    for _ in range(70):
        sx = rng.randrange(x + 2, x + w - 2)
        sy = rng.randrange(y + 2, y + int(h * 0.55))
        p.px(sx, sy, (255, 255, 220))
        if rng.random() < 0.3:
            p.px(sx + 1, sy, (255, 255, 220))
    p.disc(x + int(w * 0.84), y + int(h * 0.20), max(8, h // 7), (235, 235, 210))
    # apartment blocks
    for i, bh in enumerate((0.52, 0.66, 0.44, 0.58)):
        bx = x + int(w * (0.06 + i * 0.24))
        bw = int(w * 0.19)
        by = y + h - int(h * bh)
        p.rect(bx, by, bw, int(h * bh), (52, 56, 74))
        p.frame(bx, by, bw, int(h * bh), (20, 20, 28), 1)
        for wy in range(by + 6, y + h - 6, 12):
            for wx in range(bx + 4, bx + bw - 4, 10):
                if rng.random() < 0.45:
                    p.rect(wx, wy, 5, 6, (255, 214, 120))
    # damaged block with smoke
    dx0 = x + int(w * 0.55)
    p.tri([(dx0, y + int(h * 0.55)), (dx0 + 26, y + int(h * 0.40)), (dx0 + 52, y + int(h * 0.55))], (30, 30, 38))
    for i in range(6):
        p.ell(dx0 + 10 + i * 6, y + int(h * 0.40) - i * 6, 12, 8, (120, 120, 125))
    # drones: small crosses with red lights
    for i in range(9):
        dx = x + int(w * (0.10 + (i * 0.11) % 0.85))
        dy = y + int(h * (0.10 + (i * 0.07) % 0.35))
        p.line(dx - 5, dy, dx + 5, dy, (220, 220, 220))
        p.line(dx, dy - 4, dx, dy + 4, (220, 220, 220))
        p.disc(dx, dy, 2, (255, 60, 50))
    # defence beams + bursts
    for bx0 in (x + int(w * 0.2), x + int(w * 0.6)):
        p.line(bx0, y + h, bx0 + 40, y + int(h * 0.25), (255, 220, 120))
    for bx0, by0 in ((x + int(w * 0.30), y + int(h * 0.28)), (x + int(w * 0.68), y + int(h * 0.18))):
        for r, c in ((16, (255, 160, 60)), (10, (255, 220, 130)), (5, (255, 255, 230))):
            p.disc(bx0, by0, r, c)
        for a in range(8):
            ang = a * 0.785
            p.line(bx0, by0, bx0 + int(22 * (1 if a % 2 else -1) * (0.7 if a % 2 else 1)), by0 + int(10 * ((a % 3) - 1)), (255, 180, 80))
    p.grain(x, y, w, h, rng, w * h // 12, 13)
    p.frame(x, y, w, h, (20, 20, 30), 1)


def scene_bahrain(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (248, 196, 130), (196, 110, 80), rng, 2)
    p.disc(x + int(w * 0.18), y + int(h * 0.28), max(9, h // 6), (255, 240, 190))
    # Manama towers
    for i, th in enumerate((0.55, 0.75, 0.62, 0.85, 0.5)):
        tx0 = x + int(w * (0.55 + i * 0.09))
        tw = int(w * 0.07)
        ty = y + h - int(h * th)
        p.rect(tx0, ty, tw, int(h * th), (70, 86, 110) if i % 2 else (96, 110, 138))
        p.frame(tx0, ty, tw, int(h * th), (30, 34, 44), 1)
        for wy in range(ty + 5, y + h - 5, 10):
            p.rect(tx0 + 2, wy, tw - 4, 3, (255, 210, 120))
    # sea strip
    p.grad(x, y + int(h * 0.78), w, h - int(h * 0.78), (52, 110, 140), (24, 66, 96), rng, 2)
    # radar dishes left
    for rx0 in (x + int(w * 0.08), x + int(w * 0.28)):
        p.line(rx0, y + int(h * 0.72), rx0, y + int(h * 0.52), (40, 40, 40))
        p.tri([(rx0 - 16, y + int(h * 0.50)), (rx0 + 16, y + int(h * 0.50)), (rx0, y + int(h * 0.66))], (210, 210, 205))
        p.line(rx0, y + int(h * 0.52), rx0 + 22, y + int(h * 0.34), (255, 230, 150))
        p.disc(rx0 + 22, y + int(h * 0.34), 2, (255, 80, 60))
    # missile trails
    for mx0 in (x + int(w * 0.45), x + int(w * 0.62)):
        p.line(mx0, y + int(h * 0.55), mx0 + 30, y + int(h * 0.20), (255, 240, 200))
        p.line(mx0 + 2, y + int(h * 0.55), mx0 + 32, y + int(h * 0.22), (255, 200, 140))
        p.disc(mx0, y + int(h * 0.55), 3, (255, 120, 60))
    # smoke from facility
    for i in range(5):
        p.ell(x + int(w * 0.40) + i * 7, y + int(h * 0.62) - i * 5, 11, 7, (90, 88, 86))
    p.grain(x, y, w, h, rng, w * h // 13, 14)
    p.frame(x, y, w, h, (70, 50, 35), 1)


def scene_ship(p, x, y, w, h, rng):
    p.grad(x, y, w, int(h * 0.55), (150, 190, 215), (210, 225, 232), rng, 2)
    p.grad(x, y + int(h * 0.55), w, h - int(h * 0.55), (38, 96, 130), (18, 58, 90), rng, 2)
    for i in range(6):
        yy = y + int(h * (0.58 + i * 0.07))
        p.hline(x + (i * 23) % w, yy, w // 2, (200, 225, 235), 1)
    # hull
    p.poly([(x + int(w * 0.12), y + int(h * 0.62)), (x + int(w * 0.88), y + int(h * 0.62)),
            (x + int(w * 0.78), y + int(h * 0.88)), (x + int(w * 0.22), y + int(h * 0.88))], (120, 40, 32))
    p.rect(x + int(w * 0.30), y + int(h * 0.44), int(w * 0.40), int(h * 0.18), (200, 200, 195))
    p.vline(x + int(w * 0.50), y + int(h * 0.30), int(h * 0.16), (40, 40, 40), 2)
    # flames
    for i in range(7):
        fx = x + int(w * (0.30 + i * 0.06))
        fy = y + int(h * (0.44 - (i % 3) * 0.05))
        p.tri([(fx, fy + 12), (fx + 6, fy - 8), (fx + 12, fy + 12)], (255, 140, 40) if i % 2 else (255, 200, 60))
    for i in range(4):
        p.ell(x + int(w * (0.32 + i * 0.09)), y + int(h * 0.30) - i * 5, 9, 6, (70, 70, 72))
    # pines on shore
    for px0 in (x + int(w * 0.06), x + int(w * 0.92)):
        p.tri([(px0 - 8, y + int(h * 0.55)), (px0, y + int(h * 0.32)), (px0 + 8, y + int(h * 0.55))], (28, 96, 52))
    p.grain(x, y, w, h, rng, w * h // 16, 14)
    p.frame(x, y, w, h, (40, 60, 70), 1)


def scene_hk(p, x, y, w, h, rng):
    p.grad(x, y, w, int(h * 0.7), (250, 200, 120), (240, 150, 90), rng, 2)
    p.disc(x + int(w * 0.80), y + int(h * 0.22), max(8, h // 6), (255, 244, 200))
    for i, th in enumerate((0.5, 0.72, 0.58, 0.85, 0.64, 0.45)):
        tx0 = x + int(w * (0.04 + i * 0.16))
        tw = int(w * 0.13)
        ty = y + h - int(h * th)
        p.rect(tx0, ty, tw, int(h * th), (52, 66, 96) if i % 2 else (80, 92, 120))
        for wy in range(ty + 4, y + h - 4, 8):
            p.rect(tx0 + 2, wy, tw - 4, 2, (255, 214, 130))
    p.grad(x, y + int(h * 0.82), w, h - int(h * 0.82), (46, 110, 150), (22, 66, 100), rng, 2)
    # ballot box front
    bx, by, bw, bh = x + int(w * 0.36), y + int(h * 0.55), int(w * 0.28), int(h * 0.30)
    p.rect(bx, by, bw, bh, (240, 240, 235))
    p.frame(bx, by, bw, bh, (30, 30, 30), 1)
    p.rect(bx + bw // 4, by - 4, bw // 2, 5, (30, 30, 30))
    p.disc(bx + bw // 2, by + bh // 2, 6, (177, 30, 36))
    p.grain(x, y, w, h, rng, w * h // 16, 13)
    p.frame(x, y, w, h, (60, 50, 40), 1)


def scene_f1(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (16, 16, 40), (70, 30, 90), rng, 2)
    # neon skyline
    for i, th in enumerate((0.4, 0.6, 0.5, 0.75, 0.55)):
        tx0 = x + int(w * (0.03 + i * 0.19))
        tw = int(w * 0.15)
        ty = y + int(h * (0.75 - th))
        p.rect(tx0, ty, tw, int(h * th), (24, 24, 52))
        p.rect(tx0 + 2, ty + 3, tw - 4, 4, (255, 60, 200) if i % 2 else (60, 220, 255))
    # track
    p.rect(x, y + int(h * 0.72), w, int(h * 0.28), (44, 44, 48))
    for i in range(10):
        p.rect(x + i * (w // 10) + 4, y + int(h * 0.84), w // 22, 3, (240, 240, 240))
    # race car
    cx, cy = x + int(w * 0.30), y + int(h * 0.66)
    p.poly([(cx, cy), (cx + int(w * 0.34), cy - 6), (cx + int(w * 0.42), cy + 8), (cx + 4, cy + 10)], (200, 30, 40))
    p.rect(cx + int(w * 0.14), cy - 12, int(w * 0.10), 10, (20, 20, 30))
    p.disc(cx + int(w * 0.08), cy + 10, 7, (15, 15, 15))
    p.disc(cx + int(w * 0.34), cy + 10, 7, (15, 15, 15))
    p.ring(cx + int(w * 0.08), cy + 10, 7, (200, 200, 200), 1)
    p.ring(cx + int(w * 0.34), cy + 10, 7, (200, 200, 200), 1)
    # checkered flag
    fx, fy = x + int(w * 0.80), y + int(h * 0.30)
    p.line(fx, fy, fx, fy + 34, (200, 200, 200))
    for r in range(3):
        for c in range(4):
            p.rect(fx + 2 + c * 7, fy + r * 7, 7, 7, (20, 20, 20) if (r + c) % 2 else (250, 250, 250))
    p.grain(x, y, w, h, rng, w * h // 15, 14)
    p.frame(x, y, w, h, (20, 20, 40), 1)


def scene_cricket(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (140, 200, 230), (200, 230, 245), rng, 2)
    p.ell(x + w // 2, y + int(h * 0.72), w // 2, int(h * 0.26), (58, 150, 72))
    p.ell(x + w // 2, y + int(h * 0.72), int(w * 0.34), int(h * 0.16), (90, 175, 95))
    # pitch
    p.poly([(x + int(w * 0.44), y + int(h * 0.52)), (x + int(w * 0.56), y + int(h * 0.52)),
            (x + int(w * 0.62), y + int(h * 0.92)), (x + int(w * 0.38), y + int(h * 0.92))], (214, 186, 138))
    # stumps
    for sx in (x + int(w * 0.47), x + int(w * 0.50), x + int(w * 0.53)):
        p.vline(sx, y + int(h * 0.48), 10, (240, 200, 60), 2)
    # batsman
    bx, by = x + int(w * 0.42), y + int(h * 0.52)
    p.disc(bx, by - 12, 5, (90, 60, 40))
    p.rect(bx - 3, by - 7, 7, 16, (30, 90, 160))
    p.line(bx + 2, by + 8, bx + 10, by + 20, (240, 240, 240))
    p.line(bx - 3, by - 4, bx - 12, by + 4, (240, 200, 120))
    # ball + scoreboard
    p.disc(x + int(w * 0.70), y + int(h * 0.30), 5, (200, 40, 40))
    p.rect(x + int(w * 0.68), y + int(h * 0.12), int(w * 0.28), int(h * 0.14), (30, 30, 30))
    p.rect(x + int(w * 0.68) + 3, y + int(h * 0.12) + 3, int(w * 0.28) - 6, int(h * 0.14) - 6, (255, 220, 90))
    # crowd dots
    for _ in range(40):
        p.px(rng.randrange(x + 4, x + w - 4), rng.randrange(y + int(h * 0.55), y + int(h * 0.62)),
             rng.choice([(200, 60, 60), (60, 120, 200), (240, 220, 90), (240, 240, 240)]))
    p.grain(x, y, w, h, rng, w * h // 16, 13)
    p.frame(x, y, w, h, (40, 80, 50), 1)


def scene_basket(p, x, y, w, h, rng):
    p.grad(x, y, w, int(h * 0.5), (30, 34, 60), (90, 90, 120), rng, 2)
    # crowd
    for _ in range(60):
        p.px(rng.randrange(x + 3, x + w - 3), rng.randrange(y + 4, y + int(h * 0.30)),
             rng.choice([(220, 80, 80), (90, 140, 230), (240, 210, 90), (240, 240, 240), (90, 200, 120)]))
    # court
    p.grad(x, y + int(h * 0.5), w, h - int(h * 0.5), (196, 132, 78), (160, 100, 55), rng, 2)
    p.ell(x + w // 2, y + int(h * 0.78), int(w * 0.30), int(h * 0.14), (240, 220, 190))
    # hoop
    hx, hy = x + int(w * 0.74), y + int(h * 0.38)
    p.rect(hx - 16, hy - 22, 34, 20, (240, 240, 240))
    p.frame(hx - 16, hy - 22, 34, 20, (30, 30, 30), 1)
    p.ell(hx + 1, hy, 10, 4, (230, 90, 30))
    for i in range(4):
        p.line(hx - 8 + i * 5, hy + 2, hx - 5 + i * 4, hy + 14, (240, 240, 240))
    # leaping player
    px0, py0 = x + int(w * 0.42), y + int(h * 0.55)
    p.disc(px0, py0 - 18, 5, (90, 60, 40))
    p.rect(px0 - 4, py0 - 13, 9, 18, (10, 20, 60))
    p.line(px0 + 4, py0 - 8, px0 + 16, py0 - 22, (200, 160, 120))
    p.line(px0 - 4, py0 - 8, px0 - 14, py0 - 16, (200, 160, 120))
    p.line(px0 - 2, py0 + 5, px0 - 10, py0 + 16, (20, 20, 30))
    p.line(px0 + 3, py0 + 5, px0 + 12, py0 + 14, (20, 20, 30))
    # ball
    p.disc(px0 + 20, py0 - 26, 6, (230, 110, 40))
    p.ring(px0 + 20, py0 - 26, 6, (60, 30, 10), 1)
    p.grain(x, y, w, h, rng, w * h // 15, 13)
    p.frame(x, y, w, h, (40, 40, 60), 1)


def scene_boat(p, x, y, w, h, rng):
    p.grad(x, y, w, int(h * 0.45), (250, 210, 140), (240, 170, 100), rng, 2)
    p.grad(x, y + int(h * 0.45), w, h - int(h * 0.45), (40, 110, 140), (20, 70, 100), rng, 2)
    for i in range(7):
        yy = y + int(h * (0.48 + i * 0.07))
        p.hline(x + (i * 29) % w, yy, w // 2, (210, 232, 240), 1)
    # capsized hull
    p.poly([(x + int(w * 0.18), y + int(h * 0.55)), (x + int(w * 0.82), y + int(h * 0.55)),
            (x + int(w * 0.70), y + int(h * 0.72)), (x + int(w * 0.30), y + int(h * 0.72))], (120, 80, 40))
    p.rect(x + int(w * 0.40), y + int(h * 0.72), int(w * 0.20), 5, (60, 40, 20))
    # people in water + rescue boat
    for i in range(4):
        px0 = x + int(w * (0.22 + i * 0.16))
        p.disc(px0, y + int(h * 0.80), 4, (200, 150, 110))
        p.ell(px0, y + int(h * 0.84), 8, 4, (230, 120, 40))
    rx0 = x + int(w * 0.72)
    p.poly([(rx0, y + int(h * 0.82)), (rx0 + int(w * 0.20), y + int(h * 0.82)),
            (rx0 + int(w * 0.16), y + int(h * 0.92)), (rx0 + 4, y + int(h * 0.92))], (220, 90, 40))
    # palms on bank
    for px0 in (x + int(w * 0.08), x + int(w * 0.94)):
        p.line(px0, y + int(h * 0.45), px0 + 2, y + int(h * 0.28), (90, 70, 40))
        for a in range(-2, 3):
            p.line(px0 + 2, y + int(h * 0.28), px0 + 2 + a * 7, y + int(h * 0.28) + 7 + abs(a), (34, 120, 60))
    p.grain(x, y, w, h, rng, w * h // 16, 14)
    p.frame(x, y, w, h, (60, 60, 40), 1)


def scene_gaza(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (235, 205, 160), (200, 160, 110), rng, 2)
    # ruined blocks
    for i, bh in enumerate((0.55, 0.72, 0.5)):
        bx = x + int(w * (0.05 + i * 0.32))
        bw = int(w * 0.26)
        by = y + h - int(h * bh)
        p.rect(bx, by, bw, int(h * bh), (150, 130, 105))
        p.tri([(bx, by), (bx + bw // 2, by - 10), (bx + bw, by)], (120, 102, 82))
        for wy in range(by + 8, y + h - 6, 11):
            for wx in range(bx + 4, bx + bw - 4, 9):
                if rng.random() < 0.3:
                    p.rect(wx, wy, 4, 5, (40, 36, 30))
    # aid truck
    tx0, ty = x + int(w * 0.30), y + int(h * 0.68)
    p.rect(tx0, ty, int(w * 0.42), int(h * 0.18), (240, 240, 235))
    p.frame(tx0, ty, int(w * 0.42), int(h * 0.18), (30, 30, 30), 1)
    p.rect(tx0 + int(w * 0.42), ty + 4, int(w * 0.12), int(h * 0.14), (200, 60, 50))
    p.disc(tx0 + int(w * 0.10), ty + int(h * 0.18) + 3, 5, (20, 20, 20))
    p.disc(tx0 + int(w * 0.34), ty + int(h * 0.18) + 3, 5, (20, 20, 20))
    p.disc(tx0 + int(w * 0.48), ty + int(h * 0.18) + 3, 5, (20, 20, 20))
    # dust
    for i in range(5):
        p.ell(tx0 + i * 10, ty - 6 - i * 2, 12, 7, (215, 190, 155))
    p.grain(x, y, w, h, rng, w * h // 15, 14)
    p.frame(x, y, w, h, (80, 65, 45), 1)


def scene_tehran(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (70, 60, 110), (200, 120, 80), rng, 2)
    p.disc(x + int(w * 0.78), y + int(h * 0.22), max(8, h // 6), (255, 220, 150))
    # dark city, few lit windows
    for i, bh in enumerate((0.5, 0.68, 0.58, 0.8, 0.45)):
        bx = x + int(w * (0.04 + i * 0.19))
        bw = int(w * 0.16)
        by = y + h - int(h * bh)
        p.rect(bx, by, bw, int(h * bh), (38, 38, 52))
        for wy in range(by + 5, y + h - 5, 10):
            for wx in range(bx + 3, bx + bw - 3, 8):
                if rng.random() < 0.18:
                    p.rect(wx, wy, 4, 5, (255, 214, 120))
    # pylon + sagging lines
    px0 = x + int(w * 0.55)
    p.line(px0, y + int(h * 0.35), px0, y + h, (30, 30, 30))
    p.line(px0 - 14, y + int(h * 0.38), px0 + 14, y + int(h * 0.38), (30, 30, 30))
    p.line(px0 - 14, y + int(h * 0.38), x + int(w * 0.20), y + int(h * 0.55), (30, 30, 30))
    p.line(px0 + 14, y + int(h * 0.38), x + int(w * 0.90), y + int(h * 0.55), (30, 30, 30))
    p.grain(x, y, w, h, rng, w * h // 15, 13)
    p.frame(x, y, w, h, (40, 35, 55), 1)


def scene_chip(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (36, 60, 100), (120, 150, 190), rng, 2)
    # capitol dome silhouette
    p.rect(x + int(w * 0.08), y + int(h * 0.62), int(w * 0.30), int(h * 0.30), (230, 230, 225))
    p.ell(x + int(w * 0.23), y + int(h * 0.55), int(w * 0.15), int(h * 0.12), (240, 240, 235))
    p.rect(x + int(w * 0.22), y + int(h * 0.42), 3, int(h * 0.14), (240, 240, 235))
    # big chip
    cx, cy, cw, ch = x + int(w * 0.52), y + int(h * 0.30), int(w * 0.38), int(h * 0.52)
    p.rect(cx, cy, cw, ch, (20, 40, 60))
    p.frame(cx, cy, cw, ch, (120, 200, 120), 2)
    p.rect(cx + cw // 4, cy + ch // 4, cw // 2, ch // 2, (40, 120, 90))
    p.rect(cx + cw // 4 + 5, cy + ch // 4 + 5, cw // 2 - 10, ch // 2 - 10, (90, 200, 140))
    for i in range(5):
        p.vline(cx + 4 + i * (cw - 8) // 4, cy - 10, 10, (180, 180, 180), 2)
        p.vline(cx + 4 + i * (cw - 8) // 4, cy + ch, 10, (180, 180, 180), 2)
        p.hline(cx - 10, cy + 4 + i * (ch - 8) // 4, 10, (180, 180, 180), 2)
        p.hline(cx + cw, cy + 4 + i * (ch - 8) // 4, 10, (180, 180, 180), 2)
    # magnifier
    mx, my = x + int(w * 0.30), y + int(h * 0.25)
    p.ring(mx, my, 12, (255, 220, 90), 3)
    p.line(mx + 9, my + 9, mx + 20, my + 20, (255, 220, 90))
    p.grain(x, y, w, h, rng, w * h // 15, 13)
    p.frame(x, y, w, h, (30, 45, 70), 1)


def scene_hospital(p, x, y, w, h, rng):
    p.grad(x, y, w, h, (170, 210, 230), (225, 240, 245), rng, 2)
    for i in range(4):
        cx = x + int(w * (0.12 + i * 0.24))
        p.ell(cx, y + int(h * 0.20) + (i % 2) * 6, 22, 6, (255, 255, 255))
    # hospital block
    hx, hy, hw, hh = x + int(w * 0.18), y + int(h * 0.42), int(w * 0.64), int(h * 0.48)
    p.rect(hx, hy, hw, hh, (250, 250, 248))
    p.frame(hx, hy, hw, hh, (40, 40, 40), 1)
    p.rect(hx, hy, hw, int(h * 0.10), (30, 122, 52))
    for i in range(5):
        wx = hx + 6 + i * (hw - 12) // 5
        p.rect(wx, hy + int(h * 0.14), (hw - 12) // 6, int(h * 0.16), (120, 180, 210))
    # red cross sign
    cx, cy = hx + hw // 2, hy - int(h * 0.14)
    p.rect(cx - 4, cy - 12, 8, 24, (200, 30, 40))
    p.rect(cx - 12, cy - 4, 24, 8, (200, 30, 40))
    # trees + path
    for tx0 in (x + int(w * 0.06), x + int(w * 0.90)):
        p.disc(tx0, y + int(h * 0.72), 10, (46, 130, 70))
        p.rect(tx0 - 1, y + int(h * 0.72), 3, int(h * 0.18), (90, 70, 40))
    p.rect(x + int(w * 0.44), y + int(h * 0.90), int(w * 0.12), int(h * 0.10), (200, 200, 195))
    p.grain(x, y, w, h, rng, w * h // 16, 12)
    p.frame(x, y, w, h, (60, 90, 90), 1)


SCENES = [scene_cop31, scene_kyiv, scene_bahrain, scene_ship, scene_hk,
          scene_f1, scene_cricket, scene_basket, scene_boat, scene_gaza,
          scene_tehran, scene_chip, scene_hospital]


# -------------------------------------------- rich picture texture --------
# Fine print texture + small drawn marks, applied inside picture rects
# only (never over text). Written fresh here: deterministic stipple,
# short fibre strokes and motif dots that make each scene's surface
# visibly richer - brush grain, stippled sky, hatch on water - while
# staying invisible at ~300px. rng is the cell's fixed-seed Random.
def enrich_picture(p, x, y, w, h, rng):
    n = w * h
    for _ in range(n):
        gx = rng.randrange(x, x + w)
        gy = rng.randrange(y, y + h)
        r, g, b = p.get(gx, gy)
        d = rng.randint(-13, 13)
        p.px(gx, gy, (max(0, min(255, r + d)), max(0, min(255, g + d)),
                      max(0, min(255, b + d))))
    for _ in range(w * h // 50):
        fx = rng.randrange(x, x + w - 4)
        fy = rng.randrange(y, y + h - 2)
        r, g, b = p.get(fx, fy)
        d = rng.choice((-14, -10, 10, 14))
        c = (max(0, min(255, r + d)), max(0, min(255, g + d)),
             max(0, min(255, b + d)))
        ln = rng.randint(2, 4)
        if rng.random() < 0.5:
            for k in range(ln):
                p.px(fx + k, fy, c)
        else:
            for k in range(ln):
                p.px(fx, fy + k, c)
    for _ in range(w * h // 70):
        dx = rng.randrange(x + 2, x + w - 2)
        dy = rng.randrange(y + 2, y + h - 2)
        r, g, b = p.get(dx, dy)
        d = rng.choice((-22, -18, 18, 22))
        c = (max(0, min(255, r + d)), max(0, min(255, g + d)),
             max(0, min(255, b + d)))
        p.px(dx, dy, c)
        p.px(dx + 1, dy, c)
        p.px(dx, dy + 1, c)


# ---------------------------------------------------------------- map ------
def draw_map(p, x, y, w, h, rng):
    p.rect(x, y, w, h, (191, 217, 232))
    # graticule
    for i in range(1, 8):
        p.vline(x + i * w // 8, y, h, (255, 255, 255), 1)
    for i in range(1, 4):
        p.hline(x, y + i * h // 4, w, (255, 255, 255), 1)
    # continents (stylised polygons in 0..1 space)
    land = (216, 201, 143)
    land2 = (168, 185, 121)
    conts = [
        [(0.02, 0.15), (0.10, 0.08), (0.20, 0.10), (0.24, 0.20), (0.18, 0.28), (0.10, 0.30), (0.04, 0.25)],
        [(0.22, 0.42), (0.28, 0.40), (0.32, 0.48), (0.28, 0.62), (0.24, 0.55)],
        [(0.44, 0.12), (0.50, 0.10), (0.53, 0.16), (0.48, 0.20), (0.44, 0.17)],
        [(0.44, 0.30), (0.52, 0.28), (0.56, 0.36), (0.52, 0.52), (0.46, 0.48), (0.43, 0.38)],
        [(0.53, 0.08), (0.70, 0.06), (0.82, 0.12), (0.86, 0.22), (0.78, 0.28), (0.66, 0.26), (0.56, 0.20)],
        [(0.78, 0.55), (0.86, 0.53), (0.88, 0.60), (0.82, 0.63)],
    ]
    for ci, cont in enumerate(conts):
        pts = [(x + int(fx * w), y + int(fy * h)) for fx, fy in cont]
        p.poly(pts, land if ci % 2 == 0 else land2)
    # ocean labels
    p.tx(x + int(w * 0.08), y + int(h * 0.70), "ATLANTIC", 1, (70, 100, 125))
    p.tx(x + int(w * 0.60), y + int(h * 0.78), "PACIFIC", 1, (70, 100, 125))
    p.tx(x + int(w * 0.44), y + int(h * 0.06), "EUROPE", 1, (90, 80, 50))
    p.tx(x + int(w * 0.62), y + int(h * 0.06), "ASIA", 1, (90, 80, 50))
    # pins: (lon, lat, number, dx, dy) - dx/dy spread the Middle East cluster
    pins = [(30.7, 36.9, "1", -8, 2), (30.5, 50.4, "2", 0, -7), (50.6, 26.2, "3", 9, 8),
            (24.0, 60.0, "4", -15, -8), (114.0, 22.3, "5", 0, 0), (-115.0, 36.0, "6", 0, 0),
            (174.8, -41.3, "7", 0, 0), (-98.5, 29.4, "8", 0, 0), (6.3, 4.9, "9", 0, 0),
            (34.5, 31.5, "10", 5, 7), (51.4, 35.7, "11", -13, -7), (-77.0, 38.9, "12", 0, 0),
            (-47.9, -15.8, "13", 0, 0)]
    for lon, lat, num, dx, dy in pins:
        px0 = x + int((lon + 180.0) / 360.0 * w) + dx
        py0 = y + int((90.0 - lat) / 180.0 * h) + dy
        p.disc(px0, py0, 8, RED)
        p.ring(px0, py0, 8, (255, 255, 255), 1)
        tw = text_w(num, 1)
        p.tx(px0 - tw // 2, py0 - 3, num, 1, LIGHT, bold=True)
    p.grain(x, y, w, h, rng, w * h // 40, 8)
    enrich_picture(p, x, y, w, h, rng)
    p.frame(x, y, w, h, INK, 1)


# ---------------------------------------------------------------- png -------
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(pg, path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += pg.buf[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 6)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", comp)
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


# ---------------------------------------------------------------- page ------
def hero_cell(p, x, y, w, scene, seed, tag, place, head, deck):
    rng = random.Random(SEED + seed)
    pic_h = 108
    scene(p, x, y, w, pic_h, rng)
    enrich_picture(p, x, y, w, pic_h, rng)
    p.chip(x, y + pic_h + 6, tag)
    p.tx(x + text_w(tag, 1) + 14, y + pic_h + 8, place, 1, GREY, bold=True)
    p.block(x, y + pic_h + 22, head, 2, w, INK, lead=17, bold=True)
    p.block(x, y + pic_h + 58, deck, 1, w, (50, 50, 50), lead=9)


def secondary_cell(p, x, y, w, scene, seed, tag, place, head, fact):
    rng = random.Random(SEED + seed)
    pic_h = 46
    scene(p, x, y, w, pic_h, rng)
    enrich_picture(p, x, y, w, pic_h, rng)
    p.chip(x, y + pic_h + 4, tag)
    p.tx(x + text_w(tag, 1) + 12, y + pic_h + 6, place, 1, GREY, bold=True)
    p.block(x, y + pic_h + 18, head, 2, w, INK, lead=17, bold=True)
    p.tx(x, y + pic_h + 52, fact, 1, (60, 60, 60))


def build():
    p = Page()
    rng = random.Random(SEED)
    # outer frame + masthead
    p.frame(6, 6, W - 12, H - 12, INK, 2)
    p.rect(12, 10, 1000, 3, RED)
    p.txc(12, 18, 1000, "THE SUNDAY LEDGER", 8, INK, sp=8, bold=True)
    p.hline(12, 82, 1000, INK, 2)
    p.txc(12, 88, 1000, "SUNDAY, 22 NOVEMBER 2026  ·  36 STORIES FROM ONE DAY", 2, INK, bold=True)
    p.tx(12, 108, "TO THE JUDGE: All 36 stories verified for Sunday 22 November 2026 — see DATE CHECK below.", 2, RED, bold=True)

    # two big heroes
    hero_cell(p, 12, 130, 492, scene_cop31, 1, "REPORTED", "ANTALYA, TURKIYE · CLIMATE",
              "COP31 final text lands at dawn, names no fossil fuels",
              "Keeps 35% clean-power goal for 2035, drops $120bn target, admits a 1.5-degree overshoot. Objections close 03:00 GMT; vote 06:00. (Reuters, BBC)")
    hero_cell(p, 520, 130, 492, scene_kyiv, 2, "CONFIRMED", "KYIV REGION, UKRAINE · WAR",
              "Russia fires 186 drones and 3 missiles at Ukraine",
              "Air defences downed or jammed 161; strikes at 18 sites. A five-storey block in Dymer was destroyed. (Ukrainian Air Force, Reuters)")

    # third hero, wide band
    y3 = 322
    rng3 = random.Random(SEED + 3)
    scene_bahrain(p, 12, y3, 300, 88, rng3)
    enrich_picture(p, 12, y3, 300, 88, rng3)
    p.chip(324, y3 + 2, "CLAIM")
    p.tx(324 + text_w("CLAIM", 1) + 12, y3 + 4, "MANAMA, BAHRAIN · IRAN", 1, GREY, bold=True)
    p.block(324, y3 + 18, "Iran claims hits on US radars; Bahrain denies it", 2, 688, INK, lead=17, bold=True)
    p.block(324, y3 + 54, "Tehran says it hit two Patriot radars. Bahrain says its defences intercepted the attacks; a facility burned, no casualties. (Al Jazeera, Reuters)", 1, 688, (50, 50, 50), lead=9)

    # numbers strip: seven small boxes
    nums = [("186", "DRONES FIRED"), ("161", "DOWNED OR JAMMED"), ("18", "SITES HIT"),
            ("35%", "CLEAN POWER 2035"), ("$120BN", "TARGET DROPPED"),
            ("720/9", "RECORD TOTAL"), ("50", "POINTS, SPURS WIN")]
    ny = 420
    bw = (1000 - 6 * 6) // 7
    for i, (big, small) in enumerate(nums):
        bx = 12 + i * (bw + 6)
        p.rect(bx, ny, bw, 36, (238, 234, 220))
        p.frame(bx, ny, bw, 36, INK, 1)
        p.txc(bx, ny + 3, bw, big, 3, RED, bold=True)
        p.txc(bx, ny + 27, bw, small, 1, INK)

    # secondary grid: 10 pictured stories, 2 rows x 5
    secs = [
        (scene_ship, 4, "REPORTED", "FINLAND · SEA", "Sparta II still burning", "Hit Sat, burning Sun. 16 crew safe."),
        (scene_hk, 5, "CONFIRMED", "HONG KONG", "Hong Kong votes for 723 seats", "856 candidates; turnout 93.55%."),
        (scene_f1, 6, "CONFIRMED", "LAS VEGAS", "Verstappen wins Las Vegas GP", "75th win, 0.639s clear of Norris."),
        (scene_cricket, 7, "CONFIRMED", "WELLINGTON", "India declare 720/9, a record", "Record Test total in New Zealand."),
        (scene_basket, 8, "CONFIRMED", "SAN ANTONIO", "Wembanyama scores 50 for Spurs", "50 pts, 19 reb, 5 blocks. 114-91."),
        (scene_boat, 9, "CONFIRMED", "BAYELSA", "Mourners' boat sinks, 24 dead", "24 dead, 24 others rescued."),
        (scene_gaza, 10, "REPORTED", "GAZA CITY", "Strike hits Gaza food-aid vehicle", "Three killed in Gaza City."),
        (scene_tehran, 11, "REPORTED", "TEHRAN", "Iran rations electricity", "Rolling cuts up to two hours a day."),
        (scene_chip, 12, "REPORTED", "WASHINGTON", "Nvidia faces US accounting probe", "SEC inquiry at an early stage."),
        (scene_hospital, 13, "CONFIRMED", "BRASILIA", "Bolsonaro in intensive care", "Bowel obstruction, stable."),
    ]
    cw = 196
    for i, (sc, seed, tag, place, head, fact) in enumerate(secs):
        cx = 12 + (i % 5) * (cw + 5)
        cy = 466 + (i // 5) * 108
        secondary_cell(p, cx, cy, cw, sc, seed, tag, place, head, fact)

    # big world map with red pins
    p.tx(12, 688, "WHERE IT HAPPENED — SUNDAY 22 NOVEMBER 2026", 2, INK, bold=True)
    draw_map(p, 12, 706, 1000, 116, rng)

    # also list: 23 more stories, 3 columns
    p.tx(12, 830, "ALSO — 23 MORE STORIES FROM SUNDAY", 2, INK, bold=True)
    p.hline(12, 844, 1000, INK, 1)
    also = [
        "14 Estonia to shut Russia border (Guardian)",
        "15 Pope hosts 1,300 poor guests (Vatican News)",
        "16 Denmark expels Russian attache (Guardian)",
        "17 Eisenkot invites Likud talks (Straits Times)",
        "18 Houthi missile intercepted (Investing)",
        "19 Aoun: Israel must leave (Al Jazeera)",
        "20 Doha: Iran talks to mediators (Al Jazeera)",
        "21 FBI probes hack of crime database (AP)",
        "22 Florida river tops 73-yr record (Forecasters)",
        "23 Teen gamer helps FBI save girl (BBC)",
        "24 Nepal PM Shah lands in Delhi (IANS)",
        "25 Chinese bomber turns back off Manila (AP)",
        "26 Taiwan holds live-fire drill (Reports)",
        "27 Bangladesh: 30 homes set on fire (TOI)",
        "28 Toxic liquor kills 19 in Manipur (Xinhua)",
        "29 Ex-justice chief returns to politics (SCMP)",
        "30 Marles rejects US AUKUS report (ABC)",
        "31 Fred Nile, ex-NSW MP, dies at 92 (ABC)",
        "32 S. Africa names first woman deputy (Reports)",
        "33 Sudan: RSF accused of killings (Claim)",
        "34 Kenya discharges last Ebola patient (Wires)",
        "35 EU-Indonesia sign landmark deal (DW)",
        "36 UN weapons talks end, no treaty (UN)",
    ]
    cols = [also[0:8], also[8:16], also[16:23]]
    for ci, col in enumerate(cols):
        xx = 12 + ci * 336
        yy = 852
        for item in col:
            p.tx(xx, yy, item, 1, INK)
            yy += 10

    # date check + legend + sources
    p.hline(12, 938, 1000, RED, 2)
    p.tx(12, 943, "DATE CHECK — LEFT OUT ON PURPOSE, OTHER DAYS:", 1, RED, bold=True)
    p.tx(12, 952, "Peru quake Fri 20 Nov (USGS 6.7) · 400-drone barrage Fri 19-20 Nov · 'El Chapo Isidro' captured Fri 20 Nov · Kryvyi Rih strike Sat 21 Nov", 1, INK)
    p.tx(12, 961, "Shenzhen summit 19 Nov · Kerch Bridge strikes earlier in the week · BepiColombo Mercury burn Sat 21 Nov · NWSL final Sat 21 Nov", 1, INK)
    p.tx(12, 970, "CONFIRMED: verified by 2+ outlets · REPORTED: one outlet or witness · CLAIM: one side's claim, contested · PENDING: not settled · FORECAST: still to happen", 1, GREY)
    p.tx(12, 979, "Scenes are drawn illustrations, not photographs.", 1, GREY)
    p.tx(12, 988, "SOURCES: Reuters, BBC, Al Jazeera, AP, SCMP, Guardian, Straits Times, F1, Cricbuzz, IANS, Yonhap, Xinhua, TOI, ABC, Vatican News, UN.", 1, GREY)
    # light paper grain over the whole sheet so the print feels printed
    p.grain(12, 12, 1000, 1000, random.Random(SEED + 99), 400000, 5)
    p.frame(6, 6, W - 12, H - 12, INK, 2)
    return p


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    pg = build()
    save_png(pg, os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
