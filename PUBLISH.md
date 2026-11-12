# Dari sini ke online — langkah demi langkah

Ada dua hal berbeda yang orang maksud dengan "online". Selesaikan sesuai kebutuhan.

| Yang mau online | Status sekarang |
|---|---|
| Halaman demo / dokumentasi | **Sudah online** → https://saku.wilsench.my.id/demo/ironclad/ |
| Bisa di-install orang lewat `hermes skills install` | **Belum** — butuh repo GitHub publik |

Yang kedua butuh GitHub karena `hermes skills install` mengambil file dari URL publik, bukan dari VPS ini.

---

# BAGIAN 1 — Upload ke GitHub

Pilih **satu** cara. Cara A paling saya rekomendasikan: kamu pegang kendali penuh, tidak ada token yang berpindah tangan.

## Cara A — push dari komputermu sendiri

### Langkah 1. Bikin repo kosong di GitHub

Buka <https://github.com/new>

- **Repository name**: `ironclad`
- **Description**: `Engineering standards for AI coding agents — policy, procedure, and a linter.`
- **Visibility**: **Public**
  Kalau Private, tidak ada orang lain yang bisa install. Boleh diganti belakangan di Settings → General → Danger Zone.
- **JANGAN** centang `Add a README file`, `Add .gitignore`, atau `Choose a license`.

Repo harus benar-benar kosong. Kalau ada README, `git push` nanti ditolak dengan `fetch first`.

Klik **Create repository**. Halaman berikutnya menampilkan URL repo, contoh: `https://github.com/<username>/ironclad.git`. Catat `<username>` kamu.

### Langkah 2. Ambil paketnya

Di sini, paketnya sudah saya siapkan: `/root/projects/ironclad.tar.gz` (28 KB, 34 entri, sudah termasuk `.git`).

Di komputermu:

```bash
tar -xzf ironclad.tar.gz
cd ironclad
git log --oneline | head -3     # harus muncul commit, bukan "not a git repository"
```

Kalau `git log` bilang bukan repo, berarti yang ter-extract bukan paket ini — hentikan, jangan lanjut.

### Langkah 3. Ganti placeholder username

Semua perintah install di dokumentasi masih memakai username contoh. Ganti dengan username GitHub kamu:

```bash
./scripts/set-repo-owner.sh <username-kamu>
```

Cek dulu tanpa menulis apa pun:

```bash
./scripts/set-repo-owner.sh <username-kamu> --dry-run
```

Harus keluar 5 hit atau lebih (`README.md`, `install.sh`, `index.html`). Kalau 0, berarti kamu menjalankannya dari folder yang salah.

### Langkah 4. Commit + push

```bash
git add -A
git commit -m "docs: point install URLs at <username-kamu>"

git remote add origin https://github.com/<username-kamu>/ironclad.git
git branch -M main
git push -u origin main
```

Kalau diminta password: GitHub **tidak** menerima password akun. Yang dipakai adalah Personal Access Token sebagai password, atau lebih mudah pasang SSH key. Kalau kamu belum pernah push dari mesin itu, ikuti <https://docs.github.com/en/authentication> — jangan tempel token ke chat mana pun.

Hasil yang benar: baris terakhir `branch 'main' -> 'main'`, lalu buka `https://github.com/<username>/ironclad` dan isinya terlihat.

### Langkah 5. Verifikasi dari luar

Jangan percaya tampilan web saja — tes URL yang benar-benar dipakai installer:

```bash
curl -sI https://raw.githubusercontent.com/<username>/ironclad/main/skills/ironclad/SKILL.md | head -1
```

Harus `HTTP/2 200`. Kalau `404`, penyebabnya salah satu dari tiga: repo masih Private, nama branch bukan `main`, atau path-nya salah.

Lalu tes install sungguhan di mesin mana pun:

```bash
hermes skills install <username>/ironclad/skills/ironclad
```

---

## Cara B — saya yang push (butuh token)

Pilih ini kalau kamu tidak mau menyentuh terminal.

### Langkah 1. Bikin repo kosong

Sama seperti Cara A Langkah 1. Wajib dilakukan dulu — token tidak bisa membuat repo, hanya menulis ke repo yang sudah ada.

### Langkah 2. Bikin fine-grained token

Buka <https://github.com/settings/tokens?type=beta> → **Generate new token**

| Field | Isi |
|---|---|
| Token name | `ironclad-push` |
| Expiration | **7 days** — cukup untuk sekali push |
| Repository access | **Only select repositories** → pilih `ironclad` |
| Permissions → Repository → **Contents** | **Read and write** |
| Permissions → Repository → **Metadata** | Read (otomatis tercentang) |

Tidak perlu centang lainnya. Jangan pakai classic token dengan scope `repo` penuh — itu membuka semua repo kamu.

### Langkah 3. Taruh di `.env`, bukan di chat

```bash
ssh root@43.156.111.169
echo 'GITHUB_TOKEN=github_pat_xxx' >> ~/.hermes/.env
```

### Langkah 4. Bilang "sudah, push"

Saya akan: ganti semua placeholder dengan username kamu, push, verifikasi `raw.githubusercontent.com` balas 200, lalu tes `hermes skills install` dari GitHub asli. Token tidak akan pernah muncul di output.

### Langkah 5. Cabut token

```bash
sed -i '/^GITHUB_TOKEN=/d' ~/.hermes/.env
```

Lakukan ini walau sudah selesai — token 7 hari tetap token yang hidup.

---

## Cara C — upload lewat web, tanpa git

Paling cepat, tapi merusak struktur folder paling sering.

1. Bikin repo kosong (Cara A Langkah 1).
2. Extract `ironclad.tar.gz` di komputermu, **hapus folder `.git`**.
3. Buka `https://github.com/<username>/ironclad/upload/main`
4. Drag **folder `ironclad`-nya**, bukan file satu per satu. Struktur `skills/ironclad/...` harus utuh.
5. Commit message: `feat: ironclad skill`.
6. Setelah commit pertama, buka `.github/workflows/engineering-standards.yml` → GitHub akan minta izin menjalankan workflow. Klik **"Workflows aren't being run on this repository"** → **Enable**.

Tanpa langkah 6, CI tidak jalan (tapi install tetap bisa).

---

# BAGIAN 2 — Memakainya di repo kantor

Setelah skill ter-install, ini urutan yang benar. Jangan lompat ke langkah 3.

## Langkah 1. Install skill-nya (sekali per mesin)

```bash
hermes skills install <username>/ironclad/skills/ironclad
```

Agent lain (Claude Code / Codex / Cursor):

```bash
curl -fsSL https://raw.githubusercontent.com/<username>/ironclad/main/install.sh | bash
```

## Langkah 2. Bootstrap di repo aplikasi

```bash
cd /path/ke/repo-kantor
python3 scripts/init_standards.py . --with-checker
```

Akan muncul pertanyaan tingkat penegakan. Tekan Enter untuk `balanced`.

Kalau tidak ada TTY (agent yang menjalankan), otomatis `balanced` tanpa menggantung — sudah diuji.

Yang tertulis:

```
.agent/standards.md          aturan, ber-ID, untuk dibaca manusia & agent
.agent/standards.yml         tingkat penegakan, dibaca checker & CI
scripts/check_schema.py      linter
scripts/presets/*.yml        tiga preset, ikut supaya --preset tetap jalan
```

**Commit keempatnya.** Ini bagian yang membuat standar bertahan — kalau `.agent/` tidak ikut commit, tiap orang punya aturan sendiri lagi.

## Langkah 3. Jalankan, jangan blokir dulu

```bash
python3 scripts/check_schema.py . --json > laporan.json
python3 -c "import json;d=json.load(open('laporan.json'));print(d['errors'],'error,',d['warnings'],'warning')"
```

Repo lama akan punya ratusan temuan. **Jangan langsung pasang sebagai gate** — itu cara tercepat membuat orang mematikan CI-nya. Urutannya:

| Minggu | Preset | Yang terjadi |
|---|---|---|
| 1 | `legacy-friendly` | semua dilaporkan, build tetap hijau |
| 2–3 | `balanced` + gate hanya file yang berubah | temuan baru diblokir, utang lama dibiarkan |
| setelah baseline bersih | `strict` | semua memblokir |

Ganti tingkat:

```bash
python3 scripts/init_standards.py . --preset balanced --force
```

Atau edit 7 baris di `.agent/standards.yml` lalu commit — sama sahnya, dan lebih kelihatan di review.

## Langkah 4. Pasang di CI

Salin `.github/workflows/engineering-standards.yml` dari repo skill ke repo kantor, atau tulis sendiri intinya:

```yaml
- name: Gate changed schema files
  if: github.event_name == 'pull_request'
  run: |
    CHANGED=$(git diff --name-only --diff-filter=d origin/${{ github.base_ref }}...HEAD \
      | grep -E '\.(sql|php|prisma)$' || true)
    [ -z "$CHANGED" ] && exit 0
    python scripts/check_schema.py $CHANGED
```

Kuncinya `$CHANGED` — hanya file yang berubah yang digate. Tanpa itu, semua PR merah selamanya.

## Langkah 5. Cek apakah benar-benar bekerja

Jangan percaya "sudah dipasang". Buktikan dengan tiga percobaan:

```bash
# 1. file benar harus lolos
python3 scripts/check_schema.py examples/good.sql --preset strict; echo $?   # 0

# 2. file salah harus gagal
python3 scripts/check_schema.py examples/bad.sql --preset strict; echo $?    # 1

# 3. membuat PR yang menambah kolom enum harus merah di GitHub
```

Kalau nomor 3 tidak merah, CI-nya yang belum benar — bukan checkernya.

---

# Yang perlu kamu tahu sebelum publik

**Belum ada update otomatis ke orang yang sudah install.** `hermes skills update` memakai URL yang tercatat saat install, jadi kalau kamu push perubahan, mereka perlu menjalankan perintah itu secara manual. Belum ada versioning/changelog.

**Nama repo `ironclad` bisa bentrok.** Sudah ada proyek bernama Ironclad (kontrak legal) dan beberapa lain. Untuk skill AI, tabrakan nama tidak fatal — tapi kalau kamu mau unik, pakai `ironclad-skill` atau `<username>/ironclad`.

**`.github/workflows` di repo skill menguji checkernya sendiri**, bukan repo user. Itu memang tujuannya: memastikan linter tidak diam-diam rusak saat kamu mengubah regex.

**Checker berbasis regex, bukan parser SQL.** Dia membaca DDL, migration Laravel, dan schema Prisma. Dia tidak melihat query builder ORM, SQL yang dirangkai saat runtime, atau tipe di TypeScript. Reviewer manusia tetap lapis terakhir.

---

# Kalau ada yang gagal

| Gejala | Penyebab | Perbaikan |
|---|---|---|
| `404` saat install | repo Private, atau branch bukan `main` | ubah visibility, cek `git branch` |
| `Could not fetch ... from any source` | username/repo salah, atau file belum ada di branch itu | buka URL `raw.githubusercontent.com` di browser |
| Install jalan tapi `scripts/` kosong | file pendukung tidak ter-upload | Cara C: ulangi dengan drag folder, bukan file |
| `unknown preset strict` | `scripts/presets/` tidak ikut | jalankan ulang `init_standards.py . --with-checker` |
| CI merah di semua PR | seluruh repo digate | gate `$CHANGED` saja |
| `git push` ditolak `fetch first` | repo tidak kosong saat dibuat | `git pull --rebase origin main` lalu push |
| `Permission denied (publickey)` | belum ada SSH key / token | pakai HTTPS + PAT sebagai password, atau pasang SSH key |
