import tempfile
import unittest
from pathlib import Path

from app.services.bandit_service import BanditService
from app.services.repo_service import RepositoryService
from app.services.triage_service import TriageService
from app.services.verification_service import VerificationService


class TestRepositoryService(unittest.TestCase):
    def setUp(self):
        self.service = RepositoryService()

    def test_valid_github_urls(self):
        urls = [
            "https://github.com/fastapi/fastapi",
            "https://github.com/psf/requests/",
            "https://github.com/pallets/flask.git",
        ]
        for url in urls:
            owner, repo, ref = self.service.validate_repository_url(url)
            self.assertTrue(len(owner) > 0)
            self.assertTrue(len(repo) > 0)

    def test_invalid_github_urls(self):
        invalid_urls = [
            "http://github.com/owner/repo",  # unencrypted http
            "https://gitlab.com/owner/repo",  # not github
            "https://github.com/owner",  # missing repo
            "http://127.0.0.1/evil",  # ssrf loopback
            "https://github.com/../traversal",  # traversal
            "",  # empty
            "not a url",
        ]
        for url in invalid_urls:
            with self.assertRaises(ValueError):
                self.service.validate_repository_url(url)


class TestBanditService(unittest.TestCase):
    def setUp(self):
        self.bandit = BanditService()

    def test_bandit_on_clean_code(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            f = Path(tmp_dir) / "clean.py"
            f.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

            res = self.bandit.run_bandit_on_dir(tmp_dir)
            self.assertIn("results", res)
            self.assertEqual(len(res["results"]), 0)

    def test_bandit_on_vulnerable_code(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            f = Path(tmp_dir) / "vuln.py"
            f.write_text("def test():\n    assert 1 == 1\n", encoding="utf-8")

            res = self.bandit.run_bandit_on_dir(tmp_dir)
            self.assertIn("results", res)
            self.assertTrue(len(res["results"]) > 0)
            first = res["results"][0]
            self.assertEqual(first["test_id"], "B101")

            normalized = self.bandit.normalize_finding(first, tmp_dir)
            self.assertEqual(normalized["rule_id"], "B101")
            self.assertEqual(normalized["file_path"], "vuln.py")


class TestTriageService(unittest.TestCase):
    def setUp(self):
        self.triage = TriageService()

    def test_triage_priorities(self):
        high = self.triage.prioritize({"issue_severity": "HIGH"})
        self.assertEqual(high["priority"], "high")

        med = self.triage.prioritize({"issue_severity": "MEDIUM"})
        self.assertEqual(med["priority"], "medium")

        low = self.triage.prioritize({"issue_severity": "LOW"})
        self.assertEqual(low["priority"], "low")


class TestVerificationService(unittest.TestCase):
    def setUp(self):
        self.verifier = VerificationService()

    def test_verification_resolved(self):
        finding = {"rule_id": "B101", "file_path": "test.py"}
        # Patched code removes assert and uses if/raise
        patch = """--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
-assert 1 == 1
+if not (1 == 1):
+    raise AssertionError("Validation failed")
"""
        result = self.verifier.verify_patch(finding, patch)
        self.assertEqual(result["status"], "resolved")
        self.assertIn("bandit", result["checks_run"])

    def test_verification_still_detected(self):
        finding = {"rule_id": "B101", "file_path": "test.py"}
        # Patched code still has assert
        patch = """--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
-assert 1 == 1
+assert 2 == 2
"""
        result = self.verifier.verify_patch(finding, patch)
        self.assertEqual(result["status"], "still_detected")

    def test_verification_empty_patch(self):
        finding = {"rule_id": "B101"}
        result = self.verifier.verify_patch(finding, "")
        self.assertEqual(result["status"], "unverified")


if __name__ == "__main__":
    unittest.main()
