# 07 — Implementation Roadmap

Build in vertical slices. At the end of every milestone, the app should do something testable.

## Milestone 0 — Repository setup
**Tasks:** create frontend/backend folders, Python virtual environment, dependency file, `.gitignore`, `.env.example`, README.

**Done when:** frontend and backend start locally; `/health` returns `{"status":"ok"}`; secrets are not committed.

## Milestone 1 — API and UI skeleton
**Tasks:** implement `POST /api/scans` validation; create repository URL form; show loading and validation errors.

**Done when:** invalid URLs are rejected and valid supported URL shape creates a scan ID (even if retrieval is stubbed temporarily).

## Milestone 2 — Real GitHub retrieval
**Tasks:** parse owner/repo/ref; use GitHub API; fetch eligible Python files; enforce limits; return coverage metadata.

**Done when:** known public repository produces file list and coverage; invalid, missing, rate-limited, or oversized repositories show explicit errors.

## Milestone 3 — Bandit integration
**Tasks:** run Bandit on retrieved Python files in a controlled temporary directory; parse JSON output; normalize findings.

**Done when:** a controlled test repository produces expected scanner findings; scanner failure is not shown as a clean scan.

## Milestone 4 — Findings UI and triage
**Tasks:** display source, rule, severity, path/line, evidence, and priority rationale; optionally add AI explanation.

**Done when:** a user can distinguish Bandit findings from AI-only observations and see coverage warnings.

## Milestone 5 — Remediation proposal
**Tasks:** ask OpenAI for a patch proposal; validate target path and diff; show before/after or unified diff.

**Done when:** the proposal is reviewable, bound to a finding and scanned commit, and does not modify GitHub.

## Milestone 6 — Re-scan and verification
**Tasks:** apply proposed changes only to a temporary copy/in-memory content; run the same configured scanner; compare the relevant rule/path; record limitations.

**Done when:** demo shows `resolved`, `still_detected`, and `unverified` behavior for appropriate test cases.

## Milestone 7 — Persistence and robustness
**Tasks:** store scans/findings/proposals/verification in SQLite; add timeout/error handling; test partial scans.

**Done when:** scan results can be fetched by ID and failure cases remain honest.

## Milestone 8 — DNotifier and final demo
**Tasks:** read official DNotifier docs; map one confirmed capability to the architecture; implement a small adapter and integration test only if feasible.

**Done when:** team can show the integration actually working or accurately explain why it is not part of the runnable MVP. Never claim unsupported integration.

## Suggested team split (2–3 people)

- **Person A — Frontend:** React components, UI states, API client, demo polish.
- **Person B — Backend/security:** FastAPI, GitHub retrieval, Bandit, limits, error handling.
- **Person C — AI/orchestration (if available):** OpenAI adapter, triage/remediation prompts, schemas, re-scan comparison, documentation/testing.

If there are only two people, Person B owns the deterministic pipeline and Person A owns the UI; split AI integration and test ownership explicitly. All members should agree on API contracts before coding in parallel.
