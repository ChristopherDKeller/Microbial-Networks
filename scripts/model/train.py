import duckdb
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    average_precision_score,
)

from features import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES, TARGET, GROUP_COL
from preprocessing import clean_missing_values, clean_numeric_values


# --------------------------------------------------
# 1. Load data
# --------------------------------------------------

con = duckdb.connect("data/AGP-metadata.duckdb", read_only=True)

df = con.execute("""
    SELECT *
    FROM agp_metadata
    WHERE lower(trim(host_body_site)) = 'uberon:feces'
""").df()

con.close()


# --------------------------------------------------
# 2. Select features and target
# --------------------------------------------------

feature_cols = [col for col in FEATURES if col in df.columns]

# DECISION: Only these two target responses are considered valid labels.
y_all = (
    df[TARGET]
    .astype("string")
    .str.strip()
    .map({
        "Diagnosed by a medical professional (doctor, physician assistant)": 1,
        "I do not have this condition": 0,
    })
)

# Keep only labeled rows with a subject ID.
df = df.loc[y_all.notna() & df[GROUP_COL].notna()].copy()
df["y"] = y_all.loc[df.index].astype(int)

# DECISION: Use one randomly selected sample per subject.
# This prevents the same subject from appearing multiple times.
df = (
    df.sample(frac=1, random_state=42)
    .drop_duplicates(GROUP_COL)
    .reset_index(drop=True)
)

# Preprocess categorical and numeric features separately, then combine them.
X_cat = clean_missing_values(df[CATEGORICAL_FEATURES])
X_num = clean_numeric_values(df[NUMERIC_FEATURES])

X = pd.concat([X_cat, X_num], axis=1)
y = df["y"]


# --------------------------------------------------
# 3. Train / test split
# --------------------------------------------------

# DECISION: 20 % test data.
# DECISION: Stratification preserves the class proportions.
# DECISION: Random state 42 for reproducibility.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# --------------------------------------------------
# 4. Preprocessing
# --------------------------------------------------

# DECISION: Replace missing categorical values with the most frequent value.
# DECISION: One-hot encode categorical features.
# DECISION: Ignore categories that only occur in the test set.
#preprocessor = make_column_transformer(
#    (
#        make_pipeline(
#            SimpleImputer(strategy="most_frequent"),
#            OneHotEncoder(handle_unknown="ignore"),
#        ),
#        feature_cols,
#    ),
#    remainder="drop",
#)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            make_pipeline(
                SimpleImputer(strategy="most_frequent"),
                OneHotEncoder(handle_unknown="ignore"),
            ),
            CATEGORICAL_FEATURES,
        ),
        (
            "numeric",
            make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
            ),
            NUMERIC_FEATURES,
        ),
    ],
    remainder="drop",
)


# --------------------------------------------------
# 5. Train logistic regression
# --------------------------------------------------

# DECISION: L2 regularization (default).
# DECISION: C = 1.0 (default regularization strength).
# DECISION: class_weight=None (no class weighting).
# DECISION: max_iter=1000 (maximum optimization iterations).
# DECISION: solver='lbfgs'.
model = make_pipeline(
    preprocessor,
    LogisticRegression(
        C=1.0,
        #penalty="l2",
        l1_ratio=0,
        class_weight=None,
        max_iter=1000,
        solver="lbfgs",
        random_state=42,
    ),
)

model.fit(X_train, y_train)


# --------------------------------------------------
# 6. Evaluation
# --------------------------------------------------

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("Class distribution:")
print("Train:")
print(y_train.value_counts(normalize=True))
print("Test:")
print(y_test.value_counts(normalize=True))

print("\nClassification report:")
print(classification_report(y_test, y_pred))

print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")
print(f"PR-AUC:  {average_precision_score(y_test, y_prob):.4f}")

probabilities = model.predict_proba(X_test)[:, 1]
