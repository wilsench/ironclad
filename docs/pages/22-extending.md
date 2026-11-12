---
title: Memperluas
slug: extending
group: Referensi
order: 22
summary: Menambah domain aturan baru — API, keamanan, performa — tanpa menyentuh aturan database yang sudah ada.
---

# Memperluas

Aturan database adalah contoh yang sudah jadi. Bentuk yang sama dipakai untuk domain lain: ID berawalan, kebijakan di repo, pemeriksaan yang bisa diotomatiskan.

## Langkah 1 — Pilih awalan dan nomor

| Awalan | Domain |
|---|---|
| `DB-` | database & schema |
| `API-` | kontrak HTTP: versi, bentuk error, pagination |
| `SEC-` | rahasia, otorisasi, validasi input |
| `PERF-` | query N+1, indeks, batas ukuran respons |

Nomor tidak pernah dipakai ulang, walau aturannya dihapus. Kalau `DB-03` dicabut, nomor itu pensiun — bukan diberikan ke aturan baru, karena komentar review lama akan menunjuk aturan yang salah.

## Langkah 2 — Tambahkan ke kebijakan repo

`.agent/standards.md`:

```markdown
### API-01 — Every list endpoint is paginated

An unpaginated list is a production incident waiting for a data set large enough.

    ✗  GET /orders                → 200 [{...}]  (all rows)
    ✓  GET /orders?cursor=…       → 200 {data, next_cursor}
```

Format yang terbukti berguna: **satu paragraf alasan**, lalu contoh salah/benar. Agent memakai contoh, reviewer memakai alasan.

## Langkah 3 — Tambahkan ke config presets

`assets/presets/balanced.yml`:

```yaml
rules:
  API-01: error
  API-02: warn
```

Tanpa entri di config, aturan tetap ada di dokumen tapi tidak pernah diperiksa — dan aturan yang tidak diperiksa akan dilupakan.

## Langkah 4 — Tulis pemeriksanya

Dua pilihan, dari yang paling murah:

**A. Regex, di checker yang sudah ada.** Cocok untuk pola sintaksis (`app.get('/orders',` tanpa `.limit(`).

**B. Skrip terpisah.** Cocok kalau butuh parsing nyata. Simpan di `scripts/` skill, panggil dari CI yang sama:

```bash
python3 scripts/check_schema.py . --json
python3 scripts/check_api.py . --json
```

Jangan memaksakan semuanya ke satu skrip. Dua checker kecil yang jelas lebih baik daripada satu skrip yang menebak-nebak.

## Langkah 5 — Uji dengan fixture

Setiap aturan butuh dua berkas: satu yang harus gagal, satu yang harus lolos.

```
examples/good.sql      → exit 0 di semua preset
examples/bad.sql       → exit 1 di balanced & strict
```

Tanpa keduanya, kamu tidak tahu apakah aturannya bekerja atau hanya kebetulan tidak menemukan apa pun. CI repo ini menguji keduanya setiap push.

## Contoh nyata: aturan keamanan

```markdown
### SEC-01 — No secrets in tracked files

    ✗  const API_KEY = "sk-live-..."
    ✓  const API_KEY = process.env.API_KEY
```

Pemeriksa sederhana: regex terhadap pola kunci populer, dilewati untuk `.env.example` dan fixture. Ini menangkap kesalahan yang paling mahal dan paling sering — dan tidak butuh AST.

## Batas yang perlu diakui

Semakin jauh dari sintaksis, semakin lemah pemeriksaan otomatis:

| Aturan | Bisa diperiksa mesin? |
|---|---|
| `enum` di schema | Ya, andal |
| Uang sebagai float | Ya, andal |
| Endpoint tanpa pagination | Sebagian — hanya pola yang dikenal |
| "Error response konsisten" | Sulit; butuh skema OpenAPI |
| "Arsitektur layer benar" | Tidak. Ini tugas review, bukan linter |

Kalau sebuah aturan tidak bisa diperiksa, itu tidak berarti aturannya buruk — hanya berarti penegakannya manusia. Tulis tetap di `.agent/standards.md`, tandai sebagai *review-only*, supaya agent tetap membacanya sebagai niat tim.
