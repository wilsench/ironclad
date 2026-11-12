---
title: Pasang di agent
slug: install
group: Mulai
order: 2
summary: Satu perintah curl untuk Hermes, Claude Code, Codex, Cursor, opencode, dan Antigravity. Tanpa Python.
---

# Pasang di agent kamu

Satu installer, enam target. Formatnya [Agent Skills](https://agentskills.io) — satu folder berisi `SKILL.md` — jadi agent apa pun yang mendukung standar itu bisa memakainya.

## Perintah dasar

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

Tanpa argumen, ia memasang ke `~/.agents/skills/ironclad/`, lokasi yang dibaca **Codex, Cursor, opencode, dan Antigravity**.

> **Tidak perlu Python untuk memasang.** Installer-nya bash + curl. Python 3.8+ baru dibutuhkan kalau kamu menjalankan checker.

## Per agent

| Agent | Perintah | Folder tujuan |
|---|---|---|
| **Semua yang ada di mesin** | `… \| bash -s -- --all` | semua di bawah yang terdeteksi |
| **Codex / Cursor** | `… \| bash` atau `--target agents` | `~/.agents/skills/` |
| **Claude Code** | `… \| bash -s -- --target claude` | `~/.claude/skills/` |
| **Hermes** | `… \| bash -s -- --target hermes` | `~/.hermes/skills/` |
| **opencode** | `… \| bash -s -- --target opencode` | `~/.config/opencode/skills/` |
| **Antigravity (global)** | `… \| bash -s -- --target gemini` | `~/.gemini/config/skills/` |
| **Folder bebas** | `… \| bash -s -- --dir /path/to/skills` | apa pun |

`--all` hanya menyentuh agent yang direktorinya sudah ada, supaya tidak membuat folder nyasar.

## Antigravity: perhatikan cakupannya

Antigravity membaca dua lokasi:

- `<workspace>/.agents/skills/<nama>/` — per proyek, ikut git, dibagikan ke tim
- `~/.gemini/config/skills/<nama>/` — global, semua workspace

Kalau kamu ingin aturannya ikut repo (dan dibaca semua orang), pasang di level workspace:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --dir .agents/skills
git add .agents/skills/ironclad && git commit -m "chore: add ironclad skill"
```

## opencode

opencode membaca empat lokasi, dan yang paling portabel adalah `.agents/skills/`:

- `.opencode/skills/<nama>/SKILL.md` (native)
- `~/.config/opencode/skills/<nama>/SKILL.md`
- `.claude/skills/…` dan `~/.claude/skills/…` (kompatibel Claude)
- `.agents/skills/…` dan `~/.agents/skills/…` (kompatibel agent generik)

Karena installer default-nya `~/.agents/skills`, opencode langsung menemukannya. opencode juga punya izin per-skill di `opencode.json`:

```json
{
  "permission": {
    "skill": { "ironclad": "allow", "internal-*": "deny" }
  }
}
```

## Hermes

```bash
hermes skills install wilsench/ironclad/skills/ironclad
```

Perintah ini memakai hub Hermes (butuh repo GitHub publik). Kalau repo belum ada, pakai installer curl di atas — hasilnya sama, hanya tanpa pencatatan versi di hub.

## Claude Code

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target claude
```

Untuk dipakai bersama tim, commit ke repo dan pakai `/plugin` atau salin ke `.claude/skills/`:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --dir .claude/skills
```

## Cek hasilnya

```bash
ls ~/.agents/skills/ironclad
# SKILL.md  assets/  references/  scripts/  templates/
```

Kalau agent tidak menemukannya, penyebab paling umum:

1. nama file bukan `SKILL.md` (huruf besar semua)
2. frontmatter tidak punya `name` dan `description`
3. agent perlu restart — daftar skill dibaca saat start, bukan setiap pesan
4. nama skill bertabrakan dengan skill lain di lokasi berbeda

## Mencabut

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --uninstall
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target claude --uninstall
```

Hanya menghapus folder `ironclad`. Skill lain tidak disentuh.

## Opsi lain

| Opsi | Arti |
|---|---|
| `--project PATH` | sekalian menulis `.agent/` + checker ke repo itu |
| `--preset NAME` | `balanced` (default) · `strict` · `legacy-friendly` |
| `--policy-only` | tulis kebijakan saja, tanpa checker |
| `--ref BRANCH` | ambil dari branch/tag lain |
| `--uninstall` | hapus |

Installer mengambil dari GitHub lebih dulu; kalau repo belum terbit atau sedang kena rate-limit, ia jatuh ke mirror `wilsench.my.id/ironclad/pkg`. Kamu tidak perlu mengatur apa pun.
