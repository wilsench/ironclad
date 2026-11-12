---
title: Laravel, Prisma, dan backend lain
slug: frameworks
group: Referensi
order: 23
summary: Checker membaca apa saja, apa yang tidak terbaca, dan bagaimana tetap konsisten kalau kerangka kamu belum didukung.
---

# Laravel, Prisma, dan backend lain

Jawaban singkat: **bukan masalah selama kamu memakai salah satu dari tiga jenis
berkas yang dibaca checker.** Untuk yang lain, ada batas yang harus kamu tahu
sebelum percaya warna hijau.

## Apa yang terbaca

Checker memeriksa isi berkas, bukan menjalankan aplikasimu. Jadi yang penting
bukan "kamu pakai Laravel atau tidak", tapi "aturan itu akhirnya ditulis dalam
bentuk apa".

| Sumber | Contoh | Status |
|---|---|---|
| SQL mentah | `CREATE TABLE`, migration `.sql` | **didukung** |
| Laravel / PHP | `Schema::create`, `$table->enum()`, `$table->unsignedSmallInteger()` | **didukung** |
| Prisma | `model Order`, `enum OrderStatus` | **didukung** |
| Django / Python | `models.CharField`, `models.FloatField` | belum — dilaporkan, tidak diperiksa |
| Rails / Ruby | `create_table`, `t.integer` | belum — dilaporkan, tidak diperiksa |
| TypeORM / Drizzle | `@Entity`, `pgTable` | belum — dilaporkan, tidak diperiksa |
| Sequelize | `Model.init`, `DataTypes.*` | belum — dilaporkan, tidak diperiksa |
| GORM / Go | `gorm:"..."` | belum — dilaporkan, tidak diperiksa |
| JPA / Java / Kotlin | `@Entity` | belum — dilaporkan, tidak diperiksa |
| Entity Framework / C# | `[Table(`, `DbSet<` | belum — dilaporkan, tidak diperiksa |
| Diesel / sqlx / Rust | `#[derive(...)]`, `table_name` | belum — dilaporkan, tidak diperiksa |

## Yang penting: alat ini mengaku kalau tidak memeriksa

Ini bagian yang paling menentukan. Repo Django yang lolos tanpa pesan apa pun
lebih berbahaya daripada repo Django yang ditolak, karena yang pertama membuat
kamu mengira sudah aman.

```bash
$ ironclad check
no .sql/.php/.prisma files found

This repo does have schema files this checker cannot read: .py.
Nothing was checked. Do not treat this as a pass.
  .py: models.py
```

Exit code `2`. Di CI, itu bukan hijau — job-nya gagal.

Dan kalau repo-nya campuran (sebagian terbaca, sebagian tidak), kamu dapat
peringatan `COVERAGE` di atas hasil yang lain:

```
models.py:1: [COVERAGE] warn  1 schema file(s) checked, but this repo also has
.py schema files this checker cannot read — those files were NOT checked
```

Artinya: yang hijau hanya sebagian. Jangan anggap seluruh repo bersih.

## Kalau kamu memakai backend yang belum didukung

Ada dua pilihan jujur, dan satu pilihan yang buruk.

**1. Taruh aturannya di level yang bisa diperiksa.** Kalau kerangka kamu
menghasilkan SQL (kebanyakan melakukannya), commit juga berkas migrasi SQL-nya,
lalu arahkan checker ke sana:

```bash
ironclad check db/schema.sql
```

**2. Periksa lewat review, bukan mesin.** Untuk sementara, `.agent/standards.md`
tetap berguna: agent membacanya dan mengikuti aturan yang sama walau checker
tidak bisa memverifikasi. Yang hilang cuma gerbangnya — jadi lakukan
pemeriksaan manual di PR.

**3. Yang buruk: menambahkan `|| true`.** Itu membuat CI hijau tanpa memeriksa
apa pun. Lebih baik tidak memasang checker sama sekali daripada memasangnya
sebagai hiasan.

## Kenapa Laravel tetap aman

Tiga jebakan Laravel yang paling sering, dan ketiganya tertangkap:

```php
// ✗ ditolak DB-01 — enum tidak bisa ditambah tanpa ALTER TABLE
$table->enum('status', ['new', 'paid', 'shipped']);

// ✓ diterima — integer + foreign key ke tabel lookup
$table->unsignedSmallInteger('status_code');
$table->foreign('status_code')->references('code')->on('order_status');
```

```php
// ✗ ditolak DB-07 — timestamp() di Laravel menyimpan TANPA zona waktu
$table->timestamp('created_at');

// ✓ diterima
$table->timestampTz('created_at')->useCurrent();
```

```php
// ✗ ditolak DB-06 — uang tidak boleh float
$table->float('total');

// ✓ diterima — satuan terkecil + kode mata uang
$table->bigInteger('total_minor');
$table->char('currency', 3);
```

Satu catatan penting soal nama berkas: migrasi Laravel bernama
`2024_01_01_000000_create_orders_table.php` — kata "migration" ada di **nama
folder**, bukan nama berkas. Checker sekarang mengenali keduanya, dan juga
mengenali `Schema::create` tanpa peduli nama berkasnya.

## Eloquent dan controller

Checkernya juga membaca kode aplikasi, bukan hanya migrasi. Yang dicari di sana
adalah magic number:

```php
// ✗ ditolak DB-02
if ($order->status_code === 2) { ... }

// ✓ diterima
if ($order->status_code === OrderStatus::PAID) { ... }
```

Ini aturan yang paling sering dilanggar bukan karena orang malas, tapi karena
angka 2 terasa jelas saat ditulis dan tidak jelas enam bulan kemudian.

## Kalau kamu ragu

```bash
ironclad check --json
```

Keluarannya menyebut setiap berkas yang diperiksa dan setiap temuan. Kalau
sebuah berkas tidak muncul dan tidak ada peringatan `COVERAGE`, berarti berkas
itu tidak pernah dibaca — bukan berarti ia bersih.
