import re
from pathlib import Path

import duckdb
import pandas as pd


# ============================================================
# 1. Dateien und Einstellungen
# ============================================================

DB_FILE = Path("data/AGP-metadata.duckdb")
TABLE_NAME = "agp_metadata"

COUNTS_FILE = Path("metadata_category_counts.tsv")
SUMMARY_FILE = Path("metadata_category_summary.tsv")
OVERVIEW_FILE = Path("metadata_category_overview.txt")

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
# 2. RULES
# Reihenfolge Wichtig: Die erste passende Regel wird verwendet, um eine Kategorie zu gruppieren.
# ============================================================

RULES = [
    # Ernährungserhebung
    ("vioscreen", [r"^vioscreen_"]),

    # Kopf
    ("scalp_and_face", [r"scalp_current|facial"]),

    # Participant metadata (PM)
    ("pm_shared", [r"^pm_shared_"]),
    ("pm_participation", [r"^pm_.*participation_reason"]),
    ("pm_gastro", [r"^pm_gastro"]),
    ("pm_lifestyle", [r"^pm_lifestyle"]),
    ("pm_other", [r"^pm_"]),

    # Allergien
    ("food_allergies", [
        r"allergic_",
        r"seasonal",
    ]),
    ("non_food_allergies", [
        r"non_food_allergies",
    ]),

    # Krankheiten und Gesundheit
    ("mental_illness", [
        r"mental_illness|epilepsy_or_seizure_disorder|"
        r"depression_bipolar_schizophrenia|add_adhd|asd"
    ]),
    ("artificial_gi_disorder", [r"artificial_gi_disorder"]),
    ("cancer", [r"cancer"]),
    ("covid", [r"covid|coronavirus|sars.?cov.?2"]),
    ("disease", [
        r"disease|diagnos|clinical_condition|condition_",
        r"diabetes|ibd|asthma|skin_condition|alzheimers|"
        r"fungal_overgrowth|migraine|autoimmune|ibs|pku",
    ]),
    ("medication", [
        r"medication|meds|prescription|antibiotic|"
        r"supplement|contraceptive|multivitamin"
    ]),
    ("immunities", [r"flu_vaccine_date|chickenpox"]),
    ("intolerances", [r"gluten|lactose"]),
    ("gut_health", [
        r"acid_reflux",
        r"bowel_movement",
        r"sibo",
        r"cdiff",
        r"coprophage",
    ]),
    ("medical_history", [
        r"appendix_removed",
        r"tonsils_removed",
        r"thyroid",
        r"subset_healthy",
    ]),
    ("reproductive_early_life", [
        r"pregnant",
        r"breastmilk",
        r"fed_as_infant",
        r"csection",
    ]),

    # Demografie und Lebensstil
    ("demographics", [
        r"(^|_)(age|sex|height|weight|bmi|race|ethnic|birth|lifestage)(_|$)"
    ]),
    ("lifestyle", [
        r"smok|alcohol|drinks|stress|sleep|exercise|"
        r"physical_activity|weekday_wake_time|weekend_wake_time|"
        r"hours_outside|pool_frequency"
    ]),
    ("lifestyle_misc", [
        r"^livingwith$",
        r"^living_status$",
        r"roommates",
        r"last_move",
        r"last_travel",
        r"dominant_hand",
        r"nail_biter",
        r"vivid_dreams",
        r"types_of_plants",
        r"softener",
    ]),
    ("hygiene", [
        r"deodorant_use|cosmetics_frequency|"
        r"teethbrushing_frequency|flossing_frequency"
    ]),

    # Haustiere
    ("pets", [
        r"pet|dog|cat|animal_type|animal_gender|animal_origin"
    ]),

    # Ernährung außerhalb von Vioscreen
    ("fermented", [r"fermented"]),
    ("diet", [
        r"diet|food|meal|fasting|fiber|fibre|nutrition",
        r"whole_eggs",
        r"olive_oil",
        r"red_meat",
        r"beet_frequency",
        r"poultry_frequency",
        r"fruit_frequency",
        r"vegetable_frequency",
        r"milk_cheese_frequency",
        r"milk_substitute_frequency",
        r"plant_protein_frequency",
        r"whole_grain_frequency",
        r"salted_snacks_frequency",
        r"artificial_sweeteners",
        r"high_fat_red_meat_frequency",
        r"probiotic_frequency",
        r"oils_frequency",
        r"meat_eggs_frequency",
        r"sugar_sweetened_drink_frequency",
        r"sugary_sweets_frequency",
        r"one_liter_of_water_a_day_frequency",
        r"frozen_dessert_frequency",
        r"consume_animal_products_abx",
    ]),

    # Proben- und Studieninformationen
    ("sample_study", [
        r"sample|study|collection|empo|run_accession|subject_id"
    ]),

    # Sample Information
    ("sample", [
        r"^host_|body|scientific_name|dna_extracted|"
        r"physical_specimen_remaining|taxon_id"
    ]),

    # Location
    ("location", [
        r"longitude|latitude|country|region|geo|elevation|"
        r"state|thdmi_cohort|^env_"
    ]),

    # Umwelt und Wohnumgebung
    ("environment", [
        r"^setting$",
        r"water",
    ]),

    # Studien- und Kohorteninformationen
    ("study_metadata", [
        r"anonymized_name",
        r"^title$",
        r"^description$",
        r"^public$",
    ]),

    # Weitere spezifische Themen
    ("surf", [r"^surf"]),
]

# ============================================================
# 3. Hilfsfunktionen
# ============================================================

def quote_identifier(name: str) -> str:
    """Escape SQL identifiers such as column names."""
    return '"' + name.replace('"', '""') + '"'


def classify_category(category: str) -> str:
    """Assign the first matching RULES group."""
    name = category.casefold()

    for group, patterns in RULES:
        if any(re.search(pattern, name) for pattern in patterns):
            return group

    return "other"


def is_informative(value) -> bool:
    """Determine whether a metadata value is informative."""
    if pd.isna(value):
        return False

    return str(value).strip().casefold() not in NON_INFORMATIVE_VALUES


def get_categories(con) -> list[str]:
    """Read column names from DuckDB, excluding sample identifiers."""
    columns = con.execute(
        f"DESCRIBE {quote_identifier(TABLE_NAME)}"
    ).fetchdf()["column_name"].tolist()

    return [
        c for c in columns
        if c not in {"#SampleID", "sample_name"}
    ]


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
        groups[classify_category(category)].append(category)

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
# 4. Daten aus DuckDB abfragen
# ============================================================

if not DB_FILE.exists():
    raise FileNotFoundError(
        f"DuckDB database not found: {DB_FILE.resolve()}"
    )

con = duckdb.connect(str(DB_FILE), read_only=True)

try:
    categories = get_categories(con)
    print(f"Metadata categories: {len(categories)}")

    # One row per category and value.
    # INCLUDE NULLS ensures missing values are counted as a value group.
    # All metadata columns should be VARCHAR from the original import.
    excluded = ", ".join(
        quote_identifier(c)
        for c in ["#SampleID", "sample_name"]
        if c in con.execute(
            f"DESCRIBE {quote_identifier(TABLE_NAME)}"
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
        FROM {quote_identifier(TABLE_NAME)}
        UNPIVOT INCLUDE NULLS (
            value FOR category IN ({columns_expression})
        )
        GROUP BY category, value
    """

    print("Querying DuckDB...")
    counts_df = con.execute(query).fetchdf()

    total_samples = con.execute(
        f"SELECT COUNT(*) FROM {quote_identifier(TABLE_NAME)}"
    ).fetchone()[0]

finally:
    con.close()


# ============================================================
# 5. Häufigkeiten und informative Samples berechnen
# ============================================================

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
    lambda c: group_order[classify_category(c)]
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
