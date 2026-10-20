from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "lab4-cbioportal-luad"
    / "cohort.db"
)

GENE_QUERY_PATH = PROJECT_ROOT / "sql" / "gene_counts.sql"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "patient_features.tsv"


def main():
    base_query = """
    SELECT
        p.patient_id,
        p.sex,
        p.age_at_diagnosis,
        p.stage,
        s.tissue_source_site,
        s.tmb_nonsynonymous
    FROM patients AS p
    LEFT JOIN samples AS s
        ON s.patient_id = p.patient_id
    """

    gene_query = GENE_QUERY_PATH.read_text()

    with sqlite3.connect(DATABASE_PATH) as connection:
        base = pd.read_sql_query(base_query, connection)
        gene_long = pd.read_sql_query(gene_query, connection)

    print(f"Patient rows: {len(base)}")
    print(f"Unique patients: {base['patient_id'].nunique()}")

    assert len(base) == 566, "Expected exactly 566 patient rows"
    assert base["patient_id"].nunique() == 566
    assert not base["patient_id"].duplicated().any()

    print("\nFirst five patient rows:")
    print(base.head())

    expected_gene_rows = 566 * 5

    print(f"\nPatient-gene rows: {len(gene_long)}")
    print(
        "Unique patients in gene counts: "
        f"{gene_long['patient_id'].nunique()}"
    )

    assert len(gene_long) == expected_gene_rows
    assert gene_long["patient_id"].nunique() == 566

    rows_per_patient = gene_long.groupby("patient_id").size()
    assert rows_per_patient.eq(5).all()

    assert not gene_long.duplicated(
        subset=["patient_id", "gene_symbol"]
    ).any()

    gene_wide = (
        gene_long
        .pivot(
            index="patient_id",
            columns="gene_symbol",
            values="protein_altering_count",
        )
        .rename(
            columns=lambda gene: (
                f"{gene.lower()}_protein_altering_count"
            )
        )
        .reset_index()
    )

    gene_wide.columns.name = None

    gene_columns = [
        "tp53_protein_altering_count",
        "kras_protein_altering_count",
        "egfr_protein_altering_count",
        "stk11_protein_altering_count",
        "keap1_protein_altering_count",
    ]

    assert len(gene_wide) == 566
    assert gene_wide["patient_id"].nunique() == 566
    assert not gene_wide[gene_columns].isna().any().any()

    print(f"Wide gene rows: {len(gene_wide)}")
    print("\nFirst five wide gene-count rows:")
    print(gene_wide.head())

    features = base.merge(
        gene_wide,
        on="patient_id",
        how="left",
        validate="one_to_one",
    )

    features = features[
        [
            "patient_id",
            "sex",
            "age_at_diagnosis",
            "stage",
            "tissue_source_site",
            "tmb_nonsynonymous",
            *gene_columns,
        ]
    ]

    assert len(features) == 566
    assert features["patient_id"].nunique() == 566
    assert not features["patient_id"].duplicated().any()
    assert not features[gene_columns].isna().any().any()

    missing_counts = features[
        [
            "sex",
            "age_at_diagnosis",
            "stage",
            "tissue_source_site",
            "tmb_nonsynonymous",
        ]
    ].isna().sum()

    print(f"\nFinal rows after merge: {len(features)}")
    print("\nMissing values retained:")
    print(missing_counts)

    hand_check = features.loc[
        features["patient_id"] == "TCGA-05-4382",
        ["patient_id", *gene_columns],
    ]
    print("\nHand-check patient TCGA-05-4382:")
    print(hand_check.to_string(index=False))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(
        OUTPUT_PATH,
        sep="\t",
        index=False,
        na_rep="NA",
    )
    print(f"\nWrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
