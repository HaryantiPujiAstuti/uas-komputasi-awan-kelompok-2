# Laporan Analisis dan Pemodelan Prediksi Rings Abalone

## 1. Tujuan, Sumber Data, dan Ringkasan Dataset
- **Rumusan masalah**: Memprediksi jumlah cincin cangkang abalone (`Rings`) sebagai variabel respon kuantitatif berdasarkan ukuran fisik dan bobot tubuh abalone.
- **Sumber data dan akses**: Data bersumber dari dataset Abalone (`Dataset_Abalone_Lengkap.xlsx`, merujuk pada UCI Machine Learning Repository Abalone Dataset berlisensi CC BY 4.0) yang diakses pada 21 November 2026 melalui `https://archive.ics.uci.edu/dataset/1/abalone` dan berkas lokal proyek.
- **Deskripsi dan ringkasan EDA**: Dataset terdiri atas **4.177 baris** dan **9 kolom** tanpa nilai hilang maupun baris duplikat. Berdasarkan eksplorasi awal, terdapat 2 baris dengan nilai `Height = 0`, sedangkan korelasi linear tertinggi terhadap `Rings` ditunjukkan oleh `Shell weight` sebesar **0,63**.
- **Perlakuan `Height = 0` dan skala data**: Dua baris dengan `Height = 0` tetap dipertahankan di dalam alur pemrosesan agar tidak membuang observasi secara arbitrer ketika data masih dapat ditangani pada tahap praproses. Selain itu, variabel kontinu pada dataset mengikuti skala standar UCI (telah dibagi `200`), sehingga data baru yang dikirim ke API juga wajib menggunakan skala yang sama agar perbandingan dan prediksi tetap konsisten.

## 2. Pembagian Data dan Pencegahan Data Leakage
- Dataset dibagi menjadi data latih (`train`) dan data uji (`test`) dengan proporsi **80:20** (`random_state=42`), dan data uji tidak digunakan selama proses seleksi model maupun penentuan konfigurasi akhir.
- Seluruh transformasi praproses (`SimpleImputer`, `StandardScaler`, dan `OneHotEncoder` di dalam `ColumnTransformer`) disatukan dalam `Pipeline` bersama model dengan pengaturan `handle_unknown="ignore"`, sementara `Rings` dikeluarkan dari matriks fitur agar tidak menimbulkan kebocoran informasi.

## 3. Baseline dan Seleksi Model Kandidat
- **Baseline**: Prediksi rata-rata `Rings` pada data latih digunakan sebagai tolok ukur awal (*benchmark*) untuk menilai apakah model regresi memberikan peningkatan nyata.
- **Evaluasi validasi silang (5-fold CV pada data latih)**:
  - `Gradient Boosting`: RMSE CV `2.1436`, MAE CV `1.5180`.
  - `Random Forest`: RMSE CV `2.1548`.
  - `Ridge`: RMSE CV `2.2287`.
- `Gradient Boosting` dipilih sebagai model terbaik karena memperoleh galat validasi silang paling rendah di antara kandidat yang diuji, kemudian dilatih ulang pada seluruh data latih sebelum dievaluasi pada data uji.

## 4. Hasil Evaluasi pada Test Set
- **Model terpilih**: `Gradient Boosting` (`GradientBoostingRegressor`), selaras dengan artefak pada `model.joblib` dan catatan metrik di `metrics.json`.
- **Performa pada test set**: MAE `1.5761`, RMSE `2.2480`, dan R² `0.5332`.
- **Perbandingan dengan baseline**: Model `Gradient Boosting` mengungguli *baseline* pada data uji dengan menurunkan galat dari MAE `2.3848` menjadi `1.5761` dan RMSE `3.2906` menjadi `2.2480`, sekaligus meningkatkan R² dari `-0.0003` menjadi `0.5332`. Kedekatan nilai MAE *test set* (`1.5761`) dengan MAE *cross-validation* (`1.5180`) juga menunjukkan tidak adanya indikasi *overfitting* yang mencolok.

## 5. Interpretasi Plot dan Keterbatasan
- Pada plot **Aktual vs Prediksi** dan **Plot Residual** (`docs/evidence/evaluasi_test_set.png`), titik prediksi mengikuti arah diagonal secara umum, tetapi model cenderung melakukan *underprediction* (menaksir lebih rendah dari nilai aktual) pada pengamatan dengan `Rings` yang tinggi.
- Pola garis-garis miring pada plot residual merupakan karakteristik yang wajar karena `Rings` merupakan variabel cacahan/bilangan bulat.
- **Keterbatasan**: Model menghasilkan estimasi kontinu dengan tingkat ketidakpastian yang lebih besar pada nilai `Rings` tinggi, sehingga keandalan prediksi bergantung pada akurasi pengukuran fisik di lapangan serta kesesuaian distribusi data input terhadap data latih.

## 6. Reproduksi Hasil
1. Pastikan posisi kerja berada di *branch* `main` (setelah PR di-*merge*) pada direktori utama repositori.
2. Pasang *library* yang diperlukan pada lingkungan Python:
   ```powershell
   pip install pandas numpy scikit-learn==1.9.1 matplotlib seaborn openpyxl joblib