---
title: Memperbarui
slug: update
group: Mulai
order: 8
summary: Cara tahu ada versi baru, apa yang berubah, dan tiga pilihan yang tidak memaksa kamu memperbarui.
---

# Memperbarui

Ironclad tidak punya pembaruan otomatis. Tidak ada daemon yang berjalan, tidak ada
telemetri, dan tidak ada yang menghubungi internet tanpa kamu memintanya.

Yang ada: **satu pemeriksaan ringan yang kamu jalankan sendiri.**

## `ironclad update`

```bash
ironclad update
```

Kalau kamu sudah di versi terbaru:

```
installed: 0.9.5
latest:    0.9.5
You are on the latest version.
```

Kalau ada yang lebih baru, ia menampilkan **apa yang berubah** dalam bahasa manusia,
bukan hash commit:

```
installed: 0.9.4
latest:    0.9.5
A newer version is available.

What changed since 0.9.4:
  1 change: 1 docs

  • three layers had the wrong first layer

What do you want to do?
  1) Install 0.9.5 now  (recommended)
  2) Stay on 0.9.4 for now  (nothing changes)
  3) Show me what changed
  4) Stop asking on this machine
Choose 1-4 [2]:
```

## Empat pilihan, dan apa akibatnya

| Pilihan | Yang terjadi | Aman? |
|---|---|---|
| **1) Pasang sekarang** | Menjalankan installer versi baru. Blok agent diganti di tempat, bukan ditumpuk. | Ya. `.agent/standards.md` yang sudah kamu isi tidak disentuh. |
| **2) Tetap di versi ini** | Tidak ada yang berubah. Pilihan diingat, jadi tidak ditanya lagi hari itu. | Ya. |
| **3) Lihat perubahannya** | Menampilkan daftar lagi, lalu kembali ke menu. | Ya, hanya membaca. |
| **4) Jangan tanya lagi** | Pemeriksaan dimatikan selamanya di mesin itu. | Ya. Nyalakan lagi dengan `ironclad update`. |

Default-nya **2** — kalau kamu hanya menekan Enter, tidak terjadi apa-apa.

## Kapan ia memeriksa

- **Paling sering sekali per 24 jam.** Hasilnya disimpan di `~/.ironclad/`.
- **Tidak pernah di dalam pipe atau CI.** Kalau tidak ada terminal, ia mencetak
  fakta lalu keluar — tidak menggantung menunggu jawaban.
- **Tidak pernah mengubah exit code `ironclad check`.** Gate tetap 0 atau 1, tidak
  peduli GitHub bisa dihubungi atau tidak.
- **Paling banyak satu baris.** Kalau ada versi baru, `ironclad check` menambahkan
  satu baris di akhir:

  ```
  Ironclad 0.9.5 is available (you have 0.9.4). Run `ironclad update`.
  ```

## Untuk CI dan skrip

```bash
ironclad update --check     # 0 = terbaru, 10 = ada versi lebih baru, 1 = gagal jaringan
ironclad update --notes     # cetak daftar perubahan saja
ironclad update --mute      # matikan pemeriksaan
```

`--check` sengaja memakai **10**, bukan 1, supaya bisa dibedakan dari "ada temuan
schema". Kalau kamu ingin CI gagal karena ketinggalan versi, tulis sendiri:

```yaml
- run: ironclad update --check || [ $? -ne 10 ]
```

## Kalau mesinmu tanpa internet

Pemeriksaan gagal dengan tenang: satu baris "tidak bisa menghubungi GitHub", lalu
selesai. Semua fitur lain — `check`, `init`, `drill` — tetap bekerja penuh secara
offline. Blok agent yang sudah tertanam juga tidak butuh jaringan.

## Kalau kamu memasang dari file, bukan dari tag

Pemeriksaan membandingkan versi di `SKILL.md` dengan tag rilis terbaru. Kalau kamu
memasang dari working tree yang versinya belum dirilis, ia akan menganggap versimu
lebih baru dari tag dan diam. Itu benar: tidak ada yang perlu diperbarui.
