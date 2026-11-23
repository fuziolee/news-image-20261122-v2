#!/usr/bin/env python3
"""THE WORLD IN ONE DAY -- Sunday, 22 November 2026. Version 2.

A cleaner, more legible 1024x1024 newspaper front page summing up the
world's news of 22 November 2026: 37 stories across 7 regions (4 hero
stories with illustrated cards, 12 more stories, 21 one-liners), a UTC
timeline, a "WHERE IT HAPPENED" world map and a "DATE CHECK" banner.

Python 3, standard library only. No network, no external fonts, no image
files: the PNG encoder and the bitmap font are implemented here from
scratch. Fully deterministic: same bytes every run.

All facts were verified against the outlets named on 22 Nov 2026; this
build reuses only that verified set (v1 carried 50 stories; v2 keeps the
best 37 so the type can be larger and the page easier to read).
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap glyphs, '#' = ink. All drawn text is upper-cased first, so
# only capitals, digits and punctuation are needed. Digits are drawn
# deliberately distinct from letters (9 has a closed loop and a straight
# tail; G has an open right side) -- check them in the render.
FONT = {}
def _g(ch, rows):
    FONT[ch] = rows
_g('A', ["01110","10001","10001","11111","10001","10001","10001"])
_g('B', ["11110","10001","10001","11110","10001","10001","11110"])
_g('C', ["01110","10001","10000","10000","10000","10001","01110"])
_g('D', ["11110","10001","10001","10001","10001","10001","11110"])
_g('E', ["11111","10000","10000","11110","10000","10000","11111"])
_g('F', ["11111","10000","10000","11110","10000","10000","10000"])
_g('G', ["01110","10001","10000","10111","10001","10001","01111"])
_g('H', ["10001","10001","10001","11111","10001","10001","10001"])
_g('I', ["01110","00100","00100","00100","00100","00100","01110"])
_g('J', ["00111","00010","00010","00010","00010","10010","01100"])
_g('K', ["10001","10010","10100","11000","10100","10010","10001"])
_g('L', ["10000","10000","10000","10000","10000","10000","11111"])
_g('M', ["10001","11011","10101","10101","10001","10001","10001"])
_g('N', ["10001","11001","10101","10011","10001","10001","10001"])
_g('O', ["01110","10001","10001","10001","10001","10001","01110"])
_g('P', ["11110","10001","10001","11110","10000","10000","10000"])
_g('Q', ["01110","10001","10001","10001","10101","10010","01101"])
_g('R', ["11110","10001","10001","11110","10100","10010","10001"])
_g('S', ["01111","10000","10000","01110","00001","00001","11110"])
_g('T', ["11111","00100","00100","00100","00100","00100","00100"])
_g('U', ["10001","10001","10001","10001","10001","10001","01110"])
_g('V', ["10001","10001","10001","10001","10001","01010","00100"])
_g('W', ["10001","10001","10001","10101","10101","11011","10001"])
_g('X', ["10001","10001","01010","00100","01010","10001","10001"])
_g('Y', ["10001","10001","01010","00100","00100","00100","00100"])
_g('Z', ["11111","00001","00010","00100","01000","10000","11111"])
_g('0', ["01110","10001","10011","10101","11001","10001","01110"])
_g('1', ["00100","01100","00100","00100","00100","00100","01110"])
_g('2', ["01110","10001","00001","00110","01000","10000","11111"])
_g('3', ["11111","00010","00100","00010","00001","10001","01110"])
_g('4', ["00010","00110","01010","10010","11111","00010","00010"])
_g('5', ["11111","10000","11110","00001","00001","10001","01110"])
_g('6', ["00110","01000","10000","11110","10001","10001","01110"])
_g('7', ["11111","00001","00010","00100","01000","01000","01000"])
_g('8', ["01110","10001","10001","01110","10001","10001","01110"])
_g('9', ["01110","10001","10001","01111","00001","00010","01100"])
_g('.', ["00000","00000","00000","00000","00000","01100","01100"])
_g(',', ["00000","00000","00000","00000","01100","00100","01000"])
_g(':', ["00000","01100","01100","00000","01100","01100","00000"])
_g(';', ["00000","01100","01100","00000","01100","00100","01000"])
_g('!', ["00100","00100","00100","00100","00100","00000","00100"])
_g('?', ["01110","10001","00001","00110","00100","00000","00100"])
_g("'", ["00100","00100","01000","00000","00000","00000","00000"])
_g('"', ["01010","01010","00000","00000","00000","00000","00000"])
_g('-', ["00000","00000","00000","01110","00000","00000","00000"])
_g('/', ["00001","00010","00010","00100","01000","01000","10000"])
_g('(', ["00010","00100","01000","01000","01000","00100","00010"])
_g(')', ["01000","00100","00010","00010","00010","00100","01000"])
_g('&', ["01100","10010","10100","01000","10101","10010","01101"])
_g('$', ["00100","01111","10100","01110","00101","11110","00100"])
_g('%', ["11001","11010","00010","00100","01000","01011","10011"])
_g('+', ["00000","00100","00100","11111","00100","00100","00000"])
_g('=', ["00000","00000","11111","00000","11111","00000","00000"])
_g('*', ["00000","10101","01110","10101","00000","00000","00000"])
_g('#', ["01010","01010","11111","01010","11111","01010","01010"])
_g('@', ["01110","10001","10111","10101","10110","10000","01110"])
_g('_', ["00000","00000","00000","00000","00000","00000","11111"])
_g('[', ["01110","01000","01000","01000","01000","01000","01110"])
_g(']', ["01110","00010","00010","00010","00010","00010","01110"])
_g(' ', ["00000","00000","00000","00000","00000","00000","00000"])
_g('\u00b7', ["00000","00000","00000","01110","01110","00000","00000"])

# -------------------------------------------------------------- canvas ----
INK = (20, 20, 20)
PAPER = (248, 244, 232)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
NAVY = (28, 48, 88)
GREY = (90, 88, 82)
LGREY = (214, 208, 194)
BLUE = (52, 96, 140)
SEA = (198, 220, 232)
LAND = (196, 198, 158)
LANDLINE = (120, 122, 88)
GOLD = (176, 132, 32)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Canvas:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.px = bytearray(PAPER * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
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

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, c)

    # ---- text ----
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c, align="left"):
        s = s.upper()
        if align == "center":
            x -= self.text_w(s, scale) // 2
        elif align == "right":
            x -= self.text_w(s, scale)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == '1':
                        self.fill(cx + gx * scale, y + gy * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return x + self.text_w(s, scale)

    def wrap(self, s, max_w, scale):
        words, lines, cur = s.upper().split(), [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


# -------------------------------------------------------------- PNG -------
def _chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- stories ----
# Every story happened, or was first reported, on Sunday 22 November 2026,
# verified against the outlet named. Numbers are as the outlet reported.
# Regions: N. AMERICA, EUROPE, MIDDLE EAST, ASIA, AFRICA, LATIN AMERICA,
# OCEANIA / GLOBAL. v2 keeps the best 37 of v1's verified 50: all 4 heroes,
# all 12 mid stories, and the 21 strongest one-liners.

HEROES = [
    dict(num=1, tag="CLIMATE - ANTALYA, TURKEY",
         head="COP31 ENDS WITH NO DEAL",
         summ=("UN climate talks collapse after two days of overtime: the final "
               "draft never names fossil fuels and the EU refuses the text."),
         src="AP / REUTERS", kind="globe", lat=36.9, lon=30.7),
    dict(num=2, tag="WAR - UKRAINE",
         head="186 DRONES IN ONE NIGHT",
         summ=("Russia fires 186 drones at Ukraine overnight; air defences down "
               "161. A block of flats falls in Dymer, 14 people missing."),
         src="UKRAINIAN AIR FORCE", kind="drone", lat=50.4, lon=30.5),
    dict(num=3, tag="GULF - BAHRAIN",
         head="IRAN CLAIMS US RADAR HITS",
         summ=("Tehran says it struck two US Patriot radars in Bahrain. Manama "
               "says a civilian site burned; the US denies an F-16 was hit."),
         src="IRNA / CENTCOM", kind="radar", lat=26.2, lon=50.6),
    dict(num=4, tag="BALTIC SEA",
         head="SHIP ABLAZE IN THE BALTIC",
         summ=("A Russia-bound cargo ship burns in the Gulf of Finland after a "
               "drone attack. Air-raid alerts sound in Kaliningrad."),
         src="BBC / AP", kind="ship", lat=60.0, lon=27.0),
]

SMALL = [
    dict(num=5, tag="ASIA - SEOUL",
         head="SEOUL MINISTER QUITS IN EXAM SCANDAL",
         summ="THE MINISTER RESIGNS AFTER THE SCANDAL.",
         src="BBC"),
    dict(num=6, tag="GLOBAL - UNITED NATIONS",
         head="DEAL NEAR ON KILLER ROBOTS",
         summ="A TENTATIVE DEAL ON AUTONOMOUS WEAPONS.",
         src="DAILY PERSPECTIVE"),
    dict(num=7, tag="EUROPE - LONDON / BRUSSELS",
         head="UK AND EU STRIKE NEW DEALS",
         summ="TRADE AND TRAVEL PACTS TO REBUILD TIES.",
         src="AP"),
    dict(num=8, tag="TECH - SEATTLE",
         head="AMAZON NEARS $7.5BN AI DEAL",
         summ="TO BUY ISRAELI AI STARTUP DECART.",
         src="CRYPTO BRIEFING"),
    dict(num=9, tag="AFRICA - NIGERIA",
         head="24 DEAD AS BOAT CAPSIZES",
         summ="A BOAT OF MOURNERS CAPSIZES IN NIGERIA.",
         src="AP"),
    dict(num=10, tag="ASIA - INDONESIA",
         head="FACTORY FIRE: 3 DEAD, DOZENS MISSING",
         summ="FIRE SWEEPS A FACTORY; DOZENS MISSING.",
         src="BBC"),
    dict(num=11, tag="EUROPE - ROME",
         head="PAOLO BULGARI DIES AT 89",
         summ="BUILT A FAMILY FIRM INTO A LUXURY BRAND.",
         src="AP"),
    dict(num=12, tag="AFRICA - SOUTH AFRICA",
         head="MLAMBO-NGCUKA DIES AT 71",
         summ="EX-DEPUTY PRESIDENT AND UN WOMEN CHIEF.",
         src="AP"),
    dict(num=13, tag="ASIA - OKINAWA",
         head="SHURI CASTLE RISES AGAIN",
         summ="RESTORED HALL OPENS, SEVEN YEARS AFTER FIRE.",
         src="AP"),
    dict(num=14, tag="WAR - KYIV",
         head="ZELENSKYY: BRIDGE STRIKES 'FAIR'",
         summ="CALLS THE BRIDGE STRIKES A FAIR RESPONSE.",
         src="AP"),
    dict(num=15, tag="WAR - KRYVYI RIH",
         head="MISSILE KILLS 2 IN HIS HOME CITY",
         summ="TWO KILLED, ABOUT 60 WOUNDED IN THE CITY.",
         src="AP"),
    dict(num=16, tag="ASIA - TAIPEI",
         head="TAIWAN WARNS CANADA ON CHINA",
         summ="OTTAWA WARNED: DEEPER CHINA TIES CARRY RISK.",
         src="AP"),
]

ONELINERS = [
    ("N. AMERICA", "HEGSETH MEMO RESTRICTS US-CANADA DEFENCE TIES"),
    ("N. AMERICA", "WATCHDOG FINDS CASCADE OF FAILURES IN ICE TRAINING"),
    ("N. AMERICA", "WASHINGTON PAUSES GUN CHECKS OVER FBI DATABASE HACK"),
    ("MIDDLE EAST", "TRUMP: IRAN WANTS A DEAL"),
    ("ASIA", "RIGHTS GROUPS URGE SANCTIONS AFTER MYANMAR GENOCIDE FINDING"),
    ("ASIA", "ROHINGYA WELCOME UN COURT VERDICT, WANT TO GO HOME"),
    ("MIDDLE EAST", "UAE SHUTTLES OIL PAST IRAN IN RISKY HORMUZ OPERATION"),
    ("MIDDLE EAST", "ISRAELI OPPOSITION CALLS SETTLER ATTACKS 'TERRORISM'"),
    ("MIDDLE EAST", "ISRAELI STRIKES CONTINUE IN GAZA; AID VEHICLE HIT"),
    ("MIDDLE EAST", "IRAN BEGINS ELECTRICITY RATIONING AS WAR HITS GRID"),
    ("MIDDLE EAST", "HOUTHIS FIRE MISSILES AT RIYADH; 71 TARGETS HIT"),
    ("EUROPE", "RUSSIA GRASPS US OFFER ON EUROPEAN SECURITY"),
    ("ASIA", "CHINA CONDEMNS US BAR ON ITS TELECOM FIRMS"),
    ("ASIA", "CHINA RENEWS UN BID TO BLACKLIST BLA, MAJEED BRIGADE"),
    ("ASIA", "PAKISTAN: 15 MILITANTS KILLED IN MASTUNG OPERATIONS"),
    ("TECH", "IBM UNVEILS 520-QUBIT 'NIGHTHAWK R3' CHIP"),
    ("SPORT", "LEEDS STUN CHELSEA 4-1 AT STAMFORD BRIDGE"),
    ("SPORT", "MAN CITY 1-1 FULHAM; WINLESS IN FOUR"),
    ("EUROPE", "EU PLASTIC WASTE BAN MOVES 735,000 TONNES A YEAR"),
    ("GLOBAL", "WHO WARNS ON ANTIBIOTIC RESISTANCE"),
    ("LATIN AMERICA", "BUKELE SEEKS THIRD TERM IN EL SALVADOR"),
]

TIMELINE = [
    ("03:00", "COP31 DRAFT OBJECTION DEADLINE"),
    ("06:00", "UKRAINE: 161 OF 186 DRONES DOWNED"),
    ("12:32", "AIR ALERT SOUNDS IN KALININGRAD"),
    ("16:30", "LIVERPOOL V MAN UTD KICK OFF"),
]

SOURCES = "AP, REUTERS, BBC, AL JAZEERA, UKRAINIAN AIR FORCE, IRNA, US CENTCOM"
N_STORIES = len(HEROES) + len(SMALL) + len(ONELINERS)  # 37

# ---------------------------------------------------------- pictograms ----
def draw_globe(cv, x, y, s):
    """COP31: a globe under a hot sun, cracked by the failed talks."""
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 4
    cv.circle(cx, cy, r, SEA)
    cv.circle(cx, cy, r, NAVY, fill=False)
    cv.circle(cx, cy, r - 8, NAVY, fill=False)
    cv.line(cx - r, cy, cx + r, cy, NAVY)
    cv.line(cx, cy - r, cx, cy + r, NAVY)
    sx, sy = x + s - 20, y + 16
    cv.circle(sx, sy, 7, RED)
    for dx, dy in ((0, -11), (0, 11), (-11, 0), (11, 0),
                   (-8, -8), (8, -8), (-8, 8), (8, 8)):
        cv.line(sx, sy, sx + dx, sy + dy, RED)
    cv.line(cx - 6, cy - 4, cx + 2, cy + 4, RED)
    cv.line(cx + 2, cy + 4, cx - 2, cy + 12, RED)


def draw_drone(cv, x, y, s):
    """Ukraine: a drone silhouette over a skyline."""
    cv.fill(x, y + s - 26, s, 26, LGREY)
    for bx, bw, bh in ((6, 14, 22), (26, 10, 30), (42, 16, 18),
                       (64, 12, 26), (82, 14, 16)):
        cv.fill(x + bx, y + s - 26 - bh + 22, bw, bh, NAVY)
    cx, cy = x + s // 2, y + 26
    cv.fill(cx - 16, cy - 5, 32, 10, INK)
    cv.fill(cx - 4, cy - 9, 8, 18, INK)
    for px in (cx - 22, cx + 22):
        cv.circle(px, cy - 6, 5, INK)
        cv.line(px - 10, cy - 6, px + 10, cy - 6, INK)
    for dx, dy in ((-24, 14), (18, 18), (0, 24)):
        cv.fill(cx + dx - 2, cy + dy, 4, 4, RED)


def draw_radar(cv, x, y, s):
    """Bahrain: a radar screen with a sweep and blips."""
    cx, cy = x + s // 2, y + s // 2
    r = s // 2 - 8
    cv.circle(cx, cy, r, SEA)
    cv.circle(cx, cy, r, NAVY, fill=False)
    cv.circle(cx, cy, r // 2, NAVY, fill=False)
    cv.line(cx - r, cy, cx + r, cy, NAVY)
    cv.line(cx, cy - r, cx, cy + r, NAVY)
    cv.line(cx, cy, cx + r - 6, cy - r + 6, RED)
    for bx, by in ((cx - 14, cy - 10), (cx + 16, cy + 8), (cx - 4, cy + 18)):
        cv.circle(bx, by, 4, RED)


def draw_ship(cv, x, y, s):
    """Baltic: a cargo ship on fire."""
    cv.fill(x, y + s - 22, s, 22, SEA)
    cv.poly([(x + 8, y + s - 34), (x + s - 8, y + s - 34),
             (x + s - 20, y + s - 16), (x + 20, y + s - 16)], INK)
    cv.fill(x + 18, y + s - 52, 16, 18, NAVY)
    cv.fill(x + 38, y + s - 52, 16, 18, RED)
    cv.fill(x + 58, y + s - 46, 16, 12, GOLD)
    fx, fbase = x + 40, y + s - 52
    cv.poly([(fx, fbase), (fx + 8, y + 8), (fx + 16, fbase)], RED)
    cv.poly([(fx + 4, fbase), (fx + 8, y + 20), (fx + 12, fbase)], GOLD)

PICTOS = {"globe": draw_globe, "drone": draw_drone,
          "radar": draw_radar, "ship": draw_ship}

# -------------------------------------------------------------- map -------
# Rough continent outlines in (lon, lat), equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-97, 16), (-92, 14), (-83, 9),
     (-79, 8), (-90, 13), (-100, 17), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-79, 8), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-57, -38), (-65, -45), (-70, -54),
     (-73, -50), (-73, -37), (-70, -20), (-77, -12), (-81, -6), (-80, 1)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31),
     (35, 28), (40, 15), (43, 11), (48, 11), (51, 10), (40, 0),
     (30, -10), (20, -18), (16, -28), (12, -32), (19, -35), (25, -30),
     (32, -26), (35, -18), (40, -10), (40, -5), (35, 5), (30, 10),
     (20, 8), (10, 4), (0, 5), (-8, 4), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57),
     (10, 59), (5, 60), (12, 56), (18, 56), (21, 55), (24, 59), (28, 60),
     (30, 62), (25, 65), (20, 70), (25, 71), (30, 70), (35, 68), (40, 68),
     (45, 66), (50, 68), (55, 68), (60, 69), (65, 68), (68, 66), (60, 60),
     (55, 55), (50, 52), (45, 47), (40, 47), (35, 45), (30, 46), (28, 44),
     (23, 40), (20, 40), (15, 44), (12, 44), (8, 44), (3, 42), (0, 40),
     (-2, 37), (-6, 36)],
    [(30, 70), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (158, 66), (162, 60), (158, 55), (150, 59), (142, 55), (140, 45),
     (135, 43), (130, 42), (127, 40), (126, 38), (122, 38), (120, 32),
     (122, 28), (118, 25), (110, 20), (108, 12), (105, 9), (100, 8),
     (98, 12), (95, 16), (92, 21), (88, 22), (86, 20), (80, 15), (77, 8),
     (75, 12), (72, 20), (68, 22), (65, 25), (62, 25), (58, 26), (56, 27),
     (52, 28), (50, 29), (48, 30), (44, 29), (40, 32), (38, 36), (36, 36),
     (35, 33), (34, 31), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# -------------------------------------------------------------- layout ----
MX = 20          # side margin
CW = W - 2 * MX  # content width


def section_head(cv, y, text):
    cv.fill(MX, y, CW, 16, INK)
    cv.text(MX + 6, y + 4, text, 1, WHITE)
    return y + 16


def num_chip(cv, x, y, n, size=18):
    cv.fill(x, y, size, size, RED)
    s = str(n)
    cv.text(x + size // 2, y + (size - 7) // 2, s, 1, WHITE, align="center")


def draw(cv):
    # ---- kicker bar ----
    cv.fill(0, 0, W, 26, BLACK)
    cv.text(12, 6, "ONE DAY OF WORLD NEWS, ONE PICTURE", 2, WHITE)
    cv.text(W - 12, 6, "%d STORIES - 7 REGIONS" % N_STORIES, 2, WHITE,
            align="right")

    # ---- masthead + red date banner ----
    cv.text(W // 2, 34, "THE WORLD IN ONE DAY", 5, INK, align="center")
    cv.fill(MX, 74, CW, 26, RED)
    cv.text(W // 2, 82, "SUNDAY, 22 NOVEMBER 2026", 2, WHITE, align="center")
    cv.hline(MX, 104, CW, INK, 2)

    # ---- UTC timeline strip ----
    y = 108
    cv.fill(MX, y, CW, 32, NAVY)
    cv.text(MX + 6, y + 12, "THE DAY IN UTC", 1, GOLD)
    colw = (CW - 130) // 4
    for i, (t, label) in enumerate(TIMELINE):
        ex = MX + 130 + i * colw
        cv.text(ex, y + 3, t, 2, WHITE)
        cv.text(ex, y + 20, label, 1, WHITE)
    y = 144

    # ---- heroes: 2x2, larger cards with illustrated scenes ----
    y = section_head(cv, y, "THE DAY IN FOUR STORIES")
    cell_w, cell_h = (CW - 8) // 2, 150
    for i, h in enumerate(HEROES):
        cx = MX + (i % 2) * (cell_w + 8)
        cy = y + (i // 2) * (cell_h + 6)
        cv.rect(cx, cy, cell_w, cell_h, INK, 1)
        cv.fill(cx, cy, cell_w, 20, LGREY)
        num_chip(cv, cx + 4, cy + 2, h["num"], 16)
        cv.text(cx + 26, cy + 6, h["tag"], 1, DARKRED)
        # illustrated scene, right side
        px, py = cx + cell_w - 108, cy + 26
        cv.rect(px, py, 100, 100, INK, 1)
        PICTOS[h["kind"]](cv, px, py, 100)
        tx, tw = cx + 8, cell_w - 124
        hy = cy + 28
        for ln in cv.wrap(h["head"], tw, 2)[:2]:
            cv.text(tx, hy, ln, 2, INK)
            hy += 16
        hy += 4
        for ln in cv.wrap(h["summ"], tw, 1)[:4]:
            cv.text(tx, hy, ln, 1, INK)
            hy += 10
        cv.text(tx, cy + cell_h - 13, "SOURCE: " + h["src"], 1, GREY)
    y += 2 * cell_h + 6

    # ---- small stories: 3 columns x 4 rows ----
    y = section_head(cv, y, "MORE OF THE DAY")
    col_w = (CW - 12) // 3
    row_h = 58
    for i, s in enumerate(SMALL):
        cx = MX + (i % 3) * (col_w + 6)
        cy = y + (i // 3) * row_h
        if i % 3 < 2:
            cv.vline(cx + col_w + 3, cy + 2, row_h - 4, LGREY, 1)
        num_chip(cv, cx, cy + 2, s["num"], 16)
        tx = cx + 22
        cv.text(tx, cy + 2, s["tag"], 1, DARKRED)
        hy = cy + 13
        for ln in cv.wrap(s["head"], col_w - 24, 2)[:2]:
            cv.text(tx, hy, ln, 2, INK)
            hy += 16
        for ln in cv.wrap(s["summ"], col_w - 24, 1)[:1]:
            cv.text(tx, hy, ln, 1, GREY)
    y += 4 * row_h

    # ---- world map ----
    y = section_head(cv, y, "WHERE IT HAPPENED")
    map_x, map_y, map_w, map_h = MX, y + 2, 640, 100
    cv.fill(map_x, map_y, map_w, map_h, SEA)
    cv.rect(map_x, map_y, map_w, map_h, INK, 1)
    for gx in range(map_x + 64, map_x + map_w, 64):
        cv.vline(gx, map_y, map_h, (220, 232, 238), 1)
    for gy in range(map_y + 25, map_y + map_h, 25):
        cv.hline(map_x, gy, map_w, (220, 232, 238), 1)

    def project(lon, lat):
        x = map_x + (lon + 170) * map_w / 360.0
        yy = map_y + (75 - lat) * map_h / 130.0
        return int(x), int(yy)

    for cont in CONTINENTS:
        cv.poly([project(lon, lat) for lon, lat in cont], LAND)
        pts = [project(lon, lat) for lon, lat in cont]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            cv.line(a[0], a[1], b[0], b[1], LANDLINE)
    offsets = [(14, 16), (-38, -18), (16, 6), (-4, -26)]
    for h, (dx, dy) in zip(HEROES, offsets):
        px, py = project(h["lon"], h["lat"])
        cv.circle(px, py, 6, RED)
        cv.circle(px, py, 6, WHITE, fill=False)
        lx = min(max(px + dx, map_x + 2), map_x + map_w - 16)
        ly = min(max(py + dy, map_y + 12), map_y + map_h - 12)
        cv.line(px, py, lx + 6, ly + 5, RED)
        cv.fill(lx - 1, ly - 5, 14, 11, RED)
        cv.text(lx + 6, ly - 2, str(h["num"]), 1, WHITE, align="center")
    lx = map_x + map_w + 14
    cv.text(lx, map_y + 2, "THE FOUR BIG STORIES", 1, DARKRED)
    for i, h in enumerate(HEROES):
        yy = map_y + 16 + i * 21
        num_chip(cv, lx, yy, h["num"], 14)
        for ln in cv.wrap(h["head"], 300, 1)[:1]:
            cv.text(lx + 20, yy + 3, ln, 1, INK)
        cv.text(lx + 20, yy + 12, h["tag"].title(), 1, GREY)
    y = map_y + map_h + 4

    # ---- also on 22 november: one-liners, 2 columns ----
    y = section_head(cv, y, "ALSO ON 22 NOVEMBER")
    col_w2 = (CW - 8) // 2
    row_h2 = 11
    for i, (region, text) in enumerate(ONELINERS):
        cx = MX + (i % 2) * (col_w2 + 8)
        cy = y + (i // 2) * row_h2
        n = 17 + i
        cv.text(cx, cy, "%d." % n, 1, RED)
        cv.text(cx + 26, cy, region + " - " + text, 1, INK)
    y += ((len(ONELINERS) + 1) // 2) * row_h2

    # ---- date check banner ----
    cv.fill(MX, y, CW, 20, RED)
    cv.text(W // 2, y + 6,
            "DATE CHECK: EVERY STORY HERE HAPPENED OR WAS FIRST REPORTED "
            "ON 22 NOVEMBER 2026", 1, WHITE, align="center")
    y += 20

    # ---- footer ----
    cv.text(MX, y + 3,
            "DRAWN ILLUSTRATION - AN ILLUSTRATED SUMMARY, NOT PHOTOGRAPHS.",
            1, GREY)
    cv.text(MX, y + 13, "SOURCES: " + SOURCES + ".", 1, GREY)
    y += 24
    assert y <= H, "layout overflow: %d > %d" % (y, H)
    return y


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = Canvas()
    end_y = draw(cv)
    path = os.path.join(outdir, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes), layout ends at y=%d, stories=%d"
          % (path, size, end_y, N_STORIES))


if __name__ == "__main__":
    main()
