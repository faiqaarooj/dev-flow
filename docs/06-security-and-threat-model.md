# 06 — Security and Threat Model

## 1. Assets

- OpenAI API key and any future GitHub credentials.
- Source code and repository metadata.
- Scan results, evidence snippets, and generated patches.
- Backend availability and resource budget.

## 2. Threats and controls

| Threat | Control |
|---|---|
| Prompt injection inside repository files | Treat source as data, not instructions; delimit it; system instructions are not overridden by repository content; validate model output. |
| Arbitrary URL / SSRF | Accept only supported GitHub repository URL patterns; call GitHub API using constructed API URLs; do not fetch arbitrary user-provided hosts. |
| Path traversal | Normalize paths; reject absolute paths and `..`; constrain all file operations to a temporary workspace. |
| Resource exhaustion | Enforce request timeout, file-count limit, per-file size limit, total byte limit, token budget, and scan deadline. |
| Accidental code execution | Never execute repository files, setup scripts, tests, or dependencies. Invoke only the scanner with controlled arguments. |
| Secret exposure | Keep API keys server-side in environment variables; redact logs; never include secrets in frontend bundles or Git. |
| False claim of clean scan | Represent stage failures, skipped files, and partial coverage explicitly. |
| Malicious or malformed model patch | Validate schema and target path; show diff; never write to upstream GitHub; re-scan before reporting verification. |
| Dependency/tool failure | Pin and document dependencies; check tool availability; treat scanner failure as an error rather than no findings. |
| Cross-request data leakage | Associate findings/proposals with scan IDs; validate object ownership if authentication is introduced. |

## 3. GitHub retrieval policy

- MVP accepts public repositories only.
- Parse repository URL; do not use it as a generic fetch URL.
- Fetch files through GitHub API endpoints built by the backend.
- Apply an allowlist of file extensions and a denylist for generated/vendor directories as appropriate.
- Limit tree depth or number of files processed.
- Record exclusions so users can understand coverage.

## 4. AI data policy

- Send only relevant source snippets and necessary scanner context.
- Inform users that code snippets are sent to the configured AI provider for analysis.
- Avoid logging prompts containing source code.
- Redact obvious secrets where feasible, while acknowledging redaction is not perfect.
- Validate model outputs against schemas and allowed file paths.

## 5. Secrets and environment

- Store `OPENAI_API_KEY` in `backend/.env` for local development only.
- Add `.env` to `.gitignore`; commit `.env.example` with placeholders only.
- Do not use `VITE_` variables for private keys; frontend variables are public.
- Configure production secrets through the hosting provider's secret manager.

## 6. Limitations to disclose

Static analysis does not find every vulnerability. AI review can be wrong. A patch that removes one scanner finding may introduce other problems. A successful re-scan is evidence only for the configured checks and analyzed files, not proof of complete security.
