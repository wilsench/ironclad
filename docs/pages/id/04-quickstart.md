---
title: Quickstart
slug: quickstart
group: Mulai
order: 4
summary: Dua menit dari nol sampai checker hijau di satu repo, tanpa mengganggu pekerjaan lain.
---

# Quickstart

Dua menit. Tidak ada pertanyaan yang harus dijawab, tidak ada berkas yang harus
diedit tangan.

## 1. Pasang

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

Selesai. Skill ada di `~/.agents/skills/ironclad/`, perintah `ironclad` ada di
`~/.local/bin/`.

## 2. Lihat dulu, jangan ubah apa pun

```bash
cd repo-kamu
ironclad check
```

Ini hanya membaca. Keluarannya seperti ini:

```
bad.sql:4: [DB-01] ERROR SQL/prisma enum column; use integer code + lookup table (see DB-03)
bad.sql:6: [DB-04] ERROR status stored as text (`stock_state`); use smallint code + lookup table

preset: balanced (preset:balanced)
1 file(s), 2 error(s), 2 warning(s)
```

Kalau repo kamu besar, jangan panik melihat jumlahnya. Itu gunanya langkah 4.

## 3. Jadikan permanen

```bash
ironclad init
```

Menulis empat hal, semuanya untuk di-commit:

```
wrote   .agent/standards.yml (preset: balanced)
wrote   .agent/standards.md
wrote   scripts/check_schema.py + scripts/presets/
```

```bash
git add .agent scripts
git commit -m "chore: adopt ironclad standards"
```

Sejak commit itu, agent membaca `.agent/standards.md` sebelum menulis DDL, dan CI
membaca `.agent/standards.yml` untuk memutuskan apa yang memblokir. Satu sumber,
dua pembaca.

## 4. Pilih tingkat penegakan yang tidak membuat tim matikan CI

Ini bagian yang paling sering dilewatkan orang, dan penyebab utama alat seperti
ini dicabut dalam seminggu.

| Repo kamu | Mulai dari | Kenapa |
|---|---|---|
| repo baru, atau sudah bersih | `strict` | semua memblokir, tidak ada utang |
| repo jalan, utang wajar | `balanced` (default) | enum & status-teks memblokir, sisanya warning |
| repo tua, ratusan temuan | `legacy-friendly` | semua warning, build tetap hijau |

```bash
ironclad preset legacy-friendly   # repo tua: pasang dulu, bersihkan pelan-pelan
ironclad preset balanced          # setelah baseline bersih
ironclad preset strict            # setelah tidak ada warning tersisa
```

Naik satu tingkat setelah jumlah temuan turun, bukan setelah tanggal tertentu.

## 5. Buktikan gate-nya benar-benar bekerja

Jangan percaya tampilan hijau. Uji tiga hal:

```bash
ironclad check examples/good.sql   # harus exit 0
ironclad check examples/bad.sql    # harus exit 1
```

Lalu buka PR yang menambah satu kolom `enum` — PR itu harus merah di GitHub.
Kalau tidak merah, CI-nya belum benar, bukan checkernya.

## Selesai

Yang tersisa hanya kebiasaan: `ironclad check` sebelum commit, dan biarkan CI
menjalankan hal yang sama pada setiap PR.

Kalau ada yang tidak berjalan seperti di halaman ini, lihat
[Troubleshooting](/troubleshooting/) — disusun dari gejala, bukan dari teori.
