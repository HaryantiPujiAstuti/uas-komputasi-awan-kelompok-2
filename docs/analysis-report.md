# Laporan Analisis dan Pemodelan Prediksi Rings Abalone

## 1. Tujuan, Sumber Data, dan Ringkasan Dataset
- **Rumusan masalah**: Membangun model regresi untuk memprediksi jumlah cincin cangkang abalone (`Rings`) sebagai variabel respon kuantitatif berdasarkan karakteristik jenis kelamin dan ukuran fisik tubuh abalone. Perkiraan umur biologis abalone umumnya dihitung sebagai $\text{Rings} + 1{,}5$ tahun.
- **Sumber data dan akses**: Data bersumber dari dataset Abalone (`Dataset_Abalone_Lengkap.xlsx`, merujuk pada *UCI Machine Learning Repository — Abalone Dataset* berlisensi CC BY 4.0) yang diakses pada 21 November 2026 melalui `https://archive.ics.uci.edu/dataset/1/abalone` serta berkas lokal pada direktori utama repositori.
- **Struktur dan ringkasan EDA**:
  - Dataset terdiri atas **4.177 baris** pengamatan dan **9 kolom**, terdiri dari **1 variabel target** (`Rings`, bilangan bulat) dan **8 variabel prediktor**:
    - **Fitur kategorikal (1)**: `Sex` (`M` = *Male*, `F` = *Female*, `I` = *Infant*).
    - **Fitur numerik (7)**: `Length`, `Diameter`, `Height`, `Whole weight`, `Shucked weight`, `Viscera weight`, dan `Shell weight`.
  - Tidak ditemukan nilai hilang (*missing values*) maupun baris duplikat pada dataset mentah.
  - Korelasi linear (*Pearson*) tertinggi terhadap variabel target `Rings` ditunjukkan oleh **`Shell weight` sebesar `0,63`**, diikuti oleh fitur dimensi fisik dan bobot lainnya yang juga berkorelasi positif kuat antar-prediktor (indikasi multikolinearitas tinggi pada fitur ukuran dan berat).
- **Perlakuan `Height = 0` dan skala data**:
  - Berdasarkan eksplorasi awal pada `eda_v2.ipynb`, terdapat **2 baris** dengan nilai `Height = 0`. Baris tersebut tetap dipertahankan apa adanya karena hanya mencakup 2 dari 4.177 baris (sekitar **0,05%**), sehingga proporsinya sangat kecil dan tidak memberikan dampak signifikan terhadap parameter maupun performa model.
  - Seluruh fitur kontinu pada dataset UCI berada pada skala yang telah dinormalisasi/dibagi `200`. Oleh karena itu, data input yang dikirim ke layanan API wajib menggunakan skala serta nama kolom yang persis sama dengan skema pada `src/app/model/features.json` dan `docs/interface-contract.md`.

## 2. Pembagian Data dan Pencegahan Data Leakage
- **Skema pemisahan data**: Dataset dipisahkan secara acak menjadi **data latih (*train set*) sebesar 80% (`3.341` baris)** dan **data uji (*test set*) sebesar 20% (`836` baris)** menggunakan `train_test_split(..., test_size=0.20, random_state=42)`. Data uji dikunci sepenuhnya dan tidak pernah dilibatkan dalam proses eksplorasi lanjutan, pemilihan fitur, praproses, maupun seleksi model.
- **Integrasi `Pipeline` dan `ColumnTransformer`**:
  - Seluruh langkah praproses disusun secara modular di dalam `build_preprocessor(num_cols, cat_cols)` (`src/analysis/preprocess.py`) yang mengembalikan objek `ColumnTransformer`:
    - **Cabang numerik (`num_cols`)**: `SimpleImputer(strategy="median")` diikuti `StandardScaler()`.
    - **Cabang kategorikal (`cat_cols`)**: `SimpleImputer(strategy="most_frequent")` diikuti `OneHotEncoder(handle_unknown="ignore")`.
  - Objek `ColumnTransformer` dibungkus bersama estimator ke dalam `sklearn.pipeline.Pipeline`, sehingga parameter imputasi dan penskalaan hanya dihitung (*fit*) pada *fold* pelatihan di setiap iterasi *cross-validation* dan pada `X_train` saat pelatihan akhir. Variabel target `Rings` dipisahkan sejak awal agar tidak terjadi kebocoran fitur.

## 3. Baseline dan Seleksi Model Kandidat
- **Model *baseline***: Sebagai patokan dasar (*benchmark*), digunakan model konstan sederhana berupa nilai rata-rata `Rings` dari data latih (`y_train.mean()`) untuk memprediksi seluruh pengamatan pada data uji.
- **Evaluasi validasi silang (5-fold CV pada data latih)**:
  - Tiga model regresi kandidat dibandingkan menggunakan `KFold(n_splits=5, shuffle=True, random_state=42)` dengan kriteria utama RMSE terendah:

  | Model Kandidat | MAE (5-Fold CV) | RMSE (5-Fold CV) | R² (5-Fold CV) |
  | :--- | :---: | :---: | :---: |
  | **Gradient Boosting (`GradientBoostingRegressor`)** | **1,5180** | **2,1436** | **0,5527** |
  | Random Forest (`RandomForestRegressor`, `n_estimators=200`) | 1,5463 | 2,1548 | 0,5480 |
  | Ridge Regression (`Ridge`, `alpha=1.0`) | 1,5994 | 2,2287 | 0,5167 |

  *(Catatan: nilai MAE dan RMSE pada tabel di atas merupakan ringkasan langsung dari `docs/evidence/metrics.json`; nilai R² CV mengikuti log ringkasan validasi silang pada `metrics.json` saat `train.py` dijalankan).*
- **Alasan pemilihan model**: `Gradient Boosting` dipilih sebagai model terbaik karena menghasilkan nilai **RMSE CV terendah (`2,1436`)** dan **MAE CV terendah (`1,5180`)** dibandingkan `Random Forest` dan `Ridge Regression`. Model terpilih kemudian dilatih ulang pada seluruh data latih (`3.341` baris) sebelum dievaluasi pada data uji.

## 4. Hasil Evaluasi pada Test Set
- **Spesifikasi model terpilih**: `GradientBoostingRegressor(random_state=42)` dalam satu `Pipeline` utuh bersama `ColumnTransformer`, disimpan sebagai `src/app/model/model.joblib` menggunakan lingkungan `Python` dan `scikit-learn==1.9.1`.
- **Perbandingan *Baseline* vs Model Terpilih pada *Test Set* (`836` baris)**:

  | Model / Pendekatan | MAE (*Test*) | RMSE (*Test*) | R² (*Test*) | Keterangan |
  | :--- | :---: | :---: | :---: | :--- |
  | *Baseline* (Rata-rata `y_train`) | 2,3848 | 3,2906 | -0,0003 | Patokan dasar tanpa fitur prediktor |
  | **Gradient Boosting (Model Terpilih)** | **1,5761** | **2,2480** | **0,5332** | **Penurunan galat signifikan di seluruh metrik** |

- **Analisis kuantitatif hasil evaluasi**:
  - Dibandingkan *baseline*, `Gradient Boosting` berhasil menurunkan **MAE sebesar `0,8087` cincin** (turun sekitar **33,9%**, dari `2,3848` menjadi `1,5761`) dan menurunkan **RMSE sebesar `1,0426` cincin** (turun sekitar **31,7%**, dari `3,2906` menjadi `2,2480`).
  - Nilai koefisien determinasi **R² meningkat dari `-0,0003` menjadi `0,5332`**, yang berarti sekitar **53,32%** keragaman jumlah cincin abalone pada data uji mampu dijelaskan oleh model.
  - Selisih yang tipis antara galat validasi silang (`MAE CV = 1,5180`; `RMSE CV = 2,1436`) dan galat pada *test set* (`MAE Test = 1,5761`; `RMSE Test = 2,2480`) menunjukkan kemampuan generalisasi yang stabil tanpa indikasi *overfitting* yang mengkhawatirkan.

## 5. Analisis Residual, Interpretasi Plot, dan Keterbatasan
- **Evaluasi visual (`docs/evidence/evaluasi_test_set.png`)**:
  - **Plot Aktual vs Prediksi**: Sebaran titik prediksi mengikuti garis diagonal ideal ($y = \hat{y}$) dengan baik pada rentang menengah (`Rings` sekitar 6 hingga 13), di mana sebagian besar pengamatan terkonsentrasi. Namun, pada pengamatan dengan nilai `Rings` aktual yang tinggi (di atas 15), titik prediksi cenderung berada di bawah garis diagonal (*underprediction*).
  - **Plot Residual terhadap Nilai Prediksi & Distribusi Residual**:
    - Sebaran residual ($e_i = y_i - \hat{y}_i$) terpusat di sekitar nol pada rentang prediksi rendah hingga menengah, tetapi menunjukkan pola melebar (*heteroskedastisitas*) dan condong positif pada `Rings` tinggi akibat kecenderungan model menaksir lebih rendah untuk abalone berusia tua.
    - Munculnya pola garis-garis miring sejajar pada plot residual merupakan karakteristik alami yang wajar karena variabel respon `Rings` bersifat diskrit (bilangan bulat), sedangkan keluaran `GradientBoostingRegressor` berupa bilangan riil kontinu.
- **Keterbatasan model dan implikasi operasional**:
  - Ukuran fisik dan bobot tubuh abalone cenderung melambat pertumbuhannya setelah mencapai fase dewasa, sehingga fitur morfologi saja kurang sensitif untuk membedakan abalone yang sangat tua (`Rings > 15`).
  - Keluaran prediksi berupa angka kontinu (misalnya `9,83` untuk sampel uji standar), sehingga interpretasi umur biologis bersifat estimasi aproksimatif.
  - Keandalan prediksi saat *deployment* bergantung pada konsistensi skala input (skala UCI dibagi `200`), kelengkapan nama fitur persis sesuai `features.json`, serta kesesuaian versi `scikit-learn==1.9.1`.

## 6. Reproduksi Hasil
1. Pastikan posisi kerja berada di *branch* `main` (setelah PR di-*merge*) pada direktori utama repositori (`uas-komputasi-awan-kelompok-2`).
2. Pasang *library* yang diperlukan (pastikan versi `scikit-learn` sesuai dengan `requirements.txt` proyek, yaitu `1.9.1`):
   ```powershell
   pip install pandas numpy scikit-learn==1.9.1 matplotlib seaborn openpyxl joblib