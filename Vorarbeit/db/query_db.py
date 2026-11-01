
import duckdb

con = duckdb.connect("data/AGP-metadata.duckdb", read_only=True)

queries = {
    "Depression feces sample count": """
        SELECT COUNT(*)
        FROM agp_metadata
        WHERE lower(trim(mental_illness_type_depression)) == 'true' 
        AND lower(trim(host_body_site)) = 'uberon:feces'
    """,

    "At least one Condition": """
        SELECT COUNT(*) AS samples_with_any_condition
        FROM agp_metadata
        WHERE lower(trim(host_body_site)) = 'uberon:feces'
        AND (
            lower(trim(lung_disease)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(skin_condition)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(alzheimers)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(diabetes)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(pku)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(fungal_overgrowth)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(kidney_disease)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(migraine)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(cardiovascular_disease)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(ibd)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(clinical_condition)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(liver_disease)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(autoimmune)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(ibs)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(cancer)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(epilepsy_or_seizure_disorder)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(mental_illness_type_anorexia_nervosa)) = 'true'
            OR lower(trim(mental_illness_type_schizophrenia)) = 'true'
            OR lower(trim(mental_illness_type_bipolar_disorder)) = 'true'
            OR lower(trim(mental_illness_type_substance_abuse)) = 'true'
            OR lower(trim(mental_illness_type_ptsd_post_traumatic_stress_disorder)) = 'true'
            OR lower(trim(mental_illness_type_unspecified)) = 'true'
            OR lower(trim(add_adhd)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(asd)) =
                'diagnosed by a medical professional (doctor, physician assistant)'
            OR lower(trim(mental_illness_type_bulimia_nervosa)) = 'true'
        );
    """,

    "Healthy count": """
        SELECT COUNT(*) AS samples_with_no_reported_conditions
            FROM agp_metadata
            WHERE lower(trim(host_body_site)) = 'uberon:feces'
            AND (
                lower(trim(lung_disease)) = 'i do not have this condition'
                OR lung_disease IS NULL OR trim(lung_disease) = ''
            )
            AND (
                lower(trim(skin_condition)) = 'i do not have this condition'
                OR skin_condition IS NULL OR trim(skin_condition) = ''
            )
            AND (
                lower(trim(alzheimers)) = 'i do not have this condition'
                OR alzheimers IS NULL OR trim(alzheimers) = ''
            )
            AND (
                lower(trim(diabetes)) = 'i do not have this condition'
                OR diabetes IS NULL OR trim(diabetes) = ''
            )
            AND (
                lower(trim(pku)) = 'i do not have this condition'
                OR pku IS NULL OR trim(pku) = ''
            )
            AND (
                lower(trim(fungal_overgrowth)) = 'i do not have this condition'
                OR fungal_overgrowth IS NULL OR trim(fungal_overgrowth) = ''
            )
            AND (
                lower(trim(kidney_disease)) = 'i do not have this condition'
                OR kidney_disease IS NULL OR trim(kidney_disease) = ''
            )
            AND (
                lower(trim(migraine)) = 'i do not have this condition'
                OR migraine IS NULL OR trim(migraine) = ''
            )
            AND (
                lower(trim(cardiovascular_disease)) = 'i do not have this condition'
                OR cardiovascular_disease IS NULL OR trim(cardiovascular_disease) = ''
            )
            AND (
                lower(trim(ibd)) = 'i do not have this condition'
                OR ibd IS NULL OR trim(ibd) = ''
            )
            AND (
                lower(trim(clinical_condition)) = 'i do not have this condition'
                OR clinical_condition IS NULL OR trim(clinical_condition) = ''
            )
            AND (
                lower(trim(liver_disease)) = 'i do not have this condition'
                OR liver_disease IS NULL OR trim(liver_disease) = ''
            )
            AND (
                lower(trim(autoimmune)) = 'i do not have this condition'
                OR autoimmune IS NULL OR trim(autoimmune) = ''
            )
            AND (
                lower(trim(ibs)) = 'i do not have this condition'
                OR ibs IS NULL OR trim(ibs) = ''
            )
            AND (
                lower(trim(cancer)) = 'i do not have this condition'
                OR cancer IS NULL OR trim(cancer) = ''
            )
            AND (
                lower(trim(epilepsy_or_seizure_disorder)) = 'i do not have this condition'
                OR epilepsy_or_seizure_disorder IS NULL
                OR trim(epilepsy_or_seizure_disorder) = ''
            )
            AND (
                lower(trim(mental_illness_type_anorexia_nervosa)) = 'false'
                OR mental_illness_type_anorexia_nervosa IS NULL
                OR trim(mental_illness_type_anorexia_nervosa) = ''
            )
            AND (
                lower(trim(mental_illness_type_schizophrenia)) = 'false'
                OR mental_illness_type_schizophrenia IS NULL
                OR trim(mental_illness_type_schizophrenia) = ''
            )
            AND (
                lower(trim(mental_illness_type_bipolar_disorder)) = 'false'
                OR mental_illness_type_bipolar_disorder IS NULL
                OR trim(mental_illness_type_bipolar_disorder) = ''
            )
            AND (
                lower(trim(mental_illness_type_substance_abuse)) = 'false'
                OR mental_illness_type_substance_abuse IS NULL
                OR trim(mental_illness_type_substance_abuse) = ''
            )
            AND (
                lower(trim(mental_illness_type_ptsd_post_traumatic_stress_disorder)) = 'false'
                OR mental_illness_type_ptsd_post_traumatic_stress_disorder IS NULL
                OR trim(mental_illness_type_ptsd_post_traumatic_stress_disorder) = ''
            )
            AND (
                lower(trim(mental_illness_type_unspecified)) = 'false'
                OR mental_illness_type_unspecified IS NULL
                OR trim(mental_illness_type_unspecified) = ''
            )
            AND (
                lower(trim(add_adhd)) = 'i do not have this condition'
                OR add_adhd IS NULL OR trim(add_adhd) = ''
            )
            AND (
                lower(trim(asd)) = 'i do not have this condition'
                OR asd IS NULL OR trim(asd) = ''
            )
            AND (
                lower(trim(mental_illness_type_bulimia_nervosa)) = 'false'
                OR mental_illness_type_bulimia_nervosa IS NULL
                OR trim(mental_illness_type_bulimia_nervosa) = ''
            );
    """,

    "Feces count": """
        SELECT COUNT(*) AS fecessamples
        FROM agp_metadata
        WHERE lower(trim(host_body_site)) = 'uberon:feces'
    """,

    "Subject Sample Count": """
        SELECT
            CASE WHEN n = 1 THEN 'single_sample' ELSE 'multiple_samples' END AS category,
            COUNT(*) AS num_subjects
        FROM (
            SELECT host_subject_id, COUNT(*) AS n
            FROM agp_metadata
            WHERE lower(trim(host_body_site)) = 'uberon:feces'
            GROUP BY host_subject_id
        ) AS per_subject
        GROUP BY category;
    """
}

try:
    for title, sql in queries.items():
        print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")
        print(con.execute(sql).df().to_string(index=False))
finally:
    con.close()
