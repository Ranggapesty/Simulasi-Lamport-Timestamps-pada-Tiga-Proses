# Simulasi Lamport Timestamps

Tugas Mata Kuliah **Sistem Terdistribusi** — simulasi algoritma Lamport Timestamps pada 3 proses (P1, P2, P3) yang saling mengirim pesan, menghitung timestamp logis setiap event, dan memverifikasi konsistensi urutan kejadian.

## Konsep Lamport Timestamps

Lamport Timestamps adalah algoritma *logical clock* yang dikembangkan oleh Leslie Lamport (1978) untuk memberi penomoran urutan kejadian (event) pada sistem terdistribusi tanpa bergantung pada jam fisik (jam dinding) yang tidak sinkron. Setiap proses memiliki counter logis `C` yang diinisialisasi 0 dan diperbarui dengan tiga aturan:

1. **Setiap event** pada sebuah proses: `C = C + 1`.
2. **Send event**: timestamp `C` saat ini disertakan (dikirim) bersama pesan.
3. **Receive event**: `C = max(C lokal, timestamp pesan) + 1`.

Aturan ketiga memastikan timestamp pada penerima selalu lebih besar daripada timestamp pengirim, sehingga urutan *happened-before* (`→`) tercermin dalam penomoran: jika event A *happened-before* event B, maka `ts(A) < ts(B)`. Namun kebalikannya tidak berlaku — `ts(A) < ts(B)` tidak membuktikan `A → B`, karena dua event paralel (tidak saling terkait) bisa saja mendapat timestamp berbeda.

## Skenario Simulasi

Program mengeksekuri persis 10 event berikut:

| No | Proses | Event | Jenis         | Keterangan                        |
|----|--------|-------|---------------|-----------------------------------|
| 1  | P1     | A1    | Internal      | P1 menjalankan internal event A1  |
| 2  | P1     | A2    | Send          | P1 mengirim pesan m1 ke P2        |
| 3  | P2     | B1    | Receive       | P2 menerima pesan m1 dari P1      |
| 4  | P2     | B2    | Internal      | P2 menjalankan internal event B2  |
| 5  | P2     | B3    | Send          | P2 mengirim pesan m2 ke P3        |
| 6  | P3     | C1    | Receive       | P3 menerima pesan m2 dari P2      |
| 7  | P3     | C2    | Internal      | P3 menjalankan internal event C2  |
| 8  | P3     | C3    | Send          | P3 mengirim pesan m3 ke P1        |
| 9  | P1     | A3    | Receive       | P1 menerima pesan m3 dari P3      |
| 10 | P1     | A4    | Internal      | P1 menjalankan internal event A4  |

Perhitungan timestamp setiap event:

| Event | Proses | Jenis    | Perhitungan Clock          | Timestamp |
|-------|--------|----------|----------------------------|-----------|
| A1    | P1     | Internal | 0 + 1                      | 1         |
| A2    | P1     | Send     | 1 + 1                      | 2         |
| B1    | P2     | Receive  | max(0, 2) + 1              | 3         |
| B2    | P2     | Internal | 3 + 1                      | 4         |
| B3    | P2     | Send     | 4 + 1                      | 5         |
| C1    | P3     | Receive  | max(0, 5) + 1              | 6         |
| C2    | P3     | Internal | 6 + 1                      | 7         |
| C3    | P3     | Send     | 7 + 1                      | 8         |
| A3    | P1     | Receive  | max(2, 8) + 1              | 9         |
| A4    | P1     | Internal | 9 + 1                      | 10        |

## Struktur Program

```
.
├── main.py    # program utama simulasi
└── README.md  # dokumen ini
```

`main.py` hanya menggunakan library bawaan Python (`collections`) dan terdiri dari beberapa bagian yang dipisah:

- **`LamportSimulator`** — kelas penyimpan status logical clock, antrean pesan antar proses, dan log event. Memiliki fungsi:
  - `proses_internal()` — memproses internal event.
  - `kirim()` — memproses send event (timestamp disertakan dalam pesan).
  - `terima()` — memproses receive event (`C = max(C, ts_pesan) + 1`).
- **`jalankan_skenario()`** — mengeksekuri 10 event sesuai tabel skenario.
- **`tampilkan_tabel()`** — menampilkan hasil simulasi dalam tabel rapi di terminal.
- **`bangun_relasi_happened_before()`** — membangun relasi `→` dari urutan program dan relasi send→receive.
- **`verifikasi()`** — menjalankan pemeriksaan konsistensi otomatis.

## Cara Menjalankan

Pastikan Python 3 terpasang, lalu jalankan dari direktori ini:

```
python main.py
```

Tidak ada library eksternal yang perlu dipasang dan tidak perlu modifikasi apa pun.

## Hasil dan Verifikasi

Timestamp akhir tiap event: A1=1, A2=2, B1=3, B2=4, B3=5, C1=6, C2=7, C3=8, A3=9, A4=10. Logical clock akhir: P1=10, P2=5, P3=8.

Setelah tabel, program menjalankan tiga pemeriksaan konsistensi otomatis:

1. **Timestamp meningkat pada setiap proses** — P1: 1, 2, 9, 10; P2: 3, 4, 5; P3: 6, 7, 8 → seluruhnya meningkat.
2. **Timestamp receive > timestamp send** — m1: 2 < 3; m2: 5 < 6; m3: 8 < 9.
3. **Happened-before (A → B) ⇒ ts(A) < ts(B)** — 15 pasangan relasi (urutan program + send→receive) semuanya memenuhi syarat.

Program kemudian mencetak ringkasan **SELURUH PEMERIKSAAN LULUS**. Contoh cuplikan output:

```
+----+--------+-------+----------+------------+-----------+---------------------------------------------------+
| No | Proses | Event | Jenis    | Pesan      | Timestamp | Keterangan                                        |
+----+--------+-------+----------+------------+-----------+---------------------------------------------------+
| 1  | P1     | A1    | Internal | -          | 1         | Proses melakukan kegiatan lokal                   |
| 2  | P1     | A2    | Send     | m1 -> P2   | 2         | Mengirim pesan m1 ke P2                           |
| 3  | P2     | B1    | Receive  | m1 dari P1 | 3         | Menerima m1 dari P1: max(lokal=0, ts_pesan=2) + 1 |
...
+----+--------+-------+----------+------------+-----------+---------------------------------------------------+

[LULUS] 1. Timestamp meningkat pada setiap proses
[LULUS] 2. Timestamp receive > timestamp send
[LULUS] 3. Happened-before (A -> B) => ts(A) < ts(B)
RINGKASAN: SELURUH PEMERIKSAAN LULUS.
```

## Kesimpulan

Simulasi membuktikan bahwa algoritma Lamport Timestamps bekerja sesuai ketentuan: timestamp yang dihitung konsisten memetakan relasi *happened-before* ke urutan angka (A → B ⇒ ts(A) < ts(B)). Namun timestamp yang lebih kecil tidak selalu membuktikan hubungan sebab-akibat — misalnya A1 (ts=1) dan B1 (ts=3) dapat dibandingkan timestamp-nya, tetapi kebalikan aturan tidak berlaku sebagai bukti relasi.
