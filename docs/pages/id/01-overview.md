---
title: Apa ini, untuk siapa
slug: overview
group: Mulai
order: 1
summary: Penjelasan tanpa jargon — masalah apa yang diselesaikan, apa yang harus kamu lakukan, dan apa yang tidak perlu kamu sentuh.
---

# Ironclad, tanpa jargon

**Ironclad menjaga satu proyek tetap konsisten saat lebih dari satu orang
menggarap bagian database-nya.**

Bukan aplikasi, bukan layanan berlangganan. Isinya dua hal: satu berkas aturan di
dalam repo kamu, dan satu pemeriksa yang menolak hasil kerja yang melanggar aturan
itu.

## Masalah sebenarnya: dua developer, dua gaya

Ini bukan cerita tentang AI. Ini cerita tentang tim.

Satu proyek. Tiga developer. Ketiganya menyentuh database — menambah kolom,
membuat tabel baru, mengubah status.

Developer A menyimpan status pesanan sebagai **enum**:

```sql
status ENUM('baru', 'dibayar', 'dikirim')
```

Developer B menyimpan hal yang sama sebagai **integer**:

```sql
status_code smallint NOT NULL
```

Dua-duanya jalan. Dua-duanya lolos review, karena masing-masing masuk akal kalau
dilihat sendirian. Yang tidak ada: keputusan bersama tentang mana yang dipakai
proyek ini.

Enam bulan kemudian, satu tabel statusnya enum, tabel lain integer, tabel ketiga
teks bebas. Laporan harus menulis tiga query berbeda untuk hal yang sama. Dan saat
klien minta status baru — "ditunda karena cuaca" — developer C harus tahu dulu
tabel mana yang pakai cara apa, karena menambah nilai enum dan menambah baris
lookup table adalah dua pekerjaan yang sangat berbeda.

Tidak ada yang salah di sini. Yang hilang cuma satu: **aturan tertulis yang dibaca
semua orang sebelum mulai.**

## Rekomendasinya: integer, bukan enum

Ironclad condong ke **integer + lookup table** sebagai default. Alasannya bukan
selera:

- **Menambah nilai enum berarti mengubah struktur database.** Di MySQL itu
  `ALTER TABLE`, dan pada tabel besar ia mengunci tabel selama proses. Status
  bisnis selalu tumbuh — dan tiap pertumbuhan tidak seharusnya jadi acara
  pemeliharaan.
- **Menambah satu kode integer berarti menambah satu baris data.** Operasi biasa,
  tidak mengunci apa pun, bisa dilakukan tanpa deploy.
- **Angka yang terdaftar tidak lebih rawan daripada teks.** Selama kodenya ada di
  lookup table dan dijaga foreign key, database menolak angka yang tidak pernah
  didaftarkan. `88` aman kalau `88` terdaftar; `87` ditolak.

Jadi aturannya bukan "jangan pernah pakai enum". Aturannya: **satu cara untuk satu
proyek**, dan cara yang dipilih adalah integer + lookup — kecuali ada alasan
tertulis untuk menyimpang, dan alasan itu masuk review.

## Kenapa ini mahal diperbaiki nanti

Analogi renovasi rumah.

Kamu bebas memilih warna cat, gagang pintu, atau tata letak furnitur — murah
diubah kapan saja. Tapi pipa air dan instalasi listrik harus mengikuti satu
standar. Bukan karena kita suka aturan, tapi karena memperbaikinya berarti
membongkar dinding.

Database itu pipa dan listriknya. Tampilan bisa diganti dalam sehari. Struktur
data yang tidak konsisten menempel bertahun-tahun, dan biayanya naik setiap kali
ada data baru masuk.

## AI mempercepat masalah ini, bukan menyebabkannya

Kalau satu developer menulis enum dan yang lain integer, itu terjadi karena
masing-masing memutuskan sendiri. AI membuat keputusan itu terjadi **lebih cepat
dan lebih banyak** — ia menulis dalam hitungan detik, di banyak berkas, dan tidak
pernah bertanya "proyek ini biasanya pakai cara yang mana?"

Itu sebabnya Ironclad menaruh aturannya di tempat yang dibaca agent: bukan supaya
AI jadi pintar, tapi supaya AI tidak jadi anggota tim keempat yang punya gaya
sendiri.

## Apa yang Ironclad lakukan

Tiga hal, dan hanya tiga:

**1. Menuliskan keputusan tim di dalam repo.**
Berkas `.agent/standards.md` berisi keputusan yang sudah diambil: status disimpan
bagaimana, uang disimpan bagaimana, tanggal disimpan bagaimana. Bukan preferensi
satu orang — kesepakatan yang ikut ter-commit.

**2. Membuat AI membacanya sebelum mulai.**
Agent membaca berkas itu sebelum menulis database. Developer baru — manusia atau
AI — membaca berkas yang sama di hari pertama.

**3. Memeriksa hasilnya otomatis.**
Skrip `check_schema.py` membaca kode database dan menunjuk pelanggaran dengan nomor
aturan. Bisa dijalankan manual, bisa dipasang di CI sehingga pull request yang
melanggar tidak bisa digabung. Ini yang menangkap developer yang tidak memakai AI
sama sekali — atau yang lupa.

Poin 1 dan 2 itu saran. Poin 3 itu penegakan. Kamu butuh keduanya: saran tanpa
penegakan akan diabaikan saat tenggat, dan penegakan tanpa aturan tertulis cuma
menghasilkan daftar kesalahan yang tidak jelas cara betulkannya.

## Apa yang harus kamu lakukan

Dua perintah. Tidak ada yang perlu dijawab.

```bash
# 1. pasang (sekali per komputer)
npx github:wilsench/ironclad#v0.8.4
```

```bash
# 2. di dalam repo — lihat dulu, tidak mengubah apa pun
ironclad check
```

Kalau hasilnya masuk akal, jadikan permanen:

```bash
ironclad init
```

Lalu commit empat berkas yang ditulisnya. Sejak commit itu, setiap orang di proyek
— dan setiap agent — membaca aturan yang sama.

Panduan lengkap: [Quickstart](/quickstart/).

## Kalau kamu bukan yang menulis kode

Kamu tetap bisa memakai ini. Yang perlu kamu lakukan:

**Kirim halaman ini ke developer kamu.** Minta mereka menjalankan dua perintah di
atas, lalu commit hasilnya.

**Ajukan tiga pertanyaan ini** sesudahnya. Jawabannya menunjukkan apakah ini
benar-benar dipasang atau cuma dijanjikan:

1. "Preset apa yang dipakai?" — jawaban yang benar salah satu dari `balanced`,
   `strict`, atau `legacy-friendly`. Kalau jawabannya "apa itu preset", berarti
   belum dijalankan.
2. "Berapa temuan saat ini?" — angka. Bukan "sudah beres".
3. "Apakah pull request yang melanggar benar-benar gagal?" — kalau belum pernah
   diuji, gate-nya belum terbukti bekerja.

**Pertanyaan keempat, khusus untuk masalah enum:** "Status di proyek ini pakai
enum atau integer?" Kalau jawabannya "tergantung", berarti masalahnya masih ada —
dan itu persis yang diselesaikan Ironclad.

**Yang tidak perlu kamu pelajari:** cara kerja checker, apa itu foreign key, atau
isi berkas YAML-nya.

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
- Kalau kamu memakai checker-nya, ia tahu delapan pola tentang status di database.
  Bukan dua ratus. Yang ditanamkan ke agent cukup satu pemahaman, bukan daftar aturan.
- **Ia tidak bisa memaksa orang membaca.** Kalau ada developer yang mengabaikan
  `.agent/standards.md` dan CI-nya tidak dipasang, tidak ada yang menangkap.
  Yang membuatnya bekerja adalah CI, bukan niat baik.
- Belum ada pembaruan otomatis. Untuk versi baru, jalankan ulang installer.

## Arah selanjutnya

| Kalau kamu… | Baca |
|---|---|
| ingin tahu istilah yang dipakai di sini | [Kamus](/kamus/) |
| ingin memasang sekarang | [Pasang di agent](/install/) |
| ingin melihat langkah lengkapnya | [Quickstart](/quickstart/) |
| ingin tahu aturan apa saja yang diperiksa | [Aturan](/rules/) |
| ingin tahu kenapa alat seperti ini sering dicabut | [Tiga lapis](/three-layers/) |
