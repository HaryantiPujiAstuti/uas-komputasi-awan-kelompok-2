# Kontrak Antarmuka Model dan API

## 1. Artefak Model
- **Pipeline terlatih**: `src/app/model/model.joblib` (sudah memuat tahap praproses dan model regresi terpilih).
- **Skema fitur**: `src/app/model/features.json` (memuat daftar nama fitur, pengelompokan tipe fitur, serta kategori `Sex`).

## 2. Spesifikasi Endpoint
- `GET /health`: Memeriksa status layanan API dan memastikan artefak model berhasil dimuat serta siap digunakan.
- `POST /predict`: Menerima *payload* JSON berisi nilai prediktor abalone sesuai `features.json` dan mengembalikan nilai prediksi `Rings` beserta informasi respons yang disepakati tim.

## 3. Penanganan Error dan Ekspektasi Kinerja
- **`400` / `422`**: Dikembalikan ketika format JSON tidak valid, fitur wajib tidak lengkap, tipe data tidak sesuai, atau terdapat nilai di luar batas wajar yang telah disepakati bersama tim API.
- **Kinerja**: Layanan API di dalam *container* diharapkan dapat melayani permintaan prediksi secara stabil dengan latensi yang wajar.