#Central registry of all AGP metadata features with completeness > 60 %.

# Target / grouping (never use as features)
TARGET = "ibd"
GROUP_COL = "host_subject_id"

# Fermented food items; the same 21 items exist for three question blocks
# (consumed / produce_commercial / produce_personal). Comment items out here
# to remove them from every block at once.
_FERMENTED_ITEMS = [
    "beer",
    "chicha",
    "cider",
    "cottage_cheese",
    "fermented_beansmisonatto",
    "fermented_breadsourdoughinjera",
    "fermented_fish",
    "fermented_tofu",
    "fish_sauce",
    "kefir_milk",
    "kefir_water",
    "kimchi",
    "kombucha",
    "mead",
    "pickled_vegetables",
    "sauerkraut",
    "sour_creamcreme_fraiche",
    "tempeh",
    # "unspecified",   # free-text "other" flag, almost always empty
    "wine",
    "yogurtlassi",
]

# --------------------------------------------------------------------------
# Feature registry:  CATEGORY -> list of features
# --------------------------------------------------------------------------
CATEGORIES: dict[str, list[str]] = {

    # ----------------------------------------------------------------------
    "DEMOGRAPHICS": [
        #"host_age_normalized_years",   # cleaned age in years (numeric)
        # "host_age",                  # redundant: raw age
        # "host_age_units",            # redundant: only the unit of host_age
        # "age_cat",                   # redundant: binned version of age
        # "birth_year",                # redundant: age = collection year - birth year
        # "lifestage",                 # redundant: binned version of age
        #"bmi_cat",                     # BMI category redundant: host_height / host_weight encode the same information
        # "host_height",               # redundant: encoded in BMI
        # "host_height_units",         # redundant: unit only
        # "host_weight",               # redundant: encoded in BMI
        # "host_weight_units",         # redundant: unit only
        "sex",
        "race",
        "country_of_birth",
        #"weight_change",              # unclear
    ],

    # ----------------------------------------------------------------------
    "SAMPLE": [
        # "host_body_mass_index",      # alternative to bmi_cat (numeric, has outliers); don't use both
        # "body_site",                 # redundant: same info as host_body_site (filtered to feces)
        # "host_body_site",            # constant after filtering to uberon:feces
        # "host_body_habitat",         # constant
        # "host_body_product",         # constant
        # "host_common_name",          # constant
        # "host_taxid",                # constant
        # "scientific_name",           # constant
        # "taxon_id",                  # constant
        # "dna_extracted",             # lab metadata, not biology
        # "physical_specimen_remaining",  # lab metadata
    ],

    # ----------------------------------------------------------------------
    "LIFESTYLE": [
        # "alcohol_consumption",       # redundant: alcohol_frequency is more detailed
        "alcohol_frequency",
        "alcohol_types_beercider",
        "alcohol_types_red_wine",
        "alcohol_types_sour_beers",
        "alcohol_types_spiritshard_alcohol",
        # "alcohol_types_unspecified", # uninformative "other" flag
        "alcohol_types_white_wine",
        "exercise_frequency",
        # "exercise_location",         # probably unnecessary (indoor / outdoor)
        # "pool_frequency",            # probably unnecessary
        "sleep_duration",
        "smoking_frequency",
    ],

    # ----------------------------------------------------------------------
    "LIFESTYLE_MISC": [
        # "dominant_hand",             # probably unnecessary
        # "last_move",                 # probably unnecessary
        "last_travel",
        "livingwith",
        # "nail_biter",                # probably unnecessary
        # "roommates_in_study",        # study-specific, 26 % missing
        # "softener",                  # probably unnecessary
        "types_of_plants",             # plant diversity (diet-diversity proxy)
        # "vivid_dreams",              # probably unnecessary, 32 % missing
    ],

    # ----------------------------------------------------------------------
    "HYGIENE": [
        # "cosmetics_frequency",       # probably unnecessary
        # "deodorant_use",             # probably unnecessary
        "flossing_frequency",
        "teethbrushing_frequency",
    ],

    # ----------------------------------------------------------------------
    "PETS_AND_SOCIAL": [
        "cat",
        "dog",
        "pets_other",
        "level_of_education",
    ],

    # ----------------------------------------------------------------------
    "ENVIRONMENT": [
        "drinking_water_source",
    ],

    # ----------------------------------------------------------------------
    "LOCATION": [
        "state",
        # "country_residence",         # redundant with state / country_of_birth, 30 % missing
        # "geo_loc_name",              # redundant with state, high cardinality
        # "latitude",                  # redundant with state, quasi-identifier
        # "longitude",                 # redundant with state, quasi-identifier
        # "env_biome",                 # constant
        # "env_feature",               # constant
        # "env_material",              # constant
        # "env_package",               # constant
    ],

    # ----------------------------------------------------------------------
    # DISEASE: other diagnoses. Some are clinically close to IBD (ibs, autoimmune,
    # clinical_condition); keep them for a "realistic" model, or exclude them
    # via exclude_features / exclude_categories for a "metadata-only without GI" model.
    # EXCLUDED: diagnoses correlate with each other / with IBD according to studies (incl. ibd = TARGET)
    # "DISEASE": [
    #     "alzheimers",
    #     "autoimmune",                  # NOTE: IBD is an autoimmune condition -> proxy
    #     "cardiovascular_disease",
    #     "clinical_condition",          # NOTE: generic field, may overlap with IBD
    #     "diabetes",
    #     "fungal_overgrowth",
        # "ibd",                       # TARGET -> must never be a feature
    #     "ibs",                         # NOTE: GI condition, strong proxy
    #     "kidney_disease",
    #     "liver_disease",
    #     "lung_disease",
    #     "migraine",
    #     "pku",
    #     "skin_condition",
    # ],

    # ----------------------------------------------------------------------
    # EXCLUDED: disease, same reason as DISEASE
    # "CANCER": [
    #     "cancer",                      # 36 % missing
    # ],

    # ----------------------------------------------------------------------
    # EXCLUDED: mental / neurological conditions correlate with IBD according to studies
    # "MENTAL_ILLNESS_AND_NEUROLOGICAL_CONDITIONS": [
    #     "add_adhd",
    #     "asd",
    #     "epilepsy_or_seizure_disorder",
        # "mental_illness",            # redundant: aggregate of the mental_illness_type_* columns, 36 % missing
    #     "mental_illness_type_anorexia_nervosa",
    #     "mental_illness_type_bipolar_disorder",
    #     "mental_illness_type_bulimia_nervosa",
    #     "mental_illness_type_depression",
    #     "mental_illness_type_ptsd_post_traumatic_stress_disorder",
    #     "mental_illness_type_schizophrenia",
    #     "mental_illness_type_substance_abuse",
        # "mental_illness_type_unspecified",  # uninformative "other" flag
    # ],

    # ----------------------------------------------------------------------
    "GUT_HEALTH": [                    # NOTE: GI symptoms are close proxies of IBD
        "acid_reflux",
        "bowel_movement_frequency",
        "bowel_movement_quality",
        # "cdiff",                    # disease (EXCLUDED: diagnoses correlate with IBD)
        # "sibo",                     # disease (EXCLUDED: diagnoses correlate with IBD)
    ],

    # ----------------------------------------------------------------------
    "MEDICAL_HISTORY": [
        "appendix_removed",
        "thyroid",
        "tonsils_removed",
    ],

    # ----------------------------------------------------------------------
    "REPRODUCTIVE_EARLY_LIFE": [
        "breastmilk_formula_ensure",
        "csection",
        "fed_as_infant",
        "pregnant",
    ],

    # ----------------------------------------------------------------------
    "MEDICATION": [
        "acne_medication",
        "antibiotic_history",
        "contraceptive",
        "multivitamin",
        "other_supplement_frequency",
        "vitamin_b_supplement_frequency",
        "vitamin_d_supplement_frequency",
    ],

    # ----------------------------------------------------------------------
    "IMMUNITIES": [
        # "chickenpox",                # probably unnecessary
        # "flu_vaccine_date",          # probably unnecessary
    ],

    # ----------------------------------------------------------------------
    "INTOLERANCES": [
        "gluten",
        "lactose",
    ],

    # ----------------------------------------------------------------------
    "FOOD_ALLERGIES": [
        # "allergic_to_i_have_no_food_allergies_that_i_know_of",  # redundant: inverse of the other allergic_to_* columns
        "allergic_to_peanuts",
        "allergic_to_shellfish",
        "allergic_to_tree_nuts",
        # "allergic_to_unspecified",   # uninformative "other" flag
        # "covid_chronic_conditions_seasonal_allergies",  # redundant with seasonal_allergies
        "seasonal_allergies",
    ],

    # ----------------------------------------------------------------------
    "NON_FOOD_ALLERGIES": [
        "non_food_allergies_beestings",
        "non_food_allergies_drug_eg_penicillin",
        "non_food_allergies_pet_dander",
        "non_food_allergies_poison_ivyoak",
        "non_food_allergies_sun",
        # "non_food_allergies_unspecified",  # uninformative "other" flag
    ],

    # ----------------------------------------------------------------------
    "DIET": [
        "artificial_sweeteners",       # 30 % missing
        "consume_animal_products_abx",
        "diet_type",
        "frozen_dessert_frequency",
        "fruit_frequency",
        "high_fat_red_meat_frequency",
        "homecooked_meals_frequency",
        # "meat_eggs_frequency",       # redundant: aggregate of red_meat / poultry / seafood / eggs
        "milk_cheese_frequency",
        "milk_substitute_frequency",
        "olive_oil",
        "one_liter_of_water_a_day_frequency",
        "poultry_frequency",
        "prepared_meals_frequency",
        "probiotic_frequency",
        "ready_to_eat_meals_frequency",
        "red_meat_frequency",
        "salted_snacks_frequency",
        "seafood_frequency",
        "sugar_sweetened_drink_frequency",
        "sugary_sweets_frequency",
        "vegetable_frequency",
        "whole_eggs",
        "whole_grain_frequency",
    ],

    # ----------------------------------------------------------------------
    "SPECIALIZED_DIET": [
        "specialized_diet_exclude_dairy",
        "specialized_diet_exclude_nightshades",
        "specialized_diet_exclude_refined_sugars",
        "specialized_diet_fodmap",
        "specialized_diet_halaal",
        # "specialized_diet_i_do_not_eat_a_specialized_diet",  # redundant: inverse of the other specialized_diet_* columns
        "specialized_diet_kosher",
        "specialized_diet_modified_paleo_diet",
        "specialized_diet_other_restrictions_not_described_here",
        "specialized_diet_paleo_diet_or_primal_diet",
        "specialized_diet_raw_food_diet",
        # "specialized_diet_unspecified",  # uninformative "other" flag
        "specialized_diet_weston_price_or_other_low_grain_low_processed_food_diet",
    ],

    # ----------------------------------------------------------------------
    "FERMENTED_CONSUMED": [
        *[f"fermented_consumed_{item}" for item in _FERMENTED_ITEMS],
        "fermented_plant_frequency",   # 23 % missing
    ],
    # Where the fermented food came from: probably unnecessary
    # "FERMENTED_PRODUCE_COMMERCIAL": [f"fermented_produce_commercial_{item}" for item in _FERMENTED_ITEMS],
    # "FERMENTED_PRODUCE_PERSONAL":   [f"fermented_produce_personal_{item}" for item in _FERMENTED_ITEMS],

    # ----------------------------------------------------------------------
    # COVID: chronic conditions. Many duplicate DISEASE columns (commented out).
    # EXCLUDED: all COVID-related features removed (too specific); also disease columns
    # "COVID_CHRONIC_CONDITIONS": [
        # "covid_chronic_conditions_any_autoimmune_disease",   # redundant: autoimmune
    #     "covid_chronic_conditions_arthritis",
        # "covid_chronic_conditions_asthma_or_other_lung_problems",  # redundant: lung_disease
    #     "covid_chronic_conditions_atrial_fibrillation_or_atrial_flutter",
        # "covid_chronic_conditions_cancer",                   # redundant: cancer
    #     "covid_chronic_conditions_chronic_obstructive_pulmonary_disease_copd",
    #     "covid_chronic_conditions_congestive_heart_failure",
    #     "covid_chronic_conditions_deep_vein_thrombosis",
        # "covid_chronic_conditions_diabetes_or_high_blood_sugar",  # redundant: diabetes
        # "covid_chronic_conditions_epilepsy_or_seizures",     # redundant: epilepsy_or_seizure_disorder
        # "covid_chronic_conditions_frequent_or_very_bad_headaches",  # redundant: migraine
    #     "covid_chronic_conditions_heart_disease__myocardial_infarction",
    #     "covid_chronic_conditions_heart_problems",
    #     "covid_chronic_conditions_hiv",
    #     "covid_chronic_conditions_hypertension",
    #     "covid_chronic_conditions_immune_disorder",
        # "covid_chronic_conditions_kidney_problems",          # redundant: kidney_disease
    #     "covid_chronic_conditions_pulmonary_embolism",
        # "covid_chronic_conditions_serious_acne_or_skin_problems",  # redundant: skin_condition
    #     "covid_chronic_conditions_serious_stomach_or_bowel_problems",  # NOTE: strong IBD proxy
    #     "covid_chronic_conditions_stroke",
        # "covid_chronic_conditions_unspecified",              # uninformative "other" flag
    # ],

    # ----------------------------------------------------------------------
    # COVID: symptoms at time of sampling. Only GI-related ones kept.
    # EXCLUDED: all COVID-related features removed (too specific)
    # "COVID_SYMPTOMS": [
        # "covid_symptoms_chest_pain_or_tightness_in_chest",   # acute, unrelated to IBD
        # "covid_symptoms_cough",
    #     "covid_symptoms_diarrhea",
        # "covid_symptoms_fatigue",
        # "covid_symptoms_fever",
    #     "covid_symptoms_lack_of_appetitie",                    # (sic) spelling as in the data
        # "covid_symptoms_loss_of_taste_or_smell",
    #     "covid_symptoms_nausea",
        # "covid_symptoms_shortness_of_breath",
        # "covid_symptoms_sore_throat",
        # "covid_symptoms_unspecified",
    # ],

    # ----------------------------------------------------------------------
    # COVID: pandemic circumstances. Probably unnecessary for IBD -> all commented out.
    # "COVID_EXPOSURE_AND_IMPACT": [
    #     "covid_likely_exposure_no",
    #     "covid_likely_exposure_unspecified",
    #     "covid_likely_exposure_yes_someone_with_medical_diagnosis_but_no_test",
    #     "covid_likely_exposure_yes_someone_with_positive_test",
    #     "covid_likely_exposure_yes_someone_with_possible_symptoms_but_no_diagnosis_by_doctor",
    #     "covid_family_members_fallen_ill_physically",
    #     "covid_family_members_hospitalized",
    #     "covid_family_members_lost_job",
    #     "covid_family_members_none_of_the_above",
    #     "covid_family_members_passed_away",
    #     "covid_family_members_put_into_self_quarantine_with_symptoms",
    #     "covid_family_members_put_into_self_quarantine_without_symptoms_eg_due_to_possible_exposure",
    #     "covid_family_members_reduced_ability_to_earn_money",
    #     "covid_family_members_unspecified",
    #     "covid_happened_to_you_fallen_ill_physically",
    #     "covid_happened_to_you_hospitalized",
    #     "covid_happened_to_you_lost_job",
    #     "covid_happened_to_you_none_of_the_above",
    #     "covid_happened_to_you_put_into_self_quarantine_with_symptoms",
    #     "covid_happened_to_you_put_into_self_quarantine_without_symptoms_eg_due_to_possible_exposure",
    #     "covid_happened_to_you_reduced_ability_to_earn_money",
    #     "covid_happened_to_you_unspecified",
    # ],

    # ----------------------------------------------------------------------
    # SAMPLE_STUDY / STUDY_METADATA: identifiers, dates and constants, not features
    # (collection_date / collection_timestamp could leak batch effects, so keep them out)
    # "SAMPLE_STUDY": [
    #     "collection_date", "collection_timestamp", "empo_1", "empo_2", "empo_3",
    #     "host_subject_id",   # used as group, see GROUP_COL
    #     "qiita_study_id", "sample_type", "physical_specimen_location",
    # ],
    # "STUDY_METADATA": ["anonymized_name", "description", "public", "title"],
}

# --------------------------------------------------------------------------
# TODO Numeric features (everything else is treated as categorical)
# at the moment all disabled
# --------------------------------------------------------------------------
NUMERIC_FEATURES = [
    "host_age",
    "host_height",
    "host_weight",
]


CATEGORICAL_FEATURES = list(dict.fromkeys(
    feature
    for category_features in CATEGORIES.values()
    for feature in category_features
))

FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
FEATURES = [
    f for f in FEATURES
    if f not in {TARGET, GROUP_COL}
]
