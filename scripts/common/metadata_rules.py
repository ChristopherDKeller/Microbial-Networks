# Order is important: The first matching rule is used to group a category.
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
    ("mental_illness_and_neurological_conditions", [
        r"mental_illness|epilepsy_or_seizure_disorder|"
        r"depression_bipolar_schizophrenia|add_adhd|asd"
    ]),
    ("artificial_gi_disorder", [r"artificial_gi_disorder"]),
    ("covid", [r"covid|coronavirus|sars.?cov.?2"]),
    ("cancer", [r"cancer"]),
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