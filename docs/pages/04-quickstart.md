---
title: Quickstart
slug: quickstart
group: Mulai
order: 4
summary: Lima menit dari nol sampai checker hijau di satu repo, tanpa mengganggu pekerjaan lain.
---

# Quickstart

Lima menit. Tidak ada langkah yang bisa dilewati tanpa akibat.

## 1. Pasang skill (30 detik)

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

## 2. Bootstrap repo (10 detik)

```bash
cd ~/proyek-kamu
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --project . --preset balanced
```

Atau, kalau skill sudah terpasang dan kamu mau lebih memilih lewat menu:

```bash
python3 ~/.agents/skills/ironclad/scripts/init_standards.py . --with-checker
```

Keduanya menulis berkas yang sama:

```
.agent/standards.md          aturan ber-ID, dibaca manusia dan agent
.agent/standards.yml         tingkat penegakan, dibaca checker dan CI
scripts/check_schema.py      linter
scripts/presets/*.yml        tiga preset
```

## 3. Commit (10 detik)

```bash
git add .agent scripts
git commit -m "chore: adopt ironclad standards"
```

> Langkah ini tidak opsional. Kalau `.agent/` tidak ikut commit, setiap anggota tim punya aturan sendiri lagi — tepat masalah yang mau kamu selesaikan.

## 4. Jalankan checker (10 detik)

```bash
python3 scripts/check_schema.py .
```

Yang kamu lihat, tergantung isi repo:

```
bad.sql:4: [DB-01] ERROR SQL/prisma enum column; use integer code + lookup table (see DB-03)
bad.sql:6: [DB-04] ERROR status stored as text (`stock_state`); use smallint code + lookup table

preset: balanced (.agent/standards.yml)
1 file(s), 2 error(s), 2 warning(s)
```

Exit code: `0` bersih, `1` ada error, `2` salah pakai.

## 5. Jangan langsung blokir CI

Repo lama akan punya ratusan temuan. Kalau kamu pasang sebagai gate sekarang, dalam sehari ada yang menghapusnya dari CI.

Mulai dari yang paling longgar:

```bash
python3 scripts/check_schema.py . --preset legacy-friendly   # semua warning, exit 0
```

Kalau hasilnya sudah bisa dicerna, naikkan:

```bash
python3 scripts/init_standards.py . --preset balanced --force
```

## 6. Pasang di CI

Gate **hanya file yang berubah**, bukan seluruh repo:

```yaml
- name: Gate changed schema files
  if: github.event_name == 'pull_request'
  run: |
    CHANGED=$(git diff --name-only --diff-filter=d origin/${{ github.base_ref }}...HEAD \
      | grep -E '\.(sql|php|prisma)$' || true)
    [ -z "$CHANGED" ] && exit 0
    python scripts/check_schema.py $CHANGED
```

## 7. Buktikan benar-benar bekerja

Jangan percaya "sudah dipasang". Tiga percobaan ini yang menentukan:

```bash
python3 scripts/check_schema.py examples/good.sql --preset strict; echo $?   # harus 0
python3 scripts/check_schema.py examples/bad.sql  --preset strict; echo $?   # harus 1
```

Lalu buat PR yang menambah kolom `enum` — CI harus merah. Kalau tidak merah, CI-nya yang salah, bukan checker-nya.

## Hasil akhir

```
repo/
├── .agent/
│   ├── standards.md      ← agent membaca ini sebelum menulis DDL
│   └── standards.yml     ← CI membaca ini untuk tahu apa yang memblokir
├── scripts/
│   ├── check_schema.py
│   └── presets/
└── schema/migrations/…   ← pekerjaan biasa
```
