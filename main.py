#!/usr/bin/env python3
"""THE WORLD TODAY - front page for Sunday 22 November 2026.

Pure stdlib Python 3.13. Draws a newspaper front page with four verified
stories from 22 November 2026 (COP31 final deal, Gaza floods, Nepal PM in
Delhi, Myanmar quake) and writes /output/entry.png (or MAKEFUN_OUTPUT_DIR).
Deterministic: same bytes every run. No network, no randomness.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, written for this entry. '#' = ink, '.' = empty.
# Uppercase, digits and the punctuation the page needs.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "10110", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10111", "10000", "01110"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale."""
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Wrap text on spaces so each line fits max_width pixels."""
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------- canvas ---
class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            row = color * (x1 - x0)
            self.px[base:base + 3 * (x1 - x0)] = row

    def rect(self, x, y, w, h, color, t=2):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=False):
        if fill:
            for yy in range(cy - r, cy + r + 1):
                half = int((r * r - (yy - cy) ** 2) ** 0.5)
                self.fill_rect(cx - half, yy, 2 * half + 1, 1, color)
            return
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                           (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def fill_poly(self, pts, color):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill_rect(xa, yy, xb - xa + 1, 1, color)

    def text(self, x, y, s, scale, color):
        """Draw text with its top-left corner at (x, y)."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, color, x0=0, x1=None):
        if x1 is None:
            x1 = self.w
        w = text_width(s, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, s, scale, color)


# --------------------------------------------------------------- colors ---
PAPER = bytes((248, 245, 238))
INK = bytes((26, 26, 26))
WHITE = bytes((255, 255, 255))
NAVY = bytes((27, 42, 74))
RED = bytes((179, 38, 30))
TEAL = bytes((31, 110, 110))
SKY = bytes((178, 214, 235))
SKY_DARK = bytes((120, 170, 205))
SEA = bytes((46, 110, 160))
SAND = bytes((222, 196, 150))
TENT = bytes((204, 120, 60))
GREY = bytes((120, 120, 120))
LIGHT_GREY = bytes((210, 210, 205))
GOLD = bytes((212, 160, 40))


# --------------------------------------------------------------- panels ---
def draw_globe(cv, cx, cy, r):
    """Stylised earth: blue disc, meridian lines, land blobs in green."""
    cv.circle(cx, cy, r, SEA, fill=True)
    cv.circle(cx, cy, r, INK)
    # meridian + parallel lines, clipped to the disc by chord length
    for k in range(1, 4):
        off = r * k // 4
        half = int((r * r - off * off) ** 0.5)
        cv.line(cx - off, cy - half, cx - off, cy + half, SKY_DARK)
        cv.line(cx + off, cy - half, cx + off, cy + half, SKY_DARK)
    cv.line(cx - r, cy, cx + r, cy, SKY_DARK)
    # land blobs (simple rounded shapes, teal-green)
    green = bytes((64, 140, 90))
    cv.circle(cx - r // 3, cy - r // 3, r // 4, green, fill=True)
    cv.circle(cx + r // 2, cy + r // 4, r // 5, green, fill=True)
    cv.circle(cx, cy + r // 2, r // 6, green, fill=True)
    cv.circle(cx + r // 3, cy - r // 2, r // 7, green, fill=True)


def draw_rain_tents(cv, x, y, w, h):
    """Rain over flooded tents: slate sky, diagonal rain, tents, water."""
    cv.fill_rect(x, y, w, h, bytes((70, 90, 110)))
    # rain streaks
    for i in range(0, w, 18):
        cv.line(x + i, y + 8, x + i - 10, y + 44, bytes((170, 200, 225)))
        cv.line(x + i + 8, y + 50, x + i - 2, y + 86, bytes((170, 200, 225)))
    # tents (triangles) on the flood line
    base = y + h - 34
    for tx in (x + 18, x + w // 2 - 30, x + w - 78):
        cv.line(tx, base, tx + 30, base - 34, TENT)
        cv.line(tx + 30, base - 34, tx + 60, base, TENT)
        cv.line(tx, base, tx + 60, base, TENT)
        cv.fill_rect(tx + 26, base - 16, 8, 16, bytes((120, 70, 30)))
    # flood water
    cv.fill_rect(x, y + h - 34, w, 34, SEA)
    for i in range(6, w, 26):
        cv.line(x + i, y + h - 22, x + i + 14, y + h - 22, WHITE)
        cv.line(x + i + 4, y + h - 12, x + i + 18, y + h - 12, WHITE)


def draw_plane(cv, x, y, w, h):
    """Simple airliner in a dawn sky over a runway."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.circle(x + w - 46, y + 30, 20, GOLD, fill=True)
    cv.circle(x + w - 46, y + 30, 20, INK)
    # fuselage
    fx = x + w // 2 - 110
    fy = y + h // 2 - 10
    cv.fill_rect(fx, fy, 220, 16, NAVY)
    cv.fill_rect(fx + 200, fy + 4, 26, 8, NAVY)
    # nose: clean tapered triangle
    for i in range(9):
        cv.fill_rect(fx + 220, fy + 4 + i, 16 - i * 2, 1, NAVY)
    # tail fin
    cv.fill_rect(fx + 8, fy - 26, 10, 28, NAVY)
    cv.fill_rect(fx + 18, fy - 26, 8, 10, NAVY)
    # wings: one swept main wing under the fuselage, one tailplane
    cv.fill_poly([(fx + 96, fy + 12), (fx + 138, fy + 12),
                  (fx + 168, fy + 52), (fx + 122, fy + 52)], NAVY)
    cv.fill_poly([(fx + 22, fy + 6), (fx + 46, fy + 6),
                  (fx + 58, fy + 26), (fx + 34, fy + 26)], NAVY)
    # windows
    for wx in range(fx + 24, fx + 190, 16):
        cv.fill_rect(wx, fy + 4, 8, 6, WHITE)
    # clouds, kept clear of the fuselage
    for cx, cy in ((x + 30, y + 22), (x + w - 150, y + 18), (x + w - 60, y + 52)):
        cv.circle(cx, cy, 12, WHITE, fill=True)
        cv.circle(cx + 16, cy + 4, 10, WHITE, fill=True)
    # runway
    cv.fill_rect(x, y + h - 26, w, 26, bytes((90, 90, 90)))
    for i in range(8, w, 44):
        cv.fill_rect(x + i, y + h - 14, 24, 3, WHITE)


def draw_seismogram(cv, x, y, w, h):
    """Dark strip with a jagged quake trace and a big magnitude label."""
    cv.fill_rect(x, y, w, h, bytes((24, 28, 36)))
    # grid lines
    for gy in range(y + 16, y + h, 20):
        cv.hline(x + 8, gy, w - 16, bytes((50, 56, 68)))
    # trace: mostly flat, one sharp burst in the middle
    pts = []
    n = w - 16
    for i in range(n):
        t = i / n
        if 0.42 < t < 0.58:
            amp = (h // 2 - 14) * (1 - abs(t - 0.5) / 0.08)
            v = (i * 37) % 29 - 14
            pts.append((x + 8 + i, y + h // 2 + int(amp * v / 14)))
        else:
            v = (i * 13) % 7 - 3
            pts.append((x + 8 + i, y + h // 2 + v))
    for (px0, py0), (px1, py1) in zip(pts, pts[1:]):
        cv.line(px0, py0, px1, py1, RED)
    cv.line(x + 8, y + h // 2, x + w - 8, y + h // 2, bytes((90, 96, 110)))


# ----------------------------------------------------------------- png ----
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        c += struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(bytes(raw), 9)) +
            chunk(b'IEND', b''))


# ----------------------------------------------------------------- page ---
def panel(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, INK, 2)


def kicker(cv, x, y, s):
    cv.text(x, y, s, 2, RED)


def headline(cv, x, y, lines, scale, max_w):
    yy = y
    for line in lines:
        cv.text(x, yy, line, scale, INK)
        yy += 7 * scale + 6
    return yy


def fact_lines(cv, x, y, facts, scale, max_w, gap=6):
    yy = y
    for fact in facts:
        for line in wrap_text(fact, max_w, scale):
            cv.text(x, yy, line, scale, INK)
            yy += 7 * scale + gap
    return yy


def main():
    W, H = 1024, 1024
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.fill_rect(16, 16, 992, 104, NAVY)
    cv.text_center(30, 'THE WORLD TODAY', 6, WHITE, 16, 1008)
    cv.text_center(84, 'SUNDAY 22 NOVEMBER 2026', 3, WHITE, 16, 1008)
    cv.fill_rect(16, 120, 992, 5, RED)

    # ---- lead: COP31 (top-left, wide) ----
    lx, ly, lw, lh = 16, 140, 624, 396
    panel(cv, lx, ly, lw, lh)
    kicker(cv, lx + 20, ly + 16, 'CLIMATE')
    headline(cv, lx + 20, ly + 44, ['COP31 CLOSE TO', 'FINAL DEAL'], 5, lw - 40)
    # globe on the left, deck + facts on the right
    gx, gy = lx + 110, ly + 250
    draw_globe(cv, gx, gy, 78)
    cv.text(gx - 78, gy + 86, 'ANTALYA, TURKEY', 2, INK)
    rx = lx + 240
    fact_lines(cv, rx, ly + 168,
               ['NEW PACKAGE ANNOUNCED AS',
                'TALKS ENTER FINAL DAY',
                'PLENARY TO APPROVE',
                'SUNDAY MORNING',
                'DELEGATES HAVE UNTIL',
                '03:00 GMT TO OBJECT'],
               2, lw - 260)
    cv.hline(lx + 20, ly + lh - 40, lw - 40, LIGHT_GREY, 2)
    cv.text(lx + 20, ly + lh - 28,
            'AUSTRALIA + TURKEY HOPE FOR CONSENSUS', 2, INK)

    # ---- Gaza floods (top-right) ----
    gx0, gy0, gw, gh = 656, 140, 352, 396
    panel(cv, gx0, gy0, gw, gh)
    kicker(cv, gx0 + 20, gy0 + 16, 'GAZA')
    headline(cv, gx0 + 20, gy0 + 44, ['FIVE KILLED IN', 'GAZA FLOODS'], 3, gw - 40)
    draw_rain_tents(cv, gx0 + 20, gy0 + 128, gw - 40, 128)
    fact_lines(cv, gx0 + 20, gy0 + 272,
               ['FOUR CHILDREN AMONG',
                'THE DEAD',
                '70,000 TENTS FLOODED',
                '1,500 EMERGENCY CALLS'],
               2, gw - 40)

    # ---- Nepal PM in Delhi (bottom-left) ----
    nx, ny, nw, nh = 16, 552, 488, 408
    panel(cv, nx, ny, nw, nh)
    kicker(cv, nx + 20, ny + 16, 'DIPLOMACY')
    headline(cv, nx + 20, ny + 44, ['NEPAL PM LANDS', 'IN DELHI'], 4, nw - 40)
    draw_plane(cv, nx + 20, ny + 150, nw - 40, 120)
    fact_lines(cv, nx + 20, ny + 286,
               ['FIRST TRIP ABROAD SINCE',
                'TAKING OFFICE IN MARCH',
                'TWO-DAY STATE VISIT',
                'TALKS WITH MODI MONDAY'],
               2, nw - 40)

    # ---- Myanmar quake (bottom-right) ----
    mx, my, mw, mh = 520, 552, 488, 408
    panel(cv, mx, my, mw, mh)
    kicker(cv, mx + 20, my + 16, 'EARTHQUAKE')
    headline(cv, mx + 20, my + 44, ['M 4.1 QUAKE', 'HITS MYANMAR'], 4, mw - 40)
    draw_seismogram(cv, mx + 20, my + 150, mw - 40, 120)
    cv.text(mx + 20, my + 286, 'M 4.1', 5, RED)
    fact_lines(cv, mx + 20, my + 336,
               ['02:35 IST, DEPTH 95 KM',
                'LAT 24.404 N, LONG 94.616 E',
                'NO CASUALTIES REPORTED'],
               2, mw - 40)

    # ---- footer ----
    cv.fill_rect(16, 976, 992, 32, NAVY)
    cv.text_center(984, 'SUNDAY 22 NOVEMBER 2026 - COP31 - GAZA - DELHI - MYANMAR',
                   1, WHITE, 16, 1008)

    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'entry.png')
    data = png_bytes(cv)
    with open(path, 'wb') as f:
        f.write(data)
    print('WROTE %s %d bytes' % (path, len(data)))


if __name__ == '__main__':
    main()
