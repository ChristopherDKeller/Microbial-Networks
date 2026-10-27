
import re
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("redbiom_metadata.tsv")
OUTPUT_FILE = Path("metadata_categories.txt")

metadata = pd.read_csv(
    INPUT_FILE,
    sep="\t",
    low_memory=False,
    nrows=0,  # Nur Spaltennamen einlesen
)

columns = metadata.columns.tolist()

# Reihenfolge ist wichtig: spezifische Regeln vor allgemeinen Regeln.

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
    ("mental_illness", [r"mental_illness|epilepsy_or_seizure_disorder|depression_bipolar_schizophrenia|add_adhd|asd"]),
    ("artificial_gi_disorder", [r"artificial_gi_disorder"]),
    ("cancer", [r"cancer"]),
    ("covid", [r"covid|coronavirus|sars.?cov.?2"]),
    ("disease", [
        r"disease|diagnos|clinical_condition|condition_",
        r"diabetes|ibd|asthma|skin_condition|alzheimers|fungal_overgrowth|migraine|autoimmune|ibs|pku",
    ]),
    ("medication", [
        r"medication|meds|prescription|antibiotic|supplement|contraceptive|multivitamin"
    ]),
    ("immunities", [
        r"flu_vaccine_date|chickenpox"
    ]),
    ("intolerances", [
        r"gluten|lactose"
    ]),
    ("gut_health", [
        r"acid_reflux",
        r"bowel_movement",
        r"sibo",
        r"cdiff",
        r"coprophage",
    ]),
    # Medizinische Vorgeschichte und Gesundheitsstatus
    ("medical_history", [
        r"appendix_removed",
        r"tonsils_removed",
        r"thyroid",
        r"subset_healthy",
    ]),
    # Schwangerschaft, frühe Ernährung und Lebensphase
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
        r"smok|alcohol|drinks|stress|sleep|exercise|physical_activity|weekday_wake_time|weekend_wake_time|hours_outside|pool_frequency"
    ]),
    # Wohnen und sonstiger Lebensstil
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
        r"softener"
    ]),
    ("hygiene", [
        r"deodorant_use|cosmetics_frequency|teethbrushing_frequency|flossing_frequency"
    ]),

    #Haustiere
    ("pets", [r"pet|dog|cat|animal_type|animal_gender|animal_origin"]),

    # Ernährung außerhalb von Vioscreen
    ("fermented", [r"fermented"]),
    ("diet", [
    # Allgemeine Ernährungsvariablen
    r"diet|food|meal|fasting|fiber|fibre|nutrition",

    # Einzelne Lebensmittel
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

    # Häufigkeiten und Ernährungsgewohnheiten
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

    # Weitere ernährungsbezogene Angaben
    r"consume_animal_products_abx",
    ]),

    # Proben- und Studieninformationen
    ("sample_study", [
        r"sample|study|collection|empo|run_accession|subject_id"
    ]),

    # Sample Information
    ("sample", [r"^host_|body|scientific_name|dna_extracted|physical_specimen_remaining|taxon_id",]),

    # Location
    ("location", [r"longitude|latitude|country|region|geo|elevation|state|thdmi_cohort|^env_"]),

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

categories = {name: [] for name, _ in RULES}
categories["other"] = []

for col in columns:
    name = col.lower()
    for category, patterns in RULES:
        if any(re.search(pattern, name) for pattern in patterns):
            categories[category].append(col)
            break
    else:
        categories["other"].append(col)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    for category, cols in categories.items():
        f.write(f"{category.upper()} ({len(cols)})\n")
        f.write(";".join(cols) + "\n\n")

print(f"Gespeichert: {OUTPUT_FILE.resolve()}")
for category, cols in categories.items():
    print(f"{category}: {len(cols)}")
