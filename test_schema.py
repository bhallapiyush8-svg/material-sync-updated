from material_schema import get_attributes


def main():
    categories = [
        "BOLT",
        "BALL_VALVE",
        "BEARING",
        "PIPE",
    ]

    for category in categories:
        print(f"\n{category}")
        print("-" * len(category))

        for attribute in get_attributes(category):
            print(f"- {attribute}")


if __name__ == "__main__":
    main()