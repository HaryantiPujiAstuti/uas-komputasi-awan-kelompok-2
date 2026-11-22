import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID = {
    "Sex": "M",
    "Length": 0.455,
    "Diameter": 0.365,
    "Height": 0.095,
    "Whole weight": 0.514,
    "Shucked weight": 0.2245,
    "Viscera weight": 0.101,
    "Shell weight": 0.15,
}


def kirim(**perubahan):
    """Salin contoh valid, lalu ubah sesuai kebutuhan tes."""
    fitur = dict(VALID)
    fitur.update(perubahan)
    return client.post("/predict", json={"features": fitur})


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "model_version": "v1"}


def test_predict_valid():
    r = client.post("/predict", json={"features": VALID})
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body["prediction"], float)
    assert body["model_version"] == "v1"


def test_features_kosong_400():
    r = client.post("/predict", json={"features": {}})
    assert r.status_code == 400


def test_body_kosong_400():
    r = client.post("/predict", json={})
    assert r.status_code == 400


def test_fitur_hilang_422():
    fitur = dict(VALID)
    del fitur["Height"]
    r = client.post("/predict", json={"features": fitur})
    assert r.status_code == 422


def test_fitur_tambahan_ditolak_422():
    r = kirim(Extra=1.0)
    assert r.status_code == 422


@pytest.mark.parametrize("sex", ["X", "m", "", 1])
def test_sex_tidak_valid_422(sex):
    assert kirim(Sex=sex).status_code == 422


@pytest.mark.parametrize("nilai", ["panjang", True, None])
def test_tipe_angka_salah_422(nilai):
    assert kirim(Length=nilai).status_code == 422


def test_angka_negatif_422():
    assert kirim(Length=-0.1).status_code == 422