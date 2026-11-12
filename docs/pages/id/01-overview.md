---
title: Apa ini, untuk siapa
slug: overview
group: Mulai
order: 1
summary: Penjelasan tanpa jargon — masalah apa yang diselesaikan, apa yang harus kamu lakukan, dan apa yang tidak perlu kamu sentuh.
---

# Ironclad, tanpa jargon

**Ironclad itu buku aturan untuk AI yang menulis kode.** Bukan aplikasi, bukan
layanan berlangganan — sebuah berkas teks yang dibaca AI sebelum ia mulai bekerja,
plus pemeriksa yang menolak hasilnya kalau melanggar.

Kalau kalimat itu belum jelas, ini versi lainnya: *kalau tim kamu memakai AI untuk
membuat aplikasi, Ironclad menjaga hasilnya tetap konsisten — supaya tidak perlu
dibongkar setahun kemudian.*

**Ini untuk siapa:**

- **Kamu programmer** yang memakai AI (Claude, Copilot, Cursor) untuk membuat
  bagian database. Kamu akan memakai ini setiap hari.
- **Kamu bukan programmer**, tapi kamu yang memutuskan apakah tim memakai alat ini.
  Yang perlu kamu lakukan cuma meneruskannya ke developer, lalu bertanya tiga hal
  di [bagian bawah](#kalau-kamu-bukan-yang-menulis-kode).

**Yang tidak perlu kamu tahu untuk mulai:** apa itu enum, apa itu foreign key, apa
itu migrasi. Semua istilah seperti itu ada di [Kamus](/kamus/), dan tidak perlu
dibaca berurutan.

## Masalah yang diselesaikan

Ini kejadian yang berulang di banyak tim.

Kamu minta AI — Claude, Copilot, Cursor, apa pun — menambah fitur "pesanan".
Ia menulis bagian database-nya (tempat data disimpan). Fiturnya jalan. Semua
senang.

Enam bulan kemudian, ada tiga masalah yang muncul bersamaan:

- Di satu tabel, status pesanan disimpan sebagai `1`, `2`, `3`. Tidak ada yang
  ingat `2` itu apa. Yang menulisnya sudah pindah kerja.
- Di tabel lain, status ditulis sebagai teks: `"Sudah dibayar"`, `"sudah dibayar"`,
  `"Sudah Dibayar"` — tiga ejaan, dan laporan penjualan jadi salah hitung.
- Klien minta status baru: "ditunda karena cuaca". Untuk menambahkannya, kamu
  harus mengubah **struktur** database, bukan sekadar menambah data. Di server
  produksi, itu bisa mengunci tabel — artinya toko tutup beberapa menit.

Tidak ada satu pun dari ini yang salahnya AI. AI menulis apa yang masuk akal saat
itu. Yang tidak ada: aturan tertulis yang ia baca sebelum mulai.

## Kenapa ini mahal diperbaiki

Analogi renovasi rumah.

Kamu bebas memilih warna cat, gagang pintu, atau tata letak furnitur — itu murah
diubah kapan saja. Tapi pipa air dan instalasi listrik harus mengikuti standar.
Bukan karena kita suka aturan, tapi karena memperbaikinya berarti membongkar
dinding.

Database itu pipa dan listriknya. Tampilan bisa diganti dalam sehari. Struktur
data yang salah akan menempel bertahun-tahun, dan biayanya naik setiap kali ada
data baru masuk.

Ironclad adalah standar bangunan untuk bagian itu — bukan untuk catnya.

## Apa yang Ironclad lakukan

Tiga hal, dan hanya tiga:

**1. Memberi AI buku aturan sebelum ia mulai.**
Sebuah berkas teks di repo kamu (`.agent/standards.md`) berisi keputusan yang
sudah diambil tim: status disimpan bagaimana, uang disimpan bagaimana, tanggal
disimpan bagaimana. AI membacanya sebelum menulis database.

**2. Menyimpan aturan itu di dalam repo, bukan di kepala orang.**
Ikut tersimpan di git, ikut ter-review saat ada perubahan. Anggota tim baru —
manusia atau AI — membaca berkas yang sama.

**3. Memeriksa hasilnya secara otomatis.**
Sebuah skrip (`check_schema.py`) membaca kode database dan menunjuk pelanggaran
dengan nomor aturan. Bisa dijalankan manual, bisa dipasang di CI sehingga pull
request yang melanggar tidak bisa digabung.

Poin 1 itu saran. Poin 3 itu penegakan. Kamu butuh keduanya, karena AI yang cuma
diberi saran akan kadang mengabaikannya, dan pemeriksa tanpa aturan tertulis cuma
menghasilkan daftar kesalahan yang tidak jelas cara betulkannya.

## Apa yang harus kamu lakukan

Dua perintah. Tidak ada yang perlu dijawab, tidak ada konfigurasi.

```bash
# 1. pasang (sekali per komputer)
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

```bash
# 2. di dalam repo kamu — lihat dulu, tidak mengubah apa pun
ironclad check
```

Kalau hasilnya masuk akal, jadikan permanen:

```bash
ironclad init
```

Selesai. Sekitar dua menit, dan repo kamu belum berubah sampai kamu menjalankan
perintah ketiga.

Panduan langkah demi langkah: [Quickstart](/quickstart/).

## Kalau kamu bukan yang menulis kode

Kamu tetap bisa memakai ini. Yang perlu kamu lakukan:

**Kirim halaman ini ke developer kamu** — atau ke orang yang mengurus aplikasinya.
Minta mereka menjalankan dua perintah di atas.

**Ajukan tiga pertanyaan ini** sesudahnya. Jawabannya menunjukkan apakah ini
benar-benar dipasang atau cuma dijanjikan:

1. "Preset apa yang dipakai?" — jawaban yang benar salah satu dari
   `balanced`, `strict`, atau `legacy-friendly`. Kalau jawabannya "apa itu
   preset", berarti belum dijalankan.
2. "Berapa temuan saat ini?" — angka. Bukan "sudah beres".
3. "Apakah pull request yang melanggar benar-benar gagal?" — kalau belum pernah
   diuji, berarti gate-nya belum terbukti bekerja.

**Yang tidak perlu kamu pelajari:** cara kerja checker, apa itu foreign key, atau
isi berkas YAML-nya. Itu urusan yang menulis kode.

## Yang tidak dilakukan Ironclad

- **Bukan pengganti programmer.** Ia tidak menulis fitur, tidak memperbaiki bug.
- **Bukan pengganti review.** Ia menangkap pola yang salah; ia tidak tahu apakah
  logika bisnismu benar.
- **Bukan alat keamanan.** Tidak memeriksa kebocoran data atau celah akses.
- **Tidak mengubah tampilan aplikasi.** Tidak ada hubungannya dengan desain.
- **Tidak mengirim data ke mana pun.** Semuanya berjalan di komputermu sendiri.

## Batas jujurnya

- Pemeriksanya bekerja dengan pencocokan pola, bukan pemahaman. Ia bisa salah
  menandai kode yang sebenarnya benar, dan bisa melewatkan yang seharusnya
  ditandai. Manusia tetap lapis terakhir.
- Ia tahu tujuh aturan tentang database. Bukan dua ratus.
- Belum ada pembaruan otomatis. Untuk versi baru, jalankan ulang installer.
- Kalau tim kamu belum pernah pakai AI untuk menulis database, manfaatnya kecil —
  ini dibuat untuk masalah yang muncul justru karena AI menulis banyak dan cepat.

## Arah selanjutnya

| Kalau kamu… | Baca |
|---|---|
| ingin tahu istilah yang dipakai di sini | [Kamus](/kamus/) |
| ingin memasang sekarang | [Pasang di agent](/install/) |
| ingin melihat langkah lengkapnya | [Quickstart](/quickstart/) |
| ingin tahu aturan apa saja yang diperiksa | [Aturan](/rules/) |
| ragu ini akan dipakai tim atau tidak | [Tiga lapis](/three-layers/) — kenapa alat seperti ini sering dicabut |
