"""
services/evidence_service.py
============================
On-demand retrieval and processing of official MPLADS project evidence.

This service resolves numeric completed-work WORK_ID values, downloads only attachments asked
for by a project-details request, invokes the existing offline PDF evidence
extractor, and caches normalized results for local development.
"""

import base64
import binascii
import json
import mimetypes
import os
import re
import subprocess
import sys
import threading
from urllib.parse import quote

import httpx

from app.services import project_service
from app.services.evidence_cache import LocalEvidenceCache


ATTACHMENT_IDS_URL = (
    "https://mplads.mospi.gov.in/rest/PreLoginDashboardData/getAttachIdsbyFlag"
)
ATTACHMENT_FILE_URL = (
    "https://mplads.mospi.gov.in/rest/PreLoginCitizenWorkRcmdRest/"
    "getAttachmentById"
)
MPLADS_ORIGIN = "https://mplads.mospi.gov.in"
REQUEST_TIMEOUT_SECONDS = 60
MAX_DECODED_ATTACHMENT_BYTES = 30 * 1024 * 1024

_SERVICE_DIR = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.abspath(os.path.join(_SERVICE_DIR, "..", "..", ".."))
_EXTRACTOR_PATH = os.path.join(_PROJECT_ROOT, "scripts", "extract_pdf_evidence.py")

_CACHE = LocalEvidenceCache()
_PROJECT_LOCKS = {}
_PROJECT_LOCKS_GUARD = threading.Lock()

_FILENAME_KEYS = {
    "filename",
    "file_name",
    "attach_name",
    "attachment_name",
    "attach_file_name",
    "original_file_name",
    "document_name",
}
_CONTENT_KEYS = {
    "base64",
    "content",
    "data",
    "file",
    "file_content",
    "file_data",
    "attachment",
    "attachment_data",
    "document",
}
_ATTACHMENT_ID_KEYS = {
    "id",
    "attach_id",
    "attachment_id",
    "attachid",
    "attachmentid",
}


class ProjectNotFoundError(Exception):
    """Raised when evidence is requested for an unknown project."""


def _project_lock(project_id):
    """Returns a process-local lock preventing duplicate concurrent downloads."""
    project_key = str(project_id)
    with _PROJECT_LOCKS_GUARD:
        return _PROJECT_LOCKS.setdefault(project_key, threading.Lock())


def _normalize_key(value):
    """Normalizes response keys from inconsistent official API casing."""
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def _decode_json_strings(value):
    """Unwraps API values that contain JSON encoded as a string."""
    current = value
    for _ in range(3):
        if not isinstance(current, str):
            break
        text = current.strip()
        if not text or text[0] not in "[{\"":
            break
        try:
            current = json.loads(text)
        except json.JSONDecodeError:
            break
    return current


def _response_payload(response):
    """Validates an official API response and returns JSON or plain text."""
    response.raise_for_status()
    if not response.content or not response.text.strip():
        return None
    try:
        return _decode_json_strings(response.json())
    except (ValueError, json.JSONDecodeError):
        return _decode_json_strings(response.text)


def _collect_attachment_ids(value):
    """Extracts attachment IDs from common list and object response shapes."""
    value = _decode_json_strings(value)
    found = []
    if value is None:
        return found
    if isinstance(value, (str, int)):
        text = str(value).strip()
        return [text] if text else []
    if isinstance(value, list):
        for item in value:
            found.extend(_collect_attachment_ids(item))
        return found
    if isinstance(value, dict):
        matched_key = False
        for key, item in value.items():
            if _normalize_key(key) in _ATTACHMENT_ID_KEYS:
                matched_key = True
                found.extend(_collect_attachment_ids(item))
        if not matched_key:
            for item in value.values():
                if isinstance(item, (dict, list)):
                    found.extend(_collect_attachment_ids(item))
        return found
    return found


def _unique_attachment_ids(payload):
    """Returns non-empty attachment IDs in official response order."""
    unique = []
    seen = set()
    for attachment_id in _collect_attachment_ids(payload):
        if attachment_id not in seen:
            seen.add(attachment_id)
            unique.append(attachment_id)
    return unique


def _find_named_value(value, accepted_keys):
    """Recursively finds the first scalar value under a recognized key."""
    value = _decode_json_strings(value)
    if isinstance(value, dict):
        for key, item in value.items():
            if _normalize_key(key) in accepted_keys and isinstance(
                item, (str, int, float)
            ):
                return str(item)
        for item in value.values():
            found = _find_named_value(item, accepted_keys)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_named_value(item, accepted_keys)
            if found is not None:
                return found
    return None


def _base64_candidates(value):
    """Yields likely Base64 strings from supported attachment response shapes."""
    value = _decode_json_strings(value)
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        preferred = []
        remaining = []
        for key, item in value.items():
            target = preferred if _normalize_key(key) in _CONTENT_KEYS else remaining
            target.append(item)
        for item in preferred + remaining:
            yield from _base64_candidates(item)
    elif isinstance(value, list):
        for item in value:
            yield from _base64_candidates(item)


def _try_decode_base64(value):
    """Strictly decodes one Base64 candidate within the configured size limit."""
    text = str(value).strip()
    if text.startswith("data:") and "," in text:
        text = text.split(",", 1)[1]
    compact = re.sub(r"\s+", "", text)
    if len(compact) < 32:
        return None
    if len(compact) > (MAX_DECODED_ATTACHMENT_BYTES * 4 // 3) + 16:
        raise ValueError("Official attachment exceeds the development size limit")
    compact += "=" * (-len(compact) % 4)
    try:
        decoded = base64.b64decode(compact, validate=True)
    except (binascii.Error, ValueError):
        return None
    if not decoded:
        return None
    if len(decoded) > MAX_DECODED_ATTACHMENT_BYTES:
        raise ValueError("Official attachment exceeds the development size limit")
    return decoded


def _decode_attachment(payload):
    """Extracts filename and decoded bytes from an attachment API response."""
    filename = _find_named_value(payload, _FILENAME_KEYS)
    for candidate in _base64_candidates(payload):
        decoded = _try_decode_base64(candidate)
        if decoded is not None:
            return filename, decoded
    raise ValueError("Official attachment response contained no valid Base64 file")


def _detect_file_type(content, filename):
    """Detects a safe extension and media type from file signatures first."""
    signatures = [
        (b"%PDF-", ".pdf", "application/pdf"),
        (b"\xff\xd8\xff", ".jpg", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n", ".png", "image/png"),
        (b"GIF87a", ".gif", "image/gif"),
        (b"GIF89a", ".gif", "image/gif"),
        (b"II*\x00", ".tif", "image/tiff"),
        (b"MM\x00*", ".tif", "image/tiff"),
    ]
    for signature, extension, media_type in signatures:
        if content.startswith(signature):
            return extension, media_type
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return ".webp", "image/webp"

    extension = os.path.splitext(str(filename or ""))[1].lower()
    media_type = mimetypes.guess_type(str(filename or ""))[0]
    if extension and media_type:
        return extension, media_type
    return ".bin", "application/octet-stream"


def _safe_original_filename(filename, attachment_id, extension):
    """Returns a displayable filename that cannot escape the cache directory."""
    basename = os.path.basename(str(filename or "").replace("\\", "/")).strip()
    basename = re.sub(r"[\x00-\x1f<>:\"/\\|?*]+", "_", basename)
    basename = basename.strip(" .")
    if not basename:
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(attachment_id))[:50]
        basename = f"attachment_{safe_id or 'file'}{extension}"
    if not os.path.splitext(basename)[1]:
        basename += extension
    return basename[:180]


def _asset_url(project_id, relative_path):
    """Builds a backend URL for one cached original or extracted asset."""
    project_part = quote(str(project_id), safe="")
    asset_part = quote(relative_path.replace("\\", "/"), safe="/")
    return f"/api/projects/{project_part}/evidence/files/{asset_part}"


def _run_pdf_extractor(pdf_path, output_dir):
    """Invokes the existing PDF evidence extractor and loads its JSON output."""
    if not os.path.isfile(_EXTRACTOR_PATH):
        raise FileNotFoundError(f"PDF evidence extractor not found: {_EXTRACTOR_PATH}")
    command = [
        sys.executable,
        _EXTRACTOR_PATH,
        pdf_path,
        "--output-dir",
        output_dir,
    ]
    completed = subprocess.run(
        command,
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(detail or "PDF evidence extraction failed")
    evidence_path = os.path.join(output_dir, "evidence.json")
    with open(evidence_path, "r", encoding="utf-8") as f:
        evidence = json.load(f)
    if not isinstance(evidence, dict):
        raise ValueError("PDF evidence extractor returned an invalid record")
    return evidence


def _extractor_photo_path(evidence, output_dir):
    """Resolves the extractor's selected photo within its assigned directory."""
    photo_value = evidence.get("photo_path")
    if not photo_value:
        return None
    candidate = os.path.abspath(os.path.join(_PROJECT_ROOT, str(photo_value)))
    output_root = os.path.abspath(output_dir)
    if os.path.commonpath([output_root, candidate]) != output_root:
        candidate = os.path.join(output_root, os.path.basename(str(photo_value)))
    if os.path.commonpath([output_root, os.path.abspath(candidate)]) != output_root:
        return None
    return candidate if os.path.isfile(candidate) else None


def _empty_response(status, cached=False):
    """Builds a normalized response with no attachment records."""
    return {
        "status": status,
        "attachments": [],
        "has_project_photo": False,
        "photos": [],
        "latitude": None,
        "longitude": None,
        "location_text": None,
        "timestamp": None,
        "original_file_name": None,
        "evidence_type": status,
        "cached": cached,
    }


def _normalize_official_work_id(work_id):
    """Returns a numeric official WORK_ID string, or None when malformed."""
    if isinstance(work_id, bool) or work_id is None:
        return None
    text = str(work_id).strip()
    return text if text.isdigit() else None


def _fetch_attachment_ids(client, official_work_ids):
    """Fetches and deduplicates attachment IDs for the project's WORK_ID values."""
    attachment_ids = []
    seen = set()
    for work_id in official_work_ids:
        normalized_work_id = _normalize_official_work_id(work_id)
        if not normalized_work_id:
            continue
        response = client.post(
            ATTACHMENT_IDS_URL,
            json={
                "json": {
                    "FLAG": "3",
                    "WORK_ID": normalized_work_id,
                }
            },
        )
        for attachment_id in _unique_attachment_ids(_response_payload(response)):
            if attachment_id not in seen:
                seen.add(attachment_id)
                attachment_ids.append(attachment_id)
    return attachment_ids


def _process_attachment(
    project_id,
    attachment_id,
    attachment_index,
    client,
    cache,
    extractor_runner,
):
    """Downloads, caches, and normalizes one official attachment."""
    attachment_key = f"attachment_{attachment_index:03d}"
    response = client.post(ATTACHMENT_FILE_URL, json={"id": str(attachment_id)})
    payload = _response_payload(response)
    filename, content = _decode_attachment(payload)
    extension, content_type = _detect_file_type(content, filename)
    original_filename = _safe_original_filename(filename, attachment_id, extension)
    original_path = cache.save_attachment(
        project_id, attachment_key, original_filename, content
    )
    original_relative_path = os.path.relpath(
        original_path, cache.project_directory(project_id)
    )

    attachment = {
        "attachment_id": str(attachment_id),
        "original_file_name": original_filename,
        "content_type": content_type,
        "evidence_type": "DOCUMENT_ONLY",
        "original_url": _asset_url(project_id, original_relative_path),
        "photos": [],
        "processing_error": None,
    }
    metadata = {
        "latitude": None,
        "longitude": None,
        "location_text": None,
        "timestamp": None,
    }

    if content_type == "application/pdf":
        output_dir = os.path.join(
            cache.attachment_directory(project_id, attachment_key), "extracted"
        )
        try:
            evidence = extractor_runner(original_path, output_dir)
        except (
            OSError,
            RuntimeError,
            subprocess.SubprocessError,
            ValueError,
        ):
            attachment["evidence_type"] = "PROCESSING_FAILED"
            attachment["processing_error"] = (
                "Official PDF was downloaded but its evidence could not be extracted."
            )
            return attachment, metadata
        if evidence.get("has_project_photo"):
            photo_path = _extractor_photo_path(evidence, output_dir)
            if photo_path is None:
                raise ValueError("PDF extractor reported a photo but saved no photo file")
            photo_relative_path = os.path.relpath(
                photo_path, cache.project_directory(project_id)
            )
            photo = {
                "url": _asset_url(project_id, photo_relative_path),
                "attachment_id": str(attachment_id),
                "source_page": evidence.get("source_page"),
            }
            attachment["photos"].append(photo)
            has_gps = bool(
                evidence.get("latitude") is not None
                and evidence.get("longitude") is not None
            )
            attachment["evidence_type"] = "PHOTO_GPS" if has_gps else "PHOTO_ONLY"
            for key in metadata:
                metadata[key] = evidence.get(key)
    elif content_type.startswith("image/"):
        photo = {
            "url": attachment["original_url"],
            "attachment_id": str(attachment_id),
            "source_page": None,
        }
        attachment["photos"].append(photo)
        attachment["evidence_type"] = "PHOTO_ONLY"

    return attachment, metadata


def _aggregate_response(attachments):
    """Builds the project-level evidence classification and limited metadata."""
    photos = [photo for item in attachments for photo in item.get("photos", [])]
    gps_attachment = next(
        (item for item in attachments if item["evidence_type"] == "PHOTO_GPS"),
        None,
    )
    if gps_attachment:
        status = "PHOTO_GPS"
    elif photos:
        status = "PHOTO_ONLY"
    elif any(item["evidence_type"] == "DOCUMENT_ONLY" for item in attachments):
        status = "DOCUMENT_ONLY"
    else:
        status = "PROCESSING_FAILED"

    metadata_source = gps_attachment or next(
        (
            item
            for item in attachments
            if any((item.get("_metadata") or {}).get(key) is not None for key in (
                "latitude",
                "longitude",
                "location_text",
                "timestamp",
            ))
        ),
        None,
    )
    metadata = metadata_source.get("_metadata", {}) if metadata_source else {}
    public_attachments = []
    for item in attachments:
        public_item = dict(item)
        public_item.pop("_metadata", None)
        public_attachments.append(public_item)

    selected_attachment = gps_attachment or next(
        (item for item in attachments if item.get("photos")),
        attachments[0] if attachments else None,
    )
    return {
        "status": status,
        "attachments": public_attachments,
        "has_project_photo": bool(photos),
        "photos": photos,
        "latitude": metadata.get("latitude"),
        "longitude": metadata.get("longitude"),
        "location_text": metadata.get("location_text"),
        "timestamp": metadata.get("timestamp"),
        "original_file_name": (
            selected_attachment.get("original_file_name")
            if selected_attachment
            else None
        ),
        "evidence_type": status,
        "cached": False,
    }


def _new_http_client():
    """Creates the official MPLADS HTTP client used by on-demand requests."""
    return httpx.Client(
        headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{MPLADS_ORIGIN}/digigov/dashboard.html",
            "Origin": MPLADS_ORIGIN,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
        follow_redirects=True,
    )


def get_project_evidence(
    project_id,
    cache=None,
    client=None,
    extractor_runner=None,
):
    """Returns cached or freshly processed official evidence for one project."""
    official_work_ids = project_service.get_project_official_work_ids(project_id)
    if official_work_ids is None:
        raise ProjectNotFoundError(str(project_id))

    active_cache = cache or _CACHE
    active_extractor = extractor_runner or _run_pdf_extractor
    with _project_lock(project_id):
        cached_response = active_cache.load_response(project_id)
        if cached_response is not None:
            return cached_response

        if not official_work_ids:
            result = _empty_response("NO_ATTACHMENT")
            active_cache.save_response(project_id, result)
            return result

        owns_client = client is None
        active_client = client or _new_http_client()
        try:
            attachment_ids = _fetch_attachment_ids(active_client, official_work_ids)
            if not attachment_ids:
                result = _empty_response("NO_ATTACHMENT")
                active_cache.save_response(project_id, result)
                return result

            attachments = []
            for index, attachment_id in enumerate(attachment_ids, start=1):
                try:
                    attachment, metadata = _process_attachment(
                        project_id,
                        attachment_id,
                        index,
                        active_client,
                        active_cache,
                        active_extractor,
                    )
                    attachment["_metadata"] = metadata
                    attachments.append(attachment)
                except (
                    OSError,
                    RuntimeError,
                    subprocess.SubprocessError,
                    ValueError,
                    httpx.HTTPError,
                ):
                    attachments.append({
                        "attachment_id": str(attachment_id),
                        "original_file_name": None,
                        "content_type": None,
                        "evidence_type": "PROCESSING_FAILED",
                        "original_url": None,
                        "photos": [],
                        "processing_error": "Official attachment could not be processed.",
                    })

            result = _aggregate_response(attachments)
            if result["status"] != "PROCESSING_FAILED":
                active_cache.save_response(project_id, result)
            return result
        except (OSError, ValueError, httpx.HTTPError):
            return _empty_response("PROCESSING_FAILED")
        finally:
            if owns_client:
                active_client.close()


def get_cached_asset(project_id, asset_path, cache=None):
    """Returns a cached evidence file path, or None if it is unavailable."""
    active_cache = cache or _CACHE
    return active_cache.resolve_asset(project_id, asset_path)
