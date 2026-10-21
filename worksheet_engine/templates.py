"""
TEMPLATE v4: 20 halaman menulis huruf (A-T).  Lima JENIS tata letak; huruf dan judul diatur di sheet Excel "Templates".

  capital  Huruf Besar    1-5 huruf per halaman: huruf contoh bernomor | gambar kata kunci | baris tebalkan lalu tulis sendiri
  small    Huruf Kecil    sama, untuk huruf kecil (garis bantu tiga tingkat, ada huruf turun g j p q y)
  review   Review A-Z     26 huruf berurutan (nomor urutan abjad): baris tebalkan + baris tulis sendiri
  similar  Huruf Mirip    tiap pasangan (b-d, p-q, m-n): kartu pembeda, tebalkan bergantian, lingkari huruf yang disebut
  pairs    Aa-Zz          pasangan huruf besar-kecil, tebalkan keduanya

Gambar kata kunci: PNG buatan Anda (art.py). Belum ada PNG -> kotak teks biasa (demo).
Mau mengubah tampilan satu jenis halaman -> ubah fungsi draw_* jenis itu. Mau mengubah pembagian huruf -> cukup ubah sheet Templates.
"""
from reportlab.lib.colors import white
from .art import draw_picture, image_key
from .components import instruction, panel, text_fit, tracing_line
from .config import (CONTENT_BOTTOM, CONTENT_TOP, CONTENT_W, FONT_BOLD, FONT_REG, LETTER_U, MARGIN,
                     PAGE_W, PALETTE, TINT, hx)
from .strokefont import G, draw_model, trace_word, y_extent

ACCENTS = ["coral", "sky", "mint", "grape"]         # bergiliran per template (kuning dihindari: teks kurang terbaca)

# teks per jenis halaman. Placeholder: {LETTERS} {LETTERS_AND_EN} {LETTERS_AND_ID} {KEY} {TITLE_EN} {TITLE_ID}
TYPE_TEXT = {
    "capital": dict(
        instr_en="Trace each letter. Then write it on your own.", instr_id="Tebalkan setiap huruf. Lalu tulis sendiri.",
        objective_en="trace and write capital letters {LETTERS_AND_EN}.",
        objective_id="menebalkan dan menulis huruf besar {LETTERS_AND_ID}."),
    "small": dict(
        instr_en="Trace each letter. Then write it on your own.", instr_id="Tebalkan setiap huruf. Lalu tulis sendiri.",
        objective_en="trace and write small letters {LETTERS_AND_EN}.",
        objective_id="menebalkan dan menulis huruf kecil {LETTERS_AND_ID}."),
    "review": dict(
        instr_en="Trace the letters in order, from A to Z.", instr_id="Tebalkan huruf secara berurutan, dari A sampai Z.",
        objective_en="say and write the capital letters in alphabet order, A to Z.",
        objective_id="menyebut dan menulis huruf besar berurutan, dari A sampai Z."),
    "similar": dict(
        instr_en="Look closely! Trace each letter, then circle the one named.",
        instr_id="Perhatikan baik-baik! Tebalkan setiap huruf, lalu lingkari yang disebutkan.",
        objective_en="tell similar letters apart: {LETTERS_AND_EN}.",
        objective_id="membedakan huruf yang mirip: {LETTERS_AND_ID}."),
    "pairs": dict(
        instr_en="Trace each capital and small letter pair.", instr_id="Tebalkan setiap pasangan huruf besar dan kecil.",
        objective_en="match capital and small letters, Aa to Zz.",
        objective_id="mencocokkan huruf besar dan kecil, Aa sampai Zz."),
}


def accent_for(t) -> str:
    return ACCENTS[(ord(t.key) - 65) % len(ACCENTS)]


def model_u(ch, avail_h, max_w):
    """Ukuran huruf contoh: sebesar mungkin yang muat (tinggi dan lebar); huruf kecil boleh lebih besar karena aslinya pendek."""
    cap = 40 if ch.islower() else 32
    lo, hi = y_extent(ch)
    return min((avail_h - 22) / max(hi - lo, 1.0), (max_w - 12) / G[ch][0], cap)


def draw_model_centered(c, ch, x0, w_col, cy, u, accent):
    """Gambar huruf contoh di tengah kolom (x0..x0+w_col) dan berpusat vertikal di cy sesuai bentuk hurufnya."""
    lo, hi = y_extent(ch)
    draw_model(c, ch, x0 + (w_col - G[ch][0] * u) / 2, cy - (lo + hi) / 2 * u, u, PALETTE[accent])


def _head(c, t, txt, accent):
    return instruction(c, t, CONTENT_TOP, txt["instr_en"], txt["instr_id"], accent, t.key)


# ================================================================== capital / small
def letter_block(c, x, yb, w, bh, ch, e, accent, rows):
    panel(c, x, yb, w, bh, fill=white, stroke=PALETTE[accent], lw=2.4, r=16)
    # kolom 1: huruf contoh dengan nomor urutan goresan
    u_m = model_u(ch, bh, 70)
    draw_model_centered(c, ch, x + 14, 70, yb + bh / 2, u_m, accent)
    # kolom 2: gambar kata kunci (PNG; belum ada -> kotak teks) + kata Inggris/Indonesia
    pic = min(bh - 44, 84)
    cx2, cy2 = x + 14 + 70 + 8 + 50, yb + bh - 8 - pic / 2
    draw_picture(c, image_key(e.word_en, e.image), e.word_en, cx2, cy2, pic)
    text_fit(c, cx2, cy2 - pic / 2 - 12, e.word_en, FONT_BOLD, 10.5, 96, PALETTE["ink"], "center")
    text_fit(c, cx2, cy2 - pic / 2 - 24, e.word_id, FONT_REG, 9, 96, PALETTE[accent], "center")
    # kolom 3: baris tebalkan (titik-titik satu goresan) lalu baris tulis sendiri
    tx = x + 14 + 70 + 8 + 100 + 8
    tw = x + w - 14 - tx
    rh = (bh - 16) / rows
    u = min(LETTER_U, (rh - 10) / 2.8)
    adv = (G[ch][0] + 1.0) * u
    n_dot = max(3, min(6, int((tw - 8) / adv)))
    for j in range(rows):
        yline = yb + 8 + (rows - 1 - j) * rh + 0.8 * u + 5
        tracing_line(c, tx, yline, tw, mid=u, top=2 * u)
        count = {1: min(3, n_dot)}.get(rows, n_dot if j == 0 else (2 if j == 1 else 0))
        for k in range(count):
            trace_word(c, tx + 10 + k * adv, yline, ch, u, marks="all")


def draw_letter_page(c, t, lib, rng, accent, txt):
    y = _head(c, t, txt, accent)
    n, gap = len(t.letters), 8
    top = y - 8
    bh = min(250, (top - CONTENT_BOTTOM - gap * (n - 1)) / n)
    rows = 3 if bh >= 220 else 2 if bh >= 140 else 1
    for i, ch in enumerate(t.letters):
        letter_block(c, MARGIN, top - (i + 1) * bh - i * gap, CONTENT_W, bh, ch, lib[ch.upper()], accent, rows)


# ================================================================== review A-Z
def draw_review(c, t, lib, rng, accent, txt):
    y = _head(c, t, txt, accent)
    letters = t.letters
    chunks = [letters[i:i + 7] for i in range(0, len(letters), 7)]
    n, gap = len(chunks), 8
    top = y - 8
    bh = min(130, (top - CONTENT_BOTTOM - gap * (n - 1)) / n)
    u = 15
    cell = (CONTENT_W - 24) / 7
    for ri, chunk in enumerate(chunks):
        yb = top - (ri + 1) * bh - ri * gap
        panel(c, MARGIN, yb, CONTENT_W, bh, fill=white, stroke=PALETTE[accent], lw=2.4, r=16)
        y_write = yb + 0.8 * u + 6                        # baris tulis sendiri (kosong)
        y_trace = y_write + 2 * u + 0.8 * u + 10          # baris tebalkan
        tracing_line(c, MARGIN + 12, y_write, CONTENT_W - 24, mid=u, top=2 * u)
        tracing_line(c, MARGIN + 12, y_trace, CONTENT_W - 24, mid=u, top=2 * u)
        for k, ch in enumerate(chunk):
            cx = MARGIN + 12 + cell * (k + 0.5)
            trace_word(c, cx - G[ch][0] * u / 2, y_trace, ch, u, marks="all")
            num = ord(ch) - 64                            # urutan abjad: A=1 ... Z=26
            c.setFillColor(hx(PALETTE[accent])); c.circle(cx, yb + bh - 13, 7.5, stroke=0, fill=1)
            c.setFillColor(white); c.setFont(FONT_BOLD, 8); c.drawCentredString(cx, yb + bh - 15.8, str(num))


# ================================================================== similar letters
def draw_similar(c, t, lib, rng, accent, txt):
    y = _head(c, t, txt, accent)
    n, gap = len(t.letters), 8
    top = y - 8
    sh = min(190, (top - CONTENT_BOTTOM - gap * (n - 1)) / n)
    half = (CONTENT_W - 36) / 2
    zone_a = 72
    for si, (a, b) in enumerate(t.letters):
        yb = top - (si + 1) * sh - si * gap
        panel(c, MARGIN, yb, CONTENT_W, sh, fill=white, stroke=PALETTE[accent], lw=2.4, r=16)
        card_y = yb + sh - 8 - zone_a
        for k, ch in enumerate((a, b)):                   # dua kartu pembeda berdampingan
            cx0 = MARGIN + 12 + k * (half + 12)
            panel(c, cx0, card_y, half, zone_a, fill=TINT[accent], r=10)
            e = lib[ch.upper()]
            u_m = model_u(ch, zone_a, 50)
            draw_model_centered(c, ch, cx0 + 14, 50, card_y + zone_a / 2, u_m, accent)
            pic = 40
            px, py = cx0 + 14 + 50 + 18 + pic / 2, card_y + zone_a - 5 - pic / 2
            draw_picture(c, image_key(e.word_en, e.image), e.word_en, px, py, pic)
            text_fit(c, px, py - pic / 2 - 11, e.word_en, FONT_BOLD, 9.5, half - 100, PALETTE["ink"], "center")
            text_fit(c, px, py - pic / 2 - 21, e.word_id, FONT_REG, 8, half - 100, PALETTE[accent], "center")
        # baris tebalkan bergantian: a b a b a b
        u = 14
        y_trace = yb + 8 + 28 + 4 + 0.8 * u + 3
        tracing_line(c, MARGIN + 12, y_trace, CONTENT_W - 24, mid=u, top=2 * u)
        px = MARGIN + 22
        for k in range(6):
            ch = (a, b)[k % 2]
            trace_word(c, px, y_trace, ch, u, marks="all")
            px += (G[ch][0] + 1.4) * u
        # baris lingkari: huruf pertama pasangan = target
        target = a
        cnt = rng.randint(3, 5)
        seq = [a] * cnt + [b] * (9 - cnt)
        rng.shuffle(seq)
        c.setFont(FONT_BOLD, 10); c.setFillColor(hx(PALETTE[accent]))
        c.drawString(MARGIN + 14, yb + 20, f"Circle the {target}")
        c.setFont(FONT_REG, 9); c.setFillColor(hx(PALETTE["grey"]))
        c.drawString(MARGIN + 14, yb + 8, f"Lingkari huruf {target}")
        c.setFont(FONT_BOLD, 26); c.setFillColor(hx(PALETTE["ink"]))
        for k, ch in enumerate(seq):
            c.drawCentredString(MARGIN + 175 + k * 39, yb + 11, ch)


# ================================================================== pairs Aa-Zz
def draw_pairs(c, t, lib, rng, accent, txt):
    y = _head(c, t, txt, accent)
    letters = t.letters
    cols, gap = 4, 6
    rows = -(-len(letters) // cols)
    top = y - 8
    cw = (CONTENT_W - gap * (cols - 1)) / cols
    rh = min(80, (top - CONTENT_BOTTOM - gap * (rows - 1)) / rows)
    u = min(17, (rh - 10) / 2.8)
    for i, ch in enumerate(letters):
        r_, c_ = divmod(i, cols)
        x, yb = MARGIN + c_ * (cw + gap), top - (r_ + 1) * rh - r_ * gap
        panel(c, x, yb, cw, rh, fill=white, stroke=PALETTE[accent], lw=1.8, r=12)
        yline = yb + 0.8 * u + 6
        tracing_line(c, x + 8, yline, cw - 16, mid=u, top=2 * u)
        px = x + 14
        trace_word(c, px, yline, ch, u, marks="all")
        trace_word(c, px + (G[ch][0] + 1.5) * u, yline, ch.lower(), u, marks="all")


# ================================================================== pemilih jenis
PAGE_FN = {"capital": draw_letter_page, "small": draw_letter_page, "review": draw_review,
           "similar": draw_similar, "pairs": draw_pairs}


def draw_page(c, t, lib, rng, accent):
    PAGE_FN[t.type](c, t, lib, rng, accent, TYPE_TEXT[t.type])
