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