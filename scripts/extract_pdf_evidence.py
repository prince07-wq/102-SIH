"""
scripts/extract_pdf_evidence.py

Extracts project-photo evidence and visible location metadata from an MPLADS
attachment PDF without modifying the source document.

PDF text, embedded-image metadata, and EXIF metadata are inspected before the
optional local OCR fallback. Extracted images and a structured evidence JSON
record are written to a separate output directory.
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

try:
    import pymupdf
except ImportError:
    pymupdf = None

try:
    from PIL import ExifTags, Image
except ImportError:
    ExifTags = None
    Image = None


DEFAULT_OUTPUT_ROOT = os.path.join("data", "processed", "pdf_evidence")

LATITUDE_PATTERN = re.compile(
    r"\b(?:lat|latitude)\s*[:=\-]?\s*([NS]?\s*[+\-]?\d{1,2}(?:[.,]\d+)?)",
    re.IGNORECASE,
)
LONGITUDE_PATTERN = re.compile(
    r"\b(?:lon|long|longitude)\s*[:=\-]?\s*([EW]?\s*[+\-]?\d{1,3}(?:[.,]\d+)?)",
    re.IGNORECASE,
)
TIMESTAMP_PATTERN = re.compile(
    r"\b(\d{1,4}[/-]\d{1,2}[/-]\d{1,4})"
    r"(?:\s+|T)(\d{1,2}:\d{2}(?::\d{2})?)"
    r"(?:\s*([AP]M))?"
    r"(?:\s*(?:GMT|UTC)?\s*([+\-]\d{2}:?\d{2}))?\b",
    re.IGNORECASE,
)
LOCATION_HINT_PATTERN = re.compile(
    r"\b(?:india|address|location|village|district|taluk|state|road|street|pin)\b"
    r"|\b[A-Z0-9]{4}\+[A-Z0-9]{2,3}\b|\b\d{6}\b",
    re.IGNORECASE,
)


def calculate_sha256(filepath):
    """Calculates the SHA-256 digest of a file without changing it."""
    digest = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_json(data, filepath):
    """Saves data as UTF-8 pretty-printed JSON, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clean_ocr_text(text):
    """Normalizes whitespace while retaining OCR punctuation needed by parsers."""
    return " ".join(str(text).replace("\u00a0", " ").split())


def parse_labeled_coordinate(text, pattern, minimum, maximum):
    """Extracts and validates one labeled decimal coordinate from text."""
    match = pattern.search(text)
    if not match:
        return None

    raw_value = match.group(1).replace(" ", "").replace(",", ".")
    hemisphere = None
    if raw_value and raw_value[0].upper() in {"N", "S", "E", "W"}:
        hemisphere = raw_value[0].upper()
        raw_value = raw_value[1:]

    try:
        value = float(raw_value)
    except ValueError:
        return None

    if hemisphere in {"S", "W"}:
        value = -abs(value)
    if not minimum <= value <= maximum:
        return None
    return value


def parse_timestamp(text):
    """Extracts a visible date/time and returns raw and ISO-normalized values."""
    match = TIMESTAMP_PATTERN.search(text)
    if not match:
        return None, None

    date_text, time_text, meridiem, offset_text = match.groups()
    raw_timestamp = clean_ocr_text(match.group(0))
    date_parts = re.split(r"[/-]", date_text)

    date_formats = []
    if len(date_parts[0]) == 4:
        date_formats = ["%Y/%m/%d", "%Y-%m-%d"]
    elif int(date_parts[0]) > 12:
        date_formats = ["%d/%m/%y", "%d-%m-%y", "%d/%m/%Y", "%d-%m-%Y"]
    elif int(date_parts[1]) > 12:
        date_formats = ["%m/%d/%y", "%m-%d-%y", "%m/%d/%Y", "%m-%d-%Y"]
    else:
        # MPLADS evidence is Indian government material, so ambiguous numeric
        # dates are interpreted day-first and the untouched value is retained.
        date_formats = ["%d/%m/%y", "%d-%m-%y", "%d/%m/%Y", "%d-%m-%Y"]

    time_format = "%I:%M:%S %p" if meridiem and time_text.count(":") == 2 else None
    if meridiem and time_format is None:
        time_format = "%I:%M %p"
    if not meridiem:
        time_format = "%H:%M:%S" if time_text.count(":") == 2 else "%H:%M"

    parsed_date = None
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(date_text, date_format).date()
            break
        except ValueError:
            continue
    if parsed_date is None:
        return raw_timestamp, None

    try:
        parsed_time = datetime.strptime(
            f"{time_text} {meridiem}".strip(), time_format
        ).time()
    except ValueError:
        return raw_timestamp, None

    tzinfo = None
    if offset_text:
        compact_offset = offset_text.replace(":", "")
        sign = 1 if compact_offset[0] == "+" else -1
        hours = int(compact_offset[1:3])
        minutes = int(compact_offset[3:5])
        if hours <= 23 and minutes <= 59:
            tzinfo = timezone(sign * timedelta(hours=hours, minutes=minutes))

    parsed = datetime.combine(parsed_date, parsed_time, tzinfo=tzinfo)
    return raw_timestamp, parsed.isoformat()


def find_location_lines(ocr_rows, coordinate_row_index):
    """Finds likely place/address lines immediately preceding GPS coordinates."""
    if coordinate_row_index is None:
        return []

    candidates = []
    start = max(0, coordinate_row_index - 4)
    for row in ocr_rows[start:coordinate_row_index]:
        text = clean_ocr_text(row["text"])
        if not text or LATITUDE_PATTERN.search(text) or LONGITUDE_PATTERN.search(text):
            continue
        if TIMESTAMP_PATTERN.search(text):
            continue
        if LOCATION_HINT_PATTERN.search(text):
            candidates.append(text)
    return candidates[-3:]


def parse_visible_metadata(rows):
    """Parses coordinates, location text, and timestamp from ordered text rows."""
    combined_text = "\n".join(clean_ocr_text(row["text"]) for row in rows)
    latitude = parse_labeled_coordinate(
        combined_text, LATITUDE_PATTERN, -90.0, 90.0
    )
    longitude = parse_labeled_coordinate(
        combined_text, LONGITUDE_PATTERN, -180.0, 180.0
    )

    coordinate_row_index = None
    for index, row in enumerate(rows):
        row_text = clean_ocr_text(row["text"])
        if LATITUDE_PATTERN.search(row_text) or LONGITUDE_PATTERN.search(row_text):
            coordinate_row_index = index
            break

    location_lines = find_location_lines(rows, coordinate_row_index)
    raw_timestamp, normalized_timestamp = parse_timestamp(combined_text)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "place_text": location_lines[0] if location_lines else None,
        "address_text": location_lines[1] if len(location_lines) > 1 else None,
        "location_text": " | ".join(location_lines) if location_lines else None,
        "timestamp": normalized_timestamp or raw_timestamp,
        "timestamp_raw": raw_timestamp,
        "coordinate_row_index": coordinate_row_index,
    }


def rational_to_float(value):
    """Converts a Pillow rational value to float."""
    return float(value.numerator) / float(value.denominator)


def degrees_minutes_seconds_to_decimal(values, reference):
    """Converts EXIF degrees/minutes/seconds coordinates to decimal degrees."""
    degrees = rational_to_float(values[0])
    minutes = rational_to_float(values[1])
    seconds = rational_to_float(values[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if str(reference).upper() in {"S", "W"}:
        decimal = -decimal
    return decimal


def extract_exif_metadata(image_bytes):
    """Reads GPS and capture-time values from an embedded image's EXIF data."""
    metadata = {
        "latitude": None,
        "longitude": None,
        "timestamp": None,
    }
    if Image is None or ExifTags is None:
        return metadata

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            exif = image.getexif()
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo) if exif else {}
            latitude_values = gps_ifd.get(2)
            latitude_reference = gps_ifd.get(1)
            longitude_values = gps_ifd.get(4)
            longitude_reference = gps_ifd.get(3)
            if latitude_values and latitude_reference:
                metadata["latitude"] = degrees_minutes_seconds_to_decimal(
                    latitude_values, latitude_reference
                )
            if longitude_values and longitude_reference:
                metadata["longitude"] = degrees_minutes_seconds_to_decimal(
                    longitude_values, longitude_reference
                )

            timestamp = exif.get(ExifTags.Base.DateTimeOriginal) or exif.get(
                ExifTags.Base.DateTime
            )
            if timestamp:
                try:
                    metadata["timestamp"] = datetime.strptime(
                        str(timestamp), "%Y:%m:%d %H:%M:%S"
                    ).isoformat()
                except ValueError:
                    metadata["timestamp"] = str(timestamp)
    except (OSError, TypeError, ValueError, KeyError):
        pass
    return metadata


def run_local_ocr(image_bytes):
    """Runs local RapidOCR and returns ordered text rows with bounding boxes."""
    try:
        import cv2
        import numpy
        from rapidocr_onnxruntime import RapidOCR
    except ImportError as e:
        raise RuntimeError(
            "OCR is required but unavailable. Install dependencies from "
            "scripts/pdf_evidence_requirements.txt."
        ) from e

    image_array = cv2.imdecode(
        numpy.frombuffer(image_bytes, dtype=numpy.uint8), cv2.IMREAD_COLOR
    )
    if image_array is None:
        raise ValueError("The extracted image could not be decoded for OCR.")

    raw_result, _ = RapidOCR()(image_array)
    rows = []
    for item in raw_result or []:
        box, text, confidence = item
        rows.append({
            "text": clean_ocr_text(text),
            "confidence": round(float(confidence), 4),
            "box": [[round(float(x), 2), round(float(y), 2)] for x, y in box],
        })
    rows.sort(key=lambda row: min(point[1] for point in row["box"]))
    return rows, image_array


def get_coordinate_anchor(rows, coordinate_row_index):
    """Returns the center point of a coordinate OCR row when available."""
    if coordinate_row_index is None or coordinate_row_index >= len(rows):
        return None
    box = rows[coordinate_row_index]["box"]
    return (
        sum(point[0] for point in box) / len(box),
        sum(point[1] for point in box) / len(box),
    )


def detect_photo_crop(image_array, anchor):
    """Detects a large photo-like color region containing the GPS overlay."""
    import cv2
    import numpy

    height, width = image_array.shape[:2]
    hsv = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
    mask = numpy.where(
        (hsv[:, :, 1] > 35) | (hsv[:, :, 2] < 100), 255, 0
    ).astype(numpy.uint8)
    kernel_size = max(9, int(min(width, height) * 0.03))
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (kernel_size, kernel_size)
    )
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    _, _, stats, _ = cv2.connectedComponentsWithStats(mask)

    candidates = []
    for x, y, candidate_width, candidate_height, area in stats[1:]:
        x = int(x)
        y = int(y)
        candidate_width = int(candidate_width)
        candidate_height = int(candidate_height)
        area = int(area)
        box_area = candidate_width * candidate_height
        if box_area < width * height * 0.08:
            continue
        if candidate_width < width * 0.35 or candidate_height < height * 0.12:
            continue
        contains_anchor = bool(
            anchor
            and x <= anchor[0] <= x + candidate_width
            and y <= anchor[1] <= y + candidate_height
        )
        if anchor and not contains_anchor:
            continue
        candidates.append((contains_anchor, area, x, y, candidate_width, candidate_height))

    if not candidates:
        return None

    _, _, x, y, candidate_width, candidate_height = max(candidates)
    horizontal_padding = int(candidate_width * 0.03)
    top_padding = int(candidate_height * 0.08)
    bottom_padding = int(candidate_height * 0.04)
    left = max(0, x - horizontal_padding)
    top = max(0, y - top_padding)
    right = min(width, x + candidate_width + horizontal_padding)
    bottom = min(height, y + candidate_height + bottom_padding)

    return {
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom,
    }


def save_photo_crop(image_array, crop_box, filepath):
    """Saves a detected project-photo crop as a high-quality JPEG."""
    import cv2

    crop = image_array[
        crop_box["top"]:crop_box["bottom"],
        crop_box["left"]:crop_box["right"],
    ]
    if crop.size == 0 or not cv2.imwrite(filepath, crop, [cv2.IMWRITE_JPEG_QUALITY, 95]):
        raise OSError(f"Failed to save detected project photo: {filepath}")


def path_for_output(filepath):
    """Returns a readable path relative to the current working directory."""
    try:
        return os.path.relpath(os.path.abspath(filepath), os.getcwd())
    except ValueError:
        return os.path.abspath(filepath)


def inspect_pdf(pdf_path, output_dir):
    """Inspects all PDF pages and returns structured project evidence."""
    if pymupdf is None:
        raise RuntimeError(
            "PyMuPDF is required. Install dependencies from "
            "scripts/pdf_evidence_requirements.txt."
        )
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Required PDF not found: {pdf_path}")
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(f"Expected a PDF input file: {pdf_path}")

    os.makedirs(output_dir, exist_ok=True)
    source_hash_before = calculate_sha256(pdf_path)
    pages = []
    evidence_candidates = []

    with pymupdf.open(pdf_path) as document:
        if document.page_count < 1:
            raise ValueError(f"PDF has no pages: {pdf_path}")

        for page_index in range(document.page_count):
            page = document[page_index]
            page_number = page_index + 1
            native_text_raw = page.get_text("text")
            native_text = clean_ocr_text(native_text_raw)
            native_rows = [
                {"text": clean_ocr_text(line)}
                for line in native_text_raw.splitlines()
                if clean_ocr_text(line)
            ]
            native_metadata = parse_visible_metadata(native_rows)
            page_record = {
                "page_number": page_number,
                "native_text_character_count": len(native_text),
                "embedded_images": [],
                "ocr_used": False,
                "ocr_text": None,
                "ocr_failure": None,
            }

            images = page.get_images(full=True)
            for image_index, image_info in enumerate(images, start=1):
                xref = image_info[0]
                extracted = document.extract_image(xref)
                extension = extracted["ext"]
                image_filename = (
                    f"page_{page_number:03d}_image_{image_index:03d}.{extension}"
                )
                image_path = os.path.join(output_dir, image_filename)
                with open(image_path, "wb") as f:
                    f.write(extracted["image"])

                image_rectangles = page.get_image_rects(xref)
                page_area = max(page.rect.width * page.rect.height, 1)
                placement_area = max(
                    (rectangle.width * rectangle.height for rectangle in image_rectangles),
                    default=0,
                )
                whole_page_like = placement_area / page_area >= 0.85
                exif_metadata = extract_exif_metadata(extracted["image"])
                image_record = {
                    "image_index": image_index,
                    "path": path_for_output(image_path),
                    "width": extracted["width"],
                    "height": extracted["height"],
                    "extension": extension,
                    "whole_page_scan": whole_page_like,
                    "exif_gps_found": bool(
                        exif_metadata["latitude"] is not None
                        and exif_metadata["longitude"] is not None
                    ),
                }
                page_record["embedded_images"].append(image_record)

                selected_metadata = exif_metadata
                metadata_method = "image_exif"
                ocr_rows = []
                image_array = None
                if (
                    selected_metadata["latitude"] is None
                    or selected_metadata["longitude"] is None
                ) and (
                    native_metadata["latitude"] is None
                    or native_metadata["longitude"] is None
                ):
                    try:
                        ocr_rows, image_array = run_local_ocr(extracted["image"])
                        ocr_metadata = parse_visible_metadata(ocr_rows)
                        page_record["ocr_used"] = True
                        page_record["ocr_text"] = "\n".join(
                            row["text"] for row in ocr_rows
                        )
                        selected_metadata = ocr_metadata
                        metadata_method = "local_ocr"
                    except (RuntimeError, ValueError) as e:
                        page_record["ocr_failure"] = str(e)

                if (
                    native_metadata["latitude"] is not None
                    and native_metadata["longitude"] is not None
                ):
                    selected_metadata = native_metadata
                    metadata_method = "pdf_text"

                photo_path = image_path
                photo_method = "direct_embedded_image"
                crop_box = None
                coordinate_anchor = get_coordinate_anchor(
                    ocr_rows, selected_metadata.get("coordinate_row_index")
                )
                if whole_page_like and image_array is not None:
                    crop_box = detect_photo_crop(image_array, coordinate_anchor)
                    if crop_box:
                        photo_filename = (
                            f"page_{page_number:03d}_project_photo_{image_index:03d}.jpg"
                        )
                        photo_path = os.path.join(output_dir, photo_filename)
                        save_photo_crop(image_array, crop_box, photo_path)
                        photo_method = "detected_crop_from_page_scan"

                has_coordinates = bool(
                    selected_metadata["latitude"] is not None
                    and selected_metadata["longitude"] is not None
                )
                has_project_photo = bool(
                    crop_box or (not whole_page_like and placement_area / page_area >= 0.03)
                )
                if has_project_photo:
                    evidence_candidates.append({
                        "has_project_photo": True,
                        "photo_path": path_for_output(photo_path),
                        "embedded_image_path": path_for_output(image_path),
                        "latitude": selected_metadata["latitude"],
                        "longitude": selected_metadata["longitude"],
                        "place_text": selected_metadata.get("place_text"),
                        "address_text": selected_metadata.get("address_text"),
                        "location_text": selected_metadata.get("location_text"),
                        "timestamp": selected_metadata["timestamp"],
                        "timestamp_raw": selected_metadata.get("timestamp_raw"),
                        "source_page": page_number,
                        "metadata_extraction_method": metadata_method,
                        "photo_extraction_method": photo_method,
                        "photo_crop_box_pixels": crop_box,
                        "has_coordinates": has_coordinates,
                    })

            pages.append(page_record)

    source_hash_after = calculate_sha256(pdf_path)
    if source_hash_before != source_hash_after:
        raise RuntimeError("Source PDF changed during extraction; output was not trusted.")

    selected = max(
        evidence_candidates,
        key=lambda candidate: (
            candidate["has_coordinates"],
            candidate["location_text"] is not None,
            candidate["timestamp"] is not None,
        ),
        default=None,
    )
    result = selected or {
        "has_project_photo": False,
        "photo_path": None,
        "embedded_image_path": None,
        "latitude": None,
        "longitude": None,
        "place_text": None,
        "address_text": None,
        "location_text": None,
        "timestamp": None,
        "timestamp_raw": None,
        "source_page": None,
        "metadata_extraction_method": None,
        "photo_extraction_method": None,
        "photo_crop_box_pixels": None,
        "has_coordinates": False,
    }
    result.update({
        "source_pdf": os.path.basename(pdf_path),
        "source_pdf_sha256": source_hash_before,
        "source_pdf_preserved": True,
        "pages_inspected": len(pages),
        "pages": pages,
        "limitations": [
            "OCR text can contain spelling or punctuation errors and should be reviewed.",
            "A project photo inside a full-page scan is an estimated crop, not a distinct PDF image object.",
            "The extractor detects photo-like regions associated with GPS evidence; it does not verify what the photographed work depicts.",
        ],
    })
    return result


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract project-photo and visible GPS evidence from one PDF."
    )
    parser.add_argument("pdf_path", help="Path to the source attachment PDF.")
    parser.add_argument(
        "--output-dir",
        help=(
            "Directory for evidence.json and extracted images. Defaults to "
            "data/processed/pdf_evidence/<PDF stem>."
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = args.output_dir
    if not output_dir:
        filename = os.path.basename(args.pdf_path)
        stem = os.path.splitext(filename)[0]
        output_dir = os.path.join(DEFAULT_OUTPUT_ROOT, stem)

    try:
        result = inspect_pdf(args.pdf_path, output_dir)
        output_path = os.path.join(output_dir, "evidence.json")
        save_json(result, output_path)
    except (FileNotFoundError, OSError, RuntimeError, TypeError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("\n--- PDF Evidence Extraction Summary ---")
    print(f"Pages inspected: {result['pages_inspected']}")
    print(f"Project photo found: {result['has_project_photo']}")
    print(f"Coordinates found: {result['has_coordinates']}")
    print(f"Metadata method: {result['metadata_extraction_method']}")
    print(f"Source PDF preserved: {result['source_pdf_preserved']}")
    print(f"Output path: {output_path}")
    print("SUCCESS: PDF evidence extraction complete.")


if __name__ == "__main__":
    main()
