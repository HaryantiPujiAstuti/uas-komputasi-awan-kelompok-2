import json
import logging
import time
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent
MODEL_VERSION = "v1"

# Dimuat sekali saat aplikasi start, bukan setiap ada request
model = joblib.load(BASE_DIR / "model" / "model.joblib")
with open(BASE_DIR / "model" / "features.json", encoding="utf-8") as f:
    info = json.load(f)

FEATURES = info["features"]
NUMERIC = info["numeric_features"]
SEX_VALID = info["sex_categories"]

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("api")

app = FastAPI(title="Abalone Rings Prediction API")


class PredictRequest(BaseModel):
    features: dict | None = None


@app.middleware("http")
async def log_requests(request: Request, call_next):
    mulai = time.perf_counter()
    response = await call_next(request)
    durasi_ms = round((time.perf_counter() - mulai) * 1000, 2)
    logger.info(json.dumps({
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": durasi_ms,
    }))
    return response


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/predict")
def predict(req: PredictRequest):
    fitur = req.features

    # 400: features kosong atau tidak ada
    if not fitur:
        raise HTTPException(status_code=400, detail="features tidak boleh kosong")

    # 422: fitur hilang
    hilang = [c for c in FEATURES if c not in fitur]
    if hilang:
        raise HTTPException(status_code=422, detail=f"Fitur hilang: {hilang}")

    # 422: fitur tambahan ditolak (perlu disepakati di kontrak)
    tambahan = [c for c in fitur if c not in FEATURES]
    if tambahan:
        raise HTTPException(status_code=422, detail=f"Fitur tidak dikenal: {tambahan}")

    # 422: Sex harus M, F, atau I
    sex = fitur["Sex"]
    if not isinstance(sex, str) or sex not in SEX_VALID:
        raise HTTPException(status_code=422, detail=f"Sex harus salah satu dari {SEX_VALID}")

    # 422: fitur angka harus angka (bukan teks, bukan true/false) dan tidak negatif
    for c in NUMERIC:
        v = fitur[c]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise HTTPException(status_code=422, detail=f"{c} harus berupa angka")
        if v < 0:
            raise HTTPException(status_code=422, detail=f"{c} tidak boleh negatif")

    # Susun satu baris data dengan urutan kolom sesuai features.json
    baris = pd.DataFrame([{c: fitur[c] for c in FEATURES}])
    prediksi = float(model.predict(baris)[0])

    return {"prediction": round(prediksi, 4), "model_version": MODEL_VERSION}
