
import pandas as pd
import re

from extract_attributes import extract_attributes


MATERIALS_PATH = "data/materials.csv"
OUTPUT_PATH = "data/national_material_master.csv"


def clean_value(value):
    """
    Convert a value into a safe code component.
    """

    value = str(value).upper().strip()

    value = re.sub(
        r"[^A-Z0-9]+",
        "",
        value,
    )

    return value


def format_number(value):
    """
    Convert numeric values into compact code-friendly text.

    Example:
        10.0 -> 10
        50.0 -> 50
        50.8 -> 508
    """

    value = float(value)

    if value.is_integer():
        return str(int(value))

    return str(value).replace(".", "")


def generate_code(attributes):
    """
    Generate a deterministic prototype Common National
    Material Code from normalized attributes.
    """

    category = attributes.get(
        "category",
        "UNKNOWN",
    )

    material = attributes.get(
        "material",
        "NA",
    )

    # ---------------------------------------------------------
    # BOLT
    # ---------------------------------------------------------

    if category == "BOLT":

        diameter = attributes.get(
            "diameter_mm"
        )

        length = attributes.get(
            "length_mm"
        )

        if (
            material is not None
            and diameter is not None
            and length is not None
        ):
            return (
                "N-MAT-BLT-"
                f"{clean_value(material)}-"
                f"M{format_number(diameter)}-"
                f"L{format_number(length).zfill(3)}"
            )

    # ---------------------------------------------------------
    # BALL VALVE
    # ---------------------------------------------------------

    elif category == "BALL_VALVE":

        size = attributes.get(
            "size_mm"
        )

        pressure = attributes.get(
            "pressure_rating_psi"
        )

        connection = attributes.get(
            "connection_type",
            "NA",
        )

        if (
            material is not None
            and size is not None
            and pressure is not None
        ):

            return (
                "N-MAT-BV-"
                f"{clean_value(material)}-"
                f"S{format_number(size)}-"
                f"P{format_number(pressure)}-"
                f"{clean_value(connection)}"
            )

    # ---------------------------------------------------------
    # BEARING
    # ---------------------------------------------------------

    elif category == "BEARING":

        bearing_number = attributes.get(
            "bearing_number"
        )

        seal_type = attributes.get(
            "seal_type",
            "NA",
        )

        if bearing_number:

            return (
                "N-MAT-BRG-"
                f"{clean_value(bearing_number)}-"
                f"{clean_value(seal_type)}"
            )

    # ---------------------------------------------------------
    # PIPE
    # ---------------------------------------------------------

    elif category == "PIPE":

        diameter = attributes.get(
            "diameter_mm"
        )

        thickness = attributes.get(
            "wall_thickness_mm"
        )

        pipe_type = attributes.get(
            "pipe_type",
            "NA",
        )

        if (
            material is not None
            and diameter is not None
            and thickness is not None
        ):

            return (
                "N-MAT-PIP-"
                f"{clean_value(material)}-"
                f"D{format_number(diameter)}-"
                f"T{format_number(thickness)}-"
                f"{clean_value(pipe_type)}"
            )

    # ---------------------------------------------------------
    # Fallback
    # ---------------------------------------------------------

    return "N-MAT-UNRESOLVED"


def standardized_description(attributes):
    """
    Generate a readable standardized material description.
    """

    category = attributes.get(
        "category",
        "UNKNOWN",
    )

    material = attributes.get(
        "material"
    )

    # ---------------------------------------------------------
    # BOLT
    # ---------------------------------------------------------

    if category == "BOLT":

        diameter = attributes.get(
            "diameter_mm"
        )

        length = attributes.get(
            "length_mm"
        )

        parts = [
            "HEXAGONAL BOLT",
        ]

        if material:
            parts.append(str(material))

        if diameter is not None:
            parts.append(
                f"M{format_number(diameter)}"
            )

        if length is not None:
            parts.append(
                f"X{format_number(length)}MM"
            )

        return " ".join(parts)

    # ---------------------------------------------------------
    # BALL VALVE
    # ---------------------------------------------------------

    if category == "BALL_VALVE":

        size = attributes.get(
            "size_mm"
        )

        pressure = attributes.get(
            "pressure_rating_psi"
        )

        connection = attributes.get(
            "connection_type"
        )

        parts = [
            "BALL VALVE"
        ]

        if material:
            parts.append(str(material))

        if size is not None:
            parts.append(
                f"{format_number(size)}MM"
            )

        if connection:
            parts.append(str(connection))

        if pressure is not None:
            parts.append(
                f"{format_number(pressure)}PSI"
            )

        return " ".join(parts)

    # ---------------------------------------------------------
    # BEARING
    # ---------------------------------------------------------

    if category == "BEARING":

        bearing_number = attributes.get(
            "bearing_number"
        )

        seal_type = attributes.get(
            "seal_type"
        )

        parts = [
            "BEARING"
        ]

        if bearing_number:
            parts.append(
                str(bearing_number)
            )

        if seal_type:
            parts.append(
                str(seal_type)
            )

        return " ".join(parts)

    # ---------------------------------------------------------
    # PIPE
    # ---------------------------------------------------------

    if category == "PIPE":

        diameter = attributes.get(
            "diameter_mm"
        )

        thickness = attributes.get(
            "wall_thickness_mm"
        )

        pipe_type = attributes.get(
            "pipe_type"
        )

        parts = []

        if material:
            parts.append(
                str(material)
            )

        if pipe_type:
            parts.append(
                str(pipe_type)
            )

        parts.append("PIPE")

        if diameter is not None:
            parts.append(
                f"OD{format_number(diameter)}MM"
            )

        if thickness is not None:
            parts.append(
                f"WT{format_number(thickness)}MM"
            )

        return " ".join(parts)

    return "UNRESOLVED MATERIAL"


def main():

    df = pd.read_csv(
        MATERIALS_PATH
    )

    print(
        f"Loaded {len(df)} material records."
    )

    rows = []

    # ---------------------------------------------------------
    # Process every CPSE material
    # ---------------------------------------------------------

    for _, row in df.iterrows():

        description = str(
            row["description"]
        )

        attributes = extract_attributes(
            description
        )

        national_code = generate_code(
            attributes
        )

        standardized = standardized_description(
            attributes
        )

        rows.append({
            "national_material_code": national_code,

            "standardized_description": standardized,

            "category": attributes.get(
                "category"
            ),

            "material": attributes.get(
                "material"
            ),

            "diameter_mm": attributes.get(
                "diameter_mm"
            ),

            "length_mm": attributes.get(
                "length_mm"
            ),

            "size_mm": attributes.get(
                "size_mm"
            ),

            "pressure_rating_psi": attributes.get(
                "pressure_rating_psi"
            ),

            "connection_type": attributes.get(
                "connection_type"
            ),

            "bearing_number": attributes.get(
                "bearing_number"
            ),

            "seal_type": attributes.get(
                "seal_type"
            ),

            "wall_thickness_mm": attributes.get(
                "wall_thickness_mm"
            ),

            "pipe_type": attributes.get(
                "pipe_type"
            ),

            "cpse": row["cpse"],

            "cpse_material_code": row[
                "material_code"
            ],

            "original_description": description,
        })

    result = pd.DataFrame(rows)

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"Saved national master mapping to: "
        f"{OUTPUT_PATH}"
    )

    # ---------------------------------------------------------
    # Display examples
    # ---------------------------------------------------------

    print("\n" + "=" * 100)
    print("NATIONAL MATERIAL MASTER PREVIEW")
    print("=" * 100)

    for _, row in result.head(20).iterrows():

        print("\n" + "-" * 100)

        print(
            f"CPSE: {row['cpse']}"
        )

        print(
            f"Legacy Code: "
            f"{row['cpse_material_code']}"
        )

        print(
            f"Original: "
            f"{row['original_description']}"
        )

        print(
            f"National Code: "
            f"{row['national_material_code']}"
        )

        print(
            f"Standardized: "
            f"{row['standardized_description']}"
        )


if __name__ == "__main__":
    main()

