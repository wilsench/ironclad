# Docs site

Sumber halaman: `docs/pages/*.md` (frontmatter + markdown).
Bangun ulang lalu deploy:

```bash
python3 docs/build.py
rsync -a --delete site/ /home/wilsench/htdocs/wilsench.my.id/public/ironclad/ \
  --exclude pkg --exclude install.sh
chown -R wilsench:wilsench /home/wilsench/htdocs/wilsench.my.id/public/ironclad
```

`pkg/` dan `install.sh` sengaja disimpan manual: keduanya harus bertahan
saat docs dibangun ulang. Setelah mengubah `skills/ironclad/**`, sinkronkan
mirror dengan `./scripts/sync-mirror.sh` — installer membaca mirror lebih dulu
supaya payload selalu cocok dengan script yang diunduh.

Repo GitHub bisa tertinggal dari mirror. Kalau `raw.githubusercontent.com`
menyajikan versi lama, pengguna tetap dapat versi benar karena mirror didahulukan.

Menambah halaman: buat `docs/pages/NN-slug.md` dengan frontmatter
`title`, `slug`, `group`, `order`, `summary`.
