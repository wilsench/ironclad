---
title: Cara pakai tanpa command
slug: no-commands
group: Mulai
order: 6
summary: Tiga langkah. Setelah itu kamu tidak menjalankan perintah apa pun — agent yang bertanya dan mengerjakannya.
---

# Cara pakai tanpa command

Kalau kamu tidak ingin mengingat perintah, ini jalurnya. Tiga langkah, sekali,
lalu selesai.

## 1. Pasang

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

## 2. Selesai — benar-benar selesai

Setelah langkah 1, **tidak ada langkah kedua**. Installer sudah menulis aturan ke
konfigurasi global tiap agent yang ada di mesinmu:

```
created  .claude/CLAUDE.md     (Claude Code)
created  .codex/AGENTS.md      (Codex)
created  .gemini/GEMINI.md     (Gemini CLI)
```

Itu yang dibaca agent **di awal setiap sesi, di repo mana pun** — tanpa kamu
menjalankan apa pun.

## 3. Opsional: kunci aturan per repo

Kalau kamu ingin aturan itu ikut git (supaya seluruh tim dan CI memakai jawaban
yang sama), jalankan sekali di repo:

```bash
cd repo-kamu
ironclad init
```

Ia menanyakan satu hal:

```
How strict should this repo be?
  1) balanced  (default) — enum and text status block, the rest warn
  2) strict    — everything blocks; use for new or clean repos
  3) legacy-friendly — everything warns; use for an old repo with debt
Choose 1-3 [1]:
```

Lalu menulis:

```
wrote   .agent/standards.yml      ← aturan repo ini (bisa di-review di PR)
wrote   .agent/standards.md       ← penjelasan untuk manusia dan agent
wrote   scripts/check_schema.py   ← pemeriksa, bisa dipakai CI

  created        AGENTS.md                             (Codex, opencode, dll)
  created        CLAUDE.md                             (Claude Code)
  created        GEMINI.md                             (Gemini CLI)
  created        .cursor/rules/ironclad.mdc            (Cursor)
  created        .github/copilot-instructions.md       (GitHub Copilot)
```

Lalu commit:

```bash
git add .agent scripts AGENTS.md CLAUDE.md GEMINI.md .cursor .github
git commit -m "chore: adopt ironclad standards"
```

Yang terakhir itu kuncinya. Agent **membaca berkas-berkas itu sendiri** setiap
kali kamu buka repo — tanpa kamu menyuruh, tanpa slash command, tanpa skill yang
harus diaktifkan.

Tanpa `ironclad init`, agent tetap bertanya dan tetap memakai default `balanced`
dari skill. Yang hilang cuma dua: aturannya tidak ikut git, dan CI tidak punya
berkas untuk dijalankan.

## 4. Kerjakan seperti biasa

Buka agent, minta fitur apa pun yang menyentuh database. Yang terjadi:

> **Kamu:** tolong tambahkan fitur pesanan: tabel orders dengan status, total, waktu dibuat
>
> **Agent:** Ironclad: aturannya ditegakkan sambil kita menulis, atau diperiksa di akhir?

Pilih salah satu, dan ia lanjut:

- **sambil** — aturan diterapkan saat menulis, `ironclad check` dijalankan pada
  tiap berkas sebelum dilaporkan selesai.
- **di akhir** — ia menulis dulu, lalu memeriksa sebelum menutup pekerjaan dan
  memperbaiki apa pun yang dilaporkan.

Kamu tidak mengetik perintah apa pun. Agent yang menjalankannya.

## Kenapa ini bekerja

Skill hanya dimuat kalau agent menilai ia relevan — dan penilaian itu sering
terlambat: kode sudah ditulis sebelum skill dibaca. Berkas seperti `AGENTS.md`
dan `CLAUDE.md` berbeda: itu dibaca **setiap sesi, di awal**, sebelum agent
menjawab apa pun.

Isi yang ditanamkan ke berkas itu:

- kapan aturan berlaku (setiap perubahan schema, termasuk Laravel dan Prisma)
- pertanyaan yang harus diajukan lebih dulu, dan pilihannya
- delapan aturan dalam satu paragraf
- larangan membungkam checker demi build hijau
- kewajiban menyebut ID aturan saat menyimpang

## Kalau kamu ingin memilih preset tanpa ditanya

```bash
ironclad init strict
ironclad init legacy-friendly
```

Defaultnya `balanced`, dan agent akan tetap menanyakan preset kalau `.agent/`
belum ada — bukan memilih diam-diam.

## Kalau tidak ingin menyentuh AGENTS.md

```bash
ironclad init --no-agent-files
```

Atau saat install: `curl ... | bash -s -- --no-agent-files`.

Tanpa blok itu, agent hanya tahu aturannya kalau ia memuat skill — jadi kamu
kembali ke dunia yang butuh command. Pilihan ini ada untuk repo yang sudah punya
`AGENTS.md` sendiri dan tidak mau dicampuri.

## Mencopot blok itu saja

```bash
ironclad attach . --remove
```

Yang dihapus hanya blok bertanda `<!-- ironclad:begin v1 -->`. Tulisanmu sendiri
di berkas yang sama tidak disentuh. Sudah diuji: `CLAUDE.md` yang berisi aturan
kantor tetap utuh setelah blok Ironclad dicabut.
