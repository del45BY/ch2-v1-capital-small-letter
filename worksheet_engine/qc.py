"""
Pemeriksaan kualitas sebelum membuat produk.  Level: FAIL (tema dilewati) | WARN (dibuat, perlu dicek manusia) | PASS.
Kosakata dan terjemahan diverifikasi terhadap data/approved_vocab.csv (daftar yang Anda setujui sendiri).
"""
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from .art import has_art
from .config import DATA, QC, TRACE_U_EN, TRACE_U_ID
from .strokefont import G as STROKE_GLYPHS, text_units
from .database import WORDS_PER_THEME, slug


@dataclass
class Issue:
    theme: str      # kode template (A..J)
    ref: str        # ID kata (atau '-' bila masalah level tema)
    level: str      # FAIL | WARN
    check: str
    message: str


def load_glossary(path=DATA / "approved_vocab.csv") -> dict:
    g = {}
    if Path(path).exists():
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                g.setdefault(r["EN"].strip().lower(), set()).add(r["ID"].strip().lower())
    return g


def _system_words():
    p = Path("/usr/share/dict/words")
    return {w.strip().lower() for w in p.open(encoding="utf-8", errors="ignore")} if p.exists() else set()


def check_themes(themes, glossary=None) -> list:
    glossary = glossary if glossary is not None else load_glossary()
    sysdict = _system_words()
    issues, seen_ids = [], {}

    for t in themes:
        add = lambda ref, lvl, chk, msg: issues.append(Issue(t.key, ref, lvl, chk, msg))
        for lvl, chk, msg in t.issues:
            add("-", lvl, chk, msg)
        if not re.fullmatch(r"[A-Z]", t.key):
            add("-", "FAIL", "template", f"kode Template '{t.key}' harus satu huruf A-Z")
        if not t.en or not t.idn:
            add("-", "FAIL", "required", "Theme_EN / Theme_ID kosong")
        if len(t.words) != WORDS_PER_THEME:
            add("-", "FAIL", "word-count", f"tema {t.key} berisi {len(t.words)} kata; harus tepat {WORDS_PER_THEME}")
        try:
            t.fmt("{THEME_EN}{THEME_ID}{NUM}")
        except KeyError as e:
            add("-", "FAIL", "placeholder", f"placeholder tidak dikenal {e}")

        seen_words = set()
        for w in t.words:
            for fld, val in [("ID", w.wid), ("Word_EN", w.en), ("Word_ID", w.idn), ("Image_Prompt", w.prompt)]:
                if not val:
                    add(w.wid or "?", "FAIL", "required", f"{fld} kosong")
            if w.wid in seen_ids:
                add(w.wid, "FAIL", "duplicate", f"ID {w.wid} dobel (juga di template {seen_ids[w.wid]})")
            seen_ids[w.wid] = t.key
            if w.en.lower() in seen_words:
                add(w.wid, "FAIL", "duplicate", f"kata '{w.en}' dobel di tema {t.key}")
            seen_words.add(w.en.lower())
            if not w.en or not w.idn:
                continue

            for fld, txt in (("Word_EN", w.en), ("Word_ID", w.idn)):
                bad = sorted({ch for ch in txt if ch not in STROKE_GLYPHS})
                if bad:
                    add(w.wid, "FAIL", "tracing-font",
                        f"{fld} '{txt}' berisi karakter {bad} yang belum ada di font tracing (hanya A-Z, spasi, - dan ')")
            low = w.en.lower()
            if not re.fullmatch(r"[A-Za-z]+(?:[ '-][A-Za-z]+)*", w.en):
                add(w.wid, "FAIL", "spelling", f"Word_EN '{w.en}' berisi karakter tidak valid")
            if len(w.en.split()) > QC["max_words"] or len(w.en) > QC["max_word_len"]:
                add(w.wid, "WARN", "age-level", f"'{w.en}' panjang ({len(w.en)} huruf), cek cocok untuk usia 3-5")
            if low in glossary:
                if w.idn.lower() not in glossary[low]:
                    add(w.wid, "FAIL", "translation",
                        f"'{w.en}' -> '{w.idn}' berbeda dari glosarium: {sorted(glossary[low])}")
            else:
                add(w.wid, "WARN", "vocabulary",
                    f"'{w.en}' belum ada di glosarium - cek usia, ejaan, dan '{w.idn}' secara manual")
                if sysdict and low not in sysdict:
                    add(w.wid, "WARN", "spelling", f"'{w.en}' tidak ada di kamus Inggris")
            # muat di kotak tracing?
            if text_units(w.en) * TRACE_U_EN > 266 or text_units(w.idn) * TRACE_U_ID > 266:
                add(w.wid, "WARN", "layout", f"'{w.en}'/'{w.idn}' terlalu lebar untuk huruf tracing besar")
            if not has_art(w.en):
                add(w.wid, "WARN", "image", f"belum ada gambar '{w.en}': taruh assets/images/{slug(w.en)}.png (dipakai lencana huruf)")
            pl = w.prompt.lower()
            if w.en and w.en.lower() not in pl:
                add(w.wid, "WARN", "image-match", f"Image_Prompt tidak menyebut '{w.en}'")
            for bad in QC["banned_prompt_words"]:
                if bad in pl:
                    add(w.wid, "FAIL", "image-style", f"Image_Prompt memuat kata terlarang '{bad}'")
    return issues


def theme_status(themes, issues) -> dict:
    out = {t.key: "PASS" for t in themes}
    for i in issues:
        if i.level == "FAIL":
            out[i.theme] = "FAIL"
        elif out.get(i.theme) != "FAIL":
            out[i.theme] = "WARN"
    return out


def write_report(issues, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Template", "ID", "Level", "Check", "Message"])
        for i in issues:
            w.writerow([i.theme, i.ref, i.level, i.check, i.message])
