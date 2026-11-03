import re
from pathlib import Path

import duckdb
import pandas as pd

import common.metadata_utils as utils
from common.metadata_rules import RULES


# ============================================================
# 1. Dateien und Einstellungen
# ============================================================

DB_FILE = Path("data/AGP-metadata.duckdb")
TABLE_NAME = "agp_metadata"

RESULTS_DIR = Path("results/metadata_counts")
COUNTS_FILE = RESULTS_DIR / "metadata_category_counts.tsv"
SUMMARY_FILE = RESULTS_DIR / "metadata_category_summary.tsv"
OVERVIEW_FILE = RESULTS_DIR / "metadata_category_overview.txt"

COUNT_COLUMNS = [
    "category",
    "value",
    "count",
    "total_samples",
]

SUMMARY_COLUMNS = [
    "category",
    "total_samples",
    "n_distinct_values",
    "informative_samples",
]

NON_INFORMATIVE_VALUES = {
    "not provided",
    "not collected",
    "not applicable",
    "control sample",
    "labcontrol test",
    "i do not have this condition",
    "no",
    "false",
    "",
    "none",
    "null",
    "nan",
    "n/a",
}


# ============================================================
# 2. Hilfsfunktionen
# ============================================================

def is_informative(value) -> bool:
    """Determine whether a metadata value is informative."""
    if pd.isna(value):
        return False

    return str(value).strip().casefold() not in NON_INFORMATIVE_VALUES

def get_group_order() -> dict[str, int]:
    """Preserve the group order defined by RULES."""
    order = {
        group: index
        for index, (group, _) in enumerate(RULES)
    }
    order["other"] = len(order)
    return order

def write_overview(
    categories: list[str],
    summary_df: pd.DataFrame,
) -> None:
    """Write a readable overview grouped by RULES."""
    lookup = summary_df.set_index("category").to_dict("index")

    groups = {name: [] for name, _ in RULES}
    groups["other"] = []

    for category in categories:
        groups[utils.classify_category(category)].append(category)

    with OVERVIEW_FILE.open("w", encoding="utf-8") as f:
        f.write("AGP METADATA OVERVIEW\n")
        f.write("=" * 90 + "\n")
        f.write(
            "informative_samples = Sum of counts for values not "
            "classified as non-informative.\n"
        )
        f.write(
            "total_samples = Number of samples in the metadata table.\n"
        )
        f.write(
            "Missing values are included in total_samples but not "
            "in informative_samples.\n"
        )

        for group_name in [name for name, _ in RULES] + ["other"]:
            variables = groups[group_name]
            if not variables:
                continue

            f.write(
                f"\n{group_name.upper()} "
                f"({len(variables)} variables)\n"
            )
            f.write("-" * 90 + "\n")

            for category in variables:
                row = lookup.get(category)

                if row is None:
                    f.write(f"  {category}\tNOT PROCESSED\n")
                    continue

                f.write(
                    f"  {category:<48} "
                    f"informative={row['informative_samples']} "
                    f"total={row['total_samples']} "
                )


# ============================================================
# 3. Daten aus DuckDB abfragen
# ============================================================

if not DB_FILE.exists():
    raise FileNotFoundError(
        f"DuckDB database not found: {DB_FILE.resolve()}"
    )

con = duckdb.connect(str(DB_FILE), read_only=True)

try:
    categories = utils.get_categories(con)
    print(f"Metadata categories: {len(categories)}")

    # One row per category and value.
    # INCLUDE NULLS ensures missing values are counted as a value group.
    # All metadata columns should be VARCHAR from the original import.
    excluded = ", ".join(
        utils.quote_identifier(c)
        for c in ["#SampleID", "sample_name"]
        if c in con.execute(
            f"DESCRIBE {utils.quote_identifier(TABLE_NAME)}"
        ).fetchdf()["column_name"].tolist()
    )

    if excluded:
        columns_expression = f"COLUMNS(* EXCLUDE ({excluded}))"
    else:
        columns_expression = "COLUMNS(*)"

    query = f"""
        SELECT
            category,
            value,
            COUNT(*) AS count
        FROM {utils.quote_identifier(TABLE_NAME)}
        UNPIVOT INCLUDE NULLS (
            value FOR category IN ({columns_expression})
        )
        GROUP BY category, value
    """

    print("Querying DuckDB...")
    counts_df = con.execute(query).fetchdf()

    total_samples = con.execute(
        f"SELECT COUNT(*) FROM {utils.quote_identifier(TABLE_NAME)}"
    ).fetchone()[0]

finally:
    con.close()


# ============================================================
# 4. Häufigkeiten und informative Samples berechnen
# ============================================================
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

counts_df["count"] = counts_df["count"].astype("int64")

# Every category represents every sample, including missing values.
counts_df["total_samples"] = int(total_samples)

counts_df["is_informative"] = counts_df["value"].map(is_informative)

counts_df = counts_df[COUNT_COLUMNS].copy()
counts_df.to_csv(
    COUNTS_FILE,
    sep="\t",
    index=False,
    na_rep="<NULL>",
)

summary_df = (
    counts_df.assign(
        informative_count=[
            int(count) if is_informative(value) else 0
            for value, count in zip(
                counts_df["value"], counts_df["count"]
            )
        ]
    )
    .groupby("category", as_index=False)
    .agg(
        total_samples=("total_samples", "first"),
        n_distinct_values=("value", "size"),
        informative_samples=("informative_count", "sum"),
    )
)

# Preserve the original column order within each RULES group.
category_order = {
    category: index
    for index, category in enumerate(categories)
}
group_order = get_group_order()

summary_df["_group_order"] = summary_df["category"].map(
    lambda c: group_order[utils.classify_category(c)]
)
summary_df["_category_order"] = summary_df["category"].map(
    category_order
)

summary_df = summary_df.sort_values(
    ["_group_order", "_category_order"]
).drop(columns=["_group_order", "_category_order"])

summary_df = summary_df[SUMMARY_COLUMNS]

summary_df.to_csv(
    SUMMARY_FILE,
    sep="\t",
    index=False,
)


# ============================================================
# 5. Menschenlesbare Übersicht schreiben
# ============================================================

write_overview(categories, summary_df)

print("\nFinished.")
print(f"Counts:   {COUNTS_FILE.resolve()}")
print(f"Summary:  {SUMMARY_FILE.resolve()}")
print(f"Overview: {OVERVIEW_FILE.resolve()}")
print(f"Samples:  {total_samples:,}")
print(f"Categories: {len(categories):,}")
