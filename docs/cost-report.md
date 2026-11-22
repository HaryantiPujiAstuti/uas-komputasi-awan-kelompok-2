# Laporan Estimasi dan Realisasi Biaya Cloud

## 1. Informasi Provider dan Layanan
- **Penyedia Layanan Cloud:** Google Cloud Platform (GCP)
- **Layanan Komputasi:** Google Cloud Run (Managed Container)
- **Region:** `asia-southeast2` (Jakarta)
- **Sumber Harga Resmi:** [Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator) & [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- **Tanggal Estimasi Awal:** 22 November 2026

---

## 2. Asumsi Penggunaan untuk Estimasi Awal
Untuk kebutuhan pengembangan, pengujian beban (*load test*), dan demo UAS selama periode proyek (± 1 minggu), digunakan asumsi konfigurasi dan trafik sebagai berikut:
- **Alokasi CPU:** 1 vCPU (hanya dialokasikan saat memproses *request* / *CPU only during request processing*).
- **Alokasi Memori (RAM):** 512 MiB.
- **Jumlah Instance:** Minimum `0` (*scale-to-zero*), Maksimum `2` (`max instances = 2`).
- **Estimasi Volume Permintaan:** 10.000 *request* per bulan (mencakup pengujian fungsional, *uptime check* `/health`, *load test* 300 *request*, dan demo presentasi).
- **Rata-rata Durasi Eksekusi per Request:** 200 ms (0,2 detik).
- **Layanan Pendukung:** Cloud Logging dan Artifact Registry (penyimpanan *container image* berukuran < 500 MB).

---

## 3. Perbandingan Estimasi vs Realisasi Biaya

*(Catatan: Sesuai pedoman proyek, komponen biaya yang belum berjalan pada tahap pra-deployment dicatat sebagai `tidak diukur` dan akan diperbarui setelah layanan aktif serta melewati masa pengamatan billing).*

| Komponen Layanan | Estimasi Biaya (Asumsi) | Biaya Aktual (Realisasi) | Selisih | Keterangan |
|---|---|---|---|---|
| **Cloud Run (CPU & Memory)** | $0,00 (Rp0) — masuk dalam *Always Free Tier* GCP (2 juta *request*, 180.000 vCPU-detik, dan 360.000 GiB-detik per bulan) | `tidak diukur` | `tidak diukur` | Menunggu proses deployment dan pengamatan billing harian |
| **Artifact Registry (Storage Image)** | $0,00 (Rp0) — masuk dalam *Free Tier* (hingga 0,5 GB penyimpanan per bulan) | `tidak diukur` | `tidak diukur` | Ukuran image Docker diperkirakan < 500 MB |
| **Cloud Logging & Monitoring** | $0,00 (Rp0) — masuk dalam kuota gratis bulanan (50 GiB log/bulan) | `tidak diukur` | `tidak diukur` | Pengamatan log dilakukan selama periode aktif layanan |
| **Total Biaya** | **$0,00 (Rp0)** | `tidak diukur` | `tidak diukur` | Periode pengamatan aktual: *(diisi setelah deploy)* |

---

## 4. Analisis dan Pengendalian Biaya
1. **Pemanfaatan *Scale-to-Zero*:** Dengan konfigurasi `min instances = 0`, tidak ada biaya komputasi yang terpakai saat layanan tidak menerima *request*.
2. **Pembatasan *Max Instances*:** Konfigurasi `max instances = 2` diterapkan sebagai pengaman untuk mencegah lonjakan tagihan apabila terjadi trafik tidak wajar pada endpoint publik.
3. **Budget Alert:** Peringatan anggaran (*budget alert*) dipasang pada akun cloud sebelum layanan dijalankan untuk memantau potensi pemakaian di luar kuota gratis.
4. **Biaya yang Tidak Diukur:** Biaya transfer data jaringan keluar (*egress*) antar-region dalam skala kecil (< 1 GB/bulan) dan biaya listrik/perangkat pengembangan lokal tidak diukur dalam laporan cloud ini.
5. **Rencana *Teardown*:** Seluruh *service* Cloud Run dan *image* di Artifact Registry akan dihapus segera setelah presentasi/demo selesai untuk memastikan tidak ada biaya berjalan setelah proyek berakhir.
