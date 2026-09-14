
import re
from typing import Dict

from .unit_normalizer import parse_length


def detect_category(text: str) -> str:
    text = text.upper()

    if "BALL VALVE" in text:
        return "BALL_VALVE"

    if "BOLT" in text:
        return "BOLT"

    if "BEARING" in text:
        return "BEARING"

    if "PIPE" in text:
        return "PIPE"

    return "UNKNOWN"


def extract_material(text: str) -> str | None:
    text = text.upper()

    match = re.search(
        r"\bSS\s*(304|316)\b",
        text,
    )

    if match:
        return f"SS{match.group(1)}"

    match = re.search(
        r"\bSTAINLESS\s+STEEL\s*(304|316)\b",
        text,
    )

    if match:
        return f"SS{match.group(1)}"

    return None


def extract_bolt_attributes(
    text: str,
) -> Dict[str, object]:

    text = text.upper()

    attributes: Dict[str, object] = {}

    # M10 X 50
    # M10X50
    # M10*50
    metric_pattern = re.search(
        r"\bM\s*(\d+(?:\.\d+)?)\s*"
        r"(?:X|\*)\s*"
        r"(\d+(?:\.\d+)?)\s*(?:MM)?\b",
        text,
    )

    if metric_pattern:
        attributes["diameter_mm"] = float(
            metric_pattern.group(1)
        )

        attributes["length_mm"] = float(
            metric_pattern.group(2)
        )

        return attributes

    # 10MM X 50MM
    mm_pattern = re.search(
        r"\b(\d+(?:\.\d+)?)\s*MM\s*X\s*"
        r"(\d+(?:\.\d+)?)\s*MM\b",
        text,
    )

    if mm_pattern:
        attributes["diameter_mm"] = float(
            mm_pattern.group(1)
        )

        attributes["length_mm"] = float(
            mm_pattern.group(2)
        )

        return attributes

    # M12 60MM
    diameter_length_pattern = re.search(
        r"\bM\s*(\d+(?:\.\d+)?)\s+"
        r"(\d+(?:\.\d+)?)\s*MM\b",
        text,
    )

    if diameter_length_pattern:
        attributes["diameter_mm"] = float(
            diameter_length_pattern.group(1)
        )

        attributes["length_mm"] = float(
            diameter_length_pattern.group(2)
        )

        return attributes

    # Fallback: M10 ... X 50
    diameter = re.search(
        r"\bM\s*(\d+(?:\.\d+)?)\b",
        text,
    )

    if diameter:
        attributes["diameter_mm"] = float(
            diameter.group(1)
        )

    length = re.search(
        r"(?:X|\*)\s*"
        r"(\d+(?:\.\d+)?)\s*(?:MM)?\b",
        text,
    )

    if length:
        attributes["length_mm"] = float(
            length.group(1)
        )

    # Fallback: 10MM before X or *
    if "diameter_mm" not in attributes:

        diameter_mm = re.search(
            r"\b(\d+(?:\.\d+)?)\s*MM\s*(?:X|\*)\b",
            text,
        )

        if diameter_mm:
            attributes["diameter_mm"] = float(
                diameter_mm.group(1)
            )

    return attributes


def extract_valve_attributes(
    text: str,
) -> Dict[str, object]:

    text = text.upper()

    attributes: Dict[str, object] = {}

    # ---------------------------------------------------------
    # Size
    # ---------------------------------------------------------

    size = re.search(
        r"(\d+(?:\.\d+)?)\s*(INCH|IN|MM)\b|"
        r'(\d+(?:\.\d+)?)\s*"',
        text,
    )

    if size:

        if size.group(1) is not None:
            number = size.group(1)
            unit = size.group(2)

            parsed = parse_length(
                f"{number} {unit}"
            )

        else:
            number = size.group(3)

            parsed = parse_length(
                f'{number}"'
            )

        if parsed is not None:
            attributes["size_mm"] = parsed

    # ---------------------------------------------------------
    # Pressure
    # ---------------------------------------------------------

    pressure = re.search(
        r"\b(\d+(?:\.\d+)?)\s*PSI\b",
        text,
    )

    if pressure:
        attributes["pressure_rating_psi"] = float(
            pressure.group(1)
        )

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    if (
        "FLANGED" in text
        or "FLANGE" in text
        or "FLG" in text
    ):
        attributes["connection_type"] = "FLANGED"

    return attributes


def extract_bearing_attributes(
    text: str,
) -> Dict[str, object]:

    text = text.upper()

    attributes: Dict[str, object] = {}

    # Bearing number
    bearing_number = re.search(
        r"\b(\d{4,5})\b",
        text,
    )

    if bearing_number:
        attributes["bearing_number"] = (
            bearing_number.group(1)
        )

    # Seal notation
    if re.search(r"\b2Z\b", text):
        attributes["seal_type"] = "2Z"

    elif re.search(r"\bZZ\b", text):
        attributes["seal_type"] = "ZZ"

    # Bearing type
    if "DEEP GROOVE" in text:
        attributes["bearing_type"] = "DEEP_GROOVE"

    return attributes


def extract_pipe_attributes(
    text: str,
) -> Dict[str, object]:

    text = text.upper()

    attributes: Dict[str, object] = {}

    # ---------------------------------------------------------
    # Pipe type
    # ---------------------------------------------------------

    if "SEAMLESS" in text:
        attributes["pipe_type"] = "SEAMLESS"

    # ---------------------------------------------------------
    # Explicit OD
    # Example:
    # OD 50 MM
    # ---------------------------------------------------------

    od = re.search(
        r"\bOD\s*(\d+(?:\.\d+)?)\s*MM\b",
        text,
    )

    if od:
        attributes["diameter_mm"] = float(
            od.group(1)
        )

    # ---------------------------------------------------------
    # Explicit wall thickness
    # Example:
    # WT 3 MM
    # THICK 3 MM
    # THICKNESS 3 MM
    # ---------------------------------------------------------

    wt = re.search(
        r"\b(?:WT|THICK|THICKNESS)\s*"
        r"(\d+(?:\.\d+)?)\s*MM\b",
        text,
    )

    if wt:
        attributes["wall_thickness_mm"] = float(
            wt.group(1)
        )

    # ---------------------------------------------------------
    # Standard:
    # 50MM X 3MM
    # ---------------------------------------------------------

    generic = re.search(
        r"\b(\d+(?:\.\d+)?)\s*MM\s*X\s*"
        r"(\d+(?:\.\d+)?)\s*MM\b",
        text,
    )

    if generic:

        if "diameter_mm" not in attributes:
            attributes["diameter_mm"] = float(
                generic.group(1)
            )

        if "wall_thickness_mm" not in attributes:
            attributes["wall_thickness_mm"] = float(
                generic.group(2)
            )

    # ---------------------------------------------------------
    # Pattern:
    # 50MM 3MM THICK
    #
    # We interpret the first dimension as diameter
    # and the second as wall thickness.
    # ---------------------------------------------------------

    if (
        "diameter_mm" not in attributes
        or "wall_thickness_mm" not in attributes
    ):

        thick_pattern = re.search(
            r"\b(\d+(?:\.\d+)?)\s*MM\s+"
            r"(\d+(?:\.\d+)?)\s*MM\s+"
            r"(?:THICK|THICKNESS)\b",
            text,
        )

        if thick_pattern:

            if "diameter_mm" not in attributes:
                attributes["diameter_mm"] = float(
                    thick_pattern.group(1)
                )

            if "wall_thickness_mm" not in attributes:
                attributes["wall_thickness_mm"] = float(
                    thick_pattern.group(2)
                )

    return attributes


def extract_attributes(
    text: str,
) -> Dict[str, object]:

    category = detect_category(text)

    attributes: Dict[str, object] = {
        "category": category,
    }

    material = extract_material(text)

    if material:
        attributes["material"] = material

    if category == "BOLT":
        attributes.update(
            extract_bolt_attributes(text)
        )

    elif category == "BALL_VALVE":
        attributes.update(
            extract_valve_attributes(text)
        )

    elif category == "BEARING":
        attributes.update(
            extract_bearing_attributes(text)
        )

    elif category == "PIPE":
        attributes.update(
            extract_pipe_attributes(text)
        )

    return attributes


if __name__ == "__main__":

    examples = [

        # Bolts
        "HEX BOLT M10 X 50 SS304",
        "SS 304 HEXAGONAL BOLT 10MM X 50MM",
        "SS316 HEX BOLT M12X60",
        "HEX BOLT M10*50 STAINLESS STEEL 304",
        "HEXAGON BOLT M12 60MM SS316",

        # Valves
        "SS316 FLANGED BALL VALVE 2 INCH 150 PSI",
        "2 IN FLG BALL VALVE SS316 150 PSI",
        "BALL VALVE 50MM FLANGED SS316 150 PSI",

        # Bearings
        "BEARING 6205 ZZ",
        "6205-ZZ DEEP GROOVE BALL BEARING",
        "BEARING 6205 2Z",

        # Pipes
        "SEAMLESS PIPE SS304 50MM X 3MM",
        "SS 304 SEAMLESS PIPE OD 50 MM WT 3 MM",
        "STAINLESS STEEL 304 PIPE 50MM 3MM THICK",
        "SEAMLESS SS316 PIPE 50 MM X 3 MM",
    ]

    for example in examples:

        print("\n" + "=" * 60)

        print("Original:")
        print(example)

        print("\nExtracted:")

        attributes = extract_attributes(
            example
        )

        for key, value in attributes.items():
            print(f"  {key}: {value}")
