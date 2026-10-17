# Mesin Lembar Kerja "Tracing Words" Dwibahasa (Inggris-Indonesia), usia 3-5 tahun

Isi tabel Excel -> skrip membuat lembar kerja siap cetak (PDF), pratinjau, sampul, dan thumbnail.
Satu tampilan merek yang sama, isi berbeda. Cara kerja anak: **menebalkan kata (satu garis titik-titik di tengah goresan huruf), lalu menarik garis ke gambar yang cocok.**

```
pip install -r requirements.txt
python create_sample_database.py          # sekali saja: membuat data/worksheet_database.xlsx (10 tema, 50 kata)
python -m worksheet_engine.main --db data/worksheet_database.xlsx --out PRODUCTS
```
Panduan lengkap beserta Do & Don't: **PANDUAN.md**

## Konsep: 1 tema = 1 template = 5 kata

| Template | Tema | Kata (Inggris / Indonesia) |
|---|---|---|
| A | 01 Peternakan (Farm) | cow/sapi, chicken/ayam, duck/bebek, sheep/domba, horse/kuda |
| B | 02 Hewan Laut (Sea Animals) | fish/ikan, whale/paus, crab/kepiting, octopus/gurita, turtle/penyu |
| C | 03 Buah-buahan (Fruits) | apple/apel, banana/pisang, orange/jeruk, pineapple/nanas, grape/anggur |
| D | 04 Sayuran (Vegetables) | carrot/wortel, spinach/bayam, tomato/tomat, corn/jagung, potato/kentang |
| E | 05 Kendaraan (Vehicles) | car/mobil, bus/bus, train/kereta, ship/kapal, airplane/pesawat |
| F | 06 Anggota Tubuh (Body Parts) | eye/mata, nose/hidung, ear/telinga, mouth/mulut, hand/tangan |
| G | 07 Keluarga & Rumah (Family & Home) | father/ayah, mother/ibu, sibling/kakak, room/kamar, door/pintu |
| H | 08 Perlengkapan Sekolah (School Things) | book/buku, pencil/pensil, bag/tas, eraser/penghapus, table/meja |
| I | 09 Cuaca & Alam (Weather & Nature) | rain/hujan, cloud/awan, moon/bulan, star/bintang, tree/pohon |
| J | 10 Makanan & Minuman (Food & Drink) | rice/nasi, bread/roti, milk/susu, water/air, egg/telur |

Isi tema datang dari Excel, bukan dari kode. Menambah tema baru = menambah 5 baris dengan huruf Template baru (K, L, ...).

## Isi satu halaman (A4 portrait)
```
[garis warna merek]
[USIA 3-5]                                  Nama / Name: ______
01 Farm                       <- judul (Inggris)
Peternakan - Menebalkan Kata  <- judul (Indonesia)
* Saya bisa menebalkan dan mencocokkan kata tentang peternakan
(A) Tebalkan kata-katanya. Tarik garis ke gambar yang cocok.
 [gambar] o        o [ Cow   . . . satu garis titik per goresan ]
 [gambar] o        o [ Sapi  ........                  ]     5 baris; gambar DIACAK,
 ...                                                          kata berurutan
Merek | Halaman n / total | (c) tahun merek | teks lisensi EN/ID
```
Gaya: kartun vektor, garis tebal navy 3,4 pt, warna cerah lembut, objek besar, banyak ruang kosong.
Warna aksen per tema bergiliran: merah muda, biru, hijau, ungu (kuning sengaja dihindari: teksnya terlalu pucat saat dicetak).

## Data Excel (sheet "Database", satu baris = satu kata)
| Kolom | Isi |
|---|---|
| ID | unik, teks (`001`) |
| Template | huruf A-Z; **5 baris dengan huruf sama = 1 tema** |
| Theme_EN / Theme_ID | nama tema, sama di kelima baris |
| Word_EN / Word_ID | kata dan terjemahannya (harus ada di `data/approved_vocab.csv`) |
| Image_Prompt | harus menyebut Word_EN |

## Alur kerja
```
Excel --load_themes--> QC (qc.py) --FAIL: tema dilewati / WARN: dibuat tapi perlu dicek-->
   per tema: PDF 1 halaman + Preview + Cover + Thumbnail      -> PRODUCTS/Tracing_Words/01_Farm/ ...
   semua tema lolos: PDF paket (1 halaman per tema)           -> PRODUCTS/Tracing_Words/Tracing_Words_Complete_Pack/
   qc_report.csv, manifest.csv, (image_prompts.csv)
```
Dijalankan ulang tidak membangun ulang tema yang tidak berubah (sidik jari data + versi template + file gambar).

## Pemeriksaan kualitas (qc.py)
| Pemeriksaan | Hasil |
|---|---|
| Tema harus tepat 5 kata; kolom wajib terisi; ID dan kata tidak dobel | FAIL |
| Terjemahan berbeda dari glosarium | **FAIL** |
| Kata belum ada di glosarium | WARN (cek usia, ejaan, terjemahan manual) |
| Kata panjang (> 12 huruf / > 2 kata) atau terlalu lebar untuk huruf tracing | WARN |
| Belum ada gambar untuk kata itu | WARN (dipakai lencana huruf) |
| Karakter di Word_EN/Word_ID yang belum ada di font tracing (hanya A-Z, spasi, - dan ') | FAIL |
| Image_Prompt tidak menyebut kata / memuat kata terlarang (realistic, scary, photo ...) | WARN / FAIL |

Pemeriksaan terjemahan hanya sebaik glosarium Anda: kata di luar glosarium tidak pernah dipercaya diam-diam.

## Huruf tracing: satu goresan (bukan huruf berongga)
Kata ditulis sebagai **satu garis titik-titik di sepanjang tengah goresan** tiap huruf (`strokefont.py`, gaya "bola dan tongkat" seperti buku belajar
menulis prasekolah), bukan garis putus-putus yang mengelilingi bentuk huruf. Titik hijau menandai tempat mulai: di awal goresan pertama tiap huruf
(kata Inggris) dan di huruf pertama (kata Indonesia). Garis bantu: garis dasar, garis tengah putus-putus (tinggi huruf kecil), garis atas tipis (huruf kapital).
Pengaturan di `config.py`: `TRACE_STYLE` ("stroke" bawaan atau "outline" = gaya lama), `TRACE_U_EN` / `TRACE_U_ID` (tinggi huruf kecil, pt).

## Gambar
Urutan pencarian per kata: (1) `assets/images/<kata>.png` (PNG transparan buatan Anda) -> (2) gambar vektor bawaan di `art.py` / `art_words.py`
(50 kata contoh) -> (3) lencana huruf (QC memberi WARN). `--export-prompts` menghasilkan `image_prompts.csv` untuk membuat PNG dengan AI.

## Struktur kode
```
create_sample_database.py   pembuat Excel contoh (10 tema x 5 kata)
data/  worksheet_database.xlsx   approved_vocab.csv (69 kata terverifikasi)
assets/images/  assets/fonts/    gambar PNG dan font opsional (Fredoka / Baloo 2)
worksheet_engine/
  config.py       merek, warna, font, grid halaman, ambang QC, TEMPLATE_VERSION
  database.py     Excel -> Theme/Word, nama folder aman
  qc.py           pemeriksaan kualitas
  strokefont.py   font GORESAN TUNGGAL: tiap huruf = jalur goresan; trace_word() menggambar garis titik-titik
  art.py          mesin gambar (Ink) + pencarian PNG; art_words.py = 43 ilustrasi tema
  components.py   header, bilah instruksi, footer, huruf titik-titik, garis menulis
  templates.py    SATU tata letak "Tracing Words" + teks bilingual
  render.py       PDF, pratinjau, sampul, thumbnail, paket
  main.py         CLI
samples/          hasil contoh yang disetujui (pembanding)
```

## Skala dan versi
* `--workers 8` membangun banyak tema sekaligus. Ubah merek/warna di `config.py`, lalu naikkan `TEMPLATE_VERSION` agar semua dibuat ulang.
* **Versi sebelumnya** (produk "pasangan objek" dengan template pra-menulis A-J, template matching, mode bundle) tersimpan di tag Git `v2.1`:
  `git checkout v2.1`.
