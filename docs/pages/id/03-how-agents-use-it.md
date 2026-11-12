---
title: Cara agent memakainya
slug: how-agents-use-it
group: Mulai
order: 3
summary: Skill aktif otomatis tanpa perintah, tapi hanya kalau deskripsinya cocok dengan tugas. Ini cara kerjanya dan cara memaksanya.
---

# Cara agent memakainya

Jawaban singkat: **otomatis, tanpa kamu memerintah.** Tapi ada satu syarat — dan kalau syarat itu tidak terpenuhi, skill-nya diam saja.

## Yang terjadi setiap percakapan

Semua agent yang mendukung Agent Skills memakai pola **progressive disclosure**:

1. **Discovery** — setiap turn, agent melihat daftar skill yang terpasang: nama + deskripsi. Bukan isi lengkapnya.
2. **Activation** — kalau deskripsinya cocok dengan tugasmu, agent membaca `SKILL.md` penuh.
3. **Execution** — agent mengikuti prosedurnya.

Artinya: skill ini **tidak** "menjalankan segalanya". Ia menunggu ada pekerjaan yang cocok. Ini disengaja — kalau setiap skill dimuat penuh setiap turn, konteks habis sebelum kamu bertanya apa pun.

Deskripsi Ironclad sengaja dibuat pendek dan tajam, karena itulah satu-satunya yang dilihat agent saat memilih:

```
Enforce team engineering standards with presets.
```

## Kapan ia aktif sendiri

Agent akan memuatnya ketika tugasmu menyentuh:

- membuat tabel, migration, atau schema baru
- mengubah kolom status
- review PR yang berisi DDL
- pertanyaan "boleh pakai enum?" / "bagaimana menambah status baru?"

## Kapan ia diam

- kamu bertanya soal CSS, deploy, atau bug runtime yang tidak menyentuh schema
- repo belum punya `.agent/standards.md`, dan tugasnya bukan membuat schema

Kalau kamu ingin ia selalu ikut, sebut namanya:

```
pakai skill ironclad untuk migration ini
```

## Cara memaksa per agent

| Agent | Panggil eksplisit |
|---|---|
| **Claude Code** | `> gunakan skill ironclad` atau `/ironclad` bila didaftarkan sebagai slash command |
| **Codex CLI** | `$ironclad` untuk menyebut skill, atau `/skills` untuk melihat daftarnya |
| **opencode** | `skill({ name: "ironclad" })` lewat tool `skill`; daftar muncul di deskripsi tool |
| **Antigravity** | `/<nama-skill>` di kotak pesan |
| **Cursor** | sebut namanya di prompt; Cursor membaca `.agents/skills` |

## Yang tidak boleh diandalkan

**Skill bukan penegak.** Model bisa melewati instruksi — itu sifat model, bukan bug skill. Yang benar-benar menahan dua puluh programmer adalah checker di CI:

```bash
python3 scripts/check_schema.py . --json   # exit 1 = build gagal
```

Karena itu ada tiga lapis, bukan satu. Kalau kamu hanya memasang skill tanpa checker, kamu punya dokumentasi yang bagus dan tidak ada jaminan.

## Kalau agent mengabaikan skill

Urutan diagnosis, dari yang paling sering:

1. **Deskripsi tidak cocok.** Agent memilih berdasarkan `description`. Kalau tugasmu "menambah kolom", dan deskripsinya tidak menyebut schema, ia tidak akan memuatnya.
2. **Skill tidak terdeteksi.** Cek lokasi: `ls ~/.agents/skills/ironclad/SKILL.md`. Nama file harus `SKILL.md`, huruf besar.
3. **Belum restart.** Codex, Antigravity, dan opencode membaca daftar skill saat start.
4. **Kalah oleh skill lain.** Kalau ada dua skill dengan `name: ironclad`, agent bisa memilih yang salah. Hapus duplikatnya.
5. **Konteks penuh.** Codex membatasi daftar skill jadi ~2% context window; kalau kamu punya 50 skill, sebagian disembunyikan. Kurangi skill yang tidak dipakai.

## Apa yang terjadi setelah aktif

Agent membaca `.agent/standards.md` sebelum menulis DDL, mengklasifikasikan tiap kolom status, menulis migrasi sesuai aturan, menjalankan checker, lalu melaporkan penyimpangan dengan ID aturan.

Kalau `.agent/standards.md` tidak ada, ia menjalankan `ironclad init` (preset `balanced`). Perintah itu tidak pernah bertanya, jadi agent tidak akan menggantung menunggu jawaban yang tidak akan datang.
