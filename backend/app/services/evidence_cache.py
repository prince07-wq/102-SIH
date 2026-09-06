"""
services/evidence_cache.py
==========================
Local development cache for on-demand official project evidence.

The evidence service depends only on this small cache interface so a future
object-storage or database-backed implementation can replace it without
changing attachment download or PDF processing logic.
"""

import hashlib
import json
import os
import re


_SERVICE_DIR = os.path.dirname(__file__)
DEFAULT_CACHE_ROOT = os.path.abspath(
    os.path.join(
        _SERVICE_DIR,
        "..",
        "..",
        "..",
        "data",
        "processed",
        "evidence_cache",
    )
)

CACHE_VERSION = 2


class LocalEvidenceCache:
    """Stores normalized responses and attachment assets on the local disk."""

    def __init__(self, root=DEFAULT_CACHE_ROOT):
        self.root = os.path.abspath(root)

    def project_directory(self, project_id):
        """Returns a traversal-safe, stable directory for one project ID."""
        project_text = str(project_id)
        readable = re.sub(r"[^A-Za-z0-9_.-]+", "_", project_text).strip("._")
        readable = readable[:50] or "project"
        digest = hashlib.sha256(project_text.encode("utf-8")).hexdigest()[:12]
        return os.path.join(self.root, f"{readable}-{digest}")

    def attachment_directory(self, project_id, attachment_key):
        """Returns an attachment directory beneath its project cache."""
        if not re.fullmatch(r"attachment_\d{3}", str(attachment_key)):
            raise ValueError("Invalid cached attachment key")
        return os.path.join(self.project_directory(project_id), attachment_key)

    def load_response(self, project_id):
        """Loads a compatible cached response, or returns None on a cache miss."""
        cache_path = os.path.join(self.project_directory(project_id), "response.json")
        if not os.path.isfile(cache_path):
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

        if cached.get("cache_version") != CACHE_VERSION:
            return None
        response = cached.get("response")
        if not isinstance(response, dict):
            return None
        response["cached"] = True
        return response

    def save_response(self, project_id, response):
        """Atomically stores one normalized response."""
        project_dir = self.project_directory(project_id)
        os.makedirs(project_dir, exist_ok=True)
        cache_path = os.path.join(project_dir, "response.json")
        temporary_path = f"{cache_path}.tmp"
        stored_response = dict(response)
        stored_response["cached"] = False
        payload = {
            "cache_version": CACHE_VERSION,
            "response": stored_response,
        }
        with open(temporary_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(temporary_path, cache_path)

    def save_attachment(self, project_id, attachment_key, filename, content):
        """Stores one downloaded official file and returns its absolute path."""
        attachment_dir = self.attachment_directory(project_id, attachment_key)
        os.makedirs(attachment_dir, exist_ok=True)
        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename in {".", ".."}:
            raise ValueError("Invalid attachment filename")
        filepath = os.path.join(attachment_dir, safe_filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return filepath

    def resolve_asset(self, project_id, asset_path):
        """Resolves a public cache-relative asset path without traversal."""
        project_dir = self.project_directory(project_id)
        candidate = os.path.abspath(os.path.join(project_dir, asset_path))
        if os.path.commonpath([project_dir, candidate]) != project_dir:
            return None
        if not os.path.isfile(candidate):
            return None
        return candidate
