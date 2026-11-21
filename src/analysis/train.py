import json
import os
import sys
import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from data_loader import load_data
from preprocess import build_preprocessor


def hitung_metrik(y_true, y_pred):
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(root_mean_squared_error(y_true, y_pred)), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, "..", ".."))
    os.chdir(root_dir)

    os.makedirs("src/app/model", exist_ok=True)
    os.makedirs("docs/evidence", exist_ok=True)

    lokasi_data = os.path.join(root_dir, "Dataset_Abalone_Lengkap.xlsx")
    df = load_data(lokasi_data)
    target = "Rings"
    X = df.drop(columns=[target])
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    kolom_kategori = ["Sex"]
    kolom_angka = [c for c in X.columns if c not in kolom_kategori]

    baseline_val = float(y_train.mean())
    pred_baseline = np.full(shape=len(y_test), fill_value=baseline_val)
    metrik_baseline = hitung_metrik(y_test, pred_baseline)

    model_kandidat = {
        "Ridge Regression": Ridge(alpha=1.0, random_state=42),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    }

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_summary = {}
    nama_terbaik = None
    rmse_terbaik = float("inf")
    model_terbaik = None

    for nama, estimator in model_kandidat.items():
        pipa = Pipeline(steps=[
            ("preprocess", build_preprocessor(kolom_angka, kolom_kategori)),
            ("model", estimator),
        ])
        hasil_cv = cross_validate(
            pipa,
            X_train,
            y_train,
            cv=cv,
            scoring={
                "mae": "neg_mean_absolute_error",
                "rmse": "neg_root_mean_squared_error",
                "r2": "r2",
            },
            n_jobs=-1,
        )
        mae_cv = round(float(-np.mean(hasil_cv["test_mae"])), 4)
        rmse_cv = round(float(-np.mean(hasil_cv["test_rmse"])), 4)
        r2_cv = round(float(np.mean(hasil_cv["test_r2"])), 4)

        cv_summary[nama] = {"mae": mae_cv, "rmse": rmse_cv, "r2": r2_cv}
        print(f"{nama:18s} -> MAE: {mae_cv:.4f} | RMSE: {rmse_cv:.4f} | R2: {r2_cv:.4f}")

        if rmse_cv < rmse_terbaik:
            rmse_terbaik = rmse_cv
            nama_terbaik = nama
            model_terbaik = pipa

    model_terbaik.fit(X_train, y_train)
    pred_test = model_terbaik.predict(X_test)
    metrik_test = hitung_metrik(y_test, pred_test)

    print(f"\nModel terbaik: {nama_terbaik}")
    print(
        f"Baseline Test -> MAE: {metrik_baseline['mae']:.4f} | "
        f"RMSE: {metrik_baseline['rmse']:.4f} | R2: {metrik_baseline['r2']:.4f}"
    )
    print(
        f"{nama_terbaik:13s} -> MAE: {metrik_test['mae']:.4f} | "
        f"RMSE: {metrik_test['rmse']:.4f} | R2: {metrik_test['r2']:.4f}"
    )

    joblib.dump(model_terbaik, "src/app/model/model.joblib")

    info_fitur = {
        "target": target,
        "features": list(X.columns),
        "numeric_features": kolom_angka,
        "categorical_features": kolom_kategori,
        "sex_categories": ["M", "F", "I"],
    }
    with open("src/app/model/features.json", "w", encoding="utf-8") as f:
        json.dump(info_fitur, f, indent=2)

    ringkasan_metrik = {
        "best_model": nama_terbaik,
        "cv_results": cv_summary,
        "baseline_test": metrik_baseline,
        "test_metrics": metrik_test,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }
    with open("docs/evidence/metrics.json", "w", encoding="utf-8") as f:
        json.dump(ringkasan_metrik, f, indent=2)


if __name__ == "__main__":
    main()