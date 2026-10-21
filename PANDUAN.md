# Panduan: Mesin Lembar Kerja "Alphabet Tracing"

Bahasa ringan, langkah jelas. Ringkasan teknis ada di README.md.

## 1. Menjalankan

```
pip install -r requirements.txt                       # sekali saja
python -m worksheet_engine.main --db data/worksheet_database.xlsx --out PRODUCTS
```
Hasil di `PRODUCTS/Alphabet_Tracing/`: satu folder per template (`A_Capital_Letters_A-C`, `K_Small_Letters_a-c`, ...) berisi
`English_Indonesian_Worksheet.pdf` (1 halaman), `Preview.png`, `Cover.png`, `Thumbnail.png`; ditambah folder paket lengkap (20 halaman).
Di `PRODUCTS/`: `qc_report.csv` (hasil pemeriksaan) dan `manifest.csv` (daftar produk).

| Opsi | Fungsi |
|---|---|
| `--only A,K,T` | hanya template tertentu (paket hanya berisi template itu) |
| `--no-pack` / `--no-templates` | tanpa paket lengkap / hanya paket |
| `--pack-name Nama_Paket` | nama folder dan judul sampul paket |
| `--workers 4` | beberapa template sekaligus |
| `--force` | bangun ulang meski tidak berubah |
| `--strict` | peringatan (WARN) dianggap gagal |
| `--export-prompts` | tulis `image_prompts.csv`: daftar nama file PNG yang dibutuhkan + prompt pembuatnya |

## 2. Memasang gambar PNG (inti pekerjaan Anda berikutnya)
Kode tidak menggambar objek apa pun. Setiap huruf punya satu kata kunci bergambar (Apple untuk A, Ball untuk B, dst.).
1. Buat PNG: latar transparan, persegi (1000 x 1000 px atau lebih), gaya kartun garis tebal yang sama untuk semua.
2. Namai file dengan kata Inggris huruf kecil: `apple.png`, `ice_cream.png` (spasi dan tanda hubung menjadi garis bawah, jadi `Yo-Yo` = `yo_yo.png`).
   Huruf besar/kecil nama file tidak dipermasalahkan (`Apple.png` tetap ditemukan).
3. Simpan di `assets/images/` (folder `assets/Images/` juga dibaca).
4. Jalankan ulang. Hanya halaman yang memakai PNG baru yang dibangun ulang.
5. Selama PNG belum ada, halaman menampilkan **kotak teks biasa** berisi nama kata dan nama file yang diharapkan (khusus demo; jangan dijual).
6. Setelah semua PNG terpasang, ubah `REQUIRE_IMAGES = True` di `config.py`: PNG yang hilang jadi WARN dan `--strict` menolaknya.
Mau kata kunci lain (mis. A = Ayam)? Ganti `Word_EN`/`Word_ID` di sheet Letters (dan tambahkan ke glosarium).

## 3. Mengisi database (`data/worksheet_database.xlsx`)

**Sheet Letters** (satu baris = satu huruf + kata kunci):

| Letter | Word_EN | Word_ID | Image | Image_Prompt |
|---|---|---|---|---|
| A | Apple | Apel | (kosong = apple.png) | cute apple |

**Sheet Templates** (satu baris = satu halaman):

| Key | Type | Letters | Title_EN | Title_ID |
|---|---|---|---|---|
| A | capital | A-C | Capital Letters A-C | Huruf Besar A-C |
| S | similar | b+d, p+q, m+n | Telling Similar Letters Apart (b-d, p-q, m-n) | Membedakan Huruf Mirip (b-d, p-q, m-n) |

Jenis (kolom Type): **capital** huruf besar (1-5 huruf) | **small** huruf kecil (1-5) | **review** A-Z berurutan | **similar** pasangan huruf mirip (1-4 pasang) | **pairs** pasangan Aa-Zz.
Letters boleh berupa rentang (`A-C`), daftar (`A-C, F`), atau untuk similar pasangan dengan `+`.
Mengubah pembagian (misalnya A-C jadi A-D) atau judul cukup dengan mengganti sel; tidak ada kode yang diubah.
Menambah halaman baru: tambah baris dengan Key yang belum dipakai (U, V, ...). Template bergambar (capital, small, similar) membutuhkan baris huruf yang bersangkutan di sheet Letters.

## 4. Cara kerja halaman
* **capital / small**: tiap huruf satu blok. Kolom kiri: huruf contoh dengan **nomor urutan goresan**. Tengah: gambar kata kunci dan katanya. Kanan: baris tebalkan
  (titik-titik, titik hijau = tempat mulai tiap goresan) lalu baris menulis sendiri. Garis bantu tiga tingkat membantu tinggi huruf.
* **review**: huruf A-Z berurutan, bernomor 1-26 (urutan abjad), tiap baris: tebalkan + tulis sendiri.
* **similar**: tiap pasangan: dua kartu pembeda, baris tebalkan bergantian (b d b d), dan baris "lingkari huruf b".
* **pairs**: 26 kotak, tiap kotak huruf besar dan kecil untuk ditebalkan.

## 5. Do & Don't per bagian

### `data/worksheet_database.xlsx`
**Do:** format kolom ID/Key sebagai Teks; tutup file Excel sebelum menjalankan skrip; pilih kata kunci sederhana yang gambarnya jelas untuk anak 3-5 tahun;
pakai kata yang diawali huruf yang bersangkutan (QC memperingatkan jika tidak).
**Don't:** jangan mengganti nama kolom atau nama sheet (`Letters`, `Templates`); jangan memakai Key yang sama dua kali; jangan menulis type di luar daftar;
jangan menulis rentang terbalik (`C-A`) atau pasangan similar dengan tanda hubung (`b-d`; harus `b+d`).

### `data/approved_vocab.csv` (glosarium) dan `qc.py`
**Do:** minta penutur asli memeriksa glosarium; anggap WARN sebagai tugas (cek kata itu, tambahkan ke glosarium agar lulus berikutnya).
**Don't:** jangan menambahkan kata ke glosarium sebelum terjemahannya diverifikasi (kesalahan jadi lolos); jangan menganggap PASS berarti pasti benar;
jangan mematikan QC demi cepat.
*Catatan data contoh:* kata kunci dan terjemahan di sheet Letters adalah **usulan saya**, bukan keputusan Anda. Contoh: "Pen = Pulpen" (juga "pena"), "Queen = Ratu".

### `assets/images/`
**Do:** nama file persis seperti di bagian 2; PNG transparan; gaya gambar sama untuk semua huruf.
**Don't:** jangan memakai gambar realistis, rumit, atau berekspresi menyeramkan; jangan memakai gambar tanpa hak pakai;
jangan menjual produk yang masih menampilkan kotak teks demo; jangan menaruh PNG berlatar putih padat (kotak putih akan terlihat di kartu berwarna).

### `templates.py` dan `components.py`
**Do:** ubah tampilan satu jenis halaman di fungsi `draw_*` jenis itu; ubah header/footer di `components.py`; naikkan `TEMPLATE_VERSION` di `config.py`
setiap kali tampilan berubah, agar semua template dibuat ulang.
**Don't:** jangan menulis huruf atau kata tertentu langsung di template; jangan mengecilkan margin tanpa cetak uji.
Placeholder teks: `{LETTERS} {LETTERS_AND_EN} {LETTERS_AND_ID} {KEY} {TITLE_EN} {TITLE_ID}`.

### `strokefont.py` (huruf tracing satu goresan)
**Do:** ubah bentuk huruf di kamus `G` (tiap huruf = daftar goresan; titik pertama = tempat mulai menulis); lihat hasilnya dengan `--only A` atau `--only K` dan cetak.
**Don't:** jangan menganggap bentuk huruf ini mengikuti kurikulum tertentu tanpa dicek guru: gaya "bola dan tongkat" adalah pola umum buku prasekolah,
bukan standar resmi. Jangan memakai huruf selain A-Z/a-z pada halaman tracing.

### `config.py`
**Do:** ganti `BRAND["name"]` dengan nama merek Anda sebelum produksi; `LETTER_U` mengatur ukuran huruf tebalkan; font bulat (Fredoka/Baloo 2) di `assets/fonts/` memperbaiki tampilan teks.
**Don't:** jangan menghapus kunci di `PALETTE`; perubahan warna tidak memicu pembuatan ulang otomatis, jadi pakai `--force` atau naikkan `TEMPLATE_VERSION`.

### `render.py` dan `main.py`
**Do:** uji dengan `--only` sebelum menjalankan semua; cetak satu halaman tiap jenis di A4 skala 100% sebelum produksi.
**Don't:** jangan menjalankan dari folder lain (jalur `data/...` relatif); jangan menghapus `.build_hash` kecuali ingin membangun ulang; jangan memindahkan file hasil.

### `create_sample_database.py`
**Do:** jalankan sekali untuk contoh format, lalu salin dan edit Excel hasilnya.
**Don't:** jangan dijalankan ulang setelah database Anda terisi: file ditimpa tanpa bertanya.

## 6. Masalah umum
| Gejala | Penyebab | Solusi |
|---|---|---|
| `Sheet 'Letters' kekurangan kolom` | nama kolom/sheet salah | samakan dengan bagian 3 |
| FAIL `letters-missing` | huruf dipakai template bergambar tapi tak ada di sheet Letters | tambahkan barisnya |
| FAIL `letter-count` | terlalu banyak huruf untuk type itu (capital/small maks 5) | pecah jadi dua template |
| FAIL `translation` | terjemahan beda dari glosarium | betulkan Excel, atau perbarui glosarium jika glosarium yang salah |
| Gambar berupa kotak kuning bertuliskan nama | PNG belum ada | tambahkan PNG sesuai nama yang tertera di kotak |
| PNG sudah ditaruh tetapi tidak muncul | nama file tak cocok atau salah folder | cocokkan dengan nama di kotak teks; cek `assets/images/` |
| Warna/teks tidak berubah setelah diedit | skrip menganggap tidak berubah | `--force` |
| Excel tidak terbaca | file terbuka di Excel | tutup file |

## 7. Batasan
* Bentuk huruf tracing adalah font buatan sendiri; periksa dengan guru atau terapis okupasi sebelum dijual.
* Pemeriksaan terjemahan hanya berlaku untuk kata yang ada di glosarium.
* Belum ada halaman kunci jawaban. Tata letak sudah diperiksa secara visual, belum di printer sungguhan: cetak dulu satu halaman tiap jenis.
* Sistem sebelumnya ada di tag Git `v2.1` dan `v3.1`.
