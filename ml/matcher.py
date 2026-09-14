import math
from collections import Counter
from typing import Any, Dict, List

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None
    SKLEARN_AVAILABLE = False

from .extract_attributes import extract_attributes


# =========================================================
# LIGHTWEIGHT SEMANTIC MATCHING
# =========================================================
#
# Production/demo deployment intentionally uses TF-IDF
# cosine similarity instead of Sentence Transformers.
#
# Why:
# - no PyTorch
# - no CUDA
# - no NVIDIA packages
# - fast startup on Render Free
# - deterministic
#
# The engineering-attribute layer remains the primary
# technical evidence used by the matcher.
# =========================================================


MODEL_NAME = "tfidf-lightweight"


# =========================================================
# GENERIC VALUE COMPARISON
# =========================================================

def values_are_equal(
    value_a: Any,
    value_b: Any,
    tolerance: float = 0.0,
) -> bool:

    if value_a is None or value_b is None:
        return False


    # Numeric comparison
    if (
        isinstance(value_a, (int, float))
        and isinstance(value_b, (int, float))
    ):

        return (
            abs(value_a - value_b)
            <= tolerance
        )


    # String comparison
    if (
        isinstance(value_a, str)
        and isinstance(value_b, str)
    ):

        normalized_a = (
            value_a
            .strip()
            .upper()
        )

        normalized_b = (
            value_b
            .strip()
            .upper()
        )

        return normalized_a == normalized_b


    return value_a == value_b


# =========================================================
# DISPLAY VALUE
# =========================================================

def display_value(
    value: Any,
) -> str:

    if value is None:
        return "—"


    if isinstance(value, float):

        if value.is_integer():
            return str(int(value))

        return f"{value:.2f}"


    return str(value)


# =========================================================
# CATEGORY FIELD CONFIGURATION
# =========================================================

def get_category_fields(
    category: str,
):

    categories = {

        "BOLT": [
            ("material", 0.0),
            ("diameter_mm", 0.5),
            ("length_mm", 0.5),
        ],

        "BALL_VALVE": [
            ("material", 0.0),
            ("size_mm", 1.0),
            ("pressure_rating_psi", 0.0),
            ("connection_type", 0.0),
        ],

        "BEARING": [
            ("bearing_number", 0.0),
            ("seal_type", 0.0),
            ("bearing_type", 0.0),
            ("material", 0.0),
        ],

        "PIPE": [
            ("material", 0.0),
            ("diameter_mm", 1.0),
            ("wall_thickness_mm", 0.2),
            ("pipe_type", 0.0),
        ],

    }

    return categories.get(
        category,
        [],
    )


# =========================================================
# CATEGORY RESOLUTION
# =========================================================

def resolve_category(
    attrs_a: Dict[str, Any],
    attrs_b: Dict[str, Any],
) -> str:

    category_a = attrs_a.get(
        "category",
        "UNKNOWN",
    )

    category_b = attrs_b.get(
        "category",
        "UNKNOWN",
    )


    if category_a != "UNKNOWN":
        return category_a


    if category_b != "UNKNOWN":
        return category_b


    return "UNKNOWN"


# =========================================================
# CATEGORY COMPATIBILITY
# =========================================================

def categories_are_compatible(
    attrs_a: Dict[str, Any],
    attrs_b: Dict[str, Any],
) -> bool:

    category_a = attrs_a.get(
        "category",
        "UNKNOWN",
    )

    category_b = attrs_b.get(
        "category",
        "UNKNOWN",
    )


    if (
        category_a == "UNKNOWN"
        or category_b == "UNKNOWN"
    ):
        return True


    return category_a == category_b


# =========================================================
# ATTRIBUTE EXPLANATION
# =========================================================

def build_attribute_explanation(
    attrs_a: Dict[str, Any],
    attrs_b: Dict[str, Any],
) -> List[Dict[str, Any]]:

    category_a = attrs_a.get(
        "category",
        "UNKNOWN",
    )

    category_b = attrs_b.get(
        "category",
        "UNKNOWN",
    )


    # -----------------------------------------------------
    # Category mismatch is immediately critical.
    # -----------------------------------------------------

    if (
        category_a != "UNKNOWN"
        and category_b != "UNKNOWN"
        and category_a != category_b
    ):

        return [
            {
                "name": "category",

                "value_a":
                    display_value(
                        category_a
                    ),

                "value_b":
                    display_value(
                        category_b
                    ),

                "status":
                    "CONFLICT",

                "score":
                    0.0,

                "importance":
                    "CRITICAL",

                "reason":
                    "The material categories are different.",
            }
        ]


    category = resolve_category(
        attrs_a,
        attrs_b,
    )


    fields = get_category_fields(
        category
    )


    explanation = []


    for field, tolerance in fields:

        value_a = attrs_a.get(
            field
        )

        value_b = attrs_b.get(
            field
        )


        # -------------------------------------------------
        # Attribute absent on both sides.
        # -------------------------------------------------

        if (
            value_a is None
            and value_b is None
        ):

            continue


        # -------------------------------------------------
        # Missing from A.
        # -------------------------------------------------

        if (
            value_a is None
            and value_b is not None
        ):

            explanation.append(
                {
                    "name":
                        field,

                    "value_a":
                        "—",

                    "value_b":
                        display_value(
                            value_b
                        ),

                    "status":
                        "MISSING_A",

                    "score":
                        0.0,

                    "importance":
                        "REVIEW",

                    "reason":
                        (
                            f"{field} is present in "
                            "Material B but not "
                            "Material A."
                        ),
                }
            )

            continue


        # -------------------------------------------------
        # Missing from B.
        # -------------------------------------------------

        if (
            value_a is not None
            and value_b is None
        ):

            explanation.append(
                {
                    "name":
                        field,

                    "value_a":
                        display_value(
                            value_a
                        ),

                    "value_b":
                        "—",

                    "status":
                        "MISSING_B",

                    "score":
                        0.0,

                    "importance":
                        "REVIEW",

                    "reason":
                        (
                            f"{field} is present in "
                            "Material A but not "
                            "Material B."
                        ),
                }
            )

            continue


        # -------------------------------------------------
        # Both values exist.
        # -------------------------------------------------

        matched = values_are_equal(
            value_a,
            value_b,
            tolerance,
        )


        if matched:

            explanation.append(
                {
                    "name":
                        field,

                    "value_a":
                        display_value(
                            value_a
                        ),

                    "value_b":
                        display_value(
                            value_b
                        ),

                    "status":
                        "MATCHED",

                    "score":
                        1.0,

                    "importance":
                        "NORMAL",

                    "reason":
                        (
                            f"{field} agrees within "
                            "the configured tolerance."
                        ),
                }
            )

        else:

            explanation.append(
                {
                    "name":
                        field,

                    "value_a":
                        display_value(
                            value_a
                        ),

                    "value_b":
                        display_value(
                            value_b
                        ),

                    "status":
                        "CONFLICT",

                    "score":
                        0.0,

                    "importance":
                        "CRITICAL",

                    "reason":
                        (
                            f"{field} does not agree "
                            "within the configured tolerance."
                        ),
                }
            )


    return explanation


# =========================================================
# ATTRIBUTE SIMILARITY
# =========================================================

def attribute_similarity(
    attrs_a: Dict[str, Any],
    attrs_b: Dict[str, Any],
) -> float:

    if not categories_are_compatible(
        attrs_a,
        attrs_b,
    ):

        return 0.0


    category = resolve_category(
        attrs_a,
        attrs_b,
    )


    fields = get_category_fields(
        category
    )


    if not fields:
        return 0.0


    matched = 0.0

    available = 0.0


    for field, tolerance in fields:

        value_a = attrs_a.get(
            field
        )

        value_b = attrs_b.get(
            field
        )


        if (
            value_a is None
            and value_b is None
        ):

            continue


        available += 1.0


        if values_are_equal(
            value_a,
            value_b,
            tolerance,
        ):

            matched += 1.0


    if available == 0:
        return 0.0


    return (
        matched
        /
        available
    )


# =========================================================
# LIGHTWEIGHT TEXT SEMANTIC SIMILARITY
# =========================================================

def semantic_similarity(
    text_a: str,
    text_b: str,
) -> float:
    """
    Lightweight deterministic text similarity.

    Uses word + character n-gram TF-IDF so different
    formatting such as:

        M10 X 50
        M10*50
        10 MM X 50 MM

    can still retain some lexical similarity.

    This is a deployment-friendly substitute for a large
    embedding model. Engineering attributes remain the
    more important technical evidence.
    """

    text_a = (
        text_a
        .strip()
        .upper()
    )

    text_b = (
        text_b
        .strip()
        .upper()
    )


    if not text_a or not text_b:
        return 0.0

    if SKLEARN_AVAILABLE and TfidfVectorizer is not None:
        try:
            vectorizer = TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 5),
                lowercase=False,
                sublinear_tf=True,
            )
            matrix = vectorizer.fit_transform([text_a, text_b])
            score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
            return max(0.0, min(1.0, float(score)))
        except Exception:
            pass

    # Pure Python n-gram character TF cosine fallback (deterministic, 0-dependency)
    try:
        def _get_ngrams(t):
            padded = f" {t} "
            counts = Counter()
            for n in range(2, 6):
                for i in range(len(padded) - n + 1):
                    counts[padded[i:i+n]] += 1
            return counts

        c1 = _get_ngrams(text_a)
        c2 = _get_ngrams(text_b)
        dot = sum(c1[k] * c2[k] for k in c1 if k in c2)
        norm1 = math.sqrt(sum(v * v for v in c1.values()))
        norm2 = math.sqrt(sum(v * v for v in c2.values()))
        if norm1 > 0 and norm2 > 0:
            return max(0.0, min(1.0, float(dot / (norm1 * norm2))))
        return 0.0
    except Exception:
        return 0.0


# =========================================================
# CRITICAL ENGINEERING MISMATCH
# =========================================================

def critical_mismatch(
    attrs_a: Dict[str, Any],
    attrs_b: Dict[str, Any],
) -> bool:

    category_a = attrs_a.get(
        "category",
        "UNKNOWN",
    )

    category_b = attrs_b.get(
        "category",
        "UNKNOWN",
    )


    # -----------------------------------------------------
    # Category mismatch
    # -----------------------------------------------------

    if (
        category_a != "UNKNOWN"
        and category_b != "UNKNOWN"
        and category_a != category_b
    ):

        return True


    category = resolve_category(
        attrs_a,
        attrs_b,
    )


    # -----------------------------------------------------
    # BOLT
    # -----------------------------------------------------

    if category == "BOLT":

        material_a = attrs_a.get(
            "material"
        )

        material_b = attrs_b.get(
            "material"
        )


        if (
            material_a is not None
            and material_b is not None
            and material_a != material_b
        ):

            return True


        diameter_a = attrs_a.get(
            "diameter_mm"
        )

        diameter_b = attrs_b.get(
            "diameter_mm"
        )


        if (
            diameter_a is not None
            and diameter_b is not None
            and abs(
                diameter_a
                - diameter_b
            ) > 0.5
        ):

            return True


        length_a = attrs_a.get(
            "length_mm"
        )

        length_b = attrs_b.get(
            "length_mm"
        )


        if (
            length_a is not None
            and length_b is not None
            and abs(
                length_a
                - length_b
            ) > 0.5
        ):

            return True


    # -----------------------------------------------------
    # BALL VALVE
    # -----------------------------------------------------

    elif category == "BALL_VALVE":

        material_a = attrs_a.get(
            "material"
        )

        material_b = attrs_b.get(
            "material"
        )


        if (
            material_a is not None
            and material_b is not None
            and material_a != material_b
        ):

            return True


        size_a = attrs_a.get(
            "size_mm"
        )

        size_b = attrs_b.get(
            "size_mm"
        )


        if (
            size_a is not None
            and size_b is not None
            and abs(
                size_a
                - size_b
            ) > 1.0
        ):

            return True


        pressure_a = attrs_a.get(
            "pressure_rating_psi"
        )

        pressure_b = attrs_b.get(
            "pressure_rating_psi"
        )


        if (
            pressure_a is not None
            and pressure_b is not None
            and pressure_a != pressure_b
        ):

            return True


        connection_a = attrs_a.get(
            "connection_type"
        )

        connection_b = attrs_b.get(
            "connection_type"
        )


        if (
            connection_a is not None
            and connection_b is not None
            and connection_a != connection_b
        ):

            return True


    # -----------------------------------------------------
    # BEARING
    # -----------------------------------------------------

    elif category == "BEARING":

        number_a = attrs_a.get(
            "bearing_number"
        )

        number_b = attrs_b.get(
            "bearing_number"
        )


        if (
            number_a is not None
            and number_b is not None
            and number_a != number_b
        ):

            return True


        seal_a = attrs_a.get(
            "seal_type"
        )

        seal_b = attrs_b.get(
            "seal_type"
        )


        if (
            seal_a is not None
            and seal_b is not None
            and seal_a != seal_b
        ):

            return True


        bearing_type_a = attrs_a.get(
            "bearing_type"
        )

        bearing_type_b = attrs_b.get(
            "bearing_type"
        )


        if (
            bearing_type_a is not None
            and bearing_type_b is not None
            and bearing_type_a != bearing_type_b
        ):

            return True


    # -----------------------------------------------------
    # PIPE
    # -----------------------------------------------------

    elif category == "PIPE":

        material_a = attrs_a.get(
            "material"
        )

        material_b = attrs_b.get(
            "material"
        )


        if (
            material_a is not None
            and material_b is not None
            and material_a != material_b
        ):

            return True


        diameter_a = attrs_a.get(
            "diameter_mm"
        )

        diameter_b = attrs_b.get(
            "diameter_mm"
        )


        if (
            diameter_a is not None
            and diameter_b is not None
            and abs(
                diameter_a
                - diameter_b
            ) > 1.0
        ):

            return True


        thickness_a = attrs_a.get(
            "wall_thickness_mm"
        )

        thickness_b = attrs_b.get(
            "wall_thickness_mm"
        )


        if (
            thickness_a is not None
            and thickness_b is not None
            and abs(
                thickness_a
                - thickness_b
            ) > 0.2
        ):

            return True


        pipe_a = attrs_a.get(
            "pipe_type"
        )

        pipe_b = attrs_b.get(
            "pipe_type"
        )


        if (
            pipe_a is not None
            and pipe_b is not None
            and pipe_a != pipe_b
        ):

            return True


    return False


# =========================================================
# EXPLANATION SUMMARY
# =========================================================

def build_explanation_summary(
    attribute_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:

    matched = [
        row

        for row in attribute_rows

        if row["status"] == "MATCHED"
    ]


    conflicts = [
        row

        for row in attribute_rows

        if row["status"] == "CONFLICT"
    ]


    missing_a = [
        row

        for row in attribute_rows

        if row["status"] == "MISSING_A"
    ]


    missing_b = [
        row

        for row in attribute_rows

        if row["status"] == "MISSING_B"
    ]


    total = len(
        attribute_rows
    )


    matched_count = len(
        matched
    )


    if total:

        agreement = (
            matched_count
            /
            total
        )

    else:

        agreement = 0.0


    return {

        "matched_count":
            matched_count,

        "conflict_count":
            len(conflicts),

        "missing_a_count":
            len(missing_a),

        "missing_b_count":
            len(missing_b),

        "total_attributes":
            total,

        "attribute_agreement":
            round(
                agreement,
                4,
            ),

        "matched":
            matched,

        "conflicts":
            conflicts,

        "missing_a":
            missing_a,

        "missing_b":
            missing_b,

    }


# =========================================================
# MAIN MATERIAL COMPARISON
# =========================================================

def compare_materials(
    text_a: str,
    text_b: str,
) -> Dict[str, Any]:

    text_a = (
        text_a
        .strip()
    )

    text_b = (
        text_b
        .strip()
    )


    # -----------------------------------------------------
    # Extract engineering attributes
    # -----------------------------------------------------

    attrs_a = extract_attributes(
        text_a
    )

    attrs_b = extract_attributes(
        text_b
    )


    # -----------------------------------------------------
    # Lightweight semantic score
    # -----------------------------------------------------

    semantic_score = semantic_similarity(
        text_a,
        text_b,
    )


    # -----------------------------------------------------
    # Engineering attribute score
    # -----------------------------------------------------

    attr_score = attribute_similarity(
        attrs_a,
        attrs_b,
    )


    # -----------------------------------------------------
    # Detailed evidence
    # -----------------------------------------------------

    attribute_rows = (
        build_attribute_explanation(
            attrs_a,
            attrs_b,
        )
    )


    explanation_summary = (
        build_explanation_summary(
            attribute_rows
        )
    )


    # -----------------------------------------------------
    # Weighted overall score
    #
    # Engineering evidence gets more weight than text
    # similarity.
    # -----------------------------------------------------

    final_score = (
        semantic_score * 0.40
        +
        attr_score * 0.60
    )


    # -----------------------------------------------------
    # Critical mismatch override
    # -----------------------------------------------------

    is_critical_mismatch = (
        critical_mismatch(
            attrs_a,
            attrs_b,
        )
    )


    if is_critical_mismatch:

        final_score = min(
            final_score,
            0.60,
        )


    # -----------------------------------------------------
    # Classification
    # -----------------------------------------------------

    if is_critical_mismatch:

        classification = (
            "DIFFERENT"
        )

    elif final_score >= 0.90:

        classification = (
            "IDENTICAL"
        )

    elif final_score >= 0.75:

        classification = (
            "EQUIVALENT"
        )

    elif final_score >= 0.55:

        classification = (
            "NEAR_DUPLICATE"
        )

    else:

        classification = (
            "DIFFERENT"
        )


    # -----------------------------------------------------
    # Human-readable explanation
    # -----------------------------------------------------

    explanation_text = []


    if explanation_summary[
        "matched_count"
    ]:

        explanation_text.append(
            (
                f"{explanation_summary['matched_count']} "
                "engineering attribute(s) matched."
            )
        )


    if explanation_summary[
        "conflict_count"
    ]:

        explanation_text.append(
            (
                f"{explanation_summary['conflict_count']} "
                "engineering attribute(s) conflict."
            )
        )


    if explanation_summary[
        "missing_a_count"
    ]:

        explanation_text.append(
            (
                f"{explanation_summary['missing_a_count']} "
                "attribute(s) are missing from Material A."
            )
        )


    if explanation_summary[
        "missing_b_count"
    ]:

        explanation_text.append(
            (
                f"{explanation_summary['missing_b_count']} "
                "attribute(s) are missing from Material B."
            )
        )


    if is_critical_mismatch:

        explanation_text.append(
            (
                "A critical engineering mismatch "
                "prevents high-confidence material "
                "consolidation."
            )
        )


    if not explanation_text:

        explanation_text.append(
            (
                "No structured engineering evidence "
                "was available."
            )
        )


    return {

        "text_a":
            text_a,

        "text_b":
            text_b,

        "attributes_a":
            attrs_a,

        "attributes_b":
            attrs_b,

        "semantic_score":
            round(
                semantic_score,
                4,
            ),

        "attribute_score":
            round(
                attr_score,
                4,
            ),

        "final_score":
            round(
                final_score,
                4,
            ),

        "critical_mismatch":
            is_critical_mismatch,

        "classification":
            classification,

        "attribute_explanation":
            attribute_rows,

        "explanation_summary":
            explanation_summary,

        "explanation_text":
            explanation_text,

        "semantic_engine":
            MODEL_NAME,

    }


# =========================================================
# CONSOLE TESTING
# =========================================================

def print_result(
    result: Dict[str, Any],
) -> None:

    print(
        "\n"
        + "=" * 70
    )


    print(
        "\nMATERIAL A:"
    )

    print(
        result["text_a"]
    )


    print(
        "\nATTRIBUTES A:"
    )

    print(
        result["attributes_a"]
    )


    print(
        "\nMATERIAL B:"
    )

    print(
        result["text_b"]
    )


    print(
        "\nATTRIBUTES B:"
    )

    print(
        result["attributes_b"]
    )


    print(
        "\nATTRIBUTE EXPLANATION:"
    )


    for row in result[
        "attribute_explanation"
    ]:

        print(
            f"  {row['name']}: "
            f"{row['status']} "
            f"({row['score']:.0%}) "
            f"[A={row['value_a']} | "
            f"B={row['value_b']}]"
        )


    print(
        "\nSemantic Score    : "
        f"{result['semantic_score']:.2%}"
    )


    print(
        "Attribute Score   : "
        f"{result['attribute_score']:.2%}"
    )


    print(
        "Final Score       : "
        f"{result['final_score']:.2%}"
    )


    print(
        "Critical Mismatch : "
        f"{result['critical_mismatch']}"
    )


    print(
        "Classification     : "
        f"{result['classification']}"
    )


    print(
        "Semantic Engine    : "
        f"{result['semantic_engine']}"
    )


    print(
        "\nExplanation:"
    )


    for line in result[
        "explanation_text"
    ]:

        print(
            f"  - {line}"
        )


# =========================================================
# SAMPLE TESTS
# =========================================================

if __name__ == "__main__":

    examples = [

        (
            "HEX BOLT M10 X 50 SS304",
            "HEXAGONAL BOLT M10 X 50 MM SS304",
        ),

        (
            "HEX BOLT M10 X 50 SS304",
            "HEX BOLT M10 X 50 SS316",
        ),

        (
            "SS316 FLANGED BALL VALVE 2 INCH 150 PSI",
            "2 IN FLG BALL VALVE SS316 150 PSI",
        ),

        (
            "SEAMLESS PIPE SS304 50MM X 3MM",
            "SS304 SEAMLESS PIPE OD 50 MM WT 3 MM",
        ),

        (
            "SEAMLESS PIPE SS304 50MM X 3MM",
            "SEAMLESS SS316 PIPE 50 MM X 3 MM",
        ),

    ]


    for text_a, text_b in examples:

        result = compare_materials(
            text_a,
            text_b,
        )

        print_result(
            result
        )