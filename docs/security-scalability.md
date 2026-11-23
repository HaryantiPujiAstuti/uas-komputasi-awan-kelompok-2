# Keamanan dan Skalabilitas Sistem

## 1. Aset dan Risiko Keamanan Utama

Layanan **Model Prediktif Abalone Cloud API** memproses permintaan prediksi melalui endpoint publik berbasis HTTP pada platform Snapdeploy. Berikut aset utama dan risiko keamanan yang diidentifikasi:

| Aset | Risiko Keamanan | Dampak Potensial |
|---|---|---|
| Endpoint Publik (`POST /predict`) | Penyalahgunaan endpoint (*spam* atau *flooding request* otomatis dari pihak luar). | Kuota resource CPU/memori paket gratis habis sehingga layanan menjadi lambat atau tidak merespons (*denial-of-service*). |
| Kredensial & Token Akses | Kebocoran token deployment, API key, atau file `.env` ke repository publik GitHub. | Pengambilalihan akses konfigurasi deployment oleh pihak yang tidak berwenang. |
| Input Payload JSON | Pengiriman data korup, tipe data tidak sesuai, atau nilai ekstrem di luar rentang fitur abalone. | Kegagalan inferensi model (*crash* aplikasi) atau kesalahan informasi pada log. |
| Artefak Model (`model.joblib`) | Ketidaksesuaian dependensi atau pemuatan ulang file berulang kali. | Layanan gagal menyala (*startup failure*) atau latensi meningkat tajam. |

---

## 2. Kontrol Keamanan yang Diterapkan vs Rekomendasi

Sesuai dengan ruang lingkup pengerjaan proyek, berikut pemisahan antara kontrol keamanan yang **sudah diterapkan** pada sistem saat ini dengan **rekomendasi** untuk pengembangan lanjutan:

### 2.1 Kontrol Keamanan yang Sudah Diterapkan
- **Pembatasan Kapasitas via Free Tier Quota:** Layanan berjalan di atas paket gratis Snapdeploy yang secara bawaan membatasi alokasi CPU, memori, dan jumlah instance, sehingga mencegah pembengkakan biaya tak terduga (*zero overbilling risk*).
- **Manajemen Kredensial Terpusat:** Seluruh token deployment atau variabel sensitif disimpan eksklusif di pengaturan *Environment Variables* platform dan **GitHub Secrets** (tidak pernah ditulis di dalam source code, Dockerfile, atau terekam di video demo).
- **Pengecualian File Sensitif (`.gitignore`):** File `.env`, kunci privat, token, dan file kredensial JSON dikecualikan agar tidak masuk ke repository GitHub.
- **Prinsip *Least Privilege*:** Akses integrasi antara GitHub dan Snapdeploy dibatasi hanya pada repository proyek kelompok yang bersangkutan.
- **Validasi Input Ketat:** API menolak payload kosong dengan kode `400` dan menolak fitur yang hilang, tipe data salah, atau nilai `Sex` di luar `"M"`, `"F"`, `"I"` dengan kode `422` sebelum masuk ke model.
- **Logging Aman:** Log request dicatat ke `stdout` hanya untuk metadata operasional (method, path, status HTTP, durasi) tanpa mencatat secret, token, atau data sensitif.

### 2.2 Rekomendasi Keamanan (Belum Diterapkan pada Tahap Demo)
- **Autentikasi API (API Key / JWT):** Menambahkan mekanisme autentikasi pada header HTTP sehingga hanya klien terdaftar yang dapat mengakses endpoint `POST /predict`.
- **Rate Limiting / Reverse Proxy:** Membatasi jumlah permintaan per menit dari satu alamat IP untuk mencegah serangan *brute-force* atau *spam* trafik yang menghabiskan kuota container.
- **Web Application Firewall (WAF):** Menyaring pola trafik berbahaya sebelum permintaan mencapai container layanan.

---

## 3. Perilaku Sistem Saat Beban Meningkat (Skalabilitas)

Berikut karakteristik skalabilitas dan performa layanan container pada lingkungan Snapdeploy Free Tier:

1. **Kapasitas Instance dan Batasan Beban:**
   - Pada paket gratis Snapdeploy, aplikasi dijalankan pada satu container instance dengan batas resource CPU dan RAM tertentu tanpa *horizontal autoscaling* otomatis.
   - Apabila terjadi lonjakan trafik melebihi kapasitas CPU/RAM container, waktu respons (*latency*) akan meningkat karena permintaan mengantre untuk diproses.
2. **Concurrency per Container:**
   - Server ASGI **Uvicorn** di dalam container menangani beberapa permintaan HTTP secara bersamaan (*concurrent*) menggunakan mekanisme *asynchronous I/O*.
   - Beban kerja inferensi model `GradientBoostingRegressor` bersifat *CPU-bound* ringan sehingga tetap stabil untuk pengujian beban 10 permintaan bersamaan (*target p95 < 1 detik*).
3. **Dampak *Sleep Mode* dan *Cold Start*:**
   - Layanan container gratis umumnya akan masuk ke kondisi *idle/sleep* apabila tidak menerima permintaan dalam jangka waktu tertentu.
   - Saat permintaan pertama masuk setelah periode *sleep* (*cold start*), latensi akan lebih tinggi karena platform perlu membangunkan container dan memuat runtime Python serta model. Oleh karena itu, dilakukan pemanasan (*warm-up*) dengan memanggil `GET /health` beberapa menit sebelum demo berlangsung.
4. **Efisiensi Pemuatan Model di Memori:**
   - File `model.joblib` dimuat satu kali saja ke dalam memori RAM saat aplikasi FastAPI pertama kali menyala (*startup*), bukan dibaca ulang dari penyimpanan setiap kali ada permintaan `POST /predict`. Strategi ini menjaga waktu inferensi tetap cepat dan konsisten.
