from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

import httpx

from app.config import settings


SUPPORTED_GITHUB_REPO_RE = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:/)?(?:\.git)?/?$"
)


class RepositoryService:
    def validate_repository_url(self, repository_url: str) -> tuple[str, str, str | None]:
        if not repository_url or not isinstance(repository_url, str):
            raise ValueError("Provide a supported public GitHub repository URL.")

        cleaned = repository_url.strip()
        match = SUPPORTED_GITHUB_REPO_RE.match(cleaned)
        if not match:
            raise ValueError("Provide a supported public GitHub repository URL (e.g., https://github.com/owner/repo).")

        owner, repo = match.groups()
        # Prevent traversal or unsafe identifiers
        if owner in (".", "..") or repo in (".", "..") or "/" in owner or "/" in repo:
            raise ValueError("Invalid repository identifier.")

        return owner, repo, None

    def clone_and_prepare_repo(
        self, owner: str, repo: str, target_dir: Path, ref: str | None = None
    ) -> dict[str, Any]:
        repo_url = f"https://github.com/{owner}/{repo}.git"
        cmd = ["git", "clone", "--depth", "1"]
        if ref and ref not in ("default", "HEAD"):
            cmd.extend(["--branch", ref])
        cmd.extend([repo_url, str(target_dir)])

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Cloning repository timed out after 45 seconds.") from exc

        if completed.returncode != 0:
            error_msg = completed.stderr.strip() or completed.stdout.strip() or "Repository not accessible."
            if "not found" in error_msg.lower() or "authentication failed" in error_msg.lower():
                raise ValueError(f"Repository {owner}/{repo} could not be found or is private.")
            raise RuntimeError(f"Failed to clone repository: {error_msg}")

        # Scan files in cloned repository
        eligible_files = []
        skipped = []
        total_bytes = 0

        all_python_files = sorted(target_dir.rglob("*.py"))
        total_discovered = len(all_python_files)

        for path in all_python_files:
            rel_path = path.relative_to(target_dir).as_posix()

            # Skip hidden folders / files (e.g., .git)
            parts = rel_path.split("/")
            if any(part.startswith(".") for part in parts):
                skipped.append(f"Skipped hidden path: {rel_path}")
                continue

            # Limit file count
            if len(eligible_files) >= settings.max_repo_files:
                skipped.append(f"Skipped due to file-count limit: {rel_path}")
                continue

            try:
                size = path.stat().st_size
            except OSError:
                size = 0

            # Limit individual file size
            if size > settings.max_file_bytes:
                skipped.append(f"Skipped oversized file ({size} bytes): {rel_path}")
                continue

            # Limit total analyzed bytes
            if total_bytes + size > settings.max_repo_bytes:
                skipped.append(f"Skipped due to total-byte limit: {rel_path}")
                break

            total_bytes += size
            eligible_files.append(rel_path)

        return {
            "owner": owner,
            "repo": repo,
            "ref": ref or "default",
            "files": eligible_files,
            "skipped": skipped,
            "files_discovered": total_discovered,
            "files_analyzed": len(eligible_files),
            "files_skipped": len(skipped),
            "total_bytes": total_bytes,
            "warnings": skipped[:10],
        }

    async def fetch_repo_files(self, owner: str, repo: str, ref: str | None = None) -> dict[str, Any]:
        headers = {"Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient(timeout=20.0) as client:
            tree_url = f"{settings.github_api_base_url}/repos/{owner}/{repo}/git/trees/{ref or 'HEAD'}?recursive=1"
            response = await client.get(tree_url, headers=headers)
            response.raise_for_status()
            payload = response.json()

            items = payload.get("tree", [])
            python_files = []
            skipped = []
            total_bytes = 0

            for item in items:
                path = item.get("path")
                if not path or item.get("type") != "blob":
                    continue
                if not path.endswith(".py"):
                    continue
                if path.startswith("."):
                    skipped.append(f"Skipped hidden path: {path}")
                    continue
                if len(python_files) >= settings.max_repo_files:
                    skipped.append(f"Skipped due to file-count limit: {path}")
                    continue
                size = int(item.get("size") or 0)
                if size > settings.max_file_bytes:
                    skipped.append(f"Skipped oversized file: {path}")
                    continue
                total_bytes += size
                if total_bytes > settings.max_repo_bytes:
                    skipped.append(f"Skipped due to total-byte limit: {path}")
                    break
                python_files.append(path)

            return {
                "owner": owner,
                "repo": repo,
                "ref": ref or "default",
                "files": python_files,
                "skipped": skipped,
                "files_discovered": len(python_files),
                "files_skipped": len(skipped),
                "total_bytes": total_bytes,
            }
