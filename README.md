# Mesin Lembar Kerja "Alphabet Tracing" Dwibahasa (Inggris-Indonesia), usia 3-5 tahun

Isi tabel Excel -> skrip membuat lembar kerja menulis huruf siap cetak (PDF), pratinjau, sampul, dan thumbnail.
Anak **menebalkan huruf (satu garis titik-titik di tengah goresan)**, lalu menulis sendiri. Ada 20 template (A-T).

```
pip install -r requirements.txt
python create_sample_database.py          # sekali saja: membuat data/worksheet_database.xlsx (26 huruf, 20 template)
python -m worksheet_engine.main --db data/worksheet_database.xlsx --out PRODUCTS
```
Panduan lengkap, Do & Don't, cara memasang PNG: **PANDUAN.md**

## 20 template

| Key | Isi | Jenis |
|---|---|---|
| A-I | Huruf Besar A-C, D-F, G-I, J-L, M-O, P-R, S-U, V-X, Y-Z | capital |
| J | Review Huruf Besar A-Z & Urutan Abjad | review |
| K-R | Huruf Kecil a-c, d-f, g-i, j-l, m-o, p-r, s-u, v-z | small |
| S | Membedakan Huruf Mirip (b-d, p-q, m-n) | similar |
| T | Pasangan Huruf Besar-Kecil (Aa-Zz) | pairs |

Pembagian huruf dan judul diatur di sheet Excel **Templates**, bukan di kode. Mengubah "A-C" menjadi "A-D" cukup mengganti sel.

### Isi tiap jenis halaman (A4 portrait)
* **capital / small**: per huruf satu blok: huruf contoh dengan **nomor urutan goresan** | gambar kata kunci (PNG) + kata Inggris/Indonesia |
  baris tebalkan (titik-titik, dengan titik hijau penanda awal) lalu baris menulis sendiri. 1-5 huruf per halaman (jumlah baris latihan menyesuaikan).
* **review**: 26 huruf besar berurutan bernomor (urutan abjad), tiap baris: tebalkan + tulis sendiri.
* **similar**: tiap pasangan: dua kartu pembeda (huruf contoh + gambar), baris tebalkan bergantian (b d b d ...), dan baris "lingkari huruf b".
* **pairs**: 26 kotak Aa-Zz, tiap kotak huruf besar dan kecil untuk ditebalkan, ada ruang menulis.

## Gambar kata kunci: SATU-SATUNYA sumber adalah PNG Anda
Kode **tidak menggambar objek apa pun**. Taruh PNG di `assets/images/` (atau `assets/Images/`), nama file tidak peka huruf besar/kecil:
`Apple -> apple.png`, `Ice Cream -> ice_cream.png`, `Yo-Yo -> yo_yo.png` (atau nama lain lewat kolom Image di sheet Letters).
**Selama PNG belum ada**, halaman memakai kotak teks biasa (nama kata + nama file yang diharapkan), khusus untuk DEMO.
`--export-prompts` menulis `image_prompts.csv`: daftar nama file PNG yang dibutuhkan beserta prompt untuk membuatnya.
Setelah semua PNG terpasang, ubah `REQUIRE_IMAGES = True` di `config.py` agar PNG yang hilang terdeteksi sebagai peringatan.

## Data Excel
**Sheet Letters** (satu baris = satu huruf + kata kunci): `Letter | Word_EN | Word_ID | Image (opsional) | Image_Prompt`
**Sheet Templates** (satu baris = satu halaman): `Key | Type | Letters | Title_EN | Title_ID`
Type: `capital`, `small`, `review`, `similar`, `pairs`. Letters: `A-C`, `A-C, F`, `A-Z`; untuk similar: `b+d, p+q, m+n`.
Kata di sheet Letters hanya perlu ada untuk huruf yang dipakai template bergambar (capital, small, similar); review dan pairs tidak butuh.

## Alur kerja
```
Excel --load_library--> QC (qc.py) --FAIL: dilewati / WARN: dibuat, perlu dicek / INFO: catatan-->
   per template: PDF 1 halaman + Preview + Cover + Thumbnail  -> PRODUCTS/Alphabet_Tracing/<Key_Judul>/
   semua yang lolos: PDF paket (1 halaman per template)       -> PRODUCTS/Alphabet_Tracing/Alphabet_Tracing_Complete_Pack/
   qc_report.csv, manifest.csv, (image_prompts.csv)
```
Dijalankan ulang hanya membangun template yang berubah (sidik jari: pengaturan template + kata kunci + PNG yang dipakainya + versi template).
Menambah satu PNG hanya membangun ulang halaman yang memakai gambar itu (dan paket).

## Pemeriksaan kualitas (qc.py)
| Pemeriksaan | Hasil |
|---|---|
| Key bukan A-Z / dobel, Type tidak dikenal, judul kosong, huruf tidak valid, jumlah huruf di luar batas | FAIL |
| Huruf yang dipakai belum ada di sheet Letters; kolom kata kunci kosong | FAIL |
| Terjemahan berbeda dari glosarium (data/approved_vocab.csv) | **FAIL** |
| Kata belum ada di glosarium; kata tidak diawali huruf yang bersangkutan; Image_Prompt tidak menyebut kata | WARN |
| Image_Prompt memuat kata terlarang (realistic, scary, photo ...) | FAIL |
| PNG belum ada | INFO (WARN jika `REQUIRE_IMAGES = True`) |

Pemeriksaan terjemahan hanya sebaik glosarium Anda: kata di luar glosarium tidak pernah dipercaya diam-diam.

## Huruf tracing: satu goresan
`strokefont.py` = font goresan tunggal buatan sendiri (A-Z, a-z; gaya "bola dan tongkat" seperti buku belajar menulis prasekolah).
Garis bantu: dasar, tengah putus-putus (tinggi huruf kecil), atas tipis (huruf kapital). Tinggi huruf tebalkan: `LETTER_U` di `config.py` (22 pt).

## Struktur kode
```
create_sample_database.py   pembuat Excel contoh (26 huruf + 20 template)
data/  worksheet_database.xlsx   approved_vocab.csv (82 kata terverifikasi)
assets/images/  assets/fonts/    PNG kata kunci (Anda) dan font opsional (Fredoka / Baloo 2)
worksheet_engine/
  config.py       merek, warna, font, grid halaman, LETTER_U, REQUIRE_IMAGES, TEMPLATE_VERSION
  database.py     Excel -> Letter/Template; penguraian rentang huruf; nama folder aman
  qc.py           pemeriksaan kualitas
  art.py          pembaca PNG + kotak teks demo (TIDAK menggambar objek)
  strokefont.py   font goresan tunggal; trace_word() titik-titik; draw_model() huruf contoh bernomor
  components.py   header, bilah instruksi, footer, garis bantu menulis
  templates.py    5 jenis tata letak (capital, small, review, similar, pairs) + teks bilingual
  render.py       PDF, pratinjau, sampul (kotak huruf), thumbnail, paket
  main.py         CLI
samples/          hasil contoh yang disetujui (pembanding)
```

## Versi sebelumnya
Tag Git `v2.1` (pasangan objek, template pra-menulis, bundle) dan `v3.1` (10 tema "Tracing Words" kata + ilustrasi vektor bawaan): `git checkout v3.1`.
