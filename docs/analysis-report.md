# Laporan Analisis dan Pemodelan Prediksi Rings Abalone

## 1. Tujuan, Sumber Data, dan Ringkasan Dataset

- **Rumusan masalah**: Membangun model regresi untuk memprediksi jumlah cincin cangkang abalone (`Rings`) sebagai variabel respons kuantitatif berdasarkan karakteristik jenis kelamin dan ukuran fisik tubuh abalone. Jumlah cincin dapat digunakan untuk memperkirakan umur biologis abalone, yang secara umum dihitung menggunakan rumus $\text{Umur} = \text{Rings} + 1{,}5$ tahun.

- **Sumber data dan akses**: Data bersumber dari dataset Abalone (`Dataset_Abalone_Lengkap.xlsx`) yang merujuk pada *UCI Machine Learning Repository — Abalone Dataset* dengan lisensi CC BY 4.0. Dataset diakses pada 21 November 2026 melalui https://archive.ics.uci.edu/dataset/1/abalone serta berkas lokal yang tersedia pada direktori utama repositori.

- **Struktur dan ringkasan EDA**:
  - Dataset terdiri atas **4.177 baris** pengamatan dan **9 kolom**, yang mencakup **1 variabel target** (`Rings`) dan **8 variabel prediktor**.
  - **Fitur kategorikal (1)**: `Sex`, dengan kategori `M` (*Male*), `F` (*Female*), dan `I` (*Infant*).
  - **Fitur numerik (7)**: `Length`, `Diameter`, `Height`, `Whole weight`, `Shucked weight`, `Viscera weight`, dan `Shell weight`.
  - Tidak ditemukan nilai hilang (*missing values*) maupun baris duplikat pada dataset mentah.
  - Korelasi linear (*Pearson*) tertinggi terhadap variabel target `Rings` ditunjukkan oleh fitur `Shell weight`, yaitu sebesar **0,63**. Fitur dimensi fisik dan bobot lainnya juga menunjukkan korelasi positif terhadap variabel target Rings serta korelasi yang relatif kuat antar-prediktor, sehingga terdapat indikasi multikolinearitas pada fitur ukuran dan berat.

- **Perlakuan `Height = 0` dan skala data**:
  - Berdasarkan eksplorasi awal pada `eda_v2.ipynb`, terdapat **2 baris** dengan nilai `Height = 0` dari total 4.177 baris pengamatan atau sekitar **0,05%**. Kedua pengamatan tersebut tetap dipertahankan dalam dataset karena tidak dilakukan penghapusan khusus terhadap nilai tersebut. Dampaknya terhadap kinerja model belum diuji secara terpisah melalui analisis sensitivitas.
  - Seluruh fitur numerik menggunakan nilai pada **skala asli dataset UCI Abalone**. Tidak dilakukan pembagian nilai fitur dengan `200` sebelum proses pelatihan model.
  - Standardisasi fitur numerik dilakukan secara otomatis menggunakan `StandardScaler()` dalam pipeline praproses. Dengan demikian, data input yang dikirim ke layanan API harus menggunakan nilai pada skala asli dataset, bukan nilai yang telah dibagi `200`, serta mengikuti nama fitur yang tercantum dalam `src/app/model/features.json` dan `docs/interface-contract.md`.

## 2. Pembagian Data dan Pencegahan Data Leakage
- **Skema pemisahan data**: Dataset dibagi secara acak menjadi **data latih (*train set*) sebesar 80% (`3.341` baris)** dan **data uji (*test set*) sebesar 20% (`836` baris)** menggunakan `train_test_split(..., test_size=0.20, random_state=42)`. Data uji tidak digunakan dalam proses *fitting* praproses, pelatihan model, maupun pemilihan model melalui *cross-validation*; evaluasi akhir dilakukan menggunakan data uji setelah model terbaik ditentukan berdasarkan data latih. *(Catatan: eksplorasi data awal dilakukan pada keseluruhan dataset 4.177 baris).*
- **Integrasi `Pipeline` dan `ColumnTransformer`**:
  - Seluruh langkah praproses disusun secara modular di dalam `build_preprocessor(num_cols, cat_cols)` (`src/analysis/preprocess.py`) yang mengembalikan objek `ColumnTransformer`:
    - **Cabang numerik (`num_cols`)**: `SimpleImputer(strategy="median")` diikuti `StandardScaler()`.
    - **Cabang kategorikal (`cat_cols`)**: `SimpleImputer(strategy="most_frequent")` diikuti `OneHotEncoder(handle_unknown="ignore")`.
  - Objek `ColumnTransformer` dibungkus bersama estimator ke dalam `sklearn.pipeline.Pipeline`, sehingga parameter imputasi dan penskalaan hanya dihitung (*fit*) pada *fold* pelatihan di setiap iterasi *cross-validation* dan pada `X_train` saat pelatihan akhir. Variabel target `Rings` dipisahkan sejak awal agar tidak ikut menjadi fitur.

## 3. Baseline dan Seleksi Model Kandidat
- **Model *baseline***: Sebagai patokan dasar (*benchmark*), digunakan prediksi konstan berupa nilai rata-rata `Rings` dari data latih (`y_train.mean()`) untuk mengevaluasi peningkatan kinerja model regresi.
- **Evaluasi validasi silang (5-fold CV pada data latih)**:
  - Tiga model regresi kandidat dibandingkan menggunakan `KFold(n_splits=5, shuffle=True, random_state=42)` dengan kriteria utama RMSE terendah, merujuk pada `docs/evidence/metrics.json`:

  | Model Kandidat | MAE CV | RMSE CV | R² CV |
  | :--- | :---: | :---: | :---: |
  | **Gradient Boosting (`GradientBoostingRegressor`)** | **1,5180** | **2,1436** | **0,5513** |
  | Random Forest (`RandomForestRegressor`, `n_estimators=200`) | 1,5381 | 2,1548 | 0,5465 |
  | Ridge Regression (`Ridge`, `alpha=1.0`) | 1,5885 | 2,2287 | 0,5140 |

- **Alasan pemilihan model**: `Gradient Boosting` dipilih sebagai model terbaik karena mencatat nilai **RMSE CV terendah (`2,1436`)** dan **MAE CV terendah (`1,5180`)** di antara seluruh model kandidat pada data latih. Model terpilih kemudian dilatih ulang pada seluruh data latih (`3.341` baris) sebelum dievaluasi pada data uji.

## 4. Hasil Evaluasi pada Test Set
- **Spesifikasi model terpilih**: `GradientBoostingRegressor(random_state=42)` dalam satu `Pipeline` utuh bersama `ColumnTransformer`, disimpan sebagai `src/app/model/model.joblib` pada lingkungan dengan `scikit-learn==1.9.1`.
- **Perbandingan *Baseline* vs Model Terpilih pada *Test Set* (`836` baris)**:

  | Model / Pendekatan | MAE (*Test*) | RMSE (*Test*) | R² (*Test*) | Keterangan |
  | :--- | :---: | :---: | :---: | :--- |
  | *Baseline* (Rata-rata `y_train`) | 2,3848 | 3,2906 | -0,0003 | Patokan dasar tanpa fitur prediktor |
  | **Gradient Boosting (Model Terpilih)** | **1,5761** | **2,2480** | **0,5332** | **MAE dan RMSE lebih rendah serta R² lebih tinggi dari baseline** |

- **Ringkasan kinerja pada data uji**:
  - Model `Gradient Boosting` menghasilkan nilai MAE dan RMSE yang lebih rendah serta nilai R² yang lebih tinggi dibandingkan *baseline*. Hasil tersebut menunjukkan bahwa penggunaan fitur karakteristik fisik abalone mampu meningkatkan kemampuan prediksi jumlah cincin dibandingkan pendekatan yang hanya menggunakan rata-rata data latih.
  - Secara numerik, MAE turun sekitar **33,9%** (dari `2,3848` menjadi `1,5761`), RMSE turun sekitar **31,7%** (dari `3,2906` menjadi `2,2480`), dan R² meningkat dari `-0,0003` menjadi `0,5332`.
  - Nilai MAE dan RMSE pada data uji (`1,5761` dan `2,2480`) relatif berdekatan dengan hasil validasi silang (`1,5180` dan `2,1436`), yang menunjukkan bahwa kinerja pada data uji relatif konsisten dengan kinerja selama validasi silang, meskipun evaluasi tersebut belum sepenuhnya menjamin tidak adanya *overfitting*.

## 5. Evaluasi Visual dan Analisis Residual

Evaluasi visual dilakukan menggunakan grafik perbandingan nilai aktual dan prediksi serta plot residual pada data pengujian (*test set*). Grafik aktual dan prediksi digunakan untuk melihat kesesuaian hasil prediksi terhadap nilai Rings sebenarnya. Hasil visual menunjukkan bahwa prediksi model cenderung mengikuti pola nilai aktual, meskipun masih terdapat penyimpangan pada beberapa pengamatan, terutama pada nilai Rings yang relatif tinggi.

Plot residual digunakan untuk mengamati pola kesalahan prediksi, dengan residual dihitung sebagai selisih antara nilai aktual dan nilai prediksi. Residual yang berada di sekitar garis nol menunjukkan bahwa kesalahan prediksi relatif kecil. Namun, penyebaran residual yang semakin besar pada beberapa nilai prediksi mengindikasikan bahwa kesalahan model belum sepenuhnya seragam.

Secara keseluruhan, hasil evaluasi visual menunjukkan bahwa model Gradient Boosting mampu menangkap pola hubungan antara fitur-fitur abalone dan jumlah Rings, meskipun akurasi prediksi masih dapat berbeda pada rentang nilai Rings tertentu.

## 6. Keterbatasan Model dan Implikasi Operasional
- **Keterbatasan akurasi pada nilai tinggi**: Model masih cenderung menaksir lebih rendah pada abalone dengan jumlah cincin yang tinggi karena pertumbuhan ukuran/bobot melambat pada fase lanjut dan data pada rentang tinggi lebih jarang.
- **Belum ada pengujian statistik formal**: Pernyataan peningkatan kinerja didasarkan pada perbandingan metrik evaluasi (`MAE`, `RMSE`, `R²`) dan pemeriksaan visual plot, bukan uji signifikansi statistik formal maupun uji heteroskedastisitas khusus.
- **Implikasi operasional & integrasi API**: Keluaran prediksi berupa nilai kontinu (`9,8326` pada sampel uji standar), sehingga pemanfaatan untuk estimasi umur bersifat perkiraan. Integrasi API perlu menjaga konsistensi versi `scikit-learn==1.9.1`, kesesuaian urutan/nama fitur dengan `src/app/model/features.json` dan `docs/interface-contract.md`, serta skala input sesuai data latih UCI.

## 7. Reproduksi Hasil
1. Pastikan posisi kerja berada di *branch* `main` (setelah PR di-*merge*) pada direktori utama repositori (`uas-komputasi-awan-kelompok-2`).
2. Pasang *library* yang diperlukan dari *root* repositori:
   ```powershell
   pip install -r requirements.txt