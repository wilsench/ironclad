-- BAIK: seharusnya lolos bersih.
-- Kode sengaja tidak berurutan (88/89/90) — menunjukkan bahwa kode bebas itu sah,
-- yang wajib: terdaftar di lookup table, dipakai lewat FK, tidak ada literal di app code.
CREATE TABLE ref_stock_status (
  code        smallint PRIMARY KEY,
  label       text NOT NULL,
  sort_order  smallint NOT NULL DEFAULT 0,
  is_terminal boolean NOT NULL DEFAULT false      -- biner sejati: bisa final atau tidak
);

INSERT INTO ref_stock_status VALUES
  (88,'Kosong',   0,false),
  (89,'Menipis',  1,false),
  (90,'Tersedia', 2,false),
  (91,'Dipesan',  3,false);

CREATE TABLE product_stock (
  product_id  bigint NOT NULL REFERENCES products(id),
  status_code smallint NOT NULL DEFAULT 88 REFERENCES ref_stock_status(code),
  qty         integer  NOT NULL DEFAULT 0,
  CONSTRAINT stock_status_qty_consistent
    CHECK ((status_code = 88 AND qty = 0) OR (status_code <> 88 AND qty >= 0))
);

CREATE TABLE ref_departure_status (
  code  smallint PRIMARY KEY,          -- 99x block: keberangkatan
  label text NOT NULL
);

INSERT INTO ref_departure_status VALUES
  (990,'Dijadwalkan'),(991,'Berangkat'),(992,'Batal'),(993,'Tiba');

CREATE TABLE departures (
  id          bigint PRIMARY KEY,
  status_code smallint NOT NULL REFERENCES ref_departure_status(code)
);
