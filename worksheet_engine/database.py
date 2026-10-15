"""
Membaca database Excel.  Model data v3:

  1 TEMA (= 1 template, kode A..J)  berisi  5 KATA.
  Sheet "Database" (satu baris = satu kata):
      ID | Template | Theme_EN | Theme_ID | Word_EN | Word_ID | Image_Prompt
  Contoh:  001 | A | Farm | Peternakan | Cow | Sapi | cute cow
"""
import re
from dataclasses import dataclass, field
import pandas as pd

REQUIRED = ["ID", "Template", "Theme_EN", "Theme_ID", "Word_EN", "Word_ID", "Image_Prompt"]
WORDS_PER_THEME = 5


def safe_name(text: str) -> str:
    """Nama aman untuk folder: 'Weather & Nature' -> 'Weather_and_Nature'."""
    t = text.strip().replace("&", "and")
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    return re.sub(r"[\s-]+", "_", t).strip("_")


def slug(text: str) -> str:
    return safe_name(text).lower()


@dataclass
class Word:
    wid: str
    en: str
    idn: str                 # kata Indonesia
    prompt: str = ""


@dataclass
class Theme:
    key: str                 # kode template: A..J
    num: str                 # nomor urut tema: 01..10
    en: str
    idn: str
    words: list = field(default_factory=list)
    issues: list = field(default_factory=list)   # (level, check, message) dari loader

    @property
    def folder(self) -> str:
        return f"{self.num}_{safe_name(self.en)}"

    def tokens(self) -> dict:
        return {"KEY": self.key, "NUM": self.num, "THEME_EN": self.en, "THEME_ID": self.idn,
                "THEME_EN_LOWER": self.en.lower(), "THEME_ID_LOWER": self.idn.lower()}

    def fmt(self, text: str) -> str:
        """Ganti {THEME_EN} dst. Placeholder tak dikenal -> KeyError (ditangkap QC)."""
        toks = self.tokens()
        return re.sub(r"\{([A-Z_]+)\}", lambda m: toks[m.group(1)], text)


def _norm_header(h: str) -> str:
    return re.sub(r"[\s]+", "_", str(h).strip()).lower()


def load_themes(path) -> list:
    df = pd.read_excel(path, dtype=str, sheet_name="Database").fillna("")
    cols = {_norm_header(c): c for c in df.columns}
    missing = [c for c in REQUIRED if c.lower() not in cols]
    if missing:
        raise ValueError(f"Sheet 'Database' kekurangan kolom: {missing}")
    get = lambda r, name: str(r[cols[name.lower()]]).strip()

    groups, order = {}, []
    for _, r in df.iterrows():
        key = get(r, "Template").upper()
        if not key and not get(r, "Word_EN"):
            continue                                        # baris kosong
        wid = get(r, "ID")
        wid = wid.zfill(3) if wid.isdigit() else wid        # Excel mengubah 001 jadi 1
        if key not in groups:
            groups[key] = {"en": get(r, "Theme_EN"), "idn": get(r, "Theme_ID"), "words": [], "names": set()}
            order.append(key)
        g = groups[key]
        g["names"].add((get(r, "Theme_EN"), get(r, "Theme_ID")))
        g["words"].append(Word(wid, get(r, "Word_EN").title(), get(r, "Word_ID").title(), get(r, "Image_Prompt")))

    themes = []
    for i, key in enumerate(sorted(order), 1):             # urut A, B, C ...
        g = groups[key]
        t = Theme(key=key, num=f"{i:02d}", en=g["en"], idn=g["idn"], words=g["words"])
        if len(g["names"]) > 1:
            t.issues.append(("WARN", "theme-name", f"nama tema tidak konsisten di template {key}: {sorted(g['names'])}"))
        themes.append(t)
    return themes
