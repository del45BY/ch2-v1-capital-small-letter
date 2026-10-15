"""Satu tema -> PDF (1 halaman) + Preview + Cover + Thumbnail.   Banyak tema -> paket PDF multi-halaman."""
import hashlib
import json
import random
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from reportlab.lib.colors import white
from reportlab.pdfgen import canvas
from .art import draw_object
from .components import footer, header, panel, star, text_fit
from .config import (ASSETS, BRAND, BRAND_STRIPE, FONT_BOLD, FONT_REG, PAGE_H, PAGE_W, PALETTE,
                     TEMPLATE_VERSION, TINT, hx)
from .database import safe_name
from .templates import SPEC, accent_for, draw_tracing_words

PDF_NAME = "English_Indonesian_Worksheet.pdf"
GROUP = "Tracing_Words"                       # folder induk di dalam PRODUCTS/


# ------------------------------------------------------------------ deteksi perubahan
def _hash(payload) -> str:
    img_state = [(p.name, p.stat().st_mtime) for p in sorted((ASSETS / "images").glob("*.png"))]
    blob = json.dumps([payload, SPEC, TEMPLATE_VERSION, str(img_state), BRAND["name"]], default=str)
    return hashlib.sha1(blob.encode()).hexdigest()


def theme_payload(t):
    return [t.key, t.num, t.en, t.idn, [(w.wid, w.en, w.idn) for w in t.words]]


# ------------------------------------------------------------------ PDF
def write_pdf(themes, out_pdf, title, subject, keywords):
    c = canvas.Canvas(str(out_pdf), pagesize=(PAGE_W, PAGE_H))
    c.setTitle(title); c.setAuthor(BRAND["name"]); c.setSubject(subject); c.setKeywords(keywords)
    total = len(themes)
    for n, t in enumerate(themes, 1):
        accent = accent_for(t)
        rng = random.Random(f"{t.key}-{'-'.join(w.wid for w in t.words)}")   # susunan selalu sama untuk data yang sama
        header(c, t, SPEC, accent, t.fmt(SPEC["title_en"]), t.fmt(SPEC["title_id"]))
        draw_tracing_words(c, t, rng, accent)
        footer(c, n, total, f"Activity {t.key}: {t.num} {t.en} - {SPEC['name_en']} / {t.idn} - {SPEC['name_id']}")
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
def make_cover(title, subtitle, kicker, items, badge_en, badge_id, out_cover, out_thumb, tmp_pdf):
    S = 640
    c = canvas.Canvas(str(tmp_pdf), pagesize=(S, S))
    c.setFillColor(hx(TINT["sun"])); c.rect(0, 0, S, S, stroke=0, fill=1)
    seg = S / len(BRAND_STRIPE)
    for i, nm in enumerate(BRAND_STRIPE):
        c.setFillColor(hx(PALETTE[nm])); c.rect(i * seg, S - 18, seg + 1, 18, stroke=0, fill=1)
    panel(c, 30, 30, S - 60, S - 90, fill=white, stroke=PALETTE["ink"], lw=4, r=34)
    text_fit(c, S / 2, S - 124, title, FONT_BOLD, 52, S - 190, PALETTE["ink"], "center")
    text_fit(c, S / 2, S - 160, subtitle, FONT_BOLD, 30, S - 190, PALETTE["coral"], "center")
    text_fit(c, S / 2, S - 188, kicker, FONT_BOLD, 15, S - 150, PALETTE["grey"], "center")
    items = items[:10]
    per_row = 5 if len(items) > 5 else len(items)
    rows_n = -(-len(items) // per_row)
    size, gap = (92, 12) if rows_n == 1 else (84, 14)        # satu baris -> gambar lebih besar
    y0 = 318 if rows_n == 1 else 372
    for r_ in range(rows_n):
        chunk = items[r_ * per_row:(r_ + 1) * per_row]
        x0 = S / 2 - (len(chunk) * size + (len(chunk) - 1) * gap) / 2
        y = y0 - r_ * (size + gap + 8)
        for i, en in enumerate(chunk):
            x = x0 + i * (size + gap)
            panel(c, x, y - size / 2 - 4, size, size + 8, fill=TINT[["sky", "mint", "coral", "grape", "sun"][(r_ * per_row + i) % 5]], r=18)
            draw_object(c, en, x + size / 2, y, size - 10)
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
def _build(folder, themes, key_payload, meta, cover_args, force):
    folder.mkdir(parents=True, exist_ok=True)
    stamp, pdf = folder / ".build_hash", folder / PDF_NAME
    h = _hash(key_payload)
    if not force and stamp.exists() and stamp.read_text() == h and pdf.exists():
        return {"folder": str(folder), "built": False, "pages": len(themes)}
    write_pdf(themes, pdf, *meta)
    render_preview(pdf, folder / "Preview.png")
    make_cover(*cover_args, folder / "Cover.png", folder / "Thumbnail.png", folder / "_cover.pdf")
    stamp.write_text(h)
    return {"folder": str(folder), "built": True, "pages": len(themes)}


def build_theme(theme, out_root, force=False):
    """PRODUCTS/Tracing_Words/<NN_Tema>/  (PDF 1 halaman, Preview, Cover, Thumbnail)"""
    folder = Path(out_root) / GROUP / theme.folder
    meta = (f"{theme.en} - {SPEC['name_en']} - English / Indonesian Worksheet",
            f"{theme.idn} - {SPEC['name_id']} - Lembar Kerja Dwibahasa",
            f"{theme.en}, tracing words, preschool, bilingual, Indonesian, ages 3-5")
    cover = (theme.en, theme.idn, f"{SPEC['name_en']}  /  {SPEC['name_id']}", [w.en for w in theme.words],
             "1 Printable Worksheet", "1 Lembar Kerja Siap Cetak")
    res = _build(folder, [theme], theme_payload(theme), meta, cover, force)
    return {"key": theme.key, "name": theme.en, **res}


def build_pack(themes, name, out_root, force=False):
    """PRODUCTS/Tracing_Words/<name>/  (PDF dengan satu halaman per tema, Preview, Cover, Thumbnail)"""
    folder = Path(out_root) / GROUP / safe_name(name)
    n_words = sum(len(t.words) for t in themes)
    meta = (f"{name.replace('_', ' ')} - English / Indonesian Worksheet Pack",
            "Paket lembar kerja menebalkan kata dwibahasa",
            "tracing words, preschool, bilingual, Indonesian, ages 3-5")
    cover = (name.replace("_", " "), SPEC["name_id"],
             f"{len(themes)} Themes / {len(themes)} Tema  \u2022  {n_words} Words / {n_words} Kata",
             [t.words[0].en for t in themes],
             f"{len(themes)} Printable Worksheets", f"{len(themes)} Lembar Kerja Siap Cetak")
    res = _build(folder, themes, [theme_payload(t) for t in themes], meta, cover, force)
    return {"key": "PACK", "name": name, **res}
