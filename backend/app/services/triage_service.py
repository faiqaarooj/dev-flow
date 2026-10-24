from __future__ import annotations


class TriageService:
    def prioritize(self, finding: dict) -> dict:
        severity = (finding.get("issue_severity") or "medium").lower()
        if severity in {"high", "critical"}:
            priority = "high"
        elif severity == "medium":
            priority = "medium"
        else:
            priority = "low"

        return {
            "priority": priority,
            "rationale": "Severity was used as a first-pass triage signal; manual review is still recommended.",
            "confidence": "medium",
            "manual_review_required": True,
        }
