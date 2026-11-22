# Keamanan dan Skalabilitas Sistem
## 1. Aset dan Risiko Keamanan Utama
Layanan **Model Prediktif Abalone Cloud API** memproses permintaan prediksi melalui endpoint publik berbasis HTTP. Berikut aset utama dan risiko keamanan yang diidentifikasi:

| Aset | Risiko Keamanan | Dampak Potensial |
|---|---|---|
| Endpoint Publik (`POST /predict`) | Penyalahgunaan endpoint (*spam* atau *flooding request* otomatis dari pihak luar)[cite: 1]. | Lonjakan jumlah *instance* container yang memicu pembengkakan biaya cloud (*denial-of-wallet*)[cite: 1]. |
| Kredensial & Token Cloud | Kebocoran kunci *service account*, token deployment, atau konfigurasi `.env` ke repository publik[cite: 1]. | Pengambilalihan akses resource cloud oleh pihak yang tidak berwenang. |
| Input Payload JSON | Pengiriman data korup, tipe data tidak sesuai, atau nilai ekstrem di luar rentang fitur abalone. | Kegagalan inferensi model (*crash* aplikasi) atau kesalahan informasi pada log. |
| Artefak Model (`model.joblib`) | Ketidaksesuaian dependensi atau pemuatan ulang file berulang kali. | Layanan gagal menyala (*startup failure*) atau latensi meningkat tajam. |

---
## 2. Kontrol Keamanan yang Diterapkan vs Rekomendasi

Sesuai dengan ruang lingkup pengerjaan proyek, berikut pemisahan antara kontrol keamanan yang **sudah diterapkan** pada sistem saat ini dengan **rekomendasi** untuk pengembangan lanjutan[cite: 1]:

### 2.1 Kontrol Keamanan yang Sudah Diterapkan
- **Pembatasan Jumlah Instance (`max instances = 2`):** Membatasi skala maksimal container agar lonjakan trafik tidak menyebabkan penggunaan resource dan biaya cloud yang tidak terkendali[cite: 1].
- **Manajemen Kredensial Terpusat:** Seluruh kredensial deployment dan secret disimpan eksklusif di **GitHub Secrets** (tidak pernah ditulis di dalam source code, Dockerfile, atau terekam di video demo)[cite: 1].
- **Pengecualian File Sensitif (`.gitignore`):** File `.env`, kunci privat, token, dan file kredensial JSON dikecualikan agar tidak masuk ke repository GitHub[cite: 1].
- **Prinsip *Least Privilege*:** Akun layanan (*service account*) untuk otomatisasi CI/CD hanya diberikan hak akses minimum yang dibutuhkan untuk melakukan deployment container[cite: 1].
- **Validasi Input Ketat:** API menolak payload kosong dengan kode `400` dan menolak fitur yang hilang, tipe data salah, atau nilai `Sex` di luar `"M"`, `"F"`, `"I"` dengan kode `422` sebelum masuk ke model.
- **Logging Aman:** Log request dicatat ke `stdout` hanya untuk metadata operasional (method, path, status HTTP, durasi) tanpa mencatat secret, token, atau data sensitif[cite: 1].

- ### 2.2 Rekomendasi Keamanan (Belum Diterapkan pada Tahap Demo)
- **Autentikasi API (API Key / JWT):** Menambahkan mekanisme autentikasi pada header HTTP sehingga hanya klien terdaftar yang dapat mengakses endpoint `POST /predict`[cite: 1].
- **Rate Limiting / API Gateway:** Membatasi jumlah permintaan per menit dari satu alamat IP untuk mencegah serangan *brute-force* atau *spam* trafik[cite: 1].
- **Web Application Firewall (WAF):** Menyaring pola trafik berbahaya sebelum permintaan mencapai container layanan.

---

## 3. Perilaku Sistem Saat Beban Meningkat (Skalabilitas)

Platform *managed container* dirancang untuk menyesuaikan kapasitas komputasi secara otomatis mengikuti perubahan volume permintaan masuk[cite: 1]:

1. **Autoscaling dan Batas Maksimal:**
   - Saat tidak ada permintaan masuk, container melakukan *scale-to-zero* (0 instance aktif) untuk menghemat biaya.
   - Ketika trafik meningkat, platform otomatis menambah jumlah container aktif hingga batas maksimal yang dikonfigurasi (`max instances = 2`)[cite: 1].
2. **Concurrency per Container:**
   - Satu container FastAPI (dijalankan melalui Uvicorn) mampu menangani beberapa permintaan HTTP secara bersamaan (*concurrent*) selama kapasitas CPU dan memori masih mencukupi.
   - Apabila jumlah permintaan bersamaan melebihi ambang batas *concurrency* satu container, permintaan berikutnya akan dialihkan ke instance kedua atau masuk ke antrean sementara.
3. **Dampak *Cold Start*:**
   - Ketika container baru menyala dari kondisi 0 instance (*cold start*), permintaan pertama akan mengalami tambahan latensi karena platform harus menginisialisasi container, menjalankan Python runtime, dan memuat pustaka `scikit-learn`.
   - Setelah container aktif (*warm*), permintaan berikutnya diproses jauh lebih cepat.
4. **Efisiensi Pemuatan Model di Memori:**
   - File `model.joblib` dimuat satu kali saja ke dalam memori RAM saat aplikasi FastAPI pertama kali menyala (*startup*), bukan dibaca ulang dari penyimpanan setiap kali ada permintaan `POST /predict`[cite: 1]. Strategi ini menjaga waktu inferensi tetap rendah dan stabil saat diuji pada beban 10 permintaan bersamaan (*target p95 < 1 detik*).
