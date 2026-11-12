---
title: Kamus
slug: kamus
group: Mulai
order: 2
summary: Semua istilah teknis di dokumentasi ini, dijelaskan dengan bahasa sehari-hari. Tidak perlu dibaca berurutan.
---

# Kamus

Kalau kamu menemukan kata yang tidak jelas di halaman lain, cari di sini. Urutannya
tidak penting — ini referensi, bukan bacaan.

## Istilah dasar

**Database** — tempat data disimpan secara permanen. Kalau aplikasi kamu mati dan
hidup lagi, datanya masih ada karena tersimpan di sini. Bayangkan lemari arsip
raksasa yang isinya bisa dicari dalam sepersekian detik.

**Tabel** — satu "laci" di dalam lemari itu. Tabel `pesanan` berisi semua pesanan,
tabel `pelanggan` berisi semua pelanggan.

**Kolom** — satu "jenis isian" di dalam tabel. Tabel `pesanan` punya kolom
`nomor_pesanan`, `tanggal`, `total`, `status`.

**Baris** — satu data lengkap. Satu pesanan = satu baris berisi semua kolomnya.

**Schema** — cetak biru tabelnya: tabel apa saja ada, kolom apa saja isinya, tipe
datanya apa. Bukan datanya, tapi kerangkanya. Seperti denah rumah, bukan perabotnya.

## Istilah yang muncul saat membicarakan masalah

**Status** — keadaan sesuatu saat ini. Pesanan bisa `baru`, `dibayar`, `dikirim`,
`sampai`, `dibatalkan`. Yang tampak sederhana ini justru sumber masalah paling
umum.

**Enum** — cara menyimpan status dengan daftar pilihan yang dikunci di dalam
struktur database. Menambah pilihan baru berarti membongkar struktur — dan di
server produksi itu bisa membuat situs berhenti melayani beberapa menit. Ironclad
menyarankan cara lain: lihat [Aturan DB-01](/rules/).

**Kode status** — cara menyimpan status sebagai angka, misalnya `1` untuk `baru`,
`2` untuk `dibayar`. Lebih fleksibel, tapi berbahaya kalau angkanya tidak punya
arti yang terdokumentasi.

**Lookup table** — tabel kecil yang mendaftarkan arti setiap kode. Isinya seperti
kamus: `1 = baru`, `2 = dibayar`, `3 = dikirim`. Fungsinya supaya kode `7` yang
tidak pernah didaftarkan **ditolak** oleh database, bukan diterima diam-diam.

**Foreign key (FK)** — aturan yang mengikat satu kolom ke tabel lain. Kalau
`pesanan.status_kode` punya FK ke `lookup` tadi, database menolak menyimpan angka
yang tidak ada di daftar. Ini yang membuat kode sembarang seperti `88` atau `99`
menjadi aman.

**Migrasi** — berkas berisi perintah untuk mengubah struktur database: menambah
kolom, mengubah tipe, membuat tabel. Setiap perubahan struktur harus lewat sini,
supaya bisa diulang di komputer lain dan bisa dibatalkan.

**Produksi** — server yang dipakai pengguna sungguhan. Lawannya **staging** (salinan
untuk uji coba) dan **lokal** (komputer kamu sendiri).

## Istilah tentang AI agent

**AI coding agent** — program AI yang bisa membaca berkas, menulis kode, dan
menjalankan perintah di komputermu. Contoh: Claude Code, Codex, Cursor, opencode,
Antigravity, Hermes.

**Skill** — paket instruksi yang dibaca agent saat mengerjakan tugas tertentu.
Bentuknya folder berisi berkas `SKILL.md`. Bukan program, bukan plugin — hanya
teks yang dibaca.

**Repo (repository)** — folder proyek yang dilacak oleh git, lengkap dengan riwayat
perubahannya. "Di repo kamu" berarti di folder proyek kamu.

**Commit** — menyimpan perubahan ke riwayat git, dengan catatan kenapa diubah.

**Pull request (PR)** — usulan perubahan yang harus disetujui orang lain sebelum
masuk ke kode utama. Di sinilah pemeriksaan otomatis biasanya dipasang.

**CI (Continuous Integration)** — robot yang menjalankan pemeriksaan otomatis
setiap kali ada pull request. Kalau ada yang melanggar aturan, PR-nya diberi tanda
merah dan tidak bisa digabung.

**Pre-commit hook** — pemeriksaan yang berjalan di komputermu **sebelum** commit
tersimpan. Lebih cepat daripada menunggu CI, karena kesalahannya ketahuan saat
kamu masih ingat apa yang kamu tulis.

**TTY** — istilah untuk "terminal yang dipegang manusia". Perintah yang bertanya
butuh TTY; di dalam CI atau di dalam agent, TTY tidak ada, jadi perintah seperti
itu akan menggantung. Ironclad sengaja tidak pernah bertanya karena alasan ini.

**PATH** — daftar folder tempat sistem mencari perintah. Kalau `ironclad: command
not found`, artinya folder tempat ia dipasang belum ada di daftar itu.

## Istilah khusus Ironclad

**Preset** — tingkat seberapa keras aturan ditegakkan. Ada tiga:

- `legacy-friendly` — semua hanya peringatan, tidak pernah menggagalkan build.
  Untuk repo tua yang sudah punya banyak masalah.
- `balanced` — yang paling berbahaya memblokir, sisanya memperingatkan. Ini default.
- `strict` — semuanya memblokir. Untuk repo baru atau yang sudah bersih.

**Rule ID** — nomor aturan, misalnya `DB-04`. Dipakai supaya diskusi jadi singkat:
"ini melanggar DB-04" lebih cepat daripada menjelaskan satu paragraf.

**Checker / linter** — program yang membaca kode dan menunjuk pelanggaran aturan.
Tidak memperbaiki; hanya menunjuk.

**Gate** — pemeriksaan yang **memblokir**. Bedanya dengan peringatan: peringatan
bisa diabaikan, gate tidak.

**Finding / temuan** — satu pelanggaran yang ditemukan checker, lengkap dengan
nama berkas dan nomor baris.

**Exit code** — angka yang dikembalikan program setelah selesai. `0` berarti
bersih, `1` berarti ada pelanggaran, `2` berarti perintahnya salah pakai. Robot CI
membaca angka ini, bukan tulisannya.

## Istilah yang sering bikin bingung

**"Kenapa harus dua perintah? Bukannya satu lebih baik?"**
Yang pertama memasang alatnya di komputer. Yang kedua memakainya di satu proyek
tertentu. Satu komputer bisa punya sepuluh proyek dengan aturan berbeda.

**"Apa bedanya skill dan checker?"**
Skill itu buku aturan yang dibaca AI. Checker itu pemeriksa yang membaca hasil
kerja. Yang pertama mencegah, yang kedua menangkap.

**"Kalau checker-nya sudah ada, kenapa masih perlu skill?"**
Karena checker hanya memberi tahu setelah kodenya ditulis. Skill membuat AI
menulis hal yang benar sejak awal — jauh lebih murah daripada memperbaiki.

**"Apakah ini mengubah kode saya?"**
Tidak. `ironclad check` hanya membaca. `ironclad init` menambah empat berkas baru
dan tidak menyentuh kode yang sudah ada.

**"Apakah data saya dikirim ke internet?"**
Tidak. Semua berjalan lokal. Installer mengunduh berkas sekali, lalu selesai.

**"Kalau saya tidak paham istilah teknisnya, apakah saya tetap bisa memakai ini?"**
Bisa, untuk bagian pemasangan — dua perintah, tidak ada yang perlu dijawab. Untuk
memutuskan preset mana yang tepat, ajak yang menulis kode. Lihat bagian
[Kalau kamu bukan yang menulis kode](/overview/#kalau-kamu-bukan-yang-menulis-kode).
