# 04 — API Contracts & Protocol Specification

**Version:** 2.2 — Production Certified Specification  
**Status:** Implemented & Verified  
**Lead Designer & Software Engineer:** Faiqa Arooj (Bugfolio, SE-Tech Society, Google Developer Groups)  
**Target:** DevFlow AI REST API Engine (`backend/app/api/routes.py`)  

---

## 1. Overview & Base URLs

- **Local Development:** `http://localhost:8000`
- **Cloud Deployment:** Same-origin relative path (`/api/*`) via Vercel edge reverse proxy.
- **Protocol:** HTTP/1.1 & HTTP/2 JSON REST with Markdown attachment streaming.
- **OpenAPI / Swagger Spec:** Automatically exposed at `/docs` and `/openapi.json`.

---

## 2. Health & System Status

### `GET /health`
Validates that the ASGI application worker and database connections are operational.

**Response (`200 OK`):**
```json
{
  "status": "ok"
}
```

---

## 3. Security Auditing Endpoints

### `POST /api/scans`
Submits a public GitHub repository for automated auditing. Operates synchronously when `VERCEL=1` (serverless execution) or asynchronously via background task when running locally.

**Request:**
```json
{
  "repository_url": "https://github.com/octocat/Hello-World",
  "ref": "main"
}
```

**Response (`200 OK` / `202 Accepted`):**
```json
{
  "scan_id": "scan_4a1b8c2d",
  "status": "queued",
  "repository": {
    "owner": "octocat",
    "name": "Hello-World",
    "ref": "main"
  }
}
```

**Validation Error (`400 Bad Request`):**
```json
{
  "detail": "Provide a supported public GitHub repository URL like https://github.com/owner/repository"
}
```

---

### `GET /api/scans`
Retrieves a paginated list of historical security scans from the persistent SQLite database.

**Response (`200 OK`):**
```json
[
  {
    "scan_id": "scan_4a1b8c2d",
    "repository_url": "https://github.com/octocat/Hello-World",
    "status": "completed",
    "created_at": "2026-10-25T14:30:00",
    "completed_at": "2026-10-25T14:30:04",
    "findings_count": 2
  }
]
```

---

### `GET /api/scans/{scan_id}`
Retrieves deep diagnostic telemetry, stage execution logs, file coverage statistics, and normalized findings for a specific scan.

**Response (`200 OK`):**
```json
{
  "scan_id": "scan_4a1b8c2d",
  "repository_url": "https://github.com/octocat/Hello-World",
  "status": "completed",
  "coverage": {
    "files_discovered": 12,
    "files_analyzed": 12,
    "files_skipped": 0,
    "total_bytes": 84200,
    "warnings": []
  },
  "stages": {
    "repository": "completed",
    "bandit": "completed",
    "ai_review": "completed",
    "triage": "completed"
  },
  "findings": [
    {
      "finding_id": "finding_a89c31b2",
      "source_type": "bandit",
      "rule_id": "B104",
      "title": "hardcoded_bind_all_interfaces",
      "message": "Possible binding to all network interfaces (0.0.0.0).",
      "severity": "medium",
      "priority": "high",
      "priority_rationale": "High priority: Exposure to untrusted networks",
      "confidence": "medium",
      "file_path": "server.py",
      "line_start": 42,
      "line_end": 42,
      "evidence": "s.bind(('0.0.0.0', 8000))",
      "manual_review_required": false
    }
  ]
}
```

---

## 4. Remediation & Sandbox Verification Endpoints

### `POST /api/scans/{scan_id}/fixes`
Synthesizes an atomic patch proposal for a designated finding using the 3-tier AI engine (Gemini 2.0 Flash -> GPT-4o-mini -> deterministic AST heuristics).

**Request:**
```json
{
  "finding_id": "finding_a89c31b2"
}
```

**Response (`200 OK`):**
```json
{
  "proposal_id": "proposal_7f2d1e04",
  "finding_id": "finding_a89c31b2",
  "status": "proposed",
  "explanation": "Replaces wildcard network interface binding (0.0.0.0) with localhost loopback (127.0.0.1) to prevent unintended external network exposure.",
  "target_path": "server.py",
  "diff": "--- a/server.py\n+++ b/server.py\n@@ -42,1 +42,1 @@\n-s.bind(('0.0.0.0', 8000))\n+s.bind(('127.0.0.1', 8000))\n",
  "review_notes": [
    "Verify whether external network binding was intentionally required for reverse proxy setups."
  ]
}
```

---

### `POST /api/scans/{scan_id}/rescan`
Executes automated sandbox verification. Applies the proposed patch in an ephemeral workspace and re-scans using Bandit AST to verify suppression of the vulnerability.

**Request:**
```json
{
  "proposal_id": "proposal_7f2d1e04"
}
```

**Response (`200 OK`):**
```json
{
  "verification_id": "verification_9d1a4e82",
  "proposal_id": "proposal_7f2d1e04",
  "status": "resolved",
  "checks_run": ["bandit_ast_rescan"],
  "before_count": 1,
  "after_count": 0,
  "evidence": "Bandit rule B104 was suppressed in the patched sandbox file.",
  "limitations": [
    "Verification tests AST lint suppression only; runtime unit test suite was not executed."
  ]
}
```

---

### `GET /api/scans/{scan_id}/fixes/{proposal_id}/download`
Streams the verified unified diff as a downloadable `.diff` patch file.

**Response Headers:**
```http
Content-Type: text/x-diff
Content-Disposition: attachment; filename="patch_proposal_7f2d1e04.diff"
```

---

## 5. Deliverables & Documentation Endpoints

### `GET /api/scans/{scan_id}/export/report`
Generates and downloads a complete Markdown security audit report for the scan.

### `GET /api/docs/prd`
Streams the official Product Requirements Document ([`hackathon.md`](file:///Users/apple/Desktop/hackathon/hackathon.md)).

### `GET /api/docs/system-design`
Streams the comprehensive System Design specification ([`SYSTEM_DESIGN.md`](file:///Users/apple/Desktop/hackathon/SYSTEM_DESIGN.md)).

### `GET /api/docs/audit-report`
Streams the certified Security Audit Report ([`SECURITY_AUDIT_REPORT.md`](file:///Users/apple/Desktop/hackathon/SECURITY_AUDIT_REPORT.md)).
