"""Satu template -> PDF (1 halaman) + Preview + Cover + Thumbnail.   Semua template -> paket PDF multi-halaman."""
import hashlib
import json
import random
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from reportlab.lib.colors import white
from reportlab.pdfgen import canvas
from .art import find_png, image_key
from .components import footer, header, panel, star, text_fit
from .config import (BRAND, BRAND_STRIPE, FONT_BOLD, FONT_REG, PAGE_H, PAGE_W, PALETTE, TEMPLATE_VERSION, TINT, hx)
from .database import safe_name
from .templates import TYPE_TEXT, accent_for, draw_page

PDF_NAME = "English_Indonesian_Worksheet.pdf"
GROUP = "Alphabet_Tracing"                     # folder induk di dalam PRODUCTS/


# ------------------------------------------------------------------ deteksi perubahan
def _png_stamp(e):
    """(nama file, waktu ubah) PNG milik satu kata kunci, atau None bila belum ada."""
    p = find_png(image_key(e.word_en, e.image))
    return (p.name, p.stat().st_mtime) if p else None


def _payload(t, lib):
    """Semua yang memengaruhi tampilan SATU template. PNG hanya dihitung untuk huruf yang ditampilkannya,
    jadi menambah gambar apel hanya membangun ulang halaman yang memakai apel."""
    pics = [(ch, lib[ch].word_en, lib[ch].word_id, lib[ch].image, _png_stamp(lib[ch]))
            for ch in t.picture_letters() if ch in lib]
    return [t.key, t.type, t.spec, t.title_en, t.title_id, pics]


def _hash(payload) -> str:
    blob = json.dumps([payload, TYPE_TEXT, TEMPLATE_VERSION, BRAND["name"]], default=str)
    return hashlib.sha1(blob.encode()).hexdigest()


# ------------------------------------------------------------------ PDF
def write_pdf(templates, lib, out_pdf, title, subject, keywords):
    c = canvas.Canvas(str(out_pdf), pagesize=(PAGE_W, PAGE_H))
    c.setTitle(title); c.setAuthor(BRAND["name"]); c.setSubject(subject); c.setKeywords(keywords)
    total = len(templates)
    for n, t in enumerate(templates, 1):
        accent = accent_for(t)
        rng = random.Random(f"{t.key}-{t.type}-{t.spec}")          # susunan acak selalu sama untuk data yang sama
        header(c, t, TYPE_TEXT[t.type], accent, t.title_en, t.title_id)
        draw_page(c, t, lib, rng, accent)
        footer(c, n, total, f"Activity {t.key}: {t.title_en}")
        c.showPage()
    c.save()


def pdf_to_images(pdf_path, scale):
    pdf = pdfium.PdfDocument(str(pdf_path))
    return [pdf[i].render(scale=scale).to_pil().convert("RGB") for i in range(len(pdf))]


def render_preview(pdf_path, out_png):
    many = len(pdfium.PdfDocument(str(pdf_path))) > 6
    pages = pdf_to_images(pdf_path, 0.62 if many else 0.9)
    cols = 5 if many else (3 if len(pages) > 2 else len(pages))
    rows_n = -(-len(pages) // cols)
    pw, ph = pages[0].size
    gap = 36
    sheet = Image.new("RGB", (cols * pw + (cols + 1) * gap, rows_n * ph + (rows_n + 1) * gap), "#F1EFFA")
    d = ImageDraw.Draw(sheet)
    for i, pg in enumerate(pages):
        x, y = gap + (i % cols) * (pw + gap), gap + (i // cols) * (ph + gap)
        d.rectangle([x + 8, y + 8, x + pw + 8, y + ph + 8], fill="#D9D5EA")
        sheet.paste(pg, (x, y))
    sheet.save(out_png, optimize=True)


# ------------------------------------------------------------------ cover persegi 2000 px + thumbnail 600 px
def tiles_for(t):
    """Teks untuk kotak-kotak di sampul (huruf biasa; tidak memakai gambar)."""
    if t.type in ("capital", "small"):
        return list(t.letters)
    if t.type == "similar":
        return [x for pair in t.letters for x in pair]
    if t.type == "pairs":
        return [f"{x}{x.lower()}" for x in t.letters[:5]]
    return list(t.letters[:3]) + ["\u2026", t.letters[-1]]           # review: A B C ... Z


def make_cover(title, subtitle, kicker, tiles, badge_en, badge_id, out_cover, out_thumb, tmp_pdf):
    S = 640
    c = canvas.Canvas(str(tmp_pdf), pagesize=(S, S))
    c.setFillColor(hx(TINT["sun"])); c.rect(0, 0, S, S, stroke=0, fill=1)
    seg = S / len(BRAND_STRIPE)
    for i, nm in enumerate(BRAND_STRIPE):
        c.setFillColor(hx(PALETTE[nm])); c.rect(i * seg, S - 18, seg + 1, 18, stroke=0, fill=1)
    panel(c, 30, 30, S - 60, S - 90, fill=white, stroke=PALETTE["ink"], lw=4, r=34)
    text_fit(c, S / 2, S - 118, title, FONT_BOLD, 46, S - 190, PALETTE["ink"], "center", min_size=20)
    text_fit(c, S / 2, S - 154, subtitle, FONT_BOLD, 26, S - 190, PALETTE["coral"], "center", min_size=14)
    text_fit(c, S / 2, S - 182, kicker, FONT_BOLD, 15, S - 150, PALETTE["grey"], "center")
    n = len(tiles)
    per_row = n if n <= 5 else (3 if n == 6 else 5)
    rows_n = -(-n // per_row)
    size, gap = (96, 12) if rows_n == 1 else (84, 14)
    y0 = 318 if rows_n == 1 else 372
    for r_ in range(rows_n):
        chunk = tiles[r_ * per_row:(r_ + 1) * per_row]
        x0 = S / 2 - (len(chunk) * size + (len(chunk) - 1) * gap) / 2
        y = y0 - r_ * (size + gap + 8)
        for i, txt in enumerate(chunk):
            x = x0 + i * (size + gap)
            panel(c, x, y - size / 2 - 4, size, size + 8, fill=TINT[["sky", "mint", "coral", "grape", "sun"][(r_ * per_row + i) % 5]], r=18)
            fs = 54 if len(txt) == 1 else 42
            c.setFillColor(hx(PALETTE["ink"])); c.setFont(FONT_BOLD, fs)
            c.drawCentredString(x + size / 2, y - fs * 0.32, txt)
    panel(c, 110, 120, S - 220, 58, fill=PALETTE["coral"], r=29)
    c.setFillColor(white); c.setFont(FONT_BOLD, 22); c.drawCentredString(S / 2, 156, badge_en)
    c.setFont(FONT_REG, 14); c.drawCentredString(S / 2, 133, badge_id)
    c.setFillColor(hx(PALETTE["grey"])); c.setFont(FONT_BOLD, 15)
    c.drawCentredString(S / 2, 92, "English \u2022 Bahasa Indonesia   |   Ages 3-5 \u2022 Usia 3-5")
    c.setFont(FONT_REG, 11); c.drawCentredString(S / 2, 62, BRAND["name"])
    star(c, 64, S - 78, 20, PALETTE["sun"]); star(c, S - 64, S - 78, 20, PALETTE["sun"])
    c.save()
    img = pdf_to_images(tmp_pdf, 2000 / S)[0]
    img.save(out_cover, optimize=True)
    img.resize((600, 600), Image.LANCZOS).save(out_thumb, optimize=True)
    Path(tmp_pdf).unlink(missing_ok=True)


# ------------------------------------------------------------------ produk
def _build(folder, templates, lib, payload, meta, cover_args, force):
    folder.mkdir(parents=True, exist_ok=True)
    stamp, pdf = folder / ".build_hash", folder / PDF_NAME
    h = _hash(payload)
    if not force and stamp.exists() and stamp.read_text() == h and pdf.exists():
        return {"folder": str(folder), "built": False, "pages": len(templates)}
    write_pdf(templates, lib, pdf, *meta)
    render_preview(pdf, folder / "Preview.png")
    make_cover(*cover_args, folder / "Cover.png", folder / "Thumbnail.png", folder / "_cover.pdf")
    stamp.write_text(h)
    return {"folder": str(folder), "built": True, "pages": len(templates)}


def build_template(t, lib, out_root, force=False):
    """PRODUCTS/Alphabet_Tracing/<Key_Judul>/  (PDF 1 halaman, Preview, Cover, Thumbnail)"""
    folder = Path(out_root) / GROUP / t.folder
    meta = (f"{t.title_en} - English / Indonesian Worksheet", f"{t.title_id} - Lembar Kerja Dwibahasa",
            "alphabet, letter tracing, preschool, bilingual, Indonesian, ages 3-5")
    cover = (t.title_en, t.title_id, "Alphabet Tracing  /  Menebalkan Huruf", tiles_for(t),
             "1 Printable Worksheet", "1 Lembar Kerja Siap Cetak")
    res = _build(folder, [t], lib, _payload(t, lib), meta, cover, force)
    return {"key": t.key, "name": t.title_en, **res}


def build_pack(templates, lib, name, out_root, force=False):
    """PRODUCTS/Alphabet_Tracing/<name>/  (satu halaman per template, Preview, Cover, Thumbnail)"""
    folder = Path(out_root) / GROUP / safe_name(name)
    n = len(templates)
    meta = (f"{name.replace('_', ' ')} - English / Indonesian Worksheet Pack", "Paket lembar kerja menebalkan huruf dwibahasa",
            "alphabet, letter tracing, preschool, bilingual, Indonesian, ages 3-5")
    cover = (name.replace("_", " "), "Paket Menebalkan Huruf A-Z", f"{n} Worksheets / {n} Lembar  \u2022  Capital & Small Letters",
             [f"{x}{x.lower()}" for x in "ABCDEFGHIJ"], f"{n} Printable Worksheets", f"{n} Lembar Kerja Siap Cetak")
    res = _build(folder, templates, lib, [_payload(t, lib) for t in templates], meta, cover, force)
    return {"key": "PACK", "name": name, **res}
