
import pandas as pd

from .matcher import compare_materials


DATA_PATH = "data/materials.csv"


def main():
    # ---------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    print(f"Loaded {len(df)} materials.\n")

    # ---------------------------------------------------------
    # Compare every unique pair
    # ---------------------------------------------------------

    results = []

    for i in range(len(df)):

        for j in range(i + 1, len(df)):

            material_a = df.iloc[i]
            material_b = df.iloc[j]

            # Don't compare a material with another record
            # from the same CPSE for our current prototype.
            if material_a["cpse"] == material_b["cpse"]:
                continue

            result = compare_materials(
                material_a["description"],
                material_b["description"],
            )

            results.append({
                "cpse_a": material_a["cpse"],
                "code_a": material_a["material_code"],
                "description_a": material_a["description"],

                "cpse_b": material_b["cpse"],
                "code_b": material_b["material_code"],
                "description_b": material_b["description"],

                "semantic_score": result["semantic_score"],
                "attribute_score": result["attribute_score"],
                "final_score": result["final_score"],
                "classification": result["classification"],
            })

    results_df = pd.DataFrame(results)

    # ---------------------------------------------------------
    # Sort best matches first
    # ---------------------------------------------------------

    results_df = results_df.sort_values(
        by="final_score",
        ascending=False,
    )

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------

    output_path = "data/match_results.csv"

    results_df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Generated {len(results_df)} pair comparisons."
    )

    print(
        f"Saved results to: {output_path}\n"
    )

    # ---------------------------------------------------------
    # Show strongest matches
    # ---------------------------------------------------------

    print("=" * 80)
    print("TOP MATERIAL MATCHES")
    print("=" * 80)

    top_matches = results_df.head(15)

    for _, row in top_matches.iterrows():

        print("\n" + "-" * 80)

        print(
            f"{row['cpse_a']} | "
            f"{row['code_a']}"
        )

        print(
            f"  {row['description_a']}"
        )

        print(
            f"\n{row['cpse_b']} | "
            f"{row['code_b']}"
        )

        print(
            f"  {row['description_b']}"
        )

        print(
            f"\nSemantic   : "
            f"{row['semantic_score']:.2%}"
        )

        print(
            f"Attributes : "
            f"{row['attribute_score']:.2%}"
        )

        print(
            f"Final      : "
            f"{row['final_score']:.2%}"
        )

        print(
            f"Decision   : "
            f"{row['classification']}"
        )


if __name__ == "__main__":
    main()
