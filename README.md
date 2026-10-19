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
├── sql/
│   └── inspect_schema.sql
└── src/
```

The SQL analysis queries, feature-table script, processed TSV, and data
dictionary will be added in the next stages of the lab.

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

## Current status

Schema inspection is complete. The next step is to write and validate the two
required analysis queries, beginning with the 2,830 expected patient-gene
combinations (566 patients multiplied by five target genes).
