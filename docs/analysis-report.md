# Laporan Analisis dan Pemodelan Prediksi Rings Abalone

## 1. Tujuan, Sumber Data, dan Ringkasan Dataset
- **Rumusan masalah**: Memprediksi variabel respon `Rings` (jumlah cincin cangkang abalone) berdasarkan variabel prediktor ukuran fisik dan bobot abalone.
- **Sumber data dan akses**: Dataset Abalone (`Dataset_Abalone_Lengkap.xlsx`, merujuk pada UCI Machine Learning Repository Abalone Dataset dengan lisensi CC BY 4.0) diakses pada 21 November 2026 melalui tautan `https://archive.ics.uci.edu/dataset/1/abalone` dan berkas lokal proyek.
- **Deskripsi dan ringkasan EDA**: Dataset terdiri atas **4.177 baris** dan **9 kolom** tanpa data hilang maupun data duplikat. Pada eksplorasi data ditemukan 2 baris dengan nilai `Height = 0`, dan korelasi linear tertinggi terhadap `Rings` ditunjukkan oleh `Shell weight` sebesar **0,63**.

## 2. Pembagian Data dan Pencegahan Data Leakage
- Dataset dibagi menjadi data latih (`train`) dan data uji (`test`) dengan proporsi **80:20** (`random_state=42`), dan proses pemilihan model serta evaluasi akhir tidak menggunakan data uji.
- Seluruh tahapan praproses (`SimpleImputer`, `StandardScaler`, dan `OneHotEncoder` melalui `ColumnTransformer`) dibungkus di dalam `Pipeline` bersama estimator, dengan `handle_unknown="ignore"` dan `Rings` dipisahkan agar tidak masuk sebagai fitur.

## 3. Baseline dan Seleksi Model Kandidat
- **Model baseline**: Prediksi konstan menggunakan nilai rata-rata `Rings` dari data latih sebagai acuan pembanding.
- **Validasi silang (5-fold CV pada data latih)**:
  - `Gradient Boosting`: RMSE validasi silang `2.1436`, MAE validasi silang `1.5180`.
  - `Random Forest` dan `Ridge Regression` juga dibandingkan pada skema 5-fold cross-validation yang sama, dan `Gradient Boosting` terpilih karena mencatat galat validasi silang terendah.
- Model terpilih kemudian dilatih ulang pada seluruh data latih dan diuji pada data uji.

## 4. Hasil Evaluasi pada Test Set
- **Model terpilih**: `Gradient Boosting` (`GradientBoostingRegressor`) sesuai `model.joblib` dan `metrics.json`.
- **Performa model terpilih pada data uji**: MAE `1.5761`, RMSE `2.2480`, dan R² `0.5332`.
- **Perbandingan dengan baseline**: Model `Gradient Boosting` mengungguli *baseline* pada data uji (MAE `1.5761` vs `2.3848`, RMSE `2.2480` vs `3.2906`, dan R² `0.5332` vs `-0.0003`).

## 5. Interpretasi Plot dan Keterbatasan
- Berdasarkan plot **Aktual vs Prediksi** dan **Plot Residual** (`docs/evidence/evaluasi_test_set.png`), model cenderung menaksir terlalu rendah (*underpredict*) untuk nilai `Rings` yang tinggi.
- Pola garis-garis miring pada plot residual merupakan hal yang wajar karena nilai target `Rings` berbentuk bilangan bulat.
- **Keterbatasan**: Prediksi bersifat estimasi numerik dengan galat yang lebih terasa pada nilai `Rings` besar, sehingga bergantung pada kualitas pengukuran input dan kesesuaian distribusi data baru terhadap data latih.

## 6. Reproduksi Hasil
1. Pastikan berada di *branch* `main` (setelah PR di-*merge*) pada direktori utama repositori.
2. Jalankan perintah berikut di terminal:
   ```powershell
   python src/analysis/train.py