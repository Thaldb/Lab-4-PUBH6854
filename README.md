# PUBH 6854 Lab 4: Database-Driven Feature Table

## Project overview

This project constructs an analysis-ready feature table from a relational
SQLite database derived from the TCGA Lung Adenocarcinoma PanCancer Atlas
study. The final table will contain exactly one row per patient and will
combine clinical characteristics, tumor sample characteristics, and counts of
protein-altering mutations in five genes.

## Data

The course-provided database is expected at:

```text
data/raw/lab4-cbioportal-luad/cohort.db
```

It contains 566 de-identified patients. The database was provided for this
lab and should not be replaced with the Week 8 demonstration database.

## Repository structure

```text
.
├── README.md
├── AI_USAGE.md
├── environment.yml
├── data/
│   ├── raw/lab4-cbioportal-luad/cohort.db
│   └── processed/
│       ├── data_dictionary.tsv
│       └── patient_features.tsv
├── sql/
│   ├── gene_counts.sql
│   ├── inspect_schema.sql
│   └── site_stage_counts.sql
└── src/
    └── build_feature_table.py
```

## Reproduce the feature table

Create and activate the supplied Conda environment from the repository root:

```bash
conda env create -f environment.yml
conda activate pubh6854-lab4
```

The single command that rebuilds the feature table from `cohort.db` is:

```bash
python src/build_feature_table.py
```

The script expects the database at the path shown in the Data section and
writes `data/processed/patient_features.tsv`. It prints row counts,
missing-value counts, and a manual patient check while running. The committed
data dictionary is `data/processed/data_dictionary.tsv`.

## Schema inspection

Run the saved schema and integrity checks from the repository root:

```bash
sqlite3 -readonly -header -column \
  data/raw/lab4-cbioportal-luad/cohort.db < sql/inspect_schema.sql
```

### Tables and grain

#### `patients`

One row represents one patient. The table contains 566 rows and 566 unique
patient identifiers.

| Column | Type | Key or meaning |
|---|---|---|
| `patient_id` | TEXT | Primary key |
| `sex` | TEXT | Recorded sex |
| `age_at_diagnosis` | REAL | Age at diagnosis |
| `stage` | TEXT | Tumor stage |
| `vital_status` | TEXT | Vital status |
| `followup_months` | REAL | Follow-up time in months |

#### `samples`

One row represents one tumor sample. The table contains 566 rows and 566
unique sample identifiers.

| Column | Type | Key or meaning |
|---|---|---|
| `sample_id` | TEXT | Primary key |
| `patient_id` | TEXT | Foreign key to `patients.patient_id` |
| `tissue_source_site` | TEXT | Tissue source site |
| `tmb_nonsynonymous` | REAL | Nonsynonymous tumor mutation burden |
| `aneuploidy_score` | REAL | Aneuploidy score |
| `msi_mantis_score` | REAL | MANTIS microsatellite-instability score |

The schema permits a patient to have multiple samples because
`samples.patient_id` is not unique. In this database, however, all 566
patients have exactly one sample.

#### `mutations`

One row represents one somatic mutation call in one tumor sample. The table
contains 200,789 rows.

| Column | Type | Key or meaning |
|---|---|---|
| `mutation_id` | INTEGER | Primary key |
| `sample_id` | TEXT | Foreign key to `samples.sample_id` |
| `gene_symbol` | TEXT | Foreign key to `genes.gene_symbol` |
| `variant_classification` | TEXT | Mutation classification |
| `variant_type` | TEXT | Mutation type |
| `protein_change` | TEXT | Protein-level change |
| `chromosome` | TEXT | Chromosome |
| `start_pos` | INTEGER | Genomic start position |
| `end_pos` | INTEGER | Genomic end position |
| `t_ref_count` | INTEGER | Tumor reference-read count |
| `t_alt_count` | INTEGER | Tumor alternate-read count |

#### `genes`

One row represents one gene. The table contains 17,756 rows.

| Column | Type | Key or meaning |
|---|---|---|
| `gene_symbol` | TEXT | Primary key |
| `entrez_gene_id` | INTEGER | Entrez Gene identifier |
| `chromosome` | TEXT | Chromosome |

### Relationships

- `patients` to `samples` is structurally one-to-many through `patient_id`,
  although it is one-to-one in the observed database.
- `samples` to `mutations` is one-to-many through `sample_id`.
- `genes` to `mutations` is one-to-many through `gene_symbol`.
- Integrity checks found no samples without a matching patient and no
  mutations without a matching sample or gene.

## Missing data observed before joining

The initial checks found:

| Variable | Missing patients or samples |
|---|---:|
| Sex | 52 |
| Age at diagnosis | 71 |
| Stage | 54 |
| Tissue source site | 0 |
| Tumor mutation burden | 0 |

Missing clinical values will be retained as missing rather than imputed or
converted to zero. A gene mutation count of zero will mean that no qualifying
mutation was found for that patient and gene; it will not mean that a clinical
value was missing.

## Analysis queries and row-count validation

### Protein-altering mutation counts

`sql/gene_counts.sql` produces one row per patient and target gene for `TP53`,
`KRAS`, `EGFR`, `STK11`, and `KEAP1`. It creates all patient-gene combinations
before left joining mutations, and it places the gene and non-silent mutation
filters in the `LEFT JOIN` condition. `COUNT(m.mutation_id)` therefore returns
zero when a patient has no qualifying mutation in a target gene.

The expected row count was 2,830: 566 patients multiplied by five genes. The
actual row count was 2,830. Of those combinations, 700 had a positive count,
and they contained 746 qualifying mutation calls in total. The difference
occurs because some patients have more than one mutation call in the same
gene.

Run the query with:

```bash
sqlite3 -readonly -header -column \
  data/raw/lab4-cbioportal-luad/cohort.db < sql/gene_counts.sql
```

### Patients per tissue source site and stage

`sql/site_stage_counts.sql` groups patients by observed tissue source site and
tumor stage. It uses `COUNT(DISTINCT p.patient_id)` to count each patient once
and labels missing stages as `[Missing]` rather than dropping them.

An independent count of the observed site-stage combinations gave an expected
142 groups. The query returned 142 groups. Their patient counts sum to 566,
including all 54 patients with missing stage. The result does not contain all
34 × 10 theoretically possible combinations because only 142 combinations
occur in the database.

Run the query with:

```bash
sqlite3 -readonly -header -column \
  data/raw/lab4-cbioportal-luad/cohort.db < sql/site_stage_counts.sql
```

## Feature-table construction and validation

The build script reads the patient/sample features and the long-format gene
counts with SQL. It verifies that every patient has exactly five patient-gene
rows before using pandas to reshape those rows to wide format. The patient
table and wide gene table are merged with one-to-one validation.

| Check | Before or expected | After or actual |
|---|---:|---:|
| Patient-level base table | 566 patients | 566 rows |
| Long patient-gene table | 566 × 5 | 2,830 rows |
| Wide gene-count table | 566 patients | 566 rows |
| Final feature table | 566 patients | 566 rows and 566 unique IDs |

As a manual check, patient `TCGA-05-4382` has two qualifying EGFR mutation
rows and one qualifying TP53 mutation row in the database. The final table
records EGFR = 2, TP53 = 1, and zero for KRAS, STK11, and KEAP1.

## Missing-data handling

- Missing sex, age at diagnosis, and stage are retained as `NA` in the TSV.
  They represent clinical values that were not recorded and are not imputed.
- Tissue source site and tumor mutation burden would also remain `NA` if they
  were missing. Neither variable is missing in this database.
- A gene count of `0` means no qualifying non-silent mutation was found for
  that patient and gene. It is an observed count, not an unknown value.
- Four patients have no mutation calls at all. They remain in the final table
  with zero in all five target-gene columns.
- Row-count assertions before and after the joins confirm that no patients
  were silently dropped.

## Data dictionary

`data/processed/data_dictionary.tsv` contains one row for every column in the
final feature table. It records each column's meaning, units, source, and
missing-value coding. The gene-count definitions explicitly exclude mutation
rows whose `variant_classification` is `Silent`.
