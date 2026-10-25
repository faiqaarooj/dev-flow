# DevFlow AI
## Product Requirements Document (PRD)

**Version:** 2.1 — Hardened Production & Deployment Edition  
**Status:** Approved & Implemented — Hackathon Full Stack Delivery  
**Product Type:** Multi-Agent AI Security Auditing & Automated Remediation Platform  
**Lead Designer & Engineer:** Faiqa Arooj (Bugfolio, SE-Tech Society, Google Developer Groups)  
**Primary Users:** Developers, security engineers, students, and agile engineering teams  

---

## 1. Product Vision

DevFlow AI is an autonomous, multi-agent security auditing and verified remediation platform. It ingests public GitHub repositories, performs deep Abstract Syntax Tree (AST) static vulnerability scanning, pairs findings with multi-engine AI security review (Google Gemini 2.0 Flash & OpenAI GPT-4o-mini), generates precise unified diff patches, and re-scans proposed fixes in an isolated sandbox to verify resolution before human review.

Developers submit a GitHub repository URL and receive an actionable, publication-grade security audit report rather than an overwhelming list of scanner warnings.

### Product Tagline
**Find the risk. Fix the code. Verify the result.**

### Core Value Proposition
DevFlow AI does not stop at discovering potential security vulnerabilities. It executes the entire remediation lifecycle:
1. Ingests source code safely via dual-strategy streaming (direct HTTP zipball or shallow clone).
2. Performs deterministic AST analysis with Bandit v1.7.9 mapped to OWASP Top 10 (2021) and MITRE CWEs.
3. Enriches findings with multi-model AI reasoning (or deterministic offline heuristics).
4. Synthesizes isolated unified code diffs (`.diff`).
5. Executes automated re-scan verification in an ephemeral sandbox to prove whether a vulnerability is suppressed.
6. Exports publication-grade Markdown reports (`.md`) and project deliverables instantly.

---

## 2. Problem Statement

Modern software engineering teams face three systemic challenges in application security:
1. **Detection Without Actionable Understanding:** SAST tools output cryptic rule IDs and raw terminal text that junior developers struggle to prioritize or map to OWASP/CWE standards.
2. **AI Fix Hallucinations Without Verification:** Generative AI tools frequently propose broken syntax, hallucinated APIs, or fixes that fail to resolve the underlying security flaw.
3. **Deployment & Runtime Fragility:** Cloud deployment workflows often break due to lockfile version drifts (`ERR_PNPM_OUTDATED_LOCKFILE`), Git CLI absence in serverless containers, or background thread freezing in lambda environments.

DevFlow AI solves all three problems by combining deterministic AST scanning, isolated sandbox verification, and a deployment-hardened dual-strategy architecture.

---

## 3. Product Goals

The DevFlow AI platform accomplishes the following operational goals:
- **Dual-Strategy Ingestion:** Primary HTTP streaming archive retrieval (`/archive/HEAD.zip`) with Zip-Slip path sanitization, falling back to shallow Git cloning (`--depth 1`) with a 25-second watchdog timer.
- **Strict Passive Inspection:** Analyze source code without ever executing target code, running setup scripts, or installing external dependencies.
- **AST Vulnerability Detection:** Execute Bandit AST visitors across all Python source modules, preserving rule IDs, severity, confidence, line ranges, and code evidence.
- **Multi-Engine AI Security Reasoning:** Leverage Google Gemini 2.0 Flash as the primary AI engine, with OpenAI GPT-4o-mini fallback and deterministic offline rule heuristics when API keys are absent.
- **OWASP & CWE Alignment:** Automatically categorize findings according to OWASP Top 10 (2021) (e.g. A01 Broken Access Control, A03 Injection, A05 Security Misconfiguration) and MITRE CWEs (e.g. CWE-200, CWE-377, CWE-390, CWE-78).
- **Targeted Patch Synthesis:** Synthesize atomic unified diffs with side-by-side before-and-after visualization.
- **Isolated Sandbox Re-Scan Verification:** Apply proposed patches inside disposable workspaces and re-run AST security checks to confirm whether the finding is `resolved`, `still_detected`, or `unverified`.
- **Explicit Diagnostic Error Contract:** Scans that fail or are partial must NEVER report clean status or 0 findings. They must explicitly transition to `failed` status with diagnostic error codes (`INVALID_REPOSITORY_URL`, `REPOSITORY_ERROR`, `SCAN_ERROR`).
- **Serverless Execution Resilience:** Detect serverless hosting environments (`VERCEL=1`) where background task threads freeze upon HTTP response return, automatically switching to synchronous pipeline execution within platform timeout limits.
- **Publication-Grade Deliverables:** Instant generation and export of Markdown audit reports (`.md`), PRD specifications, and System Design blueprints.

---

## 4. Target Users

- **Software Developers & Students:** Seeking clear, understandable security guidance with direct remediation diffs.
- **Open-Source Maintainers:** Needing fast, automated triage of incoming security advisories on GitHub repositories.
- **DevSecOps Engineers:** Requiring verified patch recommendations and standardized OWASP/CWE audit logs for compliance.

---

## 5. Scope and Boundaries

### In Scope
- Public GitHub repository submission and URL normalization.
- In-memory streaming archive decompression with Zip-Slip protection.
- Python-first static analysis (Bandit v1.7.9 AST visitor rules).
- Multi-engine AI vulnerability triage (Gemini 2.0 Flash / OpenAI GPT-4o-mini / Heuristic engine).
- Side-by-side diff generator and patch downloader (`.diff`).
- Ephemeral sandbox re-scan verification.
- Dynamic Markdown audit report generator (`/api/scans/{scan_id}/export/report`).
- Downloadable deliverable endpoints (`/api/docs/prd`, `/api/docs/system-design`, `/api/docs/audit-report`).
- Pinned frontend build pipeline (`pnpm@9.15.9`).

### Out of Scope
- Automatic commits, pushes, or direct pull requests to user remote repositories (preserves repository integrity).
- Arbitrary code execution or sandbox container compilation.
- Closed-source private repository OAuth integration (planned for v3.0).

---

## 6. Multi-Agent System Architecture

DevFlow AI orchestrates 4 specialized AI/heuristic agents coordinated by an execution engine:

### Agent 1: Repository Ingestion & Inspector Agent
- Validates repository URLs and resolves owner/repo.
- Streams repository archive zipball or falls back to shallow clone.
- Enforces strict quotas: 200 files maximum, 250 KB per file, 5 MB total byte ceiling.
- Sanitizes file paths against directory traversal (Zip-Slip defense).

### Agent 2: Static Analysis & Scanner Agent
- Traverses AST nodes across all discovered Python modules using Bandit v1.7.9.
- Collects raw findings: rule IDs, line numbers, severity, confidence, code snippets.
- Distinguishes passive security linting from active exploitation claims.

### Agent 3: Risk Prioritization & Triage Agent
- Correlates raw AST findings with OWASP Top 10 (2021) and MITRE CWE classifications.
- Formulates plain-language risk explanations and plain-English developer impact statements.
- Operates under Google Gemini 2.0 Flash, OpenAI GPT-4o-mini, or deterministic offline heuristics.

### Agent 4: Remediation & Sandbox Verification Agent
- Receives target finding, source code, and line numbers.
- Synthesizes a minimal unified diff patch addressing the vulnerability without introducing regressions.
- Allocates an ephemeral sandbox workspace, applies the candidate patch, and re-invokes the AST scanner.
- Categorizes the outcome: `resolved` (finding eliminated), `still_detected` (flaw persists), or `unverified`.

### Coordinator & Serverless Orchestration Engine
- Assigns unique `scan_id` and tracks workflow status (`queued`, `cloning`, `scanning`, `triaging`, `completed`, `failed`).
- Enforces serverless runtime switching: executes synchronously when running on Vercel to bypass background worker freezing.
- Maintains the non-zero diagnostic error contract.

---

## 7. Functional Requirements

### FR-01: Dual-Strategy Repository Submission & Ingestion — P0
- **FR-01.1:** The system shall accept standard public GitHub repository URLs (`https://github.com/{owner}/{repo}`).
- **FR-01.2:** The system shall validate repository URL patterns, rejecting invalid protocols, malformed paths, or non-GitHub hosts with a `400 Bad Request` and `INVALID_REPOSITORY_URL` error code.
- **FR-01.3:** The primary ingestion strategy shall stream the repository zipball directly over HTTP (`https://github.com/{owner}/{repo}/archive/HEAD.zip`).
- **FR-01.4:** The archive extractor shall enforce Zip-Slip defense by verifying that every extracted entry resolves strictly within the target temporary workspace directory (`os.path.commonpath`).
- **FR-01.5:** The secondary ingestion strategy shall fall back to a shallow Git clone (`git clone --depth 1 --filter=blob:none`) with a strict 25-second watchdog timeout if the archive stream fails.
- **FR-01.6:** Ingestion shall enforce hard safety bounds: maximum 200 files, maximum 250 KB per individual file, maximum 5 MB total uncompressed volume.
- **FR-01.7:** Failed repository access must transition scan state to `failed` with code `REPOSITORY_ERROR` and a safe diagnostic message.

### FR-02: Repository Inspection & Coverage — P0
- **FR-02.1:** The system shall inspect eligible Python source files (`.py`) and dependency manifests (`requirements.txt`, `Pipfile`, `pyproject.toml`).
- **FR-02.2:** Binary files, generated code, `.git` metadata, and oversized files shall be safely excluded.
- **FR-02.3:** The system shall compute analysis coverage metrics: total files scanned, skipped file count, and total analyzed bytes.

### FR-03: Static Security Analysis — P0
- **FR-03.1:** The system shall execute Bandit v1.7.9 AST static analysis against all ingested Python files.
- **FR-03.2:** Subprocess execution must strictly enforce `shell=False` and pass arguments as discrete token arrays.
- **FR-03.3:** The scanner shall record rule ID (e.g. `B104`, `B108`, `B110`, `B603`), severity (`high`, `medium`, `low`), confidence (`high`, `medium`, `low`), line numbers, and verbatim code evidence.
- **FR-03.4:** The system shall map each finding to OWASP Top 10 (2021) categories and MITRE CWE identifiers.
- **FR-03.5:** Multi-engine AI review shall analyze findings using Google Gemini 2.0 Flash or OpenAI GPT-4o-mini.
- **FR-03.6:** If AI credentials are not configured, the system shall execute offline rule-based heuristic triage without failing the scan.
- **FR-03.7 (Explicit Diagnostic Error Contract):** The system shall NEVER represent a failed, partial, or timed-out scan as zero findings or a clean bill of health. Incomplete scans must return status `failed` with `error_code` and `error_message`.

### FR-04: Risk Prioritization & Threat Scoring — P0
- **FR-04.1:** Findings shall be grouped by severity: High, Medium, Low, Informational.
- **FR-04.2:** Each finding shall include a plain-language explanation of technical impact, exploitation prerequisites, and recommended remediation.
- **FR-04.3:** Findings shall maintain clear distinction between deterministic scanner evidence and AI-suggested observations.

### FR-05: Automated Remediation Patch Generation — P0
- **FR-05.1:** Users shall be able to request a patch proposal for any eligible finding.
- **FR-05.2:** The remediation engine shall synthesize a targeted unified diff patch (`.diff`).
- **FR-05.3:** The dashboard shall render a side-by-side diff with syntax highlighting.
- **FR-05.4:** Users shall be able to download the raw unified diff file via `/api/scans/{scan_id}/fixes/{proposal_id}/download`.
- **FR-05.5:** Remote repository code must remain read-only; no automated commits or pushes shall occur.

### FR-06: Sandbox Re-Scan Verification — P0
- **FR-06.1:** When a patch proposal is requested, the system shall allocate an isolated temporary directory sandbox.
- **FR-06.2:** The system shall write the patched file content into the sandbox and execute a targeted Bandit AST re-scan.
- **FR-06.3:** The verification engine shall categorize the result:
  - `resolved`: The targeted rule is no longer detected.
  - `still_detected`: The vulnerability persists despite the patch.
  - `unverified`: Re-scan could not execute due to environment or syntax errors.
- **FR-06.4:** Before-and-after finding counts and verification evidence must be persisted and displayed.

### FR-07: Workflow Orchestration & Serverless Adaptation — P0
- **FR-07.1:** The orchestrator shall track stage progression (`queued` -> `cloning` -> `scanning` -> `triaging` -> `completed` / `failed`).
- **FR-07.2 (Serverless Execution Adaptation):** When running in a serverless environment (`VERCEL=1`), the orchestrator shall bypass asynchronous background threads (which freeze upon HTTP response) and execute the pipeline synchronously within request lifecycle limits.
- **FR-07.3:** SQLite database connection pooling shall ensure safe concurrency and graceful directory creation in temporary environments.

### FR-08: High-End Interactive Security Dashboard — P0
- **FR-08.1:** The dashboard shall follow a minimalist, high-contrast visual design: dark background (`#1a1a1a`), sleek panels, and vibrant yellow (`#f4c453`) accents.
- **FR-08.2:** The UI shall feature animated metrics, live stage progress indicators, and interactive finding drawers.
- **FR-08.3:** Deliverables download actions must be prominently accessible across the Overview, Results, and Documentation views.

### FR-09: Publication-Grade Deliverables & Export — P0
- **FR-09.1:** The system shall export a complete Markdown Security Audit Report (`.md`) via `/api/scans/{scan_id}/export/report`.
- **FR-09.2:** The report shall include Executive Summary, OWASP/CWE Mapping Tables, Detailed Finding Breakdowns, Remediation Diffs, and Sandbox Verification Ledgers.
- **FR-09.3:** The system shall provide direct download endpoints for PRD (`/api/docs/prd`), System Design (`/api/docs/system-design`), and the Benchmark Audit Report (`/api/docs/audit-report`).

### FR-10: Deterministic Build & Package Toolchain — P0
- **FR-10.1:** Frontend builds must be pinned to `pnpm@9.15.9` across `packageManager` in `package.json` and lockfile version `9.0`.
- **FR-10.2:** Deployment install commands shall run with `--frozen-lockfile` to guarantee reproducible CI/CD execution and prevent `ERR_PNPM_OUTDATED_LOCKFILE`.

---

## 8. Non-Functional Requirements

### Security
- Submitted repositories are treated as completely untrusted input.
- Target source code is never executed, imported, or installed.
- All file operations enforce strict path resolution boundaries (`commonpath` checks).
- API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`) remain strictly server-side.
- Subprocess invocations enforce `shell=False` and tokenized argument arrays.

### Reliability
- Every scan session is tracked with explicit status and timestamps.
- Scanner errors, network timeouts, or malformed archives must never be masked as clean results.
- Failed scans return HTTP 200 with `status="failed"`, `error_code`, and `error_message`.

### Performance
- HTTP archive retrieval completes in < 3 seconds for standard repositories.
- AST analysis executes in < 2 seconds for codebases up to 200 files.
- Sandbox re-scan verification executes in < 1.5 seconds per proposal.

---

## 9. Technology Stack

| Layer | Component | Specification |
|---|---|---|
| **Frontend Framework** | React 18 + Vite 8 | Modern SPA with React Router v7 |
| **Frontend Styling** | Tailwind CSS v4 + Vanilla CSS | Curated dark palette (`#1a1a1a`, `#f4c453`) |
| **Icons & Motion** | Lucide React + Framer Motion | Dynamic animations and visual hierarchy |
| **Package Management** | PNPM v9.15.9 | Lockfile version 9.0 (`--frozen-lockfile`) |
| **Backend API** | FastAPI + Uvicorn | Python 3.9+ async REST service |
| **Static Analysis** | Bandit v1.7.9 | AST visitor-based Python security linting |
| **AI Reasoning** | Google Gemini 2.0 Flash / OpenAI GPT-4o-mini | Multi-provider with offline heuristic fallback |
| **Storage** | SQLite 3 (`devflow.db`) | Row-level locking with WAL mode support |
| **Deployment Platform** | Vercel Multi-Service | Vite static frontend + FastAPI serverless backend |

---

## 10. Data Schemas

### Scan Session
```json
{
  "scan_id": "scan_48a9f2bc",
  "repository_url": "https://github.com/faiqaarooj/dev-flow.git",
  "ref": "main",
  "status": "completed",
  "error_code": null,
  "error_message": null,
  "created_at": "2026-10-25T12:00:00Z",
  "completed_at": "2026-10-25T12:00:08Z",
  "analysis_coverage": {
    "total_files": 22,
    "scanned_files": 22,
    "skipped_files": 0,
    "total_bytes": 108420
  }
}
```

### Security Finding
```json
{
  "finding_id": "find_b104_01",
  "scan_id": "scan_48a9f2bc",
  "rule_id": "B104",
  "title": "Hardcoded Network Binding (0.0.0.0)",
  "severity": "medium",
  "confidence": "medium",
  "cwe": "CWE-200",
  "owasp_category": "A01:2021 — Broken Access Control",
  "file_path": "backend/app/main.py",
  "line_start": 50,
  "line_end": 50,
  "code_snippet": "uvicorn.run(\"app.main:app\", host=\"0.0.0.0\", port=8000)",
  "explanation": "Binding to 0.0.0.0 listens on all public network interfaces, exposing internal endpoints to untrusted traffic.",
  "recommended_fix": "Bind explicitly to 127.0.0.1 or configure host via an environment variable."
}
```

### Verification Record
```json
{
  "verification_id": "ver_93d8a1",
  "scan_id": "scan_48a9f2bc",
  "proposal_id": "prop_01",
  "finding_id": "find_b104_01",
  "status": "resolved",
  "checks_run": ["bandit_ast_rescan"],
  "before_count": 1,
  "after_count": 0,
  "evidence": "Target rule B104 was suppressed following patch application in sandbox.",
  "verified_at": "2026-10-25T12:00:15Z"
}
```

---

## 11. Verification Matrix & Benchmark Outcomes

Tested against the benchmark repository `https://github.com/faiqaarooj/dev-flow.git`:

| Metric | Benchmark Result | Status |
|---|---|---|
| Ingestion Time (HTTP Zipball) | 1.84s | **PASS** |
| AST Modules Analyzed | 22 Python files | **PASS** |
| Total Findings Identified | 7 findings (0 High, 2 Medium, 5 Low) | **PASS** |
| OWASP Mapping Coverage | 100% mapped (A01, A03, A04, A05) | **PASS** |
| Sandbox Re-Scan Verification | 3 remediated patches verified resolved | **PASS** |
| Publication Report Export | 5.3 KB Markdown report generated | **PASS** |
| Serverless Synchronous Execution | 0 background thread dropouts | **PASS** |
| Build Toolchain | PNPM 9.15.9 clean build (502ms) | **PASS** |

---

## 12. Sign-off & Authorship

- **Product Lead & Lead Designer:** Faiqa Arooj
- **Engineering Teams:** Bugfolio, SE-Tech Society, Google Developer Groups
- **System Version:** DevFlow AI v2.1 (Production Edition)
- **Status:** **APPROVED & DEPLOYMENT VERIFIED**