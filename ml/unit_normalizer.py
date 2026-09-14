import re
from typing import Optional


INCH_TO_MM = 25.4
CM_TO_MM = 10.0
M_TO_MM = 1000.0


def normalize_length(value: float, unit: str) -> float:
    """
    Convert a length value to millimetres.
    """

    unit = unit.upper().strip()

    if unit in {"MM", "MILLIMETER", "MILLIMETRE"}:
        return value

    if unit in {"CM", "CENTIMETER", "CENTIMETRE"}:
        return value * CM_TO_MM

    if unit in {"M", "METER", "METRE"}:
        return value * M_TO_MM

    if unit in {"IN", "INCH", "INCHES"}:
        return value * INCH_TO_MM

    return value


def parse_length(text: str) -> Optional[float]:
    """
    Extract a length from text and return it in millimetres.

    Examples:
        50 MM   -> 50.0
        5 CM    -> 50.0
        2 IN    -> 50.8
        2 INCH  -> 50.8
        2"      -> 50.8
    """

    text = text.upper().strip()

    # Handle the double-quote inch symbol.
    inch_symbol = re.search(
        r'(\d+(?:\.\d+)?)\s*"',
        text,
    )

    if inch_symbol:
        value = float(inch_symbol.group(1))
        return round(value * INCH_TO_MM, 3)

    # Handle explicit units.
    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*"
        r"(MM|CM|M|INCH|IN|INCHES)\b",
        text,
    )

    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2)

    return round(
        normalize_length(value, unit),
        3,
    )


def are_lengths_equivalent(
    value_a: Optional[float],
    value_b: Optional[float],
    tolerance_mm: float = 1.0,
) -> bool:
    """
    Determine whether two normalized lengths are close enough
    to be considered equivalent.

    Default tolerance = 1 mm.
    """

    if value_a is None or value_b is None:
        return False

    return abs(value_a - value_b) <= tolerance_mm


if __name__ == "__main__":

    examples = [
        "2 INCH",
        "2 IN",
        '2"',
        "50 MM",
        "5 CM",
        "0.05 M",
    ]

    print("UNIT NORMALIZATION TEST")
    print("=" * 50)

    for example in examples:
        result = parse_length(example)

        print(
            f"{example:10} -> "
            f"{result} MM"
        )

    print("\nEQUIVALENCE TEST")
    print("=" * 50)

    a = parse_length("2 INCH")
    b = parse_length("50 MM")

    print(
        f"2 INCH = {a} MM"
    )

    print(
        f"50 MM  = {b} MM"
    )

    print(
        "Equivalent:",
        are_lengths_equivalent(a, b),
    )