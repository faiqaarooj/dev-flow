# 01 — Requirements Specification

**Version:** 2.1 — Hardened Production & Deployment Edition  
**Lead Designer & Engineer:** Faiqa Arooj (Bugfolio, SE-Tech Society, Google Developer Groups)  
**Target:** DevFlow AI Multi-Agent Security Auditing & Verified Remediation Platform  

---

## 1. Functional Requirements

| ID | Requirement | Priority | Acceptance Criterion |
|---|---|:---:|---|
| **FR-01** | Accept & Validate Public GitHub Repository URL | P0 | Valid URL (`https://github.com/{owner}/{repo}`) creates scan session; malformed URLs receive 400 Bad Request with `INVALID_REPOSITORY_URL`. |
| **FR-02** | Dual-Strategy Repository Ingestion | P0 | Primary method streams HTTP archive zipball (`/archive/HEAD.zip`) with streaming Zip-Slip defense (`os.path.commonpath`). Secondary method falls back to shallow Git clone (`git clone --depth 1`) with 25s timeout. |
| **FR-03** | Bounded Repository Inspection & Coverage | P0 | Max 200 files, max 250 KB per file, max 5 MB total volume. Response records total files, analyzed files, skipped files, and byte counts. |
| **FR-04** | AST Static Security Analysis (Bandit v1.7.9) | P0 | AST visitor inspection across all Python modules. Findings preserve rule ID (e.g. `B104`, `B108`, `B110`, `B603`), severity, confidence, lines, and code snippets. Subprocesses enforce `shell=False`. |
| **FR-05** | OWASP Top 10 (2021) & MITRE CWE Mapping | P0 | Every finding maps to an OWASP category (e.g. A01 Broken Access Control, A03 Injection, A05 Security Misconfiguration) and a MITRE CWE (e.g. CWE-200, CWE-377, CWE-390, CWE-78). |
| **FR-06** | Multi-Engine AI Review & Triage | P0 | Native integration with Google Gemini 2.0 Flash (`google-genai` / REST) and OpenAI GPT-4o-mini (`openai`). Deterministic offline rule-based heuristic triage when AI keys are omitted. |
| **FR-07** | Automated Remediation Patch Synthesis | P0 | Generates targeted unified diff patches (`.diff`) explaining root cause and resolution. Viewable side-by-side in UI and downloadable via `/api/scans/{scan_id}/fixes/{proposal_id}/download`. |
| **FR-08** | Isolated Sandbox Re-Scan Verification | P0 | Verifier applies candidate patch in an isolated temporary directory sandbox, re-runs Bandit AST analysis, and confirms status: `resolved`, `still_detected`, or `unverified`. |
| **FR-09** | Explicit Diagnostic Error Contract (Non-Zero Invariant) | P0 | Failed, partial, or timed-out scans must NEVER return a clean bill of health or 0 findings. They must transition to `status="failed"` with `error_code` and `error_message`. |
| **FR-10** | Serverless Execution Adaptation (Vercel Support) | P0 | Orchestrator detects serverless runtime (`VERCEL=1`) where background task threads freeze upon HTTP response; executes scan synchronously within platform request limits. |
| **FR-11** | Publication-Grade Markdown Audit Report Export | P0 | Dynamically generates publication-grade Markdown audit report via `/api/scans/{scan_id}/export/report` with Executive Summary, OWASP/CWE matrices, evidence, and verification logs. |
| **FR-12** | Direct Project Deliverables Downloads | P0 | Dedicated backend endpoints for PRD (`/api/docs/prd`), System Design (`/api/docs/system-design`), and Benchmark Audit Report (`/api/docs/audit-report`). |
| **FR-13** | Deterministic Toolchain & Pinned Lockfile | P0 | Pinned `pnpm@9.15.9` across `packageManager` and lockfile version `9.0` with `--frozen-lockfile` to prevent `ERR_PNPM_OUTDATED_LOCKFILE`. |
| **FR-14** | DNotifier Integration (Capability-Gated) | Conditional | Implemented only where official API endpoints are verified; fallback to internal notification ledger. |

---

## 2. Non-Functional Requirements

- **Strict Passive Security:** Never execute, import, or install submitted repository code. Subprocess commands use discrete token lists with `shell=False`.
- **Zip-Slip & Path Traversal Prevention:** Inspect and canonicalize all archive entries with `os.path.commonpath` checks prior to writing to disk.
- **Resource Guardrails:** Enforce timeouts (25s cloning, 60s total scan), file size caps (250 KB/file), and total footprint caps (5 MB).
- **Non-Zero Error Invariant:** Scanner failures and network issues must be surfaced as explicit error states; failures never map to zero findings.
- **Credential Isolation:** Keep AI API keys and secrets strictly on the server; never expose them to client bundles or browser logs.
- **Aesthetic Excellence:** Adhere to minimalist, high-contrast dark theme (`#1a1a1a`) with vibrant yellow (`#f4c453`) accents and fluid animations.

---

## 3. User Stories

- **As a Developer:** I can paste a public GitHub URL and receive a publication-grade security audit in under 10 seconds.
- **As a DevSecOps Engineer:** I can view OWASP Top 10 and MITRE CWE classifications for every finding to satisfy compliance requirements.
- **As a Junior Engineer:** I can request an automated remediation patch, inspect the code diff, and see proof from a fresh sandbox re-scan that the vulnerability was eliminated.
- **As an Open-Source Maintainer:** I can download the official PRD, System Design, and Audit Report as clean Markdown files (`.md`) to share with contributors.
- **As a Deployment Engineer:** I can deploy DevFlow AI to Vercel without encountering PNPM lockfile mismatch errors or serverless background task freezes.

---

## 4. Explicit Product Language

- **Use:** "No findings were reported by the configured checks in the 22 analyzed Python files."
- **Do NOT Use:** "Your repository is completely secure and free of vulnerabilities."
- **Use:** "AI-suggested observation; manual security review recommended."
- **Do NOT Use:** "Vulnerability confirmed exploitable by AI." (unless verified by static evidence or deterministic testing).
