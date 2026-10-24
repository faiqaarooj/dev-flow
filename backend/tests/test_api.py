import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_connection, init_db


class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        init_db()
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_create_scan_invalid_url(self):
        response = self.client.post("/api/scans", json={"repository_url": "https://notgithub.com/abc/def"})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)

    def test_create_scan_valid_shape(self):
        response = self.client.post("/api/scans", json={"repository_url": "https://github.com/octocat/Hello-World"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("scan_id", data)
        self.assertIn("status", data)
        self.assertEqual(data["repository"]["owner"], "octocat")
        self.assertEqual(data["repository"]["name"], "Hello-World")

        scan_id = data["scan_id"]
        # Retrieve scan
        get_res = self.client.get(f"/api/scans/{scan_id}")
        self.assertEqual(get_res.status_code, 200)
        scan_data = get_res.json()
        self.assertEqual(scan_data["scan_id"], scan_id)
        self.assertIn("status", scan_data)
        self.assertIn("stages", scan_data)
        self.assertIn("findings", scan_data)

    def test_get_nonexistent_scan(self):
        response = self.client.get("/api/scans/nonexistent_scan_999")
        self.assertEqual(response.status_code, 404)

    def test_list_scans(self):
        response = self.client.get("/api/scans")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_fix_proposal_and_rescan(self):
        # Insert mock scan and finding
        scan_id = "test_scan_mock"
        finding_id = "test_finding_mock"
        with get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO scans (scan_id, repository_url, owner, repository_name, status) VALUES (?, ?, ?, ?, ?)",
                (scan_id, "https://github.com/test/repo", "test", "repo", "completed"),
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO findings (
                    finding_id, scan_id, source_type, rule_id, title, message, severity, file_path, line_start, evidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding_id,
                    scan_id,
                    "bandit",
                    "B101",
                    "Use of assert detected",
                    "Assert detected",
                    "low",
                    "src/app.py",
                    10,
                    "assert user is not None",
                ),
            )
            conn.commit()

        # Request fix proposal
        fix_res = self.client.post(f"/api/scans/{scan_id}/fixes", json={"finding_id": finding_id})
        self.assertEqual(fix_res.status_code, 200)
        fix_data = fix_res.json()
        self.assertIn("proposal_id", fix_data)
        self.assertEqual(fix_data["finding_id"], finding_id)
        self.assertIn("diff", fix_data)
        self.assertEqual(fix_data["status"], "proposed")

        proposal_id = fix_data["proposal_id"]

        # Request rescan / verification
        rescan_res = self.client.post(
            f"/api/scans/{scan_id}/rescan",
            json={"proposal_id": proposal_id, "finding_id": finding_id, "patch": fix_data["diff"]},
        )
        self.assertEqual(rescan_res.status_code, 200)
        rescan_data = rescan_res.json()
        self.assertIn("status", rescan_data)
        self.assertEqual(rescan_data["status"], "resolved")
        self.assertIn("bandit", rescan_data["checks_run"])

        # Test patch download
        patch_res = self.client.get(f"/api/scans/{scan_id}/fixes/{proposal_id}/download")
        self.assertEqual(patch_res.status_code, 200)
        self.assertIn("fix_", patch_res.headers.get("content-disposition", ""))
        self.assertIn("--- a/src/app.py", patch_res.text)

        # Test scan report download
        report_res = self.client.get(f"/api/scans/{scan_id}/export/report")
        self.assertEqual(report_res.status_code, 200)
        self.assertIn("DevFlow AI — Security Audit Report", report_res.text)
        self.assertIn("content-disposition", report_res.headers)

    def test_download_prd_endpoint(self):
        response = self.client.get("/api/docs/prd")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/markdown", response.headers.get("content-type", ""))
        self.assertIn("DevFlow-AI-PRD.md", response.headers.get("content-disposition", ""))
        self.assertIn("DevFlow AI", response.text)

    def test_download_system_design_endpoint(self):
        response = self.client.get("/api/docs/system-design")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/markdown", response.headers.get("content-type", ""))
        self.assertIn("DevFlow-AI-System-Design.md", response.headers.get("content-disposition", ""))
        self.assertIn("Architecture", response.text)


if __name__ == "__main__":
    unittest.main()
