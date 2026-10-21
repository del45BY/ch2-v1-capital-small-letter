"""
Membaca database Excel.  Model data v4 (dua sheet):

  Sheet "Letters"   : satu baris = satu huruf + kata kunci bergambar
        Letter | Word_EN | Word_ID | Image (opsional) | Image_Prompt
        A | Apple | Apel | | cute apple

  Sheet "Templates" : satu baris = satu halaman/template (A..T)
        Key | Type | Letters | Title_EN | Title_ID
        A | capital | A-C | Capital Letters A-C | Huruf Besar A-C

  Type: capital (huruf besar) | small (huruf kecil) | review (A-Z berurutan) | similar (huruf mirip) | pairs (Aa-Zz)
  Letters: daftar dipisah koma, rentang boleh ("A-C", "a-c", "A-Z"); untuk type similar pakai "b+d, p+q, m+n".
"""
import re
from dataclasses import dataclass, field
import pandas as pd

TYPES = ("capital", "small", "review", "similar", "pairs")
PICTURE_TYPES = ("capital", "small", "similar")      # jenis halaman yang menampilkan gambar kata kunci


def safe_name(text: str) -> str:
    """Nama aman untuk folder: 'Capital Letters A-C' -> 'Capital_Letters_A-C'."""
    t = text.strip().replace("&", "and").replace("\u2013", "-").replace("\u2014", "-")
    t = re.sub(r"[^\w\s-]", "", t, flags=re.UNICODE)
    return re.sub(r"\s+", "_", t).strip("_")


def slug(text: str) -> str:
    """Nama file gambar: 'Ice Cream' -> 'ice_cream', 'Yo-Yo' -> 'yo_yo'."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


@dataclass
class Letter:
    ch: str                  # huruf besar: A..Z
    word_en: str
    word_id: str
    image: str = ""
    prompt: str = ""


@dataclass
class Template:
    key: str
    type: str
    spec: str
    title_en: str
    title_id: str
    letters: list = field(default_factory=list)      # list huruf; untuk type similar: list tuple pasangan
    issues: list = field(default_factory=list)       # (level, check, message) dari loader

    @property
    def folder(self) -> str:
        return f"{self.key}_{safe_name(self.title_en)}"

    def used_letters(self) -> list:
        """Huruf (besar) yang butuh baris di sheet Letters."""
        flat = [x for g in self.letters for x in (g if isinstance(g, tuple) else (g,))]
        seen, out = set(), []
        for x in flat:
            if x.upper() not in seen:
                seen.add(x.upper()); out.append(x.upper())
        return out

    def picture_letters(self) -> list:
        """Huruf yang butuh kata kunci + gambar (baris di sheet Letters). Halaman review/pairs tidak memakai gambar."""
        return self.used_letters() if self.type in PICTURE_TYPES else []

    def _items(self) -> list:
        return [f"{g[0]}\u2013{g[1]}" if isinstance(g, tuple) else g for g in self.letters]

    def _join(self, last: str) -> str:
        """EN: 'A, B and C'   ID: 'A, B, dan C'   (dua huruf: 'A and B' / 'A dan B')."""
        it = self._items()
        if len(it) <= 2:
            return f" {last} ".join(it)
        return ", ".join(it[:-1]) + (", " if last == "dan" else " ") + f"{last} " + it[-1]

    def tokens(self) -> dict:
        return {"KEY": self.key, "TITLE_EN": self.title_en, "TITLE_ID": self.title_id,
                "LETTERS": ", ".join(self._items()),
                "LETTERS_AND_EN": self._join("and"), "LETTERS_AND_ID": self._join("dan")}

    def fmt(self, text: str) -> str:
        toks = self.tokens()
        return re.sub(r"\{([A-Z_]+)\}", lambda m: toks[m.group(1)], text)


def parse_letters(type_: str, spec: str):
    """-> (letters, issues). Menerjemahkan 'A-C, F' atau 'b+d, p+q' menjadi daftar."""
    issues, out = [], []
    for tok in [t.strip() for t in spec.split(",") if t.strip()]:
        if type_ == "similar":
            m = re.fullmatch(r"([A-Za-z])\s*\+\s*([A-Za-z])", tok)
            if not m:
                issues.append(("FAIL", "letters", f"type similar butuh pasangan 'b+d', bukan '{tok}'")); continue
            out.append((m.group(1).lower(), m.group(2).lower()))
            continue
        m = re.fullmatch(r"([A-Za-z])\s*-\s*([A-Za-z])", tok)
        if m:
            a, b = ord(m.group(1).upper()), ord(m.group(2).upper())
            if a > b:
                issues.append(("FAIL", "letters", f"rentang terbalik '{tok}'")); continue
            out += [chr(x) for x in range(a, b + 1)]
        elif re.fullmatch(r"[A-Za-z]", tok):
            out.append(tok)
        else:
            issues.append(("FAIL", "letters", f"'{tok}' bukan huruf atau rentang huruf"))
    if type_ in ("capital", "review", "pairs"):
        out = [x.upper() for x in out]
    elif type_ == "small":
        out = [x.lower() for x in out]
    return out, issues


def _norm(h) -> str:
    return re.sub(r"\s+", "_", str(h).strip()).lower()


def _need(df, cols, sheet, required):
    have = {_norm(c): c for c in df.columns}
    missing = [r for r in required if r.lower() not in have]
    if missing:
        raise ValueError(f"Sheet '{sheet}' kekurangan kolom: {missing}")
    return have


def load_library(path):
    """-> (letters: {'A': Letter}, templates: [Template] urut Key)"""
    dl = pd.read_excel(path, dtype=str, sheet_name="Letters").fillna("")
    cl = _need(dl, None, "Letters", ["Letter", "Word_EN", "Word_ID", "Image_Prompt"])
    get = lambda r, cols, n: str(r[cols[n.lower()]]).strip() if n.lower() in cols else ""
    letters = {}
    for _, r in dl.iterrows():
        ch = get(r, cl, "Letter").upper()
        if not ch:
            continue
        letters[ch] = Letter(ch, get(r, cl, "Word_EN").title(), get(r, cl, "Word_ID").title(),
                             get(r, cl, "Image"), get(r, cl, "Image_Prompt"))
    dt = pd.read_excel(path, dtype=str, sheet_name="Templates").fillna("")
    ct = _need(dt, None, "Templates", ["Key", "Type", "Letters", "Title_EN", "Title_ID"])
    templates = []
    for _, r in dt.iterrows():
        key = get(r, ct, "Key").upper()
        if not key:
            continue
        typ = get(r, ct, "Type").lower()
        spec = get(r, ct, "Letters")
        t = Template(key, typ, spec, get(r, ct, "Title_EN"), get(r, ct, "Title_ID"))
        if typ in TYPES:
            t.letters, t.issues = parse_letters(typ, spec)
        templates.append(t)
    templates.sort(key=lambda t: t.key)
    return letters, templates
