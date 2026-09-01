"""Central configuration for investigator project search."""

SEARCH_ALIAS_GROUPS = {
    "street light": (
        "street light",
        "street lights",
        "street lighting",
        "solar street light",
        "high mast light",
        "highmast light",
        "street lamp",
        "streetlamp",
        "lighting installation",
        "lighting provision",
        "illumination",
    ),
    "bridge": (
        "bridge",
        "bridges",
        "foot bridge",
        "footbridge",
        "over bridge",
        "overbridge",
        "culvert",
    ),
    "road": (
        "road",
        "roads",
        "roadway",
        "road work",
        "road construction",
        "road improvement",
        "black top",
        "blacktop",
        "black topping",
        "cc road",
        "concrete road",
        "pavement",
    ),
}

SEARCH_FIELD_WEIGHTS = {
    "project_id": 5000,
    "work_ids": 900,
    "activity_name": 700,
    "work_description": 650,
    "mp_name": 550,
    "vendor_names": 500,
    "ida_name": 450,
    "constituency": 350,
    "state_name": 300,
}

EXACT_PROJECT_ID_SCORE = 1_000_000
MIN_PARTIAL_TOKEN_LENGTH = 3
