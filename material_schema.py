# Categories and the attributes that matter for each material type.

MATERIAL_SCHEMA = {
    "BOLT": [
        "material",
        "grade",
        "diameter",
        "length",
        "thread_type",
        "standard",
        "coating",
    ],

    "NUT": [
        "material",
        "grade",
        "size",
        "thread_type",
        "standard",
        "coating",
    ],

    "BEARING": [
        "bearing_type",
        "inner_diameter",
        "outer_diameter",
        "width",
        "seal_type",
        "material",
        "standard",
    ],

    "BALL_VALVE": [
        "material",
        "grade",
        "size",
        "pressure_rating",
        "connection_type",
        "standard",
    ],

    "PIPE": [
        "material",
        "grade",
        "diameter",
        "wall_thickness",
        "length",
        "standard",
    ],
}


def get_attributes(category: str):
    category = category.upper().strip()
    return MATERIAL_SCHEMA.get(category, [])