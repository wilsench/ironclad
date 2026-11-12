-- fixture untuk DB-06 (money float) dan DB-07 (timestamp tanpa timezone)
CREATE TABLE invoices (
  id           bigint PRIMARY KEY,
  total_amount float NOT NULL,
  harga_satuan double precision,
  issued_at    timestamp NOT NULL,
  paid_at      timestamptz,
  createdAt    timestamp(3),
  updatedAt    timestamp(3)
);

-- Laravel
Schema::create('payments', function (Blueprint $table) {
    $table->float('amount_due');
    $table->timestamp('settled_at');
});
