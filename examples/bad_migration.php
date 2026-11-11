<?php
// migration Laravel yang buruk
return new class extends Migration {
    public function up(): void {
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->enum('status', ['draft', 'paid', 'shipped']);
            $table->string('departure_status');
            $table->timestamps();
        });
    }
    public function down(): void {
        Schema::dropIfExists('orders');
    }
};
