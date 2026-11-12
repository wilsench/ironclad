---
title: Aturan DB-01…DB-07
slug: rules
group: Referensi
order: 20
summary: Tujuh aturan database, masing-masing dengan contoh salah dan benar yang benar-benar diuji checker.
---

# Aturan

Setiap aturan punya ID, supaya laporan agent dan komentar review bisa mengutipnya. Formatnya `DB-nn` untuk database; domain lain memakai awalan sendiri (`API-`, `SEC-`) lewat `references/extending.md`.

## Ringkasan

Kolom **Status** di bawah adalah perilaku pada preset `balanced` (default). Pada `strict` semuanya jadi `error`; pada `legacy-friendly` semuanya `warn`.

| ID | Aturan | Status |
|---|---|---|
| DB-01 | Tidak ada `enum` native di schema | **error** |
| DB-02 | Tidak ada magic number dibandingkan ke kolom status | **error** |
| DB-03 | Integer status wajib punya FK atau `CHECK` | warn |
| DB-04 | Label manusia tidak pernah disimpan sebagai status | **error** |
| DB-05 | `boolean` hanya untuk biner sejati | warn |
| DB-06 | Uang pakai `bigint` satuan terkecil + kode mata uang | warn |
| DB-07 | Timestamp wajib membawa zona waktu | warn |

---

## DB-01 — Tidak ada `enum` native

```sql
-- ✗ ditolak
status enum('pending','shipped','cancelled')

-- ✓ diterima
status_code smallint NOT NULL REFERENCES ref_order_status(code)
```

**Alasan:** menambah nilai enum butuh `ALTER TABLE`; pada tabel besar itu mengunci dan bisa berarti downtime. Status bisnis selalu tumbuh — "ditunda karena cuaca", "dibatalkan sebagian" — dan tiap pertumbuhan tidak seharusnya jadi acara migrasi.

**Pengecualian:** enum yang memang **disengaja** dan nilainya hanya berubah lewat review kode. Tulis alasannya di komentar migrasi; pada `balanced` itu diterima saat review.

```php
// Enum disengaja: nilainya mengikat kontrak API publik, tidak akan tumbuh.
$table->enum('visibility', ['public','unlisted','private']);
```

---

## DB-02 — Tidak ada magic number pada kolom status

```php
// ✗ ditolak
if ($order->status_code === 3) { ... }
Order::where('status_code', 3)->get();

// ✓ diterima
if ($order->status_code === OrderStatus::SHIPPED) { ... }
Order::where('status_code', OrderStatus::SHIPPED)->get();
```

**Alasan:** `3` tidak berarti apa pun saat muncul di log atau stack trace. Enam bulan kemudian tidak ada yang berani mengubahnya, karena tidak ada yang tahu apa itu `3`.

**Yang tidak dilanggar:** literal di dalam `CHECK (...)` dan `INSERT` — itu DDL yang benar, dan checker mengabaikannya secara sadar.

```sql
CONSTRAINT stock_qty_consistent
  CHECK ((status_code = 88 AND qty = 0) OR (status_code <> 88 AND qty >= 0))
```

---

## DB-03 — Integer status wajib punya FK atau `CHECK`

```sql
-- ✗ ditolak: 7 bisa masuk, tidak ada yang menolak
status_code smallint NOT NULL

-- ✓ diterima
status_code smallint NOT NULL REFERENCES ref_stock_status(code)
```

**Alasan:** tanpa FK, kolom integer adalah `varchar` yang kebetulan berupa angka. Tidak ada yang mencegah `status_code = 7` saat kode sahnya hanya `88..91`.

**Peringatan desain:** `CHECK` yang menghardcode semua kode sah berarti kamu membangun ulang enum. Pakai FK ke lookup table — menambah nilai jadi satu baris data, bukan perubahan schema.

---

## DB-04 — Label manusia tidak pernah jadi nilai status

```sql
-- ✗ ditolak
stock_state varchar(20)    -- 'available', 'empty'

-- ✓ diterima
status_code smallint NOT NULL REFERENCES ref_stock_status(code)
```

**Alasan:** label berubah karena alasan pemasaran ("Kosong" → "Stok Habis"), dan setiap perubahan itu menjadi migrasi data yang menyentuh seluruh baris. Lebih buruk: label tidak pernah diterjemahkan, jadi aplikasi berbahasa Indonesia menyimpan kata Inggris selamanya.

Label tinggal di lookup table, satu tempat, dan bisa diterjemahkan lewat tabel terpisah kalau perlu.

---

## DB-05 — `boolean` hanya untuk biner sejati

```sql
-- ✗ ditolak: status punya lebih dari dua keadaan
is_status boolean

-- ✓ diterima
is_active    boolean NOT NULL DEFAULT true
is_deleted   boolean NOT NULL DEFAULT false
status_code  smallint NOT NULL REFERENCES ref_stock_status(code)
```

**Alasan:** `is_status` menjebak. Hari ini true/false; bulan depan butuh "tertunda", dan kamu menambah `is_pending`, lalu `is_partial` — tiga boolean yang saling bertentangan dan tidak ada yang tahu kombinasi mana yang sah.

**Tes cepat:** bisakah kolom ini punya keadaan ketiga dalam dua tahun? Kalau ya, ia bukan boolean.

---

## DB-06 — Uang tidak pernah `float`

```sql
-- ✗ ditolak
total_amount  float
harga_satuan  double precision
price         decimal(10,2)   -- juga ditolak: lihat catatan

-- ✓ diterima
total_minor   bigint NOT NULL          -- 1250000 = Rp 12.500,00
currency      char(3) NOT NULL         -- 'IDR'
```

**Alasan:** `0.1 + 0.2` pada float bukan `0.3`. Untuk satu transaksi selisihnya nol koma nol sekian; untuk laporan bulanan dengan 200.000 baris, itu selisih yang harus dijelaskan ke auditor.

Menyimpan satuan terkecil sebagai integer membuat semua aritmetika eksak. `decimal` sebenarnya eksak juga, tapi tiap basis data memperlakukannya berbeda dan ORM sering mengubahnya jadi string atau float di perjalanan — integer tidak punya ambiguitas itu.

---

## DB-07 — Timestamp membawa zona waktu

```sql
-- ✗ ditolak
issued_at  timestamp

-- ✓ diterima
issued_at  timestamptz
created_at timestamptz NOT NULL DEFAULT now()
```

**Alasan:** `timestamp` tanpa zona menyimpan "14:30" tanpa menjawab "di mana". Aplikasi dengan pengguna di Jakarta dan server di Singapura akan salah satu jam, dan tidak ada cara memperbaikinya setelah data bertahun-tahun terkumpul.

Laravel dan Prisma memakai `createdAt`/`updatedAt` sebagai konvensi; checker mengenali itu dan tidak melaporkannya.

---

## Uji sendiri

```bash
# harus lolos semua preset
python3 scripts/check_schema.py examples/good.sql --preset strict
# preset: strict
# 1 file(s), 0 error(s), 0 warning(s)

# harus gagal di strict
python3 scripts/check_schema.py examples/bad.sql --preset strict
```

`examples/good.sql` memakai kode `88/89/90` dan `990…993` dengan sengaja — untuk membuktikan bahwa kode tak berurutan itu sah, selama terdaftar di lookup table dan dipakai lewat FK.
