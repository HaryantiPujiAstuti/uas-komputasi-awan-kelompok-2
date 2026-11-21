"""
Skrip Training & Evaluasi Model Prediksi Umur Abalone (src/analysis/train.py)
Peran: Orang 1 (Analysis Layer)
Deskripsi: Membaca dataset Abalone, melakukan split tanpa data leakage, membandingkan
           baseline dengan model kandidat via Cross-Validation, mengevaluasi pada test set
           satu kali, dan mengekspor artefak model untuk API (Orang 3).
"""

import json
import os
import platform
import sys

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline

from preprocess import CAT_COLS, NUM_COLS, TARGET_COL, build_preprocessor

RANDOM_STATE = 42
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/abalone/abalone.data"
LOCAL_CSV_PATH = "src/analysis/data/abalone.csv"
LOCAL_RAW_PATH = "abalone.data"
LOCAL_XLSX_PATH = "Dataset_Abalone_Lengkap.xlsx"


def load_abalone_data():
    """Memuat data dari file lokal jika ada, atau mengunduh langsung dari UCI Repository."""
    columns = ["Sex"] + NUM_COLS + [TARGET_COL]

    if os.path.exists(LOCAL_CSV_PATH):
        df = pd.read_csv(LOCAL_CSV_PATH)
    elif os.path.exists(LOCAL_RAW_PATH):
        df = pd.read_csv(LOCAL_RAW_PATH, header=None, names=columns)
    elif os.path.exists(LOCAL_XLSX_PATH):
        df = pd.read_excel(LOCAL_XLSX_PATH, sheet_name="Dataset_Abalone")
    else:
        print(f"Mengunduh dataset dari {DATA_URL} ...")
        df = pd.read_csv(DATA_URL, header=None, names=columns)
        os.makedirs(os.path.dirname(LOCAL_CSV_PATH), exist_ok=True)
        df.to_csv(LOCAL_CSV_PATH, index=False)

    return df


def main():
    os.makedirs("src/app/model", exist_ok=True)
    os.makedirs("docs/evidence", exist_ok=True)

    # 1. Memuat Data
    df = load_abalone_data()
    print(f"Total observasi awal: {len(df)} baris, {df.shape[1]} kolom")

    # Cek duplikasi persis
    dup_count = df.duplicated().sum()
    print(f"Jumlah baris duplikat: {dup_count}")

    feature_cols = CAT_COLS + NUM_COLS
    X = df[feature_cols].copy()
    y = df[TARGET_COL].copy()

    # 2. Train-Test Split (80:20) SEBELUM preprocessing untuk mencegah data leakage
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE
    )
    print(f"Train set: {len(X_train)} baris | Test set: {len(X_test)} baris")

    # 3. Definisi Baseline & Model Kandidat
    models = {
        "Baseline (Dummy Mean)": DummyRegressor(strategy="mean"),
        "Ridge Regression": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_leaf=4, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=150, learning_rate=0.05, max_depth=4, random_state=RANDOM_STATE
        ),
    }

    # 4. Validasi Silang (5-Fold CV) HANYA pada Train Set
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }

    cv_summary = {}
    best_model_name = None
    best_cv_rmse = float("inf")
    best_pipeline = None

    print("\n=== HASIL 5-FOLD CROSS-VALIDATION (TRAIN SET) ===")
    for name, estimator in models.items():
        pipe = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(NUM_COLS, CAT_COLS)),
                ("regressor", estimator),
            ]
        )
        scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
        cv_mae = float(-np.mean(scores["test_mae"]))
        cv_rmse = float(-np.mean(scores["test_rmse"]))
        cv_r2 = float(np.mean(scores["test_r2"]))

        cv_summary[name] = {
            "cv_mae": round(cv_mae, 4),
            "cv_rmse": round(cv_rmse, 4),
            "cv_r2": round(cv_r2, 4),
        }
        print(f"{name:24s} -> CV MAE: {cv_mae:.4f} | CV RMSE: {cv_rmse:.4f} | CV R2: {cv_r2:.4f}")

        if cv_rmse < best_cv_rmse:
            best_cv_rmse = cv_rmse
            best_model_name = name
            best_pipeline = pipe

    # 5. Latih Ulang Model Terbaik pada Seluruh Train Set & Evaluasi SATU KALI pada Test Set
    print(f"\nModel terbaik berdasarkan CV RMSE: {best_model_name}")
    best_pipeline.fit(X_train, y_train)

    y_pred_test = best_pipeline.predict(X_test)
    test_mae = float(mean_absolute_error(y_test, y_pred_test))
    test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
    test_r2 = float(r2_score(y_test, y_pred_test))

    # Evaluasi baseline pada test set untuk perbandingan objektif
    baseline_pipe = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(NUM_COLS, CAT_COLS)),
            ("regressor", models["Baseline (Dummy Mean)"]),
        ]
    )
    baseline_pipe.fit(X_train, y_train)
    y_pred_base = baseline_pipe.predict(X_test)
    base_test_mae = float(mean_absolute_error(y_test, y_pred_base))
    base_test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_base)))
    base_test_r2 = float(r2_score(y_test, y_pred_base))

    beats_baseline = bool(test_rmse < base_test_rmse and test_mae < base_test_mae)

    print("\n=== HASIL EVALUASI AKHIR (TEST SET - DIEVALUASI 1 KALI) ===")
    print(f"Baseline Test       -> MAE: {base_test_mae:.4f} | RMSE: {base_test_rmse:.4f} | R2: {base_test_r2:.4f}")
    print(f"{best_model_name:19s} -> MAE: {test_mae:.4f} | RMSE: {test_rmse:.4f} | R2: {test_r2:.4f}")
    print(f"Mengungguli Baseline: {beats_baseline}")

    # 6. Simpan Artefak Model & Metadata untuk Orang 3 (API Layer)
    model_path = "src/app/model/model.joblib"
    joblib.dump(best_pipeline, model_path)

    features_info = {
        "model_version": "v1.0.0",
        "target": TARGET_COL,
        "target_description": "Jumlah cincin cangkang (Rings); estimasi umur (tahun) = Rings + 1.5",
        "feature_order": feature_cols,
        "categorical_features": {
            "Sex": {
                "type": "string",
                "allowed_values": ["M", "F", "I"],
                "description": "M = Male, F = Female, I = Infant",
            }
        },
        "numerical_features": {
            col: {"type": "float", "min_suggested": 0.0} for col in NUM_COLS
        },
        "sample_request": {
            "features": {
                "Sex": "M",
                "Length": 0.455,
                "Diameter": 0.365,
                "Height": 0.095,
                "Whole weight": 0.514,
                "Shucked weight": 0.2245,
                "Viscera weight": 0.101,
                "Shell weight": 0.15,
            }
        },
        "environment": {
            "python_version": platform.python_version(),
            "scikit_learn_version": sklearn.__version__,
            "pandas_version": pd.__version__,
            "joblib_version": joblib.__version__,
        },
    }
    with open("src/app/model/features.json", "w", encoding="utf-8") as f:
        json.dump(features_info, f, indent=2)

    metrics_info = {
        "selected_model": best_model_name,
        "random_state": RANDOM_STATE,
        "split_ratio": {"train": len(X_train), "test": len(X_test)},
        "cross_validation_5fold": cv_summary,
        "test_set_evaluation": {
            "baseline": {
                "mae": round(base_test_mae, 4),
                "rmse": round(base_test_rmse, 4),
                "r2": round(base_test_r2, 4),
            },
            "selected_model": {
                "mae": round(test_mae, 4),
                "rmse": round(test_rmse, 4),
                "r2": round(test_r2, 4),
            },
            "beats_baseline": beats_baseline,
            "rmse_improvement_pct": round(((base_test_rmse - test_rmse) / base_test_rmse) * 100, 2),
        },
        "environment": features_info["environment"],
    }
    with open("docs/evidence/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_info, f, indent=2)

    print("\nArtefak berhasil disimpan:")
    print("- src/app/model/model.joblib")
    print("- src/app/model/features.json")
    print("- docs/evidence/metrics.json")


if __name__ == "__main__":
    main()
