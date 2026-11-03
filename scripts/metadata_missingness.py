# Calculate missingness of metadata categories for fecessamples from the AGP dataset.
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

RESULTS_DIR = Path("results/metadata_missingness")
COUNTS_FILE = RESULTS_DIR / "metadata_category_counts.tsv"
SUMMARY_FILE = RESULTS_DIR / "metadata_category_summary.tsv"
OVERVIEW_FILE = RESULTS_DIR / "metadata_category_overview.txt"

# Minimum completeness required for a category to appear
# in the human-readable overview.
# Set to 0.0 to include all categories.
MIN_COMPLETENESS = 0.60

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
    "present_samples",
    "missing_samples",
    "completeness",
    "missingness",
]

MISSING_VALUES = {
    "not provided",
    "not collected",
    "not applicable",
    "",
    "none",
    "null",
    "nan",
    "n/a",
}


# ============================================================
# 2. Hilfsfunktionen
# ============================================================

def is_missing(value) -> bool:
    """Determine whether a metadata value is missing."""
    if pd.isna(value):
        return True

    return str(value).strip().casefold() in MISSING_VALUES


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

    included_count = sum(
        row["completeness"] >= MIN_COMPLETENESS
        for row in lookup.values()
    )

    with OVERVIEW_FILE.open("w", encoding="utf-8") as f:
        f.write("AGP METADATA MISSINGNESS OVERVIEW\n")
        f.write("=" * 110 + "\n")

        f.write(
            f"Minimum completeness filter: "
            f"{MIN_COMPLETENESS:.0%}\n"
        )
        f.write(
            f"Included categories: {included_count} "
            f"/ {len(categories)}\n"
        )
        f.write(
            "present_samples = Samples with a non-missing value.\n"
        )
        f.write(
            "missing_samples = Samples with a missing value.\n"
        )
        f.write(
            "Completeness = present_samples / total_samples.\n"
        )
        f.write(
            "Missingness = missing_samples / total_samples.\n"
        )
        f.write(
            "All categories are stored in the TSV files, "
            "regardless of the overview filter.\n"
        )

        for group_name in [name for name, _ in RULES] + ["other"]:
            variables = groups[group_name]

            # Apply completeness filter only to the overview.
            variables = [
                category
                for category in variables
                if category in lookup
                and lookup[category]["completeness"]
                >= MIN_COMPLETENESS
            ]

            if not variables:
                continue

            f.write(
                f"\n{group_name.upper()} "
                f"({len(variables)} variables)\n"
            )
            f.write("-" * 110 + "\n")

            for category in variables:
                row = lookup[category]

                f.write(
                    f"  {category:<48} "
                    #f"completeness={row['completeness']:>6.1%} "
                    f"missingness={row['missingness']:>6.1%} "
                    #f"present={row['present_samples']:>7,} "
                    #f"missing={row['missing_samples']:>7,} "
                    #f"total={row['total_samples']:>7,}\n"
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

    # Exclude sample identifiers from the UNPIVOT operation.
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
        WITH filtered_samples AS (
            SELECT *
            FROM {utils.quote_identifier(TABLE_NAME)}
            WHERE lower(trim(host_body_site)) = 'uberon:feces'
        )
        SELECT
            category,
            value,
            COUNT(*) AS count
        FROM filtered_samples
        UNPIVOT INCLUDE NULLS (
            value FOR category IN ({columns_expression})
        )
        GROUP BY category, value
    """

    print("Querying DuckDB...")
    counts_df = con.execute(query).fetchdf()

    total_samples = con.execute(
        f"SELECT COUNT(*) FROM {utils.quote_identifier(TABLE_NAME)} WHERE lower(trim(host_body_site)) = 'uberon:feces'"
    ).fetchone()[0]

finally:
    con.close()


# ============================================================
# 4. Missingness berechnen
# ============================================================

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

counts_df["count"] = counts_df["count"].astype("int64")
counts_df["total_samples"] = int(total_samples)

counts_df["is_missing"] = counts_df["value"].map(is_missing)

# Save value counts, including missing values.
counts_df[COUNT_COLUMNS].to_csv(
    COUNTS_FILE,
    sep="\t",
    index=False,
    na_rep="<NULL>",
)

# Aggregate counts per category.
summary_df = (
    counts_df.assign(
        missing_count=[
            int(count) if is_missing(value) else 0
            for value, count in zip(
                counts_df["value"], counts_df["count"]
            )
        ]
    )
    .groupby("category", as_index=False)
    .agg(
        total_samples=("total_samples", "first"),
        n_distinct_values=("value", "size"),
        missing_samples=("missing_count", "sum"),
    )
)

summary_df["present_samples"] = (
    summary_df["total_samples"] - summary_df["missing_samples"]
)

summary_df["completeness"] = (
    summary_df["present_samples"] / summary_df["total_samples"]
)

summary_df["missingness"] = (
    summary_df["missing_samples"] / summary_df["total_samples"]
)


# ============================================================
# 5. Sortierung und Ergebnisse speichern
# ============================================================

category_order = {
    category: index
    for index, category in enumerate(categories)
}

group_order = {
    group: index
    for index, (group, _) in enumerate(RULES)
}
group_order["other"] = len(group_order)

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
# 6. Menschenlesbare Übersicht schreiben
# ============================================================

write_overview(categories, summary_df)

print("\nFinished.")
print(f"Counts:   {COUNTS_FILE.resolve()}")
print(f"Summary:  {SUMMARY_FILE.resolve()}")
print(f"Overview: {OVERVIEW_FILE.resolve()}")
print(f"Samples:  {total_samples:,}")
print(f"Categories: {len(categories):,}")
print(
    f"Overview filter: completeness >= {MIN_COMPLETENESS:.0%}"
)
print(
    f"Included categories: "
    f"{(summary_df['completeness'] >= MIN_COMPLETENESS).sum():,}"
)
