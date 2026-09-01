# AGENTS.md

## Project

MPLADS Risk Intelligence System.

Pipeline:

Official MPLADS API
→ raw data
→ validation
→ project dataset
→ feature engineering
→ anomaly detectors
→ combined risk
→ API-ready dataset
→ FastAPI
→ React

The anomaly engine is an offline processing pipeline. FastAPI must consume its generated output; it must not reimplement anomaly detection logic.

---

## Existing Pipeline

The `scripts/` directory is the style reference for all new Python pipeline code.

Existing stages include:

- data collection
- validation
- dataset building
- feature engineering
- cost anomaly detection
- delay anomaly detection
- expenditure anomaly detection
- duplicate/similarity detection
- combined risk scoring

Treat existing anomaly detectors and Combined Risk V1 as frozen unless explicitly asked to modify them.

---

## Coding Style

Match the existing `scripts/` code closely.

### Structure

Prefer:

1. module docstring
2. imports
3. module-level constants
4. small focused functions
5. `main()`
6. `if __name__ == "__main__":`

Use descriptive `snake_case` function/variable names and `UPPER_CASE` constants.

Use:

```python
os.path.join("data", "processed", "file.json")
Functions

Keep functions focused and readable.

Add short docstrings:

def load_json_list(filepath):
    """Loads and validates a JSON list."""

Avoid unnecessary abstractions, classes, frameworks, or clever code.

Validation

Validate important assumptions explicitly:

required files exist
expected top-level JSON structure
project IDs
malformed/missing numeric values
join consistency where relevant

Fail clearly rather than silently producing incorrect output.

Preferred errors:

ERROR: <clear explanation>

Use sys.exit(1) for fatal pipeline failures when consistent with existing scripts.

JSON

Write UTF-8 JSON using:

json.dump(data, f, ensure_ascii=False, indent=2)

Create required output directories safely.

Terminal Output

Pipeline scripts should print concise human-readable summaries.

Preferred terminology:

SUCCESS:
ERROR:
Projects processed:
Projects flagged:
Output path:

Do not flood the terminal with per-record logging.

Dependencies

Prefer the Python standard library.

Do not introduce a dependency unless it provides a meaningful benefit and is actually needed.

Data Naming

Preserve existing field names wherever possible.

Important names include:

project_id
score
flagged
reason
overall_score
risk_level
flag_count
cost
delay
expenditure
duplicate
similar_projects

Do not rename established pipeline fields without a concrete integration reason.

Risk Rules

Risk output must remain explainable.

Never describe an anomaly as confirmed:

fraud
corruption
duplicate fraud
misuse

Prefer:

anomaly
risk signal
repeated-project pattern
requires review
candidate
unusual activity

Individual detector outputs should retain their component score, flagged, and reason.

Combined Risk V1

Combined Risk V1 is frozen.

base = max(cost, delay, expenditure, duplicate)

flag_count = number of component scores >= 50

0-1 flags: bonus 0
2 flags:   bonus 10
3 flags:   bonus 15
4 flags:   bonus 20

overall_score = min(100, base + bonus)

Risk levels:

0-19   LOW
20-49  MODERATE
50-79  HIGH
80-100 CRITICAL

Do not change this formula unless explicitly requested.

Architecture Rules

Maintain separation:

scripts/
    offline data intelligence

backend/
    API/service layer

frontend/
    presentation

The backend should read processed anomaly/risk data through its service layer.

The frontend should communicate with FastAPI and should never depend directly on pipeline JSON files.

Do not move anomaly algorithms into FastAPI route handlers or frontend code.

Preserve the existing backend and frontend architecture wherever practical.

Working Rules

Before modifying code:

inspect relevant existing files
understand their real data structures
trace dependencies
make the smallest necessary change

Do not infer a JSON schema from filenames or route names. Inspect the actual structures first.

Do not rewrite working code merely for stylistic preference.

Do not modify frozen detector scripts while performing integration work.

When generating new pipeline scripts, imitate the existing scripts/ directory so code written by Codex remains visually and structurally consistent with the Claude-written code.

Run appropriate syntax/tests after changes when possible and report what was actually verified.


Save it exactly as:

```text
AGENTS.md

at:

mplads-risk-system/
├── AGENTS.md
├── scripts/
├── backend/
├── frontend/
└── data/

This is better than repeating all these rules in every Codex prompt. From now on, individual Codex prompts can be very short, such as “Build the API-ready dataset from projects.json and combined_risk.json. Follow AGENTS.md.


## Dashboard Data Rules

Pagination applies only to displayed list/table records.

Search and filters must operate on the complete backend dataset before pagination.

Dashboard analytics must never be calculated from only the current paginated page.

Correct flow:

search + filters
→ full matching dataset
→ aggregate statistics/charts/insights
→ separately paginate matching records for the table

When no filters are active, dashboard aggregates must represent the entire dataset.

When filters/search are active, aggregates must represent all matching records, not only the displayed page.

Global search should support all useful investigation fields where available, including:
- project_id
- work/activity name
- work description
- state
- constituency
- MP name
- implementing authority
- work ID

Frontend components must not simulate nationwide statistics from paginated API results.
Aggregation belongs in the backend service/API layer.

Project list and aggregate endpoints must reuse the same canonical backend
search/filter predicate so their matching totals cannot drift.

Aggregate endpoints must not accept or apply pagination parameters. Frontend
aggregate requests must not depend on table page state.

Global investigator search must be normalized and relevance-ranked in the backend
against the full dataset before pagination. Search aliases belong in centralized,
extendable configuration rather than route handlers or frontend code.

Filtered exports and generated reports must use the same search/filter scope as
the project list and aggregates. Browser-only saved/review state must be clearly
described as local rather than server-persisted.
