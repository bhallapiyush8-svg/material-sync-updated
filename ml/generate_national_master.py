
import pandas as pd

from .extract_attributes import extract_attributes


MATERIALS_PATH = "data/materials.csv"
GROUPS_PATH = "data/material_groups.csv"

OUTPUT_PATH = "data/national_master.csv"


def format_number(value):
    """
    Convert a numeric value into a clean string.
    """

    if value is None:
        return "NA"

    value = float(value)

    if value.is_integer():
        return str(int(value))

    return str(value).replace(".", "")


def clean_code_value(value):
    """
    Make a value safe for use inside a material code.
    """

    value = str(value).upper().strip()

    replacements = {
        " ": "",
        "-": "",
        "/": "",
        ".": "",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value


def generate_national_code(attributes):
    """
    Generate one deterministic prototype Common National
    Material Code from normalized material attributes.
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
            material != "NA"
            and diameter is not None
            and length is not None
        ):

            return (
                "N-MAT-BLT-"
                f"{clean_code_value(material)}-"
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
            material != "NA"
            and size is not None
            and pressure is not None
        ):

            return (
                "N-MAT-BV-"
                f"{clean_code_value(material)}-"
                f"S{format_number(size)}-"
                f"P{format_number(pressure)}-"
                f"{clean_code_value(connection)}"
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
                f"{clean_code_value(bearing_number)}-"
                f"{clean_code_value(seal_type)}"
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
            material != "NA"
            and diameter is not None
            and thickness is not None
        ):

            return (
                "N-MAT-PIP-"
                f"{clean_code_value(material)}-"
                f"D{format_number(diameter)}-"
                f"T{format_number(thickness)}-"
                f"{clean_code_value(pipe_type)}"
            )

    return "N-MAT-UNRESOLVED"


def standardized_description(attributes):
    """
    Build a canonical human-readable description.
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
            "HEXAGONAL BOLT"
        ]

        if material:
            parts.append(
                str(material)
            )

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
            parts.append(
                str(material)
            )

        if size is not None:
            parts.append(
                f"{format_number(size)}MM"
            )

        if connection:
            parts.append(
                str(connection)
            )

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


def get_group_attributes(
    group_codes,
    materials,
):
    """
    Extract attributes from all records in a candidate group.

    For the current prototype, use the first record as the
    canonical source after validation.

    A production system would perform consensus checking
    across all group members before creating the master.
    """

    group_codes = set(
        str(code)
        for code in group_codes
    )

    subset = materials[
        materials["material_code"]
        .astype(str)
        .isin(group_codes)
    ]

    if subset.empty:
        return {}, subset

    # Extract from every member.
    extracted = []

    for _, row in subset.iterrows():

        attrs = extract_attributes(
            row["description"]
        )

        extracted.append(
            attrs
        )

    # Start with the first record.
    canonical = dict(
        extracted[0]
    )

    # ---------------------------------------------------------
    # Consensus for common attributes
    # ---------------------------------------------------------

    fields = set()

    for attrs in extracted:
        fields.update(
            attrs.keys()
        )

    for field in fields:

        values = []

        for attrs in extracted:

            if field in attrs:
                values.append(
                    attrs[field]
                )

        if not values:
            continue

        # Keep the value only if all known values agree.
        if all(
            value == values[0]
            for value in values
        ):
            canonical[field] = values[0]

    return canonical, subset


def main():

    materials = pd.read_csv(
        MATERIALS_PATH
    )

    groups = pd.read_csv(
        GROUPS_PATH
    )

    print(
        f"Materials loaded: {len(materials)}"
    )

    print(
        f"Candidate groups loaded: {len(groups)}"
    )

    output_rows = []

    # ---------------------------------------------------------
    # Process each candidate group
    # ---------------------------------------------------------

    for _, group in groups.iterrows():

        mappings = str(
            group["cpse_mappings"]
        )

        if not mappings.strip():
            continue

        # Extract legacy material codes.
        member_codes = []

        for mapping in mappings.split("|"):

            mapping = mapping.strip()

            if ":" not in mapping:
                continue

            _, code = mapping.split(
                ":",
                1,
            )

            member_codes.append(
                code.strip()
            )

        if len(member_codes) < 2:
            continue

        attributes, member_rows = (
            get_group_attributes(
                member_codes,
                materials,
            )
        )

        if not attributes:
            continue

        national_code = generate_national_code(
            attributes
        )

        standardized = standardized_description(
            attributes
        )

        output_rows.append({
            "national_material_code":
                national_code,

            "standardized_description":
                standardized,

            "category":
                attributes.get("category"),

            "material":
                attributes.get("material"),

            "diameter_mm":
                attributes.get("diameter_mm"),

            "length_mm":
                attributes.get("length_mm"),

            "size_mm":
                attributes.get("size_mm"),

            "pressure_rating_psi":
                attributes.get(
                    "pressure_rating_psi"
                ),

            "connection_type":
                attributes.get(
                    "connection_type"
                ),

            "bearing_number":
                attributes.get(
                    "bearing_number"
                ),

            "seal_type":
                attributes.get(
                    "seal_type"
                ),

            "wall_thickness_mm":
                attributes.get(
                    "wall_thickness_mm"
                ),

            "pipe_type":
                attributes.get(
                    "pipe_type"
                ),

            "cpse_mappings":
                mappings,

            "source_group":
                group["group_id"],

            "member_count":
                len(member_codes),

            "status":
                "PENDING_APPROVAL",
        })

    result = pd.DataFrame(
        output_rows
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nGenerated {len(result)} "
        f"candidate national materials."
    )

    print(
        f"Saved to: {OUTPUT_PATH}"
    )

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    print("\n" + "=" * 100)
    print("COMMON NATIONAL MATERIAL MASTER")
    print("=" * 100)

    for _, row in result.iterrows():

        print("\n" + "-" * 100)

        print(
            f"National Code: "
            f"{row['national_material_code']}"
        )

        print(
            f"Description: "
            f"{row['standardized_description']}"
        )

        print(
            f"Category: "
            f"{row['category']}"
        )

        print(
            f"Mapped CPSEs: "
            f"{row['cpse_mappings']}"
        )

        print(
            f"Status: "
            f"{row['status']}"
        )


if __name__ == "__main__":
    main()
