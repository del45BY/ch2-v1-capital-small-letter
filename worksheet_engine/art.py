"""
Gambar kata kunci (mis. apel untuk huruf A).

Kode ini TIDAK menggambar objek apa pun. Gambar selalu berasal dari file PNG buatan Anda:
    assets/images/<nama>.png     (atau assets/Images/<nama>.png; huruf besar/kecil nama file tidak dipermasalahkan)
    <nama> = kata Inggris huruf kecil, spasi menjadi garis bawah  (Apple -> apple.png, Ice Cream -> ice_cream.png)
             atau nama yang Anda tulis di kolom Image pada sheet Letters.
Jika file PNG belum ada, yang muncul hanya KOTAK TEKS BIASA (nama kata + nama file yang diharapkan), khusus untuk DEMO.
"""
from pathlib import Path
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from .config import ASSETS, FONT_BOLD, FONT_REG, PALETTE, TINT
from .database import slug

IMAGE_DIRS = [ASSETS / "images", ASSETS / "Images"]      # dua penulisan; di Windows/macOS biasanya folder yang sama


def _index() -> dict:
    """{nama_file_huruf_kecil: Path} untuk semua PNG (tidak peka huruf besar/kecil)."""
    out = {}
    for d in IMAGE_DIRS:
        if d.is_dir():
            for p in d.iterdir():
                if p.suffix.lower() == ".png" and not p.stem.endswith("_line"):
                    out.setdefault(p.name.lower(), p)
    return out


def image_key(word_en: str, image: str = "") -> str:
    return slug(image) if image else slug(word_en)


def find_png(key: str):
    return _index().get(f"{slug(key)}.png")


def has_art(key: str) -> bool:
    return find_png(key) is not None


def image_state() -> list:
    """Untuk deteksi perubahan: (nama, waktu ubah) semua PNG."""
    return sorted((n, p.stat().st_mtime) for n, p in _index().items())


def draw_picture(c, key: str, label: str, cx, cy, size):
    """Gambar PNG di kotak size x size berpusat di (cx, cy); bila belum ada -> placeholder TEKS (demo)."""
    png = find_png(key)
    if png:
        c.drawImage(ImageReader(str(png)), cx - size / 2, cy - size / 2, size, size,
                    mask="auto", preserveAspectRatio=True, anchor="c")
        return
    c.saveState()
    c.setFillColor(HexColor(TINT["sun"])); c.setStrokeColor(HexColor(PALETTE["grey"]))
    c.setLineWidth(1.2); c.setDash(4, 3)
    c.roundRect(cx - size / 2, cy - size / 2, size, size, 8, stroke=1, fill=1)
    c.setDash()
    fs = max(7, min(14, size * 0.17))
    from reportlab.pdfbase.pdfmetrics import stringWidth
    while stringWidth(label, FONT_BOLD, fs) > size - 8 and fs > 6:
        fs -= 0.5
    c.setFillColor(HexColor(PALETTE["ink"])); c.setFont(FONT_BOLD, fs)
    c.drawCentredString(cx, cy + 1, label)
    c.setFillColor(HexColor(PALETTE["grey"])); c.setFont(FONT_REG, max(5.5, fs * 0.55))
    c.drawCentredString(cx, cy - fs * 0.9, f"{slug(key)}.png")
    c.restoreState()
