---
title: Pasang di agent
slug: install
group: Mulai
order: 3
summary: Satu perintah, tanpa pertanyaan. Lalu tiga kata perintah untuk memakainya. Tanpa Python.
---

# Pasang di agent kamu

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash
```

Itu seluruh instalasinya. Tidak ada pertanyaan, tidak ada Python, tidak ada menu.

Yang dilakukannya:

1. menaruh skill di `~/.agents/skills/ironclad/` — folder yang dibaca Codex, Cursor, opencode, dan Antigravity
2. menambahkan perintah `ironclad` ke `~/.local/bin/`
3. berhenti. Repo kamu belum disentuh.

Kalau `~/.local/bin` belum ada di `PATH`, installer memberi tahu. Tambahkan satu baris ke `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Setelah itu, tiga perintah

```bash
ironclad check          # nilai schema repo ini, tidak menulis apa pun
ironclad init           # jadikan permanen: .agent/ + scripts/
ironclad preset strict  # ganti tingkat penegakan kapan saja
```

`check` bisa dipakai langsung setelah install, tanpa `init` — ia memakai preset bawaan (`balanced`) sampai repo punya `.agent/standards.yml` sendiri.

## Kenapa tidak pakai Python untuk install

Installer-nya bash + curl. Python 3.8+ hanya dibutuhkan untuk **menjalankan** checker, dan `ironclad check` sudah memanggilnya untuk kamu.

Kalau mesin kamu belum punya Python, `ironclad init` tetap berhasil — yang belum jalan hanya `check`/CI. Pasang Python kapan pun kamu siap memasang gatenya.

## Agent lain

Default-nya `~/.agents/skills`. Untuk agent yang punya folder sendiri:

```bash
# Claude Code
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target claude

# Hermes
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target hermes

# opencode (native)
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target opencode

# Antigravity global
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --target gemini

# semua yang terpasang di mesin ini
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --all
```

| Agent | Folder |
|---|---|
| Codex | `.agents/skills/` **di dalam repo** — pakai `--dir .agents/skills` |
| Cursor | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| Hermes | `~/.hermes/skills/` |
| opencode | `~/.config/opencode/skills/`, juga membaca `~/.agents/skills/` |
| Antigravity | `~/.gemini/config/skills/` (global), `.agents/skills/` (workspace) |

> **Codex tidak punya folder skill global.** Menurut dokumentasi OpenAI, Codex membaca `$CWD/.agents/skills` dan `$CWD/../.agents/skills`. Kalau kamu pengguna Codex, pasang di dalam repo supaya ikut commit:
>
> ```bash
> curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --dir .agents/skills
> ```

## Kalau ingin aturannya ikut repo

Ini yang membuat satu tim memakai aturan yang sama — skill ikut git, bukan cuma ada di laptop satu orang:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --dir .agents/skills
git add .agents/skills/ironclad && git commit -m "chore: add ironclad skill"
```

## CI: lewati semua pertanyaan

Tidak ada pertanyaan sejak awal, jadi tidak ada yang perlu dilewati. Untuk pipeline yang ingin semuanya sekaligus:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh \
  | bash -s -- --target agents --project . --preset legacy-friendly
```

## Mencopot

Ada dua hal yang bisa dicopot, dan keduanya berbeda pemiliknya. Pahami ini dulu supaya tidak menghapus aturan tim hanya karena ingin mencoba ulang.

**1. Skill-nya** — ada di folder agent kamu, bukan di repo. Satu perintah, membersihkan semua agent sekaligus:

```bash
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --uninstall
```

Yang dihapus: `~/.agents/skills/ironclad`, `~/.claude/skills/ironclad`, `~/.hermes/skills/ironclad`, `~/.gemini/config/skills/ironclad`, `~/.config/opencode/skills/ironclad`, dan perintah `~/.local/bin/ironclad`. Yang tidak ada akan dilewati, bukan error.

**2. Aturan proyek** — `.agent/standards.{md,yml}`, `scripts/check_schema.py`, `scripts/presets/`. Ini **keputusan repo**, bukan milik installer, jadi secara default ia dibiarkan. Kalau memang mau dibuang dari disk:

```bash
cd repo-kamu
curl -fsSL https://wilsench.my.id/ironclad/install.sh | bash -s -- --uninstall --purge
```

Kalau berkas itu sudah pernah di-commit, purge hanya menghapus dari disk — Git masih melacaknya. Selesaikan dengan commit:

```bash
git rm -r .agent scripts
git commit -m "chore: drop ironclad standards"
```

> **Jangan copot `.agent/` hanya karena ingin upgrade skill.** Aturan tim yang sudah disepakati bukan sampah instalasi. `--uninstall` tanpa `--purge` sengaja mempertahankannya.

### Kalau dulu memasang lewat `hermes skills install`

Itu jalur berbeda dan tidak dikenal oleh `install.sh`. Copot lewat Hermes sendiri:

```bash
hermes skills uninstall ironclad
```

Cek sisa pemasangan di mana saja:

```bash
ls -d ~/.agents/skills/ironclad ~/.claude/skills/ironclad ~/.hermes/skills/ironclad \
      ~/.gemini/config/skills/ironclad ~/.config/opencode/skills/ironclad 2>/dev/null
command -v ironclad
```

Kalau kedua perintah di atas tidak menghasilkan apa pun, sudah bersih.
