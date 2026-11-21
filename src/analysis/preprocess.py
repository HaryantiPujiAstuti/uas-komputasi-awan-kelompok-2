"""
Modul Preprocessing Dataset Abalone (src/analysis/preprocess.py)
Peran: Orang 2 (Analysis Layer)
Deskripsi: Membangun pipeline preprocessing menggunakan ColumnTransformer tanpa data leakage.
"""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUM_COLS = [
    "Length",
    "Diameter",
    "Height",
    "Whole weight",
    "Shucked weight",
    "Viscera weight",
    "Shell weight",
]
CAT_COLS = ["Sex"]
TARGET_COL = "Rings"


def build_preprocessor(num_cols=None, cat_cols=None):
    """
    Membangun ColumnTransformer untuk fitur numerik dan kategorikal.
    Fit hanya dilakukan pada data latih (train set) di dalam Pipeline.
    """
    if num_cols is None:
        num_cols = NUM_COLS
    if cat_cols is None:
        cat_cols = CAT_COLS

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols),
        ],
        remainder="drop",
    )
    return preprocessor
