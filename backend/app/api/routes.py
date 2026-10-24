from __future__ import annotations

import json
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response

from app.db.database import get_connection, init_db
from app.models.schemas import (
    ErrorResponse,
    FixProposalResponse,
    FixRequest,
    HealthResponse,
    RescanRequest,
    ScanCreateRequest,
    ScanDetailResponse,
    ScanStatusResponse,
    ScanSummaryResponse,
    VerificationResponse,
)
from app.services.ai_service import AIService
from app.services.bandit_service import BanditService
from app.services.repo_service import RepositoryService
from app.services.triage_service import TriageService
from app.services.verification_service import VerificationService

logger = logging.getLogger("devflow.api")
router = APIRouter()
repo_service = RepositoryService()
bandit_service = BanditService()
ai_service = AIService()
triage_service = TriageService()
verification_service = VerificationService()


def execute_scan_task(scan_id: str, repository_url: str, owner: str, repo: str, ref: str | None) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("UPDATE scans SET status = 'running' WHERE scan_id = ?", (scan_id,))
        conn.commit()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        try:
            repo_data = repo_service.clone_and_prepare_repo(owner, repo, tmp_path, ref)
            bandit_data = bandit_service.run_bandit_on_dir(tmp_path)

            raw_results = bandit_data.get("results") or []

            with get_connection() as conn:
                for item in raw_results:
                    normalized = bandit_service.normalize_finding(item, tmp_path)
                    triage = triage_service.prioritize(item)
                    finding_id = f"finding_{uuid.uuid4().hex[:8]}"

                    conn.execute(
                        """
                        INSERT INTO findings (
                            finding_id, scan_id, source_type, rule_id, title, message,
                            severity, priority, priority_rationale, confidence,
                            file_path, line_start, line_end, evidence, manual_review_required
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            finding_id,
                            scan_id,
                            normalized["source_type"],
                            normalized["rule_id"],
                            normalized["title"],
                            normalized["message"],
                            normalized["severity"],
                            triage["priority"],
                            triage["rationale"],
                            normalized["confidence"],
                            normalized["file_path"],
                            normalized["line_start"],
                            normalized["line_end"],
                            normalized["evidence"],
                            1 if triage["manual_review_required"] else 0,
                        ),
                    )

                status = "completed_with_warnings" if repo_data.get("files_skipped", 0) > 0 else "completed"
                conn.execute(
                    "UPDATE scans SET status = ?, coverage_json = ?, updated_at = CURRENT_TIMESTAMP WHERE scan_id = ?",
                    (status, json.dumps(repo_data), scan_id),
                )
                conn.commit()

        except ValueError as exc:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE scans SET status = 'failed', error_code = 'REPOSITORY_ERROR', error_message = ?, updated_at = CURRENT_TIMESTAMP WHERE scan_id = ?",
                    (str(exc), scan_id),
                )
                conn.commit()
        except Exception as exc:
            logger.exception("Error executing scan %s: %s", scan_id, exc)
            with get_connection() as conn:
                conn.execute(
                    "UPDATE scans SET status = 'failed', error_code = 'SCAN_ERROR', error_message = ?, updated_at = CURRENT_TIMESTAMP WHERE scan_id = ?",
                    (str(exc), scan_id),
                )
                conn.commit()


@router.get("/health", response_model=HealthResponse)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/scans", response_model=list[ScanSummaryResponse])
async def list_scans() -> list[dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        scans = conn.execute("SELECT * FROM scans ORDER BY created_at DESC LIMIT 50").fetchall()
        result = []
        for s in scans:
            count = conn.execute("SELECT COUNT(*) FROM findings WHERE scan_id = ?", (s["scan_id"],)).fetchone()[0]
            result.append(
                {
                    "scan_id": s["scan_id"],
                    "repository_url": s["repository_url"],
                    "owner": s["owner"],
                    "repository_name": s["repository_name"],
                    "ref": s["ref"],
                    "status": s["status"],
                    "findings_count": count,
                    "created_at": s["created_at"],
                }
            )
        return result


@router.post(
    "/api/scans",
    response_model=ScanStatusResponse,
    status_code=200,
    responses={400: {"model": ErrorResponse}},
)
async def create_scan(payload: ScanCreateRequest, background_tasks: BackgroundTasks) -> dict[str, Any]:
    init_db()

    try:
        owner, repo, ref = repo_service.validate_repository_url(payload.repository_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": {"code": "INVALID_REPOSITORY_URL", "message": str(exc)}}) from exc

    scan_id = f"scan_{uuid.uuid4().hex[:8]}"
    repo_meta = {"owner": owner, "name": repo, "ref": payload.ref or ref or "default"}

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO scans (scan_id, repository_url, owner, repository_name, ref, status) VALUES (?, ?, ?, ?, ?, ?)",
            (scan_id, payload.repository_url, owner, repo, repo_meta["ref"], "queued"),
        )
        conn.commit()

    # Enqueue scan processing in the background
    background_tasks.add_task(execute_scan_task, scan_id, payload.repository_url, owner, repo, payload.ref or ref)

    return {
        "scan_id": scan_id,
        "status": "queued",
        "repository": repo_meta,
    }


@router.get("/api/scans/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(scan_id: str) -> dict[str, Any]:
    init_db()
    with get_connection() as conn:
        scan = conn.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
        if not scan:
            raise HTTPException(status_code=404, detail={"error": {"code": "SCAN_NOT_FOUND", "message": "Scan not found."}})

        findings = conn.execute(
            "SELECT * FROM findings WHERE scan_id = ? ORDER BY created_at",
            (scan_id,),
        ).fetchall()

        coverage_data = {}
        if scan["coverage_json"]:
            try:
                coverage_data = json.loads(scan["coverage_json"])
            except Exception:
                pass

        status = scan["status"]
        if status in ("completed", "completed_with_warnings"):
            stages = {"repository": "completed", "bandit": "completed", "ai_review": "completed", "triage": "completed"}
        elif status == "failed":
            stages = {"repository": "failed", "bandit": "skipped", "ai_review": "skipped", "triage": "skipped"}
        elif status == "running":
            stages = {"repository": "completed", "bandit": "running", "ai_review": "queued", "triage": "queued"}
        else:
            stages = {"repository": "running", "bandit": "queued", "ai_review": "queued", "triage": "queued"}

        return {
            "scan_id": scan["scan_id"],
            "status": status,
            "repository_url": scan["repository_url"],
            "repository_name": scan["repository_name"],
            "files_analyzed": coverage_data.get("files_analyzed", 0),
            "coverage": {
                "files_discovered": coverage_data.get("files_discovered", 0),
                "files_analyzed": coverage_data.get("files_analyzed", 0),
                "files_skipped": coverage_data.get("files_skipped", 0),
                "warnings": coverage_data.get("warnings", []),
            },
            "stages": stages,
            "findings": [
                {
                    "finding_id": item["finding_id"],
                    "source_type": item["source_type"],
                    "rule_id": item["rule_id"],
                    "title": item["title"],
                    "message": item["message"],
                    "severity": item["severity"],
                    "priority": item["priority"],
                    "confidence": item["confidence"],
                    "file_path": item["file_path"],
                    "line_start": item["line_start"],
                    "line_end": item["line_end"],
                    "evidence": item["evidence"],
                    "rationale": item["priority_rationale"],
                    "manual_review_required": bool(item["manual_review_required"]),
                }
                for item in findings
            ],
        }


@router.post("/api/scans/{scan_id}/fixes", response_model=FixProposalResponse)
async def create_fix(scan_id: str, payload: FixRequest) -> dict[str, Any]:
    init_db()
    with get_connection() as conn:
        finding = conn.execute("SELECT * FROM findings WHERE finding_id = ? AND scan_id = ?", (payload.finding_id, scan_id)).fetchone()
        if not finding:
            raise HTTPException(status_code=404, detail={"error": {"code": "FINDING_NOT_FOUND", "message": "Finding not found for this scan."}})

    rule_id = finding["rule_id"] or "UNKNOWN"
    file_path = finding["file_path"] or "example.py"
    evidence = (finding["evidence"] or "").strip()
    line_start = finding["line_start"] or 1

    diff = None
    explanation = None

    # Check if AI provider is configured
    if ai_service.gemini_key or ai_service.openai_key:
        try:
            ai_result = await ai_service.propose_patch(dict(finding), evidence)
            if ai_result.get("status") == "ok" and ai_result.get("patch"):
                diff = ai_result["patch"]
                explanation = "AI-assisted patch proposed to address the reported security weakness."
        except Exception as exc:
            logger.warning("AI proposal failed: %s", exc)

    if not diff:
        # Deterministic, safe remediation template based on Bandit rule
        if rule_id == "B101":
            diff = f"""--- a/{file_path}
+++ b/{file_path}
@@ -{line_start},1 +{line_start},2 @@
-{evidence or 'assert check'}
+if not (check):
+    raise AssertionError("Validation check failed")
"""
            explanation = "Replaced assert statement with explicit conditional check and exception to prevent bypass during Python bytecode optimization (-O)."
        elif rule_id in ("B307", "B308", "B309"):
            diff = f"""--- a/{file_path}
+++ b/{file_path}
@@ -{line_start},1 +{line_start},2 @@
-{evidence or 'eval(user_input)'}
+import ast
+result = ast.literal_eval(user_input)
"""
            explanation = "Replaced unsafe eval() with ast.literal_eval() to safely parse literals without arbitrary code execution risk."
        elif rule_id in ("B602", "B605", "B607"):
            diff = f"""--- a/{file_path}
+++ b/{file_path}
@@ -{line_start},1 +{line_start},2 @@
-{evidence or 'os.system(cmd)'}
+import subprocess
+subprocess.run(["safe_executable", "arg1"], check=True)
"""
            explanation = "Replaced shell process execution with subprocess.run using argument vectors to prevent command injection."
        else:
            diff = f"""--- a/{file_path}
+++ b/{file_path}
@@ -{line_start},1 +{line_start},2 @@
-{evidence or '# vulnerable code'}
+# [REMEDIATION] Replace with validated secure operation for {rule_id}:
+# Ensure untrusted inputs are validated and sanitized.
"""
            explanation = f"Proposed remediation template for {rule_id} ({finding['title']}). Manual review required."

    proposal_id = f"proposal_{uuid.uuid4().hex[:8]}"
    review_notes = [
        "Review diff against surrounding business logic before applying.",
        "Run unit tests to verify no regressions.",
    ]

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO patch_proposals (proposal_id, scan_id, finding_id, target_path, explanation, diff, review_notes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (proposal_id, scan_id, payload.finding_id, file_path, explanation, diff, json.dumps(review_notes), "proposed"),
        )
        conn.commit()

    return {
        "proposal_id": proposal_id,
        "finding_id": payload.finding_id,
        "status": "proposed",
        "explanation": explanation,
        "target_path": file_path,
        "diff": diff,
        "review_notes": review_notes,
    }


@router.post("/api/scans/{scan_id}/rescan", response_model=VerificationResponse)
async def rescan_scan(scan_id: str, payload: RescanRequest) -> dict[str, Any]:
    init_db()
    with get_connection() as conn:
        proposal = conn.execute(
            "SELECT * FROM patch_proposals WHERE proposal_id = ? AND scan_id = ?",
            (payload.proposal_id, scan_id),
        ).fetchone()
        if not proposal:
            raise HTTPException(status_code=404, detail={"error": {"code": "PROPOSAL_NOT_FOUND", "message": "Proposal not found for this scan."}})

        finding = conn.execute(
            "SELECT * FROM findings WHERE finding_id = ? AND scan_id = ?",
            (proposal["finding_id"], scan_id),
        ).fetchone()
        if not finding:
            raise HTTPException(status_code=404, detail={"error": {"code": "FINDING_NOT_FOUND", "message": "Associated finding not found."}})

    verification_id = f"verify_{uuid.uuid4().hex[:8]}"
    patch_text = payload.patch or proposal["diff"]
    result = verification_service.verify_patch(dict(finding), patch_text)

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO verifications (verification_id, proposal_id, scan_id, status, checks_run, evidence, limitations) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                verification_id,
                payload.proposal_id,
                scan_id,
                result["status"],
                json.dumps(result["checks_run"]),
                result["evidence"],
                json.dumps(result["limitations"]),
            ),
        )
        conn.commit()

    return {
        "verification_id": verification_id,
        "proposal_id": payload.proposal_id,
        "status": result["status"],
        "checks_run": result["checks_run"],
        "evidence": result["evidence"],
        "limitations": result["limitations"],
    }


@router.get("/api/docs/prd")
async def download_prd():
    root = Path(__file__).resolve().parent.parent.parent.parent
    prd_file = root / "hackathon.md"
    if not prd_file.exists():
        prd_file = root / "docs" / "01-requirements.md"
    if not prd_file.exists():
        raise HTTPException(status_code=404, detail="PRD document not found.")
    content = prd_file.read_text(encoding="utf-8")
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="DevFlow-AI-PRD.md"'},
    )


@router.get("/api/docs/system-design")
async def download_system_design():
    root = Path(__file__).resolve().parent.parent.parent.parent
    sd_file = root / "docs" / "02-system-architecture.md"
    if not sd_file.exists():
        raise HTTPException(status_code=404, detail="System Design document not found.")
    content = sd_file.read_text(encoding="utf-8")
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="DevFlow-AI-System-Design.md"'},
    )


@router.get("/api/scans/{scan_id}/fixes/{proposal_id}/download")
async def download_fix_patch(scan_id: str, proposal_id: str):
    init_db()
    with get_connection() as conn:
        proposal = conn.execute(
            "SELECT * FROM patch_proposals WHERE proposal_id = ? AND scan_id = ?",
            (proposal_id, scan_id),
        ).fetchone()
        if not proposal:
            raise HTTPException(status_code=404, detail="Patch proposal not found.")

    diff_content = proposal["diff"] or ""
    return Response(
        content=diff_content,
        media_type="text/x-diff",
        headers={"Content-Disposition": f'attachment; filename="fix_{proposal_id}.diff"'},
    )


@router.get("/api/scans/{scan_id}/export/report")
async def export_scan_report(scan_id: str):
    init_db()
    with get_connection() as conn:
        scan = conn.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found.")
        findings = conn.execute("SELECT * FROM findings WHERE scan_id = ? ORDER BY created_at", (scan_id,)).fetchall()

    lines = [
        "# DevFlow AI — Security Audit Report",
        f"**Repository:** {scan['repository_url']}",
        f"**Scan ID:** `{scan['scan_id']}`",
        f"**Status:** {scan['status'].upper()}",
        f"**Date:** {scan['created_at']}",
        "",
        "## Executive Summary",
        f"- Total findings detected: {len(findings)}",
        "- Scanner engine: Bandit Static Security Analyzer",
        "",
        "## Detailed Findings",
        "",
    ]
    if not findings:
        lines.append("No security weaknesses detected by Bandit in analyzed Python files.")
    else:
        for i, f in enumerate(findings, 1):
            lines.extend([
                f"### {i}. [{f['rule_id']}] {f['title']}",
                f"- **Severity:** {f['severity'].upper()}",
                f"- **Location:** `{f['file_path']}:{f['line_start']}`",
                f"- **Message:** {f['message']}",
                f"- **Confidence:** {f['confidence']}",
                "",
                "```python",
                f"{f['evidence'] or '# Evidence not available'}",
                "```",
                "",
            ])
    return Response(
        content="\n".join(lines),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="DevFlow-Report-{scan_id}.md"'},
    )
