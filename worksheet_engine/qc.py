"""
Pemeriksaan kualitas sebelum membuat produk.   Level: FAIL (template dilewati) | WARN (dibuat, perlu dicek manusia) | INFO (catatan saja).
Kata kunci dan terjemahannya diverifikasi terhadap data/approved_vocab.csv (daftar yang Anda setujui sendiri).
"""
import csv
import re
from dataclasses import dataclass
from pathlib import Path
from .art import has_art, image_key
from .config import DATA, QC, REQUIRE_IMAGES
from .database import TYPES

LIMITS = {"capital": (1, 5), "small": (1, 5), "similar": (1, 4), "review": (1, 26), "pairs": (1, 26)}


@dataclass
class Issue:
    scope: str      # "T:A" (template) atau "L:A" (huruf/kata kunci)
    ref: str
    level: str      # FAIL | WARN | INFO
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


def check_library(letters, templates, glossary=None) -> list:
    glossary = glossary if glossary is not None else load_glossary()
    sysdict = _system_words()
    issues = []

    # ---------------- template
    seen_keys = {}
    for t in templates:
        add = lambda lvl, chk, msg: issues.append(Issue(f"T:{t.key}", t.key, lvl, chk, msg))
        for lvl, chk, msg in t.issues:
            add(lvl, chk, msg)
        if not re.fullmatch(r"[A-Z]", t.key):
            add("FAIL", "key", f"Key '{t.key}' harus satu huruf A-Z")
        if t.key in seen_keys:
            add("FAIL", "duplicate", f"Key {t.key} dobel")
        seen_keys[t.key] = True
        if t.type not in TYPES:
            add("FAIL", "type", f"Type '{t.type}' tidak dikenal; pilih: {', '.join(TYPES)}")
            continue
        if not t.title_en or not t.title_id:
            add("FAIL", "required", "Title_EN / Title_ID kosong")
        lo, hi = LIMITS[t.type]
        if not (lo <= len(t.letters) <= hi) and not any(i[0] == "FAIL" for i in t.issues):
            add("FAIL", "letter-count", f"type {t.type} butuh {lo}-{hi} huruf/pasangan, ditemukan {len(t.letters)}")
        for ch in t.picture_letters():
            if ch not in letters:
                add("FAIL", "letters-missing", f"huruf {ch} belum ada di sheet Letters")
        try:
            t.fmt("{LETTERS}{LETTERS_AND_EN}{LETTERS_AND_ID}{KEY}")
        except KeyError as e:
            add("FAIL", "placeholder", f"placeholder tidak dikenal {e}")

    # ---------------- kata kunci (hanya huruf yang dipakai template)
    used = sorted({ch for t in templates if t.type in TYPES for ch in t.picture_letters() if ch in letters})
    seen_words = {}
    for ch in used:
        e = letters[ch]
        add = lambda lvl, chk, msg, ch=ch: issues.append(Issue(f"L:{ch}", ch, lvl, chk, msg))
        for fld, val in [("Word_EN", e.word_en), ("Word_ID", e.word_id), ("Image_Prompt", e.prompt)]:
            if not val:
                add("FAIL", "required", f"{fld} kosong untuk huruf {ch}")
        if not e.word_en or not e.word_id:
            continue
        if e.word_en.lower() in seen_words:
            add("WARN", "duplicate", f"kata '{e.word_en}' juga dipakai huruf {seen_words[e.word_en.lower()]}")
        seen_words[e.word_en.lower()] = ch
        if not re.fullmatch(r"[A-Za-z]+(?:[ '-][A-Za-z]+)*", e.word_en):
            add("FAIL", "spelling", f"Word_EN '{e.word_en}' berisi karakter tidak valid")
        if e.word_en[:1].upper() != ch:
            add("WARN", "initial", f"kata '{e.word_en}' tidak diawali huruf {ch}")
        if len(e.word_en.split()) > QC["max_words"] or len(e.word_en) > QC["max_word_len"]:
            add("WARN", "age-level", f"'{e.word_en}' panjang, cek cocok untuk usia 3-5")
        low = e.word_en.lower()
        if low in glossary:
            if e.word_id.lower() not in glossary[low]:
                add("FAIL", "translation", f"'{e.word_en}' -> '{e.word_id}' berbeda dari glosarium: {sorted(glossary[low])}")
        else:
            add("WARN", "vocabulary", f"'{e.word_en}' belum ada di glosarium - cek usia, ejaan, dan '{e.word_id}' secara manual")
            if sysdict and low not in sysdict:
                add("WARN", "spelling", f"'{e.word_en}' tidak ada di kamus Inggris")
        key = image_key(e.word_en, e.image)
        if not has_art(key):
            add("WARN" if REQUIRE_IMAGES else "INFO", "image",
                f"belum ada gambar: taruh assets/images/{key}.png (sementara dipakai kotak teks)")
        pl = e.prompt.lower()
        if e.word_en and e.word_en.lower() not in pl:
            add("WARN", "image-match", f"Image_Prompt tidak menyebut '{e.word_en}'")
        for bad in QC["banned_prompt_words"]:
            if bad in pl:
                add("FAIL", "image-style", f"Image_Prompt memuat kata terlarang '{bad}'")
    return issues


def template_status(templates, issues) -> dict:
    """Status per template: FAIL/WARN dari masalah template itu sendiri + masalah huruf yang dipakainya. INFO tidak dihitung."""
    out = {}
    for t in templates:
        refs = {f"T:{t.key}"} | {f"L:{ch}" for ch in t.picture_letters()}
        lv = {i.level for i in issues if i.scope in refs}
        out[t.key] = "FAIL" if "FAIL" in lv else "WARN" if "WARN" in lv else "PASS"
    return out


def write_report(issues, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Scope", "Ref", "Level", "Check", "Message"])
        for i in issues:
            w.writerow([i.scope, i.ref, i.level, i.check, i.message])
