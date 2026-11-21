from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_preprocessor(num_cols, cat_cols):
    """
    Membuat preprocessing untuk fitur numerik
    dan kategorikal pada dataset Abalone.

    Parameters
    ----------
    num_cols : list
        Daftar nama kolom numerik.

    cat_cols : list
        Daftar nama kolom kategorikal.

    Returns
    -------
    ColumnTransformer
        Objek preprocessing untuk digunakan
        dalam Pipeline machine learning.
    """

    transformers = []

    # Preprocessing fitur numerik
    if num_cols:
        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )

        transformers.append(
            ("numeric", numeric_transformer, num_cols)
        )

    # Preprocessing fitur kategorikal
    if cat_cols:
        categorical_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]
        )

        transformers.append(
            ("categorical", categorical_transformer, cat_cols)
        )

    if not transformers:
        raise ValueError(
            "Daftar fitur numerik dan kategorikal tidak boleh kosong."
        )

    preprocessor = ColumnTransformer(
        transformers=transformers
    )

    return preprocessor