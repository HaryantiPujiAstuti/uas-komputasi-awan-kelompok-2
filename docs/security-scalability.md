# Analisis Keamanan, Skalabilitas, dan Kinerja Layanan

Dokumen ini memaparkan evaluasi aspek keamanan, skalabilitas, serta hasil pengujian performa (*load testing*) secara empiris terhadap layanan **Abalone Rings Prediction API** yang berjalan pada lingkungan produksi (`https://cc-kelompok2-c103e.containers.snapdeploy.app`).

---

## 1. Analisis Keamanan (*Security*)

### 1.1. Enkripsi Transportasi Data (HTTPS / TLS)
Seluruh komunikasi klien menuju layanan publik diproteksi menggunakan protokol **HTTPS (TLS)** yang dikelola secara otomatis oleh *reverse proxy* edge (Cloudflare) dan platform **Snapdeploy**. Hal ini menjamin kerahasiaan serta integritas payload fitur biologis abalone selama transmisi di jaringan publik.

### 1.2. Validasi Input Ketat (*Schema Enforcement*)
Endpoint `POST /predict` dilindungi oleh skema validasi **Pydantic / FastAPI** sebelum data diteruskan ke model *machine learning*:
* Payload yang kehilangan satu atau lebih fitur wajib (`Sex`, `Length`, `Diameter`, `Height`, `Whole weight`, `Shucked weight`, `Viscera weight`, `Shell weight`) atau memiliki tipe data tidak valid langsung ditolak di lapisan API dengan kode status **`HTTP 422 Unprocessable Entity`** (bukti verifikasi tersimpan di `docs/evidence/swagger-predict-422.png`).
* Mekanisme ini mencegah *runtime exception* pada *pipeline* inferensi `scikit-learn` maupun potensi injeksi input tak terduga.

### 1.3. Perlindungan DDoS dan Pembatasan Laju Permintaan (*Edge Rate Limiting*)
Infrastruktur Snapdeploy berjalan di balik jaringan *edge* **Cloudflare** (`server: cloudflare`). Berdasarkan pengujian empiris menggunakan 300 permintaan serentak dari satu sumber IP, lapisan *edge* secara otomatis mengaktifkan pembatasan trafik (*rate limiting*) dengan mengembalikan kode **`HTTP 429 Too Many Requests`** setelah melewati ambang batas lonjakan *burst*. Perlindungan bawaan ini mencegah penyalahgunaan sumber daya komputasi container (*resource exhaustion*) akibat *spam* atau serangan *flooding* sederhana.

### 1.4. Isolasi Container & Manajemen Rahasia (*Secrets Hygiene*)
* Aplikasi dikemas dalam *container image* berbasis `python:3.11-slim` yang terisolasi dari sistem *host* dan hanya mengekspos port layanan HTTP (`8000`).
* Repositori kode bebas dari kredensial sensitif (*hardcoded API keys*, token, maupun kata sandi); konfigurasi port dan lingkungan dikelola melalui variabel lingkungan (*environment variables*).

---

## 2. Analisis Skalabilitas dan Keandalan (*Scalability & Reliability*)

### 2.1. Arsitektur *Stateless*
Layanan prediksi bersifat **stateless**: seluruh artefak model (`model.joblib` / `v1`) dimuat ke dalam memori saat aplikasi *startup* dan tidak menyimpan status sesi pengguna di penyimpanan lokal container. Desain ini memungkinkan replikasi horizontal (*horizontal scaling*) di masa mendatang tanpa memerlukan sinkronisasi disk antar-instans.

### 2.2. Karakteristik & Batasan Paket *Free Tier* Snapdeploy
Karena layanan di-*deploy* menggunakan paket **Free Tier** Snapdeploy ($0,00), terdapat dua karakteristik operasional yang teramati selama pengujian:
1. **Batasan Konkurensi & *Burst Traffic*:** Pada lonjakan 300 *request* dengan *concurrency* 10, sistem mampu melayani hingga 103 permintaan pertama secara paralel sebelum pembatas trafik *edge* menahan sisa permintaan (`HTTP 429`).
2. **Perilaku *Idle / Cold Start*:** Apabila tidak menerima trafik dalam rentang waktu tertentu, container paket gratis dapat memasuki mode *sleep* dan memerlukan waktu inisialisasi ulang saat kembali diakses (sempat teramati respons sementara `HTTP 503` pada masa transisi sebelum layanan kembali stabil ke `HTTP 200`).

### 2.3. Rekomendasi Peningkatan Skala (*Future Scaling*)
Apabila kebutuhan trafik meningkat menuju skala produksi komersial:
* Melakukan *upgrade* ke paket *dedicated* untuk menghilangkan batasan *sleep/cold start* serta menaikkan ambang batas *rate limit*.
* Mengaktifkan *auto-scaling* horizontal berbasis utilisasi CPU/memori (misalnya menambah replika container saat CPU > 70%) di balik *load balancer*.
* Menerapkan mekanisme *client-side retry* dengan *exponential backoff* untuk menangani respons `HTTP 429` maupun transisi *cold start* secara anggun.

---

## 3. Hasil Pengujian Beban Aktual (*Load Testing*)

Pengujian performa dilakukan secara langsung terhadap endpoint publik **`POST https://cc-kelompok2-c103e.containers.snapdeploy.app/predict`** menggunakan skrip reproduksibel pada `scripts/load_test.py`. Seluruh bukti tangkapan layar tersimpan di direktori `docs/evidence/`.

| Skenario Pengujian | Total Request | Concurrency | Distribusi Status HTTP | Throughput | Latensi Rata-rata | Latensi p50 (Median) | Latensi p95 | Bukti & Evaluasi |
|---|---|---|---|---|---|---|---|---|
| **Inferensi Normal (Terukur)** | 10 | 1 | `200 OK`: 10 (100%) | — | 619,83 ms | — | **709,15 ms** | `load-test-normal-200.png` — **Memenuhi target SLA** (`p95 < 1.000 ms`). |
| **Uji Beban Tinggi (*Stress / Burst*)** | 300 | 10 | `200 OK`: 103<br>`429 Too Many Requests`: 197 | 9,78 req/detik | 991,95 ms | 884,69 ms | **1.768,68 ms** | `load-test-300-req.png` — Memproses 103 *request* paralel, lalu *rate limiter* Cloudflare menahan trafik berlebih. |

### Ringkasan Temuan Pengujian
1. **Kinerja Inferensi Normal Optimal:** Pada pola trafik normal di bawah batas *rate limit*, seluruh permintaan sukses (`100% HTTP 200`) dengan latensi **p95 sebesar `709,15 ms`** (lebih cepat dari batas maksimal yang disyaratkan sebesar `1.000 ms` / 1 detik) dan menghasilkan keluaran konsisten (`"prediction": 9.8326`, `"model_version": "v1"`).
2. **Ketahanan Terhadap Lonjakan Beban:** Pada pengujian 300 *request* (*concurrency* 10), layanan tetap responsif tanpa mengalami *crash* atau *timeout* server (`HTTP 500`); permintaan yang melewati batas paket gratis ditangani secara terkendali melalui kode status `HTTP 429`.
