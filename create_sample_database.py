"""Membuat data/worksheet_database.xlsx berisi 10 tema x 5 kata (contoh).  JANGAN dijalankan lagi setelah database Anda terisi: file akan ditimpa."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HEAD = ["ID", "Template", "Theme_EN", "Theme_ID", "Word_EN", "Word_ID", "Image_Prompt"]
THEMES = [
    ("A", "Farm", "Peternakan", [("Cow", "Sapi"), ("Chicken", "Ayam"), ("Duck", "Bebek"), ("Sheep", "Domba"), ("Horse", "Kuda")]),
    ("B", "Sea Animals", "Hewan Laut", [("Fish", "Ikan"), ("Whale", "Paus"), ("Crab", "Kepiting"), ("Octopus", "Gurita"), ("Turtle", "Penyu")]),
    ("C", "Fruits", "Buah-buahan", [("Apple", "Apel"), ("Banana", "Pisang"), ("Orange", "Jeruk"), ("Pineapple", "Nanas"), ("Grape", "Anggur")]),
    ("D", "Vegetables", "Sayuran", [("Carrot", "Wortel"), ("Spinach", "Bayam"), ("Tomato", "Tomat"), ("Corn", "Jagung"), ("Potato", "Kentang")]),
    ("E", "Vehicles", "Kendaraan", [("Car", "Mobil"), ("Bus", "Bus"), ("Train", "Kereta"), ("Ship", "Kapal"), ("Airplane", "Pesawat")]),
    ("F", "Body Parts", "Anggota Tubuh", [("Eye", "Mata"), ("Nose", "Hidung"), ("Ear", "Telinga"), ("Mouth", "Mulut"), ("Hand", "Tangan")]),
    ("G", "Family & Home", "Keluarga & Rumah", [("Father", "Ayah"), ("Mother", "Ibu"), ("Sibling", "Kakak"), ("Room", "Kamar"), ("Door", "Pintu")]),
    ("H", "School Things", "Perlengkapan Sekolah", [("Book", "Buku"), ("Pencil", "Pensil"), ("Bag", "Tas"), ("Eraser", "Penghapus"), ("Table", "Meja")]),
    ("I", "Weather & Nature", "Cuaca & Alam", [("Rain", "Hujan"), ("Cloud", "Awan"), ("Moon", "Bulan"), ("Star", "Bintang"), ("Tree", "Pohon")]),
    ("J", "Food & Drink", "Makanan & Minuman", [("Rice", "Nasi"), ("Bread", "Roti"), ("Milk", "Susu"), ("Water", "Air"), ("Egg", "Telur")]),
]

wb = Workbook(); ws = wb.active; ws.title = "Database"
ws.append(HEAD)
n = 0
for key, ten, tid, words in THEMES:
    for en, idn in words:
        n += 1
        ws.append([f"{n:03d}", key, ten, tid, en, idn, f"cute {en.lower()}"])
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="4FB3E8")
for col, w in zip("ABCDEFG", [8, 10, 20, 24, 14, 14, 30]):
    ws.column_dimensions[col].width = w
for r in range(2, 2000):
    ws.cell(r, 1).number_format = "@"                 # jaga 001 tetap teks
ws.freeze_panes = "A2"
dv = DataValidation(type="textLength", operator="lessThanOrEqual", formula1="14", showErrorMessage=True,
                    error="Kata maksimal 14 huruf agar muat besar untuk usia 3-5")
ws.add_data_validation(dv); dv.add("E2:F2000")
dv2 = DataValidation(type="list", formula1='"A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z"', showErrorMessage=True,
                     error="Template = satu huruf A-Z")
ws.add_data_validation(dv2); dv2.add("B2:B2000")

rd = wb.create_sheet("README")
for line in [
    "SATU TEMA = SATU TEMPLATE (huruf A-Z) = TEPAT 5 KATA (5 baris dengan kode Template yang sama).",
    "Kolom: ID (unik, teks, mis. 001) | Template (A-Z) | Theme_EN | Theme_ID | Word_EN | Word_ID | Image_Prompt.",
    "Theme_EN dan Theme_ID harus sama di kelima baris satu tema. Nomor tema (01, 02, ...) otomatis dari urutan huruf.",
    "Word_EN/Word_ID harus ada di data/approved_vocab.csv (terjemahan terverifikasi), kalau tidak QC memberi peringatan/gagal.",
    "Image_Prompt harus menyebut Word_EN. Gambar: assets/images/<kata_inggris_huruf_kecil>.png (opsional jika sudah ada gambar bawaan).",
    "Menambah tema baru: tambah 5 baris dengan huruf Template baru (mis. K). Tidak perlu mengubah kode.",
]:
    rd.append([line])
rd.column_dimensions["A"].width = 130
wb.save("data/worksheet_database.xlsx"); print("tersimpan: data/worksheet_database.xlsx", n, "kata")
