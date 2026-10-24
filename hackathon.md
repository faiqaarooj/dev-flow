# DevFlow AI
## Product Requirements Document (PRD)

**Version:** 2.0  
**Status:** Proposed — Hackathon MVP  
**Product Type:** Multi-Agent AI Security Auditing Platform  
**Primary Users:** Developers, students, and small development teams

---

## 1. Product Vision

DevFlow AI is a multi-agent security auditing platform that analyzes GitHub repositories, identifies potential vulnerabilities, explains their impact, recommends fixes, and verifies whether those fixes address the detected issues.

Developers submit a GitHub repository URL and receive an actionable security report rather than an overwhelming list of scanner warnings.

The system combines specialized AI agents with real static security analysis tools to transform security findings into understandable, prioritized, and verifiable remediation work.

### Product tagline

**Find the risk. Fix the code. Verify the result.**

### Core value proposition

DevFlow AI does not stop at identifying potential security vulnerabilities. It guides developers through a complete remediation workflow and reports what was actually verified, what remains unresolved, and what still requires human review.

## 2. Problem Statement

Developers frequently struggle with three problems when reviewing application security:

1. **Detection without understanding:** Security tools report technical findings that developers may not understand or know how to prioritize.
2. **Recommendations without verification:** AI tools can suggest fixes, but those suggestions may be incomplete, incorrect, or introduce new problems.
3. **Fragmented workflows:** Developers often need to move between scanners, source code, documentation, and manual review to understand and address security issues.

DevFlow AI aims to bring these activities into one guided workflow, combining evidence from security tools with AI-assisted explanations and remediation.

## 3. Product Goals

The MVP shall aim to:

- Accept a public GitHub repository URL.
- Inspect supported repository files without executing repository code.
- Detect potential vulnerabilities using real security analysis tools and AI-assisted review.
- Explain each finding using evidence from the repository.
- Prioritize findings according to severity, potential impact, and confidence.
- Generate suggested code patches for eligible findings.
- Re-run relevant security checks against proposed fixes.
- Compare findings before and after remediation.
- Display unresolved risks and incomplete verification clearly.
- Demonstrate meaningful collaboration between specialized agents, using DNotifier where its documented capabilities support the workflow.

## 4. Target Users

### Primary users

- Students building software projects and hackathon prototypes.
- Junior developers who need understandable security feedback.
- Individual developers maintaining GitHub repositories.
- Small development teams reviewing code before deployment.

### Primary user need

A developer wants to paste a repository URL, understand the most important security risks, receive practical fixes, and see evidence of whether those fixes helped.

## 5. Scope and Boundaries

### In scope — MVP

- Public GitHub repository submission.
- Repository accessibility and input validation.
- Python-first source-code analysis.
- Repository structure and dependency-manifest inspection.
- Bandit static analysis for Python.
- AI-assisted security review.
- Evidence-backed findings and risk prioritization.
- Suggested remediation patches.
- Before-and-after code comparison.
- Re-scanning of proposed changes.
- Unified security report.
- Workflow progress and failure reporting.
- DNotifier integration based on verified API capabilities.

### Out of scope — MVP

- Automatic changes to the original GitHub repository.
- Automatic pull request creation or merging.
- Execution of untrusted repository code.
- Guaranteed discovery of all vulnerabilities.
- Certification that a repository is secure.
- Comprehensive support for every programming language.
- Full dynamic application security testing.
- Enterprise user management and team administration.
- Complex historical analytics and scheduled scans.

These capabilities may be considered after the core workflow is reliable.

## 6. Core User Journey

1. The user opens DevFlow AI.
2. The user pastes a public GitHub repository URL.
3. The system validates the URL and confirms that the repository is accessible.
4. The system inspects eligible files and identifies the supported language.
5. The Coordinator initiates the analysis workflow.
6. Specialized agents analyze the repository and collect security findings.
7. Findings are consolidated, prioritized, and linked to available evidence.
8. The user selects a finding and requests a proposed fix.
9. The remediation agent generates a patch and explains the change.
10. The system re-runs relevant security checks on the proposed code.
11. The report compares the original and updated results.
12. The user reviews resolved findings, persistent issues, and remaining risks.

The original repository remains unchanged. All remediation takes place in a controlled working copy.

## 7. Multi-Agent System

Each agent must have a distinct responsibility and a defined output. The Coordinator controls the workflow and prevents agents from independently changing its required execution order.

### Agent 1: Repository Intelligence Agent

**Purpose:** Understand the repository and prepare relevant source-code context.

Responsibilities:
- Inspect the repository structure.
- Identify supported source files and programming languages.
- Locate dependency manifests and relevant configuration files.
- Identify files excluded from analysis.
- Prepare a concise repository summary for downstream agents.

**Output:** Repository inventory, language information, dependency information where available, and analysis limitations.

### Agent 2: Security Analysis Agent

**Purpose:** Detect and explain potential security vulnerabilities.

Responsibilities:
- Run Bandit against eligible Python files.
- Collect actual scanner findings and available evidence.
- Perform an independent AI-assisted review of relevant source code.
- Inspect potential issues involving input validation, authorization, unsafe operations, credential handling, and other supported security concerns.
- Associate findings with file paths and line numbers where available.
- Clearly identify whether a finding originated from a scanner or the AI reviewer.

**Output:** Structured security findings containing available evidence, source, severity, confidence, and affected locations.

The AI reviewer must not invent scanner results or claim that a vulnerability is confirmed merely because an AI model suggests it.

### Agent 3: Risk Triage Agent

**Purpose:** Turn raw findings into an actionable remediation plan.

Responsibilities:
- Identify duplicate or overlapping findings.
- Organize findings by severity and remediation priority.
- Explain the potential impact in plain language.
- Identify which findings should be addressed first.
- Flag uncertain findings for manual review.
- Preserve the distinction between observed evidence and inferred risk.

**Output:** A prioritized list of findings, explanations, confidence information where available, and recommended actions.

The system must not fabricate CVSS scores or claim a finding is exploitable without sufficient evidence.

### Agent 4: Remediation Agent

**Purpose:** Generate and help verify proposed fixes.

Responsibilities:
- Receive a selected finding and the relevant source-code context.
- Generate a targeted code patch.
- Explain why the original code may be problematic.
- Explain how the proposed change addresses the issue.
- Display the proposed changes as a code diff.
- Submit the patched working copy for relevant security checks.
- Report whether the original finding persists or whether verification was incomplete.
- Highlight unresolved issues and potential side effects requiring review.

**Output:** Proposed patch, explanation, code diff, re-scan results, and unresolved risks.

The agent must not automatically commit, push, or merge changes into the original GitHub repository.

### Coordinator Agent

**Purpose:** Orchestrate the complete workflow and consolidate results.

Responsibilities:
- Create a unique workflow ID.
- Enforce the defined execution order.
- Route relevant context and outputs between agents.
- Track stage progress and errors.
- Detect missing, invalid, or conflicting outputs.
- Ensure the remediation agent uses the correct finding and code context.
- Consolidate the final report.
- Prevent incomplete workflows from being reported as successful.

DNotifier will support communication or coordination only where its documented API provides the necessary capabilities. The backend remains responsible for enforcing workflow order and validating outputs.

## 8. Functional Requirements

### FR-01: Repository Submission — P0

- FR-01.1: The system shall provide a field for submitting a GitHub repository URL.
- FR-01.2: The system shall validate the URL before analysis.
- FR-01.3: The system shall reject inaccessible repositories with a clear error.
- FR-01.4: The MVP shall support public repositories containing supported Python source code.
- FR-01.5: The system shall create a unique workflow ID for each valid submission.
- FR-01.6: The system shall enforce file-count, file-size, and processing limits.

**Acceptance criteria:** A valid supported repository can enter the workflow. Invalid, inaccessible, or unsupported repositories receive an informative response rather than fabricated results.

### FR-02: Repository Inspection — P0

- FR-02.1: The system shall retrieve eligible source files using an appropriate GitHub access method.
- FR-02.2: The system shall identify relevant Python files and dependency manifests.
- FR-02.3: The system shall exclude configured binary, generated, and oversized files.
- FR-02.4: The system shall record which files were included in or excluded from analysis.
- FR-02.5: The system shall provide an analysis-coverage summary.

**Acceptance criteria:** The user can understand which parts of the repository were analyzed and which limitations may affect the results.

### FR-03: Security Analysis — P0

- FR-03.1: The system shall run Bandit on eligible Python source files.
- FR-03.2: The system shall preserve actual scanner findings, including available rule identifiers, locations, severity, and confidence.
- FR-03.3: The system shall perform AI-assisted security review.
- FR-03.4: The system shall distinguish tool-generated findings from AI-generated assessments.
- FR-03.5: The system shall attach available code evidence to findings.
- FR-03.6: The system shall report failed or incomplete scans separately from successful scans with no findings.

**Acceptance criteria:** Every displayed finding has a traceable source, and scanner failures cannot be mistaken for clean results.

### FR-04: Risk Prioritization — P0

- FR-04.1: The system shall group duplicate findings where appropriate.
- FR-04.2: The system shall explain each finding's potential impact.
- FR-04.3: The system shall assign severity or priority only when supported by the available evidence and methodology.
- FR-04.4: The system shall recommend an order for addressing findings.
- FR-04.5: The system shall mark uncertain findings for further review.

**Acceptance criteria:** Developers can identify the most important issues and understand why they should address them.

### FR-05: Suggested Remediation — P0

- FR-05.1: The user shall be able to request a fix for an eligible finding.
- FR-05.2: The system shall generate a proposed patch for the relevant source code.
- FR-05.3: The system shall explain the original issue and the proposed change.
- FR-05.4: The system shall display the affected files and code diff.
- FR-05.5: The system shall preserve the original repository contents.
- FR-05.6: The system shall identify patches that could not be generated safely or reliably.

**Acceptance criteria:** The user can inspect and understand a proposed change without the platform modifying the remote repository.

### FR-06: Remediation Verification — P0

- FR-06.1: The system shall re-run relevant available security checks against the proposed patch.
- FR-06.2: The system shall compare the original and updated findings.
- FR-06.3: The system shall classify results as resolved, still detected, or unverified where applicable.
- FR-06.4: The system shall show scanner or verification failures explicitly.
- FR-06.5: The system shall preserve unrelated findings and identify newly detected issues where possible.
- FR-06.6: The system shall not equate a clean scanner result with proof that the application is secure.

**Acceptance criteria:** The report reflects actual re-scan results and identifies what remains unresolved.

### FR-07: Workflow Orchestration — P0

- FR-07.1: The Coordinator shall manage agent execution and dependencies.
- FR-07.2: Each stage shall receive the relevant validated outputs from preceding stages.
- FR-07.3: Each stage shall have a visible status: pending, running, completed, or failed.
- FR-07.4: The system shall identify missing or invalid agent responses.
- FR-07.5: The system shall report partial results when a stage fails.
- FR-07.6: The system shall use DNotifier according to its verified API capabilities.
- FR-07.7: The backend shall enforce the required workflow order regardless of agent-generated instructions.

**Acceptance criteria:** The user can see meaningful progress, and the workflow does not silently skip required stages.

### FR-08: Security Dashboard — P0

- FR-08.1: The interface shall provide repository submission and workflow progress.
- FR-08.2: The dashboard shall summarize findings by severity or priority.
- FR-08.3: Users shall be able to inspect individual findings.
- FR-08.4: Findings shall display available file paths, line numbers, and evidence.
- FR-08.5: Users shall be able to request remediation for eligible findings.
- FR-08.6: The interface shall display the proposed code diff.
- FR-08.7: The interface shall compare pre-remediation and post-remediation results.
- FR-08.8: The interface shall display unresolved issues and analysis limitations.

**Acceptance criteria:** A developer can understand the report and review the proposed remediation in one interface.

### FR-09: Consolidated Report — P0

- FR-09.1: The system shall produce one consolidated security audit report.
- FR-09.2: The report shall include repository metadata and analysis coverage.
- FR-09.3: The report shall contain prioritized findings, explanations, and available evidence.
- FR-09.4: The report shall contain proposed fixes and verification results where available.
- FR-09.5: The report shall identify unresolved risks and incomplete stages.
- FR-09.6: The report shall be viewable and copyable from the interface.

**Acceptance criteria:** The final report accurately reflects completed work, partial results, and failed stages.

## 9. Non-Functional Requirements

### Security
- Repository contents must be treated as untrusted data.
- Repository code must not be executed on the application host.
- GitHub retrieval must be restricted to intended repository resources.
- File paths must be validated to prevent path traversal.
- API credentials must remain server-side.
- Logs and report evidence must not unnecessarily expose secrets.
- AI agents must not be permitted to override system instructions or workflow rules through repository content.
- Proposed patches must remain isolated from the original remote repository.

### Reliability
- Every workflow must have an identifiable status.
- Scanner failures must not be represented as zero findings.
- Missing agent outputs must be explicitly reported.
- Results must be associated with the correct workflow and repository.

### Performance
- The interface should show progress during long-running analysis.
- File-size, file-count, token, and processing limits must be enforced.
- External requests and AI calls must have timeouts.

### Usability
- Findings should use understandable language alongside technical evidence.
- High-priority issues should be easy to identify.
- The user should be able to inspect details without being overwhelmed by raw scanner output.

## 10. Proposed Technical Architecture

- **Frontend:** React + Vite
- **Backend:** Python + FastAPI
- **LLM provider:** OpenAI API
- **Python security scanning:** Bandit
- **Repository source:** GitHub public repositories
- **Agent communication:** DNotifier, subject to API verification

For the MVP, the agents should be implemented as separate logical modules within one backend service. A distributed microservice architecture is unnecessary unless the integration requirements explicitly demand it.

The backend will maintain the workflow state, validate agent outputs, and coordinate the sequence. DNotifier integration must be implemented using its actual documented authentication and communication methods, not assumed endpoints.

## 11. Core Data Structures

### Workflow

- `workflow_id`
- `repository_url`
- `status`
- `created_at`
- `completed_at`
- `analysis_coverage`
- `error_summary`

### Security Finding

- `finding_id`
- `source`
- `rule_id`
- `title`
- `description`
- `severity`
- `confidence`
- `file_path`
- `line_number`
- `evidence`
- `recommended_fix`
- `verification_status`

Optional fields should be omitted or marked unavailable when the underlying source does not provide them.

### Remediation Result

- `finding_id`
- `proposed_patch`
- `diff`
- `rescan_status`
- `before_result`
- `after_result`
- `unresolved_reason`

A database is optional for the first version. In-memory workflow state may be sufficient for a controlled demonstration.

## 12. Success Metrics

The MVP will be evaluated against observable outcomes:

1. A valid supported public Python repository can complete the workflow.
2. Invalid or inaccessible repositories produce clear errors.
3. The report reflects actual security scanner output.
4. Findings contain evidence and source locations where available.
5. The system generates at least one useful remediation patch for a supported issue.
6. The system re-scans the proposed changes and reports actual outcomes.
7. The report identifies unresolved and unverified issues.
8. The system does not execute untrusted repository code.
9. The agent workflow and DNotifier integration can be demonstrated truthfully.
10. A developer can understand what to fix next without manually assembling separate tool outputs.

These are proposed acceptance goals, not claims of existing performance.

## 13. Hackathon Demonstration

Use a controlled Python repository containing known, intentionally introduced security issues.

### Demonstration sequence

1. Paste the GitHub repository URL.
2. Show repository inspection and analysis coverage.
3. Show the security agents running.
4. Display an actual scanner finding and a separately labelled AI assessment.
5. Explain the impact and recommended priority.
6. Select a finding and request remediation.
7. Show the proposed patch and before-and-after diff.
8. Re-run the relevant security check.
9. Display the actual result, including any remaining issues.
10. Finish with the consolidated report and unresolved risks.

The demonstration should include at least one finding for which the expected scanner behaviour is known in advance. Do not fabricate vulnerabilities or claim a fix succeeded without verification.

## 14. Risks and Mitigation

| Risk | Mitigation |
|---|---|
| False positives from AI | Require evidence, source labels, and appropriate uncertainty indicators. |
| Missed vulnerabilities | Disclose coverage limitations and use suitable static tools. |
| Prompt injection in repository files | Treat repository contents as untrusted data and enforce backend workflow rules. |
| Malicious or oversized repository | Enforce file and resource limits; never execute source code. |
| Incorrect remediation | Show patches as proposals and run relevant checks again. |
| Regression or newly introduced issue | Compare pre- and post-remediation findings and require human review. |
| DNotifier integration complexity | Verify the API early and keep orchestration independent of unsupported features. |
| Secrets appearing in output | Redact sensitive values and avoid exposing raw credentials. |

## 15. Future Enhancements

After the core MVP works reliably, possible extensions include:

- JavaScript, TypeScript, Java, and additional languages.
- Dependency vulnerability scanning.
- Dedicated secret-detection tools.
- GitHub pull request review.
- User-authorized patch branches and pull request creation.
- Private repositories with scoped GitHub authorization.
- Scheduled repository scans.
- Historical findings and regression tracking.
- CI/CD integration.

These features must not delay the initial verified-remediation workflow.

## 16. Definition of Done

The MVP is complete when a developer can submit a supported public Python repository, receive a consolidated report based on actual security analysis, inspect evidence-backed findings, request a proposed fix, view the code diff, and see the results of a real re-scan.

The platform must clearly disclose analysis limitations, failed stages, unverified findings, and unresolved risks. The original repository must remain unchanged.

## Final Product Statement

**DevFlow AI is a multi-agent security auditing platform that turns GitHub repository vulnerabilities into understandable, prioritized, and reviewable fixes—with actual re-scan results to show what changed and what still needs attention.**