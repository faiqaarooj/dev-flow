# 00 — Project Charter

## 1. Product statement

DevFlow AI helps a developer inspect a public Python GitHub repository, understand security findings, review a proposed fix, and see whether a re-scan still detects the original issue.

**Tagline:** Find the risk. Fix the code. Verify the result.

## 2. Problem

Security scanner output can be difficult for learners and developers to interpret. A finding alone does not always explain why it matters, what evidence supports it, what a safe change might look like, or whether the change actually addressed the finding.

## 3. Target user

A student developer, hackathon participant, or early-career engineer who wants understandable security feedback on a Python project without needing to be a security specialist.

## 4. Core user journey

1. Paste a public GitHub repository URL.
2. DevFlow validates the URL and reports repository coverage.
3. The backend retrieves eligible Python source files and manifests within limits.
4. Bandit runs as a static-analysis tool against retrieved source files in a controlled temporary workspace.
5. The AI analysis reviews the available source and scanner results, with scanner findings and AI-only observations labeled separately.
6. Triage groups duplicate findings and recommends a priority with rationale and confidence.
7. The user selects a finding and requests a proposed patch.
8. DevFlow shows the diff and explanation without changing GitHub.
9. The proposed changed file is re-scanned.
10. The UI reports `resolved`, `still_detected`, or `unverified`, plus coverage and remaining risks.

## 5. MVP scope

### In scope
- Public GitHub repositories.
- Python-first analysis.
- Repository coverage and skipped-file reporting.
- Bandit static analysis.
- OpenAI-supported explanation and proposed remediation.
- Finding prioritization with transparent rationale.
- Diff preview and re-scan of the proposed change.
- Scan history for a demo session, using SQLite if persistence is required.
- Explicit handling of errors and incomplete scans.

### Out of scope
- Executing repository code, install scripts, tests, or dependencies.
- Claiming comprehensive security certification.
- Automatic commits, branches, or pull requests.
- Private repositories in the first milestone.
- Multi-language support in the first milestone.
- Autonomous agents with unrestricted tools or access.
- Guaranteed exploitability, CVSS scores, or guaranteed-safe patches without a grounded method.

## 6. Success criteria

A demo is successful when the team can:
- Submit a valid public Python repository URL.
- Show what files were included and skipped.
- Display real Bandit findings with source and location when available.
- Clearly distinguish scanner findings from AI-only suggestions.
- Generate a reviewable patch for a selected finding.
- Re-scan the proposed changed file and show an honest status.
- Show unresolved, skipped, or unverified risks rather than hiding them.
- Explain scanner or API failures without presenting them as zero findings.

## 7. Product principles

- Evidence before explanation.
- Least privilege and read-only repository access.
- Human review before any use of a suggested patch.
- A failed or partial scan is never represented as a clean scan.
- The system does not execute untrusted repository code.
