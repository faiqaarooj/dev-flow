from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import zipfile
import logging
from pathlib import Path
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("devflow.repo")


class RepositoryService:
    def validate_repository_url(self, repository_url: str) -> tuple[str, str, str | None]:
        if not repository_url or not isinstance(repository_url, str):
            raise ValueError("Provide a supported public GitHub repository URL.")

        cleaned = repository_url.strip()
        if cleaned.startswith("http://"):
            raise ValueError("Provide a supported public GitHub repository URL with HTTPS.")
        if not cleaned.startswith("https://"):
            cleaned = "https://" + cleaned

        cleaned = re.sub(r"^https://www\.github\.com", "https://github.com", cleaned)

        # Support tree or blob urls e.g. https://github.com/owner/repo/tree/branch-name
        m_tree = re.match(
            r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)/(?:tree|blob)/([^/]+)/?$",
            cleaned,
        )
        if m_tree:
            owner, repo, ref = m_tree.groups()
            repo = re.sub(r"\.git$", "", repo)
            self._validate_identifiers(owner, repo)
            return owner, repo, ref

        # Support standard repo urls e.g. https://github.com/owner/repo or https://github.com/owner/repo.git
        m_repo = re.match(
            r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$",
            cleaned,
        )
        if m_repo:
            owner, repo = m_repo.groups()
            repo = re.sub(r"\.git$", "", repo)
            self._validate_identifiers(owner, repo)
            return owner, repo, None

        raise ValueError(
            "Provide a supported public GitHub repository URL (e.g., https://github.com/owner/repo)."
        )

    def _validate_identifiers(self, owner: str, repo: str) -> None:
        if owner in (".", "..") or repo in (".", "..") or "/" in owner or "/" in repo:
            raise ValueError("Invalid repository identifier.")
        if not re.match(r"^[A-Za-z0-9_.-]+$", owner) or not re.match(r"^[A-Za-z0-9_.-]+$", repo):
            raise ValueError("Repository identifier contains unsupported characters.")

    def download_repo_archive(
        self, owner: str, repo: str, target_dir: Path, ref: str | None = None
    ) -> bool:
        """Downloads and extracts the repository archive via HTTP, without requiring git CLI."""
        target_ref = ref if (ref and ref not in ("default", "HEAD")) else "HEAD"
        urls_to_try = [
            f"https://github.com/{owner}/{repo}/archive/{target_ref}.zip",
            f"https://github.com/{owner}/{repo}/archive/refs/heads/{target_ref}.zip",
            f"https://github.com/{owner}/{repo}/archive/HEAD.zip",
        ]
        headers = {"User-Agent": "DevFlow-AI-Security-Auditor/1.0"}

        for url in urls_to_try:
            try:
                with httpx.Client(follow_redirects=True, timeout=35.0, headers=headers) as client:
                    resp = client.get(url)
                    if resp.status_code == 200 and resp.content:
                        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                            # Github archives wrap files under a root folder (e.g. repo-ref/)
                            top_dirs = {name.split("/")[0] for name in z.namelist() if "/" in name}
                            prefix = list(top_dirs)[0] + "/" if len(top_dirs) == 1 else ""
                            for member in z.infolist():
                                if member.is_dir():
                                    continue
                                rel_name = (
                                    member.filename[len(prefix):]
                                    if prefix and member.filename.startswith(prefix)
                                    else member.filename
                                )
                                # Prevent directory traversal / zip slip
                                if not rel_name or rel_name.startswith(("/", "\\")) or ".." in rel_name.split("/"):
                                    continue
                                out_path = target_dir / rel_name
                                out_path.parent.mkdir(parents=True, exist_ok=True)
                                with z.open(member) as src, open(out_path, "wb") as dst:
                                    dst.write(src.read())
                        logger.info("Successfully fetched repository archive via HTTP: %s", url)
                        return True
                    if resp.status_code == 404:
                        continue
                    if resp.status_code in (403, 429):
                        logger.warning("GitHub archive rate limited (status %s): %s", resp.status_code, url)
                        break
            except Exception as exc:
                logger.warning("Failed archive download attempt from %s: %s", url, exc)
                continue

        return False

    def clone_and_prepare_repo(
        self, owner: str, repo: str, target_dir: Path, ref: str | None = None
    ) -> dict[str, Any]:
        retrieval_success = False
        last_error = ""

        # Step 1: Download repository archive directly via HTTP (fastest, stateless, no git CLI dependencies)
        logger.info("Attempting HTTP repository archive download for %s/%s", owner, repo)
        try:
            retrieval_success = self.download_repo_archive(owner, repo, target_dir, ref)
        except Exception as exc:
            logger.warning("HTTP archive download raised: %s", exc)
            last_error = str(exc)

        # Step 2: Fall back to git clone if archive download did not succeed and git binary is present
        if not retrieval_success:
            git_path = shutil.which("git")
            if git_path:
                logger.info("Falling back to git clone for %s/%s", owner, repo)
                repo_url = f"https://github.com/{owner}/{repo}.git"
                cmd = [
                    git_path,
                    "-c", "filter.lfs.smudge=cat",
                    "-c", "filter.lfs.clean=cat",
                    "-c", "filter.lfs.process=",
                    "-c", "filter.lfs.required=false",
                    "clone",
                    "--depth", "1",
                ]
                if ref and ref not in ("default", "HEAD"):
                    cmd.extend(["--branch", ref])
                cmd.extend([repo_url, str(target_dir)])

                env = {
                    **os.environ,
                    "GIT_TERMINAL_PROMPT": "0",
                    "GIT_ASKPASS": "echo",
                }

                try:
                    completed = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=25,
                        check=False,
                        env=env,
                    )
                    if completed.returncode == 0:
                        retrieval_success = True
                    else:
                        last_error = completed.stderr.strip() or completed.stdout.strip()
                        logger.warning("Git clone exited %s: %s", completed.returncode, last_error)
                except Exception as exc:
                    last_error = str(exc)
                    logger.warning("Git clone failed with exception: %s", exc)

        if not retrieval_success:
            lower_err = last_error.lower()
            if (
                "remote: repository not found" in lower_err
                or "could not read username" in lower_err
                or "authentication failed" in lower_err
                or "fatal: repository" in lower_err
                or "not found" in lower_err
            ):
                raise ValueError(
                    f"Repository '{owner}/{repo}' could not be accessed. Please confirm the repository is public and the URL is correct."
                )
            if "timed out" in lower_err:
                raise RuntimeError(f"Cloning repository '{owner}/{repo}' timed out.")
            raise RuntimeError(
                f"Failed to inspect repository '{owner}/{repo}'. Please check repository access permissions."
            )

        # Step 3: Scan files in target repository
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

        warnings = skipped[:10]
        if total_discovered == 0:
            warnings.append(
                "No Python (.py) source files were detected in this repository. DevFlow security rules inspect Python code."
            )

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
            "warnings": warnings,
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
