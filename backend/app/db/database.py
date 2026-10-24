from __future__ import annotations

import sqlite3
import os
from pathlib import Path

from app.config import settings


if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/devflow.db")
else:
    DB_PATH = Path(settings.database_path)
    if not DB_PATH.is_absolute():
        DB_PATH = (Path(__file__).resolve().parent.parent.parent / settings.database_path).resolve()


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                repository_url TEXT NOT NULL,
                owner TEXT,
                repository_name TEXT,
                ref TEXT,
                status TEXT NOT NULL,
                coverage_json TEXT,
                error_code TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS findings (
                finding_id TEXT PRIMARY KEY,
                scan_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                rule_id TEXT,
                title TEXT,
                message TEXT,
                severity TEXT,
                priority TEXT,
                priority_rationale TEXT,
                confidence TEXT,
                file_path TEXT,
                line_start INTEGER,
                line_end INTEGER,
                evidence TEXT,
                manual_review_required INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(scan_id) REFERENCES scans(scan_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patch_proposals (
                proposal_id TEXT PRIMARY KEY,
                scan_id TEXT NOT NULL,
                finding_id TEXT NOT NULL,
                target_path TEXT NOT NULL,
                explanation TEXT,
                diff TEXT,
                review_notes TEXT,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(scan_id) REFERENCES scans(scan_id),
                FOREIGN KEY(finding_id) REFERENCES findings(finding_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS verifications (
                verification_id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL,
                scan_id TEXT NOT NULL,
                status TEXT NOT NULL,
                checks_run TEXT,
                evidence TEXT,
                limitations TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(proposal_id) REFERENCES patch_proposals(proposal_id),
                FOREIGN KEY(scan_id) REFERENCES scans(scan_id)
            )
            """
        )
        conn.commit()
