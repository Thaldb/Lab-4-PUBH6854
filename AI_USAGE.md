# AI Usage Disclosure

## Tool used

I used OpenAI Codex, a GPT-5-based coding agent in the Codex desktop app, on
October 19-20, 2026. I used it as an interactive guide for organizing the
repository, inspecting the SQLite schema, interpreting table grain and
relationships, writing and debugging SQL and Python, and planning validation
checks.

## Work completed with AI assistance

Codex helped me:

- create a reproducible project structure;
- write schema-inspection and database-integrity SQL;
- identify primary and foreign keys from SQLite metadata;
- distinguish the relationship permitted by the schema from the relationship
  observed in this dataset; and
- write the two analysis queries;
- build and debug the pandas reshape and one-to-one merge;
- create the data dictionary; and
- document the missing-data and reproducibility strategy.

## Verification performed

I checked the SQL results rather than relying only on whether the queries ran.
The checks confirmed:

- 566 patient rows and 566 unique patient IDs;
- 566 sample rows, 566 unique sample IDs, and one observed sample for every
  patient;
- 200,789 mutation rows and 17,756 gene rows;
- no samples without a matching patient;
- no mutations without a matching sample or gene; and
- 52 missing sex values, 71 missing ages, and 54 missing stages;
- 2,830 expected and actual patient-gene rows;
- 142 expected and actual observed site-stage groups, whose patient counts sum
  to all 566 patients;
- 566 rows and 566 unique patient IDs before and after the final merge; and
- no missing values in the five final gene-count columns.

I also checked patient `TCGA-05-4382` by comparing the underlying mutation
rows with the output. The database contains two qualifying EGFR mutations and
one qualifying TP53 mutation for this patient. The final feature table records
EGFR = 2, TP53 = 1, and zero for KRAS, STK11, and KEAP1.
