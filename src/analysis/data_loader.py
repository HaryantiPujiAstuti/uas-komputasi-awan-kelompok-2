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


def load_data(lokasi_file):
    if not lokasi_file or not os.path.exists(lokasi_file):
        raise FileNotFoundError(f"File dataset tidak ditemukan: {lokasi_file}")

    if lokasi_file.endswith((".xlsx", ".xls")):
        xls = pd.ExcelFile(lokasi_file)
        sheet = (
            "Dataset_Abalone"
            if "Dataset_Abalone" in xls.sheet_names
            else xls.sheet_names[0]
        )
        df = pd.read_excel(lokasi_file, sheet_name=sheet)
    elif lokasi_file.endswith(".csv"):
        df = pd.read_csv(lokasi_file)
    else:
        df = pd.read_csv(lokasi_file, header=None, names=NAMA_KOLOM)

    df = df.rename(columns={c: c.strip() for c in df.columns})
    return df