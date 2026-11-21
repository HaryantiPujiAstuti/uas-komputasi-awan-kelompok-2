# Laporan Analisis dan Pemodelan Prediksi Rings Abalone

## 1. Tujuan dan Dataset
- **Rumusan masalah**: Memprediksi variabel respon kontinu `Rings` (jumlah cincin cangkang abalone) berdasarkan variabel prediktor pengukuran fisik dan bobot abalone.
- **Sumber data**: Dataset Abalone (`Dataset_Abalone_Lengkap.xlsx`), mencakup variabel kategorikal `Sex` (`M`, `F`, `I`) serta variabel numerik `Length`, `Diameter`, `Height`, `Whole weight`, `Shucked weight`, `Viscera weight`, dan `Shell weight`, dengan target `Rings`.

## 2. Pembagian Data dan Pencegahan Data Leakage
- Data dibagi menjadi data latih (`train`) dan data uji (`test`) dengan proporsi **80:20** (`random_state=42`) sejak awal sebelum eksplorasi lanjutan/pemilihan model agar evaluasi pada data uji tetap objektif.
- Seluruh proses praproses (`SimpleImputer`, `StandardScaler`, dan `OneHotEncoder` melalui `ColumnTransformer`) disusun di dalam `Pipeline` bersama model sehingga parameter imputasi, penskalaan, dan encoding hanya dipelajari dari data latih.

## 3. Baseline dan Seleksi Model Kandidat
- **Model baseline**: Prediksi konstan menggunakan nilai rata-rata `Rings` dari data latih sebagai acuan minimum.
- **Model kandidat**: `Ridge Regression`, `Random Forest` (`RandomForestRegressor`), dan `Gradient Boosting` (`GradientBoostingRegressor`) dibandingkan menggunakan *5-fold cross-validation* pada data latih berdasarkan galat prediksi.
- Model dengan performa *cross-validation* terbaik dilatih ulang pada seluruh data latih, lalu dievaluasi satu kali pada *test set*.

## 4. Ringkasan Evaluasi pada Test Set
- **Model terpilih**: Random Forest (`RandomForestRegressor`)[cite: 2]
- **Baseline Test**: MAE `2.3848` | RMSE `3.2906` | R² `-0.0003`[cite: 2]
- **Random Forest Test**: MAE `1.5465` | RMSE `2.2142` | R² `0.5471`[cite: 2]
- Secara keseluruhan, Random Forest menurunkan galat rata-rata (MAE dan RMSE) dan meningkatkan proporsi keragaman yang dapat dijelaskan (R²) dibanding *baseline* pada data uji[cite: 2].

## 5. Interpretasi Plot dan Keterbatasan
- Berdasarkan plot **Aktual vs Prediksi** dan **Plot Residual** (`docs/evidence/evaluasi_test_set.png`), prediksi mengikuti pola hubungan positif dengan nilai aktual, tetapi ragam residual cenderung membesar pada pengamatan dengan `Rings` tinggi[cite: 3, 17].
- **Keterbatasan**: Model regresi ini menghasilkan estimasi numerik dengan tingkat galat yang masih terasa pada nilai ekstrem/tinggi, serta sangat bergantung pada ketepatan pengukuran fisik dan kesesuaian distribusi data baru terhadap data latih.

## 6. Reproduksi Hasil
1. Pastikan berada di *branch* `analysis-abalone` pada direktori utama repositori[cite: 12, 13].
2. Jalankan perintah:
   ```powershell
   python src/analysis/train.py