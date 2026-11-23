# Laporan Estimasi dan Realisasi Biaya Infrastruktur (*Cost Report*)

Dokumen ini merinci perencanaan, realisasi biaya aktual, serta strategi efisiensi sumber daya komputasi awan untuk proyek **Abalone Rings Prediction API** yang telah dideploy secara aktif pada alamat **`https://cc-kelompok2-c103e.containers.snapdeploy.app`**.

---

## 1. Pemilihan Platform dan Spesifikasi Sumber Daya

Berdasarkan evaluasi ketersediaan metode pembayaran tim (tanpa kartu kredit internasional) serta kebutuhan *deployment* kontainer Docker yang ringan untuk inferensi model `scikit-learn`, arsitektur infrastruktur memanfaatkan kombinasi layanan *cloud* berikut:

| Komponen Infrastruktur | Penyedia Layanan | Paket / Tier | Spesifikasi & Fungsi |
|---|---|---|---|
| **Container Hosting & Runtime** | **Snapdeploy** | **Free Tier** | Menjalankan kontainer FastAPI (`python:3.11-slim`, port `8000`) dengan dukungan HTTPS/TLS otomatis dan *reverse proxy* edge Cloudflare. |
| **CI/CD Pipeline** | **GitHub Actions** | **Free (Public Repo)** | Otomatisasi pengujian unit (`pytest`) dan verifikasi *build* Docker pada setiap *push* maupun *Pull Request*. |
| **Source Code & Artefak** | **GitHub** | **Free** | Penyimpanan kode sumber, artefak model (`model.joblib`), dokumentasi, serta bukti pengujian. |
| **Observability & Logs** | **Snapdeploy Built-in** | **Included (Free)** | Pemantauan log aplikasi kontainer dan status kesehatan layanan secara langsung melalui dasbor platform. |

---

## 2. Estimasi Biaya Operasional Bulanan (Proyeksi)

Perhitungan berikut membandingkan skenario operasional tim saat ini (paket gratis untuk pengembangan dan pengujian akademik) dengan proyeksi peningkatan kapasitas apabila layanan ditingkatkan ke skala produksi (*dedicated*):

| Komponen Layanan | Skenario Aktif (Free Tier) | Proyeksi Skala Produksi (Paid Tier) | Keterangan |
|---|---|---|---|
| **Compute & Container Hosting** | **$0,00 / bulan** | ~$5,00 – $10,00 / bulan | Paket berbayar menghilangkan mode *sleep/cold start* serta menaikkan kuota CPU/RAM dan batas *rate limit*. |
| **Bandwidth & SSL/TLS Edge** | **$0,00 / bulan** | $0,00 / bulan | Sudah termasuk dalam layanan *reverse proxy* platform. |
| **CI/CD Runner (GitHub Actions)** | **$0,00 / bulan** | $0,00 / bulan | Tidak terbatas (*unlimited minutes*) untuk repositori publik. |
| **Total Estimasi per Bulan** | **$0,00 (Rp0)** | **~$5,00 – $10,00** | Efisiensi 100% selama fase pengembangan dan evaluasi. |

---

## 3. Perbandingan Estimasi vs Realisasi Biaya Aktual

* **URL Layanan Aktif:** `https://cc-kelompok2-c103e.containers.snapdeploy.app`
* **Periode Evaluasi Aktual:** 23 November 2026 (mencakup *deployment* kontainer, verifikasi endpoint `/health` dan `/predict`, serta pengujian beban sebanyak 310 *request* pada skenario trafik normal dan lonjakan).

| Komponen Layanan | Estimasi Biaya | Biaya Aktual (Realisasi) | Selisih (*Variance*) | Status & Catatan Verifikasi |
|---|---|---|---|---|
| **Snapdeploy Container Hosting (Free Tier
