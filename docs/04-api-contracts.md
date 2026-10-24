# 04 — API Contracts

Base URL in local development: `http://localhost:8000`.

## 1. `GET /health`

Purpose: confirm the API process is running.

Example response:
```json
{"status":"ok"}
```

This endpoint does not prove GitHub, Bandit, or OpenAI are reachable.

## 2. `POST /api/scans`

Request:
```json
{
  "repository_url": "https://github.com/OWNER/REPOSITORY",
  "ref": null
}
```

Response (`202 Accepted` recommended if processing asynchronously; `200 OK` is acceptable for a simple synchronous first slice):
```json
{
  "scan_id": "scan_example",
  "status": "queued",
  "repository": {"owner": "OWNER", "name": "REPOSITORY", "ref": "default"}
}
```

Validation errors should use a consistent shape:
```json
{"error":{"code":"INVALID_REPOSITORY_URL","message":"Provide a supported public GitHub repository URL."}}
```

## 3. `GET /api/scans/{scan_id}`

Example response:
```json
{
  "scan_id": "scan_example",
  "status": "completed_with_warnings",
  "coverage": {
    "files_discovered": 18,
    "files_analyzed": 14,
    "files_skipped": 4,
    "warnings": ["Four files exceeded configured limits or were unsupported."]
  },
  "stages": {
    "repository": "completed",
    "bandit": "completed",
    "ai_review": "completed",
    "triage": "completed"
  },
  "findings": []
}
```

Suggested scan statuses: `queued`, `running`, `completed`, `completed_with_warnings`, `failed`.

## 4. `POST /api/scans/{scan_id}/fixes`

Request:
```json
{
  "finding_id": "finding_example"
}
```

Response:
```json
{
  "proposal_id": "proposal_example",
  "finding_id": "finding_example",
  "status": "proposed",
  "explanation": "Why the proposed change may address the finding.",
  "target_path": "src/example.py",
  "diff": "--- a/src/example.py\n+++ b/src/example.py\n...",
  "review_notes": ["Review the change before using it."]
}
```

The backend must validate that the finding exists and that the target path is within the scanned repository content.

## 5. `POST /api/scans/{scan_id}/rescan`

Request:
```json
{"proposal_id":"proposal_example"}
```

Response:
```json
{
  "verification_id": "verification_example",
  "proposal_id": "proposal_example",
  "status": "resolved",
  "checks_run": ["bandit"],
  "evidence": "The matching Bandit rule was not reported in the proposed changed file.",
  "limitations": ["Only the proposed changed content and configured checks were evaluated."]
}
```

Allowed verification statuses: `resolved`, `still_detected`, `unverified`.

## 6. Finding schema

```json
{
  "finding_id": "finding_example",
  "source_type": "bandit",
  "rule_id": "BXXX",
  "title": "Finding title",
  "message": "Tool or review message",
  "severity": "medium",
  "priority": "high",
  "confidence": "medium",
  "file_path": "src/example.py",
  "line_start": 10,
  "line_end": 12,
  "evidence": "Small relevant snippet, redacted if necessary",
  "rationale": "Why it matters and why it received this priority",
  "manual_review_required": true
}
```

Use `null` for unavailable locations or confidence; do not invent them. `source_type` values should include `bandit`, `ai_review`, and optionally `combined` only when provenance is preserved.

## 7. API implementation rules

- Validate with Pydantic models.
- Use appropriate HTTP status codes.
- Never return stack traces or secrets to the browser.
- Include a request/scan identifier in errors where possible.
- Do not return `completed` if required stages failed.
- Document endpoints in FastAPI's generated OpenAPI page.
