"""
Font GORESAN TUNGGAL untuk huruf tracing (satu garis titik-titik di tengah goresan, bukan tepi huruf).

Setiap huruf = daftar goresan; tiap goresan = daftar titik (x, y) dalam "satuan garis bantu":
    baseline y = 0,  garis tengah (tinggi huruf kecil) y = 1,  garis atas (huruf kapital/tinggi) y = 2,  turun y = -0.8
Gaya "bola dan tongkat" (a, d, g, q = lingkaran + tongkat) seperti buku belajar menulis prasekolah.
Titik pertama tiap goresan = tempat mulai menulis (ditandai titik hijau oleh trace_word).
Hanya huruf A-Z a-z, spasi, tanda hubung (-), dan apostrof (') yang tersedia.
"""
import math
from reportlab.lib.colors import white
from .config import PALETTE, hx

SPACING = 0.55                      # jarak antar huruf (satuan)


def L(*pts):
    return [tuple(p) for p in pts]


def A(cx, cy, rx, ry, a0, a1, n=28):
    """Busur elips dari sudut a0 ke a1 (derajat; a1 > a0 = berlawanan jarum jam)."""
    steps = max(4, int(abs(a1 - a0) / 360 * n * 2))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]


def J(*parts):
    """Sambung beberapa potongan menjadi satu goresan."""
    out = []
    for p in parts:
        out += p if not out else p[1:] if out[-1] == p[0] else p
    return out


def dotp(x, y):
    return [(x, y)]


# (lebar, [goresan...])
G = {
    # ------------------------------------------------ huruf kecil
    "a": (1.0, [A(.5, .5, .5, .5, 50, 410), L((1, 1), (1, 0))]),
    "b": (1.0, [L((0, 2), (0, 0)), A(.5, .5, .5, .5, 180, -180)]),
    "c": (0.95, [A(.5, .5, .5, .5, 45, 315)]),
    "d": (1.0, [A(.5, .5, .5, .5, 50, 410), L((1, 2), (1, 0))]),
    "e": (1.0, [J(L((0, .5), (1, .5)), A(.5, .5, .5, .5, 0, 315))]),
    "f": (1.0, [J(A(.9, 1.6, .4, .4, 90, 180), L((.5, 1.6), (.5, 0))), L((0, 1), (1, 1))]),
    "g": (1.0, [A(.5, .5, .5, .5, 50, 410), J(L((1, 1), (1, -.3)), A(.5, -.3, .5, .5, 0, -160))]),
    "h": (1.0, [L((0, 2), (0, 0)), J(A(.5, .5, .5, .5, 180, 0), L((1, .5), (1, 0)))]),
    "i": (0.2, [L((.1, 1), (.1, 0)), dotp(.1, 1.5)]),
    "j": (0.6, [J(L((.5, 1), (.5, -.3)), A(.05, -.3, .45, .5, 0, -150)), dotp(.5, 1.5)]),
    "k": (1.0, [L((0, 2), (0, 0)), L((.95, 1), (0, .4)), L((.3, .65), (.95, 0))]),
    "l": (0.2, [L((.1, 2), (.1, 0))]),
    "m": (1.8, [L((0, 1), (0, 0)), J(A(.45, .55, .45, .45, 180, 0), L((.9, .55), (.9, 0))),
                J(A(1.35, .55, .45, .45, 180, 0), L((1.8, .55), (1.8, 0)))]),
    "n": (1.0, [L((0, 1), (0, 0)), J(A(.5, .5, .5, .5, 180, 0), L((1, .5), (1, 0)))]),
    "o": (1.0, [A(.5, .5, .5, .5, 90, 450)]),
    "p": (1.0, [L((0, 1), (0, -.8)), A(.5, .5, .5, .5, 180, -180)]),
    "q": (1.0, [A(.5, .5, .5, .5, 50, 410), L((1, 1), (1, -.8))]),
    "r": (0.8, [L((0, 1), (0, 0)), A(.45, .55, .45, .45, 180, 85)]),
    "s": (0.9, [J(A(.45, .75, .42, .25, 25, 270), A(.45, .25, .42, .25, 90, -160))]),
    "t": (0.9, [L((.45, 1.75), (.45, 0)), L((0, 1), (.9, 1))]),
    "u": (1.0, [J(L((0, 1), (0, .5)), A(.5, .5, .5, .5, 180, 360)), L((1, 1), (1, 0))]),
    "v": (1.0, [L((0, 1), (.5, 0), (1, 1))]),
    "w": (1.4, [L((0, 1), (.35, 0), (.7, 1), (1.05, 0), (1.4, 1))]),
    "x": (1.0, [L((0, 1), (1, 0)), L((1, 1), (0, 0))]),
    "y": (1.0, [L((0, 1), (.5, 0)), L((1, 1), (.5, 0), (.1, -.8))]),
    "z": (1.0, [L((0, 1), (1, 1), (0, 0), (1, 0))]),
    # ------------------------------------------------ huruf kapital
    "A": (1.4, [L((0, 0), (.7, 2), (1.4, 0)), L((.25, .7), (1.15, .7))]),
    "B": (1.15, [L((0, 2), (0, 0)), J(L((0, 2), (.55, 2)), A(.55, 1.5, .5, .5, 90, -90), L((.55, 1), (0, 1))),
                 J(L((0, 1), (.6, 1)), A(.6, .5, .55, .5, 90, -90), L((.6, 0), (0, 0)))]),
    "C": (1.45, [A(.75, 1, .75, 1, 45, 315)]),
    "D": (1.35, [L((0, 2), (0, 0)), J(L((0, 2), (.5, 2)), A(.5, 1, .85, 1, 90, -90), L((.5, 0), (0, 0)))]),
    "E": (1.0, [L((0, 2), (0, 0)), L((0, 2), (1, 2)), L((0, 1), (.85, 1)), L((0, 0), (1, 0))]),
    "F": (1.0, [L((0, 2), (0, 0)), L((0, 2), (1, 2)), L((0, 1), (.85, 1))]),
    "G": (1.5, [J(A(.75, 1, .75, 1, 45, 360), L((1.5, 1), (.85, 1)))]),
    "H": (1.1, [L((0, 2), (0, 0)), L((1.1, 2), (1.1, 0)), L((0, 1), (1.1, 1))]),
    "I": (0.2, [L((.1, 2), (.1, 0))]),
    "J": (1.0, [J(L((1, 2), (1, .5)), A(.5, .5, .5, .5, 0, -180))]),
    "K": (1.2, [L((0, 2), (0, 0)), L((1.1, 2), (0, .9)), L((.35, 1.25), (1.2, 0))]),
    "L": (1.0, [L((0, 2), (0, 0), (1, 0))]),
    "M": (1.7, [L((0, 0), (0, 2), (.85, .4), (1.7, 2), (1.7, 0))]),
    "N": (1.2, [L((0, 0), (0, 2), (1.2, 0), (1.2, 2))]),
    "O": (1.5, [A(.75, 1, .75, 1, 90, 450)]),
    "P": (1.1, [L((0, 2), (0, 0)), J(L((0, 2), (.5, 2)), A(.5, 1.5, .6, .5, 90, -90), L((.5, 1), (0, 1)))]),
    "Q": (1.6, [A(.75, 1, .75, 1, 90, 450), L((1, .5), (1.6, -.2))]),
    "R": (1.1, [L((0, 2), (0, 0)), J(L((0, 2), (.5, 2)), A(.5, 1.5, .6, .5, 90, -90), L((.5, 1), (0, 1))),
                L((.5, 1), (1.1, 0))]),
    "S": (1.3, [J(A(.7, 1.5, .65, .5, 20, 270), A(.7, .5, .7, .5, 90, -160))]),
    "T": (1.4, [L((0, 2), (1.4, 2)), L((.7, 2), (.7, 0))]),
    "U": (1.2, [J(L((0, 2), (0, .8)), A(.6, .8, .6, .8, 180, 360), L((1.2, .8), (1.2, 2)))]),
    "V": (1.4, [L((0, 2), (.7, 0), (1.4, 2))]),
    "W": (2.0, [L((0, 2), (.5, 0), (1, 1.4), (1.5, 0), (2, 2))]),
    "X": (1.3, [L((0, 2), (1.3, 0)), L((1.3, 2), (0, 0))]),
    "Y": (1.3, [L((0, 2), (.65, 1)), L((1.3, 2), (.65, 1), (.65, 0))]),
    "Z": (1.2, [L((0, 2), (1.2, 2), (0, 0), (1.2, 0))]),
    # ------------------------------------------------ tanda
    "-": (0.7, [L((.05, .9), (.65, .9))]),
    "'": (0.2, [L((.1, 2), (.1, 1.55))]),
    " ": (0.45, []),
}


def text_units(text: str) -> float:
    """Lebar teks dalam satuan garis bantu (kalikan dengan u untuk dapat poin)."""
    ws = [G.get(ch, G[" "])[0] for ch in text]
    return sum(ws) + SPACING * max(0, len(ws) - 1)


def _resample(pts, gap):
    if len(pts) == 1:
        return list(pts)
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = cum[-1]
    n = max(1, round(total / gap))
    out, j = [], 0
    for i in range(n + 1):
        d = total * i / n
        while j < len(cum) - 2 and cum[j + 1] < d:
            j += 1
        seg = (cum[j + 1] - cum[j]) or 1
        t = (d - cum[j]) / seg
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * t, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * t))
    if len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < gap * 0.6:
        out.pop()                                         # lingkaran tertutup: jangan dobel titik akhir
    return out


def trace_word(c, x, y, text, u, color="#7C7C94", max_w=None, gap=0.30, marks="letters"):
    """Gambar kata sebagai garis titik-titik SATU goresan. (x, y) = awal baseline; u = tinggi huruf kecil (pt).
    marks: 'letters' = titik hijau di awal goresan pertama TIAP huruf | 'word' = hanya huruf pertama |
           'all' = awal setiap goresan | None = tanpa penanda.   Mengembalikan u yang dipakai (mengecil bila kata panjang)."""
    if max_w and text_units(text) * u > max_w:
        u = max_w / text_units(text)
    r = max(1.0, 0.085 * u)
    c.saveState()
    pen = x
    for li, ch in enumerate(text):
        width, strokes = G.get(ch, G[" "])
        for si, stroke in enumerate(strokes):
            pts = [(pen + px * u, y + py * u) for px, py in stroke]
            dots = _resample(pts, gap * u)
            mark = len(dots) > 1 and ((marks == "all") or (marks == "letters" and si == 0)
                                      or (marks == "word" and li == 0 and si == 0))
            c.setFillColor(hx(color))
            for dx, dy in (dots[1:] if mark else dots):
                c.circle(dx, dy, r, stroke=0, fill=1)
            if mark:
                c.setFillColor(hx(PALETTE["mint"])); c.setStrokeColor(white); c.setLineWidth(0.6)
                c.circle(dots[0][0], dots[0][1], r * 1.8, stroke=1, fill=1)
        pen += (width + SPACING) * u
    c.restoreState()
    return u


def _mix(hexcolor: str, amount: float) -> str:
    """Campur warna dengan putih (amount 0..1 = seberapa pucat) -> warna utuh tanpa transparansi."""
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    f = lambda v: int(v + (255 - v) * amount)
    return "#%02X%02X%02X" % (f(r), f(g), f(b))


def y_extent(ch):
    """(y_min, y_max) huruf dalam satuan garis bantu (untuk memusatkan huruf contoh secara vertikal)."""
    ys = [py for stroke in G[ch][1] for _, py in stroke]
    return (min(ys), max(ys)) if ys else (0.0, 1.0)


def _point_along(pts, dist):
    """Titik pada jarak dist (pt) dari awal goresan."""
    left = dist
    for a, b in zip(pts, pts[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if seg >= left > 0:
            t = left / seg
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        left -= seg
    return pts[-1]


def draw_model(c, ch, x, y, u, color, numbers=True):
    """Huruf CONTOH: goresan tebal berwarna pucat + nomor urutan goresan (1, 2, 3 ...) di titik mulai.
    Bila beberapa goresan mulai di titik yang sama, nomornya digeser sepanjang goresan agar tidak saling menimpa.
    (x, y) = awal baseline; u = tinggi huruf kecil. Mengembalikan lebar huruf (pt)."""
    width, strokes = G[ch]
    c.saveState()
    c.setStrokeColor(hx(_mix(color, 0.55))); c.setFillColor(hx(_mix(color, 0.55)))
    c.setLineWidth(0.30 * u); c.setLineCap(1); c.setLineJoin(1)
    spts = []
    for stroke in strokes:
        pts = [(x + px * u, y + py * u) for px, py in stroke]
        spts.append(pts)
        if len(pts) == 1:
            c.circle(pts[0][0], pts[0][1], 0.15 * u, stroke=0, fill=1)
            continue
        p = c.beginPath(); p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        c.drawPath(p, stroke=1, fill=0)
    if numbers:
        from .config import FONT_BOLD
        r = max(5.0, 0.27 * u)
        placed = []
        for i, pts in enumerate(spts, 1):
            pos = pts[0]
            if any(math.hypot(pos[0] - q[0], pos[1] - q[1]) < 2.1 * r for q in placed) and len(pts) > 1:
                for d in (1.6 * r, 2.6 * r, 3.6 * r, 4.6 * r):          # geser sepanjang goresan sampai tidak bertumpuk
                    cand = _point_along(pts, d)
                    if all(math.hypot(cand[0] - q[0], cand[1] - q[1]) >= 2.1 * r for q in placed):
                        pos = cand
                        break
                else:
                    pos = cand
            placed.append(pos)
            c.setFillColor(hx(color)); c.setStrokeColor(white); c.setLineWidth(1)
            c.circle(pos[0], pos[1], r, stroke=1, fill=1)
            c.setFillColor(white); c.setFont(FONT_BOLD, r * 1.25)
            c.drawCentredString(pos[0], pos[1] - r * 0.42, str(i))
    c.restoreState()
    return width * u
