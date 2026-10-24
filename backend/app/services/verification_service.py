from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

from app.services.bandit_service import BanditService


class VerificationService:
    def __init__(self) -> None:
        self.bandit_service = BanditService()

    def evaluate(self, original_finding: dict[str, Any], re_scan_results: dict[str, Any]) -> dict[str, Any]:
        findings = re_scan_results.get("results") or []
        target_rule = str(original_finding.get("rule_id") or "").strip()

        matches = []
        for item in findings:
            item_test_id = item.get("test_id") or item.get("issue", {}).get("test_id")
            if target_rule and item_test_id == target_rule:
                matches.append(item)

        if not matches:
            return {
                "status": "resolved",
                "checks_run": ["bandit"],
                "evidence": f"Re-scan verified that Bandit rule {target_rule or 'reported issue'} was eliminated.",
                "limitations": ["Only the configured static security checks and provided code were evaluated."],
            }

        return {
            "status": "still_detected",
            "checks_run": ["bandit"],
            "evidence": f"The Bandit rule {target_rule} was still detected after evaluating the proposed patch.",
            "limitations": ["This check is scoped to the analyzed code snippet and Bandit static rule set."],
        }

    def verify_patch(self, original_finding: dict[str, Any], patch_text: str | None) -> dict[str, Any]:
        if not patch_text or not patch_text.strip():
            return {
                "status": "unverified",
                "checks_run": ["bandit"],
                "evidence": "No patch content was provided for verification.",
                "limitations": ["Verification requires patch diff or replacement code."],
            }

        rule_id = original_finding.get("rule_id")
        # Extract lines from unified diff or replacement code
        code_lines = []
        for line in patch_text.splitlines():
            if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
                continue
            if line.startswith("+"):
                code_lines.append(line[1:])
            elif not line.startswith("-"):
                code_lines.append(line)

        test_code = "\n".join(code_lines).strip()
        if not test_code:
            test_code = patch_text.strip()

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "patched_module.py"
            file_path.write_text(test_code, encoding="utf-8")

            try:
                bandit_output = self.bandit_service.run_bandit_on_dir(tmp_dir)
                return self.evaluate(original_finding, bandit_output)
            except Exception as exc:
                return {
                    "status": "unverified",
                    "checks_run": ["bandit"],
                    "evidence": f"Verification scanner error: {exc}",
                    "limitations": ["Bandit could not parse or analyze the patched content."],
                }
