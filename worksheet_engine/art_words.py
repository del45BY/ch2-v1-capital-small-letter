"""
43 ilustrasi vektor tambahan untuk tema "Tracing Words" (gaya sama dengan art.py:
garis tebal, bentuk bulat, wajah ramah). Semua digambar dalam kotak 100x100 unit berpusat di (0,0).
Gambar PNG di assets/images/<kata>.png selalu didahulukan (lihat art.py).
"""
import math
from contextlib import contextmanager
from reportlab.lib.colors import HexColor, white
from .art import BASE_LW, INK, Ink

SKIN, SKIN_DK = "#F2C29B", "#E8A98A"


# ------------------------------------------------------------------ helper kecil
@contextmanager
def rotated(k, cx, cy, ang):
    k.c.saveState(); k.c.translate(cx, cy); k.c.rotate(ang)
    yield
    k.c.restoreState()


@contextmanager
def clip_path(k, fn):
    k.c.saveState()
    p = k.c.beginPath(); fn(p)
    k.c.clipPath(p, stroke=0, fill=0)
    yield
    k.c.restoreState()


def E(k, cx, cy, rx, ry, ang=0):
    """Elips (boleh diputar) untuk dilebur menjadi satu bentuk."""
    def f(stroke):
        c = k.c; c.saveState(); c.translate(cx, cy); c.rotate(ang)
        c.ellipse(-rx, -ry, rx, ry, stroke=stroke, fill=1); c.restoreState()
    return f


def C(k, x, y, r):
    return lambda stroke: k.c.circle(x, y, r, stroke=stroke, fill=1)


def R(k, x, y, w, h, r):
    return lambda stroke: k.c.roundRect(x, y, w, h, r, stroke=stroke, fill=1)


def fuse(k, color, shapes):
    """Beberapa bentuk digabung jadi SATU siluet dengan satu garis tepi."""
    k._set(color)
    k.c.setLineWidth(BASE_LW * 2)
    for s in shapes:
        s(1)
    for s in shapes:
        s(0)


def star_pts(cx, cy, ro, ri, n=5):
    out = []
    for i in range(n * 2):
        a = math.pi / 2 + i * math.pi / n
        r = ro if i % 2 == 0 else ri
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def dark(k, x, y, r):
    k.circle(x, y, r, "#2B2B3A", keep=True, stroke=0)


# ================================================================== PETERNAKAN
def duck(k):
    for x in (-8, 8):
        k.line(x, -38, x, -48, "#FF9F1C", w=1.4); k.line(x - 7, -48, x + 6, -48, "#FF9F1C", w=1.4)
    k.poly([(-30, -4), (-52, 10), (-32, 14)], "#FFC94D")
    k.ellipse(-4, -14, 34, 26, "#FFE27A")
    k.ellipse(-12, -14, 16, 11, "#FFC94D")
    k.circle(20, 22, 18, "#FFE27A")
    k.ellipse(40, 17, 11, 6, "#FF9F1C")
    k.eye(26, 27, 3.6); k.blush(22, 16, 0, 4.2)


def horse(k):
    k.poly([(-18, 26), (-24, 46), (-7, 34)], "#B9855A"); k.poly([(18, 26), (24, 46), (7, 34)], "#B9855A")
    k.ellipse(0, 4, 29, 38, "#5B3A29")
    k.ellipse(0, 0, 22, 35, "#B9855A")
    k.ellipse(0, 8, 5, 23, "#FFFFFF", stroke=0)
    k.ellipse(0, -26, 16, 10, "#E6C3A0")
    dark(k, -6, -26, 2.5); dark(k, 6, -26, 2.5)
    k.eyes(0, 10, 25, 3.8)
    k.ellipse(0, 34, 14, 9, "#5B3A29")


# ================================================================== HEWAN LAUT
def fish(k):
    k.poly([(-26, 0), (-52, 22), (-52, -22)], "#FF9F1C")
    k.poly([(-8, 20), (6, 38), (16, 20)], "#FFB347")
    k.poly([(-4, -20), (8, -34), (14, -20)], "#FFB347")
    k.ellipse(0, 0, 36, 24, "#FF8A3D")
    with k.clip_ellipse(0, 0, 35, 23):
        k.rrect(-12, -30, 8, 60, 0, "#FFFFFF", stroke=0); k.rrect(6, -30, 8, 60, 0, "#FFFFFF", stroke=0)
    k.eye(20, 6, 3.8); k.smile(26, -5, 5)


def whale(k):
    k.poly([(-36, -4), (-50, 14), (-56, 32), (-40, 26), (-30, 14)], "#5AA9E6")
    k.ellipse(0, -10, 42, 28, "#6BB6F2")
    with k.clip_ellipse(0, -10, 41, 27):
        k.ellipse(8, -30, 38, 15, "#E3F4FF", stroke=0)
    k.eye(22, -2, 3.8); k.smile(28, -12, 6); k.blush(18, -10, 0, 4.2)
    k.line(8, 18, 8, 30, "#6BB6F2", w=1.2)
    for x, y, r in [(0, 40, 4.2), (16, 40, 4.2), (8, 46, 3.4)]:
        k.circle(x, y, r, "#BEE6FF")


def crab(k):
    for s in (-1, 1):
        for (x0, y0, x1, y1) in [(24, -12, 50, -30), (28, -6, 52, -12), (28, 0, 50, 4)]:
            k.line(s * x0, y0, s * x1, y1, "#E8503F", w=1.3)
        k.line(s * 24, 6, s * 38, 22, "#E8503F", w=1.6)
    k.ellipse(0, -8, 30, 20, "#FF6B5E")
    for s in (-1, 1):
        k.line(s * 8, 8, s * 8, 22, "#E8503F", w=1.0)
        k.eye(s * 8, 26, 3.6, light=True)
        k.circle(s * 42, 28, 11, "#FF6B5E")
        k.line(s * 42, 28, s * 48, 38, "#E8503F", w=1.0)
    k.smile(0, -4, 7); k.blush(0, -6, 38, 4.2)


def octopus(k):
    for x, h in [(-26, 16), (-9, 22), (9, 22), (26, 16)]:
        k.ellipse(x, -22, 9, h, "#B38BE6")
    k.circle(0, 12, 28, "#B38BE6")
    if k.mode == "color":
        k.c.setFillColor(HexColor("#CDB3F2"))
        for x, y in [(-12, 30), (10, 32), (18, 22)]:
            k.c.circle(x, y, 3.2, stroke=0, fill=1)
    k.eyes(0, 14, 22, 4); k.smile(0, 5, 7); k.blush(0, 8, 40, 4.5)


def turtle(k):
    k.ellipse(-22, -26, 10, 8, "#A8E6A1"); k.ellipse(20, -26, 10, 8, "#A8E6A1")
    k.poly([(-34, -8), (-52, -12), (-34, -18)], "#A8E6A1")
    k.circle(38, -2, 14, "#A8E6A1")
    k.ellipse(0, -2, 36, 28, "#6FCF7F")
    hexp = [(-12, -2), (-6, 10), (6, 10), (12, -2), (6, -14), (-6, -14)]
    k.poly(hexp, "#4FB36A")
    for (x, y), (x2, y2) in zip(hexp, [(-30, -2), (-20, 20), (20, 20), (30, -2), (20, -22), (-20, -22)]):
        k.line(x, y, x2, y2, "#4FB36A", w=.7)
    k.eye(42, 2, 3.2); k.smile(42, -6, 4.5)


# ================================================================== BUAH
def banana(k):
    def shape(p):
        p.moveTo(-34, 30)
        p.curveTo(-40, -34, 14, -50, 44, -2)
        p.curveTo(48, 4, 40, 8, 34, 2)
        p.curveTo(12, -22, -6, -14, -10, 38)
        p.close()
    k.path(shape, "#FFD23F")
    k.rrect(-34, 34, 20, 9, 3, "#8B5E3C")
    k.circle(43, -2, 3.6, "#6B4A2B")
    k.eyes(-16, 4, 13, 3.2); k.smile(-16, -4, 5); k.blush(-16, -1, 25, 3.2)
    k.shine(lambda p: (p.moveTo(-26, 24), p.curveTo(-30, 8, -26, -6, -14, -18)), w=.6)


def orange(k):
    k.circle(0, -2, 33, "#FFA62B")
    k.rrect(-2, 28, 4, 8, 1.5, "#8B5E3C"); k.ellipse(9, 34, 12, 6, "#5CCB6B")
    if k.mode == "color":
        k.c.setFillColor(HexColor("#FFC468"))
        for x, y in [(-18, 16), (16, 18), (22, -14), (-24, -14), (4, -30)]:
            k.c.circle(x, y, 2.2, stroke=0, fill=1)
    k.eyes(0, 4, 22, 4); k.smile(0, -6, 8); k.blush(0, -2, 40, 5)
    k.shine(lambda p: (p.moveTo(-22, 14), p.curveTo(-26, 6, -26, 0, -24, -6)))


def pineapple(k):
    for pts in ([(-12, 20), (-24, 46), (-4, 28)], [(-2, 24), (-8, 52), (8, 24)], [(4, 28), (22, 48), (12, 20)],
                [(-18, 22), (-34, 34), (-14, 28)]):
        k.poly(pts, "#5CCB6B")
    k.ellipse(0, -12, 26, 34, "#FFC83D")
    if k.mode == "color":
        with k.clip_ellipse(0, -12, 25, 33):
            for i in range(-4, 5):
                k.line(-40 + i * 14, -60, 20 + i * 14, 40, "#E8A100", w=.45)
                k.line(40 + i * 14, -60, -20 + i * 14, 40, "#E8A100", w=.45)
    k.circle(0, -4, 14, "#FFC83D", stroke=0)
    k.eyes(0, -2, 16, 3.6); k.smile(0, -10, 6); k.blush(0, -6, 30, 4)


def grape(k):
    k.circle(0, -28, 13, "#9B6BD6")
    for x, y in [(-10, -6), (10, -6)]:
        k.circle(x, y, 13, "#9B6BD6")
    for x, y in [(-20, 16), (0, 16), (20, 16)]:
        k.circle(x, y, 13, "#9B6BD6")
    k.line(0, 29, 2, 42, "#8B5E3C", w=1.2); k.ellipse(16, 44, 12, 5, "#5CCB6B")
    k.eyes(0, -4, 12, 2.8); k.smile(0, -9, 4)
    k.shine(lambda p: (p.moveTo(-24, 20), p.lineTo(-24, 14)), w=.6)


# ================================================================== SAYURAN
def carrot(k):
    for x, y, h in [(-8, 38, 14), (0, 42, 16), (8, 38, 14)]:
        k.ellipse(x, y, 6, h, "#5CCB6B")
    k.poly([(-17, 30), (17, 30), (0, -50)], "#FF8A3D")
    for y, w in [(14, 7), (-4, 5), (-20, 3.5)]:
        k.line(-w, y, w * .4, y, "#E06A1F", w=.6)
    k.eyes(0, 18, 14, 3.4); k.smile(0, 10, 5.5); k.blush(0, 12, 26, 3.6)


def spinach(k):
    k.rrect(-3, -48, 6, 24, 2, "#9FDC8A")
    def leaf(p):
        p.moveTo(0, 46); p.curveTo(-48, 26, -46, -28, 0, -32)
        p.curveTo(46, -28, 48, 26, 0, 46); p.close()
    k.path(leaf, "#3FB760")
    k.line(0, -30, 0, 36, "#2E9A4C", w=.7)
    for y in (-10, 6, 20):
        k.line(0, y, -16, y + 10, "#2E9A4C", w=.5); k.line(0, y, 16, y + 10, "#2E9A4C", w=.5)
    k.eyes(0, 4, 22, 3.8); k.smile(0, -6, 7); k.blush(0, -2, 38, 4.5)


def tomato(k):
    k.circle(0, -4, 33, "#FF5A5F")
    k.poly([(-16, 28), (-6, 25), (0, 38), (6, 25), (16, 28), (8, 20), (-8, 20)], "#4CC96A")
    k.rrect(-2, 32, 4, 10, 1.5, "#4CA05A")
    k.eyes(0, 2, 22, 4); k.smile(0, -8, 8); k.blush(0, -4, 40, 5)
    k.shine(lambda p: (p.moveTo(-24, 14), p.curveTo(-28, 6, -28, -2, -26, -8)))


def corn(k):
    k.ellipse(0, 8, 20, 38, "#FFD23F")
    if k.mode == "color":
        with k.clip_ellipse(0, 8, 19, 37):
            k.c.setFillColor(HexColor("#F2B600"))
            for x in range(-18, 19, 9):
                for y in range(-26, 46, 9):
                    k.c.circle(x, y, 2.8, stroke=0, fill=1)
    k.poly([(0, -48), (-34, -8), (-26, 16), (0, -14)], "#5CCB6B")
    k.poly([(0, -48), (34, -8), (26, 16), (0, -14)], "#4CB85C")
    k.circle(0, 28, 11, "#FFD23F", stroke=0)
    k.eyes(0, 28, 12, 3.2); k.smile(0, 22, 4.5)


def potato(k):
    k.blob([(-14, 0, 20), (12, -4, 22), (0, 10, 18)], "#C99A6B")
    if k.mode == "color":
        k.c.setFillColor(HexColor("#A9794A"))
        for x, y in [(-22, -10), (20, -16), (8, 24), (-8, -22)]:
            k.c.ellipse(x - 3.2, y - 2.2, x + 3.2, y + 2.2, stroke=0, fill=1)
    k.eyes(0, 6, 18, 3.8); k.smile(0, -2, 7); k.blush(0, 0, 34, 4.5)


# ================================================================== KENDARAAN
def _wheel(k, x, y, r=11):
    k.circle(x, y, r, "#2B2B3A", keep=True); k.circle(x, y, r * .45, "#C9C9D6", keep=True)


def car(k):
    k.rrect(-44, -18, 88, 28, 10, "#FF6B5E")
    k.poly([(-26, 10), (-16, 34), (18, 34), (32, 10)], "#FF6B5E")
    k.poly([(-21, 12), (-14, 29), (2, 29), (2, 12)], "#BEE6FF"); k.poly([(7, 12), (7, 29), (17, 29), (26, 12)], "#BEE6FF")
    k.circle(40, -3, 4.5, "#FFE27A"); k.rrect(-46, -8, 5, 8, 2, "#FFB347")
    _wheel(k, -24, -18); _wheel(k, 24, -18)


def bus(k):
    k.rrect(-46, -24, 92, 56, 10, "#FFC83D")
    for i in range(3):
        k.rrect(-40 + i * 24, 6, 20, 18, 3, "#BEE6FF")
    k.rrect(32, 2, 10, 26, 2, "#BEE6FF")
    k.line(-46, -6, 46, -6, "#FF7A6B", w=1.4)
    k.circle(43, -14, 3.4, "#FFFFFF"); _wheel(k, -28, -24); _wheel(k, 28, -24)


def train(k):
    for x, y, r in [(-28, 46, 6.5), (-20, 52, 4.5)]:
        k.circle(x, y, r, "#E4E4EE")
    k.rrect(-34, 16, 14, 18, 3, "#2B2B3A", keep=True); k.rrect(-38, 32, 22, 6, 3, "#2B2B3A", keep=True)
    k.rrect(-42, -14, 52, 32, 6, "#4FB3E8")
    k.circle(-42, 2, 4, "#FFE27A")
    k.rrect(10, -14, 32, 48, 5, "#FF7A6B")
    k.rrect(16, 10, 20, 16, 3, "#BEE6FF")
    k.rrect(6, 32, 40, 8, 3, "#2B2B3A", keep=True)
    k.rrect(-46, -26, 92, 12, 3, "#2B2B3A", keep=True)
    for x in (-28, -6, 24):
        k.circle(x, -26, 10, "#FF7A6B"); k.circle(x, -26, 4, "#FFFFFF", keep=True)


def ship(k):
    k.poly([(-46, -8), (46, -8), (32, -30), (-32, -30)], "#FF6B5E")
    k.rrect(-22, -8, 42, 26, 3, "#FFFFFF")
    for x in (-12, 0, 12):
        k.circle(x, 6, 4.2, "#BEE6FF")
    k.rrect(-8, 18, 16, 16, 2, "#FFC83D"); k.rrect(-10, 32, 20, 6, 2, "#2B2B3A", keep=True)
    k.line(24, -8, 24, 34, "#2B2B3A", w=.7); k.poly([(24, 34), (24, 20), (40, 27)], "#FFD23F")
    for x in (-30, 0, 30):
        k.ellipse(x, -36, 18, 7, "#4FB3E8")


def airplane(k):
    k.poly([(-36, 6), (-50, 32), (-38, 32), (-18, 8)], "#FF6B5E")
    k.ellipse(0, 0, 46, 13, "#FFFFFF")
    k.poly([(-2, -4), (-26, -36), (-12, -36), (16, -4)], "#FF6B5E")
    for x in (-18, -8, 2, 12):
        k.circle(x, 3, 3.4, "#4FB3E8")
    k.ellipse(34, 3, 8, 5, "#4FB3E8")


# ================================================================== ANGGOTA TUBUH
def eye_part(k):
    def almond(p):
        p.moveTo(-46, 0); p.curveTo(-26, 36, 26, 36, 46, 0); p.curveTo(26, -36, -26, -36, -46, 0); p.close()
    for x, y, x2, y2 in [(-26, 24, -34, 38), (0, 30, 0, 46), (26, 24, 34, 38)]:
        k.line(x, y, x2, y2, "#2B2B3A", w=1.0)
    k.path(almond, "#FFFFFF")
    with clip_path(k, almond):
        k.circle(0, 0, 18, "#4FB3E8"); k.circle(0, 0, 9, "#2B2B3A", keep=True)
    k.circle(6, 7, 3.4, "#FFFFFF", keep=True, stroke=0)
    k.stroke_path(almond, "#2B2B3A", 1.0)


def nose(k):
    def shape(p):
        p.moveTo(-9, 42); p.curveTo(-12, 12, -32, -2, -27, -20)
        p.curveTo(-24, -34, -5, -34, 0, -27); p.curveTo(5, -34, 24, -34, 27, -20)
        p.curveTo(32, -2, 12, 12, 9, 42); p.close()
    k.path(shape, SKIN)
    k.ellipse(-11, -20, 5.4, 3.6, "#B97F5C", stroke=0); k.ellipse(11, -20, 5.4, 3.6, "#B97F5C", stroke=0)
    k.shine(lambda p: (p.moveTo(-4, 30), p.curveTo(-6, 18, -8, 10, -12, 2)), w=.6)


def ear(k):
    fuse(k, SKIN, [E(k, 0, 8, 25, 34), E(k, -3, -26, 11, 9)])
    k.ellipse(3, 10, 14, 24, SKIN_DK, stroke=0)
    k.stroke_path(lambda p: (p.moveTo(-8, 24), p.curveTo(-18, 6, -10, -16, 8, -12)), "#B97F5C", .9)
    k.stroke_path(lambda p: (p.moveTo(-2, 12), p.curveTo(-6, 4, 0, -4, 7, 0)), "#B97F5C", .8)
    k.circle(4, -6, 2.6, SKIN_DK, stroke=0)


def mouth(k):
    def bowl(p):
        p.moveTo(-42, 12); p.curveTo(-30, -42, 30, -42, 42, 12); p.curveTo(20, 18, -20, 18, -42, 12); p.close()
    k.path(bowl, "#B8323F")
    with clip_path(k, bowl):
        k.rrect(-46, 2, 92, 10, 0, "#FFFFFF", stroke=0)
        k.ellipse(0, -22, 18, 11, "#FF8FA3", stroke=0)
    k.stroke_path(lambda p: (p.moveTo(-42, 12), p.curveTo(-20, 18, 20, 18, 42, 12)), "#E8505B", 1.8)


def hand(k):
    fuse(k, SKIN, [E(k, 0, -12, 26, 24), E(k, -22, 14, 6.6, 16, 14), E(k, -9, 25, 7, 22, 5),
                   E(k, 5, 27, 7.2, 24, -2), E(k, 18, 23, 7, 21, -9), E(k, 30, -4, 7.6, 17, -52)])
    if k.mode == "color":
        k.stroke_path(lambda p: (p.moveTo(-12, -6), p.curveTo(-2, -12, 10, -10, 16, -2)), "#C98F6C", .6)
        k.stroke_path(lambda p: (p.moveTo(-14, -18), p.curveTo(-4, -22, 8, -20, 14, -14)), "#C98F6C", .6)


# ================================================================== KELUARGA & RUMAH
def person(k, cx, cy, s, hair, shirt, kind, skin=SKIN):
    c = k.c
    c.saveState(); c.translate(cx, cy); c.scale(s, s)
    if kind == "mom":
        k.ellipse(0, 0, 28, 36, hair)
    k.ellipse(0, -34, 29, 20, shirt)
    if kind == "dad":
        k.poly([(-6, -17), (6, -17), (3, -26), (-3, -26)], "#FFFFFF"); k.poly([(-2.6, -26), (2.6, -26), (3.4, -44), (0, -48), (-3.4, -44)], "#FF6B5E")
    k.circle(-20, 4, 4.4, skin); k.circle(20, 4, 4.4, skin)
    k.ellipse(0, 6, 20, 21, skin)
    def cap(p):
        p.moveTo(-21, 10); p.curveTo(-24, 38, 24, 38, 21, 10); p.curveTo(12, 24, -12, 24, -21, 10); p.close()
    k.path(cap, hair)
    if kind == "mom":
        k.ellipse(-22, -4, 5, 18, hair, stroke=1); k.ellipse(22, -4, 5, 18, hair, stroke=1)
    if kind == "kid":
        k.circle(-22, 22, 7, hair); k.circle(22, 22, 7, hair)
    k.eyes(0, 4, 15, 2.9); k.smile(0, -4, 5.5); k.blush(0, -1, 29, 3.6)
    if kind == "dad":
        k.ellipse(0, -7, 8, 2.8, hair, stroke=0)
    c.restoreState()


def father(k):
    person(k, 0, 6, 1.0, "#3B2A20", "#4FB3E8", "dad")


def mother(k):
    person(k, 0, 6, 1.0, "#7A4B2A", "#FF7A9C", "mom")


def sibling(k):
    person(k, 22, 0, .66, "#8B4A2B", "#4CC9A0", "kid", "#E8B48A")
    person(k, -16, 4, .84, "#3B2A20", "#FFC83D", "kid")


def room(k):
    k.rrect(10, 12, 34, 32, 4, "#BEE6FF"); k.line(27, 12, 27, 44, w=.6); k.line(10, 28, 44, 28, w=.6)
    k.rrect(-48, -30, 8, 54, 3, "#A9744F")
    k.rrect(-44, -24, 90, 22, 5, "#FFFFFF")
    k.rrect(-14, -22, 60, 24, 6, "#4FB3E8")
    k.rrect(-40, -6, 28, 13, 6, "#FFF1C9")
    k.rrect(-46, -40, 7, 12, 2, "#A9744F"); k.rrect(38, -40, 7, 16, 2, "#A9744F")
    k.poly(star_pts(14, -10, 6, 2.6), "#FFD23F")


def door(k):
    k.rrect(-32, -50, 64, 100, 4, "#8B5E3C")
    k.rrect(-25, -50, 50, 94, 3, "#C98B4E")
    k.rrect(-17, -42, 34, 38, 3, "#B07638"); k.rrect(-17, 2, 34, 34, 3, "#B07638")
    k.circle(16, -6, 4.2, "#FFD23F")


# ================================================================== PERLENGKAPAN SEKOLAH
def book(k):
    k.rrect(-22, -42, 56, 76, 4, "#FFFFFF")
    k.rrect(-32, -38, 58, 76, 6, "#4FB3E8")
    k.rrect(-32, -38, 12, 76, 6, "#3A8FC0")
    k.rrect(-12, 2, 30, 26, 4, "#FFF1C9")
    k.poly(star_pts(-3, 24, 7, 3), "#FFC83D")
    k.eyes(3, 12, 12, 2.4); k.smile(3, 7, 4)
    k.line(-8, -16, 14, -16, "#FFFFFF", w=.8); k.line(-8, -26, 8, -26, "#FFFFFF", w=.8)


def pencil(k):
    with rotated(k, 0, 0, -40):
        k.rrect(-11, -36, 22, 56, 3, "#FFC83D")
        k.rrect(-11, -48, 22, 12, 3, "#FF9EB5")
        k.rrect(-11, -38, 22, 5, 0, "#C9C9D6")
        k.poly([(-11, 20), (11, 20), (0, 42)], "#F2D2A0")
        k.poly([(-3.8, 33), (3.8, 33), (0, 42)], "#2B2B3A", keep=True)
        k.eyes(0, -2, 10, 2.6); k.smile(0, -9, 4)


def bag(k):
    k.stroke_path(lambda p: (p.moveTo(-10, 36), p.curveTo(-10, 52, 10, 52, 10, 36)), "#C9553F", 1.6)
    k.rrect(-34, -12, 8, 32, 4, "#E85A4A"); k.rrect(26, -12, 8, 32, 4, "#E85A4A")
    k.rrect(-30, -42, 60, 78, 18, "#FF7A6B")
    k.rrect(-22, -38, 44, 30, 9, "#FFB1A8")
    k.line(-22, -23, 22, -23, "#E85A4A", w=.5); k.circle(0, -23, 3.4, "#FFD23F")
    k.eyes(0, 20, 20, 3.6); k.smile(0, 12, 7); k.blush(0, 14, 38, 4.2)


def eraser(k):
    with rotated(k, 0, 0, -18):
        k.rrect(-40, -20, 80, 40, 8, "#FF9EB5")
        k.rrect(-2, -22, 42, 44, 6, "#4FB3E8")
        k.rrect(18, -22, 6, 44, 0, "#FFFFFF", stroke=0)
        k.eyes(-20, 3, 16, 3.6); k.smile(-20, -5, 6); k.blush(-20, -1, 32, 4)


def table(k):
    k.rrect(-40, -46, 9, 54, 2, "#A9744F"); k.rrect(31, -46, 9, 54, 2, "#A9744F")
    k.rrect(-36, -6, 72, 10, 2, "#B07638")
    k.rrect(-48, 4, 96, 14, 5, "#C98B4E")
    k.rrect(-10, 18, 20, 18, 4, "#4FB3E8"); k.rrect(-12, 34, 24, 5, 2, "#3A8FC0")
    k.poly(star_pts(0, 27, 5, 2.2), "#FFD23F")


# ================================================================== CUACA & ALAM
def rain(k):
    for x, y in [(-20, -22), (0, -34), (20, -22), (-8, -46)]:
        k.poly([(x - 5, y), (x + 5, y), (x, y + 12)], "#4FB3E8"); k.circle(x, y, 5, "#4FB3E8")
    k.blob([(-22, 22, 18), (0, 30, 22), (24, 22, 17), (0, 18, 20)], "#CBD5E6")
    k.eyes(0, 24, 18, 3.8); k.smile(0, 17, 6); k.blush(0, 20, 34, 4.2)


def cloud(k):
    k.blob([(-24, -4, 20), (0, 8, 28), (26, -4, 21), (0, -8, 24)], "#FFFFFF")
    if k.mode == "color":
        k.c.setFillColor(HexColor("#E3F4FF")); k.c.ellipse(-30, -22, 28, -14, stroke=0, fill=1)
    k.eyes(0, 4, 20, 4); k.smile(0, -6, 7); k.blush(0, -2, 38, 4.6)
    k.shine(lambda p: (p.moveTo(-14, 28), p.curveTo(-22, 26, -26, 20, -26, 14)))


def moon(k):
    def shape(p):
        p.moveTo(22, 44); p.curveTo(-38, 42, -38, -42, 22, -44); p.curveTo(-8, -26, -8, 26, 22, 44); p.close()
    k.path(shape, "#FFD23F")
    k.eye(-14, 6, 3.4); k.smile(-12, -4, 5); k.blush(-14, -2, 0, 3.6)
    for x, y, r in [(34, 24, 7), (40, -8, 5)]:
        k.poly(star_pts(x, y, r, r * .45), "#FFE27A")


def star(k):
    k.poly(star_pts(0, 2, 46, 21), "#FFD23F")
    k.eyes(0, 4, 17, 3.8); k.smile(0, -4, 7); k.blush(0, -1, 32, 4.4)


# ================================================================== MAKANAN & MINUMAN
def rice(k):
    k.blob([(-20, 8, 14), (0, 16, 16), (20, 8, 14), (-8, 2, 15), (10, 2, 15)], "#FFFFFF")
    k.rrect(-16, -42, 32, 10, 3, "#3A8FC0")
    def bowl(p):
        p.moveTo(-42, 4); p.curveTo(-42, -42, 42, -42, 42, 4); p.close()
    k.path(bowl, "#4FB3E8")
    k.ellipse(0, 4, 42, 6, "#3A8FC0")
    k.eyes(0, -12, 20, 3.8); k.smile(0, -20, 7); k.blush(0, -16, 38, 4.2)


def bread(k):
    c = k.c
    fuse(k, "#D9A066", [R(k, -30, -40, 60, 56, 10), C(k, -17, 18, 17), C(k, 17, 18, 17)])
    k._set("#FFE6B8")
    k.c.roundRect(-24, -34, 48, 48, 7, stroke=0, fill=1)
    k.c.circle(-17, 18, 11, stroke=0, fill=1); k.c.circle(17, 18, 11, stroke=0, fill=1)
    k.eyes(0, 2, 18, 3.6); k.smile(0, -8, 7); k.blush(0, -4, 34, 4.2)


def water(k):
    k.poly([(-26, 44), (26, 44), (19, -42), (-19, -42)], "#EAF6FF")
    k.poly([(-24.2, 22), (24.2, 22), (19.2, -40), (-19.2, -40)], "#7FC8F8")
    k.ellipse(0, 22, 24.2, 5, "#BEE6FF")
    k.eyes(0, 2, 16, 3.6); k.smile(0, -6, 6); k.blush(0, -3, 30, 3.8)
    for x, y, r in [(-9, -26, 3), (8, -20, 2.2), (-4, -32, 1.8)]:
        k.circle(x, y, r, "#FFFFFF", stroke=0)


WORD_DRAWERS = {
    "duck": duck, "horse": horse, "fish": fish, "whale": whale, "crab": crab, "octopus": octopus,
    "turtle": turtle, "banana": banana, "orange": orange, "pineapple": pineapple, "grape": grape,
    "carrot": carrot, "spinach": spinach, "tomato": tomato, "corn": corn, "potato": potato,
    "car": car, "bus": bus, "train": train, "ship": ship, "airplane": airplane,
    "eye": eye_part, "nose": nose, "ear": ear, "mouth": mouth, "hand": hand,
    "father": father, "mother": mother, "sibling": sibling, "room": room, "door": door,
    "book": book, "pencil": pencil, "bag": bag, "eraser": eraser, "table": table,
    "rain": rain, "cloud": cloud, "moon": moon, "star": star,
    "rice": rice, "bread": bread, "water": water,
}
