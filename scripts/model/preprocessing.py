import numpy as np
import pandas as pd

MISSING_VALUES = {
    "not provided",
    "not collected",
    "not applicable",
    "unknown",
    "n/a",
    "na",
    "",
}

NUMERIC_RANGES = {
    "host_age": (0, 120),
    "host_height": (20, 230),
    "host_weight": (2, 300),
}

def clean_missing_values(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()

    for col in X.columns:
        X[col] = X[col].astype("object")

        # Strings bereinigen, echte NULL-Werte bleiben fehlend
        X[col] = X[col].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )

        # Definierte Missing-Value-Kategorien erkennen
        mask = X[col].apply(
            lambda value: isinstance(value, str)
            and value.casefold() in MISSING_VALUES
        )

        X.loc[mask, col] = np.nan

    return X

def clean_numeric_values(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()

    for col, (lower, upper) in NUMERIC_RANGES.items():
        X[col] = pd.to_numeric(X[col], errors="coerce")

        # Unplausible Werte als fehlend behandeln
        invalid = (X[col] < lower) | (X[col] > upper)
        X.loc[invalid, col] = np.nan

    return X