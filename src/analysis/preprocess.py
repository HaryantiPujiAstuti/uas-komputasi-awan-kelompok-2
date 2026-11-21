import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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


def ambil_data_manual():
    lokasi_file = None
    try:
        from google.colab import files
        diupload = files.upload()
        if diupload:
            lokasi_file = list(diupload.keys())[0]
    except ImportError:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        lokasi_file = filedialog.askopenfilename(
            title="Pilih file dataset Abalone",
            filetypes=[
                ("File Dataset", "*.xlsx *.xls *.csv *.data"),
                ("Semua File", "*.*"),
            ],
        )
        root.destroy()

    if not lokasi_file:
        raise FileNotFoundError("File belum dipilih.")

    if lokasi_file.endswith((".xlsx", ".xls")):
        xls = pd.ExcelFile(lokasi_file)
        sheet = "Dataset_Abalone" if "Dataset_Abalone" in xls.sheet_names else xls.sheet_names[0]
        df = pd.read_excel(lokasi_file, sheet_name=sheet)
    elif lokasi_file.endswith(".csv"):
        df = pd.read_csv(lokasi_file)
    else:
        df = pd.read_csv(lokasi_file, header=None, names=NAMA_KOLOM)

    df = df.rename(columns={c: c.strip() for c in df.columns})
    return df


def buat_preprocessor(fitur):
    kolom_kategori = [k for k in ["Sex"] if k in fitur]
    kolom_angka = [k for k in fitur if k not in kolom_kategori]

    pipa_angka = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    pipa_kategori = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore")),
    ])

    daftar = []
    if kolom_angka:
        daftar.append(("angka", pipa_angka, kolom_angka))
    if kolom_kategori:
        daftar.append(("kategori", pipa_kategori, kolom_kategori))

    preprocessor = ColumnTransformer(transformers=daftar)
    return preprocessor, kolom_angka, kolom_kategori