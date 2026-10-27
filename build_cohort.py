from pathlib import Path
import subprocess
import zipfile

import pandas as pd


# ============================================================
# Konfiguration
# ============================================================

BASE_DIR = Path("data")
RAW_DIR = BASE_DIR / "raw"
EXTRACT_DIR = RAW_DIR / "AGP-sample-information"

ZIP_PATH = RAW_DIR / "AGP-sample-information.zip"

DOWNLOAD_URL = (
    "https://qiita.ucsd.edu/public_download/"
    "?data=sample_information&study_id=10317"
)

# Alle Kohortendefinitionen lassen sich hier erweitern.
#general_criteria = [
#    # Sample type
#    ("host_body_site", ["UBERON:feces"]),
#
#    # Other diseases: explicitly absent or not provided/collected
#    ("lung_disease",["I do not have this condition"]),
#    ("ibd_diagnosis_refined",["not provided", "not applicable"]),
#    ("skin_condition",["I do not have this condition"]),
#    ("alzheimers",["I do not have this condition"]),
#    ("diabetes",["I do not have this condition"]),
#    ("pku",["I do not have this condition"]),
#    ("fungal_overgrowth",["I do not have this condition", "not provided"]),
#    ("kidney_disease",["I do not have this condition"]),
#    ("migraine",["I do not have this condition"]),
#    ("cardiovascular_disease",["I do not have this condition"]),
#    ("ibd",["I do not have this condition"]),
#    ("clinical_condition",["I do not have this condition"]),
#    ("liver_disease",["I do not have this condition"]),
#    ("autoimmune",["I do not have this condition"]),
#    ("ibs",["I do not have this condition"]),
#    ("diabetes_type",["not provided"]),
#    ("cancer",["I do not have this condition", "not provided"]),
#    # Mental illness
#    ("epilepsy_or_seizure_disorder", ["I do not have this condition", "not collected", "not provided"]),
#    ("mental_illness_type_anorexia_nervosa", ["false", "not collected", "not applicable"]),
#    ("mental_illness_type_schizophrenia", ["false", "not collected", "not applicable"]),
#    ("mental_illness_type_bipolar_disorder", ["false", "not collected", "not applicable"]),
#    ("mental_illness_type_substance_abuse", ["false", "not collected", "not applicable"]),
#    #("depression_bipolar_schizophrenia", ["I do not have this condition", "not collected", "not provided"]),
#    ("mental_illness_type_ptsd_post_traumatic_stress_disorder", ["false", "not collected", "not applicable"]),
#    ("mental_illness_type_unspecified", ["false", "not collected", "not applicable"]),
#    ("add_adhd", ["I do not have this condition", "not collected", "not provided", "not applicable"]),
#    ("asd", ["I do not have this condition", "not collected", "not provided", "not applicable"]),
#    ("mental_illness_type_bulimia_nervosa", ["false", "not collected", "not applicable"]),
#    # Antibiotic history
#    ("antibiotic_history", ["I have not taken antibiotics in the past year.", "Year", "not collected", "not provided", "not applicable"]),
#]
#14000 ganz ohne antibiotika 9000 antibiotika streng 12000 antibiotika locker
#missing values filter nichts verändert
#sql mässig prüfen wie viel menschen eine krankheit haben

# Common representations of missing values in metadata
MISSING_VALUES = [
    None,
    "",
    " ",
    "None",
    "none",
    "NULL",
    "null",
    "NaN",
    "nan",
    "N/A",
    "n/a",
    "not provided",
    "not collected",
    "not applicable",
]

general_criteria = [
    # Sample type
    ("host_body_site", ["UBERON:feces"]),

    # Other diseases: explicitly absent or missing
    #("lung_disease", ["I do not have this condition"] + MISSING_VALUES),
    ##("ibd_diagnosis_refined", MISSING_VALUES),
    #("skin_condition", ["I do not have this condition"] + MISSING_VALUES),
    #("alzheimers", ["I do not have this condition"] + MISSING_VALUES),
    #("diabetes", ["I do not have this condition"] + MISSING_VALUES),
    #("pku", ["I do not have this condition"] + MISSING_VALUES),
    #("fungal_overgrowth", ["I do not have this condition"] + MISSING_VALUES),
    #("kidney_disease", ["I do not have this condition"] + MISSING_VALUES),
    #("migraine", ["I do not have this condition"] + MISSING_VALUES),
    #("cardiovascular_disease", ["I do not have this condition"] + MISSING_VALUES),
    #("ibd", ["I do not have this condition"] + MISSING_VALUES),
    #("clinical_condition", ["I do not have this condition"] + MISSING_VALUES),
    #("liver_disease", ["I do not have this condition"] + MISSING_VALUES),
    #("autoimmune", ["I do not have this condition"] + MISSING_VALUES),
    #("ibs", ["I do not have this condition"] + MISSING_VALUES),
    #("diabetes_type", MISSING_VALUES),
    #("cancer", ["I do not have this condition"] + MISSING_VALUES),

    # Mental illness
    ("epilepsy_or_seizure_disorder", ["I do not have this condition"] + MISSING_VALUES),
    ("mental_illness_type_anorexia_nervosa", ["false"] + MISSING_VALUES),
    ("mental_illness_type_schizophrenia", ["false"] + MISSING_VALUES),
    ("mental_illness_type_bipolar_disorder", ["false"] + MISSING_VALUES),
    ("mental_illness_type_substance_abuse", ["false"] + MISSING_VALUES),
    # ("depression_bipolar_schizophrenia",  ["I do not have this condition"] + MISSING_VALUES),
    ("mental_illness_type_ptsd_post_traumatic_stress_disorder", ["false"] + MISSING_VALUES),
    ("mental_illness_type_unspecified", ["false"] + MISSING_VALUES),
    ("add_adhd", ["I do not have this condition"] + MISSING_VALUES),
    ("asd", ["I do not have this condition"] + MISSING_VALUES),
    ("mental_illness_type_bulimia_nervosa", ["false"] + MISSING_VALUES),

    # Antibiotic history
    ("antibiotic_history",
     ["I have not taken antibiotics in the past year.", "Year"] + MISSING_VALUES),
]

COHORTS = {
    "depression_case": {
        "criteria": [
            ("mental_illness_type_depression", ["true"]),
            #("mental_illness", ["No", "not provided"])
        ],
    },
    "control": {
        "criteria": [
            ("mental_illness_type_depression", ["false", "not collected"]),
        ],
    },
}

# Ausgabedateien
ALL_ASSIGNMENTS_PATH = BASE_DIR / "AGP-cohort-assignments.tsv"
COHORT_PATH = BASE_DIR / "AGP-cohort-depression.tsv"
SUMMARY_PATH = BASE_DIR / "AGP-cohort-summary.tsv"


# ============================================================
# 1. Verzeichnisse erstellen
# ============================================================

RAW_DIR.mkdir(parents=True, exist_ok=True)
BASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. Metadaten herunterladen, falls Metadaten nicht vorhanden
# ============================================================
matching_files = list(EXTRACT_DIR.glob("10317*.txt"))

if matching_files and matching_files[0].stat().st_size > 0:
    print(f"Daten bereits in \"{EXTRACT_DIR}\" vorhanden.")
else:
    print("Lade AGP-Metadaten herunter ...")

    subprocess.run(
        [
            "wget",
            "-O",
            str(ZIP_PATH),
            DOWNLOAD_URL,
        ],
        check=True,
    )

    if not ZIP_PATH.exists() or ZIP_PATH.stat().st_size == 0:
        raise RuntimeError("Download fehlgeschlagen: ZIP fehlt oder ist leer.")

    print(f"Download abgeschlossen: {ZIP_PATH}")


# ============================================================
# 3. ZIP entpacken, falls noch keine TXT-Datei vorhanden ist
# ============================================================

def find_txt_files(directory: Path) -> list[Path]:
    """TXT-Dateien direkt im Zielordner finden."""
    return sorted(
        path
        for path in directory.glob("*.txt")
        if path.is_file()
    )


txt_files = (
    find_txt_files(EXTRACT_DIR)
    if EXTRACT_DIR.exists()
    else []
)

if not txt_files:
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    print("Entpacke ZIP-Datei ...")

    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        root = EXTRACT_DIR.resolve()

        for member in archive.infolist():
            if member.is_dir():
                continue

            # Den templates/-Präfix entfernen
            relative_path = Path(member.filename)

            if relative_path.parts and relative_path.parts[0] == "templates":
                relative_path = Path(*relative_path.parts[1:])

            # Andere Verzeichnisse unverändert behandeln
            target = (EXTRACT_DIR / relative_path).resolve()

            if not target.is_relative_to(root):
                raise RuntimeError(
                    f"Unsicherer ZIP-Dateipfad: {member.filename}"
                )

        for member in archive.infolist():
            if member.is_dir():
                continue

            relative_path = Path(member.filename)

            if relative_path.parts and relative_path.parts[0] == "templates":
                relative_path = Path(*relative_path.parts[1:])

            if not relative_path.parts:
                continue

            target = EXTRACT_DIR / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)

            with archive.open(member) as source, target.open("wb") as destination:
                destination.write(source.read())

    txt_files = find_txt_files(EXTRACT_DIR)

    if not txt_files:
        raise FileNotFoundError(
            f"Keine TXT-Datei direkt im Zielordner gefunden: {EXTRACT_DIR}"
        )

    # ZIP erst nach erfolgreichem Entpacken und Validieren löschen
    ZIP_PATH.unlink()
    print(f"ZIP-Datei gelöscht: {ZIP_PATH}")

# Erste Datei nach alphabetischer Sortierung
metadata_path = txt_files[0]

print(f"Verwende Metadatendatei: {metadata_path}")


# ============================================================
# 4. TSV einlesen
# ============================================================

df = pd.read_csv(
    metadata_path,
    sep="\t",
    dtype=str,
    keep_default_na=False,
)

df.columns = df.columns.str.strip()

print(f"Metadaten geladen: {len(df)} Zeilen, {len(df.columns)} Spalten")


# ============================================================
# 5. Benötigte Spalten prüfen
# ============================================================

required_columns = {
    column
    for cohort in COHORTS.values()
    for column, _ in cohort["criteria"]
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise KeyError(
        "Folgende benötigte Metadatenspalten fehlen: "
        + ", ".join(sorted(missing_columns))
    )


# ============================================================
# 6. Kohortenbedingungen auswerten
# ============================================================

def normalize_value(value, missing_values=MISSING_VALUES):
    """Normalize values; configured missing values become None."""
    if pd.isna(value):
        return None

    normalized = str(value).strip().casefold()

    normalized_missing = {
        str(v).strip().casefold()
        for v in missing_values
        if v is not None and not pd.isna(v)
    }

    if value is None or normalized in normalized_missing:
        return None

    return normalized


def matches_criteria(
    data: pd.DataFrame,
    criteria: list[tuple[str, list]],
) -> pd.Series:
    """All criteria must match (AND logic)."""

    mask = pd.Series(True, index=data.index)

    for column, allowed_values in criteria:
        if column not in data.columns:
            raise KeyError(f"Metadatenspalte fehlt: {column}")

        actual = data[column].map(normalize_value)

        allowed = {
            normalize_value(value)
            for value in allowed_values
        }

        mask &= actual.isin(allowed)

    return mask


# Allgemeine Kriterien gelten für alle Kohorten.
general_mask = matches_criteria(df, general_criteria)

# Kohortenspezifische Kriterien zusätzlich anwenden.
matches = {
    name: general_mask & matches_criteria(
        df,
        definition["criteria"],
    )
    for name, definition in COHORTS.items()
}

case_mask = matches["depression_case"]
control_mask = matches["control"]

conflict_mask = case_mask & control_mask

group = pd.Series(
    "not_selected",
    index=df.index,
    dtype="string",
)

group.loc[case_mask & ~control_mask] = "depression_case"
group.loc[control_mask & ~case_mask] = "control"
group.loc[conflict_mask] = "conflict"

# Separate Kennzeichnung für die vollständige Tabelle
assignments = df.copy()
assignments["cohort_group"] = group

# Alle Metadaten einschließlich Gruppenzuordnung speichern.
assignments.to_csv(
    ALL_ASSIGNMENTS_PATH,
    sep="\t",
    index=False,
)


# ============================================================
# 7. Ausgewählte Kohorte exportieren
# ============================================================

selected = assignments[
    assignments["cohort_group"].isin(
        ["depression_case", "control"]
    )
].copy()

selected.to_csv(
    COHORT_PATH,
    sep="\t",
    index=False,
)


# ============================================================
# 8. Zusammenfassung erstellen
# ============================================================

summary_rows = [
    {
        "cohort_group": name,
        "n_samples": int(mask.sum()),
    }
    for name, mask in matches.items()
]

summary_rows.extend([
    {
        "cohort_group": "conflict",
        "n_samples": int(conflict_mask.sum()),
    },
    {
        "cohort_group": "not_selected",
        "n_samples": int((group == "not_selected").sum()),
    },
    {
        "cohort_group": "selected_total",
        "n_samples": len(selected),
    },
])

summary = pd.DataFrame(summary_rows)

summary.to_csv(
    SUMMARY_PATH,
    sep="\t",
    index=False,
)

print("\nKohortenzusammenfassung:")
print(summary.to_string(index=False))

print("\nErstellte Dateien:")
print(f"Alle Gruppenzuordnungen: {ALL_ASSIGNMENTS_PATH}")
print(f"Ausgewählte Kohorte:     {COHORT_PATH}")
print(f"Zusammenfassung:         {SUMMARY_PATH}")
