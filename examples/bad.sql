-- BURUK: contoh yang harus ditolak checker
CREATE TABLE orders (
  id          bigint PRIMARY KEY,
  status      enum('draft','paid','shipped','cancelled') NOT NULL,
  is_status   boolean DEFAULT false,
  stock_state varchar(32) NOT NULL DEFAULT 'out_of_stock'
);

CREATE TABLE departures (
  id           bigint PRIMARY KEY,
  status_code  smallint NOT NULL
);
