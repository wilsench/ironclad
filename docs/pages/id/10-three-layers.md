---
title: Tiga lapis
slug: three-layers
group: Konsep
order: 10
summary: Kenapa skill saja tidak cukup, dan kenapa checker saja juga tidak. Masing-masing menutup celah yang lain.
---

# Tiga lapis

Setiap lapis menutup celah yang tidak bisa ditutup lapis lain. Membuang salah satunya membuat sistemnya rapuh dengan cara yang berbeda.

## Lapis 1 — Kebijakan

Kebijakan punya dua bentuk, dan kamu boleh memakai salah satu atau keduanya:

- **yang tertulis** — `.agent/standards.md`, di repo kamu, ikut git
- **yang ditanam** — blok pendek di konfigurasi global agent, ditulis saat install.
  Isinya tiga cabang keputusan, dan satu baris tambahan kalau kamu memakai mode
  `house`. Lihat [Mode](/modes/).

Yang tertulis menang kalau keduanya ada, karena keputusan proyek lebih spesifik
daripada default alat. Yang ditanam menutup celah yang tidak bisa ditutup berkas
repo: agent yang bekerja di repo yang belum punya `.agent/standards.md`.

`.agent/standards.md`, di repo kamu, ikut git.

Isinya aturan ber-ID:

```markdown
### DB-04 — Never store a human label as the status

Status columns hold a code, never the label users read.

    ✗  status varchar(20)         -- 'shipped', 'pending'
    ✓  status_code smallint       -- FK to ref_order_status
```

**Kenapa harus di repo, bukan di skill:** aturan yang hanya ada di skill tidak ada bagi anggota baru, tidak ada bagi agent yang tidak memasang skill itu, dan tidak muncul di diff PR. Aturan yang tidak bisa dikutip dalam review akan hilang dalam dua sprint.

## Lapis 2 — Prosedur

`SKILL.md` + `references/`. Ini yang dijalankan agent: urutan langkah, tabel keputusan, dan jebakan yang sudah diketahui.

Contoh tabel keputusan dari `references/database.md`:

| Situasi | Pilihan | Alasan |
|---|---|---|
| Status bisa bertambah kapan saja | `smallint` + lookup + FK | Menambah nilai = satu baris data, bukan `ALTER TABLE` |
| Persis dua keadaan, tidak akan tumbuh | `boolean` | `is_active`, `is_deleted` |
| Nilai harus melalui review kode untuk berubah | `enum` **boleh** | Enum yang disengaja adalah dokumentasi, bukan kecelakaan |
| Label tampilan | kolom terpisah di lookup table | Jangan pernah jadi nilai yang disimpan |

**Kenapa di skill, bukan di README:** README dibaca sekali. Skill dibaca setiap kali agent mengerjakan tugas yang cocok — dan isinya masuk ke konteks model, bukan ke mata manusia yang sudah lupa.

## Lapis 3 — Mekanisme

`scripts/check_schema.py`, dijalankan di CI.

Ini satu-satunya lapis yang **tidak bisa dilobi model**. Kalau ada yang menulis `enum`, build merah, apa pun yang dikatakan agent.

```bash
python3 scripts/check_schema.py . --json
```

**Kenapa tetap butuh lapis 1 dan 2:** checker hanya tahu pola sintaksis. Ia tidak tahu bahwa `status_code = 7` di kode aplikasi sebenarnya merujuk "dibatalkan karena cuaca". Ia juga tidak bisa memilih desain yang benar — hanya menolak yang salah.

## Ketiganya, dan akibat kalau hilang

| Yang ada | Akibat |
|---|---|
| Skill saja | Dokumentasi bagus, nol jaminan. Drift dalam sebulan. |
| Checker saja | Semua orang tahu apa yang dilarang, tidak ada yang tahu apa yang **seharusnya**. Orang menambal sampai hijau. |
| Kebijakan saja | Dokumen mati. Tidak dibaca agent, tidak diperiksa mesin. |
| **Ketiganya** | Agent memilih desain yang benar **dan** mesin menolak yang menyimpang. |

## Alur lengkapnya

```
kamu minta fitur
      │
      ▼
agent melihat daftar skill  ──►  deskripsi cocok?  ──►  baca SKILL.md
                                                            │
                                                            ▼
                                              baca .agent/standards.md
                                                            │
                                              klasifikasi tiap kolom
                                                            │
                                                            ▼
                                                   tulis migrasi
                                                            │
                                                            ▼
                                             jalankan check_schema.py
                                                            │
                                          exit 0 ───────────┴─────── exit 1
                                            │                        │
                                        selesai              perbaiki schema
                                                                     │
                                                          (jangan matikan rule)
```

## Kesalahan paling umum

**Menganggap skill sebagai penegakan.** Ini yang paling sering. Skill adalah instruksi; instruksi bisa dilewati. Kalau kamu hanya punya skill dan suatu hari schema-nya melenceng, sistemnya bekerja persis seperti yang dirancang — longgar.

**Menaruh aturan di skill, bukan di repo.** Agent lalu punya aturan yang tidak dilihat reviewer, dan setiap orang memakai versi skill yang berbeda.

**Menjalankan checker tapi tidak pernah memperbaiki temuannya.** Itu `warn` selamanya, dan repo dengan seluruh warning adalah repo tanpa standar.
