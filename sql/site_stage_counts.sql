-- Expected observed tissue-site/stage groups: 142.
-- Actual groups: 142; patient_count sums to all 566 patients.
SELECT
    s.tissue_source_site,
    COALESCE(p.stage, '[Missing]') AS stage,
    COUNT(DISTINCT p.patient_id) AS patient_count
FROM patients AS p
LEFT JOIN samples AS s
    ON s.patient_id = p.patient_id
GROUP BY
    s.tissue_source_site,
    COALESCE(p.stage, '[Missing]')
ORDER BY
    s.tissue_source_site,
    stage;
