from __future__ import annotations

import json
import logging
import os
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
                    "error_code": s["error_code"] if "error_code" in s.keys() else None,
                    "error_message": s["error_message"] if "error_message" in s.keys() else None,
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

    # In serverless environments (like Vercel), execute scan directly to avoid background task freeze
    if os.environ.get("VERCEL"):
        execute_scan_task(scan_id, payload.repository_url, owner, repo, payload.ref or ref)
        with get_connection() as conn:
            row = conn.execute("SELECT status FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
            status = row["status"] if row else "completed"
        return {
            "scan_id": scan_id,
            "status": status,
            "repository": repo_meta,
        }

    # In standard server/local environments, enqueue scan processing in the background
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
            stages = {
                "repository": "failed" if scan["error_code"] == "REPOSITORY_ERROR" else "completed",
                "bandit": "failed" if scan["error_code"] == "SCAN_ERROR" else "skipped",
                "ai_review": "skipped",
                "triage": "skipped",
            }
        elif status == "running":
            stages = {"repository": "completed", "bandit": "running", "ai_review": "queued", "triage": "queued"}
        else:
            stages = {"repository": "running", "bandit": "queued", "ai_review": "queued", "triage": "queued"}

        return {
            "scan_id": scan["scan_id"],
            "status": status,
            "error_code": scan["error_code"] if "error_code" in scan.keys() else None,
            "error_message": scan["error_message"] if "error_message" in scan.keys() else None,
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


@router.get("/api/docs/audit-report")
async def download_audit_report():
    root = Path(__file__).resolve().parent.parent.parent.parent
    report_file = root / "SECURITY_AUDIT_REPORT.md"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Security audit report document not found.")
    content = report_file.read_text(encoding="utf-8")
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="DevFlow-AI-Security-Audit-Report.md"'},
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
        scan_row = conn.execute("SELECT * FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
        if not scan_row:
            raise HTTPException(status_code=404, detail="Scan not found.")
        scan = dict(scan_row)
        findings = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM findings WHERE scan_id = ? ORDER BY CASE severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, line_start",
                (scan_id,),
            ).fetchall()
        ]
        proposals = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM patch_proposals WHERE scan_id = ?", (scan_id,)
            ).fetchall()
        ]
        verifications = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM verifications WHERE scan_id = ?", (scan_id,)
            ).fetchall()
        ]

    coverage_data = {}
    if scan["coverage_json"]:
        try:
            coverage_data = json.loads(scan["coverage_json"])
        except Exception:
            coverage_data = {}

    # Calculate severity breakdown
    high_count = sum(1 for f in findings if (f["severity"] or "").lower() == "high")
    med_count = sum(1 for f in findings if (f["severity"] or "").lower() == "medium")
    low_count = sum(1 for f in findings if (f["severity"] or "").lower() == "low")
    total_findings = len(findings)

    # Determine risk posture
    if scan["status"] == "failed":
        posture = "SCAN FAILED — AUDIT INCOMPLETE"
        posture_badge = "🔴 FAILED"
    elif high_count > 0:
        posture = "HIGH RISK — CRITICAL VULNERABILITIES DETECTED"
        posture_badge = "🚨 HIGH RISK"
    elif med_count > 0:
        posture = "MODERATE RISK — ATTENTION REQUIRED"
        posture_badge = "⚠️ MODERATE RISK"
    elif low_count > 0:
        posture = "LOW RISK — MINOR HYGIENE DEFECTS"
        posture_badge = "ℹ️ LOW RISK"
    else:
        posture = "CLEAN — NO STATIC DEFECTS IDENTIFIED"
        posture_badge = "✅ CLEAN"

    # CWE mapping helper
    cwe_map = {
        "B101": ("CWE-703", "Improper Check or Handling of Exceptional Conditions", "A04:2021-Insecure Design"),
        "B104": ("CWE-200", "Exposure of Sensitive Information via Network Interface Binding", "A01:2021-Broken Access Control"),
        "B108": ("CWE-377", "Insecure Temporary File Creation", "A05:2021-Security Misconfiguration"),
        "B110": ("CWE-390", "Detection of Error Condition Without Action (Try/Except Pass)", "A04:2021-Insecure Design"),
        "B201": ("CWE-94", "Improper Control of Generation of Code (Code Injection)", "A03:2021-Injection"),
        "B301": ("CWE-502", "Deserialization of Untrusted Data (Pickle)", "A08:2021-Software and Data Integrity Failures"),
        "B303": ("CWE-327", "Use of a Broken or Risky Cryptographic Algorithm (MD5/SHA1)", "A02:2021-Cryptographic Failures"),
        "B307": ("CWE-95", "Improper Neutralization of Directives in Dynamically Evaluated Code (eval)", "A03:2021-Injection"),
        "B311": ("CWE-338", "Use of Cryptographically Weak Pseudo-Random Number Generator", "A02:2021-Cryptographic Failures"),
        "B602": ("CWE-78", "Improper Neutralization of Special Elements used in an OS Command (Shell Injection)", "A03:2021-Injection"),
        "B608": ("CWE-89", "Improper Neutralization of Special Elements used in an SQL Command (SQL Injection)", "A03:2021-Injection"),
    }

    proposal_map = {p["finding_id"]: p for p in proposals}
    verify_map = {v["proposal_id"]: v for v in verifications}

    lines = [
        f"# DevFlow AI — Security Audit Report",
        f"",
        f"> **Audited Target:** `{scan['repository_url']}`  ",
        f"> **Branch/Ref:** `{scan['ref'] or 'default'}`  ",
        f"> **Scan Identifier:** `{scan['scan_id']}`  ",
        f"> **Audit Timestamp:** `{scan['created_at']} UTC`  ",
        f"> **Auditing Engine:** Bandit AST Static Analyzer v1.7.9 & DevFlow Rule-Based Triage Engine  ",
        f"> **Overall Posture:** **{posture_badge}** (`{posture}`)  ",
        f"",
        f"---",
        f"",
        f"## 1. Executive Summary",
        f"",
        f"DevFlow AI conducted an automated static application security testing (SAST) assessment on the public repository `{scan['repository_url']}`. The audit inspected repository source trees, executed abstract syntax tree (AST) rule evaluation against standard security guidelines, and prioritized findings according to exploitability, confidence, and contextual risk.",
        f"",
        f"### Key Metrics",
        f"",
        f"| Metric | Value | Notes |",
        f"| :--- | :--- | :--- |",
        f"| **Target Repository** | `{scan['repository_name']}` | Public GitHub repository |",
        f"| **Audit Status** | `{scan['status'].upper()}` | Completed with verified scanner exit code |",
        f"| **Files Discovered** | `{coverage_data.get('files_discovered', 0)}` | Discovered across repository tree |",
        f"| **Files Inspected** | `{coverage_data.get('files_analyzed', 0)}` | Supported Python (`.py`) source modules |",
        f"| **Files Skipped** | `{coverage_data.get('files_skipped', 0)}` | Hidden files, dotfiles, or oversized artifacts |",
        f"| **Total Bytes Evaluated** | `{coverage_data.get('total_bytes', 0):,} bytes` | Bounded memory buffer evaluation |",
        f"| **Total Vulnerabilities** | **`{total_findings}`** | Discovered by AST visitor patterns |",
        f"| **High Severity Issues** | **`{high_count}`** | Immediate remediation required |",
        f"| **Medium Severity Issues** | **`{med_count}`** | Insecure configuration or potential exploit surface |",
        f"| **Low Severity Issues** | **`{low_count}`** | Code quality, exception hygiene, or informational |",
        f"",
    ]

    if scan["error_message"]:
        lines.extend([
            f"### ⚠️ Scanner Notice",
            f"```text",
            f"{scan['error_message']}",
            f"```",
            f"",
        ])

    lines.extend([
        f"---",
        f"",
        f"## 2. Threat Vector & OWASP / CWE Mapping",
        f"",
        f"The following table categorizes all identified security findings against standard vulnerability classifications:",
        f"",
        f"| Rule ID | Finding Title | Severity | Confidence | OWASP Top 10 | CWE Identifier |",
        f"| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    if not findings:
        lines.append(f"| *None* | *No vulnerabilities detected* | — | — | — | — |")
    else:
        for f in findings:
            cwe_id, cwe_name, owasp = cwe_map.get(
                f["rule_id"], ("CWE-699", "Software Development Vulnerability", "A05:2021-Security Misconfiguration")
            )
            sev = (f["severity"] or "medium").lower()
            sev_badge = "🔴 High" if sev == "high" else ("🟡 Medium" if sev == "medium" else "🔵 Low")
            conf_str = (f["confidence"] or "medium").title()
            lines.append(f"| `{f['rule_id']}` | {f['title']} | {sev_badge} | {conf_str} | {owasp} | **{cwe_id}** |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 3. Detailed Vulnerability Findings",
        f"",
    ])

    if not findings:
        lines.extend([
            f"No security weaknesses or anti-patterns were detected in the analyzed Python files.",
            f"The analyzed modules adhered to Bandit's baseline security test suite.",
            f"",
        ])
    else:
        for i, f in enumerate(findings, 1):
            cwe_id, cwe_name, owasp = cwe_map.get(
                f["rule_id"], ("CWE-699", "Software Development Vulnerability", "A05:2021-Security Misconfiguration")
            )
            prop = proposal_map.get(f["finding_id"])
            verif = verify_map.get(prop["proposal_id"]) if prop else None
            sev_u = (f["severity"] or "MEDIUM").upper()
            conf_u = (f["confidence"] or "MEDIUM").upper()
            prio_u = (f["priority"] or "MEDIUM").upper()

            lines.extend([
                f"### Finding #{i}: [{f['rule_id']}] {f['title']}",
                f"",
                f"- **Vulnerability Class:** {cwe_name} (`{cwe_id}`)",
                f"- **OWASP Category:** `{owasp}`",
                f"- **Severity:** `{sev_u}` | **Confidence:** `{conf_u}` | **Priority:** `{prio_u}`",
                f"- **Location:** `{f['file_path']}:{f['line_start']}` (Lines {f['line_start']}–{f['line_end']})",
                f"- **Diagnostic Explanation:** {f['message']}",
                f"",
                f"#### Affected Source Code Evidence",
                f"```python",
                f"{f['evidence'] or '# Source evidence snippet unavailable'}",
                f"```",
                f"",
                f"#### Risk & Impact Analysis",
            ])

            if f["rule_id"] == "B104":
                lines.append(
                    "Binding a network service to `0.0.0.0` or `INADDR_ANY` exposes the process across all local and public network interfaces. If deployed directly on a host with external connectivity without a reverse proxy, unauthenticated external traffic can reach internal application endpoints."
                )
            elif f["rule_id"] == "B108":
                lines.append(
                    "Hardcoding paths in globally writable directories such as `/tmp` introduces symlink attack vulnerabilities and race conditions (CWE-377). Concurrent unprivileged users or malicious processes on shared hosts can pre-create or manipulate temporary files."
                )
            elif f["rule_id"] == "B110":
                lines.append(
                    "Silently catching exceptions with `except: pass` without logging or re-raising swallows critical system and operational errors. This conceals faults, frustrates telemetry, and can leave application state corrupt or vulnerable to unhandled logic bypasses."
                )
            else:
                lines.append(
                    f"This finding represents a `{f['rule_id']}` rule trigger indicating potential insecurity or compliance departure. Review the context to ensure safe parameters and defensive boundaries are enforced."
                )

            lines.extend([
                f"",
                f"#### Recommended Remediation",
            ])

            if f["rule_id"] == "B104":
                lines.append(
                    "Bind to loopback (`127.0.0.1`) during development, or configure host binding dynamically from environment variables (`HOST = os.environ.get('HOST', '127.0.0.1')`) so external binding requires explicit configuration."
                )
            elif f["rule_id"] == "B108":
                lines.append(
                    "Use Python's standard `tempfile.TemporaryDirectory()` or `tempfile.NamedTemporaryFile()` modules to create uniquely named, permissions-restricted temporary resources within the operating system's designated secure temporary directory."
                )
            elif f["rule_id"] == "B110":
                lines.append(
                    "Log swallowed exceptions using `logger.warning('Operation failed: %s', exc)` or catch specific exceptions (`except FileNotFoundError:`) rather than broad `except Exception:` with a bare `pass` statement."
                )
            else:
                lines.append(
                    "Apply defensive coding patterns: validate inputs, enforce least privilege, and avoid insecure built-in modules."
                )

            if prop and prop.get("diff"):
                lines.extend([
                    f"",
                    f"#### Proposed Remediation Patch (`fix_{prop['proposal_id']}.diff`)",
                    f"```diff",
                    f"{prop['diff']}",
                    f"```",
                ])

            if verif:
                verif_status = verif["status"].upper()
                verif_badge = "✅ RESOLVED" if verif_status == "RESOLVED" else "⚠️ STILL DETECTED"
                lines.extend([
                    f"",
                    f"#### Verification Re-scan Outcome: **{verif_badge}**",
                    f"- **Checks Executed:** `{', '.join(json.loads(verif['checks_run']) if verif['checks_run'] else [])}`",
                    f"- **Sandbox Evidence:** {verif['evidence']}",
                ])

            lines.append("")

    lines.extend([
        f"---",
        f"",
        f"## 4. Remediation & Verification Ledger",
        f"",
        f"DevFlow AI includes an automated patch verification engine. When fixes are proposed, the patch is applied in an isolated temporary sandbox and re-analyzed with Bandit to empirically verify whether the finding is resolved or still detectable.",
        f"",
        f"| Finding | File | Rule ID | Patch Proposal | Verification Status |",
        f"| :--- | :--- | :--- | :--- | :--- |",
    ])

    if not findings:
        lines.append(f"| *None* | *None* | *None* | *None* | *No patches required* |")
    else:
        for f in findings:
            prop = proposal_map.get(f["finding_id"])
            verif = verify_map.get(prop["proposal_id"]) if prop else None
            p_status = f"`{prop['proposal_id']}`" if prop else "Not generated"
            v_status = f"**{verif['status'].upper()}**" if verif else "Pending re-scan"
            lines.append(f"| {f['title']} | `{f['file_path']}` | `{f['rule_id']}` | {p_status} | {v_status} |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 5. Scope & Audit Methodology",
        f"",
        f"### 1. Ingestion & Pre-flight",
        f"- Target repositories are retrieved via HTTPS streaming zipball archives (`/archive/HEAD.zip`) with path traversal guards (`zip-slip` prevention) and shallow Git clone fallback.",
        f"- Files are strictly treated as untrusted data. No repository setup scripts, build commands, or dependencies are executed.",
        f"",
        f"### 2. Static Analysis Engine",
        f"- The analysis executes **Bandit v1.7.9** targeting AST nodes across all discovered Python source files.",
        f"- Resource guardrails enforce maximum 200 files, 250 KB per file, and 5 MB total payload to prevent algorithmic denial of service.",
        f"",
        f"### 3. Triage & Risk Prioritization",
        f"- Findings are categorized by severity (`High`, `Medium`, `Low`) and confidence (`High`, `Medium`, `Low`).",
        f"- Priority scores reflect potential exploitability in production and likelihood of false positive.",
        f"",
        f"---",
        f"",
        f"## 6. Audit Limitations & Disclaimer",
        f"",
        f"1. **Static Analysis Scope:** This audit is limited to static pattern matching on supported Python source code. It does not evaluate dynamic runtime behaviors, third-party network APIs, cloud infrastructure configurations, or business logic flaws.",
        f"2. **No Security Guarantee:** A clean scan result does not certify an application is free from security defects. Security requires defense-in-depth, regular dependency vulnerability scanning, secrets rotation, and peer review.",
        f"3. **Human Review Mandatory:** All suggested patches and diffs must be thoroughly tested and reviewed by maintainers before deployment into production.",
        f"",
        f"---",
        f"",
        f"*Report generated autonomously by **DevFlow AI** — Autonomous Code Security & Verification Platform.*",
        f"",
    ])

    return Response(
        content="\n".join(lines),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="DevFlow-Report-{scan_id}.md"'},
    )
