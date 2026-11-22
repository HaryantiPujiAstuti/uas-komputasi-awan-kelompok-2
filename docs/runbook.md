# Runbook: Abalone Rings Prediction API

Layer: Infrastructure & Operations. Penulis utama: Orang 3.

## 1. Prasyarat
- Git, Python 3.11, dan Docker.
- scikit-learn dikunci di `==1.9.1` (`src/app/requirements.txt`), sama dengan versi saat training. Versi berbeda dapat membuat `model.joblib` gagal dimuat.
- Berkas model ada di `src/app/model/` (`model.joblib`, `features.json`).
- Tidak ada secret yang dibutuhkan. Jangan commit `.env`, key, atau token (sudah dikecualikan di `.gitignore`).

## 2. Menjalankan lokal
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r src/app/requirements.txt
cd src/app
uvicorn main:app --reload
```
API berjalan di port 8000. Dokumentasi interaktif: `/docs`.

## 3. Menjalankan tes
Dari root repo:
```bash
pytest src/app -v
```
Tes mencakup `/health`, prediksi valid, `features` kosong (400), fitur hilang, fitur tambahan, `Sex` tidak valid, tipe salah, dan nilai negatif (422).

## 4. Build dan run Docker
Dari root repo:
```bash
docker build -t abalone-api .
docker run -p 8080:8080 abalone-api
```
API berjalan di port 8080 (`${PORT}` bila disediakan platform).
Menghentikan: `Ctrl + C`. Jika terminal tidak merespons, buka terminal lain:
```bash
docker ps
docker stop <CONTAINER ID>
```
(ganti `<CONTAINER ID>` dengan kode dari `docker ps`).

## 5. Cek kesehatan
`GET /health` -> `{"status":"ok","model_version":"v1"}`

## 6. Contoh /predict
`POST /predict`, `Content-Type: application/json`:
```json
{"features": {"Sex": "M", "Length": 0.455, "Diameter": 0.365, "Height": 0.095,
 "Whole weight": 0.514, "Shucked weight": 0.2245, "Viscera weight": 0.101,
 "Shell weight": 0.15}}
```
Respons sukses: `{"prediction": ..., "model_version": "v1"}`.
Nama fitur harus persis seperti di atas (termasuk spasi dan huruf besar).

| Kondisi | Status |
|---|---|
| `features` kosong atau tidak ada | 400 |
| Fitur hilang atau fitur tidak dikenal | 422 |
| `Sex` bukan M/F/I | 422 |
| Nilai angka bukan angka atau negatif | 422 |

## 7. Cek log
API mencatat tiap permintaan ke stdout sebagai JSON: `method`, `path`, `status`, `duration_ms`. Isi data permintaan tidak dicatat. Saat dijalankan lokal atau Docker, log muncul di terminal.
Log di platform cloud: [BELUM DIISI: menunggu platform deploy ditentukan]

## 8. Deploy
[BELUM DIISI: platform dan langkah deploy belum ditentukan]
Catatan alasan pemilihan platform: Render, Google Cloud, dan Hugging Face Spaces (Docker) memerlukan kartu atau paket berbayar untuk akun kami, sedangkan Azure for Students menolak kelayakan akun. [Lengkapi setelah keputusan akhir.]

## 9. Rollback
[BELUM DIISI: bergantung pada platform]

## 10. Troubleshooting
- **Model gagal dimuat saat start:** periksa versi scikit-learn (harus 1.9.1) dan keberadaan `src/app/model/model.joblib`.
- **422 padahal data terlihat benar:** periksa ejaan nama fitur (spasi dan huruf besar) dan pastikan angka bukan teks.
- **`Address already in use`:** hentikan proses atau container lain yang memakai port tersebut.
- **Container tidak berhenti dengan Ctrl + C:** gunakan `docker ps` lalu `docker stop`.

## 11. Teardown
[BELUM DIISI: bergantung pada platform] Setelah presentasi, hapus layanan dan resource terkait, lalu simpan screenshot buktinya di `docs/evidence/`. Jangan menghapus bukti proyek.

## 12. Peringatan biaya
Biaya aktual: [BELUM DIISI: belum ada layanan cloud yang berjalan, jadi tidak diukur].