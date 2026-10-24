from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from app.config import settings


class BanditService:
    def run_bandit_on_dir(self, target_dir: Path | str) -> dict[str, Any]:
        target_path = Path(target_dir)
        if not target_path.exists():
            return {"results": [], "metrics": {"_totals": {"loc": 0, "nosec": 0, "skipped_tests": 0}}}

        cmd = [sys.executable, "-m", "bandit", "-r", str(target_path), "-f", "json"]

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.bandit_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Bandit analysis timed out after {settings.bandit_timeout_seconds} seconds.") from exc

        # Bandit returns 0 (clean) or 1 (issues found). Both are normal.
        if completed.returncode not in (0, 1):
            error_details = completed.stderr.strip() or completed.stdout.strip()
            # If no files were found to scan, return empty results
            if "No files found to scan" in error_details or "no files found" in error_details.lower():
                return {"results": [], "metrics": {"_totals": {"loc": 0, "nosec": 0, "skipped_tests": 0}}}
            raise RuntimeError(f"Bandit execution failed: {error_details or 'unknown error'}")

        output = completed.stdout.strip()
        if not output:
            return {"results": [], "metrics": {"_totals": {"loc": 0, "nosec": 0, "skipped_tests": 0}}}

        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise ValueError("Bandit returned malformed JSON output.") from exc

    def normalize_finding(self, item: dict[str, Any], base_dir: Path | str) -> dict[str, Any]:
        filename = item.get("filename") or ""
        try:
            rel_path = os.path.relpath(filename, str(base_dir))
        except (ValueError, OSError):
            rel_path = filename

        test_id = item.get("test_id") or "UNKNOWN"
        test_name = (item.get("test_name") or "Security Issue").replace("_", " ").title()
        issue_text = item.get("issue_text") or "Potential security issue detected."
        severity = (item.get("issue_severity") or "medium").lower()
        confidence = (item.get("issue_confidence") or "medium").lower()

        line_num = item.get("line_number")
        line_range = item.get("line_range") or ([line_num] if line_num else [])
        line_end = line_range[-1] if line_range else line_num

        evidence = (item.get("code") or "").strip()

        return {
            "source_type": "bandit",
            "rule_id": test_id,
            "title": f"[{test_id}] {test_name}",
            "message": issue_text,
            "severity": severity,
            "confidence": confidence,
            "file_path": rel_path,
            "line_start": line_num,
            "line_end": line_end,
            "evidence": evidence,
        }

    async def run_bandit(self, file_paths: list[str]) -> dict:
        if not file_paths:
            return {
                "results": [],
                "metrics": {"_totals": {"loc": 0, "nosec": 0, "skipped_tests": 0}},
            }

        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_root = Path(tmp_dir)
            for relative_path in file_paths:
                source_file = temp_root / relative_path
                source_file.parent.mkdir(parents=True, exist_ok=True)
                source_file.write_text("", encoding="utf-8")

            return self.run_bandit_on_dir(temp_root)
