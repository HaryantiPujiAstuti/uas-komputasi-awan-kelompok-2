# Laporan Estimasi dan Realisasi Biaya Cloud

## 1. Informasi Provider dan Layanan
- **Penyedia Layanan Cloud:** Snapdeploy (Managed Container Platform)
- **Paket / Tier:** Free Tier (Gratis tanpa kartu kredit)
- **Alasan Pemilihan Alternatif:** Dipilih sebagai alternatif pengganti Google Cloud Run karena kelompok tidak menggunakan metode pembayaran/kartu kredit untuk aktivasi billing, serta sudah mendukung deployment berbasis Docker container secara gratis.
- **Sumber Harga Resmi:** Halaman Pricing resmi Snapdeploy (Free Plan)
- **Tanggal Estimasi Awal:** 23 November 2026

---

## 2. Asumsi Penggunaan untuk Estimasi Awal
Untuk kebutuhan pengembangan, pengujian beban (*load test*), dan demo UAS selama periode proyek (± 1 minggu), digunakan asumsi sebagai berikut:
- **Jenis Deployment:** Single Docker Container (`Dockerfile` dari repository GitHub).
- **Kapasitas Resource:** Mengikuti batas alokasi standar *Free Tier* Snapdeploy.
- **Estimasi Volume Permintaan:** 10.000 *request* selama masa pengujian & demo (mencakup pengujian fungsional, *health check* `/health`, *load test* 300 *request*, dan presentasi).
- **Layanan Pendukung:** Built-in container logs dan auto-deploy terintegrasi dengan GitHub.

---

## 3. Perbandingan Estimasi vs Realisasi Biaya

*(Catatan: Sesuai pedoman proyek, komponen yang belum selesai diamati dicatat sebagai `tidak diukur` dan diperbarui setelah layanan live serta melewati periode pengamatan dashboard).*

| Komponen Layanan | Estimasi Biaya (Asumsi) | Biaya Aktual (Realisasi) | Selisih | Keterangan |
|---|---|---|---|---|
| **Snapdeploy Container Hosting (Free Tier)** | $0,00 (Rp0) — paket gratis tidak memungut biaya bulanan/per-request selama dalam batas kuota free tier | `tidak diukur` | `tidak diukur` | Menunggu konfirmasi deployment live dan tangkapan layar dashboard akun |
| **GitHub Actions (CI Workflow)** | $0,00 (Rp0) — gratis untuk public repository | `tidak diukur` | `tidak diukur` | Berjalan otomatis setiap push/PR ke `main` |
| **Built-in Logging & Monitoring** | $0,00 (Rp0) — sudah termasuk dalam paket gratis platform | `tidak diukur` | `tidak diukur` | Pengamatan log dilakukan selama periode aktif layanan |
| **Total Biaya** | **$0,00 (Rp0)** | `tidak diukur` | `tidak diukur` | Periode pengamatan aktual: *(diisi setelah deploy)* |

---

## 4. Analisis dan Pengendalian Biaya
1. **Zero-Cost dengan Free Tier:** Penggunaan paket gratis Snapdeploy memastikan tidak ada biaya tagihan tak terduga (*overbilling*) selama masa pengujian maupun demo.
2. **Perbedaan Operasional Platform Gratis:** Berbeda dengan Google Cloud Run yang memiliki konfigurasi *autoscaling* multi-instance berbayar, layanan *container* gratis umumnya berjalan pada satu *instance* dengan batasan resource tertentu dan berpotensi mengalami *sleep/idle* jika lama tidak diakses (sehingga perlu dilakukan *warm-up* `GET /health` sebelum demo).
3. **Biaya yang Tidak Diukur:** Biaya koneksi internet lokal, listrik, dan perangkat pengujian lokal tidak diukur dalam laporan cloud ini.
4. **Rencana *Teardown*:** Setelah presentasi/demo selesai, layanan (*service/app*) pada dashboard Snapdeploy akan dihapus atau dinonaktifkan dan disimpan bukti tangkapan layarnya.
