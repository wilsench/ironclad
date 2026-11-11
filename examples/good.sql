-- BAIK: seharusnya lolos bersih
CREATE TABLE ref_stock_status (
  code        smallint PRIMARY KEY,
  label       text NOT NULL,
  sort_order  smallint NOT NULL DEFAULT 0,
  is_terminal boolean NOT NULL DEFAULT false
);

INSERT INTO ref_stock_status VALUES
  (0,'Kosong',0,false),(1,'Menipis',1,false),
  (2,'Tersedia',2,false),(3,'Dipesan',3,false);

CREATE TABLE product_stock (
  product_id  bigint NOT NULL REFERENCES products(id),
  status_code smallint NOT NULL DEFAULT 0 REFERENCES ref_stock_status(code),
  qty         integer  NOT NULL DEFAULT 0,
  CONSTRAINT stock_status_qty_consistent
    CHECK ((status_code = 0 AND qty = 0) OR (status_code <> 0 AND qty >= 0))
);

CREATE TABLE ref_departure_status (
  code smallint PRIMARY KEY,
  label text NOT NULL
);

CREATE TABLE departures (
  id bigint PRIMARY KEY,
  status_code smallint NOT NULL REFERENCES ref_departure_status(code)
);
