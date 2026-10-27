
import csv
import re
import subprocess
from pathlib import Path

import pandas as pd


# ============================================================
# 1. Dateien und Einstellungen
# ============================================================

METADATA_FILE = Path("redbiom_metadata.tsv")
SAMPLE_IDS_FILE = Path("all_sample_ids.txt")
COUNTS_FILE = Path("metadata_category_counts.tsv")
SUMMARY_FILE = Path("metadata_category_summary.tsv")
OVERVIEW_FILE = Path("metadata_category_overview.txt")

TIMEOUT_SECONDS = 180

COUNT_COLUMNS = [
    "category", "value", "count", "total_samples"
]

SUMMARY_COLUMNS = [
    "category", "total_samples",
    "n_distinct_values", "informative_samples"
]

# Diese Werte werden bei informative_samples nicht mitgezählt.
NON_INFORMATIVE_VALUES = {
    "not provided",
    "not collected",
    "not applicable",
    "control sample",
    "labcontrol test",
    "i do not have this condition",
    "no",
    "false"
}


# ============================================================
# 2. Deine Kategorisierungsregeln
#    Die Reihenfolge ist wichtig: erster Treffer gewinnt.
# ============================================================

RULES = [
    # Ernährungserhebung
    ("vioscreen", [r"^vioscreen_"]),

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
        r"drinking_water_source",
        r"toilet_water_access",
    ]),

    # Studien- und Kohorteninformationen
    ("study_metadata", [
        r"anonymized_name",
        r"^title$",
        r"^description$",
        r"^public$",
    ]),

    # Weitere spezifische Themen
    ("surf", [r"^surf_"]),
]


# ============================================================
# 3. Hilfsfunktionen
# ============================================================

def read_tsv_or_empty(path, columns):
    """Liest eine TSV-Datei oder erzeugt einen leeren DataFrame."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=columns)

    try:
        df = pd.read_csv(path, sep="\t")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns)

    for column in columns:
        if column not in df.columns:
            df[column] = pd.NA

    return df[columns]


def classify_category(category):
    """Ordnet eine Metadatenvariable der ersten passenden Regel zu."""
    name = category.lower()

    for group, patterns in RULES:
        if any(re.search(pattern, name) for pattern in patterns):
            return group

    return "other"


def is_informative(value):
    """Prüft, ob ein ausgegebener Wert als informativ gezählt wird."""
    return str(value).strip().casefold() not in NON_INFORMATIVE_VALUES


def save_counts(df):
    df.to_csv(COUNTS_FILE, sep="\t", index=False)


def rebuild_summary(counts_df):
    """Berechnet die Zusammenfassung aus allen gespeicherten Counts."""
    rows = []

    if counts_df.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)

    for category, group in counts_df.groupby("category", sort=False):
        total_values = pd.to_numeric(
            group["count"], errors="coerce"
        ).fillna(0)

        informative_mask = group["value"].map(is_informative)

        total_samples = pd.to_numeric(
            group["total_samples"], errors="coerce"
        ).dropna()

        rows.append({
            "category": category,
            "total_samples": (
                int(total_samples.iloc[0])
                if not total_samples.empty else None
            ),
            "n_distinct_values": len(group),
            "informative_samples": int(
                total_values[informative_mask].sum()
            ),
        })

    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def write_overview(categories, summary_df):
    """Schreibt eine nach RULES gruppierte Textübersicht."""
    summary_lookup = {}

    for _, row in summary_df.iterrows():
        summary_lookup[row["category"]] = row

    groups = {name: [] for name, _ in RULES}
    groups["other"] = []

    for category in categories:
        group = classify_category(category)
        groups[group].append(category)

    with OVERVIEW_FILE.open("w", encoding="utf-8") as f:
        f.write("AGP METADATA OVERVIEW\n")
        f.write("=" * 72 + "\n")
        f.write(
            "informative_samples = Summe der Werte, die nicht als "
            "nicht-informativ klassifiziert wurden.\n"
        )
        f.write(
            "Hinweis: Die Kennzahl ist eine vorläufige "
            "Namens-/Wert-basierte Heuristik.\n\n"
        )

        for group_name, _ in RULES:
            variables = groups[group_name]
            if not variables:
                continue

            f.write(f"\n{group_name.upper()} ({len(variables)} variables)\n")
            f.write("-" * 72 + "\n")

            for category in variables:
                row = summary_lookup.get(category)

                if row is None:
                    informative = "not processed"
                    total = "unknown"
                else:
                    value = row["informative_samples"]
                    informative = (
                        str(int(value)) if pd.notna(value) else "unknown"
                    )
                    total_value = row["total_samples"]
                    total = (
                        str(int(total_value))
                        if pd.notna(total_value) else "unknown"
                    )

                f.write(
                    f"  {category:<48} "
                    f"informative_samples={informative:<8} "
                    f"total_samples={total}\n"
                )

        variables = groups["other"]
        if variables:
            f.write(f"\nOTHER ({len(variables)} variables)\n")
            f.write("-" * 72 + "\n")

            for category in variables:
                row = summary_lookup.get(category)

                if row is None:
                    informative = "not processed"
                    total = "unknown"
                else:
                    value = row["informative_samples"]
                    informative = (
                        str(int(value)) if pd.notna(value) else "unknown"
                    )
                    total_value = row["total_samples"]
                    total = (
                        str(int(total_value))
                        if pd.notna(total_value) else "unknown"
                    )

                f.write(
                    f"  {category:<48} "
                    f"informative_samples={informative:<8} "
                    f"total_samples={total}\n"
                )


# ============================================================
# 4. Metadatenvariablen aus der Kopfzeile lesen
# ============================================================

with METADATA_FILE.open("r", encoding="utf-8") as f:
    categories = next(csv.reader(f, delimiter="\t"))

categories = [
    category for category in categories
    if category not in {"#SampleID", "sample_name"}
]

print(f"Metadatenvariablen insgesamt: {len(categories)}")


# ============================================================
# 5. Bereits gespeicherte Ergebnisse laden
# ============================================================

counts_df = read_tsv_or_empty(COUNTS_FILE, COUNT_COLUMNS)

# Kategorie gilt als verarbeitet, sobald sie in der Counts-Datei
# mindestens eine Zeile besitzt.
completed_categories = set(counts_df["category"].dropna().astype(str))

pending_categories = [
    category for category in categories
    if category not in completed_categories
]

print(f"Bereits verarbeitet: {len(completed_categories)}")
print(f"Noch abzufragen: {len(pending_categories)}")

sample_ids = SAMPLE_IDS_FILE.read_text(encoding="utf-8").strip()

if not sample_ids:
    raise ValueError(f"Keine Sample-IDs in {SAMPLE_IDS_FILE}")


# ============================================================
# 6. Nur fehlende Kategorien mit Redbiom abfragen
# ============================================================

for i, category in enumerate(pending_categories, start=1):
    print(
        f"[{i}/{len(pending_categories)}] {category}",
        flush=True,
    )

    command = [
        "redbiom",
        "summarize",
        "samples",
        "--category",
        category,
    ]

    try:
        result = subprocess.run(
            command,
            input=sample_ids + "\n",
            text=True,
            capture_output=True,
            check=True,
            timeout=TIMEOUT_SECONDS,
        )

        new_rows = []
        total_samples = None

        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            parts = line.rsplit(maxsplit=1)
            if len(parts) != 2:
                continue

            value, count_text = parts

            try:
                count = int(count_text)
            except ValueError:
                continue

            if value.strip().casefold() == "total samples":
                total_samples = count
                continue

            new_rows.append({
                "category": category,
                "value": value.strip(),
                "count": count,
                "total_samples": total_samples,
            })

        # Einige Redbiom-Ausgaben führen "Total samples" erst am Ende auf.
        for row in new_rows:
            row["total_samples"] = total_samples

        if new_rows:
            counts_df = pd.concat(
                [counts_df, pd.DataFrame(new_rows)],
                ignore_index=True,
            )
            save_counts(counts_df)
            print(f"  Gespeichert: {len(new_rows)} Werte", flush=True)
        else:
            print(
                "  Keine Wertzeilen zurückgegeben; "
                "Kategorie wird nicht als abgeschlossen markiert.",
                flush=True,
            )

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {category}", flush=True)

    except subprocess.CalledProcessError as e:
        print(f"  FEHLER: {category}: {e.stderr}", flush=True)

    # Nach jedem Versuch Zusammenfassung und Übersicht aktualisieren.
    summary_df = rebuild_summary(counts_df)
    summary_df.to_csv(SUMMARY_FILE, sep="\t", index=False)
    write_overview(categories, summary_df)


# ============================================================
# 7. Finale Aktualisierung aller drei Ausgabedateien
# ============================================================

summary_df = rebuild_summary(counts_df)
summary_df.to_csv(SUMMARY_FILE, sep="\t", index=False)
write_overview(categories, summary_df)

print("\nFertig.")
print(f"Häufigkeiten:   {COUNTS_FILE.resolve()}")
print(f"Zusammenfassung: {SUMMARY_FILE.resolve()}")
print(f"Gruppierte Übersicht: {OVERVIEW_FILE.resolve()}")
