# Panduan: Mesin Lembar Kerja "Tracing Words"

Bahasa ringan, langkah jelas. Ringkasan teknis ada di README.md.

## 1. Menjalankan

```
pip install -r requirements.txt                       # sekali saja
python -m worksheet_engine.main --db data/worksheet_database.xlsx --out PRODUCTS
```
Hasil di `PRODUCTS/Tracing_Words/`: satu folder per tema (`01_Farm`, `02_Sea_Animals`, ...) berisi `English_Indonesian_Worksheet.pdf`
(1 halaman), `Preview.png`, `Cover.png`, `Thumbnail.png`; ditambah folder paket lengkap (10 halaman). Di `PRODUCTS/` ada
`qc_report.csv` (hasil pemeriksaan) dan `manifest.csv` (daftar produk).

| Opsi | Fungsi |
|---|---|
| `--only A,C` | hanya template tertentu (paket hanya berisi template itu) |
| `--no-pack` / `--no-themes` | tanpa paket lengkap / hanya paket |
| `--pack-name Nama_Paket` | nama folder dan judul sampul paket |
| `--workers 4` | beberapa tema sekaligus |
| `--force` | bangun ulang meski tidak berubah |
| `--strict` | peringatan (WARN) dianggap gagal |
| `--export-prompts` | tulis `image_prompts.csv` untuk membuat gambar dengan AI |

## 2. Cara kerja satu halaman
Satu tema = satu template = **tepat 5 kata**. Di halaman: 5 kata di kanan (Inggris di atas Indonesia, huruf titik-titik),
5 gambar di kiri (urutan diacak). Anak menebalkan kata, lalu menarik garis dari titik di kata ke titik di gambar yang cocok.
Urutan gambar acak tetapi **selalu sama** untuk data yang sama, dan tidak pernah ada gambar yang sejajar dengan katanya sendiri.

## 3. Mengisi database (`data/worksheet_database.xlsx`, sheet Database)
Satu baris = satu kata. Contoh satu tema:

| ID | Template | Theme_EN | Theme_ID | Word_EN | Word_ID | Image_Prompt |
|---|---|---|---|---|---|---|
| 001 | A | Farm | Peternakan | Cow | Sapi | cute cow |
| 002 | A | Farm | Peternakan | Chicken | Ayam | cute chicken |
| ... | A | (tiga baris lagi dengan Template A) | | | | |

**Menambah tema baru:** tambah 5 baris dengan huruf Template yang belum dipakai (mis. `K`). Tidak ada kode yang diubah.
Nomor tema (01, 02, ...) otomatis dari urutan huruf, jadi memakai huruf berurutan (A, B, C ...) menjaga nomor tetap rapi.

**Mengganti kata:** ubah Word_EN dan Word_ID di barisnya. Jika kata baru, tambahkan juga ke `data/approved_vocab.csv`.

## 4. Menyiapkan kata dan gambar baru
1. Tambahkan kata dan terjemahannya ke `data/approved_vocab.csv` (kolom `EN,ID,Age_Min,Notes`) **setelah** terjemahan diverifikasi penutur asli.
2. Tambahkan 5 baris di Excel.
3. Gambar: bawaan tersedia untuk 50 kata contoh. Kata lain: jalankan dengan `--export-prompts`, buat PNG dari `image_prompts.csv`,
   simpan di `assets/images/` dengan nama kata Inggris huruf kecil (`zebra.png`). PNG berlatar transparan, persegi, gaya kartun garis tebal.
4. Jalankan, lalu baca `qc_report.csv`.

## 5. Do & Don't per bagian

### `data/worksheet_database.xlsx`
**Do:** format kolom ID sebagai Teks; isi Theme_EN dan Theme_ID sama di kelima baris satu tema; tutup file Excel sebelum menjalankan skrip;
pakai kata sederhana (satu kata, maksimal 12 huruf).
**Don't:** jangan mengganti nama kolom; jangan membuat tema berisi 4 atau 6 kata (QC menggagalkan); jangan memakai ID yang sama dua kali;
jangan menaruh dua kata dalam satu sel.

### `data/approved_vocab.csv` (glosarium) dan `qc.py`
**Do:** minta penutur asli memeriksa glosarium; anggap WARN sebagai tugas (cek kata itu, tambahkan ke glosarium agar lulus berikutnya).
**Don't:** jangan menambahkan kata ke glosarium sebelum terjemahannya diverifikasi (kesalahan jadi lolos); jangan menganggap PASS berarti pasti benar;
jangan mematikan QC demi cepat.
*Catatan data saat ini:* "Sibling = Kakak" berbeda arti (kakak = saudara lebih tua) dan "Room = Kamar" menyempit ke kamar tidur.
Pertimbangkan "Brother/Sister" atau "Bedroom".

### `art.py`, `art_words.py`, `assets/images/`
**Do:** nama file PNG persis kata Inggris huruf kecil; PNG transparan; gaya gambar sama untuk semua kata.
**Don't:** jangan memakai gambar realistis, rumit, atau berekspresi menyeramkan; jangan memakai gambar tanpa hak pakai;
jangan menjual produk yang masih berisi lencana huruf (tanda gambar belum ada); jangan mengedit folder `.cache` (boleh dihapus).

### `templates.py` dan `components.py`
**Do:** ubah tampilan halaman di `draw_tracing_words()` (satu tempat untuk semua tema); ubah header/footer di `components.py`; naikkan
`TEMPLATE_VERSION` di `config.py` setiap kali tampilan berubah, agar semua tema dibuat ulang.
**Don't:** jangan menulis kata tertentu (mis. "farm") langsung di template, pakai `{THEME_EN}` dst; jangan mengecilkan margin tanpa cetak uji.
Placeholder yang tersedia: `{THEME_EN} {THEME_ID} {THEME_EN_LOWER} {THEME_ID_LOWER} {NUM} {KEY}`.

### `config.py`
**Do:** ganti `BRAND["name"]` dengan nama merek Anda sebelum produksi; font bulat (Fredoka/Baloo 2) di `assets/fonts/` memperbaiki tampilan huruf tracing.
**Don't:** jangan menghapus kunci di `PALETTE`; perubahan warna tidak memicu pembuatan ulang otomatis, jadi pakai `--force` atau naikkan `TEMPLATE_VERSION`.

### `render.py` dan `main.py`
**Do:** uji dengan `--only` sebelum menjalankan semua; pakai `--workers` untuk banyak tema; cetak satu halaman di A4 skala 100% sebelum produksi.
**Don't:** jangan menjalankan dari folder lain (jalur `data/...` relatif); jangan menghapus `.build_hash` kecuali ingin membangun ulang; jangan memindahkan file hasil
(nama dan jalurnya dipakai `manifest.csv`).

### `create_sample_database.py`
**Do:** jalankan sekali untuk contoh format, lalu salin dan edit Excel hasilnya.
**Don't:** jangan dijalankan ulang setelah database Anda terisi: file ditimpa tanpa bertanya.

## 6. Masalah umum
| Gejala | Penyebab | Solusi |
|---|---|---|
| `Sheet 'Database' kekurangan kolom` | nama kolom salah | samakan dengan 7 kolom di bagian 3 |
| Tema berstatus FAIL, `word-count` | bukan tepat 5 baris | perbaiki jumlah baris tema itu |
| FAIL `translation` | terjemahan beda dari glosarium | betulkan Excel, atau perbarui glosarium jika glosarium yang salah |
| Gambar berupa lingkaran berhuruf | belum ada gambar | tambahkan `kata.png` ke `assets/images/` |
| Warna/teks tidak berubah setelah diedit | skrip menganggap tidak berubah | `--force` |
| Excel tidak terbaca | file terbuka di Excel | tutup file |
| ID tertulis `1` bukan `001` | Excel membuang angka nol | format kolom sebagai Teks (skrip juga merapikan) |

## 7. Batasan
* Gambar bawaan hanya untuk 50 kata contoh; selebihnya perlu PNG Anda.
* Pemeriksaan terjemahan dan usia hanya berlaku untuk kata yang ada di glosarium.
* Belum ada halaman kunci jawaban. Tata letak sudah diuji secara visual, belum di printer sungguhan.
* Versi sebelumnya (pasangan objek, template pra-menulis, mode bundle) ada di tag Git `v2.1`.
