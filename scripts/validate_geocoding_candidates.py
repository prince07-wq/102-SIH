"""
scripts/validate_geocoding_candidates.py

Classifies frozen Location Extraction V1.1 records for a future geocoding
stage. This script validates candidates only; it does not call a geocoding API.

Inputs:
  data/processed/projects.json
  data/processed/project_locations.json

Outputs:
  data/processed/geocoding_candidates.json
  data/processed/geocoding_candidate_diagnostics.json
"""

import json
import os
import re
import sys
from collections import Counter

PROJECTS_PATH = os.path.join("data", "processed", "projects.json")
LOCATIONS_PATH = os.path.join(
    "data", "processed", "project_locations.json"
)
OUTPUT_PATH = os.path.join(
    "data", "processed", "geocoding_candidates.json"
)
DIAGNOSTICS_PATH = os.path.join(
    "data", "processed", "geocoding_candidate_diagnostics.json"
)

EXPECTED_PROJECT_COUNT = 78079
EXAMPLE_LIMIT = 20
MAX_CANDIDATE_LENGTH = 30

STATUSES = ["GEOCODE_READY", "NEEDS_REVIEW", "NOT_ELIGIBLE"]
LOCATION_FIELDS = [
    "village_or_locality",
    "ward",
    "block_or_taluk",
    "district",
]
REQUIRED_PROJECT_FIELDS = {
    "project_id",
    "work_description",
    "constituency",
    "state_name",
}
REQUIRED_LOCATION_FIELDS = {
    "project_id",
    "raw_location_text",
    "village_or_locality",
    "ward",
    "block_or_taluk",
    "district",
    "district_source",
    "constituency",
    "state",
    "location_source",
    "confidence",
}
OUTPUT_FIELDS = {
    "project_id",
    "geocoding_status",
    "confidence",
    "village_or_locality",
    "ward",
    "block_or_taluk",
    "district",
    "district_source",
    "constituency",
    "state",
    "location_source",
    "reason_codes",
    "reasons",
}

VALID_CONFIDENCE_LEVELS = {"HIGH", "MEDIUM", "LOW", "NONE"}
VALID_DISTRICT_SOURCES = {
    "WORK_DESCRIPTION",
    "IDA_NAME (administrative jurisdiction)",
    None,
}

GENERIC_DIRECTIONAL_JURISDICTIONS = {
    "central",
    "east",
    "north",
    "south",
    "west",
}
GENERIC_LOCATION_VALUES = {
    "area",
    "block",
    "city",
    "colony",
    "district",
    "location",
    "locality",
    "mandal",
    "nagar",
    "panchayat",
    "sector",
    "taluk",
    "taluka",
    "town",
    "village",
    "ward",
}

GENERIC_MODIFIER_VALUES = {
    "all",
    "carry the system",
    "chauraha",
    "chowk",
    "dhani",
    "eb",
    "end",
    "entrance",
    "every",
    "govt owned open space",
    "is",
    "jn",
    "junction",
    "land",
    "limits",
    "new",
    "no",
    "old",
    "on",
    "open space owned by",
    "or",
    "other",
    "others",
    "pas",
    "pass",
    "pond",
    "pcc",
    "remaining",
    "rto",
    "scheduled caste area",
    "way",
}
PERSON_NAME_VALUES = {
    "devi",
    "gurjar",
    "kumar",
    "singh",
    "yadav",
}

CONTAMINATION_PATTERN = re.compile(
    r"\b(?:"
    r"construct|construction|providing|installation|development|repair|"
    r"renovation|building|boundary\s+wall|compound(?:\s+wall)?|"
    r"community\s+hall|community\s+centre|"
    r"community\s+center|school|college|collage|library|hospital|"
    r"mandir|temple|mosque|masjid|church|bhavan|bhawan|anganwadi|"
    r"academy|campus|office|house|home|ghar|h\s*\.?\s*/\s*o|"
    r"bus\s*(?:stand|stop|shelter)|dharmshala|market|mokshdham|park|"
    r"samaj|sangh|sabha|station|"
    r"vidyalay|vidyalaya|vidyapith|"
    r"work|road|street|bridge|path|drain|nali|pavement|"
    r"play\s*ground|playground|ground|cremation|crematorium|cemetery|"
    r"graveyard|trader|traders|treader|treaders|hotel|scheme|site|"
    r"shed|sitting|pump|tank|room|shop|field|club|society|trust|"
    r"nirman|kary|karya|sthan|sthit|public|various|"
    r"executive\s+agency|working\s+agency"
    r")\b",
    re.IGNORECASE,
)
CONCATENATED_INSTITUTION_PATTERN = re.compile(
    r"(?:school|college|collage|hospital|library|mandir|temple)(?=[A-Za-z])",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(r"\d{7,}")
TRAILING_CONNECTOR_PATTERN = re.compile(
    r"\b(?:"
    r"and|at|from|in|ka|ke|ki|mai|me|mein|near|of|on|par|se|"
    r"tak|thi|to|under|via"
    r")$",
    re.IGNORECASE,
)
LEADING_CONNECTOR_PATTERN = re.compile(
    r"^(?:antargat|antargart|antergar|antergart|antergrat|at|in|"
    r"mai|me|mein|near|on|par|pas|pass)\b",
    re.IGNORECASE,
)
INTERNAL_CONNECTOR_PATTERN = re.compile(
    r"\b(?:antargat|antargart|antergar|antergart|antergrat|at|"
    r"mai|me|mein|near|on|par|pas|pass|tak)\b",
    re.IGNORECASE,
)
GENERIC_PROPERTY_PATTERN = re.compile(
    r"\b(?:land|open\s+space|property)\b",
    re.IGNORECASE,
)
ADMINISTRATIVE_PHRASE_PATTERN = re.compile(
    r"\b(?:"
    r"administration|authority|committee|corporation|department|"
    r"group|h\s*\.\s*o\.?|hobali|hoballi|hobli|"
    r"implementing\s+agency|municipality|"
    r"nagar\s+nigam|panchayat|panchayt|panchyat|panchyet|parishad|samiti|samity"
    r"|post|ps"
    r")\b",
    re.IGNORECASE,
)
PERSON_LEAKAGE_PATTERN = re.compile(
    r"\b(?:"
    r"add|daughter|d\s*/\s*o|mob|mobile|mr|mrs|putr|shri|smt|"
    r"son|s\s*/\s*o|wife|w\s*/\s*o"
    r")\b",
    re.IGNORECASE,
)
ROAD_OR_WORK_FRAGMENT_PATTERN = re.compile(
    r"\b(?:"
    r"approach|culvert|interlock|interlocking|kary|karya|marg|"
    r"meter|metre|mtr|nali|nirman|pahunch|paver|pewar|piece|"
    r"pitch|pich|pulia|rasta|sadak|system|till|upto"
    r")\b",
    re.IGNORECASE,
)
CONCATENATED_WORK_FRAGMENT_PATTERN = re.compile(
    r"\d+\s*(?:meter|metre|mtr|piece)\b",
    re.IGNORECASE,
)
METADATA_PATTERN = re.compile(
    r"\b(?:l\s*\.\s*no|letter|plot\s*\.?\s*no|property(?:\s+no)?|"
    r"survey\s*\.?\s*no)\b|"
    r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
    re.IGNORECASE,
)
ORDINAL_OR_ROMAN_PATTERN = re.compile(
    r"^(?:\d+(?:st|nd|rd|th)|[ivxlcdm]+|no\s*\d*)$",
    re.IGNORECASE,
)

REASON_TEXT = {
    "READY_CLEAN_HIGH_LOCALITY": (
        "HIGH-confidence description locality passed conservative checks."
    ),
    "CONFIDENCE_LOW_OR_NONE": (
        "LOW/NONE extraction confidence is not eligible for automatic geocoding."
    ),
    "CONFIDENCE_MEDIUM": (
        "MEDIUM extraction confidence requires human or stricter validation."
    ),
    "MISSING_STATE": "State context is missing.",
    "NO_DESCRIPTION_LOCATION": (
        "No location clue was extracted from the work description."
    ),
    "NO_VILLAGE_OR_LOCALITY": (
        "No village/locality is available; ward or administrative context alone "
        "requires review."
    ),
    "SUSPICIOUS_LONG_VALUE": (
        "An extracted location value is longer than 30 characters."
    ),
    "CONTAMINATED_VALUE": (
        "An extracted value contains activity, institution, or non-location text."
    ),
    "PHONE_NUMBER_IN_VALUE": (
        "An extracted value contains a phone-like numeric sequence."
    ),
    "TRAILING_CONNECTOR": (
        "An extracted value ends with a connector that suggests boundary leakage."
    ),
    "MALFORMED_CONNECTOR": (
        "An extracted value begins with a connector that suggests boundary leakage."
    ),
    "GENERIC_LOCATION_VALUE": (
        "An extracted value is only a generic location label."
    ),
    "GENERIC_MODIFIER_VALUE": (
        "An extracted value is a generic modifier or non-place phrase."
    ),
    "ADMINISTRATIVE_PHRASE": (
        "An extracted value contains an administrative or institutional phrase."
    ),
    "PERSON_NAME_LEAKAGE": (
        "An extracted value contains person or address language."
    ),
    "ROAD_OR_WORK_FRAGMENT": (
        "An extracted value contains road, work, quantity, or route language."
    ),
    "MALFORMED_HIERARCHY_VALUE": (
        "A hierarchy field is an ordinal, label, or otherwise malformed value."
    ),
    "OVERLY_COMPLEX_LOCALITY": (
        "The locality contains four or more words and requires boundary review."
    ),
    "SOURCE_CONTEXT_MISMATCH": (
        "The extracted locality cannot be matched back to the source description."
    ),
    "VILLAGE_EQUALS_BLOCK": (
        "Village/locality and block/taluk are identical and require hierarchy review."
    ),
    "VILLAGE_EQUALS_DISTRICT": (
        "Village/locality and district are identical and require hierarchy review."
    ),
    "BLOCK_EQUALS_DISTRICT": (
        "Block/taluk and district are identical and require hierarchy review."
    ),
    "VILLAGE_EQUALS_WARD": (
        "Village/locality and ward are identical and require hierarchy review."
    ),
    "IDA_JURISDICTION_CONTEXT": (
        "District is an IDA administrative jurisdiction, not a verified project site."
    ),
    "GENERIC_IDA_JURISDICTION": (
        "IDA jurisdiction is only a generic direction and requires review."
    ),
    "MISSING_DISTRICT_CONTEXT": (
        "No district or IDA jurisdiction context is available."
    ),
}


def load_json_list(filepath):
    """Loads and validates a JSON list."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON list in {filepath}, got {type(data).__name__}"
        )

    return data


def clean_source_value(value):
    """Returns a trimmed string or None for a missing source value."""
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    value = value.strip()
    return value or None


def normalize_value(value):
    """Normalizes a location value for conservative equality checks."""
    if not isinstance(value, str):
        return None
    return " ".join(value.casefold().split()) or None


def normalize_search_text(value):
    """Normalizes punctuation and whitespace for source-context checks."""
    if not isinstance(value, str):
        return ""
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def has_person_context_leakage(project, village):
    """Checks whether a locality candidate includes adjacent person context."""
    normalized_village = normalize_search_text(village)
    normalized_description = normalize_search_text(
        project.get("work_description")
    )
    village_words = normalized_village.split()
    if len(village_words) < 2 or not normalized_description:
        return False

    escaped_village = re.escape(normalized_village)
    if re.search(
        rf"\b(?:dhani|house|resident)\s+of\s+{escaped_village}\b",
        normalized_description,
    ):
        return True

    match = re.search(rf"\b{escaped_village}\b", normalized_description)
    if not match:
        return False
    following_text = normalized_description[match.end():].strip()
    return re.match(
        r"^(?:ji\s+)?(?:k|ke)\s+(?:avas|darwaja|door|ghar|makan|niwas)\b|"
        r"^(?:putr|son)\b",
        following_text,
    ) is not None


def validate_inputs(projects, locations):
    """Validates source schemas, counts, IDs, order, and copied context."""
    if len(projects) != EXPECTED_PROJECT_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_PROJECT_COUNT} projects, got {len(projects)}"
        )
    if len(locations) != EXPECTED_PROJECT_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_PROJECT_COUNT} locations, got {len(locations)}"
        )

    project_ids = []
    location_ids = []
    seen_project_ids = set()
    seen_location_ids = set()

    for position, (project, location) in enumerate(
        zip(projects, locations), start=1
    ):
        if not isinstance(project, dict) or not isinstance(location, dict):
            raise ValueError(f"Record {position} must contain JSON objects")

        missing_project_fields = REQUIRED_PROJECT_FIELDS - set(project)
        if missing_project_fields:
            raise ValueError(
                f"Project record {position} is missing field(s): "
                + ", ".join(sorted(missing_project_fields))
            )
        missing_location_fields = REQUIRED_LOCATION_FIELDS - set(location)
        if missing_location_fields:
            raise ValueError(
                f"Location record {position} is missing field(s): "
                + ", ".join(sorted(missing_location_fields))
            )

        project_id = project.get("project_id")
        location_id = location.get("project_id")
        if not isinstance(project_id, int) or isinstance(project_id, bool):
            raise ValueError(f"Malformed project_id at project record {position}")
        if not isinstance(location_id, int) or isinstance(location_id, bool):
            raise ValueError(f"Malformed project_id at location record {position}")
        if project_id in seen_project_ids:
            raise ValueError(f"Duplicate source project_id: {project_id}")
        if location_id in seen_location_ids:
            raise ValueError(f"Duplicate location project_id: {location_id}")
        if project_id != location_id:
            raise ValueError(
                f"Project/location ID mismatch at record {position}: "
                f"{project_id} != {location_id}"
            )

        if location.get("confidence") not in VALID_CONFIDENCE_LEVELS:
            raise ValueError(f"Invalid confidence for project {project_id}")
        if location.get("district_source") not in VALID_DISTRICT_SOURCES:
            raise ValueError(f"Invalid district_source for project {project_id}")
        for field in REQUIRED_LOCATION_FIELDS - {"project_id"}:
            value = location.get(field)
            if value is not None and not isinstance(value, str):
                raise ValueError(
                    f"Malformed location field {field} for project {project_id}"
                )
        if bool(location.get("district")) != bool(
            location.get("district_source")
        ):
            raise ValueError(
                f"District/source inconsistency for project {project_id}"
            )

        source_state = clean_source_value(project.get("state_name"))
        source_constituency = clean_source_value(project.get("constituency"))
        if location.get("state") != source_state:
            raise ValueError(f"State mismatch for project {project_id}")
        if location.get("constituency") != source_constituency:
            raise ValueError(f"Constituency mismatch for project {project_id}")

        seen_project_ids.add(project_id)
        seen_location_ids.add(location_id)
        project_ids.append(project_id)
        location_ids.append(location_id)

    if project_ids != location_ids:
        raise ValueError("Project and location IDs are not aligned in source order")

    return project_ids


def find_suspicious_fields(project, location):
    """Returns conservative quality signals found in extracted fields."""
    signals = {
        "long": [],
        "contaminated": [],
        "phone": [],
        "trailing_connector": [],
        "malformed_connector": [],
        "generic": [],
        "generic_modifier": [],
        "administrative": [],
        "person": [],
        "road_or_work": [],
        "malformed_hierarchy": [],
        "overly_complex": [],
        "source_context_mismatch": [],
    }

    for field in LOCATION_FIELDS:
        value = location.get(field)
        if not isinstance(value, str):
            continue
        if len(value) > MAX_CANDIDATE_LENGTH:
            signals["long"].append(field)
        if (
            CONTAMINATION_PATTERN.search(value)
            or CONCATENATED_INSTITUTION_PATTERN.search(value)
        ):
            signals["contaminated"].append(field)
        if PHONE_PATTERN.search(value):
            signals["phone"].append(field)
        if TRAILING_CONNECTOR_PATTERN.search(value.strip()):
            signals["trailing_connector"].append(field)
        if LEADING_CONNECTOR_PATTERN.search(value.strip()):
            signals["malformed_connector"].append(field)
        elif INTERNAL_CONNECTOR_PATTERN.search(value.strip()):
            signals["malformed_connector"].append(field)
        if normalize_value(value) in GENERIC_LOCATION_VALUES:
            signals["generic"].append(field)
        if (
            normalize_value(value) in GENERIC_MODIFIER_VALUES
            or GENERIC_PROPERTY_PATTERN.search(value)
        ):
            signals["generic_modifier"].append(field)
        if ADMINISTRATIVE_PHRASE_PATTERN.search(value):
            signals["administrative"].append(field)
        if field in {"village_or_locality", "block_or_taluk"}:
            if PERSON_LEAKAGE_PATTERN.search(value):
                signals["person"].append(field)
            if (
                ROAD_OR_WORK_FRAGMENT_PATTERN.search(value)
                or CONCATENATED_WORK_FRAGMENT_PATTERN.search(value)
            ):
                signals["road_or_work"].append(field)

    village = location.get("village_or_locality")
    if isinstance(village, str):
        if len(village.split()) >= 4:
            signals["overly_complex"].append("village_or_locality")
        if ORDINAL_OR_ROMAN_PATTERN.fullmatch(village.strip()):
            signals["malformed_hierarchy"].append("village_or_locality")
        if METADATA_PATTERN.search(village):
            signals["malformed_hierarchy"].append("village_or_locality")
        if has_person_context_leakage(project, village):
            signals["person"].append("village_or_locality")
        if normalize_value(village) in PERSON_NAME_VALUES:
            signals["person"].append("village_or_locality")

        normalized_village = normalize_search_text(village)
        normalized_description = normalize_search_text(
            project.get("work_description")
        )
        if (
            normalized_village
            and normalized_village not in normalized_description
        ):
            signals["source_context_mismatch"].append(
                "village_or_locality"
            )

    for field in {"ward", "block_or_taluk", "district"}:
        value = location.get(field)
        if not isinstance(value, str):
            continue
        normalized = normalize_value(value)
        if normalized in GENERIC_MODIFIER_VALUES:
            signals["malformed_hierarchy"].append(field)
        if field != "ward" and ORDINAL_OR_ROMAN_PATTERN.fullmatch(value.strip()):
            signals["malformed_hierarchy"].append(field)

    return signals


def find_hierarchy_reasons(location):
    """Returns exact cross-level equality signals needing hierarchy review."""
    village = normalize_value(location.get("village_or_locality"))
    ward = normalize_value(location.get("ward"))
    block = normalize_value(location.get("block_or_taluk"))
    district = normalize_value(location.get("district"))
    reasons = []

    if village and village == block:
        reasons.append("VILLAGE_EQUALS_BLOCK")
    if village and village == district:
        reasons.append("VILLAGE_EQUALS_DISTRICT")
    if block and block == district:
        reasons.append("BLOCK_EQUALS_DISTRICT")
    if village and village == ward:
        reasons.append("VILLAGE_EQUALS_WARD")

    return reasons


def classify_location(project, location):
    """Classifies one frozen location record with explainable reason codes."""
    confidence = location["confidence"]
    location_source = location.get("location_source") or ""
    village = location.get("village_or_locality")
    district = location.get("district")
    district_source = location.get("district_source")
    state = location.get("state")

    reason_codes = []
    review_reasons = []

    if district_source == "IDA_NAME (administrative jurisdiction)":
        reason_codes.append("IDA_JURISDICTION_CONTEXT")

    if confidence in {"LOW", "NONE"}:
        reason_codes.append("CONFIDENCE_LOW_OR_NONE")
        if not location_source.startswith("WORK_DESCRIPTION"):
            reason_codes.append("NO_DESCRIPTION_LOCATION")
        return "NOT_ELIGIBLE", reason_codes

    if not state:
        reason_codes.append("MISSING_STATE")
        return "NOT_ELIGIBLE", reason_codes

    if confidence == "MEDIUM":
        review_reasons.append("CONFIDENCE_MEDIUM")

    if not village:
        review_reasons.append("NO_VILLAGE_OR_LOCALITY")

    suspicious = find_suspicious_fields(project, location)
    suspicious_reason_map = {
        "long": "SUSPICIOUS_LONG_VALUE",
        "contaminated": "CONTAMINATED_VALUE",
        "phone": "PHONE_NUMBER_IN_VALUE",
        "trailing_connector": "TRAILING_CONNECTOR",
        "malformed_connector": "MALFORMED_CONNECTOR",
        "generic": "GENERIC_LOCATION_VALUE",
        "generic_modifier": "GENERIC_MODIFIER_VALUE",
        "administrative": "ADMINISTRATIVE_PHRASE",
        "person": "PERSON_NAME_LEAKAGE",
        "road_or_work": "ROAD_OR_WORK_FRAGMENT",
        "malformed_hierarchy": "MALFORMED_HIERARCHY_VALUE",
        "overly_complex": "OVERLY_COMPLEX_LOCALITY",
        "source_context_mismatch": "SOURCE_CONTEXT_MISMATCH",
    }
    for signal, reason_code in suspicious_reason_map.items():
        if suspicious[signal]:
            review_reasons.append(reason_code)

    review_reasons.extend(find_hierarchy_reasons(location))

    if not district:
        review_reasons.append("MISSING_DISTRICT_CONTEXT")
    elif (
        district_source == "IDA_NAME (administrative jurisdiction)"
        and normalize_value(district) in GENERIC_DIRECTIONAL_JURISDICTIONS
    ):
        review_reasons.append("GENERIC_IDA_JURISDICTION")

    reason_codes.extend(review_reasons)
    reason_codes = list(dict.fromkeys(reason_codes))

    if review_reasons:
        return "NEEDS_REVIEW", reason_codes

    reason_codes.append("READY_CLEAN_HIGH_LOCALITY")
    return "GEOCODE_READY", reason_codes


def build_candidate(project, location):
    """Builds one candidate record without changing extracted location values."""
    status, reason_codes = classify_location(project, location)
    return {
        "project_id": location["project_id"],
        "geocoding_status": status,
        "confidence": location["confidence"],
        "village_or_locality": location["village_or_locality"],
        "ward": location["ward"],
        "block_or_taluk": location["block_or_taluk"],
        "district": location["district"],
        "district_source": location["district_source"],
        "constituency": location["constituency"],
        "state": location["state"],
        "location_source": location["location_source"],
        "reason_codes": reason_codes,
        "reasons": [REASON_TEXT[code] for code in reason_codes],
    }


def select_representative_examples(records, status, limit=EXAMPLE_LIMIT):
    """Selects deterministic examples spread across one status bucket."""
    matching = [
        record for record in records
        if record["geocoding_status"] == status
    ]
    if len(matching) <= limit:
        return matching
    if limit == 1:
        return [matching[len(matching) // 2]]

    last_index = len(matching) - 1
    indexes = [round(index * last_index / (limit - 1)) for index in range(limit)]
    return [matching[index] for index in indexes]


def build_diagnostics(candidates):
    """Builds status, reason, and representative-sample diagnostics."""
    status_counts = Counter(
        candidate["geocoding_status"] for candidate in candidates
    )
    reason_counts = Counter(
        reason
        for candidate in candidates
        for reason in candidate["reason_codes"]
    )

    return {
        "total_projects": len(candidates),
        "status_counts": {
            status: status_counts.get(status, 0) for status in STATUSES
        },
        "reason_counts": {
            reason: reason_counts.get(reason, 0) for reason in REASON_TEXT
        },
        "policy": {
            "GEOCODE_READY": (
                "HIGH confidence with a clean description-derived village/locality, "
                "state, district context, and no hierarchy warning."
            ),
            "NEEDS_REVIEW": (
                "MEDIUM confidence, missing village/locality, suspicious extracted "
                "text, generic IDA jurisdiction, missing district, or hierarchy warning."
            ),
            "NOT_ELIGIBLE": (
                "LOW/NONE confidence, fallback-only location, or missing state."
            ),
        },
        "representative_samples": {
            status: select_representative_examples(candidates, status)
            for status in STATUSES
        },
    }


def validate_outputs(project_ids, candidates, diagnostics):
    """Validates output schema, order, counts, statuses, and diagnostics."""
    if len(candidates) != EXPECTED_PROJECT_COUNT:
        raise ValueError("Candidate count does not match the expected project count")

    output_ids = [candidate.get("project_id") for candidate in candidates]
    if output_ids != project_ids:
        raise ValueError("Candidate project IDs do not preserve source order")
    if len(set(output_ids)) != len(output_ids):
        raise ValueError("Duplicate project IDs found in candidate output")

    for candidate in candidates:
        if set(candidate) != OUTPUT_FIELDS:
            raise ValueError(
                f"Unexpected candidate schema for project "
                f"{candidate.get('project_id')}"
            )
        if candidate["geocoding_status"] not in STATUSES:
            raise ValueError(
                f"Invalid geocoding status for project {candidate['project_id']}"
            )
        if not candidate["reason_codes"]:
            raise ValueError(
                f"Missing classification reason for project {candidate['project_id']}"
            )
        if len(candidate["reason_codes"]) != len(candidate["reasons"]):
            raise ValueError(
                f"Reason mismatch for project {candidate['project_id']}"
            )
        if any(code not in REASON_TEXT for code in candidate["reason_codes"]):
            raise ValueError(
                f"Unknown reason code for project {candidate['project_id']}"
            )

    expected_status_counts = dict(
        Counter(candidate["geocoding_status"] for candidate in candidates)
    )
    actual_status_counts = {
        status: expected_status_counts.get(status, 0) for status in STATUSES
    }
    if diagnostics.get("status_counts") != actual_status_counts:
        raise ValueError("Diagnostic status counts do not match candidates")
    if sum(actual_status_counts.values()) != EXPECTED_PROJECT_COUNT:
        raise ValueError("Diagnostic status counts do not total 78,079")
    if diagnostics.get("total_projects") != EXPECTED_PROJECT_COUNT:
        raise ValueError("Diagnostic project total is incorrect")

    expected_reason_counter = Counter(
        reason
        for candidate in candidates
        for reason in candidate["reason_codes"]
    )
    expected_reason_counts = {
        reason: expected_reason_counter.get(reason, 0)
        for reason in REASON_TEXT
    }
    if diagnostics.get("reason_counts") != expected_reason_counts:
        raise ValueError("Diagnostic reason counts do not match candidates")

    for status in STATUSES:
        examples = diagnostics["representative_samples"].get(status, [])
        expected_examples = min(EXAMPLE_LIMIT, actual_status_counts[status])
        if len(examples) != expected_examples:
            raise ValueError(
                f"Incorrect representative sample count for {status}"
            )
        if any(example["geocoding_status"] != status for example in examples):
            raise ValueError(f"Incorrect representative sample status: {status}")


def save_json(data, filepath):
    """Saves UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(diagnostics):
    """Prints a concise validation summary."""
    counts = diagnostics["status_counts"]
    print("\n--- Geocoding Candidate Validation Summary ---")
    print(f"Projects processed: {diagnostics['total_projects']}")
    print(f"GEOCODE_READY: {counts['GEOCODE_READY']}")
    print(f"NEEDS_REVIEW: {counts['NEEDS_REVIEW']}")
    print(f"NOT_ELIGIBLE: {counts['NOT_ELIGIBLE']}")
    print(f"Output path: {OUTPUT_PATH}")
    print(f"Diagnostics path: {DIAGNOSTICS_PATH}")


def main():
    try:
        projects = load_json_list(PROJECTS_PATH)
        locations = load_json_list(LOCATIONS_PATH)
        project_ids = validate_inputs(projects, locations)
        candidates = [
            build_candidate(project, location)
            for project, location in zip(projects, locations)
        ]
        diagnostics = build_diagnostics(candidates)
        validate_outputs(project_ids, candidates, diagnostics)
        save_json(candidates, OUTPUT_PATH)
        save_json(diagnostics, DIAGNOSTICS_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to validate geocoding candidates: {e}")
        sys.exit(1)

    print("SUCCESS: Geocoding candidate validation complete.")
    print_summary(diagnostics)


if __name__ == "__main__":
    main()
