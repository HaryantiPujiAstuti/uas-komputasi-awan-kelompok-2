import os
import pandas as pd

NAMA_KOLOM = [
    "Sex",
    "Length",
    "Diameter",
    "Height",
    "Whole weight",
    "Shucked weight",
    "Viscera weight",
    "Shell weight",
    "Rings",
]

EKSTENSI_DIDUKUNG = (".xlsx", ".xls", ".csv", ".data")


def load_data(lokasi_file):
    if not lokasi_file or not os.path.exists(lokasi_file):
        raise FileNotFoundError(f"File dataset tidak ditemukan: {lokasi_file}")

    lower_path = lokasi_file.lower()
    if not lower_path.endswith(EKSTENSI_DIDUKUNG):
        raise ValueError(
            f"Ekstensi file tidak didukung: '{os.path.splitext(lokasi_file)[1]}'. "
            f"Gunakan salah satu dari: {', '.join(EKSTENSI_DIDUKUNG)}"
        )

    if lower_path.endswith((".xlsx", ".xls")):
        xls = pd.ExcelFile(lokasi_file)
        sheet = (
            "Dataset_Abalone"
            if "Dataset_Abalone" in xls.sheet_names
            else xls.sheet_names[0]
        )
        df = pd.read_excel(lokasi_file, sheet_name=sheet)
    elif lower_path.endswith(".csv"):
        df = pd.read_csv(lokasi_file)
    else:
        df = pd.read_csv(lokasi_file, header=None, names=NAMA_KOLOM)

    df = df.rename(columns={c: c.strip() for c in df.columns})
    return df