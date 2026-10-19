# AI Usage Disclosure

## Tool used

I used OpenAI Codex in the Codex desktop app on October 19, 2026. I used it as
an interactive guide for organizing the repository, inspecting the SQLite
schema, interpreting table grain and relationships, and planning validation
checks.

## Work completed with AI assistance

Codex helped me:

- create a reproducible project structure;
- write schema-inspection and database-integrity SQL;
- identify primary and foreign keys from SQLite metadata;
- distinguish the relationship permitted by the schema from the relationship
  observed in this dataset; and
- document the missing-data strategy before constructing the feature table.

## Verification performed so far

I checked the SQL results rather than relying only on whether the queries ran.
The checks confirmed:

- 566 patient rows and 566 unique patient IDs;
- 566 sample rows, 566 unique sample IDs, and one observed sample for every
  patient;
- 200,789 mutation rows and 17,756 gene rows;
- no samples without a matching patient;
- no mutations without a matching sample or gene; and
- 52 missing sex values, 71 missing ages, and 54 missing stages.

This file will be updated as AI assistance and verification continue. The
final version will document validation of the analysis queries, including row
counts and a patient checked by hand.
