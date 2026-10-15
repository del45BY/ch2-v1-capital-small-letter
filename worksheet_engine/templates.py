"""
TEMPLATE v3: "Tracing Words" (Menebalkan Kata).

Satu tata letak, diisi data dari Excel. Setiap TEMA (A..J) = satu halaman berisi 5 kata:
  - kanan : 5 kata (Inggris di atas Indonesia) dalam huruf titik-titik untuk ditebalkan
  - kiri  : 5 gambar (urutannya diacak, tetapi selalu sama untuk tema yang sama)
  - anak  : menebalkan kata, lalu menarik garis dari kata ke gambar yang cocok

Mau mengubah tampilan semua halaman -> ubah draw_tracing_words().
Mau menambah tema -> cukup tambah 5 baris di Excel (kode Template baru, mis. K). Tidak perlu kode.
"""
from reportlab.lib.colors import white
from .art import draw_object
from .components import dot, dotted_text, instruction, panel, text_fit, tracing_line
from .config import (CONTENT_BOTTOM, CONTENT_TOP, CONTENT_W, FONT_BOLD, FONT_REG, MARGIN, PAGE_W, PALETTE, TINT)

ACCENTS = ["coral", "sky", "mint", "grape"]          # bergiliran per tema (kuning dihindari: teks kurang terbaca)

# teks per halaman (boleh memakai {THEME_EN} {THEME_ID} {THEME_EN_LOWER} {THEME_ID_LOWER} {NUM} {KEY})
SPEC = {
    "name_en": "Tracing Words", "name_id": "Menebalkan Kata",
    "title_en": "{NUM} {THEME_EN}",
    "title_id": "{THEME_ID} - Menebalkan Kata",
    "objective_en": "trace and match {THEME_EN_LOWER} words.",
    "objective_id": "menebalkan dan mencocokkan kata tentang {THEME_ID_LOWER}.",
    "instr_en": "Trace the words. Draw a line to the matching picture.",
    "instr_id": "Tebalkan kata-katanya. Tarik garis ke gambar yang cocok.",
}


def accent_for(theme) -> str:
    return ACCENTS[(int(theme.num) - 1) % len(ACCENTS)]


def shuffled_order(n, rng):
    """Urutan gambar yang diacak, tanpa satu pun gambar sejajar dengan katanya sendiri."""
    idx = list(range(n))
    for _ in range(100):
        rng.shuffle(idx)
        if all(i != j for i, j in enumerate(idx)):
            return idx
    return idx[1:] + idx[:1]                             # cadangan: geser satu (selalu tanpa titik tetap)


def draw_tracing_words(c, theme, rng, accent):
    y = instruction(c, theme, CONTENT_TOP, SPEC["instr_en"], SPEC["instr_id"], accent, theme.key)
    words = theme.words
    n = len(words)
    order = shuffled_order(n, rng)

    gap = 6
    avail = (y - 10) - CONTENT_BOTTOM
    rh = min(100, (avail - gap * (n - 1)) / n)
    pic_w = 120
    word_x = MARGIN + pic_w + 92
    word_w = PAGE_W - MARGIN - word_x
    top = y - 10
    for i in range(n):
        yy = top - (i + 1) * rh - i * gap
        # kiri: gambar (diacak)
        pic = words[order[i]]
        panel(c, MARGIN, yy, pic_w, rh, fill=TINT[accent], stroke=PALETTE[accent], lw=2, r=16)
        draw_object(c, pic.en, MARGIN + pic_w / 2, yy + rh / 2, rh - 22, "color")
        # kanan: kata untuk ditebalkan
        w = words[i]
        panel(c, word_x, yy, word_w, rh, fill=white, stroke=PALETTE[accent], lw=2, r=16)
        gx, gw = word_x + 16, word_w - 32
        tracing_line(c, gx, yy + rh * 0.55, gw)
        dotted_text(c, gx + 2, yy + rh * 0.55, w.en, 40, max_w=gw - 6)
        tracing_line(c, gx, yy + rh * 0.13, gw)
        dotted_text(c, gx + 2, yy + rh * 0.13, w.idn, 28, color="#8686A0", max_w=gw - 6)
        # titik penghubung
        dot(c, MARGIN + pic_w, yy + rh / 2, 8)
        dot(c, word_x, yy + rh / 2, 8)
