"""
scripts/build_locations.py

Extracts structured location clues from the processed MPLADS project dataset.
This is a text-only offline extraction stage; it does not geocode locations.

Input:
  data/processed/projects.json

Outputs:
  data/processed/project_locations.json
  data/processed/location_diagnostics.json
"""

import json
import os
import re
import sys
from collections import Counter

PROJECTS_PATH = os.path.join("data", "processed", "projects.json")
OUTPUT_PATH = os.path.join("data", "processed", "project_locations.json")
DIAGNOSTICS_PATH = os.path.join(
    "data", "processed", "location_diagnostics.json"
)

REQUIRED_FIELDS = [
    "project_id",
    "work_description",
    "ida_name",
    "constituency",
    "state_name",
]

OUTPUT_FIELDS = {
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

TEXT_FIELDS = [
    "work_description",
    "ida_name",
    "constituency",
    "state_name",
]

CONFIDENCE_LEVELS = ["HIGH", "MEDIUM", "LOW", "NONE"]
EXPECTED_PROJECT_COUNT = 78079
DISTRICT_SOURCES = {
    "WORK_DESCRIPTION",
    "IDA_NAME (administrative jurisdiction)",
    None,
}
EXAMPLE_LIMIT = 20
MAX_LOCATION_WORDS = 5
MAX_LOCATION_LENGTH = 80

VILLAGE_OR_GP_PATTERN = re.compile(
    r"(?<!\w)(?:"
    r"gram\s+sabha|"
    r"grama?\s+panchayat(?:h)?|"
    r"g\s*\.?\s*p\s*\.?|"
    r"panchayat(?:h)?|pyt\.?|"
    r"village|vilage|vill\.?|gaon|gram"
    r")(?!\w)",
    re.IGNORECASE,
)

WARD_PATTERN = re.compile(r"\bward\b", re.IGNORECASE)

BLOCK_OR_TALUK_PATTERN = re.compile(
    r"(?<!\w)(?:"
    r"vikas\s*khand|vikash\s*khand|prakhand|"
    r"block|blok|taluk|taluka|tq|tehsil|tahsil|mandal|ta|tal"
    r")(?!\w)\.?",
    re.IGNORECASE,
)

DISTRICT_PATTERN = re.compile(
    r"\b(?:district|distt|dist|dis)\b\.?",
    re.IGNORECASE,
)

AT_LOCATION_PATTERN = re.compile(
    r"(?<!\w)(?:At|AT|at)\.|(?<!\w)(?:At|AT)(?!\w)"
)

LOCALITY_PATTERN = re.compile(
    r"\b(?:colony|locality|mohalla|nagar|sector|area)\b",
    re.IGNORECASE,
)

ALL_LOCATION_MARKERS_PATTERN = re.compile(
    r"(?<!\w)(?:"
    r"gram\s+sabha|"
    r"grama?\s+panchayat(?:h)?|"
    r"g\s*\.?\s*p\s*\.?|"
    r"panchayat(?:h)?|pyt\.?|"
    r"village|vilage|vill\.?|gaon|gram|"
    r"ward|vikas\s*khand|vikash\s*khand|prakhand|"
    r"block|blok|taluk|taluka|tq|tehsil|tahsil|mandal|ta|tal|"
    r"district|distt|dist|dis|colony|locality|location|mohalla|nagar|sector|area"
    r")(?!\w)",
    re.IGNORECASE,
)

CONTEXT_BOUNDARY_PATTERN = re.compile(
    r"\b(?:"
    r"municipality|municipal|corporation|division|constituency|assembly|"
    r"vidhan\s*sabha|vidhansabha|union"
    r")\b",
    re.IGNORECASE,
)

AFTER_STOP_PATTERN = re.compile(
    r"\b(?:"
    r"at|in|of|under|near|from|to|for|with|within|via|by|"
    r"where|which|whose|work|construction|providing|repair|renovation|development|"
    r"executing|executive|agency|pry|survey|sy|house|home|road|"
    r"school|schools|college|collage|library|hospital|mandir|temple|office|"
    r"mahavidyalaya|vidyalaya|vidyapith|madrasa|madrasha|masjid|"
    r"building|installation|solar|nirman|kary|karya|kam|"
    r"light|lights|phone|mobile|contact|distance|length|metres|meters|"
    r"antargat|antargart|antrgat|hastak|hetu|yethe|yethil|between|"
    r"me|mein|men|mai|ma|par|ka|ki|ke|k|te|thi|sudhi|yanchya|"
    r"pase|paas|pass|sthit|sthith|situated|located|"
    r"and|aur|avam|evam|toward|towards|toword|towords"
    r")\b",
    re.IGNORECASE,
)

BEFORE_CUE_PATTERN = re.compile(
    r"\b(?:"
    r"at|in|of|under|near|from|to|for|within|via|"
    r"me|mein|men|mai|ma|par|ka|ki|ke|k|te|thi|sudhi|yanchya|"
    r"pase|paas|pass|"
    r"antargat|antargart|antrgat|yethe|yethil|between|"
    r"library|school|schools|college|hospital|mandir|temple|"
    r"sthit|sthith|situated|located|and|aur|avam|evam|"
    r"protect|toward|towards|toword|towords"
    r")\b",
    re.IGNORECASE,
)

WARD_ID_PATTERN = re.compile(
    r"^\s*[-:#]?\s*("
    r"(?:(?:no|number)\.?\s*[-:#]?\s*)?"
    r"(?:[A-Za-z]?\d+[A-Za-z]?|[IVXLCDM]+)(?![A-Za-z])"
    r"(?:\s*(?:to|through|and|&|-)\s*"
    r"(?:[A-Za-z]?\d+[A-Za-z]?|[IVXLCDM]+)(?![A-Za-z]))?"
    r")",
    re.IGNORECASE,
)

GENERIC_NAME_WORDS = {
    "agency",
    "area",
    "block",
    "building",
    "branch",
    "cc",
    "college",
    "community",
    "common",
    "construction",
    "central",
    "development",
    "different",
    "dumping",
    "district",
    "executing",
    "executive",
    "elementary",
    "elementry",
    "floor",
    "faliya",
    "gam",
    "gaam",
    "house",
    "hospital",
    "government",
    "govt",
    "location",
    "local",
    "letter",
    "main",
    "magistrate",
    "marag",
    "marg",
    "member",
    "mp",
    "my",
    "near",
    "number",
    "office",
    "open",
    "panchayat",
    "paver",
    "place",
    "primary",
    "pratham",
    "public",
    "remaining",
    "repair",
    "road",
    "school",
    "schools",
    "scheme",
    "sc",
    "sitting",
    "station",
    "taluk",
    "temple",
    "chatt",
    "town",
    "covered",
    "fund",
    "irrigation",
    "library",
    "department",
    "parliament",
    "pustkalaya",
    "various",
    "village",
    "ward",
    "work",
    "as",
    "ka",
    "ke",
    "ki",
    "per",
    "antargat",
    "antargart",
    "antrgat",
    "a",
    "an",
    "and",
    "the",
}

BLOCK_MATERIAL_WORDS = {
    "aerated",
    "brick",
    "cement",
    "concrete",
    "hollow",
    "interlock",
    "interlocking",
    "paver",
    "pavers",
    "pavar",
    "pevar",
    "pever",
    "pevers",
    "pewer",
    "pewers",
    "pewor",
    "paving",
    "solid",
    "stone",
    "oewar",
    "toilet",
    "toilets",
}

BLOCK_OPERATION_WORDS = {
    "kam",
    "nakhvani",
    "nu",
    "paving",
    "tiles",
    "work",
    "works",
}

DISTRICT_AUTHORITY_WORDS = {
    "administration",
    "authority",
    "bar",
    "chairman",
    "branch",
    "central",
    "collector",
    "coordinator",
    "court",
    "general",
    "government",
    "govt",
    "headquarter",
    "headquarters",
    "hospital",
    "magistrate",
    "office",
    "panchayat",
    "president",
    "secretary",
    "library",
}

MANDAL_ORGANIZATION_WORDS = {
    "education",
    "festival",
    "ganeshotsav",
    "kelavani",
    "managed",
    "operated",
    "prasarak",
    "samaj",
    "samiti",
    "sanchalit",
    "seva",
    "utsav",
    "vidya",
}

MANDAL_NON_ADMIN_FOLLOW_WORDS = {
    "bhavan",
    "bhawan",
    "booth",
    "college",
    "highschool",
    "mahavidyalaya",
    "more",
    "para",
    "school",
    "society",
    "tola",
    "trust",
    "welfare",
}

HEALTH_WARD_WORDS = {
    "emergency",
    "hospital",
    "icu",
    "maternity",
    "medical",
    "patient",
}

WARD_ROLE_WORDS = {"councillor", "member", "panch", "parshad"}

PLACEHOLDER_VALUES = {"", "-", "0", "n/a", "na", "nil", "none", "null"}

LOCATION_LEAKAGE_PATTERN = re.compile(
    r"\b(?:"
    r"construction|providing|installation|development|repair|renovation|"
    r"building|community|hall|school|schools|college|collage|library|"
    r"hospital|mandir|temple|mahavidyalaya|vidyalaya|vidyapith|"
    r"house|work|road|bhavan|bhawan|academy|campus|centre|center|"
    r"office|karya|nirman|light|lights|run"
    r")\b",
    re.IGNORECASE,
)

CONCATENATED_INSTITUTION_PATTERN = re.compile(
    r"(?:school|college|collage|hospital|library|mandir|temple)(?=[A-Za-z])",
    re.IGNORECASE,
)

AT_NON_LOCALITY_PATTERN = re.compile(
    r"\b(?:"
    r"construction|providing|installation|development|repair|renovation|work|"
    r"building|community|hall|road|light|lights|"
    r"govt|government|primary|elementary|elementry|boys|girls|junior|senior|"
    r"school|college|collage|mahavidyalaya|vidyalaya|vidyapith|hospital|"
    r"house|home|bridge|play\s*ground|playground|cremation|crematory|"
    r"crematorium|mahasamsan|smashan|"
    r"ghat|shop|office|anganwadi|madrasa|madrasha|masjid|dharamshala|"
    r"kabristan|kabarstan|kabrasthan|trust|tent|field|junction|camp|"
    r"gra+m\s*panchayat|gra+mpanchayat"
    r")\b|\bh\s*\.?\s*o\b|\bexecutive\s*agency\b|\bexecutiveagency\b",
    re.IGNORECASE,
)

PERSON_CONTEXT_PATTERN = re.compile(
    r"\b(?:house|residence|son|daughter|wife)\s+of\b|"
    r"\b(?:s/o|d/o|w/o|shri|smt|mr|mrs|mob|mobile)\b",
    re.IGNORECASE,
)


def load_json_list(filepath):
    """Loads a JSON file and validates that its top-level structure is a list."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Required file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON list in {filepath}, got {type(data).__name__}"
        )

    return data


def is_missing(value):
    """Treats None, blank strings, and common placeholders as missing."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().casefold() in PLACEHOLDER_VALUES
    return False


def clean_source_value(value):
    """Returns a trimmed source string without changing its spelling or case."""
    if is_missing(value):
        return None
    return str(value).strip()


def normalize_extracted_whitespace(value):
    """Collapses whitespace in an extracted name while preserving source spelling."""
    return " ".join(value.split())


def validate_projects(projects):
    """Validates the real processed-project schema and project ID uniqueness."""
    if len(projects) != EXPECTED_PROJECT_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_PROJECT_COUNT} source projects, got {len(projects)}"
        )

    project_ids = []
    seen_ids = set()

    for position, project in enumerate(projects, start=1):
        if not isinstance(project, dict):
            raise ValueError(
                f"Project record {position} must be an object, "
                f"got {type(project).__name__}"
            )

        missing_fields = [field for field in REQUIRED_FIELDS if field not in project]
        if missing_fields:
            raise ValueError(
                f"Project record {position} is missing field(s): "
                f"{', '.join(missing_fields)}"
            )

        project_id = project.get("project_id")
        if not isinstance(project_id, int) or isinstance(project_id, bool):
            raise ValueError(
                f"Project record {position} has a missing or malformed project_id"
            )
        if project_id in seen_ids:
            raise ValueError(f"Duplicate project_id found: {project_id}")

        for field in TEXT_FIELDS:
            value = project.get(field)
            if value is not None and not isinstance(value, str):
                raise ValueError(
                    f"Project {project_id} has a malformed text field: {field}"
                )

        seen_ids.add(project_id)
        project_ids.append(project_id)

    return project_ids


def previous_word(text, position):
    """Returns the word immediately before a marker position."""
    match = re.search(r"([A-Za-z]+)\W*$", text[:position])
    return match.group(1).casefold() if match else None


def next_word(text, position):
    """Returns the word immediately after a marker position."""
    match = re.search(r"^\W*([A-Za-z]+)", text[position:])
    return match.group(1).casefold() if match else None


def marker_is_ambiguous(text, match, marker_kind):
    """Rejects common non-geographic uses of block and ward markers."""
    marker_text = match.group(0).casefold().rstrip(".")

    if marker_kind == "village" and "panchayat" in marker_text:
        word_before = previous_word(text, match.start())
        word_after = next_word(text, match.end())
        if word_before == "district" or word_after == "hastak":
            return True

    if marker_kind == "admin" and marker_text in {"block", "blok"}:
        word_before = previous_word(text, match.start())
        word_after = next_word(text, match.end())
        if word_before in BLOCK_MATERIAL_WORDS:
            return True
        if word_before and len(word_before) == 1:
            return True
        if word_after in BLOCK_OPERATION_WORDS:
            return True
        if re.match(r"^\s*['â€™]s\b", text[match.end():], re.IGNORECASE):
            return True

    if marker_kind == "admin" and marker_text == "mandal":
        word_before = previous_word(text, match.start())
        word_after = next_word(text, match.end())
        nearby_before = text[max(0, match.start() - 40):match.start()].casefold()
        nearby_after = text[match.end():match.end() + 70]
        if (
            word_before == "mahila"
            or word_before in MANDAL_ORGANIZATION_WORDS
            or word_after in MANDAL_NON_ADMIN_FOLLOW_WORDS
            or word_after in {
                "adhyaksh",
                "chairman",
                "member",
                "president",
                "secretary",
            }
        ):
            return True
        if re.search(
            r"\b(?:house|residence)\s+of\b|\bh\s*[-/]\s*o\b|"
            r"\b(?:shri|smt|mr|mrs|sh)\.?\s+[A-Za-z]+\s*$",
            nearby_before,
            re.IGNORECASE,
        ):
            return True
        if re.match(r"^\s*(?:ke\s+ghar|['â€™]s\b)", text[match.end():], re.IGNORECASE):
            return True
        if (
            word_after == "in"
            and VILLAGE_OR_GP_PATTERN.search(nearby_after) is not None
        ):
            return True

    if marker_kind == "admin" and marker_text == "taluka":
        if next_word(text, match.end()) in {"library", "office", "pustkalaya"}:
            return True

    if marker_kind == "ward":
        nearby_text = text[max(0, match.start() - 35):match.end() + 35].casefold()
        has_ward_number = WARD_ID_PATTERN.match(text[match.end():]) is not None
        if not has_ward_number and any(
            word in nearby_text for word in HEALTH_WARD_WORDS
        ):
            return True
        if not has_ward_number and next_word(text, match.end()) in WARD_ROLE_WORDS:
            return True

    return False


def trim_candidate_words(candidate, direction):
    """Limits noisy free-text captures to a short location phrase."""
    words = candidate.split()
    if len(words) <= MAX_LOCATION_WORDS:
        return candidate
    if direction == "before":
        return " ".join(words[-MAX_LOCATION_WORDS:])
    return " ".join(words[:MAX_LOCATION_WORDS])


def clean_candidate(candidate, direction, allow_numeric=False):
    """Cleans and validates a candidate without normalizing the place name."""
    candidate = normalize_extracted_whitespace(candidate)
    candidate = candidate.strip(" \t\r\n,;:.|/_-–—[]{}")
    candidate = re.sub(
        r"^(?:the|a|an)\s+",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(
        r"^(?:palika|parishad|panchayat|nigam)\s+",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(
        r"^(?:(?:govt|government)\.?\s*)?"
        r"(?:(?:high|primary|middle)\.?\s*)?school\.?\s+",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = re.sub(
        r"^(?:(?:cc|pcc|rcc)\s+)?road\s+",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = trim_candidate_words(candidate, direction)
    candidate = candidate.strip(" \t\r\n,;:.|/_-–—[]{}")

    if not candidate or len(candidate) > MAX_LOCATION_LENGTH:
        return None
    if candidate.casefold() in PLACEHOLDER_VALUES:
        return None
    if not allow_numeric and not any(character.isalpha() for character in candidate):
        return None

    words = re.findall(r"[A-Za-z]+", candidate.casefold())
    if words and all(
        len(word) == 1 or word in GENERIC_NAME_WORDS for word in words
    ):
        return None
    if LOCATION_LEAKAGE_PATTERN.search(candidate):
        return None
    if len(words) >= 3 and CONCATENATED_INSTITUTION_PATTERN.search(candidate):
        return None
    if re.search(r"\b(?:19|20)\d{2}(?:\s*[-/]\s*\d{2,4})?\b", candidate):
        return None
    if re.search(
        r"\b(?:working|executing)\s+agency\b|\bwill\s+be\b",
        candidate,
        re.IGNORECASE,
    ):
        return None

    return candidate


def extract_after_candidate(text, match, allow_numeric=False):
    """Extracts a location candidate appearing after a marker."""
    remaining = text[match.end():]
    if re.match(r"^\s*[,;.!?\)\]]", remaining):
        return None

    remaining = re.sub(r"^\s*[-:–—]\s*", "", remaining, count=1)
    remaining = re.sub(
        r"^\s*(?:of|at|in)\s+",
        "",
        remaining,
        count=1,
        flags=re.IGNORECASE,
    )
    delimiter_match = re.search(
        r"[,;\n!?()\[\]]|(?<=[A-Za-z]{3})\.\s+",
        remaining,
    )
    if delimiter_match:
        remaining = remaining[:delimiter_match.start()]

    marker_stop = ALL_LOCATION_MARKERS_PATTERN.search(remaining)
    context_stop = CONTEXT_BOUNDARY_PATTERN.search(remaining)
    word_stop = AFTER_STOP_PATTERN.search(remaining)
    stop_positions = [
        match.start()
        for match in [marker_stop, context_stop, word_stop]
        if match is not None
    ]
    if stop_positions:
        remaining = remaining[:min(stop_positions)]

    return clean_candidate(remaining, "after", allow_numeric=allow_numeric)


def extract_before_candidate(text, match, allow_numeric=False):
    """Extracts a location candidate appearing before a marker."""
    preceding = text[:match.start()].rstrip()
    delimiter_matches = list(
        re.finditer(
            r"[,;\n!?()\[\]]|(?<=[A-Za-z]{3})\.\s+",
            preceding,
        )
    )
    if delimiter_matches:
        preceding = preceding[delimiter_matches[-1].end():]

    marker_matches = list(ALL_LOCATION_MARKERS_PATTERN.finditer(preceding))
    context_matches = list(CONTEXT_BOUNDARY_PATTERN.finditer(preceding))
    cue_matches = list(BEFORE_CUE_PATTERN.finditer(preceding))
    boundary_positions = [
        item.end() for item in marker_matches + context_matches + cue_matches
    ]
    if boundary_positions:
        preceding = preceding[max(boundary_positions):]

    return clean_candidate(preceding, "before", allow_numeric=allow_numeric)


def has_prefix_cue(text, marker_start):
    """Returns whether marker context indicates a prefix-style label."""
    preceding = text[:marker_start]
    if not preceding.strip():
        return True
    if re.search(r"[,;.!?]\s*$", preceding):
        return True
    return re.search(
        r"\b(?:at|in|of|under|near|from|within|the)\s*$",
        preceding,
        re.IGNORECASE,
    ) is not None


def has_separator_after(text, marker_end):
    """Returns whether a marker is followed by a label separator."""
    return re.match(r"^\s*[-:–—]", text[marker_end:]) is not None


def has_prior_location_marker_in_clause(text, marker_start):
    """Returns whether another location marker occurs in the same clause."""
    preceding = text[:marker_start]
    delimiter_matches = list(re.finditer(r"[,;\n!?()]", preceding))
    clause_start = delimiter_matches[-1].end() if delimiter_matches else 0
    clause = preceding[clause_start:]
    marker_matches = list(ALL_LOCATION_MARKERS_PATTERN.finditer(clause))
    if not marker_matches:
        return False
    text_after_prior_marker = clause[marker_matches[-1].end():]
    return BEFORE_CUE_PATTERN.search(text_after_prior_marker) is None


def extract_immediate_word_before(text, marker_start):
    """Extracts one preserved word immediately before a suffix marker."""
    match = re.search(r"([A-Za-z][A-Za-z'-]*)\W*$", text[:marker_start])
    if not match:
        return None
    return clean_candidate(match.group(1), "before")


def extract_ward_id(text, match):
    """Extracts a numeric or alphanumeric ward identifier after Ward."""
    ward_match = WARD_ID_PATTERN.match(text[match.end():])
    if not ward_match:
        return None
    return clean_candidate(ward_match.group(1), "after", allow_numeric=True)


def extract_labeled_name(text, marker_pattern, marker_kind):
    """Extracts the first usable name associated with a location marker."""
    for match in marker_pattern.finditer(text):
        if marker_is_ambiguous(text, match, marker_kind):
            continue

        if marker_kind == "ward":
            ward_id = extract_ward_id(text, match)
            if ward_id:
                return ward_id

        after_candidate = extract_after_candidate(text, match)
        before_candidate = extract_before_candidate(text, match)
        nearby_before = text[max(0, match.start() - 90):match.start()]
        if (
            before_candidate
            and after_candidate
            and PERSON_CONTEXT_PATTERN.search(nearby_before)
        ):
            before_candidate = None
        prefix_style = has_separator_after(text, match.end()) or has_prefix_cue(
            text, match.start()
        )
        explicit_prefix_style = prefix_style

        marker_text = match.group(0).casefold().rstrip(".")
        compact_marker = re.sub(r"[\s.]", "", marker_text)
        village_followed_by_admin = bool(
            marker_kind == "village"
            and re.match(
                r"^\s*(?:of|in|under)\b",
                text[match.end():],
                re.IGNORECASE,
            )
            and BLOCK_OR_TALUK_PATTERN.search(
                text[match.end():match.end() + 90]
            )
        )
        admin_after_contaminated = False
        if marker_kind == "admin" and after_candidate:
            following_clause = re.split(
                r"[,;\n!?()]|(?<=[A-Za-z]{3})\.\s+",
                text[match.end():],
                maxsplit=1,
            )[0]
            if (
                len(after_candidate.split()) > 1
                and LOCATION_LEAKAGE_PATTERN.search(following_clause)
            ):
                after_candidate = None
                admin_after_contaminated = True
        if marker_kind == "village" and (
            compact_marker in {"gp", "pyt", "panchayat", "panchayath"}
            or marker_text.startswith("gram")
        ):
            prefix_style = True
            if re.match(
                r"^\s*(?:at|in|of|under|near)\b",
                text[match.end():],
                re.IGNORECASE,
            ):
                prefix_style = False
        if marker_kind == "admin" and (
            marker_text in {"block", "blok"}
            or marker_text == "taluka"
            or compact_marker in {"ta", "tal"}
            or marker_text.startswith("vikas")
            or marker_text.startswith("vikash")
            or marker_text == "prakhand"
        ):
            prefix_style = True
        if marker_kind == "district":
            prefix_style = True

        candidates = (
            [after_candidate, before_candidate]
            if prefix_style
            else [before_candidate, after_candidate]
        )
        if village_followed_by_admin:
            candidates = [before_candidate]
        elif (
            marker_kind == "admin"
            and compact_marker in {"taluk", "taluka", "tq", "tal"}
            and next_word(text, match.end()) == "di"
        ):
            candidates = [extract_immediate_word_before(text, match.start())]
        elif marker_kind == "admin" and compact_marker in {"ta", "tal"}:
            candidates = [after_candidate]
        elif marker_kind == "district" and (
            next_word(text, match.end()) in DISTRICT_AUTHORITY_WORDS
        ):
            candidates = [before_candidate]
        elif marker_kind == "admin" and (
            explicit_prefix_style
            or (
                admin_after_contaminated
                and has_prior_location_marker_in_clause(text, match.start())
            )
        ):
            candidates = [after_candidate]

        for candidate in candidates:
            if candidate:
                if marker_kind == "locality":
                    source_marker = normalize_extracted_whitespace(match.group(0))
                    if candidate.casefold().endswith(source_marker.casefold()):
                        return candidate
                    if candidate == before_candidate:
                        return f"{candidate} {source_marker}"
                    return candidate
                return candidate

    return None


def extract_marker_sequence_locations(text):
    """Extracts suffix-style admin-to-village or admin-to-district chains."""
    markers = []
    markers.extend(
        (match.start(), "admin", match)
        for match in BLOCK_OR_TALUK_PATTERN.finditer(text)
    )
    markers.extend(
        (match.start(), "village", match)
        for match in VILLAGE_OR_GP_PATTERN.finditer(text)
    )
    markers.extend(
        (match.start(), "district", match)
        for match in DISTRICT_PATTERN.finditer(text)
    )
    markers.sort(key=lambda item: item[0])

    extracted = {
        "village_or_locality": None,
        "block_or_taluk": None,
        "district": None,
    }

    for index in range(len(markers) - 1):
        _, left_kind, left_match = markers[index]
        _, right_kind, right_match = markers[index + 1]

        if left_kind != "admin" or right_kind not in {"village", "district"}:
            continue
        if marker_is_ambiguous(text, left_match, "admin"):
            continue
        if marker_is_ambiguous(text, right_match, right_kind):
            continue

        between_text = text[left_match.end():right_match.start()]
        if not between_text.strip() or re.search(r"[,;\n!?()]", between_text):
            continue
        if re.match(
            r"^\s*(?:at|in|of|under|near|from|to|ka|ki|ke)\b",
            between_text,
            re.IGNORECASE,
        ):
            continue
        right_candidate = clean_candidate(between_text, "after")
        if not right_candidate:
            continue

        right_after_candidate = extract_after_candidate(text, right_match)
        if right_after_candidate:
            if extracted["block_or_taluk"] is None:
                extracted["block_or_taluk"] = right_candidate
            if (
                right_kind == "village"
                and extracted["village_or_locality"] is None
            ):
                extracted["village_or_locality"] = right_after_candidate
            if right_kind == "district" and extracted["district"] is None:
                extracted["district"] = right_after_candidate
            continue

        left_candidate = extract_before_candidate(text, left_match)
        if not left_candidate:
            continue

        if extracted["block_or_taluk"] is None:
            extracted["block_or_taluk"] = left_candidate
        if right_kind == "village" and extracted["village_or_locality"] is None:
            extracted["village_or_locality"] = right_candidate
        if right_kind == "district" and extracted["district"] is None:
            extracted["district"] = right_candidate

    return extracted


def extract_at_locality(text):
    """Extracts a conservative locality from the At./At administrative shorthand."""
    for match in AT_LOCATION_PATTERN.finditer(text):
        following_text = text[match.end():]
        clause_stops = [
            item.start()
            for item in [
                re.search(
                    r"[,;\n!?()]|(?<=[A-Za-z]{3})\.\s+",
                    following_text,
                ),
                AT_LOCATION_PATTERN.search(following_text),
            ]
            if item is not None
        ]
        immediate_clause = (
            following_text[:min(clause_stops)]
            if clause_stops
            else following_text
        )
        if AT_NON_LOCALITY_PATTERN.search(immediate_clause):
            continue

        candidate = extract_after_candidate(text, match)
        if not candidate or len(candidate.split()) > 4:
            continue
        if any(character.isdigit() for character in candidate):
            continue

        has_boundary = bool(
            re.search(r"[,;\n]", following_text)
            or ALL_LOCATION_MARKERS_PATTERN.search(following_text)
            or CONTEXT_BOUNDARY_PATTERN.search(following_text)
        )
        candidate_reaches_end = following_text.rstrip().endswith(candidate)
        if has_boundary or candidate_reaches_end:
            return candidate

    return None


def extract_district_from_ida(ida_name):
    """Extracts the district-like jurisdiction before the IDA authority details."""
    if not ida_name or "(" not in ida_name:
        return None

    candidate = ida_name.split("(", 1)[0]
    return clean_candidate(candidate, "after")


def extract_description_locations(description):
    """Extracts labeled location fields from a work description."""
    if not description:
        return {
            "village_or_locality": None,
            "ward": None,
            "block_or_taluk": None,
            "district": None,
        }

    sequence_locations = extract_marker_sequence_locations(description)

    village_or_locality = sequence_locations["village_or_locality"]
    if not village_or_locality:
        village_or_locality = extract_labeled_name(
            description, VILLAGE_OR_GP_PATTERN, "village"
        )
    if not village_or_locality:
        village_or_locality = extract_labeled_name(
            description, LOCALITY_PATTERN, "locality"
        )
    if not village_or_locality:
        village_or_locality = extract_at_locality(description)

    block_or_taluk = sequence_locations["block_or_taluk"]
    if not block_or_taluk:
        block_or_taluk = extract_labeled_name(
            description, BLOCK_OR_TALUK_PATTERN, "admin"
        )

    district = sequence_locations["district"]
    if not district:
        district = extract_labeled_name(
            description, DISTRICT_PATTERN, "district"
        )

    return {
        "village_or_locality": village_or_locality,
        "ward": extract_labeled_name(description, WARD_PATTERN, "ward"),
        "block_or_taluk": block_or_taluk,
        "district": district,
    }


def build_location_source(description_locations, district_source, constituency, state):
    """Describes the strongest source that supplied a usable location clue."""
    description_labels = []
    if description_locations["village_or_locality"]:
        description_labels.append("village/locality")
    if description_locations["ward"]:
        description_labels.append("ward")
    if description_locations["block_or_taluk"]:
        description_labels.append("block/taluk")
    if description_locations["district"]:
        description_labels.append("district")

    if description_labels:
        return f"WORK_DESCRIPTION ({', '.join(description_labels)})"
    if district_source == "IDA_NAME":
        return "IDA_NAME (administrative jurisdiction)"
    if constituency:
        return "CONSTITUENCY"
    if state:
        return "STATE_NAME"
    return "NONE"


def classify_confidence(description_locations, district, constituency, state):
    """Assigns confidence from explicit detail and available admin context."""
    has_clear_locality = bool(
        description_locations["village_or_locality"]
        or description_locations["ward"]
    )
    has_admin_context = bool(
        description_locations["block_or_taluk"]
        or district
        or constituency
        or state
    )
    has_description_location = any(description_locations.values())

    if has_clear_locality and has_admin_context:
        return "HIGH"
    if has_description_location:
        return "MEDIUM"
    if district or constituency:
        return "LOW"
    return "NONE"


def build_location_record(project):
    """Builds one structured location record from one processed project."""
    description = clean_source_value(project.get("work_description"))
    ida_name = clean_source_value(project.get("ida_name"))
    constituency = clean_source_value(project.get("constituency"))
    state = clean_source_value(project.get("state_name"))

    description_locations = extract_description_locations(description)
    district = description_locations["district"]
    district_source = "WORK_DESCRIPTION" if district else None

    if not district:
        district = extract_district_from_ida(ida_name)
        if district:
            district_source = "IDA_NAME"

    confidence = classify_confidence(
        description_locations, district, constituency, state
    )
    location_source = build_location_source(
        description_locations, district_source, constituency, state
    )

    if any(description_locations.values()):
        raw_location_text = description
    elif district_source == "IDA_NAME":
        raw_location_text = ida_name
    elif constituency:
        raw_location_text = constituency
    elif state:
        raw_location_text = state
    else:
        raw_location_text = None

    return {
        "project_id": project["project_id"],
        "raw_location_text": raw_location_text,
        "village_or_locality": description_locations["village_or_locality"],
        "ward": description_locations["ward"],
        "block_or_taluk": description_locations["block_or_taluk"],
        "district": district,
        "district_source": (
            "IDA_NAME (administrative jurisdiction)"
            if district_source == "IDA_NAME"
            else district_source
        ),
        "constituency": constituency,
        "state": state,
        "location_source": location_source,
        "confidence": confidence,
    }


def select_representative_examples(records, levels, limit=EXAMPLE_LIMIT):
    """Selects deterministic examples spread across matching input records."""
    candidates = [record for record in records if record["confidence"] in levels]
    if len(candidates) <= limit:
        return candidates
    if limit == 1:
        return [candidates[len(candidates) // 2]]

    last_index = len(candidates) - 1
    indexes = [round(index * last_index / (limit - 1)) for index in range(limit)]
    return [candidates[index] for index in indexes]


def build_diagnostics(location_records):
    """Builds aggregate coverage counts and representative examples."""
    confidence_counts = Counter(
        record["confidence"] for record in location_records
    )

    return {
        "total_projects": len(location_records),
        "confidence_counts": {
            level: confidence_counts.get(level, 0)
            for level in CONFIDENCE_LEVELS
        },
        "projects_with_village_or_locality": sum(
            record["village_or_locality"] is not None
            for record in location_records
        ),
        "projects_with_ward": sum(
            record["ward"] is not None for record in location_records
        ),
        "projects_with_block_or_taluk": sum(
            record["block_or_taluk"] is not None
            for record in location_records
        ),
        "projects_with_district": sum(
            record["district"] is not None for record in location_records
        ),
        "district_source_counts": dict(
            Counter(
                record["district_source"] or "NONE"
                for record in location_records
            )
        ),
        "high_examples": select_representative_examples(
            location_records, {"HIGH"}
        ),
        "medium_examples": select_representative_examples(
            location_records, {"MEDIUM"}
        ),
        "low_or_none_examples": select_representative_examples(
            location_records, {"LOW", "NONE"}
        ),
    }


def validate_outputs(project_ids, location_records, diagnostics):
    """Validates counts, IDs, confidence values, and diagnostic consistency."""
    output_ids = [record.get("project_id") for record in location_records]

    if len(location_records) != len(project_ids):
        raise ValueError(
            "Location record count does not match the input project count"
        )
    if output_ids != project_ids:
        raise ValueError(
            "Location project IDs do not match input project IDs and order"
        )
    if len(set(output_ids)) != len(output_ids):
        raise ValueError("Duplicate project IDs found in location output")

    for record in location_records:
        if set(record) != OUTPUT_FIELDS:
            raise ValueError(
                f"Unexpected output schema for project {record.get('project_id')}"
            )
        if bool(record.get("district")) != bool(record.get("district_source")):
            raise ValueError(
                "District and district_source must either both exist or both be null"
            )

    invalid_confidence = [
        record["confidence"]
        for record in location_records
        if record.get("confidence") not in CONFIDENCE_LEVELS
    ]
    if invalid_confidence:
        raise ValueError("Invalid confidence value found in location output")

    invalid_district_sources = [
        record.get("district_source")
        for record in location_records
        if record.get("district_source") not in DISTRICT_SOURCES
    ]
    if invalid_district_sources:
        raise ValueError("Invalid district_source found in location output")

    confidence_total = sum(diagnostics["confidence_counts"].values())
    if confidence_total != len(location_records):
        raise ValueError(
            "Diagnostic confidence counts do not match the output record count"
        )
    if diagnostics["total_projects"] != len(location_records):
        raise ValueError(
            "Diagnostic total_projects does not match the output record count"
        )

    expected_district_source_counts = dict(
        Counter(
            record["district_source"] or "NONE" for record in location_records
        )
    )
    if diagnostics["district_source_counts"] != expected_district_source_counts:
        raise ValueError(
            "Diagnostic district source counts do not match location records"
        )

    field_checks = {
        "projects_with_village_or_locality": "village_or_locality",
        "projects_with_ward": "ward",
        "projects_with_block_or_taluk": "block_or_taluk",
        "projects_with_district": "district",
    }
    for diagnostic_field, record_field in field_checks.items():
        actual_count = sum(
            record[record_field] is not None for record in location_records
        )
        if diagnostics[diagnostic_field] != actual_count:
            raise ValueError(
                f"Diagnostic count does not match output field: {record_field}"
            )


def save_json(data, filepath):
    """Saves UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_summary(diagnostics):
    """Prints a concise extraction and coverage summary."""
    counts = diagnostics["confidence_counts"]

    print("\n--- Location Extraction Summary ---")
    print(f"Projects processed: {diagnostics['total_projects']}")
    print(
        "Confidence: "
        f"HIGH={counts['HIGH']}, "
        f"MEDIUM={counts['MEDIUM']}, "
        f"LOW={counts['LOW']}, "
        f"NONE={counts['NONE']}"
    )
    print(
        "Projects with village/locality: "
        f"{diagnostics['projects_with_village_or_locality']}"
    )
    print(f"Projects with ward: {diagnostics['projects_with_ward']}")
    print(
        "Projects with block/taluk: "
        f"{diagnostics['projects_with_block_or_taluk']}"
    )
    print(f"Projects with district: {diagnostics['projects_with_district']}")
    print(
        "District sources: "
        + ", ".join(
            f"{source}={count}"
            for source, count in diagnostics["district_source_counts"].items()
        )
    )
    print(f"Output path: {OUTPUT_PATH}")
    print(f"Diagnostics path: {DIAGNOSTICS_PATH}")


def main():
    try:
        projects = load_json_list(PROJECTS_PATH)
        project_ids = validate_projects(projects)
        location_records = [
            build_location_record(project) for project in projects
        ]
        diagnostics = build_diagnostics(location_records)
        validate_outputs(project_ids, location_records, diagnostics)
        save_json(location_records, OUTPUT_PATH)
        save_json(diagnostics, DIAGNOSTICS_PATH)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to build project locations: {e}")
        sys.exit(1)

    print("SUCCESS: Location extraction complete.")
    print_summary(diagnostics)


if __name__ == "__main__":
    main()
