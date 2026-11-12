---
title: Preset
slug: presets
group: Konsep
order: 11
summary: Tiga tingkat penegakan, satu default otomatis. Pilih sekali saat install, ubah kapan saja lewat satu baris di repo.
---

# Preset — guardrail yang bisa disetel

Masalah nyata sebuah linter perusahaan: repo lama punya ratusan pelanggaran, dan gate yang menyala di hari pertama akan dimatikan di hari yang sama. Preset ada supaya kamu bisa **mulai longgar, lalu mengencangkan** tanpa mengubah kode.

## Tiga preset

| Preset | Memblokir | Hanya warning | Untuk |
|---|---|---|---|
| `legacy-friendly` | — | semua | repo yang sudah punya utang teknis |
| `balanced` **(default)** | DB-01, DB-02, DB-04 | sisanya | pekerjaan produk normal |
| `strict` | semua | — | keuangan, kesehatan, sistem yang diaudit |

Angka nyata dari fixture yang sama (`examples/bad.sql`):

```
balanced           errors=3 warns=2
legacy-friendly    errors=0 warns=7
strict             errors=7 warns=0
```

## Default otomatis

Wizard memilih `balanced` lebih dulu dan menandainya:

```
Choose a preset [1]:
  1) balanced         Balanced — recommended default  (default)
  2) legacy-friendly  Legacy-friendly — brownfield
  3) strict           Strict — regulated
```

Kalau stdin bukan TTY — misalnya agent yang menjalankannya — tidak ada pertanyaan sama sekali:

```
$ printf '' | init_standards.py .
non-interactive: using preset 'balanced'
```

Ini penting: agent tidak boleh menggantung menunggu jawaban yang tidak akan datang.

## Memilih saat install

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --project . --preset strict
```

Atau lewat bootstrap:

```bash
python3 scripts/init_standards.py . --preset strict --with-checker
```

## Mengubah setelah install

Pilihanmu hidup di `.agent/standards.yml` **di dalam repo**, bukan di dalam skill. Tiga cara mengubahnya, semuanya sah:

**1. Tulis ulang dari preset:**

```bash
python3 scripts/init_standards.py . --preset strict --force
```

**2. Edit langsung — tujuh baris, bisa di-review di PR:**

```yaml
name: balanced
rules:
  DB-01: error      # enum dilarang
  DB-02: error      # magic number pada kolom status
  DB-03: warn       # status tanpa FK/CHECK
  DB-04: error      # label manusia disimpan sebagai status
  DB-05: warn       # boolean untuk konsep non-biner
  DB-06: warn       # uang sebagai float
  DB-07: warn       # timestamp tanpa zona waktu
exceptions: []
boolean_allowlist:
  - is_active
  - is_deleted
```

**3. Sekali jalan, tanpa mengubah berkas:**

```bash
python3 scripts/check_schema.py . --preset legacy-friendly
```

## Urutan adopsi yang tidak menyakitkan

| Tahap | Preset | Yang terjadi |
|---|---|---|
| Minggu 1 | `legacy-friendly` | semua dilaporkan, build tetap hijau |
| Minggu 2–3 | `balanced` + gate hanya file berubah | temuan baru diblokir, utang lama dibiarkan |
| Setelah baseline bersih | `strict` | semua memblokir |

Melewati tahap pertama adalah cara tercepat membuat tim membenci alat ini.

## Preset sendiri

Buat `presets/tim.yml`:

```yaml
name: tim
title: Aturan internal kita
rules:
  DB-01: error
  DB-02: error
  DB-03: error
  DB-04: error
  DB-05: off        # proyek ini memang penuh flag biner
  DB-06: error
  DB-07: warn
exceptions:
  - migrations/2023_legacy_import.sql
boolean_allowlist:
  - is_active
  - is_deleted
```

Lalu:

```bash
python3 scripts/check_schema.py . --config presets/tim.yml
```

> **`off` bukan tombol bisu.** Mematikan satu aturan adalah keputusan yang di-review dan dicatat, bukan jalan pintas agar build hijau. Kalau alasannya tidak bisa ditulis dalam satu baris PR, berarti aturannya belum perlu dimatikan.

## Prioritas pembacaan

```
--config  >  --preset  >  .agent/standards.yml  >  built-in balanced
```

Yang paling kanan adalah jaring pengaman: kalau semua berkas hilang, checker tetap jalan dengan `balanced`, bukan crash.
