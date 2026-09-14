import pandas as pd

DATA_PATH = "data/materials.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    print("Total records:", len(df))

    print("\nCPSE counts:")
    print(df["cpse"].value_counts())

    print("\nFirst 10 records:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()