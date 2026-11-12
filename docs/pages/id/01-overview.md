---
title: Ikhtisar
slug: overview
group: Mulai
order: 1
summary: Ironclad memberi setiap AI coding agent satu rulebook yang sama, plus linter yang menegakkannya di CI.
---

# Ironclad

Aturan engineering tim, ditegakkan mesin — bukan ingatan.

Sepuluh orang memakai AI agent untuk membangun aplikasi yang sama. Tidak ada yang membaca wiki yang sama. Enam bulan kemudian schema-nya jadi museum selera masing-masing: `enum` di satu tabel, `varchar` status di tabel lain, `boolean` untuk konsep yang punya empat keadaan.

Ironclad memasang tiga lapis untuk mencegahnya:

| Lapis | Berkas | Ditegakkan oleh |
|---|---|---|
| **Kebijakan** — apa yang tim mau | `.agent/standards.md` di repo kamu | Review + agent |
| **Prosedur** — bagaimana agent memutuskan | `SKILL.md` + `references/` | Agent itu sendiri |
| **Mekanisme** — apa yang bisa diperiksa mesin | `scripts/check_schema.py` | CI / pre-commit |

Skill saja hanya nasihat; model bisa mengabaikannya. Checker-nya yang membuat standar bertahan lintas dua puluh programmer.

## Pasang dalam satu baris

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

Itu memasang skill ke `~/.agents/skills/ironclad` — dibaca Codex, Cursor, opencode, dan Antigravity. Untuk agent lain:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target claude
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target hermes
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --all
```

[Tabel lengkap per agent →](/install/)

## Lalu di repo kamu

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --project .
```

Menulis `.agent/standards.md`, `.agent/standards.yml`, `scripts/check_schema.py`, dan `scripts/presets/`. Commit semuanya, atau anggota tim berikutnya mendapat rulebook yang berbeda.

> **Python tidak diperlukan untuk memasang atau menulis kebijakan.** Installer-nya bash + curl. Python 3.8+ hanya dibutuhkan saat menjalankan checker — dan checker itu opsional kalau kamu hanya ingin aturannya dibaca agent.

## Kenapa kode integer, bukan `enum`

`enum` memaksa perubahan nilai lewat migrasi schema. Di MySQL, menambah satu nilai berarti `ALTER TABLE`, dan pada tabel besar itu mengunci. Sementara status bisnis selalu tumbuh: "dijadwalkan", "menunggu konfirmasi", "ditunda karena cuaca", "dibatalkan sebagian".

Kode integer dengan lookup table memberi kebebasan itu tanpa kehilangan integritas:

```sql
CREATE TABLE ref_stock_status (
  code   smallint PRIMARY KEY,
  label  text NOT NULL
);
INSERT INTO ref_stock_status VALUES (88,'Kosong'),(89,'Menipis'),(90,'Tersedia');

CREATE TABLE product_stock (
  product_id  bigint NOT NULL REFERENCES products(id),
  status_code smallint NOT NULL DEFAULT 88 REFERENCES ref_stock_status(code)
);
```

Kode `88` itu sah — bukan harus berurutan dari nol. Yang membuatnya aman hanya dua hal: **terdaftar di lookup table** (sehingga `87` ditolak database), dan **konstanta bernama di kode aplikasi** (bukan `if (status === 88)` yang berserakan).

[Aturan lengkapnya →](/rules/)

## Batasan yang perlu kamu tahu

- **Checker berbasis regex**, bukan parser SQL. Ia membaca DDL `.sql`, migration Laravel, dan `.prisma`. Ia tidak melihat query builder ORM atau SQL yang dirangkai saat runtime.
- **Tidak ada auto-update.** `hermes skills update` memakai URL saat install; agent lain perlu memasang ulang. Belum ada changelog bertanda versi.
- **Tiga preset, bukan konfigurasi bebas.** Kamu bisa menulis preset sendiri, tapi tidak ada GUI.
- **Cocok untuk database-centric rule**, dan sekarang juga PR/API lewat `references/extending.md`. Bukan linter sempurna.

## Langkah berikutnya

1. [Pasang di agent kamu](/install/) — Hermes, Claude Code, Codex, Cursor, opencode, Antigravity
2. [Pahami cara agent memakainya](/how-agents-use-it/) — otomatis atau dipanggil manual
3. [Quickstart 5 menit](/quickstart/) di satu repo
4. [Pilih tingkat penegakan](/presets/) — jangan langsung `strict`
