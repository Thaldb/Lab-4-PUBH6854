-- Lab 4 schema inspection and relationship checks.
-- Run from the repository root with:
-- sqlite3 -readonly -header -column \
--   data/raw/lab4-cbioportal-luad/cohort.db < sql/inspect_schema.sql

.tables

SELECT 'patients' AS table_name, COUNT(*) AS row_count FROM patients
UNION ALL
SELECT 'samples', COUNT(*) FROM samples
UNION ALL
SELECT 'mutations', COUNT(*) FROM mutations
UNION ALL
SELECT 'genes', COUNT(*) FROM genes;

PRAGMA table_info(patients);
PRAGMA table_info(samples);
PRAGMA table_info(mutations);
PRAGMA table_info(genes);

PRAGMA foreign_key_list(samples);
PRAGMA foreign_key_list(mutations);

-- Check identifiers and the observed patient-to-sample relationship.
SELECT
    (SELECT COUNT(*) FROM patients) AS patient_rows,
    (SELECT COUNT(DISTINCT patient_id) FROM patients) AS unique_patients,
    (SELECT COUNT(*) FROM samples) AS sample_rows,
    (SELECT COUNT(DISTINCT sample_id) FROM samples) AS unique_samples,
    (SELECT COUNT(DISTINCT patient_id) FROM samples) AS patients_with_samples;

SELECT patient_id, COUNT(*) AS sample_count
FROM samples
GROUP BY patient_id
HAVING COUNT(*) <> 1
ORDER BY sample_count DESC, patient_id;

-- Check for foreign-key values that do not match a parent row.
SELECT
    SUM(CASE WHEN p.patient_id IS NULL THEN 1 ELSE 0 END)
        AS samples_without_patient
FROM samples AS s
LEFT JOIN patients AS p
    ON p.patient_id = s.patient_id;

SELECT
    SUM(CASE WHEN s.sample_id IS NULL THEN 1 ELSE 0 END)
        AS mutations_without_sample,
    SUM(CASE WHEN g.gene_symbol IS NULL THEN 1 ELSE 0 END)
        AS mutations_without_gene
FROM mutations AS m
LEFT JOIN samples AS s
    ON s.sample_id = m.sample_id
LEFT JOIN genes AS g
    ON g.gene_symbol = m.gene_symbol;

-- Record missingness before constructing the feature table.
SELECT
    SUM(sex IS NULL) AS missing_sex,
    SUM(age_at_diagnosis IS NULL) AS missing_age,
    SUM(stage IS NULL) AS missing_stage
FROM patients;

SELECT
    SUM(tissue_source_site IS NULL) AS missing_site,
    SUM(tmb_nonsynonymous IS NULL) AS missing_tmb
FROM samples;

SELECT variant_classification, COUNT(*) AS mutation_count
FROM mutations
GROUP BY variant_classification
ORDER BY mutation_count DESC;
