"""
scripts/collect_data.py

Collects raw MPLADS data (Sanctioned Works, Expenditure) from the
confirmed MoSPI PreLoginDashboardData API and saves the responses
unchanged to data/raw/.
"""

import json
import os
import sys

import requests

API_URL = "https://mplads.mospi.gov.in/rest/PreLoginDashboardData/getTilesReportData"

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://mplads.mospi.gov.in/digigov/dashboard.html",
    "Origin": "https://mplads.mospi.gov.in",
}

COMBO_NATIONWIDE_LOK_SABHA = "0,0,0,2"

RAW_DATA_DIR = os.path.join("data", "raw")

REQUEST_TIMEOUT_SECONDS = 180


def fetch_report(session, key, response_property):
    """
    Calls the getTilesReportData endpoint with the given report key
    and extracts the specified response property.

    Returns the parsed data as a Python list.
    """
    payload = {
        "combo": COMBO_NATIONWIDE_LOK_SABHA,
        "key": key,
    }

    response = session.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    top_level_data = response.json()

    if response_property not in top_level_data:
        raise ValueError(
            f"Response property '{response_property}' not found in API response "
            f"for key '{key}'."
        )

    report_data = top_level_data[response_property]

    # The report property may itself be a JSON-encoded string.
    if isinstance(report_data, str):
        report_data = json.loads(report_data)

    if not isinstance(report_data, list):
        raise ValueError(
            f"Expected a list for '{response_property}' (key '{key}'), "
            f"got {type(report_data).__name__} instead."
        )

    return report_data


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def count_unique_ids(rows, id_field="WORK_RECOMMENDATION_DTL_ID"):
    """Counts unique non-null values of id_field across row dictionaries."""
    return len({
        row.get(id_field)
        for row in rows
        if row.get(id_field) is not None
    })


def main():
    session = requests.Session()

    try:
        print("Fetching sanctioned works data...")
        sanctioned = fetch_report(
            session,
            key="Works Sanctioned",
            response_property="Total Sanction Work",
        )
        print(f"  Retrieved {len(sanctioned)} sanctioned rows.")

        print("Fetching expenditure data...")
        expenditure = fetch_report(
            session,
            key="Expenditure on Completed and On-going Works as on Date",
            response_property="Total Expenditure",
        )
        print(f"  Retrieved {len(expenditure)} expenditure rows.")

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network/API request failed: {e}")
        sys.exit(1)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: Failed to parse API response: {e}")
        sys.exit(1)

    sanctioned_path = os.path.join(RAW_DATA_DIR, "sanctioned.json")
    expenditure_path = os.path.join(RAW_DATA_DIR, "expenditure.json")

    try:
        save_json(sanctioned, sanctioned_path)
        save_json(expenditure, expenditure_path)
    except OSError as e:
        print(f"ERROR: Failed to save data to disk: {e}")
        sys.exit(1)

    unique_sanctioned_ids = count_unique_ids(sanctioned)
    unique_expenditure_ids = count_unique_ids(expenditure)

    print("\n--- Collection Summary ---")
    print(f"Sanctioned rows: {len(sanctioned)}")
    print(f"Expenditure rows: {len(expenditure)}")
    print(f"Unique sanctioned WORK_RECOMMENDATION_DTL_ID: {unique_sanctioned_ids}")
    print(f"Unique expenditure WORK_RECOMMENDATION_DTL_ID: {unique_expenditure_ids}")
    print(f"\nSaved: {sanctioned_path}")
    print(f"Saved: {expenditure_path}")
    print("SUCCESS: Data collection complete.")


if __name__ == "__main__":
    main()