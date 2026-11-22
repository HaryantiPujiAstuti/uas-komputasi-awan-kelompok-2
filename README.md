# Model Prediktif sebagai Cloud API – Abalone

## 1. Deskripsi Proyek

Proyek ini dikembangkan untuk memenuhi tugas UAS Komputasi Awan dengan membangun model prediktif menggunakan dataset Abalone. Model digunakan untuk memprediksi jumlah cincin (*Rings*) berdasarkan karakteristik fisik abalone.

Proyek mencakup tahapan analisis data, preprocessing, pelatihan dan evaluasi model, penyimpanan model, serta pengembangan layanan prediksi berbasis Cloud API.

## 2. Dataset

Dataset yang digunakan adalah **Abalone** dari UCI Machine Learning Repository. Dataset ini digunakan untuk memprediksi jumlah cincin (*Rings*) berdasarkan karakteristik fisik abalone.

- Sumber: [UCI Machine Learning Repository – Abalone](https://archive.ics.uci.edu/dataset/1/abalone)
- File dataset dalam repository: `Dataset_Abalone_Lengkap.xlsx`
- Jumlah observasi: 4.177 baris
- Jumlah variabel: 9 kolom (8 prediktor dan 1 target)
- Variabel target: `Rings`
- Tahun publikasi dataset: 1994
- Lisensi: Creative Commons Attribution 4.0 International (CC BY 4.0)
- DOI: [10.24432/C55C7W](https://doi.org/10.24432/C55C7W)
- Tanggal akses sumber: 22 November 2026

Variabel prediktor terdiri atas `Sex`, `Length`, `Diameter`, `Height`, `Whole weight`, `Shucked weight`, `Viscera weight`, dan `Shell weight`.

**Sitasi dataset:**

Nash, W., Sellers, T., Talbot, S., Cawthorn, A., & Ford, W. (1994). *Abalone* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55C7W.

## 3. Struktur Repository

```text
uas-komputasi-awan-kelompok-2/
│
├── docs/
│   ├── evidence/
│   ├── ai-disclosure.md
│   ├── analysis-report.md
│   ├── architecture.md
│   ├── interface-contract.md
│   └── role-log.md
│
├── src/
│   ├── analysis/
│   │   ├── data_loader.py
│   │   ├── eda_v2.ipynb
│   │   ├── preprocess.py
│   │   └── train.py
│   │
│   └── app/
│       └── model/
│           ├── features.json
│           └── model.joblib
│
├── Dataset_Abalone_Lengkap.xlsx
├── requirements.txt
└── README.md
```

Struktur ini menggambarkan komponen proyek yang telah tersedia dan dokumentasi yang disiapkan. Implementasi API serta konfigurasi deployment akan disesuaikan setelah pekerjaan layer terkait selesai.

## 4. Prasyarat

- Python yang kompatibel dengan dependensi pada `requirements.txt`.
- Git untuk mengambil repository.
- Terminal atau PowerShell untuk menjalankan perintah.

## 5. Instalasi

Clone repository:

```bash
git clone https://github.com/HaryantiPujiAstuti/uas-komputasi-awan-kelompok-2.git
```

Masuk ke direktori proyek:

```bash
cd uas-komputasi-awan-kelompok-2
```

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment pada Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

## 6. Menjalankan Analisis dan Pelatihan Model

Pastikan file dataset tersedia sesuai lokasi yang digunakan oleh kode pemuatan data.

Jalankan perintah berikut dari direktori utama repository:

```bash
python src/analysis/train.py
```

Proses tersebut menjalankan tahapan preprocessing, pelatihan, dan evaluasi model.

Artefak utama proyek meliputi:

- `docs/evidence/metrics.json`
- `docs/evidence/evaluasi_test_set.png`
- `src/app/model/model.joblib`
- `src/app/model/features.json`

Penjelasan mengenai analisis, metode, hasil evaluasi, dan keterbatasan model dapat dilihat pada `docs/analysis-report.md`.

## 7. Model dan Preprocessing

Model terbaik berdasarkan hasil evaluasi validasi silang adalah `GradientBoostingRegressor`.

Preprocessing dilakukan menggunakan pipeline yang mencakup penanganan nilai hilang, standardisasi fitur numerik, dan encoding fitur kategorik. Seluruh proses preprocessing ditempatkan dalam pipeline model untuk menghindari kebocoran informasi data.

Model disimpan menggunakan format Joblib, sedangkan informasi fitur tersedia pada `src/app/model/features.json`.

## 8. API

Layanan prediksi dirancang untuk menggunakan model yang telah disimpan pada `src/app/model/model.joblib`.

Rancangan endpoint, format input, output, dan ketentuan validasi dijelaskan dalam `docs/interface-contract.md`.

Petunjuk menjalankan dan menguji API akan dilengkapi setelah implementasi API tersedia dan diverifikasi.

## 9. Dokumentasi Proyek

Dokumentasi proyek tersedia pada direktori `docs/`:

| File | Keterangan |
|---|---|
| `analysis-report.md` | Laporan analisis dan evaluasi model |
| `interface-contract.md` | Rancangan kontrak API |
| `architecture.md` | Rancangan arsitektur sistem |
| `role-log.md` | Catatan pembagian tugas dan kontribusi anggota |
| `ai-disclosure.md` | Pengungkapan penggunaan bantuan AI |

Bukti visualisasi dan hasil evaluasi tersedia pada direktori `docs/evidence/`.

## 10. Pengujian

Evaluasi model dilakukan menggunakan pembagian data latih dan data uji serta validasi silang pada data latih.

Hasil evaluasi model dan baseline dicatat dalam laporan analisis dan file `metrics.json`.

Pengujian endpoint API dan integrasi antarlayer akan didokumentasikan setelah implementasinya tersedia.

## 11. Deployment

Panduan deployment, konfigurasi infrastruktur, serta pengelolaan resource cloud akan dilengkapi berdasarkan teknologi dan layanan yang benar-benar digunakan pada tahap implementasi.

## 12. Status Pengembangan

Repository ini dikembangkan secara bertahap berdasarkan pembagian tanggung jawab setiap anggota kelompok. Dokumentasi API, integrasi, dan deployment akan diperbarui sesuai perkembangan implementasi masing-masing layer.