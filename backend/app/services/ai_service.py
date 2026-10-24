from __future__ import annotations

import json

import httpx
from openai import AsyncOpenAI

from app.config import settings


class AIService:
    def __init__(self) -> None:
        self.gemini_key = settings.gemini_api_key
        self.openai_key = settings.openai_api_key
        self.provider = settings.ai_provider.lower() if settings.ai_provider else "gemini"
        self.openai_client = AsyncOpenAI(api_key=self.openai_key) if self.openai_key else None

    async def _call_gemini(self, prompt: str) -> str:
        if not self.gemini_key:
            raise ValueError("Gemini API key is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini returned no candidates.")

        return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    async def _call_openai(self, prompt: str, temperature: float = 0.2) -> str:
        if not self.openai_client:
            raise ValueError("OpenAI API key is not configured.")

        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a safe and precise code security assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content or ""

    async def explain_finding(self, finding: dict) -> dict:
        prompt = (
            "You are a security review assistant. Explain the finding in plain language. "
            "Do not claim it is confirmed unless the evidence is explicit. "
            f"Finding context: {json.dumps(finding, ensure_ascii=False)}"
        )

        try:
            if self.provider == "openai":
                content = await self._call_openai(prompt, temperature=0.2)
            else:
                content = await self._call_gemini(prompt)
            return {"status": "ok", "message": content}
        except Exception as exc:
            return {"status": "unavailable", "message": f"AI provider unavailable: {exc}"}

    async def propose_patch(self, finding: dict, source_snippet: str) -> dict:
        prompt = (
            "Propose a reviewable patch for the issue described below. "
            "Return only a code patch diff or a clear replacement snippet. "
            "Do not change unrelated logic. "
            f"Finding: {json.dumps(finding, ensure_ascii=False)}\n\nSource:\n{source_snippet}"
        )

        try:
            if self.provider == "openai":
                content = await self._call_openai(prompt, temperature=0.1)
            else:
                content = await self._call_gemini(prompt)
            return {"status": "ok", "patch": content}
        except Exception as exc:
            return {"status": "unavailable", "message": f"AI provider unavailable: {exc}"}
