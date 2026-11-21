# Kontrak Antarmuka Model dan API

## 1. Versi dan Persetujuan
- **Versi kontrak**: `1.0` (21 November 2026)
- **Disetujui oleh**: *(Isi nama anggota tim / tim API setelah disepakati bersama)*

## 2. Endpoint dan Contoh Payload
- **`GET /health`**: Memeriksa status layanan dan kesiapan model yang dimuat.
  - Contoh respons sukses:
    ```json
    {
      "status": "ok",
      "model_version": "v1"
    }
    ```
- **`POST /predict`** (`Content-Type: application/json`): Mengembalikan prediksi nilai `Rings` berdasarkan fitur abalone.
  - Contoh *request*:
    ```json
    {
      "features": {
        "Sex": "M",
        "Length": 0.455,
        "Diameter": 0.365,
        "Height": 0.095,
        "Whole weight": 0.514,
        "Shucked weight": 0.2245,
        "Viscera weight": 0.101,
        "Shell weight": 0.15
      }
    }
    ```
  - Contoh respons sukses:
    ```json
    {
      "prediction": 9.83,
      "model_version": "v1"
    }
    ```
  - **Catatan keluaran**: Nilai `prediction` berasal dari model `GradientBoostingRegressor` (`model.joblib` dengan `scikit-learn==1.9.1`) dan berbentuk angka desimal; perkiraan umur biologis umumnya `Rings + 1.5`.

## 3. Skema Fitur Input
Seluruh fitur wajib disertakan dengan nama dan urutan yang persis sesuai skema model (`features.json`), termasuk fitur yang memakai spasi:
- `Sex`: nilai kategorikal `"M"`, `"F"`, atau `"I"` (harus divalidasi di API karena `OneHotEncoder(handle_unknown="ignore")` tidak menolak kategori baru secara otomatis).
- `Length`, `Diameter`, dan `Height`: menggunakan nilai numerik pada skala asli sebagaimana tercantum dalam dataset UCI Abalone.
- `Whole weight`, `Shucked weight`, `Viscera weight`, dan `Shell weight`: menggunakan nilai numerik nonnegatif pada skala asli sebagaimana tercantum dalam dataset UCI Abalone.
- **Standardisasi fitur numerik**: dilakukan secara otomatis oleh `StandardScaler` dalam pipeline praproses model. Input API tidak perlu dibagi 200.
- **Rentang wajar fitur**: Mengacu pada nilai minimum–maksimum (`describe()`) data latih pada notebook analisis (`eda_v2.ipynb`).
- **Fitur tambahan**: Disesuaikan dengan kesepakatan implementasi API (ditolak atau diabaikan).

## 4. Validasi, Kegagalan, dan Kinerja
- **Status `400`**: *Body* kosong, bukan JSON yang valid, atau objek `features` kosong.
- **Status `422`**: Fitur wajib tidak lengkap, tipe data tidak sesuai, nilai `Sex` di luar `"M"`/`"F"`/`"I"`, atau nilai numerik negatif.
- **Kegagalan dan *timeout***: *Health check* gagal apabila model gagal dimuat; detail *timeout* serta pesan *error* mengikuti implementasi layanan API.
- **Kinerja**: Permintaan HTTP *on-demand* dengan target usulan `p95 < 1 detik` pada 10 *concurrent request* (hasil aktual diukur dan dilaporkan oleh tim API/pengujian).

## 5. Riwayat Revisi Kontrak
| Tanggal | Perubahan | Alasan | Disetujui Oleh |
| :--- | :--- | :--- | :--- |
| 2026-11-21 | Penyusunan kontrak antarmuka v1.0 (`GET /health`, `POST /predict`, skema fitur, dan aturan status `400`/`422`) | Menyamakan ekspektasi input, skala fitur, dan respons antara layer analisis/model dan layer API | *(Menunggu konfirmasi tim API)* |