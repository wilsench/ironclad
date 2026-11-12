# Publish ke GitHub

Repo ini sudah git-committed dan siap push. Pilih satu dari tiga cara.

## Cara A — kamu push sendiri (paling aman, tanpa kasih token)

**1. Bikin repo kosong di GitHub**

<https://github.com/new>

- Repository name: `company-standards-skill`
- Visibility: **Public** (wajib kalau orang lain mau `hermes skills install` tanpa token)
- **Jangan** centang "Add a README", ".gitignore", atau license — repo harus benar-benar kosong.

**2. Ambil paketnya dari VPS** (salah satu)

```bash
# di VPS
tar -czf /root/company-standards-skill.tar.gz -C /root/projects company-standards-skill
# lalu ambil /root/company-standards-skill.tar.gz lewat scp / SFTP / MEDIA
```

**3. Di komputer kamu**

```bash
tar -xzf company-standards-skill.tar.gz
cd company-standards-skill

./scripts/set-repo-owner.sh <username-kamu>
git add -A && git commit -m "docs: point install URLs at <username>"

git remote add origin https://github.com/<username>/company-standards-skill.git
git push -u origin main
```

**4. Cek hasilnya**

```bash
hermes skills install <username>/company-standards-skill/skills/company-engineering-standards
```

## Cara B — saya push (butuh token)

**1. Bikin fine-grained PAT**

<https://github.com/settings/tokens?type=beta>

| Field | Isi |
|---|---|
| Token name | `hermes-skill-push` |
| Expiration | 7 days (cukup untuk sekali push) |
| Repository access | **Only select repositories** → `company-standards-skill` |
| Permissions → Repository → **Contents** | **Read and write** |
| Permissions → Repository → **Metadata** | Read (otomatis) |

Jangan centang apa pun lagi. Jangan pakai classic token dengan scope `repo` penuh — itu memberi akses ke semua repo kamu.

**2. Taruh di `.env`, jangan di chat**

```bash
echo 'GITHUB_TOKEN=github_pat_xxxxxxxx' >> ~/.hermes/.env
```

Di VPS: `ssh root@43.156.111.169` lalu jalankan perintah di atas di sana.

**3. Bilang "sudah, push"** — saya baca dari `.env`, push, ganti URL, lalu tes install.

Saya tidak akan pernah menampilkan isi token itu di output.

**4. Setelah selesai** — hapus lagi:

```bash
sed -i '/^GITHUB_TOKEN=/d' ~/.hermes/.env
```

## Cara C — upload lewat web GitHub (tanpa git, tanpa token)

Cocok kalau kamu cuma mau cepat dan tidak butuh CI.

1. Bikin repo kosong seperti Cara A.
2. Buka `https://github.com/<username>/company-standards-skill/upload/main`
3. Drag seluruh isi folder `company-standards-skill` (kecuali `.git/`)
4. Commit.

Kekurangan: `.github/workflows/` kadang perlu izin workflow saat commit pertama; `.gitignore` dan struktur folder harus ikut ter-upload apa adanya (drag folder, bukan file satu-satu).

---

## Setelah ter-push: yang perlu dicek

```bash
# 1. SKILL.md bisa diakses publik
curl -sI https://raw.githubusercontent.com/<owner>/company-standards-skill/main/skills/company-engineering-standards/SKILL.md | head -1

# 2. Install lewat Hermes
hermes skills install <owner>/company-standards-skill/skills/company-engineering-standards

# 3. Install lewat script (agent lain)
curl -fsSL https://raw.githubusercontent.com/<owner>/company-standards-skill/main/install.sh | bash
```

Kalau langkah 1 balas `404`, berarti path atau nama branch salah — cek `main` vs `master`.

## Kalau mau diperbarui orang lain otomatis

`hermes skills update` memakai URL yang tercatat saat install. Karena install-nya dari GitHub, update ikut repo — asal orang itu tidak mengedit skill-nya secara lokal (kalau diedit, Hermes sengaja melewatinya supaya perubahan mereka tidak tertimpa).

## Hal yang sering bikin gagal

| Gejala | Penyebab |
|---|---|
| `404` saat install | Repo private, atau nama branch bukan `main` |
| `Could not fetch ... from any source` | Username/repo salah, atau file belum ada di branch itu |
| Install jalan tapi tanpa `scripts/` | File pendukung tidak ter-upload — cek `skills/company-engineering-standards/scripts/` ada di repo |
| CI merah | `scripts/check_schema.py` belum ada di root repo — workflow mengasumsikan sudah dijalankan `init_standards.py --with-checker` |
