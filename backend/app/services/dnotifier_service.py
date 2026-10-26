from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("devflow.dnotifier")


class DNotifierService:
    """Real-life integration client for DNotifier notification gateway."""

    def __init__(self) -> None:
        self.app_id = settings.dnotifier_app_id
        self.app_secret = settings.dnotifier_app_secret
        self.api_url = (settings.dnotifier_api_url or "https://api.dnotifier.com").rstrip("/")
        self.enabled = bool(self.app_id and self.app_secret)

    def _generate_signature(self, payload_bytes: bytes) -> str:
        if not self.app_secret:
            return ""
        return hmac.new(
            self.app_secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

    async def send_scan_alert(
        self,
        scan_id: str,
        repository_url: str,
        findings_count: int,
        status: str,
        summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Dispatch real-life notification payload to DNotifier endpoint."""
        if not self.enabled:
            logger.info("DNotifier integration skipped: credentials not provided.")
            return {"status": "skipped", "reason": "credentials_not_configured"}

        payload = {
            "app_id": self.app_id,
            "event": "security.scan_completed",
            "timestamp": int(time.time()),
            "data": {
                "scan_id": scan_id,
                "repository_url": repository_url,
                "findings_count": findings_count,
                "status": status,
                "summary": summary or {},
            },
        }

        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = self._generate_signature(payload_bytes)

        headers = {
            "Content-Type": "application/json",
            "X-DNotifier-App-Id": self.app_id or "",
            "X-DNotifier-Signature": signature,
        }

        url = f"{self.api_url}/v1/alerts"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, content=payload_bytes, headers=headers)
                if response.status_code in (200, 201, 202):
                    logger.info("DNotifier alert dispatched successfully for scan %s", scan_id)
                    return {"status": "delivered", "status_code": response.status_code}
                logger.warning(
                    "DNotifier returned HTTP %d: %s",
                    response.status_code,
                    response.text[:200],
                )
                return {"status": "unacknowledged", "status_code": response.status_code}
        except Exception as exc:
            logger.warning("DNotifier alert dispatch failed (non-blocking): %s", exc)
            return {"status": "fallback", "error": str(exc)}
