# 01 — Requirements Specification

## 1. Functional requirements

| ID | Requirement | Priority | Acceptance criterion |
|---|---|---:|---|
| FR-01 | Accept a public GitHub repository URL | P0 | Valid URL creates a scan session; invalid URL receives a useful 4xx response. |
| FR-02 | Validate repository host, owner, repository, and default/ref selection | P0 | Only supported GitHub URL forms are accepted; arbitrary hosts are rejected. |
| FR-03 | Retrieve eligible repository files through GitHub API | P0 | Files are bounded by configured count, size, and total bytes. |
| FR-04 | Report repository coverage | P0 | Response includes included/skipped counts and reasons. |
| FR-05 | Run Bandit static analysis | P0 | Scanner findings are returned with tool identity and available locations. |
| FR-06 | Run AI-assisted review | P1 | AI observations are explicitly marked as AI-generated and are not presented as scanner-confirmed. |
| FR-07 | Normalize and triage findings | P0 | Findings have stable IDs, severity category, rationale, confidence, and source. |
| FR-08 | Generate a proposed patch for a selected finding | P0 | Output contains target file, explanation, and unified diff or changed content. |
| FR-09 | Re-scan the proposed change | P0 | The result is based on a new scanner run, not on the model's assertion. |
| FR-10 | Display verification status | P0 | Status is `resolved`, `still_detected`, or `unverified`, with evidence. |
| FR-11 | Preserve scan and finding status | P1 | A scan can be fetched by ID after creation. |
| FR-12 | Handle integration failures | P0 | Failure state and useful message are shown; failure never maps to zero findings. |
| FR-13 | DNotifier integration | Conditional | Implement only the capability confirmed by official docs and a successful integration test. |

## 2. Non-functional requirements

- **Security:** never execute source code from a submitted repository.
- **Read-only:** no write scopes or GitHub modifications in MVP.
- **Bounded work:** configure timeouts, file-count limits, per-file byte limits, total-byte limits, and model-token limits.
- **Reliability:** scanner errors and partial coverage are explicit.
- **Traceability:** each finding records its source (`bandit`, `ai_review`, or normalized combination) and evidence.
- **Usability:** explanations use plain language while retaining technical details.
- **Maintainability:** separate API routes, orchestration, scanner adapters, model adapters, and schemas.
- **Privacy:** do not log API keys or entire source files by default; document what is sent to the AI provider.

## 3. User stories

- As a developer, I can submit a repository and know what was analyzed.
- As a developer, I can see a scanner finding's rule, file, line, and evidence where available.
- As a learner, I can understand the possible impact in plain language.
- As a developer, I can request a proposed fix and inspect its diff before accepting it.
- As a developer, I can see whether a fresh scan still detects the issue.
- As a user, I can tell when the scan was incomplete or failed.

## 4. Explicit product language

Use: “No findings were reported by the configured checks in the analyzed files.”

Do not use: “Your repository is completely secure.”

Use: “AI-suggested observation; manual review recommended.”

Do not present AI-only claims as confirmed vulnerabilities without supporting evidence.
