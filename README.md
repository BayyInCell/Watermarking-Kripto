## 🚀 Petunjuk Penggunaan

Aplikasi ini telah di-deploy secara online dan dapat diakses langsung melalui browser tanpa perlu instalasi lokal. Berikut adalah panduan langkah demi langkah pengujiannya:

### 1. Tahap Penyisipan (Embedding)
1. Buka tautan aplikasi web (Vercel).
2. Pada bagian **1. Sisipkan watermark**, klik `Choose File` lalu unggah citra asli (format `.jpg`, `.jpeg`, atau `.png`).
3. Pilih "Jenis watermark" (Teks atau Logo Biner).
4. Jika memilih teks, masukkan identitas Anda (misalnya NPM: `247006111107`).
5. Atur nilai Kekuatan ($\alpha$) penyisipan (default: 30).
6. Klik tombol **Sisipkan**. 
7. Sistem akan menampilkan metrik **PSNR** dan menyimpan ID Kunci rahasia secara aman di server.

### 2. Tahap Uji Serangan & Ekstraksi Otomatis (Blind Detection)
Sistem ini menggunakan mode ekstraksi *blind* yang terintegrasi. Anda tidak perlu mengunggah ulang gambar asli untuk mengekstrak watermark.
1. Gulir ke bagian **2. Serang citra ber-watermark**.
2. Klik salah satu tombol simulasi serangan yang tersedia (misal: `Kecerahan +30`, `JPEG Q70`, atau `Crop 10%`).
3. Tunggu beberapa detik, layar akan memuat urutan gambar dari kiri ke kanan:
   - Gambar Asli
   - Citra Ber-watermark (Stego-image)
   - Citra Termanipulasi (Hasil Serangan)
   - **Hasil Ekstraksi Watermark** (Berada di posisi paling kanan)
4. Amati hasil ekstraksi di paling kanan. Jika menggunakan logo, bentuk logo akan direkonstruksi. Jika menggunakan teks, aplikasi akan menampilkan teks yang berhasil diselamatkan beserta kalkulasi nilai ketahanannya (**NC** dan **BER**).
5. Ulangi menekan tombol serangan lain untuk membandingkan tingkat ketahanan algoritma DCT.