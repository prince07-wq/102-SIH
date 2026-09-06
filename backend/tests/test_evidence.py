"""
tests/test_evidence.py
======================
Focused tests for on-demand official project evidence and local caching.
"""

import base64
import json
import os

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import evidence_service
from app.services.evidence_cache import LocalEvidenceCache


client = TestClient(app)


class FakeResponse:
    """Small HTTPX-like response used by the evidence service tests."""

    def __init__(self, payload):
        self.payload = payload
        self.text = "" if payload is None else json.dumps(payload)
        self.content = self.text.encode("utf-8")

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeOfficialClient:
    """Returns configured attachment-list and attachment-file responses."""

    def __init__(self, attachment_ids, attachment_payload=None):
        self.attachment_ids = attachment_ids
        self.attachment_payload = attachment_payload
        self.calls = []

    def post(self, url, json):
        self.calls.append((url, json))
        if url == evidence_service.ATTACHMENT_IDS_URL:
            return FakeResponse(self.attachment_ids)
        return FakeResponse(self.attachment_payload)


def test_photo_gps_attachment_is_processed_on_demand_and_cached(tmp_path, monkeypatch):
    cache = LocalEvidenceCache(str(tmp_path))
    monkeypatch.setattr(
        evidence_service.project_service,
        "get_project_official_work_ids",
        lambda project_id: [58590],
    )
    attachment_payload = {
        "FILE_NAME": "WC_0001.pdf",
        "FILE_DATA": base64.b64encode(b"%PDF-1.4 test attachment").decode("ascii"),
    }
    official_client = FakeOfficialClient(
        [{
            "FILE_NAME": ["WC.pdf"],
            "ATTACH_ID": ["1416112.1462689"],
        }],
        attachment_payload,
    )
    extractor_calls = []

    def fake_extractor(pdf_path, output_dir):
        extractor_calls.append((pdf_path, output_dir))
        os.makedirs(output_dir, exist_ok=True)
        photo_path = os.path.join(output_dir, "page_001_project_photo_001.jpg")
        with open(photo_path, "wb") as f:
            f.write(b"\xff\xd8\xffmock-photo")
        return {
            "has_project_photo": True,
            "photo_path": photo_path,
            "latitude": 18.5204,
            "longitude": 73.8567,
            "location_text": "Example location",
            "timestamp": "2026-09-05T10:00:00+05:30",
            "source_page": 1,
        }

    result = evidence_service.get_project_evidence(
        "133166",
        cache=cache,
        client=official_client,
        extractor_runner=fake_extractor,
    )

    assert result["status"] == "PHOTO_GPS"
    assert result["evidence_type"] == "PHOTO_GPS"
    assert result["has_project_photo"] is True
    assert result["latitude"] == 18.5204
    assert result["longitude"] == 73.8567
    assert result["original_file_name"] == "WC_0001.pdf"
    assert len(result["attachments"]) == 1
    assert len(result["photos"]) == 1
    assert len(extractor_calls) == 1
    assert official_client.calls[0][1] == {
        "json": {
            "FLAG": "3",
            "WORK_ID": "58590",
        }
    }
    assert official_client.calls[1][1] == {"id": "1416112.1462689"}

    cached = evidence_service.get_project_evidence(
        "133166",
        cache=cache,
        client=FakeOfficialClient(None),
        extractor_runner=fake_extractor,
    )
    assert cached["cached"] is True
    assert cached["status"] == "PHOTO_GPS"
    assert len(extractor_calls) == 1


def test_no_attachment_response_is_cached(tmp_path, monkeypatch):
    cache = LocalEvidenceCache(str(tmp_path))
    monkeypatch.setattr(
        evidence_service.project_service,
        "get_project_official_work_ids",
        lambda project_id: [58590, 58591],
    )
    official_client = FakeOfficialClient([])

    result = evidence_service.get_project_evidence(
        "1", cache=cache, client=official_client
    )
    cached = evidence_service.get_project_evidence(
        "1", cache=cache, client=FakeOfficialClient(None)
    )

    assert result == {
        "status": "NO_ATTACHMENT",
        "attachments": [],
        "has_project_photo": False,
        "photos": [],
        "latitude": None,
        "longitude": None,
        "location_text": None,
        "timestamp": None,
        "original_file_name": None,
        "evidence_type": "NO_ATTACHMENT",
        "cached": False,
    }
    assert cached["status"] == "NO_ATTACHMENT"
    assert cached["cached"] is True
    assert [call[1]["json"]["WORK_ID"] for call in official_client.calls] == [
        "58590",
        "58591",
    ]


def test_missing_work_id_returns_no_attachment_without_network(tmp_path, monkeypatch):
    cache = LocalEvidenceCache(str(tmp_path))
    monkeypatch.setattr(
        evidence_service.project_service,
        "get_project_official_work_ids",
        lambda project_id: [],
    )

    result = evidence_service.get_project_evidence(
        "1", cache=cache, client=FakeOfficialClient(None)
    )
    assert result["status"] == "NO_ATTACHMENT"


def test_processing_failure_is_retryable_and_not_cached(tmp_path, monkeypatch):
    cache = LocalEvidenceCache(str(tmp_path))
    monkeypatch.setattr(
        evidence_service.project_service,
        "get_project_official_work_ids",
        lambda project_id: [58590],
    )

    class FailingClient:
        def post(self, url, json):
            raise httpx.ConnectError("official service unavailable")

    result = evidence_service.get_project_evidence(
        "1", cache=cache, client=FailingClient()
    )
    assert result["status"] == "PROCESSING_FAILED"
    assert cache.load_response("1") is None


def test_evidence_route_contract_and_unknown_project(monkeypatch):
    normalized = {
        "status": "DOCUMENT_ONLY",
        "attachments": [{
            "attachment_id": "1",
            "original_file_name": "official.pdf",
            "content_type": "application/pdf",
            "evidence_type": "DOCUMENT_ONLY",
            "original_url": "/api/projects/133166/evidence/files/attachment_001/official.pdf",
            "photos": [],
            "processing_error": None,
        }],
        "has_project_photo": False,
        "photos": [],
        "latitude": None,
        "longitude": None,
        "location_text": None,
        "timestamp": None,
        "original_file_name": "official.pdf",
        "evidence_type": "DOCUMENT_ONLY",
        "cached": False,
    }
    monkeypatch.setattr(
        evidence_service, "get_project_evidence", lambda project_id: normalized
    )
    response = client.get("/api/projects/133166/evidence")
    assert response.status_code == 200
    assert response.json() == normalized

    def not_found(project_id):
        raise evidence_service.ProjectNotFoundError(project_id)

    monkeypatch.setattr(evidence_service, "get_project_evidence", not_found)
    response = client.get("/api/projects/does-not-exist/evidence")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


def test_cache_asset_resolution_rejects_traversal(tmp_path):
    cache = LocalEvidenceCache(str(tmp_path))
    attachment_dir = cache.attachment_directory("1", "attachment_001")
    os.makedirs(attachment_dir, exist_ok=True)
    filepath = os.path.join(attachment_dir, "official.pdf")
    with open(filepath, "wb") as f:
        f.write(b"%PDF-1.4")

    assert cache.resolve_asset("1", "attachment_001/official.pdf") == filepath
    assert cache.resolve_asset("1", "../outside.pdf") is None


def test_version_one_no_attachment_cache_is_invalidated(tmp_path):
    cache = LocalEvidenceCache(str(tmp_path))
    project_dir = cache.project_directory("133312")
    os.makedirs(project_dir, exist_ok=True)
    with open(os.path.join(project_dir, "response.json"), "w", encoding="utf-8") as f:
        json.dump({
            "cache_version": 1,
            "response": {
                "status": "NO_ATTACHMENT",
                "cached": False,
            },
        }, f)

    assert cache.load_response("133312") is None


def test_cached_original_document_is_served_inline(tmp_path, monkeypatch):
    filepath = os.path.join(tmp_path, "official record.pdf")
    with open(filepath, "wb") as f:
        f.write(b"%PDF-1.4 official")
    monkeypatch.setattr(
        evidence_service.project_service,
        "get_project_by_id",
        lambda project_id: object(),
    )
    monkeypatch.setattr(
        evidence_service,
        "get_cached_asset",
        lambda project_id, asset_path: filepath,
    )

    response = client.get(
        "/api/projects/1/evidence/files/attachment_001/official%20record.pdf"
    )
    assert response.status_code == 200
    assert response.content == b"%PDF-1.4 official"
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].startswith("inline;")


def test_real_pdf_extractor_integration_when_fixture_is_supplied(tmp_path, monkeypatch):
    """Runs the existing extractor against an opt-in local attachment fixture."""
    pdf_path = os.environ.get("MPLADS_EVIDENCE_TEST_PDF")
    if not pdf_path:
        pytest.skip("Set MPLADS_EVIDENCE_TEST_PDF for the local PDF integration test")

    with open(pdf_path, "rb") as f:
        encoded_pdf = base64.b64encode(f.read()).decode("ascii")
    cache = LocalEvidenceCache(str(tmp_path))
    monkeypatch.setattr(
        evidence_service.project_service,
        "get_project_official_work_ids",
        lambda project_id: [58590],
    )
    official_client = FakeOfficialClient(
        [{"ATTACH_ID": "local-fixture"}],
        {
            "FILE_NAME": os.path.basename(pdf_path),
            "FILE_DATA": encoded_pdf,
        },
    )

    result = evidence_service.get_project_evidence(
        "133166",
        cache=cache,
        client=official_client,
    )

    assert result["status"] == "PHOTO_GPS"
    assert result["has_project_photo"] is True
    assert result["latitude"] is not None
    assert result["longitude"] is not None
    photo_url = result["photos"][0]["url"]
    asset_path = photo_url.split("/evidence/files/", 1)[1]
    assert cache.resolve_asset("133166", asset_path) is not None
